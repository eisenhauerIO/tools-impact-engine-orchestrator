"""MEASURE adapter wrapping impact_engine.evaluate_impact."""

import json
from dataclasses import asdict

from impact_engine import evaluate_impact

from impact_engine_orchestrator.components.base import PipelineComponent
from impact_engine_orchestrator.config import InitiativeConfig
from impact_engine_orchestrator.contracts.measure import MeasureResult
from impact_engine_orchestrator.contracts.types import ModelType


def _resolve_param_key(treatment_var: str, params: dict) -> str:
    """Find the statsmodels coefficient key for a treatment variable.

    Statsmodels encodes categoricals as e.g. ``enriched[T.True]``.
    Returns an exact match first, then falls back to prefix matching.
    """
    if treatment_var in params:
        return treatment_var
    matches = [k for k in params if k.startswith(f"{treatment_var}[")]
    if len(matches) == 1:
        return matches[0]
    raise KeyError(f"Treatment variable {treatment_var!r} not found in params: {list(params.keys())}")


def _extract_estimates(result: dict) -> dict:
    """Extract effect_estimate, ci_lower, ci_upper, p_value, sample_size from model-specific output."""
    model_type = result["model_type"]
    estimates = result["data"]["impact_estimates"]
    summary = result["data"]["model_summary"]

    if model_type == "experiment":
        # OLS regression: first predictor in formula is the treatment variable.
        # statsmodels encodes categoricals as e.g. "enriched[T.True]", so we
        # match by prefix when an exact key isn't found.
        formula = result["data"]["model_params"]["formula"]
        treatment_var = formula.split("~")[1].strip().split("+")[0].strip()
        key = _resolve_param_key(treatment_var, estimates["params"])
        return {
            "effect_estimate": estimates["params"][key],
            "ci_lower": estimates["conf_int"][key][0],
            "ci_upper": estimates["conf_int"][key][1],
            "p_value": estimates["pvalues"][key],
            "sample_size": int(summary["nobs"]),
        }

    if model_type == "synthetic_control":
        return {
            "effect_estimate": estimates["att"],
            "ci_lower": estimates["ci_lower"],
            "ci_upper": estimates["ci_upper"],
            "p_value": None,
            "sample_size": summary["n_post_periods"],
        }

    if model_type == "nearest_neighbour_matching":
        att = estimates["att"]
        att_se = estimates["att_se"]
        return {
            "effect_estimate": att,
            "ci_lower": att - 1.96 * att_se,
            "ci_upper": att + 1.96 * att_se,
            "p_value": None,
            "sample_size": summary["n_observations"],
        }

    if model_type == "interrupted_time_series":
        effect = estimates["intervention_effect"]
        return {
            "effect_estimate": effect,
            "ci_lower": effect,
            "ci_upper": effect,
            "p_value": None,
            "sample_size": summary["n_observations"],
        }

    if model_type == "subclassification":
        effect = estimates["treatment_effect"]
        return {
            "effect_estimate": effect,
            "ci_lower": effect,
            "ci_upper": effect,
            "p_value": None,
            "sample_size": summary["n_observations"],
        }

    if model_type == "metrics_approximation":
        effect = estimates["impact"]
        return {
            "effect_estimate": effect,
            "ci_lower": effect,
            "ci_upper": effect,
            "p_value": None,
            "sample_size": summary["n_products"],
        }

    raise ValueError(f"Unknown model_type: {model_type!r}")


class Measure(PipelineComponent):
    """Adapter that delegates to impact_engine.evaluate_impact."""

    def __init__(self, initiatives: list[InitiativeConfig], storage_url: str):
        self._config_lookup = {i.initiative_id: i.measure_config for i in initiatives}
        self._storage_url = storage_url

    def execute(self, event: dict) -> dict:
        """Run evaluate_impact for one initiative and return a MeasureResult dict."""
        initiative_id = event["initiative_id"]
        config_path = self._config_lookup[initiative_id]

        result_path = evaluate_impact(
            config_path=config_path,
            storage_url=self._storage_url,
            job_id=initiative_id,
        )

        with open(result_path) as f:
            result = json.load(f)

        extracted = _extract_estimates(result)

        measure_result = MeasureResult(
            initiative_id=initiative_id,
            effect_estimate=extracted["effect_estimate"],
            ci_lower=extracted["ci_lower"],
            ci_upper=extracted["ci_upper"],
            p_value=extracted["p_value"] if extracted["p_value"] is not None else 0.0,
            sample_size=extracted["sample_size"],
            model_type=ModelType(result["model_type"]),
            diagnostics=result["data"]["model_summary"],
        )
        return asdict(measure_result)
