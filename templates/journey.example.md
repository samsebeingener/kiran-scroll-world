# Example journey (03-journey.md)

## Style preamble

```text
…verbatim English style lock…
```

## Board & playback

| Field | Value |
|-------|-------|
| **M** | 6 |
| **K** | 4 |
| **playback_chain** | PREFIX panels 1..4 |
| **reserve** | TAIL panels 5..6 |
| **legs_now** | 3 (= K − 1) |

Rationale (RU ok): тяжёлая пластика identity → 3 длинные ноги (≈8–10s), доска 6 панелей с запасом 5–6 на продолжение.

## Transition plan (обязательно — только legs текущей цепи)

Режиссура между keyframes **playback**. Каталог типов: `shared/cinematic-transition-contract.md`.  
Камера: ids из `shared/camera-movement-registry.md` (без prompt_snippet).  
Объект: code из `shared/object-transform-registry.md` (comfort_sec мягкий).

### Leg 0 — KF1 → KF2
- **type:** drone_flythrough + morph_transform
- **duration_sec:** 8
- **camera_moves:** [helicopter_style_aerial, pan_right, slow_zoom_in]
- **object_transform_code:** plastic_morph
- **camera:** slow diagonal aerial glide ~8s along the clay ground axis toward the next island; no reverse
- **world_continuity:** same off-white clay ground plane and soft studio backdrop; ticket-stub debris trail leads the eye
- **object_transform:** carnival masks and hype blobs collapse/melt into identical clone busts while camera advances
- **forbidden:** simple crossfade / teleport / dark void jump
- **video_prompt_seed (EN):** Opening plate: carnival masks and ticket stubs scattered on off-white clay, aerial view. Landing plate: rows of identical clone busts on low pedestals ahead. Camera: slow diagonal drone glide ~8s along ground axis — no reverse. Beat 1 (0–2s): pass over mask pile; masks soften edges. Beat 2 (2–5s): masks melt into clay puddles that rise as bust shoulders. Beat 3 (5–7s): bust heads pop into identical silhouettes. Final 1s: forward drift toward pedestal row. Same studio warm light, continuous ground plane, debris trail leads eye east. Not dissolve — real travel through one miniature set.

### Leg 1 — KF2 → KF3
- **type:** …
- **duration_sec:** …
- **camera_moves:** […]
- **object_transform_code:** …
- **camera:** …
- **world_continuity:** …
- **object_transform:** …
- **forbidden:** …
- **video_prompt_seed (EN):** …

### Leg 2 — KF3 → KF4
- **type:** …
- **duration_sec:** …
- **camera_moves:** […]
- **object_transform_code:** …
- **camera:** …
- **world_continuity:** …
- **object_transform:** …
- **forbidden:** …
- **video_prompt_seed (EN):** …

(Ровно **K − 1** = 3 legs. Reserve KF5–KF6 без Transition plan до продолжения.)

## Keyframe map (единый мир — все M панелей)

| KF | role | Beat | Camera position on the path | Must-keep from previous |
|----|------|------|-----------------------------|-------------------------|
| 1 | playback | … | establishing island A | — |
| 2 | playback | … | further along same axis | ground plane + debris trail |
| 3 | playback | … | mid path, denser props | same horizon / light |
| 4 | playback | … | end of current chain | continuous diorama |
| 5 | reserve | (later) | further east / deeper | — |
| 6 | reserve | (later) | finale zone | — |

## Scene 1: …

- **eyebrow**: …
- **title**: …
- **body**: …
- **tags**: …
- **accent**: #…
- **scroll**: 1.6
- **linger**: 0.45
- **keyframe:** 1
- **arriving_via_leg:** — (start)
- **leaving_via_leg:** 0

…
