# Video leg prompt template (cinematic, detailed)

Fill from `03-journey.md` → Transition plan (`camera_moves`, `object_transform_code`, `duration_sec`) + registries + live read of the start/end PNG plates. Copy **only** the block inside ` ```text ` into `05-image-prompts/{NNN}-leg-{LL}.md` — sent to Kie verbatim.

**Length (Kie API):** min 3, max 20 000 chars. **Product target:** **1 200–4 000** chars per leg (light model needs rich direction). Script rejects &lt; 800.

**Agent rules (not for Kie):** which PNGs are uploaded → `kie_seedance_2_mini.py`. See `shared/kie-prompt-contract.md`. No pipeline meta in the prompt file.

**Fill helpers:**
- `{{DURATION}}` = leg `duration_sec` (scale all beat timings to this length).
- `{{CAMERA_MOVE_SNIPPETS}}` = `prompt_snippet` from `shared/camera-movement-registry.md` for each `camera_moves` id (primary first).
- `{{TRANSFORM_MECHANIC}}` = adapted `prompt_examples` / `short_clip_variant` from `shared/object-transform-registry.md` for `object_transform_code` (match actual plates).

```text
The first frame is the exact start. The last frame is the exact end.
Single continuous cinematic shot, no cuts, no edits, no jump cuts, no time-lapse jumps.

SHOT:
One unbroken take, {{DURATION}}s feel, {{CELL_ASPECT}} miniature diorama. Shallow-to-medium depth of field; foreground parallax on props; horizon stable.

TRANSITION TYPE: {{TYPE_CODES}}

FIRST FRAME (what we see at t=0):
{{FIRST_FRAME_DESCRIPTION}}
List key props, materials, colors, spatial layout left/center/right, depth layers.

LAST FRAME (what we must land on at t=end):
{{LAST_FRAME_DESCRIPTION}}
Same axes — what changed vs the first frame; every major prop accounted for.
Copy geometry, accent placement, and silhouette from a live read of the end PNG — do not paraphrase journey text.

VISUAL PLATE FIDELITY:
Start plate locks: {{START_PLATE_LOCKS}}
End plate locks: {{END_PLATE_LOCKS}}
Do not introduce geometry not present in either plate. Landing frame must match end plate silhouette, accent axis, and material exactly.

CAMERA PATH (timed beats — one continuous move; scale all times to {{DURATION}}s):
{{CAMERA_MOVE_SNIPPETS}}
0.0–{{BEAT_1_END}}s: {{CAMERA_BEAT_1}}
{{BEAT_1_END}}–{{BEAT_2_END}}s: {{CAMERA_BEAT_2}}
{{BEAT_2_END}}–{{BEAT_3_END}}s: {{CAMERA_BEAT_3}}
Final ~0.5s: ease-in-out settle on the last-frame composition; no sudden stop or snap zoom.

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

FORBIDDEN:
No text, letters, numbers, logos, watermarks, captions, UI, readable signs, subtitles, or new objects not implied by the two plates.
```
