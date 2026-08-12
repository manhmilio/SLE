import { z } from "zod";

export const cardSchema = z.object({
  front: z.string().trim().min(1, "Front text is required").max(2000, "Keep it under 2000 characters"),
  back: z.string().trim().max(2000, "Keep it under 2000 characters").optional(),
});

export type CardFormValues = z.infer<typeof cardSchema>;
