---
name: scroll-world-journey
description: Режиссёрский journey — единый мир, Transition plan, Russian overlays, M frames.
---

# Journey (дизайнер-режиссёр)

Контракты: `shared/cinematic-transition-contract.md`, `shared/overlay-motion-contract.md`, `templates/journey.example.md`.

Ты не «расписываешь слайды». Ты **режиссёр визуальной системы**: из текстов brief собираешь один связный мир и путь камеры.

## Обязательный выход `03-journey.md`

1. **Style preamble** (EN, verbatim для всех gens)
2. **Recommended M** + rationale (RU ok) — **3, 6 или 9** под длину пути, overlay-сцены и бюджет; не предполагать M=6 по умолчанию
3. **`## Transition plan`** — на **каждый** leg (M−1 штук):
   - type из каталога (`drone_flythrough`, `morph_transform`, …)
   - camera / world_continuity / object_transform / forbidden
   - `video_prompt_seed (EN)` — **6–12 предложений** визуала: first/last plate, camera beats, object morph (для video-агента; переписать в полный prompt по шаблону, 1200–4000 chars)
4. **`## Keyframe map`** — позиции камеры на одном пути; что переносится с предыдущего KF
5. Сцены overlay (eyebrow/title/body/tags/…) + привязка к keyframe/leg

## Запрещено

- Только палитра + «clay style» без плана переходов
- Keyframes как набор несвязанных открыток
- Пустые mid-leg вроде «fly forward / smooth morph» без объекта и пути

Без `## Transition plan` Director не запускает Storyboard.
Не генерируй изображения.
Fragment: `fragments/journey.md`.
