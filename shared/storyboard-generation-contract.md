# Scroll World — Storyboard Generation Contract

See **`shared/media-format-contract.md`** — panel aspect = `media_aspect_ratio` in `project.meta.json`.

## Goal

**M keyframes** at exact **`media_aspect_ratio`** (same as Seedance video), at **2K** (default) or **4K** (user request).  
**M ∈ {3, 6, 9}** — выбирается на Journey под задачу проекта (длина пути, overlay-сцены, бюджет), не фиксируется в коде.  
A stitched contact sheet is only for human Gate review — not the source of video plates; its pixel aspect (e.g. `8:3` for M=6 + cell `16:9`) is **local stitch math only**, never a Kie `aspect_ratio`.

## Source (only)

| Backend | How |
|---------|-----|
| **Kie** `gpt-image-2-text-to-image` via `scripts/generate_storyboard_panels.py` | M panels @ cell aspect + local stitch |

Requires `KIE_API_KEY`. Allowed image backends: `gpt-image-2-text-to-image` (production via `generate_storyboard_panels.py`); `gpt-image-2-image-to-image` (repair only). No other image generators in this repository.

## Aspect ratios

**Cell / panel** = `media_aspect_ratio` from meta (`16:9` default).  
**Video** = same value.

| M (из Journey) | Grid | Production |
|----------------|------|------------|
| 3 | 3×1 | panels @ `media_aspect_ratio` |
| 6 | 3×2 | panels @ `media_aspect_ratio` |
| 9 | 3×3 | panels @ `media_aspect_ratio` |

## CLI

```bash
python scripts/generate_storyboard_panels.py \
  --project <path> \
  --prompt-file 05-image-prompts/001-storyboard.md
# optional: --resolution 4K   (or meta storyboard_resolution)
```

Writes:

```text
assets/frames/{NNN}-frame-01.png … {NNN}-frame-0M.png   # exact cell aspect
assets/storyboard/{NNN}-board.png                         # stitched review sheet
assets/storyboard/{NNN}-board.panels.json
```

## Prompt rules

```text
TEXT ON IMAGE (MANDATORY):
- No visible text, letters, numbers, logos, watermarks, UI labels inside cells.
- Russian/brand copy will be DOM overlays later.
```

Shared style preamble (from journey) must be identical across panels.  
Panel generator appends: generate **only** panel N as a single `media_aspect_ratio` frame.

## Continuity (required)

See `shared/cinematic-transition-contract.md`.

- One continuous world / camera path
- Each panel further along the same flight
- Neighbor panels share a readable landmark
- Do not generate if journey lacks `## Transition plan`

## Outputs (versioned)

```text
assets/storyboard/001-board.png     # stitched review; never overwrite
assets/frames/001-frame-01.png …
05-image-prompts/001-storyboard.md
```

If `NNN-board.panels.json` exists, **do not** run `slice_storyboard.py` on that board.  
Active frame set: `manifest.json` → `frames.active_map`.
