"""
Day 14 - Master Demonstration Script.

Demonstrates:
1. Read-only tool execution (get_ticket_status)
2. State-changing tool execution (close_ticket) with Confirmation Gate
3. Argument validation rejection of invalid arguments (ticket_id <= 0)
4. Simulated tool failure & recovery path execution (ticket_id = 999)
5. 20-prompt evaluation benchmark execution
"""

import sys
import os
import json

# Ensure Day14 directory is in sys.path

from tool_executor import ToolExecutor
from evaluation import run_evaluation_benchmark


def run_demo():
    """Runs interactive demonstration of all Day 14 tool features."""
    executor = ToolExecutor()

    print("=========================================================================================")
    print("                      Day 14 - Tool Use & Validation Master Demo                         ")
    print("=========================================================================================")

    # Demo Scenario 1: Read-only tool execution
    print("\n--- Demo Scenario 1: Read-Only Tool Execution (get_ticket_status) ---")
    prompt_1 = "What is the current status of ticket 101?"
    print(f"User Prompt: '{prompt_1}'")
    res_1 = executor.execute_prompt(prompt_1)
    print(f"Tool Invoked      : {res_1.tool_name}")
    print(f"Execution Status  : {res_1.status}")
    print(f"Confirmation Gate : {res_1.confirmation_status}")
    print(f"Result Output     : {json.dumps(res_1.result, indent=2)}")

    # Demo Scenario 2: State-changing tool execution with Confirmation Gate Approval
    print("\n--- Demo Scenario 2: State-Changing Tool Execution (close_ticket) - CONFIRMED ---")
    prompt_2 = "Please close ticket 101 with reason: Issue resolved after system update."
    print(f"User Prompt: '{prompt_2}'")
    res_2 = executor.execute_prompt(prompt_2, auto_confirm=True)
    print(f"Tool Invoked      : {res_2.tool_name}")
    print(f"Execution Status  : {res_2.status}")
    print(f"Confirmation Gate : {res_2.confirmation_status}")
    print(f"Result Output     : {json.dumps(res_2.result, indent=2)}")

    # Demo Scenario 3: State-changing tool execution REJECTED by user at Confirmation Gate
    print("\n--- Demo Scenario 3: State-Changing Tool Execution (close_ticket) - REJECTED ---")
    prompt_3 = "Please close ticket 102 with reason: Resolved."
    print(f"User Prompt: '{prompt_3}'")
    res_3 = executor.execute_prompt(prompt_3, auto_confirm=False)
    print(f"Tool Invoked      : {res_3.tool_name}")
    print(f"Execution Status  : {res_3.status}")
    print(f"Confirmation Gate : {res_3.confirmation_status}")
    print(f"Result Output     : {json.dumps(res_3.result, indent=2)}")

    # Demo Scenario 4: Pydantic Argument Validation Rejection
    print("\n--- Demo Scenario 4: Invalid Argument Rejection (Pydantic Schema Validation) ---")
    prompt_4 = "Check status of ticket -5."
    print(f"User Prompt: '{prompt_4}'")
    res_4 = executor.execute_prompt(prompt_4)
    print(f"Tool Invoked      : {res_4.tool_name}")
    print(f"Execution Status  : {res_4.status}")
    print(f"Validation Error  : {res_4.error.message if res_4.error else 'N/A'}")
    print(f"Suggestion        : {res_4.error.suggestion if res_4.error else 'N/A'}")

    # Demo Scenario 5: Simulated Tool Failure & Failure Recovery Path Execution
    print("\n--- Demo Scenario 5: Simulated Tool Failure & Recovery Path (Ticket 999) ---")
    prompt_5 = "What is the status of ticket 999?"
    print(f"User Prompt: '{prompt_5}'")
    res_5 = executor.execute_prompt(prompt_5)
    print(f"Tool Invoked      : {res_5.tool_name}")
    print(f"Execution Status  : {res_5.status}")
    print(f"Error Type        : {res_5.error.error_type if res_5.error else 'N/A'}")
    print(f"Recovery Result   : {json.dumps(res_5.result, indent=2)}")

    # Demo Scenario 6: Run 20-Prompt Evaluation Benchmark
    print("\n--- Demo Scenario 6: 20-Prompt Evaluation Benchmark Suite ---")
    run_evaluation_benchmark(auto_confirm=True)

    print("=========================================================================================")
    print("                  Day 14 Master Demonstration Completed Successfully                     ")
    print("=========================================================================================\n")


if __name__ == "__main__":
    run_demo()
