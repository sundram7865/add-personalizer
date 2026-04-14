"use client";

import { useState, useCallback } from "react";
import { personalizeFull } from "@/lib/api";
import type { PersonalizeState, PersonalizeStatus } from "@/types";

const INITIAL_STATE: PersonalizeState = {
  status: "idle",
  data: null,
  error: null,
};

/**
 * Drives the full 3-layer personalization pipeline.
 * Components only see: state, run(), reset().
 */
export function usePersonalize() {
  const [state, setState] = useState<PersonalizeState>(INITIAL_STATE);

  const setStatus = (status: PersonalizeStatus) =>
    setState((prev) => ({ ...prev, status }));

  const run = useCallback(
    async (adImageUrl: string, landingPageUrl: string) => {
      // Reset any previous result
      setState({ status: "analyzing", data: null, error: null });

      try {
        // Step labels so the UI can show live progress.
        // The backend chains all 3 steps internally — we just simulate the UI steps.
        setStatus("analyzing");
        await new Promise((r) => setTimeout(r, 800)); // brief pause for UX feel

        setStatus("scraping");
        await new Promise((r) => setTimeout(r, 600));

        setStatus("personalizing");

        const data = await personalizeFull({
          ad_image_url: adImageUrl,
          landing_page_url: landingPageUrl,
        });

        setState({ status: "done", data, error: null });
      } catch (err: unknown) {
        const message =
          err instanceof Error ? err.message : "An unexpected error occurred.";
        setState({ status: "error", data: null, error: message });
      }
    },
    []
  );

  const reset = useCallback(() => setState(INITIAL_STATE), []);

  return { state, run, reset };
}