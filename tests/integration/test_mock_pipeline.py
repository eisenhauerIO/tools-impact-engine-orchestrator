import pytest
from impact_engine_evaluate import Evaluate

from impact_engine_orchestrator.components.allocate.mock import MockAllocate
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
        allocate=MockAllocate(),
        config=config,
    )


def test_all_mocks_pipeline(measure_env):
    orchestrator = _make_orchestrator(measure_env)
    result = orchestrator.run()

    assert len(result["outcome_reports"]) > 0

    # Verify determinism
    result2 = orchestrator.run()
    assert result["pilot_results"] == result2["pilot_results"]


def test_contract_invariants(measure_env):
    orchestrator = _make_orchestrator(measure_env)
    result = orchestrator.run()

    for pilot in result["pilot_results"]:
        assert pilot["ci_lower"] <= pilot["effect_estimate"] <= pilot["ci_upper"]
        assert 0.0 <= pilot["p_value"] <= 1.0
        assert pilot["sample_size"] >= 30
        assert isinstance(pilot["model_type"], ModelType)

    for evalu in result["evaluate_results"]:
        assert evalu["return_worst"] <= evalu["return_median"] <= evalu["return_best"]
        assert 0.0 <= evalu["confidence"] <= 1.0
        assert evalu["cost"] > 0
        assert isinstance(evalu["model_type"], ModelType)

    alloc = result["allocate_result"]
    for iid in alloc["selected_initiatives"]:
        assert iid in alloc["predicted_returns"]
        assert iid in alloc["budget_allocated"]

    for report in result["outcome_reports"]:
        assert report["prediction_error"] == pytest.approx(report["actual_return"] - report["predicted_return"])
        assert report["sample_size_scale"] >= report["sample_size_pilot"]
        assert isinstance(report["model_type"], ModelType)


def test_empty_allocation(measure_env):
    """Budget too small for any initiative — no initiatives selected."""
    orchestrator = _make_orchestrator(measure_env, budget=1)
    result = orchestrator.run()

    assert result["allocate_result"]["selected_initiatives"] == []
    assert result["scale_results"] == []
    assert result["outcome_reports"] == []


def test_single_initiative(measure_env):
    orchestrator = _make_orchestrator(measure_env, initiative_specs=[("only-one", 5000)])
    result = orchestrator.run()

    assert len(result["pilot_results"]) == 1
    assert len(result["outcome_reports"]) == 1
    assert result["outcome_reports"][0]["initiative_id"] == "only-one"
