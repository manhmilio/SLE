"use client";

import { useQuery } from "@tanstack/react-query";
import { listSets, type ListSetsParams } from "@/lib/api/sets.api";

export function useSetsQuery(params?: ListSetsParams) {
  return useQuery({
    queryKey: ["sets", params ?? {}],
    queryFn: () => listSets(params),
  });
}
