"use client";

import { toast } from "sonner";
import { useFoldersQuery } from "@/lib/queries/use-folders-query";
import { useDeleteFolderMutation } from "@/lib/mutations/folder-mutations";
import { extractApiErrorMessage } from "@/lib/api/errors";
import type { Folder } from "@/lib/api/folders.api";

export function useFolderListController() {
  const foldersQuery = useFoldersQuery();
  const deleteMutation = useDeleteFolderMutation();

  function remove(folder: Folder) {
    if (!window.confirm(`Delete "${folder.name}"? Sets inside will not be deleted.`)) return;
    deleteMutation.mutate(folder.id, {
      onSuccess: () => toast.success("Folder deleted."),
      onError: (error) => toast.error(extractApiErrorMessage(error, "Couldn't delete the folder.")),
    });
  }

  return {
    folders: foldersQuery.data ?? [],
    isLoading: foldersQuery.isLoading,
    remove,
  };
}
