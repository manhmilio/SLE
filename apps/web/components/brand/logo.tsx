import { Sprout } from "lucide-react";
import { cn } from "@/lib/utils";

interface LogoProps {
  className?: string;
  iconClassName?: string;
  wordmarkClassName?: string;
  showWordmark?: boolean;
}

export function Logo({
  className,
  iconClassName,
  wordmarkClassName,
  showWordmark = true,
}: LogoProps) {
  return (
    <div className={cn("inline-flex items-center gap-2", className)}>
      <span
        className={cn(
          "inline-flex size-8 items-center justify-center rounded-full bg-primary/10 text-primary",
          iconClassName
        )}
      >
        <Sprout className="size-4.5" />
      </span>
      {showWordmark && (
        <span
          className={cn(
            "font-display text-xl font-medium tracking-tight text-foreground",
            wordmarkClassName
          )}
        >
          Soulee
        </span>
      )}
    </div>
  );
}
