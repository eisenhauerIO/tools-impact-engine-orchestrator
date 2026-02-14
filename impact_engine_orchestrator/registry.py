"""Component registry mapping short names to class objects."""

from impact_engine_evaluate import Evaluate
from portfolio_allocation import MinimaxRegretAllocate

from impact_engine_orchestrator.components.allocate.mock import MockAllocate
from impact_engine_orchestrator.components.base import PipelineComponent
from impact_engine_orchestrator.components.measure.measure import Measure
from impact_engine_orchestrator.config import StageConfig

COMPONENT_REGISTRY: dict[str, type[PipelineComponent]] = {
    "Measure": Measure,
    "MockAllocate": MockAllocate,
    "Evaluate": Evaluate,
    "MinimaxRegretAllocate": MinimaxRegretAllocate,
}


def build(stage_config: StageConfig) -> PipelineComponent:
    """Construct a component from a StageConfig."""
    name = stage_config.component
    if name not in COMPONENT_REGISTRY:
        raise KeyError(f"Unknown component {name!r}. Available: {sorted(COMPONENT_REGISTRY)}")
    cls = COMPONENT_REGISTRY[name]
    return cls(**stage_config.kwargs)
