"""
Day 19 - Evaluator and Output Parser Module.

Provides robust parsing of model responses and accurate scoring of predictions against ground truth labels.
"""

import re
import json
import logging
from typing import Dict, Any, List, Tuple

logger = logging.getLogger(__name__)

VALID_CATEGORIES = ["Billing", "Technical", "Account", "General"]


def parse_category_from_output(output_text: str) -> str:
    """
    Safely parses predicted category from raw text or JSON response.

    Args:
        output_text: Model output string.

    Returns:
        One of ['Billing', 'Technical', 'Account', 'General'] or 'UNPARSED'.
    """
    if not output_text or not isinstance(output_text, str):
        return "UNPARSED"

    clean_text = output_text.strip()

    # 1. Try parsing JSON format first
    try:
        data = json.loads(clean_text)
        if isinstance(data, dict) and "category" in data:
            cat = str(data["category"]).strip().capitalize()
            if cat in VALID_CATEGORIES:
                return cat
    except Exception:
        pass

    # 2. Look for JSON block in markdown backticks
    json_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", clean_text, re.DOTALL)
    if json_match:
        try:
            data = json.loads(json_match.group(1))
            if isinstance(data, dict) and "category" in data:
                cat = str(data["category"]).strip().capitalize()
                if cat in VALID_CATEGORIES:
                    return cat
        except Exception:
            pass

    # 3. Regex fallback search for category names
    for cat in VALID_CATEGORIES:
        if re.search(rf"\b{cat}\b", clean_text, re.IGNORECASE):
            return cat

    return "UNPARSED"


def evaluate_prediction(item: Dict[str, Any], raw_output: str) -> Dict[str, Any]:
    """
    Evaluates a single ticket prediction against expected ground truth category.

    Args:
        item: Ticket item dict containing 'id' and 'expected_category'.
        raw_output: Model text output string.

    Returns:
        Result dictionary containing item metadata, expected, predicted, and match boolean.
    """
    expected = item.get("expected_category", "")
    predicted = parse_category_from_output(raw_output)
    is_correct = expected.lower() == predicted.lower()

    return {
        "item_id": item.get("id"),
        "expected_category": expected,
        "predicted_category": predicted,
        "is_correct": is_correct,
        "raw_output": raw_output
    }


def evaluate_batch(
    dataset: List[Dict[str, Any]],
    raw_outputs: List[str]
) -> Dict[str, Any]:
    """
    Evaluates a full dataset batch against raw outputs.

    Args:
        dataset: List of evaluation ticket items.
        raw_outputs: Corresponding list of model output strings.

    Returns:
        Structured evaluation batch summary with total count, correct count, accuracy, and items detail.
    """
    if len(dataset) != len(raw_outputs):
        raise ValueError(f"Dataset length ({len(dataset)}) mismatch with outputs length ({len(raw_outputs)})")

    item_results = []
    correct_count = 0

    for item, out in zip(dataset, raw_outputs):
        res = evaluate_prediction(item, out)
        item_results.append(res)
        if res["is_correct"]:
            correct_count += 1

    total = len(dataset)
    accuracy = round((correct_count / total) * 100.0, 2) if total > 0 else 0.0

    return {
        "total_items": total,
        "correct_count": correct_count,
        "incorrect_count": total - correct_count,
        "accuracy_percentage": accuracy,
        "item_results": item_results
    }
