# Scroll World — кинематографические переходы

## Проблема, которую закрываем

Запрещён «слайдшоу»: два кадра + промпт «smooth transition / fly forward» → модель делает **плавную смену картинок без режиссуры**.

Нужна режиссёрская работа: **один непрерывный мир**, понятный путь камеры и явная трансформация объектов между keyframes.

## Связанные реестры

| Файл | Роль |
|------|------|
| `shared/camera-movement-registry.md` | Конкретные ходы камеры (`id` / `name_ru` / `for_journey`). Journey пишет **ids** в `camera_moves`; **не** копирует `prompt_snippet` (это Video). |
| `shared/object-transform-registry.md` | Механики смены объекта (`object_transform_code`). Timing **мягкий**: `comfort_sec` / `warn_below_sec` — рекомендация; **4s не хард-блок**. |

Жанровый `type` из каталога ниже ≠ код камеры из camera registry ≠ object mechanic. На leg сочетают все три слоя.

## Роли

| Кто | Что делает |
|-----|------------|
| **Journey (дизайнер-режиссёр)** | Единый мир + **Board & playback** (M/K) + **план переходов** только для текущей цепи (K−1 legs) + plain-RU pitch |
| **Storyboard** | Рисует contact sheet как **позиции одной камеры** в одном мире (не набор несвязанных открыток с общей палитрой) |
| **Video** | Пишет **богатый** English prompt по плану перехода; mid-leg move обязателен и конкретен; вставляет `prompt_snippet` камеры |

Director **не** пропускает Storyboard/Video, если в `03-journey.md` нет секций `## Board & playback` и `## Transition plan`.

## Каталог типов перехода (выбрать 1 на leg)

Код типа пишется в journey и копируется в video prompt.

| Code | Русское имя | Когда | Камера / действие |
|------|-------------|-------|-------------------|
| `drone_flythrough` | Пролёт дрона | Связать два острова одной местности | Плавный aerial glide вперёд/по диагонали над непрерывным ground plane; горизонт и земля не «прыгают» |
| `push_in_reveal` | Приближение с раскрытием | Войти внутрь структуры | Dolly/push-in к объекту; стены/крыша раскрываются или камера проходит в проём |
| `morph_transform` | Трансформация объектов | Сменить метафору при той же локации | Камера почти стабильна или медленный drift; объекты **перестраиваются** (маски→клоны, хаос→шестерни), не просто dissolve картинки |
| `lateral_track` | Боковой трек | Процесс / конвейер / путь | Steadicam parallel track; параллакс переднего плана |
| `orbit_continue` | Полуорбита → вперёд | Герой-объект в центре акта | Slow half-orbit, затем settle в forward drift к следующей зоне |
| `crane_bridge` | Подъём и мост | Связать два уровня | Crane-up, короткий air bridge, descent к следующей зоне (не «rewind» назад в ту же точку) |
| `portal_dive` | Нырок в портал | Смена масштаба/интерьера | Dive through arch/tunnel/hatch; interior of end-frame already hinted in start |
| `macro_micro` | Смена масштаба | Деталь ↔ система | Continuous zoom/scale shift along same axis; shared material language |
| `assembly_build` | Сборка | К финальному ядру/продукту | Части влетают/стыкуются в структуру end-frame под спокойной камерой |
| `erosion_melt` | Эрозия / расплав | Негативный акт (копирование, безликость) | Формы start тают/стираются в формы end; камера медленный push или drift |

Можно комбинировать **primary + secondary** (например `drone_flythrough` + лёгкий `morph_transform` на props).

## Board & playback (перед Transition plan)

В `03-journey.md` → `## Board & playback`:

- **M** ∈ {3, 6, 9} — размер доски (все панели storyboard)
- **K** ≤ M — длина текущей playback-цепочки; **K = legs_now + 1**
- **playback_chain** = PREFIX panels `[1..K]`
- **reserve** = TAIL panels `[K+1..M]`
- **legs_now** = K − 1 (видео сейчас; **не** всегда M − 1)

`## Transition plan` покрывает **только** legs текущей цепи (K−1), не reserve.

## Обязательные поля на каждый leg

В `03-journey.md` → `## Transition plan` (только playback legs):

```markdown
### Leg 0 — KF1 → KF2
- **type:** drone_flythrough + morph_transform
- **duration_sec:** 8
- **camera_moves:** [helicopter_style_aerial, pan_right, slow_zoom_in]
- **object_transform_code:** plastic_morph
- **camera:** …
- **world_continuity:** что общего в пространстве (земля, ось, landmark)
- **object_transform:** что именно превращается во что
- **forbidden:** simple crossfade / hard cut / random teleport
- **video_prompt_seed (EN):** 6–12 sentences; beats match duration_sec
```

- `camera_moves`: 1–3 **id** из camera-movement-registry (`for_journey` only в journey).
- `object_transform_code`: code из object-transform-registry; при коротком `duration_sec` адаптируй по `on_short_clip`, не блокируй 4s.

## Правила единого мира (storyboard)

1. Все keyframes — **одна diorama-территория** или явный непрерывный путь по ней.
2. Общий ground plane / horizon language / light (уже в style preamble).
3. В каждом следующем кадре должен читаться **остаток предыдущего** (landmark, ось пути, материал).
4. Запрещено: шесть несвязанных «открыток», связанных только палитрой и стилем глины.
5. В storyboard prompt явно: «continuous camera path; panel N is further along the same flight than panel N-1».

## Правила video prompt (только то, что видит Kie)

Контракт: `shared/kie-prompt-contract.md`. Kie получает **два PNG + текст**. Не объясняй пайплайн в prompt.

Промпт **обязан** (см. `templates/video-leg-prompt.template.md`, **1 200–4 000** chars):

1. **Anchor** — exact start/end + single continuous shot
2. **CREATIVE DIRECTION** — одно предложение (subject + event + camera idea)
3. **STAGES** — STAGE A/B/C… состояния мира **до** timed beats
4. **FIRST FRAME** / **LAST FRAME** — что видно на каждом plate (props, layout, materials)
5. **VISUAL PLATE FIDELITY** — structured plate locks (silhouette / accent / ground / horizon / materials / prop_count) на start и end + delta; только после live PNG read
6. **CAMERA PATH** — shot grammar (size start→end; primary/secondary) + registry snippets + timed beats; каждый beat с observable end-state («by Xs: …»)
7. **LANDING CONTRACT** — settle **≥ 0.4 s** (обычно 0.4–0.6s) на last-frame composition; без late zoom/crop/silhouette после начала settle
8. **OBJECT TRANSFORM** — по элементам, что во что превращается
9. WORLD CONTINUITY + MATERIAL & LIGHT + MOTION QUALITY (anti-slideshow)
10. **COUNT** / **EXCLUSIONS** + **FORBIDDEN** (no text / logos / new objects not in plates)

Named transition type(s) из каталога выше входят в creative direction / stages / object transform — не отдельный tech-dump.

**Запрещено в тексте для Kie:** leg numbers, storyboard, MP4, «preserve rendered end», «continue momentum from previous leg», FRAME SOURCES, snap-back к storyboard, dump `480p`/`720p`/API settings. Это делает код через `first_frame_url` / `last_frame_url` и createTask JSON.

`video_prompt_seed` в journey — заметки агенту; перед createTask переписать в чистый визуальный prompt.

Запрещённые единственные mid-leg фразы: `smooth transition`, `gently morph`, `fade into`, `fly forward` без деталей.

## QA

QA валит leg, если motion выглядит как crossfade двух stills без камеры/трансформации объектов → BLOCKER + INC (prompt/journey transition plan).
