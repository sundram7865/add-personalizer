import type { PersonalizeStatus } from "@/types";

/** Returns a human-readable label for each pipeline status step. */
export function getStatusLabel(status: PersonalizeStatus): string {
  const labels: Record<PersonalizeStatus, string> = {
    idle: "Ready",
    analyzing: "Analyzing your ad creative...",
    scraping: "Reading the landing page...",
    personalizing: "Personalizing copy with AI...",
    done: "Done",
    error: "Something went wrong",
  };
  return labels[status];
}

/** Returns the step index (0-based) for the progress indicator. */
export function getStatusStep(status: PersonalizeStatus): number {
  const steps: Record<PersonalizeStatus, number> = {
    idle: -1,
    analyzing: 0,
    scraping: 1,
    personalizing: 2,
    done: 3,
    error: -1,
  };
  return steps[status];
}

/** Truncates a string with ellipsis if it exceeds maxLen. */
export function truncate(str: string, maxLen: number): string {
  if (str.length <= maxLen) return str;
  return str.slice(0, maxLen).trimEnd() + "…";
}

/** Maps CRO principle names to a short color token for badges. */
export function principleColor(principle: string): string {
  const map: Record<string, string> = {
    "Message Match": "accent",
    Specificity: "blue",
    "Audience Alignment": "purple",
    "Value First": "green",
    Urgency: "orange",
    Trust: "teal",
  };
  return map[principle] ?? "gray";
}