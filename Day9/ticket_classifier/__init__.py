"""
Ticket Classifier - A Resilient Async LLM Ticket Classification Package
"""

from .client import AsyncLLMClient
from .circuit_breaker import CircuitBreaker
from .models import SupportTicket, ClassificationResult, LLMLogEntry, PriorityResult
from .priority import predict_priority
from .logger import log_llm_call, save_to_review_queue
from .redaction import redact_text
from .report import generate_report
from .tracer import trace_langfuse_call, flush_langfuse_traces, get_tracing_status
from .utils import timer
from .cost import (
    calculate_request_cost,
    compress_prompt,
    compare_language_inflation,
    get_model_recommendation,
)
from .reasoning import (
    analyze_ticket_complexity,
    should_use_reasoning_model,
    estimate_reasoning_tokens,
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
]
