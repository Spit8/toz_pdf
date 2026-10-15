@echo off
setlocal
cd /d "%~dp0"

if not exist "output" (
    echo Le dossier output\ n'existe pas. Rien a supprimer.
    pause
    exit /b 0
)

echo Suppression du contenu de output\ ...
rd /s /q "output"
mkdir "output"
type nul > "output\.gitkeep"

echo Termine. output\ est vide.
pause
endlocal
