"use client";

import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { toast } from "sonner";
import { loginSchema, type LoginFormValues } from "@/lib/validations/auth.schema";
import { useLoginMutation } from "@/lib/mutations/auth-mutations";
import { extractApiErrorMessage } from "@/lib/api/errors";

export function useLoginController() {
  const router = useRouter();
  const form = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: { email: "", password: "" },
  });
  const { mutate, isPending } = useLoginMutation();

  const onSubmit = form.handleSubmit((values) => {
    mutate(values, {
      onSuccess: () => {
        toast.success("Welcome back.");
        router.push("/dashboard");
      },
      onError: (error) => {
        toast.error(extractApiErrorMessage(error, "Email or password is incorrect."));
      },
    });
  });

  return { form, onSubmit, isPending };
}
