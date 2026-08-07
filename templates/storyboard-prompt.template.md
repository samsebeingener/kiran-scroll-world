# Storyboard board prompt template

**No hardcoded cell aspect.** Everything comes from intake math:

1. User picks Seedance / video format → `project.meta.json` `media_aspect_ratio`
   (`1:1` | `4:3` | `3:4` | `16:9` | `9:16` | `21:9`)
2. M ∈ {3,6,9} → grid → exact board aspect
3. Script picks Kie canvas `aspect_ratio` + `resolution` (1K|2K|4K; **2K/4K cannot use 3:1 / 1:3 / 5:4 / 4:5 / 9:21** → may force 1K)
4. Slice → frames at **the same** `media_aspect_ratio` as Seedance

## Agent notes (NOT sent to Kie)

Slug / journey notes stay outside the fence.  
`generate_storyboard_panels.py` extracts ` ```text ` then **prepends computed FORMAT LOCK**.

Fill tokens from `--dry-run` / `resolve_storyboard_request` — **never invent ratios**:

- `{{CELL_ASPECT}}` = `media_aspect_ratio` (video + sliced frames)
- `{{REQUEST_ASPECT}}` = Kie createTask `aspect_ratio` (whole canvas)
- `{{EXACT_BOARD_ASPECT}}` = math `cols×cell : rows×cell`
- `{{RESOLUTION}}` = Kie resolution actually used (may be 1K)
- `{{M}}` `{{COLS}}` `{{ROWS}}`

**MANDATORY — NO TEXT ON IMAGE.** Copy = DOM overlays later.

```text
STYLE: {{STYLE_PREAMBLE}}
(Each panel is a {{CELL_ASPECT}} still inside the {{REQUEST_ASPECT}} contact-sheet canvas — do not describe the WHOLE image as {{CELL_ASPECT}}.)

ONE CONTINUOUS MINIATURE WORLD (CRITICAL):
All panels are keyframes along ONE camera flight through the SAME diorama territory — not separate unrelated postcards that only share a color palette.
Shared ground plane, shared light, shared material language. Panel N is further along the same flight path than panel N-1. Keep a readable continuity landmark or path axis between neighbors.

Contact sheet: {{M}} panels in {{COLS}} COLUMNS × {{ROWS}} ROWS on one {{REQUEST_ASPECT}} canvas (exact grid math {{EXACT_BOARD_ASPECT}}; Kie resolution {{RESOLUTION}}).
Each panel cell = {{CELL_ASPECT}} (= Seedance media_aspect_ratio). Order L→R, T→B:

1) {{KF1_BEAT}} — camera position: {{KF1_CAMERA}}. Continuity seed: {{KF1_LANDMARK}}.
2) {{KF2_BEAT}} — further along the path: {{KF2_CAMERA}}. Must still read leftover of KF1: {{KF2_FROM_PREV}}. Transition intent into this frame: {{LEG0_TYPE}}.
…
{{M}}) {{KFM_BEAT}} — …

Between panels the implied motion must match the journey Transition plan (drone / push-in / morph / track / etc.).
MANDATORY — NO TEXT ON IMAGE: absolutely no text, no letters, no numbers, no logos, no watermarks, no signage in any panel. All copy is overlaid later via DOM overlays.
```
