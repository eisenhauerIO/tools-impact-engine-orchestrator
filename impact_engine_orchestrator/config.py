"""Pipeline and initiative configuration."""

from dataclasses import dataclass

import yaml


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
    initiatives: list[InitiativeConfig]
    max_workers: int = 4


def load_config(path: str) -> PipelineConfig:
    """Load a PipelineConfig from a YAML file."""
    with open(path) as f:
        raw = yaml.safe_load(f)
    return PipelineConfig(
        budget=raw["budget"],
        scale_sample_size=raw.get("scale_sample_size", 5000),
        max_workers=raw.get("max_workers", 4),
        initiatives=[InitiativeConfig(**i) for i in raw["initiatives"]],
    )
