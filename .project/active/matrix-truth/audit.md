# Audit: Item 7 — REQ/Matrix Reconciliation (F2, F4, Divergent Rows)

**Verdict:** PASS
**Audited:** 2026-07-06
**Branch:** pipeline-truth-epic
**Commits:** 834695e, 812b3b9, 02fe0a3, 46d3e0e, 05ec41e, 39d621f

---

## Summary

Item 7 delivers what the spec, design, and both reviews require. The matrix now tells the
truth: no PASS row text asserts live usage of unwired code, the counts reconcile row-by-row,
the F4 verdict rests on named probe artifacts, and F2's restored ORCH-04 assertion actually
bites under the phase-order regression it exists to catch. I reproduced the two load-bearing
proofs myself — the ORCH-04 red-mutation (RED under the swap, GREEN reverted, src clean) and
the parity test run (23 passed) — and independently recounted the matrix (253 = 249 PASS + 4
UNTESTED + 0 PENDING, exactly the summary block). Every design-review binding resolution
(C1, C2, M3–M6) landed. No blocking findings. One cosmetic note below, not a defect.

## Findings

### Plan completion

All nine phases verified complete against the delivered artifacts.

- **Phase 0–2 (re-baseline, F4 atomic, cutover filing):** the F4 reframe is one atomic commit
  (834695e). IR-05 (matrix:288) and IR-07 (matrix:290) requirement **texts** are rewritten to
  capability claims ("`AGG_STRATEGIES` SHALL order…", "`resolve_input()`… SHALL resolve… the
  same channel the backtracker DFS resolves… parity-validated; not yet the live aggregation
  path") — a status re-label was correctly judged insufficient (C2). RES-02 (matrix:461) names
  the three live mechanisms and the live `_resolve_aggregation_input_channel`, deleting the
  dead-path name. The 22 skipifs in `test_input_resolver.py` stay (recount confirms 22, not the
  epic's un-recounted "24"). The parity parametrization is committed as
  `TestResolveInputParityExtended` (`test_dual_resolution.py:631`) and **runs green** (23
  passed) — the reframed rows cite a CI-running test, not the `.project/` probe (M6).
- **Phase 3 (F2 + ORCH-04):** REQ-OR-05/06/08 and doc-10 corrected to the real registrations.
  ORCH-04 restored as a genuine presence assertion over a hand-transcribed 3-alias list
  (`test_orchestrator.py:454-491`, INV-E-clean). **Red-mutation reproduced by the auditor**
  (see Code integrity). Both lying docstrings fixed.
- **Phase 4–6 (rows, untested, markers, xfails):** 9 divergent rows reframed; 4 UNTESTED rows
  each carry an inline argument; all 6 `# REQ-*` markers (BASE-05, BT-11, CA-10, LVP-09, OR-09,
  VBR-11) present in test source and cited by their rows; PGD-06 re-framed PENDING→UNTESTED-
  argued; AST-10 confirmed legit; xfail documented as one parametrized contract.
- **Phase 7–9 (doc fold-in, sweep, recount):** doc-23 staleness fix landed; sweep residue
  named (~46 rows); R4 table, discovery register, and memory note all produced/updated.

### Spec conformance

- **SC: F2/F4 closed by recorded decision; DOCS-SCRUB-F2/F4 + [ITEM7-PGD06] retired.** ✓
  All three marked RETIRED in `BACKLOG.md` (lines 131, 153, 355). Decisions live in the R4
  table, design, and D7 close-out — not just chat.
- **SC: F4 verdict via three probes, each a named artifact, one atomic change.** ✓ All four
  probe artifacts present under `probes/` (i/ii/iii + iv per M4); R4 table cites each by name;
  the consequence set moved in commit 834695e. INV-A grep is clean — no matrix row or doc
  03/04/05 asserts live `resolve_input`/`AGG_STRATEGIES` usage (the one DRA-02 grep hit is the
  reframed "not-yet-wired… the live path is `_resolve_aggregation_input_channel`" text itself).
- **SC: zero divergent-PASS rows remain.** ✓ EXT-09 and PGD-08 confirmed honest; CA-05,
  PY-01/03/05, GEN-02, SR-07, DM-06/07, GA-07 reframed to what the cited test checks (spot-
  checked GA-07 "asserted structurally, not measured" and SR-07 "skip behavior is not
  executed" against their rows — both honest).
- **SC: UNTESTED deliberately dispositioned; RES-02 rewritten.** ✓ 4 remain (DM-08, PGD-06,
  RES-05, RES-08), each carrying its argument; the three genuine gaps filed
  `[ITEM7-MATRIX-TEST-GAPS]`. RES-02 rewritten for the real architecture.
- **SC: recount matches row reality; footer corrected; markers added.** ✓ Auditor recount:
  253 rows = 249 PASS + 4 UNTESTED + 0 PENDING, matching the summary block exactly. Footer
  "57 distinct cited" verified — all 57 filenames resolve on disk; the "41 conformance + 16
  unit/integration" split reconciles exactly (6 cited filenames exist in both trees and are
  attributed to unit/integration: 47−6=41, 10+6=16). The 6 markers landed; PGD-08 correctly
  routed through the divergent disposition, not the marker path.
- **SC: 5 xfails decided.** ✓ Re-framed as one parametrized contract (`test_computed_
  attributes.py:787`, strict=False); classifier fix filed `[ITEM7-CLASSIFIER-FIX]`.
- **SC: suite green; baselines byte-identical; ruff/mypy ≤ 21/109.** ✓ Orchestrator-verified
  2069 passed / 4 skipped / 5 xfailed; ruff 17, mypy 104 (better than the 21/109 ceiling). No
  `src/` changed by the item (matrix/docs/tests only) — byte-identity trivially held (INV-D).
- **SC: R4 table produced; register updated in place.** ✓ `r4-verification-table.md` maps every
  finding → probe → CONFIRMED/NOT-REPRODUCED/RECLASSIFIED including the ORCH-04 red-mutation;
  the D7 close-out back-annotates each finding.

Non-goals respected: no F4 code cutover (filed), no classifier fix (filed), no Strategy D
feature work (delete deferred to cutover), no Item-6 test-body re-anchoring.

### Design conformance

- **INV-A** (no PASS text asserts live usage of unwired code): holds — grep clean.
- **INV-B** (no PASS pins less than its text; every UNTESTED carries its argument): holds for
  the dispositioned rows; the ~30 sweep-found "pins-narrower" rows are filed with per-row
  dispositions in `[ITEM7-MATRIX-SWEEP-RESIDUE]` under the leash (design-sanctioned).
- **INV-C** (counts reconcile to the recount): verified independently.
- **INV-D** (byte-identity / ruff-mypy ceiling): held.
- **INV-E** (no re-anchored test computes its own expectation): the ORCH-04 aliases are
  hand-transcribed constants; the parity test compares two independent resolution paths.
- **D1–D5** decisions all reflected in the delivered artifacts (LAND+split, fix-text, presence
  assertion, xfail re-frame, Strategy D rides the cutover). Cutover filing carries the M3
  comparand (`_resolve_aggregation_input_channel`), the M4 probe_iv EP-key evidence with
  concrete baseline line numbers, the fallback-gap list, and the Strategy-D deletion+docstring
  instruction — pickable cold.

### Code integrity

**ORCH-04 red-mutation reproduced (C1 — the review found the prior assertion vacuous).**
I applied the named mutation in `output_registry_builder.py` Phase 1a — swapped `register_scoped`
(line 183) and `register_alias` (line 186) so the alias registers before its canonical target.
`test_expected_key_a_aliases_present_solar_battery` turned **RED** (guard logged "possible phase
ordering violation" and dropped the aliases; all three expected aliases vanished). Reverting the
swap returned it to **GREEN**, and `git diff src/` is empty. The assertion bites the exact
phase-order regression the design specifies — it is not vacuous.

No slop or failure-honesty issues: this item ships no new production abstractions. The one
guarded fallback in scope (`register_alias`'s warn+skip on an unregistered target) is the
existing contract the presence assertion now pins, not a new silent default.

---

## Minor note (non-blocking)

- The Phase-6 completion note in `plan.md` records two marker filenames imprecisely (e.g.
  "VBR-11→test_cost_per_joule_wired_to_gamma"; the marker and its matrix citation are actually
  `test_spec_chain_twolevel.py`). The delivered artifacts are internally consistent
  (row ↔ marker ↔ test all agree); only the plan's prose note is loose. Cosmetic.

---

## Certification

Verified and marked:
- **Plan:** all 9 phases confirmed complete (checkboxes already set by implement; re-verified).
- **Spec:** all 7 success criteria verified met and marked.
- **Epic:** Item 7 / SC-F — the item's own criteria are met; marked. (Epic-wide certification is
  the epic-scope audit's job once sibling items settle.)

Checks performed with execution: INV-A grep (matrix + docs), IR-05/07 text inspection, parity
test run (23 passed), 22-skipif recount, ORCH-04 presence-assertion read + **red-mutation
reproduce/revert**, independent matrix recount (253/249/4/0), 57-file citation resolution +
split reconciliation, cutover/sweep-residue/test-gaps/classifier filings read, three retirements
confirmed, 6-marker presence, 5-plus-2 divergent/reframe spot-checks, PGD-06 breadcrumb
resolution (no PENDING rows remain), D7 close-out and memory-note updates confirmed.

ARTIFACT: .project/active/matrix-truth/audit.md
