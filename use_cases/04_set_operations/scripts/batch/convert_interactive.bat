@echo off
REM Interactive Format Converter
echo ========================================
echo FORMAT CONVERTER - INTERACTIVE MODE
echo ========================================
echo.
echo This tool converts between different list formats
echo.

REM Get input
echo Enter your input (file path or direct data):
set /p INPUT="Input: "
echo.

REM Choose output format
echo Choose output format:
echo   1. Columnar (one item per line)
echo   2. Comma-separated
echo   3. JSON array
echo   4. Custom delimiter
echo.
set /p FORMAT="Enter choice (1-4): "

REM Set format parameter
if "%FORMAT%"=="1" set TOFORMAT=columnar
if "%FORMAT%"=="2" set TOFORMAT=comma
if "%FORMAT%"=="3" set TOFORMAT=json
if "%FORMAT%"=="4" (
    set /p DELIM="Enter custom delimiter: "
    set TOFORMAT=delimiter
)

REM Ask about sorting
echo.
set /p SORT="Sort alphabetically? (y/n): "
if /i "%SORT%"=="y" (
    set SORTFLAG=--sort
) else (
    set SORTFLAG=
)

REM Get output destination
echo.
set /p OUTPUT="Output file (or press Enter for console): "

REM Execute conversion
echo.
echo Converting...
echo ------------

if "%OUTPUT%"=="" (
    REM Output to console
    if "%FORMAT%"=="4" (
        python ..\..\bin\set_operations.py --convert -a "%INPUT%" --to-format comma --output-delimiter "%DELIM%" %SORTFLAG%
    ) else (
        python ..\..\bin\set_operations.py --convert -a "%INPUT%" --to-format %TOFORMAT% %SORTFLAG%
    )
) else (
    REM Output to file
    if "%FORMAT%"=="4" (
        python ..\..\bin\set_operations.py --convert -a "%INPUT%" --to-format comma --output-delimiter "%DELIM%" %SORTFLAG% --output "%OUTPUT%"
    ) else (
        python ..\..\bin\set_operations.py --convert -a "%INPUT%" --to-format %TOFORMAT% %SORTFLAG% --output "%OUTPUT%"
    )
    echo.
    echo [SUCCESS] Conversion complete!
    echo [SUCCESS] Result saved to: %OUTPUT%
)

echo.
pause