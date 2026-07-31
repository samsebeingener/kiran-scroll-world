# Storyboard panel prompt template (per-panel)

One panel = one Kie `gpt-image-2-text-to-image` call at exact `media_aspect_ratio` via `generate_storyboard_panels.py`. **No contact sheet / grid / board layout in the prompt** — the stitched board is local review math only (`shared/storyboard-generation-contract.md`, `shared/media-format-contract.md`).

Replace tokens. No text inside the frame. Continuity > pretty separate postcards.

```text
STYLE: {{STYLE_PREAMBLE}}

ONE CONTINUOUS MINIATURE WORLD (CRITICAL):
This frame is keyframe {{PANEL_INDEX}} of {{M}} along ONE camera flight through the SAME diorama territory — not a standalone postcard that only shares a color palette.
Shared ground plane, shared light, shared material language with every other keyframe of this journey.

THIS PANEL:
{{KF_BEAT}} — camera position on the path: {{KF_CAMERA}}.
Continuity landmark carried from the previous keyframe: {{KF_FROM_PREV}}.
Transition intent into the next keyframe: {{LEG_TYPE}}.

OUTPUT (single frame):
- Exactly one {{CELL_ASPECT}} keyframe (`media_aspect_ratio`), full-bleed scene.
- No grid, no contact sheet, no panel borders, no gutters, no collage layout.
- No text, no letters, no numbers, no logos, no watermarks.
```

Notes for the agent (not for Kie):

- `generate_storyboard_panels.py` appends the per-panel OUTPUT CONSTRAINT itself — keep this template single-frame.
- Style preamble must be **identical** across all M panels (`shared/storyboard-generation-contract.md`).
- Between panels the implied motion must match the journey Transition plan (drone / push-in / morph / track / etc.).
