@echo off
:: Complete Admin Launcher for Browser Automation Development
:: This script launches both VS Code and runs the browser automation with admin privileges

title Browser Automation - Complete Admin Launcher
color 0A

:: Check for admin privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo.
    echo =====================================================
    echo  Requesting Administrator Privileges...
    echo =====================================================
    echo.
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

:: We have admin privileges
cls
echo.
echo ======================================================================
echo  BROWSER AUTOMATION PROJECT - ADMIN MODE
echo ======================================================================
echo.
echo [STATUS] Running with Administrator privileges
echo [PROJECT] POC Browser Automation
echo [PATH] %~dp0
echo.

:: Change to project directory
cd /d "%~dp0"

:: Show menu
:menu
echo Please select an option:
echo.
echo   1. Launch VS Code (Admin) for development
echo   2. Run Multi-Timeframe Viewer (BTSG ticker)
echo   3. Run Multi-Timeframe Viewer (custom ticker)
echo   4. Run AI Analysis mode
echo   5. Launch VS Code AND run viewer (BTSG)
echo   6. Open project documentation
echo   7. Exit
echo.
set /p choice="Enter your choice (1-7): "

if "%choice%"=="1" goto launch_vscode
if "%choice%"=="2" goto run_viewer_btsg
if "%choice%"=="3" goto run_viewer_custom
if "%choice%"=="4" goto run_analysis
if "%choice%"=="5" goto launch_both
if "%choice%"=="6" goto open_docs
if "%choice%"=="7" goto end

echo Invalid choice. Please try again.
pause
cls
goto menu

:launch_vscode
echo.
echo Launching VS Code with admin privileges...
if exist "%LocalAppData%\Programs\Microsoft VS Code\Code.exe" (
    start "" "%LocalAppData%\Programs\Microsoft VS Code\Code.exe" "%~dp0"
) else (
    start "" code "%~dp0"
)
echo VS Code launched! Look for [Administrator] in title bar.
pause
cls
goto menu

:run_viewer_btsg
echo.
echo Starting Multi-Timeframe Viewer for BTSG...
echo.
call C:\Users\uvdsa\anaconda3\Scripts\activate.bat browser_automation
python main.py --mode viewer --ticker BTSG
pause
cls
goto menu

:run_viewer_custom
echo.
set /p ticker="Enter ticker symbol: "
echo.
echo Starting Multi-Timeframe Viewer for %ticker%...
echo.
call C:\Users\uvdsa\anaconda3\Scripts\activate.bat browser_automation
python main.py --mode viewer --ticker %ticker%
pause
cls
goto menu

:run_analysis
echo.
set /p ticker="Enter ticker symbol for AI analysis: "
echo.
echo Starting AI Analysis for %ticker%...
echo.
call C:\Users\uvdsa\anaconda3\Scripts\activate.bat browser_automation
python main.py --mode analysis --ticker %ticker%
pause
cls
goto menu

:launch_both
echo.
echo Launching VS Code...
if exist "%LocalAppData%\Programs\Microsoft VS Code\Code.exe" (
    start "" "%LocalAppData%\Programs\Microsoft VS Code\Code.exe" "%~dp0"
) else (
    start "" code "%~dp0"
)
echo.
echo Waiting 3 seconds before starting viewer...
timeout /t 3 /nobreak >nul
echo.
echo Starting Multi-Timeframe Viewer for BTSG...
call C:\Users\uvdsa\anaconda3\Scripts\activate.bat browser_automation
python main.py --mode viewer --ticker BTSG
pause
cls
goto menu

:open_docs
echo.
echo Opening project documentation...
if exist "README.md" (
    start "" "README.md"
)
if exist "CLAUDE.md" (
    start "" "CLAUDE.md"
)
echo Documentation opened in default editor.
pause
cls
goto menu

:end
echo.
echo ======================================================================
echo  Goodbye! Remember to run with admin for fullscreen to work.
echo ======================================================================
echo.
timeout /t 3 /nobreak >nul
exit