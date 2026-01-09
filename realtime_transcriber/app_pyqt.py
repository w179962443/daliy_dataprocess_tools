"""
PyQt6桌面应用版本 (可选)
提供原生桌面界面，不需要打开浏览器

安装: pip install PyQt6

运行: python app_pyqt.py
"""

import sys
import threading
import time
from datetime import datetime
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QComboBox,
    QTextEdit,
    QStatusBar,
    QTabWidget,
    QScrollArea,
    QGroupBox,
    QSpinBox,
    QCheckBox,
    QMessageBox,
    QFileDialog,
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QTimer
from PyQt6.QtGui import QTextCursor, QFont, QColor
from PyQt6.QtCore import QSize

from audio_recorder import AudioRecorder
from whisper_transcriber import WhisperTranscriber, TranscriptionLogger
import numpy as np


class TranscriptionThread(QThread):
    """后台转录线程"""

    transcription_signal = pyqtSignal(dict)
    error_signal = pyqtSignal(str)

    def __init__(self, recorder, transcriber, logger, interval=2):
        super().__init__()
        self.recorder = recorder
        self.transcriber = transcriber
        self.logger = logger
        self.interval = interval
        self.is_running = False

    def run(self):
        """运行转录线程"""
        self.is_running = True
        last_transcribe_time = 0

        while self.is_running:
            try:
                current_time = time.time()

                if current_time - last_transcribe_time > self.interval:
                    audio_chunk = self.recorder.get_audio_chunk()

                    if audio_chunk is not None and len(audio_chunk) > 0:
                        result = self.transcriber.transcribe_audio(audio_chunk)

                        if result.get("text"):
                            language = result.get("language", "unknown")
                            self.logger.log_transcription(
                                text=result["text"], language=language, confidence=0.9
                            )

                            self.transcription_signal.emit(
                                {
                                    "text": result["text"],
                                    "language": language,
                                    "timestamp": datetime.now().isoformat(),
                                }
                            )

                        self.recorder.clear_buffer()

                    last_transcribe_time = current_time

                time.sleep(0.1)

            except Exception as e:
                self.error_signal.emit(str(e))

    def stop(self):
        """停止线程"""
        self.is_running = False
        self.wait()


class TranscriberApp(QMainWindow):
    """实时转录应用主窗口"""

    def __init__(self):
        super().__init__()
        self.initUI()

        # 初始化组件
        self.recorder = AudioRecorder()
        self.transcriber = None
        self.logger = TranscriptionLogger()

        self.is_recording = False
        self.entry_count = 0
        self.start_time = None
        self.transcription_thread = None

        # 启动定时器更新时间
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)

    def initUI(self):
        """初始化UI"""
        self.setWindowTitle("实时转录软件 🎙️")
        self.setGeometry(100, 100, 1000, 700)

        # 主窗口
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # 主布局
        main_layout = QHBoxLayout()

        # 左侧控制面板
        left_panel = self.create_control_panel()
        main_layout.addWidget(left_panel, 1)

        # 右侧转录显示
        right_panel = self.create_transcript_panel()
        main_layout.addWidget(right_panel, 2)

        main_widget.setLayout(main_layout)

        # 状态栏
        self.status_label = QLabel("就绪")
        self.time_label = QLabel()
        self.counter_label = QLabel("文本条数: 0")

        statusbar = self.statusBar()
        statusbar.addWidget(self.status_label, 1)
        statusbar.addPermanentWidget(self.counter_label)
        statusbar.addPermanentWidget(self.time_label)

    def create_control_panel(self):
        """创建控制面板"""
        group = QGroupBox("控制面板")
        layout = QVBoxLayout()

        # 启动/停止按钮
        button_layout = QHBoxLayout()

        self.start_btn = QPushButton("▶️ 开始转录")
        self.start_btn.clicked.connect(self.start_recording)
        self.start_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #667eea;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5568d3;
            }
        """
        )

        self.stop_btn = QPushButton("⏹️ 停止转录")
        self.stop_btn.clicked.connect(self.stop_recording)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
            QPushButton:disabled {
                background-color: #999;
            }
        """
        )

        button_layout.addWidget(self.start_btn)
        button_layout.addWidget(self.stop_btn)
        layout.addLayout(button_layout)

        # 音源选择
        layout.addWidget(QLabel("音源选择:"))
        self.source_combo = QComboBox()
        self.source_combo.addItems(["麦克风", "系统声音", "麦克风 + 系统声音"])
        layout.addWidget(self.source_combo)

        # 语言选择
        layout.addWidget(QLabel("语言设置:"))
        self.language_combo = QComboBox()
        self.language_combo.addItems(
            [
                "自动检测",
                "中文",
                "English",
                "日本語",
                "한국어",
                "Français",
                "Deutsch",
                "Español",
            ]
        )
        layout.addWidget(self.language_combo)

        # 模型选择
        layout.addWidget(QLabel("模型选择:"))
        self.model_combo = QComboBox()
        self.model_combo.addItems(
            ["Tiny (最快)", "Base (推荐)", "Small", "Medium", "Large (最精准)"]
        )
        self.model_combo.setCurrentIndex(1)
        layout.addWidget(self.model_combo)

        # 转录间隔
        layout.addWidget(QLabel("转录间隔 (秒):"))
        self.interval_spin = QSpinBox()
        self.interval_spin.setMinimum(1)
        self.interval_spin.setMaximum(10)
        self.interval_spin.setValue(2)
        layout.addWidget(self.interval_spin)

        # 其他选项
        self.show_timestamp_check = QCheckBox("显示时间戳")
        self.show_timestamp_check.setChecked(True)
        layout.addWidget(self.show_timestamp_check)

        self.show_language_check = QCheckBox("显示语言标签")
        self.show_language_check.setChecked(True)
        layout.addWidget(self.show_language_check)

        # 操作按钮
        layout.addSpacing(20)

        clear_btn = QPushButton("🗑️ 清空屏幕")
        clear_btn.clicked.connect(self.clear_transcript)
        layout.addWidget(clear_btn)

        download_btn = QPushButton("💾 下载文本")
        download_btn.clicked.connect(self.download_transcript)
        layout.addWidget(download_btn)

        layout.addStretch()

        # 信息框
        info_text = """
<b>提示:</b>
• 首次运行会下载模型 (1-3GB)
• 自动检测支持混合语言
• 转录内容自动保存到文件
• 文件位置: recordings/
        """
        info_label = QLabel(info_text)
        info_label.setStyleSheet(
            "background-color: #e7f3ff; padding: 10px; border-radius: 5px;"
        )
        layout.addWidget(info_label)

        group.setLayout(layout)
        return group

    def create_transcript_panel(self):
        """创建转录显示面板"""
        group = QGroupBox("实时转录")
        layout = QVBoxLayout()

        self.transcript_text = QTextEdit()
        self.transcript_text.setReadOnly(True)
        self.transcript_text.setStyleSheet(
            """
            QTextEdit {
                font-family: 'Courier New';
                font-size: 12px;
                background-color: white;
                border: 1px solid #ddd;
            }
        """
        )

        # 设置字体
        font = QFont("Courier New", 11)
        self.transcript_text.setFont(font)

        # 欢迎文本
        self.transcript_text.setText(
            "准备就绪！\n\n" "点击左边的'开始转录'按钮开始...\n"
        )

        layout.addWidget(self.transcript_text)
        group.setLayout(layout)
        return group

    def start_recording(self):
        """开始录制"""
        if self.is_recording:
            return

        # 加载模型
        model_index = self.model_combo.currentIndex()
        models = ["tiny", "base", "small", "medium", "large"]
        model_name = models[model_index]

        try:
            self.status_label.setText("加载模型中...")
            QApplication.processEvents()

            self.transcriber = WhisperTranscriber(
                model_name=model_name, language="auto"
            )

            # 启动录制
            self.is_recording = True
            self.entry_count = 0
            self.start_time = time.time()

            source = self.source_combo.currentText()
            self.recorder.start_recording(source="mic")

            # 启动转录线程
            self.transcription_thread = TranscriptionThread(
                self.recorder,
                self.transcriber,
                self.logger,
                interval=self.interval_spin.value(),
            )
            self.transcription_thread.transcription_signal.connect(
                self.on_transcription
            )
            self.transcription_thread.error_signal.connect(self.on_error)
            self.transcription_thread.start()

            # 更新UI
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.status_label.setText("录制中...")
            self.status_label.setStyleSheet("color: green; font-weight: bold;")

            self.transcript_text.clear()

            self.logger.start_new_session()

            QMessageBox.information(self, "成功", f"开始录制 (模型: {model_name})")

        except Exception as e:
            QMessageBox.critical(self, "错误", f"启动失败: {str(e)}")
            self.is_recording = False

    def stop_recording(self):
        """停止录制"""
        if not self.is_recording:
            return

        self.is_recording = False
        self.recorder.stop_recording()

        if self.transcription_thread:
            self.transcription_thread.stop()

        # 更新UI
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.status_label.setText("已停止")
        self.status_label.setStyleSheet("color: red;")

        QMessageBox.information(self, "成功", "录制已停止，转录内容已保存")

    def on_transcription(self, data):
        """处理转录结果"""
        timestamp = ""
        if self.show_timestamp_check.isChecked():
            dt = datetime.fromisoformat(data["timestamp"])
            timestamp = f"[{dt.strftime('%H:%M:%S')}] "

        language = ""
        if self.show_language_check.isChecked():
            language = f"[{data['language'].upper()}] "

        text = timestamp + language + data["text"]

        # 添加到文本框
        cursor = self.transcript_text.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.transcript_text.setTextCursor(cursor)
        self.transcript_text.insertPlainText(text + "\n")

        # 自动滚动
        self.transcript_text.ensureCursorVisible()

        self.entry_count += 1
        self.counter_label.setText(f"文本条数: {self.entry_count}")

    def on_error(self, error_msg):
        """处理错误"""
        QMessageBox.warning(self, "转录错误", error_msg)

    def clear_transcript(self):
        """清空转录"""
        if (
            QMessageBox.question(
                self,
                "确认",
                "确定要清空屏幕上的转录内容吗？\n(文件中仍有数据)",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            == QMessageBox.StandardButton.Yes
        ):
            self.transcript_text.clear()
            self.entry_count = 0
            self.counter_label.setText("文本条数: 0")

    def download_transcript(self):
        """下载转录文本"""
        if self.logger.current_file:
            filename = str(self.logger.current_file)
            save_path, _ = QFileDialog.getSaveFileName(
                self, "保存转录文本", filename, "Text Files (*.txt)"
            )

            if save_path:
                import shutil

                try:
                    shutil.copy(filename, save_path)
                    QMessageBox.information(self, "成功", f"文件已保存到: {save_path}")
                except Exception as e:
                    QMessageBox.critical(self, "错误", f"保存失败: {str(e)}")
        else:
            QMessageBox.warning(self, "警告", "没有可下载的文件")

    def update_time(self):
        """更新时间显示"""
        current_time = datetime.now().strftime("%H:%M:%S")
        self.time_label.setText(current_time)

        if self.is_recording and self.start_time:
            elapsed = int(time.time() - self.start_time)
            minutes = elapsed // 60
            seconds = elapsed % 60
            self.status_label.setText(f"录制中... ({minutes:02d}:{seconds:02d})")

    def closeEvent(self, event):
        """关闭窗口事件"""
        if self.is_recording:
            self.stop_recording()

        self.timer.stop()
        if self.transcription_thread and self.transcription_thread.isRunning():
            self.transcription_thread.stop()

        event.accept()


def main():
    """主函数"""
    app = QApplication(sys.argv)

    # 设置全局样式
    app.setStyle("Fusion")

    window = TranscriberApp()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
