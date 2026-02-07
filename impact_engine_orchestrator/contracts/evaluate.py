"""Contract for EVALUATE stage output."""

from dataclasses import dataclass

from impact_engine_orchestrator.contracts.types import ModelType


@dataclass
class EvaluateResult:
    """Confidence-scored initiative with scenario returns."""

    initiative_id: str
    confidence: float
    cost: float
    return_best: float
    return_median: float
    return_worst: float
    model_type: ModelType
    sample_size: int
