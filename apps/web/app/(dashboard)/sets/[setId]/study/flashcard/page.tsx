import type { Metadata } from "next";
import { Flashcard } from "@/components/study/flashcard";

export const metadata: Metadata = { title: "Flashcards — Soulee" };

export default async function FlashcardStudyPage({
  params,
}: {
  params: Promise<{ setId: string }>;
}) {
  const { setId } = await params;
  return <Flashcard setId={setId} />;
}
