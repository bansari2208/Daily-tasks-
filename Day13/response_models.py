"""
Day 13 Response Models.
Provides structured Pydantic models for ticket classification, schema validation,
and boundary enforcement.
"""

from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator
import sys
import os

# Ensure parent directory is accessible to import Day10 models if available
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
try:
    from Day10.ticket_classifier.models import SupportTicket, ClassificationResult
except ImportError:
    class SupportTicket(BaseModel):
        ticket_id: Optional[int] = None
        text: str
        force_outcome: Optional[str] = None

    class ClassificationResult(BaseModel):
        category: str = "General"
        confidence: float = 1.0
        provider: str = "unknown"
        status: str = "success"


class CategoryEnum(str, Enum):
    BILLING = "Billing"
    TECHNICAL = "Technical"
    ACCOUNT = "Account"
    SECURITY = "Security"
    REFUND = "Refund"
    GENERAL = "General"


class FlexibleCategoryEnum(str, Enum):
    BILLING = "Billing"
    TECHNICAL = "Technical"
    ACCOUNT = "Account"
    SECURITY = "Security"
    REFUND = "Refund"
    GENERAL = "General"
    UNKNOWN = "UNKNOWN"


class PriorityEnum(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"


class TicketClassificationResponse(BaseModel):
    """Strict Ticket Classification Response Model."""
    ticket_id: int
    category: CategoryEnum
    priority: PriorityEnum = PriorityEnum.LOW
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    reasoning: str = Field(..., min_length=3)


class FlexibleTicketResponse(BaseModel):
    """Flexible Ticket Classification Model supporting explicit UNKNOWN fallback."""
    ticket_id: int
    category: FlexibleCategoryEnum
    priority: PriorityEnum = PriorityEnum.LOW
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    reasoning: str = Field(default="No reasoning provided")

    @field_validator("category", mode="before")
    @classmethod
    def normalize_category(cls, value: Any) -> Any:
        if isinstance(value, str):
            val_clean = value.strip().capitalize()
            allowed = [e.value for e in FlexibleCategoryEnum]
            if value in allowed:
                return value
            if val_clean in allowed:
                return val_clean
            # Out-of-domain or unmapped categories fall back explicitly to UNKNOWN
            return FlexibleCategoryEnum.UNKNOWN
        return value
