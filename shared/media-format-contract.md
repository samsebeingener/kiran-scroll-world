# Scroll World — Media Format Contract

## Problem

Storyboard **panels** and Seedance video legs **must share one cell aspect ratio**.  
Generating a contact sheet at a nearest board ratio then equal-grid slicing yields wrong cell aspects (e.g. near-square crops when video is `16:9`).

## Single source of truth

`project.meta.json`:

| Field | Meaning |
|-------|---------|
| `media_aspect_ratio` | Aspect of **each keyframe panel** and **each video leg** |
| `storyboard_resolution` | `2K` (default) \| `4K` — per-panel Kie gpt-image-2 budget |
| `video_resolution` | `480p` (default) \| `720p` — Seedance / encode short edge |
| `insert_placement` | Where the block sits on the page |
| `frames` | **M** — число keyframe-панелей; задаётся на **Journey / Gate Budget** под задачу проекта (не хардкод в коде) |

Legacy alias: `video_aspect_ratio` → read as `media_aspect_ratio` if the latter is missing.

## M (frames) — выбор под проект

- Допустимые значения в v1: **M ∈ {3, 6, 9}** (сетки 3×1, 3×2, 3×3).
- **M не зашит в коде** — Director/Journey предлагают M по длине пути, числу overlay-сцен и бюджету Kie; пользователь подтверждает на Gate Budget.
- До approve бюджета в `project.meta.json` может быть `"frames": null` (см. `prepare_project_folder.ps1`).
- Видео-ног = **M − 1**.

## Kie API vs локальная сшивка (важно)

**В Kie gpt-image-2** уходит только **`media_aspect_ratio` одной панели** — значение из whitelist API  
(`16:9`, `9:16`, `4:3`, `3:4`, `1:1`, `21:9`, …). См. [Kie gpt-image-2](https://kie.ai/gpt-image-2?model=gpt-image-2-text-to-image).

**Не отправлять в Kie:**

- aspect сшитого review-board (например `8:3` при M=6 и cell `16:9`) — такого ratio **нет** в API;
- `board_aspect_ratio()` в `media_format.py` — **только математика** локальной сшивки M панелей в `stitch_storyboard.py` для Gate; на генерацию и видео не влияет.

```text
Kie × M:  panel i @ media_aspect_ratio  (каждая панель отдельно)
Local:    stitch → {NNN}-board.png      (произвольный pixel aspect, не параметр API)
Seedance: aspect_ratio = media_aspect_ratio
```

## Allowed cell aspects (intake)

| Value | When to offer (RU) |
|-------|-------------------|
| `16:9` | **По умолчанию** — горизонтальный блок на лендинге / hero |
| `9:16` | Вертикальная колонка, mobile-first секция |
| `4:3` | Классический горизонтальный блок |
| `3:4` | Портретная вставка в узкой колонке |
| `1:1` | Квадратная карточка / тайл |
| `21:9` | Широкая кинематографическая полоса |

Intake **must** ask this **before** storyboard generation.  
Director gate: no Storyboard / Video without `media_aspect_ratio`.

## Production path

**Only:** Kie `gpt-image-2-text-to-image` → M separate panels at exact `media_aspect_ratio` @ **2K/4K**, then local stitch for Gate review.

| Stage | Uses |
|-------|------|
| Storyboard panels | `media_aspect_ratio` + `storyboard_resolution` via `generate_storyboard_panels.py` |
| Review board | local stitch only (does not redefine cell aspect) |
| Seedance | `aspect_ratio` = **`media_aspect_ratio`** |
| `encode_scrub_clips.py` | pixels from `video_resolution` + **`media_aspect_ratio`** |

Helper: `scripts/media_format.py`.

## project.meta.json

```json
{
  "media_aspect_ratio": "16:9",
  "storyboard_resolution": "2K",
  "video_resolution": "480p",
  "insert_placement": "hero-below-nav",
  "frames": null
}
```

`frames` = M — выставляется после Journey / Gate Budget (`3`, `6` или `9` под задачу). Prefer `storyboard_resolution: "4K"` when the user asks.

## Pitfalls

- Do **not** hardcode `16:9` in prompts if meta says otherwise.
- Do **not** run Seedance with a different `aspect_ratio` than `media_aspect_ratio`.
- Do **not** re-slice a stitched board that came from `panels.json` (gutters shrink panels).
- Panel PNGs inherit aspect at Kie generation time — fix there, not in video.
