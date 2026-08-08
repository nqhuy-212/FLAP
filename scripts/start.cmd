@echo off
rem Khởi động FLAP Dashboard ngầm bằng pythonw — không cửa sổ console.
rem Dùng bởi Task Scheduler (scripts/install-task.ps1) hoặc bấm đúp thủ công.
setlocal
for %%I in ("%~dp0..") do set "ROOT=%%~fI"
set "PYTHONW=%ROOT%\backend\.venv\Scripts\pythonw.exe"
set "SCRIPT=%ROOT%\backend\run_server.py"

if not exist "%PYTHONW%" (
    echo Khong tim thay %PYTHONW% - kiem tra lai backend\.venv
    exit /b 1
)

start "" "%PYTHONW%" "%SCRIPT%"
endlocal
