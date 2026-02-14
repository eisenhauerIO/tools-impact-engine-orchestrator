import pytest
from portfolio_allocation import MinimaxRegretAllocate

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
        allocate=MinimaxRegretAllocate(),
        config=config,
    )


def test_real_allocate_pipeline():
    orchestrator = _make_orchestrator()
    result = orchestrator.run()

    assert len(result["outcome_reports"]) > 0


def test_real_allocate_contract_invariants():
    orchestrator = _make_orchestrator()
    result = orchestrator.run()

    alloc = result["allocate_result"]
    for iid in alloc["selected_initiatives"]:
        assert iid in alloc["predicted_returns"]
        assert iid in alloc["budget_allocated"]

    for report in result["outcome_reports"]:
        assert report["prediction_error"] == pytest.approx(report["actual_return"] - report["predicted_return"])
        assert report["sample_size_scale"] >= report["sample_size_pilot"]
        assert isinstance(report["model_type"], ModelType)


def test_real_allocate_determinism():
    orchestrator = _make_orchestrator()
    result1 = orchestrator.run()
    result2 = orchestrator.run()

    assert result1["allocate_result"] == result2["allocate_result"]


def test_real_allocate_empty_budget():
    orchestrator = _make_orchestrator(budget=1)
    result = orchestrator.run()

    assert result["allocate_result"]["selected_initiatives"] == []
    assert result["scale_results"] == []
    assert result["outcome_reports"] == []
