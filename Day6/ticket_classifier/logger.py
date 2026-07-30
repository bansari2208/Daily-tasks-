import os
import json
import uuid
from datetime import datetime, timezone
from ticket_classifier.redaction import redact_text

LOG_FILE_PATH = os.path.join("logs", "llm_logs.jsonl")


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
    log_file: str = LOG_FILE_PATH,
) -> dict:
    """
    Logs an LLM call to a JSON Lines (.jsonl) file with OpenTelemetry-compatible span metadata.

    Parameters match the required schema:
    - trace_id (UUID string)
    - span_id (Span identifier)
    - parent_span_id (Optional parent span ID)
    - start_time (ISO 8601 string)
    - end_time (ISO 8601 string)
    - duration_ms (Latency in milliseconds)
    - timestamp (ISO 8601 string)
    - model_name
    - prompt (redacted)
    - completion (redacted)
    - prompt_tokens
    - completion_tokens
    - total_tokens
    - estimated_cost
    - latency_ms
    - retry_count
    - finish_reason
    - provider
    - success (bool)
    """
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
        "model_name": model_name,
        "prompt": redacted_prompt,
        "completion": redacted_completion,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
        "estimated_cost": estimated_cost,
        "latency_ms": latency_ms,
        "retry_count": retry_count,
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

