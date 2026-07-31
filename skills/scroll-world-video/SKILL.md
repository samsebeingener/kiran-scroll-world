---
name: scroll-world-video
description: Cinematic Seedance legs; chain in code, visual-only Kie prompts.
---

# Video

Контракты: `shared/video-generation-contract.md`, **`shared/media-format-contract.md`**, **`shared/kie-prompt-contract.md`**, `shared/cinematic-transition-contract.md`, `shared/asset-versioning-contract.md`.
Реестры (обязательно читать перед промптом): **`shared/camera-movement-registry.md`**, **`shared/object-transform-registry.md`**.
Шаблон Kie prompt: `templates/video-leg-prompt.template.md`.

## Kie видит только

`first_frame_url` + `last_frame_url` + текст из `05-image-prompts/*-leg-*.md`.

**Промпт = визуал между двумя PNG.** Без leg numbers, storyboard, MP4, «preserve previous leg», FRAME SOURCES. Цепочка кадров — в `kie_seedance_2_mini.py`, не в тексте.

## Plates (обязательно)

1. Перед каждым leg визуально прочитать start PNG + end PNG.
2. FIRST FRAME = то, что в **start PNG** (leg>0: last frame прошлого MP4, не текст journey).
3. LAST FRAME = то, что в **end PNG** (геометрия, ось акцента, силуэт).
4. Секция **VISUAL PLATE FIDELITY** в Kie prompt (см. template).

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
| `camera_moves` | ids → `shared/camera-movement-registry.md` → взять **`prompt_snippet`** для каждого id; в CAMERA PATH **primary первым**, затем secondary |
| `object_transform_code` | → `shared/object-transform-registry.md` → **`prompt_examples`**; если `duration_sec ≤ 5` — брать **`short_clip_variant`** (+ сжатые examples) |
| `duration_sec` | масштабировать timed beats; CLI `--duration` = это значение |
| `video_prompt_seed` | заметки; финальный prompt **после** live read PNG |

**Адаптация, не слепой paste:** snippets/examples подгонять под **реальные plates** (subject, силуэт, материалы из start/end PNG). Не вставлять чужой субъект из примера реестра.

Заполнить `templates/video-leg-prompt.template.md`:

- `{{CAMERA_MOVE_SNIPPETS}}` — склеенные EN snippets (primary → secondary)
- `{{TRANSFORM_MECHANIC}}` — механика из реестра, адаптированная к plates
- timed beats масштабировать под `{{DURATION}}` (= `duration_sec`)
- сохранить **VISUAL PLATE FIDELITY**

**Цель: 1 200–4 000 символов.** Секции: FIRST FRAME, LAST FRAME, **VISUAL PLATE FIDELITY**, CAMERA PATH (+ snippets), OBJECT TRANSFORM (+ mechanic), MATERIAL & LIGHT. Скрипт отклоняет &lt; 800.

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

`--dry-run` — без upload/createTask.

Fragment: `fragments/video.md`.
