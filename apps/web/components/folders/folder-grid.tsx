import { FolderPlus } from "lucide-react";
import { FolderCard } from "@/components/folders/folder-card";
import type { Folder } from "@/lib/api/folders.api";

interface FolderGridProps {
  folders: Folder[];
  onEdit: (folder: Folder) => void;
  onDelete: (folder: Folder) => void;
}

export function FolderGrid({ folders, onEdit, onDelete }: FolderGridProps) {
  if (folders.length === 0) {
    return (
      <div className="flex flex-col items-center gap-2 rounded-xl border border-dashed border-border py-12 text-center">
        <FolderPlus className="size-8 text-primary" />
        <p className="font-display text-lg text-foreground">No folders yet</p>
        <p className="max-w-xs text-sm text-muted-foreground">
          Group your sets into folders to keep your study space tidy.
        </p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
      {folders.map((folder) => (
        <FolderCard key={folder.id} folder={folder} onEdit={onEdit} onDelete={onDelete} />
      ))}
    </div>
  );
}
