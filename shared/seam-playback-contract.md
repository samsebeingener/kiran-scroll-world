# Scroll World — Seam & playback contract

**Mandatory for every run** (encode → builder → QA → deploy). Applies to `references/scrub-engine.js` and all generated `src/scrub-engine.js` copies.

## Problem

Bad seams come from three layers:

1. **Content** — leg `i` last frame ≠ leg `i+1` first frame (chain / drift).
2. **Assets** — poster PNGs extracted at a different resolution or crop than encoded scrub clips.
3. **Engine** — overlapping dive opacity, dissolve between legs, or hiding the outgoing clip before the incoming video has painted → **white flash** on `--sw-bg`.

## Generation (video chain)

| Rule | Detail |
|------|--------|
| Chain order | Legs `0 → 1 → …`; leg `i>0` **start** = last frame of active leg `i−1` MP4 |
| Plate fidelity | `shared/frame-fidelity-contract.md` — prompts calibrated from actual PNG plates |
| Drift log | After each leg, append `{NNN}-leg-drift-log.md`; **major/blocker** → re-gen before continuing |
| Re-gen leg `k` | Must re-run legs `k+1…` or recalibrate their start plates |
| No storyboard stills in scrub | Posters from encoded video only — `shared/scrub-still-contract.md` |

## Encode & scrub media

After `encode_scrub_clips.py`:

```bash
python scripts/build_scrub_media.py --project <proj> --refresh
```

| Rule | Detail |
|------|--------|
| One section per leg | `scrub-media.json` sections = active leg count = `overlays.json` sections |
| No bookends | No still-only intro/outro sections |
| Poster source | Extract `*-first.png` / `*-last.png` from **encoded MP4** (same crop as scrub), not raw Kie MP4 unless encoded missing |
| Playback clip | Prefer `assets/encoded/*.webm` in `scrub-media.json` when present (portfolio deploy); MP4 fallback OK for local dev |
| Dimension match | Boundary PNGs must match encoded scrub dimensions (e.g. 854×480 for 480p 16:9) — re-run `--refresh` after re-encode |

### Mandatory ±5-frame compatibility check

After every encode, run:

```bash
python scripts/check_seam_compatibility.py --project <proj> --window 5
```

For every adjacent pair `leg i → leg i+1`, the checker:

1. extracts the last five decoded frames of leg `i` and the first five decoded
   frames of leg `i+1` from the encoded playback source;
2. builds the complete `5 × 5` MAE matrix (`last[-5..-1] × first[0..4]`);
3. records the exact endpoint error, the best compatible pair, improvement, and
   suggested outgoing trim in `assets/seam-compatibility.json` and `.md`;
4. returns exit code `2` when the best-window MAE exceeds the configured
   threshold (default `0.08`), so CI/release gates can stop before publication.

The best pair is a diagnostic and a permitted non-regeneration adjustment
candidate; it must not silently rewrite video assets. If a trim is applied in
the engine, rerun the checker and record the chosen `seamTrimFrames` value in
the project handoff/QA report. A low MAE does not override visual QA when the
scene has a semantic geometry change.

## Engine (`scrub-engine.js`) — non-negotiable

Canonical source: `references/scrub-engine.js`. Builder copies into `src/`.

### Dive seam opacity

- **Hard cut** at shared dive boundaries (`seg[i].end === seg[i+1].start`).
- **Never** cross-dissolve two dive legs (no simultaneous partial opacity on neighbours).
- **Eager preload:** leg 0 loads in the visible scene immediately; legs 1…N warm in off-screen `sw-preload` after leg 0 metadata (bandwidth priority).
- **Reveal gate:** hide still only when video is mounted in the scene **and** `readyState >= 2` (never mark painted from preload host).
- **`<link rel="preload" as="image">`** for leg-0 still in `index.html` / `mount.js` (do **not** use `as="video"` — unsupported in Chrome).
- **Early `fetch(priority: high)`** for leg-0 clip URL in `mount.js` before overlays load.
- `connectors: []` — no connector clips in v1.

### CSS / still behaviour

- `object-fit: cover`; **`object-position: center center`** on `.sw-scene__video` and `.sw-scene__still` (all breakpoints).
- **No** `translateX` Ken Burns on stills — scale only until clip paints.
- Still hidden only after `has-clip` (video frame painted), not on metadata alone.

### `overlays.json` motion defaults

Builder / `build_overlays_from_plan.py` should emit (or merge):

```json
{
  "crossfade": 0.12,
  "scrubLerp": 0.08,
  "scrubEps": 0.002
}
```

- **`crossfade`** — fade for **first/last exterior** edges and copy only; **not** dissolve between dive legs.
- Do **not** lower `crossfade` below `0.08` to “fix” seams — that causes white flash.

### `mount.js`

- `connectors: []`
- Pass `crossfade`, `scrubLerp`, `scrubEps` from `overlays.json`
- Clips load via same-origin `<video src>` (no `blob:` URLs) — required under portfolio CSP

## QA gates (BLOCKER)

- White flash or cream background visible at any leg seam during scroll
- Both dive scenes at visible opacity > 0.5 at the same seam scroll position
- `object-position` not centred (42% / 44% / 46% drift)
- `still` path uses `*-frame-0N.png` storyboard slice
- `scrub-media` section count ≠ leg count
- Boundary PNG resolution ≠ encoded scrub resolution
- Seam compatibility report is missing or stale after encode
- Best-window seam MAE exceeds the configured threshold without documented user acceptance
- A suggested trim is applied without rerunning the compatibility check

## Deploy

Portfolio packs must copy **current** `src/scrub-engine.js`, `mount.js`, `overlays.json`, `scrub-media.json`, encoded `*.webm`, and `*-first.png` posters from the project — not stale `_dist` engine.

## Related

- `shared/scrub-still-contract.md`
- `shared/frame-fidelity-contract.md`
- `shared/video-generation-contract.md`
- `references/pipeline.md` § Seam playback
