"""
音频转文字工具（含说话人识别）- 使用 WhisperX + pyannote.audio
支持多种音频格式，输出带时间轴和说话人标签的 CSV 文件
支持断点续传功能

依赖安装:
    pip install whisperx
    pip install pyannote.audio

说话人识别需要 HuggingFace Token:
    1. 注册 https://huggingface.co
    2. 申请访问 https://huggingface.co/pyannote/speaker-diarization-3.1
    3. 在 https://huggingface.co/settings/tokens 生成 token
    4. 通过 -t 参数传入，或设置环境变量 HF_TOKEN
"""

import argparse
import csv
import os
from datetime import timedelta
from pathlib import Path

# 尝试导入繁简转换库（可选）
try:
    from opencc import OpenCC

    cc = OpenCC("t2s")
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
    return text


def format_timestamp(seconds):
    """将秒数转换为 HH:MM:SS.mmm 格式"""
    td = timedelta(seconds=float(seconds))
    total_secs = int(td.total_seconds())
    hours = total_secs // 3600
    minutes = (total_secs % 3600) // 60
    secs = total_secs % 60
    millis = round((float(seconds) - int(float(seconds))) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"


def read_last_timestamp(csv_file):
    """读取 CSV 文件中最后一条记录的结束时间"""
    if not os.path.exists(csv_file):
        return 0.0
    try:
        with open(csv_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            if rows:
                return float(rows[-1]["end_time"])
    except Exception as e:
        print(f"⚠ 读取现有文件失败: {e}")
    return 0.0


def check_gpu():
    """检查 GPU 是否可用"""
    try:
        import torch

        if torch.cuda.is_available():
            print(f"✓ GPU可用: {torch.cuda.get_device_name(0)}")
            print(f"✓ CUDA版本: {torch.version.cuda}")
            return True
    except ImportError:
        pass
    print("⚠ 未检测到GPU，将使用CPU运行（速度较慢）")
    return False


def transcribe_with_diarization(
    audio_file,
    model_name="turbo",
    language="zh",
    output_file=None,
    model_dir=None,
    hf_token=None,
    min_speakers=None,
    max_speakers=None,
    force_simplified=True,
):
    """
    使用 WhisperX 转录音频并进行说话人识别

    Args:
        audio_file:      音频文件路径
        model_name:      WhisperX 模型大小
        language:        语言代码 ('zh', 'en', 'auto' 等)
        output_file:     输出 CSV 文件路径（可选）
        model_dir:       模型存储目录（可选）
        hf_token:        HuggingFace Token（说话人识别必需）
        min_speakers:    最少说话人数（可选）
        max_speakers:    最多说话人数（可选）
        force_simplified: 强制转换为简体中文（默认: True）
    """
    try:
        import whisperx
    except ImportError:
        raise ImportError("未安装 whisperx，请运行: pip install whisperx")

    if not os.path.exists(audio_file):
        raise FileNotFoundError(f"音频文件不存在: {audio_file}")

    # 确定输出文件路径
    if output_file is None:
        audio_path = Path(audio_file)
        output_file = audio_path.parent / f"{audio_path.stem}_diarize.csv"

    # 断点续传检测
    last_timestamp = read_last_timestamp(output_file)
    is_resume = last_timestamp > 0

    if is_resume:
        print("\n✓ 检测到现有转录文件")
        print(f"✓ 上次转录到: {format_timestamp(last_timestamp)}")
        print("✓ 将从该位置继续转录...")
    else:
        print("\n✓ 开始新的转录任务")

    has_gpu = check_gpu()
    device = "cuda" if has_gpu else "cpu"
    compute_type = "float16" if has_gpu else "int8"

    # ── Step 1: 加载模型并转录 ──────────────────────────────────
    print(f"\n正在加载 WhisperX 模型: {model_name}...")
    if model_dir:
        print(f"模型目录: {model_dir}")

    lang = None if language == "auto" else language
    model = whisperx.load_model(
        model_name,
        device,
        compute_type=compute_type,
        language=lang,
        download_root=model_dir,
    )

    print(f"✓ 模型加载成功! (运行在 {device.upper()} 上)")
    print(f"\n正在加载音频: {audio_file}")
    audio = whisperx.load_audio(audio_file)

    print("正在转录，请稍候...")
    transcribe_options = {"batch_size": 16}
    if language == "zh":
        transcribe_options["initial_prompt"] = "以下是简体中文的转录内容："

    result = model.transcribe(audio, **transcribe_options)
    detected_language = result.get("language", language or "unknown")
    print(f"✓ 转录完成! 检测语言: {detected_language}，共 {len(result['segments'])} 段")

    # ── Step 2: 时间戳对齐 ─────────────────────────────────────
    print("\n正在对齐时间戳...")
    try:
        align_lang = detected_language if detected_language != "unknown" else "en"
        model_a, metadata = whisperx.load_align_model(
            language_code=align_lang, device=device
        )
        result = whisperx.align(
            result["segments"],
            model_a,
            metadata,
            audio,
            device,
            return_char_alignments=False,
        )
        print("✓ 时间戳对齐完成")
    except Exception as e:
        print(f"⚠ 时间戳对齐失败（将使用原始时间戳）: {e}")

    # ── Step 3: 说话人分离 ─────────────────────────────────────
    if hf_token:
        print("\n正在进行说话人分离...")
        try:
            diarize_kwargs = {"audio": audio}
            if min_speakers:
                diarize_kwargs["min_speakers"] = min_speakers
            if max_speakers:
                diarize_kwargs["max_speakers"] = max_speakers

            diarize_model = whisperx.DiarizationPipeline(
                use_auth_token=hf_token, device=device
            )
            diarize_segments = diarize_model(**diarize_kwargs)
            result = whisperx.assign_word_speakers(diarize_segments, result)
            print("✓ 说话人分离完成")
        except Exception as e:
            print(f"⚠ 说话人分离失败: {e}")
            print("  将继续保存转录结果，但不含说话人信息")
    else:
        print("\n⚠ 未提供 HuggingFace Token，跳过说话人分离")
        print("  使用 -t YOUR_TOKEN 参数启用说话人识别")

    # ── Step 4: 处理分段并写入 CSV ─────────────────────────────
    segments = result.get("segments", [])
    new_segments = [seg for seg in segments if seg["end"] > last_timestamp]

    if is_resume:
        skipped = len(segments) - len(new_segments)
        print(f"\n已跳过分段: {skipped}，新增分段: {len(new_segments)}")

    if not new_segments:
        print("\n✓ 没有新内容需要转录")
        return result

    processed = []
    for seg in new_segments:
        text = seg.get("text", "").strip()
        if force_simplified and detected_language == "zh":
            text = convert_to_simplified(text)

        speaker = seg.get("speaker", "UNKNOWN")
        processed.append(
            {
                "start_time": seg["start"],
                "end_time": seg["end"],
                "start_timestamp": format_timestamp(seg["start"]),
                "end_timestamp": format_timestamp(seg["end"]),
                "duration": round(seg["end"] - seg["start"], 3),
                "speaker": speaker,
                "text": text,
            }
        )

    if force_simplified and detected_language == "zh":
        if HAS_OPENCC or HAS_ZHCONV:
            print("✓ 已转换为简体中文")
        else:
            print(
                "⚠ 未安装繁简转换库，建议安装: pip install opencc-python-reimplemented"
            )

    file_exists = os.path.exists(output_file)
    mode = "a" if file_exists else "w"

    with open(output_file, mode, encoding="utf-8-sig", newline="") as f:
        fieldnames = [
            "start_time",
            "end_time",
            "start_timestamp",
            "end_timestamp",
            "duration",
            "speaker",
            "text",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        for seg in processed:
            writer.writerow(seg)

    print(f"\n✓ 结果已保存到: {output_file}")
    print(f"✓ 新增记录: {len(processed)} 条")

    # 预览最近 3 条
    print("\n最近3条记录预览:")
    print("-" * 90)
    for seg in processed[-3:]:
        preview = seg["text"][:45] + ("..." if len(seg["text"]) > 45 else "")
        print(
            f"[{seg['speaker']}] "
            f"{seg['start_timestamp']} --> {seg['end_timestamp']}  "
            f"{preview}"
        )
    print("-" * 90)

    return result


def main():
    parser = argparse.ArgumentParser(
        description="WhisperX 音频转文字（含说话人识别），输出带时间轴的 CSV",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 仅转录（无说话人识别）
  python audio_to_text_diarize.py audio.mp3 -m turbo -l zh

  # 完整功能（含说话人识别）
  python audio_to_text_diarize.py audio.mp3 -m turbo -l zh -t hf_xxxx

  # 指定说话人数量（提高准确率）
  python audio_to_text_diarize.py audio.mp3 -m turbo -l zh -t hf_xxxx --min-speakers 2 --max-speakers 2

  # 指定输出文件和模型目录
  python audio_to_text_diarize.py audio.mp3 -m turbo -l zh -t hf_xxxx -o result.csv -d D:\\models

断点续传:
  输出文件已存在时，自动从上次位置继续，重复运行相同命令即可

输出 CSV 字段:
  start_time      开始时间（秒）
  end_time        结束时间（秒）
  start_timestamp 开始时间戳 HH:MM:SS.mmm
  end_timestamp   结束时间戳 HH:MM:SS.mmm
  duration        持续时间（秒）
  speaker         说话人标签（如 SPEAKER_00、SPEAKER_01）
  text            转录文本

获取 HuggingFace Token:
  1. 注册 https://huggingface.co
  2. 申请访问 https://huggingface.co/pyannote/speaker-diarization-3.1
  3. 生成 token: https://huggingface.co/settings/tokens
        """,
    )

    parser.add_argument("audio_file", help="音频文件路径")
    parser.add_argument(
        "-m",
        "--model",
        default="turbo",
        choices=["tiny", "base", "small", "medium", "large", "turbo"],
        help="WhisperX 模型大小 (默认: turbo)",
    )
    parser.add_argument(
        "-l",
        "--language",
        default="zh",
        help="语言代码 (zh=简体中文, en=英文, auto=自动检测, 默认: zh)",
    )
    parser.add_argument(
        "-t",
        "--token",
        default=os.environ.get("HF_TOKEN"),
        help="HuggingFace Token（说话人识别必需，也可设置环境变量 HF_TOKEN）",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="输出 CSV 文件路径 (默认: 音频文件名_diarize.csv)",
    )
    parser.add_argument(
        "-d",
        "--model-dir",
        help="模型存储目录 (默认: ~/.cache/whisper)",
    )
    parser.add_argument(
        "--min-speakers",
        type=int,
        default=None,
        help="最少说话人数（可选，提高识别准确率）",
    )
    parser.add_argument(
        "--max-speakers",
        type=int,
        default=None,
        help="最多说话人数（可选，提高识别准确率）",
    )
    parser.add_argument(
        "--no-force-simplified",
        action="store_true",
        help="禁用繁简转换，保留原始输出",
    )

    args = parser.parse_args()

    try:
        transcribe_with_diarization(
            audio_file=args.audio_file,
            model_name=args.model,
            language=args.language,
            output_file=args.output,
            model_dir=args.model_dir,
            hf_token=args.token,
            min_speakers=args.min_speakers,
            max_speakers=args.max_speakers,
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
