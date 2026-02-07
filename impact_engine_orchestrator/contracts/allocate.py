"""Contract for ALLOCATE stage output."""

from dataclasses import dataclass


@dataclass
class AllocateResult:
    """Portfolio selection with budget allocation."""

    selected_initiatives: list[str]
    predicted_returns: dict[str, float]
    budget_allocated: dict[str, float]
