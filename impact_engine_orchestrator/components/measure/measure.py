"""MEASURE adapter wrapping impact_engine_measure.measure_impact."""

import json
from dataclasses import asdict
from pathlib import Path

from impact_engine_measure import load_results, measure_impact
from impact_engine_measure.normalize import MEASURE_RESULT_FILENAME

from impact_engine_orchestrator.components.base import PipelineComponent
from impact_engine_orchestrator.contracts.measure import MeasureResult
from impact_engine_orchestrator.contracts.types import ModelType


class Measure(PipelineComponent):
    """Adapter that delegates to impact_engine_measure.measure_impact.

    Reads ``measure_result.json`` (written by the measure package) for
    normalized estimates instead of parsing model-specific output schemas.
    """

    def __init__(self, storage_url: str):
        self._storage_url = storage_url

    def execute(self, event: dict) -> dict:
        """Run measure_impact for one initiative and return a MeasureResult dict."""
        initiative_id = event["initiative_id"]
        config_path = event["measure_config"]
        evaluate_strategy = event.get("evaluate_strategy", "score")

        job_info = measure_impact(
            config_path=config_path,
            storage_url=self._storage_url,
            job_id=initiative_id,
        )

        # Write evaluate_strategy into the manifest so the evaluate stage can read it.
        job_dir = Path(job_info.full_path)
        manifest_path = job_dir / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["evaluate_strategy"] = evaluate_strategy
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

        # Read normalized estimates written by the measure package.
        measure_result_path = job_dir / MEASURE_RESULT_FILENAME
        extracted = json.loads(measure_result_path.read_text(encoding="utf-8"))

        impact_results = load_results(job_info).impact_results

        measure_result = MeasureResult(
            initiative_id=initiative_id,
            effect_estimate=extracted["effect_estimate"],
            ci_lower=extracted["ci_lower"],
            ci_upper=extracted["ci_upper"],
            p_value=extracted["p_value"] if extracted["p_value"] is not None else 0.0,
            sample_size=extracted["sample_size"],
            model_type=ModelType(impact_results["model_type"]),
            diagnostics=impact_results["data"]["model_summary"],
        )
        result_dict = asdict(measure_result)
        result_dict["job_dir"] = str(job_dir)
        return result_dict
