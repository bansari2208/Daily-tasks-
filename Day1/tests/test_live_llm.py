import os
import pytest

from app.config import settings
from app.schemas.career import CareerGuidanceRequest
from app.schemas.domain import CareerRecommendation
from app.services.llm_service import LLMService


@pytest.mark.live
def test_live_llm_model_invocation() -> None:
    """Tier 3 Live Model Test.

    Requires live API key configured in environment settings or GROQ_API_KEY.
    Excluded from default pytest execution. Run explicitly via: pytest -m live
    """
    api_key = settings.groq_api_key or os.getenv("GROQ_API_KEY")
    if not api_key:
        pytest.skip("GROQ_API_KEY is not configured in settings or environment. Skipping live test.")

    service = LLMService(api_key=api_key)
    req = CareerGuidanceRequest(
        skills="Python, SQL, HTML",
        interests="Data Science, Web Development",
        goal="Become a Data Engineer"
    )

    result = service.generate_career_guidance(req)

    # Validate output structure and schema rules without strict text assertion
    assert isinstance(result, CareerRecommendation)
    assert result.category is not None
    assert 0.0 <= result.confidence <= 1.0
    assert len(result.career_paths) >= 1
    assert len(result.skills_to_improve) >= 1
    assert result.motivation_tip is not None
    assert result.formatted_markdown is not None
