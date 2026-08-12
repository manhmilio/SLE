import { CheckCircle2, Sprout, BookOpen, Clock } from "lucide-react";
import type { LucideIcon } from "lucide-react";
import { formatDuration } from "@/lib/utils";
import type { StatsOverview } from "@/lib/api/stats.api";

function StatTile({
  label,
  value,
  icon: Icon,
}: {
  label: string;
  value: string | number;
  icon: LucideIcon;
}) {
  return (
    <div className="flex flex-col gap-1 rounded-xl border border-border bg-card p-4">
      <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
        <Icon className="size-3.5" />
        {label}
      </div>
      <span className="font-display text-2xl text-foreground">{value}</span>
    </div>
  );
}

export function StatsSummaryGrid({ stats }: { stats: StatsOverview }) {
  return (
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
      <StatTile label="Known" value={stats.total_cards_known} icon={CheckCircle2} />
      <StatTile label="Learning" value={stats.total_cards_learning} icon={Sprout} />
      <StatTile label="Sessions" value={stats.total_sessions} icon={BookOpen} />
      <StatTile label="Study time" value={formatDuration(stats.total_study_time_seconds)} icon={Clock} />
    </div>
  );
}
