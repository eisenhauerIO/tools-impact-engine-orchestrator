"""Contract for EVALUATE stage output."""

from dataclasses import dataclass

from impact_engine_orchestrator.contracts.types import ModelType


@dataclass
class EvaluateResult:
    """Confidence-scored initiative with scenario returns."""

    initiative_id: str
    confidence: float
    cost: float
    R_best: float
    R_med: float
    R_worst: float
    model_type: ModelType
    sample_size: int
