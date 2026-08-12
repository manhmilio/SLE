"use client";

import { useSetStatsQuery } from "@/lib/queries/use-set-stats-query";

export function useSetStatsController(setId: string) {
  const query = useSetStatsQuery(setId);

  return {
    stats: query.data,
    isLoading: query.isLoading,
  };
}
