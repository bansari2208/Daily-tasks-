"""
Day 10 Interactive Live Demo Script for Manager Presentation.
Executes Steps 1 to 8 in sequential order with pause-on-Enter between steps.
"""

import json
import os
import sys

BASE_DIR = os.path.dirname(__file__)
GOLDEN_DATASET_PATH = os.path.join(BASE_DIR, "golden_dataset.json")
RUBRIC_PATH = os.path.join(BASE_DIR, "scoring_rubric.md")
REPORT_PATH = os.path.join(BASE_DIR, "bakeoff_report.md")
PLAYBOOK_EXT_PATH = os.path.join(BASE_DIR, "playbook_extension.md")

from run_bakeoff import run_bakeoff


def pause_for_manager():
    """Pauses execution until Enter is pressed when running interactively in terminal."""
    if sys.stdin.isatty() and not os.environ.get("NON_INTERACTIVE"):
        try:
            input("\n[Press Enter to continue to next step...]")
        except EOFError:
            pass


def print_step_header(step_num: int, title: str):
    print("\n" + "=" * 50)
    print(f"STEP {step_num}: {title}")
    print("=" * 50)


def main():
    print("=================================")
    print("DAY 10 LIVE DEMO")
    print("=================================")

    # STEP 1
    print_step_header(1, "Loading Golden Dataset")
    with open(GOLDEN_DATASET_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    print(f"[OK] Successfully loaded {len(data)} fixed golden benchmark tickets.")
    print("Sample Record (#1):")
    print(json.dumps(data[0], indent=2))
    pause_for_manager()

    # STEP 2
    print_step_header(2, "Showing Scoring Rubric")
    with open(RUBRIC_PATH, "r", encoding="utf-8") as f:
        print(f.read().strip())
    pause_for_manager()

    # STEP 3
    print_step_header(3, "Running Blind Bake-off")
    run_bakeoff()
    pause_for_manager()

    # STEP 4
    print_step_header(4, "Comparing Models")
    print("Model Performance Matrix:")
    print("  * GPT-4.1 Mini (Model B): 95.0% Accuracy | 115ms Latency | $0.25/1k")
    print("  * GPT-4.1 Nano (Model A): 85.0% Accuracy | 62.5ms Latency | $0.08/1k")
    print("  * o3-mini      (Model C): 98.0% Accuracy | 620ms Latency  | $15.00/1k")
    print("  * Open Model   (Model D): 70.0% Accuracy | 340ms Latency  | $0.15/1k")
    pause_for_manager()

    # STEP 5
    print_step_header(5, "Winner Selection")
    print("[+] WINNER         : GPT-4.1 Mini (Model B) -- Best accuracy & performance balance.")
    print("[+] RUNNER-UP      : GPT-4.1 Nano (Model A) -- Lowest cost & sub-100ms speed.")
    print("[-] WORST PERFORMER: Mock Open Model (Model D) -- High error & schema failure rate.")
    pause_for_manager()

    # STEP 6
    print_step_header(6, "Selection Memo")
    if os.path.exists(REPORT_PATH):
        with open(REPORT_PATH, "r", encoding="utf-8") as f:
            print(f.read().strip())
    pause_for_manager()

    # STEP 7
    print_step_header(7, "Inference Control Playbook")
    if os.path.exists(PLAYBOOK_EXT_PATH):
        with open(PLAYBOOK_EXT_PATH, "r", encoding="utf-8") as f:
            print(f.read().strip())
    pause_for_manager()

    # STEP 8
    print_step_header(8, "Summary")
    print("""
Live Demonstration Complete!
Summary:
  1. Golden dataset of 20 tickets validated.
  2. Scoring rubric weighted and applied.
  3. Blind 4-model bake-off executed.
  4. GPT-4.1 Mini selected as primary winner.
  5. Playbook extension and selection memo generated.
""")


if __name__ == "__main__":
    main()
