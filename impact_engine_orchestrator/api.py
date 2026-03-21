"""Package-level entry point: run_pipeline()."""

from __future__ import annotations

import logging
from pathlib import Path

from impact_engine_orchestrator.config import load_config
from impact_engine_orchestrator.orchestrator import Orchestrator

logger = logging.getLogger(__name__)


def run_pipeline(fname: str | Path) -> dict:
    """Load a pipeline config file and execute the full pipeline.

    Parameters
    ----------
    fname : str | Path
        Path to the YAML pipeline configuration file.

    Returns
    -------
    dict
        Pipeline results with keys ``pilot_results``, ``evaluate_results``,
        ``allocate_result``, ``scale_results``, and ``outcome_reports``.

    Examples
    --------
    >>> result = run_pipeline("pipeline.yaml")
    >>> print(result["outcome_reports"])
    [...]
    """
    config = load_config(str(fname))
    orchestrator = Orchestrator.from_config(config)
    logger.info("Running pipeline from config: %s", fname)
    return orchestrator.run()
