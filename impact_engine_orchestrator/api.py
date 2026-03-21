"""Package-level entry point: run_pipeline()."""

from __future__ import annotations

import logging
from pathlib import Path

from impact_engine_orchestrator.config import load_config
from impact_engine_orchestrator.contracts.pipeline import PipelineResult
from impact_engine_orchestrator.orchestrator import Orchestrator

logger = logging.getLogger(__name__)


def run_pipeline(fname: str | Path) -> PipelineResult:
    """Load a pipeline config file and execute the full pipeline.

    Parameters
    ----------
    fname : str | Path
        Path to the YAML pipeline configuration file.

    Returns
    -------
    PipelineResult
        Typed pipeline result with ``outcome_reports`` as the primary
        user-facing field, plus stage-level detail in ``pilot_results``,
        ``evaluate_results``, ``allocate_result``, and ``scale_results``.

    Examples
    --------
    >>> result = run_pipeline("pipeline.yaml")
    >>> print(result.outcome_reports)
    [...]
    """
    config = load_config(str(fname))
    orchestrator = Orchestrator.from_config(config)
    logger.info("Running pipeline from config: %s", fname)
    return orchestrator.run()
