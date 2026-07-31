---
name: scroll-world-video
description: Generate sequential video legs with bytedance/seedance-2-mini using first_frame_url + last_frame_url.
model: inherit
readonly: false
is_background: false
---

Следуй `skills/scroll-world-video/SKILL.md`, `shared/video-generation-contract.md`, **`shared/media-format-contract.md`**. Промпт: `prompt_snippet` / `prompt_examples` из `shared/camera-movement-registry.md` + `shared/object-transform-registry.md`; `--duration` = per-leg `duration_sec`; legs = K−1 по `playback_chain`.
Модель только `bytedance/seedance-2-mini`. Промпт для Kie — **только визуал** между двумя PNG (`shared/kie-prompt-contract.md`). Цепочка кадров — в скрипте, не в тексте.
