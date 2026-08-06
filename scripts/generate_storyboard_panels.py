#!/usr/bin/env python3
"""Generate ONE storyboard board via Kie gpt-image-2, then slice.

Two backend modes (shared/storyboard-generation-contract.md):
  - text-to-image (gpt-image-2-text-to-image) — default, no user references.
  - image-to-image (gpt-image-2-image-to-image) — when the user supplied
    storyboard reference images. Local files are first uploaded through the
    Kie File Upload API (scripts/kie_file_upload.py) and the resulting HTTPS
    fileUrls are passed as image input. The image-to-image endpoint/payload
    follows the Kie docs for gpt-image-2-image-to-image (image urls input).

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

from PIL import Image

from asset_versions import format_version, next_version, register_storyboard
from kie_common import KieTaskClient, extract_kie_prompt_from_markdown
from kie_file_upload import KieFileUploadClient
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
    validate_board_pixels_for_grid,
)
from slice_storyboard import slice_board

MODEL_T2I = "gpt-image-2-text-to-image"
MODEL_I2I = "gpt-image-2-image-to-image"
MAX_REFERENCES = 8
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
        image_urls: list[str] | None = None,
        callback_url: str | None = None,
    ) -> str:
        if aspect_ratio not in SUPPORTED:
            raise ValueError(f"Unsupported aspect_ratio {aspect_ratio!r}")
        if aspect_ratio == "1:1" and resolution == "4K":
            raise ValueError("1:1 cannot use 4K")
        model = MODEL_I2I if image_urls else MODEL_T2I
        input_payload: dict[str, Any] = {
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "resolution": resolution,
        }
        # gpt-image-2-image-to-image: reference image urls as image input
        # (endpoint/payload per Kie docs for gpt-image-2-image-to-image).
        if image_urls:
            input_payload["image_urls"] = image_urls
        payload: dict[str, Any] = {"model": model, "input": input_payload}
        if callback_url:
            payload["callBackUrl"] = callback_url
        return self.create_task_raw(payload)


def resolve_storyboard_references(
    meta: dict[str, Any], cli_refs: list[Path] | None
) -> list[Path]:
    """CLI --reference wins; else meta.storyboard_references (local paths)."""
    raw: list[str] = []
    if cli_refs:
        raw = [str(p) for p in cli_refs]
    else:
        meta_refs = meta.get("storyboard_references")
        if isinstance(meta_refs, list):
            raw = [str(p) for p in meta_refs if str(p).strip()]
        elif isinstance(meta_refs, str) and meta_refs.strip():
            raw = [meta_refs.strip()]
    if len(raw) > MAX_REFERENCES:
        raise SystemExit(
            f"Too many storyboard references ({len(raw)} > {MAX_REFERENCES})"
        )
    paths = [Path(p).expanduser().resolve() for p in raw]
    missing = [str(p) for p in paths if not p.is_file()]
    if missing:
        raise SystemExit(f"Storyboard reference file(s) not found: {missing}")
    return paths


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
    parser.add_argument(
        "--reference",
        type=Path,
        action="append",
        default=None,
        help="Local storyboard reference image (repeatable). "
        "Presence switches to gpt-image-2-image-to-image; files are uploaded "
        "via the Kie File Upload API first. Overrides meta storyboard_references.",
    )
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
    raw_prompt = prompt_path.read_text(encoding="utf-8-sig")
    # Kie gets ONLY the ```text fence — never slug / M / grid / workaround notes.
    prompt = extract_kie_prompt_from_markdown(
        raw_prompt,
        require_text_fence=True,
        source=prompt_path,
    )
    print(f"prompt_chars={len(prompt)} (extracted from ```text fence)", flush=True)

    sb_dir = project / "assets" / "storyboard"
    sb_dir.mkdir(parents=True, exist_ok=True)

    ver_num = args.version or next_version(sb_dir, "*-board.png")
    ver = format_version(ver_num)

    refs = resolve_storyboard_references(meta, args.reference)
    model = MODEL_I2I if refs else MODEL_T2I

    print(
        f"provider=kie model={model} strategy=board_then_slice "
        f"M={m} cell={cell_aspect} grid={cols}x{rows} board_aspect={board_ratio} "
        f"request_aspect={request_aspect} resolution={resolution} version={ver} "
        f"references={len(refs)}"
    )

    if args.dry_run:
        print(
            f"would_generate board aspect={request_aspect} resolution={resolution} "
            f"-> {ver}-board.png, then slice {cols}x{rows} -> {m} frames"
        )
        return

    image_urls: list[str] | None = None
    if refs:
        uploader = KieFileUploadClient(workspace=args.workspace or project)
        image_urls = []
        for ref in refs:
            url = uploader.upload_local(ref)
            print(f"uploaded reference {ref.name} -> {url}")
            image_urls.append(url)

    client = GptImage2Client(workspace=args.workspace or project)
    print(f"createTask board {model} aspect={request_aspect} res={resolution}")
    task_id = client.create_image(prompt, request_aspect, resolution, image_urls=image_urls)
    print(f"taskId={task_id}")
    data = client.wait_for_task(task_id)
    urls = client.extract_result_urls(data)
    if not urls:
        raise SystemExit(f"No resultUrls for board: {data}")
    board_out = sb_dir / f"{ver}-board.png"
    client.download(urls[0], board_out)
    print(board_out)

    # Hard gate: Kie sometimes returns 2:1 (flipped 2×3) when asked 3:1 for 3×2.
    with Image.open(board_out) as im:
        bw, bh = im.size
    validate_board_pixels_for_grid(
        bw,
        bh,
        cols=cols,
        rows=rows,
        cell_aspect=cell_aspect,
        request_aspect=request_aspect,
    )
    print(
        f"board_aspect_ok size={bw}x{bh} ar={bw / bh:.4f} "
        f"(requested {request_aspect}, grid {cols}x{rows})",
        flush=True,
    )

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
