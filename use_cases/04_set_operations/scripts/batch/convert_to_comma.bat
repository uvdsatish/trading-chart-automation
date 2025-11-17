@echo off
REM Convert columnar list to comma-separated format
echo ========================================
echo CONVERT TO COMMA-SEPARATED FORMAT
echo ========================================
echo.

if "%1"=="" goto interactive

REM Command line mode
if "%2"=="" (
    REM Output to console
    python ..\..\bin\set_operations.py --convert -a "%1" --to-format comma --sort
) else (
    REM Output to file
    python ..\..\bin\set_operations.py --convert -a "%1" --to-format comma --sort --output "%2"
    echo.
    echo [SUCCESS] Converted to comma-separated format: %2
)
goto end

:interactive
REM Interactive mode
set /p INPUT="Enter input file (columnar format): "
echo.
set /p OUTPUT="Enter output file (or press Enter for console): "

if "%OUTPUT%"=="" (
    echo.
    echo Comma-separated result:
    echo -----------------------
    python ..\..\bin\set_operations.py --convert -a "%INPUT%" --to-format comma --sort
) else (
    python ..\..\bin\set_operations.py --convert -a "%INPUT%" --to-format comma --sort --output "%OUTPUT%"
    echo.
    echo [SUCCESS] Saved to %OUTPUT%
)

:end
echo.
pause