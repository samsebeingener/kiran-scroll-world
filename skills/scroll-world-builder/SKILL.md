---
name: scroll-world-builder
description: Mount scrub-engine with encoded clips and overlays.json.
---

# Builder

Контракты: `shared/overlay-motion-contract.md`, **`shared/scrub-still-contract.md`**, **`shared/seam-playback-contract.md`**. Engine: `references/scrub-engine.js`.

1. `python scripts/build_scrub_media.py --project <PROJECT>` (encoded clips готовит Encoder: `encode_scrub_clips.py` — Builder его не запускает)
2. `python scripts/build_overlays_from_plan.py --project <PROJECT>` (emits `crossfade` / `scrubLerp` / `scrubEps`)
3. Скопируй **canonical** `references/scrub-engine.js` → `src/` (не правь seam-логику ad-hoc)
4. `mount.js` грузит **`overlays.json` + `scrub-media.json`**; **`connectors: []`**
5. Stills только из `*-leg-*-first.png` (encoded video), **не** `001-frame-*.png`
6. Seam QA: hard cut, hold-back, `object-position: center center` — см. seam contract
7. Не хардкодь русский текст в исходниках

Fragment: `fragments/builder.md`.
