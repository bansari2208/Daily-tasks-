"""
Day 19 - Statistical Analysis Module.

Provides pure Python statistical utility functions (with math library):
- mean()
- median()
- stdev() [Sample standard deviation, N-1 degrees of freedom]
- min()
- max()
- range() [Max - Min spread]
"""

import math
from typing import List, Dict, Any


def calc_mean(scores: List[float]) -> float:
    """Calculate arithmetic mean of a list of scores."""
    if not scores:
        return 0.0
    return round(sum(scores) / float(len(scores)), 2)


def calc_median(scores: List[float]) -> float:
    """Calculate median of a list of scores."""
    if not scores:
        return 0.0
    sorted_scores = sorted(scores)
    n = len(sorted_scores)
    mid = n // 2
    if n % 2 == 1:
        return round(float(sorted_scores[mid]), 2)
    else:
        return round((sorted_scores[mid - 1] + sorted_scores[mid]) / 2.0, 2)


def calc_stdev(scores: List[float]) -> float:
    """
    Calculate sample standard deviation of a list of scores (N-1 degrees of freedom).
    Returns 0.0 if fewer than 2 data points are provided.
    """
    if not scores or len(scores) < 2:
        return 0.0
    mean_val = sum(scores) / float(len(scores))
    variance = sum((x - mean_val) ** 2 for x in scores) / float(len(scores) - 1)
    return round(math.sqrt(variance), 2)


def calc_min(scores: List[float]) -> float:
    """Calculate minimum score."""
    if not scores:
        return 0.0
    return round(float(min(scores)), 2)


def calc_max(scores: List[float]) -> float:
    """Calculate maximum score."""
    if not scores:
        return 0.0
    return round(float(max(scores)), 2)


def calc_range(scores: List[float]) -> float:
    """Calculate score range (spread = Max - Min)."""
    if not scores:
        return 0.0
    return round(float(max(scores) - min(scores)), 2)


def compute_run_statistics(scores: List[float]) -> Dict[str, Any]:
    """
    Computes complete statistical profile for repeated experiment runs.

    Args:
        scores: List of numerical accuracy percentages across runs.

    Returns:
        Dict containing mean, median, sample_stdev, min, max, range, and stdev_definition note.
    """
    return {
        "scores": scores,
        "mean": calc_mean(scores),
        "median": calc_median(scores),
        "sample_stdev": calc_stdev(scores),
        "min": calc_min(scores),
        "max": calc_max(scores),
        "range": calc_range(scores),
        "stdev_definition": "Sample standard deviation (N-1 degrees of freedom)"
    }
