import { useEffect, useState, type FormEvent } from "react";
import { generatePlan } from "./api/plans";
import type { EventInput, GeneratedPlan } from "./types/plan";
import heroImage from "./assets/hero-illustration.svg";
import "./App.css";

const emptyForm: EventInput = {
  event_type: "",
  city: "",
  date: "",
  guest_count: 50,
  budget: 5000,
  vibe: "",
  food_preferences: "",
  indoor_outdoor: "Outdoor",
};

const EXAMPLE_FORM: EventInput = {
  event_type: "Birthday party",
  city: "Chicago",
  date: "2026-06-19",
  guest_count: 26,
  budget: 48000,
  vibe: "Fun and lively",
  food_preferences: "Vegetarian options",
  indoor_outdoor: "Indoor",
};

const FEATURES = [
  "Real venue search",
  "Budget breakdown",
  "Checklist & timeline",
];

const LOADING_STEPS = [
  "Searching venues (cache or Google Places)…",
  "Selecting venues and writing summary…",
  "Building budget breakdown…",
  "Adding vendors, checklist, and timeline…",
];

function App() {
  const [form, setForm] = useState<EventInput>(emptyForm);
  const [plan, setPlan] = useState<GeneratedPlan | null>(null);
  const [loading, setLoading] = useState(false);
  const [loadingStep, setLoadingStep] = useState(0);
  const [error, setError] = useState<string | null>(null);

  function updateField<K extends keyof EventInput>(
    key: K,
    value: EventInput[K],
  ) {
    setForm((prev) => ({ ...prev, [key]: value }));
  }

  function fillExample() {
    setForm(EXAMPLE_FORM);
    setPlan(null);
    setError(null);
    document.querySelector(".event-form")?.scrollIntoView({
      behavior: "smooth",
      block: "start",
    });
  }

  useEffect(() => {
    if (plan) {
      document.querySelector(".results")?.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
    }
  }, [plan]);

  useEffect(() => {
    if (!loading) {
      setLoadingStep(0);
      return;
    }

    const interval = window.setInterval(() => {
      setLoadingStep((prev) =>
        prev < LOADING_STEPS.length - 1 ? prev + 1 : prev,
      );
    }, 3500);

    return () => window.clearInterval(interval);
  }, [loading]);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setLoading(true);
    setLoadingStep(0);
    setError(null);

    try {
      const result = await generatePlan(form);
      setPlan(result);
    } catch (err) {
      setPlan(null);
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="page">
      <header className="hero">
        <div className="hero-copy">
          <h1>Planora AI</h1>
          <p className="hero-tagline">
            Turn event details into a starter plan with real venues, a budget
            breakdown, vendors, checklist, and timeline.
          </p>
          <ul className="feature-chips" aria-label="Features">
            {FEATURES.map((feature) => (
              <li key={feature}>{feature}</li>
            ))}
          </ul>
          <button type="button" className="btn-example" onClick={fillExample}>
            Try an example →
          </button>
        </div>
        <div className="hero-visual">
          <img
            src={heroImage}
            alt="Event plan with calendar and checklist"
            className="hero-image"
          />
        </div>
      </header>

      <form className="card form event-form" onSubmit={handleSubmit}>
        <div className="form-header">
          <h2>Event details</h2>
          <button type="button" className="btn-link" onClick={fillExample}>
            Fill example
          </button>
        </div>

        <div className="form-grid">
          <label>
            Event type
            <input
              value={form.event_type}
              onChange={(e) => updateField("event_type", e.target.value)}
              placeholder="Birthday party"
            />
          </label>

          <label>
            City
            <input
              value={form.city}
              onChange={(e) => updateField("city", e.target.value)}
              placeholder="Toronto"
              required
            />
          </label>

          <label>
            Date
          <input
            type="date"
            value={form.date}
            onChange={(e) => updateField("date", e.target.value)}
            required
            />
          </label>

          <label>
            Guest count
          <input
            type="number"
            min={1}
            value={form.guest_count}
            onChange={(e) => updateField("guest_count", Number(e.target.value))}
            required
            />
          </label>

          <label>
            Budget
          <input
            type="number"
            min={1}
            value={form.budget}
            onChange={(e) => updateField("budget", Number(e.target.value))}
            required
            />
          </label>

          <label>
            Vibe
          <input
            value={form.vibe}
            onChange={(e) => updateField("vibe", e.target.value)}
            placeholder="Elegant and cozy"
            required
            />
          </label>

          <label>
            Food preferences
          <input
            value={form.food_preferences}
            onChange={(e) => updateField("food_preferences", e.target.value)}
            placeholder="Vegetarian options"
            required
            />
          </label>

          <label>
            Indoor / Outdoor
          <select
            value={form.indoor_outdoor}
            onChange={(e) => updateField("indoor_outdoor", e.target.value)}
          >
            <option value="Outdoor">Outdoor</option>
            <option value="Indoor">Indoor</option>
          </select>
        </label>
        </div>

        <button type="submit" className="btn-primary" disabled={loading}>
          {loading ? "Generating plan…" : "Generate plan"}
        </button>

        {loading && (
          <div className="loading-panel" aria-live="polite">
            <div className="loading-bar">
              <div
                className="loading-bar-fill"
                style={{
                  width: `${((loadingStep + 1) / LOADING_STEPS.length) * 100}%`,
                }}
              />
            </div>
            <p className="loading-step">{LOADING_STEPS[loadingStep]}</p>
            <p className="loading-hint">
              Plans usually take 15–30 seconds while agents run.
            </p>
          </div>
        )}

        {error && <p className="error">{error}</p>}
      </form>

      {plan && (
        <section className="card results">
          <h2>Your plan</h2>
          <div className="block">
            <h3>Event summary</h3>
            <p>{plan.event_summary}</p>
          </div>
          <div className="block">
            <h3>Venue ideas</h3>
            <ul>
              {plan.venue_ideas.map((venue) => (
                <li key={venue}>{venue}</li>
              ))}
            </ul>
          </div>
          <div className="block">
            <h3>Vendor suggestions</h3>
            <ul>
              {plan.vendor_suggestions.map((vendor) => (
                <li key={vendor}>{vendor}</li>
              ))}
            </ul>
          </div>
          <div className="block">
            <h3>Budget breakdown</h3>
            <ul>
              {plan.budget_breakdown.map((item) => (
                <li key={item.category}>
                  <strong>{item.category}</strong>: ${item.amount} — {item.notes}
                </li>
              ))}
            </ul>
          </div>
          <div className="block">
            <h3>Checklist</h3>
            <ul>
              {plan.checklist.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </div>
          <div className="block">
            <h3>Timeline</h3>
            <ul>
              {plan.timeline.map((item) => (
                <li key={`${item.when}-${item.task}`}>
                  <strong>{item.when}</strong>: {item.task}
                </li>
              ))}
            </ul>
          </div>
        </section>
      )}
    </main>
  );
}

export default App;
