// apps/web/lib/mutations/auth-mutations.ts
import { useMutation } from "@tanstack/react-query";
import type { components } from "@repo/types";
import { apiClient } from "@/lib/api-client";
import { useAuthStore } from "@/store/auth-store";

type LoginRequest = components["schemas"]["LoginRequest"];
type RegisterRequest = components["schemas"]["RegisterRequest"];
type SuccessEnvelopeLogin = components["schemas"]["SuccessEnvelope_LoginResponse_"];
type SuccessEnvelopeRegister = components["schemas"]["SuccessEnvelope_RegisterResponse_"];

// ---------------------------------------------------------------------------
// POST /auth/login
// ---------------------------------------------------------------------------
async function loginRequest(body: LoginRequest): Promise<SuccessEnvelopeLogin> {
  const { data } = await apiClient.post<SuccessEnvelopeLogin>("/auth/login", body);
  return data;
}

export function useLoginMutation() {
  const setAuth = useAuthStore((s) => s.setAuth);

  return useMutation({
    mutationFn: loginRequest,
    onSuccess: (response) => {
      const { user, tokens } = response.data;
      setAuth(user, tokens.access_token);
    },
  });
}

// ---------------------------------------------------------------------------
// POST /auth/register
// ---------------------------------------------------------------------------
async function registerRequest(body: RegisterRequest): Promise<SuccessEnvelopeRegister> {
  const { data } = await apiClient.post<SuccessEnvelopeRegister>("/auth/register", body);
  return data;
}

export function useRegisterMutation() {
  const setAuth = useAuthStore((s) => s.setAuth);

  return useMutation({
    mutationFn: registerRequest,
    onSuccess: (response) => {
      const { user, tokens } = response.data;
      setAuth(user, tokens.access_token);
    },
  });
}

// ---------------------------------------------------------------------------
// POST /auth/logout
// ---------------------------------------------------------------------------
async function logoutRequest(): Promise<void> {
  await apiClient.post("/auth/logout");
}

export function useLogoutMutation() {
  const clearAuth = useAuthStore((s) => s.clearAuth);

  return useMutation({
    mutationFn: logoutRequest,
    onSuccess: () => clearAuth(),
    onError: () => clearAuth(), // dù BE lỗi vẫn dọn state FE, tránh kẹt trạng thái đăng nhập ảo
  });
}