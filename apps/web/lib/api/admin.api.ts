import type { components } from "@repo/types";
import { apiClient } from "@/lib/api-client";

export type AdminDashboard = components["schemas"]["DashboardResponse"];
export type ChartPoint = components["schemas"]["ChartPoint"];
export type AdminUserListItem = components["schemas"]["AdminUserListItem"];
export type AdminUserListResponse = components["schemas"]["AdminUserListResponse"];
export type AdminUserUpdateRequest = components["schemas"]["AdminUserUpdateRequest"];
export type AdminUserUpdateResponse = components["schemas"]["AdminUserUpdateResponse"];
export type AdminSetListItem = components["schemas"]["AdminSetListItem"];
export type AdminSetListResponse = components["schemas"]["AdminSetListResponse"];
export type AdminSetUpdateRequest = components["schemas"]["AdminSetUpdateRequest"];
export type AdminSetUpdateResponse = components["schemas"]["AdminSetUpdateResponse"];
export type SystemConfig = components["schemas"]["SystemConfigResponse"];
export type SystemConfigUpdateRequest = components["schemas"]["SystemConfigUpdateRequest"];

export interface AdminListUsersParams {
  search?: string;
  role?: string;
  is_active?: boolean;
  page?: number;
  limit?: number;
}

export interface AdminListSetsParams {
  is_public?: boolean;
  page?: number;
  limit?: number;
}

export async function getAdminDashboard(range?: string): Promise<AdminDashboard> {
  const { data } = await apiClient.get<AdminDashboard>("/admin/dashboard", { params: { range } });
  return data;
}

export async function listAdminUsers(params?: AdminListUsersParams): Promise<AdminUserListResponse> {
  const { data } = await apiClient.get<AdminUserListResponse>("/admin/users", { params });
  return data;
}

export async function updateAdminUser(
  userId: string,
  body: AdminUserUpdateRequest
): Promise<AdminUserUpdateResponse> {
  const { data } = await apiClient.patch<AdminUserUpdateResponse>(`/admin/users/${userId}`, body);
  return data;
}

export async function deleteAdminUser(userId: string): Promise<void> {
  await apiClient.delete(`/admin/users/${userId}`);
}

export async function listAdminSets(params?: AdminListSetsParams): Promise<AdminSetListResponse> {
  const { data } = await apiClient.get<AdminSetListResponse>("/admin/sets", { params });
  return data;
}

export async function updateAdminSet(
  setId: string,
  body: AdminSetUpdateRequest
): Promise<AdminSetUpdateResponse> {
  const { data } = await apiClient.patch<AdminSetUpdateResponse>(`/admin/sets/${setId}`, body);
  return data;
}

export async function deleteAdminSet(setId: string): Promise<void> {
  await apiClient.delete(`/admin/sets/${setId}`);
}

export async function getSystemConfig(): Promise<SystemConfig> {
  const { data } = await apiClient.get<SystemConfig>("/admin/config");
  return data;
}

export async function updateSystemConfig(body: SystemConfigUpdateRequest): Promise<SystemConfig> {
  const { data } = await apiClient.patch<SystemConfig>("/admin/config", body);
  return data;
}
