@echo off
:: VS Code Admin Launcher for Browser Automation Project
:: This script launches VS Code with administrator privileges for the POC Browser Automation project

:: Set title and color
title VS Code Admin Launcher - Browser Automation
color 0A

:: Check for admin privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo.
    echo =====================================================
    echo  Requesting Administrator Privileges...
    echo =====================================================
    echo.
    echo You will see a UAC prompt - please click "Yes"
    echo.

    :: Re-launch this script with admin privileges
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

:: We have admin privileges, proceed with launching VS Code
echo.
echo =====================================================
echo  [ADMIN MODE ACTIVE] Launching VS Code...
echo =====================================================
echo.
echo Project: POC Browser Automation
echo Path: %~dp0
echo Status: Running with Administrator privileges
echo.

:: Change to project directory
cd /d "%~dp0"

:: Launch VS Code with this project folder
:: Try multiple possible VS Code locations
if exist "%LocalAppData%\Programs\Microsoft VS Code\Code.exe" (
    echo Starting VS Code from user installation...
    start "" "%LocalAppData%\Programs\Microsoft VS Code\Code.exe" "%~dp0"
) else if exist "%ProgramFiles%\Microsoft VS Code\Code.exe" (
    echo Starting VS Code from system installation...
    start "" "%ProgramFiles%\Microsoft VS Code\Code.exe" "%~dp0"
) else if exist "%ProgramFiles(x86)%\Microsoft VS Code\Code.exe" (
    echo Starting VS Code from x86 installation...
    start "" "%ProgramFiles(x86)%\Microsoft VS Code\Code.exe" "%~dp0"
) else (
    :: Try using the 'code' command if it's in PATH
    echo Trying to start VS Code using PATH...
    start "" code "%~dp0"
)

echo.
echo =====================================================
echo  VS Code launched successfully!
echo =====================================================
echo.
echo IMPORTANT NOTES:
echo - VS Code is running with Administrator privileges
echo - Terminal sessions in VS Code will have admin rights
echo - The browser automation will work with fullscreen
echo - Look for "[Administrator]" in VS Code title bar
echo.
echo You can close this window now.
echo.

:: Keep window open for 5 seconds so user can read the message
timeout /t 5 /nobreak >nul
exit