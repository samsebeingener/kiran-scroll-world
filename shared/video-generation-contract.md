# Scroll World — Video Generation Contract

## Model (only)

**Kie** `bytedance/seedance-2-mini` via `scripts/kie_seedance_2_mini.py`.

Docs: https://docs.kie.ai/market/bytedance/seedance-2-mini  

This repository has **no other video clients**.

## Architecture

Sequential legs with **video chain**:

| Leg | first frame (start) | last frame (end) |
|-----|---------------------|------------------|
| `0` | storyboard `active_map[str(playback_chain[0])]` (default `1`) | storyboard `active_map[str(playback_chain[1])]` (default `2`) |
| `i>0` | **last frame of active leg `i−1` MP4** (ffmpeg extract) | storyboard `active_map[str(playback_chain[i+1])]` (default `i+2`) |

- Default: `playback_chain` omitted → K = M → video count = **M − 1**.
- With `playback_chain` = prefix `[1..K]`: video count = **K − 1** (max leg index = K − 2). Optional `reserve` = `[K+1..M]` are board frames not used in video legs; `active_map` still holds all M frames.
- Generate legs **in order** `0 → 1 → …`.
- After each leg: cache `assets/frames/{NNN}-leg-{LL}-last.png`.
- `connectors: []` in scrub config — dive legs hard-cut at seams (`shared/seam-playback-contract.md`).
- After encoding the complete active chain, run the mandatory `last[5] × first[5]`
  compatibility gate. The gate may recommend a small outgoing trim, but it never
  rewrites source video silently.

Manual override: `--start` / `--end` on `kie_seedance_2_mini.py` (repair only).

## API

```text
POST https://api.kie.ai/api/v1/jobs/createTask
Authorization: Bearer $KIE_API_KEY
```

```json
{
  "model": "bytedance/seedance-2-mini",
  "input": {
    "prompt": "...",
    "first_frame_url": "https://.../frame-a.png",
    "last_frame_url": "https://.../frame-b.png",
    "resolution": "480p",
    "aspect_ratio": "16:9",
    "duration": 5,
    "generate_audio": false,
    "nsfw_checker": false
  }
}
```

### resolution

| Value | When |
|-------|------|
| `480p` | **Default** — маленькая вставка / стандарт |
| `720p` | Только если пользователь явно выбрал крупный блок |

If unset in meta and CLI — script uses **`480p`**.

Also ask **куда вставляется** блок (`insert_placement`) if unset — at the latest before uploading frames to Kie.

### duration

- Product range: **4–15** seconds.
- **No default.** Duration is mandatory and is chosen by the Director when designing the journey (per-leg `duration_sec` in the Transition plan — режиссёрское решение).
- Complex morphs often need **8–12**.
- Resolve order: CLI `--duration` → `video_durations[leg]` → `video_duration`. If none is set — configuration error, not a fallback default.

### aspect_ratio

`1:1`, `4:3`, `3:4`, `16:9`, `9:16`, `21:9`, `adaptive`

**Required:** same as storyboard panels → `project.meta.json` → **`media_aspect_ratio`**.

Upload local frames via `scripts/kie_file_upload.py` → `fileUrl` as `first_frame_url` / `last_frame_url`.

## Prompt rules

Контракт: `shared/kie-prompt-contract.md`.  
Промпт пишет **scroll-world-video** по `templates/video-leg-prompt.template.md`.

Must include (detailed template, **≥ 800** chars, target **1 200–4 000**):

1. FIRST FRAME / LAST FRAME plate descriptions
2. Timed CAMERA PATH beats aligned with `duration`
3. Beat-by-beat OBJECT TRANSFORM
4. WORLD CONTINUITY, MATERIAL & LIGHT
5. MOTION QUALITY + FORBIDDEN (no text/logos)

## Env

```text
KIE_API_KEY=...
KIE_API_BASE_URL=https://api.kie.ai
KIE_FILE_UPLOAD_BASE=https://kieai.redpandaai.co
```

## project.meta.json (video)

```json
{
  "video_model": "bytedance/seedance-2-mini",
  "media_aspect_ratio": "16:9",
  "insert_placement": "hero-below-nav",
  "video_resolution": "480p",
  "video_duration": 6,
  "video_durations": [4, 8, 10],
  "frames": 6,
  "playback_chain": [1, 2, 3, 4],
  "reserve": [5, 6]
}
```

| Field | Role |
|-------|------|
| `frames` | M — задаётся после Journey / Gate Pitch (`3`, `6` или `9`) |
| `playback_chain` | Optional prefix `[1..K]`; omit → K=M. Legs = K−1 |
| `reserve` | Optional `[K+1..M]` when chain is a proper prefix of M |
| `video_duration` | Scalar fallback for all legs |
| `video_durations` | Optional per-leg list (index = leg); overrides scalar when CLI unset |

## Scripts

| Script | Role |
|--------|------|
| `scripts/kie_common.py` | auth + poll |
| `scripts/kie_file_upload.py` | Official Kie CDN upload → HTTPS `fileUrl` |
| `scripts/video_frame_chain.py` | Resolve start/end paths + ffmpeg last-frame extract + `playback_chain` |
| `scripts/extract_last_frame.py` | CLI: MP4 → PNG last frame |
| `scripts/kie_seedance_2_mini.py` | create + download leg (canonical, chained) |
| `scripts/encode_scrub_clips.py` | ffmpeg scrub-friendly encodes |
| `scripts/check_seam_compatibility.py` | mandatory ±5-frame seam matrix + MAE gate |

## Outputs (versioned)

```text
assets/frames/001-leg-00-last.png
assets/video/legs/001-leg-00.mp4
assets/encoded/001-leg-00.mp4
assets/manifest.json
```

See `shared/asset-versioning-contract.md`.
