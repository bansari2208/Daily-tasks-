from unittest.mock import Mock
import pytest

from app.schemas.career import CareerGuidanceRequest
from app.schemas.domain import CareerRecommendation
from app.services.llm_service import LLMService


# ==========================================
# 1. SUCCESSFUL RESPONSE TEST
# ==========================================

def test_mock_llm_successful_response(
    valid_llm_response: Mock,
    sample_request: CareerGuidanceRequest
) -> None:
    service = LLMService(llm_client=valid_llm_response)
    result = service.generate_career_guidance(sample_request)

    # Tolerant and structural assertions
    assert isinstance(result, CareerRecommendation)
    assert result.category is not None
    assert result.category == "positive"
    assert 0.0 <= result.confidence <= 1.0
    assert len(result.career_paths) >= 1
    assert len(result.skills_to_improve) >= len(result.career_paths)
    assert result.motivation_tip is not None
    assert result.formatted_markdown is not None


# ==========================================
# 2. MALFORMED JSON RESPONSE TEST
# ==========================================

def test_mock_llm_malformed_json_response(
    malformed_response: Mock,
    sample_request: CareerGuidanceRequest
) -> None:
    service = LLMService(llm_client=malformed_response)

    # Verify controlled error handling on malformed JSON
    with pytest.raises(ValueError) as exc_info:
        service.generate_career_guidance(sample_request)

    assert "parsing/validation failed" in str(exc_info.value) or "malformed" in str(exc_info.value).lower()


# ==========================================
# 3. TIMEOUT SCENARIO TEST
# ==========================================

def test_mock_llm_timeout_scenario(
    timeout_response: Mock,
    sample_request: CareerGuidanceRequest
) -> None:
    service = LLMService(llm_client=timeout_response)

    # Verify TimeoutError is caught and raised as a controlled timeout error
    with pytest.raises(TimeoutError) as exc_info:
        service.generate_career_guidance(sample_request)

    assert "timed out" in str(exc_info.value).lower()


# ==========================================
# 4. REFUSAL / EMPTY RESPONSE TEST
# ==========================================

def test_mock_llm_refusal_response(
    refusal_response: Mock,
    sample_request: CareerGuidanceRequest
) -> None:
    service = LLMService(llm_client=refusal_response)

    # Verify safe refusal handling without creating invalid domain objects
    with pytest.raises(ValueError) as exc_info:
        service.generate_career_guidance(sample_request)

    assert "refused" in str(exc_info.value).lower() or "empty" in str(exc_info.value).lower()
