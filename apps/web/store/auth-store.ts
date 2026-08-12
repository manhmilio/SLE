// apps/web/store/auth-store.ts
import { create } from "zustand";
import { persist } from "zustand/middleware";
import { setAccessToken, registerAuthExpiredHandler } from "@/lib/api-client";

export interface AuthUser {
  id: string;
  email: string;
  display_name: string;
  avatar_url: string | null;
  role: string;
  is_active: boolean;
  streak: number;
  last_studied: string | null;
  created_at: string;
}

interface AuthState {
  user: AuthUser | null;
  accessToken: string | null;
  isAuthenticated: boolean;
  /** true cho tới khi rehydrate từ localStorage xong — dùng để tránh flash UI sai trạng thái */
  hasHydrated: boolean;

  setAuth: (user: AuthUser, accessToken: string) => void;
  setAccessTokenOnly: (accessToken: string) => void;
  clearAuth: () => void;
  setHasHydrated: (value: boolean) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      accessToken: null,
      isAuthenticated: false,
      hasHydrated: false,

      setAuth: (user, accessToken) => {
        setAccessToken(accessToken); // đồng bộ sang api-client
        set({ user, accessToken, isAuthenticated: true });
      },

      setAccessTokenOnly: (accessToken) => {
        // Dùng khi interceptor tự refresh xong, không có user mới để cập nhật
        setAccessToken(accessToken);
        set({ accessToken });
      },

      clearAuth: () => {
        setAccessToken(null);
        set({ user: null, accessToken: null, isAuthenticated: false });
      },

      setHasHydrated: (value) => set({ hasHydrated: value }),
    }),
    {
      name: "soulee-auth",
      onRehydrateStorage: () => (state) => {
        // Sau khi Zustand đọc xong localStorage, đồng bộ accessToken sang api-client
        if (state?.accessToken) {
          setAccessToken(state.accessToken);
        }
        state?.setHasHydrated(true);
      },
      partialize: (state) => ({
        user: state.user,
        accessToken: state.accessToken,
        isAuthenticated: state.isAuthenticated,
        // hasHydrated KHÔNG persist — luôn phải bắt đầu false mỗi lần load trang
      }),
    }
  )
);

// Đăng ký handler: khi api-client refresh thất bại hẳn (refresh cookie hết hạn/invalid)
// → tự động clear auth state để UI redirect về /login qua protected route middleware (9.2)
registerAuthExpiredHandler(() => {
  useAuthStore.getState().clearAuth();
});