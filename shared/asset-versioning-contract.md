# Scroll World — версионирование ассетов

## Закон

Старые варианты **никогда не удаляются**. Каждый новый генерат получает следующий числовой префикс `001`, `002`, `003`…

## Имена файлов

| Тип | Паттерн | Пример |
|-----|---------|--------|
| Раскадровка (board) | `assets/storyboard/{NNN}-board.png` | `001-board.png`, `002-board.png` |
| Промпт board | `05-image-prompts/{NNN}-storyboard.md` | `001-storyboard.md` |
| Промпт video leg | `05-image-prompts/{NNN}-leg-{LL}.md` | `002-leg-01.md` (тот же `NNN`, что у активного `*-leg-*.mp4`) |
| Кадры после slice | `assets/frames/{NNN}-frame-{II}.png` | `001-frame-01.png` (`NNN` = версия **исходного board**) |
| Last frame leg (chain) | `assets/frames/{NNN}-leg-{LL}-last.png` | `001-leg-00-last.png` → start leg 1 |
| Видео leg | `assets/video/legs/{NNN}-leg-{LL}.mp4` | `001-leg-00.mp4`, `002-leg-00.mp4` |
| Лог video | `assets/video/legs/{NNN}-leg-{LL}.json` | |
| Encode | `assets/encoded/{NNN}-leg-{LL}.mp4` | |

`NNN` и `II`/`LL` — zero-padded (`001`, `01`, `00`).

## Поведение

1. **Первый** storyboard → `001-board.png` (не `board.png`).
2. Пользователь просит пересоздать → оставить `001-*`, создать `002-board.png` (+ новый промпт `002-storyboard.md` при изменении).
3. То же для video legs: re-gen leg 0 → `002-leg-00.mp4`, старый `001-leg-00.mp4` остаётся.
4. **Микс кадров:** часть keyframes может браться из разных версий board по указанию пользователя. Активная карта — в `assets/manifest.json` → `frames.active_map`.

### Пример микса

```json
"frames": {
  "active_map": {
    "1": "assets/frames/001-frame-01.png",
    "2": "assets/frames/001-frame-02.png",
    "3": "assets/frames/002-frame-03.png",
    "4": "assets/frames/002-frame-04.png"
  }
}
```

Video leg `i>0` **start** = last frame of active leg `i−1` MP4 (not storyboard frame `i+1`). **End** = storyboard `active_map[str(playback_chain[i+1])]` (default continuous: `i+2`).

### playback_chain / reserve

`project.meta.json` may set a **prefix** of board indices for video:

- `playback_chain`: must be contiguous `[1, 2, …, K]` with no gaps (K ≤ M). Video legs = K−1.
- `reserve`: optional `[K+1, …, M]` — storyboard frames kept in the board but not used as video end targets.
- `frames.active_map` in the manifest **still lists all M frames** (1..M), including reserved cells. Only the video chain skips them.

Example (M=6, video through KF1→KF4, reserve KF5–KF6):

```json
"playback_chain": [1, 2, 3, 4],
"reserve": [5, 6]
```

## Манифест

`assets/manifest.json` обязан содержать:

```json
{
  "storyboard": {
    "latest_version": 2,
    "active_version": 2,
    "versions": {
      "001": "assets/storyboard/001-board.png",
      "002": "assets/storyboard/002-board.png"
    }
  },
  "frames": {
    "active_map": { "1": "…", "2": "…" }
  },
  "legs": {
    "0": { "latest_version": 2, "active_version": 1, "versions": { "001": "…", "002": "…" } }
  }
}
```

`active_*` — что идёт в encode/builder. Переключение active без удаления файлов.

## Скрипты

- `scripts/asset_versions.py` — next version / list / update manifest helpers (importable + CLI)
- `scripts/video_frame_chain.py` — chain resolve + ffmpeg extract
- `scripts/extract_last_frame.py` — manual last-frame extract
- `generate_storyboard_panels.py` — Kie gpt-image-2 panels → `{NNN}-frame-*.png` + stitch board + `active_map`
- `kie_seedance_2_mini.py` — legs **по порядку** 0→1→…; пишет `{NNN}-leg-*`, не перезаписывает предыдущие
- `encode_scrub_clips.py` — scrub-friendly encode
- `slice_storyboard.py` — legacy only; refuses boards with `*.panels.json`

## Запрещено

- Перезаписывать `001-*` новым генератом
- Удалять предыдущие версии «для порядка»
- Использовать имя без префикса (`board.png`, `leg-00.mp4`) в новых прогонах
