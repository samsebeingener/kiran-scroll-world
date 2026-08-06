#!/usr/bin/env python3
"""Media aspect ratio helpers — one board generation + slice, encode pixels.

Storyboard and Seedance share one cell aspect from project.meta.json → media_aspect_ratio.
Storyboard: ONE Kie gpt-image-2-text-to-image board (grid of M cells), then local slice.
Video: seedance-2-mini.
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

# (rows, cols) for the one-generation board grid (board_then_slice)
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
                "Gate Pitch, or pass --frames."
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
    """Pixel aspect of the one-generation board (grid of M cells).

    Used to (a) pick the nearest Kie `aspect_ratio` for the single board request
    and (b) verify the slice grid. May not exist in the Kie whitelist (e.g. `8:3`
    for M=6, cell 16:9, grid 3×2) — then the script picks a wider whitelist ratio
    and `slice_storyboard.py` centre-crops the excess before slicing.
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
    """Only production path: ONE Kie gpt-image-2 board generation, then local slice."""
    return "board_then_slice"


def choose_request_aspect(cols: int, rows: int, cell_aspect: str, supported: set[str] | frozenset[str]) -> str:
    """Pick the Kie whitelist aspect for the single board request.

    Rule: smallest whitelist ratio with width/height >= board ratio, so the slice
    only ever centre-crops excess width/height, never invents pixels. SystemExit
    (via ValueError) if nothing is wide/tall enough.
    """
    cw, ch = parse_aspect(cell_aspect)
    target = (cols * cw) / (rows * ch)
    candidates = sorted(
        ((aspect_to_float(a), a) for a in supported if aspect_to_float(a) >= target),
        key=lambda t: t[0],
    )
    if not candidates:
        raise ValueError(
            f"No Kie aspect_ratio covers board grid {cols}x{rows} of {cell_aspect} cells "
            f"(board ratio {target:.3f}). Use a larger M grid (6 or 9) or a different "
            "media_aspect_ratio, then regenerate the board."
        )
    return candidates[0][1]


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


def validate_board_pixels_for_grid(
    width: int,
    height: int,
    *,
    cols: int,
    rows: int,
    cell_aspect: str,
    request_aspect: str | None = None,
    min_vs_grid_tol: float = 0.05,
    request_tol: float = 0.12,
) -> None:
    """Hard-fail if downloaded board cannot be a valid contact sheet for this grid.

    Kie sometimes ignores ``aspect_ratio`` (e.g. returns 2:1 when asked 3:1) and
    paints a flipped 2×3 sheet. Slicing that as 3×2 produces garbage cells.
    Refuse before centre-crop / equal-grid slice.
    """
    if width <= 0 or height <= 0:
        raise SystemExit(f"Invalid board size {width}x{height}")
    actual = width / height
    cw, ch = parse_aspect(cell_aspect)
    grid_ar = (cols * cw) / (rows * ch)

    if actual < grid_ar * (1.0 - min_vs_grid_tol):
        req_note = f" (requested {request_aspect})" if request_aspect else ""
        raise SystemExit(
            f"BOARD ASPECT GATE: board is {width}x{height} (AR {actual:.4f}){req_note}, "
            f"but {cols}x{rows} grid of {cell_aspect} cells needs AR ≥ {grid_ar:.4f} "
            f"(exact board {simplify_aspect(cols * cw, rows * ch)}). "
            f"Kie likely returned the wrong aspect or a flipped {rows}x{cols} sheet. "
            f"Do NOT slice — regenerate via generate_storyboard_panels.py."
        )

    if request_aspect:
        try:
            req = aspect_to_float(request_aspect)
        except ValueError:
            req = None
        if req and abs(actual - req) / req > request_tol:
            raise SystemExit(
                f"BOARD ASPECT GATE: board is {width}x{height} (AR {actual:.4f}), "
                f"but createTask requested aspect_ratio={request_aspect} (AR {req:.4f}). "
                f"Relative error {abs(actual - req) / req:.1%} > {request_tol:.0%}. "
                f"Do NOT slice — regenerate the board (Kie ignored aspect_ratio)."
            )


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
