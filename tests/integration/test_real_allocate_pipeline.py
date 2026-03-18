import dataclasses

import pytest

from impact_engine_orchestrator.components.allocate.allocate import Allocate
from impact_engine_orchestrator.components.evaluate.evaluate import Evaluate
from impact_engine_orchestrator.config import PipelineConfig, StageConfig
from impact_engine_orchestrator.contracts.types import ModelType
from impact_engine_orchestrator.orchestrator import Orchestrator


def _make_orchestrator(measure_env, budget=100000, initiative_specs=None, allocate_kwargs=None):
    make_initiative, make_measure, storage_url = measure_env
    if initiative_specs is None:
        initiative_specs = [
            ("init-001", 10000),
            ("init-002", 15000),
            ("init-003", 8000),
        ]
    if allocate_kwargs is None:
        allocate_kwargs = {"rule": "minimax_regret", "min_portfolio_worst_return": -1e9}

    initiatives = [make_initiative(iid, cost) for iid, cost in initiative_specs]
    config = dataclasses.asdict(
        PipelineConfig(
            budget=budget,
            scale_sample_size=5000,
            initiatives=initiatives,
            max_workers=1,
            measure_stage=StageConfig(component="Measure", kwargs={"storage_url": storage_url}),
            allocate_stage=StageConfig(component="MinimaxRegretAllocate", kwargs=allocate_kwargs),
        )
    )
    return Orchestrator(
        measure=make_measure(),
        evaluate=Evaluate(),
        allocate=Allocate(),
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


# --- Bayesian pipeline tests ---

_BAYESIAN_KWARGS = {
    "rule": "bayesian",
    "weights": {"best": 0.25, "med": 0.50, "worst": 0.25},
    "min_portfolio_worst_return": -1e9,
}


def test_bayesian_pipeline(measure_env):
    orchestrator = _make_orchestrator(measure_env, allocate_kwargs=_BAYESIAN_KWARGS)
    result = orchestrator.run()

    selected = result["allocate_result"]["selected_initiatives"]
    assert len(result["outcome_reports"]) == len(selected)
    assert len(result["scale_results"]) == len(selected)


def test_bayesian_contract_invariants(measure_env):
    orchestrator = _make_orchestrator(measure_env, allocate_kwargs=_BAYESIAN_KWARGS)
    result = orchestrator.run()

    alloc = result["allocate_result"]
    for iid in alloc["selected_initiatives"]:
        assert iid in alloc["predicted_returns"]
        assert iid in alloc["budget_allocated"]
    assert alloc["solver_detail"]["rule"] == "bayesian"

    for report in result["outcome_reports"]:
        assert report["prediction_error"] == pytest.approx(report["actual_return"] - report["predicted_return"])
        assert report["sample_size_scale"] >= report["sample_size_pilot"]
        assert isinstance(report["model_type"], ModelType)


def test_bayesian_determinism(measure_env):
    orchestrator = _make_orchestrator(measure_env, allocate_kwargs=_BAYESIAN_KWARGS)
    result1 = orchestrator.run()
    result2 = orchestrator.run()

    assert result1["allocate_result"] == result2["allocate_result"]


def test_bayesian_empty_budget(measure_env):
    orchestrator = _make_orchestrator(measure_env, budget=1, allocate_kwargs=_BAYESIAN_KWARGS)
    result = orchestrator.run()

    assert result["allocate_result"]["selected_initiatives"] == []
    assert result["scale_results"] == []
    assert result["outcome_reports"] == []
