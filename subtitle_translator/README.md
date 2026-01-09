# 字幕翻译器

实时屏幕字幕 OCR 识别与翻译工具，支持监控屏幕指定区域，自动识别文字并翻译成中文。

## 功能特点

- 🖼️ **区域选择**: 可视化选择需要监控的屏幕区域
- ⏱️ **智能稳定检测**: 内容稳定指定时间后才进行翻译，避免频繁翻译
- 🔍 **OCR 识别**: 基于 Tesseract OCR 引擎识别屏幕文字
- 🌐 **腾讯云翻译**: 使用腾讯云翻译 API，支持多种语言互译
- 📊 **实时显示**: 实时显示原文和译文

## 安装步骤

### 1. 安装 Python 依赖

```bash
cd subtitle_translator
pip install -r requirements.txt
```

### 2. 安装 Tesseract OCR

**Windows:**

1. 下载 Tesseract 安装包: https://github.com/UB-Mannheim/tesseract/wiki
2. 运行安装程序，建议安装到默认路径 `C:\Program Files\Tesseract-OCR`
3. 安装时选择需要的语言包（中文简体、英文等）

**验证安装:**

```bash
tesseract --version
```

### 3. 配置腾讯云 API 密钥

设置环境变量（必需）：

**Windows PowerShell:**

```powershell
# 临时设置（仅当前会话）
$env:TENCENT_SECRET_ID = "你的SecretId"
$env:TENCENT_SECRET_KEY = "你的SecretKey"

# 永久设置
[System.Environment]::SetEnvironmentVariable('TENCENT_SECRET_ID', '你的SecretId', 'User')
[System.Environment]::SetEnvironmentVariable('TENCENT_SECRET_KEY', '你的SecretKey', 'User')
```

**获取 API 密钥:**

1. 访问腾讯云控制台: https://console.cloud.tencent.com/cam/capi
2. 创建或查看 API 密钥
3. 记录 SecretId 和 SecretKey

## 使用方法

### 启动程序

```bash
python app.py
```

### 操作步骤

1. **选择区域**

   - 点击"选择区域"按钮
   - 主窗口会隐藏，出现半透明遮罩
   - 用鼠标拖拽选择需要监控的屏幕区域
   - 释放鼠标完成选择

2. **配置参数**（可选）

   - **稳定持续时间**: 内容需要保持不变的时间（默认 2 秒）
   - **捕获间隔**: 截图检测的时间间隔（默认 0.3 秒）

3. **开始监控**

   - 点击"开始监控"按钮
   - 程序将持续监控选定区域
   - 当内容稳定后自动识别并翻译

4. **查看结果**

   - 原文和译文会实时显示在界面下方
   - 状态栏显示翻译状态和字符用量

5. **停止监控**
   - 点击"停止监控"按钮即可停止

## 配置说明

编辑 `config.py` 可以修改默认配置：

```python
# 稳定性检测配置
STABLE_DURATION = 2.0  # 内容稳定持续时间（秒）
CAPTURE_INTERVAL = 0.3  # 截图间隔（秒）

# 翻译配置
SOURCE_LANG = 'auto'  # 源语言（auto为自动识别）
TARGET_LANG = 'zh'  # 目标语言（zh为中文）

# OCR配置
OCR_LANGUAGE = 'chi_sim+eng'  # OCR语言（中文简体+英文）
```

## 项目结构

```
subtitle_translator/
├── app.py                    # GUI主程序
├── config.py                 # 配置文件
├── translator.py             # 腾讯云翻译客户端
├── screen_ocr.py             # 屏幕OCR识别模块
├── stability_detector.py     # 内容稳定性检测器
├── requirements.txt          # Python依赖
└── README.md                 # 说明文档
```

## 技术架构

- **GUI 框架**: PyQt5
- **OCR 引擎**: Tesseract OCR + pytesseract
- **图像处理**: OpenCV, Pillow
- **翻译 API**: 腾讯云机器翻译 TMT
- **多线程**: QThread 实现后台监控

## 常见问题

### 1. OCR 识别不准确

- 确保选择的屏幕区域清晰、字体大小适中
- 尝试调整区域大小，避免包含过多背景
- 检查 Tesseract 是否正确安装语言包

### 2. 翻译 API 报错

- 确认已正确设置环境变量 `TENCENT_SECRET_ID` 和 `TENCENT_SECRET_KEY`
- 检查腾讯云账户余额和 API 权限
- 查看腾讯云控制台是否开通了机器翻译服务

### 3. 程序无法启动

- 确认所有依赖已正确安装: `pip install -r requirements.txt`
- 确认 Tesseract OCR 已正确安装
- 检查 Python 版本（建议 3.7+）

### 4. 识别速度慢

- 减小监控区域大小
- 增加 `CAPTURE_INTERVAL` 值减少检测频率
- 关闭不必要的后台程序

## 使用场景

- 观看外语视频时实时翻译字幕
- 翻译游戏内对话文本
- 翻译不可复制的屏幕文字
- 实时会议字幕翻译

## 注意事项

- 腾讯云翻译 API 按字符计费，请注意用量
- 建议合理设置稳定持续时间，避免频繁翻译
- 确保有足够的屏幕空间显示翻译窗口
- OCR 识别效果取决于原文清晰度

## 许可证

本项目仅供学习和个人使用。

## 支持的翻译语言

根据腾讯云文档，支持的语言对包括：

- 中文 ↔️ 英语、日语、韩语、法语、西班牙语等
- 英语 ↔️ 多种语言
- 自动检测源语言

详见腾讯云翻译文档: https://cloud.tencent.com/document/product/551
