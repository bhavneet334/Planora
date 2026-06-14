import type { EventInput, GeneratedPlan } from '../types/plan'

const API_BASE = 'http://127.0.0.1:8000'

export async function generatePlan(event: EventInput): Promise<GeneratedPlan> {
  const response = await fetch(`${API_BASE}/plans/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(event),
  })

  if (!response.ok) {
    const text = await response.text()
    throw new Error(text || 'Failed to generate plan')
  }

  return response.json()
}
