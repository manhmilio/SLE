"use client";

import { useSequentialStudyController } from "@/controllers/study/use-sequential-study-controller";
import { StudySessionSummary } from "@/components/study/study-session-summary";
import { StudyEmptyState } from "@/components/study/study-empty-state";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

export function Flashcard({ setId }: { setId: string }) {
  const study = useSequentialStudyController(setId, "flashcard");

  if (study.isEmpty) {
    return <StudyEmptyState setId={setId} />;
  }

  if (study.isDone && study.summary) {
    return <StudySessionSummary summary={study.summary} setId={setId} />;
  }

  if (!study.currentCard) {
    return <div className="h-64 animate-pulse rounded-xl bg-muted" />;
  }

  const card = study.currentCard;

  return (
    <div className="flex flex-col items-center gap-6">
      <p className="text-sm text-muted-foreground">
        {study.index + 1} / {study.total}
      </p>
      <Card
        className="flex h-64 w-full max-w-md cursor-pointer items-center justify-center p-8 text-center"
        onClick={study.reveal}
      >
        <CardContent className="flex items-center justify-center">
          <p className="font-display text-xl text-foreground">
            {study.revealed ? card.back : card.front}
          </p>
        </CardContent>
      </Card>
      {study.revealed ? (
        <div className="flex gap-3">
          <Button variant="outline" onClick={() => study.advance({ isCorrect: false })}>
            Didn&apos;t know
          </Button>
          <Button onClick={() => study.advance({ isCorrect: true })}>Knew it</Button>
        </div>
      ) : (
        <p className="text-sm text-muted-foreground">Tap the card to reveal the answer</p>
      )}
    </div>
  );
}
