"use client";

import { Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { FolderGrid } from "@/components/folders/folder-grid";
import { FolderFormDialog } from "@/components/folders/folder-form-dialog";
import { useFolderListController } from "@/controllers/folders/use-folder-list-controller";
import { useFolderFormController } from "@/controllers/folders/use-folder-form-controller";

export function FoldersView() {
  const list = useFolderListController();
  const form = useFolderFormController();

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <h1 className="font-display text-2xl text-foreground">Folders</h1>
        <Button onClick={form.openCreate}>
          <Plus className="size-4" />
          New folder
        </Button>
      </div>

      {list.isLoading ? (
        <div className="h-32 animate-pulse rounded-xl bg-muted" />
      ) : (
        <FolderGrid folders={list.folders} onEdit={form.openEdit} onDelete={list.remove} />
      )}

      <FolderFormDialog
        dialogState={form.dialogState}
        form={form.form}
        onSubmit={form.onSubmit}
        closeDialog={form.closeDialog}
        isSaving={form.isSaving}
      />
    </div>
  );
}
