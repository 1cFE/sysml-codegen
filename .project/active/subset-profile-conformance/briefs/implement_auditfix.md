# Brief: /_my_implement — final-audit fixes for EXEC-SUBSET-CONTRACT Item 2a

Fix the final audit's findings (`.project/active/subset-profile-conformance/audit.md`, final section), then stop and report. Orchestrator rulings ([AGENT], 2026-10-19; record them in the plan's notes):

**Blockers**
1. `elaborate.py:684` (constraint association) and `graph.py:614` (graph integrity) are reached by corpus cases but recorded as reached by no model. Reclassify both, give each a site reason, witness and mutation (spec E3, E4), and fix their disagreement entries' stale reasons.
   - **Structural fix:** make it impossible to repeat. A site that any corpus case reaches (the tracer knows) may not carry an unreachable / internal-invariant disposition, and a reached public site must carry a reason. Add the test; show it fails on the pre-fix records.
   - `graph.py:614` firing on the valid model `candidate-es-002__part_inside_item_usage__attribute_value` likely means a generator defect. Add it to `rg1-recommendations.md` as a new candidate with a recommendation (a fix changes accept/refuse, so RG-1), and file a sysml-codegen backlog row citing the case. No generator change.
2. Complete `evidence/r3-closure.md` (the four missing R3 rows, spec C4) and `evidence/changed-outputs.md` (the Phase 2.4 message changes, design invariant 10).

**Advisories**
3. The ~20 disagreement entries the screen could likely judge from facts agentic-mbse already extracts: file one agentic-mbse backlog row (owner Reid Westwood) listing them, routed to epic Item 3, so they have a real home instead of "Item 3 or Item 5". Point the entries at that row.
4. Fix the ~6 mislabelled entries the audit lists.
5. Owner field honesty: record that resolutions were agent-assigned (e.g. a `decided_by` field or a schema-level statement the test checks). Pick the smallest honest change.
6. Fix the stale text in `modeling-assumptions.md`, `rg2-string-policy.md`, `rescan.md`.

Leave the RG-1 tensions (RG1-10, RG1-5) as they are; they are the owner's to weigh, but make sure the recommendations document states the tension plainly next to each.

After the fixes, if any agentic-mbse file under `src/agentic_mbse/sysml/` or `errors.py` changed, re-run the gate and commit a fresh receipt. Run the codegen subset suite, the agentic-mbse suite (all extras) and the phase gate's snapshot/oracle checks; compare with the baseline by test ID.

Repositories and rules: as in `briefs/implement_p2.md` (subset-conformance branches only; never push/merge; no RG-1 changes; check off and annotate). End with a short report and `ARTIFACT: <path>`.
