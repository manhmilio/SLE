import { z } from "zod";

export const folderSchema = z.object({
  name: z.string().trim().min(1, "Name is required").max(100, "Keep it under 100 characters"),
  description: z.string().trim().max(500, "Keep it under 500 characters").optional(),
});

export type FolderFormValues = z.infer<typeof folderSchema>;
