# 快速开始指南

## 第一次使用

### 1. 安装依赖

```bash
# 进入项目目录
cd subtitle_translator

# 安装Python依赖
pip install -r requirements.txt
```

### 2. 安装 Tesseract OCR

- **下载地址**: https://github.com/UB-Mannheim/tesseract/wiki
- **推荐版本**: 5.0 或更高
- **安装路径**: 建议使用默认路径 `C:\Program Files\Tesseract-OCR`
- **语言包**: 安装时选择 "Chinese (Simplified)" 和 "English"

### 3. 配置腾讯云 API 密钥

在 PowerShell 中执行：

```powershell
# 设置环境变量（永久）
[System.Environment]::SetEnvironmentVariable('TENCENT_SECRET_ID', '你的SecretId', 'User')
[System.Environment]::SetEnvironmentVariable('TENCENT_SECRET_KEY', '你的SecretKey', 'User')

# 重启终端或重新登录后生效
```

**获取密钥**: https://console.cloud.tencent.com/cam/capi

### 4. 运行程序

双击运行 `run.bat` 或在命令行执行：

```bash
python app.py
```

## 基本使用流程

1. 点击 **"选择区域"** → 拖拽鼠标选择屏幕监控区域
2. 调整 **"稳定持续时间"** （默认 2 秒）
3. 点击 **"开始监控"**
4. 在下方查看实时翻译结果
5. 完成后点击 **"停止监控"**

## 常见使用场景

### 场景 1: 翻译视频字幕

1. 播放外语视频
2. 选择字幕显示区域
3. 设置稳定时间为 2-3 秒
4. 开始监控

### 场景 2: 翻译游戏对话

1. 启动游戏
2. 选择对话框区域
3. 设置稳定时间为 1.5-2 秒
4. 开始监控

### 场景 3: 翻译网页文字

1. 打开网页
2. 选择需要翻译的文字区域
3. 开始监控

## 最佳实践

✅ **选区建议**

- 选择区域尽量小，仅包含文字内容
- 避免包含过多背景和无关元素
- 确保文字清晰、对比度高

✅ **参数调优**

- 字幕变化快 → 降低稳定时间（1-1.5 秒）
- 字幕变化慢 → 保持默认（2 秒）
- 性能优化 → 增加捕获间隔（0.5 秒）

✅ **费用控制**

- 合理设置稳定时间，避免频繁翻译
- 不用时及时停止监控
- 腾讯云翻译按字符计费

## 故障排查

❌ **无法识别文字**

- 检查 Tesseract 是否正确安装
- 确认已安装对应语言包
- 尝试放大字体或调整选区

❌ **翻译失败**

- 确认环境变量已设置
- 检查网络连接
- 验证腾讯云账户余额

❌ **程序启动失败**

- 确认依赖已安装完整
- 检查 Python 版本（需要 3.7+）
- 查看错误信息

## 下一步

- 阅读完整 [README.md](README.md) 了解更多功能
- 修改 [config.py](config.py) 自定义配置
- 查看腾讯云翻译文档了解更多语言支持

---

**需要帮助?** 检查 README.md 的"常见问题"部分
