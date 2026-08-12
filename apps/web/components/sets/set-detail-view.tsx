"use client";

import Link from "next/link";
import { ArrowLeft, Pencil, Trash2, Plus, Globe, Lock } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { CloneButton } from "@/components/sets/clone-button";
import { SetFormDialog } from "@/components/sets/set-form-dialog";
import { CardEditorDialog } from "@/components/cards/card-editor-dialog";
import { ReorderableCardList } from "@/components/cards/reorderable-card-list";
import { StudyModeLinks } from "@/components/study/study-mode-links";
import { useSetDetailController } from "@/controllers/sets/use-set-detail-controller";
import { useSetFormController } from "@/controllers/sets/use-set-form-controller";
import { useCardListController } from "@/controllers/cards/use-card-list-controller";
import { useCardFormController } from "@/controllers/cards/use-card-form-controller";

export function SetDetailView({ setId }: { setId: string }) {
  const detail = useSetDetailController(setId);
  const setForm = useSetFormController();
  const cardList = useCardListController(setId);
  const cardForm = useCardFormController(setId);

  if (detail.isLoading || !detail.set) {
    return <div className="h-40 animate-pulse rounded-xl bg-muted" />;
  }

  const set = detail.set;

  return (
    <div className="flex flex-col gap-6">
      <Link
        href="/sets"
        className="inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground"
      >
        <ArrowLeft className="size-3.5" />
        All sets
      </Link>

      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div className="flex flex-col gap-1.5">
          <div className="flex items-center gap-2">
            <h1 className="font-display text-2xl text-foreground">{set.title}</h1>
            {set.is_public ? (
              <Globe className="size-4 text-muted-foreground" />
            ) : (
              <Lock className="size-4 text-muted-foreground" />
            )}
          </div>
          {set.description && <p className="text-muted-foreground">{set.description}</p>}
          {set.tags.length > 0 && (
            <div className="flex flex-wrap gap-1.5">
              {set.tags.map((tag) => (
                <Badge key={tag} variant="secondary">
                  {tag}
                </Badge>
              ))}
            </div>
          )}
        </div>
        <div className="flex shrink-0 gap-2">
          <CloneButton setId={set.id} />
          <Button variant="outline" size="icon" aria-label="Edit set" onClick={() => setForm.openEdit(set)}>
            <Pencil className="size-4" />
          </Button>
          <Button variant="outline" size="icon" aria-label="Delete set" onClick={detail.remove}>
            <Trash2 className="size-4" />
          </Button>
        </div>
      </div>

      <StudyModeLinks setId={set.id} />

      <div className="flex flex-col gap-3">
        <div className="flex items-center justify-between">
          <h2 className="font-display text-lg text-foreground">Cards ({cardList.total})</h2>
          <Button onClick={cardForm.openCreate}>
            <Plus className="size-4" />
            Add card
          </Button>
        </div>
        {cardList.isLoading ? (
          <div className="h-40 animate-pulse rounded-xl bg-muted" />
        ) : (
          <ReorderableCardList
            cards={cardList.cards}
            onReorder={cardList.reorder}
            onEdit={cardForm.openEdit}
            onDelete={cardList.remove}
          />
        )}
      </div>

      <SetFormDialog
        dialogState={setForm.dialogState}
        form={setForm.form}
        onSubmit={setForm.onSubmit}
        closeDialog={setForm.closeDialog}
        isSaving={setForm.isSaving}
      />
      <CardEditorDialog
        dialogState={cardForm.dialogState}
        form={cardForm.form}
        onSubmit={cardForm.onSubmit}
        closeDialog={cardForm.closeDialog}
        isSaving={cardForm.isSaving}
        setImageFile={cardForm.setImageFile}
      />
    </div>
  );
}
