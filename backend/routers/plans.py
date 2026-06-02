from fastapi import APIRouter

from schemas.event import EventInput, GeneratedPlan
from services.plan_service import generate_plan

router = APIRouter(prefix="/plans", tags=["plans"])


@router.post("/generate", response_model=GeneratedPlan)
def create_plan(event: EventInput) -> GeneratedPlan:
    return generate_plan(event)
