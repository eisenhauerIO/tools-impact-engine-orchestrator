"""Data contracts shared across pipeline stages."""

from impact_engine_orchestrator.contracts.pipeline import PipelineResult
from impact_engine_orchestrator.contracts.report import OutcomeReport

__all__ = [
    "OutcomeReport",
    "PipelineResult",
]
