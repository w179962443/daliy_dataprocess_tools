# ── 基础镜像：CUDA 12.1 + cuDNN 8 + Ubuntu 22.04 ──────────────
FROM nvidia/cuda:12.1.1-cudnn8-runtime-ubuntu22.04

# 避免交互式提示
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# ── 系统依赖 + FFmpeg ─────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.11 \
    python3.11-dev \
    python3-pip \
    ffmpeg \
    git \
    curl \
    libsndfile1 \
    && ln -sf /usr/bin/python3.11 /usr/bin/python \
    && ln -sf /usr/bin/python3.11 /usr/bin/python3 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# ── 升级 pip ──────────────────────────────────────────────────
RUN pip install --no-cache-dir --upgrade pip

# ── 安装 GPU 版 PyTorch (cu121) ───────────────────────────────
RUN pip install --no-cache-dir \
    torch==2.2.2+cu121 \
    torchaudio==2.2.2+cu121 \
    --index-url https://download.pytorch.org/whl/cu121

# ── 安装 audio_to_text 基础依赖 ───────────────────────────────
RUN pip install --no-cache-dir \
    openai-whisper>=20231117 \
    numpy>=1.24.0 \
    ffmpeg-python>=0.2.0 \
    opencc-python-reimplemented>=0.1.7

# ── 安装 audio_to_text_diarize 依赖 ──────────────────────────
RUN pip install --no-cache-dir \
    whisperx \
    pyannote.audio>=3.1.0

# ── 工作目录 ──────────────────────────────────────────────────
WORKDIR /app

# ── 复制脚本 ──────────────────────────────────────────────────
COPY audio_to_text.py .
COPY audio_to_text_diarize.py .

# ── 挂载点：音频输入 / 模型缓存 / 输出结果 ────────────────────
VOLUME ["/data", "/root/.cache/whisper", "/root/.cache/huggingface"]

# ── 默认命令：显示帮助 ────────────────────────────────────────
CMD ["python", "audio_to_text.py", "--help"]
