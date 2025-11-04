@echo off
setlocal enabledelayedexpansion
title Automatic Installer for Python + Tkinter App
echo ======================================================
echo          Python and Dependencies Installer
echo ======================================================

:: Step 1: Check if Python is already installed
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Python is already installed.
    goto check_path
)

:: Step 2: Detect system architecture
echo Python is not installed. Detecting system type...
set "ARCH="
wmic os get osarchitecture | find "64" >nul && set "ARCH=64" || set "ARCH=32"

if "%ARCH%"=="64" (
    set "PY_URL=https://www.python.org/ftp/python/3.12.6/python-3.12.6-amd64.exe"
) else (
    set "PY_URL=https://www.python.org/ftp/python/3.12.6/python-3.12.6.exe"
)

echo Detected %ARCH%-bit operating system.
echo Downloading Python installer from:
echo %PY_URL%

:: Step 3: Download the installer
powershell -Command "Invoke-WebRequest -Uri '%PY_URL%' -OutFile 'python_installer.exe'"

if not exist python_installer.exe (
    echo ❌ Error: Could not download the Python installer.
    pause
    exit /b
)

:: Step 4: Install Python silently (with PATH)
echo Installing Python...
start /wait python_installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_pip=1



:check_path
echo ======================================================
echo Verifying system PATH...
echo ======================================================

:: Detect Python installation folder
for /f "tokens=2*" %%A in ('reg query "HKLM\SOFTWARE\Python\PythonCore\3.12\InstallPath" /v ExecutablePath 2^>nul') do set PY_PATH=%%B

if not defined PY_PATH (
    for /f "tokens=2*" %%A in ('where python') do set PY_PATH=%%A
)

set "PY_DIR=%PY_PATH:\python.exe=%"
set "SCRIPTS_DIR=%PY_DIR%\Scripts"

echo Python installation directory: %PY_DIR%
echo Scripts directory: %SCRIPTS_DIR%

:: Step 6: Install required libraries
echo ======================================================
echo Installing required Python libraries...
echo ======================================================

pip install --upgrade pip
pip install pillow PyPDF2 PyMuPDF

echo ======================================================
echo ✅ Installation completed successfully!
echo You can now use the Tkinter App.
echo ======================================================

pause
exit