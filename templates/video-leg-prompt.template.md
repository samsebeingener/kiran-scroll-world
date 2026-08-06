# Video leg prompt template (cinematic, detailed)

Fill from `03-journey.md` → Transition plan (`camera_moves`, `object_transform_code`, `duration_sec`) + registries + live read of the start/end PNG plates. Copy **only** the block inside ` ```text ` into `05-image-prompts/{NNN}-leg-{LL}.md` — sent to Kie verbatim.

## Agent rules (NOT sent to Kie)

- **Length:** API min 3 / max 20 000. **Product target:** **1 200–4 000** chars per leg. Script rejects &lt; **800**.
- Do **NOT** put `480p` / `720p` / API settings / duration field names in Kie prose — those live in the createTask JSON.
- `{{CELL_ASPECT}}` — only as composition language if needed (e.g. “vertical 3:4 frame”), never as API dump.
- **STAGES** describe states **before** timed beats; exact seconds only for camera handoffs in CAMERA PATH.
- Fill **plate locks ONLY after live PNG read** of start/end frames — never invent from journey text alone.
- **Beat budget** (scale to `{{DURATION}}`):
  | Duration | Beats |
  |----------|-------|
  | 4–6 s | 2–3 |
  | 7–10 s | 3–4 |
  | 11–15 s | 4–5 |
- Which PNGs are uploaded → `kie_seedance_2_mini.py`. See `shared/kie-prompt-contract.md`. No pipeline meta in the prompt file.

**Fill helpers:**
- `{{DURATION}}` = leg `duration_sec` (scale all beat timings to this length).
- `{{CREATIVE_DIRECTION}}` = one sentence: subject + event + camera idea.
- `{{STAGES}}` = STAGE A/B/C… state descriptions (what the world looks like at each stage) — **before** timestamps.
- `{{CAMERA_MOVE_SNIPPETS}}` = `prompt_snippet` from `shared/camera-movement-registry.md` for each `camera_moves` id (primary first).
- `{{TRANSFORM_MECHANIC}}` = adapted `prompt_examples` / `short_clip_variant` from `shared/object-transform-registry.md` for `object_transform_code` (match actual plates).
- Plate lock fields (`{{START_*}}` / `{{END_*}}` / `{{PLATE_DELTA}}`) — from live PNG read only.
- `{{COUNT_LINE}}` / `{{EXCLUSIONS_LINE}}` — explicit counts of major props and what must not appear.

```text
The first frame is the exact start. The last frame is the exact end.
Single continuous cinematic shot, no cuts, no edits, no jump cuts, no time-lapse jumps.

CREATIVE DIRECTION:
{{CREATIVE_DIRECTION}}

STAGES:
{{STAGES}}

FIRST FRAME (what we see at t=0):
{{FIRST_FRAME_DESCRIPTION}}
List key props, materials, colors, spatial layout left/center/right, depth layers.

LAST FRAME (what we must land on at t=end):
{{LAST_FRAME_DESCRIPTION}}
Same axes — what changed vs the first frame; every major prop accounted for.
Copy geometry, accent placement, and silhouette from a live read of the end PNG — do not paraphrase journey text.

VISUAL PLATE FIDELITY:
Start plate locks:
- silhouette_axis: {{START_SILHOUETTE_AXIS}}
- accent_color_position: {{START_ACCENT_POS}}
- ground_plane: {{START_GROUND}}
- horizon: {{START_HORIZON}}
- materials: {{START_MATERIALS}}
- prop_count: {{START_PROP_COUNT}} ({{START_PROP_LIST}})

End plate locks:
- silhouette_axis: {{END_SILHOUETTE_AXIS}}
- accent_color_position: {{END_ACCENT_POS}}
- ground_plane: {{END_GROUND}}
- horizon: {{END_HORIZON}}
- materials: {{END_MATERIALS}}
- prop_count: {{END_PROP_COUNT}} ({{END_PROP_LIST}})
Delta vs start: {{PLATE_DELTA}}
Do not invent geometry absent from either plate. Landing frame must match end plate silhouette, accent axis, and material exactly.

CAMERA PATH (timed beats — one continuous move; scale all times to {{DURATION}}s):
Shot grammar: {{SHOT_SIZE_START}} → {{SHOT_SIZE_END}}; primary={{PRIMARY_MOVE}}; secondary={{SECONDARY_MOVE_OR_NONE}}
{{CAMERA_MOVE_SNIPPETS}}
0.0–{{BEAT_1_END}}s: {{CAMERA_BEAT_1}} — by {{BEAT_1_END}}s: {{BEAT_1_END_STATE}}
{{BEAT_1_END}}–{{BEAT_2_END}}s: {{CAMERA_BEAT_2}} — by {{BEAT_2_END}}s: {{BEAT_2_END_STATE}}
{{BEAT_2_END}}–{{BEAT_3_END}}s: {{CAMERA_BEAT_3}} — by {{BEAT_3_END}}s: {{BEAT_3_END_STATE}}
(Add or drop beats to match duration budget; every beat MUST end with an observable "by Xs: …" end-state.)

LANDING CONTRACT:
Final 0.4–0.6s settle on the last-frame composition; no late zoom, crop, or silhouette change after settle begins.

WORLD CONTINUITY:
Same miniature clay diorama throughout. {{CONTINUITY_LANDMARKS}}.
Shared off-white ground plane #{{GROUND_HEX}}; identical warm soft studio key + gentle fill; same backdrop gradient; scale consistent (toy-world proportions).

OBJECT TRANSFORM (in-camera, while camera moves):
{{TRANSFORM_MECHANIC}}
{{OBJECT_TRANSFORM_BEAT_BY_BEAT}}
Name each visible element in the first frame and what it becomes in the last frame (material, silhouette, position). No pop-in; no teleport; change happens along the camera path using the mechanic above.

MATERIAL & LIGHT:
Matte soft clay, subtle fingerprints, no glossy plastic. Shadows soft and consistent with studio lighting. No bloom, no lens flare, no film grain overlay.

MOTION QUALITY (anti-slideshow):
Not a dissolve between two stills. Not a crossfade or morph wipe. Real spatial travel through one continuous set — camera and objects move together in 3D space.

COUNT: {{COUNT_LINE}}
EXCLUSIONS: {{EXCLUSIONS_LINE}}

FORBIDDEN:
No text, letters, numbers, logos, watermarks, captions, UI, readable signs, subtitles, BGM cues, or new objects not present in either plate.
```
