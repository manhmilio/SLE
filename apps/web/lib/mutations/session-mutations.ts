"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import {
  createSession,
  submitAnswer,
  endSession,
  type SessionCreate,
  type AnswerSubmit,
} from "@/lib/api/sessions.api";

export function useCreateSessionMutation() {
  return useMutation({
    mutationFn: (body: SessionCreate) => createSession(body),
  });
}

export function useSubmitAnswerMutation() {
  return useMutation({
    mutationFn: ({ sessionId, body }: { sessionId: string; body: AnswerSubmit }) =>
      submitAnswer(sessionId, body),
  });
}

export function useEndSessionMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (sessionId: string) => endSession(sessionId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["sets"] });
      queryClient.invalidateQueries({ queryKey: ["stats"] });
    },
  });
}
