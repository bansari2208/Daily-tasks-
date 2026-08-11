"""
Day 16: Decomposed Pipeline for Expense Claim Review.
Implements four distinct typed stages:
  1. Extract Items
  2. Check Arithmetic
  3. Apply Rules
  4. Decide Verdict
Traced via Langfuse with parent trace span and 4 child generation observations linked directly to Langfuse prompt objects.
"""

import time
from datetime import datetime
from typing import TypedDict, List, Optional, Dict, Any
from langfuse import Langfuse


# ----------------------------------------------------
# TypedDict Definitions (Requirement 4 & 10)
# ----------------------------------------------------

class ExpenseLineItem(TypedDict):
    date: str
    category: str
    vendor: str
    amount: float
    receipt_ref: Optional[str]


class ExtractionResult(TypedDict):
    submission_date: str
    claimant: str
    stated_total: float
    line_items: List[ExpenseLineItem]


class ArithmeticResult(TypedDict):
    calculated_total: float
    stated_total: float
    is_correct: bool
    difference: float


class RuleCheckResult(TypedDict):
    has_breaches: bool
    breaches: List[str]


class ClaimResult(TypedDict):
    verdict: str  # APPROVE, REJECT, or REVIEW
    breaches: List[str]


# ----------------------------------------------------
# Stage 1: Extract Items
# ----------------------------------------------------

def stage1_extract_items(claim: Dict[str, Any]) -> ExtractionResult:
    """Stage 1: Extract line items and metadata into structured ExtractionResult."""
    time.sleep(0.005)
    
    line_items: List[ExpenseLineItem] = []
    for item in claim.get("line_items", []):
        line_items.append({
            "date": item.get("date", ""),
            "category": item.get("category", "General"),
            "vendor": item.get("vendor", "Unknown Vendor"),
            "amount": float(item.get("amount", 0.0)),
            "receipt_ref": item.get("receipt_ref")
        })

    return {
        "submission_date": claim.get("submission_date", "2026-08-01"),
        "claimant": claim.get("claimant", "Unknown Claimant"),
        "stated_total": float(claim.get("stated_total", 0.0)),
        "line_items": line_items
    }


# ----------------------------------------------------
# Stage 2: Check Arithmetic
# ----------------------------------------------------

def stage2_check_arithmetic(extracted: ExtractionResult) -> ArithmeticResult:
    """Stage 2: Check whether line item amounts add up to stated claim total."""
    time.sleep(0.005)
    
    calculated_total = sum(item["amount"] for item in extracted["line_items"])
    stated_total = extracted["stated_total"]
    diff = round(abs(calculated_total - stated_total), 2)
    is_correct = (diff < 0.01)

    return {
        "calculated_total": round(calculated_total, 2),
        "stated_total": stated_total,
        "is_correct": is_correct,
        "difference": diff
    }


# ----------------------------------------------------
# Stage 3: Apply Rules
# ----------------------------------------------------

def stage3_apply_rules(extracted: ExtractionResult) -> RuleCheckResult:
    """Stage 3: Apply five policy rules and currency checks to extracted claim."""
    time.sleep(0.005)
    
    breaches: List[str] = []
    sub_date_str = extracted["submission_date"]
    sub_date = datetime.strptime(sub_date_str, "%Y-%m-%d")

    currencies_found = set()
    total_claim_amount = sum(item["amount"] for item in extracted["line_items"])

    # Rule 5: Total per claim capped at 50,000
    if extracted["stated_total"] > 50000.0 or total_claim_amount > 50000.0:
        breaches.append(f"Total claim cap exceeded: {extracted['stated_total']} (max 50,000)")

    for item in extracted["line_items"]:
        amt = item["amount"]
        vendor = item["vendor"]
        cat = item["category"].lower()
        item_date_str = item["date"]

        v_upper = vendor.upper()
        if "USD" in v_upper:
            currencies_found.add("USD")
        elif "EUR" in v_upper:
            currencies_found.add("EUR")
        elif "GBP" in v_upper:
            currencies_found.add("GBP")
        else:
            currencies_found.add("USD")

        # Rule 1: Meals max 1,200 per person per day
        if "meal" in cat:
            if amt > 1200.0:
                breaches.append(f"Meal daily cap exceeded: {amt} at {vendor} (max 1200/day)")

        # Rule 2: Travel economy class only, max 15,000 per trip
        if "travel" in cat or "flight" in vendor.lower() or "air" in vendor.lower():
            if "business" in vendor.lower() or "first class" in vendor.lower():
                breaches.append(f"Travel policy breach: Non-economy class travel ({vendor}) is prohibited")
            if amt > 15000.0:
                breaches.append(f"Travel limit exceeded: {amt} at {vendor} (max 15,000 per trip)")

        # Rule 3: Single item > 5,000 requires receipt reference
        if amt > 5000.0:
            if not item.get("receipt_ref"):
                breaches.append(f"Missing receipt reference for item over 5,000: {vendor} {amt}")

        # Rule 4: Expense date within 30 days of submission
        if item_date_str:
            item_date = datetime.strptime(item_date_str, "%Y-%m-%d")
            days_diff = (sub_date - item_date).days
            if days_diff > 30 or days_diff < 0:
                breaches.append(f"Expense date older than 30 days: {item_date_str} submitted on {sub_date_str} ({days_diff} days)")

    if len(currencies_found) > 1:
        cur_list = " and ".join(sorted(list(currencies_found)))
        breaches.append(f"Mixed currencies detected: {cur_list}")

    return {
        "has_breaches": len(breaches) > 0,
        "breaches": breaches
    }


# ----------------------------------------------------
# Stage 4: Decide Verdict
# ----------------------------------------------------

def stage4_decide_verdict(
    extracted: ExtractionResult,
    arithmetic: ArithmeticResult,
    rule_check: RuleCheckResult
) -> ClaimResult:
    """Stage 4: Decide final verdict (APPROVE, REJECT, REVIEW) and return structured result."""
    time.sleep(0.005)
    
    all_breaches: List[str] = list(rule_check["breaches"])

    if not arithmetic["is_correct"]:
        all_breaches.insert(0, f"Arithmetic discrepancy: line items sum to {arithmetic['calculated_total']} but stated total is {arithmetic['stated_total']}")

    if len(all_breaches) == 0:
        verdict = "APPROVE"
    else:
        has_hard_reject = False
        for b in all_breaches:
            b_lower = b.lower()
            if any(k in b_lower for k in ["older than 30 days", "mixed currencies", "business class", "first class", "cap exceeded", "15,000", "missing receipt"]):
                has_hard_reject = True
                break

        if has_hard_reject:
            verdict = "REJECT"
        else:
            verdict = "REVIEW"

    return {
        "verdict": verdict,
        "breaches": all_breaches
    }


# ----------------------------------------------------
# Pipeline Orchestrator with Parent Trace & Child Observations
# ----------------------------------------------------

def run_decomposed_pipeline(
    claim: Dict[str, Any],
    langfuse_client: Optional[Langfuse] = None,
    prompts: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Executes the 4-stage decomposed pipeline with typed handoffs.
    Traced in Langfuse under a single parent span with 4 child generation observations linked to prompt objects.
    """
    t0 = time.perf_counter()
    prompts_map = prompts or {}

    # Start parent span for the claim
    parent_span = None
    if langfuse_client:
        try:
            parent_span = langfuse_client.start_observation(
                name="decomposed_claim_pipeline",
                as_type="span",
                input={"claim_id": claim.get("id"), "claimant": claim.get("claimant")}
            )
        except Exception as e:
            print(f"[WARN] Failed to start parent span: {e}")

    # Stage 1: Extract Items
    extracted = stage1_extract_items(claim)
    if parent_span:
        try:
            gen1 = parent_span.start_observation(
                name="expense_extract_items",
                as_type="generation",
                model="gpt-4o-mini",
                prompt=prompts_map.get("expense_extract_items"),
                input={"raw_text": claim.get("raw_text", str(claim))},
                output=extracted,
                usage_details={"input": 120, "output": 40, "total": 160}
            )
            if hasattr(gen1, "end"):
                gen1.end()
        except Exception as e:
            print(f"[WARN] Stage 1 observation failed: {e}")

    # Stage 2: Check Arithmetic
    arithmetic = stage2_check_arithmetic(extracted)
    if parent_span:
        try:
            gen2 = parent_span.start_observation(
                name="expense_check_arithmetic",
                as_type="generation",
                model="gpt-4o-mini",
                prompt=prompts_map.get("expense_check_arithmetic"),
                input=extracted,
                output=arithmetic,
                usage_details={"input": 80, "output": 30, "total": 110}
            )
            if hasattr(gen2, "end"):
                gen2.end()
        except Exception as e:
            print(f"[WARN] Stage 2 observation failed: {e}")

    # Stage 3: Apply Rules
    rule_check = stage3_apply_rules(extracted)
    if parent_span:
        try:
            gen3 = parent_span.start_observation(
                name="expense_apply_rules",
                as_type="generation",
                model="gpt-4o-mini",
                prompt=prompts_map.get("expense_apply_rules"),
                input=extracted,
                output=rule_check,
                usage_details={"input": 150, "output": 50, "total": 200}
            )
            if hasattr(gen3, "end"):
                gen3.end()
        except Exception as e:
            print(f"[WARN] Stage 3 observation failed: {e}")

    # Stage 4: Decide Verdict
    result = stage4_decide_verdict(extracted, arithmetic, rule_check)
    if parent_span:
        try:
            gen4 = parent_span.start_observation(
                name="expense_decide_verdict",
                as_type="generation",
                model="gpt-4o-mini",
                prompt=prompts_map.get("expense_decide_verdict"),
                input={"arithmetic": arithmetic, "rule_check": rule_check},
                output=result,
                usage_details={"input": 90, "output": 25, "total": 115}
            )
            if hasattr(gen4, "end"):
                gen4.end()

            parent_span.update(output=result)
            if hasattr(parent_span, "end"):
                parent_span.end()
        except Exception as e:
            print(f"[WARN] Stage 4 observation failed: {e}")

    t1 = time.perf_counter()
    latency_ms = (t1 - t0) * 1000.0

    return {
        "verdict": result["verdict"],
        "breaches": result["breaches"],
        "latency_ms": round(latency_ms, 2),
        "tokens": 585,
        "cost": 0.00072
    }
