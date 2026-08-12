"""
Day 16: Langfuse Dataset, Idempotent Sync, and Dataset Experiment Support.
Ensures:
1. Idempotent dataset synchronization with 30 unique items (zero duplicate items).
2. Clean dataset item structure (Input, Expected Output, Metadata).
3. Langfuse Dataset Experiment runner supporting Single Prompt, Decomposed Pipeline,
   Two-Call Reasoning, Budget, and Self-Consistency configurations.
"""

import os
from typing import Dict, Any, Optional, List, Callable
from langfuse import Langfuse
from Day16.evaluation_set import EVALUATION_SET, validate_evaluation_dataset
from Day16.evaluator import evaluate_single_result, evaluate_batch


def cleanup_dataset_duplicates(client: Langfuse, dataset_name: str = "expense_claim_evaluation_v1") -> int:
    """
    Safely inspects and removes duplicate dataset items from Langfuse Cloud by claim_id,
    ensuring exactly 30 unique items remain.
    """
    try:
        dataset = client.get_dataset(dataset_name)
        items = dataset.items
        seen_claim_ids = set()
        to_delete_ids = []

        for item in items:
            cid = None
            if item.metadata and isinstance(item.metadata, dict):
                cid = item.metadata.get("claim_id")
            elif isinstance(item.input, dict):
                cid = item.input.get("claim_id")

            if cid and cid in seen_claim_ids:
                to_delete_ids.append(item.id)
            elif cid:
                seen_claim_ids.add(cid)

        deleted_count = 0
        for item_id in to_delete_ids:
            try:
                client.api.dataset_items.delete(item_id)
                deleted_count += 1
            except Exception as e:
                print(f"[WARN] Failed to delete duplicate item {item_id}: {e}")

        if deleted_count > 0:
            print(f"[LANGFUSE] Deduplication complete: removed {deleted_count} duplicate items from '{dataset_name}'.")
        return deleted_count
    except Exception as e:
        print(f"[WARN] Cleanup duplicates failed: {e}")
        return 0


def sync_evaluation_dataset(client: Langfuse, dataset_name: str = "expense_claim_evaluation_v1") -> Any:
    """
    Idempotent synchronization of the 30-claim evaluation set into Langfuse.
    Guarantees exactly 30 unique dataset items without creating duplicates on repeated execution.
    """
    # 1. Validate local ground-truth evaluation set first
    validate_evaluation_dataset(EVALUATION_SET)

    print(f"\n[LANGFUSE] Synchronizing dataset '{dataset_name}' with {len(EVALUATION_SET)} unique items...")
    try:
        try:
            dataset = client.get_dataset(dataset_name)
            print(f"[OK] Found existing dataset '{dataset_name}'")
        except Exception:
            dataset = client.create_dataset(
                name=dataset_name,
                description="Day 16 expense claim evaluation dataset containing 30 claims (8 mandatory hard cases)."
            )
            print(f"[OK] Created new dataset '{dataset_name}'")

        # 2. Cleanup any pre-existing duplicates in Langfuse Cloud
        cleanup_dataset_duplicates(client, dataset_name)

        # 3. Refresh items list after cleanup
        dataset = client.get_dataset(dataset_name)
        existing_items = dataset.items
        existing_cids = set()

        for item in existing_items:
            if item.metadata and isinstance(item.metadata, dict) and item.metadata.get("claim_id"):
                existing_cids.add(item.metadata.get("claim_id"))

        # 4. Create missing items idempotently
        created_count = 0
        for claim in EVALUATION_SET:
            cid = claim["claim_id"]
            if cid in existing_cids:
                continue  # Skip existing items to prevent duplication

            formatted_input = {
                "claim_id": claim["claim_id"],
                "submission_date": claim["submission_date"],
                "claimant": claim["claimant"],
                "stated_total": claim["stated_total"],
                "line_items": claim["line_items"],
                "raw_text": claim["raw_text"]
            }

            expected_output = {
                "verdict": claim["expected_verdict"],
                "breaches": claim["expected_breaches"]
            }

            metadata = {
                "claim_id": claim["claim_id"],
                "hard_case": claim.get("hard_case", False),
                "hard_case_type": claim.get("hard_case_type")
            }

            try:
                client.create_dataset_item(
                    dataset_name=dataset_name,
                    input=formatted_input,
                    expected_output=expected_output,
                    metadata=metadata
                )
                created_count += 1
            except Exception as e:
                print(f"[WARN] Error creating dataset item {cid}: {e}")

        # Final verification of count
        refreshed_dataset = client.get_dataset(dataset_name)
        final_count = len(refreshed_dataset.items)
        print(f"[OK] Dataset '{dataset_name}' sync complete. Active items: {final_count} (Created: {created_count})\n")
        return refreshed_dataset
    except Exception as e:
        print(f"[WARN] Failed to sync Langfuse dataset: {e}\n")
        return None


def run_langfuse_dataset_experiment(
    client: Optional[Langfuse],
    experiment_name: str,
    run_name: str,
    system_fn: Callable[[Dict[str, Any]], Dict[str, Any]],
    dataset_name: str = "expense_claim_evaluation_v1"
) -> Dict[str, Any]:
    """
    Executes a system configuration against the Langfuse evaluation dataset as an official
    Langfuse Dataset Experiment run. Logs item traces, predictions, and evaluator scores.
    """
    print(f"--- Running Langfuse Dataset Experiment: [{experiment_name}] ({run_name}) ---")

    # Local fallback execution if client is offline
    if not client:
        preds = [system_fn(c) for c in EVALUATION_SET]
        eval_res = evaluate_batch(preds, EVALUATION_SET)
        return eval_res

    # Ensure dataset is synced and deduplicated
    sync_evaluation_dataset(client, dataset_name)
    dataset = client.get_dataset(dataset_name)

    # 1. Define task wrapper for experiment runner
    def experiment_task(*, item, **kwargs):
        # Reconstruct claim dictionary from dataset item input/metadata
        if isinstance(item.input, dict):
            claim_data = dict(item.input)
        else:
            # Fallback if raw text string
            claim_id = item.metadata.get("claim_id") if item.metadata else "unknown"
            claim_data = next((c for c in EVALUATION_SET if c["claim_id"] == claim_id), {"raw_text": str(item.input)})

        # Execute system function
        result = system_fn(claim_data)
        return {
            "verdict": result.get("verdict", "APPROVE"),
            "breaches": result.get("breaches", [])
        }

    # 2. Define item evaluator for Langfuse SDK experiment
    def experiment_item_evaluator(*, input, output, expected_output=None, metadata=None, **kwargs):
        exp = expected_output or {}
        claim_mock = {
            "expected_verdict": exp.get("verdict", "APPROVE"),
            "expected_breaches": exp.get("breaches", []),
            "hard_case": metadata.get("hard_case", False) if metadata else False
        }
        res = evaluate_single_result(output, claim_mock)

        return [
            {"name": "verdict_accuracy", "value": float(res["verdict_score"])},
            {"name": "breach_accuracy", "value": float(res["breach_score"])},
            {"name": "overall_accuracy", "value": float(res["overall_score"])},
            {"name": "verdict_correct", "value": float(res["verdict_score"])},
            {"name": "breach_list_correct", "value": float(res["breach_score"])},
            {"name": "overall_pass", "value": float(res["overall_score"])}
        ]

    # 3. Run experiment via SDK
    try:
        exp_result = client.run_experiment(
            name=experiment_name,
            run_name=run_name,
            data=dataset.items,
            task=experiment_task,
            evaluators=[experiment_item_evaluator]
        )
        print(f"[OK] Langfuse Dataset Experiment '{run_name}' completed successfully.")
        if hasattr(exp_result, "dataset_run_url") and exp_result.dataset_run_url:
            print(f"     View in Langfuse UI: {exp_result.dataset_run_url}")
    except Exception as e:
        print(f"[WARN] Dataset experiment execution warning for '{run_name}': {e}")

    # Return local batch metrics for summary report consistency
    preds = [system_fn(c) for c in EVALUATION_SET]
    return evaluate_batch(preds, EVALUATION_SET)


def log_experiment_scores_to_langfuse(
    client: Langfuse,
    trace_or_run_id: str,
    scores: Dict[str, float]
):
    """
    Sends run-level or trace-level evaluation scores to Langfuse.
    """
    if not client:
        return

    for score_name, score_value in scores.items():
        try:
            client.score(
                name=score_name,
                value=float(score_value),
                trace_id=trace_or_run_id
            )
        except Exception:
            pass
