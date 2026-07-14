# Brief: Item 8 implement — Snapshot v3

You are the implement stage for Item 8 in the orchestrated CONSTRAINT-EXEC epic run. Repo: sysml-codegen, branch `constraint-exec-epic`.

## Process constraints
- Work synchronously; never pause for background agents or schedule check-backs.
- You ARE allowed to commit in this repo — you are the only session writing to this tree. Commit at each completed plan phase; check off plan.md checkboxes with implementation notes. End commit messages with: `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`.
- Do NOT touch `.project/` outside `.project/active/snapshot-v3/`.
- **License env (works from any shell here):** `env $(grep -v '^#' ~/1cfe/agentic-mbse/.env | xargs) uv run pytest ...` — the key lives in agentic-mbse/.env.

## Input — execute the plan
`.project/active/snapshot-v3/plan.md` (Phases 1–5, spike-first) is authoritative; `design.md` rev 2 holds the three-key gate, mode enum, RecordingOccurrenceIndex, INV-7 ordering, and the rejection-test matrix.

## Context landed since the plan was written
**Item 7 is CERTIFIED on this branch**: full constraint generation (modules, aggregator, catalog) exists and runs under real simkit with `lower_constraints_enabled=True`. Consequences for your phases:
- Phase 3's live/snapshot parity is now provable at the ARTIFACT level, not just graph/catalog — extend the parity assertion to generated packages (byte-identical artifacts, per the epic criterion this item owns).
- Phase 5's corpus re-capture happens exactly once, with Item 7's emission live — constraint-bearing fixtures will show facts + occurrences + lowered structure + generated constraint artifacts in their expected-diff classes.
- The suite baseline is 2236 passed / 4 skipped (with license env), mypy 76, ruff clean.

## Quality bar
- Phase 1 spike gates everything: occurrence round-trip + constraint_id parity on constraint_multi_instance before serializer surgery.
- The mid-epic red between Phases 2–5 is planned and loud — keep each phase's own targeted gates green and say plainly in commit messages which suite-level tests are expectedly red until Phase 5.
- The grandfathered pair (plant_values, fusion_tea) must show byte-identical baselines and the loud marker; every other fixture's diff must match an enumerated expected-diff class — record the per-fixture review in plan notes.
- Final gates: full suite green (license env), mypy 76, ruff clean, both rejection cases + mode-enum validation as kept tests, live/snapshot byte-identical artifacts for the clean constraint-bearing fixtures.
- If a gate fails and the fix is outside plan scope, STOP and report precisely.
