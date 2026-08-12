"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import {
  createFolder,
  updateFolder,
  deleteFolder,
  type FolderCreate,
  type FolderUpdate,
} from "@/lib/api/folders.api";

export function useCreateFolderMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (body: FolderCreate) => createFolder(body),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["folders"] }),
  });
}

export function useUpdateFolderMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ folderId, body }: { folderId: string; body: FolderUpdate }) =>
      updateFolder(folderId, body),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["folders"] }),
  });
}

export function useDeleteFolderMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (folderId: string) => deleteFolder(folderId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["folders"] }),
  });
}
