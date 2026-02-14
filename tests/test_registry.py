"""Tests for the component registry and from_config round-trip."""

import pytest
import yaml

from impact_engine_orchestrator.config import StageConfig, load_config
from impact_engine_orchestrator.orchestrator import Orchestrator
from impact_engine_orchestrator.registry import build


def test_build_unknown_component():
    """Unknown component name raises a clear error."""
    stage = StageConfig(component="DoesNotExist")
    with pytest.raises(KeyError, match="Unknown component 'DoesNotExist'"):
        build(stage)


def test_build_measure():
    """Registry builds Measure with kwargs."""
    from impact_engine_orchestrator.components.measure.measure import Measure

    stage = StageConfig(component="Measure", kwargs={"storage_url": "/tmp/test"})
    component = build(stage)
    assert isinstance(component, Measure)


def test_build_evaluate():
    """Registry builds Evaluate."""
    from impact_engine_evaluate import Evaluate

    stage = StageConfig(component="Evaluate")
    component = build(stage)
    assert isinstance(component, Evaluate)


def test_build_mock_allocate():
    """Registry builds MockAllocate."""
    from impact_engine_orchestrator.components.allocate.mock import MockAllocate

    stage = StageConfig(component="MockAllocate")
    component = build(stage)
    assert isinstance(component, MockAllocate)


def test_build_minimax_regret_allocate():
    """Registry builds MinimaxRegretAllocate."""
    from portfolio_allocation import MinimaxRegretAllocate

    stage = StageConfig(component="MinimaxRegretAllocate")
    component = build(stage)
    assert isinstance(component, MinimaxRegretAllocate)


def test_missing_stage_config_file():
    """Missing stage config file raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError, match="Stage config file not found"):
        from impact_engine_orchestrator.config import _load_stage_config

        _load_stage_config("/nonexistent/path/config.yaml")


def test_from_config_round_trip(tmp_path):
    """Load config → build orchestrator → verify component types."""
    from impact_engine_orchestrator.components.allocate.mock import MockAllocate

    # Create stage config files
    measure_cfg = tmp_path / "measure.yaml"
    measure_cfg.write_text(yaml.dump({"component": "MockAllocate"}))

    evaluate_cfg = tmp_path / "evaluate.yaml"
    evaluate_cfg.write_text(yaml.dump({"component": "Evaluate"}))

    allocate_cfg = tmp_path / "allocate.yaml"
    allocate_cfg.write_text(yaml.dump({"component": "MockAllocate"}))

    # Create orchestrator config
    orchestrator_cfg = tmp_path / "config.yaml"
    orchestrator_cfg.write_text(
        yaml.dump(
            {
                "budget": 100000,
                "scale_sample_size": 5000,
                "measure": {"config": "measure.yaml"},
                "evaluate": {"config": "evaluate.yaml"},
                "allocate": {"config": "allocate.yaml"},
                "initiatives": [
                    {"initiative_id": "test-1", "cost_to_scale": 10000, "measure_config": "dummy.yaml"},
                ],
            }
        )
    )

    config = load_config(str(orchestrator_cfg))
    orchestrator = Orchestrator.from_config(config)

    assert isinstance(orchestrator.allocate, MockAllocate)
    assert isinstance(orchestrator, Orchestrator)


def test_from_config_with_real_components(tmp_path):
    """Load config with Measure + Evaluate + MinimaxRegretAllocate → verify types."""
    from impact_engine_evaluate import Evaluate
    from portfolio_allocation import MinimaxRegretAllocate

    from impact_engine_orchestrator.components.measure.measure import Measure

    measure_cfg = tmp_path / "measure.yaml"
    measure_cfg.write_text(yaml.dump({"component": "Measure", "storage_url": "./data"}))

    evaluate_cfg = tmp_path / "evaluate.yaml"
    evaluate_cfg.write_text(yaml.dump({"component": "Evaluate"}))

    allocate_cfg = tmp_path / "allocate.yaml"
    allocate_cfg.write_text(yaml.dump({"component": "MinimaxRegretAllocate"}))

    orchestrator_cfg = tmp_path / "config.yaml"
    orchestrator_cfg.write_text(
        yaml.dump(
            {
                "budget": 50000,
                "scale_sample_size": 3000,
                "measure": {"config": "measure.yaml"},
                "evaluate": {"config": "evaluate.yaml"},
                "allocate": {"config": "allocate.yaml"},
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
    assert isinstance(orchestrator.allocate, MinimaxRegretAllocate)
