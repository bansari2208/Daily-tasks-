import os
import json
import uuid
from datetime import datetime, timezone
from ticket_classifier.redaction import redact_text

LOG_FILE_PATH = os.path.join("logs", "llm_logs.jsonl")
REVIEW_QUEUE_FILE_PATH = os.path.join("logs", "review_queue.json")


def save_to_review_queue(
    ticket_id: int,
    category: str,
    confidence: float,
    reason: str,
    timestamp: str = None,
    queue_file: str = REVIEW_QUEUE_FILE_PATH,
) -> dict:
    """Appends a low-confidence ticket to the human review queue with ISO UTC timestamp."""
    if timestamp is None:
        timestamp = datetime.now(timezone.utc).isoformat()

    entry = {
        "ticket_id": ticket_id,
        "timestamp": timestamp,
        "category": category,
        "confidence": round(confidence, 2),
        "reason": reason,
    }

    queue_dir = os.path.dirname(queue_file)
    if queue_dir:
        os.makedirs(queue_dir, exist_ok=True)

    items = []
    if os.path.exists(queue_file):
        try:
            with open(queue_file, "r", encoding="utf-8") as f:
                items = json.load(f)
        except Exception:
            items = []

    items.append(entry)

    with open(queue_file, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2)

    return entry


def log_llm_call(
    model_name: str,
    prompt: str,
    completion: str,
    prompt_tokens: int = 0,
    completion_tokens: int = 0,
    total_tokens: int = 0,
    estimated_cost: float = 0.0,
    latency_ms: float = 0.0,
    retry_count: int = 0,
    finish_reason: str = "stop",
    provider: str = "unknown",
    success: bool = True,
    trace_id: str = None,
    span_id: str = None,
    parent_span_id: str = None,
    start_time: str = None,
    end_time: str = None,
    timestamp: str = None,
    ttft_ms: float = 0.0,
    tpot_ms: float = 0.0,
    request_started_at: str = None,
    request_finished_at: str = None,
    circuit_breaker: str = "CLOSED",
    temperature: float = 0.0,
    top_p: float = 0.7,
    confidence_score: float = 0.95,
    routing_decision: str = "AUTO_PROCESSED",
    schema_valid: bool = True,
    validation_retry: bool = False,
    complexity: str = "EASY",
    model_used: str = "GPT-4.1 Nano",
    reasoning_tokens: int = 0,
    used_reasoning_model: bool = False,
    task_type: str = "SIMPLE_CLASSIFICATION",
    recommended_model: str = "GPT-4.1 Nano",
    selected_model: str = "GPT-4.1 Nano",
    playbook_version: str = "v1.1",
    playbook_last_updated: str = "2026-07-30",
    playbook_decision_reason: str = "Fastest and cheapest for routine tickets",
    log_file: str = LOG_FILE_PATH,
) -> dict:
    """Logs an LLM call to a JSON Lines file with production latency, decoding, circuit breaker, reasoning, and playbook metadata."""
    if trace_id is None:
        trace_id = str(uuid.uuid4())

    if span_id is None:
        span_id = str(uuid.uuid4())[:16]

    if timestamp is None:
        timestamp = datetime.now(timezone.utc).isoformat()

    if start_time is None:
        start_time = timestamp

    if end_time is None:
        end_time = datetime.now(timezone.utc).isoformat()

    if request_started_at is None:
        request_started_at = start_time

    if request_finished_at is None:
        request_finished_at = end_time

    if total_tokens == 0 and (prompt_tokens > 0 or completion_tokens > 0):
        total_tokens = prompt_tokens + completion_tokens

    # Redact any PII from prompt and completion before logging
    redacted_prompt = redact_text(prompt)
    redacted_completion = redact_text(completion)

    log_entry = {
        "trace_id": trace_id,
        "span_id": span_id,
        "parent_span_id": parent_span_id,
        "start_time": start_time,
        "end_time": end_time,
        "duration_ms": latency_ms,
        "timestamp": timestamp,
        "request_started_at": request_started_at,
        "request_finished_at": request_finished_at,
        "model_name": model_name,
        "prompt": redacted_prompt,
        "completion": redacted_completion,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
        "estimated_cost": estimated_cost,
        "latency_ms": latency_ms,
        "total_latency_ms": latency_ms,
        "ttft_ms": round(ttft_ms, 2),
        "tpot_ms": round(tpot_ms, 2),
        "retry_count": retry_count,
        "circuit_breaker": circuit_breaker,
        "temperature": temperature,
        "top_p": top_p,
        "confidence_score": round(confidence_score, 2),
        "routing_decision": routing_decision,
        "schema_valid": schema_valid,
        "validation_retry": validation_retry,
        "complexity": complexity,
        "model_used": model_used,
        "reasoning_tokens": reasoning_tokens,
        "used_reasoning_model": used_reasoning_model,
        "task_type": task_type,
        "recommended_model": recommended_model,
        "selected_model": selected_model,
        "playbook_version": playbook_version,
        "playbook_last_updated": playbook_last_updated,
        "playbook_decision_reason": playbook_decision_reason,
        "finish_reason": finish_reason,
        "provider": provider,
        "success": success,
    }

    log_dir = os.path.dirname(log_file)
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)

    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")

    return log_entry
