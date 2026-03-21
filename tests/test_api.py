"""Smoke test for the run_pipeline() public API."""

import yaml

from impact_engine_orchestrator import run_pipeline


def test_run_pipeline_returns_expected_shape(measure_env, tmp_path):
    """run_pipeline() loads config from file and returns well-formed results."""
    make_initiative, _make_measure, storage_url = measure_env
    initiative = make_initiative("api-test-init", 10000)

    config_path = tmp_path / "pipeline.yaml"
    config_path.write_text(
        yaml.dump(
            {
                "storage_url": storage_url,
                "budget": 100000,
                "max_workers": 1,
                "allocate": {"rule": "minimax_regret"},
                "initiatives": [
                    {
                        "initiative_id": initiative.initiative_id,
                        "cost_to_scale": initiative.cost_to_scale,
                        "measure_config": initiative.measure_config,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    result = run_pipeline(config_path)

    assert "pilot_results" in result
    assert "evaluate_results" in result
    assert "allocate_result" in result
    assert "scale_results" in result
    assert "outcome_reports" in result
    assert len(result["pilot_results"]) == 1
