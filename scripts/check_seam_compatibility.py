#!/usr/bin/env python3
"""Measure adjacent video seams using a +/- frame compatibility window.

The check compares the last ``window`` decoded frames of leg i with the first
``window`` decoded frames of leg i+1. It reports the full MAE matrix, the best
pair, and the suggested outgoing trim. It never changes video assets.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from PIL import Image, ImageChops, ImageStat

from asset_versions import active_leg_files


def require_binary(name: str) -> str:
    path = shutil.which(name)
    if not path:
        raise SystemExit(f"{name} not found on PATH")
    return path


def frame_count(video: Path) -> int:
    ffprobe = require_binary("ffprobe")
    result = subprocess.run(
        [
            ffprobe,
            "-v",
            "error",
            "-count_frames",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=nb_read_frames",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(video),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return int(result.stdout.strip())


def extract_window(video: Path, mode: str, window: int, directory: Path) -> list[Image.Image]:
    count = frame_count(video)
    if count < window:
        raise SystemExit(f"{video} has {count} frames; need at least {window}")

    start = 0 if mode == "first" else count - window
    end = start + window - 1
    output = directory / f"{video.stem}-{mode}-%02d.png"
    ffmpeg = require_binary("ffmpeg")
    subprocess.run(
        [
            ffmpeg,
            "-y",
            "-loglevel",
            "error",
            "-i",
            str(video),
            "-vf",
            f"select='between(n,{start},{end})'",
            "-vsync",
            "0",
            str(output),
        ],
        check=True,
    )
    frames = sorted(directory.glob(f"{video.stem}-{mode}-*.png"))
    if len(frames) != window:
        raise SystemExit(f"Expected {window} {mode} frames from {video}, got {len(frames)}")
    return [Image.open(path).convert("RGB") for path in frames]


def mae(left: Image.Image, right: Image.Image) -> float:
    if left.size != right.size:
        raise SystemExit(f"Boundary resolution mismatch: {left.size} != {right.size}")
    diff = ImageChops.difference(left, right)
    return sum(ImageStat.Stat(diff).mean) / (3 * 255)


def active_encoded_path(project: Path, leg: Path) -> Path:
    encoded = project / "assets" / "encoded" / leg.name
    return encoded if encoded.is_file() else leg


def evaluate(project: Path, window: int, fail_mae: float) -> dict[str, Any]:
    legs = [active_encoded_path(project, leg) for leg in active_leg_files(project)]
    if len(legs) < 2:
        raise SystemExit("Need at least two active encoded legs")

    seams: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="scroll-world-seams-") as raw_dir:
        directory = Path(raw_dir)
        first = [extract_window(leg, "first", window, directory) for leg in legs]
        last = [extract_window(leg, "last", window, directory) for leg in legs]

        for index in range(len(legs) - 1):
            matrix = [
                [round(mae(last[index][left], first[index + 1][right]), 6) for right in range(window)]
                for left in range(window)
            ]
            best_value = min(value for row in matrix for value in row)
            best_left, best_right = next(
                (left, right)
                for left, row in enumerate(matrix)
                for right, value in enumerate(row)
                if value == best_value
            )
            # The extracted last window is ordered oldest -> newest, so the
            # actual endpoint is the final row, not row zero.
            exact_value = matrix[window - 1][0]
            seam = {
                "from_leg": index,
                "to_leg": index + 1,
                "from_file": legs[index].as_posix(),
                "to_file": legs[index + 1].as_posix(),
                "mae_matrix": matrix,
                "exact_last_to_first_mae": exact_value,
                "best_mae": best_value,
                "best_from_window_index": best_left,
                "best_to_window_index": best_right,
                "suggested_outgoing_trim_frames": window - 1 - best_left,
                "improvement": round(exact_value - best_value, 6),
                "status": "PASS" if best_value <= fail_mae else "REVIEW",
            }
            seams.append(seam)

    return {
        "schema": "scroll-world.seam-compatibility.v1",
        "window": window,
        "comparison": f"last[{window}] x first[{window}]",
        "fail_mae": fail_mae,
        "project": project.as_posix(),
        "seams": seams,
        "status": "PASS" if all(seam["status"] == "PASS" for seam in seams) else "REVIEW",
    }


def write_outputs(project: Path, report: dict[str, Any], output: Path | None) -> None:
    destination = output or project / "assets" / "seam-compatibility.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Seam compatibility report",
        "",
        f"- status: **{report['status']}**",
        f"- window: `{report['comparison']}`",
        f"- fail threshold: `{report['fail_mae']}` MAE",
        "",
        "| seam | exact MAE | best MAE | trim suggestion | status |",
        "|---|---:|---:|---:|---|",
    ]
    for seam in report["seams"]:
        lines.append(
            f"| {seam['from_leg']} → {seam['to_leg']} | "
            f"{seam['exact_last_to_first_mae']:.4f} | {seam['best_mae']:.4f} | "
            f"{seam['suggested_outgoing_trim_frames']} frames | {seam['status']} |"
        )
    (destination.parent / "seam-compatibility.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )
    print(destination)
    print(destination.parent / "seam-compatibility.md")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--window", type=int, default=5, help="Frames on each side of every seam")
    parser.add_argument(
        "--fail-mae",
        type=float,
        default=0.08,
        help="Best-window MAE above this value marks a seam REVIEW",
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.window < 2:
        raise SystemExit("--window must be >= 2")
    report = evaluate(args.project.resolve(), args.window, args.fail_mae)
    write_outputs(args.project.resolve(), report, args.output)
    raise SystemExit(0 if report["status"] == "PASS" else 2)


if __name__ == "__main__":
    main()
