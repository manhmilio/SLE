import type { components } from "@repo/types";
import { apiClient } from "@/lib/api-client";

export type StatsOverview = components["schemas"]["StatsOverviewResponse"];
export type SessionHistoryResponse = components["schemas"]["SessionHistoryResponse"];
export type SessionHistoryItem = components["schemas"]["SessionHistoryItem"];
export type SetStatsResponse = components["schemas"]["SetStatsResponse"];

export interface GetSessionsHistoryParams {
  range?: "7d" | "30d" | "90d";
  group_by?: "day" | "week";
}

export async function getStatsOverview(): Promise<StatsOverview> {
  const { data } = await apiClient.get<StatsOverview>("/stats/overview");
  return data;
}

export async function getSessionsHistory(
  params?: GetSessionsHistoryParams
): Promise<SessionHistoryResponse> {
  const { data } = await apiClient.get<SessionHistoryResponse>("/stats/sessions", { params });
  return data;
}

export async function getSetStats(setId: string): Promise<SetStatsResponse> {
  const { data } = await apiClient.get<SetStatsResponse>(`/sets/${setId}/stats`);
  return data;
}
