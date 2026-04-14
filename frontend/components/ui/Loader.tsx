"use client";

import type { PersonalizeStatus } from "@/types";
import { getStatusLabel, getStatusStep } from "@/lib/utils";

const STEPS = [
  { label: "Analyze Ad", icon: "◈" },
  { label: "Read Page", icon: "◎" },
  { label: "Personalize", icon: "◆" },
];

interface LoaderProps {
  status: PersonalizeStatus;
}

export function Loader({ status }: LoaderProps) {
  const currentStep = getStatusStep(status);
  const label = getStatusLabel(status);

  return (
    <div className="flex flex-col items-center gap-8 py-12 animate-fade-in">
      {/* Steps */}
      <div className="flex items-center gap-0">
        {STEPS.map((step, i) => {
          const done = i < currentStep;
          const active = i === currentStep;
          return (
            <div key={step.label} className="flex items-center">
              {/* Node */}
              <div className="flex flex-col items-center gap-2">
                <div
                  className={`
                    w-10 h-10 rounded-full flex items-center justify-center text-sm
                    border transition-all duration-500
                    ${done ? "bg-accent border-accent text-ink" : ""}
                    ${active ? "border-accent text-accent shadow-[0_0_20px_rgba(232,255,71,0.4)] animate-pulse_slow" : ""}
                    ${!done && !active ? "border-border text-ash-dark" : ""}
                  `}
                >
                  {done ? (
                    <svg className="w-4 h-4" viewBox="0 0 16 16" fill="none">
                      <path d="M3 8l3.5 3.5L13 5" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                  ) : (
                    <span>{step.icon}</span>
                  )}
                </div>
                <span className={`text-xs tracking-wide ${active ? "text-accent" : done ? "text-ash-light" : "text-ash-dark"}`}>
                  {step.label}
                </span>
              </div>

              {/* Connector */}
              {i < STEPS.length - 1 && (
                <div className={`w-16 h-px mx-1 mb-5 transition-all duration-700 ${i < currentStep ? "bg-accent" : "bg-border"}`} />
              )}
            </div>
          );
        })}
      </div>

      {/* Status label */}
      <div className="flex flex-col items-center gap-3">
        <div className="flex gap-1">
          {[0, 1, 2].map((i) => (
            <span
              key={i}
              className="w-1.5 h-1.5 rounded-full bg-accent animate-bounce"
              style={{ animationDelay: `${i * 0.15}s` }}
            />
          ))}
        </div>
        <p className="text-sm text-ash-light font-body">{label}</p>
      </div>
    </div>
  );
}