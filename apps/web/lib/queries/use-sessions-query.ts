"use client";

import { useQuery } from "@tanstack/react-query";
import { listSessions, type ListSessionsParams } from "@/lib/api/sessions.api";

export function useSessionsQuery(params?: ListSessionsParams) {
  return useQuery({
    queryKey: ["sessions", params ?? {}],
    queryFn: () => listSessions(params),
  });
}
