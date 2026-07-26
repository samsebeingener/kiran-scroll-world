#!/usr/bin/env python3
"""Generate M storyboard panels via Kie gpt-image-2-text-to-image, then stitch board.

Each panel is generated at exact media_aspect_ratio (2K default / 4K on request).
M (3|6|9) comes from project.meta.json frames — set on Journey / Gate Budget, not hardcoded.
Stitched board aspect (e.g. 8:3) is local PIL only; never sent to Kie as aspect_ratio.
Requires KIE_API_KEY. Local stitch is for Gate review only — video uses the panel PNGs.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from asset_versions import format_version, next_version, register_storyboard, set_frame_active_map
from kie_common import KieTaskClient
from media_format import (
    grid_cols_rows,
    gpt_image_resolution,
    load_project_meta,
    resolve_cell_aspect,
    resolve_frames_count,
    resolve_storyboard_resolution,
    storyboard_strategy,
)
from stitch_storyboard import stitch_frames_to_board

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


def _panel_prompt(base: str, *, panel: int, m: int, cell_aspect: str) -> str:
    suffix = (
        f"\n\nOUTPUT CONSTRAINT (CRITICAL):\n"
        f"Generate ONLY keyframe panel {panel} of {m} as a SINGLE standalone "
        f"{cell_aspect} image. Do NOT draw a contact sheet, grid, or other panels. "
        f"Fill the full frame with this one camera position. "
        f"No text, letters, numbers, logos, watermarks."
    )
    beat = re.search(rf"(?im)^\s*{panel}\)\s*(.+)$", base)
    if beat:
        focus = f"\nFOCUS THIS IMAGE ON BEAT {panel}: {beat.group(1).strip()}\n"
        return base.strip() + focus + suffix
    return base.strip() + suffix


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Kie gpt-image-2: M panels at cell aspect (2K/4K) + stitch review board"
    )
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--prompt-file", required=True, type=Path)
    parser.add_argument("--frames", type=int, default=None)
    parser.add_argument("--resolution", default=None, help="2K (default) or 4K")
    parser.add_argument("--workspace", type=Path, default=None)
    parser.add_argument("--version", type=int, default=None, help="Force NNN version")
    parser.add_argument(
        "--only-panels",
        type=str,
        default=None,
        help="Comma list of 1-based panel indexes (default: all)",
    )
    parser.add_argument("--gutter", type=int, default=8)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    project = args.project.resolve()
    meta = load_project_meta(project)
    m = resolve_frames_count(meta, args.frames)
    cell_aspect = resolve_cell_aspect(None, meta)
    preferred = resolve_storyboard_resolution(meta, args.resolution)
    resolution = gpt_image_resolution(m, cell_aspect, preferred)
    strategy = storyboard_strategy(m, cell_aspect, resolution)
    if strategy != "panels_then_stitch":
        raise SystemExit(f"Unexpected strategy {strategy!r}")

    prompt_arg = Path(args.prompt_file)
    if prompt_arg.is_file():
        prompt_path = prompt_arg.resolve()
    else:
        prompt_path = project / prompt_arg
    if not prompt_path.is_file():
        raise SystemExit(f"Prompt file not found: {args.prompt_file}")
    base_prompt = prompt_path.read_text(encoding="utf-8-sig").strip()
    if not base_prompt:
        raise SystemExit(f"Empty prompt file: {prompt_path}")

    if args.only_panels:
        panels = sorted({int(x.strip()) for x in args.only_panels.split(",") if x.strip()})
    else:
        panels = list(range(1, m + 1))
    for p in panels:
        if p < 1 or p > m:
            raise SystemExit(f"Panel {p} out of range 1..{m}")

    frames_dir = project / "assets" / "frames"
    sb_dir = project / "assets" / "storyboard"
    frames_dir.mkdir(parents=True, exist_ok=True)
    sb_dir.mkdir(parents=True, exist_ok=True)

    ver_num = args.version or next_version(sb_dir, "*-board.png")
    ver = format_version(ver_num)
    cols, rows = grid_cols_rows(m)

    print(
        f"provider=kie model={MODEL} strategy=panels_then_stitch "
        f"M={m} cell={cell_aspect} resolution={resolution} grid={cols}x{rows} version={ver}"
    )

    if args.dry_run:
        for p in panels:
            print(f"would_generate panel={p} aspect={cell_aspect} resolution={resolution}")
        print(f"would_stitch {ver}-board.png")
        return

    client = GptImage2Client(workspace=args.workspace or project)
    active_map: dict[str, str] = {}
    jobs: list[dict[str, Any]] = []

    for p in panels:
        panel_prompt = _panel_prompt(base_prompt, panel=p, m=m, cell_aspect=cell_aspect)
        print(f"createTask panel={p} {MODEL} aspect={cell_aspect} res={resolution}")
        task_id = client.create_image(panel_prompt, cell_aspect, resolution)
        print(f"taskId={task_id}")
        data = client.wait_for_task(task_id)
        urls = client.extract_result_urls(data)
        if not urls:
            raise SystemExit(f"No resultUrls for panel {p}: {data}")
        dest = frames_dir / f"{ver}-frame-{p:02d}.png"
        client.download(urls[0], dest)
        rel = str(dest.relative_to(project)).replace("\\", "/")
        active_map[str(p)] = rel
        jobs.append({"panel": p, "taskId": task_id, "url": urls[0], "path": rel})
        print(dest)

    set_frame_active_map(project, active_map, merge=bool(args.only_panels))

    frame_paths = [frames_dir / f"{ver}-frame-{i:02d}.png" for i in range(1, m + 1)]
    if all(p.is_file() for p in frame_paths):
        board_out = sb_dir / f"{ver}-board.png"
        stitch_frames_to_board(
            frame_paths,
            board_out,
            cols=cols,
            rows=rows,
            gutter=args.gutter,
        )
        rel_board = str(board_out.relative_to(project)).replace("\\", "/")
        register_storyboard(project, ver_num, rel_board, set_active=True)
        print(board_out)
    else:
        missing = [str(p) for p in frame_paths if not p.is_file()]
        print(f"WARN: skip stitch; missing frames: {missing}")

    meta_path = sb_dir / f"{ver}-board.panels.json"
    meta_path.write_text(
        json.dumps(
            {
                "provider": "kie",
                "model": MODEL,
                "strategy": "panels_then_stitch",
                "version": ver,
                "frames": m,
                "cell_aspect": cell_aspect,
                "resolution": resolution,
                "panels": jobs,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
