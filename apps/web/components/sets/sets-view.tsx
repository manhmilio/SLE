"use client";

import { Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { SetSearchBar } from "@/components/sets/set-search-bar";
import { TagFilterChips } from "@/components/sets/tag-filter-chips";
import { SetGrid } from "@/components/sets/set-grid";
import { SetFormDialog } from "@/components/sets/set-form-dialog";
import { useSetListController } from "@/controllers/sets/use-set-list-controller";
import { useSetFormController } from "@/controllers/sets/use-set-form-controller";

export function SetsView() {
  const list = useSetListController();
  const form = useSetFormController();

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <h1 className="font-display text-2xl text-foreground">Your sets</h1>
        <Button onClick={form.openCreate}>
          <Plus className="size-4" />
          New set
        </Button>
      </div>

      <div className="flex flex-col gap-3">
        <SetSearchBar value={list.search} onChange={list.setSearch} />
        <TagFilterChips tags={list.availableTags} activeTag={list.activeTag} onSelect={list.setActiveTag} />
      </div>

      {list.isLoading ? (
        <div className="h-40 animate-pulse rounded-xl bg-muted" />
      ) : (
        <SetGrid sets={list.sets} onEdit={form.openEdit} onDelete={list.remove} />
      )}

      <SetFormDialog
        dialogState={form.dialogState}
        form={form.form}
        onSubmit={form.onSubmit}
        closeDialog={form.closeDialog}
        isSaving={form.isSaving}
      />
    </div>
  );
}
