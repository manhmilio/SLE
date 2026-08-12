import type { Metadata } from "next";
import { SetDetailView } from "@/components/sets/set-detail-view";

export const metadata: Metadata = { title: "Set — Soulee" };

export default async function SetDetailPage({
  params,
}: {
  params: Promise<{ setId: string }>;
}) {
  const { setId } = await params;
  return <SetDetailView setId={setId} />;
}
