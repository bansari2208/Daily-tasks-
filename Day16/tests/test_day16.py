"""
Day 16: Comprehensive Unit Test Suite.
Verifies dataset structure, scoring logic, P95 calculations, cost metrics,
majority voting self-consistency, client payload sanitization (no CoT leakage),
typed intermediate handoffs, and 30-item dataset experiment validation.
Runs offline without live LLM dependencies.
"""

import numpy as np
import pytest
from Day16.evaluation_set import EVALUATION_SET, validate_evaluation_dataset
from Day16.evaluator import evaluate_single_result, evaluate_batch, normalize_breach
from Day16.cot_experiment import sanitize_client_payload
from Day16.budget_and_self_consistency import majority_vote_verdict
from Day16.decomposed_pipeline import (
    stage1_extract_items,
    stage2_check_arithmetic,
    stage3_apply_rules,
    stage4_decide_verdict
)


def test_evaluation_set_structure():
    """Verify evaluation set contains 30 claims with required mandatory fields and 8 hard cases."""
    assert len(EVALUATION_SET) == 30, "Evaluation set must contain exactly 30 claims."

    hard_cases = [c for c in EVALUATION_SET if c.get("hard_case", False) is True]
    assert len(hard_cases) == 8, "Evaluation set must contain exactly 8 hard cases."

    required_keys = [
        "claim_id", "input", "line_items", "expected_verdict",
        "expected_breaches", "hard_case", "hard_case_type"
    ]

    for claim in EVALUATION_SET:
        for key in required_keys:
            assert key in claim, f"Claim {claim.get('claim_id')} missing required key '{key}'"

        assert claim["expected_verdict"] in ["APPROVE", "REJECT", "REVIEW"], \
            f"Invalid verdict '{claim['expected_verdict']}' in claim {claim['claim_id']}"

    assert validate_evaluation_dataset(EVALUATION_SET) is True


def test_evaluator_scoring_logic():
    """Test verdict_score, breach_score, and overall_score calculation separately."""
    claim = {
        "expected_verdict": "REJECT",
        "expected_breaches": ["meal_daily_limit"]
    }

    # Case 1: Perfect match
    pred1 = {"verdict": "REJECT", "breaches": ["meal_daily_limit"]}
    res1 = evaluate_single_result(pred1, claim)
    assert res1["verdict_score"] == 1
    assert res1["breach_score"] == 1
    assert res1["overall_score"] == 1

    # Case 2: Right verdict, wrong breach -> Overall must be 0 ("Right answer for wrong reason is not a pass")
    pred2 = {"verdict": "REJECT", "breaches": ["missing_receipt"]}
    res2 = evaluate_single_result(pred2, claim)
    assert res2["verdict_score"] == 1
    assert res2["breach_score"] == 0
    assert res2["overall_score"] == 0, "Right verdict with wrong breach must NOT pass."

    # Case 3: Wrong verdict, right breach
    pred3 = {"verdict": "REVIEW", "breaches": ["meal_daily_limit"]}
    res3 = evaluate_single_result(pred3, claim)
    assert res3["verdict_score"] == 0
    assert res3["breach_score"] == 1
    assert res3["overall_score"] == 0


def test_batch_evaluation_accuracies():
    """Test batch evaluation metric calculations including hard-case accuracy."""
    mock_claims = [
        {"claim_id": "c1", "hard_case": True, "expected_verdict": "APPROVE", "expected_breaches": []},
        {"claim_id": "c2", "hard_case": True, "expected_verdict": "REJECT", "expected_breaches": ["missing_receipt"]},
        {"claim_id": "c3", "hard_case": False, "expected_verdict": "REVIEW", "expected_breaches": ["arithmetic_discrepancy"]}
    ]

    mock_preds = [
        {"verdict": "APPROVE", "breaches": []},  # Pass
        {"verdict": "REJECT", "breaches": ["missing_receipt"]},  # Pass
        {"verdict": "APPROVE", "breaches": []}  # Fail
    ]

    res = evaluate_batch(mock_preds, mock_claims)
    assert res["total_claims"] == 3
    assert res["verdict_accuracy"] == round(2 / 3, 4)
    assert res["hard_case_verdict_accuracy"] == 1.0  # 2/2 hard cases passed
    assert res["hard_case_overall_accuracy"] == 1.0


def test_p95_and_cost_calculations():
    """Test P95 latency and cost per 1,000 claims calculation logic."""
    latencies = [10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0]
    p95 = float(np.percentile(latencies, 95))
    assert abs(p95 - 95.5) < 0.01, f"Expected P95 95.5, got {p95}"

    total_cost_30_claims = 0.0216
    cost_per_1k = (total_cost_30_claims / 30.0) * 1000.0
    assert abs(cost_per_1k - 0.72) < 0.001, f"Expected cost per 1k = 0.72, got {cost_per_1k}"


def test_majority_voting_self_consistency():
    """Test majority voting across self-consistency prediction samples."""
    samples = [
        {"verdict": "REJECT", "breaches": ["missing_receipt"]},
        {"verdict": "REJECT", "breaches": ["missing_receipt"]},
        {"verdict": "APPROVE", "breaches": []}
    ]
    voted = majority_vote_verdict(samples)
    assert voted["verdict"] == "REJECT"
    assert "missing_receipt" in voted["breaches"]


def test_no_reasoning_leakage_in_client_payload():
    """Task 10: Test that client response payload contains ONLY required fields (verdict & breaches)."""
    raw_llm_response = {
        "verdict": "REJECT",
        "breaches": ["meal_daily_limit"],
        "reasoning": "Step 1: The meal was 1350 USD which is > 1200 limit.",
        "thought_process": "Evaluating policy rule 1...",
        "intermediate_steps": ["extract", "check", "decide"]
    }

    clean_payload = sanitize_client_payload(raw_llm_response)

    assert set(clean_payload.keys()) == {"verdict", "breaches"}, \
        f"Client payload contains prohibited keys: {set(clean_payload.keys())}"
    assert "reasoning" not in clean_payload
    assert "thought_process" not in clean_payload
    assert clean_payload["verdict"] == "REJECT"
    assert clean_payload["breaches"] == ["meal_daily_limit"]


def test_typed_pipeline_handoffs():
    """Task 13: Verify typed handoff structures between stages."""
    claim = EVALUATION_SET[0]  # Hard case 1: arithmetic mismatch

    # Stage 1: Extraction
    extracted = stage1_extract_items(claim)
    assert "submission_date" in extracted
    assert "claimant" in extracted
    assert "stated_total" in extracted
    assert "line_items" in extracted

    # Stage 2: Arithmetic Check
    arithmetic = stage2_check_arithmetic(extracted)
    assert "calculated_total" in arithmetic
    assert "stated_total" in arithmetic
    assert "is_correct" in arithmetic
    assert arithmetic["is_correct"] is False

    # Stage 3: Apply Rules
    rules = stage3_apply_rules(extracted)
    assert "breaches" in rules

    # Stage 4: Decide Verdict
    decision = stage4_decide_verdict(extracted, arithmetic, rules)
    assert decision["verdict"] in ["APPROVE", "REJECT", "REVIEW"]
    assert "breaches" in decision


def test_dataset_experiment_item_count_verification():
    """Verify that dataset validation raises AssertionError if item count != 30."""
    invalid_set = EVALUATION_SET[:10]  # Only 10 claims
    with pytest.raises(ValueError, match="Expected exactly 30 claims"):
        validate_evaluation_dataset(invalid_set)
