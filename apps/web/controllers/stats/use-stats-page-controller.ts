"use client";

import { useState } from "react";
import { useStatsOverviewQuery } from "@/lib/queries/use-stats-overview-query";
import { useSessionsHistoryQuery } from "@/lib/queries/use-sessions-history-query";
import { useSessionsQuery } from "@/lib/queries/use-sessions-query";
import type { GetSessionsHistoryParams } from "@/lib/api/stats.api";

type Range = NonNullable<GetSessionsHistoryParams["range"]>;
type GroupBy = NonNullable<GetSessionsHistoryParams["group_by"]>;

export function useStatsPageController() {
  const [range, setRange] = useState<Range>("30d");
  const [groupBy, setGroupBy] = useState<GroupBy>("day");

  const overviewQuery = useStatsOverviewQuery();
  const historyQuery = useSessionsHistoryQuery({ range, group_by: groupBy });
  const sessionsQuery = useSessionsQuery({ page: 1, limit: 10 });

  return {
    stats: overviewQuery.data,
    isStatsLoading: overviewQuery.isLoading,
    range,
    setRange,
    groupBy,
    setGroupBy,
    history: historyQuery.data?.data ?? [],
    isHistoryLoading: historyQuery.isLoading,
    recentSessions: sessionsQuery.data?.items ?? [],
    isSessionsLoading: sessionsQuery.isLoading,
  };
}
