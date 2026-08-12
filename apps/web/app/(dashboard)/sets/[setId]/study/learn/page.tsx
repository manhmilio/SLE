import type { Metadata } from "next";
import { Learn } from "@/components/study/learn";

export const metadata: Metadata = { title: "Learn — Soulee" };

export default async function LearnStudyPage({
  params,
}: {
  params: Promise<{ setId: string }>;
}) {
  const { setId } = await params;
  return <Learn setId={setId} />;
}
