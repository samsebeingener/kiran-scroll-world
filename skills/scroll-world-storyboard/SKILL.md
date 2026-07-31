---
name: scroll-world-storyboard
description: One Kie gpt-image-2 board generation (grid of M panels) + local slice at media_aspect_ratio (2K/4K). Two modes: text-to-image (default) / image-to-image (user references).
---

# Storyboard

Контракты: `shared/storyboard-generation-contract.md`, `shared/cinematic-transition-contract.md`, `shared/asset-versioning-contract.md`.
Шаблон: `templates/storyboard-prompt.template.md`.

**NO TEXT ON IMAGE (MANDATORY):** никакого текста/букв/цифр/логотипов/водяных знаков на board и кадрах. Текст — только DOM overlays позже.

## Перед генерацией

Прочитай `project.meta.json` → **`media_aspect_ratio`** (обязательно; контракт `shared/media-format-contract.md`; кадры board = формат видео, mismatch запрещён).
Опционально `storyboard_resolution` (`2K` default / `4K` по запросу пользователя).
Прочитай `03-journey.md` → **Transition plan** + **Keyframe map**. Если секций нет — STOP, верни Director.

Нужен `KIE_API_KEY`.

## Два режима backend

- **text-to-image** (`gpt-image-2-text-to-image`) — по умолчанию, когда у пользователя нет референсов (`storyboard_references` пусто/отсутствует, `--reference` не передан).
- **image-to-image** (`gpt-image-2-image-to-image`) — когда пользователь дал референс(ы). Скрипт сам загружает локальные файлы через Kie File Upload API (`scripts/kie_file_upload.py`) → HTTPS `fileUrl` → image input в запросе. Текстовый промпт **всё равно обязателен** (референс задаёт стиль/композицию, промпт — сцену); блок NO TEXT остаётся.

## Промпт + генерация

1. Следующий `{NNN}` через `asset_versions.py next … *-board.png`
2. Файл: `05-image-prompts/{NNN}-storyboard.md` — заполни `templates/storyboard-prompt.template.md`:
   - {{M}}, {{COLS}}×{{ROWS}} grid, {{CELL_ASPECT}} = `media_aspect_ratio` (не хардкодить 16:9)
   - ONE CONTINUOUS WORLD / same flight path через весь board
   - beat / camera / continuity landmark / from-prev для каждой панели
   - transition intent из Transition plan
   - блок **MANDATORY NO TEXT ON IMAGE** — не удалять
3. **Только** Kie, ОДИН запрос:

```bash
python scripts/generate_storyboard_panels.py \
  --project <PROJECT> \
  --prompt-file 05-image-prompts/{NNN}-storyboard.md
# --resolution 4K  если пользователь просил 4K
# --reference ref.png (повторяемый) — если meta storyboard_references не задан
```

Скрипт генерирует **один** `assets/storyboard/{NNN}-board.png` и сразу нарезает его в `assets/frames/{NNN}-frame-*.png` (hard aspect gate: каждый кадр = `media_aspect_ratio`, иначе SystemExit — ремонт новой генерацией board).

## Self-check перед сдачей

- [ ] Панели board читаются как один пролёт, не коллаж открыток
- [ ] Общий light/ground
- [ ] Между соседями видна преемственность сюжета/геометрии
- [ ] Aspect нарезанных кадров = `media_aspect_ratio`
- [ ] На board/кадрах **нет** текста/букв/цифр/логотипов (иначе регенерация board, новый NNN)

Fragment: `fragments/storyboard.md`.
