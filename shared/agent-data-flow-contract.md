# Scroll World — Agent Data Flow

```text
User → Director
  → Intake → Journey (+ overlay copy + Transition plan)
  → 04-journey-pitch.md [Gate Pitch — plain Russian]
  → 04-budget.md (internal) + project.meta.json (frames, playback_chain, reserve)
  → Storyboard (Kie gpt-image-2 panels @ media_aspect_ratio, 2K/4K)
  → [Gate Storyboard]
  → Video leg 0 (Kie bytedance/seedance-2-mini first_frame_url+last_frame_url)
  → [Gate First Video]
  → remaining legs (K−1)
  → Encoder (`encode_scrub_clips.py`) → Seam check (`check_seam_compatibility.py`, exit 2 = BLOCKER)
  → Builder (`build_scrub_media.py` + scrub-engine + overlays.json)
  → QA → Fixic (on BLOCKER / open queue)
```

## Field ownership

| Data | Owner agent | Path |
|------|-------------|------|
| Brief | Director / Intake | `00-brief.md` |
| Brand kit + format | Intake | `02-brand-kit.md`, `project.meta.json` (`media_aspect_ratio`, `storyboard_resolution`, `video_resolution`) |
| Journey + Russian copy + Transition plan | Journey | `03-journey.md` |
| Plain Russian pitch (user approve) | Journey → Director gate | `04-journey-pitch.md` |
| Budget / M / K (internal) | Director + Journey | `04-budget.md` |
| `playback_chain` / `reserve` / `video_durations` | Journey → Director meta | `project.meta.json` |
| Camera / object transform codes | Journey / Video (registries) | `shared/camera-movement-registry.md`, `shared/object-transform-registry.md` |
| Storyboard panels + review board | Storyboard | `assets/frames/{NNN}-frame-*.png`, `assets/storyboard/{NNN}-board.png` |
| Frame active map | Storyboard (panels) | `manifest.frames.active_map` |
| Video legs | Video | `assets/video/legs/{NNN}-leg-{LL}.mp4` (count = K−1) |
| Encoded scrub clips | Encoder (`encode_scrub_clips.py`) | `assets/encoded/{NNN}-leg-*.mp4` |
| Seam compatibility gate | Encoder (после encode: `check_seam_compatibility.py`) | `assets/seam-compatibility.json`, `assets/seam-compatibility.md` |
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
- `playback_chain` must be contiguous PREFIX `[1..K]`; legs = K−1; reserve frames are board-only, not scrub clips.
- User gate before Storyboard uses `04-journey-pitch.md`, not raw budget jargon.
