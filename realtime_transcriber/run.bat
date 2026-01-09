@echo off
REM 实时转录软件 - Windows启动脚本

echo.
echo ============================================================
echo   实时转录软件 - Windows启动脚本
echo ============================================================
echo.

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.8+
    echo 访问 https://www.python.org/downloads/
    pause
    exit /b 1
)

REM 创建虚拟环境 (可选)
if not exist "venv" (
    echo.
    echo 创建虚拟环境...
    python -m venv venv
    echo 虚拟环境创建成功
)

REM 激活虚拟环境
echo.
echo 激活虚拟环境...
call venv\Scripts\activate.bat

REM 安装依赖
echo.
echo 检查依赖...
pip show flask >nul 2>&1
if errorlevel 1 (
    echo 安装依赖...
    pip install -r requirements.txt
)

REM 启动应用
echo.
echo ============================================================
echo 启动应用...
echo ============================================================
echo.
echo 应用地址: http://localhost:5000
echo.
echo 按 Ctrl+C 停止应用
echo.

python app.py

pause
