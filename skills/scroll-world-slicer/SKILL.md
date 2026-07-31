---
name: scroll-world-slicer
description: Confirm frames sliced from the one-generation board; repair-slice only when needed.
---

# Slicer

Контракты: `shared/storyboard-generation-contract.md`, `shared/asset-versioning-contract.md`.

## Production

Кадры `assets/frames/{NNN}-frame-*.png` создаются автоматически: `generate_storyboard_panels.py` генерирует **один** board и сразу вызывает `slice_storyboard.py`.

Проверь `assets/manifest.json` → `frames.active_map`: все M кадров присутствуют, пути существуют, версия NNN совпадает с активным board.

## Repair only

Повторный запуск `slice_storyboard.py` — только для ремонта (другой `--gutter`, `--only-cells`). Скрипт сам валится (`SystemExit`), если crop ≠ `media_aspect_ratio` — это hard aspect gate. Ремонт mismatch: новая генерация board через `generate_storyboard_panels.py` с более подходящим grid/aspect.

Fragment: `fragments/slicer.md` + Errors & Fixes + `incident_report: none|…`.
