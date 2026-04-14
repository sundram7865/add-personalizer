import type { ChangeItem } from "@/types";
import { Badge } from "@/components/ui/Badge";
import { principleColor } from "@/lib/utils";

interface ChangesPanelProps {
  changes: ChangeItem[];
}

export function ChangesPanel({ changes }: ChangesPanelProps) {
  if (changes.length === 0) {
    return (
      <div className="rounded-2xl border border-border bg-surface p-5 text-center">
        <p className="text-sm text-ash">No changes were logged.</p>
      </div>
    );
  }

  return (
    <div className="rounded-2xl border border-border bg-surface overflow-hidden">
      {/* Header */}
      <div className="px-5 py-4 border-b border-border flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-accent text-sm">◆</span>
          <h3 className="text-sm font-medium text-white font-body">What Changed & Why</h3>
        </div>
        <span className="text-xs text-ash bg-surface-raised border border-border px-2.5 py-1 rounded-full">
          {changes.length} {changes.length === 1 ? "change" : "changes"}
        </span>
      </div>

      {/* Change list */}
      <div className="divide-y divide-border">
        {changes.map((change, i) => (
          <div key={i} className="px-5 py-4 flex flex-col gap-3">
            {/* Element + principle */}
            <div className="flex items-center justify-between flex-wrap gap-2">
              <span className="text-xs font-medium text-white font-body">{change.element}</span>
              <Badge
                label={change.cro_principle}
                color={principleColor(change.cro_principle)}
              />
            </div>

            {/* Before → After */}
            <div className="flex flex-col gap-2">
              <div className="rounded-lg bg-surface-raised border border-border px-3 py-2">
                <p className="text-xs text-ash mb-0.5 uppercase tracking-widest">Before</p>
                <p className="text-sm text-ash-light font-body line-through opacity-60 leading-relaxed">
                  {change.original}
                </p>
              </div>
              <div className="rounded-lg bg-accent/5 border border-accent/20 px-3 py-2">
                <p className="text-xs text-accent mb-0.5 uppercase tracking-widest">After</p>
                <p className="text-sm text-white font-body leading-relaxed">{change.updated}</p>
              </div>
            </div>

            {/* Reason */}
            <p className="text-xs text-ash leading-relaxed font-body">
              <span className="text-accent/70">Reason: </span>
              {change.reason}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}