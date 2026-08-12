"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import {
  createSet,
  updateSet,
  deleteSet,
  cloneSet,
  type StudySetCreate,
  type StudySetUpdate,
} from "@/lib/api/sets.api";

export function useCreateSetMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (body: StudySetCreate) => createSet(body),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["sets"] }),
  });
}

export function useUpdateSetMutation(setId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (body: StudySetUpdate) => updateSet(setId, body),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["sets"] }),
  });
}

export function useDeleteSetMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (setId: string) => deleteSet(setId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["sets"] }),
  });
}

export function useCloneSetMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (setId: string) => cloneSet(setId),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["sets"] }),
  });
}
