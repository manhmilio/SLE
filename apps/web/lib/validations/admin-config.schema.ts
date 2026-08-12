import { z } from "zod";

export const systemConfigSchema = z
  .object({
    initial_ease_factor: z.number().min(1.3, "Must be at least 1.3"),
    min_ease_factor: z.number().min(1.3, "Must be at least 1.3"),
    known_threshold_days: z.number().int().min(1, "Must be at least 1 day"),
    max_sets_per_user: z.number().int().min(1, "Must be at least 1"),
    max_cards_per_set: z.number().int().min(1, "Must be at least 1"),
    max_image_size_mb: z.number().int().min(1, "Must be at least 1"),
    allow_registration: z.boolean(),
  })
  .refine((data) => data.min_ease_factor <= data.initial_ease_factor, {
    message: "Can't exceed the initial ease factor",
    path: ["min_ease_factor"],
  });

export type SystemConfigFormValues = z.infer<typeof systemConfigSchema>;
