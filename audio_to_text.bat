@echo off
chcp 65001 >nul
echo ====================================
echo 音频转文字工具 - Whisper GPU加速
echo ====================================
echo.

python audio_to_text.py %*

if errorlevel 1 (
    echo.
    echo 执行失败!
    pause
)
