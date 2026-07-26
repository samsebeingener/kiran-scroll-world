# Scroll World — Pipeline Incident → Fix Contract

## Queue

`projects/scroll-world/<slug>/pipeline-fix-queue.md`

## When Fixic runs

1. **In-run:** QA `❌ BLOCKER` or Gate First Video hard fail after retry → Director appends INC → Task(`scroll-world-fixic`) → surgical durable fix + max +1 re-run of failed leg(s).
2. **Post-run:** open `status: open` incidents remain after PASS or terminal stop → Task(`scroll-world-fixic`).

## INC template

```markdown
## INC-YYYYMMDD-NN
status: open
run_date: YYYY-MM-DD
severity: P0 | P1
summary: …
evidence: …
suggested_files:
- `skills/…`
- `scripts/…`
```

## Fixic may change

- `skills/`, `agents/`, `shared/`, `scripts/`, `commands/`, `.env.example`
- `shared/agent-pipeline-pitfalls.md`

## Fixic must not change / commit

- Runtime `projects/scroll-world/**` media (PNG/MP4)
- Secrets / `.env`
- Unrelated plugins

After fix: set `status: fixed` (+ `fix_summary`, `files_changed`) or `needs-human`.
