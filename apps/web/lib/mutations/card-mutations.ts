"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import {
  createCard,
  updateCard,
  deleteCard,
  reorderCard,
  uploadCardImage,
  type CardCreate,
  type CardUpdate,
  type CardReorderRequest,
} from "@/lib/api/cards.api";

export function useCreateCardMutation(setId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (body: CardCreate) => createCard(setId, body),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["sets"] }),
  });
}

export function useUpdateCardMutation(setId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ cardId, body }: { cardId: string; body: CardUpdate }) => updateCard(setId, cardId, body),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["sets"] }),
  });
}

export function useDeleteCardMutation(setId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (cardId: string) => deleteCard(setId, cardId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["sets"] }),
  });
}

export function useReorderCardMutation(setId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ cardId, body }: { cardId: string; body: CardReorderRequest }) =>
      reorderCard(setId, cardId, body),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["sets"] }),
  });
}

export function useUploadCardImageMutation(setId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ cardId, file }: { cardId: string; file: File }) => uploadCardImage(setId, cardId, file),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["sets"] }),
  });
}
