# 实时转录软件

一个基于 Whisper 的实时语音转录应用，支持多语言识别和混合语言转录。

## 特性

- 🎙️ **实时转录**: 实时将语音转换为文字
- 🌐 **多语言支持**: 自动检测并支持多种语言
- 🗣️ **混合语言**: 智能识别混合语言和夹杂词汇
- 💾 **自动保存**: 每次会话的转录内容自动保存到文本文件
- ⏱️ **时间戳**: 每条转录内容都记录精确的时间戳
- 🎛️ **灵活配置**: 支持选择不同的 Whisper 模型和音源
- 📊 **统计信息**: 实时显示转录统计和运行时间

## 系统要求

- Python 3.8+
- Windows/Mac/Linux
- 麦克风或系统音频设备

## 安装

### 1. 克隆或下载项目

```bash
cd d:\daliy_dataprocess_tools\realtime_transcriber
```

### 2. 创建虚拟环境 (可选但推荐)

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

**第一次运行会下载 Whisper 模型** (1-3GB，取决于选择的模型)

## 使用

### 启动应用

```bash
python app.py
```

应用将在 `http://localhost:5000` 启动

### Web 界面操作

1. **打开浏览器**: http://localhost:5000
2. **选择设置**:

   - 音源: 麦克风/系统声音/两者
   - 语言: 自动检测或指定语言
   - 模型: 选择精度和速度的平衡

3. **开始转录**: 点击"开始转录"按钮
4. **查看结果**: 转录内容实时显示在屏幕上
5. **停止转录**: 点击"停止转录"按钮
6. **下载文本**: 点击"下载文本"保存为文件

## 文件结构

```
realtime_transcriber/
├── app.py                      # Flask主应用
├── audio_recorder.py           # 音频录制模块
├── whisper_transcriber.py      # Whisper转录模块
├── requirements.txt            # Python依赖
├── recordings/                 # 转录文件保存目录
├── static/                     # 静态资源
└── templates/
    └── index.html              # Web前端界面
```

## 配置说明

编辑 `app.py` 中的 `CONFIG` 部分可以修改:

```python
CONFIG = {
    'sample_rate': 16000,        # 采样率
    'chunk_duration': 0.5,       # 音频块持续时间（秒）
    'model_name': 'base',        # Whisper模型大小
    'language': 'auto',          # 语言设置
    'transcribe_interval': 2,    # 转录间隔（秒）
}
```

### 模型选择

| 模型   | 参数数 | 相对速度 | 精度 |
| ------ | ------ | -------- | ---- |
| tiny   | 39M    | 最快     | 低   |
| base   | 74M    | 快       | 中   |
| small  | 244M   | 中       | 中高 |
| medium | 769M   | 慢       | 高   |
| large  | 1550M  | 最慢     | 最高 |

## 转录文件

转录内容保存到 `recordings/` 目录，文件名格式: `transcription_YYYYMMDD_HHMMSS.txt`

### 文件内容格式

```
============================================================
转录会话开始时间: 2024-01-09 14:30:00
============================================================

[2024-01-09 14:30:05.123] [zh] 你好世界
[2024-01-09 14:30:07.456] [en] Hello
[2024-01-09 14:30:10.789] [zh] 这是一个测试
```

## 音源配置

### Windows 系统

**麦克风** - 默认支持，无需配置

**系统声音** - 需要额外配置:

1. 安装虚拟音频设备 (如 Voicemeeter Banana 或 VB-Audio Virtual Cable)
2. 在 Windows 音频设置中配置立体声混音
3. 在应用中选择对应的设备

### Mac 系统

系统声音录制需要:

1. 安装 BlackHole 或类似虚拟音频设备
2. 在系统偏好设置中配置

### Linux 系统

```bash
# 安装PulseAudio工具
sudo apt-get install pulseaudio pavucontrol

# 启用立体声混音
# 在 pavucontrol 中配置
```

## 多语言和混合语言支持

Whisper 默认支持以下语言:

- 中文 (zh, zh-Hans, zh-Hant)
- 英文 (en)
- 日文 (ja)
- 韩文 (ko)
- 法文 (fr)
- 德文 (de)
- 西班牙文 (es)
- 俄文 (ru)
- 葡萄牙文 (pt)
- ...以及 99 种其他语言

对于**混合语言**，建议:

- ✅ 使用"自动检测"模式
- ✅ 使用更大的模型 (small, medium, large) 获得更好的准确率
- ✅ 如果混合特定两种语言，可以在 `whisper_transcriber.py` 中修改 `language` 参数

## 常见问题

### Q: 麦克风不工作怎么办?

A: 检查:

1. Windows 设置 > 声音 > 输入 中是否启用了麦克风
2. 应用权限 (隐私设置)
3. 是否选择了正确的设备

### Q: 系统声音无法录制

A: 需要安装虚拟音频驱动程序:

- **Windows**: Voicemeeter Banana, VB-Cable
- **Mac**: BlackHole
- **Linux**: PulseAudio 虚拟设备

### Q: 转录不准确

A:

1. 尝试使用更大的模型 (medium 或 large)
2. 确保音频清晰，背景噪音少
3. 指定具体语言而不是自动检测
4. 检查采样率配置

### Q: 模型下载失败

A:

```bash
# 手动下载指定模型
python -c "import whisper; whisper.load_model('base')"

# 或设置代理
pip install -r requirements.txt -i https://pypi.tsinghua.edu.cn/simple
```

### Q: 内存占用过高

A:

1. 使用更小的模型 (tiny 或 base)
2. 增加 `chunk_duration` 的间隔
3. 关闭其他应用释放内存

## 扩展功能建议

### 可以添加的功能:

1. **说话人识别**: 识别不同说话人
2. **实时翻译**: 集成翻译 API
3. **情感分析**: 分析语音情感
4. **命令识别**: 识别特定命令词
5. **自定义词汇**: 添加专业术语字典
6. **数据库存储**: 改为保存到数据库
7. **Web 上传**: 上传和分享转录
8. **批量处理**: 处理音频文件夹

## 性能优化建议

1. **使用 GPU 加速**: 配置 CUDA 实现 GPU 推理

   ```bash
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
   ```

2. **并行处理**: 使用线程池处理多个音频流

3. **增量转录**: 避免重复处理相同音频

## 许可证

MIT

## 支持

如有问题或建议，欢迎反馈！

---

**提示**: 首次运行时会下载 Whisper 模型，请耐心等待。建议使用`base`模型平衡速度和准确率。
