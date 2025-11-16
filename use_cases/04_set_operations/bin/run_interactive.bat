@echo off
REM Quick launcher for Set Operations Interactive Mode
REM Automatically navigates to correct directory and runs utility

echo ========================================
echo SET OPERATIONS UTILITY - INTERACTIVE MODE
echo ========================================
echo.

REM Navigate to use case directory
cd /d "%~dp0\.."

REM Run interactive mode
"C:\Users\uvdsa\.conda\envs\browser_automation\python.exe" bin\set_operations.py

echo.
pause