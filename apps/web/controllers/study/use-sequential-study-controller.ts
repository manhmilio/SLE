"use client";

import { useEffect, useRef, useState } from "react";
import { useStudySessionController } from "@/controllers/study/use-study-session-controller";
import type { StudyMode } from "@/lib/api/sessions.api";

/** Shared "one card at a time" flow for flashcard/learn/test — reveal, then answer, then advance. */
export function useSequentialStudyController(setId: string, mode: StudyMode) {
  const session = useStudySessionController(setId, mode);
  const [index, setIndex] = useState(0);
  const [revealed, setRevealed] = useState(false);
  const finishedRef = useRef(false);

  useEffect(() => {
    session.start();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const isEmpty = session.hasStarted && session.cards.length === 0;
  const isDone = session.hasStarted && !isEmpty && index >= session.cards.length;
  const currentCard = isEmpty || isDone ? null : session.cards[index] ?? null;

  useEffect(() => {
    if ((isEmpty || isDone) && !finishedRef.current) {
      finishedRef.current = true;
      session.finish();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isEmpty, isDone]);

  function reveal() {
    setRevealed(true);
  }

  function advance(input: { isCorrect: boolean; quality?: number; userAnswer?: string }) {
    if (!currentCard) return;
    session.submitAnswer({ cardId: currentCard.id, ...input }, () => {
      setRevealed(false);
      setIndex((i) => i + 1);
      session.markCardShown();
    });
  }

  return {
    ...session,
    currentCard,
    index,
    total: session.cards.length,
    revealed,
    reveal,
    advance,
    isEmpty,
    isDone,
  };
}
