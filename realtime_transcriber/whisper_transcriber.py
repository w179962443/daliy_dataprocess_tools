"""
Whisper转录模块 - 支持多语言和混合语言
"""

import whisper
import numpy as np
from datetime import datetime
import os
from pathlib import Path


class WhisperTranscriber:
    def __init__(self, model_name="base", language="auto"):
        """
        初始化Whisper转录器

        Args:
            model_name: 模型大小 ('tiny', 'base', 'small', 'medium', 'large')
            language: 语言代码或'auto'自动检测
        """
        self.model_name = model_name
        self.language = language if language != "auto" else None
        self.model = self._load_model(model_name)
        self.last_transcript = ""

    def _load_model(self, model_name):
        """加载Whisper模型"""
        try:
            print(f"加载Whisper模型: {model_name}")
            model = whisper.load_model(model_name)
            print(f"模型加载成功!")
            return model
        except Exception as e:
            print(f"加载模型失败: {e}")
            raise

    def transcribe_audio(self, audio_data, language=None):
        """
        转录音频

        Args:
            audio_data: numpy数组或音频文件路径
            language: 语言代码 (可选，覆盖默认语言)
                      常见代码: 'zh' (中文), 'en' (英文), 'auto' (自动检测)

        Returns:
            dict: 包含转录文本、语言、置信度等信息
        """
        if isinstance(audio_data, np.ndarray):
            # 如果是numpy数组，直接处理
            audio = audio_data
        else:
            # 如果是文件路径，加载音频
            import librosa

            audio, _ = librosa.load(audio_data, sr=16000)

        try:
            # 设置语言参数
            transcribe_kwargs = {}
            if language and language != "auto":
                transcribe_kwargs["language"] = language
            else:
                # 自动检测语言
                transcribe_kwargs["language"] = None

            result = self.model.transcribe(audio, **transcribe_kwargs)

            return {
                "text": result["text"].strip(),
                "language": result.get("language", "unknown"),
                "segments": result.get("segments", []),
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            print(f"转录错误: {e}")
            return {
                "text": "",
                "language": "unknown",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def transcribe_with_timestamps(self, audio_data):
        """
        获取带时间戳的转录结果

        Returns:
            list: 包含时间戳和文本的分段列表
        """
        result = self.transcribe_audio(audio_data)

        segments = []
        for segment in result.get("segments", []):
            segments.append(
                {
                    "start": segment["start"],
                    "end": segment["end"],
                    "text": segment["text"].strip(),
                }
            )

        return segments


class TranscriptionLogger:
    """转录日志记录器 - 保存转录内容到文件"""

    def __init__(self, output_dir="recordings"):
        """
        初始化日志记录器

        Args:
            output_dir: 输出目录
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.current_session = None
        self.current_file = None

    def start_new_session(self):
        """创建新的转录会话和文件"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"transcription_{timestamp}.txt"
        self.current_file = self.output_dir / filename
        self.current_session = {
            "start_time": datetime.now(),
            "filename": filename,
            "entries": [],
        }

        # 创建文件头
        with open(self.current_file, "w", encoding="utf-8") as f:
            f.write(f"{'='*60}\n")
            f.write(
                f"转录会话开始时间: {self.current_session['start_time'].strftime('%Y-%m-%d %H:%M:%S')}\n"
            )
            f.write(f"{'='*60}\n\n")

        print(f"新转录会话创建: {filename}")
        return self.current_file

    def log_transcription(self, text, language="unknown", confidence=0.0):
        """
        记录转录内容

        Args:
            text: 转录文本
            language: 检测到的语言
            confidence: 置信度
        """
        if not self.current_file:
            self.start_new_session()

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

        entry = {
            "timestamp": timestamp,
            "text": text,
            "language": language,
            "confidence": confidence,
        }

        self.current_session["entries"].append(entry)

        # 写入文件
        try:
            with open(self.current_file, "a", encoding="utf-8") as f:
                f.write(f"[{timestamp}] [{language}] {text}\n")
        except Exception as e:
            print(f"记录失败: {e}")

    def get_session_summary(self):
        """获取当前会话的摘要"""
        if not self.current_session:
            return None

        return {
            "filename": self.current_session["filename"],
            "start_time": self.current_session["start_time"].isoformat(),
            "total_entries": len(self.current_session["entries"]),
            "entries": self.current_session["entries"],
        }

    def export_session(self, format="txt"):
        """导出当前会话"""
        if not self.current_session:
            return None

        return {
            "file": str(self.current_file),
            "entries": len(self.current_session["entries"]),
            "format": format,
        }


if __name__ == "__main__":
    # 测试
    import time

    # 测试转录器
    transcriber = WhisperTranscriber(model_name="base")

    # 创建测试音频（3秒的静音）
    test_audio = np.zeros(16000 * 3)
    result = transcriber.transcribe_audio(test_audio)
    print("转录结果:", result)

    # 测试日志记录器
    logger = TranscriptionLogger()
    logger.start_new_session()
    logger.log_transcription("Hello world", language="en", confidence=0.95)
    logger.log_transcription("你好世界", language="zh", confidence=0.92)

    print("日志摘要:", logger.get_session_summary())
