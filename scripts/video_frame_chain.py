#!/usr/bin/env python3
"""Video leg frame chain: storyboard end + previous leg last frame (ffmpeg).

Chain policy
------------
Default (no ``playback_chain`` in ``project.meta.json``):
  leg 0: start = storyboard frame 1, end = storyboard frame 2
  leg i>0: start = last frame of active leg i-1 MP4, end = storyboard frame i+2
  (assumes continuous board indices 1..M; max leg = M-2)

With ``playback_chain`` = prefix ``[1, 2, …, K]`` (no gaps; K ≤ M):
  leg i connects ``playback_chain[i]`` → ``playback_chain[i+1]``
  leg 0: start = storyboard ``playback_chain[0]``, end = ``playback_chain[1]``
  leg i>0: start = prev video last frame, end = storyboard ``playback_chain[i+1]``
  max leg index = K-2 (video count = K-1)
  optional ``reserve`` = ``[K+1, …, M]`` — board frames not used in video legs
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Any, Literal

from asset_versions import format_version, load_manifest, parse_version_prefix
from media_format import load_project_meta

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


def resolve_playback_chain(meta: dict[str, Any], frames_m: int) -> list[int]:
    """Return 1-based storyboard indices used for video legs (prefix 1..K).

    If ``meta.playback_chain`` is missing or empty, returns ``[1, 2, …, frames_m]`` (K=M).
    If present, must equal ``[1, 2, …, K]`` with no gaps or reordering.
    Optional ``meta.reserve`` must equal ``[K+1, …, frames_m]`` when provided.
    """
    m = int(frames_m)
    if m < 2:
        raise SystemExit(f"frames_m must be >= 2 for a video chain; got {m}")

    raw = meta.get("playback_chain")
    if raw is None or (isinstance(raw, list) and len(raw) == 0):
        return list(range(1, m + 1))

    if not isinstance(raw, list):
        raise SystemExit(
            f"playback_chain must be a list of 1-based board indices; got {type(raw).__name__}"
        )

    try:
        chain = [int(x) for x in raw]
    except (TypeError, ValueError) as exc:
        raise SystemExit(f"playback_chain entries must be integers; got {raw!r}") from exc

    if len(chain) < 2:
        raise SystemExit(
            f"playback_chain must have at least 2 indices (need ≥1 video leg); got {chain!r}"
        )

    k = len(chain)
    expected = list(range(1, k + 1))
    if chain != expected:
        raise SystemExit(
            "playback_chain must be a contiguous prefix [1, 2, …, K] with no gaps "
            f"(got {chain!r}, expected {expected!r}). Sparse or reordered chains are not supported."
        )

    if k > m:
        raise SystemExit(f"playback_chain length K={k} exceeds frames M={m}")

    reserve = meta.get("reserve")
    if reserve is not None:
        if not isinstance(reserve, list):
            raise SystemExit(f"reserve must be a list of 1-based board indices; got {type(reserve).__name__}")
        try:
            reserve_list = [int(x) for x in reserve]
        except (TypeError, ValueError) as exc:
            raise SystemExit(f"reserve entries must be integers; got {reserve!r}") from exc
        expected_reserve = list(range(k + 1, m + 1))
        if reserve_list != expected_reserve:
            raise SystemExit(
                f"reserve must equal [K+1, …, M] = {expected_reserve!r} when "
                f"playback_chain has K={k} and frames M={m}; got {reserve_list!r}"
            )

    return chain


def resolve_leg_frame_paths(
    project: Path,
    leg_index: int,
    *,
    start_override: Path | None = None,
    end_override: Path | None = None,
    refresh_extract: bool = False,
) -> tuple[Path, Path, dict[str, Any]]:
    """
    Resolve local start/end PNG paths for a video leg.

    Default (no playback_chain):
      leg 0: start = storyboard frame 1, end = storyboard frame 2
      leg i>0: start = last frame of active leg i-1 MP4, end = storyboard frame i+2

    With playback_chain [1..K]:
      leg i connects playback_chain[i] → playback_chain[i+1]
      max leg index = K-2
    """
    if leg_index < 0:
        raise SystemExit("--leg must be >= 0")

    project_meta = load_project_meta(project)
    chain_raw = project_meta.get("playback_chain")
    using_chain = isinstance(chain_raw, list) and len(chain_raw) > 0

    if using_chain:
        frames_raw = project_meta.get("frames")
        if frames_raw is None:
            raise SystemExit(
                "project.meta.json frames (M) is required when playback_chain is set"
            )
        chain = resolve_playback_chain(project_meta, int(frames_raw))
        max_leg = len(chain) - 2
        if leg_index > max_leg:
            raise SystemExit(
                f"leg index {leg_index} exceeds max {max_leg} for playback_chain "
                f"length K={len(chain)} (video legs = K-1 = {max_leg + 1})"
            )
        end_frame_index = chain[leg_index + 1]
        start_storyboard_index = chain[0]
    else:
        chain = None
        frames_raw = project_meta.get("frames")
        if frames_raw is not None:
            try:
                frames_m = int(frames_raw)
            except (TypeError, ValueError):
                raise SystemExit(
                    f"project.meta.json frames must be an integer; got {frames_raw!r}"
                )
            if leg_index + 2 > frames_m:
                raise SystemExit(
                    f"leg index {leg_index} requires storyboard frame {leg_index + 2}, "
                    f"but frames M={frames_m} (max leg = M-2 = {frames_m - 2}). "
                    "Set playback_chain in project.meta.json or reduce --leg."
                )
        end_frame_index = leg_index + 2
        start_storyboard_index = 1

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
        "playback_chain": chain,
    }

    if start_override is not None:
        start_path = start_override if start_override.is_absolute() else (project / start_override)
        meta["start_source"] = "manual"
        meta["prev_leg"] = None
        return start_path, end_path, meta

    if leg_index == 0:
        start_path = resolve_storyboard_frame(project, start_storyboard_index)
        meta["start_source"] = "storyboard"
        meta["start_frame_index"] = start_storyboard_index
        meta["prev_leg"] = None
        return start_path, end_path, meta

    prev_leg = leg_index - 1
    prev_mp4 = get_active_leg_mp4(project, prev_leg)
    ver = parse_version_prefix(prev_mp4.name)
    if ver is None:
        raise SystemExit(f"Leg file must be NNN-leg-LL.mp4, got: {prev_mp4.name}")

    extract_dest = last_frame_path_for_leg(project, ver, prev_leg)
    if (
        refresh_extract
        or not extract_dest.is_file()
        or extract_dest.stat().st_mtime < prev_mp4.stat().st_mtime
    ):
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
