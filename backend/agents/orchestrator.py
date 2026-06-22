from typing import NotRequired, TypedDict

from langgraph.graph import END, StateGraph

from schemas.event import EventInput, GeneratedPlan
from agents.venue_agent import run_venue_agent
from agents.budget_agent import run_budget_agent
from agents.details_agent import run_details_agent


class PlanState(TypedDict):
    event: EventInput
    event_summary: NotRequired[str]
    venue_ideas: NotRequired[list[str]]
    budget_breakdown: NotRequired[list[dict]]
    vendor_suggestions: NotRequired[list[str]]
    checklist: NotRequired[list[str]]
    timeline: NotRequired[list[dict]]


def venue_node(state: PlanState) -> dict:
    result = run_venue_agent(state["event"])
    return {
        "event_summary": result["event_summary"],
        "venue_ideas": result["venue_ideas"],
    }


def budget_node(state: PlanState) -> dict:
    result = run_budget_agent(state["event"])
    return {"budget_breakdown": result["budget_breakdown"]}


def details_node(state: PlanState) -> dict:
    result = run_details_agent(state["event"])
    return {
        "vendor_suggestions": result["vendor_suggestions"],
        "checklist": result["checklist"],
        "timeline": result["timeline"],
    }


def build_graph():
    graph = StateGraph(PlanState)

    graph.add_node("venue", venue_node)
    graph.add_node("budget", budget_node)
    graph.add_node("details", details_node)

    graph.set_entry_point("venue")
    graph.add_edge("venue", "budget")
    graph.add_edge("budget", "details")
    graph.add_edge("details", END)

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
