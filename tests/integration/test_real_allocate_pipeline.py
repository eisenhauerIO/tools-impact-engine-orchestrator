import pytest
from impact_engine_evaluate import Evaluate
from portfolio_allocation import MinimaxRegretAllocate

from impact_engine_orchestrator.config import PipelineConfig
from impact_engine_orchestrator.contracts.types import ModelType
from impact_engine_orchestrator.orchestrator import Orchestrator


def _make_orchestrator(measure_env, budget=100000, initiative_specs=None):
    make_initiative, make_measure = measure_env
    if initiative_specs is None:
        initiative_specs = [
            ("init-001", 10000),
            ("init-002", 15000),
            ("init-003", 8000),
        ]
    initiatives = [make_initiative(iid, cost) for iid, cost in initiative_specs]
    config = PipelineConfig(
        budget=budget,
        scale_sample_size=5000,
        initiatives=initiatives,
    )
    return Orchestrator(
        measure=make_measure(),
        evaluate=Evaluate(),
        allocate=MinimaxRegretAllocate(),
        config=config,
    )


def test_real_allocate_pipeline(measure_env):
    orchestrator = _make_orchestrator(measure_env)
    result = orchestrator.run()

    assert len(result["outcome_reports"]) > 0


def test_real_allocate_contract_invariants(measure_env):
    orchestrator = _make_orchestrator(measure_env)
    result = orchestrator.run()

    alloc = result["allocate_result"]
    for iid in alloc["selected_initiatives"]:
        assert iid in alloc["predicted_returns"]
        assert iid in alloc["budget_allocated"]

    for report in result["outcome_reports"]:
        assert report["prediction_error"] == pytest.approx(report["actual_return"] - report["predicted_return"])
        assert report["sample_size_scale"] >= report["sample_size_pilot"]
        assert isinstance(report["model_type"], ModelType)


def test_real_allocate_determinism(measure_env):
    orchestrator = _make_orchestrator(measure_env)
    result1 = orchestrator.run()
    result2 = orchestrator.run()

    assert result1["allocate_result"] == result2["allocate_result"]


def test_real_allocate_empty_budget(measure_env):
    orchestrator = _make_orchestrator(measure_env, budget=1)
    result = orchestrator.run()

    assert result["allocate_result"]["selected_initiatives"] == []
    assert result["scale_results"] == []
    assert result["outcome_reports"] == []
