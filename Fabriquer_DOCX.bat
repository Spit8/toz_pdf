@echo off
setlocal
cd /d "%~dp0"

rem === Chemins (modifiables) ===
set DOCX_DIR=input_docx
set IMAGES=output\mon_pdf

if not exist ".venv\Scripts\python.exe" (
    echo .venv absent. Lancez d'abord setup.bat
    pause
    exit /b 1
)

if not exist "input_docx" mkdir input_docx

if "%DOCX_DIR%"=="" (
    echo Variable DOCX_DIR non definie. Editez Fabriquer_DOCX.bat
    pause
    exit /b 1
)

if "%IMAGES%"=="" (
    echo Variable IMAGES non definie. Editez Fabriquer_DOCX.bat
    pause
    exit /b 1
)

echo Insertion des images de "%IMAGES%" a partir du .docx source de "%DOCX_DIR%" ...
echo ^(sortie: *_images.docx — la source n'est pas modifiee^)
".venv\Scripts\python.exe" insert_docx.py "%DOCX_DIR%" "%IMAGES%"
set ERR=%ERRORLEVEL%

echo.
if not "%ERR%"=="0" (
    echo Echec de l'insertion ^(code %ERR%^). Voir le detail ci-dessus.
) else (
    echo Termine. Copie *_images.docx ecrite dans: %DOCX_DIR% ^(source intacte^)
)
pause
exit /b %ERR%
