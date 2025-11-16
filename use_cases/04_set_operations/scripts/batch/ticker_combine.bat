@echo off
REM Combine multiple ticker lists (A + B + C)
echo ========================================
echo TICKER COMBINE TOOL (A + B + C)
echo Combine multiple ticker lists
echo ========================================
echo.

set /p LISTA="Enter path to List A: "
set /p LISTB="Enter path to List B (or press Enter to skip): "
set /p LISTC="Enter path to List C (or press Enter to skip): "
echo.
set /p OUTPUT="Enter output file name (or press Enter for console): "

REM Build the command based on provided lists
set CMD=python ..\..\bin\set_operations.py -a "%LISTA%"
set OP=A

if not "%LISTB%"=="" (
    set CMD=%CMD% -b "%LISTB%"
    set OP=%OP%+B
)

if not "%LISTC%"=="" (
    set CMD=%CMD% -c "%LISTC%"
    set OP=%OP%+C
)

set CMD=%CMD% --operation "%OP%" --sort

if "%OUTPUT%"=="" (
    echo.
    echo Combined list:
    echo --------------
    %CMD%
) else (
    %CMD% --output "%OUTPUT%"
    echo.
    echo [SUCCESS] Combined list saved to %OUTPUT%
)

echo.
pause