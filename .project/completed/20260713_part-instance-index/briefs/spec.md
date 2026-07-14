# Brief: Item 4 — Part-Instance Index: Subtype Closure and Cardinality Expansion (spec stage)

You are one stage of the orchestrated CONSTRAINT-EXEC epic run. Repo: sysml-codegen, branch `constraint-exec-epic`.

## Process constraints
- Work synchronously. Never pause for background agents, never schedule check-backs.
- Do NOT run `git commit` — the orchestrator commits. Leave files in the working tree.
- Artifact: `spec.md` in `.project/active/part-instance-index/`.

## Provenance of what you're given
- The concept (`.project/concepts/constraint-execution-and-design-space-studies-claude.md`) is the owner-ratified design; its Required Invariants are settled.
- S3 spike result + review carry-forwards (concept Appendix B, S3 section) are verified agent-grade evidence — binding inputs; surface contradictions loudly, never resolve silently.

## Intent
Constraint lowering (Item 5) must find every concrete part instance — including instances of part definitions that own only constraints, no calculations. Today's instance discovery is driven by virtual calculation expansion, so a constraint-only definition may have zero discovered instances; S3 proved the miss live (a plain subtype inheriting the base constraint was invisible to the current lookup). This item builds the production index from part structure alone. It deliberately consumes no constraint fact schemas — it is pure part-structure analysis, which is why it can start before Items 1–2 land.

## Objective
Production part-structure-owned instance index: subtype closure over a source owner, retyped-path deduplication, concrete-cardinality expansion — independent of calc templates.

## Scope
1. One index derived from `PartUsage` structure and PartDefinition heritage: project a source owner over its subtype closure; deduplicate redefined/retyped paths; find constraint-only definitions' instances.
2. Fixed-multiplicity expansion **keyed by owning definition + feature** — S3 carry-forward (1): the probe keyed by bare leaf usage name and asserted the fixture has no collisions; production must key by `owning_part_def_qn` + feature or two same-named members with different counts collide.
3. Block parameterized, variable, ordered, and unbounded multiplicities with a named diagnostic (finite concrete cardinality required at lowering).

## Out of scope
- Constraint expansion itself (Item 5 consumes this index); virtual-calc instance discovery (unchanged for calcs).

## Success criteria (from the epic)
- S3's nine-instance fixture oracle: 9/9 found (including the plain subtype the current lookup misses), zero unexpected, with zero calculations in the model.
- Two same-named multiplicity members under different owners with different counts expand correctly (the collision case the probe asserted away).
- Non-finite cardinality blocks with a named diagnostic; index results deterministic across repeated loads.
- Existing corpus regenerates byte-identically (index addition must not disturb calc-driven discovery).

## Required reading
1. Concept "Concrete Lowering" instance-index sentences + Appendix B S3 result and carry-forwards.
2. `.project/active/spike-concrete-expansion-instance-index/findings.md` §1–2 (+ the committed probe and fixture model there — the fixture is promotable).
3. Current discovery path: how virtual calc expansion drives instance discovery today (start from `analysis/` and the S3 findings' code citations).
