"""Component registry mapping short names to class objects."""

from impact_engine_orchestrator.components.allocate.allocate import AllocateComponent
from impact_engine_orchestrator.components.allocate.mock import MockAllocate
from impact_engine_orchestrator.components.base import PipelineComponentProtocol
from impact_engine_orchestrator.components.evaluate.evaluate import Evaluate
from impact_engine_orchestrator.components.measure.measure import Measure
from impact_engine_orchestrator.config import StageConfig

COMPONENT_REGISTRY: dict[str, type[PipelineComponentProtocol]] = {
    "Measure": Measure,
    "Evaluate": Evaluate,
    "MinimaxRegretAllocate": AllocateComponent,  # key preserved for config compatibility
    "MockAllocate": MockAllocate,
}


def build(stage_config: StageConfig) -> PipelineComponentProtocol:
    """Construct a component from a StageConfig."""
    name = stage_config.component
    if name not in COMPONENT_REGISTRY:
        raise KeyError(f"Unknown component {name!r}. Available: {sorted(COMPONENT_REGISTRY)}")
    cls = COMPONENT_REGISTRY[name]
    return cls(**stage_config.kwargs)
