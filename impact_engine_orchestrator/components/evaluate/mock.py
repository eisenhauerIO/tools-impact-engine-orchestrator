"""Mock EVALUATE component with confidence scoring by model type."""

import hashlib
import random
from dataclasses import asdict

from impact_engine_orchestrator.components.base import PipelineComponent
from impact_engine_orchestrator.contracts.evaluate import EvaluateResult
from impact_engine_orchestrator.contracts.types import ModelType

CONFIDENCE_MAP = {
    ModelType.EXPERIMENT: (0.85, 1.0),
    ModelType.QUASI_EXPERIMENT: (0.60, 0.84),
    ModelType.TIME_SERIES: (0.40, 0.59),
    ModelType.OBSERVATIONAL: (0.20, 0.39),
}


def _stable_seed(s: str) -> int:
    """Return a deterministic 32-bit seed from a string, stable across processes."""
    return int(hashlib.md5(s.encode()).hexdigest(), 16) % 2**32


class MockEvaluate(PipelineComponent):
    """Deterministic confidence scorer based on model type."""

    def execute(self, event: dict) -> dict:
        """Return a validated EvaluateResult dict."""
        model_type = event["model_type"]
        conf_range = CONFIDENCE_MAP[model_type]
        seed = _stable_seed(event["initiative_id"])
        rng = random.Random(seed)
        confidence = rng.uniform(conf_range[0], conf_range[1])

        result = EvaluateResult(
            initiative_id=event["initiative_id"],
            confidence=confidence,
            cost=event["cost_to_scale"],
            return_best=event["ci_upper"],
            return_median=event["effect_estimate"],
            return_worst=event["ci_lower"],
            model_type=model_type,
            sample_size=event["sample_size"],
        )
        return asdict(result)
