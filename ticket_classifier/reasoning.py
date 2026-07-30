"""
Intelligent Model Routing & Complexity Analysis Module.
"""


def analyze_ticket_complexity(ticket_text: str) -> str:
    """
    Analyzes ticket content and returns complexity level: EASY, MEDIUM, or COMPLEX.
    Uses simple keyword matching rules suitable for junior developer maintenance.
    """
    if not ticket_text:
        return "EASY"

    text_lower = ticket_text.lower()

    # Complex keywords indicating multi-step reasoning or high-impact financial/technical edge cases
    complex_keywords = [
        "refund", "duplicate charge", "invoice", "finance",
        "tax", "404", "escalation", "multiple issues", "charged twice"
    ]

    # Medium complexity keywords
    medium_keywords = [
        "payment failed", "login issue", "subscription", "card", "checkout"
    ]

    # Check for complex triggers
    for kw in complex_keywords:
        if kw in text_lower:
            return "COMPLEX"

    # Multiple issue indicators or long tickets escalate to COMPLEX
    if ("and" in text_lower and len(ticket_text) > 120) or len(ticket_text) > 180:
        return "COMPLEX"

    # Check for medium triggers
    for kw in medium_keywords:
        if kw in text_lower:
            return "MEDIUM"

    return "EASY"


def should_use_reasoning_model(complexity: str) -> bool:
    """Returns True if the ticket requires an advanced Reasoning Model (o3-mini)."""
    return complexity.upper() == "COMPLEX"


def estimate_reasoning_tokens(complexity: str) -> int:
    """Returns estimated hidden reasoning tokens generated during test-time compute."""
    comp_upper = complexity.upper()
    if comp_upper == "COMPLEX":
        return 700
    elif comp_upper == "MEDIUM":
        return 150
    return 0
