// ─── Request types ────────────────────────────────────────────────────────────

export interface PersonalizeFullRequest {
  ad_image_url: string;
  landing_page_url: string;
}

// ─── Domain types ─────────────────────────────────────────────────────────────

export interface AdSignals {
  headline: string;
  cta_text: string;
  tone: string;
  target_audience: string;
  value_proposition: string;
  emotional_hook: string;
  color_mood: string;
}

export interface PageElements {
  h1: string | null;
  h2: string | null;
  hero_paragraph: string | null;
  cta_button_text: string | null;
  page_title: string | null;
}

export interface ChangeItem {
  element: string;
  original: string;
  updated: string;
  cro_principle: string;
  reason: string;
}

export interface PersonalizedPage {
  modified_html: string;
  changes: ChangeItem[];
  new_elements: PageElements;
}

// ─── Response types ───────────────────────────────────────────────────────────

export interface PersonalizeFullResponse {
  success: boolean;
  ad_signals: AdSignals;
  page_elements: PageElements;
  personalized_page: PersonalizedPage;
}

export interface ApiError {
  success: false;
  error: string;
}

// ─── UI state types ───────────────────────────────────────────────────────────

export type PersonalizeStatus =
  | "idle"
  | "analyzing"
  | "scraping"
  | "personalizing"
  | "done"
  | "error";

export interface PersonalizeState {
  status: PersonalizeStatus;
  data: PersonalizeFullResponse | null;
  error: string | null;
}