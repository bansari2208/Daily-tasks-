"""
Day 14 - Tool Selection & Argument Accuracy Evaluation Benchmark.

Evaluates performance across 20 test prompts measuring:
1. Tool Selection Accuracy %
2. Argument Extraction & Validation Accuracy %
3. "No Tool" Decision Accuracy %
4. Overall Benchmark Pass Rate %
"""

import time
from typing import Dict, Any, List
from prompts import EVALUATION_PROMPTS
from tool_executor import ToolExecutor


def run_evaluation_benchmark(auto_confirm: bool = True) -> Dict[str, Any]:
    """
    Runs the complete 20-prompt evaluation suite.

    Args:
        auto_confirm: Boolean override to auto-approve state-changing tools.

    Returns:
        Dict containing accuracy metrics and detailed test results.
    """
    executor = ToolExecutor()

    total_prompts = len(EVALUATION_PROMPTS)
    correct_tool_selection = 0
    correct_arguments = 0
    correct_no_tool_decisions = 0
    total_no_tool_prompts = 0

    results = []

    print("\n=========================================================================================")
    print("                 Day 14 Tool Selection & Argument Accuracy Evaluation                    ")
    print("=========================================================================================")
    print(f"{'ID':<4} | {'Expected Tool':<22} | {'Actual Tool':<22} | {'Status':<16} | {'Match'}")
    print("-" * 91)

    for p_item in EVALUATION_PROMPTS:
        p_id = p_item["id"]
        prompt = p_item["prompt"]
        exp_tool = p_item["expected_tool"]
        exp_args = p_item["expected_args"]

        exec_res = executor.execute_prompt(prompt, auto_confirm=auto_confirm)
        act_tool = exec_res.tool_name
        act_status = exec_res.status

        # Check tool selection accuracy
        tool_match = (act_tool == exp_tool)
        if tool_match:
            correct_tool_selection += 1

        # Check "No Tool" decision accuracy
        if exp_tool is None:
            total_no_tool_prompts += 1
            if act_tool is None and act_status == "NO_TOOL":
                correct_no_tool_decisions += 1

        # Check arguments accuracy (for valid tool calls or valid validation errors)
        args_match = False
        if tool_match:
            if exp_tool is None:
                args_match = True
            elif act_status == "VALIDATION_ERROR" and any(v < 0 for v in exp_args.values() if isinstance(v, (int, float))):
                # Correctly caught invalid argument
                args_match = True
            elif exec_res.arguments.get("ticket_id") == exp_args.get("ticket_id"):
                args_match = True

        if args_match:
            correct_arguments += 1

        overall_pass = tool_match and args_match
        match_str = "PASS" if overall_pass else "FAIL"

        exp_tool_str = str(exp_tool) if exp_tool else "None (No Tool)"
        act_tool_str = str(act_tool) if act_tool else "None (No Tool)"

        print(f"{p_id:<4} | {exp_tool_str:<22} | {act_tool_str:<22} | {act_status:<16} | {match_str}")

        results.append({
            "id": p_id,
            "prompt": prompt,
            "expected_tool": exp_tool,
            "actual_tool": act_tool,
            "status": act_status,
            "tool_match": tool_match,
            "args_match": args_match,
            "passed": overall_pass,
        })

    tool_acc_pct = (correct_tool_selection / total_prompts) * 100.0
    args_acc_pct = (correct_arguments / total_prompts) * 100.0
    no_tool_acc_pct = (correct_no_tool_decisions / total_no_tool_prompts * 100.0) if total_no_tool_prompts > 0 else 100.0
    overall_pass_pct = (sum(1 for r in results if r["passed"]) / total_prompts) * 100.0

    print("=========================================================================================")
    print("\nEvaluation Summary Results:")
    print(f"  Total Evaluated Prompts        : {total_prompts}")
    print(f"  Tool Selection Accuracy        : {tool_acc_pct:.1f}% ({correct_tool_selection}/{total_prompts})")
    print(f"  Argument Validation Accuracy   : {args_acc_pct:.1f}% ({correct_arguments}/{total_prompts})")
    print(f"  'No Tool' Decision Accuracy    : {no_tool_acc_pct:.1f}% ({correct_no_tool_decisions}/{total_no_tool_prompts})")
    print(f"  Overall Benchmark Pass Rate    : {overall_pass_pct:.1f}%\n")

    return {
        "total_prompts": total_prompts,
        "tool_selection_accuracy_pct": tool_acc_pct,
        "argument_accuracy_pct": args_acc_pct,
        "no_tool_accuracy_pct": no_tool_acc_pct,
        "overall_pass_pct": overall_pass_pct,
        "results": results,
    }


if __name__ == "__main__":
    run_evaluation_benchmark()
