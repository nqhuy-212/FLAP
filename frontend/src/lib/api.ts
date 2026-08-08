import type { HealthResponse, SystemStatus, WipKpi, WipSummary, WipTrolley } from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "";
const BASE_PATH = process.env.NEXT_PUBLIC_BASE_PATH ?? "";

/**
 * Ghép URL gọi API. Production (static export nhúng vào FastAPI): API_BASE_URL
 * rỗng, gọi cùng origin. Dev (`next dev` chạy port riêng): API_BASE_URL trỏ
 * sang backend dev server — xem frontend/.env.example.
 */
export function apiUrl(path: string): string {
  return `${API_BASE_URL}${BASE_PATH}${path}`;
}

async function getJson<T>(path: string): Promise<T> {
  const res = await fetch(apiUrl(path));
  if (!res.ok) {
    throw new Error(`API ${path} trả lỗi ${res.status}`);
  }
  return res.json() as Promise<T>;
}

export function getWipDetail(): Promise<WipTrolley[]> {
  return getJson<WipTrolley[]>("/api/wip/detail");
}

export function getWipSummary(): Promise<WipSummary[]> {
  return getJson<WipSummary[]>("/api/wip/summary");
}

export function getWipKpi(): Promise<WipKpi> {
  return getJson<WipKpi>("/api/wip/kpi");
}

export function getHealth(): Promise<HealthResponse> {
  return getJson<HealthResponse>("/api/meta/health");
}

/** 403 = token sai, 503 = FLAP_SYSTEM_TOKEN chưa cấu hình ở backend — phân biệt để hiện đúng thông báo. */
export async function getSystemStatus(token: string): Promise<SystemStatus> {
  const res = await fetch(apiUrl(`/api/system/status?token=${encodeURIComponent(token)}`));
  if (res.status === 403) throw new Error("invalid_token");
  if (res.status === 503) throw new Error("token_not_configured");
  if (!res.ok) throw new Error(`API /api/system/status trả lỗi ${res.status}`);
  return res.json() as Promise<SystemStatus>;
}
