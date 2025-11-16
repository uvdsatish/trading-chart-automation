@echo off
REM Run all Set Operations demonstrations

echo ========================================
echo RUNNING ALL SET OPERATIONS DEMOS
echo ========================================
echo.

REM Navigate to demos directory
cd /d "%~dp0"

echo [1/2] Running General Demonstrations...
echo ----------------------------------------
"C:\Users\uvdsa\.conda\envs\browser_automation\python.exe" demo_set_operations.py

echo.
echo.
echo [2/2] Running Ticker Examples...
echo ----------------------------------------
"C:\Users\uvdsa\.conda\envs\browser_automation\python.exe" ticker_examples.py

echo.
echo ========================================
echo ALL DEMOS COMPLETE!
echo ========================================
pause