"use client";

import { StreakBadge } from "@/components/stats/streak-badge";
import { StatsSummaryGrid } from "@/components/stats/stats-summary-grid";
import { SetGrid } from "@/components/sets/set-grid";
import { useDashboardController } from "@/controllers/dashboard/use-dashboard-controller";

export function DashboardHome() {
  const { displayName, stats, isStatsLoading, recentSets, isSetsLoading } =
    useDashboardController();

  return (
    <div className="flex flex-col gap-8">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="font-display text-2xl text-foreground">Welcome back, {displayName}</h1>
          <p className="text-muted-foreground">Here&apos;s where your English has taken root.</p>
        </div>
        {stats && <StreakBadge streak={stats.streak} />}
      </div>

      {isStatsLoading ? (
        <div className="h-24 animate-pulse rounded-xl bg-muted" />
      ) : (
        stats && <StatsSummaryGrid stats={stats} />
      )}

      <div className="flex flex-col gap-3">
        <h2 className="font-display text-lg text-foreground">Your sets</h2>
        {isSetsLoading ? (
          <div className="h-40 animate-pulse rounded-xl bg-muted" />
        ) : (
          <SetGrid sets={recentSets} />
        )}
      </div>
    </div>
  );
}
