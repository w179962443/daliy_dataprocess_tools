"""
GUI界面 - 字幕翻译器主窗口
"""

import sys
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QTextEdit,
    QGroupBox,
    QSpinBox,
    QDoubleSpinBox,
    QLineEdit,
    QMessageBox,
    QRubberBand,
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QRect, QPoint, QSize
from PyQt5.QtGui import QFont, QPalette, QColor, QCursor, QPainter, QPen
import config
from translator import TencentTranslator
from stability_detector import StabilityDetector


class RegionSelector(QWidget):
    """区域选择窗口"""

    region_selected = pyqtSignal(tuple)  # 发送选中的区域坐标

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowOpacity(0.3)

        # 设置全屏
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen)

        self.begin = QPoint()
        self.end = QPoint()
        self.is_drawing = False

    def paintEvent(self, event):
        """绘制选择区域"""
        if self.is_drawing:
            painter = QPainter(self)
            painter.setPen(QPen(Qt.red, 3, Qt.SolidLine))
            painter.drawRect(QRect(self.begin, self.end))

    def mousePressEvent(self, event):
        """鼠标按下"""
        if event.button() == Qt.LeftButton:
            self.begin = event.pos()
            self.end = event.pos()
            self.is_drawing = True
            self.update()

    def mouseMoveEvent(self, event):
        """鼠标移动"""
        if self.is_drawing:
            self.end = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        """鼠标释放"""
        if event.button() == Qt.LeftButton and self.is_drawing:
            self.is_drawing = False

            # 计算区域坐标
            x1 = min(self.begin.x(), self.end.x())
            y1 = min(self.begin.y(), self.end.y())
            x2 = max(self.begin.x(), self.end.x())
            y2 = max(self.begin.y(), self.end.y())

            # 发送选中的区域
            if x2 - x1 > 10 and y2 - y1 > 10:  # 确保区域足够大
                self.region_selected.emit((x1, y1, x2, y2))

            self.close()


class MonitorThread(QThread):
    """监控线程"""

    text_detected = pyqtSignal(str)  # 检测到文本信号
    translation_completed = pyqtSignal(dict)  # 翻译完成信号
    error_occurred = pyqtSignal(str)  # 错误信号

    def __init__(self, bbox, stable_duration, capture_interval):
        super().__init__()
        self.bbox = bbox
        self.stable_duration = stable_duration
        self.capture_interval = capture_interval
        self.running = False
        self.translator = None
        self.detector = None

    def init_services(self):
        """初始化服务（在线程中）"""
        try:
            self.translator = TencentTranslator()
            self.detector = StabilityDetector(
                stable_duration=self.stable_duration,
                capture_interval=self.capture_interval,
            )
        except Exception as e:
            self.error_occurred.emit(f"初始化错误: {e}")

    def on_stable_content(self, text):
        """当内容稳定时的回调"""
        if not text.strip():
            return

        # 发送检测到的文本
        self.text_detected.emit(text)

        # 翻译文本
        if self.translator:
            result = self.translator.translate(text)
            self.translation_completed.emit(result)

    def run(self):
        """运行监控"""
        self.running = True
        self.init_services()

        if self.detector:
            self.detector.monitor_region(
                self.bbox, self.on_stable_content, stop_flag=lambda: not self.running
            )

    def stop(self):
        """停止监控"""
        self.running = False


class SubtitleTranslatorGUI(QMainWindow):
    """主窗口"""

    def __init__(self):
        super().__init__()
        self.bbox = None
        self.monitor_thread = None
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("字幕翻译器")
        self.setGeometry(100, 100, config.WINDOW_WIDTH, config.WINDOW_HEIGHT)

        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # 1. 区域选择组
        region_group = QGroupBox("1. 选择屏幕区域")
        region_layout = QHBoxLayout()

        self.select_btn = QPushButton("选择区域")
        self.select_btn.clicked.connect(self.select_region)
        region_layout.addWidget(self.select_btn)

        self.region_label = QLabel("未选择")
        region_layout.addWidget(self.region_label)
        region_layout.addStretch()

        region_group.setLayout(region_layout)
        main_layout.addWidget(region_group)

        # 2. 配置组
        config_group = QGroupBox("2. 配置参数")
        config_layout = QVBoxLayout()

        # 稳定时间
        stable_layout = QHBoxLayout()
        stable_layout.addWidget(QLabel("稳定持续时间(秒):"))
        self.stable_spin = QDoubleSpinBox()
        self.stable_spin.setRange(0.5, 10.0)
        self.stable_spin.setSingleStep(0.5)
        self.stable_spin.setValue(config.STABLE_DURATION)
        stable_layout.addWidget(self.stable_spin)
        stable_layout.addStretch()
        config_layout.addLayout(stable_layout)

        # 捕获间隔
        interval_layout = QHBoxLayout()
        interval_layout.addWidget(QLabel("捕获间隔(秒):"))
        self.interval_spin = QDoubleSpinBox()
        self.interval_spin.setRange(0.1, 5.0)
        self.interval_spin.setSingleStep(0.1)
        self.interval_spin.setValue(config.CAPTURE_INTERVAL)
        interval_layout.addWidget(self.interval_spin)
        interval_layout.addStretch()
        config_layout.addLayout(interval_layout)

        # API密钥提示
        api_layout = QVBoxLayout()
        api_layout.addWidget(QLabel("腾讯云API密钥（通过环境变量配置）:"))
        api_hint = QLabel("TENCENT_SECRET_ID 和 TENCENT_SECRET_KEY")
        api_hint.setStyleSheet("color: gray; font-size: 10px;")
        api_layout.addWidget(api_hint)
        config_layout.addLayout(api_layout)

        config_group.setLayout(config_layout)
        main_layout.addWidget(config_group)

        # 3. 控制按钮
        control_layout = QHBoxLayout()

        self.start_btn = QPushButton("开始监控")
        self.start_btn.clicked.connect(self.start_monitoring)
        self.start_btn.setEnabled(False)
        control_layout.addWidget(self.start_btn)

        self.stop_btn = QPushButton("停止监控")
        self.stop_btn.clicked.connect(self.stop_monitoring)
        self.stop_btn.setEnabled(False)
        control_layout.addWidget(self.stop_btn)

        main_layout.addLayout(control_layout)

        # 4. 显示区域
        display_group = QGroupBox("翻译结果")
        display_layout = QVBoxLayout()

        # 原文
        display_layout.addWidget(QLabel("原文:"))
        self.source_text = QTextEdit()
        self.source_text.setReadOnly(True)
        self.source_text.setMaximumHeight(80)
        display_layout.addWidget(self.source_text)

        # 译文
        display_layout.addWidget(QLabel("译文:"))
        self.translation_text = QTextEdit()
        self.translation_text.setReadOnly(True)
        font = QFont()
        font.setPointSize(config.TRANSLATION_DISPLAY_FONT_SIZE)
        self.translation_text.setFont(font)
        display_layout.addWidget(self.translation_text)

        display_group.setLayout(display_layout)
        main_layout.addWidget(display_group)

        # 状态栏
        self.statusBar().showMessage("就绪")

    def select_region(self):
        """选择屏幕区域"""
        self.hide()  # 隐藏主窗口

        # 创建区域选择器
        selector = RegionSelector()
        selector.region_selected.connect(self.on_region_selected)
        selector.show()

    def on_region_selected(self, bbox):
        """区域选择完成"""
        self.bbox = bbox
        self.region_label.setText(f"({bbox[0]}, {bbox[1]}) - ({bbox[2]}, {bbox[3]})")
        self.start_btn.setEnabled(True)
        self.show()  # 显示主窗口
        self.statusBar().showMessage(f"已选择区域: {bbox}")

    def start_monitoring(self):
        """开始监控"""
        if not self.bbox:
            QMessageBox.warning(self, "警告", "请先选择屏幕区域")
            return

        # 创建并启动监控线程
        self.monitor_thread = MonitorThread(
            self.bbox, self.stable_spin.value(), self.interval_spin.value()
        )
        self.monitor_thread.text_detected.connect(self.on_text_detected)
        self.monitor_thread.translation_completed.connect(self.on_translation_completed)
        self.monitor_thread.error_occurred.connect(self.on_error)
        self.monitor_thread.start()

        # 更新UI状态
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.select_btn.setEnabled(False)
        self.stable_spin.setEnabled(False)
        self.interval_spin.setEnabled(False)
        self.statusBar().showMessage("监控中...")

    def stop_monitoring(self):
        """停止监控"""
        if self.monitor_thread:
            self.monitor_thread.stop()
            self.monitor_thread.wait()
            self.monitor_thread = None

        # 更新UI状态
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.select_btn.setEnabled(True)
        self.stable_spin.setEnabled(True)
        self.interval_spin.setEnabled(True)
        self.statusBar().showMessage("已停止")

    def on_text_detected(self, text):
        """检测到文本"""
        self.source_text.setText(text)
        self.statusBar().showMessage("检测到新文本，正在翻译...")

    def on_translation_completed(self, result):
        """翻译完成"""
        if result.get("error"):
            self.translation_text.setText(f"错误: {result['error']}")
            self.statusBar().showMessage("翻译失败")
        else:
            self.translation_text.setText(result["target_text"])
            self.statusBar().showMessage(
                f"翻译完成 | {result['source']} -> {result['target']} | "
                f"用量: {result['used_amount']} 字符"
            )

    def on_error(self, error_msg):
        """发生错误"""
        QMessageBox.critical(self, "错误", error_msg)
        self.stop_monitoring()

    def closeEvent(self, event):
        """关闭窗口时停止监控"""
        self.stop_monitoring()
        event.accept()


def main():
    app = QApplication(sys.argv)
    window = SubtitleTranslatorGUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
