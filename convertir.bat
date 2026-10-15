@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo .venv absent. Lancez d'abord setup.bat
    pause
    exit /b 1
)

if not exist "input" mkdir input
if not exist "output" mkdir output

echo Conversion de tous les PDF dans input\ ...
".venv\Scripts\python.exe" convert.py input -o output

echo.
if errorlevel 1 (
    echo Echec de la conversion.
) else (
    echo Termine. JPEG dans output\^(un dossier par PDF^)
)
pause
endlocal
