<#
Mở inbound firewall TCP 8080 cho FLAP Dashboard — CẦN QUYỀN ADMIN.
PC chạy dashboard không có quyền Admin (CLAUDE.md mục 3) nên không tự chạy
được file này — đưa cho IT chạy một lần ("Run as Administrator").

Chỉ mở cho profile Domain/Private (mạng nhà máy), KHÔNG mở Public để tránh mở
cổng ra ngoài nếu máy từng đổi profile mạng.
#>
$ErrorActionPreference = "Stop"

$existing = Get-NetFirewallRule -DisplayName "FLAP Dashboard (TCP 8080)" -ErrorAction SilentlyContinue
if ($existing) {
    Write-Host "Rule 'FLAP Dashboard (TCP 8080)' da ton tai, khong tao lai."
} else {
    New-NetFirewallRule `
        -DisplayName "FLAP Dashboard (TCP 8080)" `
        -Direction Inbound `
        -Protocol TCP `
        -LocalPort 8080 `
        -Action Allow `
        -Profile Domain,Private

    Write-Host "Da mo inbound TCP 8080 (Domain/Private) cho FLAP Dashboard."
}
