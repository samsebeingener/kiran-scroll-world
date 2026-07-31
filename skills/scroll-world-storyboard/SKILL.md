---
name: scroll-world-storyboard
description: One Kie gpt-image-2 board generation (grid of M panels) + local slice at media_aspect_ratio (2K/4K).
---

# Storyboard

Контракты: `shared/storyboard-generation-contract.md`, `shared/cinematic-transition-contract.md`, `shared/asset-versioning-contract.md`.
Шаблон: `templates/storyboard-prompt.template.md`.

## Перед генерацией

Прочитай `project.meta.json` → **`media_aspect_ratio`** (обязательно; контракт `shared/media-format-contract.md`).
Опционально `storyboard_resolution` (`2K` default / `4K` по запросу пользователя).
Прочитай `03-journey.md` → **Transition plan** + **Keyframe map**. Если секций нет — STOP, верни Director.

Нужен `KIE_API_KEY`.

## Промпт + генерация

1. Следующий `{NNN}` через `asset_versions.py next … *-board.png`
2. Файл: `05-image-prompts/{NNN}-storyboard.md` — заполни `templates/storyboard-prompt.template.md`:
   - {{M}}, {{COLS}}×{{ROWS}} grid, {{CELL_ASPECT}} = `media_aspect_ratio` (не хардкодить 16:9)
   - ONE CONTINUOUS WORLD / same flight path через весь board
   - beat / camera / continuity landmark / from-prev для каждой панели
   - transition intent из Transition plan
3. **Только** Kie, ОДИН запрос:

```bash
python scripts/generate_storyboard_panels.py \
  --project <PROJECT> \
  --prompt-file 05-image-prompts/{NNN}-storyboard.md
# --resolution 4K  если пользователь просил 4K
```

Скрипт генерирует **один** `assets/storyboard/{NNN}-board.png` и сразу нарезает его в `assets/frames/{NNN}-frame-*.png` (hard aspect gate: каждый кадр = `media_aspect_ratio`, иначе SystemExit — ремонт новой генерацией board).

## Self-check перед сдачей

- [ ] Панели board читаются как один пролёт, не коллаж открыток
- [ ] Общий light/ground
- [ ] Между соседями видна преемственность сюжета/геометрии
- [ ] Aspect нарезанных кадров = `media_aspect_ratio`

Fragment: `fragments/storyboard.md`.
