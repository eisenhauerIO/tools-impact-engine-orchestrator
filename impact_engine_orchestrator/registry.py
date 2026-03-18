"""Component registry mapping short names to class objects."""

from impact_engine_orchestrator.components.allocate.allocate import Allocate
from impact_engine_orchestrator.components.allocate.mock import MockAllocate
from impact_engine_orchestrator.components.base import PipelineComponentProtocol
from impact_engine_orchestrator.components.evaluate.evaluate import Evaluate
from impact_engine_orchestrator.components.measure.measure import Measure

COMPONENT_REGISTRY: dict[str, type[PipelineComponentProtocol]] = {
    "Measure": Measure,
    "Evaluate": Evaluate,
    "Allocate": Allocate,
    "MockAllocate": MockAllocate,
}


def build(stage_config: dict) -> PipelineComponentProtocol:
    """Construct a component from a stage config dict."""
    name = stage_config["component"]
    if name not in COMPONENT_REGISTRY:
        raise KeyError(f"Unknown component {name!r}. Available: {sorted(COMPONENT_REGISTRY)}")
    cls = COMPONENT_REGISTRY[name]
    kwargs = stage_config.get("kwargs", {})
    # Allocate kwargs flow through the config dict at execute time, not constructor.
    if cls is Allocate:
        return cls()
    return cls(**kwargs)
