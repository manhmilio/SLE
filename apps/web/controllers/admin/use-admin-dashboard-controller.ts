"use client";

import { useState } from "react";
import { useAdminDashboardQuery } from "@/lib/queries/use-admin-dashboard-query";

type Range = "7d" | "30d" | "90d";

export function useAdminDashboardController() {
  const [range, setRange] = useState<Range>("30d");
  const query = useAdminDashboardQuery(range);

  return {
    dashboard: query.data,
    isLoading: query.isLoading,
    range,
    setRange,
  };
}
