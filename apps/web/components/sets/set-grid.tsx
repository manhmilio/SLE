import { Sprout } from "lucide-react";
import { SetCard } from "@/components/sets/set-card";
import type { StudySet } from "@/lib/api/sets.api";

export function SetGrid({ sets }: { sets: StudySet[] }) {
  if (sets.length === 0) {
    return (
      <div className="flex flex-col items-center gap-2 rounded-xl border border-dashed border-border py-12 text-center">
        <Sprout className="size-8 text-primary" />
        <p className="font-display text-lg text-foreground">Nothing planted yet</p>
        <p className="max-w-xs text-sm text-muted-foreground">
          Create your first set and watch your vocabulary take root.
        </p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
      {sets.map((set) => (
        <SetCard key={set.id} set={set} />
      ))}
    </div>
  );
}
