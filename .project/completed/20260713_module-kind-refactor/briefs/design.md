# Brief: Item 6 design — module_kind and the Generation-Seam Refactor

You are the design stage for Item 6 in the orchestrated CONSTRAINT-EXEC epic run. Repo: sysml-codegen, branch `constraint-exec-epic`.

## Process constraints
- Work synchronously; never pause for background agents.
- Do NOT run `git commit` — the orchestrator commits.
- Artifact: `design.md` in `.project/active/module-kind-refactor/`.

## Input
- Spec (committed, review-revised, orchestrator-accepted): `.project/active/module-kind-refactor/spec.md`. Its `[HARD]` requirements are fixed; its Open Questions are yours to decide and record.
- Spec review (context for what was contested): `.project/active/module-kind-refactor/spec-review.md`.
- S4 seam findings: `.project/active/spike-vertical-slice-constraint-execution/findings.md`.

## Design guidance (orchestrator, agent-grade)
- This is a byte-identity refactor: design for a mechanical, per-seam migration that a sonnet implement session can execute without judgment calls. Every seam's before/after dispatch shape should be spelled out.
- Decide and record the open questions: enum representation (recommend str-valued Enum for JSON friendliness — but verify against how ComputationGraph serializes today), fail-loud guard form/message, how far "structured output schema identity as graph data" goes in this item vs Item 7 (recommend: the minimal field Item 7 needs, defaulted so existing kinds are untouched byte-identically), byte-identity harness choice.
- Plan the migration order so the tree is never in a mixed state a test run can't interpret: models first, construction sites, seams, then test files + baselines in lockstep (the spec's lockstep note).
- The committed `computation_graph.json` baseline regeneration is an intentional, reviewable diff — design must say exactly what changes in those files (flag keys → module_kind key) so the implement stage's diff review is mechanical.
- A skeptical design_review follows; make dispatch-shape choices explicit with their rejected alternatives.
