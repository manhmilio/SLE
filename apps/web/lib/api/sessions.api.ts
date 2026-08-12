import type { components } from "@repo/types";
import { apiClient } from "@/lib/api-client";

export type StudyMode = components["schemas"]["StudyMode"];
export type CardInSession = components["schemas"]["CardInSession"];
export type SessionCreate = components["schemas"]["SessionCreate"];
export type SessionCreateResponse = components["schemas"]["SessionCreateResponse"];
export type AnswerSubmit = components["schemas"]["AnswerSubmit"];
export type AnswerResponse = components["schemas"]["AnswerResponse"];
export type SessionEndResponse = components["schemas"]["SessionEndResponse"];

export async function createSession(body: SessionCreate): Promise<SessionCreateResponse> {
  const { data } = await apiClient.post<SessionCreateResponse>("/sessions", body);
  return data;
}

export async function submitAnswer(sessionId: string, body: AnswerSubmit): Promise<AnswerResponse> {
  const { data } = await apiClient.post<AnswerResponse>(`/sessions/${sessionId}/answers`, body);
  return data;
}

export async function endSession(sessionId: string): Promise<SessionEndResponse> {
  const { data } = await apiClient.post<SessionEndResponse>(`/sessions/${sessionId}/end`);
  return data;
}
