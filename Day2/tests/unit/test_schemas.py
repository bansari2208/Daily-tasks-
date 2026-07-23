from pydantic import ValidationError
from app.schemas.career import CareerGuidanceRequest
from app.schemas.domain import CareerRecommendation
from app.schemas.llm import CareerGuidanceLLMResponse
from app.schemas.mapper import map_llm_response_to_domain
from app.schemas.api_response import SuccessResponse, ErrorResponse, CareerAPIResponse
from app.schemas.memory import MemoryItem


def test_career_guidance_request_valid() -> None:
    req = CareerGuidanceRequest(
        skills="Python, HTML, CSS",
        interests="Artificial Intelligence",
        goal="Want to become an AI Full Stack Engineer"
    )
    assert req.skills == "Python, HTML, CSS"
    assert req.interests == "Artificial Intelligence"
    assert req.goal == "Want to become an AI Full Stack Engineer"


def test_career_guidance_llm_response_and_mapping() -> None:
    llm_resp = CareerGuidanceLLMResponse(
        career_paths=["AI Engineer", "Web Developer"],
        skills_to_improve=["TypeScript", "FastAPI"],
        project_ideas=["AI Agent Dashboard"],
        learning_roadmap=["Days 1-7: Python"],
        internship_tips=["Build in public"],
        motivation_quote="Stay consistent!",
        formatted_markdown="### Markdown Guidance",
        category="career_guidance",
        confidence=0.95
    )
    domain_model: CareerRecommendation = map_llm_response_to_domain(llm_resp)
    assert isinstance(domain_model, CareerRecommendation)
    assert domain_model.career_paths == ["AI Engineer", "Web Developer"]
    assert domain_model.motivation_tip == "Stay consistent!"
    assert domain_model.category == "career_guidance"
    assert domain_model.confidence == 0.95


def test_domain_model_business_rule_validator() -> None:
    # Test valid business rule (skills_to_improve >= career_paths count)
    valid_rec = CareerRecommendation(
        career_paths=["AI Engineer"],
        skills_to_improve=["Python", "FastAPI"],
        project_ideas=["AI App"],
        learning_roadmap=["Days 1-7: Basics"],
        internship_tips=["Networking"],
        motivation_tip="Keep going!",
        formatted_markdown="Markdown",
        category="career_guidance",
        confidence=0.9
    )
    assert valid_rec.career_paths == ["AI Engineer"]

    # Test business rule failure: 2 career paths, but only 1 skill to improve
    failed = False
    try:
        CareerRecommendation(
            career_paths=["AI Engineer", "Full Stack Dev"],
            skills_to_improve=["Python"],
            project_ideas=["AI App"],
            learning_roadmap=["Days 1-7: Basics"],
            internship_tips=["Networking"],
            motivation_tip="Keep going!",
            formatted_markdown="Markdown",
            category="career_guidance",
            confidence=0.9
        )
    except ValidationError as exc:
        failed = True
        assert "Business Rule Violation" in str(exc)

    assert failed, "Expected ValidationError for business rule violation"


def test_discriminated_union_api_response() -> None:
    rec = CareerRecommendation(
        career_paths=["AI Developer"],
        skills_to_improve=["Python"],
        project_ideas=["Bot"],
        learning_roadmap=["Day 1"],
        internship_tips=["Tips"],
        motivation_tip="Quote",
        formatted_markdown="MD",
        category="career_guidance",
        confidence=0.88
    )
    success = SuccessResponse(data=rec)
    assert success.type == "success"

    error = ErrorResponse(message="Invalid payload", details=["Field required"])
    assert error.type == "error"
