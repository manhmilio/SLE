import Link from "next/link";
import { Layers, Lock, Globe, Pencil, Trash2 } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import type { StudySet } from "@/lib/api/sets.api";

interface SetCardProps {
  set: StudySet;
  onEdit?: (set: StudySet) => void;
  onDelete?: (set: StudySet) => void;
}

export function SetCard({ set, onEdit, onDelete }: SetCardProps) {
  return (
    <Card className="h-full transition-shadow hover:shadow-md">
      <CardHeader className="flex-row items-start justify-between gap-2">
        <Link href={`/sets/${set.id}`} className="min-w-0 flex-1">
          <CardTitle className="line-clamp-1 text-base font-medium">{set.title}</CardTitle>
        </Link>
        {(onEdit || onDelete) && (
          <div className="flex shrink-0 gap-1">
            {onEdit && (
              <Button variant="ghost" size="icon-sm" aria-label="Edit set" onClick={() => onEdit(set)}>
                <Pencil className="size-3.5" />
              </Button>
            )}
            {onDelete && (
              <Button variant="ghost" size="icon-sm" aria-label="Delete set" onClick={() => onDelete(set)}>
                <Trash2 className="size-3.5" />
              </Button>
            )}
          </div>
        )}
      </CardHeader>
      <Link href={`/sets/${set.id}`}>
        <CardContent className="flex items-center justify-between text-sm text-muted-foreground">
          <span className="inline-flex items-center gap-1">
            <Layers className="size-3.5" />
            {set.card_count} cards
          </span>
          {set.is_public ? <Globe className="size-3.5" /> : <Lock className="size-3.5" />}
        </CardContent>
      </Link>
    </Card>
  );
}
