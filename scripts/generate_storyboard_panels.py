#!/usr/bin/env python3
"""Generate ONE storyboard board via Kie gpt-image-2-text-to-image, then slice.

The prompt file (05-image-prompts/{NNN}-storyboard.md, built from
templates/storyboard-prompt.template.md) describes a contact sheet of M panels
in a {COLS}x{ROWS} grid on a single image. One Kie request → {NNN}-board.png →
slice_storyboard.slice_board() cuts it into M frames at media_aspect_ratio.
M (3|6|9) comes from project.meta.json frames — set on Journey / Gate Pitch.
Requires KIE_API_KEY.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from asset_versions import format_version, next_version, register_storyboard
from kie_common import KieTaskClient
from media_format import (
    board_aspect_ratio,
    choose_request_aspect,
    grid_cols_rows,
    gpt_image_resolution,
    load_project_meta,
    resolve_cell_aspect,
    resolve_frames_count,
    resolve_storyboard_resolution,
    storyboard_strategy,
)
from slice_storyboard import slice_board

MODEL = "gpt-image-2-text-to-image"
SUPPORTED = frozenset(
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


class GptImage2Client(KieTaskClient):
    def create_image(
        self,
        prompt: str,
        aspect_ratio: str,
        resolution: str = "2K",
        callback_url: str | None = None,
    ) -> str:
        if aspect_ratio not in SUPPORTED:
            raise ValueError(f"Unsupported aspect_ratio {aspect_ratio!r}")
        if aspect_ratio == "1:1" and resolution == "4K":
            raise ValueError("1:1 cannot use 4K")
        payload: dict[str, Any] = {
            "model": MODEL,
            "input": {
                "prompt": prompt,
                "aspect_ratio": aspect_ratio,
                "resolution": resolution,
            },
        }
        if callback_url:
            payload["callBackUrl"] = callback_url
        return self.create_task_raw(payload)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Kie gpt-image-2: ONE board generation (grid of M cells) + slice to frames"
    )
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--prompt-file", required=True, type=Path)
    parser.add_argument("--frames", type=int, default=None)
    parser.add_argument("--resolution", default=None, help="2K (default) or 4K")
    parser.add_argument("--workspace", type=Path, default=None)
    parser.add_argument("--version", type=int, default=None, help="Force NNN version")
    parser.add_argument("--gutter", type=int, default=2)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    project = args.project.resolve()
    meta = load_project_meta(project)
    m = resolve_frames_count(meta, args.frames)
    cell_aspect = resolve_cell_aspect(None, meta)
    preferred = resolve_storyboard_resolution(meta, args.resolution)
    resolution = gpt_image_resolution(cell_aspect, preferred)
    strategy = storyboard_strategy()
    if strategy != "board_then_slice":
        raise SystemExit(f"Unexpected strategy {strategy!r}")

    cols, rows = grid_cols_rows(m)
    board_ratio = board_aspect_ratio(m, cell_aspect)
    try:
        request_aspect = choose_request_aspect(cols, rows, cell_aspect, SUPPORTED)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
    if request_aspect == "1:1" and resolution == "4K":
        resolution = "2K"

    prompt_arg = Path(args.prompt_file)
    if prompt_arg.is_file():
        prompt_path = prompt_arg.resolve()
    else:
        prompt_path = project / prompt_arg
    if not prompt_path.is_file():
        raise SystemExit(f"Prompt file not found: {args.prompt_file}")
    prompt = prompt_path.read_text(encoding="utf-8-sig").strip()
    if not prompt:
        raise SystemExit(f"Empty prompt file: {prompt_path}")

    sb_dir = project / "assets" / "storyboard"
    sb_dir.mkdir(parents=True, exist_ok=True)

    ver_num = args.version or next_version(sb_dir, "*-board.png")
    ver = format_version(ver_num)

    print(
        f"provider=kie model={MODEL} strategy=board_then_slice "
        f"M={m} cell={cell_aspect} grid={cols}x{rows} board_aspect={board_ratio} "
        f"request_aspect={request_aspect} resolution={resolution} version={ver}"
    )

    if args.dry_run:
        print(
            f"would_generate board aspect={request_aspect} resolution={resolution} "
            f"-> {ver}-board.png, then slice {cols}x{rows} -> {m} frames"
        )
        return

    client = GptImage2Client(workspace=args.workspace or project)
    print(f"createTask board {MODEL} aspect={request_aspect} res={resolution}")
    task_id = client.create_image(prompt, request_aspect, resolution)
    print(f"taskId={task_id}")
    data = client.wait_for_task(task_id)
    urls = client.extract_result_urls(data)
    if not urls:
        raise SystemExit(f"No resultUrls for board: {data}")
    board_out = sb_dir / f"{ver}-board.png"
    client.download(urls[0], board_out)
    print(board_out)

    rel_board = str(board_out.relative_to(project)).replace("\\", "/")
    register_storyboard(project, ver_num, rel_board, set_active=True)

    slice_board(
        project,
        board_out,
        frames=m,
        version=ver_num,
        gutter=args.gutter,
    )
    print(f"sliced {m} frames from {ver}-board.png")


if __name__ == "__main__":
    main()
