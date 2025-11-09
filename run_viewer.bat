@echo off
echo Starting Multi-Timeframe Viewer with Enhanced Fullscreen...
echo.

REM Activate conda environment and run the script
call C:\Users\uvdsa\anaconda3\Scripts\activate.bat browser_automation
python main.py --mode viewer --ticker BTSG

echo.
echo Browser closed.
pause