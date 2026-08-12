import type { Metadata } from "next";
import { MatchBoard } from "@/components/study/match-board";

export const metadata: Metadata = { title: "Match — Soulee" };

export default async function MatchStudyPage({
  params,
}: {
  params: Promise<{ setId: string }>;
}) {
  const { setId } = await params;
  return <MatchBoard setId={setId} />;
}
