"""
Flask后端服务 - 实时转录API
"""

from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_cors import CORS
import threading
import time
import numpy as np
from datetime import datetime
from audio_recorder import AudioRecorder
from whisper_transcriber import WhisperTranscriber, TranscriptionLogger
import queue
import json

app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)

# 全局状态
recorder = None
transcriber = None
logger = None
transcription_queue = queue.Queue()
is_running = False
current_session = None

# 配置
CONFIG = {
    "sample_rate": 16000,
    "chunk_duration": 0.5,
    "model_name": "base",  # 可选: 'tiny', 'base', 'small', 'medium', 'large'
    "language": "auto",  # 自动检测语言
    "transcribe_interval": 2,  # 每2秒转录一次
}


def initialize_system():
    """初始化系统组件"""
    global recorder, transcriber, logger

    recorder = AudioRecorder(
        sample_rate=CONFIG["sample_rate"], chunk_duration=CONFIG["chunk_duration"]
    )

    transcriber = WhisperTranscriber(
        model_name=CONFIG["model_name"], language=CONFIG["language"]
    )

    logger = TranscriptionLogger(output_dir="recordings")

    print("系统初始化完成")


def transcription_worker():
    """后台转录工作线程"""
    global is_running, current_session

    logger.start_new_session()
    current_session = logger.get_session_summary()

    last_transcribe_time = 0

    while is_running:
        try:
            current_time = time.time()

            # 定期转录音频
            if current_time - last_transcribe_time > CONFIG["transcribe_interval"]:
                audio_chunk = recorder.get_audio_chunk()

                if audio_chunk is not None and len(audio_chunk) > 0:
                    # 转录
                    result = transcriber.transcribe_audio(audio_chunk)

                    if result.get("text"):
                        # 记录到文件和队列
                        language = result.get("language", "unknown")
                        logger.log_transcription(
                            text=result["text"], language=language, confidence=0.9
                        )

                        # 发送到前端
                        transcription_queue.put(
                            {
                                "type": "transcription",
                                "text": result["text"],
                                "language": language,
                                "timestamp": datetime.now().isoformat(),
                            }
                        )

                    # 清空缓冲区以避免重复转录
                    recorder.clear_buffer()

                last_transcribe_time = current_time

            time.sleep(0.1)

        except Exception as e:
            print(f"转录工作线程错误: {e}")
            transcription_queue.put({"type": "error", "message": str(e)})


@app.route("/")
def index():
    """主页"""
    return render_template("index.html")


@app.route("/api/start", methods=["POST"])
def start_transcription():
    """开始转录"""
    global is_running, recorder

    if is_running:
        return jsonify({"status": "error", "message": "已在运行"})

    try:
        is_running = True
        source = request.json.get("source", "mic")

        # 启动录制
        recorder.start_recording(source=source)

        # 启动转录线程
        worker_thread = threading.Thread(target=transcription_worker, daemon=True)
        worker_thread.start()

        return jsonify(
            {"status": "success", "message": "转录已启动", "session": current_session}
        )

    except Exception as e:
        is_running = False
        return jsonify({"status": "error", "message": str(e)})


@app.route("/api/stop", methods=["POST"])
def stop_transcription():
    """停止转录"""
    global is_running, recorder

    if not is_running:
        return jsonify({"status": "error", "message": "未在运行"})

    try:
        is_running = False
        recorder.stop_recording()

        # 等待线程结束
        time.sleep(1)

        summary = logger.get_session_summary()

        return jsonify(
            {"status": "success", "message": "转录已停止", "summary": summary}
        )

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


@app.route("/api/status")
def get_status():
    """获取当前状态"""
    return jsonify(
        {"is_running": is_running, "current_session": current_session, "config": CONFIG}
    )


@app.route("/api/transcriptions")
def get_transcriptions():
    """获取待发送的转录结果 (Server-Sent Events)"""

    def generate():
        while is_running:
            try:
                # 等待队列中的消息
                if not transcription_queue.empty():
                    data = transcription_queue.get(timeout=1)
                    yield f"data: {json.dumps(data)}\n\n"
                else:
                    yield ": heartbeat\n\n"

                time.sleep(0.1)

            except queue.Empty:
                yield ": heartbeat\n\n"

            except Exception as e:
                yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return app.response_class(
        generate(),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.route("/api/config", methods=["GET", "POST"])
def manage_config():
    """获取或更新配置"""
    global CONFIG

    if request.method == "GET":
        return jsonify(CONFIG)

    if request.method == "POST":
        if is_running:
            return jsonify({"status": "error", "message": "运行中无法修改配置"})

        updates = request.json
        CONFIG.update(updates)
        return jsonify({"status": "success", "config": CONFIG})


@app.route("/api/download/<filename>")
def download_file(filename):
    """下载转录文件"""
    try:
        return send_from_directory("recordings", filename)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 404


@app.route("/api/sessions")
def list_sessions():
    """列出所有转录会话"""
    import os
    from pathlib import Path

    recordings_dir = Path("recordings")
    sessions = []

    for file in recordings_dir.glob("transcription_*.txt"):
        try:
            with open(file, "r", encoding="utf-8") as f:
                content = f.read()
                lines = content.split("\n")
                entry_count = sum(1 for line in lines if line.startswith("["))
        except:
            entry_count = 0

        sessions.append(
            {
                "filename": file.name,
                "created": datetime.fromtimestamp(file.stat().st_ctime).isoformat(),
                "size": file.stat().st_size,
                "entries": entry_count,
            }
        )

    return jsonify(
        {"sessions": sorted(sessions, key=lambda x: x["created"], reverse=True)}
    )


if __name__ == "__main__":
    initialize_system()
    app.run(debug=True, host="0.0.0.0", port=5000, use_reloader=False)
