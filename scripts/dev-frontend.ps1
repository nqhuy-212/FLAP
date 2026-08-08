# Chạy `next dev` (port 3000, gọi sang backend port riêng qua NEXT_PUBLIC_API_BASE_URL
# trong frontend/.env.development.local — xem CLAUDE.md mục 3.3).
# Node không nằm trong PATH (CLAUDE.md mục 3) — thêm tạm vào Path của phiên này.
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$nodeDir = "D:\2025 nqhuy\Setup\node-v24.11.0-win-x64"
$env:Path = "$nodeDir;$env:Path"

Set-Location (Join-Path $root "frontend")
& "$nodeDir\npm.cmd" run dev
