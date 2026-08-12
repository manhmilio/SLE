"use client";

import { useQuery } from "@tanstack/react-query";
import { getFolder } from "@/lib/api/folders.api";

export function useFolderQuery(folderId: string) {
  return useQuery({
    queryKey: ["folders", folderId],
    queryFn: () => getFolder(folderId),
    enabled: Boolean(folderId),
  });
}
