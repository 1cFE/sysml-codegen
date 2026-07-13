# Brief: Item 8 design review — Snapshot v3

You are a fresh review session in the orchestrated CONSTRAINT-EXEC epic run. Repo: sysml-codegen, branch `constraint-exec-epic`. You did not write this design; review it skeptically.

## Process constraints
- Work synchronously; never pause for background agents.
- Do NOT run `git commit` — the orchestrator commits.
- Artifact: `design-review.md` in `.project/active/snapshot-v3/`.

## Review target
`.project/active/snapshot-v3/design.md` (spec + briefs beside it).

## Ground truth
`snapshot/` (serializer, graph_rebuild, the v2 gate); `analysis/constraint_lowering.py` (lower_constraints signature — what it actually needs from occ_index); `analysis/part_instance_index.py` (occurrences_of semantics, AllOccurrencesResult.blocked); capture scripts; Item 5's plan notes (the 22-divergence measurement, hif_plant gain).

## What to probe hardest
1. **The frozen occurrence table's sufficiency.** Walk lower_constraints' actual use of occ_index: is per-owner occurrences_of the ONLY call (what about blocked-owner detection — D2 claims a per-owner query raises at capture so no blocked entry reaches a valid snapshot; but what about a model whose blocked-multiplicity def has an assert — does capture then fail entirely, and is that the right semantics vs. cataloging?)? Any second index consumer (Item 7's emission? future callers)?
2. **Determinism across capture/reload.** The occurrence table keyed by owner EQN: is its ordering pinned (sorted?) so constraint_id parity holds byte-identically? What happens if the live index and the frozen table disagree post-model-edit (staleness detection — is the existing snapshot-vs-model guard sufficient)?
3. **The marker semantics.** `constraint_lowering_mode: "grandfathered_off"`: who reads it, and can a NON-grandfathered v3 snapshot be loaded with lowering off (a third state?) — enumerate the full mode × section-present matrix and check every cell has defined behavior.
4. **Rejection completeness**: absent section → SnapshotFormatError; old version → existing gate. What about a v3 snapshot with facts but a MISSING occurrence table (partial section)? Torn/hand-edited snapshots?
5. **The de-risk spike**: is its pass/fail criterion concrete (round-trip + ID parity on constraint_multi_instance)?
6. **Corpus re-capture plan**: expected-diff classes enumerated per fixture class; the timestamp discipline; grandfathered pair unchanged — is the review procedure mechanical?

Verdict format: must-fix list (each with why), nice-to-haves, overall verdict (Approved / Approved-with-must-fixes / Rework). Verify against code — do not take the design's word.
