@echo off
REM Convert comma-separated list to columnar format
echo ========================================
echo CONVERT TO COLUMNAR FORMAT
echo ========================================
echo.

if "%1"=="" goto interactive

REM Command line mode
if "%2"=="" (
    REM Output to console
    python ..\..\bin\set_operations.py --convert -a "%1" --to-format columnar --sort
) else (
    REM Output to file
    python ..\..\bin\set_operations.py --convert -a "%1" --to-format columnar --sort --output "%2"
    echo.
    echo [SUCCESS] Converted to columnar format: %2
)
goto end

:interactive
REM Interactive mode
echo Enter comma-separated input (file or direct text):
set /p INPUT="Input: "
echo.
set /p OUTPUT="Enter output file (or press Enter for console): "

if "%OUTPUT%"=="" (
    echo.
    echo Columnar result:
    echo ----------------
    python ..\..\bin\set_operations.py --convert -a "%INPUT%" --to-format columnar --sort
) else (
    python ..\..\bin\set_operations.py --convert -a "%INPUT%" --to-format columnar --sort --output "%OUTPUT%"
    echo.
    echo [SUCCESS] Saved to %OUTPUT%
)

:end
echo.
pause