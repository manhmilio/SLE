"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/store/auth-store";

/**
 * The refresh-token cookie is httpOnly and scoped to the API's own origin
 * (see apps/api/app/routers/auth.py — path=/api/v1/auth, different port in dev),
 * so a same-origin Next.js middleware can never see it. The auth check has to
 * happen client-side, after the Zustand auth store rehydrates from storage.
 */
export function useProtectedRoute() {
  const router = useRouter();
  const hasHydrated = useAuthStore((s) => s.hasHydrated);
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);

  useEffect(() => {
    if (hasHydrated && !isAuthenticated) {
      router.replace("/login");
    }
  }, [hasHydrated, isAuthenticated, router]);

  return { isReady: hasHydrated && isAuthenticated };
}

/** Opposite guard for auth pages — bounce an already-logged-in user to the dashboard. */
export function useGuestRoute() {
  const router = useRouter();
  const hasHydrated = useAuthStore((s) => s.hasHydrated);
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);

  useEffect(() => {
    if (hasHydrated && isAuthenticated) {
      router.replace("/dashboard");
    }
  }, [hasHydrated, isAuthenticated, router]);
}
