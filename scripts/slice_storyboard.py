#!/usr/bin/env python3
"""Board→frames slicer with centre-crop + hard aspect gate (production path).

The board comes from ONE Kie generation (generate_storyboard_panels.py). Before
any crop/slice, ``validate_board_pixels_for_grid`` refuses boards whose pixel AR
is too narrow for the contact sheet (e.g. Kie returned 2:1 when 3:1 / 3×2 was
required). If the requested Kie aspect is wider than the exact grid aspect, the
excess is centre-cropped before the equal-grid slice. Each cell must then match
media_aspect_ratio (aspect_close) or the script exits — repair via a new board
generation with a better grid/aspect, not by weakening the gate.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image

from asset_versions import (
    format_version,
    parse_version_prefix,
    set_frame_active_map,
)
from media_format import (
    aspect_close,
    choose_request_aspect,
    load_project_meta,
    parse_aspect,
    resolve_cell_aspect,
    validate_board_pixels_for_grid,
)

GRID_FOR_FRAMES = {
    3: (3, 1),  # cols x rows
    6: (3, 2),
    9: (3, 3),
}

# Post-slice content gate (white-studio + subject; also catches blank/cut cells).
_DARK_LUMA = 200
_NEAR_WHITE_LUMA = 245
_MIN_DARK_RATIO = 0.08
_SPARSE_DARK_RATIO = 0.15
_EDGE_STRIP_FRAC = 0.15
_EDGE_MASS_FAIL = 0.75
_BLANK_STD = 20.0
_BLANK_MEAN = 240.0


def _luma_stats(cell: Image.Image) -> dict[str, float]:
    """Cheap luminance stats for sliced cell QA (no numpy)."""
    gray = cell.convert("L")
    w, h = gray.size
    if w < 8 or h < 8:
        return {
            "dark_ratio": 0.0,
            "white_ratio": 1.0,
            "mean": 255.0,
            "std": 0.0,
            "edge_max": 1.0,
        }
    pixels = list(gray.getdata())
    n = len(pixels)
    mean = sum(pixels) / n
    var = sum((p - mean) ** 2 for p in pixels) / n
    std = var**0.5
    dark_n = sum(1 for p in pixels if p < _DARK_LUMA)
    white_n = sum(1 for p in pixels if p > _NEAR_WHITE_LUMA)
    dark_ratio = dark_n / n
    white_ratio = white_n / n

    strip_w = max(1, int(w * _EDGE_STRIP_FRAC))
    strip_h = max(1, int(h * _EDGE_STRIP_FRAC))
    # Row-major flat index: y * w + x
    def edge_dark_frac(xs: range, ys: range) -> float:
        if dark_n == 0:
            return 0.0
        hit = 0
        for y in ys:
            row = y * w
            for x in xs:
                if pixels[row + x] < _DARK_LUMA:
                    hit += 1
        return hit / dark_n

    left = edge_dark_frac(range(0, strip_w), range(h))
    right = edge_dark_frac(range(w - strip_w, w), range(h))
    top = edge_dark_frac(range(w), range(0, strip_h))
    bottom = edge_dark_frac(range(w), range(h - strip_h, h))
    return {
        "dark_ratio": dark_ratio,
        "white_ratio": white_ratio,
        "mean": mean,
        "std": std,
        "edge_max": max(left, right, top, bottom),
    }


def cell_content_issues(cell: Image.Image, cell_idx: int) -> list[str]:
    """Return human-readable issues for one sliced cell (empty list = OK)."""
    s = _luma_stats(cell)
    issues: list[str] = []
    if s["std"] < _BLANK_STD and s["mean"] > _BLANK_MEAN:
        issues.append(
            f"cell {cell_idx}: blank/near-uniform "
            f"(mean={s['mean']:.0f} std={s['std']:.1f})"
        )
    if s["dark_ratio"] < _MIN_DARK_RATIO:
        issues.append(
            f"cell {cell_idx}: almost no subject "
            f"(dark_ratio={s['dark_ratio']:.3f} < {_MIN_DARK_RATIO})"
        )
    # Sparse subject glued to one edge → classic wrong-grid / half-cut slice
    if s["dark_ratio"] < _SPARSE_DARK_RATIO and s["edge_max"] >= _EDGE_MASS_FAIL:
        issues.append(
            f"cell {cell_idx}: subject glued to one edge "
            f"(dark_ratio={s['dark_ratio']:.3f}, edge_mass={s['edge_max']:.2f}) "
            f"— likely bad grid slice / cut-off panel"
        )
    return issues


def validate_sliced_cells_content(cells: list[tuple[int, Image.Image]]) -> None:
    """Hard-fail if any sliced cell looks empty or half-cut."""
    issues: list[str] = []
    for idx, im in cells:
        issues.extend(cell_content_issues(im, idx))
    if issues:
        joined = "; ".join(issues)
        raise SystemExit(
            f"SLICE CONTENT GATE: {joined}. "
            "Do not trust these frames — regenerate the board "
            "(generate_storyboard_panels.py) after fixing prompt/aspect."
        )


def resolve_board(project: Path, board_version: int | None, explicit: Path | None) -> tuple[Path, int]:
    if explicit is not None:
        path = explicit if explicit.is_absolute() else (project / explicit)
        v = parse_version_prefix(path.name)
        if v is None:
            raise SystemExit(f"Board filename must start with NNN- prefix: {path.name}")
        return path, v

    sb_dir = project / "assets" / "storyboard"
    if board_version is not None:
        path = sb_dir / f"{format_version(board_version)}-board.png"
        if not path.is_file():
            raise SystemExit(f"Missing board: {path}")
        return path, board_version

    versions = []
    if sb_dir.is_dir():
        for p in sb_dir.glob("*-board.png"):
            v = parse_version_prefix(p.name)
            if v is not None:
                versions.append((v, p))
    if not versions:
        raise SystemExit(
            "No versioned board found. Expected assets/storyboard/001-board.png "
            "(use generate_storyboard_panels.py)."
        )
    v, path = max(versions, key=lambda t: t[0])
    return path, v


def _crop_to_grid_aspect(image: Image.Image, cols: int, rows: int, cell_aspect: str) -> Image.Image:
    """Centre-crop board to the exact grid aspect (cols*cw : rows*ch)."""
    cw, ch = parse_aspect(cell_aspect)
    target = (cols * cw) / (rows * ch)
    w, h = image.size
    current = w / h
    if abs(current - target) / target <= 1e-3:
        return image
    if current > target:  # too wide — trim left/right
        new_w = round(h * target)
        left = (w - new_w) // 2
        return image.crop((left, 0, left + new_w, h))
    new_h = round(w / target)  # too tall — trim top/bottom
    upper = (h - new_h) // 2
    return image.crop((0, upper, w, upper + new_h))


def slice_board(
    project: Path,
    board: Path,
    *,
    frames: int,
    version: int,
    gutter: int = 2,
    cells: set[int] | None = None,
    merge: bool = True,
    skip_content_gate: bool = False,
) -> dict[str, str]:
    """Slice a versioned board into assets/frames/{NNN}-frame-*.png. Returns active_map."""
    project = project.resolve()
    meta = load_project_meta(project)
    cell_aspect = resolve_cell_aspect(None, meta)
    ver = format_version(version)

    cols, rows = GRID_FOR_FRAMES[frames]
    out_dir = project / "assets" / "frames"
    out_dir.mkdir(parents=True, exist_ok=True)

    image = Image.open(board).convert("RGB")
    # Refuse wrong Kie output BEFORE centre-crop (crop cannot fix a flipped grid).
    supported = frozenset(
        {
            "1:1",
            "3:2",
            "2:3",
            "4:3",
            "3:4",
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
    try:
        request_aspect = choose_request_aspect(cols, rows, cell_aspect, supported)
    except ValueError:
        request_aspect = None
    bw, bh = image.size
    validate_board_pixels_for_grid(
        bw,
        bh,
        cols=cols,
        rows=rows,
        cell_aspect=cell_aspect,
        request_aspect=request_aspect,
    )
    print(
        f"board_ok size={bw}x{bh} ar={bw / bh:.4f} "
        f"grid={cols}x{rows} cell={cell_aspect} request_aspect={request_aspect}",
        flush=True,
    )
    image = _crop_to_grid_aspect(image, cols, rows, cell_aspect)
    width, height = image.size
    cell_w = width // cols
    cell_h = height // rows
    gutter = max(gutter, 0)

    selected = cells if cells is not None else set(range(1, frames + 1))

    # Crop all selected cells first → content QA → then write (no half-bad active_map).
    pending: list[tuple[int, Image.Image]] = []
    for i in range(frames):
        cell_idx = i + 1
        if cell_idx not in selected:
            continue
        col = i % cols
        row = i // cols
        left = col * cell_w + gutter
        upper = row * cell_h + gutter
        right = (col + 1) * cell_w - gutter
        lower = (row + 1) * cell_h - gutter
        cell = image.crop((left, upper, right, lower))
        cw, ch = cell.size
        if not aspect_close(cw, ch, cell_aspect):
            raise SystemExit(
                f"Sliced cell {cell_idx} is {cw}x{ch} (~{cw / ch:.4f}), "
                f"expected media_aspect_ratio {cell_aspect}. "
                "Repair: regenerate the board via generate_storyboard_panels.py "
                "with a grid/aspect that slices into media_aspect_ratio cells."
            )
        pending.append((cell_idx, cell))

    if skip_content_gate:
        print("WARN: --skip-content-gate — empty/edge-cut QA disabled", flush=True)
    else:
        validate_sliced_cells_content(pending)
    for cell_idx, cell in pending:
        s = _luma_stats(cell)
        print(
            f"cell_{cell_idx:02d}_qa dark={s['dark_ratio']:.3f} "
            f"white={s['white_ratio']:.3f} edge_max={s['edge_max']:.2f}",
            flush=True,
        )

    active_map: dict[str, str] = {}
    for cell_idx, cell in pending:
        dest = out_dir / f"{ver}-frame-{cell_idx:02d}.png"
        cell.save(dest)
        rel = str(dest.relative_to(project)).replace("\\", "/")
        active_map[str(cell_idx)] = rel
        print(dest)

    set_frame_active_map(project, active_map, merge=merge)
    return active_map


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Slice one-generation board into frames (hard aspect gate)"
    )
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--frames", type=int, choices=[3, 6, 9], required=True)
    parser.add_argument("--input", type=Path, default=None, help="Versioned board path")
    parser.add_argument("--board-version", type=int, default=None, help="e.g. 2 for 002-board.png")
    parser.add_argument(
        "--only-cells",
        type=str,
        default=None,
        help="Comma list of 1-based cell indexes to write/update in active_map (default: all)",
    )
    parser.add_argument("--gutter", type=int, default=2)
    parser.add_argument(
        "--skip-content-gate",
        action="store_true",
        help="Skip post-slice empty/edge-cut content QA (repair only)",
    )
    parser.add_argument(
        "--replace-active-map",
        action="store_true",
        help="Replace entire active_map instead of merging selected cells",
    )
    args = parser.parse_args()

    project = args.project.resolve()
    board, board_ver = resolve_board(project, args.board_version, args.input)
    ver = format_version(board_ver)

    cells = None
    if args.only_cells:
        cells = {int(x.strip()) for x in args.only_cells.split(",") if x.strip()}

    slice_board(
        project,
        board,
        frames=args.frames,
        version=board_ver,
        gutter=args.gutter,
        cells=cells,
        merge=not args.replace_active_map,
        skip_content_gate=args.skip_content_gate,
    )
    print(f"board_version={ver} cells={sorted(cells) if cells else list(range(1, args.frames + 1))}")


if __name__ == "__main__":
    main()
