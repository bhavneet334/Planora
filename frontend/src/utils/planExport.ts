import { jsPDF } from "jspdf";
import type { EventInput, GeneratedPlan } from "../types/plan";

const MARGIN_X = 56;
const MARGIN_TOP = 56;
const MARGIN_BOTTOM = 56;
const BODY_SIZE = 10.5;
const BODY_LINE = 15;
const HEADING_SIZE = 12;
const TITLE_SIZE = 18;

const COLOR_TEXT = [26, 29, 33] as const;
const COLOR_MUTED = [92, 99, 112] as const;
const COLOR_FOOTER = [139, 145, 154] as const;
const COLOR_LINE = [226, 229, 234] as const;

function downloadFilename(form: EventInput): string {
  const slug = (form.city || "event").toLowerCase().replace(/\s+/g, "-");
  return `planora-${slug}-${form.date || "plan"}.pdf`;
}

class PdfWriter {
  private y = MARGIN_TOP;
  private readonly maxWidth: number;
  private readonly pageHeight: number;
  private readonly doc: jsPDF;

  constructor(doc: jsPDF) {
    this.doc = doc;
    this.maxWidth = doc.internal.pageSize.getWidth() - MARGIN_X * 2;
    this.pageHeight = doc.internal.pageSize.getHeight();
  }

  private newPageIfNeeded(height: number) {
    if (this.y + height > this.pageHeight - MARGIN_BOTTOM) {
      this.doc.addPage();
      this.y = MARGIN_TOP;
    }
  }

  brand(text: string) {
    this.doc.setFont("helvetica", "normal");
    this.doc.setFontSize(9);
    this.doc.setTextColor(...COLOR_MUTED);
    this.newPageIfNeeded(BODY_LINE);
    this.doc.text(text, MARGIN_X, this.y);
    this.y += BODY_LINE + 2;
  }

  title(text: string) {
    this.doc.setFont("helvetica", "bold");
    this.doc.setFontSize(TITLE_SIZE);
    this.doc.setTextColor(...COLOR_TEXT);
    for (const line of this.doc.splitTextToSize(text, this.maxWidth)) {
      this.newPageIfNeeded(22);
      this.doc.text(line, MARGIN_X, this.y);
      this.y += 22;
    }
    this.y += 4;
  }

  meta(text: string) {
    this.doc.setFont("helvetica", "normal");
    this.doc.setFontSize(10);
    this.doc.setTextColor(...COLOR_MUTED);
    for (const line of this.doc.splitTextToSize(text, this.maxWidth)) {
      this.newPageIfNeeded(BODY_LINE);
      this.doc.text(line, MARGIN_X, this.y);
      this.y += BODY_LINE;
    }
    this.y += 16;
  }

  sectionHeading(text: string) {
    this.newPageIfNeeded(32);
    this.y += 8;
    this.doc.setFont("helvetica", "bold");
    this.doc.setFontSize(HEADING_SIZE);
    this.doc.setTextColor(...COLOR_TEXT);
    this.doc.text(text, MARGIN_X, this.y);
    this.y += 8;
    this.doc.setDrawColor(...COLOR_LINE);
    this.doc.setLineWidth(0.5);
    this.doc.line(MARGIN_X, this.y, MARGIN_X + this.maxWidth, this.y);
    this.y += 12;
  }

  paragraph(text: string) {
    this.doc.setFont("helvetica", "normal");
    this.doc.setFontSize(BODY_SIZE);
    this.doc.setTextColor(...COLOR_TEXT);
    for (const line of this.doc.splitTextToSize(text, this.maxWidth)) {
      this.newPageIfNeeded(BODY_LINE);
      this.doc.text(line, MARGIN_X, this.y);
      this.y += BODY_LINE;
    }
    this.y += 10;
  }

  hint(text: string) {
    this.doc.setFont("helvetica", "italic");
    this.doc.setFontSize(9.5);
    this.doc.setTextColor(...COLOR_MUTED);
    this.newPageIfNeeded(BODY_LINE);
    this.doc.text(text, MARGIN_X, this.y);
    this.y += BODY_LINE + 6;
  }

  bullets(items: string[]) {
    const bulletX = MARGIN_X;
    const textX = MARGIN_X + 14;
    const textWidth = this.maxWidth - 14;

    this.doc.setFont("helvetica", "normal");
    this.doc.setFontSize(BODY_SIZE);
    this.doc.setTextColor(...COLOR_TEXT);

    for (const item of items) {
      const lines = this.doc.splitTextToSize(item, textWidth);
      for (let i = 0; i < lines.length; i++) {
        this.newPageIfNeeded(BODY_LINE);
        if (i === 0) {
          this.doc.text("•", bulletX, this.y);
        }
        this.doc.text(lines[i], textX, this.y);
        this.y += BODY_LINE;
      }
      this.y += 3;
    }
    this.y += 6;
  }

  footer(text: string) {
    this.newPageIfNeeded(20);
    this.y += 10;
    this.doc.setFont("helvetica", "italic");
    this.doc.setFontSize(9);
    this.doc.setTextColor(...COLOR_FOOTER);
    this.doc.text(text, MARGIN_X, this.y);
  }
}

export function formatPlanAsMarkdown(
  form: EventInput,
  plan: GeneratedPlan,
): string {
  const budgetTotal = plan.budget_breakdown.reduce(
    (sum, item) => sum + item.amount,
    0,
  );

  const lines = [
    `Event Plan — ${form.event_type || "Event"}`,
    "",
    `City: ${form.city}`,
    `Date: ${form.date}`,
    `Guests: ${form.guest_count}`,
    `Budget: $${form.budget.toLocaleString()}`,
    `Vibe: ${form.vibe}`,
    `Food: ${form.food_preferences}`,
    `Setting: ${form.indoor_outdoor}`,
    "",
    "Event summary",
    plan.event_summary,
    "",
    "Venue ideas",
    ...plan.venue_ideas.map((venue) => `• ${venue}`),
    "",
    "Vendor suggestions",
    "Suggested names — confirm before booking.",
    ...plan.vendor_suggestions.map((vendor) => `• ${vendor}`),
    "",
    `Budget breakdown (total: $${budgetTotal.toLocaleString()})`,
    ...plan.budget_breakdown.map(
      (item) =>
        `• ${item.category}: $${item.amount.toLocaleString()} — ${item.notes}`,
    ),
    "",
    "Checklist",
    ...plan.checklist.map((item) => `☐ ${item}`),
    "",
    "Timeline",
    ...plan.timeline.map((item) => `• ${item.when}: ${item.task}`),
    "",
    "Generated by Planora AI",
  ];

  return lines.join("\n");
}

export function downloadPlanPdf(form: EventInput, plan: GeneratedPlan): void {
  const doc = new jsPDF({ unit: "pt", format: "letter" });
  const writer = new PdfWriter(doc);
  const budgetTotal = plan.budget_breakdown.reduce(
    (sum, item) => sum + item.amount,
    0,
  );

  const meta = [
    form.city,
    form.date,
    `${form.guest_count} guests`,
    `$${form.budget.toLocaleString()} budget`,
    form.vibe,
    `${form.food_preferences}, ${form.indoor_outdoor}`,
  ].join(" · ");

  writer.brand("Planora AI");
  writer.title(`${form.event_type || "Event"} plan`);
  writer.meta(meta);

  writer.sectionHeading("Event summary");
  writer.paragraph(plan.event_summary);

  writer.sectionHeading("Venue ideas");
  writer.bullets(plan.venue_ideas);

  writer.sectionHeading("Vendor suggestions");
  writer.hint("Suggested names — confirm before booking.");
  writer.bullets(plan.vendor_suggestions);

  writer.sectionHeading(
    `Budget breakdown (total $${budgetTotal.toLocaleString()})`,
  );
  writer.bullets(
    plan.budget_breakdown.map(
      (item) =>
        `${item.category}: $${item.amount.toLocaleString()} — ${item.notes}`,
    ),
  );

  writer.sectionHeading("Checklist");
  writer.bullets(plan.checklist.map((item) => `[ ] ${item}`));

  writer.sectionHeading("Timeline");
  writer.bullets(plan.timeline.map((item) => `${item.when}: ${item.task}`));

  writer.footer("Generated by Planora AI");

  doc.save(downloadFilename(form));
}
