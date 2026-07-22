from typing import List
from pydantic import BaseModel, Field


class CareerGuidanceLLMResponse(BaseModel):
    """Raw structured response model produced directly by LLM API."""

    career_paths: List[str] = Field(..., min_length=1, description="Recommended career path titles")
    skills_to_improve: List[str] = Field(..., min_length=1, description="Skills to learn/enhance")
    project_ideas: List[str] = Field(..., min_length=1, description="Portfolio project ideas")
    learning_roadmap: List[str] = Field(..., min_length=1, description="30-day roadmap steps")
    internship_tips: List[str] = Field(..., min_length=1, description="Internship and application tips")
    motivation_quote: str = Field(..., description="Motivational quote or closing tip")
    formatted_markdown: str = Field(..., description="Raw formatted markdown representation")
