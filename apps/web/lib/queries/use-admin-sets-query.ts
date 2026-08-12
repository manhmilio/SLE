"use client";

import { useQuery } from "@tanstack/react-query";
import { listAdminSets, type AdminListSetsParams } from "@/lib/api/admin.api";

export function useAdminSetsQuery(params: AdminListSetsParams) {
  return useQuery({
    queryKey: ["admin", "sets", params],
    queryFn: () => listAdminSets(params),
  });
}
