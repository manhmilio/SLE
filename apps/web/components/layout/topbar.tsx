"use client";

import { LogOut } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ThemeToggle } from "@/components/layout/theme-toggle";
import { useAppShellController } from "@/controllers/layout/use-app-shell-controller";

export function Topbar() {
  const { user, logout, isLoggingOut } = useAppShellController();

  return (
    <header className="flex h-14 shrink-0 items-center justify-end gap-2 border-b border-border px-4 md:px-6">
      <span className="mr-auto font-display text-sm text-muted-foreground md:hidden">
        Soulee
      </span>
      {user && (
        <span className="hidden text-sm text-muted-foreground sm:inline">
          {user.display_name}
        </span>
      )}
      <ThemeToggle />
      <Button
        variant="ghost"
        size="icon"
        aria-label="Log out"
        onClick={logout}
        disabled={isLoggingOut}
      >
        <LogOut className="size-4" />
      </Button>
    </header>
  );
}
