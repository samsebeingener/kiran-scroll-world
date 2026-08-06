# Scroll World — prompts

## Intake (Director → user in Russian)

1. World topic
2. `media_aspect_ratio` (panels = video)
3. Brand kit
4. Art direction
5. Embed vs demo-page + insert placement + video size (480p default / 720p large)

## Gates

1. Gate Pitch: show `04-journey-pitch.md` verbatim (plain Russian); internal budget M panels + (K−1) videos; approve before storyboard
2. Gate Video Settings (if unset): insert place + resolution before first createTask; duration 4–15 (required per-leg from journey — no default)

## Storyboard board prompt shape

```text
Contact sheet storyboard with {M} panels in a {COLS}x{ROWS} grid on one image.
Each panel is a `{media_aspect_ratio}` keyframe of one camera journey.
Continuity landmark between neighbors; transition intent from the journey Transition plan.
No text, letters, numbers, logos, watermarks.
```

Шаблон: `templates/storyboard-prompt.template.md`; в Kie уходит **один** запрос через `generate_storyboard_panels.py`.

## Video leg prompt shape (Seedance 2.0 Mini, P0–P2)

Шаблон: `templates/video-leg-prompt.template.md`.  
Filled example: `templates/examples/video-leg-prompt.filled.md`.  
Порядок заполнения: `skills/scroll-world-video/SKILL.md` (live PNG → locks → STAGES → CREATIVE DIRECTION → shot grammar → beats → landing → COUNT/EXCLUSIONS).

```text
Anchor: first frame = exact start; last frame = exact end; single continuous shot
CREATIVE DIRECTION: one sentence (subject + event + camera)
SHOT / shot grammar: shot size + 1 primary + ≤1 secondary (registry snippets)
FIRST FRAME / LAST FRAME: plate descriptions from live PNG read
VISUAL PLATE FIDELITY: structured start/end locks (silhouette_axis, accent, ground, horizon, materials, prop_count)
STAGES: A / B / C… scene states before timestamps
CAMERA PATH: timed beats scaled to duration_sec; each beat ends with "by Xs: …"
LANDING CONTRACT: settle 0.4–0.6s; no late zoom/crop/silhouette change
OBJECT TRANSFORM: mechanic + beat-by-beat with end-states (respect beat budget)
WORLD CONTINUITY / MATERIAL & LIGHT / MOTION QUALITY
COUNT: / EXCLUSIONS:
FORBIDDEN: no text/logos/… 
```

Beat budget: 4–6s → 2–3 camera beats; 7–10 → 3–4; 11–15 → 4–5 (object-transform ≤ same caps).

Visual motion only — `shared/kie-prompt-contract.md`. No legs/storyboard/MP4/`@image`/480p/720p in prompt text.
