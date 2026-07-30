# Async Support Ticket Classifier (Day 3: Resilient LLM Clients)

A lightweight, standalone Python project demonstrating how to build a production-grade, resilient async LLM client for ticket classification.

---

## 🎓 Learning Outcomes

This project demonstrates the core resilience techniques used in production LLM applications:

- Asynchronous API calls using asyncio
- Timeout handling
- Exponential backoff with jitter
- Retry-After support
- Bounded concurrency with asyncio.Semaphore
- Provider fallback
- Circuit breaker
- Batch processing with partial failure handling

---

## 🧩 Day 3 Requirements Mapping

| Concept / Requirement | Implementation File | Description |
| :--- | :--- | :--- |
| **Reusable Async Client** | `ticket_classifier/client.py` | Built with `async/await` and `httpx.AsyncClient`. |
| **Retry Logic** | `ticket_classifier/client.py` | Exponential backoff, jitter, and `Retry-After` header handling (retries 429/500/timeout, skips 400). |
| **Semaphore / Concurrency Limit** | `ticket_classifier/client.py` | Uses `asyncio.Semaphore(5)` to strictly enforce in-flight request limits. |
| **Provider Fallback** | `ticket_classifier/providers.py` | `MockPrimaryProvider` with safety net fallback `MockFallbackProvider`. |
| **Circuit Breaker** | `ticket_classifier/circuit_breaker.py` | Standalone 3-State machine (`CLOSED`, `OPEN`, `HALF-OPEN`) to protect failing services. |
| **Batch Processing** | `ticket_classifier/demo.py` | Runs 100 tickets concurrently using `asyncio.gather` preserving completed results. |

---

## 🎯 Day 3 Resilience Concepts Covered

1. **Async HTTP Execution**: Native `async/await` using `httpx`.
2. **Timeout Handling**: Graceful error catching on network timeouts.
3. **Exponential Backoff & Jitter**:
   - Retries transient errors: **HTTP 429 (Rate Limit)** and **HTTP 500 (Internal Server Error)**.
   - Respects **`Retry-After`** header when returned by the server.
   - **Does NOT retry HTTP 400 (Bad Request)** to avoid repeating invalid calls.
4. **Concurrency Control**:
   - Uses `asyncio.Semaphore(5)` to limit max concurrent requests.
   - Tracks `current_inflight` and asserts `max_inflight_seen <= semaphore_limit`.
5. **Circuit Breaker Pattern**:
   - 3-State Machine (`CLOSED`, `OPEN`, `HALF-OPEN`).
   - Opens after 3 consecutive failures to protect upstream APIs.
6. **Provider Fallback**:
   - Switches automatically to `MockFallbackProvider` when primary provider retries are exhausted or circuit breaker is open.
7. **Batch Resilience**:
   - Processes 100 tickets concurrently using `asyncio.gather(..., return_exceptions=True)`.
   - Never crashes the entire batch due to isolated ticket errors.

---

## 📁 Project Structure

```text
ticket_classifier/
│
├── client.py              # Async client with retries and concurrency
├── providers.py           # Primary and fallback providers
├── circuit_breaker.py     # Circuit breaker implementation
├── demo.py                # Runs 100-ticket demo
├── test_client.py         # Pytest test suite
├── requirements.txt
└── README.md
```

---

## ⚡ Quickstart

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Demo
```bash
python demo.py
```
*or*
```bash
python -m ticket_classifier.demo
```

### 3. Run Tests
```bash
python -m pytest
```
