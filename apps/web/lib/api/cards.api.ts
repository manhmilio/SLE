import type { components } from "@repo/types";
import { apiClient } from "@/lib/api-client";

export type Card = components["schemas"]["CardResponse"];
export type CardCreate = components["schemas"]["CardCreate"];
export type CardUpdate = components["schemas"]["CardUpdate"];
export type CardReorderRequest = components["schemas"]["CardReorderRequest"];
export type CardListResponse = components["schemas"]["CardListResponse"];

export interface ListCardsParams {
  page?: number;
  page_size?: number;
}

export async function listCards(setId: string, params?: ListCardsParams): Promise<CardListResponse> {
  const { data } = await apiClient.get<CardListResponse>(`/sets/${setId}/cards`, { params });
  return data;
}

export async function createCard(setId: string, body: CardCreate): Promise<Card> {
  const { data } = await apiClient.post<Card>(`/sets/${setId}/cards`, body);
  return data;
}

export async function updateCard(setId: string, cardId: string, body: CardUpdate): Promise<Card> {
  const { data } = await apiClient.patch<Card>(`/sets/${setId}/cards/${cardId}`, body);
  return data;
}

export async function deleteCard(setId: string, cardId: string): Promise<void> {
  await apiClient.delete(`/sets/${setId}/cards/${cardId}`);
}

export async function reorderCard(
  setId: string,
  cardId: string,
  body: CardReorderRequest
): Promise<Card> {
  const { data } = await apiClient.patch<Card>(`/sets/${setId}/cards/${cardId}/order`, body);
  return data;
}

export async function uploadCardImage(setId: string, cardId: string, file: File): Promise<Card> {
  const formData = new FormData();
  formData.append("file", file);
  const { data } = await apiClient.post<Card>(`/sets/${setId}/cards/${cardId}/image`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}
