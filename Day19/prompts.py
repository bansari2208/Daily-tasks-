"""
Day 19 - Prompt Variants Registry & Dynamic Optimiser Module.

Defines the 4 baseline/controlled prompt variants:
- Baseline: Simple unconstrained prompt
- V2: Structured output instructions (JSON schema)
- V3: Few-shot classification examples
- V4: Chain-of-Thought (CoT) step-by-step reasoning

Also provides dynamic prompt construction for Optimized_Largest_Failure.
"""

from typing import Dict, Any

PROMPT_VARIANTS: Dict[str, str] = {
    "Baseline": (
        "Classify the following customer support ticket into one of these categories: Billing, Technical, Account, General.\n"
        "Ticket: {ticket_text}\n"
        "Respond with the category name."
    ),
    "V2": (
        "You are an automated support ticket classifier.\n"
        "Classify the customer support ticket into EXACTLY ONE of the following categories:\n"
        "- Billing\n"
        "- Technical\n"
        "- Account\n"
        "- General\n\n"
        "Output JSON in this format:\n"
        '{"category": "<Billing|Technical|Account|General>", "reasoning": "<brief summary>"}\n\n'
        "Ticket text:\n{ticket_text}"
    ),
    "V3": (
        "Classify the customer support ticket into: Billing, Technical, Account, or General.\n\n"
        "Examples:\n"
        'Input: "I was charged twice on my invoice." -> Category: Billing\n'
        'Input: "API endpoint returns 500 error." -> Category: Technical\n'
        'Input: "Reset my 2FA security settings." -> Category: Account\n'
        'Input: "What are your business hours?" -> Category: General\n\n'
        "Ticket text: {ticket_text}\n"
        'Output JSON format: {"category": "<category_name>", "reasoning": "<explanation>"}'
    ),
    "V4": (
        "Analyze the customer support ticket step-by-step before classifying.\n\n"
        "Step 1: Identify key keywords and user intent.\n"
        "Step 2: Compare intent against available categories: Billing, Technical, Account, General.\n"
        "Step 3: Select the single best matching category.\n\n"
        "Ticket text: {ticket_text}\n\n"
        'Output JSON format: {"step_by_step_analysis": "<analysis>", "category": "<category_name>"}'
    )
}


def build_optimized_prompt(largest_failure_class: str) -> str:
    """
    Dynamically constructs the Optimized_Largest_Failure prompt targeting the actual largest failure class.

    Args:
        largest_failure_class: The category string with the highest number of errors (e.g. 'Billing', 'Technical', 'Account', 'General').

    Returns:
        Optimized prompt string with specialized disambiguation rules.
    """
    rules = {
        "Billing": (
            "SPECIAL RULE FOR BILLING: Any ticket mentioning payments, invoices, credit card charges, refunds, receipts, "
            "subscription renewals, pricing credits, or billing disputes MUST be classified as 'Billing', even if technical terms or errors are present."
        ),
        "Technical": (
            "SPECIAL RULE FOR TECHNICAL: Any ticket mentioning API errors, HTTP status codes, server timeouts, database failures, "
            "SSL certificates, software crashes, latency, or system bugs MUST be classified as 'Technical'."
        ),
        "Account": (
            "SPECIAL RULE FOR ACCOUNT: Any ticket mentioning login issues, 2FA recovery, password resets, email updates, "
            "account lockouts, workspace transfers, or SSO/SAML login errors MUST be classified as 'Account'."
        ),
        "General": (
            "SPECIAL RULE FOR GENERAL: Any ticket inquiring about business hours, product roadmaps, privacy policies, "
            "discounts, or courtesy thank-you notes MUST be classified as 'General'."
        )
    }

    target_rule = rules.get(
        largest_failure_class,
        f"SPECIAL DISAMBIGUATION RULE: Pay extra attention to accurately classifying '{largest_failure_class}' tickets."
    )

    optimized_prompt = (
        "You are an expert enterprise support ticket classifier.\n"
        "Classify the ticket into EXACTLY ONE category: Billing, Technical, Account, General.\n\n"
        f"{target_rule}\n\n"
        "Step 1: Analyze user intent.\n"
        "Step 2: Check against category rules.\n"
        "Step 3: Select final category.\n\n"
        "Ticket text: {ticket_text}\n\n"
        'Output JSON format: {"category": "<Billing|Technical|Account|General>", "reasoning": "<explanation>"}'
    )

    return optimized_prompt
