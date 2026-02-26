# 音频转文字工具

使用 OpenAI Whisper 模型将音频文件转换为带时间轴的 CSV 格式文本，支持 GPU 加速和断点续传。

## 功能特点

- ✅ GPU 加速（CUDA）- 显著提升转录速度
- ✅ 支持多种音频格式（mp3, wav, m4a, mp4, flac, ogg等）
- ✅ 自动语言检测或指定语言
- ✅ 多种模型大小可选（速度/准确度平衡）
- ✅ **CSV 格式输出**，包含时间轴信息
- ✅ **断点续传** - 支持从上次位置继续转录
- ✅ **自动繁简转换** - 确保输出简体中文

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

输出：`audio_transcript.csv` （带时间轴的 CSV 文件）

#### Windows 批处理

```bash
audio_to_text.bat audio.mp3
```

#### 指定模型和语言

```bash
# 使用 turbo 模型，指定简体中文（推荐）
python audio_to_text.py audio.wav -m turbo -l zh

# 使用 large 模型，英文
python audio_to_text.py podcast.mp3 -m large -l en

# 自定义输出文件
python audio_to_text.py video.mp4 -m turbo -l zh -o result.csv

# 指定模型存储目录
python audio_to_text.py audio.mp3 -m turbo -l zh -d D:\whisper_models
```

#### 断点续传功能

如果转录被中断或想继续未完成的任务，只需重复运行相同命令：

```bash
# 第一次运行
python audio_to_text.py long_audio.mp3 -m turbo -l zh

# 如果中断，再次运行相同命令，会自动从上次位置继续
python audio_to_text.py long_audio.mp3 -m turbo -l zh
```

程序会自动：

1. 检测输出文件是否存在
2. 读取最后一条记录的结束时间
3. 从该时间点后继续转录
4. 将新内容追加到现有文件

## 命令行参数

```
usage: audio_to_text.py [-h] [-m {tiny,base,small,medium,large,turbo}]
                        [-l LANGUAGE] [-o OUTPUT] [-d MODEL_DIR]
                        [--no-force-simplified]
                        audio_file

参数说明:
  audio_file            音频文件路径
  -m, --model          模型大小 (默认: base)
  -l, --language       语言代码 (zh=简体中文, en=英文, auto=自动检测)
  -o, --output         输出CSV文件路径 (默认: 音频文件名_transcript.csv)
  -d, --model-dir      模型存储目录 (默认: ~/.cache/whisper)
  --no-force-simplified 禁用繁简转换
```

## CSV 输出格式

输出的 CSV 文件包含以下字段：

| 字段            | 说明                      | 示例             |
| --------------- | ------------------------- | ---------------- |
| start_time      | 开始时间（秒）            | 0.0              |
| end_time        | 结束时间（秒）            | 3.5              |
| start_timestamp | 开始时间戳 (HH:MM:SS.mmm) | 00:00:00.000     |
| end_timestamp   | 结束时间戳 (HH:MM:SS.mmm) | 00:00:03.500     |
| duration        | 持续时间（秒）            | 3.5              |
| text            | 转录文本内容              | 大家好，欢迎收听 |

示例 CSV 内容：

```csv
start_time,end_time,start_timestamp,end_timestamp,duration,text
0.0,3.5,00:00:00.000,00:00:03.500,3.5,大家好，欢迎收听本期节目
3.5,8.2,00:00:03.500,00:00:08.200,4.7,今天我们要讲的是人工智能的发展
```

## 模型选择

| 模型      | 速度   | 准确度 | 显存需求 | 适用场景   |
| --------- | ------ | ------ | -------- | ---------- |
| tiny      | 最快   | 较低   | ~1GB     | 快速预览   |
| base      | 快     | 一般   | ~1GB     | 日常使用   |
| small     | 中等   | 良好   | ~2GB     | 平衡选择   |
| medium    | 较慢   | 很好   | ~5GB     | 高质量需求 |
| **turbo** | **快** | **高** | **~6GB** | **推荐⭐** |
| large     | 最慢   | 最好   | ~10GB    | 专业用途   |

**推荐使用 `turbo` 模型**：它提供了速度和准确度的最佳平衡！

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
