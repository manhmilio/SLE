"use client";

import { useMemo, useState } from "react";
import { toast } from "sonner";
import { useSetsQuery } from "@/lib/queries/use-sets-query";
import { useDeleteSetMutation } from "@/lib/mutations/set-mutations";
import { extractApiErrorMessage } from "@/lib/api/errors";
import type { StudySet } from "@/lib/api/sets.api";

interface UseSetListControllerOptions {
  folderId?: string;
}

export function useSetListController(options: UseSetListControllerOptions = {}) {
  const { folderId } = options;
  const [search, setSearch] = useState("");
  const [activeTag, setActiveTag] = useState<string | null>(null);

  const setsQuery = useSetsQuery({
    ...(search ? { search } : {}),
    ...(folderId ? { folder_id: folderId } : {}),
  });
  const deleteMutation = useDeleteSetMutation();

  const allSets = setsQuery.data ?? [];

  const availableTags = useMemo(() => {
    const tags = new Set<string>();
    allSets.forEach((set) => set.tags.forEach((tag) => tags.add(tag)));
    return Array.from(tags).sort();
  }, [allSets]);

  const sets = useMemo(
    () => (activeTag ? allSets.filter((set) => set.tags.includes(activeTag)) : allSets),
    [allSets, activeTag]
  );

  function remove(set: StudySet) {
    if (!window.confirm(`Delete "${set.title}"? This also deletes its cards.`)) return;
    deleteMutation.mutate(set.id, {
      onSuccess: () => toast.success("Set deleted."),
      onError: (error) => toast.error(extractApiErrorMessage(error, "Couldn't delete the set.")),
    });
  }

  return {
    search,
    setSearch,
    availableTags,
    activeTag,
    setActiveTag,
    sets,
    isLoading: setsQuery.isLoading,
    remove,
  };
}
