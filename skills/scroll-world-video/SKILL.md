---
name: scroll-world-video
description: Cinematic Seedance legs; chain in code, visual-only Kie prompts.
---

# Video

Контракты: `shared/video-generation-contract.md`, **`shared/media-format-contract.md`**, **`shared/kie-prompt-contract.md`**, `shared/cinematic-transition-contract.md`, `shared/asset-versioning-contract.md`.
Реестры (обязательно читать перед промптом): **`shared/camera-movement-registry.md`**, **`shared/object-transform-registry.md`**.
Шаблон Kie prompt: `templates/video-leg-prompt.template.md`.
Filled example (P0–P2): `templates/examples/video-leg-prompt.filled.md`.

## Kie видит только

`first_frame_url` + `last_frame_url` + текст из `05-image-prompts/*-leg-*.md`.

**Промпт = визуал между двумя PNG.** Без leg numbers, storyboard, MP4, «preserve previous leg», FRAME SOURCES. Цепочка кадров — в `kie_seedance_2_mini.py`, не в тексте.

## P0–P2: обязательный порядок заполнения

Перед `createTask` заполнять Kie-промпт **строго в этом порядке** (шаблон → `05-image-prompts/{NNN}-leg-{LL}.md`):

1. **Live read** start PNG + end PNG (пиксели, не текст journey).
2. **Structured plate locks** из пикселей (`silhouette_axis`, `accent_color_position`, `ground_plane`, `horizon`, `materials`, `prop_count` + list) — **не** пересказ Transition plan.
3. **STAGES** (A / B / C…) — состояния сцены до timed beats.
4. **CREATIVE DIRECTION** — одно предложение: subject + event + camera idea.
5. **Shot grammar:** shot size (`CU` / `MCU` / `MS` / `WS` / …) + **1 primary** move + **≤1** secondary из `shared/camera-movement-registry.md` (`prompt_snippet`; primary первым).
6. **Timed beats** масштабировать под `duration_sec`; у **каждого** beat — observable end-state: `by Xs: …`.
7. **Beat budget** (камера; object-transform beats — те же потолки или ниже):

| `duration_sec` | Camera beats | Object-transform beats |
|----------------|--------------|------------------------|
| 4–6 | 2–3 | ≤ 2–3 |
| 7–10 | 3–4 | ≤ 3–4 |
| 11–15 | 4–5 | ≤ 4–5 |

   При `duration_sec ≤ 5` — `short_clip_variant` из object-transform registry + сжатый budget.
8. **LANDING CONTRACT** — settle **0.4–0.6s** на end plate; без late zoom / crop / silhouette change после settle.
9. **COUNT & EXCLUSIONS** — явный счёт props + запреты (субтитры, лишние объекты, BGM-текст и т.п.).
10. **Не в Kie-тексте:** `480p` / `720p` / API SETTINGS, `@image1` / `@image2`, pipeline meta (leg N, MP4, storyboard filenames).

## Plates (обязательно)

1. Перед каждым leg визуально прочитать start PNG + end PNG.
2. FIRST FRAME = то, что в **start PNG** (leg>0: last frame прошлого MP4, не текст journey).
3. LAST FRAME = то, что в **end PNG** (геометрия, ось акцента, силуэт).
4. Секции **VISUAL PLATE FIDELITY** (structured locks) + **STAGES** + **LANDING CONTRACT** + **COUNT & EXCLUSIONS** в Kie prompt (см. template + filled example).

## Playback chain (сколько legs)

- Legs только по **`playback_chain`**: число клипов = **K − 1** (не `M − 1`, если `K < M`).
- `reserve` панели не генерятся как Seedance legs в текущем прогоне.
- Meta: `playback_chain` / `reserve` в `project.meta.json` (fallback без chain = классическая цепочка 1…M).

## Цепочка (код, не prompt)

| Leg | `first_frame_url` | `last_frame_url` |
|-----|-------------------|------------------|
| 0 | storyboard KF `playback_chain[0]` (обычно 1) | storyboard KF `playback_chain[1]` |
| i>0 | last frame MP4 leg i−1 | storyboard KF `playback_chain[i+1]` |

Без `playback_chain`: как раньше — KF1→KF2, затем last(MP4)→KFi+2.

Генерировать **0 → 1 → …** до `K−2`. Re-gen leg k → перегенерить k+1…

## Journey → prompt (реестры)

Для **каждого** leg из Transition plan (`03-journey.md`) прочитать:

| Поле journey | Действие Video |
|--------------|----------------|
| `camera_moves` | ids → `shared/camera-movement-registry.md` → взять **`prompt_snippet`**; shot grammar: **1 primary** + **≤1** secondary; в CAMERA PATH **primary первым** |
| `object_transform_code` | → `shared/object-transform-registry.md` → **`prompt_examples`**; если `duration_sec ≤ 5` — брать **`short_clip_variant`** (+ сжатые examples) |
| `duration_sec` | масштабировать timed beats + соблюсти **beat budget**; CLI `--duration` = это значение |
| `video_prompt_seed` | заметки; финальный prompt **после** live read PNG и plate locks |

**Адаптация, не слепой paste:** snippets/examples подгонять под **реальные plates** (subject, силуэт, материалы из start/end PNG). Не вставлять чужой субъект из примера реестра.

Заполнить `templates/video-leg-prompt.template.md` (ориентир: `templates/examples/video-leg-prompt.filled.md`):

- `{{CAMERA_MOVE_SNIPPETS}}` — склеенные EN snippets (primary → optional secondary)
- `{{TRANSFORM_MECHANIC}}` — механика из реестра, адаптированная к plates
- timed beats масштабировать под `{{DURATION}}` (= `duration_sec`) с `by Xs:` end-states
- сохранить **VISUAL PLATE FIDELITY**, **STAGES**, **LANDING CONTRACT**, **COUNT & EXCLUSIONS**, **CREATIVE DIRECTION**

**Цель: 1 200–4 000 символов.** Секции: FIRST/LAST FRAME, plate locks, CREATIVE DIRECTION, STAGES, CAMERA PATH (+ shot grammar + snippets), OBJECT TRANSFORM, LANDING CONTRACT, COUNT & EXCLUSIONS, MATERIAL & LIGHT. Скрипт отклоняет &lt; 800.

## Запуск

`aspect_ratio` берётся из `project.meta.json` → **`media_aspect_ratio`**.

`--duration` = **`duration_sec` этой ноги** из Transition plan (fallback: `video_durations[leg]` или `video_duration` в meta; если нигде не задан — ошибка конфигурации, дефолта нет). Диапазон продукта **4–15**.

```bash
python scripts/kie_seedance_2_mini.py \
  --workspace <PROJECT_ROOT> \
  --project <PROJECT> --leg <N> \
  --prompt-file 05-image-prompts/001-leg-00.md \
  --resolution 480p --duration <duration_sec>
```

`--dry-run` — без upload/createTask. Resolution / duration — **только CLI**, не в тексте промпта.

Fragment: `fragments/video.md`.
