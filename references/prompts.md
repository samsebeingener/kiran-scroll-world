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

## Storyboard panel prompt shape

```text
<STYLE PREAMBLE, identical>. Continuous fly-through keyframes.
Each panel is a `{media_aspect_ratio}` keyframe of one camera journey.
No text, letters, numbers, logos, watermarks.
```

CLI appends per-panel OUTPUT CONSTRAINT via `generate_storyboard_panels.py`.

## Video leg prompt shape (Seedance 2.0 Mini)

```text
FIRST FRAME: …
LAST FRAME: …
CAMERA PATH (timed beats for {{DURATION}}s): …
OBJECT TRANSFORM: …
MATERIAL & LIGHT / MOTION QUALITY / FORBIDDEN
```

Visual motion only — `shared/kie-prompt-contract.md`. No legs/storyboard/MP4 in prompt text.
