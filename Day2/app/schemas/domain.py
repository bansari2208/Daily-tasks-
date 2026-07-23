from typing import List
from pydantic import BaseModel, Field, model_validator
from typing_extensions import Self


class CareerRecommendation(BaseModel):
    """Domain model used throughout the application business logic."""

    career_paths: List[str] = Field(..., min_length=1, description="Recommended career path titles")
    skills_to_improve: List[str] = Field(..., min_length=1, description="Skills to learn/enhance")
    project_ideas: List[str] = Field(..., min_length=1, description="Portfolio project ideas")
    learning_roadmap: List[str] = Field(..., min_length=1, description="30-day roadmap steps")
    internship_tips: List[str] = Field(..., min_length=1, description="Internship and application tips")
    motivation_tip: str = Field(..., description="Motivational closing tip")
    formatted_markdown: str = Field(..., description="Full formatted markdown text representation")
    category: str = Field(..., description="Category of recommendation")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score between 0 and 1")

    @model_validator(mode="after")
    def validate_business_rules(self) -> Self:
        """Genuine domain business rule validation."""
        # Business Rule 1: The number of skills to improve must be at least equal to the number of career paths
        if len(self.skills_to_improve) < len(self.career_paths):
            raise ValueError(
                "Business Rule Violation: Identified skills to improve must be at least equal to the number of recommended career paths."
            )

        # Business Rule 2: If learning roadmap exists, project ideas count must meet or exceed roadmap milestones
        if len(self.project_ideas) == 0 and len(self.learning_roadmap) > 0:
            raise ValueError(
                "Business Rule Violation: A learning roadmap must be accompanied by portfolio project ideas."
            )

        return self
