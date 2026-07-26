---
name: scroll-world-video
description: Cinematic Seedance legs; chain in code, visual-only Kie prompts.
---

# Video

Контракты: `shared/video-generation-contract.md`, **`shared/media-format-contract.md`**, **`shared/kie-prompt-contract.md`**, `shared/cinematic-transition-contract.md`, `shared/asset-versioning-contract.md`.
Шаблон Kie prompt: `templates/video-leg-prompt.template.md`.

## Kie видит только

`first_frame_url` + `last_frame_url` + текст из `05-image-prompts/*-leg-*.md`.

**Промпт = визуал между двумя PNG.** Без leg numbers, storyboard, MP4, «preserve previous leg», FRAME SOURCES. Цепочка кадров — в `kie_seedance_2_mini.py`, не в тексте.

## Цепочка (код, не prompt)

| Leg | `first_frame_url` | `last_frame_url` |
|-----|-------------------|------------------|
| 0 | storyboard KF1 | storyboard KF2 |
| i>0 | last frame MP4 leg i−1 | storyboard KFi+2 |

Генерировать **0 → 1 → …**. Re-gen leg k → перегенерить k+1…

## Journey → prompt

`video_prompt_seed` → развернуть в `05-image-prompts/*-leg-*.md` по **`templates/video-leg-prompt.template.md`**.

**Цель: 1 200–4 000 символов.** Секции: FIRST FRAME, LAST FRAME, timed CAMERA PATH, OBJECT TRANSFORMATION, MATERIAL & LIGHT. Скрипт отклоняет &lt; 800.

## Запуск

`aspect_ratio` берётся из `project.meta.json` → **`media_aspect_ratio`** (тот же, что у ячеек сториборда).

```bash
python scripts/kie_seedance_2_mini.py \
  --workspace <PROJECT_ROOT> \
  --project <PROJECT> --leg <N> \
  --prompt-file 05-image-prompts/001-leg-00.md \
  --resolution 480p --duration 4
```

Defaults if omitted: **480p**, duration **4** (allowed 4–8). `--dry-run` — без upload/createTask.

Fragment: `fragments/video.md`.
