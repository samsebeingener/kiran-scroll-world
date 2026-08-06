---
name: scroll-world-video
description: Generate sequential video legs with bytedance/seedance-2-mini using first_frame_url + last_frame_url.
model: inherit
readonly: false
is_background: false
---

Следуй `skills/scroll-world-video/SKILL.md`, `shared/video-generation-contract.md`, **`shared/media-format-contract.md`**, **`shared/kie-prompt-contract.md`**.
Промпт: заполнять по **P0–P2 порядку** из skill (live PNG → structured plate locks → STAGES → CREATIVE DIRECTION → shot grammar → timed beats с `by Xs:` → beat budget → LANDING CONTRACT → COUNT & EXCLUSIONS).
Реестры: `prompt_snippet` / `prompt_examples` из `shared/camera-movement-registry.md` + `shared/object-transform-registry.md` (1 primary + ≤1 secondary; `--duration` = per-leg `duration_sec`).
Шаблон: `templates/video-leg-prompt.template.md`; пример: `templates/examples/video-leg-prompt.filled.md`.
Legs = K−1 по `playback_chain`. Модель только `bytedance/seedance-2-mini`. Промпт для Kie — **только визуал** между двумя PNG. Цепочка кадров — в `kie_seedance_2_mini.py`, не в тексте. Без 480p/720p/@image/pipeline meta в Kie-тексте.
