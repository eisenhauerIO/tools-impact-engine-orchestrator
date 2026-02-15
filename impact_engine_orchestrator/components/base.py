"""Abstract base class and protocol for pipeline components."""

from abc import ABC, abstractmethod
from typing import Protocol


class PipelineComponentProtocol(Protocol):
    """Structural interface for pipeline stage components."""

    def execute(self, event: dict) -> dict:
        """Process event and return result."""
        ...


class PipelineComponent(ABC):
    """Single-initiative processor conforming to the handler interface."""

    @abstractmethod
    def execute(self, event: dict) -> dict:
        """Process single initiative, return result."""
