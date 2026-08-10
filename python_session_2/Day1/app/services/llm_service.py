import logging
import httpx
from typing import Optional
from langchain_groq import ChatGroq
from pydantic import SecretStr
from app.config import settings
from app.schemas.career import CareerGuidanceRequest
from app.schemas.domain import CareerRecommendation
from app.schemas.llm import CareerGuidanceLLMResponse
from app.schemas.mapper import map_llm_response_to_domain

logger = logging.getLogger(__name__)


def generate_fallback_llm_response(skills: str, interests: str, goal: str) -> CareerGuidanceLLMResponse:
    md_content = f"""### 🚀 Personalized Career Mentor Roadmap

Here is your tailored career plan based on your profile:

#### 1. Best Career Paths
Given your interest in **{interests}** and skills in **{skills}**, here are the best suited career paths for your goal (**{goal}**):
* **AI-Assisted Web Developer / Engineer**: Bridging frontend development with modern generative AI tools and APIs.
* **Specialized AI Solution Architect**: Developing specialized products that address your core interest of {interests}.
* **Full-Stack Developer**: Leverages {skills} to build robust, modern applications.

#### 2. Skills To Improve & Learn
To reach your goal of **{goal}**, prioritize learning these:
* **Advanced JavaScript/TypeScript**: Essential for modern interactive UI and application logic.
* **AI API Integration**: Practice working with model APIs (OpenAI, Groq, Anthropic) to build intelligent features.
* **Backend Frameworks**: Python (Django/FastAPI) or Node.js to connect database and AI layers.
* **Database & Deployment**: SQL/NoSQL databases and hosting platforms (Vercel, Render, AWS).

#### 3. High-Impact Project Ideas
Start building these projects to showcase in your portfolio:
* **AI-Powered Interactive App**: A web app built with {skills} that utilizes APIs to recommend paths matching {interests}.
* **Personalized Portfolio Site**: Create a showcase of your projects with an embedded chatbot mentor trained to answer questions about your work.
* **Smart Dashboard**: A project focusing on {goal} that aggregates key tools and uses lightweight local intelligence.

#### 4. 30-Day Step-by-Step Learning Roadmap
* **Days 1-7 (Foundation)**: Solidify your knowledge in {skills}. Build a clean, responsive interface.
* **Days 8-15 (API Integration)**: Learn how to perform asynchronous API requests, handle JSON payloads, and manage environment variables securely.
* **Days 16-23 (Database & State)**: Connect your frontend to a backend database, storing user inputs and saving session state.
* **Days 24-30 (Deployment & Polish)**: Polish your project's UX with modern styling, deploy it live, and start sharing it on GitHub and LinkedIn.

#### 5. Internship & Job Application Tips
* **Build in Public**: Share your learning progress daily on Twitter/X or LinkedIn. It attracts recruiters looking for self-driven talents.
* **Open Source Contribution**: Contribute to repositories related to {interests} or {skills}.
* **Tailored Resume**: Highlight your experience in {skills} and explicitly state your drive towards {goal}.

#### 6. Motivation & Core Mindset
> "The best way to predict the future is to create it." 
You already have a solid foundation with **{skills}**. By aligning your daily learning with your passion for **{interests}**, you are well on your way to achieving your goal: **{goal}**. Stay consistent, build daily, and enjoy the journey!"""

    return CareerGuidanceLLMResponse(
        career_paths=[
            f"AI-Assisted Web Developer / Engineer using {skills}",
            f"Specialized AI Solution Architect focused on {interests}",
            f"Full-Stack Developer aiming for {goal}"
        ],
        skills_to_improve=[
            "Advanced JavaScript/TypeScript",
            "AI API Integration (Groq / OpenAI)",
            "Backend Frameworks (FastAPI / Django)",
            "Database & Cloud Deployment"
        ],
        project_ideas=[
            f"AI-Powered Interactive App incorporating {skills}",
            "Personalized Portfolio Site with Chatbot",
            f"Smart Dashboard targeting {goal}"
        ],
        learning_roadmap=[
            f"Days 1-7: Solidify {skills} foundation",
            "Days 8-15: API Integration & JSON handling",
            "Days 16-23: Database connection & backend state",
            "Days 24-30: UI Polish, Deployment & Sharing"
        ],
        internship_tips=[
            "Build in public on LinkedIn / GitHub",
            f"Contribute to open source projects in {interests}",
            f"Tailor resume towards {goal}"
        ],
        motivation_quote=f"You already have a solid foundation with {skills}. By aligning daily learning with {interests}, you will achieve {goal}!",
        formatted_markdown=md_content
    )


class LLMService:
    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None) -> None:
        self.api_key: Optional[str] = api_key or settings.groq_api_key
        self.model_name: str = model_name or settings.model_name
        self._llm: Optional[ChatGroq] = None

        if self.api_key:
            try:
                secret_key = SecretStr(self.api_key)
                self._llm = ChatGroq(
                    groq_api_key=secret_key,
                    model_name=self.model_name,
                    request_timeout=float(settings.request_timeout_seconds)
                )
            except (ValueError, TypeError) as exc:
                logger.warning(f"Could not initialize ChatGroq client: {exc}")

    def generate_career_guidance(self, request: CareerGuidanceRequest) -> CareerRecommendation:
        prompt = f"""You are an AI Career Mentor.

Student Skills:
{request.skills}

Interests:
{request.interests}

Career Goal:
{request.goal}

Provide:
1. Best Career Paths
2. Skills To Improve
3. Project Ideas
4. Learning Roadmap
5. Internship Tips
6. Motivation
"""

        raw_llm_response: CareerGuidanceLLMResponse

        if not self._llm:
            logger.info("Groq LLM client not available, returning fallback LLM response.")
            raw_llm_response = generate_fallback_llm_response(request.skills, request.interests, request.goal)
        else:
            try:
                response = self._llm.invoke(prompt)
                raw_text = str(response.content) if response and hasattr(response, 'content') else ""
                if not raw_text.strip():
                    raw_llm_response = generate_fallback_llm_response(request.skills, request.interests, request.goal)
                else:
                    raw_llm_response = CareerGuidanceLLMResponse(
                        career_paths=["AI Engineer", "Web Developer", "Solutions Architect"],
                        skills_to_improve=["Advanced JS/TS", "AI Integration", "FastAPI"],
                        project_ideas=["Interactive AI App", "Portfolio Chatbot"],
                        learning_roadmap=["Days 1-7: Foundation", "Days 8-15: APIs", "Days 16-30: Projects"],
                        internship_tips=["Build in public", "Tailor your resume"],
                        motivation_quote="Consistency is key to mastering AI & Software Development!",
                        formatted_markdown=raw_text
                    )
            except (httpx.HTTPError, ValueError, RuntimeError, AttributeError) as exc:
                logger.error(f"Error calling Groq API: {exc}. Using fallback guidance.")
                raw_llm_response = generate_fallback_llm_response(request.skills, request.interests, request.goal)

        # Map LLM response model explicitly to Domain Model
        domain_recommendation: CareerRecommendation = map_llm_response_to_domain(raw_llm_response)
        return domain_recommendation


llm_service = LLMService()
