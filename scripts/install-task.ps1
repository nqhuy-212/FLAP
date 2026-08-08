<#
Đăng ký Task Scheduler chạy "FLAP Dashboard" tự khởi động + tự restart khi lỗi.
Không cần quyền Admin (CLAUDE.md mục 3) ở chế độ mặc định.

Mặc định: trigger "khi đăng nhập" (-AtLogOn), chạy dưới tài khoản hiện tại —
KHÔNG cần Admin, KHÔNG cần mật khẩu.

-RunWithoutLogon: thử kiểu "Run whether user is logged on or not" (task chạy
được cả khi chưa đăng nhập Windows). PLAN.md Bước 0 ghi rõ **CHƯA kiểm chứng**
tuỳ chọn này có bị domain policy chặn không — cần chạy PowerShell này thủ công
(không chạy được qua agent vì Get-Credential cần nhập tương tác), và có thể
vẫn cần quyền Admin tuỳ chính sách domain dù Register-ScheduledTask không luôn
đòi hỏi. Nếu bị chặn: dự phòng là để PC luôn đăng nhập sẵn, dùng trigger mặc
định -AtLogOn.
#>
param(
    [switch]$RunWithoutLogon
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$taskName = "FLAP Dashboard"
$pythonw = Join-Path $root "backend\.venv\Scripts\pythonw.exe"
$script = Join-Path $root "backend\run_server.py"
$workDir = Join-Path $root "backend"

if (-not (Test-Path $pythonw)) {
    throw "Khong tim thay $pythonw - kiem tra lai backend\.venv"
}

$action = New-ScheduledTaskAction -Execute $pythonw -Argument "`"$script`"" -WorkingDirectory $workDir
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable `
    -RestartCount 999 -RestartInterval (New-TimeSpan -Minutes 1) `
    -ExecutionTimeLimit ([TimeSpan]::Zero)

if ($RunWithoutLogon) {
    $trigger = New-ScheduledTaskTrigger -AtStartup
    $cred = Get-Credential -Message "Tai khoan chay '$taskName' khi chua dang nhap"
    $principal = New-ScheduledTaskPrincipal -UserId $cred.UserName -LogonType Password -RunLevel Limited
    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger `
        -Principal $principal -Settings $settings `
        -Password $cred.GetNetworkCredential().Password -Force
} else {
    $trigger = New-ScheduledTaskTrigger -AtLogOn
    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger `
        -Settings $settings -Force
}

Write-Host "Da dang ky task '$taskName'. Kiem tra: Get-ScheduledTask -TaskName '$taskName'"
Write-Host "Chay thu ngay: Start-ScheduledTask -TaskName '$taskName'"
