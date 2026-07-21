# Brief: Item 6 spec review — module_kind and the Generation-Seam Refactor

You are a fresh review session in the orchestrated CONSTRAINT-EXEC epic run. Repo: sysml-codegen, branch `constraint-exec-epic`. You did not write this spec; review it adversarially.

## Process constraints
- Work synchronously; never pause for background agents.
- Do NOT run `git commit` — the orchestrator commits.
- Artifact: `spec-review.md` in `.project/active/module-kind-refactor/`.

## Review target
`.project/active/module-kind-refactor/spec.md`.

## Context
- The stage brief the author received: `.project/active/module-kind-refactor/briefs/spec.md`.
- Owner-ratified concept: `.project/concepts/constraint-execution-and-design-space-studies-claude.md` (`PipelineModule` paragraph + Appendix B S4 seam findings).
- S4 findings: `.project/active/spike-vertical-slice-constraint-execution/findings.md`.
- Epic Item 6: `.project/backlog/epic_constraint_execution.md`.

## What this item must get right (weigh findings against these)
1. **Byte-identity is the acceptance gate.** The spec's claims about what regenerates byte-identically (generated packages) vs. what intentionally changes (committed `computation_graph.json` baselines) must be exactly right — verify the decoupling-from-Item-8 claim yourself (the author grepped extraction snapshots for the flags; check the grep is the right question, e.g. that snapshot *rebuild* paths don't reconstruct PipelineModule from serialized graph JSON in a way that makes the field version-relevant).
2. **Completeness of flag-consumer migration.** The spec lists the four S4 seams plus other consumers (`pipeline.py`, `test_gen.py`). Grep for every consumer of `is_computed_attribute`/`is_aggregation` yourself and check the list is complete — a missed consumer is exactly the silent mis-render this item exists to kill.
3. **Kind-space correctness.** Five kinds (calculation, formula, aggregation, constraint, report_aggregator) vs. today's two-flag space: is the mapping at the three graph_builder construction sites total and unambiguous? Is "formula" (computed attribute) the right reading of `is_computed_attribute`?
4. Constraint/report_aggregator kinds reaching a calc seam must fail loud, not mis-render (concept: silence is never an outcome).

Verdict format: must-fix list (each with why), nice-to-haves, overall verdict (Approved / Approved-with-must-fixes / Rework). Verify against code — do not take the spec's word.
