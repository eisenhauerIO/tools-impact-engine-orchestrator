"""Shared types used across contracts."""

from enum import Enum


class ModelType(str, Enum):
    """Causal inference model type identifiers."""

    EXPERIMENT = "experiment"
    SYNTHETIC_CONTROL = "synthetic_control"
    NEAREST_NEIGHBOUR_MATCHING = "nearest_neighbour_matching"
    INTERRUPTED_TIME_SERIES = "interrupted_time_series"
    SUBCLASSIFICATION = "subclassification"
    METRICS_APPROXIMATION = "metrics_approximation"


__all__ = ["ModelType"]
