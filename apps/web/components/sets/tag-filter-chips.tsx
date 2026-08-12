import { cn } from "@/lib/utils";

interface TagFilterChipsProps {
  tags: string[];
  activeTag: string | null;
  onSelect: (tag: string | null) => void;
}

export function TagFilterChips({ tags, activeTag, onSelect }: TagFilterChipsProps) {
  if (tags.length === 0) return null;

  return (
    <div className="flex flex-wrap gap-2">
      <button
        type="button"
        onClick={() => onSelect(null)}
        className={cn(
          "rounded-full border px-3 py-1 text-xs font-medium transition-colors",
          activeTag === null
            ? "border-primary bg-primary text-primary-foreground"
            : "border-border text-muted-foreground hover:bg-accent"
        )}
      >
        All
      </button>
      {tags.map((tag) => (
        <button
          key={tag}
          type="button"
          onClick={() => onSelect(tag)}
          className={cn(
            "rounded-full border px-3 py-1 text-xs font-medium transition-colors",
            activeTag === tag
              ? "border-primary bg-primary text-primary-foreground"
              : "border-border text-muted-foreground hover:bg-accent"
          )}
        >
          {tag}
        </button>
      ))}
    </div>
  );
}
