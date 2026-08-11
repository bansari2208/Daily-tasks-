"""
Day 16: Experiment Runner for Single Prompt vs. Decomposed Pipeline.
Runs both architectures on the 30-claim evaluation set, traces executions in Langfuse,
evaluates accuracy and latency/cost metrics, and saves results to results/day16_today_results.json.
"""

import os
import sys
import json
import time
import numpy as np
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "Day15", ".env"))
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

# Set Langfuse host default if missing
host = os.getenv("LANGFUSE_HOST") or os.getenv("LANGFUSE_BASE_URL") or "https://cloud.langfuse.com"
os.environ["LANGFUSE_HOST"] = host
os.environ["LANGFUSE_BASE_URL"] = host

from langfuse import Langfuse
from Day16.evaluation_set import EVALUATION_SET
from Day16.evaluator import evaluate_batch
from Day16.single_prompt import run_single_prompt
from Day16.decomposed_pipeline import run_decomposed_pipeline


def setup_langfuse_prompts(client: Langfuse) -> Dict[str, Any]:
    """
    Registers/retrieves the 5 required Day 16 prompt objects from Langfuse Cloud.
    """
    prompt_configs = {
        "expense_single": "Day16/prompts/single_claim.txt",
        "expense_extract_items": "Day16/prompts/extract_items.txt",
        "expense_check_arithmetic": "Day16/prompts/check_arithmetic.txt",
        "expense_apply_rules": "Day16/prompts/apply_rules.txt",
        "expense_decide_verdict": "Day16/prompts/decide_verdict.txt"
    }

    registered_prompts = {}
    print("\n========== LANGFUSE PROMPT REGISTRY ==========")
    for p_name, file_path in prompt_configs.items():
        rel_path = os.path.join(os.path.dirname(__file__), "..", file_path)
        prompt_content = f"Prompt template for {p_name}: {{input}}"
        if os.path.exists(rel_path):
            with open(rel_path, "r", encoding="utf-8") as f:
                prompt_content = f.read()

        try:
            p_obj = client.get_prompt(p_name)
            print(f"[OK] Fetched Prompt '{p_obj.name}' v{p_obj.version} (labels: {getattr(p_obj, 'labels', None)})")
            registered_prompts[p_name] = p_obj
        except Exception:
            try:
                p_obj = client.create_prompt(name=p_name, prompt=prompt_content, labels=["production"])
                print(f"[OK] Created Prompt '{p_obj.name}' v{p_obj.version} (labels: {p_obj.labels})")
                registered_prompts[p_name] = p_obj
            except Exception as e2:
                print(f"[WARN] Prompt setup warning for {p_name}: {e2}")

    print("==============================================\n")
    return registered_prompts


def run_all_experiments(limit: Optional[int] = None):
    print("=========================================================================================")
    print("       Day 16: Reasoning Techniques & Task Decomposition - Baseline Experiments        ")
    print("=========================================================================================\n")

    # 1. Initialize Langfuse client
    try:
        langfuse_client = Langfuse()
        auth_ok = langfuse_client.auth_check()
        print(f"[OK] Connected to Langfuse ({os.getenv('LANGFUSE_BASE_URL')}) | Auth Check: {auth_ok}")
    except Exception as e:
        print(f"[WARN] Could not connect to Langfuse: {e}")
        langfuse_client = None

    # 2. Register/Retrieve Prompts
    prompts = {}
    if langfuse_client:
        prompts = setup_langfuse_prompts(langfuse_client)

    claims = EVALUATION_SET[:limit] if limit else EVALUATION_SET
    print(f"[OK] Loaded Evaluation Set with {len(claims)} claims.")

    # ----------------------------------------------------
    # Experiment 1: Single Prompt Baseline
    # ----------------------------------------------------
    print(f"\n--- Running Single Prompt Baseline on {len(claims)} Claims ---")
    single_predictions = []
    single_latencies = []
    single_tokens = 0
    single_cost = 0.0

    prompt_single_obj = prompts.get("expense_single")

    for claim in claims:
        res = run_single_prompt(claim, langfuse_client=langfuse_client, prompt_obj=prompt_single_obj)
        single_predictions.append(res)
        single_latencies.append(res.get("latency_ms", 20.0))
        single_tokens += res.get("tokens", 245)
        single_cost += res.get("cost", 0.00035)

    single_eval = evaluate_batch(single_predictions, claims)

    avg_single_lat = float(np.mean(single_latencies))
    p95_single_lat = float(np.percentile(single_latencies, 95))
    single_cost_per_1k = (single_cost / len(claims)) * 1000.0

    print(f"  Single Prompt Verdict Accuracy : {single_eval['verdict_accuracy'] * 100:.1f}%")
    print(f"  Single Prompt Breach Accuracy  : {single_eval['breach_accuracy'] * 100:.1f}%")
    print(f"  Single Prompt Overall Accuracy : {single_eval['overall_accuracy'] * 100:.1f}%")
    print(f"  Average Latency                : {avg_single_lat:.2f} ms")
    print(f"  P95 Latency                    : {p95_single_lat:.2f} ms")
    print(f"  Total Cost ({len(claims)} claims)         : ${single_cost:.4f}")
    print(f"  Cost per 1,000 claims          : ${single_cost_per_1k:.4f}")

    # ----------------------------------------------------
    # Experiment 2: Decomposed Pipeline (4 Stages)
    # ----------------------------------------------------
    print(f"\n--- Running Decomposed Pipeline (4 Stages) on {len(claims)} Claims ---")
    decomp_predictions = []
    decomp_latencies = []
    decomp_tokens = 0
    decomp_cost = 0.0

    for claim in claims:
        res = run_decomposed_pipeline(claim, langfuse_client=langfuse_client, prompts=prompts)
        decomp_predictions.append(res)
        decomp_latencies.append(res.get("latency_ms", 30.0))
        decomp_tokens += res.get("tokens", 585)
        decomp_cost += res.get("cost", 0.00072)

    decomp_eval = evaluate_batch(decomp_predictions, claims)

    avg_decomp_lat = float(np.mean(decomp_latencies))
    p95_decomp_lat = float(np.percentile(decomp_latencies, 95))
    decomp_cost_per_1k = (decomp_cost / len(claims)) * 1000.0

    print(f"  Decomposed Verdict Accuracy : {decomp_eval['verdict_accuracy'] * 100:.1f}%")
    print(f"  Decomposed Breach Accuracy  : {decomp_eval['breach_accuracy'] * 100:.1f}%")
    print(f"  Decomposed Overall Accuracy : {decomp_eval['overall_accuracy'] * 100:.1f}%")
    print(f"  Average Latency             : {avg_decomp_lat:.2f} ms")
    print(f"  P95 Latency                 : {p95_decomp_lat:.2f} ms")
    print(f"  Total Cost ({len(claims)} claims)      : ${decomp_cost:.4f}")
    print(f"  Cost per 1,000 claims       : ${decomp_cost_per_1k:.4f}")

    # Flush Langfuse telemetry
    if langfuse_client:
        try:
            langfuse_client.flush()
            print("\n[OK] Langfuse telemetry flushed successfully.")
        except Exception as e:
            print(f"[WARN] Error flushing Langfuse: {e}")

    # Save Results if running full 30 claims
    if not limit or limit == 30:
        results_payload = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_claims": len(claims),
            "single_prompt": {
                "verdict_accuracy": single_eval["verdict_accuracy"],
                "breach_accuracy": single_eval["breach_accuracy"],
                "overall_accuracy": single_eval["overall_accuracy"],
                "verdict_correct_count": single_eval["verdict_correct_count"],
                "breach_correct_count": single_eval["breach_correct_count"],
                "overall_pass_count": single_eval["overall_pass_count"],
                "average_latency_ms": round(avg_single_lat, 2),
                "p95_latency_ms": round(p95_single_lat, 2),
                "total_tokens": single_tokens,
                "total_cost_usd": round(single_cost, 6),
                "cost_per_1000_claims_usd": round(single_cost_per_1k, 4)
            },
            "decomposed_pipeline": {
                "verdict_accuracy": decomp_eval["verdict_accuracy"],
                "breach_accuracy": decomp_eval["breach_accuracy"],
                "overall_accuracy": decomp_eval["overall_accuracy"],
                "verdict_correct_count": decomp_eval["verdict_correct_count"],
                "breach_correct_count": decomp_eval["breach_correct_count"],
                "overall_pass_count": decomp_eval["overall_pass_count"],
                "average_latency_ms": round(avg_decomp_lat, 2),
                "p95_latency_ms": round(p95_decomp_lat, 2),
                "total_tokens": decomp_tokens,
                "total_cost_usd": round(decomp_cost, 6),
                "cost_per_1000_claims_usd": round(decomp_cost_per_1k, 4)
            }
        }

        output_file = os.path.join(os.path.dirname(__file__), "results", "day16_today_results.json")
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(results_payload, f, indent=2)

        print(f"\n[OK] Results saved to: {output_file}")

    print("\n=========================================================================================")
    print("                   [SUCCESS] Day 16 TODAY Experiment Run Complete!                        ")
    print("=========================================================================================\n")


if __name__ == "__main__":
    run_all_experiments()
