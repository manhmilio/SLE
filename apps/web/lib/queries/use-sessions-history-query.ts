"use client";

import { useQuery } from "@tanstack/react-query";
import { getSessionsHistory, type GetSessionsHistoryParams } from "@/lib/api/stats.api";

export function useSessionsHistoryQuery(params: GetSessionsHistoryParams) {
  return useQuery({
    queryKey: ["stats", "sessions", params],
    queryFn: () => getSessionsHistory(params),
  });
}
