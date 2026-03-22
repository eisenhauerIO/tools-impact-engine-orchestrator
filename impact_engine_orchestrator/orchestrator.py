"""Fan-out/fan-in pipeline runner."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

from impact_engine_orchestrator.components.base import PipelineComponentProtocol
from impact_engine_orchestrator.contracts.pipeline import PipelineResult
from impact_engine_orchestrator.contracts.report import OutcomeReport

_MEASURE_REQUIRED_KEYS = frozenset(
    {
        "initiative_id",
        "effect_estimate",
        "ci_lower",
        "ci_upper",
        "p_value",
        "sample_size",
        "model_type",
        "diagnostics",
    }
)
_EVALUATE_REQUIRED_KEYS = frozenset(
    {
        "initiative_id",
        "confidence",
    }
)
_ALLOCATE_REQUIRED_KEYS = frozenset(
    {
        "selected_initiatives",
        "predicted_returns",
        "budget_allocated",
    }
)


def _validate_stage_output(stage: str, result: dict, required_keys: frozenset[str]) -> None:
    """Raise if required keys are missing from a stage output dict."""
    missing = required_keys - result.keys()
    if missing:
        raise ValueError(f"{stage} output missing required keys: {sorted(missing)}")


class Orchestrator:
    """Run the full MEASURE-EVALUATE-ALLOCATE-SCALE pipeline."""

    def __init__(
        self,
        measure: PipelineComponentProtocol,
        evaluate: PipelineComponentProtocol,
        allocate: PipelineComponentProtocol,
        config: dict,
    ):
        self.measure = measure
        self.evaluate = evaluate
        self.allocate = allocate
        self.config = config

    @classmethod
    def from_config(cls, config: dict) -> Orchestrator:
        """Build an Orchestrator from a pipeline config dict with stage configs."""
        from impact_engine_orchestrator import registry

        if config.get("allocate_stage") is None:
            raise ValueError("allocate_stage is required")

        measure = registry.build(config["measure_stage"])
        evaluate = registry.build(config["evaluate_stage"])
        allocate = registry.build(config["allocate_stage"])
        return cls(measure=measure, evaluate=evaluate, allocate=allocate, config=config)

    def run(self) -> PipelineResult:
        """Execute all pipeline stages and return combined results."""
        initiatives = self.config["initiatives"]
        cost_by_id = {i["initiative_id"]: i["cost_to_scale"] for i in initiatives}
        config_by_id = {i["initiative_id"]: i["measure_config"] for i in initiatives}
        data_dir = self.config["measure_stage"]["kwargs"]["storage_url"]

        with ThreadPoolExecutor(max_workers=self.config["max_workers"]) as pool:
            # 1. MEASURE (pilot) - parallel (enrich with measure_config and evaluate_strategy)
            measure_inputs = [
                {
                    "initiative_id": i["initiative_id"],
                    "measure_config": i["measure_config"],
                    "evaluate_strategy": i["evaluate_strategy"],
                }
                for i in initiatives
            ]
            pilot_results = self._fan_out(self.measure, measure_inputs, pool)
            for r in pilot_results:
                _validate_stage_output("MEASURE", r, _MEASURE_REQUIRED_KEYS)

            # 2. EVALUATE - parallel (pilot results carry job_dir; enrich with cost_to_scale)
            # evaluate_confidence() writes evaluate_result.json to each job_dir.
            eval_inputs = [{**result, "cost_to_scale": cost_by_id[result["initiative_id"]]} for result in pilot_results]
            eval_results = self._fan_out(self.evaluate, eval_inputs, pool)
            for r in eval_results:
                _validate_stage_output("EVALUATE", r, _EVALUATE_REQUIRED_KEYS)

            # 3. ALLOCATE - reads impact_results.json + evaluate_result.json from disk
            allocate_config = {
                "costs": cost_by_id,
                **self._allocate_kwargs(),
            }
            alloc_result = self.allocate.execute(
                {
                    "data_dir": data_dir,
                    "allocate_config": allocate_config,
                }
            )
            _validate_stage_output("ALLOCATE", alloc_result, _ALLOCATE_REQUIRED_KEYS)

            # 4. MEASURE (scale) - parallel on selected only (enrich with measure_config)
            selected_ids = alloc_result["selected_initiatives"]
            scale_inputs = [
                {
                    "initiative_id": iid,
                    "measure_config": config_by_id[iid],
                }
                for iid in selected_ids
            ]
            scale_results = self._fan_out(self.measure, scale_inputs, pool)
            for r in scale_results:
                _validate_stage_output("MEASURE", r, _MEASURE_REQUIRED_KEYS)

        # 5. Generate outcome reports
        reports = self._generate_reports(pilot_results, eval_results, alloc_result, scale_results)

        return PipelineResult(
            outcome_reports=reports,
            pilot_results=pilot_results,
            evaluate_results=eval_results,
            allocate_result=alloc_result,
            scale_results=scale_results,
        )

    def _allocate_kwargs(self) -> dict:
        """Extract allocate-specific kwargs from stage config."""
        stage = self.config.get("allocate_stage")
        if stage is None:
            return {}
        return dict(stage.get("kwargs", {}))

    def _fan_out(self, component, inputs, pool):
        """Submit inputs to the pool and collect results in submission order.

        If any component raises, the exception propagates immediately but
        already-submitted futures continue running until the pool's context
        manager shuts them down.
        """
        futures = [pool.submit(component.execute, inp) for inp in inputs]
        return [f.result() for f in futures]

    def _generate_reports(self, pilot_results, eval_results, alloc_result, scale_results):
        """Build outcome reports comparing pilot predictions to scale actuals."""
        pilot_by_id = {p["initiative_id"]: p for p in pilot_results}
        eval_by_id = {e["initiative_id"]: e for e in eval_results}
        scale_by_id = {s["initiative_id"]: s for s in scale_results}

        reports = []
        for iid in alloc_result["selected_initiatives"]:
            pilot = pilot_by_id[iid]
            evalu = eval_by_id[iid]
            scale = scale_by_id[iid]
            predicted = alloc_result["predicted_returns"][iid]
            actual = scale["effect_estimate"]

            report = OutcomeReport(
                initiative_id=iid,
                predicted_return=predicted,
                actual_return=actual,
                prediction_error=actual - predicted,
                sample_size_pilot=pilot["sample_size"],
                sample_size_scale=scale["sample_size"],
                budget_allocated=alloc_result["budget_allocated"][iid],
                confidence_score=evalu["confidence"],
                model_type=pilot["model_type"],
            )
            reports.append(report)
        return reports
