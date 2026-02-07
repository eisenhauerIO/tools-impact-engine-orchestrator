"""Contract for MEASURE stage output."""

from dataclasses import dataclass

from impact_engine_orchestrator.contracts.types import ModelType


@dataclass
class MeasureResult:
    """Causal effect estimate with confidence interval and diagnostics."""

    initiative_id: str
    effect_estimate: float
    ci_lower: float
    ci_upper: float
    p_value: float
    sample_size: int
    model_type: ModelType
    diagnostics: dict

    def __post_init__(self):
        """Validate contract invariants."""
        assert self.ci_lower <= self.effect_estimate <= self.ci_upper
        assert self.sample_size >= 30
