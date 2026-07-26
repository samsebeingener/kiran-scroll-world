---
name: scroll-world-encoder
description: Encode legs to scrub-friendly MP4 via ffmpeg.
---

# Encoder

```bash
python scripts/encode_scrub_clips.py --project <PROJECT>
```

Размер scale из `project.meta.json`:
- `video_resolution` — короткая сторона (`480p` → 480, `720p` → 720)
- **`media_aspect_ratio`** — пропорции кадра (тот же, что сториборд и Seedance)

Примеры при `480p` (default):
- `16:9` → 854×480
- `9:16` → 480×854
- `1:1` → 480×480

При `720p` (если пользователь явно выбрал):
- `16:9` → 1280×720
- `9:16` → 720×1280
- `1:1` → 720×720

override ширины: `--width 1280` (высота из aspect)

Контракт: `shared/media-format-contract.md`, `scripts/media_format.py`.

Нужен `ffmpeg` на PATH. Выход: `assets/encoded/{NNN}-leg-*.mp4`.
Fragment: `fragments/encoder.md`.
