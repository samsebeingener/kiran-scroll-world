# Scroll World — Kie video prompt contract

**Kie receives exactly:** `first_frame_url` + `last_frame_url` + `prompt` string.

The model has **no** memory of prior tasks, leg indices, MP4 files, storyboard paths, or our pipeline. It only animates between the **two PNGs you uploaded**.

## Split of responsibilities

| Layer | Who | Content |
|-------|-----|---------|
| **Which images** | `video_frame_chain.py` + `kie_seedance_2_mini.py` | leg 0: storyboard `playback_chain[0]`→`[1]` (default KF1→KF2); leg i>0: ffmpeg last frame of leg i−1 → storyboard `playback_chain[i+1]` (default KFi+2) |
| **What happens between them** | `05-image-prompts/*-leg-*.md` → Kie `prompt` | Pure visual/cinematic English only |

Never explain the pipeline inside the Kie prompt.

## NO TEXT ON IMAGE (MANDATORY)

Промпты **storyboard и video всегда** содержат блок NO TEXT: на генерируемых изображениях/видео запрещены **текст, буквы, цифры, логотипы, водяные знаки**. Русский/брендовый copy накладывается потом через DOM overlays (`assets/overlays.json`), никогда через генерацию. В режиме image-to-image референс задаёт стиль/композицию — текстовый промпт всё равно **обязателен** и тоже содержит блок NO TEXT.

## Length (Kie API)

| | Chars |
|---|------|
| API minimum | 3 |
| API maximum | 20 000 |
| **Script minimum** | **800** (hard reject) |
| **Recommended** | **1 200–4 000** (warn if &lt; 1 200) |

Short prompts under-direct the model. Use `templates/video-leg-prompt.template.md` — timed camera beats, explicit first/last plate descriptions, beat-by-beat object morph.

## Allowed in Kie prompt

- What is visible in the **first frame plate** and **last frame plate**
- Camera path (dolly, crane, steadicam, aerial glide, …)
- Object/material transforms between those two looks
- World continuity **as seen in the plates** (ground, light, landmarks)
- Anti-slideshow as **motion quality** (no dissolve-only, no crossfade wipe) — not as pipeline rules
- `The first frame is the exact start. The last frame is the exact end.` — anchors the two uploaded images

## Forbidden in Kie prompt (script rejects)

Pipeline / meta (model cannot act on these):

- `FRAME SOURCES`, `frame sources`
- `previous leg`, `next leg`, `leg 0`, `leg 1`, …
- `storyboard`, `storyboard slice`, `intermediate storyboard`
- `preserve rendered`, `rendered end`, `previous generation`, `previous video`
- `snap-back`, `snap back to storyboard`
- `momentum from previous`, `continue the velocity`, `continue momentum`
- `MP4`, `ffmpeg`, `extract`, `active_map`, `kie`, `seedance task`
- `@image1`, `@image2`

## Journey vs Kie prompt

`03-journey.md` → `video_prompt_seed` is **notes for the video agent** (may mention KF numbers, legs, continuity plan).

The video agent **rewrites** that into `05-image-prompts/*-leg-*.md` with **only** visual language before `createTask`.

## Agent checklist before createTask

1. Prompt **≥ 800** chars (target **1 200–4 000**); all template sections filled with concrete visuals
2. Describes motion between **these two PNGs** — not how we chose them
3. No filenames, leg numbers, or storyboard references
4. Timed camera beats match `duration` (**4–15** s; required per leg from the journey — no default; complex morphs often 8–12). Prefer camera-path snippets from the journey / camera registry so beats land on the real clip length
5. Ending: slow forward drift in final ~0.5s — no “next leg”
