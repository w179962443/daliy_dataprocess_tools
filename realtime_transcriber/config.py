"""
配置文件 - config.py
可在这里修改应用的所有配置选项
"""

# 音频配置
AUDIO_CONFIG = {
    "sample_rate": 16000,  # 采样率 (Hz)
    "chunk_duration": 0.5,  # 每个音频块的时长 (秒)
    "max_buffer_size": 50,  # 缓冲区最大块数
    "audio_source": "mic",  # 音频源: 'mic', 'system', 'both'
}

# Whisper配置
WHISPER_CONFIG = {
    "model_name": "base",  # 模型大小: 'tiny', 'base', 'small', 'medium', 'large'
    "language": "auto",  # 语言: 'auto', 'zh', 'en', 等
    "transcribe_interval": 2,  # 转录间隔 (秒)
    "use_gpu": False,  # 是否使用GPU加速
}

# Flask应用配置
FLASK_CONFIG = {
    "host": "0.0.0.0",
    "port": 5000,
    "debug": True,
}

# 日志和存储配置
STORAGE_CONFIG = {
    "output_dir": "recordings",  # 转录文件保存目录
    "log_level": "INFO",  # 日志级别
    "encoding": "utf-8",  # 文件编码
}

# 性能配置
PERFORMANCE_CONFIG = {
    "max_concurrent_streams": 1,  # 最大并发流数
    "enable_caching": True,  # 是否启用缓存
    "cache_size_mb": 500,  # 缓存大小 (MB)
}

# UI配置
UI_CONFIG = {
    "theme": "light",  # 主题: 'light', 'dark'
    "auto_scroll": True,  # 是否自动滚动
    "show_timestamps": True,  # 是否显示时间戳
    "show_language": True,  # 是否显示语言标签
}

# 支持的语言列表
SUPPORTED_LANGUAGES = {
    "auto": "自动检测",
    "zh": "中文 (简体)",
    "zh-Hans": "中文 (简体)",
    "zh-Hant": "中文 (繁体)",
    "en": "English",
    "ja": "日本語",
    "ko": "한국어",
    "fr": "Français",
    "de": "Deutsch",
    "es": "Español",
    "ru": "Русский",
    "pt": "Português",
    "it": "Italiano",
    "nl": "Nederlands",
    "pl": "Polski",
    "tr": "Türkçe",
    "ar": "العربية",
    "hi": "हिन्दी",
    "th": "ไทย",
    "vi": "Tiếng Việt",
}


def get_config():
    """获取完整配置"""
    return {
        "audio": AUDIO_CONFIG,
        "whisper": WHISPER_CONFIG,
        "flask": FLASK_CONFIG,
        "storage": STORAGE_CONFIG,
        "performance": PERFORMANCE_CONFIG,
        "ui": UI_CONFIG,
        "languages": SUPPORTED_LANGUAGES,
    }


def validate_config():
    """验证配置有效性"""
    issues = []

    if AUDIO_CONFIG["sample_rate"] not in [8000, 16000, 22050, 44100, 48000]:
        issues.append("警告: 采样率应为标准值")

    if WHISPER_CONFIG["model_name"] not in ["tiny", "base", "small", "medium", "large"]:
        issues.append("错误: 无效的模型名称")

    if FLASK_CONFIG["port"] < 1024 or FLASK_CONFIG["port"] > 65535:
        issues.append("错误: 无效的端口号")

    return issues


if __name__ == "__main__":
    issues = validate_config()
    if issues:
        for issue in issues:
            print(issue)
    else:
        print("✓ 配置有效")
        print("\n当前配置:")
        import json

        print(json.dumps(get_config(), indent=2, ensure_ascii=False))
