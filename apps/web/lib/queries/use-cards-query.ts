"use client";

import { useQuery } from "@tanstack/react-query";
import { listCards, type ListCardsParams } from "@/lib/api/cards.api";

export function useCardsQuery(setId: string, params?: ListCardsParams) {
  return useQuery({
    queryKey: ["sets", setId, "cards", params ?? {}],
    queryFn: () => listCards(setId, params),
    enabled: Boolean(setId),
  });
}
