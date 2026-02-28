"""EVALUATE stage adapter for the orchestrator pipeline."""

from dataclasses import asdict

from impact_engine_evaluate.api import evaluate_confidence

from impact_engine_orchestrator.components.base import PipelineComponent


class Evaluate(PipelineComponent):
    """Wraps evaluate_confidence as a pipeline component.

    Parameters
    ----------
    config : dict | str | None
        Backend configuration for the review strategy. Passed through to
        ``evaluate_confidence()``.
    """

    def __init__(self, *, config: dict | str | None = None) -> None:
        self._config = config

    def execute(self, event: dict) -> dict:
        """Evaluate an initiative from its job directory.

        Parameters
        ----------
        event : dict
            Must contain ``"job_dir"``. May contain ``"cost_to_scale"``
            as an override.

        Returns
        -------
        dict
            Keys: ``initiative_id``, ``confidence``, ``confidence_range``,
            ``strategy``, ``report``.
        """
        result = evaluate_confidence(
            config=self._config,
            job_dir=event["job_dir"],
            cost_to_scale=event.get("cost_to_scale"),
        )
        return asdict(result)
