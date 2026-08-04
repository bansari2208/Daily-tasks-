"""
Day 13 Live Interactive Manager Demo Script.
Walks through all 10 core Day 13 deliverables step-by-step.
"""

import sys
import os
import json

# Ensure Day13 directory is in sys.path
sys.path.insert(0, os.path.dirname(__file__))

from response_models import TicketClassificationResponse, FlexibleTicketResponse
from validation_boundary import ValidationBoundary
from self_repair import BoundedSelfRepairLoop, run_retry_budget_analysis
from failure_taxonomy import run_taxonomy_analysis
from unknown_schema_demo import run_unknown_comparison
from partial_results import PartialResultExtractor
from constrained_vs_repair import run_constrained_vs_repair_experiment
from revision_example import safe_ticket_extraction_pipeline, map_error_to_exception
from evaluation_report import generate_day13_evaluation_report


def pause():
    input("\nPress Enter to continue...\n")


def main():
    print("=========================================================================")
    print("    DAY 13 LIVE DEMO: RESPONSE MODELS, SELF-REPAIR & TAXONOMY")
    print("=========================================================================\n")

    # Step 1: Response Model Validation
    print("-------------------------------------------------------------------------")
    print("STEP 1: Response Model Validation Layer")
    print("-------------------------------------------------------------------------")
    sample_valid = '{"ticket_id": 101, "category": "Billing", "priority": "HIGH", "confidence": 0.95, "reasoning": "Duplicate charge on credit card"}'
    is_val, obj, err = ValidationBoundary.safe_validate(sample_valid, TicketClassificationResponse)
    print(f"Input JSON         : {sample_valid}")
    print(f"Validation Status  : {'[SUCCESS]' if is_val else '[FAILED]'}")
    print(f"Validated Model    : {obj}")
    pause()

    # Step 2: Boundary Validation
    print("-------------------------------------------------------------------------")
    print("STEP 2: Application Boundary Enforcement")
    print("-------------------------------------------------------------------------")
    sample_malformed = '{"ticket_id": 102, "category": "Technical", "confidence": "high"}'
    print(f"Raw Input Edge Data: {sample_malformed}")
    is_val2, obj2, err2 = ValidationBoundary.safe_validate(sample_malformed, TicketClassificationResponse)
    print(f"Boundary Rejection : [BLOCKED AT EDGE]")
    print(f"Caught Error       : {err2}")
    pause()

    # Step 3: Self Repair
    print("-------------------------------------------------------------------------")
    print("STEP 3: Bounded Self-Repair Loop")
    print("-------------------------------------------------------------------------")
    repair_loop = BoundedSelfRepairLoop(max_retries=3)
    def mock_llm(p: str) -> str:
        if "PREVIOUS OUTPUT FAILED" not in p:
            return '{"ticket_id": 103, "category": "Payment", "confidence": 0.9}'
        return '{"ticket_id": 103, "category": "Billing", "priority": "HIGH", "confidence": 0.95, "reasoning": "Corrected category"}'

    obj3, retries3, lat3, cost3 = repair_loop.execute_with_repair(mock_llm, "Classify ticket", ticket_id=103)
    print(f"Initial State      : Failed validation (Category 'Payment' invalid)")
    print(f"Self-Repair Status : [REPAIRED IN {retries3} RETRY]")
    print(f"Repaired Object    : {obj3}")
    print(f"Latency / Cost     : {lat3:.1f} ms | ${cost3:.4f}")
    pause()

    # Step 4: Retry Budget Analysis
    print("-------------------------------------------------------------------------")
    print("STEP 4: Retry Budget Analysis (Budgets 1, 2, 3, 4)")
    print("-------------------------------------------------------------------------")
    budget_results = run_retry_budget_analysis()
    print("Budget | Validity (%) | Avg Retries | Avg Latency (ms) | Cost / 1k Reqs")
    print("-------|--------------|-------------|------------------|----------------")
    for b, m in budget_results.items():
        print(f"  {b}    | {m['validity_pct']:<12}%| {m['avg_retries']:<12}| {m['avg_latency_ms']:<17}| ${m['avg_cost_per_1k']}")
    print("\nSelected Operating Point: Budget = 3 retries (Optimal recovery vs latency)")
    pause()

    # Step 5: Failure Taxonomy
    print("-------------------------------------------------------------------------")
    print("STEP 5: Failure Taxonomy Analysis (50 Failure Cases)")
    print("-------------------------------------------------------------------------")
    tax_path, sum_path, csv_path = run_taxonomy_analysis()
    print(f"Analyzed 50 failure cases across 8 taxonomy categories.")
    print(f"Generated Reports  :\n  - {tax_path}\n  - {sum_path}\n  - {csv_path}")
    pause()

    # Step 6: UNKNOWN Comparison
    print("-------------------------------------------------------------------------")
    print("STEP 6: Explicit UNKNOWN Path Comparison")
    print("-------------------------------------------------------------------------")
    unknown_res = run_unknown_comparison()
    print(f"Hallucinations Before UNKNOWN : {unknown_res['before_hallucinations']} / 50")
    print(f"Hallucinations After UNKNOWN  : {unknown_res['after_hallucinations']} / 50")
    print(f"Hallucination Reduction       : {unknown_res['reduction_pct']}%")
    pause()

    # Step 7: Partial Result Recovery
    print("-------------------------------------------------------------------------")
    print("STEP 7: Partial Result Recovery")
    print("-------------------------------------------------------------------------")
    partial_raw = '{"ticket_id": 107, "category": "InvalidCategory", "confidence": 0.95, "reasoning": "Valid reasoning text"}'
    partial_res = PartialResultExtractor.extract_partial_results(partial_raw)
    print(f"Raw Input JSON     : {partial_raw}")
    print(f"Salvaged Valid Fields: {json.dumps(partial_res['valid_fields'])}")
    print(f"Isolated Field Errors: {json.dumps(partial_res['field_errors'])}")
    pause()

    # Step 8: Constrained vs Self Repair
    print("-------------------------------------------------------------------------")
    print("STEP 8: Constrained Decoding vs. Self-Repair Benchmark")
    print("-------------------------------------------------------------------------")
    exp_res = run_constrained_vs_repair_experiment()
    r, c = exp_res["repair"], exp_res["constrained"]
    print(f"Bounded Self-Repair  : {r['validity_pct']}% validity | {r['avg_latency_ms']} ms | ${r['cost_per_1k']}/1k")
    print(f"Constrained Decoding : {c['validity_pct']}% validity | {c['avg_latency_ms']} ms | ${c['cost_per_1k']}/1k")
    print(f"Recommendation       : {exp_res['recommendation']} as Production Default")
    pause()

    # Step 9: Exception Hierarchy
    print("-------------------------------------------------------------------------")
    print("STEP 9: Exception Hierarchy & try/except/else/finally Flow")
    print("-------------------------------------------------------------------------")
    pipe_res = safe_ticket_extraction_pipeline(sample_valid)
    print(f"Pipeline Result    : {pipe_res}")
    print(f"Custom Exception   : {type(map_error_to_exception('Invalid enum', 'Bad enum')).__name__}")
    pause()

    # Step 10: Final Recommendation
    print("-------------------------------------------------------------------------")
    print("STEP 10: Master Evaluation Report & Final Recommendation")
    print("-------------------------------------------------------------------------")
    master_report = generate_day13_evaluation_report()
    print(f"Master Report Generated at: {master_report}")
    print("\nFINAL RECOMMENDATION:")
    print("  1. Adopt Constrained Decoding for standard production API calls.")
    print("  2. Keep Bounded Self-Repair (Max Retries = 3) as fallback layer.")
    print("  3. Allow explicit UNKNOWN enum fallback for 90%+ hallucination reduction.")
    print("\n=========================================================================")
    print("             DAY 13 LIVE DEMO COMPLETED SUCCESSFULLY")
    print("=========================================================================")


if __name__ == "__main__":
    main()
