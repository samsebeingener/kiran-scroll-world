#!/usr/bin/env python3
"""Extract first frame from a video leg MP4 (for scrub stills)."""

from __future__ import annotations

import argparse
from pathlib import Path

from asset_versions import parse_version_prefix
from video_frame_chain import extract_first_frame, first_frame_path_for_leg


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", required=True, type=Path, help="Source MP4 (NNN-leg-LL.mp4)")
    parser.add_argument("--out", type=Path, default=None, help="Output PNG (default: assets/frames/NNN-leg-LL-first.png)")
    parser.add_argument("--project", type=Path, default=None, help="Project root if --out omitted")
    parser.add_argument("--leg", type=int, default=None, help="Leg index if inferring --out from filename")
    args = parser.parse_args()

    video = args.video.resolve()
    if args.out:
        dest = args.out if args.out.is_absolute() else (args.project or Path.cwd()) / args.out
    else:
        if args.project is None or args.leg is None:
            raise SystemExit("Provide --out or both --project and --leg")
        ver = parse_version_prefix(video.name)
        if ver is None:
            raise SystemExit(f"Cannot infer output path from {video.name}")
        dest = first_frame_path_for_leg(args.project.resolve(), ver, args.leg)

    out = extract_first_frame(video, dest)
    print(out)


if __name__ == "__main__":
    main()
