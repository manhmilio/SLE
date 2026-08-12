"use client";

import { useQuery } from "@tanstack/react-query";
import { getSystemConfig } from "@/lib/api/admin.api";

export function useSystemConfigQuery() {
  return useQuery({
    queryKey: ["admin", "config"],
    queryFn: getSystemConfig,
  });
}
