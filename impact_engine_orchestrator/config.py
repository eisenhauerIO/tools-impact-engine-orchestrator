"""Pipeline and initiative configuration."""

import dataclasses
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class InitiativeConfig:
    """Single initiative with its scaling cost."""

    initiative_id: str
    cost_to_scale: float
    measure_config: str = ""
    evaluate_strategy: str = "score"


@dataclass
class StageConfig:
    """Parsed stage configuration (component name + constructor kwargs)."""

    component: str
    kwargs: dict = field(default_factory=dict)


@dataclass
class PipelineConfig:
    """Problem-level parameters for a single orchestrator run."""

    budget: float
    scale_sample_size: int
    initiatives: list[InitiativeConfig]
    max_workers: int = 4
    measure_stage: StageConfig | None = None
    evaluate_stage: StageConfig | None = None
    allocate_stage: StageConfig | None = None

    def __post_init__(self):
        """Validate configuration invariants."""
        if self.budget <= 0:
            raise ValueError(f"budget must be positive, got {self.budget}")
        if self.scale_sample_size <= 0:
            raise ValueError(f"scale_sample_size must be positive, got {self.scale_sample_size}")
        if len(self.initiatives) == 0:
            raise ValueError("initiatives must not be empty")
        if self.max_workers <= 0:
            raise ValueError(f"max_workers must be positive, got {self.max_workers}")


def load_config(path: str) -> dict[str, Any]:
    """Load pipeline configuration from a YAML file.

    The YAML must specify ``storage_url`` (where measure writes results) and an
    ``allocate`` block with the decision rule.  Measure and Evaluate components
    are always the canonical implementations; only Allocate parameters vary.
    """
    config_dir = Path(path).parent
    with open(path) as f:
        raw = yaml.safe_load(f)

    storage_url = raw["storage_url"]
    measure_stage = StageConfig(component="Measure", kwargs={"storage_url": storage_url})
    evaluate_stage = StageConfig(component="Evaluate")
    allocate_stage = StageConfig(component="Allocate", kwargs=dict(raw["allocate"]))

    # Resolve initiative measure_config paths relative to orchestrator YAML
    initiatives = []
    for i in raw["initiatives"]:
        ic = InitiativeConfig(**i)
        if ic.measure_config:
            ic.measure_config = str(config_dir / ic.measure_config)
        initiatives.append(ic)

    return dataclasses.asdict(
        PipelineConfig(
            budget=raw["budget"],
            scale_sample_size=raw.get("scale_sample_size", 5000),
            max_workers=raw.get("max_workers", 4),
            initiatives=initiatives,
            measure_stage=measure_stage,
            evaluate_stage=evaluate_stage,
            allocate_stage=allocate_stage,
        )
    )
