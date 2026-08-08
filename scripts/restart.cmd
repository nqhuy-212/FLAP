@echo off
rem Dừng rồi khởi động lại FLAP Dashboard.
call "%~dp0stop.cmd"
timeout /t 2 /nobreak >nul
call "%~dp0start.cmd"
