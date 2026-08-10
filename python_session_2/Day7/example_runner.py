import asyncio
from ticket_classifier import (
    AsyncLLMClient,
    predict_priority,
    redact_text,
    generate_report,
    flush_langfuse_traces,
    get_tracing_status,
    timer,
)


async def main():
    print("==================================")
    print("External Package Integration Runner")
    print("==================================")
    print(f"{get_tracing_status()}\n")

    # Sample customer support tickets
    tickets = [
        "Card payment failed twice on checkout page. Card 4532 1234 5678 9012.",
        "How do I change my profile email address?",
        "Mobile app keeps crashing on startup. Please contact me at user@example.com.",
    ]

    # Initialize client from public package import
    client = AsyncLLMClient(max_concurrency=3, max_retries=1)

    print("Classifying tickets asynchronously...")
    with timer("External Runner Execution"):
        for i, text in enumerate(tickets, start=1):
            # 1. Redact PII before printing
            clean_text = redact_text(text)
            
            # 2. Classify ticket via package client
            result = await client.classify_ticket(clean_text, ticket_id=i)
            
            # 3. Predict urgency priority
            priority = predict_priority(clean_text, category=result.get("category", "General"))

            print(f"\n[Ticket #{i}] {clean_text}")
            print(f"  |- Category: {result['category']}")
            print(f"  |- Provider: {result['provider']}")
            print(f"  +- Priority: {priority.priority} (Score: {priority.score:.2f}) - {priority.reason}")

    # Flush traces & display cost report
    flush_langfuse_traces()
    generate_report()


if __name__ == "__main__":
    asyncio.run(main())

