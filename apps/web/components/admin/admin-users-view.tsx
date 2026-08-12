"use client";

import { Search } from "lucide-react";
import { Input } from "@/components/ui/input";
import { AdminUsersTable } from "@/components/admin/admin-users-table";
import { AdminPagination } from "@/components/admin/admin-pagination";
import { cn } from "@/lib/utils";
import { useAdminUsersController } from "@/controllers/admin/use-admin-users-controller";

const ROLE_FILTERS = [
  { value: "", label: "All roles" },
  { value: "user", label: "User" },
  { value: "admin", label: "Admin" },
];

const ACTIVE_FILTERS = [
  { value: "", label: "All statuses" },
  { value: "active", label: "Active" },
  { value: "banned", label: "Banned" },
];

function Pill({ active, onClick, children }: { active: boolean; onClick: () => void; children: React.ReactNode }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        "rounded-full border px-3 py-1 text-xs font-medium transition-colors",
        active
          ? "border-primary bg-primary text-primary-foreground"
          : "border-border text-muted-foreground hover:bg-accent"
      )}
    >
      {children}
    </button>
  );
}

export function AdminUsersView() {
  const controller = useAdminUsersController();

  return (
    <div className="flex flex-col gap-6">
      <h1 className="font-display text-2xl text-foreground">Users</h1>

      <div className="flex flex-col gap-3">
        <div className="relative max-w-sm">
          <Search className="absolute top-1/2 left-2.5 size-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            value={controller.search}
            onChange={(e) => controller.setSearch(e.target.value)}
            placeholder="Search by name or email…"
            className="pl-8"
          />
        </div>
        <div className="flex flex-wrap gap-3">
          <div className="flex gap-1.5">
            {ROLE_FILTERS.map((f) => (
              <Pill key={f.value} active={controller.roleFilter === f.value} onClick={() => controller.setRoleFilter(f.value)}>
                {f.label}
              </Pill>
            ))}
          </div>
          <div className="flex gap-1.5">
            {ACTIVE_FILTERS.map((f) => (
              <Pill
                key={f.value}
                active={controller.activeFilter === f.value}
                onClick={() => controller.setActiveFilter(f.value)}
              >
                {f.label}
              </Pill>
            ))}
          </div>
        </div>
      </div>

      {controller.isLoading ? (
        <div className="h-40 animate-pulse rounded-xl bg-muted" />
      ) : (
        <AdminUsersTable
          users={controller.users}
          isSelf={controller.isSelf}
          onToggleActive={controller.toggleActive}
          onToggleRole={controller.toggleRole}
          onResetPassword={controller.resetPassword}
          onDelete={controller.remove}
        />
      )}

      <AdminPagination
        page={controller.page}
        limit={controller.limit}
        total={controller.total}
        onPageChange={controller.setPage}
      />
    </div>
  );
}
