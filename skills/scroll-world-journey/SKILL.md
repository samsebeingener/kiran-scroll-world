---
name: scroll-world-journey
description: Режиссёрский journey — единый мир, Transition plan, Russian overlays, M frames.
---

# Journey (дизайнер-режиссёр)

Контракты: `shared/cinematic-transition-contract.md`, `shared/overlay-motion-contract.md`, `shared/camera-movement-registry.md`, `shared/object-transform-registry.md`, `shared/media-format-contract.md`, `templates/journey.example.md`, `templates/journey-pitch.example.md`.

Ты не «расписываешь слайды». Ты **режиссёр визуальной системы**: из текстов brief собираешь один связный мир и путь камеры.

## Обязательное чтение реестров (до написания journey)

1. **`shared/camera-movement-registry.md`**
   - Бери только: `id`, `name_ru`, `for_journey`.
   - **Никогда** не вставляй `prompt_snippet` в `03-journey.md` / pitch — сниппеты только для Video.
   - На leg: 1–3 id в `camera_moves` (1 primary + до 2 secondary).

2. **`shared/object-transform-registry.md`**
   - Бери: `code`, `name_ru`, `for_journey`, `when`, `comfort_sec`, `warn_below_sec`, `on_short_clip`.
   - Timing **мягкий**: `comfort_sec` — ориентир, **не** хард-блок. **4s всегда допустимы**; при коротком клипе адаптируй механику (`on_short_clip`), не отказывай.

## Эвристика M / K (до раскадровки)

1. Оцени путь: сколько **ног** (video legs) и типичный `duration_sec` на ногу.
2. **K = legs + 1** (число keyframes в **текущей** playback-цепочке).
3. **M** = наименьшее из `{3, 6, 9}` такое, что **M ≥ K**.
4. **Запрещено** M ∉ `{3, 6, 9}`.
5. Тяжёлая identity / пластика → предпочитай **меньше длинных ног** (пример: K=4, M=6, duration 8–10s).
6. Лёгкий travel / пролёт → можно **больше коротких ног**.
7. Панели **[1..K]** = playback chain; **[K+1..M]** = reserve (продолжение позже, без видео сейчас).

## Обязательный выход `03-journey.md`

1. **Style preamble** (EN, verbatim для всех gens)
2. **`## Board & playback`**
   - `M` — размер доски ∈ {3, 6, 9}
   - `K` — длина текущей playback-цепочки (K ≤ M)
   - `playback_chain` = PREFIX panels `[1..K]`
   - `reserve` = TAIL panels `[K+1..M]`
   - `legs_now` = K − 1 (видео сейчас; не всегда M − 1)
3. **`## Transition plan`** — **только** для текущей цепи: **K − 1** legs (не для reserve). На каждый leg:
   - `type` — из каталога cinematic (`drone_flythrough`, `morph_transform`, …)
   - `duration_sec`
   - `camera_moves` — 1–3 **id** из camera-movement-registry (без prompt_snippet)
   - `object_transform_code` — code из object-transform-registry
   - `camera` / `world_continuity` / `object_transform` / `forbidden` — prose
   - `video_prompt_seed (EN)` — 6–12 предложений; биты по секундам **совпадают** с `duration_sec`
4. **`## Keyframe map`** — **все M** панелей; у каждой `role`: `playback` | `reserve`
5. Сцены overlay (eyebrow/title/body/tags/…) + привязка к keyframe/leg (только playback)

## Также: `04-journey-pitch.md` (ДО storyboard)

Пиши **простым русским** для approve пользователя **до** Gate Pitch / Storyboard.

**Запрещено в pitch:** коды реестров, аббревиатуры (M/K/KF/leg/API), markdown-символы вроде `##` `[]` `→`, slug моделей, имена файлов.

**Содержание (проза):**
- мир и настроение;
- как движется глаз / камера по сегментам;
- что меняется с объектами в каждом сегменте;
- сколько картинок на раскадровке **сейчас**, сколько **видео сейчас**, сколько кадров **в запасе** на продолжение;
- примерно сколько секунд каждый клип — **человеческими словами**;
- одна строка оценки объёма работы.

См. `templates/journey-pitch.example.md`.

## Запрещено

- Только палитра + «clay style» без плана переходов
- Keyframes как набор несвязанных открыток
- Пустые mid-leg вроде «fly forward / smooth morph» без объекта и пути
- Вставка `prompt_snippet` камеры в journey
- Хард-блок длительности 4s из-за `comfort_sec`
- Transition plan на reserve-панели «на будущее» как будто они в текущей генерации

Без `## Transition plan` и `## Board & playback` Director не запускает Storyboard.  
Без `04-journey-pitch.md` — не просить approve раскадровки.  
Не генерируй изображения.  
Fragment: `fragments/journey.md`.
