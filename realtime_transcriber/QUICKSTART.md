# 快速开始指南

## 五分钟快速上手

### 第 1 步: 安装依赖

打开终端/命令行，进入项目目录:

```bash
cd d:\daliy_dataprocess_tools\realtime_transcriber
```

安装 Python 依赖:

```bash
# 推荐使用国内镜像加速
pip install -r requirements.txt -i https://pypi.tsinghua.edu.cn/simple
```

**等待安装完成** (第一次会下载 Whisper 模型，约 1-3GB)

### 第 2 步: 选择启动方式

#### 方案 A: Web 版本 (推荐)

```bash
python app.py
```

然后打开浏览器访问: **http://localhost:5000**

#### 方案 B: 桌面版本 (PyQt)

```bash
pip install PyQt6
python app_pyqt.py
```

#### 方案 C: Windows 一键启动

双击运行 `run.bat` 文件

### 第 3 步: 开始转录

1. 选择音源 (麦克风/系统声音)
2. 选择语言 (建议自动检测)
3. 点击"开始转录" ▶️
4. 说话！转录内容会实时显示
5. 点击"停止转录" ⏹️ 完成

### 第 4 步: 查看结果

转录内容自动保存在 `recordings/` 文件夹

文件格式: `transcription_YYYYMMDD_HHMMSS.txt`

可以在 Web 界面点击"下载文本"导出

---

## 常见问题速查

### 问: 麦克风没反应?

**检查清单:**

- ✓ Windows 设置 > 隐私 > 麦克风 (启用)
- ✓ 物理麦克风是否接好
- ✓ 音量是否静音
- ✓ 其他应用是否占用麦克风

### 问: 安装特别慢?

用国内镜像:

```bash
pip install -r requirements.txt -i https://pypi.tsinghua.edu.cn/simple
```

或选择更小的模型 (tiny):

```bash
# 编辑 config.py，改为:
'model_name': 'tiny'  # 最小 39M
```

### 问: 模型下载失败?

手动下载:

```bash
python -c "import whisper; whisper.load_model('base')"
```

### 问: 识别不准确?

- 使用更大模型 (medium/large)
- 确保麦克风清晰
- 指定具体语言而不是自动检测
- 减少背景噪音

### 问: 内存占用过高?

- 改用 'tiny' 模型
- 关闭其他应用
- 增加转录间隔 (在 config.py)

---

## 核心概念

### 模型大小对比

| 模型   | 大小 | 速度   | 准确率     |
| ------ | ---- | ------ | ---------- |
| tiny   | 39M  | 🚀🚀🚀 | ⭐         |
| base   | 74M  | 🚀🚀   | ⭐⭐       |
| small  | 244M | 🚀     | ⭐⭐⭐     |
| medium | 769M | 🐢     | ⭐⭐⭐⭐   |
| large  | 1.5G | 🐢🐢   | ⭐⭐⭐⭐⭐ |

**建议:** 选 base 或 small，速度和准确率平衡最好

### 语言支持

- 🇨🇳 中文 (简体/繁体)
- 🇬🇧 English
- 🇯🇵 日本語
- 🇰🇷 한국어
- 🇫🇷 Français
- 🇩🇪 Deutsch
- 🇪🇸 Español
- ...等 99 种语言

**混合语言:** 选"自动检测"可识别中文+英文等混合

### 转录结果保存位置

```
recordings/
├── transcription_20240109_143000.txt
├── transcription_20240109_151530.txt
└── ...
```

每个文件内容:

```
[2024-01-09 14:30:05.123] [zh] 你好
[2024-01-09 14:30:07.456] [en] Hello
[2024-01-09 14:30:10.789] [zh] 世界
```

---

## 进阶配置

### 修改 model 和语言

编辑 `config.py`:

```python
WHISPER_CONFIG = {
    'model_name': 'small',      # 改为 small 模型
    'language': 'zh',           # 指定中文
    'transcribe_interval': 2,
}
```

### GPU 加速 (快 10 倍+)

如果有 NVIDIA GPU:

```bash
# 安装CUDA版PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# 编辑 config.py
'use_gpu': True
```

### 系统声音录制 (Windows)

1. 安装 Voicemeeter Banana (免费)
2. 启用"立体声混音"
3. 在应用中选择 WASAPI 设备

---

## 文件说明

| 文件                   | 说明             |
| ---------------------- | ---------------- |
| app.py                 | Web 版本主程序   |
| app_pyqt.py            | 桌面版本主程序   |
| audio_recorder.py      | 音频录制模块     |
| whisper_transcriber.py | Whisper 转录模块 |
| config.py              | 配置文件         |
| requirements.txt       | Python 依赖列表  |
| run.py                 | Python 启动脚本  |
| run.bat                | Windows 启动脚本 |
| templates/index.html   | Web 界面         |
| recordings/            | 转录文件保存目录 |

---

## 获取帮助

### 查看日志

Web 版本在启动时会显示详细日志:

```
[日期 时间] 加载Whisper模型: base
[日期 时间] 模型加载成功!
[日期 时间] 系统初始化完成
```

### 常用命令

```bash
# 查看Python版本
python --version

# 查看已安装包
pip list

# 升级pip
python -m pip install --upgrade pip

# 卸载重装
pip uninstall -r requirements.txt -y
pip install -r requirements.txt

# 清理缓存
pip cache purge
```

### 联系反馈

遇到问题? 可以尝试:

1. 重启应用
2. 重新安装依赖
3. 更新 Python 版本
4. 检查麦克风设置
5. 尝试更小的模型

---

**祝你使用愉快! 🎉**

有任何问题欢迎反馈和改进建议!
