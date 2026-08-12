"use client";

import { useMatchController } from "@/controllers/study/use-match-controller";
import { StudySessionSummary } from "@/components/study/study-session-summary";
import { StudyEmptyState } from "@/components/study/study-empty-state";
import { cn } from "@/lib/utils";

export function MatchBoard({ setId }: { setId: string }) {
  const match = useMatchController(setId);

  if (match.isEmpty) {
    return <StudyEmptyState setId={setId} />;
  }

  if (match.isDone && match.summary) {
    return <StudySessionSummary summary={match.summary} setId={setId} />;
  }

  if (match.tiles.length === 0) {
    return <div className="h-64 animate-pulse rounded-xl bg-muted" />;
  }

  return (
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-4">
      {match.tiles
        .filter((tile) => !tile.matched)
        .map((tile) => (
          <button
            key={tile.id}
            type="button"
            onClick={() => match.selectTile(tile.id)}
            className={cn(
              "flex min-h-24 items-center justify-center rounded-xl border p-3 text-center text-sm font-medium transition-colors",
              match.selectedId === tile.id
                ? "border-primary bg-primary/10 text-primary"
                : "border-border bg-card text-foreground hover:bg-accent",
              match.shakeIds.includes(tile.id) && "border-destructive text-destructive"
            )}
          >
            {tile.text}
          </button>
        ))}
    </div>
  );
}
