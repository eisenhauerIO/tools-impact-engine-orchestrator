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

    def __post_init__(self):
        """Validate configuration invariants."""
        assert self.budget > 0, f"budget must be positive, got {self.budget}"
        assert self.scale_sample_size > 0, f"scale_sample_size must be positive, got {self.scale_sample_size}"
        assert len(self.initiatives) > 0, "initiatives must not be empty"
        assert self.max_workers > 0, f"max_workers must be positive, got {self.max_workers}"


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
