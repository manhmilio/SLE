import Link from "next/link";
import { Button } from "@/components/ui/button";

export function StudyEmptyState({ setId }: { setId: string }) {
  return (
    <div className="flex flex-col items-center gap-3 py-16 text-center">
      <p className="font-display text-xl text-foreground">You&apos;re all caught up</p>
      <p className="text-sm text-muted-foreground">No cards are due right now — check back later.</p>
      <Button asChild variant="outline">
        <Link href={`/sets/${setId}`}>Back to set</Link>
      </Button>
    </div>
  );
}
