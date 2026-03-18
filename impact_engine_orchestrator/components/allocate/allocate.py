"""ALLOCATE stage adapter for the orchestrator pipeline."""

import logging
from dataclasses import asdict

from impact_engine_allocate import allocate, load_initiatives
from impact_engine_allocate.models import AllocateResult

from impact_engine_orchestrator.components.base import PipelineComponent

logger = logging.getLogger(__name__)


class AllocateComponent(PipelineComponent):
    """Delegate portfolio selection to the allocate package facade.

    The adapter calls ``allocate(config, data_dir)`` which reads
    ``impact_results.json`` and ``evaluate_result.json`` from each
    initiative's job directory, handles field mapping, and dispatches
    to the configured decision rule.
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
            Serialized ``AllocateResult`` with ``selected_initiatives``,
            ``predicted_returns``, ``budget_allocated``, and
            ``solver_detail``.
        """
        data_dir = event["data_dir"]
        allocate_config = event["allocate_config"]

        solver_result = allocate(allocate_config, data_dir)

        # Read initiatives to build predicted_returns and budget_allocated.
        initiatives = load_initiatives(data_dir, allocate_config["costs"])
        init_by_id = {i["id"]: i for i in initiatives}

        selected_ids = solver_result["selected_initiatives"]
        status = solver_result["status"]

        if status != "Optimal":
            logger.warning(
                "Solver returned non-optimal status: %s — returning empty allocation",
                status,
            )
        else:
            logger.info(
                "Allocation complete: status=%s, selected=%d initiatives",
                status,
                len(selected_ids),
            )

        result = asdict(
            AllocateResult(
                selected_initiatives=selected_ids,
                predicted_returns={sid: init_by_id[sid]["R_med"] for sid in selected_ids},
                budget_allocated={sid: init_by_id[sid]["cost"] for sid in selected_ids},
            )
        )
        result["solver_detail"] = {
            "rule": solver_result["rule"],
            "objective_value": solver_result["objective_value"],
            "total_actual_returns": solver_result["total_actual_returns"],
            "detail": solver_result["detail"],
        }
        return result
