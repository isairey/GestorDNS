@echo off
cd /d "%~dp0"
echo ==============================
echo Compilando ejecutable OneClickDNS...
echo ==============================

pyinstaller --onefile --windowed --icon=..\assets\icons\icon.ico --name OneClickDNS --distpath ..\dist --add-data "..\assets\icons;assets/icons" ..\src\main.py

if %errorlevel% neq 0 (
    echo Error durante la compilación de PyInstaller
    pause
    exit /b 1
)

echo ==============================
echo Ejecutable creado: dist\OneClickDNS.exe
echo ==============================

echo Compilando instalador Inno Setup...
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" setup.iss

echo ==============================
echo Limpiando archivos temporales...
echo ==============================
rmdir /s /q build
rmdir /s /q __pycache__
del /q *.spec

echo ==============================
echo Proceso completado correctamente.
pause