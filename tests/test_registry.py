"""Tests for the component registry and from_config round-trip."""

import pytest
import yaml

from impact_engine_orchestrator.config import load_config
from impact_engine_orchestrator.orchestrator import Orchestrator
from impact_engine_orchestrator.registry import build


def test_build_unknown_component():
    """Unknown component name raises a clear error."""
    with pytest.raises(KeyError, match="Unknown component 'DoesNotExist'"):
        build({"component": "DoesNotExist"})


def test_build_measure():
    """Registry builds Measure with kwargs."""
    from impact_engine_orchestrator.components.measure.measure import Measure

    component = build({"component": "Measure", "kwargs": {"storage_url": "/tmp/test"}})
    assert isinstance(component, Measure)


def test_build_evaluate():
    """Registry builds Evaluate."""
    from impact_engine_orchestrator.components.evaluate.evaluate import Evaluate

    component = build({"component": "Evaluate"})
    assert isinstance(component, Evaluate)


def test_build_mock_allocate():
    """Registry builds MockAllocate."""
    from impact_engine_orchestrator.components.allocate.mock import MockAllocate

    component = build({"component": "MockAllocate"})
    assert isinstance(component, MockAllocate)


def test_build_allocate():
    """Registry builds stateless Allocate."""
    from impact_engine_orchestrator.components.allocate.allocate import Allocate

    component = build({"component": "Allocate"})
    assert isinstance(component, Allocate)


def test_from_config_round_trip(tmp_path):
    """Load config → build orchestrator → verify component types."""
    from impact_engine_orchestrator.components.allocate.allocate import Allocate

    orchestrator_cfg = tmp_path / "config.yaml"
    orchestrator_cfg.write_text(
        yaml.dump(
            {
                "budget": 100000,
                "scale_sample_size": 5000,
                "storage_url": "./data",
                "allocate": {"rule": "minimax_regret"},
                "initiatives": [
                    {"initiative_id": "test-1", "cost_to_scale": 10000, "measure_config": "dummy.yaml"},
                ],
            }
        )
    )

    config = load_config(str(orchestrator_cfg))
    orchestrator = Orchestrator.from_config(config)

    assert isinstance(orchestrator.allocate, Allocate)
    assert isinstance(orchestrator, Orchestrator)


def test_from_config_with_real_components(tmp_path):
    """Load config with Measure + Evaluate + Allocate → verify types."""
    from impact_engine_orchestrator.components.allocate.allocate import Allocate
    from impact_engine_orchestrator.components.evaluate.evaluate import Evaluate
    from impact_engine_orchestrator.components.measure.measure import Measure

    orchestrator_cfg = tmp_path / "config.yaml"
    orchestrator_cfg.write_text(
        yaml.dump(
            {
                "budget": 50000,
                "scale_sample_size": 3000,
                "storage_url": "./data",
                "allocate": {"rule": "minimax_regret"},
                "initiatives": [
                    {"initiative_id": "test-1", "cost_to_scale": 10000, "measure_config": "dummy.yaml"},
                ],
            }
        )
    )

    config = load_config(str(orchestrator_cfg))
    orchestrator = Orchestrator.from_config(config)

    assert isinstance(orchestrator.measure, Measure)
    assert isinstance(orchestrator.evaluate, Evaluate)
    assert isinstance(orchestrator.allocate, Allocate)
