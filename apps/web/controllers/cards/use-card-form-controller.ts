"use client";

import { useState } from "react";
import { toast } from "sonner";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { cardSchema, type CardFormValues } from "@/lib/validations/card.schema";
import {
  useCreateCardMutation,
  useUpdateCardMutation,
  useUploadCardImageMutation,
} from "@/lib/mutations/card-mutations";
import { extractApiErrorMessage } from "@/lib/api/errors";
import type { Card } from "@/lib/api/cards.api";

export function useCardFormController(setId: string) {
  const [dialogState, setDialogState] = useState<{ open: boolean; editing: Card | null }>({
    open: false,
    editing: null,
  });
  const [imageFile, setImageFile] = useState<File | null>(null);

  const form = useForm<CardFormValues>({
    resolver: zodResolver(cardSchema),
    defaultValues: { front: "", back: "" },
  });

  const createMutation = useCreateCardMutation(setId);
  const updateMutation = useUpdateCardMutation(setId);
  const uploadImageMutation = useUploadCardImageMutation(setId);

  function openCreate() {
    form.reset({ front: "", back: "" });
    setImageFile(null);
    setDialogState({ open: true, editing: null });
  }

  function openEdit(card: Card) {
    form.reset({ front: card.front, back: card.back ?? "" });
    setImageFile(null);
    setDialogState({ open: true, editing: card });
  }

  function closeDialog() {
    setDialogState({ open: false, editing: null });
    setImageFile(null);
  }

  async function uploadPendingImage(cardId: string) {
    if (!imageFile) return;
    try {
      await uploadImageMutation.mutateAsync({ cardId, file: imageFile });
    } catch (error) {
      toast.error(extractApiErrorMessage(error, "Card saved, but the image failed to upload."));
    }
  }

  const onSubmit = form.handleSubmit((values) => {
    const editing = dialogState.editing;
    if (editing) {
      updateMutation.mutate(
        { cardId: editing.id, body: values },
        {
          onSuccess: async () => {
            await uploadPendingImage(editing.id);
            toast.success("Card updated.");
            closeDialog();
          },
          onError: (error) => toast.error(extractApiErrorMessage(error, "Couldn't update the card.")),
        }
      );
    } else {
      createMutation.mutate(values, {
        onSuccess: async (card) => {
          await uploadPendingImage(card.id);
          toast.success("Card added.");
          closeDialog();
        },
        onError: (error) => toast.error(extractApiErrorMessage(error, "Couldn't create the card.")),
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
    imageFile,
    setImageFile,
    isSaving: createMutation.isPending || updateMutation.isPending || uploadImageMutation.isPending,
  };
}
