"""Mock ALLOCATE component with greedy confidence-weighted selection."""

from dataclasses import asdict

from impact_engine_allocate.job_reader import load_initiatives

from impact_engine_orchestrator.components.base import PipelineComponent
from impact_engine_orchestrator.contracts.allocate import AllocateResult


class MockAllocate(PipelineComponent):
    """Select top initiatives by confidence * median return until budget exhausted.

    Uses the allocate package's ``load_initiatives()`` to read from disk,
    then applies a simple greedy heuristic instead of an LP solver.
    """

    def execute(self, event: dict) -> dict:
        """Return a validated AllocateResult dict."""
        data_dir = event["data_dir"]
        config = event["allocate_config"]
        budget = config["budget"]
        costs = config["costs"]

        initiatives = load_initiatives(data_dir, costs)

        # Score by confidence * R_med
        scored = [(i, i["confidence"] * i["R_med"]) for i in initiatives]
        scored.sort(key=lambda x: x[1], reverse=True)

        # Select until budget exhausted
        selected = []
        remaining = budget
        for init, _score in scored:
            if init["cost"] <= remaining:
                selected.append(init["id"])
                remaining -= init["cost"]

        init_by_id = {i["id"]: i for i in initiatives}
        result = AllocateResult(
            selected_initiatives=selected,
            predicted_returns={sid: init_by_id[sid]["R_med"] for sid in selected},
            budget_allocated={sid: init_by_id[sid]["cost"] for sid in selected},
        )
        return asdict(result)
