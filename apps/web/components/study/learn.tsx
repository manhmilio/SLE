"use client";

import { useSequentialStudyController } from "@/controllers/study/use-sequential-study-controller";
import { StudySessionSummary } from "@/components/study/study-session-summary";
import { StudyEmptyState } from "@/components/study/study-empty-state";
import { LearnQualityPicker } from "@/components/study/learn-quality-picker";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

export function Learn({ setId }: { setId: string }) {
  const study = useSequentialStudyController(setId, "learn");

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

  function handleQuality(quality: number) {
    study.advance({ isCorrect: quality >= 3, quality });
  }

  return (
    <div className="flex flex-col items-center gap-6">
      <p className="text-sm text-muted-foreground">
        {study.index + 1} / {study.total}
      </p>
      <Card className="flex h-64 w-full max-w-md flex-col items-center justify-center gap-3 p-8 text-center">
        <CardContent className="flex flex-col items-center gap-3">
          <p className="font-display text-xl text-foreground">{card.front}</p>
          {study.revealed && <p className="text-muted-foreground">{card.back}</p>}
        </CardContent>
      </Card>
      {study.revealed ? (
        <LearnQualityPicker onSelect={handleQuality} />
      ) : (
        <Button onClick={study.reveal}>Show answer</Button>
      )}
    </div>
  );
}
