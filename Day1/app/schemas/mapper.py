from app.schemas.domain import CareerRecommendation
from app.schemas.llm import CareerGuidanceLLMResponse


def map_llm_response_to_domain(llm_resp: CareerGuidanceLLMResponse) -> CareerRecommendation:
    """Explicitly maps raw LLM structured output to domain entity."""
    return CareerRecommendation(
        career_paths=list(llm_resp.career_paths),
        skills_to_improve=list(llm_resp.skills_to_improve),
        project_ideas=list(llm_resp.project_ideas),
        learning_roadmap=list(llm_resp.learning_roadmap),
        internship_tips=list(llm_resp.internship_tips),
        motivation_tip=llm_resp.motivation_quote,
        formatted_markdown=llm_resp.formatted_markdown,
    )
