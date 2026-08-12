"use client";

import { AdminSetsTable } from "@/components/admin/admin-sets-table";
import { AdminPagination } from "@/components/admin/admin-pagination";
import { cn } from "@/lib/utils";
import { useAdminSetsController } from "@/controllers/admin/use-admin-sets-controller";

const VISIBILITY_FILTERS = [
  { value: "", label: "All sets" },
  { value: "public", label: "Public" },
  { value: "private", label: "Private" },
];

export function AdminSetsView() {
  const controller = useAdminSetsController();

  return (
    <div className="flex flex-col gap-6">
      <h1 className="font-display text-2xl text-foreground">Sets</h1>

      <div className="flex gap-1.5">
        {VISIBILITY_FILTERS.map((f) => (
          <button
            key={f.value}
            type="button"
            onClick={() => controller.setVisibilityFilter(f.value)}
            className={cn(
              "rounded-full border px-3 py-1 text-xs font-medium transition-colors",
              controller.visibilityFilter === f.value
                ? "border-primary bg-primary text-primary-foreground"
                : "border-border text-muted-foreground hover:bg-accent"
            )}
          >
            {f.label}
          </button>
        ))}
      </div>

      {controller.isLoading ? (
        <div className="h-40 animate-pulse rounded-xl bg-muted" />
      ) : (
        <AdminSetsTable
          sets={controller.sets}
          onToggleVisibility={controller.toggleVisibility}
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
