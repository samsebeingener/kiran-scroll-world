---
name: scroll-world-storyboard
description: One Kie gpt-image-2 board generation (grid of M panels at media_aspect_ratio, 2K/4K) + slice. Modes: text-to-image (default) / image-to-image (user references via Kie File Upload API).
model: inherit
readonly: false
is_background: false
---

# Storyboard agent

Следуй `skills/scroll-world-storyboard/SKILL.md` и `shared/storyboard-generation-contract.md`.

Генератор: **Kie** через `scripts/generate_storyboard_panels.py`, два режима:

- `gpt-image-2-text-to-image` — по умолчанию, без референсов пользователя.
- `gpt-image-2-image-to-image` — когда пользователь дал референс(ы) (`storyboard_references` в meta или `--reference`); локальные файлы сначала загружаются через Kie File Upload API.

Жёстко: **NO TEXT ON IMAGE** (текст — только DOM overlays позже); кадры board = `media_aspect_ratio` видео.

**Kie prompt:** в `05-image-prompts/{NNN}-storyboard.md` визуал только внутри ` ```text `; slug/M/grid/mode/workaround — снаружи. Скрипт вырезает fence; целый `.md` в API слать нельзя.

**После slice:** board AR gate + per-cell `aspect_close` + content gate (пустой/edge-cut кадр → hard fail до `active_map`).
