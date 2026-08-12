"use client";

import { useState } from "react";
import { toast } from "sonner";
import { useAuthStore } from "@/store/auth-store";
import { useAdminUsersQuery } from "@/lib/queries/use-admin-users-query";
import { useUpdateAdminUserMutation, useDeleteAdminUserMutation } from "@/lib/mutations/admin-mutations";
import { extractApiErrorMessage } from "@/lib/api/errors";
import type { AdminUserListItem } from "@/lib/api/admin.api";

const PAGE_LIMIT = 20;

export function useAdminUsersController() {
  const currentUserId = useAuthStore((s) => s.user?.id);
  const [search, setSearchState] = useState("");
  const [roleFilter, setRoleFilterState] = useState("");
  const [activeFilter, setActiveFilterState] = useState("");
  const [page, setPage] = useState(1);

  const query = useAdminUsersQuery({
    search: search || undefined,
    role: roleFilter || undefined,
    is_active: activeFilter === "" ? undefined : activeFilter === "active",
    page,
    limit: PAGE_LIMIT,
  });

  const updateMutation = useUpdateAdminUserMutation();
  const deleteMutation = useDeleteAdminUserMutation();

  function setSearch(value: string) {
    setSearchState(value);
    setPage(1);
  }
  function setRoleFilter(value: string) {
    setRoleFilterState(value);
    setPage(1);
  }
  function setActiveFilter(value: string) {
    setActiveFilterState(value);
    setPage(1);
  }

  function isSelf(user: AdminUserListItem) {
    return user.id === currentUserId;
  }

  function toggleActive(user: AdminUserListItem) {
    if (isSelf(user)) return;
    const willBan = user.is_active;
    if (!window.confirm(`${willBan ? "Ban" : "Unban"} ${user.email}?`)) return;
    updateMutation.mutate(
      { userId: user.id, body: { is_active: !user.is_active } },
      {
        onSuccess: () => toast.success(willBan ? "User banned." : "User unbanned."),
        onError: (error) =>
          toast.error(extractApiErrorMessage(error, `Couldn't ${willBan ? "ban" : "unban"} this user.`)),
      }
    );
  }

  function toggleRole(user: AdminUserListItem) {
    if (isSelf(user)) return;
    const nextRole = user.role === "admin" ? "user" : "admin";
    if (!window.confirm(`Make ${user.email} ${nextRole === "admin" ? "an admin" : "a regular user"}?`)) return;
    updateMutation.mutate(
      { userId: user.id, body: { role: nextRole } },
      {
        onSuccess: () => toast.success("Role updated."),
        onError: (error) => toast.error(extractApiErrorMessage(error, "Couldn't update this user's role.")),
      }
    );
  }

  function resetPassword(user: AdminUserListItem) {
    if (!window.confirm(`Reset ${user.email}'s password? They'll be signed out everywhere.`)) return;
    updateMutation.mutate(
      { userId: user.id, body: { force_reset_password: true } },
      {
        onSuccess: (response) => {
          if (response.temp_password) {
            toast.success(`Temporary password: ${response.temp_password}`, { duration: 20000 });
          } else {
            toast.success("Password reset.");
          }
        },
        onError: (error) => toast.error(extractApiErrorMessage(error, "Couldn't reset this user's password.")),
      }
    );
  }

  function remove(user: AdminUserListItem) {
    if (isSelf(user)) return;
    if (!window.confirm(`Permanently delete ${user.email}? This deletes all their data.`)) return;
    deleteMutation.mutate(user.id, {
      onSuccess: () => toast.success("User deleted."),
      onError: (error) => toast.error(extractApiErrorMessage(error, "Couldn't delete this user.")),
    });
  }

  return {
    users: query.data?.items ?? [],
    total: query.data?.total ?? 0,
    isLoading: query.isLoading,
    search,
    setSearch,
    roleFilter,
    setRoleFilter,
    activeFilter,
    setActiveFilter,
    page,
    setPage,
    limit: PAGE_LIMIT,
    isSelf,
    toggleActive,
    toggleRole,
    resetPassword,
    remove,
  };
}
