from datetime import date

from pydantic import BaseModel, Field


class EventInput(BaseModel):
    event_type: str = Field(..., examples=["Birthday party"])
    city: str = Field(..., examples=["Toronto"])
    date: date
    guest_count: int = Field(..., gt=0, examples=[50])
    budget: float = Field(..., gt=0, examples=[5000])
    vibe: str = Field(..., examples=["Elegant and cozy"])
    food_preferences: str = Field(..., examples=["Vegetarian options"])
    indoor_outdoor: str = Field(..., examples=["Outdoor"])


class BudgetItem(BaseModel):
    category: str
    amount: float
    notes: str


class TimelineItem(BaseModel):
    when: str
    task: str


class GeneratedPlan(BaseModel):
    event_summary: str
    venue_ideas: list[str]
    vendor_suggestions: list[str]
    budget_breakdown: list[BudgetItem]
    checklist: list[str]
    timeline: list[TimelineItem]
