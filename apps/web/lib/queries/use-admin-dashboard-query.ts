"use client";

import { useQuery } from "@tanstack/react-query";
import { getAdminDashboard } from "@/lib/api/admin.api";

export function useAdminDashboardQuery(range: string) {
  return useQuery({
    queryKey: ["admin", "dashboard", range],
    queryFn: () => getAdminDashboard(range),
  });
}
