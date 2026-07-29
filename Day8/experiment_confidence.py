"""
Day 8 — Confidence Scoring & Human Review Routing Experiment
Simulates logprob-based confidence extraction and automated routing
for support ticket predictions.
"""

import sys
import logging
from dataclasses import dataclass
from pathlib import Path

# Ensure UTF-8 output encoding for cross-platform terminal compatibility
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


@dataclass
class TicketPrediction:
    """Dataclass holding ticket classification, confidence score, and routing status."""
    ticket_id: int
    text_snippet: str
    predicted_category: str
    confidence_score: float
    routing_action: str


def run_confidence_experiment():
    """Evaluates confidence score threshold routing for human review."""
    logging.info("Starting Day 8 Confidence Scoring & Routing Experiment...")

    # Simulated dataset of support tickets
    # Note: Logprob confidence scores are simulated for demonstration purposes
    sample_tickets = [
        (101, "Payment failed on checkout page. Card error 402.", "Billing", 0.96),
        (102, "Need to update company billing address on tax invoice.", "Billing", 0.89),
        (103, "System threw 500 internal server error on export button.", "Technical", 0.93),
        (104, "App feels a bit laggy sometimes when running on mobile data.", "General", 0.62),
        (105, "Could you maybe assist with modifying profile settings?", "General", 0.68),
    ]

    human_review_threshold = 0.70
    predictions = []

    print("\n" + "=" * 96)
    print("                      Day 8 Confidence Scoring & Human Review Routing                     ")
    print("=" * 96)
    print(f"Simulation Note: Logprob token probabilities are simulated to demonstrate threshold routing.")
    print(f"Routing Rule   : If Confidence < {human_review_threshold:.2f} -> Send to Human Review, else Accept.\n")

    print(f"{'ID':<6} | {'Ticket Snippet':<48} | {'Prediction':<10} | {'Confidence':<10} | {'Action':<22}")
    print("-" * 96)

    human_count = 0
    accepted_count = 0

    for tid, text, category, conf in sample_tickets:
        if conf < human_review_threshold:
            action = "Send to Human Review"
            human_count += 1
        else:
            action = "Accept Prediction"
            accepted_count += 1

        snippet = text[:45] + "..." if len(text) > 45 else text
        predictions.append(TicketPrediction(tid, snippet, category, conf, action))

        print(f"{tid:<6} | {snippet:<48} | {category:<10} | {conf:<10.2f} | {action:<22}")

    print("=" * 96)

    print("\nRouting Summary:")
    print(f"  • Total Evaluated      : {len(sample_tickets)}")
    print(f"  • Accepted Predictions : {accepted_count} (Confidence >= {human_review_threshold:.2f})")
    print(f"  • Sent to Human Review : {human_count} (Confidence < {human_review_threshold:.2f})")
    print("  • Impact               : Low-confidence predictions are safely routed to human agents, preventing automated misclassifications.\n")


if __name__ == "__main__":
    run_confidence_experiment()
