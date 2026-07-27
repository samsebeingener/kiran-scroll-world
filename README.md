# Kiran Scroll World

![Kiran Scroll World — scroll-scrub fly-through](docs/assets/github-cover.png)

**Kiran Scroll World** — project-local [Cursor](https://cursor.com) plugin для **scroll-scrubbed fly-through** лендинга: пока гость скроллит, камера летит сквозь единый мини-мир бренда без склеек «из ниоткуда».

> Один мир. M ключевых кадров. M−1 кинематографичных перехода. Русский текст — поверх видео, не в генерации.

## Возможности

- **Сессионный intake** — `/scroll-world-start`: тема мира, бренд, стиль, формат кадра (`media_aspect_ratio`), куда встроить блок
- **Journey + Transition plan** — единый мир, типы переходов между кадрами, русские overlay-тексты
- **Storyboard** — **M ∈ {3, 6, 9}** (выбор на Journey под задачу) панелей через Kie `gpt-image-2-text-to-image` @ **2K** / **4K**; каждая панель = точный `media_aspect_ratio` (не aspect сшитого board)
- **Video legs** — Kie `bytedance/seedance-2-mini` (`first_frame_url` + `last_frame_url`), default **480p**, duration **4** (диапазон 4–8)
- **DOM overlays** — русский copy в `assets/overlays.json` (можно править без регенерации медиа)
- **scrub-engine.js** — portable scroll-scrub (upstream [oso95/scroll-world](https://github.com/oso95/scroll-world), MIT)
- **Fixic** — post-run исправления по `pipeline-fix-queue.md`

Image + video generation: **Kie only** (`gpt-image-2-text-to-image` production; `gpt-image-2-image-to-image` — repair).

## Быстрый старт

### 1. Установка

```powershell
git clone https://github.com/samsebeingener/kiran-scroll-world.git
cd kiran-scroll-world
pip install -e ".[dev]"
copy .env.example .env   # KIE_API_KEY
.\scripts\sync-to-cursor.ps1
```

Требуется **ffmpeg** / **ffprobe** в PATH.

### 2. Открыть в Cursor

Откройте папку `kiran-scroll-world` как workspace — подхватятся agents, commands, skills, rules.

**Reload Window**, затем:

```
/scroll-world-start
```

### 3. Память проекта

```text
<PROJECT_ROOT>/projects/scroll-world/<YYYY-MM-DD-slug>/
```

Продакшн-прогоны и медиа **не коммитятся** (см. `.gitignore`).

## Команды Cursor

| Команда | Назначение |
|---------|------------|
| `/scroll-world-start` | Новый проект, intake, journey, gates, полный пайплайн |
| `/scroll-world-run` | Продолжить по `project.meta.json` |

## Архитектура

```text
/scroll-world-start (Director)
  → Intake (media_aspect_ratio, brand)
  → Journey (+ Transition plan)
  → [Gate Budget]
  → Storyboard (Kie gpt-image-2 panels)
  → [Gate Storyboard]
  → [Gate Video Settings]
  → Video legs (Seedance 2 Mini, chain 0→1→…)
  → Encode → Builder (overlays + scrub-engine)
  → QA → [Fixic]
```

Видео-отрезков = **M − 1** (M кадров).

Контракты: `shared/media-format-contract.md`, `shared/video-generation-contract.md`, `shared/storyboard-generation-contract.md`.

## Приватность

- Исходные тексты, промпты и медиа сессий **не коммитятся**
- `KIE_API_KEY` только в локальном `.env`
- Не отправляйте чужие персональные данные в Kie без согласия

## Разработка

```powershell
python -m pytest -q
python scripts/validate_install.py
```

## Лицензия

MIT — см. [LICENSE](LICENSE). Upstream scrub-engine: MIT (oso95/scroll-world).

## Автор

Проект разработал [Никита Куликов](https://samsebeingener.ru/).

---

**GitHub About (краткое описание):**

> Cursor plugin: scroll-scrub fly-through — Kie gpt-image-2 storyboard panels + Seedance 2 Mini video legs + DOM overlays. By Nikita Kulikov.
