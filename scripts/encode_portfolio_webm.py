#!/usr/bin/env python3
"""Re-encode assets/encoded/*.mp4 -> VP9 WebM for portfolio deploy (smaller, scrub-friendly GOP)."""

from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path


def which_ffmpeg() -> str:
    path = shutil.which("ffmpeg")
    if not path:
        raise SystemExit("ffmpeg not found on PATH")
    return path


def encode_webm(src: Path, dest: Path, *, crf: int) -> None:
    ffmpeg = which_ffmpeg()
    dest.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        ffmpeg,
        "-y",
        "-i",
        str(src),
        "-an",
        "-c:v",
        "libvpx-vp9",
        "-crf",
        str(crf),
        "-b:v",
        "0",
        "-g",
        "8",
        "-keyint_min",
        "8",
        "-row-mt",
        "1",
        "-deadline",
        "good",
        "-cpu-used",
        "2",
        str(dest),
    ]
    subprocess.run(cmd, check=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--crf", type=int, default=32, help="VP9 CRF (higher = smaller, default 32)")
    args = parser.parse_args()

    project = args.project.resolve()
    enc = project / "assets" / "encoded"
    mp4s = sorted(enc.glob("*.mp4"))
    if not mp4s:
        raise SystemExit(f"No encoded MP4 in {enc}")

    for mp4 in mp4s:
        webm = mp4.with_suffix(".webm")
        before = webm.stat().st_size if webm.is_file() else 0
        print(f"encode {mp4.name} -> {webm.name} (crf {args.crf})")
        encode_webm(mp4, webm, crf=args.crf)
        after = webm.stat().st_size
        if before:
            pct = round(100 * (1 - after / before))
            print(f"  {before // 1024}KB -> {after // 1024}KB ({pct}% smaller)")
        else:
            print(f"  -> {after // 1024}KB")


if __name__ == "__main__":
    main()
