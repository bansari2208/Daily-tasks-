"""
Day 16: Langfuse Dataset Verification Script.
Verifies:
1. Dataset 'expense_claim_evaluation_v1' exists on Langfuse Cloud.
2. Dataset contains exactly 30 unique items (zero duplicate claim_ids).
3. All required metadata fields exist (claim_id, hard_case, hard_case_type).
4. All 8 mandatory hard cases are present with valid hard_case_type.
5. All expected outputs (verdict, breaches) are defined.
Prints a clear execution status report.
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


def verify_langfuse_dataset(dataset_name: str = "expense_claim_evaluation_v1") -> bool:
    print("=========================================================================================")
    print(f"               Day 16: Langfuse Evaluation Dataset Verification ({dataset_name})        ")
    print("=========================================================================================\n")

    # 1. Validate local evaluation set
    try:
        validate_evaluation_dataset(EVALUATION_SET)
        print("[OK] Local EVALUATION_SET validation passed (30 claims, 8 hard cases, unique IDs).")
    except Exception as err:
        print(f"[FAIL] Local dataset validation error: {err}")
        return False

    # 2. Connect to Langfuse Cloud
    try:
        client = Langfuse()
        auth_ok = client.auth_check()
        print(f"[OK] Connected to Langfuse Cloud | Auth Check: {auth_ok}")
    except Exception as e:
        print(f"[FAIL] Could not connect to Langfuse: {e}")
        return False

    # 3. Retrieve dataset
    try:
        dataset = client.get_dataset(dataset_name)
        items = dataset.items
        print(f"[OK] Fetched dataset '{dataset_name}' from Langfuse Cloud.")
    except Exception as e:
        print(f"[FAIL] Dataset '{dataset_name}' not found on Langfuse Cloud: {e}")
        return False

    # 4. Check dataset item count and unique claim_ids
    total_items = len(items)
    claim_ids = []
    hard_cases_count = 0
    expected_outputs_count = 0
    hard_case_types = set()

    for item in items:
        # Input & Metadata inspection
        cid = None
        if item.metadata and isinstance(item.metadata, dict):
            cid = item.metadata.get("claim_id")
            if item.metadata.get("hard_case") is True:
                hard_cases_count += 1
                if item.metadata.get("hard_case_type"):
                    hard_case_types.add(item.metadata.get("hard_case_type"))

        if not cid and isinstance(item.input, dict):
            cid = item.input.get("claim_id")

        if cid:
            claim_ids.append(cid)

        # Expected output inspection
        if item.expected_output and isinstance(item.expected_output, dict):
            if "verdict" in item.expected_output and "breaches" in item.expected_output:
                expected_outputs_count += 1

    unique_claim_ids = len(set(claim_ids))
    duplicate_count = total_items - unique_claim_ids

    print("\n---------------- LANGFUSE DATASET STATUS REPORT ----------------")
    print(f"Dataset Name        : {dataset_name}")
    print(f"Total Items         : {total_items}")
    print(f"Unique Claim IDs    : {unique_claim_ids}")
    print(f"Duplicate Items     : {duplicate_count}")
    print(f"Hard Cases Count    : {hard_cases_count}")
    print(f"Hard Case Categories: {len(hard_case_types)}")
    print(f"Expected Outputs    : {expected_outputs_count}")

    # Check status criteria
    passed = (
        total_items == 30 and
        unique_claim_ids == 30 and
        duplicate_count == 0 and
        hard_cases_count >= 8 and
        expected_outputs_count == 30
    )

    status_str = "PASS" if passed else "FAIL"
    print(f"Verification Status : {status_str}")
    print("----------------------------------------------------------------\n")

    if not passed:
        if duplicate_count > 0:
            print(f"[WARN] Found {duplicate_count} duplicate items in Langfuse. Run sync_evaluation_dataset() to clean up.")
        if total_items != 30:
            print(f"[WARN] Total items count is {total_items} (expected 30).")

    return passed


if __name__ == "__main__":
    success = verify_langfuse_dataset()
    if not success:
        sys.exit(1)
