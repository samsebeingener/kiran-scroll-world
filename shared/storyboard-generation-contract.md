# Scroll World — Storyboard Generation Contract

See **`shared/media-format-contract.md`** — panel aspect = `media_aspect_ratio` in `project.meta.json`.

## Goal

**ONE Kie generation** of a single image containing a grid of **M keyframe panels**, then **local slice** into M frames at exact **`media_aspect_ratio`** (same as Seedance video), at **2K** (default) or **4K** (user request).  
**M ∈ {3, 6, 9}** — выбирается на Journey под задачу проекта (длина пути, overlay-сцены, бюджет), не фиксируется в коде.  
Grids: 3 → 3×1, 6 → 3×2, 9 → 3×3.

## Backend modes (two)

| Backend | When |
|---------|------|
| **Kie** `gpt-image-2-text-to-image` (2K/4K) | **Default** — пользователь НЕ дал референсы для сториборда |
| **Kie** `gpt-image-2-image-to-image` (2K/4K) | Пользователь дал референс(ы) для сториборда. Локальные файлы сначала загружаются через **Kie File Upload API** (`scripts/kie_file_upload.py`, docs.kie.ai/file-upload-api) → HTTPS `fileUrl` → передаются в запрос image-to-image как image input вместе с текстовым промптом |

Оба режима: **ONE board request** (grid of M panels) → slice. Текстовый промпт обязателен в обоих режимах (в i2i референс задаёт стиль/композицию, промпт — сцену).

Requires `KIE_API_KEY`. Allowed image backends: `gpt-image-2-text-to-image` and `gpt-image-2-image-to-image` via `scripts/generate_storyboard_panels.py`. No other image generators in this repository.

## NO TEXT ON IMAGE (MANDATORY)

**НИКАКОГО текста, букв, цифр, логотипов и водяных знаков на генерируемых изображениях — в ОБОИХ режимах (t2i и i2i).**
Русский/брендовый текст накладывается позже отдельно через **DOM overlays** (`assets/overlays.json`), НИКОГДА через генерацию.
Если на board/кадрах виден впечатанный текст — board бракуется и регенерируется (новый NNN).

## Prompt

Prompt file = `05-image-prompts/{NNN}-storyboard.md` filled from
`templates/storyboard-prompt.template.md`.

**Kie payload = only the ```text … ``` fence.** Agent notes outside the fence
(slug, M, grid, mode, journey, resolution workarounds) must **never** reach
`createTask`. `scripts/generate_storyboard_panels.py` extracts the fence and
hard-fails if it is missing or if pipeline meta leaked into the fence body.

Inside the fence:

- contact sheet of {{M}} panels in a {{COLS}}x{{ROWS}} grid on **one** image
- per-panel tokens: beat / camera position / continuity landmark / from-prev leftover
- ONE CONTINUOUS WORLD: one diorama territory, one camera flight, shared ground/light/materials — continuity runs across the whole board
- **NO TEXT ON IMAGE (MANDATORY): no text, letters, numbers, logos, watermarks inside cells** (Russian/brand copy = DOM overlays later)

**В Kie уходит ОДИН запрос** с извлечённым visual prompt. В режиме i2i к запросу добавляются HTTPS URL референсов (см. Backend modes).

## Storyboard references (meta)

Режим выбирается по наличию референсов: CLI `--reference <path>` (повторяемый) или поле meta. Пример `project.meta.json`:

```json
{
  "storyboard_references": []
}
```

- `[]` или поле отсутствует → **text-to-image**
- список локальных путей → **image-to-image** (upload через Kie File Upload API → `fileUrl`)

## Aspect ratios

**Cell / panel** = `media_aspect_ratio` from meta (`16:9` default). **Video** = same value.

| M (из Journey) | Grid | Board aspect (cell 16:9) |
|----------------|------|--------------------------|
| 3 | 3×1 | 16:3 |
| 6 | 3×2 | 8:3 |
| 9 | 3×3 | 16:9 |

Board aspect может не входить в whitelist Kie API. Правило выбора `aspect_ratio` для запроса (см. `choose_request_aspect` в `media_format.py` / `SUPPORTED` в `generate_storyboard_panels.py`):

> Из whitelist берётся **ближайший aspect с соотношением ширина/высота >= board**. Slice: **equal-grid по полному board**, затем **per-cell** centre-crop к `media_aspect_ratio`. **Запрещён** board-level centre-crop к exact grid AR (ломает gutters на full-bleed 3:1 → bleed соседней панели / left-sliver).

**Hard aspect + content gates:** после download — `validate_board_pixels_for_grid`. После slice каждая панель: (1) `aspect_close`; (2) content gate (пустой / edge-cut / **vertical seam bleed**). Fail → `SystemExit` до `active_map` (кроме `--skip-content-gate`). Repair = новая генерация board или re-slice с актуальным slicer.

## CLI

```bash
# одна генерация → board → slice (всё внутри одного скрипта)
python scripts/generate_storyboard_panels.py \
  --project <path> \
  --prompt-file 05-image-prompts/001-storyboard.md
# optional: --resolution 4K   (or meta storyboard_resolution)
# optional (i2i mode): --reference ref1.png --reference ref2.png
#   (или meta storyboard_references: ["ref1.png", ...])

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
