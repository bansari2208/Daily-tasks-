import re
from .models import PriorityResult

HIGH_KEYWORDS = {"failed", "charge", "crash", "down", "breach", "api_key", "twice", "error 500"}
MEDIUM_KEYWORDS = {"update", "cannot", "slow", "issue", "reset", "help"}


def predict_priority(ticket_text: str, category: str = "General") -> PriorityResult:
    """
    Predicts urgency level (HIGH, MEDIUM, LOW) for a support ticket.
    """
    if not ticket_text or not ticket_text.strip():
        raise ValueError("Ticket text cannot be empty or blank.")

    text_lower = ticket_text.lower()

    # Check for HIGH priority keywords or critical billing signals
    if any(re.search(r"\b" + re.escape(kw) + r"\b", text_lower) for kw in HIGH_KEYWORDS):
        return PriorityResult(
            priority="HIGH",
            score=0.90,
            reason="Ticket contains urgent outage or payment failure keywords.",
        )

    if category == "Billing":
        return PriorityResult(
            priority="HIGH",
            score=0.85,
            reason="Billing category ticket requiring high priority attention.",
        )

    # Check for MEDIUM priority keywords
    if any(re.search(r"\b" + re.escape(kw) + r"\b", text_lower) for kw in MEDIUM_KEYWORDS):
        return PriorityResult(
            priority="MEDIUM",
            score=0.60,
            reason="Ticket contains standard technical or account request keywords.",
        )

    # Default to LOW priority
    return PriorityResult(
        priority="LOW",
        score=0.30,
        reason="General inquiry or low urgency request.",
    )
