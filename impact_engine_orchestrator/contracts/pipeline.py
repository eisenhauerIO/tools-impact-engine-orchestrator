"""Contract for the full pipeline result."""

from dataclasses import dataclass

from impact_engine_orchestrator.contracts.report import OutcomeReport


@dataclass
class PipelineResult:
    """Full result of a pipeline run.

    Parameters
    ----------
    outcome_reports : list[OutcomeReport]
        Per-initiative comparison of pilot prediction vs scale actual.
        Primary user-facing output.
    pilot_results : list[dict]
        Raw MEASURE stage outputs for the pilot run, one dict per initiative.
    evaluate_results : list[dict]
        Raw EVALUATE stage outputs, one dict per initiative.
    allocate_result : dict
        Raw ALLOCATE stage output containing selected initiatives and budget allocation.
    scale_results : list[dict]
        Raw MEASURE stage outputs for the scale run on selected initiatives.
    """

    outcome_reports: list[OutcomeReport]
    pilot_results: list[dict]
    evaluate_results: list[dict]
    allocate_result: dict
    scale_results: list[dict]
