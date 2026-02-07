"""Mock EVALUATE component with confidence scoring by model type."""

import random

from impact_engine_orchestrator.components.base import PipelineComponent

CONFIDENCE_MAP = {
    "experiment": (0.85, 1.0),
    "quasi-experiment": (0.60, 0.84),
    "time-series": (0.40, 0.59),
    "observational": (0.20, 0.39),
}


class MockEvaluate(PipelineComponent):
    """Deterministic confidence scorer based on model type."""

    def execute(self, event: dict, context=None) -> dict:
        """Return a synthetic EvaluateResult dict."""
        model_type = event["model_type"]
        conf_range = CONFIDENCE_MAP[model_type]
        seed = hash(event["initiative_id"]) % 2**32
        rng = random.Random(seed)
        confidence = rng.uniform(conf_range[0], conf_range[1])

        return {
            "initiative_id": event["initiative_id"],
            "confidence": confidence,
            "cost": event["cost_to_scale"],
            "R_best": event["ci_upper"],
            "R_med": event["effect_estimate"],
            "R_worst": event["ci_lower"],
            "model_type": model_type,
            "sample_size": event["sample_size"],
        }
