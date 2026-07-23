from datetime import datetime
from typing import List, Optional
from uuid import uuid4
from pydantic import BaseModel, Field


class MemoryItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    skills: str
    interests: str
    goal: str


class MemoryHistory(BaseModel):
    items: List[MemoryItem] = Field(default_factory=list)
