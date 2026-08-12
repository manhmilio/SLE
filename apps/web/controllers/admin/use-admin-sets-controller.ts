"use client";

import { useState } from "react";
import { toast } from "sonner";
import { useAdminSetsQuery } from "@/lib/queries/use-admin-sets-query";
import { useUpdateAdminSetMutation, useDeleteAdminSetMutation } from "@/lib/mutations/admin-mutations";
import { extractApiErrorMessage } from "@/lib/api/errors";
import type { AdminSetListItem } from "@/lib/api/admin.api";

const PAGE_LIMIT = 20;

export function useAdminSetsController() {
  const [visibilityFilter, setVisibilityFilterState] = useState("");
  const [page, setPage] = useState(1);

  const query = useAdminSetsQuery({
    is_public: visibilityFilter === "" ? undefined : visibilityFilter === "public",
    page,
    limit: PAGE_LIMIT,
  });

  const updateMutation = useUpdateAdminSetMutation();
  const deleteMutation = useDeleteAdminSetMutation();

  function setVisibilityFilter(value: string) {
    setVisibilityFilterState(value);
    setPage(1);
  }

  function toggleVisibility(set: AdminSetListItem) {
    const next = !set.is_public;
    updateMutation.mutate(
      { setId: set.id, body: { is_public: next } },
      {
        onSuccess: () => toast.success(next ? "Set made public." : "Set made private."),
        onError: (error) => toast.error(extractApiErrorMessage(error, "Couldn't update this set.")),
      }
    );
  }

  function remove(set: AdminSetListItem) {
    if (!window.confirm(`Permanently delete "${set.title}"? This deletes all its cards.`)) return;
    deleteMutation.mutate(set.id, {
      onSuccess: () => toast.success("Set deleted."),
      onError: (error) => toast.error(extractApiErrorMessage(error, "Couldn't delete this set.")),
    });
  }

  return {
    sets: query.data?.items ?? [],
    total: query.data?.total ?? 0,
    isLoading: query.isLoading,
    visibilityFilter,
    setVisibilityFilter,
    page,
    setPage,
    limit: PAGE_LIMIT,
    toggleVisibility,
    remove,
  };
}
