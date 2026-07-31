# Storyboard board prompt template

Replace tokens. Continuity > pretty separate postcards.

**MANDATORY — NO TEXT ON IMAGE: no text, no letters, no numbers, no logos, no watermarks anywhere on the generated image. Russian/brand copy is added later as DOM overlays, never baked into pixels.**

```text
STYLE: {{STYLE_PREAMBLE}}

ONE CONTINUOUS MINIATURE WORLD (CRITICAL):
All panels are keyframes along ONE camera flight through the SAME diorama territory — not separate unrelated postcards that only share a color palette.
Shared ground plane, shared light, shared material language. Panel N is further along the same flight path than panel N-1. Keep a readable continuity landmark or path axis between neighbors.

Contact sheet storyboard with {{M}} panels in a {{COLS}}x{{ROWS}} grid on one wide image.
Each panel is a {{CELL_ASPECT}} keyframe. Order L→R, T→B:

1) {{KF1_BEAT}} — camera position: {{KF1_CAMERA}}. Continuity seed: {{KF1_LANDMARK}}.
2) {{KF2_BEAT}} — further along the path: {{KF2_CAMERA}}. Must still read leftover of KF1: {{KF2_FROM_PREV}}. Transition intent into this frame: {{LEG0_TYPE}}.
…
{{M}}) {{KFM_BEAT}} — …

Between panels the implied motion must match the journey Transition plan (drone / push-in / morph / track / etc.).
MANDATORY — NO TEXT ON IMAGE: absolutely no text, no letters, no numbers, no logos, no watermarks, no signage in any panel. All copy is overlaid later via DOM overlays.
```
