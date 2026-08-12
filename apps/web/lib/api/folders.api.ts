import type { components } from "@repo/types";
import { apiClient } from "@/lib/api-client";

export type Folder = components["schemas"]["FolderResponse"];
export type FolderCreate = components["schemas"]["FolderCreate"];
export type FolderUpdate = components["schemas"]["FolderUpdate"];

export async function listFolders(): Promise<Folder[]> {
  const { data } = await apiClient.get<Folder[]>("/folders");
  return data;
}

export async function createFolder(body: FolderCreate): Promise<Folder> {
  const { data } = await apiClient.post<Folder>("/folders", body);
  return data;
}

export async function getFolder(folderId: string): Promise<Folder> {
  const { data } = await apiClient.get<Folder>(`/folders/${folderId}`);
  return data;
}

export async function updateFolder(folderId: string, body: FolderUpdate): Promise<Folder> {
  const { data } = await apiClient.patch<Folder>(`/folders/${folderId}`, body);
  return data;
}

export async function deleteFolder(folderId: string): Promise<void> {
  await apiClient.delete(`/folders/${folderId}`);
}
