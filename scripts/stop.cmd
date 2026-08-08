@echo off
rem Dừng FLAP Dashboard đang chạy ngầm — đọc PID từ logs\flap.pid (ghi bởi
rem run_server.py lúc khởi động, vì pythonw không có cửa sổ để Ctrl+C).
setlocal
for %%I in ("%~dp0..") do set "ROOT=%%~fI"
set "PIDFILE=%ROOT%\logs\flap.pid"

if not exist "%PIDFILE%" (
    echo Khong tim thay %PIDFILE% - co the FLAP Dashboard chua chay.
    exit /b 1
)

set /p FLAP_PID=<"%PIDFILE%"
taskkill /PID %FLAP_PID% /T /F
del "%PIDFILE%"
endlocal
