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
        if not (self.ci_lower <= self.effect_estimate <= self.ci_upper):
            raise ValueError(
                f"effect_estimate {self.effect_estimate} must lie within [{self.ci_lower}, {self.ci_upper}]"
            )
        if self.sample_size < 30:
            raise ValueError(f"sample_size must be >= 30, got {self.sample_size}")
