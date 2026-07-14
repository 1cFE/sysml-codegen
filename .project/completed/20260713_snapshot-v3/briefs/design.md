# Brief: Item 8 design — Snapshot v3

You are the design stage for Item 8 in the orchestrated CONSTRAINT-EXEC epic run. Repo: sysml-codegen, branch `constraint-exec-epic`.

## Process constraints
- Work synchronously; never pause for background agents.
- Do NOT run `git commit` — the orchestrator commits.
- Artifact: `design.md` in `.project/active/snapshot-v3/`.

## Input
- Spec (committed): `.project/active/snapshot-v3/spec.md` — the grandfather carve-out, facts+occurrences serialization, rejection semantics, and default-flip responsibilities are fixed; its Open Questions (offline part-instance-index shape, two-flip-surface coordination, present-empty-vs-absent encoding) are yours to decide and record.
- The snapshot machinery: `snapshot/` (serializer, graph_rebuild, the v2 hard-gate), `scripts/capture_pipeline_baselines.py` + the capture scripts; Item 5's lowering + flag; Item 1's serialize/parse (`constraint_facts.py` via the editable install or `.project/reference/agentic-mbse-landed/`).

## Design guidance (orchestrator, agent-grade)
- The offline index question: prefer serializing the resolved occurrence list (instance_path + owning-def/feature keys + blocked set) captured at snapshot time from the live index — it is small, deterministic, and avoids rebuilding subtype closure offline. Reject-with-reasons if you find a better shape.
- Design the flip precisely: which call sites flip (build_pipeline_context default; graph_rebuild's new lowering step), the grandfather mechanism (per-fixture capture flag? exclusion list in the capture script? — pick the one that is loud in the artifacts), and the parity test fixture set (wi014_toy + constraint_multi_instance + constraint_inline).
- Rejection semantics reuse the existing v2 hard-gate idiom — cite it.
- Corpus re-capture plan: per-fixture, timestamp-churn discipline, with the expected-diff classes enumerated (constraint-bearing fixtures gain facts section + lowered structure; constraint-free gain facts section only — or absent-encoding per your OQ decision; grandfathered two unchanged).
- A skeptical design_review follows; make serialization shapes and flip mechanics explicit with rejected alternatives.
