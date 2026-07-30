"""
Inference Control Playbook Module for Ticket Classifier.
"""

PLAYBOOK_VERSION = "v1.1"
PLAYBOOK_LAST_UPDATED = "2026-07-30"


def detect_task_type(ticket_text: str) -> str:
    """
    Detects ticket task category: SIMPLE_CLASSIFICATION, BILLING, TECHNICAL, or MULTI_STEP_REASONING.
    Uses simple keyword matching suitable for junior developer maintenance.
    """
    if not ticket_text:
        return "SIMPLE_CLASSIFICATION"

    text_lower = ticket_text.lower()

    # Multi-step reasoning keywords (complex financial/technical edge cases or multi-request tickets)
    multi_step_keywords = [
        "refund", "404", "invoice", "finance", "tax", "escalation", "charged twice", "multiple issues"
    ]
    for kw in multi_step_keywords:
        if kw in text_lower:
            return "MULTI_STEP_REASONING"

    if ("and" in text_lower and len(ticket_text) > 120) or len(ticket_text) > 180:
        return "MULTI_STEP_REASONING"

    # Billing keywords
    billing_keywords = ["payment", "card", "billing", "checkout", "subscription"]
    for kw in billing_keywords:
        if kw in text_lower:
            return "BILLING"

    # Technical keywords
    technical_keywords = ["crash", "error", "api", "bug", "technical", "login issue"]
    for kw in technical_keywords:
        if kw in text_lower:
            return "TECHNICAL"

    return "SIMPLE_CLASSIFICATION"


def get_recommended_model(task_type: str) -> str:
    """Returns the recommended LLM model for the detected task type."""
    t_type = task_type.upper()
    if t_type == "MULTI_STEP_REASONING":
        return "o3-mini"
    elif t_type in ("BILLING", "TECHNICAL"):
        return "GPT-4.1 Mini"
    return "GPT-4.1 Nano"


def get_model_reason(task_type: str) -> str:
    """Returns a clear explanation of why the selected model was chosen."""
    t_type = task_type.upper()
    if t_type == "MULTI_STEP_REASONING":
        return "Best for complex multi-step reasoning"
    elif t_type == "BILLING":
        return "Balanced cost and precision for payment/invoice inquiries"
    elif t_type == "TECHNICAL":
        return "Best balance of cost and accuracy"
    return "Fastest and cheapest for routine tickets"


def get_model_tradeoffs(task_type: str) -> dict:
    """Returns detailed model selection trade-offs (selected model, why selected, why not alternatives)."""
    t_type = task_type.upper()
    if t_type == "MULTI_STEP_REASONING":
        return {
            "selected": "o3-mini",
            "why_selected": "Best for complex multi-step rule evaluation and reasoning.",
            "why_not_nano": "Nano lacks deep reasoning capabilities for edge cases.",
            "why_not_mini": "Mini is cheaper but has lower accuracy on multi-step reasoning.",
        }
    elif t_type == "BILLING":
        return {
            "selected": "GPT-4.1 Mini",
            "why_selected": "Balanced cost and precision for payment and invoice inquiries.",
            "why_not_nano": "Nano may occasionally misclassify complex billing nuances.",
            "why_not_reasoning": "o3-mini adds unnecessary latency and cost for routine billing queries.",
        }
    elif t_type == "TECHNICAL":
        return {
            "selected": "GPT-4.1 Mini",
            "why_selected": "Best balance of cost and accuracy for technical error extraction.",
            "why_not_nano": "Nano may miss complex technical error relationships.",
            "why_not_reasoning": "o3-mini adds unnecessary cost for routine technical queries.",
        }
    return {
        "selected": "GPT-4.1 Nano",
        "why_selected": "Fastest and cheapest model for routine support tickets.",
        "why_not_mini": "Mini adds extra cost without improving simple classification accuracy.",
        "why_not_reasoning": "o3-mini is far too expensive for simple routine queries.",
    }


def get_default_temperature(task_type: str) -> float:
    """Returns task-specific default temperature."""
    if task_type.upper() == "MULTI_STEP_REASONING":
        return 0.2
    return 0.0


def get_default_top_p(task_type: str) -> float:
    """Returns task-specific default top-p hyperparameter."""
    return 0.7


def get_playbook_version() -> str:
    """Returns the active playbook version."""
    return PLAYBOOK_VERSION


def get_playbook_last_updated() -> str:
    """Returns the last updated date of the playbook."""
    return PLAYBOOK_LAST_UPDATED
