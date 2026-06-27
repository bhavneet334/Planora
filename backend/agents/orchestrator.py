from typing import Literal, NotRequired, TypedDict

from langgraph.graph import END, StateGraph

from schemas.event import EventInput, GeneratedPlan
from agents.venue_research import run_venue_research
from agents.venue_agent import run_venue_agent
from agents.budget_agent import run_budget_agent
from agents.details_agent import run_details_agent
from agents.validator import validate_budget

MAX_BUDGET_RETRIES = 2


class PlanState(TypedDict):
    event: EventInput
    researched_venues : NotRequired[list[dict]]
    event_summary: NotRequired[str]
    venue_ideas: NotRequired[list[str]]
    budget_breakdown: NotRequired[list[dict]]
    vendor_suggestions: NotRequired[list[str]]
    checklist: NotRequired[list[str]]
    timeline: NotRequired[list[dict]]
    validation_passed: NotRequired[bool]
    budget_retry_count: NotRequired[int]

def venue_research_node(state:PlanState) -> dict:
    venues = run_venue_research(state["event"])
    return {"researched_venues":venues}


def venue_node(state: PlanState) -> dict:
    researched = state.get["researched_venues",[]]
    result = run_venue_agent(state["event"], researched_venues=researched)
    return {
        "event_summary": result["event_summary"],
        "venue_ideas": result["venue_ideas"],
    }


def budget_node(state: PlanState) -> dict:
    result = run_budget_agent(state["event"])

    retry_count = state.get("budget_retry_count", 0)
    if state.get("validation_passed") is False:
        retry_count+=1

    return {"budget_breakdown": result["budget_breakdown"], 
            "budget_retry_count" : retry_count,
            "validation_passed" : False
           }


def details_node(state: PlanState) -> dict:
    result = run_details_agent(state["event"])
    return {
        "vendor_suggestions": result["vendor_suggestions"],
        "checklist": result["checklist"],
        "timeline": result["timeline"],
    }


def validator_node(state: PlanState) -> dict:
    is_valid = validate_budget(state["event"], state.get("budget_breakdown", []))
    return {"validation_passed": is_valid}


def route_after_validation(state: PlanState) -> Literal["budget", "__end__"]:
    if state.get("validation_passed"):
        return "__end__"

    if state.get("budget_retry_count", 0) >= MAX_BUDGET_RETRIES:
        return "__end__"

    return "budget"


def build_graph():
    graph = StateGraph(PlanState)

    graph.add_node("venue_research", venue_research_node)
    graph.add_node("venue", venue_node)
    graph.add_node("budget", budget_node)
    graph.add_node("details", details_node)
    graph.add_node("validator", validator_node)

    graph.set_entry_point("venue_research")
    graph.add_edge("venue_research","venue")
    graph.add_edge("venue", "budget")
    graph.add_edge("budget", "details")
    graph.add_edge("details", "validator")
    graph.add_conditional_edges("validator", route_after_validation)

    return graph.compile()


_graph = build_graph()


def run_orchestrator(event: EventInput) -> GeneratedPlan:
    final_state = _graph.invoke({"event": event})

    return GeneratedPlan(
        event_summary=final_state["event_summary"],
        venue_ideas=final_state["venue_ideas"],
        budget_breakdown=final_state["budget_breakdown"],
        vendor_suggestions=final_state["vendor_suggestions"],
        checklist=final_state["checklist"],
        timeline=final_state["timeline"],
    )
