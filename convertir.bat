@echo off
setlocal
cd /d "%~dp0"

rem === Options de conversion (modifiables) ===
set DPI=200
set PADDING=70
set QUALITY=90
set THRESHOLD=245
set TOLERANCE=100
set HEIGHT=890

if not exist ".venv\Scripts\python.exe" (
    echo .venv absent. Lancez d'abord setup.bat
    pause
    exit /b 1
)

if not exist "input" mkdir input
if not exist "output" mkdir output

set HEIGHT_ARGS=
if defined HEIGHT if not "%HEIGHT%"=="0" set HEIGHT_ARGS=--height %HEIGHT%

echo Conversion de tous les PDF dans input\ ...
echo Options: dpi=%DPI% padding=%PADDING% quality=%QUALITY% threshold=%THRESHOLD% tolerance=%TOLERANCE% height=%HEIGHT%
".venv\Scripts\python.exe" convert.py input -o output --dpi %DPI% --padding %PADDING% --quality %QUALITY% --threshold %THRESHOLD% --tolerance %TOLERANCE% %HEIGHT_ARGS%
set ERR=%ERRORLEVEL%

echo.
if not "%ERR%"=="0" (
    echo Echec de la conversion ^(code %ERR%^). Voir le detail ci-dessus.
) else (
    echo Termine. JPEG dans output\^(un dossier par PDF^)
)
pause
exit /b %ERR%
