export type EventInput = {
  event_type: string
  city: string
  date: string
  guest_count: number
  budget: number
  vibe: string
  food_preferences: string
  indoor_outdoor: string
}

export type BudgetItem = {
  category: string
  amount: number
  notes: string
}

export type TimelineItem = {
  when: string
  task: string
}

export type GeneratedPlan = {
  event_summary: string
  venue_ideas: string[]
  vendor_suggestions: string[]
  budget_breakdown: BudgetItem[]
  checklist: string[]
  timeline: TimelineItem[]
}
