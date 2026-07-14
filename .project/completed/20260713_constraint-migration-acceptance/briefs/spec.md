# Brief: Item 14 spec — Migration, Docs, and IFE Acceptance

You are the spec stage for Item 14, the closing item of the orchestrated CONSTRAINT-EXEC epic run. Repo: sysml-codegen, branch `constraint-exec-epic` (the item spans all three repos + fusion-tea; artifacts live here).

## Process constraints
- Work synchronously; never pause for background agents.
- Do NOT run `git commit` — the orchestrator commits.
- An Item 13 implement session is committing to this tree — write ONLY spec.md (+ CURRENT_WORK entry); touch no code.
- Artifact: `spec.md` in `.project/active/constraint-migration-acceptance/`.

## Provenance
- Concept (owner-ratified): Problem + Migration invariant + Validation Strategy (Acceptance). The epic's Critical Success Factor: "the IFE sweep's hand-coded viability rule is replaced by the generated assertion with every existing grid classification matching — and no modeled limit anywhere ends in silence."
- Epic Item 14: `.project/backlog/epic_constraint_execution.md`.
- Memories the epic names: Item-3 fusion-tea acceptance facts; plant-idiom fixtures.

## The run's accumulated handoff ledger (all recorded in the named items' artifacts — this item discharges them)
1. **The `gain` extraction gap (PREREQUISITE)**: `materialize_supplied_values` doesn't synthesize a top-level design-instance self-redefinition (Item 5 plan third pass; Item 8 spec). fusion_tea's Viability Threshold constraint cannot lower until fixed. Item 14's FIRST work: fix the gap, then re-land the two grandfathered fixtures (plant_values, fusion_tea) lowered, under their own gates (Item 8's GRANDFATHERED set shrinks to empty).
2. **Drop-manifest retirement**: every constraint in today's manifest maps 1:1 to a catalog source record (kept test); manifest + both blanket warnings delete; REQ-EXT-09-family tests re-anchor on the catalog.
3. **Docs across three repos**: authoring guidance flips from "constraints are not executable" to the executable profile + block list (incl. the real-equality → two-inequality idiom); architecture docs cover lowering phase, catalog, contracts, evaluator, study layer; verification-matrix rows under the register discipline (memory: verification-matrix drift modes).
4. **Acceptance**: regenerate the fusion-tea IFE package (lowered); replace the sweep harness's hand-coded viability rule with the generated assertion via the study layer (teax study CLI/API, Items 10–12); EVERY existing grid classification matches; record the cross-model prepare-once benchmark (S5 carry-forward (2)).
5. **Small recorded seams to sweep**: GENERATOR_MISMATCH second env axis (Item 9 audit — wire or document); teax loader seal verification wiring (Item 9 design D7 seam); tracking-key correlation docs note (Item 12 spec).

## Out of scope
New IFE modeling; performance tuning beyond recording the benchmark.

## Success criteria (from the epic)
- Migration mapping test green; grep finds no drop-manifest emission or blanket warning.
- IFE grid classifications match 100%; the hand-coded rule is deleted from the sweep harness.
- Docs updated in all three repos; epic Success Criteria checklist fully checkable.

## Environment
fusion-tea checkout: `~/1cfe/fusion-tea` (owner authorized modification). The IFE sweep harness + hand-coded rule live there (memory: Item-3 fusion-tea acceptance facts has the retirement grep scope + abs-path parity gotcha). License env: `env $(grep -v '^#' ~/1cfe/agentic-mbse/.env | xargs) uv run ...`.
