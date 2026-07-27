# 🎫 Ticket Classifier (`ticket-classifier`)

A production-grade, resilient, async LLM ticket classification Python package. Built with **bounded concurrency**, **exponential retries**, **circuit breakers**, **PII redaction**, **structured JSON logging**, **cost reporting**, and **Langfuse v4 tracing**.

---

## 1. 📦 Package Overview

`ticket-classifier` is a lightweight, beginner-friendly Python package designed to handle support ticket processing asynchronously. It protects LLM workloads against rate limits (HTTP 429), server errors (HTTP 500), and outages using resilient design patterns while delivering observability out of the box.

---

## 2. ✨ Key Features

- **⚡ Async & Concurrent Execution**: Process hundreds of tickets concurrently using `asyncio` and `asyncio.Semaphore`.
- **🛡️ Resilience Patterns**:
  - Exponential backoff with random jitter for HTTP 500 and timeouts.
  - Automatic `Retry-After` header parsing for HTTP 429 rate limits.
  - 3-State **Circuit Breaker** (`CLOSED`, `OPEN`, `HALF-OPEN`).
  - Automatic failover to `MockFallbackProvider` on primary failure.
- **🔒 PII Redaction**: Automatic regex masking of emails, phone numbers, credit card numbers, passwords, and API keys.
- **📊 Analytics & Cost Report**: Summarizes requests, token usage, total/average cost, throughput, and P50/P95 latencies.
- **🔍 Langfuse Tracing**: Real-time trace tracking with session grouping, tags, and metadata.
- **🚨 Priority Prediction**: Fast heuristic priority classification (`HIGH`, `MEDIUM`, `LOW`).

---

## 3. ⚙️ Installation

Install the package locally in editable mode:

```bash
pip install -e .
```

Or install directly:

```bash
pip install .
```

---

## 4. 📁 Folder Structure

```text
ticket_classifier/
│
├── __init__.py         # Package entry point exposing top-level public API exports
├── models.py           # Typed Pydantic schemas (SupportTicket, ClassificationResult, LLMLogEntry)
├── client.py           # Resilient Async LLM client with retries, semaphore, and fallback
├── providers.py        # Primary & fallback mock providers
├── circuit_breaker.py  # 3-State circuit breaker
├── logger.py           # Structured JSONL logger with OpenTelemetry fields
├── report.py           # Batch analytics & cost report generator
├── redaction.py        # Regex-based PII masking
├── priority.py         # Priority prediction module
├── tracer.py           # Langfuse v4 & LangSmith tracing integrations
├── utils.py            # Context manager timer utility
├── demo.py             # 100-ticket batch demo implementation
├── test_*.py          # Automated unit test suite (26 unit tests)
├── .env               # Langfuse environment credentials
├── pyproject.toml      # Standard Python package build & metadata configuration
└── README.md           # Package documentation
```

---

## 5. 🚀 Quick Start Example

```python
import asyncio
from ticket_classifier import AsyncLLMClient, predict_priority

async def main():
    # 1. Initialize client
    client = AsyncLLMClient(max_concurrency=5, max_retries=2)

    # 2. Classify a ticket
    result = await client.classify_ticket("Payment failed on checkout page. Card 4532 1234 5678 9012 failed.", ticket_id=1)
    print("Classification:", result)

    # 3. Predict priority
    priority = predict_priority("Payment failed on checkout page", category=result["category"])
    print("Priority:", priority)

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 6. 📖 Example API Usage

### Public Package Exports (`from ticket_classifier import ...`)

```python
from ticket_classifier import (
    AsyncLLMClient,
    SupportTicket,
    ClassificationResult,
    predict_priority,
    generate_report,
    log_llm_call,
    redact_text,
    flush_langfuse_traces,
)

# PII Redaction
masked = redact_text("Contact user@example.com or call +1-555-0199")
# Output: "Contact [REDACTED] or call [REDACTED]"

# Priority Prediction
pred = predict_priority("API returning 500 error", category="Technical")
# Output: PriorityResult(priority='HIGH', score=0.9, reason="Ticket contains urgent outage or payment failure keywords.")

# Analytics Report
generate_report("logs/llm_logs.jsonl", batch_time=2.5)
```

---

## 7. 💰 Cost & Latency Reporting

The reporting module (`report.py`) parses structured logs (`logs/llm_logs.jsonl`) to compute operational metrics:

- **Token Aggregation**: Prompt tokens, completion tokens, total tokens.
- **Cost Metrics**: Total cost and average cost per request ($0.00010/token estimation).
- **Latency Analysis**: Mean latency, P50 (median), and P95 percentiles.
- **Throughput**: Requests per second (`req/s`).

### Run Standalone Report:
```bash
python report.py
```

---

## 8. 🔄 Retry Behaviour

The client manages transient network errors gracefully:

- **HTTP 500 & Timeouts**: Retries up to `max_retries` with exponential backoff and random jitter (`delay = base_delay * 2^attempt + jitter`).
- **HTTP 429 Rate Limits**: Inspects the `Retry-After` response header and pauses execution accordingly before retrying.
- **HTTP 400 Bad Requests**: Fails immediately without retrying (invalid prompt/input).

---

## 9. 🔌 Circuit Breaker Pattern

The 3-State Circuit Breaker prevents hammering failing downstream services:

```text
       [CLOSED] --(3 failures)--> [OPEN]
          ^                         |
          |                  (cooldown elapsed)
          |                         v
       (success) <---------- [HALF-OPEN]
```

- **CLOSED**: Normal state. Requests route to Primary Provider.
- **OPEN**: Triggered after 3 consecutive failures. Immediately routes requests to Fallback Provider without calling Primary.
- **HALF-OPEN**: Automatically transitions after `cooldown_seconds` (1.0s) to test a single trial request.

---

## 10. 🛰️ Langfuse Tracing Integration

Traces every LLM request to [Langfuse Cloud](https://hipaa.cloud.langfuse.com) using the native **v4 Python SDK**.

### Configuration (`ticket_classifier/.env`):
```env
LANGFUSE_PUBLIC_KEY="pk-lf-..."
LANGFUSE_SECRET_KEY="sk-lf-..."
LANGFUSE_BASE_URL="https://hipaa.cloud.langfuse.com"
```

### Trace Metadata:
Every trace includes:
- `session_id` (groups all batch execution traces into one session)
- `ticket_id`, `provider`, `retry_count`, `fallback_used`, `latency_ms`
- `tags`: `["day4", "ticket-classifier", "demo"]`

---

## 11. ⚠️ Failure Modes & Handling

| Failure Scenario | Resolution / Behavior |
| :--- | :--- |
| Primary Provider HTTP 500 / Timeout | Exponential retries -> Fallback Provider failover. |
| Primary Provider HTTP 429 Rate Limit | Sleeps for `Retry-After` duration -> Retries. |
| 3 Consecutive Failures | Circuit Breaker OPENS -> Bypasses primary to Fallback Provider. |
| Missing Langfuse Credentials | Disables tracing gracefully (`Tracing: Disabled`) without crashing. |

---

## 12. 📌 Limitations

- **In-Memory Circuit Breaker**: State is tracked per process instance (not shared across distributed workers).
- **Mock Providers**: Built with simulated network latency and mock responses for demonstration.
- **Local File Logs**: Logs append to local JSONL files (`logs/llm_logs.jsonl`).

---

## 13. 🧪 Running Tests

Execute the full automated test suite (26 unit tests):

```bash
python -m unittest discover -s ticket_classifier
```

---

## 🏗️ 14. Project Architecture

```text
 [Client Invocation]
        │
        ▼
[AsyncLLMClient] (Semaphore Limit = 5)
        │
        ├──► [Circuit Breaker Check]
        │         ├── CLOSED ──► [MockPrimaryProvider] ──(HTTP 429/500)──► Exponential Retries
        │         └── OPEN ────► [MockFallbackProvider]
        │
        ├──► [PII Redaction] (Masks sensitive data)
        ├──► [JSONL Logger] (Appends to logs/llm_logs.jsonl)
        └──► [Langfuse Tracing] (Flushes trace telemetry)
```

---

## 🎉 15. Stretch Goal Completed

- **Package Published Locally**: Installed `ticket_classifier` as a local editable package (`pip install -e .`).
- **Second Independent Project Created**: Built `internal_demo_project/` containing `app.py` and dedicated `README.md`.
- **Zero Code Duplication**: `app.py` consumes public exports (`AsyncLLMClient`, `SupportTicket`, `predict_priority`, `redact_text`, `flush_langfuse_traces`) directly via `from ticket_classifier import ...`.
- **Reusability Demonstrated**: Verified end-to-end async classification, PII masking, urgency prediction, and tracing in an external standalone consumer application.

