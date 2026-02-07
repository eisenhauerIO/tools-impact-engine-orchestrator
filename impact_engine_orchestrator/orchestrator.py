"""Fan-out/fan-in pipeline runner."""

from concurrent.futures import ThreadPoolExecutor

from impact_engine_orchestrator.config import PipelineConfig


class Orchestrator:
    """Run the full MEASURE-EVALUATE-ALLOCATE-SCALE pipeline."""

    def __init__(self, measure, evaluate, allocate, config: PipelineConfig):
        self.measure = measure
        self.evaluate = evaluate
        self.allocate = allocate
        self.config = config

    def run(self) -> dict:
        """Execute all pipeline stages and return combined results."""
        initiatives = self.config.initiatives
        cost_by_id = {i.initiative_id: i.cost_to_scale for i in initiatives}

        with ThreadPoolExecutor(max_workers=self.config.max_workers) as pool:
            # 1. MEASURE (pilot) - parallel
            measure_inputs = [{"initiative_id": i.initiative_id} for i in initiatives]
            pilot_results = self._fan_out(self.measure, measure_inputs, pool)

            # 2. EVALUATE - parallel (enrich with cost_to_scale from config)
            eval_inputs = [{**result, "cost_to_scale": cost_by_id[result["initiative_id"]]} for result in pilot_results]
            eval_results = self._fan_out(self.evaluate, eval_inputs, pool)

            # 3. ALLOCATE - single (budget from config)
            alloc_result = self.allocate.execute(
                {
                    "initiatives": eval_results,
                    "budget": self.config.budget,
                }
            )

            # 4. MEASURE (scale) - parallel on selected only
            selected_ids = alloc_result["selected_initiatives"]
            scale_inputs = [
                {"initiative_id": iid, "sample_size": self.config.scale_sample_size} for iid in selected_ids
            ]
            scale_results = self._fan_out(self.measure, scale_inputs, pool)

        # 5. Generate outcome reports
        reports = self._generate_reports(pilot_results, eval_results, alloc_result, scale_results)

        return {
            "pilot_results": pilot_results,
            "evaluate_results": eval_results,
            "allocate_result": alloc_result,
            "scale_results": scale_results,
            "outcome_reports": reports,
        }

    def _fan_out(self, component, inputs, pool):
        futures = [pool.submit(component.execute, inp) for inp in inputs]
        return [f.result() for f in futures]

    def _generate_reports(self, pilot_results, eval_results, alloc_result, scale_results):
        reports = []
        pilot_by_id = {p["initiative_id"]: p for p in pilot_results}
        eval_by_id = {e["initiative_id"]: e for e in eval_results}
        scale_by_id = {s["initiative_id"]: s for s in scale_results}

        for iid in alloc_result["selected_initiatives"]:
            pilot = pilot_by_id[iid]
            evalu = eval_by_id[iid]
            scale = scale_by_id[iid]
            predicted = alloc_result["predicted_returns"][iid]
            actual = scale["effect_estimate"]

            reports.append(
                {
                    "initiative_id": iid,
                    "predicted_return": predicted,
                    "actual_return": actual,
                    "prediction_error": actual - predicted,
                    "sample_size_pilot": pilot["sample_size"],
                    "sample_size_scale": scale["sample_size"],
                    "budget_allocated": alloc_result["budget_allocated"][iid],
                    "confidence_score": evalu["confidence"],
                    "model_type": evalu["model_type"],
                }
            )
        return reports
