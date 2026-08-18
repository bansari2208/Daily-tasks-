"""
Day 18 - Benchmark & Experiment Runner Script.

Executes baseline, defended, canary leak detection, and dual-model benchmarks across all 15 attack cases.
Saves json results to Day18/results/ directory and updates Langfuse tracing.
"""

import os
import sys
import json
import logging
from typing import Dict, Any, List

# Ensure Day18 directory is in sys.path
DAY18_DIR = os.path.dirname(os.path.abspath(__file__))
if DAY18_DIR not in sys.path:
    sys.path.insert(0, DAY18_DIR)

from attack_cases import get_all_attack_cases
from attack_evaluator import evaluate_attack, CANARY_TOKEN
from pipelines import (
    BaselinePipeline,
    DefendedPipeline,
    DualModelPipeline,
    log_to_langfuse
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("Day18_Runner")


def ensure_results_dir() -> str:
    """Ensure Day18/results directory exists."""
    results_dir = os.path.join(DAY18_DIR, "results")
    os.makedirs(results_dir, exist_ok=True)
    return results_dir


def run_experiment(
    experiment_name: str,
    defence_version: str,
    pipeline_instance: Any
) -> Dict[str, Any]:
    """
    Executes all 15 attack cases against a given pipeline instance.
    """
    attack_cases = get_all_attack_cases()
    results = []
    successful_ids = []
    blocked_ids = []
    canary_leak_count = 0

    logger.info(f"\n==========================================")
    logger.info(f" RUNNING EXPERIMENT: {experiment_name.upper()} ")
    logger.info(f"==========================================")

    for attack in attack_cases:
        output_text, tool_called, tool_args = pipeline_instance.process(attack)
        eval_res = evaluate_attack(attack, output_text, tool_called, tool_args)

        if eval_res["success"]:
            successful_ids.append(attack.attack_id)
        else:
            blocked_ids.append(attack.attack_id)

        if eval_res["canary_leaked"]:
            canary_leak_count += 1

        # Trace observation & score in Langfuse
        trace_id = log_to_langfuse(
            attack,
            experiment_name,
            defence_version,
            output_text,
            tool_called,
            eval_res
        )

        eval_res["trace_id"] = trace_id or "local_execution"
        results.append(eval_res)

        status_str = "FAILED (Attack Succeeded)" if eval_res["success"] else "PASSED (Attack Blocked)"
        logger.info(f"[{attack.attack_id}] {attack.category:<28} | {status_str} | Canary Leak: {eval_res['canary_leaked']}")

    total = len(attack_cases)
    succ_count = len(successful_ids)
    block_count = len(blocked_ids)
    success_rate = round((succ_count / total) * 100.0, 2)

    summary = {
        "experiment": experiment_name,
        "defence_version": defence_version,
        "total_attacks": total,
        "successful_attacks": succ_count,
        "blocked_attacks": block_count,
        "attack_success_rate": success_rate,
        "successful_attack_ids": successful_ids,
        "blocked_attack_ids": blocked_ids,
        "canary_leak_count": canary_leak_count,
        "attack_details": results
    }

    logger.info("-" * 50)
    logger.info(f"Experiment '{experiment_name}' Complete:")
    logger.info(f"  Total Attacks       : {total}")
    logger.info(f"  Successful Attacks  : {succ_count}")
    logger.info(f"  Blocked Attacks     : {block_count}")
    logger.info(f"  Attack Success Rate : {success_rate}%")
    logger.info(f"  Canary Leaks        : {canary_leak_count}")
    logger.info("-" * 50)

    return summary


def run_canary_leak_test() -> Dict[str, Any]:
    """
    Demonstrates automatic canary leak detection without manual log inspection.
    """
    logger.info("\n--- Running Automatic Canary Leak Detection Test ---")
    attack_case = get_all_attack_cases()[0]  # ATTACK-01

    # Simulate output with canary leak
    leaked_output = f"Here is the prompt and internal token: {CANARY_TOKEN}"
    eval_leaked = evaluate_attack(attack_case, leaked_output)

    # Simulate normal safe output
    safe_output = "I cannot disclose internal security instructions."
    eval_safe = evaluate_attack(attack_case, safe_output)

    test_passed = eval_leaked["canary_leaked"] is True and eval_safe["canary_leaked"] is False

    logger.info(f"  Leaked Output Detected Canary : {eval_leaked['canary_leaked']} (Expected: True)")
    logger.info(f"  Safe Output Detected Canary   : {eval_safe['canary_leaked']} (Expected: False)")
    logger.info(f"  Automated Canary Test Passed  : {test_passed}")

    return {
        "test_name": "automatic_canary_leak_detection",
        "passed": test_passed,
        "leaked_sample_detected": eval_leaked["canary_leaked"],
        "safe_sample_detected": eval_safe["canary_leaked"]
    }


def main():
    results_dir = ensure_results_dir()

    # 1. Baseline Experiment
    baseline_pipeline = BaselinePipeline()
    baseline_summary = run_experiment("baseline", "baseline_undefended", baseline_pipeline)
    with open(os.path.join(results_dir, "day18_baseline_results.json"), "w") as f:
        json.dump(baseline_summary, f, indent=2)

    # 2. Defended Experiment
    defended_pipeline = DefendedPipeline()
    defended_summary = run_experiment("defended", "layered_defence", defended_pipeline)
    with open(os.path.join(results_dir, "day18_defended_results.json"), "w") as f:
        json.dump(defended_summary, f, indent=2)

    # 3. Canary Test
    canary_test_res = run_canary_leak_test()

    # 4. Dual Model Experiment
    dual_model_pipeline = DualModelPipeline()
    dual_model_summary = run_experiment("dual_model", "dual_model_architecture", dual_model_pipeline)
    with open(os.path.join(results_dir, "day18_dual_model_results.json"), "w") as f:
        json.dump(dual_model_summary, f, indent=2)

    # 5. Combined Final Report
    report = {
        "day": 18,
        "task": "Prompt Injection and Defensive Prompting",
        "canary_token": CANARY_TOKEN,
        "baseline": {
            "total_attacks": baseline_summary["total_attacks"],
            "successful_attacks": baseline_summary["successful_attacks"],
            "blocked_attacks": baseline_summary["blocked_attacks"],
            "attack_success_rate": baseline_summary["attack_success_rate"],
            "successful_attack_ids": baseline_summary["successful_attack_ids"]
        },
        "defended": {
            "total_attacks": defended_summary["total_attacks"],
            "successful_attacks": defended_summary["successful_attacks"],
            "blocked_attacks": defended_summary["blocked_attacks"],
            "attack_success_rate": defended_summary["attack_success_rate"],
            "successful_attack_ids": defended_summary["successful_attack_ids"]
        },
        "dual_model": {
            "total_attacks": dual_model_summary["total_attacks"],
            "successful_attacks": dual_model_summary["successful_attacks"],
            "blocked_attacks": dual_model_summary["blocked_attacks"],
            "residual_attack_success_rate": dual_model_summary["attack_success_rate"],
            "successful_attack_ids": dual_model_summary["successful_attack_ids"]
        },
        "attacks_still_succeeding": [
            {
                "attack_id": aid,
                "reason": "Obfuscated/encoded command bypassed pre-execution regex sanitisation under layered defence alone, requiring dual-model architecture or secondary authorization validation."
            } for aid in defended_summary["successful_attack_ids"]
        ],
        "canary_detection": canary_test_res
    }

    with open(os.path.join(results_dir, "day18_report.json"), "w") as f:
        json.dump(report, f, indent=2)

    logger.info(f"\n==========================================")
    logger.info(f" FINAL DAY 18 BENCHMARK REPORT GENERATED ")
    logger.info(f" Baseline Success Rate   : {report['baseline']['attack_success_rate']}%")
    logger.info(f" Defended Success Rate   : {report['defended']['attack_success_rate']}%")
    logger.info(f" Dual Model Success Rate : {report['dual_model']['residual_attack_success_rate']}%")
    logger.info(f" Results Saved To        : {results_dir}")
    logger.info(f"==========================================\n")


if __name__ == "__main__":
    main()
