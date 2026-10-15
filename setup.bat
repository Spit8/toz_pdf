@echo off
setlocal
cd /d "%~dp0"

where python >nul 2>&1
if errorlevel 1 (
    echo Python introuvable. Installez Python 3.10+ et cochez "Add to PATH".
    exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
    echo Creation de .venv ...
    python -m venv .venv
    if errorlevel 1 exit /b 1
)

echo Installation des dependances ...
".venv\Scripts\python.exe" -m pip install --upgrade pip
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 exit /b 1

echo.
echo Pret. Lancez: run.bat
endlocal
