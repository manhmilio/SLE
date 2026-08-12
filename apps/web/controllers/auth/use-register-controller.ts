"use client";

import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { toast } from "sonner";
import { registerSchema, type RegisterFormValues } from "@/lib/validations/auth.schema";
import { useRegisterMutation } from "@/lib/mutations/auth-mutations";
import { extractApiErrorMessage } from "@/lib/api/errors";

export function useRegisterController() {
  const router = useRouter();
  const form = useForm<RegisterFormValues>({
    resolver: zodResolver(registerSchema),
    defaultValues: { email: "", display_name: "", password: "", confirmPassword: "" },
  });
  const { mutate, isPending } = useRegisterMutation();

  const onSubmit = form.handleSubmit(({ confirmPassword, ...values }) => {
    void confirmPassword;
    mutate(values, {
      onSuccess: () => {
        toast.success("Welcome to Soulee — your first seed is planted.");
        router.push("/dashboard");
      },
      onError: (error) => {
        toast.error(extractApiErrorMessage(error, "Couldn't create your account."));
      },
    });
  });

  return { form, onSubmit, isPending };
}
