#!/usr/bin/env python3
"""Media aspect ratio helpers — panels @ cell aspect, encode pixels.

Storyboard and Seedance share one cell aspect from project.meta.json → media_aspect_ratio.
Panels are generated via Kie gpt-image-2-text-to-image (2K/4K); video via seedance-2-mini.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Any

# Seedance 2 Mini + gpt-image-2 panel aspects (shared).
SUPPORTED_CELL_ASPECTS = frozenset({"16:9", "9:16", "4:3", "3:4", "1:1", "21:9"})
DEFAULT_CELL_ASPECT = "16:9"
STORYBOARD_RESOLUTIONS = frozenset({"2K", "4K"})

FRAME_COUNTS = frozenset({3, 6, 9})

# (rows, cols) for contact-sheet layout after panels_then_stitch
GRID_BY_M: dict[int, tuple[int, int]] = {
    3: (1, 3),
    6: (2, 3),
    9: (3, 3),
}


def load_project_meta(project: Path) -> dict[str, Any]:
    meta_path = project / "project.meta.json"
    if not meta_path.is_file():
        return {}
    try:
        return json.loads(meta_path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as exc:
        print(
            f"WARN: broken JSON in {meta_path}: {exc} — continuing with empty meta",
            file=sys.stderr,
            flush=True,
        )
        return {}


def parse_aspect(ratio: str) -> tuple[int, int]:
    parts = ratio.strip().split(":")
    if len(parts) != 2:
        raise ValueError(f"Invalid aspect ratio {ratio!r}")
    w, h = int(parts[0]), int(parts[1])
    if w <= 0 or h <= 0:
        raise ValueError(f"Invalid aspect ratio {ratio!r}")
    return w, h


def aspect_to_float(ratio: str) -> float:
    w, h = parse_aspect(ratio)
    return w / h


def simplify_aspect(w: int, h: int) -> str:
    g = math.gcd(w, h)
    return f"{w // g}:{h // g}"


def resolve_frames_count(meta: dict[str, Any], cli_frames: int | None) -> int:
    if cli_frames is not None:
        m = int(cli_frames)
    else:
        raw = meta.get("frames")
        if raw is None:
            raise SystemExit(
                "frames (M) not set. Set project.meta.json frames (3|6|9) after Journey / "
                "Gate Budget, or pass --frames."
            )
        m = int(raw)
    if m not in FRAME_COUNTS:
        raise SystemExit(f"frames must be one of {sorted(FRAME_COUNTS)}; got {m}")
    return m


def resolve_cell_aspect(cli_value: str | None, meta: dict[str, Any], *, required: bool = True) -> str:
    raw = (
        cli_value
        or meta.get("media_aspect_ratio")
        or meta.get("video_aspect_ratio")
        or ""
    )
    raw = str(raw).strip()
    if not raw:
        if required:
            raise SystemExit(
                "media_aspect_ratio not set in project.meta.json. "
                "Ask user on intake (RU): 16:9 / 9:16 / 4:3 / 3:4 / 1:1 / 21:9 — "
                "same for storyboard panels and Seedance video."
            )
        return DEFAULT_CELL_ASPECT
    if raw not in SUPPORTED_CELL_ASPECTS:
        raise SystemExit(
            f"Unsupported media_aspect_ratio {raw!r}. "
            f"Use one of: {', '.join(sorted(SUPPORTED_CELL_ASPECTS))}"
        )
    return raw


def board_aspect_ratio(m: int, cell_aspect: str) -> str:
    """Pixel aspect of stitched review board after local PIL stitch (informational only).

    Never sent to Kie — API accepts only per-panel ratios (e.g. 16:9), not composite
    board aspects like 8:3 (M=6, cell 16:9, grid 3×2). See media-format-contract.md.
    """
    if m not in GRID_BY_M:
        raise ValueError(f"M must be one of {sorted(GRID_BY_M)}; got {m}")
    if cell_aspect not in SUPPORTED_CELL_ASPECTS:
        raise ValueError(f"Unsupported cell aspect {cell_aspect!r}")
    rows, cols = GRID_BY_M[m]
    cw, ch = parse_aspect(cell_aspect)
    return simplify_aspect(cols * cw, rows * ch)


def grid_cols_rows(m: int) -> tuple[int, int]:
    """Return (cols, rows) for contact-sheet layout."""
    if m not in GRID_BY_M:
        raise ValueError(f"M must be one of {sorted(GRID_BY_M)}; got {m}")
    rows, cols = GRID_BY_M[m]
    return cols, rows


def resolve_storyboard_resolution(meta: dict[str, Any], cli: str | None = None) -> str:
    raw = (cli or meta.get("storyboard_resolution") or "2K").strip().upper()
    if raw not in STORYBOARD_RESOLUTIONS:
        raise SystemExit(f"storyboard_resolution must be 2K|4K; got {raw!r}")
    return raw


def storyboard_strategy() -> str:
    """Only production path: Kie gpt-image-2 panels at cell aspect, then local stitch."""
    return "panels_then_stitch"


def gpt_image_resolution(cell_aspect: str, preferred: str = "2K") -> str:
    """Resolution for panel generation via Kie gpt-image-2 (2K default; 4K on request)."""
    if preferred not in STORYBOARD_RESOLUTIONS:
        preferred = "2K"
    # gpt-image-2: 1:1 cannot use 4K
    if preferred == "4K" and cell_aspect == "1:1":
        return "2K"
    return preferred


def aspect_close(actual_w: int, actual_h: int, target_aspect: str, *, tol: float = 0.04) -> bool:
    """True if pixel size matches target aspect within relative tolerance."""
    if actual_w <= 0 or actual_h <= 0:
        return False
    target = aspect_to_float(target_aspect)
    return abs((actual_w / actual_h) - target) / target <= tol


def encode_dimensions(resolution: str, cell_aspect: str) -> tuple[int, int]:
    """Scrub encode size; short edge matches video_resolution (480 or 720)."""
    res = (resolution or "").strip().lower()
    short = 480 if res in {"480", "480p"} else 720
    w, h = parse_aspect(cell_aspect)
    if w >= h:
        height = short
        width = round(height * w / h)
    else:
        width = short
        height = round(width * h / w)
    width += width % 2
    height += height % 2
    return width, height


def resolve_encode_dimensions(
    cli_width: int | None,
    meta: dict[str, Any],
) -> tuple[int, int]:
    if cli_width is not None:
        cell = resolve_cell_aspect(None, meta, required=False)
        w, h = parse_aspect(cell)
        width = int(cli_width)
        width += width % 2
        height = round(width * h / w)
        height += height % 2
        return width, height
    resolution = (meta.get("video_resolution") or "480p").strip().lower()
    cell = resolve_cell_aspect(None, meta, required=False)
    return encode_dimensions(resolution, cell)
