# Scroll World — Overlay Motion Contract

Russian (or brand-language) copy is **never** baked into storyboard or video.
It is rendered as **DOM overlays** driven by scroll progress — same idea as scroll-scrub `overlay-motion`.

## Source

`scroll-world-journey` writes per-section copy into `03-journey.md`:

| Field | Required |
|-------|----------|
| title (headline) | yes |
| body | yes |
| cta | last section only |
| eyebrow | optional — короткая надзаголовочная строка (label над title) |
| tags | optional — список коротких тегов/чипов сцены (`string[]`) |

## Runtime file

```text
assets/overlays.json
```

Built by:

```bash
python scripts/build_overlays_from_plan.py --project <project-path>
```

### Schema (compatible spirit with scroll-scrub)

```json
{
  "diveScroll": 1.3,
  "crossfade": 0.12,
  "scrubLerp": 0.08,
  "scrubEps": 0.002,
  "sections": [
    {
      "id": "scene-01",
      "eyebrow": "…",
      "title": "…",
      "body": "…",
      "tags": ["…", "…"],
      "scroll": 1.6,
      "linger": 0.45,
      "accent": "#8FB98A"
    }
  ],
  "cta": {
    "primary": { "label": "…", "href": "#cta" },
    "secondary": { "label": "…", "href": "#more" }
  }
}
```

Builder maps this into `mountScrollWorld(… sections[…].title/body/cta …)`.
**Do not hardcode Russian strings in `.js` / `.html`.**

Seam playback: `crossfade` is for exterior/copy fades only — **not** dissolve between dive legs. See `shared/seam-playback-contract.md`.

## Edit loop

User: «подправь текст» → edit `overlays.json` (or journey + rebuild) → refresh preview.
**No Kie re-run.**

## QA

- Overlay text appears in planned scroll ranges
- Last section CTA visible
- Reduced-motion still shows static copy
- No baked text in media
