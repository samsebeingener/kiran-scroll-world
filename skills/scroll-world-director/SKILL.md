---
name: scroll-world-director
description: Director Scroll World — storyboard M∈{3,6,9} (from Journey) → slice → bytedance/seedance-2-mini → DOM overlays → QA → Fixic. Delegate via Task only.
---

# Director — Scroll World

Память: `shared/memory-protocol.md`  
Данные: `shared/agent-data-flow-contract.md`  
Pitfalls: `shared/agent-pipeline-pitfalls.md`  
Общение с пользователем: `shared/user-communication-contract.md` (**только русский**, варианты с пояснениями)

## Gate после Journey (plain pitch)

После Journey — **STOP** по `04-journey-pitch.md`: показать пользователю plain Russian питч verbatim; варианты **Утвердить** / **Поправить**.  
Внутренний `04-budget.md` + meta (`frames`, `playback_chain`, `reserve`, `video_durations`) — не подменять питч техническим бюджетом.  
Без явного «Утвердить» — Storyboard не стартовать. См. `agents/director.md` §3.

Реестры камеры / трансформаций (для Journey и Video субагентов, не для текста питча пользователю):

- `shared/camera-movement-registry.md`
- `shared/object-transform-registry.md`
- `shared/cinematic-transition-contract.md`

## Цепочка

См. `agents/director.md`.

## Skills субагентов

| Role | Skill / playbook |
|------|------------------|
| intake | skills/scroll-world-intake |
| journey | skills/scroll-world-journey |
| storyboard | skills/scroll-world-storyboard |
| slicer | skills/scroll-world-slicer |
| video | skills/scroll-world-video |
| encoder | skills/scroll-world-encoder |
| builder | skills/scroll-world-builder |
| qa | skills/scroll-world-qa |
| fixic | skills/scroll-world-fixic |

Пользовательские команды: `/scroll-world-start`, `/scroll-world-run`.
