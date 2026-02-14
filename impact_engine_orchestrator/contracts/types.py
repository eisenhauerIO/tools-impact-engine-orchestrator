"""Shared types used across contracts."""

from enum import Enum


class ModelType(Enum):
    """Causal inference methodology used for measurement."""

    EXPERIMENT = "experiment"
    QUASI_EXPERIMENT = "quasi-experiment"
    TIME_SERIES = "time-series"
    OBSERVATIONAL = "observational"
    INTERRUPTED_TIME_SERIES = "interrupted_time_series"
    SYNTHETIC_CONTROL = "synthetic_control"
    NEAREST_NEIGHBOUR_MATCHING = "nearest_neighbour_matching"
    SUBCLASSIFICATION = "subclassification"
    METRICS_APPROXIMATION = "metrics_approximation"
