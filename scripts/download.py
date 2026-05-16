#!/usr/bin/env python3

import argparse
import shlex
import subprocess
import sys
from pathlib import Path

BLOCKED_ARGS = {
    "--exec",
    "--use-postprocessor",
    "--postprocessor-args",
    "--ppa",
    "--config-location",
    "--batch-file",
    "-a",
}

MODE_CONFIG = {
    "best-mp4": {
        "format": "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/bv*+ba/best",
        "merge_output_format": "mp4",
    },
    "1080p-mp4": {
        "format": "bv*[height<=1080][ext=mp4]+ba[ext=m4a]/b[height<=1080][ext=mp4]/best[height<=1080]",
        "merge_output_format": "mp4",
    },
    "720p-mp4": {
        "format": "bv*[height<=720][ext=mp4]+ba[ext=m4a]/b[height<=720][ext=mp4]/best[height<=720]",
        "merge_output_format": "mp4",
    },
    "audio-mp3": {
        "extract_audio": True,
        "audio_format": "mp3",
        "audio_quality": "0",
        "format": "bestaudio/best",
    },
    "audio-m4a": {
        "extract_audio": True,
        "audio_format": "m4a",
        "audio_quality": "0",
        "format": "bestaudio/best",
    },
}

OUTPUT_TEMPLATE = "downloads/%(title).180B [%(id)s].%(ext)s"


def parse_bool(value: str) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def validate_extra_args(extra_args_raw: str) -> list[str]:
    if not extra_args_raw:
        return []

    try:
        args = shlex.split(extra_args_raw)
    except ValueError as exc:
        raise SystemExit(f"Invalid extra_ytdlp_args: {exc}") from None

    for arg in args:
        normalized = arg.lower()
        if normalized in BLOCKED_ARGS:
            raise SystemExit(f"Blocked yt-dlp argument detected: {arg}")
        for blocked in BLOCKED_ARGS:
            if blocked.startswith("--") and normalized.startswith(blocked + "="):
                raise SystemExit(f"Blocked yt-dlp argument detected: {arg}")
    return args


def build_command(args: argparse.Namespace) -> list[str]:
    config = MODE_CONFIG[args.mode]
    command = [
        "yt-dlp",
        "--output",
        OUTPUT_TEMPLATE,
        "--restrict-filenames",
        "--windows-filenames",
        "--continue",
        "--retries",
        "10",
        "--fragment-retries",
        "10",
        "--socket-timeout",
        "20",
        "--concurrent-fragments",
        "16",
        "--downloader",
        "aria2c",
        "--downloader-args",
        "aria2c:-x 16 -s 16 -k 1M --file-allocation=none --summary-interval=0",
        "--temp-dir",
        "temp",
    ]

    if args.playlist:
        command.append("--yes-playlist")
    else:
        command.append("--no-playlist")

    if args.subtitles:
        command.extend([
            "--write-subs",
            "--write-auto-subs",
            "--sub-langs",
            "en.*,fa.*,all",
            "--convert-subs",
            "srt",
        ])

    if config.get("merge_output_format"):
        command.extend(["--format", config["format"], "--merge-output-format", config["merge_output_format"]])
    else:
        command.extend(["--format", config["format"]])

    if config.get("extract_audio"):
        command.extend([
            "--extract-audio",
            "--audio-format",
            config["audio_format"],
            "--audio-quality",
            config["audio_quality"],
        ])

    if Path("cookies.txt").is_file():
        command.extend(["--cookies", "cookies.txt"])

    command.extend(args.extra_args)
    command.append(args.url)
    return command


def main() -> int:
    parser = argparse.ArgumentParser(description="Authorized media downloader wrapper for yt-dlp")
    parser.add_argument("--url", required=True, help="Media URL to download")
    parser.add_argument(
        "--mode",
        required=True,
        choices=list(MODE_CONFIG.keys()),
        help="Download mode"
    )
    parser.add_argument(
        "--playlist",
        required=True,
        type=parse_bool,
        help="Enable playlist download",
    )
    parser.add_argument(
        "--subtitles",
        required=True,
        type=parse_bool,
        help="Enable subtitle download",
    )
    parser.add_argument(
        "--extra-args",
        default="",
        help="Extra yt-dlp arguments to pass after validation",
    )
    parsed = parser.parse_args()

    parsed.extra_args = validate_extra_args(parsed.extra_args)

    Path("downloads").mkdir(parents=True, exist_ok=True)
    Path("temp").mkdir(parents=True, exist_ok=True)

    command = build_command(parsed)

    print("Running yt-dlp with secure configuration...")
    result = subprocess.run(command)
    if result.returncode != 0:
        raise SystemExit(result.returncode)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
