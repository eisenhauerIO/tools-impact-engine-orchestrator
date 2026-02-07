"""Mock MEASURE component with deterministic hash-seeded results."""

import hashlib
import random
from dataclasses import asdict

from impact_engine_orchestrator.components.base import PipelineComponent
from impact_engine_orchestrator.contracts.measure import MeasureResult
from impact_engine_orchestrator.contracts.types import ModelType


def _stable_seed(s: str) -> int:
    """Return a deterministic 32-bit seed from a string, stable across processes."""
    return int(hashlib.md5(s.encode()).hexdigest(), 16) % 2**32


class MockMeasure(PipelineComponent):
    """Deterministic fake causal effect estimator seeded by initiative_id."""

    def execute(self, event: dict) -> dict:
        """Return a validated MeasureResult dict."""
        initiative_id = event["initiative_id"]
        seed = _stable_seed(initiative_id)
        rng = random.Random(seed)

        effect = rng.uniform(0.05, 0.25)
        ci_width = effect * rng.uniform(0.3, 0.6)
        sample_size = event.get("sample_size", rng.randint(50, 500))

        # Add controlled noise for scale runs so pilot vs scale
        # produce related but distinct estimates
        noise_rng = random.Random(seed + sample_size)
        noise = noise_rng.gauss(0, 0.01)
        effect += noise

        result = MeasureResult(
            initiative_id=initiative_id,
            effect_estimate=effect,
            ci_lower=effect - ci_width / 2,
            ci_upper=effect + ci_width / 2,
            p_value=rng.uniform(0.001, 0.05),
            sample_size=sample_size,
            model_type=ModelType(rng.choice(["experiment", "quasi-experiment", "time-series", "observational"])),
            diagnostics={"r_squared": rng.uniform(0.6, 0.95)},
        )
        return asdict(result)
