import { Search } from "lucide-react";
import { Input } from "@/components/ui/input";

interface SetSearchBarProps {
  value: string;
  onChange: (value: string) => void;
}

export function SetSearchBar({ value, onChange }: SetSearchBarProps) {
  return (
    <div className="relative">
      <Search className="absolute top-1/2 left-2.5 size-4 -translate-y-1/2 text-muted-foreground" />
      <Input
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="Search your sets…"
        className="pl-8"
      />
    </div>
  );
}
