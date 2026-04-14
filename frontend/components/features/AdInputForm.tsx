"use client";

import { useState, FormEvent } from "react";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";

interface AdInputFormProps {
  onSubmit: (adImageUrl: string, landingPageUrl: string) => void;
  loading: boolean;
}

function isValidUrl(value: string): boolean {
  try {
    const url = new URL(value);
    return url.protocol === "http:" || url.protocol === "https:";
  } catch {
    return false;
  }
}

export function AdInputForm({ onSubmit, loading }: AdInputFormProps) {
  const [adUrl, setAdUrl] = useState("");
  const [pageUrl, setPageUrl] = useState("");
  const [errors, setErrors] = useState({ adUrl: "", pageUrl: "" });

  function validate(): boolean {
    const next = { adUrl: "", pageUrl: "" };
    if (!adUrl.trim()) next.adUrl = "Ad image URL is required";
    else if (!isValidUrl(adUrl)) next.adUrl = "Enter a valid https:// URL";

    if (!pageUrl.trim()) next.pageUrl = "Landing page URL is required";
    else if (!isValidUrl(pageUrl)) next.pageUrl = "Enter a valid https:// URL";

    setErrors(next);
    return !next.adUrl && !next.pageUrl;
  }

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (validate()) onSubmit(adUrl.trim(), pageUrl.trim());
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-5" noValidate>
      <Input
        label="Ad Creative URL"
        type="url"
        placeholder="https://example.com/ad-banner.png"
        value={adUrl}
        onChange={(e) => setAdUrl(e.target.value)}
        error={errors.adUrl}
        hint="Direct link to your ad image (JPG, PNG, WebP)"
        disabled={loading}
        autoComplete="off"
      />

      <Input
        label="Landing Page URL"
        type="url"
        placeholder="https://yourproduct.com"
        value={pageUrl}
        onChange={(e) => setPageUrl(e.target.value)}
        error={errors.pageUrl}
        hint="The page visitors land on after clicking the ad"
        disabled={loading}
        autoComplete="off"
      />

      <Button
        type="submit"
        variant="primary"
        loading={loading}
        className="mt-1 w-full py-3.5 text-base"
      >
        {loading ? "Personalizing…" : "Personalize Page"}
      </Button>
    </form>
  );
}