---
name: scroll-world-fixic
description: Fixic — durable plugin fixes from pipeline-fix-queue; surgical leg retry.
---

# Fixic

Контракт: `shared/pipeline-incident-fix-contract.md`.
Pitfalls: `shared/agent-pipeline-pitfalls.md`.

1. Читай `pipeline-fix-queue.md` (open INC текущего run)
2. Минимальный durable diff в plugin (`skills/`, `agents/`, `shared/`, `scripts/`, `commands/`)
3. Обнови pitfalls при общем уроке
4. Пометь INC `fixed` / `needs-human`
5. При seam/video P0 — допускается max +1 surgical re-run failed leg через video script (не полный рестарт)

Не коммить media / secrets / runtime projects.
Fragment: `fragments/fixic.md` с `incident_report:`.
