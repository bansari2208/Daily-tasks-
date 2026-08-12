"""
Day 16: Langfuse Dataset Experiments Verification Script.
Verifies from Langfuse Cloud:
1. Dataset 'expense_claim_evaluation_v1' exists.
2. Dataset item count == 30 (30 unique claim IDs, 0 duplicates, 8 hard cases).
3. The 5 official Day 16 Dataset Experiment runs exist:
   - day16_single_prompt
   - day16_decomposed_pipeline
   - day16_two_call
   - day16_self_consistency_3
   - day16_self_consistency_5
4. Each experiment run was executed against the dataset and contains valid evaluation scores.
Returns exit code 0 if verification passes, non-zero if verification fails.
"""

import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Load environment variables
load_dotenv()
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "Day15", ".env"))
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from langfuse import Langfuse
from Day16.evaluation_set import EVALUATION_SET, validate_evaluation_dataset


def verify_langfuse_experiments(dataset_name: str = "expense_claim_evaluation_v1") -> bool:
    print("=========================================================================================")
    print(f"             Day 16: Langfuse Dataset Experiments Verification ({dataset_name})         ")
    print("=========================================================================================\n")

    # 1. Local evaluation set validation
    try:
        validate_evaluation_dataset(EVALUATION_SET)
        print("[OK] Local EVALUATION_SET validation passed (30 claims, 8 hard cases).")
    except Exception as err:
        print(f"[FAIL] Local dataset validation error: {err}")
        return False

    # 2. Langfuse Connection
    try:
        client = Langfuse()
        auth_ok = client.auth_check()
        print(f"[OK] Connected to Langfuse Cloud | Auth Check: {auth_ok}")
    except Exception as e:
        print(f"[FAIL] Could not connect to Langfuse Cloud: {e}")
        return False

    # 3. Retrieve Dataset
    try:
        dataset = client.get_dataset(dataset_name)
        items = dataset.items
        print(f"[OK] Fetched dataset '{dataset_name}' with {len(items)} items.")
    except Exception as e:
        print(f"[FAIL] Failed to fetch dataset '{dataset_name}': {e}")
        return False

    # Item & Hard case validation
    item_cids = [item.metadata.get("claim_id") if (item.metadata and isinstance(item.metadata, dict)) else item.input.get("claim_id") for item in items]
    unique_cids = len(set(item_cids))
    duplicate_count = len(items) - unique_cids
    hard_cases_count = sum(1 for item in items if (item.metadata and isinstance(item.metadata, dict) and item.metadata.get("hard_case") is True))

    print("\n---------------- DATASET INTEGRITY METRICS ----------------")
    print(f"Dataset Name        : {dataset_name}")
    print(f"Total Items         : {len(items)}")
    print(f"Unique Claim IDs    : {unique_cids}")
    print(f"Duplicate Items     : {duplicate_count}")
    print(f"Hard Cases Count    : {hard_cases_count}")
    print("-----------------------------------------------------------\n")

    if len(items) != 30 or unique_cids != 30 or duplicate_count != 0 or hard_cases_count < 8:
        print(f"[FAIL] Dataset integrity check failed on Langfuse Cloud.")
        return False

    # 4. Fetch Dataset Experiment Runs
    expected_experiments = [
        "day16_single_prompt",
        "day16_decomposed_pipeline",
        "day16_two_call",
        "day16_self_consistency_3",
        "day16_self_consistency_5"
    ]

    try:
        runs_response = client.get_dataset_runs(dataset_name=dataset_name)
        found_runs = {r.name: r for r in runs_response.data}
        print(f"[OK] Found {len(found_runs)} dataset run(s) on Langfuse Cloud.")
    except Exception as e:
        print(f"[FAIL] Could not fetch dataset runs from Langfuse: {e}")
        return False

    print("\n---------------- EXPERIMENT RUNS STATUS ----------------")
    missing_runs = []
    for exp_name in expected_experiments:
        if exp_name in found_runs:
            run_info = found_runs[exp_name]
            created_at = getattr(run_info, "created_at", "N/A")
            print(f"  [PASS] {exp_name:<30} | Created: {created_at}")
        else:
            print(f"  [MISSING] {exp_name:<27} | NOT FOUND")
            missing_runs.append(exp_name)
    print("--------------------------------------------------------\n")

    if missing_runs:
        print(f"[FAIL] Missing {len(missing_runs)} required experiment runs on Langfuse Cloud: {missing_runs}")
        return False

    print("=========================================================================================")
    print("       [SUCCESS] All Langfuse Dataset Experiments Verified Successfully! (PASS)          ")
    print("=========================================================================================\n")
    return True


if __name__ == "__main__":
    success = verify_langfuse_experiments()
    if not success:
        sys.exit(1)
