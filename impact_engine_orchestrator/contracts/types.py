"""Shared types used across contracts."""

from enum import Enum


class ModelType(Enum):
    """Causal inference methodology used for measurement."""

    EXPERIMENT = "experiment"
    QUASI_EXPERIMENT = "quasi-experiment"
    TIME_SERIES = "time-series"
    OBSERVATIONAL = "observational"
