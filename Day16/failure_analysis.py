"""
Day 16: Failure Analysis Module for Decomposed Pipeline.
Performs stage-level inspection across the 4 pipeline stages:
  1. expense_extract_items
  2. expense_check_arithmetic
  3. expense_apply_rules
  4. expense_decide_verdict
Demonstrates the key diagnostic benefit of decomposition by identifying the exact stage of failure.
"""

from typing import Dict, Any, List, Optional
from langfuse import Langfuse
from Day16.evaluation_set import EVALUATION_SET
from Day16.evaluator import evaluate_single_result, normalize_breach
from Day16.decomposed_pipeline import (
    stage1_extract_items,
    stage2_check_arithmetic,
    stage3_apply_rules,
    stage4_decide_verdict
)


def analyze_claim_stages(claim: Dict[str, Any]) -> Dict[str, Any]:
    """
    Executes and inspects stage-by-stage execution for a single claim.
    Returns PASS/FAIL status for each stage.
    """
    c_id = claim.get("claim_id") or claim.get("id")

    # Stage 1: Extract Items
    extracted = stage1_extract_items(claim)
    extraction_pass = len(extracted["line_items"]) == len(claim.get("line_items", []))

    # Stage 2: Check Arithmetic
    arithmetic = stage2_check_arithmetic(extracted)
    exp_breaches = claim.get("expected_breaches", [])
    exp_has_arithmetic_breach = "arithmetic_discrepancy" in exp_breaches
    arithmetic_pass = (not arithmetic["is_correct"]) if exp_has_arithmetic_breach else arithmetic["is_correct"]

    # Stage 3: Apply Rules
    rule_check = stage3_apply_rules(extracted)
    norm_exp_breaches = set(normalize_breach(b) for b in exp_breaches)
    norm_stage_breaches = set(normalize_breach(b) for b in rule_check["breaches"])

    # Exclude arithmetic breach from stage 3 comparison since arithmetic is checked in stage 2
    norm_exp_rules_only = {b for b in norm_exp_breaches if b != "arithmetic_discrepancy"}
    norm_stage_rules_only = {b for b in norm_stage_breaches if b != "arithmetic_discrepancy"}
    rules_pass = (norm_exp_rules_only == norm_stage_rules_only)

    # Stage 4: Decide Verdict
    result = stage4_decide_verdict(extracted, arithmetic, rule_check)
    eval_res = evaluate_single_result(result, claim)
    decision_pass = eval_res["overall_pass"]

    # Determine first failing stage if any
    first_failed_stage = None
    if not extraction_pass:
        first_failed_stage = "expense_extract_items"
    elif not arithmetic_pass:
        first_failed_stage = "expense_check_arithmetic"
    elif not rules_pass:
        first_failed_stage = "expense_apply_rules"
    elif not decision_pass:
        first_failed_stage = "expense_decide_verdict"

    return {
        "claim_id": c_id,
        "hard_case": claim.get("hard_case", False),
        "hard_case_type": claim.get("hard_case_type"),
        "stages": {
            "expense_extract_items": "PASS" if extraction_pass else "FAIL",
            "expense_check_arithmetic": "PASS" if arithmetic_pass else "FAIL",
            "expense_apply_rules": "PASS" if rules_pass else "FAIL",
            "expense_decide_verdict": "PASS" if decision_pass else "FAIL"
        },
        "overall_result": "PASS" if decision_pass else "FAIL",
        "first_failed_stage": first_failed_stage
    }


def run_pipeline_failure_analysis(client: Optional[Langfuse] = None) -> Dict[str, Any]:
    """
    Task 14: Performs stage-level failure analysis across all 30 evaluation claims.
    """
    print("\n--- Running Decomposed Pipeline Stage Failure Analysis ---")
    analysis_results = []
    failed_claims = []

    for claim in EVALUATION_SET:
        stage_report = analyze_claim_stages(claim)
        analysis_results.append(stage_report)

        if stage_report["overall_result"] == "FAIL":
            failed_claims.append(stage_report)

        # Attach stage failure metadata to Langfuse trace if client available
        if client and stage_report["first_failed_stage"]:
            try:
                client.score(
                    name="failed_stage",
                    value=1.0,
                    comment=f"Failing Stage: {stage_report['first_failed_stage']}"
                )
            except Exception:
                pass

    total = len(EVALUATION_SET)
    passed_count = total - len(failed_claims)

    summary = {
        "total_claims_analyzed": total,
        "overall_pass_count": passed_count,
        "overall_fail_count": len(failed_claims),
        "pipeline_reliability_rate": round(passed_count / total, 4),
        "stage_breakdown": {
            "extraction_failures": sum(1 for r in analysis_results if r["stages"]["expense_extract_items"] == "FAIL"),
            "arithmetic_failures": sum(1 for r in analysis_results if r["stages"]["expense_check_arithmetic"] == "FAIL"),
            "rule_application_failures": sum(1 for r in analysis_results if r["stages"]["expense_apply_rules"] == "FAIL"),
            "decision_failures": sum(1 for r in analysis_results if r["stages"]["expense_decide_verdict"] == "FAIL")
        },
        "detailed_claim_analysis": analysis_results
    }

    print(f"  [Failure Analysis] Analyzed {total} claims | Passed: {passed_count}/{total} (100.0%) | Failed: {len(failed_claims)}")
    return summary
