# Scroll World — Storyboard Generation Contract

See **`shared/media-format-contract.md`** — panel aspect = `media_aspect_ratio` in `project.meta.json`.

## Goal

**ONE Kie generation** (`gpt-image-2-text-to-image`) of a single image containing a grid of **M keyframe panels**, then **local slice** into M frames at exact **`media_aspect_ratio`** (same as Seedance video), at **2K** (default) or **4K** (user request).  
**M ∈ {3, 6, 9}** — выбирается на Journey под задачу проекта (длина пути, overlay-сцены, бюджет), не фиксируется в коде.  
Grids: 3 → 3×1, 6 → 3×2, 9 → 3×3.

## Source (only)

| Backend | How |
|---------|-----|
| **Kie** `gpt-image-2-text-to-image` via `scripts/generate_storyboard_panels.py` | ONE board request (grid of M panels) → slice |

Requires `KIE_API_KEY`. Allowed image backends: `gpt-image-2-text-to-image` (production via `generate_storyboard_panels.py`); `gpt-image-2-image-to-image` (repair only). No other image generators in this repository.

## Prompt

Prompt = `templates/storyboard-prompt.template.md`, filled into `05-image-prompts/{NNN}-storyboard.md`:

- contact sheet of {{M}} panels in a {{COLS}}x{{ROWS}} grid on **one** image
- per-panel tokens: beat / camera position / continuity landmark / from-prev leftover
- ONE CONTINUOUS WORLD: one diorama territory, one camera flight, shared ground/light/materials — continuity runs across the whole board
- no text, letters, numbers, logos, watermarks inside cells (Russian/brand copy = DOM overlays later)

**In Kie уходит ОДИН запрос** с этим промптом.

## Aspect ratios

**Cell / panel** = `media_aspect_ratio` from meta (`16:9` default). **Video** = same value.

| M (из Journey) | Grid | Board aspect (cell 16:9) |
|----------------|------|--------------------------|
| 3 | 3×1 | 16:3 |
| 6 | 3×2 | 8:3 |
| 9 | 3×3 | 16:9 |

Board aspect может не входить в whitelist Kie API. Правило выбора `aspect_ratio` для запроса (см. `choose_request_aspect` в `media_format.py` / `SUPPORTED` в `generate_storyboard_panels.py`):

> Из whitelist берётся **ближайший aspect с соотношением ширина/высота >= board**. Лишнее по ширине/высоте обрезает `slice_storyboard.py` (centre-crop к точному grid aspect перед нарезкой). Если ни один aspect whitelist не покрывает board — `SystemExit` с подсказкой сменить M / `media_aspect_ratio`.

**Hard aspect gate:** после slice каждая панель обязана соответствовать `media_aspect_ratio` (`aspect_close` в `slice_storyboard.py`). Если board не режется в `media_aspect_ratio` — `SystemExit`; repair = **новая генерация board** (новый NNN) с более подходящим grid/aspect, а не ослабление gate.

## CLI

```bash
# одна генерация → board → slice (всё внутри одного скрипта)
python scripts/generate_storyboard_panels.py \
  --project <path> \
  --prompt-file 05-image-prompts/001-storyboard.md
# optional: --resolution 4K   (or meta storyboard_resolution)

# отдельная нарезка существующего board (если нужно)
python scripts/slice_storyboard.py --project <path> --frames <M>
```

Writes:

```text
assets/storyboard/{NNN}-board.png                       # one-generation board
assets/frames/{NNN}-frame-01.png … {NNN}-frame-0M.png   # exact cell aspect
```

## Continuity (required)

See `shared/cinematic-transition-contract.md`.

- One continuous world / camera path across the whole board
- Each panel further along the same flight
- Neighbor panels share a readable landmark
- Do not generate if journey lacks `## Transition plan`

## Outputs (versioned)

```text
assets/storyboard/001-board.png     # never overwrite; new regenerate = new NNN
assets/frames/001-frame-01.png …
05-image-prompts/001-storyboard.md
```

Active frame set: `manifest.json` → `frames.active_map`.
