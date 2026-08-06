# Video leg prompt — filled example (P0–P2)

Reference only. Not a real run file. Copy the ` ```text ` block pattern into `05-image-prompts/{NNN}-leg-{LL}.md` after a live PNG read.

**Scenario:** clay miniature diorama, marsh → lab, **5s**, **3** camera beats (budget 4–6s → 2–3).  
**Shot grammar:** `MS` → `MCU`; primary `dolly_in`; secondary `slow_zoom_in`.  
**Transform:** soft plastic morph (marsh clump → lab flask), short-clip adapted.

Template: `templates/video-leg-prompt.template.md` · Skill: `skills/scroll-world-video/SKILL.md`

```text
The first frame is the exact start. The last frame is the exact end.
Single continuous cinematic shot, no cuts, no edits, no jump cuts, no time-lapse jumps.

CREATIVE DIRECTION:
A matte clay marsh clump soft-morphs into a clear lab flask while the camera dollies in and gently zooms to the final upright silhouette.

STAGES:
STAGE A: marsh platform — olive mound and reeds readable, camera MS on the clump.
STAGE B: airborne reshape — mound rises into flask body, reeds retract toward cork, pool edge frosts.
STAGE C: lab courtyard lock — upright flask, cork seated, amber fill calm, end-plate framing.

FIRST FRAME (what we see at t=0):
Center: a soft olive-green clay marsh clump with three thin reed stalks leaning right; wet-looking matte glaze on the mound. Left: a low beige clay bank with two pebble dots. Right: a shallow blue-grey water pool, no ripples. Background: warm off-white cyclorama with a soft taupe gradient. Ground: shared off-white clay plane.

LAST FRAME (what we must land on at t=end):
Center: a clear upright clay lab flask (round body, narrow neck) filled with pale amber liquid, same ground anchor as the former clump. Left: the beige bank remains, pebbles unchanged. Right: water pool becomes a thin frosted glass tray edge, same footprint. Reeds gone — replaced by a single matte cork stopper on the flask neck. Same cyclorama and ground plane.

VISUAL PLATE FIDELITY:
Start plate locks:
- silhouette_axis: vertical mound center-frame, reeds leaning ~20° right
- accent_color_position: olive-green clump center; blue-grey pool right third
- ground_plane: continuous off-white matte clay, no seams
- horizon: soft taupe band mid-height, level
- materials: matte soft clay, subtle fingerprints, damp glaze on clump only
- prop_count: 6 (marsh clump, reed×3, beige bank, pebble×2, water pool, cyclorama)

End plate locks:
- silhouette_axis: upright flask center-frame, neck vertical, cork on top
- accent_color_position: pale amber liquid in flask body; frosted tray edge right third
- ground_plane: same off-white matte clay, identical footprint under flask
- horizon: same soft taupe band, level — no tilt
- materials: matte clay flask walls, translucent amber fill, matte cork; bank/pebbles unchanged
- prop_count: 6 (flask+cork, amber fill, beige bank, pebble×2, frosted tray edge, cyclorama)
Delta vs start: mound→flask silhouette; reeds→cork; pool→frosted tray; bank/ground/horizon unchanged.
Do not invent geometry absent from either plate. Landing frame must match end plate silhouette, accent axis, and material exactly.

CAMERA PATH (timed beats — one continuous move; scale all times to 5s):
Shot grammar: MS → MCU; primary=dolly_in; secondary=slow_zoom_in
Camera: dolly in (primary). Movement: physically push the camera forward toward the subject along a straight path. Speed: smooth constant approach. Framing: keep the subject centered as scale grows. End: settle on the final closer composition.
Camera: slow zoom in (secondary, soft). Movement: gently increase lens magnification without a crash punch. Speed: slow continuous. Framing: tighten on the flask silhouette after the dolly has established depth. End: hold the locked end-plate framing.
0.0–1.6s: MS hold then start dolly_in; by 1.6s: clump fills more of frame, reeds still readable, horizon level, no zoom punch.
1.6–3.4s: continue dolly_in with soft slow_zoom_in; by 3.4s: flask body silhouette readable, reeds mostly gone, cork forming on neck, camera still moving forward gently.
3.4–4.5s: finish approach into end framing; by 4.5s: flask upright, cork seated, amber fill calm, tray edge crisp — composition matches end plate.

LANDING CONTRACT:
Final 0.5s (4.5–5.0s) settle on the last-frame composition; no late zoom, crop, or silhouette change after settle begins.

WORLD CONTINUITY:
Same miniature clay diorama throughout. Continuity landmarks: beige bank left, off-white ground plane, taupe cyclorama band.
Shared off-white ground plane; identical warm soft studio key + gentle fill; same backdrop gradient; scale consistent (toy-world proportions).

OBJECT TRANSFORM (in-camera, while camera moves):
Short-clip plastic morph: one accelerated soft reshape with hard settle on form B before the clip ends — no long intermediate plateau.
0.0–1.6s: by 1.6s: clump softens at crown, reeds shorten; bank and pebbles unchanged.
1.6–3.4s: by 3.4s: mound becomes flask body + neck; reeds collapse into cork stub; pool edge frosts into tray; no pop-in props.
3.4–4.5s: by 4.5s: amber fill solid and still; cork seated; identity fully lab flask matching end plate.
Name each visible start element and its end form. No teleport; change rides the camera path.

MATERIAL & LIGHT:
Matte soft clay, subtle fingerprints, no glossy plastic. Shadows soft and consistent with studio lighting. No bloom, no lens flare, no film grain overlay.

MOTION QUALITY (anti-slideshow):
Not a dissolve between two stills. Not a crossfade or morph wipe. Real spatial travel through one continuous set — camera and objects move together in 3D space.

COUNT: Props: 6 start → 6 end (no extras). Visible subjects: 1 primary (clump→flask). Camera moves: 1 primary dolly_in + 1 secondary slow_zoom_in. Beats: 3 camera / 3 transform (within 4–6s budget).

EXCLUSIONS: No text, letters, numbers, logos, watermarks, captions, UI, readable signs, subtitles, burned-in timecode, or BGM waveform graphics. No extra reeds, bubbles, lab labels, tubes, or people. No second flask. No resolution/settings language.

FORBIDDEN:
No text, letters, numbers, logos, watermarks, captions, UI, readable signs, subtitles, BGM cues, or new objects not present in either plate.
```
