"use client";

import Link from "next/link";
import { Logo } from "@/components/brand/logo";
import { useGuestRoute } from "@/hooks/use-protected-route";

export function AuthShell({ children }: { children: React.ReactNode }) {
  useGuestRoute();

  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-8 bg-gradient-to-b from-secondary/50 to-background px-4 py-12">
      <Link href="/">
        <Logo />
      </Link>
      <div className="w-full max-w-sm">{children}</div>
    </div>
  );
}
