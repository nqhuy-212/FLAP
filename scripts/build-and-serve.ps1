# Build frontend tĩnh (next build, output:'export') rồi chạy backend production
# (uvicorn, reload=False, 1 worker) TRONG cửa sổ này — dùng để kiểm tra thủ công
# trước khi giao cho Task Scheduler chạy bằng pythonw (scripts/start.cmd).
# Ctrl+C để dừng.
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$nodeDir = "D:\2025 nqhuy\Setup\node-v24.11.0-win-x64"
$env:Path = "$nodeDir;$env:Path"
$python = Join-Path $root "backend\.venv\Scripts\python.exe"

Write-Host "== Build frontend (next build) ==" -ForegroundColor Cyan
Set-Location (Join-Path $root "frontend")
& "$nodeDir\npm.cmd" run build
if (-not $?) { throw "next build thất bại" }

# Next.js (trailingSlash:true) xuất trang 404 thành out/404/index.html, nhưng
# Starlette StaticFiles(html=True) chỉ tự tìm "404.html" PHẲNG ở gốc thư mục
# (xem starlette/staticfiles.py: lookup_path(self, "404.html")) — không tìm
# theo thư mục như các route khác. Copy thủ công để trang 404 hiển thị đúng
# thay vì rơi về JSON mặc định của FastAPI.
Copy-Item (Join-Path $root "frontend\out\404\index.html") (Join-Path $root "frontend\out\404.html") -Force

Write-Host "== Chạy backend production (Ctrl+C để dừng) ==" -ForegroundColor Cyan
Set-Location (Join-Path $root "backend")
& $python run_server.py
