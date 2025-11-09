@echo off
echo [INFO] Running ChartList Batch Viewer...
echo.

REM Use the browser_automation conda environment Python directly
"C:\Users\uvdsa\anaconda3\envs\browser_automation\python.exe" main.py --mode chartlist-batch --config config/chartlist_config_S1.xlsx

if errorlevel 1 (
    echo.
    echo [ERROR] Script failed with error code %errorlevel%
    pause
) else (
    echo.
    echo [SUCCESS] ChartList Batch Viewer completed
)