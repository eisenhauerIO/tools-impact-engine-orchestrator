"""ALLOCATE stage adapter for the orchestrator pipeline."""

import logging
from collections.abc import Callable
from dataclasses import asdict
from typing import Any

from impact_engine_allocate.allocation import (
    AllocationRule,
    MinimaxRegretAllocation,
    calculate_gamma,
    empty_rule_result,
    preprocess,
)
from impact_engine_allocate.models import AllocateResult

from impact_engine_orchestrator.components.base import PipelineComponent

logger = logging.getLogger(__name__)


_FIELD_MAP_IN: dict[str, str] = {
    "initiative_id": "id",
    "return_best": "R_best",
    "return_median": "R_med",
    "return_worst": "R_worst",
}


def _to_solver_format(initiative: dict[str, Any]) -> dict[str, Any]:
    """Map an orchestrator initiative dict to allocation field names.

    Parameters
    ----------
    initiative : dict[str, Any]
        Initiative dict with orchestrator field names.

    Returns
    -------
    dict[str, Any]
        Initiative dict with allocation field names.
    """
    return {_FIELD_MAP_IN.get(key, key): value for key, value in initiative.items()}


class AllocateComponent(PipelineComponent):
    """Select initiatives via a pluggable decision rule.

    Handles field mapping and preprocessing (confidence filtering,
    effective return computation), then delegates portfolio selection
    to the configured rule.

    Parameters
    ----------
    solver : AllocationRule, optional
        Decision rule to use. Defaults to :class:`MinimaxRegretAllocation`.
    min_confidence_threshold : float
        Initiatives below this confidence are excluded before optimization.
    min_portfolio_worst_return : float
        Minimum aggregate worst-case return constraint.
    confidence_penalty_func : Callable[[float], float], optional
        Maps confidence to penalty factor gamma. Default: ``1 - confidence``.
    """

    def __init__(
        self,
        solver: AllocationRule | None = None,
        min_confidence_threshold: float = 0.0,
        min_portfolio_worst_return: float = 0.0,
        confidence_penalty_func: Callable[[float], float] = calculate_gamma,
    ) -> None:
        self._solver = solver or MinimaxRegretAllocation()
        self.min_confidence_threshold = min_confidence_threshold
        self.min_portfolio_worst_return = min_portfolio_worst_return
        self._confidence_penalty_func = confidence_penalty_func

    def execute(self, event: dict) -> dict:
        """Run allocation and return an ``AllocateResult`` dict with solver detail.

        Parameters
        ----------
        event : dict
            Must contain ``initiatives`` (list of dicts with orchestrator
            field names) and ``budget`` (float).

        Returns
        -------
        dict
            Serialized ``AllocateResult`` with ``selected_initiatives``,
            ``predicted_returns``, ``budget_allocated``, and
            ``solver_detail``.
        """
        if "initiatives" not in event or "budget" not in event:
            raise ValueError("event must contain 'initiatives' and 'budget'")
        initiatives = event["initiatives"]
        budget = event["budget"]

        solver_initiatives = [_to_solver_format(i) for i in initiatives]
        id_to_initiative = {i["id"]: i for i in solver_initiatives}

        processed = preprocess(
            solver_initiatives,
            self.min_confidence_threshold,
            self._confidence_penalty_func,
        )

        if not processed:
            solver_result = empty_rule_result("No Eligible Initiatives", "none")
        else:
            solver_result = self._solver(processed, budget, self.min_portfolio_worst_return)

        status = solver_result["status"]
        selected_ids = solver_result["selected_initiatives"]

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
                predicted_returns={sid: id_to_initiative[sid]["R_med"] for sid in selected_ids},
                budget_allocated={sid: id_to_initiative[sid]["cost"] for sid in selected_ids},
            )
        )
        result["solver_detail"] = {
            "rule": solver_result["rule"],
            "objective_value": solver_result["objective_value"],
            "total_actual_returns": solver_result["total_actual_returns"],
            "detail": solver_result["detail"],
        }
        return result
