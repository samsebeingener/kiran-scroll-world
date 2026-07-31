---
name: scroll-world-slicer
description: Confirm panel frames from generate_storyboard_panels; do not re-slice stitched boards with panels.json.
---

# Slicer

Контракт: `shared/storyboard-generation-contract.md`.

## Production

Если `assets/storyboard/{NNN}-board.panels.json` существует — кадры уже в `assets/frames/{NNN}-frame-*.png`.  
**Не** запускай `slice_storyboard.py` (gutters испортят aspect).

Проверь `manifest.json` → `frames.active_map` указывает на эти panel PNGs.

## Legacy only

`slice_storyboard.py` — только если board **без** `panels.json` и нужно аварийно нарезать; скрипт сам валится, если crop ≠ `media_aspect_ratio`. Предпочтительный ремонт: перегенерировать панели через `generate_storyboard_panels.py`.

Fragment: `fragments/slicer.md` + Errors & Fixes + `incident_report: none|…`.
