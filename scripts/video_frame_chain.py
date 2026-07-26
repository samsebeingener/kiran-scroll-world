#!/usr/bin/env python3
"""Video leg frame chain: storyboard end + previous leg last frame (ffmpeg)."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Any, Literal

from asset_versions import format_version, load_manifest, parse_version_prefix

StartSource = Literal["storyboard", "prev_video", "manual"]


def which_ffmpeg() -> str:
    path = shutil.which("ffmpeg")
    if not path:
        raise SystemExit("ffmpeg not found on PATH (required for video frame chain)")
    return path


def extract_last_frame(video_path: Path, dest_path: Path) -> Path:
    """Extract the final rendered frame from an MP4 (for chaining legs)."""
    video_path = Path(video_path)
    dest_path = Path(dest_path)
    if not video_path.is_file():
        raise SystemExit(f"Missing video for frame extract: {video_path}")

    ffmpeg = which_ffmpeg()
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        ffmpeg,
        "-y",
        "-sseof",
        "-0.05",
        "-i",
        str(video_path),
        "-update",
        "1",
        "-q:v",
        "2",
        "-frames:v",
        "1",
        str(dest_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise SystemExit(f"ffmpeg extract failed: {result.stderr or result.stdout}")
    if not dest_path.is_file() or dest_path.stat().st_size == 0:
        raise SystemExit(f"Failed to extract last frame: {dest_path}")
    return dest_path


def extract_first_frame(video_path: Path, dest_path: Path) -> Path:
    """Extract the first rendered frame from an MP4 (for scrub stills / posters)."""
    video_path = Path(video_path)
    dest_path = Path(dest_path)
    if not video_path.is_file():
        raise SystemExit(f"Missing video for frame extract: {video_path}")

    ffmpeg = which_ffmpeg()
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        ffmpeg,
        "-y",
        "-ss",
        "0",
        "-i",
        str(video_path),
        "-frames:v",
        "1",
        "-q:v",
        "2",
        str(dest_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise SystemExit(f"ffmpeg first-frame extract failed: {result.stderr or result.stdout}")
    if not dest_path.is_file() or dest_path.stat().st_size == 0:
        raise SystemExit(f"Failed to extract first frame: {dest_path}")
    return dest_path


def last_frame_path_for_leg(project: Path, leg_version: int, leg_index: int) -> Path:
    return project / "assets" / "frames" / f"{format_version(leg_version)}-leg-{leg_index:02d}-last.png"


def first_frame_path_for_leg(project: Path, leg_version: int, leg_index: int) -> Path:
    return project / "assets" / "frames" / f"{format_version(leg_version)}-leg-{leg_index:02d}-first.png"


def get_active_leg_mp4(project: Path, leg_index: int) -> Path:
    manifest = load_manifest(project)
    entry = (manifest.get("legs") or {}).get(str(leg_index))
    if not isinstance(entry, dict):
        raise SystemExit(
            f"Leg {leg_index} not in manifest. Generate legs in order (0 → 1 → …); "
            f"leg {leg_index} needs active leg {leg_index - 1} first."
        )
    active = entry.get("active_version")
    versions = entry.get("versions") or {}
    if active is None:
        raise SystemExit(f"Leg {leg_index} has no active_version in manifest")
    key = format_version(int(active))
    rel = versions.get(key)
    if not rel:
        raise SystemExit(f"Leg {leg_index} active version {key} missing in manifest.versions")
    path = project / rel
    if not path.is_file():
        raise SystemExit(f"Missing active leg file: {path}")
    return path


def resolve_storyboard_frame(project: Path, frame_index: int) -> Path:
    """1-based storyboard cell index from manifest.frames.active_map."""
    manifest = load_manifest(project)
    active_map = (manifest.get("frames") or {}).get("active_map") or {}
    key = str(frame_index)
    rel = active_map.get(key)
    if not rel:
        raise SystemExit(
            f"manifest.frames.active_map missing key {key!r} "
            f"(need storyboard frame for leg target). Run slice_storyboard.py first."
        )
    path = project / rel
    if not path.is_file():
        raise SystemExit(f"Missing storyboard frame file: {path}")
    return path


def resolve_leg_frame_paths(
    project: Path,
    leg_index: int,
    *,
    start_override: Path | None = None,
    end_override: Path | None = None,
    refresh_extract: bool = True,
) -> tuple[Path, Path, dict[str, Any]]:
    """
    Chain policy (default):
      leg 0: start = storyboard frame 1, end = storyboard frame 2
      leg i>0: start = last frame of active leg i-1 MP4, end = storyboard frame i+2
    """
    if leg_index < 0:
        raise SystemExit("--leg must be >= 0")

    end_frame_index = leg_index + 2
    if end_override is not None:
        end_path = end_override if end_override.is_absolute() else (project / end_override)
        end_source = "manual"
    else:
        end_path = resolve_storyboard_frame(project, end_frame_index)
        end_source = "storyboard"

    meta: dict[str, Any] = {
        "leg": leg_index,
        "end_frame_index": end_frame_index,
        "end_source": end_source,
    }

    if start_override is not None:
        start_path = start_override if start_override.is_absolute() else (project / start_override)
        meta["start_source"] = "manual"
        meta["prev_leg"] = None
        return start_path, end_path, meta

    if leg_index == 0:
        start_path = resolve_storyboard_frame(project, 1)
        meta["start_source"] = "storyboard"
        meta["prev_leg"] = None
        return start_path, end_path, meta

    prev_leg = leg_index - 1
    prev_mp4 = get_active_leg_mp4(project, prev_leg)
    ver = parse_version_prefix(prev_mp4.name)
    if ver is None:
        raise SystemExit(f"Leg file must be NNN-leg-LL.mp4, got: {prev_mp4.name}")

    extract_dest = last_frame_path_for_leg(project, ver, prev_leg)
    if refresh_extract or not extract_dest.is_file():
        extract_last_frame(prev_mp4, extract_dest)

    meta["start_source"] = "prev_video"
    meta["prev_leg"] = prev_leg
    meta["prev_leg_file"] = str(prev_mp4).replace("\\", "/")
    meta["extracted_last_frame"] = str(extract_dest).replace("\\", "/")
    return extract_dest, end_path, meta


def save_leg_last_frame(project: Path, leg_mp4: Path, leg_index: int) -> Path:
    """After a leg is generated, cache its last frame for the next leg."""
    ver = parse_version_prefix(leg_mp4.name)
    if ver is None:
        raise SystemExit(f"Cannot cache last frame — bad leg name: {leg_mp4.name}")
    dest = last_frame_path_for_leg(project, ver, leg_index)
    return extract_last_frame(leg_mp4, dest)


def save_leg_first_frame(project: Path, leg_mp4: Path, leg_index: int) -> Path:
    """Cache first frame of a leg MP4 (scrub intro / poster stills)."""
    ver = parse_version_prefix(leg_mp4.name)
    if ver is None:
        raise SystemExit(f"Cannot cache first frame — bad leg name: {leg_mp4.name}")
    dest = first_frame_path_for_leg(project, ver, leg_index)
    return extract_first_frame(leg_mp4, dest)
