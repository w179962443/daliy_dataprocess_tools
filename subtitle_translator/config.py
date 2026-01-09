"""
配置文件
"""

import os

# 腾讯云API配置
TENCENT_SECRET_ID = os.getenv("TENCENT_SECRET_ID", "")  # 从环境变量获取
TENCENT_SECRET_KEY = os.getenv("TENCENT_SECRET_KEY", "")  # 从环境变量获取
TENCENT_REGION = "ap-guangzhou"  # 地域
TENCENT_PROJECT_ID = 0  # 项目ID

# OCR配置
OCR_LANGUAGE = "chi_sim+eng"  # 中文简体+英文

# 稳定性检测配置
STABLE_DURATION = 2.0  # 内容稳定持续时间（秒），可配置
CAPTURE_INTERVAL = 0.3  # 截图间隔（秒）

# 翻译配置
SOURCE_LANG = "auto"  # 源语言，auto为自动识别
TARGET_LANG = "zh"  # 目标语言，中文

# GUI配置
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 400
TRANSLATION_DISPLAY_FONT_SIZE = 16
