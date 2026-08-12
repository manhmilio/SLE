"use client";

import { useQuery } from "@tanstack/react-query";
import { listFolders } from "@/lib/api/folders.api";

export function useFoldersQuery() {
  return useQuery({
    queryKey: ["folders"],
    queryFn: listFolders,
  });
}
