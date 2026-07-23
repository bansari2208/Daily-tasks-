from typing import Annotated, List, Literal, Optional, Union
from pydantic import BaseModel, Field
from app.schemas.domain import CareerRecommendation


class SuccessResponse(BaseModel):
    type: Literal["success"] = "success"
    data: CareerRecommendation


class ErrorResponse(BaseModel):
    type: Literal["error"] = "error"
    message: str
    details: Optional[List[str]] = None


CareerAPIResponse = Annotated[
    Union[SuccessResponse, ErrorResponse],
    Field(discriminator="type")
]
