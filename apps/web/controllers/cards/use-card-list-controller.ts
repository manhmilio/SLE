"use client";

import { toast } from "sonner";
import { useCardsQuery } from "@/lib/queries/use-cards-query";
import { useDeleteCardMutation, useReorderCardMutation } from "@/lib/mutations/card-mutations";
import { extractApiErrorMessage } from "@/lib/api/errors";
import type { Card, CardReorderRequest } from "@/lib/api/cards.api";

/** Fetches up to this many cards at once — fine for MVP, revisit if sets regularly exceed it. */
const CARDS_PAGE_SIZE = 200;

export function useCardListController(setId: string) {
  const cardsQuery = useCardsQuery(setId, { page: 1, page_size: CARDS_PAGE_SIZE });
  const deleteMutation = useDeleteCardMutation(setId);
  const reorderMutation = useReorderCardMutation(setId);

  function remove(card: Card) {
    if (!window.confirm("Delete this card?")) return;
    deleteMutation.mutate(card.id, {
      onError: (error) => toast.error(extractApiErrorMessage(error, "Couldn't delete the card.")),
    });
  }

  function reorder(cardId: string, body: CardReorderRequest) {
    reorderMutation.mutate(
      { cardId, body },
      { onError: (error) => toast.error(extractApiErrorMessage(error, "Couldn't reorder that card.")) }
    );
  }

  return {
    cards: cardsQuery.data?.items ?? [],
    total: cardsQuery.data?.total ?? 0,
    isLoading: cardsQuery.isLoading,
    remove,
    reorder,
  };
}
