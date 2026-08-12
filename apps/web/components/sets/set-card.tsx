import Link from "next/link";
import { Layers, Lock, Globe } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { StudySet } from "@/lib/api/sets.api";

export function SetCard({ set }: { set: StudySet }) {
  return (
    <Link href={`/sets/${set.id}`}>
      <Card className="h-full transition-shadow hover:shadow-md">
        <CardHeader>
          <CardTitle className="line-clamp-1 text-base font-medium">{set.title}</CardTitle>
        </CardHeader>
        <CardContent className="flex items-center justify-between text-sm text-muted-foreground">
          <span className="inline-flex items-center gap-1">
            <Layers className="size-3.5" />
            {set.card_count} cards
          </span>
          {set.is_public ? <Globe className="size-3.5" /> : <Lock className="size-3.5" />}
        </CardContent>
      </Card>
    </Link>
  );
}
