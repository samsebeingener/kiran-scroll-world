---
name: scroll-world-slicer
description: Confirm Kie panel frames in active_map; do not re-slice boards with panels.json.
model: inherit
readonly: false
is_background: false
---

Следуй `skills/scroll-world-slicer/SKILL.md`.

Если есть `assets/storyboard/{NNN}-board.panels.json` — кадры уже от `generate_storyboard_panels.py`; подтверди `active_map`, не запускай slice.
