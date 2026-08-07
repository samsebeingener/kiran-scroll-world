# Scroll World — Media Format Contract

## Problem

Storyboard **panels** and Seedance video legs **must share one cell aspect ratio**.  
The storyboard is born as **one board image** (grid of M panels) from a single Kie request; the slice must yield cells at exactly `media_aspect_ratio` — this is guarded by a hard aspect gate in `slice_storyboard.py`.

## Single source of truth

`project.meta.json`:

| Field | Meaning |
|-------|---------|
| `media_aspect_ratio` | **Seedance video + каждый sliced frame** (обязателен с intake) |
| `storyboard_resolution` | Preferred board: `1K` \| `2K` (default prefer) \| `4K` — скрипт может **форсировать 1K**, если canvas требует `3:1`/`1:3` |
| `video_resolution` | `480p` (default) \| `720p` — Seedance / encode short edge |
| `insert_placement` | Where the block sits on the page |
| `frames` | **M** — keyframe panels (3\|6\|9) after Journey / Gate Pitch |

Legacy alias: `video_aspect_ratio` → `media_aspect_ratio`.

## Цепочка форматов (обязательная)

```text
1) User → media_aspect_ratio   (Seedance: 1:1 4:3 3:4 16:9 9:16 21:9)
2) M + grid → exact_board      (cols×cell_w : rows×cell_h)
3) resolve_storyboard_request → Kie aspect_ratio + resolution
     - 2K/4K FORBIDDEN aspects: 5:4, 4:5, 3:1, 1:3, 9:21
     - if covering canvas is 3:1/1:3 → use 1K automatically
4) Slice → frames @ media_aspect_ratio
5) Seedance → aspect_ratio = media_aspect_ratio  (тот же cell)
```

**Не хардкодить cell как 16:9** в промптах/агентах. Только значение из meta + computed FORMAT LOCK.

## Kie API vs локальная нарезка

| Слой | Что это | Кто считает |
|------|---------|-------------|
| **Cell / video** | `media_aspect_ratio` | intake / meta |
| **Exact board** | grid × cell | `board_aspect_ratio(M, cell)` |
| **Kie canvas** | whitelist ≥ exact | `resolve_storyboard_request` |
| **Kie resolution** | 1K\|2K\|4K с учётом блокировок 2K/4K | то же |

Промпт в createTask = **FORMAT LOCK** + ` ```text ` fence.  
JSON `aspect_ratio` = **canvas**, не cell.

```text
Kie ×1:   board @ request_aspect + resolution  + FORMAT LOCK
Local:    equal-grid on FULL board → per-cell crop to media_aspect_ratio
Seedance: aspect_ratio = media_aspect_ratio
```

## Allowed cell aspects (intake = Seedance)

**ЗАПРЕТ MISMATCH:** frames после slice == Seedance `aspect_ratio` == `media_aspect_ratio`.

| Value | When to offer (RU) |
|-------|-------------------|
| `16:9` | Горизонтальный блок / hero (частый выбор, не единственный) |
| `9:16` | Вертикальная колонка, mobile-first |
| `4:3` | Классический горизонтальный блок |
| `3:4` | Портретная вставка |
| `1:1` | Квадратная карточка |
| `21:9` | Широкая кинематографическая полоса |

Intake **must** ask **before** storyboard. Director: no Storyboard / Video without `media_aspect_ratio`.

## Production path

**Only:** Kie `gpt-image-2-*` → ONE board (`resolve_storyboard_request`) → `slice_storyboard.py` (AR gate + content gate + per-cell crop to `media_aspect_ratio`).

| Stage | Uses |
|-------|------|
| Storyboard board | computed canvas + resolution via `generate_storyboard_panels.py` |
| Frames | local slice; every cell = `media_aspect_ratio` |
| Seedance | `aspect_ratio` = **`media_aspect_ratio`** |
| encode | `video_resolution` + **`media_aspect_ratio`** |

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

- Do **not** hardcode any single cell aspect (including 16:9) as the only format — cell = `media_aspect_ratio` from intake.
- Do **not** hardcode `16:9` as the **whole board** canvas if Kie `aspect_ratio` is `3:1` (or other request aspect). Cell ≠ canvas.
- Do **not** hand-wave grid/aspect in the fence — script prepends computed FORMAT LOCK; fill tokens from `--dry-run` / `resolve_storyboard_request`.
- Do **not** request 2K/4K with canvas `3:1`/`1:3` — Kie forbids; script must use 1K.
- Do **not** run Seedance with a different `aspect_ratio` than `media_aspect_ratio`.
- Do **not** bypass the slice aspect/content gates — repair via re-slice or new board NNN.
- Some pairs are impossible (e.g. cell `21:9` + M=6 → exact board `7:2` > max Kie `3:1`) — change M or cell.
- Frame PNGs inherit aspect from board + per-cell crop — fix there, not in video.
