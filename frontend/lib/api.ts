"use client";

import { clearTokens, getAccessToken, saveTokens } from "@/lib/auth";
import type {
  DashboardSummary,
  EnvelopeExtractionResponse,
  Repair,
  RepairImage,
  RepairImageType,
  RepairListResponse,
  RepairPayload,
  RepairStatus,
  StatusCount,
  TokenResponse,
  User,
  WeeklyProfit
} from "@/types/api";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "/api/v1";

type RequestOptions = RequestInit & { auth?: boolean };

function formatApiError(detail: unknown): string {
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        if (typeof item === "string") return item;
        if (item && typeof item === "object" && "msg" in item) {
          const message = (item as { msg?: unknown }).msg;
          return typeof message === "string" ? message : JSON.stringify(item);
        }
        return JSON.stringify(item);
      })
      .join(" ");
  }
  if (detail && typeof detail === "object") {
    if ("message" in detail && typeof (detail as { message?: unknown }).message === "string") {
      return (detail as { message: string }).message;
    }
    return JSON.stringify(detail);
  }
  return "Request failed";
}

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const headers = new Headers(options.headers);
  if (!(options.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }
  if (options.auth !== false) {
    const token = getAccessToken();
    if (token) headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers
  });

  if (!response.ok) {
    const body = await response.json().catch(() => null);
    if (response.status === 401) {
      clearTokens();
      if (typeof window !== "undefined" && window.location.pathname !== "/login") {
        window.location.assign("/login");
      }
      throw new Error("Sesion expirada. Vuelve a iniciar sesion.");
    }
    throw new Error(formatApiError(body?.detail));
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

export async function login(email: string, password: string) {
  const tokens = await request<TokenResponse>("/auth/login", {
    method: "POST",
    auth: false,
    body: JSON.stringify({ email, password })
  });
  saveTokens(tokens.access_token, tokens.refresh_token);
  return tokens;
}

export function me() {
  return request<User>("/auth/me");
}

export function getDashboardSummary() {
  return request<DashboardSummary>("/dashboard/summary");
}

export function getRepairsByStatus() {
  return request<StatusCount[]>("/dashboard/repairs-by-status");
}

export function getProfitByWeek() {
  return request<WeeklyProfit[]>("/dashboard/profit-by-week");
}

export type RepairFilters = {
  search?: string;
  status?: RepairStatus | "";
  date_from?: string;
  date_to?: string;
  page?: number;
  page_size?: number;
};

export function listRepairs(filters: RepairFilters = {}) {
  const params = new URLSearchParams();
  Object.entries(filters).forEach(([key, value]) => {
    if (value) params.set(key, String(value));
  });
  const query = params.toString();
  return request<RepairListResponse>(`/repairs${query ? `?${query}` : ""}`);
}

export function getRepair(id: number) {
  return request<Repair>(`/repairs/${id}`);
}

export function createRepair(payload: RepairPayload) {
  return request<Repair>("/repairs", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function updateRepair(id: number, payload: Partial<RepairPayload>) {
  return request<Repair>(`/repairs/${id}`, {
    method: "PATCH",
    body: JSON.stringify(payload)
  });
}

export function deleteRepair(id: number) {
  return request<void>(`/repairs/${id}`, { method: "DELETE" });
}

export function uploadRepairImage(id: number, file: File, imageType: RepairImageType = "watch") {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("image_type", imageType);
  return request<RepairImage>(`/repairs/${id}/images`, {
    method: "POST",
    body: formData
  });
}

export function extractEnvelope(file: File) {
  const formData = new FormData();
  formData.append("file", file);
  return request<EnvelopeExtractionResponse>("/repairs/extract-envelope", {
    method: "POST",
    body: formData
  });
}

