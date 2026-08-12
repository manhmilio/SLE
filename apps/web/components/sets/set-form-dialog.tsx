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
import { Switch } from "@/components/ui/switch";
import { Button } from "@/components/ui/button";
import type { useSetFormController } from "@/controllers/sets/use-set-form-controller";

type SetFormController = ReturnType<typeof useSetFormController>;

export function SetFormDialog({
  dialogState,
  form,
  onSubmit,
  closeDialog,
  isSaving,
}: Pick<SetFormController, "dialogState" | "form" | "onSubmit" | "closeDialog" | "isSaving">) {
  const {
    register,
    watch,
    setValue,
    formState: { errors },
  } = form;
  const isPublic = watch("is_public");

  return (
    <Dialog open={dialogState.open} onOpenChange={(open) => !open && closeDialog()}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{dialogState.editing ? "Edit set" : "New study set"}</DialogTitle>
          <DialogDescription>
            {dialogState.editing ? "Update this set's details." : "Give your set a title, tags, and visibility."}
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={onSubmit} className="flex flex-col gap-4" noValidate>
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="set-title">Title</Label>
            <Input id="set-title" {...register("title")} />
            {errors.title && <p className="text-xs text-destructive">{errors.title.message}</p>}
          </div>
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="set-description">Description (optional)</Label>
            <Textarea id="set-description" rows={3} {...register("description")} />
          </div>
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="set-tags">Tags</Label>
            <Input id="set-tags" placeholder="IELTS, vocabulary" {...register("tagsInput")} />
            <p className="text-xs text-muted-foreground">Comma separated.</p>
          </div>
          <div className="flex items-center justify-between rounded-lg border border-border p-3">
            <div>
              <Label htmlFor="set-is-public">Public</Label>
              <p className="text-xs text-muted-foreground">Anyone can find and clone this set.</p>
            </div>
            <Switch
              id="set-is-public"
              checked={isPublic}
              onCheckedChange={(checked) => setValue("is_public", checked)}
            />
          </div>
          <DialogFooter>
            <Button type="submit" disabled={isSaving}>
              {isSaving ? "Saving…" : dialogState.editing ? "Save changes" : "Create set"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
