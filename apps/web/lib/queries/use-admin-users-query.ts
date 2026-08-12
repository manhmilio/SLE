"use client";

import { useQuery } from "@tanstack/react-query";
import { listAdminUsers, type AdminListUsersParams } from "@/lib/api/admin.api";

export function useAdminUsersQuery(params: AdminListUsersParams) {
  return useQuery({
    queryKey: ["admin", "users", params],
    queryFn: () => listAdminUsers(params),
  });
}
