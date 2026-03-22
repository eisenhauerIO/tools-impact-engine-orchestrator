import dataclasses

import pytest

from impact_engine_orchestrator.components.allocate.mock import MockAllocate
from impact_engine_orchestrator.components.evaluate.evaluate import Evaluate
from impact_engine_orchestrator.config import PipelineConfig, StageConfig
from impact_engine_orchestrator.contracts.pipeline import PipelineResult
from impact_engine_orchestrator.contracts.types import ModelType
from impact_engine_orchestrator.orchestrator import Orchestrator


def _make_orchestrator(measure_env, budget=100000, initiative_specs=None):
    make_initiative, make_measure, storage_url = measure_env
    if initiative_specs is None:
        initiative_specs = [
            ("init-001", 10000),
            ("init-002", 15000),
            ("init-003", 8000),
        ]
    initiatives = [make_initiative(iid, cost) for iid, cost in initiative_specs]
    config = dataclasses.asdict(
        PipelineConfig(
            initiatives=initiatives,
            max_workers=1,
            measure_stage=StageConfig(component="Measure", kwargs={"storage_url": storage_url}),
            allocate_stage=StageConfig(component="MockAllocate", kwargs={"budget": budget, "rule": "minimax_regret"}),
        )
    )
    return Orchestrator(
        measure=make_measure(),
        evaluate=Evaluate(),
        allocate=MockAllocate(),
        config=config,
    )


def test_all_mocks_pipeline(measure_env):
    orchestrator = _make_orchestrator(measure_env)
    result = orchestrator.run()

    assert isinstance(result, PipelineResult)
    assert len(result.outcome_reports) > 0

    # Verify determinism
    result2 = orchestrator.run()
    assert result.pilot_results == result2.pilot_results


def test_contract_invariants(measure_env):
    orchestrator = _make_orchestrator(measure_env)
    result = orchestrator.run()

    for pilot in result.pilot_results:
        assert pilot["ci_lower"] <= pilot["effect_estimate"] <= pilot["ci_upper"]
        assert 0.0 <= pilot["p_value"] <= 1.0
        assert pilot["sample_size"] >= 30
        assert isinstance(pilot["model_type"], ModelType)

    for evalu in result.evaluate_results:
        assert 0.0 <= evalu["confidence"] <= 1.0

    alloc = result.allocate_result
    for iid in alloc["selected_initiatives"]:
        assert iid in alloc["predicted_returns"]
        assert iid in alloc["budget_allocated"]

    for report in result.outcome_reports:
        assert report.prediction_error == pytest.approx(report.actual_return - report.predicted_return)
        assert report.sample_size_scale >= report.sample_size_pilot
        assert isinstance(report.model_type, ModelType)


def test_empty_allocation(measure_env):
    """Budget too small for any initiative — no initiatives selected."""
    orchestrator = _make_orchestrator(measure_env, budget=1)
    result = orchestrator.run()

    assert result.allocate_result["selected_initiatives"] == []
    assert result.scale_results == []
    assert result.outcome_reports == []


def test_single_initiative(measure_env):
    orchestrator = _make_orchestrator(measure_env, initiative_specs=[("only-one", 5000)])
    result = orchestrator.run()

    assert len(result.pilot_results) == 1
    assert len(result.outcome_reports) == 1
    assert result.outcome_reports[0].initiative_id == "only-one"


class _IncompleteMeasure:
    """Mock that returns a dict missing required keys."""

    def execute(self, event: dict) -> dict:
        return {"initiative_id": event["initiative_id"]}


def test_missing_keys_raises(measure_env):
    """Validation catches incomplete stage output with a clear message."""
    make_initiative, _, storage_url = measure_env
    initiatives = [make_initiative("bad-init", 5000)]
    config = dataclasses.asdict(
        PipelineConfig(
            initiatives=initiatives,
            measure_stage=StageConfig(component="Measure", kwargs={"storage_url": storage_url}),
            allocate_stage=StageConfig(component="MockAllocate", kwargs={"budget": 100000, "rule": "minimax_regret"}),
        )
    )
    orchestrator = Orchestrator(
        measure=_IncompleteMeasure(),
        evaluate=Evaluate(),
        allocate=MockAllocate(),
        config=config,
    )

    with pytest.raises(ValueError, match="MEASURE output missing required keys"):
        orchestrator.run()
