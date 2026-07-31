# Scroll World — Media Format Contract

## Problem

Storyboard **panels** and Seedance video legs **must share one cell aspect ratio**.  
The storyboard is born as **one board image** (grid of M panels) from a single Kie request; the slice must yield cells at exactly `media_aspect_ratio` — this is guarded by a hard aspect gate in `slice_storyboard.py`.

## Single source of truth

`project.meta.json`:

| Field | Meaning |
|-------|---------|
| `media_aspect_ratio` | Aspect of **each keyframe panel** and **each video leg** |
| `storyboard_resolution` | `2K` (default) \| `4K` — Kie gpt-image-2 budget for the one board request |
| `video_resolution` | `480p` (default) \| `720p` — Seedance / encode short edge |
| `insert_placement` | Where the block sits on the page |
| `frames` | **M** — число keyframe-панелей; задаётся на **Journey / Gate Pitch** под задачу проекта (не хардкод в коде) |

Legacy alias: `video_aspect_ratio` → read as `media_aspect_ratio` if the latter is missing.

## M / K — доска и playback

| Символ | Смысл |
|--------|--------|
| **M** | Размер доски (число keyframe-панелей). **M ∈ {3, 6, 9}** (сетки 3×1, 3×2, 3×3). |
| **K** | Длина **текущей** playback-цепочки. **K ≤ M**. Панели PREFIX `[1..K]`. |
| **reserve** | Хвост доски TAIL `[K+1..M]` — на продолжение, без видео сейчас. |
| **legs_now** | Число видео-ног **сейчас** = **K − 1** (не всегда M − 1). |

- **M не зашит в коде** — Journey: сначала оценка ног + `duration_sec` → K = legs+1 → M = min∈{3,6,9} с M≥K; пользователь подтверждает на Gate Pitch.
- До approve бюджета в `project.meta.json` может быть `"frames": null` (см. `prepare_project_folder.ps1`).
- В meta после Journey: `frames` = M; рекомендуется также `playback_chain` / K (см. `shared/memory-protocol.md`).
- Полный прогон «вся доска в видео» — частный случай **K = M**, тогда legs = M − 1.

## Kie API vs локальная нарезка (важно)

**В Kie gpt-image-2 уходит ОДИН запрос** — промпт описывает contact sheet с сеткой M панелей на одном изображении. `aspect_ratio` запроса выбирается из whitelist API  
(`16:9`, `9:16`, `4:3`, `3:4`, `1:1`, `21:9`, `2:1`, `3:1`, …). См. [Kie gpt-image-2](https://kie.ai/gpt-image-2?model=gpt-image-2-text-to-image).

Правило выбора (`choose_request_aspect` в `media_format.py`): **ближайший aspect из whitelist с соотношением ширина/высота >= board grid**. Лишнее обрезает `slice_storyboard.py` — centre-crop к точному grid aspect, затем равная нарезка по сетке. Если ни один aspect не покрывает board — `SystemExit` (сменить M или `media_aspect_ratio`, регенерировать board).

`board_aspect_ratio()` в `media_format.py` — **математика ВЫБОРА** aspect для запроса и проверки slice, не параметр API как есть (например `8:3` при M=6 и cell `16:9` в whitelist отсутствует → берётся более широкий `3:1`, излишек срезается при slice).

**Локальная сшивка не нужна** — board рождается сразу одной генерацией; `stitch_storyboard.py` в production не используется.

```text
Kie ×1:   board @ nearest whitelist aspect ≥ grid  (ОДИН запрос)
Local:    centre-crop → slice → {NNN}-frame-*.png  (hard aspect gate)
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

**Only:** Kie `gpt-image-2-text-to-image` → **ONE board request** (grid of M panels) @ **2K/4K** → `slice_storyboard.py` режет board в M кадров с hard aspect gate (`aspect_close` → `media_aspect_ratio`; mismatch = `SystemExit`, repair через новую генерацию board).

| Stage | Uses |
|-------|------|
| Storyboard board | nearest whitelist aspect ≥ grid + `storyboard_resolution` via `generate_storyboard_panels.py` |
| Frames | local slice only; every cell must match `media_aspect_ratio` |
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

`frames` = M — выставляется после Journey / Gate Pitch (`3`, `6` или `9` под задачу). Prefer `storyboard_resolution: "4K"` when the user asks.

## Pitfalls

- Do **not** hardcode `16:9` in prompts if meta says otherwise.
- Do **not** run Seedance with a different `aspect_ratio` than `media_aspect_ratio`.
- Do **not** bypass the slice aspect gate — if the board does not slice into `media_aspect_ratio` cells, regenerate the board (new NNN) with a better grid/aspect.
- Frame PNGs inherit aspect from board + slice — fix there, not in video.
