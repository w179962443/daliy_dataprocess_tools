"""
快速启动脚本 - Windows用户推荐
"""

import subprocess
import sys
import os


def main():
    print("=" * 60)
    print("实时转录软件 - 快速启动")
    print("=" * 60)

    # 检查Python版本
    if sys.version_info < (3, 8):
        print("❌ 错误: 需要 Python 3.8+")
        sys.exit(1)

    print("✓ Python 版本正确")

    # 检查依赖
    print("\n检查依赖...")
    try:
        import flask
        import sounddevice
        import whisper

        print("✓ 所有依赖已安装")
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("\n正在安装依赖...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]
        )

    # 创建recordings目录
    os.makedirs("recordings", exist_ok=True)
    print("✓ 转录目录已准备")

    # 启动应用
    print("\n" + "=" * 60)
    print("启动应用...")
    print("=" * 60)
    print("\n🌐 应用地址: http://localhost:5000")
    print("📝 按 Ctrl+C 停止应用\n")

    try:
        subprocess.run([sys.executable, "app.py"])
    except KeyboardInterrupt:
        print("\n\n应用已停止")
        sys.exit(0)


if __name__ == "__main__":
    main()
