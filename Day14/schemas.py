"""
Day 14 - Pydantic Schemas and Tool Execution Models.

Defines Pydantic request argument validation models, tool classification enums,
structured error payloads, and tool execution result containers.
Conforms to OpenAI Function Calling and Amazon Bedrock Tool Use specifications.
"""

from enum import Enum
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict


class ToolType(str, Enum):
    """Classification of tool execution side-effects."""
    READ_ONLY = "READ_ONLY"
    STATE_CHANGING = "STATE_CHANGING"


class GetTicketStatusArgs(BaseModel):
    """Pydantic schema validating arguments for read-only tool 'get_ticket_status'."""
    model_config = ConfigDict(strict=False, extra="forbid")

    ticket_id: int = Field(
        ...,
        gt=0,
        description="Unique positive integer identifier for the ticket."
    )


class CloseTicketArgs(BaseModel):
    """Pydantic schema validating arguments for state-changing tool 'close_ticket'."""
    model_config = ConfigDict(strict=False, extra="forbid")

    ticket_id: int = Field(
        ...,
        gt=0,
        description="Unique positive integer identifier for the ticket to close."
    )
    reason: str = Field(
        ...,
        min_length=3,
        description="Detailed mandatory resolution reason for closing the ticket."
    )


class UpdateTicketPriorityArgs(BaseModel):
    """Pydantic schema validating arguments for state-changing tool 'update_ticket_priority'."""
    model_config = ConfigDict(strict=False, extra="forbid")

    ticket_id: int = Field(
        ...,
        gt=0,
        description="Unique positive integer identifier for the ticket."
    )
    priority: str = Field(
        ...,
        pattern="^(HIGH|MEDIUM|LOW)$",
        description="Target priority level: HIGH, MEDIUM, or LOW."
    )


class StructuredError(BaseModel):
    """Structured error payload for graceful exception handling and recovery paths."""
    status: str = "FAILED"
    error_type: str = Field(..., description="Error classification (e.g. DatabaseError, ValidationError)")
    message: str = Field(..., description="Human-readable exception details")
    recoverable: bool = Field(True, description="Indicates whether recovery path can be safely executed")
    suggestion: str = Field(..., description="Actionable recovery recommendation for the user/system")


class ToolExecutionResult(BaseModel):
    """Container holding standardized output from tool execution pipeline."""
    tool_name: Optional[str] = None
    status: str = Field("SUCCESS", description="SUCCESS, FAILED, CANCELLED, VALIDATION_ERROR, NO_TOOL")
    arguments: Dict[str, Any] = Field(default_factory=dict)
    raw_arguments: Dict[str, Any] = Field(default_factory=dict)
    result: Optional[Dict[str, Any]] = None
    error: Optional[StructuredError] = None
    execution_time_ms: float = 0.0
    confirmation_status: Optional[str] = None  # EXECUTED_IMMEDIATELY, CONFIRMED, REJECTED, N/A
