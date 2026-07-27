# Async Support Ticket Classifier (Day 4: Observability & Tracing)

A lightweight, standalone Python project demonstrating how to build a production-grade async LLM ticket classification client with resilience, structured logging, cost analytics, PII redaction, and Langfuse tracing.

---

## 🏗️ Architecture & Execution Flow

```text
[Incoming Tickets] -> [AsyncLLMClient (Semaphore max 5)]
                           |
            +--------------+--------------+
            |                             |
   [MockPrimaryProvider]        [MockFallbackProvider]
   (Retries 429/500/Timeout)   (Circuit Breaker Triggered)
            |                             |
            +--------------+--------------+
                           |
            +--------------+--------------+
            |              |              |
     [PII Redaction] [JSONL Logger] [Langfuse Tracing]
```

### Execution Flow:
1. `demo.py` triggers batch execution of 100 tickets using `asyncio.gather`.
2. `AsyncLLMClient` enforces `asyncio.Semaphore(5)` bounded concurrency.
3. Requests hit `MockPrimaryProvider`. Transient errors (HTTP 429/500/Timeouts) trigger exponential retries with jitter and `Retry-After` handling.
4. Consecutive primary failures trigger `CircuitBreaker` to switch to `MockFallbackProvider`.
5. Every completed request is sanitized via `redact_text` (PII masking), logged to `logs/llm_logs.jsonl`, and traced via `Langfuse` v4 SDK.
6. `report.py` processes JSON logs to produce the Day 4 Cost & Latency Report.

---

## 📁 Project Structure

```text
ticket_classifier/
│
├── client.py          # Resilient Async LLM client (semaphore, retries, fallback)
├── providers.py       # Primary & fallback mock providers
├── circuit_breaker.py # 3-State circuit breaker
├── logger.py          # Structured JSONL logger with OpenTelemetry fields
├── report.py          # Batch analytics & cost report generator
├── redaction.py       # Regex-based PII masking
├── tracer.py          # Langfuse v4 & LangSmith tracing integrations
├── utils.py           # Context manager timer utility
├── demo.py            # 100-ticket batch demo entry point
├── test_*.py          # Pytest / Unittest automated test suite
├── .env               # Langfuse credentials
├── requirements.txt
└── README.md
```

---

## 🛠️ Day 4 Feature Mapping

- **Structured Logging** -> `ticket_classifier/logger.py`
- **Analytics Report** -> `ticket_classifier/report.py`
- **Langfuse Tracing** -> `ticket_classifier/tracer.py`
- **PII Redaction** -> `ticket_classifier/redaction.py`
- **Batch Processing** -> `ticket_classifier/demo.py`

---

## 🎓 Learning Outcomes

- **Asynchronous Execution**: High-throughput processing with `asyncio.gather`.
- **Resilience Engineering**: Bounded concurrency (`Semaphore`), exponential retries with jitter, `Retry-After` parsing, 3-State `CircuitBreaker`, and provider fallbacks.
- **Observability**: Structured JSON logging, OpenTelemetry-compatible span schemas, and real-time dashboard tracing with `Langfuse`.
- **Data Governance**: In-flight regex PII masking for emails, phone numbers, credit card numbers, passwords, and API keys.

---

## ⚡ How to Run

### 1. Run the Full Demo Pipeline
```bash
python demo.py
```

### 2. Run the Standalone Cost & Analytics Report
```bash
python report.py
```

### 3. Run Automated Tests
```bash
python -m unittest discover -s ticket_classifier
```

---

## 🔍 How Langfuse is Integrated

Langfuse tracing uses the native **v4 Python SDK** via manual observations (`start_observation`). Tracing reads credentials (`LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, `LANGFUSE_BASE_URL`) from `.env`.

Every trace includes:
- `session_id` (groups batch traces together)
- `ticket_id`
- `provider`
- `retry_count`
- `fallback_used`
- `latency_ms`
- `finish_reason`
- `success`
- `tags` (`["day4", "ticket-classifier", "demo"]`)

Tracing runs safely in the background. If credentials are missing, tracing prints `Tracing: Disabled` without crashing.

---

## 📊 Example Output

```text
==================================
Day 4 Batch Classification Demo
==================================
Tracing: Enabled (Langfuse)

Starting batch processing of 100 support tickets...
[Batch Processing] Finished in 1.92 s

-----------------------------------
Langfuse Summary
-----------------------------------
Tracing: Enabled (Langfuse)
Session ID: session_a1b2c3d4e5f6
Traces Sent: 100
Flush Status: Success
Dashboard: https://hipaa.cloud.langfuse.com
-----------------------------------

==================================
Day 4 Cost & Latency Report
==================================
Requests:                  100
Primary Success:           91
Fallback Success:          9
Failed Requests:           0

Retry Rate:                21.00%
Average Retries/Request:   0.22

Prompt Tokens:             921
Completion Tokens:         100
Total Tokens:              1021

Total Cost:                $0.010210
Average Cost:              $0.000102

Average Latency:           90.44 ms
P50 Latency:               61.71 ms
P95 Latency:               232.81 ms

Batch Execution Time:      1.92 s
Throughput:                52.08 req/s

Logs Saved To:
logs\llm_logs.jsonl
==================================
```
