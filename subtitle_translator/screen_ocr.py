"""
屏幕OCR识别模块
"""

import pytesseract
from PIL import ImageGrab, Image
import numpy as np
import cv2
import config


class ScreenOCR:
    """屏幕OCR识别器"""

    def __init__(self, tesseract_cmd=None):
        """
        初始化OCR识别器
        :param tesseract_cmd: Tesseract可执行文件路径（可选）
        """
        # 如果提供了Tesseract路径，则设置
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

        # 在Windows上，通常需要设置Tesseract的路径
        # 可以尝试常见的安装路径
        try:
            pytesseract.get_tesseract_version()
        except Exception:
            # 尝试设置常见的Windows安装路径
            common_paths = [
                r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            ]
            for path in common_paths:
                try:
                    pytesseract.pytesseract.tesseract_cmd = path
                    pytesseract.get_tesseract_version()
                    break
                except Exception:
                    continue

    def capture_screen_region(self, bbox):
        """
        截取屏幕指定区域
        :param bbox: 区域坐标 (x1, y1, x2, y2)
        :return: PIL Image对象
        """
        try:
            screenshot = ImageGrab.grab(bbox=bbox)
            return screenshot
        except Exception as e:
            print(f"截图错误: {e}")
            return None

    def preprocess_image(self, image):
        """
        预处理图像以提高OCR准确率
        :param image: PIL Image对象
        :return: 预处理后的PIL Image对象
        """
        # 转换为numpy数组
        img_np = np.array(image)

        # 转换为灰度图
        if len(img_np.shape) == 3:
            gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_np

        # 二值化处理
        # 使用自适应阈值
        binary = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )

        # 去噪
        denoised = cv2.fastNlMeansDenoising(binary, None, 10, 7, 21)

        # 转换回PIL Image
        processed_image = Image.fromarray(denoised)

        return processed_image

    def extract_text(self, image, lang=None, preprocess=True):
        """
        从图像中提取文本
        :param image: PIL Image对象
        :param lang: OCR语言，默认使用配置文件中的设置
        :param preprocess: 是否预处理图像
        :return: 识别出的文本
        """
        try:
            if image is None:
                return ""

            # 预处理图像
            if preprocess:
                image = self.preprocess_image(image)

            # 执行OCR
            text = pytesseract.image_to_string(image, lang=lang or config.OCR_LANGUAGE)

            # 清理文本（去除多余空白）
            text = text.strip()

            return text

        except Exception as e:
            print(f"OCR识别错误: {e}")
            return ""

    def capture_and_extract(self, bbox, lang=None, preprocess=True):
        """
        截取屏幕区域并提取文本（一步完成）
        :param bbox: 区域坐标 (x1, y1, x2, y2)
        :param lang: OCR语言
        :param preprocess: 是否预处理图像
        :return: 识别出的文本
        """
        image = self.capture_screen_region(bbox)
        if image is None:
            return ""
        return self.extract_text(image, lang, preprocess)


# 测试代码
if __name__ == "__main__":
    ocr = ScreenOCR()

    # 测试OCR（需要手动调整坐标）
    print("请在5秒内准备好要识别的屏幕区域...")
    import time

    time.sleep(5)

    # 示例：截取屏幕左上角的区域
    bbox = (100, 100, 500, 300)
    text = ocr.capture_and_extract(bbox)
    print(f"识别结果:\n{text}")
