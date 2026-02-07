"""Pipeline and initiative configuration."""

from dataclasses import dataclass


@dataclass
class InitiativeConfig:
    """Single initiative with its scaling cost."""

    initiative_id: str
    cost_to_scale: float


@dataclass
class PipelineConfig:
    """Problem-level parameters for a single orchestrator run."""

    budget: float
    scale_sample_size: int
    max_workers: int
    initiatives: list[InitiativeConfig]
