"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAdminRoute } from "@/hooks/use-protected-route";
import { cn } from "@/lib/utils";

const ADMIN_NAV = [
  { href: "/admin", label: "Dashboard" },
  { href: "/admin/users", label: "Users" },
  { href: "/admin/sets", label: "Sets" },
  { href: "/admin/config", label: "Config" },
];

export function AdminShell({ children }: { children: React.ReactNode }) {
  const { isReady } = useAdminRoute();

  if (!isReady) {
    return (
      <div className="flex min-h-32 items-center justify-center text-sm text-muted-foreground">
        Checking access…
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-6">
      <AdminNav />
      {children}
    </div>
  );
}

function AdminNav() {
  const pathname = usePathname();

  return (
    <nav className="flex gap-1 border-b border-border">
      {ADMIN_NAV.map((item) => {
        const active = pathname === item.href;
        return (
          <Link
            key={item.href}
            href={item.href}
            className={cn(
              "border-b-2 px-3 py-2 text-sm font-medium transition-colors",
              active
                ? "border-primary text-foreground"
                : "border-transparent text-muted-foreground hover:text-foreground"
            )}
          >
            {item.label}
          </Link>
        );
      })}
    </nav>
  );
}
