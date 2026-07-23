import json
from typing import Generator
from unittest.mock import Mock
import pytest

from app.schemas.career import CareerGuidanceRequest


@pytest.fixture(scope="function")
def sample_request() -> CareerGuidanceRequest:
    return CareerGuidanceRequest(
        skills="Python, FastAPI, Docker",
        interests="Artificial Intelligence, Backend Architecture",
        goal="Become a Senior AI Engineer"
    )


@pytest.fixture(scope="function")
def valid_llm_json_dict() -> dict:
    return {
        "career_paths": [
            "Senior AI Engineer",
            "GenAI Solutions Architect",
            "Backend MLOps Specialist"
        ],
        "skills_to_improve": [
            "Pytest & Testing Strategies",
            "LangChain / LlamaIndex",
            "FastAPI Async Workflows",
            "Vector Databases (Qdrant/Pinecone)"
        ],
        "project_ideas": [
            "Automated LLM Evaluation Pipeline",
            "RAG-Powered Technical Documentation Assistant"
        ],
        "learning_roadmap": [
            "Days 1-7: Pytest and LLM testing",
            "Days 8-15: Vector DB & RAG pipelines",
            "Days 16-23: Async FastAPI services",
            "Days 24-30: CI/CD Deployment and monitoring"
        ],
        "internship_tips": [
            "Build open-source tools",
            "Publish blog posts explaining AI architecture"
        ],
        "motivation_quote": "Consistency and rigorous testing build trustworthy AI systems.",
        "formatted_markdown": "### AI Mentor Guidance\n- Focus on architecture and testing.",
        "category": "positive",
        "confidence": 0.95
    }


@pytest.fixture(scope="function")
def valid_llm_json_str(valid_llm_json_dict: dict) -> str:
    return json.dumps(valid_llm_json_dict)


@pytest.fixture(scope="function")
def mock_llm_client() -> Mock:
    return Mock()


@pytest.fixture(scope="function")
def valid_llm_response(mock_llm_client: Mock, valid_llm_json_str: str) -> Mock:
    mock_resp = Mock()
    mock_resp.content = valid_llm_json_str
    mock_llm_client.invoke.return_value = mock_resp
    return mock_llm_client


@pytest.fixture(scope="function")
def malformed_response(mock_llm_client: Mock) -> Mock:
    mock_resp = Mock()
    mock_resp.content = "{ invalid json"
    mock_llm_client.invoke.return_value = mock_resp
    return mock_llm_client


@pytest.fixture(scope="function")
def timeout_response(mock_llm_client: Mock) -> Mock:
    mock_llm_client.invoke.side_effect = TimeoutError("Request timed out")
    return mock_llm_client


@pytest.fixture(scope="function")
def refusal_response(mock_llm_client: Mock) -> Mock:
    mock_resp = Mock()
    mock_resp.content = "I cannot answer this request as it violates policy."
    mock_llm_client.invoke.return_value = mock_resp
    return mock_llm_client
