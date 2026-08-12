"use client";

import { StreakBadge } from "@/components/stats/streak-badge";
import { StatsSummaryGrid } from "@/components/stats/stats-summary-grid";
import { RangeControls } from "@/components/stats/range-controls";
import { SessionsChart } from "@/components/stats/sessions-chart";
import { SessionsHistoryTable } from "@/components/stats/sessions-history-table";
import { useStatsPageController } from "@/controllers/stats/use-stats-page-controller";

export function StatsView() {
  const controller = useStatsPageController();

  return (
    <div className="flex flex-col gap-8">
      <div className="flex items-center justify-between">
        <h1 className="font-display text-2xl text-foreground">Your progress</h1>
        {controller.stats && <StreakBadge streak={controller.stats.streak} />}
      </div>

      {controller.isStatsLoading ? (
        <div className="h-24 animate-pulse rounded-xl bg-muted" />
      ) : (
        controller.stats && <StatsSummaryGrid stats={controller.stats} />
      )}

      <div className="flex flex-col gap-4">
        <RangeControls
          range={controller.range}
          onRangeChange={controller.setRange}
          groupBy={controller.groupBy}
          onGroupByChange={controller.setGroupBy}
        />
        {controller.isHistoryLoading ? (
          <div className="h-64 animate-pulse rounded-xl bg-muted" />
        ) : (
          <SessionsChart data={controller.history} />
        )}
      </div>

      <div className="flex flex-col gap-3">
        <h2 className="font-display text-lg text-foreground">Recent sessions</h2>
        {controller.isSessionsLoading ? (
          <div className="h-32 animate-pulse rounded-xl bg-muted" />
        ) : (
          <SessionsHistoryTable sessions={controller.recentSessions} />
        )}
      </div>
    </div>
  );
}
