from schemas.event import EventInput

BUDGET_TOLERANCE = 0.10


def validate_budget(event: EventInput, budget_breakdown: list[dict]) -> bool:
    if not budget_breakdown:
        return False

    for item in budget_breakdown:
        if not item.get("category") or item.get("amount") is None:
            return False
        if float(item["amount"]) < 0:
            return False

    total = sum(float(item["amount"]) for item in budget_breakdown)
    target = float(event.budget)
    allowed_gap = target * BUDGET_TOLERANCE

    return abs(total - target) <= allowed_gap
