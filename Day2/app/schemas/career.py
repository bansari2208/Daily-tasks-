import re
from typing import List
from pydantic import BaseModel, Field, field_validator


class CareerGuidanceRequest(BaseModel):
    skills: str = Field(
        ...,
        min_length=2,
        max_length=500,
        description="Student skills (e.g., Python, HTML, CSS)",
        examples=["HTML, CSS, Python, FastAPI"]
    )
    interests: str = Field(
        ...,
        min_length=2,
        max_length=500,
        description="Student interests (e.g., AI, Web Development)",
        examples=["Artificial Intelligence, Machine Learning"]
    )
    goal: str = Field(
        ...,
        min_length=5,
        max_length=500,
        description="Career goal",
        examples=["Want to become an AI-Assisted Full-Stack Engineer"]
    )

    @field_validator("skills", "interests", "goal")
    @classmethod
    def sanitize_input(cls, v: str) -> str:
        if not isinstance(v, str):
            raise ValueError("Field must be a string")
        cleaned = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F]', '', v).strip()
        if not cleaned:
            raise ValueError("Field cannot consist solely of whitespace or control characters")
        return cleaned


class CareerPath(BaseModel):
    title: str = Field(..., description="Job role or career path title")
    description: str = Field(..., description="Why this path fits the profile")


class RoadmapPhase(BaseModel):
    timeline: str = Field(..., description="Timeline e.g. Days 1-7")
    title: str = Field(..., description="Phase focus area")
    details: str = Field(..., description="Actionable tasks")


class CareerGuidanceResponse(BaseModel):
    best_career_paths: List[str] = Field(..., min_length=1)
    skills_to_improve: List[str] = Field(..., min_length=1)
    project_ideas: List[str] = Field(..., min_length=1)
    learning_roadmap: List[str] = Field(..., min_length=1)
    internship_tips: List[str] = Field(..., min_length=1)
    motivation_tip: str = Field(..., description="Motivational closing tip")
    formatted_markdown: str = Field(..., description="Full formatted markdown text representation")
