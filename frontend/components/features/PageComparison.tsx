"use client";

import { useState, useRef, useEffect } from "react";

interface PageComparisonProps {
  originalUrl: string;
  modifiedHtml: string;
}

type ActiveTab = "split" | "original" | "personalized";

export function PageComparison({ originalUrl, modifiedHtml }: PageComparisonProps) {
  const [activeTab, setActiveTab] = useState<ActiveTab>("split");
  const personalizedRef = useRef<HTMLIFrameElement>(null);

  // Write modified HTML into the personalized iframe
  useEffect(() => {
    const iframe = personalizedRef.current;
    if (!iframe || !modifiedHtml) return;

    const doc = iframe.contentDocument ?? iframe.contentWindow?.document;
    if (!doc) return;

    doc.open();
    doc.write(modifiedHtml);
    doc.close();
  }, [modifiedHtml]);

  const tabs: { id: ActiveTab; label: string }[] = [
    { id: "split", label: "Split View" },
    { id: "original", label: "Original" },
    { id: "personalized", label: "Personalized" },
  ];

  return (
    <div className="rounded-2xl border border-border bg-surface overflow-hidden flex flex-col">
      {/* Tab bar */}
      <div className="flex items-center gap-1 px-4 py-3 border-b border-border bg-surface-raised">
        <div className="flex gap-1 bg-surface rounded-xl p-1">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`
                px-4 py-1.5 rounded-lg text-xs font-medium font-body transition-all duration-200
                ${activeTab === tab.id
                  ? "bg-accent text-ink shadow-sm"
                  : "text-ash hover:text-ash-light"
                }
              `}
            >
              {tab.label}
            </button>
          ))}
        </div>

        <div className="ml-auto flex items-center gap-2">
          {/* Live indicator */}
          <div className="flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-accent animate-pulse_slow" />
            <span className="text-xs text-ash">Live preview</span>
          </div>

          {/* Open in new tab */}
          <a
            href={`${process.env.NEXT_PUBLIC_API_URL}/api/preview`}
            target="_blank"
            rel="noopener noreferrer"
            className="text-xs text-ash hover:text-accent transition-colors border border-border rounded-lg px-2.5 py-1.5 hover:border-accent/30"
          >
            Open ↗
          </a>
        </div>
      </div>

      {/* Iframe area */}
      <div
        className={`
          flex gap-0.5 bg-surface-overlay
          ${activeTab === "split" ? "flex-row" : "flex-col"}
        `}
        style={{ height: "640px" }}
      >
        {/* Original */}
        {(activeTab === "split" || activeTab === "original") && (
          <div className={`flex flex-col ${activeTab === "split" ? "w-1/2" : "flex-1"}`}>
            <div className="px-3 py-2 bg-surface border-b border-border flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-red-500/70" />
              <span className="text-xs text-ash font-body">Original Page</span>
            </div>
            <iframe
              src={originalUrl}
              title="Original landing page"
              className="flex-1 w-full border-none bg-white"
              sandbox="allow-scripts allow-same-origin"
            />
          </div>
        )}

        {/* Divider in split mode */}
        {activeTab === "split" && (
          <div className="w-px bg-border-strong flex-shrink-0" />
        )}

        {/* Personalized */}
        {(activeTab === "split" || activeTab === "personalized") && (
          <div className={`flex flex-col ${activeTab === "split" ? "w-1/2" : "flex-1"}`}>
            <div className="px-3 py-2 bg-surface border-b border-border flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-accent" />
              <span className="text-xs text-accent font-body">Personalized Page</span>
            </div>
            <iframe
              ref={personalizedRef}
              title="Personalized landing page"
              className="flex-1 w-full border-none bg-white"
              sandbox="allow-scripts allow-same-origin"
            />
          </div>
        )}
      </div>
    </div>
  );
}