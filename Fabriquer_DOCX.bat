@echo off
setlocal
cd /d "%~dp0"

rem === Chemins (modifiables) ===
set DOCX=document.docx
set IMAGES=output\mon_pdf

if not exist ".venv\Scripts\python.exe" (
    echo .venv absent. Lancez d'abord setup.bat
    pause
    exit /b 1
)

if "%DOCX%"=="" (
    echo Variable DOCX non definie. Editez Fabriquer_DOCX.bat
    pause
    exit /b 1
)

if "%IMAGES%"=="" (
    echo Variable IMAGES non definie. Editez Fabriquer_DOCX.bat
    pause
    exit /b 1
)

echo Insertion des images de "%IMAGES%" dans "%DOCX%" ...
".venv\Scripts\python.exe" insert_docx.py "%DOCX%" "%IMAGES%"
set ERR=%ERRORLEVEL%

echo.
if not "%ERR%"=="0" (
    echo Echec de l'insertion ^(code %ERR%^). Voir le detail ci-dessus.
) else (
    echo Termine. Fichier ecrase: %DOCX%
)
pause
exit /b %ERR%
