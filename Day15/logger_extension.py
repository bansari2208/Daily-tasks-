import os
import json
import uuid
from datetime import datetime, timezone
from Day7.ticket_classifier.redaction import redact_text

LOG_FILE_PATH = os.path.join("logs", "llm_logs.jsonl")


def log_llm_call_versioned(
    model_name: str,
    prompt: str,
    completion: str,
    prompt_name: str = "ticket_classifier 1",
    prompt_version: str = "1",
    prompt_tokens: int = 0,
    completion_tokens: int = 0,
    total_tokens: int = 0,
    estimated_cost: float = 0.0,
    latency_ms: float = 0.0,
    retry_count: int = 0,
    finish_reason: str = "stop",
    provider: str = "langfuse",
    success: bool = True,
    trace_id: str = None,
    span_id: str = None,
    log_file: str = LOG_FILE_PATH,
) -> dict:
    """
    Day 15 Extended Logging helper.
    
    Appends prompt_name and prompt_version to the Day 4 OpenTelemetry-compatible JSONL schema.
    """
    if trace_id is None:
        trace_id = str(uuid.uuid4())

    if span_id is None:
        span_id = str(uuid.uuid4())[:16]

    timestamp = datetime.now(timezone.utc).isoformat()

    if total_tokens == 0 and (prompt_tokens > 0 or completion_tokens > 0):
        total_tokens = prompt_tokens + completion_tokens

    redacted_prompt = redact_text(prompt)
    redacted_completion = redact_text(completion)

    log_entry = {
        "trace_id": trace_id,
        "span_id": span_id,
        "timestamp": timestamp,
        "duration_ms": latency_ms,
        "prompt_name": prompt_name,
        "prompt_version": str(prompt_version),
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
