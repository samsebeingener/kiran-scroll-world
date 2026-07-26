---
name: scroll-world-storyboard
description: Versioned storyboard panels via Kie gpt-image-2 at exact media_aspect_ratio (2K/4K).
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
2. Файл: `05-image-prompts/{NNN}-storyboard.md`
3. В промпте явно:
   - ONE CONTINUOUS WORLD / same flight path
   - **каждый panel = `media_aspect_ratio` keyframe** (не хардкодить 16:9)
   - continuity landmark между соседями
   - transition intent из Transition plan
4. **Только** Kie:

```bash
python scripts/generate_storyboard_panels.py \
  --project <PROJECT> \
  --prompt-file 05-image-prompts/{NNN}-storyboard.md
# --resolution 4K  если пользователь просил 4K
```

Скрипт пишет `assets/frames/{NNN}-frame-*.png` + stitched `assets/storyboard/{NNN}-board.png`.

## Self-check перед сдачей

- [ ] Панели читаются как один пролёт, не коллаж открыток
- [ ] Общий light/ground
- [ ] Между соседями видна преемственность сюжета/геометрии
- [ ] Aspect панелей = `media_aspect_ratio`

Fragment: `fragments/storyboard.md`.
