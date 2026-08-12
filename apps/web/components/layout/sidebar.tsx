"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { House, Folder, Layers, ChartBar, Settings, ShieldCheck } from "lucide-react";
import { Logo } from "@/components/brand/logo";
import { cn } from "@/lib/utils";
import { useAppShellController } from "@/controllers/layout/use-app-shell-controller";

const NAV_ITEMS = [
  { href: "/dashboard", label: "Home", icon: House },
  { href: "/folders", label: "Folders", icon: Folder },
  { href: "/sets", label: "Sets", icon: Layers },
  { href: "/stats", label: "Stats", icon: ChartBar },
  { href: "/settings", label: "Settings", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();
  const { isAdmin } = useAppShellController();

  const items = isAdmin
    ? [...NAV_ITEMS, { href: "/admin", label: "Admin", icon: ShieldCheck }]
    : NAV_ITEMS;

  return (
    <aside className="hidden w-60 shrink-0 flex-col border-r border-sidebar-border bg-sidebar px-4 py-6 md:flex">
      <Link href="/dashboard" className="mb-8 px-2">
        <Logo />
      </Link>
      <nav className="flex flex-col gap-1">
        {items.map(({ href, label, icon: Icon }) => {
          const active = pathname === href || pathname.startsWith(`${href}/`);
          return (
            <Link
              key={href}
              href={href}
              className={cn(
                "flex items-center gap-2.5 rounded-lg px-3 py-2 text-sm font-medium text-sidebar-foreground/80 transition-colors hover:bg-sidebar-accent hover:text-sidebar-accent-foreground",
                active && "bg-sidebar-accent text-sidebar-accent-foreground"
              )}
            >
              <Icon className="size-4" />
              {label}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
