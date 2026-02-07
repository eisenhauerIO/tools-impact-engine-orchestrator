import pytest

from impact_engine_orchestrator.components.allocate.mock import MockAllocate
from impact_engine_orchestrator.components.evaluate.mock import MockEvaluate
from impact_engine_orchestrator.components.measure.mock import MockMeasure
from impact_engine_orchestrator.config import InitiativeConfig, PipelineConfig
from impact_engine_orchestrator.contracts.types import ModelType
from impact_engine_orchestrator.orchestrator import Orchestrator


def _make_orchestrator(budget=100000, initiatives=None):
    if initiatives is None:
        initiatives = [
            InitiativeConfig("init-001", cost_to_scale=10000),
            InitiativeConfig("init-002", cost_to_scale=15000),
            InitiativeConfig("init-003", cost_to_scale=8000),
        ]
    config = PipelineConfig(
        budget=budget,
        scale_sample_size=5000,
        initiatives=initiatives,
    )
    return Orchestrator(
        measure=MockMeasure(),
        evaluate=MockEvaluate(),
        allocate=MockAllocate(),
        config=config,
    )


def test_all_mocks_pipeline():
    orchestrator = _make_orchestrator()
    result = orchestrator.run()

    assert len(result["outcome_reports"]) > 0

    # Verify determinism
    result2 = orchestrator.run()
    assert result["pilot_results"] == result2["pilot_results"]


def test_contract_invariants():
    orchestrator = _make_orchestrator()
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


def test_empty_allocation():
    """Budget too small for any initiative — no initiatives selected."""
    orchestrator = _make_orchestrator(budget=1)
    result = orchestrator.run()

    assert result["allocate_result"]["selected_initiatives"] == []
    assert result["scale_results"] == []
    assert result["outcome_reports"] == []


def test_single_initiative():
    orchestrator = _make_orchestrator(initiatives=[InitiativeConfig("only-one", cost_to_scale=5000)])
    result = orchestrator.run()

    assert len(result["pilot_results"]) == 1
    assert len(result["outcome_reports"]) == 1
    assert result["outcome_reports"][0]["initiative_id"] == "only-one"
