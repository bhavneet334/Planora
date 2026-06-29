import { useMemo, useState } from "react";
import type { EventInput, GeneratedPlan } from "../types/plan";
import { downloadPlanPdf, formatPlanAsMarkdown } from "../utils/planExport";

const BUDGET_COLORS = [
  "#0f6b5f",
  "#3d6b8c",
  "#6b8f71",
  "#c9a227",
  "#9a6b5c",
];

type PlanResultsProps = {
  form: EventInput;
  plan: GeneratedPlan;
};

export function PlanResults({ form, plan }: PlanResultsProps) {
  const [checked, setChecked] = useState<Record<string, boolean>>({});
  const [copyStatus, setCopyStatus] = useState<string | null>(null);
  const [downloadStatus, setDownloadStatus] = useState<string | null>(null);

  const budgetTotal = useMemo(
    () => plan.budget_breakdown.reduce((sum, item) => sum + item.amount, 0),
    [plan.budget_breakdown],
  );

  const budgetDelta = budgetTotal - form.budget;

  async function handleCopy() {
    try {
      await navigator.clipboard.writeText(formatPlanAsMarkdown(form, plan));
      setCopyStatus("Copied!");
      setTimeout(() => setCopyStatus(null), 2000);
    } catch {
      setCopyStatus("Copy failed");
      setTimeout(() => setCopyStatus(null), 2000);
    }
  }

  function handleDownload() {
    setDownloadStatus("Preparing…");
    try {
      downloadPlanPdf(form, plan);
      setDownloadStatus("Downloaded");
      setTimeout(() => setDownloadStatus(null), 2000);
    } catch {
      setDownloadStatus("Failed");
      setTimeout(() => setDownloadStatus(null), 2000);
    }
  }

  function toggleChecklistItem(item: string) {
    setChecked((prev) => ({ ...prev, [item]: !prev[item] }));
  }

  return (
    <section className="card results">
      <div className="results-header">
        <div>
          <h2>Your plan</h2>
          <p className="event-meta">
            {form.event_type} · {form.city} · {form.date} · {form.guest_count}{" "}
            guests · ${form.budget.toLocaleString()}
          </p>
        </div>
        <div className="results-actions">
          <button type="button" className="btn-secondary" onClick={handleCopy}>
            {copyStatus ?? "Copy"}
          </button>
          <button
            type="button"
            className="btn-secondary"
            onClick={handleDownload}
            disabled={!!downloadStatus && downloadStatus === "Preparing…"}
          >
            {downloadStatus ?? "Download PDF"}
          </button>
        </div>
      </div>

      <div className="block block-full">
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
        <p className="hint">Suggested names — confirm before booking.</p>
        <ul>
          {plan.vendor_suggestions.map((vendor) => (
            <li key={vendor}>{vendor}</li>
          ))}
        </ul>
      </div>

      <div className="block block-full">
        <div className="block-title-row">
          <h3>Budget breakdown</h3>
          <span className="budget-total">
            Total: ${budgetTotal.toLocaleString()}
            {Math.abs(budgetDelta) >= 1 && (
              <span className="budget-delta">
                {" "}
                ({budgetDelta > 0 ? "+" : ""}
                {budgetDelta.toLocaleString()} vs target)
              </span>
            )}
          </span>
        </div>
        <div
          className="budget-bar"
          role="img"
          aria-label="Budget breakdown by category"
        >
          {plan.budget_breakdown.map((item, index) => (
            <div
              key={item.category}
              className="budget-segment"
              style={{
                width: `${(item.amount / budgetTotal) * 100}%`,
                backgroundColor: BUDGET_COLORS[index % BUDGET_COLORS.length],
              }}
              title={`${item.category}: $${item.amount.toLocaleString()}`}
            />
          ))}
        </div>
        <ul className="budget-legend">
          {plan.budget_breakdown.map((item, index) => (
            <li key={item.category}>
              <span
                className="legend-swatch"
                style={{
                  backgroundColor: BUDGET_COLORS[index % BUDGET_COLORS.length],
                }}
              />
              <strong>{item.category}</strong>: ${item.amount.toLocaleString()}{" "}
              — {item.notes}
            </li>
          ))}
        </ul>
      </div>

      <div className="block">
        <h3>Checklist</h3>
        <ul className="checklist">
          {plan.checklist.map((item) => (
            <li key={item}>
              <label className="checklist-item">
                <input
                  type="checkbox"
                  checked={!!checked[item]}
                  onChange={() => toggleChecklistItem(item)}
                />
                <span className={checked[item] ? "checked" : undefined}>
                  {item}
                </span>
              </label>
            </li>
          ))}
        </ul>
      </div>

      <div className="block">
        <h3>Timeline</h3>
        <ol className="timeline">
          {plan.timeline.map((item) => (
            <li key={`${item.when}-${item.task}`}>
              <span className="timeline-when">{item.when}</span>
              <span className="timeline-task">{item.task}</span>
            </li>
          ))}
        </ol>
      </div>
    </section>
  );
}
