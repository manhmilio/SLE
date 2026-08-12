import Link from "next/link";
import { Layers, GraduationCap, PencilLine, Shuffle } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";

const STUDY_MODES = [
  { mode: "flashcard", label: "Flashcards", icon: Layers },
  { mode: "learn", label: "Learn", icon: GraduationCap },
  { mode: "test", label: "Test", icon: PencilLine },
  { mode: "match", label: "Match", icon: Shuffle },
] as const;

export function StudyModeLinks({ setId }: { setId: string }) {
  return (
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
      {STUDY_MODES.map(({ mode, label, icon: Icon }) => (
        <Link key={mode} href={`/sets/${setId}/study/${mode}`}>
          <Card className="h-full transition-shadow hover:shadow-md">
            <CardContent className="flex flex-col items-center gap-2 py-4 text-center">
              <Icon className="size-5 text-primary" />
              <span className="text-sm font-medium text-foreground">{label}</span>
            </CardContent>
          </Card>
        </Link>
      ))}
    </div>
  );
}
