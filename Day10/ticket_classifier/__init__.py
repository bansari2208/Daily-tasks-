"""
Ticket Classifier - A Resilient Async LLM Ticket Classification Package
"""

from ticket_classifier.client import AsyncLLMClient
from ticket_classifier.circuit_breaker import CircuitBreaker
from ticket_classifier.models import SupportTicket, ClassificationResult, LLMLogEntry, PriorityResult
from ticket_classifier.priority import predict_priority
from ticket_classifier.logger import log_llm_call, save_to_review_queue
from ticket_classifier.redaction import redact_text
from ticket_classifier.report import generate_report
from ticket_classifier.tracer import trace_langfuse_call, flush_langfuse_traces, get_tracing_status
from ticket_classifier.utils import timer
from ticket_classifier.cost import (
    calculate_request_cost,
    compress_prompt,
    compare_language_inflation,
    get_model_recommendation,
)
from ticket_classifier.reasoning import (
    analyze_ticket_complexity,
    should_use_reasoning_model,
    estimate_reasoning_tokens,
)
from ticket_classifier.playbook import (
    detect_task_type,
    get_recommended_model,
    get_model_reason,
    get_model_tradeoffs,
    get_default_temperature,
    get_default_top_p,
    get_playbook_version,
    get_playbook_last_updated,
)

__all__ = [
    "AsyncLLMClient",
    "CircuitBreaker",
    "SupportTicket",
    "ClassificationResult",
    "LLMLogEntry",
    "PriorityResult",
    "predict_priority",
    "log_llm_call",
    "save_to_review_queue",
    "redact_text",
    "generate_report",
    "trace_langfuse_call",
    "flush_langfuse_traces",
    "get_tracing_status",
    "timer",
    "calculate_request_cost",
    "compress_prompt",
    "compare_language_inflation",
    "get_model_recommendation",
    "analyze_ticket_complexity",
    "should_use_reasoning_model",
    "estimate_reasoning_tokens",
    "detect_task_type",
    "get_recommended_model",
    "get_model_reason",
    "get_model_tradeoffs",
    "get_default_temperature",
    "get_default_top_p",
    "get_playbook_version",
    "get_playbook_last_updated",
]
