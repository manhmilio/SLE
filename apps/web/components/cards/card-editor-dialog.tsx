"use client";

import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import type { useCardFormController } from "@/controllers/cards/use-card-form-controller";

type CardFormController = ReturnType<typeof useCardFormController>;

export function CardEditorDialog({
  dialogState,
  form,
  onSubmit,
  closeDialog,
  isSaving,
  setImageFile,
}: Pick<
  CardFormController,
  "dialogState" | "form" | "onSubmit" | "closeDialog" | "isSaving" | "setImageFile"
>) {
  const {
    register,
    formState: { errors },
  } = form;

  return (
    <Dialog open={dialogState.open} onOpenChange={(open) => !open && closeDialog()}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{dialogState.editing ? "Edit card" : "New card"}</DialogTitle>
        </DialogHeader>
        <form onSubmit={onSubmit} className="flex flex-col gap-4" noValidate>
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="card-front">Front</Label>
            <Textarea id="card-front" rows={2} {...register("front")} />
            {errors.front && <p className="text-xs text-destructive">{errors.front.message}</p>}
          </div>
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="card-back">Back</Label>
            <Textarea id="card-back" rows={2} {...register("back")} />
          </div>
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="card-image">Image (optional)</Label>
            <Input
              id="card-image"
              type="file"
              accept="image/jpeg,image/png,image/webp"
              onChange={(e) => setImageFile(e.target.files?.[0] ?? null)}
            />
          </div>
          <DialogFooter>
            <Button type="submit" disabled={isSaving}>
              {isSaving ? "Saving…" : dialogState.editing ? "Save changes" : "Add card"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
