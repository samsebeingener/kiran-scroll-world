# Scrub still contract

Scroll sections map **one-to-one to encoded video legs**. The experience must start at **t=0 of leg 0** and end on the **last frame of the final leg**. No still-only intro/outro bookends.

## Why

Storyboard cells are planning references. Seedance output diverges from slices. Using `001-frame-*.png` as scroll posters causes visible jumps at seams.

Still-only bookends (intro before leg 0, outro after the final leg) trigger Ken Burns zoom in `scrub-engine.js` instead of video scrub — forbidden.

## Rule

| Scroll section | `clip` | `still` (poster until decode) | Never use |
|----------------|--------|-------------------------------|-----------|
| Leg `i` (0…N−1) | `assets/encoded/NNN-leg-{i:02d}.mp4` | **first frame** of that encoded leg | storyboard `001-frame-*.png` |

- **`scrub-media.json` section count** = **active leg count** (must match `overlays.json` sections).
- Extract posters from **`assets/encoded/NNN-leg-LL.mp4`** (what the browser scrubs), not raw Kie output unless encoded is missing.
- Prefer **`.webm`** in `scrub-media.json` `clip` when encoded WebM exists (deploy); extract boundary PNGs from encoded **MP4** so dimensions match the scrub crop.
- Seam playback rules: **`shared/seam-playback-contract.md`**
- `*-leg-*-last.png` frames remain for QA / chain reference; they are **not** a separate scroll section.

## Pipeline

After `encode_scrub_clips.py`:

```bash
python scripts/build_scrub_media.py --project <proj>
```

(`encode_scrub_clips.py` calls this automatically.)

Outputs:

- `assets/frames/{NNN}-leg-{LL}-first.png`
- `assets/frames/{NNN}-leg-{LL}-last.png` (refreshed from encoded)
- `assets/scrub-media.json` — one `{ still, clip }` entry per leg

Builder / `mount.js` loads **`scrub-media.json` + `overlays.json`**. Do not hardcode storyboard frame paths for stills.

Overlays: `build_overlays_from_plan.py` trims journey scenes to leg count (M keyframe scenes → use scenes `1…L−1` + final scene for CTA).

## Storyboard frames

`assets/frames/001-frame-*.png` remain valid for:

- Kie `first_frame_url` / `last_frame_url` **targets** during generation
- QA reference / journey keyframe map

They are **forbidden** as scrub-engine `still` paths.

## QA

BLOCKER if:

- any `scrub-media.json` section lacks `clip`
- section count ≠ active leg count
- any `still` path points to `*-frame-0N.png` storyboard slices instead of `*-leg-*-first.png` from encoded video
- seam playback violations (`shared/seam-playback-contract.md`): white flash, dive-leg crossfade, non-centred `object-position`
