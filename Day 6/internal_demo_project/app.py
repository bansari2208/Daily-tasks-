import asyncio
from ticket_classifier import (
    AsyncLLMClient,
    SupportTicket,
    predict_priority,
    redact_text,
    generate_report,
    flush_langfuse_traces,
)


async def main():
    print("==================================")
    print("Internal Demo Project App")
    print("==================================")
    print("Consuming local 'ticket_classifier' package from an independent project.\n")

    # 1. Instantiate SupportTicket model from package
    ticket_input = SupportTicket(
        ticket_id=101,
        text="Card payment failed twice on checkout page. Card 4532 1234 5678 9012 failed.",
    )

    print(f"Original Ticket #{ticket_input.ticket_id}:")
    print(f"  {ticket_input.text}\n")

    # 2. Redact sensitive PII using exported package API
    clean_text = redact_text(ticket_input.text)
    print("Sanitized Ticket (PII Redacted):")
    print(f"  {clean_text}\n")

    # 3. Classify ticket using AsyncLLMClient from package
    client = AsyncLLMClient(max_concurrency=2, max_retries=1)
    print("Classifying ticket via AsyncLLMClient...")
    result = await client.classify_ticket(clean_text, ticket_id=ticket_input.ticket_id)

    print("\nClassification Result:")
    print(f"  |- Category: {result['category']}")
    print(f"  |- Provider: {result['provider']}")
    print(f"  +- Status:   {result['status']}")

    # 4. Predict ticket urgency using predict_priority exported API
    priority = predict_priority(clean_text, category=result["category"])
    print("\nPriority Prediction:")
    print(f"  |- Urgency Level: {priority.priority}")
    print(f"  |- Score:         {priority.score:.2f}")
    print(f"  +- Rationale:     {priority.reason}\n")

    # Flush trace observations & print cost report
    flush_langfuse_traces()

    print("==================================")
    print("Package Reusability Verified!")
    print("==================================\n")


if __name__ == "__main__":
    asyncio.run(main())

