"use client";

import { useState } from "react";
import { useSequentialStudyController } from "@/controllers/study/use-sequential-study-controller";
import { StudySessionSummary } from "@/components/study/study-session-summary";
import { StudyEmptyState } from "@/components/study/study-empty-state";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export function TestQuestion({ setId }: { setId: string }) {
  const study = useSequentialStudyController(setId, "test");
  const [answer, setAnswer] = useState("");
  const [checked, setChecked] = useState<{ isCorrect: boolean } | null>(null);

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

  function handleCheck() {
    const isCorrect = answer.trim().toLowerCase() === card.back.trim().toLowerCase();
    setChecked({ isCorrect });
  }

  function handleNext() {
    if (!checked) return;
    study.advance({ isCorrect: checked.isCorrect, userAnswer: answer });
    setAnswer("");
    setChecked(null);
  }

  return (
    <div className="flex flex-col items-center gap-6">
      <p className="text-sm text-muted-foreground">
        {study.index + 1} / {study.total}
      </p>
      <Card className="w-full max-w-md p-8 text-center">
        <CardContent className="flex flex-col items-center gap-4">
          <p className="font-display text-xl text-foreground">{card.front}</p>
          <Input
            value={answer}
            onChange={(e) => setAnswer(e.target.value)}
            placeholder="Type your answer…"
            disabled={checked !== null}
            onKeyDown={(e) => e.key === "Enter" && !checked && handleCheck()}
          />
          {checked && (
            <p className={cn("text-sm", checked.isCorrect ? "text-primary" : "text-destructive")}>
              {checked.isCorrect ? "Correct!" : `Correct answer: ${card.back}`}
            </p>
          )}
        </CardContent>
      </Card>
      {checked ? (
        <Button onClick={handleNext}>Next</Button>
      ) : (
        <Button onClick={handleCheck} disabled={!answer.trim()}>
          Check
        </Button>
      )}
    </div>
  );
}
