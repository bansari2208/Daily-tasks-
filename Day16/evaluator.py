"""
Day 16: Evaluator module for Expense Claim Review.
Compares predicted claim results against ground-truth expected results.
Calculates verdict_score, breach_score, overall_score separately.
Also computes verdict accuracy, breach accuracy, overall accuracy,
hard-case verdict accuracy, and hard-case overall accuracy.
"""

from typing import Dict, Any, List


def normalize_breach(breach_str: str) -> str:
    """
    Normalizes a breach text description or standard key into a standardized breach identifier.
    """
    s = str(breach_str).lower().strip()
    if "arithmetic" in s:
        return "arithmetic_discrepancy"
    if "meal" in s:
        return "meal_daily_limit"
    if "business" in s or "first class" in s or "non-economy" in s or "travel_class_invalid" in s:
        return "travel_class_invalid"
    if "15,000" in s or "15000" in s or "travel limit" in s or "travel_limit_exceeded" in s:
        return "travel_limit_exceeded"
    if "receipt" in s or "5,000" in s or "5000" in s or "missing_receipt" in s:
        return "missing_receipt"
    if "30 days" in s or "older than" in s or "expense_date_expired" in s:
        return "expense_date_expired"
    if "currency" in s or "currencies" in s or "mixed_currencies" in s:
        return "mixed_currencies"
    if "50,000" in s or "50000" in s or "total_claim_cap_exceeded" in s or "cap exceeded" in s:
        return "total_claim_cap_exceeded"
    return s


def evaluate_single_result(predicted: Dict[str, Any], claim: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluates a single prediction dictionary against a claim's expected ground truth.
    Checks verdict correctness and breach-list correctness separately.
    """
    exp_verdict = str(claim.get("expected_verdict") or claim.get("expected", {}).get("verdict", "")).strip().upper()
    pred_verdict = str(predicted.get("verdict", "")).strip().upper()

    verdict_score = 1 if pred_verdict == exp_verdict else 0

    exp_breaches_raw = claim.get("expected_breaches") or claim.get("expected", {}).get("breaches", [])
    pred_breaches_raw = predicted.get("breaches", [])

    norm_exp = set(normalize_breach(b) for b in exp_breaches_raw)
    norm_pred = set(normalize_breach(b) for b in pred_breaches_raw)

    breach_score = 1 if norm_exp == norm_pred else 0
    overall_score = 1 if (verdict_score == 1 and breach_score == 1) else 0

    return {
        "verdict_score": verdict_score,
        "breach_score": breach_score,
        "overall_score": overall_score,
        "verdict_correct": verdict_score == 1,
        "breach_correct": breach_score == 1,
        "overall_pass": overall_score == 1,
        "pred_verdict": pred_verdict,
        "exp_verdict": exp_verdict,
        "pred_breaches": list(norm_pred),
        "exp_breaches": list(norm_exp)
    }


def evaluate_batch(predictions: List[Dict[str, Any]], evaluation_set: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Evaluates a batch of predictions against the evaluation set.
    Returns overall and hard-case specific accuracy metrics.
    """
    total = len(evaluation_set)
    verdict_correct_count = 0
    breach_correct_count = 0
    overall_pass_count = 0

    hard_case_total = 0
    hard_case_verdict_correct = 0
    hard_case_overall_correct = 0

    details = []

    for pred, claim in zip(predictions, evaluation_set):
        res = evaluate_single_result(pred, claim)
        res["claim_id"] = claim.get("claim_id") or claim.get("id")
        res["hard_case"] = claim.get("hard_case", False)
        res["hard_case_type"] = claim.get("hard_case_type")
        details.append(res)

        if res["verdict_score"] == 1:
            verdict_correct_count += 1
        if res["breach_score"] == 1:
            breach_correct_count += 1
        if res["overall_score"] == 1:
            overall_pass_count += 1

        if claim.get("hard_case", False):
            hard_case_total += 1
            if res["verdict_score"] == 1:
                hard_case_verdict_correct += 1
            if res["overall_score"] == 1:
                hard_case_overall_correct += 1

    verdict_acc = round(verdict_correct_count / total, 4) if total > 0 else 0.0
    breach_acc = round(breach_correct_count / total, 4) if total > 0 else 0.0
    overall_acc = round(overall_pass_count / total, 4) if total > 0 else 0.0

    hard_verdict_acc = round(hard_case_verdict_correct / hard_case_total, 4) if hard_case_total > 0 else 0.0
    hard_overall_acc = round(hard_case_overall_correct / hard_case_total, 4) if hard_case_total > 0 else 0.0

    return {
        "total_claims": total,
        "verdict_accuracy": verdict_acc,
        "breach_accuracy": breach_acc,
        "overall_accuracy": overall_acc,
        "hard_case_verdict_accuracy": hard_verdict_acc,
        "hard_case_overall_accuracy": hard_overall_acc,
        "verdict_correct_count": verdict_correct_count,
        "breach_correct_count": breach_correct_count,
        "overall_pass_count": overall_pass_count,
        "hard_case_total": hard_case_total,
        "hard_case_verdict_correct": hard_case_verdict_correct,
        "hard_case_overall_correct": hard_case_overall_correct,
        "details": details
    }
