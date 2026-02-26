"""
音频转文字工具 - 使用Whisper模型（GPU加速）
支持多种音频格式，将识别结果保存到带时间轴的CSV文件
支持断点续传功能
"""

import whisper
import argparse
import os
from pathlib import Path
import torch
import csv
from datetime import timedelta

# 尝试导入繁简转换库（可选）
try:
    from opencc import OpenCC

    cc = OpenCC("t2s")  # 繁体转简体
    HAS_OPENCC = True
except ImportError:
    HAS_OPENCC = False
    try:
        import zhconv

        HAS_ZHCONV = True
    except ImportError:
        HAS_ZHCONV = False


def convert_to_simplified(text):
    """将文本转换为简体中文"""
    if HAS_OPENCC:
        return cc.convert(text)
    elif HAS_ZHCONV:
        return zhconv.convert(text, "zh-cn")
    else:
        return text


def format_timestamp(seconds):
    """将秒数转换为时:分:秒.毫秒格式"""
    td = timedelta(seconds=seconds)
    hours = td.seconds // 3600
    minutes = (td.seconds % 3600) // 60
    secs = td.seconds % 60
    millis = td.microseconds // 1000
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"


def read_last_timestamp(csv_file):
    """读取CSV文件中最后一条记录的结束时间"""
    if not os.path.exists(csv_file):
        return 0.0

    try:
        with open(csv_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            if rows:
                last_row = rows[-1]
                return float(last_row["end_time"])
    except Exception as e:
        print(f"⚠ 读取现有文件失败: {e}")

    return 0.0


def check_gpu():
    """检查GPU是否可用"""
    if torch.cuda.is_available():
        print(f"✓ GPU可用: {torch.cuda.get_device_name(0)}")
        print(f"✓ CUDA版本: {torch.version.cuda}")
        return True
    else:
        print("⚠ 未检测到GPU，将使用CPU运行（速度较慢）")
        return False


def transcribe_audio(
    audio_file,
    model_name="base",
    language="auto",
    output_file=None,
    model_dir=None,
    force_simplified=True,
):
    """
    转录音频文件到CSV格式（带时间轴），支持断点续传

    Args:
        audio_file: 音频文件路径
        model_name: Whisper模型大小 ('tiny', 'base', 'small', 'medium', 'large', 'turbo')
        language: 语言代码 ('zh', 'en', 'auto'等)
        output_file: 输出CSV文件路径（可选）
        model_dir: 模型存储位置（可选）
        force_simplified: 强制转换为简体中文（默认: True）

    Returns:
        转录结果字典
    """
    # 检查音频文件是否存在
    if not os.path.exists(audio_file):
        raise FileNotFoundError(f"音频文件不存在: {audio_file}")

    # 确定输出文件路径
    if output_file is None:
        audio_path = Path(audio_file)
        output_file = audio_path.parent / f"{audio_path.stem}_transcript.csv"

    # 检查是否存在现有文件（断点续传）
    last_timestamp = read_last_timestamp(output_file)
    is_resume = last_timestamp > 0

    if is_resume:
        print("\n✓ 检测到现有转录文件")
        print(f"✓ 上次转录到: {format_timestamp(last_timestamp)}")
        print("✓ 将从该位置继续转录...")
    else:
        print("\n✓ 开始新的转录任务")

    # 检查GPU
    has_gpu = check_gpu()

    # 加载模型
    print(f"\n正在加载Whisper模型: {model_name}...")
    if model_dir:
        print(f"模型目录: {model_dir}")
    device = "cuda" if has_gpu else "cpu"
    model = whisper.load_model(model_name, device=device, download_root=model_dir)
    print(f"✓ 模型加载成功! (运行在{device.upper()}上)")

    # 转录音频
    print(f"\n正在转录音频: {audio_file}")
    print("请稍候，这可能需要一些时间...")

    # 设置转录选项
    options = {"fp16": has_gpu, "verbose": False}  # GPU时使用半精度加速

    if language != "auto":
        options["language"] = language

    # 如果是中文，添加简体中文提示以引导模型输出简体
    if language == "zh" or (language == "auto" and "zh" in str(language)):
        options["initial_prompt"] = "以下是简体中文的转录内容："

    # 执行转录
    result = model.transcribe(audio_file, **options)

    # 提取分段信息
    segments = result["segments"]
    detected_language = result.get("language", "未知")

    print("\n✓ 转录完成!")
    print(f"检测语言: {detected_language}")
    print(f"总分段数: {len(segments)}")

    # 过滤已转录的分段（断点续传）
    new_segments = [seg for seg in segments if seg["end"] > last_timestamp]

    if is_resume:
        print(f"已跳过分段: {len(segments) - len(new_segments)}")
        print(f"新增分段: {len(new_segments)}")

    if not new_segments:
        print("\n✓ 没有新内容需要转录")
        return result

    # 处理分段文本（繁简转换）
    processed_segments = []
    for seg in new_segments:
        text = seg["text"].strip()

        # 如果是中文且需要强制转换为简体
        if force_simplified and detected_language == "zh":
            text = convert_to_simplified(text)

        processed_segments.append(
            {
                "start_time": seg["start"],
                "end_time": seg["end"],
                "start_timestamp": format_timestamp(seg["start"]),
                "end_timestamp": format_timestamp(seg["end"]),
                "duration": seg["end"] - seg["start"],
                "text": text,
            }
        )

    if force_simplified and detected_language == "zh":
        if HAS_OPENCC or HAS_ZHCONV:
            print("✓ 已转换为简体中文")
        else:
            msg = "⚠ 未安装繁简转换库，建议安装: "
            msg += "pip install opencc-python-reimplemented"
            print(msg)

    # 写入CSV文件
    file_exists = os.path.exists(output_file)
    mode = "a" if file_exists else "w"

    with open(output_file, mode, encoding="utf-8-sig", newline="") as f:
        fieldnames = [
            "start_time",
            "end_time",
            "start_timestamp",
            "end_timestamp",
            "duration",
            "text",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        # 如果是新文件，写入表头
        if not file_exists:
            writer.writeheader()

        # 写入所有新分段
        for seg in processed_segments:
            writer.writerow(seg)

    print(f"\n✓ 转录结果已保存到: {output_file}")
    print(f"✓ 新增记录: {len(processed_segments)} 条")

    # 打印预览
    print("\n最近3条记录预览:")
    print("-" * 80)
    for seg in processed_segments[-3:]:
        text_preview = seg["text"][:50]
        if len(seg["text"]) > 50:
            text_preview += "..."
        start_ts = seg["start_timestamp"]
        end_ts = seg["end_timestamp"]
        print(f"[{start_ts} --> {end_ts}] {text_preview}")
    print("-" * 80)

    return result


def main():
    """命令行主函数"""
    parser = argparse.ArgumentParser(
        description="使用Whisper将音频文件转换为带时间轴的CSV文本（GPU加速，支持断点续传）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python audio_to_text.py audio.mp3
  python audio_to_text.py audio.wav -m turbo -l zh
  python audio_to_text.py audio.mp4 -m large -l zh -o output.csv
  python audio_to_text.py audio.mp3 -m turbo -l zh -d D:\\whisper_models
  
断点续传:
  如果输出文件已存在，会自动从上次转录的位置继续
  重复运行相同命令即可继续未完成的转录任务
  
输出格式 (CSV):
  start_time      - 开始时间（秒）
  end_time        - 结束时间（秒）
  start_timestamp - 开始时间戳 (HH:MM:SS.mmm)
  end_timestamp   - 结束时间戳 (HH:MM:SS.mmm)
  duration        - 持续时间（秒）
  text            - 转录文本内容
  
支持的音频格式:
  mp3, wav, m4a, mp4, flac, ogg, webm等
  
模型大小说明:
  tiny   - 最快，准确度较低（~1GB显存）
  base   - 快速，准确度一般（~1GB显存）
  small  - 中等速度和准确度（~2GB显存）
  medium - 较慢，准确度较高（~5GB显存）
  large  - 最慢，准确度最高（~10GB显存）
  turbo  - 速度快，准确度高（~6GB显存，推荐）
  
语言代码说明:
  zh    - 简体中文
  en    - 英文
  auto  - 自动检测语言
        """,
    )

    parser.add_argument("audio_file", help="音频文件路径")
    parser.add_argument(
        "-m",
        "--model",
        default="base",
        choices=["tiny", "base", "small", "medium", "large", "turbo"],
        help="Whisper模型大小 (默认: base)",
    )
    parser.add_argument(
        "-l",
        "--language",
        default="auto",
        help="语言代码 (zh=中文, en=英文, auto=自动检测, 默认: auto)",
    )
    parser.add_argument(
        "-o", "--output", help="输出CSV文件路径 (默认: 音频文件名_transcript.csv)"
    )
    parser.add_argument(
        "-d", "--model-dir", help="模型存储目录 (默认: ~/.cache/whisper)"
    )
    parser.add_argument(
        "--no-force-simplified", action="store_true", help="禁用繁简转换，保留原始输出"
    )

    args = parser.parse_args()

    try:
        # 执行转录
        transcribe_audio(
            audio_file=args.audio_file,
            model_name=args.model,
            language=args.language,
            output_file=args.output,
            model_dir=args.model_dir,
            force_simplified=not args.no_force_simplified,
        )
        print("\n✓ 任务完成!")

    except KeyboardInterrupt:
        print("\n\n⚠ 用户中断")
    except Exception as e:
        print(f"\n✗ 错误: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
