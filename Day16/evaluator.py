"""
Day 16: Evaluator module for Expense Claim Review.
Compares predicted claim results against ground-truth expected results.
"""

from typing import Dict, Any, List


def match_breach(expected_breach: str, predicted_breaches: List[str]) -> bool:
    """
    Checks if an expected breach is captured in predicted breaches using concept/keyword matching.
    """
    exp_lower = expected_breach.lower()
    
    keywords = []
    if "arithmetic" in exp_lower:
        keywords.append("arithmetic")
    if "meal" in exp_lower:
        keywords.append("meal")
    if "travel" in exp_lower or "flight" in exp_lower or "business" in exp_lower or "first class" in exp_lower:
        keywords.extend(["travel", "flight", "business", "class", "15,000", "15000", "economy"])
    if "receipt" in exp_lower or "5,000" in exp_lower or "5000" in exp_lower:
        keywords.extend(["receipt", "5,000", "5000", "missing"])
    if "older than 30 days" in exp_lower or "30 days" in exp_lower or "date" in exp_lower:
        keywords.extend(["30", "date", "old", "submitted"])
    if "currency" in exp_lower or "currencies" in exp_lower:
        keywords.extend(["currency", "currencies", "eur", "gbp", "usd", "mixed"])
    if "cap" in exp_lower or "50,000" in exp_lower or "50000" in exp_lower:
        keywords.extend(["50,000", "50000", "cap", "total"])

    for pred in predicted_breaches:
        pred_lower = pred.lower()
        if any(kw in pred_lower for kw in keywords):
            return True
    return False


def evaluate_single_result(predicted: Dict[str, Any], expected: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluates a single prediction dictionary against expected ground truth.
    Checks verdict correctness and breach-list correctness separately.
    """
    pred_verdict = str(predicted.get("verdict", "")).strip().upper()
    exp_verdict = str(expected.get("verdict", "")).strip().upper()

    verdict_correct = (pred_verdict == exp_verdict)

    pred_breaches = predicted.get("breaches", [])
    exp_breaches = expected.get("breaches", [])

    if len(exp_breaches) == 0:
        breach_correct = (len(pred_breaches) == 0)
    else:
        if len(pred_breaches) < len(exp_breaches):
            breach_correct = False
        else:
            matches = [match_breach(eb, pred_breaches) for eb in exp_breaches]
            breach_correct = all(matches)

    overall_pass = verdict_correct and breach_correct

    return {
        "verdict_correct": verdict_correct,
        "breach_correct": breach_correct,
        "overall_pass": overall_pass,
        "pred_verdict": pred_verdict,
        "exp_verdict": exp_verdict,
        "pred_breaches_count": len(pred_breaches),
        "exp_breaches_count": len(exp_breaches)
    }


def evaluate_batch(predictions: List[Dict[str, Any]], evaluation_set: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Evaluates a batch of predictions against the evaluation set.
    """
    total = len(evaluation_set)
    verdict_correct_count = 0
    breach_correct_count = 0
    overall_pass_count = 0

    item_results = []

    for pred, claim in zip(predictions, evaluation_set):
        res = evaluate_single_result(pred, claim["expected"])
        res["claim_id"] = claim["id"]
        res["claim_name"] = claim["name"]
        item_results.append(res)

        if res["verdict_correct"]:
            verdict_correct_count += 1
        if res["breach_correct"]:
            breach_correct_count += 1
        if res["overall_pass"]:
            overall_pass_count += 1

    return {
        "total_claims": total,
        "verdict_accuracy": round(verdict_correct_count / total, 4) if total > 0 else 0.0,
        "breach_accuracy": round(breach_correct_count / total, 4) if total > 0 else 0.0,
        "overall_accuracy": round(overall_pass_count / total, 4) if total > 0 else 0.0,
        "verdict_correct_count": verdict_correct_count,
        "breach_correct_count": breach_correct_count,
        "overall_pass_count": overall_pass_count,
        "details": item_results
    }
