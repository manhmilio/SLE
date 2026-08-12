"use client";

import { Users, Layers, BookOpen, Activity } from "lucide-react";
import type { LucideIcon } from "lucide-react";
import { AdminChart } from "@/components/admin/admin-chart";
import { cn } from "@/lib/utils";
import { useAdminDashboardController } from "@/controllers/admin/use-admin-dashboard-controller";

const RANGES = [
  { value: "7d" as const, label: "7 days" },
  { value: "30d" as const, label: "30 days" },
  { value: "90d" as const, label: "90 days" },
];

function StatTile({ label, value, icon: Icon }: { label: string; value: string | number; icon: LucideIcon }) {
  return (
    <div className="flex flex-col gap-1 rounded-xl border border-border bg-card p-4">
      <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
        <Icon className="size-3.5" />
        {label}
      </div>
      <span className="font-display text-2xl text-foreground">{value}</span>
    </div>
  );
}

export function AdminDashboardView() {
  const { dashboard, isLoading, range, setRange } = useAdminDashboardController();

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <h1 className="font-display text-2xl text-foreground">Admin dashboard</h1>
        <div className="flex gap-1.5">
          {RANGES.map((r) => (
            <button
              key={r.value}
              type="button"
              onClick={() => setRange(r.value)}
              className={cn(
                "rounded-full border px-3 py-1 text-xs font-medium transition-colors",
                range === r.value
                  ? "border-primary bg-primary text-primary-foreground"
                  : "border-border text-muted-foreground hover:bg-accent"
              )}
            >
              {r.label}
            </button>
          ))}
        </div>
      </div>

      {isLoading || !dashboard ? (
        <div className="h-24 animate-pulse rounded-xl bg-muted" />
      ) : (
        <>
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
            <StatTile label="Total users" value={dashboard.users.total} icon={Users} />
            <StatTile label="Active users" value={dashboard.users.active} icon={Activity} />
            <StatTile label="Total sets" value={dashboard.sets.total} icon={Layers} />
            <StatTile label="Sessions today" value={dashboard.sessions.today} icon={BookOpen} />
          </div>
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
            <StatTile label="New today" value={dashboard.users.new_today} icon={Users} />
            <StatTile label="New (7d)" value={dashboard.users.new_7d} icon={Users} />
            <StatTile label="DAU" value={dashboard.active_users.dau} icon={Activity} />
            <StatTile label="MAU" value={dashboard.active_users.mau} icon={Activity} />
          </div>

          <div className="flex flex-col gap-2">
            <h2 className="font-display text-lg text-foreground">User growth</h2>
            <AdminChart data={dashboard.user_growth} />
          </div>
          <div className="flex flex-col gap-2">
            <h2 className="font-display text-lg text-foreground">Sessions</h2>
            <AdminChart data={dashboard.session_chart} />
          </div>
        </>
      )}
    </div>
  );
}
