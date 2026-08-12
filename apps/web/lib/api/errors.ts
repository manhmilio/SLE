import { isAxiosError } from "axios";

interface StructuredErrorDetail {
  success?: boolean;
  error?: { code?: string; message?: string };
}

/**
 * Backend error body is either `{ detail: "message" }` or the more structured
 * `{ detail: { success: false, error: { code, message } } }` (see auth endpoints).
 */
export function extractApiErrorMessage(
  error: unknown,
  fallback = "Something went wrong. Please try again."
): string {
  if (!isAxiosError(error)) return fallback;

  const detail = error.response?.data?.detail as string | StructuredErrorDetail | undefined;
  if (typeof detail === "string") return detail;
  if (detail?.error?.message) return detail.error.message;
  return fallback;
}
