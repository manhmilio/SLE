"use client";

import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { useFolderQuery } from "@/lib/queries/use-folder-query";
import { useDeleteFolderMutation } from "@/lib/mutations/folder-mutations";
import { extractApiErrorMessage } from "@/lib/api/errors";

export function useFolderDetailController(folderId: string) {
  const router = useRouter();
  const folderQuery = useFolderQuery(folderId);
  const deleteMutation = useDeleteFolderMutation();

  function remove() {
    const folder = folderQuery.data;
    if (!folder) return;
    if (!window.confirm(`Delete "${folder.name}"? Sets inside will not be deleted.`)) return;
    deleteMutation.mutate(folder.id, {
      onSuccess: () => {
        toast.success("Folder deleted.");
        router.push("/folders");
      },
      onError: (error) => toast.error(extractApiErrorMessage(error, "Couldn't delete the folder.")),
    });
  }

  return {
    folder: folderQuery.data,
    isLoading: folderQuery.isLoading,
    remove,
  };
}
