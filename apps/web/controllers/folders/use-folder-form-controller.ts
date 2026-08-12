"use client";

import { useState } from "react";
import { toast } from "sonner";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { folderSchema, type FolderFormValues } from "@/lib/validations/folder.schema";
import { useCreateFolderMutation, useUpdateFolderMutation } from "@/lib/mutations/folder-mutations";
import { extractApiErrorMessage } from "@/lib/api/errors";
import type { Folder } from "@/lib/api/folders.api";

interface UseFolderFormControllerOptions {
  onCreated?: (folder: Folder) => void;
}

export function useFolderFormController(options: UseFolderFormControllerOptions = {}) {
  const [dialogState, setDialogState] = useState<{ open: boolean; editing: Folder | null }>({
    open: false,
    editing: null,
  });

  const form = useForm<FolderFormValues>({
    resolver: zodResolver(folderSchema),
    defaultValues: { name: "", description: "" },
  });

  const createMutation = useCreateFolderMutation();
  const updateMutation = useUpdateFolderMutation();

  function openCreate() {
    form.reset({ name: "", description: "" });
    setDialogState({ open: true, editing: null });
  }

  function openEdit(folder: Folder) {
    form.reset({ name: folder.name, description: folder.description ?? "" });
    setDialogState({ open: true, editing: folder });
  }

  function closeDialog() {
    setDialogState({ open: false, editing: null });
  }

  const onSubmit = form.handleSubmit((values) => {
    const editing = dialogState.editing;
    if (editing) {
      updateMutation.mutate(
        { folderId: editing.id, body: values },
        {
          onSuccess: () => {
            toast.success("Folder updated.");
            closeDialog();
          },
          onError: (error) => toast.error(extractApiErrorMessage(error, "Couldn't update the folder.")),
        }
      );
    } else {
      createMutation.mutate(values, {
        onSuccess: (folder) => {
          toast.success("Folder created.");
          closeDialog();
          options.onCreated?.(folder);
        },
        onError: (error) => toast.error(extractApiErrorMessage(error, "Couldn't create the folder.")),
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
