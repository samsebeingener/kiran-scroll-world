# Scroll World — Agent Data Flow

```text
User → Director
  → Intake → Journey (+ overlay copy)
  → [Gate Budget]
  → Storyboard (Kie gpt-image-2 panels @ media_aspect_ratio, 2K/4K)
  → [Gate Storyboard]
  → Video leg 0 (Kie bytedance/seedance-2-mini first_frame_url+last_frame_url)
  → [Gate First Video]
  → remaining legs
  → Encoder → Builder (scrub-engine + overlays.json)
  → QA → Fixic (on BLOCKER / open queue)
```

## Field ownership

| Data | Owner agent | Path |
|------|-------------|------|
| Brief | Director / Intake | `00-brief.md` |
| Brand kit + format | Intake | `02-brand-kit.md`, `project.meta.json` (`media_aspect_ratio`, `storyboard_resolution`, `video_resolution`) |
| Journey + Russian copy | Journey | `03-journey.md` |
| Budget / M | Director + Journey | `04-budget.md` |
| Storyboard panels + review board | Storyboard | `assets/frames/{NNN}-frame-*.png`, `assets/storyboard/{NNN}-board.png` |
| Frame active map | Storyboard (panels) | `manifest.frames.active_map` |
| Video legs | Video | `assets/video/legs/{NNN}-leg-{LL}.mp4` |
| Overlays | Builder (from journey) | `assets/overlays.json` |
| Scrub stills + clip map | Builder (`build_scrub_media.py`) | `assets/scrub-media.json`, `assets/frames/*-leg-*-first.png` |
| Page | Builder | `src/` |
| QA report | QA | `fragments/qa.md` |
| Incidents | QA / Director → Fixic | `pipeline-fix-queue.md` |

## Hard rules

- Image gen: Kie `gpt-image-2-text-to-image` via `generate_storyboard_panels.py` (production); `gpt-image-2-image-to-image` allowed for repair only.
- Video gen: only Kie `bytedance/seedance-2-mini` via `kie_seedance_2_mini.py`.
- No baked text in images/video.
- Russian UI copy only via DOM / `overlays.json`.
- One web chain per project; format fixed by `media_aspect_ratio`.
- Asset versions: never delete/overwrite `001-*`; regenerations use `002-*`, `003-*`.
- Frame mix: `manifest.frames.active_map` may point different cells to different panel versions.
