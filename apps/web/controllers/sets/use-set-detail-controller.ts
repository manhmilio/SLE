"use client";

import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { useSetQuery } from "@/lib/queries/use-set-query";
import { useDeleteSetMutation } from "@/lib/mutations/set-mutations";
import { extractApiErrorMessage } from "@/lib/api/errors";

export function useSetDetailController(setId: string) {
  const router = useRouter();
  const setQuery = useSetQuery(setId);
  const deleteMutation = useDeleteSetMutation();

  function remove() {
    const set = setQuery.data;
    if (!set) return;
    if (!window.confirm(`Delete "${set.title}"? This also deletes its cards.`)) return;
    deleteMutation.mutate(set.id, {
      onSuccess: () => {
        toast.success("Set deleted.");
        router.push("/sets");
      },
      onError: (error) => toast.error(extractApiErrorMessage(error, "Couldn't delete the set.")),
    });
  }

  return {
    set: setQuery.data,
    isLoading: setQuery.isLoading,
    remove,
  };
}
