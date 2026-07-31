# Scroll World — Memory Protocol

Per-run memory lives under the **host project**, not inside the plugin install:

```text
<PROJECT_ROOT>/projects/scroll-world/<YYYY-MM-DD-slug>/
```

## Layout

```text
00-brief.md
01-handoff.md
02-brand-kit.md
03-journey.md              # Board & playback, Transition plan, Keyframe map, overlays
04-journey-pitch.md        # plain Russian pitch for user approve BEFORE storyboard
04-budget.md               # internal: M∈{3,6,9}, K, legs_now, estimated gens (после pitch approve)
pipeline-fix-queue.md
project.meta.json          # frames=M; playback_chain / K when set
assets/
  storyboard/001-board.png
  storyboard/002-board.png          # regenerations keep older files
  frames/001-frame-01.png …
  frames/002-frame-03.png …         # mix via manifest.frames.active_map
  video/legs/001-leg-00.mp4
  video/legs/002-leg-00.mp4
  encoded/
  seam-compatibility.json      # gate: check_seam_compatibility.py (exit 2 = BLOCKER)
  seam-compatibility.md
  overlays.json
  manifest.json
src/                       # page + scrub-engine mount
fragments/                 # per-agent reports + incident_report
05-image-prompts/001-storyboard.md
```

## Journey artifacts

| File | Audience | Notes |
|------|----------|-------|
| `03-journey.md` | agents | M/K, Transition plan (K−1 legs), Keyframe map (all M with role playback\|reserve) |
| `04-journey-pitch.md` | user | Plain Russian; no codes / M-K jargon / model slugs / filenames — approve before Storyboard |
| `04-budget.md` | internal | Budget numbers after pitch; not the user-facing pitch |

In `project.meta.json` after Gate Pitch approve: `frames` = **M**; store **playback_chain** (PREFIX 1..K) and/or `K` so Video/Encoder know legs_now = K−1. `04-budget.md` пишется **после** утверждения питча, не параллельно.

## Rules

- One animation = one slug folder. Never mix runs.
- Absolute user home paths must not appear in artifacts — use `<PROJECT_ROOT>` / relative paths.
- Handoff markers written by Director only after each Task completes.
- Fragments must include `## Errors & Fixes` and `incident_report:` (or `none`).
- Asset versions: never delete/overwrite `001-*`; see `shared/asset-versioning-contract.md`.
