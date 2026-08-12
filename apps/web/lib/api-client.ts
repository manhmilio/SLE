// apps/web/lib/api-client.ts
import axios, {
  AxiosError,
  type AxiosRequestConfig,
  type InternalAxiosRequestConfig,
} from "axios";

// ---------------------------------------------------------------------------
// Access token holder (module-scope, KHÔNG lưu localStorage trực tiếp ở đây)
// Zustand auth store là nguồn sự thật cho persist; store sẽ gọi setAccessToken()
// mỗi khi token đổi (login/refresh/logout) để đồng bộ 2 chiều.
// ---------------------------------------------------------------------------
let accessToken: string | null = null;

export function setAccessToken(token: string | null): void {
  accessToken = token;
}

export function getAccessToken(): string | null {
  return accessToken;
}

// ---------------------------------------------------------------------------
// Axios instance
// ---------------------------------------------------------------------------
export const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1",
  withCredentials: true, // bắt buộc để trình duyệt gửi kèm cookie refresh_token httpOnly
});

apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`;
  }
  return config;
});

// ---------------------------------------------------------------------------
// Refresh queue — tránh gọi /auth/refresh nhiều lần song song khi nhiều
// request cùng 401 một lúc.
// ---------------------------------------------------------------------------
let isRefreshing = false;
let refreshWaiters: Array<(token: string | null) => void> = [];

function onRefreshed(token: string | null): void {
  refreshWaiters.forEach((cb) => cb(token));
  refreshWaiters = [];
}

/** Callback được gọi khi refresh thất bại hẳn (refresh token cũng hết hạn/invalid).
 *  Đăng ký từ auth store để trigger logout + redirect, tránh import store ở đây. */
let onAuthExpired: (() => void) | null = null;

export function registerAuthExpiredHandler(handler: () => void): void {
  onAuthExpired = handler;
}

interface RetriableConfig extends AxiosRequestConfig {
  _retry?: boolean;
}

apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as RetriableConfig | undefined;

    if (
      error.response?.status !== 401 ||
      !originalRequest ||
      originalRequest._retry ||
      originalRequest.url?.includes("/auth/refresh") ||
      originalRequest.url?.includes("/auth/login") ||
      originalRequest.url?.includes("/auth/register")
    ) {
      return Promise.reject(error);
    }

    originalRequest._retry = true;

    if (isRefreshing) {
      // Đã có 1 refresh đang chạy → xếp hàng chờ kết quả
      return new Promise((resolve, reject) => {
        refreshWaiters.push((newToken) => {
          if (!newToken) {
            reject(error);
            return;
          }
          originalRequest.headers = {
            ...originalRequest.headers,
            Authorization: `Bearer ${newToken}`,
          };
          resolve(apiClient(originalRequest));
        });
      });
    }

    isRefreshing = true;
    try {
      const { data } = await apiClient.post<{
        success: boolean;
        data: { tokens: { access_token: string; token_type: string; expires_in: number } };
      }>("/auth/refresh");

      const newToken = data.data.tokens.access_token;
      setAccessToken(newToken);
      onRefreshed(newToken);

      originalRequest.headers = {
        ...originalRequest.headers,
        Authorization: `Bearer ${newToken}`,
      };
      return apiClient(originalRequest);
    } catch (refreshError) {
      setAccessToken(null);
      onRefreshed(null);
      onAuthExpired?.();
      return Promise.reject(refreshError);
    } finally {
      isRefreshing = false;
    }
  }
);