import { cn } from "@/lib/utils";

const RANGES = [
  { value: "7d", label: "7 days" },
  { value: "30d", label: "30 days" },
  { value: "90d", label: "90 days" },
] as const;

const GROUP_BYS = [
  { value: "day", label: "Day" },
  { value: "week", label: "Week" },
] as const;

interface RangeControlsProps {
  range: string;
  onRangeChange: (range: (typeof RANGES)[number]["value"]) => void;
  groupBy: string;
  onGroupByChange: (groupBy: (typeof GROUP_BYS)[number]["value"]) => void;
}

function Pill({
  active,
  onClick,
  children,
}: {
  active: boolean;
  onClick: () => void;
  children: React.ReactNode;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        "rounded-full border px-3 py-1 text-xs font-medium transition-colors",
        active
          ? "border-primary bg-primary text-primary-foreground"
          : "border-border text-muted-foreground hover:bg-accent"
      )}
    >
      {children}
    </button>
  );
}

export function RangeControls({ range, onRangeChange, groupBy, onGroupByChange }: RangeControlsProps) {
  return (
    <div className="flex flex-wrap items-center gap-3">
      <div className="flex gap-1.5">
        {RANGES.map((r) => (
          <Pill key={r.value} active={range === r.value} onClick={() => onRangeChange(r.value)}>
            {r.label}
          </Pill>
        ))}
      </div>
      <div className="flex gap-1.5">
        {GROUP_BYS.map((g) => (
          <Pill key={g.value} active={groupBy === g.value} onClick={() => onGroupByChange(g.value)}>
            {g.label}
          </Pill>
        ))}
      </div>
    </div>
  );
}
