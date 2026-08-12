"use client";

import Link from "next/link";
import { ArrowLeft, Pencil, Trash2, Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { SetGrid } from "@/components/sets/set-grid";
import { SetFormDialog } from "@/components/sets/set-form-dialog";
import { FolderFormDialog } from "@/components/folders/folder-form-dialog";
import { useFolderDetailController } from "@/controllers/folders/use-folder-detail-controller";
import { useFolderFormController } from "@/controllers/folders/use-folder-form-controller";
import { useSetListController } from "@/controllers/sets/use-set-list-controller";
import { useSetFormController } from "@/controllers/sets/use-set-form-controller";

export function FolderDetailView({ folderId }: { folderId: string }) {
  const detail = useFolderDetailController(folderId);
  const folderForm = useFolderFormController();
  const setList = useSetListController({ folderId });
  const setForm = useSetFormController({ defaultFolderId: folderId });

  if (detail.isLoading || !detail.folder) {
    return <div className="h-32 animate-pulse rounded-xl bg-muted" />;
  }

  const folder = detail.folder;

  return (
    <div className="flex flex-col gap-6">
      <Link
        href="/folders"
        className="inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground"
      >
        <ArrowLeft className="size-3.5" />
        All folders
      </Link>

      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h1 className="font-display text-2xl text-foreground">{folder.name}</h1>
          {folder.description && <p className="text-muted-foreground">{folder.description}</p>}
        </div>
        <div className="flex shrink-0 gap-2">
          <Button variant="outline" size="icon" aria-label="Rename folder" onClick={() => folderForm.openEdit(folder)}>
            <Pencil className="size-4" />
          </Button>
          <Button variant="outline" size="icon" aria-label="Delete folder" onClick={detail.remove}>
            <Trash2 className="size-4" />
          </Button>
          <Button onClick={setForm.openCreate}>
            <Plus className="size-4" />
            New set
          </Button>
        </div>
      </div>

      {setList.isLoading ? (
        <div className="h-40 animate-pulse rounded-xl bg-muted" />
      ) : (
        <SetGrid sets={setList.sets} onEdit={setForm.openEdit} onDelete={setList.remove} />
      )}

      <FolderFormDialog
        dialogState={folderForm.dialogState}
        form={folderForm.form}
        onSubmit={folderForm.onSubmit}
        closeDialog={folderForm.closeDialog}
        isSaving={folderForm.isSaving}
      />
      <SetFormDialog
        dialogState={setForm.dialogState}
        form={setForm.form}
        onSubmit={setForm.onSubmit}
        closeDialog={setForm.closeDialog}
        isSaving={setForm.isSaving}
      />
    </div>
  );
}
