"use client";

import { useQuery } from "@tanstack/react-query";
import { getSetStats } from "@/lib/api/stats.api";

export function useSetStatsQuery(setId: string) {
  return useQuery({
    queryKey: ["sets", setId, "stats"],
    queryFn: () => getSetStats(setId),
    enabled: Boolean(setId),
  });
}
