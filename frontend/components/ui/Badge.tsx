interface BadgeProps {
  label: string;
  color?: string;
}

const colorMap: Record<string, string> = {
  accent: "bg-accent/10 text-accent border-accent/20",
  blue: "bg-blue-500/10 text-blue-300 border-blue-500/20",
  purple: "bg-purple-500/10 text-purple-300 border-purple-500/20",
  green: "bg-emerald-500/10 text-emerald-300 border-emerald-500/20",
  orange: "bg-orange-500/10 text-orange-300 border-orange-500/20",
  teal: "bg-teal-500/10 text-teal-300 border-teal-500/20",
  gray: "bg-white/5 text-ash-light border-border",
};

export function Badge({ label, color = "gray" }: BadgeProps) {
  const cls = colorMap[color] ?? colorMap.gray;
  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-md text-xs font-medium border font-body ${cls}`}
    >
      {label}
    </span>
  );
}