import { Globe, Lock, Trash2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import type { AdminSetListItem } from "@/lib/api/admin.api";

interface AdminSetsTableProps {
  sets: AdminSetListItem[];
  onToggleVisibility: (set: AdminSetListItem) => void;
  onDelete: (set: AdminSetListItem) => void;
}

export function AdminSetsTable({ sets, onToggleVisibility, onDelete }: AdminSetsTableProps) {
  if (sets.length === 0) {
    return <p className="py-8 text-center text-sm text-muted-foreground">No sets found.</p>;
  }

  return (
    <div className="overflow-x-auto rounded-xl border border-border">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-border text-left text-xs text-muted-foreground">
            <th className="px-3 py-2">Title</th>
            <th className="px-3 py-2">Owner</th>
            <th className="px-3 py-2">Visibility</th>
            <th className="px-3 py-2">Cards</th>
            <th className="px-3 py-2">Sessions</th>
            <th className="px-3 py-2">Clones</th>
            <th className="px-3 py-2 text-right">Actions</th>
          </tr>
        </thead>
        <tbody className="tabular-nums">
          {sets.map((set) => (
            <tr key={set.id} className="border-b border-border last:border-0">
              <td className="max-w-48 truncate px-3 py-2 font-medium text-foreground">{set.title}</td>
              <td className="max-w-40 truncate px-3 py-2 text-muted-foreground">{set.owner_email}</td>
              <td className="px-3 py-2">
                <Badge variant={set.is_public ? "secondary" : "outline"}>
                  {set.is_public ? "public" : "private"}
                </Badge>
              </td>
              <td className="px-3 py-2 text-muted-foreground">{set.card_count}</td>
              <td className="px-3 py-2 text-muted-foreground">{set.total_sessions}</td>
              <td className="px-3 py-2 text-muted-foreground">{set.total_clones}</td>
              <td className="px-3 py-2">
                <div className="flex justify-end gap-1">
                  <Button
                    variant="ghost"
                    size="icon-sm"
                    aria-label={set.is_public ? "Make private" : "Make public"}
                    onClick={() => onToggleVisibility(set)}
                  >
                    {set.is_public ? <Lock className="size-3.5" /> : <Globe className="size-3.5" />}
                  </Button>
                  <Button variant="ghost" size="icon-sm" aria-label="Delete set" onClick={() => onDelete(set)}>
                    <Trash2 className="size-3.5" />
                  </Button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
