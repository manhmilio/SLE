import type { Metadata } from "next";
import { FolderDetailView } from "@/components/folders/folder-detail-view";

export const metadata: Metadata = { title: "Folder — Soulee" };

export default async function FolderDetailPage({
  params,
}: {
  params: Promise<{ folderId: string }>;
}) {
  const { folderId } = await params;
  return <FolderDetailView folderId={folderId} />;
}
