import type { components } from "@repo/types";
import { apiClient } from "@/lib/api-client";

export type StudySet = components["schemas"]["StudySetResponse"];

export interface ListSetsParams {
  search?: string;
  folder_id?: string;
}

export async function listSets(params?: ListSetsParams): Promise<StudySet[]> {
  const { data } = await apiClient.get<StudySet[]>("/sets", { params });
  return data;
}
