# Brief: Item 8 plan — Snapshot v3

You are the plan stage for Item 8 in the orchestrated CONSTRAINT-EXEC epic run. Repo: sysml-codegen, branch `constraint-exec-epic`.

## Process constraints
- Work synchronously; never pause for background agents.
- Do NOT run `git commit` — the orchestrator commits.
- Artifact: `plan.md` in `.project/active/snapshot-v3/`.

## Input
Design rev 2 (committed): `.project/active/snapshot-v3/design.md` — three-key gate, mode enum, RecordingOccurrenceIndex, INV-7 ordering, grandfather set, rejection-test matrix, and the design's own de-risk-first note (constraint_multi_instance occurrence round-trip + constraint_id parity spike before corpus re-capture) are authoritative.

## Planning guidance (orchestrator, agent-grade)
- Implement runs on sonnet: mechanical phases, exact files (serializer, graph_rebuild, capture scripts), per-phase gates.
- Phase the de-risk spike FIRST as the design says (round-trip + ID parity on constraint_multi_instance) — it validates the whole occurrence-table bet before serializer surgery.
- Then: serializer + gates + mode enum with the full rejection-test matrix; then graph_rebuild offline lowering + parity tests (wi014_toy, constraint_multi_instance, constraint_inline); then the default flip (both surfaces together per the design) + grandfather set; then corpus re-capture per-fixture under the timestamp discipline with the expected-diff enumeration as the review checklist.
- Live tests via uv run pytest in-repo (stage-session env has working license). Corpus re-capture per-fixture, never blanket.
- Keep phases resumable from checkboxes.
