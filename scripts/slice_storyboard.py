#!/usr/bin/env python3
"""Board→frames slicer with centre-crop + hard aspect gate (production path).

The board comes from ONE Kie generation (generate_storyboard_panels.py). If the
requested Kie aspect is wider/taller than the exact grid aspect, the excess is
centre-cropped before the equal-grid slice. Each cell must then match
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
    load_project_meta,
    parse_aspect,
    resolve_cell_aspect,
)

GRID_FOR_FRAMES = {
    3: (3, 1),  # cols x rows
    6: (3, 2),
    9: (3, 3),
}


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
    image = _crop_to_grid_aspect(image, cols, rows, cell_aspect)
    width, height = image.size
    cell_w = width // cols
    cell_h = height // rows
    gutter = max(gutter, 0)

    selected = cells if cells is not None else set(range(1, frames + 1))

    active_map: dict[str, str] = {}
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
    )
    print(f"board_version={ver} cells={sorted(cells) if cells else list(range(1, args.frames + 1))}")


if __name__ == "__main__":
    main()
