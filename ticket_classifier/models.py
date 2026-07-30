from typing import Optional
from pydantic import BaseModel, Field


class SupportTicket(BaseModel):
    """Input support ticket model."""

    ticket_id: Optional[int] = None
    text: str
    force_outcome: Optional[str] = None


class ClassificationResult(BaseModel):
    """Output ticket classification result model."""

    category: str = "General"
    confidence: float = 1.0
    provider: str = "unknown"
    status: str = "success"
    ticket_id: Optional[int] = None
    fallback_reason: Optional[str] = None
    error: Optional[str] = None


class LLMLogEntry(BaseModel):
    """Structured LLM call log entry model."""

    trace_id: str
    timestamp: str
    provider: str
    model_name: str
    prompt: str
    completion: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    estimated_cost: float = 0.0
    latency_ms: float = 0.0
    retry_count: int = 0
    finish_reason: str = "stop"
    success: bool = True


class PriorityResult(BaseModel):
    """Output priority prediction model."""

    priority: str = "LOW"
    score: float = Field(default=0.30, ge=0.0, le=1.0)
    reason: str = "General inquiry"

