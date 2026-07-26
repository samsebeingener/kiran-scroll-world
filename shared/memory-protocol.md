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
03-journey.md              # scenes + Russian overlay copy table
04-budget.md               # M∈{3,6,9} (from Journey), estimated gens
pipeline-fix-queue.md
project.meta.json
assets/
  storyboard/001-board.png
  storyboard/002-board.png          # regenerations keep older files
  frames/001-frame-01.png …
  frames/002-frame-03.png …         # mix via manifest.frames.active_map
  video/legs/001-leg-00.mp4
  video/legs/002-leg-00.mp4
  encoded/
  overlays.json
  manifest.json
src/                       # page + scrub-engine mount
fragments/                 # per-agent reports + incident_report
05-image-prompts/001-storyboard.md
```

## Rules

- One animation = one slug folder. Never mix runs.
- Absolute user home paths must not appear in artifacts — use `<PROJECT_ROOT>` / relative paths.
- Handoff markers written by Director only after each Task completes.
- Fragments must include `## Errors & Fixes` and `incident_report:` (or `none`).
- Asset versions: never delete/overwrite `001-*`; see `shared/asset-versioning-contract.md`.
