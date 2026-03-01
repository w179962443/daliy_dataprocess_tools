@echo off
setlocal enabledelayedexpansion

:: ============================================================
::  Audio-to-Text Tool - Environment Setup Script
::  Creates conda env and installs all dependencies
:: ============================================================

set ENV_NAME=audio_to_text
set PYTHON_VERSION=3.10
set HTTP_PROXY=http://127.0.0.1:7890
set HTTPS_PROXY=http://127.0.0.1:7890

echo ============================================================
echo  Setting proxy: %HTTP_PROXY%
echo ============================================================
set http_proxy=%HTTP_PROXY%
set https_proxy=%HTTPS_PROXY%

echo.
echo ============================================================
echo  Checking conda env: %ENV_NAME%
echo ============================================================

:: Check if conda is available
where conda >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] conda not found. Please install Anaconda or Miniconda and add to PATH.
    pause
    exit /b 1
)

:: Check if the env already exists
conda env list | findstr /B "%ENV_NAME% " >nul 2>&1
if %errorlevel% equ 0 (
    echo [INFO] conda env "%ENV_NAME%" already exists, skipping creation.
) else (
    echo [INFO] conda env "%ENV_NAME%" not found, creating with Python %PYTHON_VERSION% ...
    call conda create -n %ENV_NAME% python=%PYTHON_VERSION% -y
    :: Verify by checking env list instead of relying on errorlevel
    conda env list | findstr /B "%ENV_NAME% " >nul 2>&1
    if !errorlevel! neq 0 (
        echo [ERROR] Failed to create conda env. Please check the output above.
        pause
        exit /b 1
    )
    echo [OK] conda env "%ENV_NAME%" created.
)

echo.
echo ============================================================
echo  Installing dependencies into: %ENV_NAME%
echo ============================================================

echo [1/4] Upgrading pip...
call conda run -n %ENV_NAME% python -m pip install --upgrade pip

echo.
echo [2/4] Installing PyTorch with CUDA 12.8 ...
call conda run -n %ENV_NAME% pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128
if %errorlevel% neq 0 (
    echo [ERROR] PyTorch installation failed. Check network or proxy settings.
    pause
    exit /b 1
)
echo [OK] PyTorch installed.

echo.
echo [3/4] Installing remaining packages...
call conda run -n %ENV_NAME% pip install "openai-whisper>=20231117" "numpy>=1.24.0" "ffmpeg-python>=0.2.0" "opencc-python-reimplemented>=0.1.7"
if %errorlevel% neq 0 (
    echo [ERROR] Package installation failed.
    pause
    exit /b 1
)
echo [OK] All packages installed.

echo.
echo [4/4] Installing ffmpeg binary (conda-forge)...
call conda install -n %ENV_NAME% -c conda-forge ffmpeg -y
if %errorlevel% neq 0 (
    echo [ERROR] ffmpeg installation failed.
    pause
    exit /b 1
)
echo [OK] ffmpeg installed.

echo.
echo ============================================================
echo  Setup complete!
echo  Usage: conda activate %ENV_NAME%
echo         python audio_to_text.py
echo ============================================================
pause
