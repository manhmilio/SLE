"use client";

import { useEffect } from "react";
import { toast } from "sonner";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useSystemConfigQuery } from "@/lib/queries/use-system-config-query";
import { useUpdateSystemConfigMutation } from "@/lib/mutations/admin-mutations";
import { systemConfigSchema, type SystemConfigFormValues } from "@/lib/validations/admin-config.schema";
import { extractApiErrorMessage } from "@/lib/api/errors";

export function useAdminConfigController() {
  const query = useSystemConfigQuery();
  const updateMutation = useUpdateSystemConfigMutation();

  const form = useForm<SystemConfigFormValues>({
    resolver: zodResolver(systemConfigSchema),
  });

  useEffect(() => {
    if (query.data) {
      form.reset({
        initial_ease_factor: query.data.initial_ease_factor,
        min_ease_factor: query.data.min_ease_factor,
        known_threshold_days: query.data.known_threshold_days,
        max_sets_per_user: query.data.max_sets_per_user,
        max_cards_per_set: query.data.max_cards_per_set,
        max_image_size_mb: query.data.max_image_size_mb,
        allow_registration: query.data.allow_registration,
      });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [query.data]);

  const onSubmit = form.handleSubmit((values) => {
    updateMutation.mutate(values, {
      onSuccess: () => toast.success("Config updated."),
      onError: (error) => toast.error(extractApiErrorMessage(error, "Couldn't update the config.")),
    });
  });

  return {
    isLoading: query.isLoading,
    form,
    onSubmit,
    isSaving: updateMutation.isPending,
  };
}
