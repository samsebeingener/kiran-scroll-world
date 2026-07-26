#!/usr/bin/env python3
"""Encode active versioned legs into scrub-friendly MP4 (short GOP, yuv420p)."""

from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path

from asset_versions import active_leg_files, load_manifest
from media_format import load_project_meta, resolve_encode_dimensions


def which_ffmpeg() -> str:
    path = shutil.which("ffmpeg")
    if not path:
        raise SystemExit("ffmpeg not found on PATH")
    return path


def encode(src: Path, dest: Path, width: int, height: int) -> None:
    ffmpeg = which_ffmpeg()
    dest.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        ffmpeg,
        "-y",
        "-i",
        str(src),
        "-an",
        "-vf",
        f"scale={width}:{height}",
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-g",
        "4",
        "-keyint_min",
        "4",
        "-sc_threshold",
        "0",
        "-movflags",
        "+faststart",
        str(dest),
    ]
    subprocess.run(cmd, check=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument(
        "--width",
        type=int,
        default=None,
        help="Override scale width (height derived from media_aspect_ratio)",
    )
    parser.add_argument(
        "--all-versions",
        action="store_true",
        help="Encode every *-leg-*.mp4 (default: only active versions from manifest)",
    )
    parser.add_argument(
        "--seam-window",
        type=int,
        default=5,
        help="Decoded frames checked on each side of every seam",
    )
    parser.add_argument(
        "--seam-fail-mae",
        type=float,
        default=0.08,
        help="Best-window MAE above this value fails the encode gate",
    )
    args = parser.parse_args()

    project = args.project.resolve()
    meta = load_project_meta(project)
    width, height = resolve_encode_dimensions(args.width, meta)
    resolution = meta.get("video_resolution") or "(default 480p)"
    aspect = meta.get("media_aspect_ratio") or meta.get("video_aspect_ratio") or "16:9"
    print(f"encode {width}x{height} (video_resolution={resolution}, media_aspect_ratio={aspect})")

    if args.all_versions:
        legs = sorted((project / "assets" / "video" / "legs").glob("*-leg-*.mp4"))
    else:
        legs = active_leg_files(project)
    if not legs:
        raise SystemExit("No versioned legs found (expected NNN-leg-LL.mp4)")

    out_dir = project / "assets" / "encoded"
    for leg in legs:
        dest = out_dir / leg.name
        print(f"encode {leg.name} -> {dest}")
        encode(leg, dest, width=width, height=height)
        print(dest)

    from build_scrub_media import build_scrub_media
    from check_seam_compatibility import evaluate, write_outputs

    build_scrub_media(project)
    seam_report = evaluate(project, args.seam_window, args.seam_fail_mae)
    write_outputs(project, seam_report, None)
    if seam_report["status"] != "PASS":
        raise SystemExit(
            "Seam compatibility gate failed: inspect assets/seam-compatibility.md "
            "before publishing."
        )


if __name__ == "__main__":
    main()
