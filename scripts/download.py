#!/usr/bin/env python3
import argparse
import shlex
import subprocess
import sys
from pathlib import Path


def to_bool(value: str) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "y", "on"}


def main() -> int:
    parser = argparse.ArgumentParser(description="Authorized fast media downloader")
    parser.add_argument("--url", required=True)
    parser.add_argument("--mode", required=True)
    parser.add_argument("--playlist", default="false")
    parser.add_argument("--subtitles", default="false")
    parser.add_argument("--extra-args", default="")
    args = parser.parse_args()

    url = args.url.strip()
    mode = args.mode.strip()
    playlist = to_bool(args.playlist)
    subtitles = to_bool(args.subtitles)
    extra_args = args.extra_args.strip()

    if not url:
        print("ERROR: URL is empty.")
        return 1

    Path("downloads").mkdir(exist_ok=True)
    Path("temp").mkdir(exist_ok=True)

    cmd = [
        "yt-dlp",
        url,

        "--ignore-errors",
        "--no-overwrites",
        "--continue",
        "--retries", "10",
        "--fragment-retries", "10",
        "--socket-timeout", "20",

        "--concurrent-fragments", "16",
        "--downloader", "aria2c",
        "--downloader-args", "aria2c:-x 16 -s 16 -k 1M --file-allocation=none --summary-interval=0",

        "--paths", "home:downloads",
        "--paths", "temp:temp",
        "-o", "%(title).180B [%(id)s].%(ext)s",
        "--restrict-filenames",
        "--windows-filenames",

        "--write-info-json",
        "--write-thumbnail",
        "--embed-metadata",
    ]

    if Path("cookies.txt").exists():
        cmd += ["--cookies", "cookies.txt"]

    if playlist:
        cmd += ["--yes-playlist"]
    else:
        cmd += ["--no-playlist"]

    if subtitles:
        cmd += [
            "--write-subs",
            "--write-auto-subs",
            "--sub-langs", "en.*,fa.*,all",
            "--convert-subs", "srt",
        ]

    if mode == "best-mp4":
        cmd += [
            "-f", "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/bv*+ba/best",
            "--merge-output-format", "mp4",
        ]
    elif mode == "1080p-mp4":
        cmd += [
            "-f", "bv*[height<=1080][ext=mp4]+ba[ext=m4a]/b[height<=1080][ext=mp4]/best[height<=1080]",
            "--merge-output-format", "mp4",
        ]
    elif mode == "720p-mp4":
        cmd += [
            "-f", "bv*[height<=720][ext=mp4]+ba[ext=m4a]/b[height<=720][ext=mp4]/best[height<=720]",
            "--merge-output-format", "mp4",
        ]
    elif mode == "audio-mp3":
        cmd += [
            "-x",
            "--audio-format", "mp3",
            "--audio-quality", "0",
        ]
    elif mode == "audio-m4a":
        cmd += [
            "-f", "ba[ext=m4a]/ba",
            "-x",
            "--audio-format", "m4a",
        ]
    else:
        print(f"ERROR: Unknown mode: {mode}")
        return 1

    blocked = {
        "--exec",
        "--use-postprocessor",
        "--postprocessor-args",
        "--ppa",
        "--config-location",
        "--batch-file",
        "-a",
    }

    if extra_args:
        parts = shlex.split(extra_args)
        for part in parts:
            if part in blocked or any(part.startswith(b + "=") for b in blocked):
                print(f"ERROR: Blocked unsafe yt-dlp argument: {part}")
                return 1
        cmd += parts

    print("Running yt-dlp with secure configuration...")
    print(f"Mode: {mode}")
    print(f"Playlist: {playlist}")
    print(f"Subtitles: {subtitles}")

    result = subprocess.run(cmd)
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
