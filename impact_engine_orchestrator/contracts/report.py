"""Contract for the final outcome report."""

from dataclasses import dataclass

from impact_engine_orchestrator.contracts.types import ModelType


@dataclass
class OutcomeReport:
    """Comparison of pilot prediction vs scale actual for one initiative."""

    initiative_id: str
    predicted_return: float
    actual_return: float
    prediction_error: float
    sample_size_pilot: int
    sample_size_scale: int
    budget_allocated: float
    confidence_score: float
    model_type: ModelType
