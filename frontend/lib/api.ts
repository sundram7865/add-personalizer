import type {
  PersonalizeFullRequest,
  PersonalizeFullResponse,
  ApiError,
} from "@/types";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

// ─── Generic fetcher ──────────────────────────────────────────────────────────

async function apiFetch<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  const data = await res.json();

  if (!res.ok) {
    const err = data as ApiError;
    throw new Error(err.error ?? `Request failed with status ${res.status}`);
  }

  return data as T;
}

// ─── Public API ───────────────────────────────────────────────────────────────

/**
 * Runs all 3 AI layers in one call.
 * Analyzes the ad → scrapes the page → personalizes the copy.
 */
export async function personalizeFull(
  payload: PersonalizeFullRequest
): Promise<PersonalizeFullResponse> {
  return apiFetch<PersonalizeFullResponse>("/api/personalize-full", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}