---
name: scroll-world-slicer
description: Confirm sliced frames in active_map after the one-board generation; run slice only for repair.
model: inherit
readonly: false
is_background: false
---

Следуй `skills/scroll-world-slicer/SKILL.md`.

Кадры нарезаются из board автоматически внутри `generate_storyboard_panels.py`; подтверди `active_map`. Повторный `slice_storyboard.py` — только для repair (другой gutter / only-cells).
