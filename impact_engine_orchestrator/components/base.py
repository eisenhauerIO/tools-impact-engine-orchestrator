"""Abstract base class for pipeline components."""

from abc import ABC, abstractmethod


class PipelineComponent(ABC):
    """Single-initiative processor conforming to the handler interface."""

    @abstractmethod
    def execute(self, event: dict, context=None) -> dict:
        """Process single initiative, return result."""
        pass
