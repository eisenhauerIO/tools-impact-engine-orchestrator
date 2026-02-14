"""Pipeline and initiative configuration."""

from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class InitiativeConfig:
    """Single initiative with its scaling cost."""

    initiative_id: str
    cost_to_scale: float
    measure_config: str = ""


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
        assert self.budget > 0, f"budget must be positive, got {self.budget}"
        assert self.scale_sample_size > 0, f"scale_sample_size must be positive, got {self.scale_sample_size}"
        assert len(self.initiatives) > 0, "initiatives must not be empty"
        assert self.max_workers > 0, f"max_workers must be positive, got {self.max_workers}"


def _load_stage_config(config_path: str) -> StageConfig:
    """Load a stage config YAML and return a StageConfig."""
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Stage config file not found: {config_path}")
    with open(path) as f:
        raw = yaml.safe_load(f)
    component = raw.pop("component")
    return StageConfig(component=component, kwargs=raw)


def load_config(path: str) -> PipelineConfig:
    """Load a PipelineConfig from a YAML file."""
    config_dir = Path(path).parent
    with open(path) as f:
        raw = yaml.safe_load(f)

    # Load stage configs (resolve paths relative to orchestrator YAML)
    measure_stage = None
    if "measure" in raw and "config" in raw["measure"]:
        measure_stage = _load_stage_config(config_dir / raw["measure"]["config"])

    evaluate_stage = None
    if "evaluate" in raw and "config" in raw["evaluate"]:
        evaluate_stage = _load_stage_config(config_dir / raw["evaluate"]["config"])

    allocate_stage = None
    if "allocate" in raw and "config" in raw["allocate"]:
        allocate_stage = _load_stage_config(config_dir / raw["allocate"]["config"])

    # Resolve initiative measure_config paths relative to orchestrator YAML
    initiatives = []
    for i in raw["initiatives"]:
        ic = InitiativeConfig(**i)
        if ic.measure_config:
            ic.measure_config = str(config_dir / ic.measure_config)
        initiatives.append(ic)

    return PipelineConfig(
        budget=raw["budget"],
        scale_sample_size=raw.get("scale_sample_size", 5000),
        max_workers=raw.get("max_workers", 4),
        initiatives=initiatives,
        measure_stage=measure_stage,
        evaluate_stage=evaluate_stage,
        allocate_stage=allocate_stage,
    )
