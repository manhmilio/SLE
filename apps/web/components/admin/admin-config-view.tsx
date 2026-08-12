"use client";

import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Switch } from "@/components/ui/switch";
import { Button } from "@/components/ui/button";
import { useAdminConfigController } from "@/controllers/admin/use-admin-config-controller";

const NUMBER_FIELDS = [
  { name: "initial_ease_factor" as const, label: "Initial ease factor", step: "0.1" },
  { name: "min_ease_factor" as const, label: "Min ease factor", step: "0.1" },
  { name: "known_threshold_days" as const, label: "Known threshold (days)", step: "1" },
  { name: "max_sets_per_user" as const, label: "Max sets per user", step: "1" },
  { name: "max_cards_per_set" as const, label: "Max cards per set", step: "1" },
  { name: "max_image_size_mb" as const, label: "Max image size (MB)", step: "1" },
];

export function AdminConfigView() {
  const { isLoading, form, onSubmit, isSaving } = useAdminConfigController();
  const {
    register,
    watch,
    setValue,
    formState: { errors },
  } = form;
  const allowRegistration = watch("allow_registration");

  return (
    <div className="flex max-w-lg flex-col gap-6">
      <h1 className="font-display text-2xl text-foreground">System config</h1>

      {isLoading ? (
        <div className="h-64 animate-pulse rounded-xl bg-muted" />
      ) : (
        <form onSubmit={onSubmit} className="flex flex-col gap-4" noValidate>
          {NUMBER_FIELDS.map((field) => (
            <div key={field.name} className="flex flex-col gap-1.5">
              <Label htmlFor={field.name}>{field.label}</Label>
              <Input
                id={field.name}
                type="number"
                step={field.step}
                {...register(field.name, { valueAsNumber: true })}
              />
              {errors[field.name] && (
                <p className="text-xs text-destructive">{errors[field.name]?.message}</p>
              )}
            </div>
          ))}

          <div className="flex items-center justify-between rounded-lg border border-border p-3">
            <div>
              <Label htmlFor="allow_registration">Allow registration</Label>
              <p className="text-xs text-muted-foreground">Turn off to lock new sign-ups platform-wide.</p>
            </div>
            <Switch
              id="allow_registration"
              checked={allowRegistration}
              onCheckedChange={(checked) => setValue("allow_registration", checked)}
            />
          </div>

          <Button type="submit" disabled={isSaving} className="self-start">
            {isSaving ? "Saving…" : "Save changes"}
          </Button>
        </form>
      )}
    </div>
  );
}
