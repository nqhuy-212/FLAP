import type { NextConfig } from "next";
import { existsSync, readFileSync } from "node:fs";
import path from "node:path";

/**
 * Đọc FLAP_BASE_PATH trực tiếp từ .env ở gốc dự án (không phải frontend/.env)
 * để backend và frontend luôn dùng chung một giá trị — tránh lệch cấu hình
 * khi nhiều dashboard sau này chạy chung 1 port qua reverse proxy (CLAUDE.md mục 10).
 */
function readRootEnvVar(key: string): string | undefined {
  const rootEnvPath = path.resolve(__dirname, "..", ".env");
  if (!existsSync(rootEnvPath)) return undefined;
  for (const line of readFileSync(rootEnvPath, "utf-8").split("\n")) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#")) continue;
    const eq = trimmed.indexOf("=");
    if (eq === -1) continue;
    if (trimmed.slice(0, eq).trim() === key) return trimmed.slice(eq + 1).trim();
  }
  return undefined;
}

const basePath = readRootEnvVar("FLAP_BASE_PATH") || "";

const nextConfig: NextConfig = {
  output: "export",
  // Bắt buộc với static export — không có server Next.js nào để tự optimize ảnh lúc chạy.
  images: { unoptimized: true },
  // Xuất mỗi route thành thư mục + index.html (vd out/tv/wip/index.html) thay
  // vì file .html rời (out/tv/wip.html) — khớp cách FastAPI StaticFiles(html=True)
  // tự tìm index.html khi request khớp một thư mục (Bước 7).
  trailingSlash: true,
  ...(basePath ? { basePath, assetPrefix: basePath } : {}),
  env: {
    NEXT_PUBLIC_BASE_PATH: basePath,
  },
};

export default nextConfig;
