@echo off
chcp 65001 >nul
echo ========================================
echo     字幕翻译器启动脚本
echo ========================================
echo.

REM 检查环境变量
if "%TENCENT_SECRET_ID%"=="" (
    echo [警告] 未设置环境变量 TENCENT_SECRET_ID
    echo 请先设置腾讯云API密钥环境变量
    echo.
    echo 设置方法：
    echo $env:TENCENT_SECRET_ID = "你的SecretId"
    echo $env:TENCENT_SECRET_KEY = "你的SecretKey"
    echo.
    pause
    exit /b 1
)

if "%TENCENT_SECRET_KEY%"=="" (
    echo [警告] 未设置环境变量 TENCENT_SECRET_KEY
    echo 请先设置腾讯云API密钥环境变量
    echo.
    pause
    exit /b 1
)

echo [信息] 环境变量检查通过
echo [信息] 启动程序...
echo.

python app.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [错误] 程序异常退出
    pause
)
