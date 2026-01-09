"""
内容稳定性检测器
检测屏幕区域内容是否在指定时间内保持稳定
"""

import time
import hashlib
from screen_ocr import ScreenOCR
import config


class StabilityDetector:
    """内容稳定性检测器"""

    def __init__(self, stable_duration=None, capture_interval=None):
        """
        初始化稳定性检测器
        :param stable_duration: 稳定持续时间（秒）
        :param capture_interval: 截图间隔（秒）
        """
        self.stable_duration = stable_duration or config.STABLE_DURATION
        self.capture_interval = capture_interval or config.CAPTURE_INTERVAL
        self.ocr = ScreenOCR()

        # 记录状态
        self.last_text = ""
        self.last_hash = ""
        self.stable_start_time = None
        self.is_stable = False

    def get_content_hash(self, text):
        """
        获取文本内容的哈希值
        :param text: 文本内容
        :return: MD5哈希值
        """
        return hashlib.md5(text.encode("utf-8")).hexdigest()

    def reset(self):
        """重置检测器状态"""
        self.last_text = ""
        self.last_hash = ""
        self.stable_start_time = None
        self.is_stable = False

    def check_stability(self, bbox, lang=None, preprocess=True):
        """
        检查区域内容是否稳定
        :param bbox: 区域坐标 (x1, y1, x2, y2)
        :param lang: OCR语言
        :param preprocess: 是否预处理图像
        :return: (is_stable, text) 元组，is_stable表示是否稳定，text为稳定的文本
        """
        # 提取当前文本
        current_text = self.ocr.capture_and_extract(bbox, lang, preprocess)
        current_hash = self.get_content_hash(current_text)

        current_time = time.time()

        # 如果内容与上次相同
        if current_hash == self.last_hash and current_text.strip():
            # 如果是第一次发现稳定
            if self.stable_start_time is None:
                self.stable_start_time = current_time

            # 检查是否已经稳定足够长时间
            elapsed_time = current_time - self.stable_start_time
            if elapsed_time >= self.stable_duration:
                # 内容已稳定
                if not self.is_stable:
                    self.is_stable = True
                    return True, current_text
                else:
                    # 已经处于稳定状态，不重复返回
                    return False, current_text
            else:
                # 还在稳定中，但时间不够
                return False, current_text
        else:
            # 内容发生变化，重置
            self.last_text = current_text
            self.last_hash = current_hash
            self.stable_start_time = None
            self.is_stable = False
            return False, current_text

    def monitor_region(
        self, bbox, callback, lang=None, preprocess=True, stop_flag=None
    ):
        """
        持续监控区域，当内容稳定时调用回调函数
        :param bbox: 区域坐标 (x1, y1, x2, y2)
        :param callback: 回调函数，参数为稳定的文本
        :param lang: OCR语言
        :param preprocess: 是否预处理图像
        :param stop_flag: 停止标志，当该函数返回True时停止监控
        """
        self.reset()

        while True:
            # 检查停止标志
            if stop_flag and stop_flag():
                break

            # 检查稳定性
            is_stable, text = self.check_stability(bbox, lang, preprocess)

            # 如果稳定，调用回调
            if is_stable:
                callback(text)
                # 重置状态，等待下一次稳定
                self.reset()

            # 等待一段时间再次检查
            time.sleep(self.capture_interval)


# 测试代码
if __name__ == "__main__":
    detector = StabilityDetector(stable_duration=2.0, capture_interval=0.5)

    def on_stable(text):
        print(f"检测到稳定内容:\n{text}\n" + "=" * 50)

    # 测试监控（需要手动调整坐标）
    print("开始监控屏幕区域...")
    bbox = (100, 100, 500, 300)

    try:
        detector.monitor_region(bbox, on_stable)
    except KeyboardInterrupt:
        print("\n监控已停止")
