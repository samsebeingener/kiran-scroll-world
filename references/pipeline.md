# Scroll World — pipeline (active)

Generators: **Kie** `gpt-image-2-text-to-image` (одна генерация board) + **Kie** `bytedance/seedance-2-mini` (video).

## 1. Storyboard

1. Next version: `python scripts/asset_versions.py next --dir <proj>/assets/storyboard --glob "*-board.png"`
2. Prompt → `05-image-prompts/{NNN}-storyboard.md` (шаблон `templates/storyboard-prompt.template.md`, contact sheet grid)
3. Kie board + slice (всё внутри одного скрипта):

```bash
python scripts/generate_storyboard_panels.py \
  --project <proj> \
  --prompt-file 05-image-prompts/001-storyboard.md
# --resolution 4K  if user requested 4K; default 2K from meta storyboard_resolution
```

Пишет `assets/storyboard/{NNN}-board.png` (одна генерация) и нарезает в `assets/frames/{NNN}-frame-*.png` (hard aspect gate).

4. Gate Storyboard — if reject / regenerate → новый NNN (старый файл остаётся).

## 2. Frames

Кадры уже нарезаны генератором (`active_map` в `manifest.json`). Повторный `slice_storyboard.py` — только repair.

## 3. Video legs (Seedance 2.0 Mini + chain)

Перед генерацией: `insert_placement` в meta; `video_resolution` default **480p**; длительность обязательна — per-leg `duration_sec` из journey / `video_durations` (диапазон **4–15**, дефолта нет; если не задана нигде — ошибка конфигурации).

**Цепочка:** legs = **K − 1** (`playback_chain` prefix `[1..K]`; omit → K=M). Leg 0 start/end из storyboard panels по chain; leg `i>0` start = last frame предыдущего MP4, end = storyboard `playback_chain[i+1]`.

```bash
python scripts/kie_seedance_2_mini.py \
  --workspace <ROOT> --project <proj> --leg 0 \
  --prompt-file 05-image-prompts/001-leg-00.md \
  --resolution 480p --duration 5

python scripts/kie_seedance_2_mini.py \
  --workspace <ROOT> --project <proj> --leg 1 \
  --prompt-file 05-image-prompts/001-leg-01.md \
  --resolution 480p --duration 5
```

## 4. Encode + scrub media

```bash
python scripts/encode_scrub_clips.py --project <proj>
# width auto: 480p short-edge from project.meta.json; or --width 1280
python scripts/build_scrub_media.py --project <proj>
python scripts/check_seam_compatibility.py --project <proj> --window 5
```

**One section per leg** — scrub from leg 0 `t=0` through the final leg's last frame. No still-only intro/outro bookends. See `shared/scrub-still-contract.md`.

For portfolio deployment, WebM is encoded with **VP9 CRF 32**:

```bash
python scripts/encode_portfolio_webm.py --project <proj>
```

CRF 32 is the fixed quality/size default. Do not silently use CRF 38 or
lower-quality values for production; changing it requires an explicit A/B test
and a documented decision.

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
