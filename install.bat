@echo off
setlocal enabledelayedexpansion
title Instalador Automático de Python + App Tkinter
echo ======================================================
echo          Instalador de Python y Dependencias
echo ======================================================

:: Paso 1: Verificar si Python ya está instalado
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Python ya está instalado.
    goto check_path
)

:: Paso 2: Detectar arquitectura del sistema
echo Python no está instalado. Detectando tipo de sistema...
set "ARCH="
wmic os get osarchitecture | find "64" >nul && set "ARCH=64" || set "ARCH=32"

if "%ARCH%"=="64" (
    set "PY_URL=https://www.python.org/ftp/python/3.12.6/python-3.12.6-amd64.exe"
) else (
    set "PY_URL=https://www.python.org/ftp/python/3.12.6/python-3.12.6.exe"
)

echo Detectado sistema operativo de %ARCH% bits.
echo Descargando instalador de Python desde:
echo %PY_URL%

:: Paso 3: Descargar instalador
powershell -Command "Invoke-WebRequest -Uri '%PY_URL%' -OutFile 'python_installer.exe'"

if not exist python_installer.exe (
    echo ❌ Error: no se pudo descargar el instalador de Python.
    pause
    exit /b
)

:: Paso 4: Instalar Python en modo silencioso (con PATH)
echo Instalando Python...
start /wait python_installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_pip=1

:: Paso 5: Confirmar instalación
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python no se instaló correctamente.
    pause
    exit /b
)

:check_path
echo ======================================================
echo Verificando PATH del sistema...
echo ======================================================

:: Detectar carpeta de instalación de Python
for /f "tokens=2*" %%A in ('reg query "HKLM\SOFTWARE\Python\PythonCore\3.12\InstallPath" /v ExecutablePath 2^>nul') do set PY_PATH=%%B

if not defined PY_PATH (
    for /f "tokens=2*" %%A in ('where python') do set PY_PATH=%%A
)

set "PY_DIR=%PY_PATH:\python.exe=%"
set "SCRIPTS_DIR=%PY_DIR%\Scripts"

:: Agregar rutas al PATH si faltan
echo Verificando variables de entorno...
setx PATH "%PATH%;%PY_DIR%;%SCRIPTS_DIR%" /M

echo ✅ PATH actualizado con:
echo    %PY_DIR%
echo    %SCRIPTS_DIR%

:: Actualizar sesión actual del CMD
set "PATH=%PATH%;%PY_DIR%;%SCRIPTS_DIR%"

:: Paso 6: Instalar dependencias
echo ======================================================
echo Instalando dependencias desde requirements.txt
echo ======================================================

python -m pip install --upgrade pip

if exist requirements.txt (
    python -m pip install -r requirements.txt
) else (
    echo ⚠️ No se encontró archivo requirements.txt, se omite instalación de librerías.
)

:: Paso 7: Ejecutar aplicación
echo ======================================================
echo Instalación completada ✅
echo ======================================================

if exist app.py (
    echo Iniciando la aplicación...
    python app.py
) else if exist dist\app.exe (
    echo Ejecutando versión compilada...
    start dist\app.exe
)

pause
exit /b