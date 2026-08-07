#!/usr/bin/env python3
"""Media aspect ratio helpers — one board generation + slice, encode pixels.

Pipeline (no hand-waved 16:9):
  1) User / intake sets ``media_aspect_ratio`` = Seedance cell
     (1:1 | 4:3 | 3:4 | 16:9 | 9:16 | 21:9)
  2) M ∈ {3,6,9} → grid → exact board aspect = cols×cell_w : rows×cell_h
  3) Kie board ``aspect_ratio`` + ``resolution`` chosen so the canvas can hold
     that grid (2K/4K cannot use 3:1 / 1:3 / … → may force 1K)
  4) Slice → frames at ``media_aspect_ratio`` (= Seedance video)
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Any

# Seedance 2 Mini video / cell aspects (shared with sliced frames).
SUPPORTED_CELL_ASPECTS = frozenset({"16:9", "9:16", "4:3", "3:4", "1:1", "21:9"})
# Only used when required=False (legacy); production paths require meta.
DEFAULT_CELL_ASPECT = "16:9"

# gpt-image-2 whitelist (1K). Docs: 2K/4K disallow 5:4, 4:5, 3:1, 1:3, 9:21.
GPT_IMAGE_ASPECTS_1K = frozenset(
    {
        "1:1",
        "3:2",
        "2:3",
        "4:3",
        "3:4",
        "5:4",
        "4:5",
        "16:9",
        "9:16",
        "2:1",
        "1:2",
        "3:1",
        "1:3",
        "21:9",
        "9:21",
    }
)
GPT_IMAGE_ASPECTS_BLOCKED_AT_2K_4K = frozenset({"5:4", "4:5", "3:1", "1:3", "9:21"})

STORYBOARD_RESOLUTIONS = frozenset({"1K", "2K", "4K"})
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
    """Seedance + sliced-frame aspect from intake (never assume a fixed ratio)."""
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
                "Ask user on intake (RU) — Seedance: 1:1 / 4:3 / 3:4 / 16:9 / 9:16 / 21:9. "
                "That value IS each storyboard frame after slice AND each video leg."
            )
        return DEFAULT_CELL_ASPECT
    if raw not in SUPPORTED_CELL_ASPECTS:
        raise SystemExit(
            f"Unsupported media_aspect_ratio {raw!r}. "
            f"Seedance / cell must be one of: {', '.join(sorted(SUPPORTED_CELL_ASPECTS))}"
        )
    return raw


def board_aspect_ratio(m: int, cell_aspect: str) -> str:
    """Exact contact-sheet aspect for M cells of ``cell_aspect`` (math, not Kie param)."""
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
    """Preferred board resolution (may be overridden to 1K if aspect requires it)."""
    raw = (cli or meta.get("storyboard_resolution") or "2K").strip().upper()
    if raw not in STORYBOARD_RESOLUTIONS:
        raise SystemExit(f"storyboard_resolution must be 1K|2K|4K; got {raw!r}")
    return raw


def storyboard_strategy() -> str:
    """Only production path: ONE Kie gpt-image-2 board generation, then local slice."""
    return "board_then_slice"


def kie_aspects_for_resolution(resolution: str) -> frozenset[str]:
    """gpt-image-2 aspect whitelist for a resolution tier."""
    res = resolution.strip().upper()
    if res == "1K":
        return GPT_IMAGE_ASPECTS_1K
    if res in {"2K", "4K"}:
        return GPT_IMAGE_ASPECTS_1K - GPT_IMAGE_ASPECTS_BLOCKED_AT_2K_4K
    raise ValueError(f"Unknown storyboard resolution {resolution!r}")


def choose_request_aspect(
    cols: int, rows: int, cell_aspect: str, supported: set[str] | frozenset[str]
) -> str:
    """Smallest whitelist aspect with W/H >= exact grid board ratio."""
    cw, ch = parse_aspect(cell_aspect)
    target = (cols * cw) / (rows * ch)
    candidates = sorted(
        ((aspect_to_float(a), a) for a in supported if aspect_to_float(a) >= target),
        key=lambda t: t[0],
    )
    if not candidates:
        raise ValueError(
            f"No Kie aspect_ratio covers board grid {cols}x{rows} of {cell_aspect} cells "
            f"(board ratio {target:.3f}). Change M or media_aspect_ratio, or use 1K if "
            f"the covering aspect is 3:1/1:3 (blocked at 2K/4K)."
        )
    return candidates[0][1]


def resolve_storyboard_request(
    *,
    m: int,
    cell_aspect: str,
    preferred_resolution: str,
) -> dict[str, Any]:
    """Compute board request from video cell + M (single source of truth).

    Returns dict with: cols, rows, cell_aspect, exact_board_aspect, request_aspect,
    resolution, preferred_resolution, resolution_forced_1k (bool), note (str).
    """
    cols, rows = grid_cols_rows(m)
    exact = board_aspect_ratio(m, cell_aspect)
    preferred = preferred_resolution.strip().upper()
    if preferred not in STORYBOARD_RESOLUTIONS:
        preferred = "2K"

    # Try preferred → 2K → 4K → 1K (1K last: only tier that allows 3:1 / 1:3).
    try_order: list[str] = []
    for res in (preferred, "2K", "4K", "1K"):
        if res not in try_order and res in STORYBOARD_RESOLUTIONS:
            try_order.append(res)

    errors: list[str] = []
    for res in try_order:
        if res == "4K" and cell_aspect == "1:1":
            errors.append("4K+1:1 unsupported by gpt-image-2")
            continue
        supported = kie_aspects_for_resolution(res)
        try:
            request_aspect = choose_request_aspect(cols, rows, cell_aspect, supported)
        except ValueError as exc:
            errors.append(f"{res}: {exc}")
            continue
        if request_aspect not in supported:
            errors.append(f"{res}: picked {request_aspect} not in whitelist")
            continue
        forced = res == "1K" and preferred != "1K"
        note = ""
        if forced:
            note = (
                f"preferred {preferred} cannot cover exact board {exact} "
                f"(need canvas ≥ {exact}; 2K/4K block 3:1/1:3) → using 1K + {request_aspect}"
            )
        return {
            "m": m,
            "cols": cols,
            "rows": rows,
            "cell_aspect": cell_aspect,
            "exact_board_aspect": exact,
            "request_aspect": request_aspect,
            "resolution": res,
            "preferred_resolution": preferred,
            "resolution_forced_1k": forced,
            "note": note,
        }

    raise SystemExit(
        "Cannot resolve storyboard Kie aspect+resolution for "
        f"M={m} cell={cell_aspect} exact_board={exact} preferred={preferred}. "
        f"Tried: {try_order}. Errors: {' | '.join(errors)}"
    )


def build_storyboard_format_lock(
    *,
    m: int,
    cols: int,
    rows: int,
    cell_aspect: str,
    request_aspect: str,
    resolution: str | None = None,
) -> str:
    """Machine-computed FORMAT LOCK prepended to the Kie storyboard prompt."""
    exact = board_aspect_ratio(m, cell_aspect)
    exact_f = aspect_to_float(exact)
    req_f = aspect_to_float(request_aspect)
    res_line = f"- Kie createTask resolution: {resolution}\n" if resolution else ""
    wider_note = ""
    if abs(req_f - exact_f) / exact_f > 0.02:
        wider_note = (
            f"- NOTE: API canvas {request_aspect} differs from exact grid {exact}; "
            f"fill the full {request_aspect} canvas with an equal {cols}×{rows} contact sheet "
            f"(thin white gutters). Local slice = equal-grid on full board, then each cell "
            f"centre-cropped to {cell_aspect}. Do NOT invent a {rows}×{cols} flipped layout.\n"
        )
    return (
        "FORMAT LOCK (COMPUTED — BINDING; do not contradict):\n"
        f"- Kie createTask aspect_ratio (WHOLE IMAGE canvas): {request_aspect}\n"
        f"{res_line}"
        f"- Exact math for {cols} COLUMNS × {rows} ROWS of {cell_aspect} cells: {exact} "
        f"(ratio {exact_f:.4f})\n"
        f"- Grid: {cols} COLUMNS × {rows} ROWS = {m} panels. Order L→R, then T→B "
        f"(top row 1…{cols}, next rows continue). FORBIDDEN: {rows}×{cols} flip, "
        f"portrait stack, 1×{m}, {m}×1.\n"
        f"- EACH panel/cell (after local slice) = {cell_aspect} — SAME as Seedance video "
        f"media_aspect_ratio. {cell_aspect} is NOT the whole-image canvas.\n"
        f"{wider_note}"
        f"- Equal thin white gutters between panels. Continuity across the sheet.\n"
    )


def gpt_image_resolution(cell_aspect: str, preferred: str = "2K") -> str:
    """Legacy helper — prefer ``resolve_storyboard_request`` in new code."""
    preferred = (preferred or "2K").strip().upper()
    if preferred not in STORYBOARD_RESOLUTIONS:
        preferred = "2K"
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
    """Hard-fail if downloaded board cannot be a valid contact sheet for this grid."""
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
