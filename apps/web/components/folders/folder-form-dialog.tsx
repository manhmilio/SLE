"use client";

import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import type { useFolderFormController } from "@/controllers/folders/use-folder-form-controller";

type FolderFormController = ReturnType<typeof useFolderFormController>;

export function FolderFormDialog({
  dialogState,
  form,
  onSubmit,
  closeDialog,
  isSaving,
}: Pick<FolderFormController, "dialogState" | "form" | "onSubmit" | "closeDialog" | "isSaving">) {
  const {
    register,
    formState: { errors },
  } = form;

  return (
    <Dialog open={dialogState.open} onOpenChange={(open) => !open && closeDialog()}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{dialogState.editing ? "Rename folder" : "New folder"}</DialogTitle>
          <DialogDescription>
            {dialogState.editing ? "Update this folder's name or description." : "Group your sets under a name."}
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={onSubmit} className="flex flex-col gap-4" noValidate>
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="folder-name">Name</Label>
            <Input id="folder-name" {...register("name")} />
            {errors.name && <p className="text-xs text-destructive">{errors.name.message}</p>}
          </div>
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="folder-description">Description (optional)</Label>
            <Textarea id="folder-description" rows={3} {...register("description")} />
          </div>
          <DialogFooter>
            <Button type="submit" disabled={isSaving}>
              {isSaving ? "Saving…" : dialogState.editing ? "Save changes" : "Create folder"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
