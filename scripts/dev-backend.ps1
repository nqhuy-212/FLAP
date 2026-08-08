# Chạy backend ở chế độ dev (reload=True, xem log ngay trên console).
# Python không nằm trong PATH (CLAUDE.md mục 3) — luôn gọi thẳng venv.
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$python = Join-Path $root "backend\.venv\Scripts\python.exe"

Set-Location (Join-Path $root "backend")
& $python -m app.main
