#!/usr/bin/env python3
"""Extract scrub stills from encoded legs + write assets/scrub-media.json.

Scroll stills MUST come from actual video frames, not storyboard slices.
See shared/scrub-still-contract.md.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from asset_versions import active_leg_files, format_version, load_manifest, parse_version_prefix
from video_frame_chain import (
    extract_first_frame,
    extract_last_frame,
    first_frame_path_for_leg,
    last_frame_path_for_leg,
)


def rel_posix(project: Path, path: Path) -> str:
    assets = project / "assets"
    return path.relative_to(assets).as_posix()


def encoded_leg_path(project: Path, leg_mp4: Path) -> Path:
    encoded_dir = project / "assets" / "encoded"
    webm = encoded_dir / f"{leg_mp4.stem}.webm"
    mp4 = encoded_dir / leg_mp4.name
    if webm.is_file():
        return webm
    return mp4


def encoded_extract_source(project: Path, leg_mp4: Path) -> Path:
    """Frame extraction prefers encoded MP4 (stable GOP); playback may use WebM."""
    mp4 = project / "assets" / "encoded" / leg_mp4.name
    if mp4.is_file():
        return mp4
    return encoded_leg_path(project, leg_mp4)


def cache_leg_boundary_frames(
    project: Path,
    leg_mp4: Path,
    encoded_clip: Path,
    leg_index: int,
    *,
    refresh: bool,
) -> tuple[Path, Path]:
    ver = parse_version_prefix(leg_mp4.name)
    if ver is None:
        raise SystemExit(f"Leg file must be NNN-leg-LL.mp4, got: {leg_mp4.name}")

    if encoded_clip.is_file():
        src = encoded_extract_source(project, leg_mp4)
    else:
        src = leg_mp4
    first_png = first_frame_path_for_leg(project, ver, leg_index)
    last_png = last_frame_path_for_leg(project, ver, leg_index)

    if refresh or not first_png.is_file():
        extract_first_frame(src, first_png)
        print(f"first {first_png.name}")
    if refresh or not last_png.is_file():
        extract_last_frame(src, last_png)
        print(f"last  {last_png.name}")

    return first_png, last_png


def build_sections(
    project: Path,
    legs: list[Path],
    boundaries: list[tuple[Path, Path]],
) -> list[dict[str, Any]]:
    """
    One scroll section per encoded leg.

    Scrub starts at t=0 of leg 0 and ends on the last frame of the final leg.
    `still` is the leg's first video frame (decode poster only until the clip paints).
  """
    if not legs:
        raise SystemExit("No active legs in manifest")

    sections: list[dict[str, Any]] = []
    for leg_idx, leg_mp4 in enumerate(legs):
        encoded = encoded_leg_path(project, leg_mp4)
        sections.append(
            {
                "still": rel_posix(project, boundaries[leg_idx][0]),
                "clip": rel_posix(project, encoded),
            }
        )

    return sections


def build_scrub_media(project: Path, *, refresh: bool = False) -> Path:
    project = project.resolve()
    legs = active_leg_files(project)
    if not legs:
        raise SystemExit("No active legs found")

    ver = parse_version_prefix(legs[0].name)
    if ver is None:
        raise SystemExit(f"Bad leg filename: {legs[0].name}")

    boundaries: list[tuple[Path, Path]] = []
    for leg_idx, leg_mp4 in enumerate(legs):
        encoded = encoded_leg_path(project, leg_mp4)
        boundaries.append(
            cache_leg_boundary_frames(
                project, leg_mp4, encoded, leg_idx, refresh=refresh
            )
        )

    sections = build_sections(project, legs, boundaries)
    out = {
        "batch": format_version(ver),
        "source": "encoded_legs",
        "policy": "one section per leg; scrub 0s→end; still=leg first frame (poster only); no still-only bookends",
        "sections": sections,
    }

    out_path = project / "assets" / "scrub-media.json"
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(out_path)

    manifest_path = project / "assets" / "manifest.json"
    manifest: dict[str, Any] = {}
    if manifest_path.is_file():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["scrub_media"] = "assets/scrub-media.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Re-extract all first/last frames even if PNG exists",
    )
    args = parser.parse_args()
    build_scrub_media(args.project, refresh=args.refresh)


if __name__ == "__main__":
    main()
