# 🎫 Async Support Ticket Classifier (`ticket-classifier`)

A beginner-friendly, production-grade Python package that automatically classifies customer support tickets using artificial intelligence (AI). It is built to be fast, reliable, secure, and easy to monitor.

---

## 1. 📌 Project Overview

This project provides a reusable Python library (`ticket-classifier`) that processes customer support tickets asynchronously. It automatically sorts incoming tickets into categories (such as *Billing*, *Technical*, or *General*), assigns urgency priorities, masks sensitive personal data, tracks API costs, and records real-time dashboard telemetry.

It is designed to handle network errors gracefully without crashing or slowing down.

---

## 2. ✨ Key Features

- **⚡ Fast Async Execution**: Handles multiple tickets at the same time without waiting for each one to finish sequentially.
- **🛡️ Built-in Resilience**: Automatically retries failed requests, respects server wait times, and switches to a backup server if the main server goes down.
- **🔒 PII Redaction**: Automatically hides sensitive data like credit card numbers, passwords, and emails before saving logs.
- **📊 Cost & Performance Analytics**: Calculates total API costs, token counts, throughput, and average response times.
- **🔍 Real-Time Dashboard Tracing**: Integrates with Langfuse to track every request on a visual dashboard.
- **🚨 Urgency Priority Prediction**: Automatically tags tickets as `HIGH`, `MEDIUM`, or `LOW` priority for fast agent routing.

---

## 3. 📖 Key Technical Concepts (Simplified)

- **Async / Asyncio**: Allows Python to handle many tasks at once without freezing or blocking.
- **Semaphore**: Limits how many requests run at the exact same time to prevent overwhelming the server.
- **Exponential Backoff**: Gradually increases wait time between retries (e.g., wait 1s, then 2s, then 4s) when an error occurs.
- **Retry-After**: Waits for the exact number of seconds requested by the server during rate limit errors.
- **Circuit Breaker**: Temporarily stops sending requests to a primary server if it repeatedly fails.
- **Fallback Provider**: A backup AI service that takes over when the main service fails.
- **PII (Personally Identifiable Information)**: Private details like email addresses, phone numbers, and credit cards.
- **Langfuse Tracing**: A monitoring tool that creates visual step-by-step records of AI requests.

---

## 4. 📁 Project Structure

```text
Ticket Classifier/
├── ticket_classifier/          # Reusable core Python package
│   ├── __init__.py             # Public package exports
│   ├── client.py               # Main Async LLM client (handles concurrency & retries)
│   ├── models.py               # Typed Pydantic data schemas
│   ├── priority.py             # Urgency prediction module (HIGH, MEDIUM, LOW)
│   ├── logger.py               # Structured JSON log recorder
│   ├── report.py               # Cost & performance analytics generator
│   ├── redaction.py            # Regex-based PII masker
│   ├── circuit_breaker.py      # 3-State circuit breaker safety logic
│   ├── providers.py            # Primary and backup mock LLM providers
│   ├── tracer.py               # Langfuse dashboard tracing integration
│   └── test_*.py              # Automated unit tests (26 test cases)
├── internal_demo_project/      # Independent project proving package reusability
│   ├── app.py                  # Standalone app using the ticket_classifier library
│   └── README.md               # Independent project documentation
├── pyproject.toml              # Standard Python package installation file
├── demo.py                     # 100-ticket batch execution demonstration script
├── report.py                   # Standalone report runner script
├── example_runner.py           # External library integration runner
├── AI_REVIEW.md                # Professional code review findings
└── README.md                   # Project documentation
```

---

## 5. ⚙️ Installation

To install `ticket-classifier` as a local Python package, run:

```bash
pip install -e .
```

*Note: `-e` stands for "editable", allowing code edits to take effect immediately.*

---

## 6. 🚀 How to Run

### Run the Full 100-Ticket Demo
```bash
python demo.py
```

### Run the Cost & Analytics Report
```bash
python report.py
```

### Run the External Package Integration Script
```bash
python example_runner.py
```

### Run from the Independent Consumer Project
```bash
cd internal_demo_project
python app.py
```

---

## 7. 💻 Package Usage Example

You can import and use `ticket-classifier` in any Python project with just a few lines of code:

```python
import asyncio
from ticket_classifier import AsyncLLMClient, predict_priority, redact_text

async def main():
    # 1. Initialize the client
    client = AsyncLLMClient(max_concurrency=5, max_retries=2)

    # 2. Raw ticket with sensitive credit card info
    raw_ticket = "Payment failed on checkout page. Card 4532 1234 5678 9012 failed."

    # 3. Mask PII before processing
    safe_ticket = redact_text(raw_ticket)

    # 4. Classify ticket asynchronously
    result = await client.classify_ticket(safe_ticket, ticket_id=1)
    
    # 5. Predict urgency level
    priority = predict_priority(safe_ticket, category=result["category"])

    print(f"Category: {result['category']}")
    print(f"Priority: {priority.priority} (Score: {priority.score})")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 8. 🔄 Retry Logic & Rate Limit Handling

- **HTTP 500 & Timeouts**: If a server error occurs, the client automatically retries up to 2 times using exponential backoff with small random delays (jitter).
- **HTTP 429 Rate Limit**: If the server says "too many requests", the client reads the `Retry-After` header and pauses execution until the server is ready.
- **HTTP 400 Bad Request**: Bad user inputs fail immediately without wasting retry attempts.

---

## 9. 🚦 Concurrency & Semaphore Control

- **Semaphore (Limit = 5)**: Ensures that no more than 5 ticket requests hit the AI provider simultaneously.
- **Why it matters**: Prevents crashing AI endpoints or exceeding API rate limits during high-volume batch workloads.

---

## 10. 🔌 Circuit Breaker Pattern

The Circuit Breaker protects failing services by monitoring consecutive errors:

```text
  [CLOSED] --(3 failures)--> [OPEN]
     ^                         |
     |                  (cooldown 1s)
     |                         v
  (success) <---------- [HALF-OPEN]
```

- **CLOSED**: Normal operation. Requests go to the Primary Provider.
- **OPEN**: After 3 consecutive failures, the circuit opens and routes all requests directly to the Backup Fallback Provider.
- **HALF-OPEN**: After a 1-second cooldown, it tests 1 request on the Primary Provider. If successful, it switches back to `CLOSED`.

---

## 11. 🔄 Provider Fallback System

- If the **Primary Provider** fails all retries or if the **Circuit Breaker is OPEN**, the request automatically switches to the **MockFallbackProvider**.
- Guarantees 100% processing completion so user tickets are never lost or dropped.

---

## 12. 🔒 PII Redaction & Data Governance

Before saving log records, all text passes through `redact_text()` which uses regular expressions (regex) to replace sensitive data with `[REDACTED]`.

- **Emails**: `john@example.com` ➔ `[REDACTED]`
- **Phone Numbers**: `+1-555-123-4567` ➔ `[REDACTED]`
- **Credit Cards**: `4532 1234 5678 9012` ➔ `[REDACTED]`
- **Passwords**: `Secret123!` ➔ `[REDACTED]`
- **API Keys**: `sk_live_998877...` ➔ `[REDACTED]`

---

## 13. 📊 Cost & Latency Reporting

The analytics module (`report.py`) parses `logs/llm_logs.jsonl` to calculate key business metrics:

```text
==================================
Day 4 Cost & Latency Report
==================================
Requests:                  100
Primary Success:           91
Fallback Success:          9
Failed Requests:           0

Retry Rate:                21.00%
Average Retries/Request:   0.22

Total Tokens:              1021
Total Cost:                $0.010210
Average Cost:              $0.000102

Average Latency:           90.44 ms
P50 Latency:               61.71 ms
P95 Latency:               232.81 ms

Batch Execution Time:      1.92 s
Throughput:                52.08 req/s
==================================
```

---

## 14. 🛰️ Langfuse Tracing Integration

Integrates with **Langfuse v4 SDK** to record visual execution traces:

- **Session Grouping**: Assigns a single `session_id` to group all 100 ticket traces in a batch execution.
- **Tags & Metadata**: Attaches tags (`["day4", "ticket-classifier", "demo"]`) and metadata (`ticket_id`, `provider`, `retry_count`, `fallback_used`, `latency_ms`).
- **Safe Fallback**: If credentials are missing, tracing prints `Tracing: Disabled` and processing continues without crashing.

---

## 15. 🧪 Automated Unit Testing

Contains 26 automated unit tests covering all package components (client, logger, report, tracer, redaction, priority, models, utils).

Run all tests:
```bash
python -m unittest discover -s ticket_classifier
```

---

## 16. ⚠️ Failure Modes Summary

| Event | Automatic Action |
| :--- | :--- |
| **Server Timeout / HTTP 500** | Retries up to 2 times with backoff, then switches to backup provider. |
| **HTTP 429 Rate Limit** | Waits for `Retry-After` seconds, then retries request. |
| **3 Primary Server Failures** | Circuit Breaker OPENS, routing traffic directly to backup provider. |
| **Missing Tracing Keys** | Disables dashboard tracing gracefully without crashing the app. |

---

## 🔍 17. AI Code Review (`AI_REVIEW.md`)

A formal code review document ([AI_REVIEW.md](file:///c:/Users/SVI/Desktop/Ticket%20Classifier/AI_REVIEW.md)) was generated to evaluate feature quality:

1. **Case Sensitivity**: Recommends normalizing category strings (`.capitalize()`).
2. **Enum Constraints**: Recommends `Literal["HIGH", "MEDIUM", "LOW"]` type bounds in Pydantic models.
3. **Auditability**: Suggests logging specific matching keywords in priority explanation output.

---

## 🏗️ 18. Project Architecture

```text
 [Incoming Ticket]
        │
        ▼
[AsyncLLMClient] (Max Concurrency = 5)
        │
        ├──► [Circuit Breaker Check]
        │         ├── CLOSED ──► [Primary Provider] ──(HTTP 429/500)──► Retries
        │         └── OPEN ────► [Backup Provider]
        │
        ├──► [PII Redaction] (Masks sensitive data)
        ├──► [JSON Logger] (Saves to logs/llm_logs.jsonl)
        └──► [Langfuse Dashboard] (Flushes trace telemetry)
```

---

## 🔁 19. Project Flow (Step-by-Step)

Here is how a single ticket moves through the complete system from start to finish:

1. **User Input** ➔ A raw support ticket is submitted to the application.
2. **Async Client** ➔ Enters `AsyncLLMClient` under the `Semaphore(5)` concurrency limit.
3. **Retry Logic** ➔ If temporary errors occur (429/500/timeout), the client retries automatically.
4. **Circuit Breaker** ➔ If repeated primary failures occur, the circuit breaker opens to prevent server overload.
5. **Fallback Provider** ➔ If primary retries fail or circuit is open, the backup provider processes the ticket.
6. **Classification & Priority** ➔ The ticket is categorized (*Billing/Technical/General*) and assigned an urgency level (*HIGH/MEDIUM/LOW*).
7. **PII Redaction & Logging** ➔ Private data is masked, and structured JSON logs are written to `logs/llm_logs.jsonl`.
8. **Langfuse Tracing** ➔ Execution telemetry (latency, retries, provider used) is sent to the Langfuse dashboard.
9. **Report Generation** ➔ `report.py` calculates overall cost, throughput, and performance metrics for the batch.

---

## ⚡ 20. Day 6 — Transformer Internals & Inference Control (`benchmark.py`)

Day 6 introduces a lightweight benchmarking module to inspect LLM Transformer inference dynamics, specifically analyzing **Prefill** vs **Decode** performance characteristics and measuring the user experience impact of response streaming.

### Key Concepts

- **TTFT (Time To First Token)**: The duration from initiating a request until the first output token is received. TTFT measures the **Prefill Phase**, where the Transformer processes all input prompt tokens in parallel to initialize KV caches and compute self-attention.
- **TPOT (Time Per Output Token)**: The average duration required to generate each subsequent token during the **Decode Phase**. Decoding happens auto-regressively, generating one token at a time.
- **Prefill vs. Decode**:
  - **Prefill Dominated**: Large prompts (~20,000 tokens) take significant time processing input context. TTFT accounts for >90% of total latency.
  - **Decode Dominated**: Small prompts (~200 tokens) with long generation targets (~200 output tokens) spend >95% of total time sequentially producing output tokens.
- **Perceived Speed (Streaming)**: Streaming returns the first token at TTFT (e.g. ~0.04s) rather than blocking until full completion, giving users immediate feedback.

### How to Run the Benchmark

```bash
python benchmark.py
```

### Sample Benchmark Output

```text
=========================================================================================
                      Day 6 Benchmark: Prefill & Decode Analysis                         
=========================================================================================
Prompt Size     | Output   | TTFT (s)   | Total Latency (s)  | Output Tokens | TPOT (ms) 
-------------------------------------------------------------------------------------------
Small (~200)    | Short    | 0.049      | 0.365              | 20            | 16.63     
Small (~200)    | Long     | 0.049      | 3.310              | 200           | 16.39     
Medium (~2,000) | Short    | 0.221      | 0.537              | 20            | 16.59     
Medium (~2,000) | Long     | 0.220      | 3.456              | 200           | 16.26     
Large (~20,000) | Short    | 2.030      | 2.357              | 20            | 17.22     
Large (~20,000) | Long     | 2.022      | 5.307              | 200           | 16.51     
=========================================================================================
```

### Key Observations

1. **Large Prompts Increase TTFT**: Increasing prompt tokens from 200 to 20,000 increases TTFT from ~0.049s to ~2.030s due to prefill self-attention computation across all input tokens.
2. **Long Outputs Increase Total Latency**: Increasing output tokens from 20 to 200 increases total latency by ~3.0s regardless of prompt size because each output token requires an auto-regressive decode step.
3. **TPOT Remains Constant**: Time per output token (~16.5ms) remains relatively stable across different prompt and output sizes.

---

## 💰 21. Day 7 — Cost Optimization & Token Economics (`cost_model.py`)

Day 7 introduces financial modeling and token economics analysis to simulate a high-volume production scenario (5,000 requests/day, 150,000 requests/month) and evaluate cost reduction techniques.

### Key Concepts & Comparisons

1. **Model Tier Comparison**: Compares frontier models (**GPT-4.1**) with lightweight models (**GPT-4.1 Mini**, **GPT-4.1 Nano**).
2. **Prompt Engineering Optimization**: Compares a **Verbose Prompt A** (~400 input tokens, ~100 completion tokens) against a concise, **Optimized Prompt B** (~220 input tokens, ~60 completion tokens).
3. **Multilingual Token Inflation**: Demonstrates subword tokenization inflation when processing non-English text (e.g. Hindi / Gujarati text incurs ~146% token overhead compared to English).
4. **Prompt Caching**: Reuses repeated prompt context (e.g., system instructions) across requests, offering a 50% discount on cached input tokens.
5. **Batch API Processing**: Utilizes asynchronous batch processing for non-realtime jobs to receive a flat 50% discount on all input and output tokens.
6. **Best Overall Configuration**: Combining **GPT-4.1 Nano**, **Prompt B**, **Prompt Caching**, and **Batch API** reduces monthly costs from **$420.00** down to **$22.14** (**94.7% total cost reduction**).

### Comprehensive Cost Comparison Table

```text
=========================================================================================
                      Day 7 Comprehensive Cost Comparison                                
=========================================================================================
Configuration               | Model         | Monthly Cost ($) | Savings ($)  | Reduction %
-------------------------------------------------------------------------------------------
Naive Configuration         | GPT-4.1       | $420.00          | -            | 0.0%
Optimized Prompt            | GPT-4.1       | $244.50          | $175.50      | 41.8%
Cheaper Model               | GPT-4.1 Mini  | $150.00          | $270.00      | 64.3%
Prompt Caching              | GPT-4.1 Nano  | $44.28           | $375.72      | 89.5%
Batch API                   | GPT-4.1 Nano  | $26.10           | $393.90      | 93.8%
Best Overall Configuration  | GPT-4.1 Nano  | $22.14           | $397.86      | 94.7%
=========================================================================================
```

### Quality Verification Strategy

To downscale models and prompts without degrading system quality:
- **Classification Consistency**: Validate category agreement rate (>95%) across 1,000 historical tickets between frontier and lightweight models.
- **Manual Sample Review**: Conduct expert manual reviews on 100 random predictions.
- **Validation Dataset Accuracy**: Enforce a strict F1-score threshold (≥ 0.92) on golden evaluation sets.
- **Structured Schema Integrity**: Guarantee 100% Pydantic JSON output schema compliance.

### How to Run

```bash
python cost_model.py
```




