# Scroll World — Kie video prompt contract

**Kie получает ровно:** `first_frame_url` + `last_frame_url` + строка `prompt`.

У модели **нет** памяти о прошлых задачах, индексах leg, MP4, путях storyboard или нашем пайплайне. Она только анимирует между **двумя загруженными PNG**.

## Разделение ответственности

| Слой | Кто | Содержание |
|------|-----|------------|
| **Какие картинки** | `video_frame_chain.py` + `kie_seedance_2_mini.py` | leg 0: storyboard `playback_chain[0]`→`[1]` (default KF1→KF2); leg i>0: ffmpeg last frame of leg i−1 → storyboard `playback_chain[i+1]` (default KFi+2) |
| **Что происходит между ними** | `05-image-prompts/*-leg-*.md` → Kie `prompt` | Только визуальный/кинематографический English |

Никогда не объясняй пайплайн внутри Kie prompt.

## NO TEXT ON IMAGE (MANDATORY)

Промпты **storyboard и video всегда** содержат блок NO TEXT: на генерируемых изображениях/видео запрещены **текст, буквы, цифры, логотипы, водяные знаки**. Русский/брендовый copy накладывается потом через DOM overlays (`assets/overlays.json`), никогда через генерацию. В режиме image-to-image референс задаёт стиль/композицию — текстовый промпт всё равно **обязателен** и тоже содержит блок NO TEXT.

## Length (Kie API)

| | Chars |
|---|------|
| API minimum | 3 |
| API maximum | 20 000 |
| **Script minimum** | **800** (hard reject) |
| **Recommended** | **1 200–4 000** (warn if &lt; 1 200) |

Короткие промпты недонаправляют модель. Используй `templates/video-leg-prompt.template.md` — CREATIVE DIRECTION, STAGES, structured plate locks, timed camera beats с end-state, LANDING CONTRACT, COUNT/EXCLUSIONS.

> Soft/hard validation длины и запрещённых фраз живёт в `scripts/kie_seedance_2_mini.py` (отдельный агент/скрипт). Этот контракт задаёт **содержание** prompt.

## Must-include в Kie prompt

Обязательные секции (порядок как в template):

1. **Anchor** — exact start/end + single continuous shot
2. **CREATIVE DIRECTION** — одно предложение: subject + event + camera idea
3. **STAGES** — STAGE A/B/C… состояния мира **до** timed beats
4. **FIRST FRAME** / **LAST FRAME** — описания plates
5. **VISUAL PLATE FIDELITY** — structured plate locks:
   - Start/End: `silhouette_axis`, `accent_color_position`, `ground_plane`, `horizon`, `materials`, `prop_count` (+ list)
   - `Delta vs start`
   - Не изобретать геометрию, которой нет ни на одном plate
6. **CAMERA PATH**:
   - Shot grammar: shot size start→end; primary / secondary move
   - Registry `prompt_snippet`s
   - Timed beats с observable end-state («by Xs: …»)
7. **LANDING CONTRACT** — settle 0.4–0.6s на last-frame composition; без late zoom/crop/silhouette после начала settle
8. **WORLD CONTINUITY** / **OBJECT TRANSFORM** / **MATERIAL & LIGHT** / **MOTION QUALITY**
9. **COUNT** / **EXCLUSIONS**
10. **FORBIDDEN** — no text/letters/numbers/logos/watermarks/captions/UI/subtitles/BGM cues/new objects not in plates

Также допустимо:

- World continuity **как видно на plates** (ground, light, landmarks)
- Anti-slideshow как **motion quality** (no dissolve-only, no crossfade wipe) — не как pipeline rules
- `{{CELL_ASPECT}}` только как composition language при необходимости

## Beat budget

| Duration | Beats |
|----------|-------|
| 4–6 s | 2–3 |
| 7–10 s | 3–4 |
| 11–15 s | 4–5 |

Каждый beat **обязан** заканчиваться observable end-state phrase (`by Xs: …`). Тайминги масштабировать к `duration_sec` leg.

## Forbidden в Kie prompt

### Tech dump (не класть в prose)

- `480p`, `720p`, имена API-полей (`resolution`, `generate_audio`, …) как настройки задачи
- Длительность как «API duration=N» — только кинематографический feel (`{{DURATION}}s feel` / beat times)

### Pipeline / meta (script rejects)

- `FRAME SOURCES`, `frame sources`
- `previous leg`, `next leg`, `leg 0`, `leg 1`, …
- `storyboard`, `storyboard slice`, `intermediate storyboard`
- `preserve rendered`, `rendered end`, `previous generation`, `previous video`
- `snap-back`, `snap back to storyboard`
- `momentum from previous`, `continue the velocity`, `continue momentum`
- `MP4`, `ffmpeg`, `extract`, `active_map`, `kie`, `seedance task`
- `@image1`, `@image2`

## Journey vs Kie prompt

`03-journey.md` → `video_prompt_seed` — **заметки для video-агента** (можно упоминать KF, legs, план continuity).

Video-агент **переписывает** это в `05-image-prompts/*-leg-*.md` с **только** визуальным языком перед `createTask`.

## Agent checklist before createTask

1. Prompt **≥ 800** chars (target **1 200–4 000**); все must-include секции заполнены конкретными visuals
2. Есть **CREATIVE DIRECTION**, **STAGES** (до timestamps), **LANDING CONTRACT**, **COUNT** / **EXCLUSIONS**
3. Plate locks заполнены **после live PNG read**; structured fields (silhouette / accent / ground / horizon / materials / prop_count) на start и end + delta
4. CAMERA PATH: shot grammar + registry snippets; число beats по beat budget; каждый beat с «by Xs: …» end-state
5. Описывает motion между **этими двумя PNG** — не то, как мы их выбрали
6. Нет filenames, leg numbers, storyboard references, resolution/API tech dump
7. Timed beats совпадают с `duration` (**4–15** s; обязателен per leg из journey — без default; сложные morphs часто 8–12)
8. Ending: LANDING settle **0.4–0.6s** на last-frame — без «next leg», без late zoom/crop после settle
