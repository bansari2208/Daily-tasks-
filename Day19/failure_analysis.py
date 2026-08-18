"""
Day 19 - Failure Analysis Module.

Identifies misclassified evaluation items, categorizes failures, determines the largest failure class,
and verifies failure reduction before vs. after targeted prompt optimization.
"""

from typing import Dict, Any, List, Tuple

VALID_CATEGORIES = ["Billing", "Technical", "Account", "General"]


def analyze_failures(item_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyzes item evaluation results, categorizing incorrect predictions by expected category.

    Args:
        item_results: List of item prediction dictionaries.

    Returns:
        Dict containing category failure counts, largest failure class, total failures, and failed items.
    """
    category_failures = {cat: 0 for cat in VALID_CATEGORIES}
    failed_items = []

    for res in item_results:
        if not res["is_correct"]:
            exp_cat = res["expected_category"]
            if exp_cat in category_failures:
                category_failures[exp_cat] += 1
            else:
                category_failures[exp_cat] = 1
            failed_items.append(res)

    total_failures = len(failed_items)

    # Determine largest failure class dynamically
    largest_class = None
    max_count = -1

    # Deterministic tie-breaking by category order
    for cat in VALID_CATEGORIES:
        count = category_failures.get(cat, 0)
        if count > max_count:
            max_count = count
            largest_class = cat

    return {
        "total_failures": total_failures,
        "category_failure_counts": category_failures,
        "largest_failure_class": largest_class,
        "largest_failure_count": max_count,
        "failed_item_details": failed_items
    }


def verify_failure_reduction(before_count: int, after_count: int) -> Tuple[bool, int]:
    """
    Explicitly verifies whether the targeted failure count decreased (After < Before).

    Args:
        before_count: Failure count before optimization.
        after_count: Failure count after optimization.

    Returns:
        Tuple of (is_reduced: bool, count_difference: int).
    """
    diff = before_count - after_count
    is_reduced = after_count < before_count
    return is_reduced, diff
