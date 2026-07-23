from pathlib import Path
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.api.deps import get_llm_service, get_memory_service
from app.schemas.api_response import CareerAPIResponse, SuccessResponse
from app.schemas.career import CareerGuidanceRequest
from app.schemas.domain import CareerRecommendation
from app.services.llm_service import LLMService
from app.services.memory_service import MemoryService

router = APIRouter()

templates_dir = Path(__file__).resolve().parent.parent.parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))


@router.get("/", response_class=HTMLResponse)
async def home(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request=request, name="index.html")


@router.post("/career", response_class=HTMLResponse)
async def career_form(
    request: Request,
    skills: str = Form(...),
    interests: str = Form(...),
    goal: str = Form(...),
    llm_svc: LLMService = Depends(get_llm_service),
    mem_svc: MemoryService = Depends(get_memory_service)
) -> HTMLResponse:
    guidance_req = CareerGuidanceRequest(
        skills=skills,
        interests=interests,
        goal=goal
    )

    recommendation: CareerRecommendation = llm_svc.generate_career_guidance(guidance_req)

    mem_svc.add_entry(
        skills=guidance_req.skills,
        interests=guidance_req.interests,
        goal=guidance_req.goal
    )

    return templates.TemplateResponse(
        request=request,
        name="result.html",
        context={
            "formatted_markdown": recommendation.formatted_markdown,
            "guidance": recommendation
        }
    )


@router.post("/api/v1/career", response_model=CareerAPIResponse)
async def career_api(
    payload: CareerGuidanceRequest,
    llm_svc: LLMService = Depends(get_llm_service),
    mem_svc: MemoryService = Depends(get_memory_service)
) -> SuccessResponse:
    recommendation: CareerRecommendation = llm_svc.generate_career_guidance(payload)
    mem_svc.add_entry(
        skills=payload.skills,
        interests=payload.interests,
        goal=payload.goal
    )
    return SuccessResponse(data=recommendation)
