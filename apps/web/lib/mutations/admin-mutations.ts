"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import {
  updateAdminUser,
  deleteAdminUser,
  updateAdminSet,
  deleteAdminSet,
  updateSystemConfig,
  type AdminUserUpdateRequest,
  type AdminSetUpdateRequest,
  type SystemConfigUpdateRequest,
} from "@/lib/api/admin.api";

export function useUpdateAdminUserMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ userId, body }: { userId: string; body: AdminUserUpdateRequest }) =>
      updateAdminUser(userId, body),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["admin", "users"] }),
  });
}

export function useDeleteAdminUserMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (userId: string) => deleteAdminUser(userId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["admin", "users"] }),
  });
}

export function useUpdateAdminSetMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ setId, body }: { setId: string; body: AdminSetUpdateRequest }) =>
      updateAdminSet(setId, body),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["admin", "sets"] }),
  });
}

export function useDeleteAdminSetMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (setId: string) => deleteAdminSet(setId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["admin", "sets"] }),
  });
}

export function useUpdateSystemConfigMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (body: SystemConfigUpdateRequest) => updateSystemConfig(body),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["admin", "config"] }),
  });
}
