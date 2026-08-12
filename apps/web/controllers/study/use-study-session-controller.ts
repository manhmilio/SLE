"use client";

import { useCallback, useRef, useState } from "react";
import { toast } from "sonner";
import {
  useCreateSessionMutation,
  useSubmitAnswerMutation,
  useEndSessionMutation,
} from "@/lib/mutations/session-mutations";
import { extractApiErrorMessage } from "@/lib/api/errors";
import type { CardInSession, SessionEndResponse, StudyMode } from "@/lib/api/sessions.api";

interface SubmitAnswerInput {
  cardId: string;
  isCorrect: boolean;
  quality?: number;
  userAnswer?: string;
}

/**
 * Mode-agnostic session lifecycle: start -> submit answers per card -> end.
 * How cards are sequenced (one at a time vs. a match board) is a concern for
 * the mode-specific controllers built on top of this one.
 */
export function useStudySessionController(setId: string, mode: StudyMode) {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [cards, setCards] = useState<CardInSession[]>([]);
  const [answeredCount, setAnsweredCount] = useState(0);
  const [correctCount, setCorrectCount] = useState(0);
  const [summary, setSummary] = useState<SessionEndResponse | null>(null);
  const cardShownAt = useRef<number>(Date.now());

  const createSession = useCreateSessionMutation();
  const submitAnswerMutation = useSubmitAnswerMutation();
  const endSessionMutation = useEndSessionMutation();

  const start = useCallback(() => {
    createSession.mutate(
      { set_id: setId, mode },
      {
        onSuccess: (response) => {
          setSessionId(response.id);
          setCards(response.cards);
          cardShownAt.current = Date.now();
        },
        onError: (error) => toast.error(extractApiErrorMessage(error, "Couldn't start this session.")),
      }
    );
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [setId, mode]);

  function markCardShown() {
    cardShownAt.current = Date.now();
  }

  function submitAnswer(input: SubmitAnswerInput, onDone?: () => void) {
    if (!sessionId) return;
    const timeSpent = Date.now() - cardShownAt.current;
    submitAnswerMutation.mutate(
      {
        sessionId,
        body: {
          card_id: input.cardId,
          is_correct: input.isCorrect,
          quality: input.quality,
          user_answer: input.userAnswer,
          time_spent: timeSpent,
        },
      },
      {
        onSuccess: () => {
          setAnsweredCount((n) => n + 1);
          if (input.isCorrect) setCorrectCount((n) => n + 1);
          onDone?.();
        },
        onError: (error) => toast.error(extractApiErrorMessage(error, "Couldn't save that answer.")),
      }
    );
  }

  function finish() {
    if (!sessionId) return;
    endSessionMutation.mutate(sessionId, {
      onSuccess: (response) => setSummary(response),
      onError: (error) => toast.error(extractApiErrorMessage(error, "Couldn't end the session.")),
    });
  }

  return {
    sessionId,
    cards,
    hasStarted: sessionId !== null,
    isStarting: createSession.isPending,
    start,
    markCardShown,
    submitAnswer,
    isSubmitting: submitAnswerMutation.isPending,
    finish,
    isFinishing: endSessionMutation.isPending,
    summary,
    answeredCount,
    correctCount,
  };
}
