"use client";

import {
  DndContext,
  closestCenter,
  PointerSensor,
  useSensor,
  useSensors,
  type DragEndEvent,
} from "@dnd-kit/core";
import {
  SortableContext,
  arrayMove,
  verticalListSortingStrategy,
  useSortable,
} from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import { GripVertical, Pencil, Trash2, Sprout } from "lucide-react";
import { Button } from "@/components/ui/button";
import type { Card, CardReorderRequest } from "@/lib/api/cards.api";

interface ReorderableCardListProps {
  cards: Card[];
  onReorder: (cardId: string, body: CardReorderRequest) => void;
  onEdit: (card: Card) => void;
  onDelete: (card: Card) => void;
}

function SortableCardRow({
  card,
  onEdit,
  onDelete,
}: {
  card: Card;
  onEdit: (card: Card) => void;
  onDelete: (card: Card) => void;
}) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({
    id: card.id,
  });
  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.6 : 1,
  };

  return (
    <div
      ref={setNodeRef}
      style={style}
      className="flex items-center gap-3 rounded-xl border border-border bg-card p-3"
    >
      <button
        type="button"
        aria-label="Drag to reorder"
        className="cursor-grab touch-none text-muted-foreground"
        {...attributes}
        {...listeners}
      >
        <GripVertical className="size-4" />
      </button>
      <div className="min-w-0 flex-1">
        <p className="truncate text-sm font-medium text-foreground">{card.front}</p>
        {card.back && <p className="truncate text-xs text-muted-foreground">{card.back}</p>}
      </div>
      <div className="flex shrink-0 gap-1">
        <Button variant="ghost" size="icon-sm" aria-label="Edit card" onClick={() => onEdit(card)}>
          <Pencil className="size-3.5" />
        </Button>
        <Button variant="ghost" size="icon-sm" aria-label="Delete card" onClick={() => onDelete(card)}>
          <Trash2 className="size-3.5" />
        </Button>
      </div>
    </div>
  );
}

export function ReorderableCardList({ cards, onReorder, onEdit, onDelete }: ReorderableCardListProps) {
  const sensors = useSensors(useSensor(PointerSensor, { activationConstraint: { distance: 4 } }));

  if (cards.length === 0) {
    return (
      <div className="flex flex-col items-center gap-2 rounded-xl border border-dashed border-border py-12 text-center">
        <Sprout className="size-8 text-primary" />
        <p className="font-display text-lg text-foreground">No cards yet</p>
        <p className="max-w-xs text-sm text-muted-foreground">Add your first card to start this set.</p>
      </div>
    );
  }

  function handleDragEnd(event: DragEndEvent) {
    const { active, over } = event;
    if (!over || active.id === over.id) return;

    const oldIndex = cards.findIndex((c) => c.id === active.id);
    const newIndex = cards.findIndex((c) => c.id === over.id);
    if (oldIndex === -1 || newIndex === -1) return;

    const reordered = arrayMove(cards, oldIndex, newIndex);
    const prev = reordered[newIndex - 1];
    const next = reordered[newIndex + 1];

    onReorder(active.id as string, {
      prev_order: prev?.order ?? null,
      next_order: next?.order ?? null,
    });
  }

  return (
    <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
      <SortableContext items={cards.map((c) => c.id)} strategy={verticalListSortingStrategy}>
        <div className="flex flex-col gap-2">
          {cards.map((card) => (
            <SortableCardRow key={card.id} card={card} onEdit={onEdit} onDelete={onDelete} />
          ))}
        </div>
      </SortableContext>
    </DndContext>
  );
}
