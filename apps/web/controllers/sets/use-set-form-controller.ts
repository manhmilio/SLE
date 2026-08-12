"use client";

import { useState } from "react";
import { toast } from "sonner";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { setSchema, type SetFormValues, parseTagsInput } from "@/lib/validations/set.schema";
import { useCreateSetMutation, useUpdateSetMutation } from "@/lib/mutations/set-mutations";
import { extractApiErrorMessage } from "@/lib/api/errors";
import type { StudySet } from "@/lib/api/sets.api";

interface UseSetFormControllerOptions {
  defaultFolderId?: string | null;
  onCreated?: (set: StudySet) => void;
}

export function useSetFormController(options: UseSetFormControllerOptions = {}) {
  const { defaultFolderId = null, onCreated } = options;
  const [dialogState, setDialogState] = useState<{ open: boolean; editing: StudySet | null }>({
    open: false,
    editing: null,
  });

  const form = useForm<SetFormValues>({
    resolver: zodResolver(setSchema),
    defaultValues: {
      title: "",
      description: "",
      tagsInput: "",
      is_public: false,
      folder_id: defaultFolderId,
    },
  });

  const createMutation = useCreateSetMutation();
  const updateMutation = useUpdateSetMutation(dialogState.editing?.id ?? "");

  function openCreate() {
    form.reset({
      title: "",
      description: "",
      tagsInput: "",
      is_public: false,
      folder_id: defaultFolderId,
    });
    setDialogState({ open: true, editing: null });
  }

  function openEdit(set: StudySet) {
    form.reset({
      title: set.title,
      description: set.description ?? "",
      tagsInput: set.tags.join(", "),
      is_public: set.is_public,
      folder_id: set.folder_id ?? null,
    });
    setDialogState({ open: true, editing: set });
  }

  function closeDialog() {
    setDialogState({ open: false, editing: null });
  }

  const onSubmit = form.handleSubmit(({ tagsInput, ...values }) => {
    const payload = { ...values, tags: parseTagsInput(tagsInput) };
    const editing = dialogState.editing;
    if (editing) {
      updateMutation.mutate(payload, {
        onSuccess: () => {
          toast.success("Set updated.");
          closeDialog();
        },
        onError: (error) => toast.error(extractApiErrorMessage(error, "Couldn't update the set.")),
      });
    } else {
      createMutation.mutate(payload, {
        onSuccess: (set) => {
          toast.success("Set created.");
          closeDialog();
          onCreated?.(set);
        },
        onError: (error) => toast.error(extractApiErrorMessage(error, "Couldn't create the set.")),
      });
    }
  });

  return {
    dialogState,
    form,
    onSubmit,
    openCreate,
    openEdit,
    closeDialog,
    isSaving: createMutation.isPending || updateMutation.isPending,
  };
}
