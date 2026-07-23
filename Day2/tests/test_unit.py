import re
import pytest
from pydantic import ValidationError
from hypothesis import given, strategies as st, settings as hypothesis_settings

from app.schemas.career import CareerGuidanceRequest
from app.schemas.domain import CareerRecommendation
from app.schemas.llm import CareerGuidanceLLMResponse
from app.schemas.mapper import map_llm_response_to_domain
from app.services.llm_service import generate_fallback_llm_response


def contains_pii(text: str) -> bool:
    """Helper function to check if text contains PII (emails, phone numbers, SSNs)."""
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    phone_pattern = r'\b(?:\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'
    ssn_pattern = r'\b\d{3}-\d{2}-\d{4}\b'

    if re.search(email_pattern, text) or re.search(phone_pattern, text) or re.search(ssn_pattern, text):
        return True
    return False


# ==========================================
# 1. INPUT PREPROCESSING & SANITIZATION
# ==========================================

def test_career_request_input_sanitization() -> None:
    req = CareerGuidanceRequest(
        skills="  Python, FastAPI \x00 ",
        interests=" AI Systems \x07 ",
        goal=" Become a Staff Engineer "
    )
    assert req.skills == "Python, FastAPI"
    assert req.interests == "AI Systems"
    assert req.goal == "Become a Staff Engineer"


# ==========================================
# 2. PARAMETRIZED INPUT VALIDATION TESTS
# ==========================================

@pytest.mark.parametrize("skills,interests,goal,is_valid", [
    ("Python, JS", "Web Dev", "Full-Stack Dev", True),
    ("", "AI", "Become AI Dev", False),
    ("Python", "", "Become AI Dev", False),
    ("Python", "AI", "", False),
    ("  \x00\x08  ", "AI", "Become AI Dev", False),
    ("P" * 501, "AI", "Become AI Dev", False),
])
def test_career_request_validation_parametrized(skills: str, interests: str, goal: str, is_valid: bool) -> None:
    if is_valid:
        req = CareerGuidanceRequest(skills=skills, interests=interests, goal=goal)
        assert req.skills is not None
    else:
        with pytest.raises(ValidationError):
            CareerGuidanceRequest(skills=skills, interests=interests, goal=goal)


# ==========================================
# 3. SCHEMA MAPPING & DOMAIN TRANSFORMATION
# ==========================================

def test_map_llm_response_to_domain_model() -> None:
    llm_resp = CareerGuidanceLLMResponse(
        career_paths=["AI Developer", "ML Engineer"],
        skills_to_improve=["Pytest", "FastAPI", "Docker"],
        project_ideas=["Test Framework"],
        learning_roadmap=["Days 1-7: Python"],
        internship_tips=["Open Source"],
        motivation_quote="Always be testing!",
        formatted_markdown="### Guidance",
        category="positive",
        confidence=0.95
    )

    domain_model = map_llm_response_to_domain(llm_resp)

    assert isinstance(domain_model, CareerRecommendation)
    assert domain_model.career_paths == ["AI Developer", "ML Engineer"]
    assert domain_model.skills_to_improve == ["Pytest", "FastAPI", "Docker"]
    assert domain_model.motivation_tip == "Always be testing!"
    assert domain_model.category == "positive"
    assert 0.0 <= domain_model.confidence <= 1.0


# ==========================================
# 4. DOMAIN BUSINESS RULE VALIDATION LOGIC
# ==========================================

def test_domain_model_valid_business_rules() -> None:
    rec = CareerRecommendation(
        career_paths=["AI Engineer"],
        skills_to_improve=["Python", "FastAPI"],
        project_ideas=["Project 1"],
        learning_roadmap=["Roadmap 1"],
        internship_tips=["Tip 1"],
        motivation_tip="Work hard!",
        formatted_markdown="MD content",
        category="positive",
        confidence=0.9
    )
    assert rec.category == "positive"
    assert rec.confidence == 0.9


def test_domain_model_business_rule_violation_skills_count() -> None:
    with pytest.raises(ValidationError) as exc_info:
        CareerRecommendation(
            career_paths=["AI Engineer", "ML Engineer", "DevOps"],
            skills_to_improve=["Python"],  # 1 skill < 3 paths -> Rule violation
            project_ideas=["Project 1"],
            learning_roadmap=["Roadmap 1"],
            internship_tips=["Tip 1"],
            motivation_tip="Work hard!",
            formatted_markdown="MD content",
            category="positive",
            confidence=0.9
        )
    assert "Business Rule Violation" in str(exc_info.value)


def test_domain_model_business_rule_violation_missing_projects() -> None:
    with pytest.raises(ValidationError) as exc_info:
        CareerRecommendation(
            career_paths=["AI Engineer"],
            skills_to_improve=["Python"],
            project_ideas=[],  # 0 projects with roadmap > 0 -> Rule violation
            learning_roadmap=["Days 1-7: Learn"],
            internship_tips=["Tip 1"],
            motivation_tip="Work hard!",
            formatted_markdown="MD content",
            category="positive",
            confidence=0.85
        )
    exc_str = str(exc_info.value)
    assert "Business Rule Violation" in exc_str or "List should have at least 1 item" in exc_str or "too_short" in exc_str


# ==========================================
# 5. PII PROTECTION TEST
# ==========================================

def test_fallback_response_contains_no_pii() -> None:
    fallback = generate_fallback_llm_response("Python", "AI", "Become AI Engineer")
    assert not contains_pii(fallback.formatted_markdown)
    assert not contains_pii(fallback.motivation_quote)


# ==========================================
# 6. BONUS STRETCH: HYPOTHESIS PROPERTY TEST
# ==========================================

@hypothesis_settings(max_examples=10, deadline=None)
@given(
    skills=st.text(min_size=2, max_size=100),
    interests=st.text(min_size=2, max_size=100),
    goal=st.text(min_size=5, max_size=100)
)
def test_hypothesis_property_based_input_validation(skills: str, interests: str, goal: str) -> None:
    """Generates random string inputs and verifies validation never crashes unexpectedly."""
    try:
        req = CareerGuidanceRequest(skills=skills, interests=interests, goal=goal)
        assert isinstance(req.skills, str)
        assert isinstance(req.interests, str)
        assert isinstance(req.goal, str)
    except ValidationError:
        pass  # Controlled validation failure is expected for invalid inputs
