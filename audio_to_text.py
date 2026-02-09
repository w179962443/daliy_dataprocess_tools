"""
音频转文字工具 - 使用Whisper模型（GPU加速）
支持多种音频格式，将识别结果保存到文本文件
"""

import whisper
import argparse
import os
from pathlib import Path
import torch


def check_gpu():
    """检查GPU是否可用"""
    if torch.cuda.is_available():
        print(f"✓ GPU可用: {torch.cuda.get_device_name(0)}")
        print(f"✓ CUDA版本: {torch.version.cuda}")
        return True
    else:
        print("⚠ 未检测到GPU，将使用CPU运行（速度较慢）")
        return False


def transcribe_audio(audio_file, model_name="base", language="auto", output_file=None):
    """
    转录音频文件到文本

    Args:
        audio_file: 音频文件路径
        model_name: Whisper模型大小 ('tiny', 'base', 'small', 'medium', 'large')
        language: 语言代码 ('zh', 'en', 'auto'等)
        output_file: 输出文本文件路径（可选）

    Returns:
        转录结果字典
    """
    # 检查音频文件是否存在
    if not os.path.exists(audio_file):
        raise FileNotFoundError(f"音频文件不存在: {audio_file}")

    # 检查GPU
    has_gpu = check_gpu()

    # 加载模型
    print(f"\n正在加载Whisper模型: {model_name}...")
    device = "cuda" if has_gpu else "cpu"
    model = whisper.load_model(model_name, device=device)
    print(f"✓ 模型加载成功! (运行在{device.upper()}上)")

    # 转录音频
    print(f"\n正在转录音频: {audio_file}")
    print("请稍候，这可能需要一些时间...")

    # 设置转录选项
    options = {"fp16": has_gpu, "verbose": False}  # GPU时使用半精度加速

    if language != "auto":
        options["language"] = language

    # 执行转录
    result = model.transcribe(audio_file, **options)

    # 提取转录文本
    text = result["text"]
    detected_language = result.get("language", "未知")

    print(f"\n✓ 转录完成!")
    print(f"检测语言: {detected_language}")
    print(f"文本长度: {len(text)} 字符")

    # 确定输出文件路径
    if output_file is None:
        audio_path = Path(audio_file)
        output_file = audio_path.parent / f"{audio_path.stem}_transcript.txt"

    # 保存到文件
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"音频文件: {audio_file}\n")
        f.write(f"模型: {model_name}\n")
        f.write(f"检测语言: {detected_language}\n")
        f.write(f"{'='*60}\n\n")
        f.write(text)

    print(f"✓ 转录结果已保存到: {output_file}")

    # 打印预览
    print(f"\n文本预览（前200字）:")
    print("-" * 60)
    print(text[:200] + ("..." if len(text) > 200 else ""))
    print("-" * 60)

    return result


def main():
    """命令行主函数"""
    parser = argparse.ArgumentParser(
        description="使用Whisper将音频文件转换为文本（GPU加速）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python audio_to_text.py audio.mp3
  python audio_to_text.py audio.wav -m medium -l zh
  python audio_to_text.py audio.mp4 -m large -o output.txt
  
支持的音频格式:
  mp3, wav, m4a, mp4, flac, ogg, webm等
  
模型大小说明:
  tiny   - 最快，准确度较低（~1GB显存）
  base   - 快速，准确度一般（~1GB显存）
  small  - 中等速度和准确度（~2GB显存）
  medium - 较慢，准确度较高（~5GB显存）
  large  - 最慢，准确度最高（~10GB显存）
        """,
    )

    parser.add_argument("audio_file", help="音频文件路径")
    parser.add_argument(
        "-m",
        "--model",
        default="base",
        choices=["tiny", "base", "small", "medium", "large"],
        help="Whisper模型大小 (默认: base)",
    )
    parser.add_argument(
        "-l",
        "--language",
        default="auto",
        help="语言代码 (zh=中文, en=英文, auto=自动检测, 默认: auto)",
    )
    parser.add_argument(
        "-o", "--output", help="输出文件路径 (默认: 音频文件名_transcript.txt)"
    )

    args = parser.parse_args()

    try:
        # 执行转录
        transcribe_audio(
            audio_file=args.audio_file,
            model_name=args.model,
            language=args.language,
            output_file=args.output,
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
