@echo off
REM Find tickers in List A that are NOT in List B
echo ========================================
echo TICKER DIFFERENCE TOOL (A - B)
echo Find tickers in A that are NOT in B
echo ========================================
echo.

if "%1"=="" goto interactive
if "%2"=="" goto interactive

REM Command line mode
python ..\..\bin\set_operations.py -a "%1" -b "%2" --operation "A-B" --sort
goto end

:interactive
REM Interactive mode
set /p LISTA="Enter path to List A (base list): "
set /p LISTB="Enter path to List B (subtract list): "
echo.
set /p OUTPUT="Enter output file name (or press Enter for console): "

if "%OUTPUT%"=="" (
    echo.
    echo Results:
    echo --------
    python ..\..\bin\set_operations.py -a "%LISTA%" -b "%LISTB%" --operation "A-B" --sort
) else (
    python ..\..\bin\set_operations.py -a "%LISTA%" -b "%LISTB%" --operation "A-B" --sort --output "%OUTPUT%"
    echo.
    echo [SUCCESS] Results saved to %OUTPUT%
)

:end
echo.
pause