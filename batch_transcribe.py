"""
批量音频/视频转文字工具
遍历指定目录下所有音视频文件，逐个调用 audio_to_text.py 进行转录
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

# 支持的音视频扩展名
AUDIO_VIDEO_EXTENSIONS = {
    ".mp3",
    ".wav",
    ".m4a",
    ".flac",
    ".ogg",
    ".webm",
    ".aac",
    ".wma",
    ".mp4",
    ".mkv",
    ".avi",
    ".mov",
    ".wmv",
    ".flv",
    ".ts",
    ".m4v",
}

# 当前脚本所在目录，用于定位 audio_to_text.py
SCRIPT_DIR = Path(__file__).parent
TRANSCRIBE_SCRIPT = SCRIPT_DIR / "audio_to_text.py"


def find_media_files(directory, recursive=False):
    """遍历目录，返回所有音视频文件路径列表"""
    directory = Path(directory)
    if not directory.exists():
        raise FileNotFoundError(f"目录不存在: {directory}")
    if not directory.is_dir():
        raise NotADirectoryError(f"路径不是目录: {directory}")

    pattern = "**/*" if recursive else "*"
    files = [
        f
        for f in directory.glob(pattern)
        if f.is_file() and f.suffix.lower() in AUDIO_VIDEO_EXTENSIONS
    ]
    return sorted(files)


def run_transcribe(audio_file, model, language, model_dir, extra_args):
    """
    调用 audio_to_text.py 对单个文件进行转录
    输出文件与音频文件同目录，扩展名改为 .csv
    """
    output_file = audio_file.with_suffix(".csv")

    cmd = [
        sys.executable,
        str(TRANSCRIBE_SCRIPT),
        str(audio_file),
        "-m",
        model,
        "-l",
        language,
        "-o",
        str(output_file),
    ]

    if model_dir:
        cmd += ["-d", model_dir]
    if extra_args:
        cmd += extra_args

    print(f"\n{'='*70}")
    print(f"▶ 处理文件: {audio_file.name}")
    print(f"  输出到:   {output_file.name}")
    print(f"{'='*70}")

    result = subprocess.run(cmd)
    return result.returncode


def main():
    parser = argparse.ArgumentParser(
        description="批量遍历目录，对所有音视频文件调用 audio_to_text.py 转录",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 转录当前目录下所有音视频文件
  python batch_transcribe.py .

  # 指定目录，递归子目录
  python batch_transcribe.py D:\\recordings -r

  # 指定模型和语言（中文）
  python batch_transcribe.py D:\\recordings -m turbo -l zh

  # 转录英文内容
  python batch_transcribe.py D:\\recordings -m turbo -l en

  # 指定模型缓存目录
  python batch_transcribe.py D:\\recordings -m turbo -l zh -d D:\\whisper_models

  # 跳过已存在 CSV 的文件（断点续传模式）
  python batch_transcribe.py D:\\recordings --skip-existing

支持的格式:
  音频: mp3 wav m4a flac ogg webm aac wma
  视频: mp4 mkv avi mov wmv flv ts m4v
        """,
    )

    parser.add_argument("directory", help="要遍历的目录路径")
    parser.add_argument(
        "-m",
        "--model",
        default="turbo",
        choices=["tiny", "base", "small", "medium", "large", "turbo"],
        help="Whisper 模型大小 (默认: turbo)",
    )
    parser.add_argument(
        "-l",
        "--language",
        default="zh",
        choices=["zh", "en", "auto"],
        help="语言代码 (zh=简体中文, en=英文, auto=自动检测, 默认: zh)",
    )
    parser.add_argument(
        "-d",
        "--model-dir",
        help="模型存储目录 (默认: ~/.cache/whisper)",
    )
    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="递归遍历子目录",
    )
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="跳过已存在对应 CSV 文件的音视频（断点续传）",
    )
    parser.add_argument(
        "--no-force-simplified",
        action="store_true",
        help="禁用繁简转换，保留原始输出",
    )

    args = parser.parse_args()

    # 检查 audio_to_text.py 是否存在
    if not TRANSCRIBE_SCRIPT.exists():
        print(f"✗ 找不到转录脚本: {TRANSCRIBE_SCRIPT}")
        return 1

    # 查找所有音视频文件
    try:
        media_files = find_media_files(args.directory, recursive=args.recursive)
    except (FileNotFoundError, NotADirectoryError) as e:
        print(f"✗ {e}")
        return 1

    if not media_files:
        print(f"⚠ 目录中未找到任何音视频文件: {args.directory}")
        return 0

    print(f"✓ 找到 {len(media_files)} 个音视频文件")

    # 过滤已有 CSV 的文件
    if args.skip_existing:
        skipped = [f for f in media_files if f.with_suffix(".csv").exists()]
        media_files = [f for f in media_files if not f.with_suffix(".csv").exists()]
        if skipped:
            print(f"⚠ 跳过 {len(skipped)} 个已有 CSV 的文件:")
            for f in skipped:
                print(f"  - {f.name}")

    if not media_files:
        print("\n✓ 所有文件均已转录完毕，无需重新处理")
        return 0

    print(f"▶ 待处理: {len(media_files)} 个文件\n")
    for i, f in enumerate(media_files, 1):
        print(f"  {i:>3}. {f.name}")

    # 组装传递给子脚本的额外参数
    extra_args = []
    if args.no_force_simplified:
        extra_args.append("--no-force-simplified")

    # 逐个处理
    success, failed = [], []
    total = len(media_files)

    for idx, media_file in enumerate(media_files, 1):
        print(f"\n[{idx}/{total}] 开始处理...")
        code = run_transcribe(
            audio_file=media_file,
            model=args.model,
            language=args.language,
            model_dir=args.model_dir,
            extra_args=extra_args,
        )
        if code == 0:
            success.append(media_file)
        else:
            failed.append(media_file)
            print(f"  ✗ 处理失败 (exit code {code}): {media_file.name}")

    # 汇总报告
    print(f"\n{'='*70}")
    print(f"批量转录完成")
    print(f"  成功: {len(success)} 个")
    print(f"  失败: {len(failed)} 个")

    if failed:
        print("\n失败文件列表:")
        for f in failed:
            print(f"  ✗ {f.name}")
        return 1

    print("=" * 70)
    return 0


if __name__ == "__main__":
    exit(main())
