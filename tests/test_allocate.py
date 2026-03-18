"""Integration tests for the Allocate adapter."""

import logging

import pytest

from impact_engine_orchestrator.components.allocate.allocate import Allocate

ALLOCATE_RESULT_KEYS = {"selected_initiatives", "predicted_returns", "budget_allocated", "solver_detail"}


@pytest.fixture()
def allocate_event(allocate_data_dir):
    """Build an allocate event from the disk-based fixture."""
    data_dir, costs, _initiatives = allocate_data_dir
    return {
        "data_dir": data_dir,
        "allocate_config": {
            "budget": 10,
            "costs": costs,
            "rule": "minimax_regret",
            "min_confidence_threshold": 0.0,
            "min_portfolio_worst_return": 0.0,
        },
    }


class TestAdapterContract:
    def test_result_keys(self, allocate_event):
        adapter = Allocate()
        result = adapter.execute(allocate_event)
        assert set(result.keys()) == ALLOCATE_RESULT_KEYS

    def test_selected_subset_of_input(self, allocate_event):
        adapter = Allocate()
        result = adapter.execute(allocate_event)
        input_ids = set(allocate_event["allocate_config"]["costs"].keys())
        assert set(result["selected_initiatives"]).issubset(input_ids)

    def test_budget_respected(self, allocate_event):
        adapter = Allocate()
        result = adapter.execute(allocate_event)
        total_allocated = sum(result["budget_allocated"].values())
        assert total_allocated <= allocate_event["allocate_config"]["budget"]

    def test_predicted_returns_for_selected(self, allocate_event):
        adapter = Allocate()
        result = adapter.execute(allocate_event)
        assert set(result["predicted_returns"].keys()) == set(result["selected_initiatives"])

    def test_budget_allocated_for_selected(self, allocate_event):
        adapter = Allocate()
        result = adapter.execute(allocate_event)
        assert set(result["budget_allocated"].keys()) == set(result["selected_initiatives"])

    def test_solver_detail_present(self, allocate_event):
        adapter = Allocate()
        result = adapter.execute(allocate_event)
        detail = result["solver_detail"]
        assert "rule" in detail
        assert "objective_value" in detail
        assert "total_actual_returns" in detail
        assert "detail" in detail


class TestAdapterDeterminism:
    def test_repeated_calls_identical(self, allocate_event):
        adapter = Allocate()
        r1 = adapter.execute(allocate_event)
        r2 = adapter.execute(allocate_event)
        assert r1 == r2


class TestAdapterEdgeCases:
    def test_budget_too_small(self, allocate_event):
        allocate_event["allocate_config"]["budget"] = 0.5
        adapter = Allocate()
        result = adapter.execute(allocate_event)
        assert result["selected_initiatives"] == []

    def test_single_initiative(self, allocate_data_dir, tmp_path):
        data_dir, costs, _initiatives = allocate_data_dir
        # Create a separate data_dir with only initiative A
        single_dir = tmp_path / "single"
        import shutil

        shutil.copytree(f"{data_dir}/A", str(single_dir / "A"))
        event = {
            "data_dir": str(single_dir),
            "allocate_config": {
                "budget": 10,
                "costs": {"A": costs["A"]},
                "rule": "minimax_regret",
                "min_confidence_threshold": 0.0,
                "min_portfolio_worst_return": 0.0,
            },
        }
        adapter = Allocate()
        result = adapter.execute(event)
        assert result["selected_initiatives"] == ["A"]

    def test_all_filtered_by_confidence(self, allocate_event):
        allocate_event["allocate_config"]["min_confidence_threshold"] = 1.0
        adapter = Allocate()
        result = adapter.execute(allocate_event)
        assert result["selected_initiatives"] == []

    def test_non_optimal_logs_warning(self, allocate_event, caplog):
        allocate_event["allocate_config"]["min_confidence_threshold"] = 1.0
        adapter = Allocate()
        with caplog.at_level(logging.WARNING, logger="impact_engine_orchestrator.components.allocate.allocate"):
            adapter.execute(allocate_event)
        assert "non-optimal status" in caplog.text.lower()


class TestAdapterFieldMapping:
    def test_roundtrip_id_preservation(self, allocate_event, allocate_data_dir):
        _, _, initiatives = allocate_data_dir
        adapter = Allocate()
        result = adapter.execute(allocate_event)
        input_ids = {i["id"] for i in initiatives}
        for sid in result["selected_initiatives"]:
            assert sid in input_ids

    def test_predicted_returns_match_input(self, allocate_event, allocate_data_dir):
        _, _, initiatives = allocate_data_dir
        adapter = Allocate()
        result = adapter.execute(allocate_event)
        id_to_median = {i["id"]: i["R_med"] for i in initiatives}
        for sid, ret in result["predicted_returns"].items():
            assert ret == pytest.approx(id_to_median[sid])

    def test_budget_allocated_matches_cost(self, allocate_event, allocate_data_dir):
        _, _, initiatives = allocate_data_dir
        adapter = Allocate()
        result = adapter.execute(allocate_event)
        id_to_cost = {i["id"]: i["cost"] for i in initiatives}
        for sid, cost in result["budget_allocated"].items():
            assert cost == id_to_cost[sid]


class TestAdapterSolverSelection:
    def test_minimax_regret_rule_identifier(self, allocate_event):
        adapter = Allocate()
        result = adapter.execute(allocate_event)
        assert result["solver_detail"]["rule"] == "minimax_regret"

    def test_bayesian_via_config(self, allocate_event):
        allocate_event["allocate_config"]["rule"] = "bayesian"
        allocate_event["allocate_config"]["weights"] = {"best": 0.25, "med": 0.50, "worst": 0.25}
        adapter = Allocate()
        result = adapter.execute(allocate_event)
        assert set(result.keys()) == ALLOCATE_RESULT_KEYS
        assert result["solver_detail"]["rule"] == "bayesian"
        assert "weights" in result["solver_detail"]["detail"]

    def test_laplace_as_equal_weights(self, allocate_event):
        allocate_event["allocate_config"]["rule"] = "bayesian"
        allocate_event["allocate_config"]["weights"] = {"best": 1 / 3, "med": 1 / 3, "worst": 1 / 3}
        adapter = Allocate()
        result = adapter.execute(allocate_event)
        assert result["solver_detail"]["rule"] == "bayesian"
        assert len(result["selected_initiatives"]) > 0
