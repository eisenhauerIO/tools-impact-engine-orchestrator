"""Mock ALLOCATE component with greedy confidence-weighted selection."""

from impact_engine_orchestrator.components.base import PipelineComponent


class MockAllocate(PipelineComponent):
    """Select top initiatives by confidence * R_med until budget exhausted."""

    def execute(self, event: dict, context=None) -> dict:
        """Return a synthetic AllocateResult dict."""
        initiatives = event["initiatives"]
        budget = event["budget"]

        # Score by confidence * R_med
        scored = [(i, i["confidence"] * i["R_med"]) for i in initiatives]
        scored.sort(key=lambda x: x[1], reverse=True)

        # Select until budget exhausted
        selected = []
        remaining = budget
        for init, score in scored:
            if init["cost"] <= remaining:
                selected.append(init["initiative_id"])
                remaining -= init["cost"]

        return {
            "selected_initiatives": selected,
            "predicted_returns": {
                i["initiative_id"]: i["R_med"] for i in initiatives if i["initiative_id"] in selected
            },
            "budget_allocated": {i["initiative_id"]: i["cost"] for i in initiatives if i["initiative_id"] in selected},
        }
