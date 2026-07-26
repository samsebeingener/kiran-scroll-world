# Scroll World — pipeline (active)

Generators: **Kie** `gpt-image-2-text-to-image` (panels) + **Kie** `bytedance/seedance-2-mini` (video).

## 1. Storyboard

1. Next version: `python scripts/asset_versions.py next --dir <proj>/assets/storyboard --glob "*-board.png"`
2. Prompt → `05-image-prompts/{NNN}-storyboard.md`
3. Kie panels:

```bash
python scripts/generate_storyboard_panels.py \
  --project <proj> \
  --prompt-file 05-image-prompts/001-storyboard.md
# --resolution 4K  if user requested 4K; default 2K from meta storyboard_resolution
```

Writes `assets/frames/{NNN}-frame-*.png` + stitched `assets/storyboard/{NNN}-board.png`.

4. Gate Storyboard — if reject / regenerate → новый NNN (старый файл остаётся).

## 2. Frames

If `*.panels.json` exists — use panel PNGs as-is (`active_map`). Do **not** re-slice the stitched board.

## 3. Video legs (Seedance 2.0 Mini + chain)

Перед генерацией: `insert_placement` в meta; `video_resolution` default **480p**; `video_duration` default **4** (4–8).

**Цепочка:** leg 0 start/end из storyboard panels; leg `i>0` start = last frame предыдущего MP4, end = storyboard.

```bash
python scripts/kie_seedance_2_mini.py \
  --workspace <ROOT> --project <proj> --leg 0 \
  --prompt-file 05-image-prompts/001-leg-00.md \
  --resolution 480p --duration 4

python scripts/kie_seedance_2_mini.py \
  --workspace <ROOT> --project <proj> --leg 1 \
  --prompt-file 05-image-prompts/001-leg-01.md \
  --resolution 480p --duration 4
```

## 4. Encode + scrub media

```bash
python scripts/encode_scrub_clips.py --project <proj>
# width auto: 480p short-edge from project.meta.json; or --width 1280
python scripts/build_scrub_media.py --project <proj>
python scripts/check_seam_compatibility.py --project <proj> --window 5
```

**One section per leg** — scrub from leg 0 `t=0` through the final leg's last frame. No still-only intro/outro bookends. See `shared/scrub-still-contract.md`.

`check_seam_compatibility.py` is a mandatory gate after every encode. It compares
`last[5] × first[5]` for every adjacent pair, writes
`assets/seam-compatibility.json` and `assets/seam-compatibility.md`, and records
the exact endpoint MAE, best pair, improvement, and suggested outgoing trim.
`REVIEW` (best-window MAE above the configured threshold) blocks publish until
the leg is regenerated, a non-regeneration trim is applied and rechecked, or
the user explicitly accepts the seam.

## 5. Overlays + page

```bash
python scripts/build_overlays_from_plan.py --project <proj>
```

Stills from `scrub-media.json` only — video first/last frames, not storyboard panels.

## 6. Seam playback (mandatory)

See **`shared/seam-playback-contract.md`**.

- Builder copies canonical `references/scrub-engine.js` → `src/`
- Hard cut between dive legs; hold outgoing until incoming paints
- `object-position: center center`; no dissolve between legs
- `build_scrub_media.py --refresh` after every re-encode
- `check_seam_compatibility.py --window 5` after every encode; never inspect only
  the single last/first frame pair
- QA must reject white flash at seams
