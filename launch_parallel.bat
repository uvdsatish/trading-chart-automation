@echo off
REM Parallel Launcher for Use Cases #2 and #3
REM This batch file launches both use cases in parallel with split-screen browsers

echo ======================================================================
echo PARALLEL CHARTLIST LAUNCHER
echo ======================================================================
echo [USE CASE #2] ChartList Batch Viewer
echo [USE CASE #3] ChartList Viewer
echo ======================================================================
echo.

REM Set the Python executable from conda environment
set PYTHON_EXE=C:\Users\uvdsa\.conda\envs\browser_automation\python.exe

REM Check if Python exists
if not exist "%PYTHON_EXE%" (
    echo [ERROR] Python executable not found at: %PYTHON_EXE%
    echo Please ensure the browser_automation conda environment is installed
    pause
    exit /b 1
)

REM Default config files - Using S1 configs
set BATCH_CONFIG=config\chartlist_config_S1.xlsx
set VIEWER_CONFIG=config\justChartlist-S1-daily.xlsx

REM Check if user wants to use custom config files
echo Current configuration:
echo   Batch Config:  %BATCH_CONFIG%
echo   Viewer Config: %VIEWER_CONFIG%
echo.
echo Press Enter to use these configs, or type 'custom' to specify different files:
set /p USER_CHOICE=

if /i "%USER_CHOICE%"=="custom" (
    echo.
    set /p BATCH_CONFIG=Enter path to ChartList Batch config file:
    set /p VIEWER_CONFIG=Enter path to ChartList Viewer config file:
)

REM Check if config files exist
if not exist "%BATCH_CONFIG%" (
    echo [ERROR] Batch config file not found: %BATCH_CONFIG%
    pause
    exit /b 1
)

if not exist "%VIEWER_CONFIG%" (
    echo [ERROR] Viewer config file not found: %VIEWER_CONFIG%
    pause
    exit /b 1
)

echo.
echo Starting parallel execution...
echo ======================================================================
echo.

REM Run the parallel launcher
"%PYTHON_EXE%" main.py --mode parallel --batch-config "%BATCH_CONFIG%" --viewer-config "%VIEWER_CONFIG%"

echo.
echo ======================================================================
echo Parallel execution complete!
echo ======================================================================
pause