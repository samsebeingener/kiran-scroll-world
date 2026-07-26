#!/usr/bin/env python3
"""Stitch panel PNGs (exact cell aspect) into a contact-sheet board for Gate review.

Output board pixel aspect is derived from M × grid × cell aspect (informational).
Never use board aspect as Kie gpt-image-2 aspect_ratio — API only accepts per-panel ratios.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image

from media_format import (
    aspect_close,
    grid_cols_rows,
    load_project_meta,
    resolve_cell_aspect,
    resolve_frames_count,
)


def stitch_frames_to_board(
    frame_paths: list[Path],
    out: Path,
    *,
    cols: int,
    rows: int,
    gutter: int = 8,
    bg: tuple[int, int, int] = (245, 245, 245),
) -> Path:
    if len(frame_paths) != cols * rows:
        raise SystemExit(
            f"Expected {cols * rows} frames for {cols}x{rows} grid; got {len(frame_paths)}"
        )
    images = [Image.open(p).convert("RGB") for p in frame_paths]
    tw, th = images[0].size
    for i, im in enumerate(images):
        if im.size != (tw, th):
            images[i] = im.resize((tw, th), Image.Resampling.LANCZOS)

    g = max(0, int(gutter))
    board_w = cols * tw + (cols + 1) * g
    board_h = rows * th + (rows + 1) * g
    board = Image.new("RGB", (board_w, board_h), bg)
    for i, im in enumerate(images):
        col = i % cols
        row = i // cols
        x = g + col * (tw + g)
        y = g + row * (th + g)
        board.paste(im, (x, y))
    out.parent.mkdir(parents=True, exist_ok=True)
    board.save(out)
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Stitch versioned frames into review board")
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--frames", type=int, default=None)
    parser.add_argument("--version", type=int, required=True, help="NNN of *-frame-*.png")
    parser.add_argument("--gutter", type=int, default=8)
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()

    project = args.project.resolve()
    meta = load_project_meta(project)
    m = resolve_frames_count(meta, args.frames)
    cell = resolve_cell_aspect(None, meta)
    cols, rows = grid_cols_rows(m)
    ver = f"{args.version:03d}"
    frames_dir = project / "assets" / "frames"
    paths = [frames_dir / f"{ver}-frame-{i:02d}.png" for i in range(1, m + 1)]
    missing = [p for p in paths if not p.is_file()]
    if missing:
        raise SystemExit("Missing frames:\n" + "\n".join(str(p) for p in missing))

    for p in paths:
        with Image.open(p) as im:
            w, h = im.size
        if not aspect_close(w, h, cell):
            raise SystemExit(
                f"{p.name} is {w}x{h} (~{w / h:.4f}), expected cell aspect {cell}. "
                "Regenerate with generate_storyboard_panels.py at media_aspect_ratio."
            )

    out = args.out
    if out is None:
        out = project / "assets" / "storyboard" / f"{ver}-board.png"
    elif not out.is_absolute():
        out = project / out

    stitch_frames_to_board(paths, out, cols=cols, rows=rows, gutter=args.gutter)
    print(out)


if __name__ == "__main__":
    main()
