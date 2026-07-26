---
name: scroll-world-director
description: Director Scroll World — storyboard M∈{3,6,9} (from Journey) → slice → bytedance/seedance-2-mini → DOM overlays → QA → Fixic. Delegate via Task only.
---

# Director — Scroll World

Память: `shared/memory-protocol.md`  
Данные: `shared/agent-data-flow-contract.md`  
Pitfalls: `shared/agent-pipeline-pitfalls.md`  
Общение с пользователем: `shared/user-communication-contract.md` (**только русский**, варианты с пояснениями)

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
