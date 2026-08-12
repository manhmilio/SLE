"use client";

import { useQuery } from "@tanstack/react-query";
import { getSet } from "@/lib/api/sets.api";

export function useSetQuery(setId: string) {
  return useQuery({
    queryKey: ["sets", setId],
    queryFn: () => getSet(setId),
    enabled: Boolean(setId),
  });
}
