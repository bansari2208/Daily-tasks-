"""
Ticket Classifier - A Resilient Async LLM Ticket Classification Package
"""

from ticket_classifier.client import AsyncLLMClient
from ticket_classifier.circuit_breaker import CircuitBreaker
from ticket_classifier.models import SupportTicket, ClassificationResult, LLMLogEntry, PriorityResult
from ticket_classifier.priority import predict_priority
from ticket_classifier.logger import log_llm_call
from ticket_classifier.redaction import redact_text
from ticket_classifier.report import generate_report
from ticket_classifier.tracer import trace_langfuse_call, flush_langfuse_traces, get_tracing_status
from ticket_classifier.utils import timer

__all__ = [
    "AsyncLLMClient",
    "CircuitBreaker",
    "SupportTicket",
    "ClassificationResult",
    "LLMLogEntry",
    "PriorityResult",
    "predict_priority",
    "log_llm_call",
    "redact_text",
    "generate_report",
    "trace_langfuse_call",
    "flush_langfuse_traces",
    "get_tracing_status",
    "timer",
]
