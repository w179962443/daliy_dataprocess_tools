# 音频转文字工具

使用 OpenAI Whisper 模型将音频文件转换为文本，支持 GPU 加速。

## 功能特点

- ✅ GPU 加速（CUDA）- 显著提升转录速度
- ✅ 支持多种音频格式（mp3, wav, m4a, mp4, flac, ogg等）
- ✅ 自动语言检测或指定语言
- ✅ 多种模型大小可选（速度/准确度平衡）
- ✅ 自动保存转录结果到文本文件

## 快速开始

### 1. 安装依赖

```bash
pip install -r audio_to_text_requirements.txt
```

**注意**: 要使用 GPU 加速，需要：
- NVIDIA GPU（支持 CUDA）
- 已安装 CUDA Toolkit
- 已安装对应版本的 PyTorch（GPU 版本）

安装 GPU 版本的 PyTorch:
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### 2. 安装 FFmpeg

Whisper 需要 FFmpeg 处理音频文件。

**Windows**: 
- 从 [FFmpeg官网](https://ffmpeg.org/download.html) 下载
- 解压并添加到系统 PATH

**或使用 Chocolatey**:
```bash
choco install ffmpeg
```

### 3. 使用方法

#### 基本用法
```bash
python audio_to_text.py audio.mp3
```

#### Windows 批处理
```bash
audio_to_text.bat audio.mp3
```

#### 指定模型和语言
```bash
# 使用 medium 模型，指定中文
python audio_to_text.py audio.wav -m medium -l zh

# 使用 large 模型，英文
python audio_to_text.py podcast.mp3 -m large -l en

# 自定义输出文件
python audio_to_text.py video.mp4 -m small -o transcript.txt
```

## 命令行参数

```
usage: audio_to_text.py [-h] [-m {tiny,base,small,medium,large}] 
                        [-l LANGUAGE] [-o OUTPUT] 
                        audio_file

参数说明:
  audio_file            音频文件路径
  -m, --model          模型大小 (默认: base)
  -l, --language       语言代码 (默认: auto 自动检测)
  -o, --output         输出文件路径 (默认: 音频文件名_transcript.txt)
```

## 模型选择

| 模型    | 速度 | 准确度 | 显存需求 | 适用场景 |
|---------|------|--------|----------|----------|
| tiny    | 最快 | 较低   | ~1GB     | 快速预览 |
| base    | 快   | 一般   | ~1GB     | 日常使用 |
| small   | 中等 | 良好   | ~2GB     | 平衡选择 |
| medium  | 较慢 | 很好   | ~5GB     | 高质量需求 |
| large   | 最慢 | 最好   | ~10GB    | 专业用途 |

## 支持的语言

常用语言代码：
- `zh` - 中文
- `en` - 英文
- `ja` - 日文
- `ko` - 韩文
- `auto` - 自动检测（默认）

完整语言列表请参考 [Whisper 文档](https://github.com/openai/whisper)

## 示例

### 示例1: 转录中文播客
```bash
python audio_to_text.py podcast.mp3 -m medium -l zh
```

### 示例2: 转录英文讲座（高质量）
```bash
python audio_to_text.py lecture.wav -m large -l en -o lecture_notes.txt
```

### 示例3: 快速转录视频音轨
```bash
python audio_to_text.py video.mp4 -m small
```

## 输出格式

输出的文本文件包含：
```
音频文件: audio.mp3
模型: medium
检测语言: zh
============================================================

[转录的文本内容...]
```

## 性能优化

### GPU 加速
- 脚本会自动检测并使用 GPU
- GPU 可以提升 5-10 倍转录速度
- 确保安装了支持 CUDA 的 PyTorch

### 模型选择建议
- 测试/开发: 使用 `tiny` 或 `base`
- 生产环境: 使用 `medium` 或 `large`
- 根据显存大小选择合适的模型

## 故障排除

### FFmpeg 未找到
```
错误: ffmpeg not found
解决: 安装 FFmpeg 并添加到 PATH
```

### CUDA 不可用
```
⚠ 未检测到GPU，将使用CPU运行
解决: 
1. 检查 NVIDIA 驱动
2. 安装 CUDA Toolkit
3. 重新安装 PyTorch GPU 版本
```

### 显存不足
```
错误: CUDA out of memory
解决: 使用更小的模型（如从 large 改为 medium）
```

## 技术细节

- **模型**: OpenAI Whisper
- **框架**: PyTorch
- **加速**: CUDA/cuDNN（GPU）或 CPU
- **音频处理**: FFmpeg

## 相关项目

- [realtime_transcriber](realtime_transcriber/) - 实时语音转文字工具
- [subtitle_translator](subtitle_translator/) - 字幕翻译工具
