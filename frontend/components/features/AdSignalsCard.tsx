import type { AdSignals } from "@/types";

interface AdSignalsCardProps {
  signals: AdSignals;
  adImageUrl: string;
}

const SIGNAL_FIELDS: { key: keyof AdSignals; label: string; icon: string }[] = [
  { key: "headline", label: "Headline", icon: "◈" },
  { key: "cta_text", label: "CTA Text", icon: "→" },
  { key: "tone", label: "Tone", icon: "◎" },
  { key: "target_audience", label: "Audience", icon: "◉" },
  { key: "value_proposition", label: "Value Prop", icon: "◆" },
  { key: "emotional_hook", label: "Hook", icon: "◇" },
  { key: "color_mood", label: "Color Mood", icon: "○" },
];

export function AdSignalsCard({ signals, adImageUrl }: AdSignalsCardProps) {
  return (
    <div className="rounded-2xl border border-border bg-surface overflow-hidden">
      {/* Header */}
      <div className="px-5 py-4 border-b border-border flex items-center gap-2">
        <span className="text-accent text-sm">◈</span>
        <h3 className="text-sm font-medium text-white font-body">Ad Signals Extracted</h3>
      </div>

      {/* Ad image preview */}
      {adImageUrl && (
        <div className="px-5 pt-4">
          <div className="rounded-xl overflow-hidden border border-border bg-surface-raised h-28 flex items-center justify-center">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={adImageUrl}
              alt="Ad creative"
              className="h-full w-full object-contain"
              onError={(e) => {
                (e.target as HTMLImageElement).style.display = "none";
              }}
            />
          </div>
        </div>
      )}

      {/* Signal list */}
      <div className="p-5 flex flex-col gap-3">
        {SIGNAL_FIELDS.map(({ key, label, icon }) => (
          <div key={key} className="flex flex-col gap-0.5">
            <div className="flex items-center gap-1.5">
              <span className="text-accent/60 text-xs">{icon}</span>
              <span className="text-xs uppercase tracking-widest text-ash font-body">{label}</span>
            </div>
            <p className="text-sm text-ash-light font-body pl-4 leading-relaxed">
              {signals[key]}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}