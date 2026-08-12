import { z } from "zod";

export const setSchema = z.object({
  title: z.string().trim().min(1, "Title is required").max(200, "Keep it under 200 characters"),
  description: z.string().trim().max(1000, "Keep it under 1000 characters").optional(),
  tagsInput: z.string().optional(),
  is_public: z.boolean(),
  folder_id: z.string().uuid().nullable().optional(),
});

export type SetFormValues = z.infer<typeof setSchema>;

/** The form keeps tags as one comma-separated field; the API wants string[]. */
export function parseTagsInput(tagsInput?: string): string[] {
  if (!tagsInput) return [];
  return Array.from(
    new Set(
      tagsInput
        .split(",")
        .map((tag) => tag.trim())
        .filter(Boolean)
    )
  );
}
