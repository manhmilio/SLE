"use client";

import { useQuery } from "@tanstack/react-query";
import { getStatsOverview } from "@/lib/api/stats.api";

export function useStatsOverviewQuery() {
  return useQuery({
    queryKey: ["stats", "overview"],
    queryFn: getStatsOverview,
  });
}
