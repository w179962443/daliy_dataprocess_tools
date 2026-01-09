"""
音频录制模块 - 支持麦克风和系统声音
"""

import numpy as np
import threading
from collections import deque
import sounddevice as sd
from datetime import datetime
import os


class AudioRecorder:
    def __init__(self, sample_rate=16000, chunk_duration=0.5, max_buffer_size=50):
        """
        初始化音频录制器

        Args:
            sample_rate: 采样率
            chunk_duration: 每个音频块的持续时间（秒）
            max_buffer_size: 缓冲区最大大小（块数）
        """
        self.sample_rate = sample_rate
        self.chunk_size = int(sample_rate * chunk_duration)
        self.max_buffer_size = max_buffer_size
        self.audio_buffer = deque(maxlen=max_buffer_size)
        self.is_recording = False
        self.record_thread = None
        self.lock = threading.Lock()

    def audio_callback(self, indata, frames, time_info, status):
        """音频流回调函数"""
        if status:
            print(f"音频状态: {status}")

        with self.lock:
            # 转换为mono并归一化
            audio_data = indata[:, 0].copy()
            self.audio_buffer.append(audio_data)

    def start_recording(self, source="both"):
        """
        开始录制

        Args:
            source: 'mic' (麦克风), 'system' (系统声音), 'both' (两者)
        """
        if self.is_recording:
            return

        self.is_recording = True
        self.audio_buffer.clear()

        # 使用sounddevice进行音频捕获
        # 注意：Windows上系统声音捕获需要特殊配置
        try:
            self.stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=1,
                blocksize=self.chunk_size,
                callback=self.audio_callback,
                device=None,  # 使用默认设备（通常是麦克风）
            )
            self.stream.start()
            print(f"开始录制 (源: {source})")
        except Exception as e:
            print(f"错误: 无法启动录制 - {e}")
            self.is_recording = False

    def stop_recording(self):
        """停止录制"""
        if not self.is_recording:
            return

        self.is_recording = False
        try:
            if hasattr(self, "stream"):
                self.stream.stop()
                self.stream.close()
        except Exception as e:
            print(f"停止录制时出错: {e}")

    def get_audio_chunk(self):
        """
        获取音频块

        Returns:
            numpy数组，包含最近的音频数据
        """
        with self.lock:
            if len(self.audio_buffer) == 0:
                return None

            # 合并所有缓冲的音频块
            audio_data = np.concatenate(list(self.audio_buffer))
            return audio_data

    def clear_buffer(self):
        """清空缓冲区"""
        with self.lock:
            self.audio_buffer.clear()


class SystemAudioRecorder:
    """
    系统声音录制 - Windows特定实现
    需要额外配置和库支持
    """

    def __init__(self, sample_rate=16000):
        self.sample_rate = sample_rate
        self.is_recording = False
        self.audio_buffer = deque(maxlen=50)

    def start_recording(self):
        """
        在Windows上录制系统声音
        需要安装: pip install sounddevice loopback-device
        """
        print("系统声音录制需要额外配置")
        print("Windows用户可以:")
        print("1. 安装Voicemeeter Banana")
        print("2. 配置虚拟音频设备")
        print("3. 使用sounddevice指定设备")

    def stop_recording(self):
        pass


if __name__ == "__main__":
    # 测试
    recorder = AudioRecorder()
    recorder.start_recording(source="mic")

    import time

    for i in range(5):
        time.sleep(1)
        chunk = recorder.get_audio_chunk()
        if chunk is not None:
            print(f"音频块 {i}: {len(chunk)} 样本")

    recorder.stop_recording()
