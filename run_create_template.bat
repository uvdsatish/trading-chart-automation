@echo off
echo Creating Excel Template for ChartList Batch Viewer...
echo.

REM Activate conda environment
call C:\Users\uvdsa\anaconda3\Scripts\activate.bat browser_automation

REM Install openpyxl if needed
pip install openpyxl > nul 2>&1

REM Create template
python create_excel_template.py

echo.
pause