---
name: scroll-world-qa
description: QA seams, scrub, overlays, responsive for Scroll World.
---

# QA

Чеклист:

- [ ] M−1 encoded legs present; scrub seeks without stall
- [ ] Seams: hard cut between legs, no white flash (`shared/seam-playback-contract.md`)
- [ ] Boundary frames same resolution as encoded scrub; posters from `*-leg-*-first.png`
- [ ] Overlays appear in planned ranges; CTA on last scene
- [ ] No baked text in media
- [ ] Legs look cinematic (camera travel / object transform) — not still-to-still crossfade
- [ ] Journey has Transition plan; video prompts cite transition types
- [ ] Responsive / reduced-motion OK
- [ ] No wrong model slug in logs (only gpt-image-2-text-to-image / gpt-image-2-image-to-image / bytedance/seedance-2-mini)
- [ ] Panel frames share media_aspect_ratio with Seedance legs
- [ ] video_resolution default path is 480p unless user chose 720p
- [ ] video_duration in 4–8 (default 4)

При fail P0 → `❌ BLOCKER` + INC в `pipeline-fix-queue.md`.
Fragment: `fragments/qa.md`.
