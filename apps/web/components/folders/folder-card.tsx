"use client";

import Link from "next/link";
import { Folder as FolderIcon, Pencil, Trash2 } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import type { Folder } from "@/lib/api/folders.api";

interface FolderCardProps {
  folder: Folder;
  onEdit: (folder: Folder) => void;
  onDelete: (folder: Folder) => void;
}

export function FolderCard({ folder, onEdit, onDelete }: FolderCardProps) {
  return (
    <Card className="h-full">
      <CardHeader className="flex-row items-start justify-between gap-2">
        <Link href={`/folders/${folder.id}`} className="flex min-w-0 items-center gap-2">
          <FolderIcon className="size-4 shrink-0 text-primary" />
          <CardTitle className="line-clamp-1 text-base font-medium">{folder.name}</CardTitle>
        </Link>
        <div className="flex shrink-0 gap-1">
          <Button variant="ghost" size="icon-sm" aria-label="Edit folder" onClick={() => onEdit(folder)}>
            <Pencil className="size-3.5" />
          </Button>
          <Button variant="ghost" size="icon-sm" aria-label="Delete folder" onClick={() => onDelete(folder)}>
            <Trash2 className="size-3.5" />
          </Button>
        </div>
      </CardHeader>
      {folder.description && (
        <CardContent className="line-clamp-2 text-sm text-muted-foreground">
          {folder.description}
        </CardContent>
      )}
    </Card>
  );
}
