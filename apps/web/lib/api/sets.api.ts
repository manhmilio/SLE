import type { components } from "@repo/types";
import { apiClient } from "@/lib/api-client";

export type StudySet = components["schemas"]["StudySetResponse"];
export type StudySetCreate = components["schemas"]["StudySetCreate"];
export type StudySetUpdate = components["schemas"]["StudySetUpdate"];

export interface ListSetsParams {
  search?: string;
  folder_id?: string;
}

export async function listSets(params?: ListSetsParams): Promise<StudySet[]> {
  const { data } = await apiClient.get<StudySet[]>("/sets", { params });
  return data;
}

export async function createSet(body: StudySetCreate): Promise<StudySet> {
  const { data } = await apiClient.post<StudySet>("/sets", body);
  return data;
}

export async function getSet(setId: string): Promise<StudySet> {
  const { data } = await apiClient.get<StudySet>(`/sets/${setId}`);
  return data;
}

export async function updateSet(setId: string, body: StudySetUpdate): Promise<StudySet> {
  const { data } = await apiClient.patch<StudySet>(`/sets/${setId}`, body);
  return data;
}

export async function deleteSet(setId: string): Promise<void> {
  await apiClient.delete(`/sets/${setId}`);
}

export async function cloneSet(setId: string): Promise<StudySet> {
  const { data } = await apiClient.post<StudySet>(`/sets/${setId}/clone`);
  return data;
}
