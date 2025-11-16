@echo off
REM Find tickers that appear in BOTH List A and List B
echo ========================================
echo TICKER INTERSECTION TOOL (A & B)
echo Find tickers in BOTH A and B
echo ========================================
echo.

if "%1"=="" goto interactive
if "%2"=="" goto interactive

REM Command line mode
python ..\..\bin\set_operations.py -a "%1" -b "%2" --operation "A&B" --sort
goto end

:interactive
REM Interactive mode
set /p LISTA="Enter path to List A: "
set /p LISTB="Enter path to List B: "
echo.
set /p OUTPUT="Enter output file name (or press Enter for console): "

if "%OUTPUT%"=="" (
    echo.
    echo Common tickers:
    echo ---------------
    python ..\..\bin\set_operations.py -a "%LISTA%" -b "%LISTB%" --operation "A&B" --sort
) else (
    python ..\..\bin\set_operations.py -a "%LISTA%" -b "%LISTB%" --operation "A&B" --sort --output "%OUTPUT%"
    echo.
    echo [SUCCESS] Results saved to %OUTPUT%
)

:end
echo.
pause