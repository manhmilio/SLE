import type { components } from "@repo/types";
import { apiClient } from "@/lib/api-client";

export type StatsOverview = components["schemas"]["StatsOverviewResponse"];

export async function getStatsOverview(): Promise<StatsOverview> {
  const { data } = await apiClient.get<StatsOverview>("/stats/overview");
  return data;
}
