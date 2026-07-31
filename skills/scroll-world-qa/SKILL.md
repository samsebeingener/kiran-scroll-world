---
name: scroll-world-qa
description: QA seams, scrub, overlays, responsive for Scroll World.
---

# QA

Чеклист:

- [ ] Encoded legs present: **K − 1** when `playback_chain` set (else M − 1); scrub seeks without stall
- [ ] If `playback_chain` set: reserve frames may exist on board, but scrub sections = **legs only** (K − 1 clips)
- [ ] Seams: hard cut between legs, no white flash (`shared/seam-playback-contract.md`)
- [ ] `assets/seam-compatibility.json` fresh (после последнего encode; новее всех `assets/encoded/*-leg-*.mp4`), verdict без REVIEW; exit code 2 от `check_seam_compatibility.py` → `❌ BLOCKER`
- [ ] Boundary frames same resolution as encoded scrub; posters from `*-leg-*-first.png`
- [ ] Overlays appear in planned ranges; CTA on last scene
- [ ] No baked text in media
- [ ] Legs look cinematic (camera travel / object transform) — not still-to-still crossfade
- [ ] Journey has **Transition plan** + `camera_moves` / `object_transform_code` on legs
- [ ] Responsive / reduced-motion OK
- [ ] No wrong model slug in logs (only gpt-image-2-text-to-image / gpt-image-2-image-to-image / bytedance/seedance-2-mini)
- [ ] Panel frames share media_aspect_ratio with Seedance legs
- [ ] video_resolution default path is 480p unless user chose 720p
- [ ] `video_duration` / per-leg `duration_sec` in **4–15** (required, from journey — no default)

## WARN (не BLOCKER)

- [ ] `comfort_sec` mismatch vs chosen transform / camera (registry soft warn) — **WARN only**, adapt mechanic; do not hard-fail QA

При fail P0 → `❌ BLOCKER` + INC в `pipeline-fix-queue.md`.
Fragment: `fragments/qa.md`.
