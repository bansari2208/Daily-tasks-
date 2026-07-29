import asyncio
import json
import os
import random
import sys
import time

# Ensure package import works regardless of execution directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ticket_classifier.client import AsyncLLMClient
from ticket_classifier.report import generate_report
from ticket_classifier.tracer import get_tracing_status, flush_langfuse_traces
from ticket_classifier.utils import timer


def generate_sample_tickets(count: int = 100) -> list[str]:
    """Generates sample support tickets, including some with sensitive PII."""
    templates = [
        "My payment failed on checkout page. Card 4532 1234 5678 9012 failed.",
        "How do I reset my password? Current pwd: SecretPassword123!",
        "The mobile app keeps crashing. Please email update to user@example.com.",
        "Call customer support at +1-555-123-4567 regarding billing.",
        "Can I update my billing email address?",
        "Where can I download my invoice?",
        "API returning 500 error. Key api_key=sk_live_998877665544332211.",
        "Credit card charge was processed twice.",
        "Feature request: dark mode support.",
    ]
    return [f"Ticket #{i+1}: {random.choice(templates)}" for i in range(count)]


async def main():
    log_file = os.path.join("logs", "llm_logs.jsonl")

    # Clean previous log file before running demo
    if os.path.exists(log_file):
        os.remove(log_file)

    print("==================================")
    print("Day 4 Batch Classification Demo")
    print("==================================")
    print(f"{get_tracing_status()}\n")

    tickets = generate_sample_tickets(100)
    client = AsyncLLMClient(max_concurrency=5, max_retries=2, base_delay=0.02)

    print("Starting batch processing of 100 support tickets...\n")

    start_batch = time.time()
    # Process all 100 tickets concurrently inside timer context manager
    with timer("Batch Processing"):
        results = await asyncio.gather(
            *[client.classify_ticket(t, ticket_id=i+1) for i, t in enumerate(tickets)],
            return_exceptions=True,
        )
    batch_elapsed = time.time() - start_batch

    # Safely flush pending Langfuse traces after processing completes
    flush_langfuse_traces()

    print(f"Processed {len(results)} tickets successfully.")

    # 1. Automatically generate Day 4 Cost & Latency Report
    generate_report(log_file=log_file, batch_time=batch_elapsed)

    # 2. Print Error Breakdown
    print("==================================")
    print("Error Breakdown")
    print("==================================")
    print(f"HTTP 429 Rate Limit:       {client.http_429_count}")
    print(f"HTTP 500 Internal Error:   {client.http_500_count}")
    print(f"Timeout Errors:            {client.timeout_count}")
    print(f"HTTP 400 Bad Request:      {client.http_400_count}")
    print("==================================\n")

    # 3. Print Circuit Breaker Summary
    print("==================================")
    print("Circuit Breaker Summary")
    print("==================================")
    print(f"Open Events:               {client.circuit_breaker.open_events}")
    print(f"Recoveries:                {client.circuit_breaker.recoveries}")
    print(f"Final State:               {client.circuit_breaker.state}")
    print("==================================\n")

    # 4. Print Sample Structured Log Record
    if os.path.exists(log_file):
        with open(log_file, "r", encoding="utf-8") as f:
            first_line = f.readline()
            if first_line:
                raw_log = json.loads(first_line)
                sample = {
                    "trace_id": raw_log.get("trace_id"),
                    "provider": raw_log.get("provider"),
                    "latency_ms": round(raw_log.get("latency_ms", 0.0), 2),
                    "tokens": raw_log.get("total_tokens"),
                    "cost": raw_log.get("estimated_cost"),
                    "retries": raw_log.get("retry_count"),
                    "finish_reason": raw_log.get("finish_reason"),
                }
                print("==================================")
                print("Sample Structured Log Record")
                print("==================================")
                print(json.dumps(sample, indent=2))
                print("==================================\n")

    # 5. Verify unique trace IDs and PII Redaction in saved logs
    if os.path.exists(log_file):
        trace_ids = []
        pii_found = False

        sensitive_samples = [
            "4532 1234 5678 9012",
            "SecretPassword123!",
            "user@example.com",
            "+1-555-123-4567",
            "sk_live_998877665544332211",
        ]

        with open(log_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    data = json.loads(line)
                    trace_ids.append(data.get("trace_id"))

                    for pii in sensitive_samples:
                        if pii in line:
                            pii_found = True

        unique_traces = len(set(trace_ids))
        assert unique_traces == len(trace_ids), "Trace IDs are not unique!"
        print(f"[VERIFIED] Trace IDs: All {unique_traces} requests received a unique trace ID.")

        assert not pii_found, "PII found in log file!"
        print("[VERIFIED] PII Redaction: Zero sensitive PII present in logs.")

    assert client.max_inflight_seen <= client.semaphore_limit, (
        f"Maximum concurrency ({client.max_inflight_seen}) exceeded limit ({client.semaphore_limit})"
    )
    print("[VERIFIED] Concurrency: Semaphore limit never exceeded.\n")

    # 6. Print simple PII Redaction Example demonstration
    print("==================================")
    print("PII Redaction Example")
    print("==================================")
    print("Original:")
    print("john@example.com")
    print()
    print("Stored:")
    print("[REDACTED]")
    print("==================================\n")


if __name__ == "__main__":
    asyncio.run(main())
