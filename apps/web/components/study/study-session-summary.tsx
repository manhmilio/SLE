import Link from "next/link";
import { Button } from "@/components/ui/button";
import type { SessionEndResponse } from "@/lib/api/sessions.api";

export function StudySessionSummary({
  summary,
  setId,
}: {
  summary: SessionEndResponse;
  setId: string;
}) {
  return (
    <div className="flex flex-col items-center gap-6 py-16 text-center">
      <p className="font-display text-2xl text-foreground">Nice work.</p>
      <div className="flex gap-8">
        <div>
          <p className="font-display text-3xl text-primary">{Math.round(summary.accuracy)}%</p>
          <p className="text-xs text-muted-foreground">accuracy</p>
        </div>
        <div>
          <p className="font-display text-3xl text-primary">{summary.cards_studied}</p>
          <p className="text-xs text-muted-foreground">cards studied</p>
        </div>
        <div>
          <p className="font-display text-3xl text-primary">{summary.duration_seconds}s</p>
          <p className="text-xs text-muted-foreground">time</p>
        </div>
      </div>
      <Button asChild>
        <Link href={`/sets/${setId}`}>Back to set</Link>
      </Button>
    </div>
  );
}
