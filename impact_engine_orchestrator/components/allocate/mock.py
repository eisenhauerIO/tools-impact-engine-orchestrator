"""Mock ALLOCATE component with greedy confidence-weighted selection."""

from dataclasses import asdict

from impact_engine_orchestrator.components.base import PipelineComponent
from impact_engine_orchestrator.contracts.allocate import AllocateResult


class MockAllocate(PipelineComponent):
    """Select top initiatives by confidence * return_median until budget exhausted."""

    def execute(self, event: dict, context=None) -> dict:
        """Return a validated AllocateResult dict."""
        initiatives = event["initiatives"]
        budget = event["budget"]

        # Score by confidence * return_median
        scored = [(i, i["confidence"] * i["return_median"]) for i in initiatives]
        scored.sort(key=lambda x: x[1], reverse=True)

        # Select until budget exhausted
        selected = []
        remaining = budget
        for init, score in scored:
            if init["cost"] <= remaining:
                selected.append(init["initiative_id"])
                remaining -= init["cost"]

        result = AllocateResult(
            selected_initiatives=selected,
            predicted_returns={
                i["initiative_id"]: i["return_median"] for i in initiatives if i["initiative_id"] in selected
            },
            budget_allocated={i["initiative_id"]: i["cost"] for i in initiatives if i["initiative_id"] in selected},
        )
        return asdict(result)
