import type { Metadata } from "next";
import { TestQuestion } from "@/components/study/test-question";

export const metadata: Metadata = { title: "Test — Soulee" };

export default async function TestStudyPage({
  params,
}: {
  params: Promise<{ setId: string }>;
}) {
  const { setId } = await params;
  return <TestQuestion setId={setId} />;
}
