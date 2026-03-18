"""ALLOCATE stage adapter for the orchestrator pipeline."""

import json
import logging
from pathlib import Path

from impact_engine_allocate import allocate_portfolio
from impact_engine_allocate.allocation import ALLOCATE_RESULT_FILENAME

from impact_engine_orchestrator.components.base import PipelineComponent

logger = logging.getLogger(__name__)


class Allocate(PipelineComponent):
    """Delegate portfolio selection to the allocate package facade.

    Calls ``allocate_portfolio(config, data_dir)`` which runs the solver and
    writes ``allocate_result.json`` to ``data_dir``. The adapter reads this
    file back as its output.
    """

    def execute(self, event: dict) -> dict:
        """Run allocation via the allocate package facade.

        Parameters
        ----------
        event : dict
            Must contain ``data_dir`` (path to storage with per-initiative
            subdirectories) and ``allocate_config`` (dict with ``budget``,
            ``costs``, ``rule``, and optional solver kwargs).

        Returns
        -------
        dict
            Dict with ``selected_initiatives``, ``predicted_returns``,
            ``budget_allocated``, and ``solver_detail``.
        """
        data_dir = event["data_dir"]
        allocate_config = event["allocate_config"]

        allocate_portfolio(allocate_config, data_dir)

        result_path = Path(data_dir) / ALLOCATE_RESULT_FILENAME
        result = json.loads(result_path.read_text(encoding="utf-8"))

        status = result.get("solver_detail", {}).get("rule", "unknown")
        selected = result.get("selected_initiatives", [])

        if not selected:
            logger.warning("Allocation selected no initiatives (rule=%s)", status)
        else:
            logger.info("Allocation complete: rule=%s, selected=%d initiatives", status, len(selected))

        return result
