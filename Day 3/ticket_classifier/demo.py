import asyncio
import time
import random
import sys
import os

# Ensure package import works regardless of execution directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ticket_classifier.client import AsyncLLMClient


def generate_sample_tickets(count: int = 100) -> list[str]:
    """Generates a list of realistic sample support ticket descriptions."""
    ticket_templates = [
        "My payment failed on checkout page.",
        "How do I reset my password?",
        "The mobile app keeps crashing on launch.",
        "Can I update my billing email address?",
        "Where can I download my invoice?",
        "API returning 500 error on webhook endpoint.",
        "Credit card charge was processed twice.",
        "Feature request: dark mode support."
    ]
    return [f"Ticket #{i+1}: {random.choice(ticket_templates)}" for i in range(count)]


async def main():
    tickets = generate_sample_tickets(100)
    client = AsyncLLMClient(max_concurrency=5, max_retries=2, base_delay=0.02)

    print("Starting batch processing of 100 support tickets...")
    start_time = time.time()

    # Process all 100 tickets concurrently
    results = await asyncio.gather(
        *[client.classify_ticket(t, ticket_id=i+1) for i, t in enumerate(tickets)],
        return_exceptions=True
    )
    
    elapsed_time = time.time() - start_time
    processed = len(results)

    # Filter fallback and failed requests for summary
    fallback_items = [r for r in results if isinstance(r, dict) and r.get("status") == "fallback_success"]
    failed_items = [r for r in results if isinstance(r, dict) and r.get("status") == "failed"]

    print("\n========================================")
    print("Day 3 Demo Report")
    print("========================================")
    print(f"Processed: {processed}")
    print(f"Primary Success: {client.primary_success_count}")
    print(f"Fallback Success: {client.fallback_success_count}")
    print(f"Failed: {client.failed_count}")
    print(f"Retries: {client.total_retries}")
    print(f"Maximum Concurrent Requests: {client.max_inflight_seen}")
    print(f"Execution Time: {elapsed_time:.1f} seconds")
    print("========================================\n")

    # Print short summary of requests requiring fallback
    if fallback_items:
        print("Fallback Requests")
        for item in fallback_items:
            t_id = item.get("ticket_id", "?")
            reason = item.get("fallback_reason", "Unknown")
            print(f"Ticket {t_id} -> {reason}")
        print()

    # Print summary of permanently failed requests
    if failed_items:
        print("Failed Requests")
        for item in failed_items:
            t_id = item.get("ticket_id", "?")
            reason = item.get("fallback_reason", "Unknown")
            print(f"Ticket {t_id} -> {reason} after maximum retries")
        print()

    # Explicitly verify semaphore limit
    assert client.max_inflight_seen <= client.semaphore_limit, (
        f"Maximum concurrency ({client.max_inflight_seen}) exceeded limit ({client.semaphore_limit})"
    )
    print("[VERIFIED] Semaphore verified: maximum concurrency never exceeded the configured limit.\n")


if __name__ == "__main__":
    asyncio.run(main())
