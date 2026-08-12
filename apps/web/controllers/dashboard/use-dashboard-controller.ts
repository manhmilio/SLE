"use client";

import { useAuthStore } from "@/store/auth-store";
import { useStatsOverviewQuery } from "@/lib/queries/use-stats-overview-query";
import { useSetsQuery } from "@/lib/queries/use-sets-query";

const RECENT_SETS_LIMIT = 6;

export function useDashboardController() {
  const displayName = useAuthStore((s) => s.user?.display_name) ?? "there";
  const statsQuery = useStatsOverviewQuery();
  const setsQuery = useSetsQuery();

  const recentSets = [...(setsQuery.data ?? [])]
    .sort((a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime())
    .slice(0, RECENT_SETS_LIMIT);

  return {
    displayName,
    stats: statsQuery.data,
    isStatsLoading: statsQuery.isLoading,
    recentSets,
    isSetsLoading: setsQuery.isLoading,
  };
}
