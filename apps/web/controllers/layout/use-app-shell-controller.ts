"use client";

import { useRouter } from "next/navigation";
import { useAuthStore } from "@/store/auth-store";
import { useLogoutMutation } from "@/lib/mutations/auth-mutations";

/** Orchestrates the data the AppShell (Sidebar/Topbar) needs — Views stay pure. */
export function useAppShellController() {
  const router = useRouter();
  const user = useAuthStore((s) => s.user);
  const { mutate: logoutMutate, isPending: isLoggingOut } = useLogoutMutation();

  function logout() {
    logoutMutate(undefined, {
      onSuccess: () => router.push("/login"),
    });
  }

  return {
    user,
    isAdmin: user?.role === "admin",
    logout,
    isLoggingOut,
  };
}
