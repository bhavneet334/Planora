from schemas.event import BudgetItem, EventInput, GeneratedPlan, TimelineItem


def generate_plan(event: EventInput) -> GeneratedPlan:
    """Return a mock plan based on user input. AI generation comes later."""
    venue_budget = round(event.budget * 0.4, 2)
    catering_budget = round(event.budget * 0.35, 2)
    decor_budget = round(event.budget * 0.15, 2)
    misc_budget = round(event.budget * 0.1, 2)

    setting = event.indoor_outdoor.lower()
    venue_suffix = "garden venues" if "out" in setting else "event halls"

    return GeneratedPlan(
        event_summary=(
            f"A {event.vibe.lower()} {event.event_type.lower()} for "
            f"{event.guest_count} guests in {event.city} on {event.date}. "
            f"Budget: ${event.budget:,.0f}. Food preference: {event.food_preferences}."
        ),
        venue_ideas=[
            f"{event.city} {venue_suffix} with space for {event.guest_count} guests",
            f"Boutique {setting} venue matching a {event.vibe.lower()} vibe",
            f"Community space in {event.city} with flexible layout options",
        ],
        vendor_suggestions=[
            f"Caterer specializing in {event.food_preferences.lower()}",
            "Local photographer for event coverage",
            "DJ or live band based on guest count and vibe",
            "Decorator aligned with your theme and budget",
        ],
        budget_breakdown=[
            BudgetItem(
                category="Venue",
                amount=venue_budget,
                notes=f"Estimated for {setting} options in {event.city}",
            ),
            BudgetItem(
                category="Catering",
                amount=catering_budget,
                notes=f"Covers {event.guest_count} guests with {event.food_preferences.lower()}",
            ),
            BudgetItem(
                category="Decor",
                amount=decor_budget,
                notes=f"Supports a {event.vibe.lower()} atmosphere",
            ),
            BudgetItem(
                category="Miscellaneous",
                amount=misc_budget,
                notes="Invitations, tips, and small last-minute items",
            ),
        ],
        checklist=[
            "Confirm guest count and send save-the-dates",
            "Shortlist and visit top venue options",
            "Book caterer and finalize menu tasting",
            "Confirm vendors and payment schedules",
            "Create day-of run sheet and assign helpers",
        ],
        timeline=[
            TimelineItem(when="8 weeks before", task="Finalize guest list and budget"),
            TimelineItem(when="6 weeks before", task="Book venue and key vendors"),
            TimelineItem(when="3 weeks before", task="Confirm menu, decor, and timeline"),
            TimelineItem(when="1 week before", task="Final headcount and vendor check-ins"),
            TimelineItem(when="Event day", task="Setup, welcome guests, and enjoy"),
        ],
    )
