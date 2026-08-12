import { Flame } from "lucide-react";
import { cn } from "@/lib/utils";

interface StreakBadgeProps {
  streak: number;
  className?: string;
}

export function StreakBadge({ streak, className }: StreakBadgeProps) {
  return (
    <div
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full bg-flame/10 px-3 py-1.5 text-sm font-medium text-flame",
        className
      )}
    >
      <Flame className="size-4" />
      {streak > 0 ? (
        <span>
          {streak} day{streak === 1 ? "" : "s"} strong
        </span>
      ) : (
        <span>Start your streak today</span>
      )}
    </div>
  );
}
