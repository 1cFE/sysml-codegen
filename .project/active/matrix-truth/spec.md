# Spec: Item 7 — REQ/Matrix Reconciliation (F2, F4, and the Divergent Rows)

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-07-06
**Complexity:** HIGH
**Branch:** pipeline-truth-epic
**Epic:** PIPELINE-TRUTH, Item 7 (SC-F)

---

## Problem

The verification matrix is supposed to be the one place a reader can trust: every
`REQ-*` tag maps to a conformance test that actually pins the requirement. Today it
claims more than it verifies, in specific and enumerated places. Discovery's D7 sweep
found the divergences; this item closes them.

The failures are not uniform. They fall into seven groups, worst first.

**1. F4 — the whole Input Resolver family pins dead code.**
- *The claim.* `resolve_input()` / `AGG_STRATEGIES`
  (`src/sysml_codegen/resolution/input_resolver.py`) have **zero production callers** —
  verified: the only `src/` references are inside the module that defines them. The live
  aggregation path is `_resolve_aggregation_input_channel` (`graph_builder.py:1194`).
- *What the matrix claims anyway.* The 7 IR rows (REQ-IR-01..07) read PASS, pinned by 22
  skipif-gated tests in `test_input_resolver.py` (recount at implement) that call the
  bypassed function directly. REQ-DRA-02/04/05 partly pin it too — DRA-04 compares the
  live backtracker against a function that never runs. REQ-RES-02 names the dead path in
  its text.
- *Why it's stuck, not a deletion call.* Docs 03/04/05 present `resolve_input()` as the
  **intended** consolidated architecture with recorded rationale (doc 03's "What Changed
  vs. What Stayed" table; doc 04's whole existence). Git-verified: the module and its
  call site were born in one COST-PATTERN commit (`d6c725f`); only the final rewire of
  the factory call sites was skipped, so it replaced nothing and nothing broke. The
  matrix, the code, and the docs disagree about whether this module is the architecture
  or a corpse.

**2. F2 — the registry contract text contradicts the code, and a test was weakened to
hide it.**
- *The contradiction.* REQ-OR-05/08 and doc 10's "Eliminated Key Formats" say Key_A and
  Key_F are never registered. The code registers both: Phase 1a registers Key_A via
  `register_alias()`, Phase 1c registers Key_F via `register_scoped()`; Phases 3–4 also
  consult a construction-time `instance_attr_to_channel` Key_A-format dict before typed
  lookups (vs REQ-OR-06's "through typed lookup").
- *Why the rows still read PASS.* `test_output_registry.py::TestReqOR08` narrowed its own
  reading (an inline NOTE in the matrix admits it consciously), and REQ-ORCH-04's
  phase-order assertion was weakened to `min(phase1) < min(alias)` (first-call-only) to
  accommodate the divergence. Two test docstrings misstate their own bodies.

**3. Divergent-PASS rows — PASS that pins less than the text.** The D7 list: REQ-CA-05
(vacuous on empty coverage), REQ-PY-01/03/05 (blacklist / rebuilt-map weaknesses),
REQ-GEN-02 (CalcUsage-only, in-memory, no filesystem check), REQ-SR-07 (source-text
grep, no behavior), REQ-DM-06/07 (test something categorically different), REQ-GA-07
(identifier grep), REQ-PGD-08 (cited file doesn't cover the claim), REQ-EXT-09's
part-usage-owner leg. Two of these have moved since the D7 sweep and must be re-verified
against the **current** matrix row before acting, not treated as settled:
- **REQ-EXT-09** — Item 4 landed the part-usage leg (`test_extractor.py:888-934`, a new
  anti-pattern-free class spanning calc-def / part-def / part-usage owners). This leg is
  DONE; confirm and mark at implement.
- **REQ-PGD-08** — its row now cites `test_matcher_fixes_item7.py` (backtracker
  propagation) + `test_parameter_group_deriver.py`, both post-dating the D7 verdict.
  Re-verify coverage against that current row. One disposition (this resolves the §5
  double-listing too): if real coverage is absent, the row needs a genuine test or a
  re-frame — **not** a marker, since you cannot tag a test that does not pin the claim.
  Decided at implement on fresh evidence.

**4. UNTESTED-12 undispositioned.** Twelve rows carry `— | UNTESTED`. Some are
risky-cheap to convert (REQ-CA-08, REQ-GEN-07); one is the riskiest row in the item
(REQ-RES-08, a cross-cutting scoping claim, now has Item 1's cross-part fixtures as
substrate); REQ-RES-02 names the dead F4 path and must be rewritten; RES-01/03/04/05/06
discharge by cross-citing component tests; REQ-DM-08 is a static check; REQ-GEN-03
cross-cites. None carry an argument for why they stay untested.

**5. Marker hygiene and a count that already lies.** Recount from rows (not the summary
block, per the memory note) surfaces live drift:
- The summary says **248 total / 236 PASS / 12 UNTESTED**. The file has **249 REQ
  rows** — 236 + 12 = 248 leaves the **REQ-PGD-06 PENDING-ITEM7 row (matrix:380)
  uncounted**. Its status is neither PASS nor UNTESTED.
- The footer says **"33 test files"**; `tests/conformance/` holds **57**. The index's
  "54 distinct test files cited" is a third, different number. 9 cited files live
  outside `tests/conformance/`, straining the matrix's own PASS definition.
- D7 named 7 PASS rows with no REQ marker binding row→test. **Six get markers**
  (BASE-05, BT-11, CA-10, LVP-09, OR-09, VBR-11): their matrix test-file cells are
  populated; the missing piece is the `# REQ-*` tag in the test **source** that the
  traceability generator greps — verify and add. **PGD-08 is excluded here** and routed
  through the §3 divergent-row disposition instead: D7 found it has neither a marker nor
  real coverage, so a marker cannot be added to a test that does not pin the claim. It
  needs a genuine test or a re-frame (decided at implement, §3).

**6. The 5 xfails lock a misclassification in as "expected."** `test_computed_attributes.py:787`
xfails an inherited-attr classification (EXPOSE_COMPUTED where FORMULA is correct; a
supertype-namespace QN defeats the Step-2b prefix check). Companion tests pin the wrong
behavior as expected. The epic carries this as an explicit fix-vs-reframe decision.

**7. ~175 PASS rows were never deep-read.** Discovery triaged all 248 rows but
deep-read only ~35. The rest are asserted PASS on the traceability check alone. Item 7
completes the sweep with the D7 heuristics (strong-word REQs, diagnostics, structural
counts).

Two prior epics staged this: UPSTREAM-FINDINGS left F2/F4 as filed residue
(DOCS-SCRUB-F2/F4), and this epic's own Item 8 deleted `get_default_value` (firing
[ITEM7-PGD06]) and added REQ-AST-10. The matrix is the last artifact standing between
"the code is the truth" and a reader who believes a green row.

## Success Criteria

- [x] **F2 and F4 closed by recorded decision.** BACKLOG DOCS-SCRUB-F2, DOCS-SCRUB-F4,
  and [ITEM7-PGD06] retired. The decision and its evidence live in the docs, not just
  in chat.
- [x] **The F4 verdict is reached by running the three kill-condition probes**, each of
  which produces a named evidence artifact the verdict cites (see the HARD-F4 block), and
  whichever outcome lands, the full consequence set moves in **one change**: the 7 IR
  rows, REQ-DRA-02/03/04/05, REQ-BT-09, REQ-RES-02/07/08 text, the 22
  `test_input_resolver.py` skipifs (recount at implement), `test_dual_resolution.py`, and
  docs 03/04/05 prose all end mutually consistent. No row pins a module the code doesn't
  call; no doc describes an architecture the code doesn't have.
- [x] **Zero divergent-PASS rows from the D7 list remain.** Each is fixed (test
  strengthened or REQ re-framed) or, if it surfaces new feature work, filed with a
  matrix pointer. No PASS row pins less than its text.
- [x] **UNTESTED count deliberately dispositioned.** Target: ≤ the rows argued
  untestable-as-written, each carrying its argument in the matrix. REQ-RES-02 rewritten
  for the real architecture.
- [x] **Matrix recount matches row-by-row reality.** Total/PASS/UNTESTED/PENDING counts
  reconcile to the actual rows (the 249-vs-248 gap closed); the footer file count is
  correct or the PASS definition is re-framed honestly; the 7 missing row→test markers
  added.
- [x] **The 5 xfails decided** (fix classifier or re-frame REQ + document as contract);
  no xfail silently carried.
- [x] **Suite green; baselines byte-identical.** Any code touched (F2 fix, an F4
  cutover, a Strategy D dedup) keeps existing baselines byte-identical or lands as a
  reviewed capture-script diff (SC-G / R3). ruff/mypy not worse than the 21/109
  baseline.
- [x] **The R4 verification table is a produced artifact** (finding → probe →
  CONFIRMED / NOT-REPRODUCED / RECLASSIFIED), and the discovery register is updated in
  place for the F2/F4/divergent findings this item confirms or strikes.

## Known Requirements

- **[HARD]** R4 protocol is mandatory for this item (the epic names Item 7 as a
  verification-table producer). For every finding picked up: read the component's
  reference doc + REQ rows for intent first; reproduce with a failing test or live
  probe before fixing; fix per family at the cleanest choke point; close the docs loop
  (reference doc + matrix + register) in the same change — including deleting intent
  prose on a re-frame so the next reader inherits no ghost architecture.

- **[HARD]** F4 lands as an atomic, mutually-consistent change across its whole
  consequence set. The set is fixed regardless of outcome: 7 IR rows (REQ-IR-01..07),
  REQ-DRA-02/03/04/05, REQ-BT-09, REQ-RES-02/07/08 text, the 22 skipifs in
  `test_input_resolver.py` (recount at implement — the epic's "24" was never recounted;
  the count adds no precision since the set is "all of them"), `test_dual_resolution.py`
  (the parity suite), and the REQ-mirroring prose in docs 03/04/05. DRA-03 and BT-09 are
  in the set because they **also cite `test_dual_resolution.py`** (`matrix:166`,
  `matrix:120`): either outcome rewrites or removes that file (cutover deletes the inline
  comparand; excise deletes the module), so a citation left behind dangles. A partial
  move (rows without docs, docs without skipifs, or a moving test file with a stale
  citation) fails.

- **[HARD]** Each F4 kill probe produces a **named evidence artifact** that the
  design-time verdict must cite by name. This is the guard against the presumption
  winning by inertia: the verdict rests on evidence a reviewer can open, not on a design
  agent waving a soft probe through. Presumption stays "land the cutover (a)"; it flips
  to excise (b) only if a probe fires a kill.
  - **Probe (i) — parity extended.** Extend the `test_dual_resolution.py` parity suite
    over an **enumerated** fixture set: `plant_values`, `plant_value_shapes`, and the
    extended `spec_chain_twolevel` (Item 1's landed fixtures; no open-ended "shapes
    beyond the corpus" hole). The suite runs and passes **before** any factory call site
    is rewired. *Artifact:* the extended parity run log. *Pass bar / kill:* 100% parity
    on the extended corpus; any per-fixture value-or-wiring disagreement is a kill (the
    module has diverged from the live path's correctness).
  - **Probe (ii) — Strategy D dedup.** Implement-or-delete Strategy D
    (`DesignAttributeLookup`, a documented no-op at `input_resolver.py:208`) explicitly;
    its promised aggregation-EP dedup churns params-JSON key sets. *Artifact:* the actual
    key-set diff computed against the `catf_mfe` and `solar_battery` params-JSON
    baselines, plus a one-paragraph behavior-change review. *Kill:* the diff collapses
    keys a consumer depends on, or the review judges the change otherwise unwanted.
  - **Probe (iii) — module drift.** Diff `input_resolver.py` against the live
    `_resolve_aggregation_input_channel` path **both directions**. *Artifact:* a
    commit-list comparison — the inventory of live-path fixes landed since the module's
    COST-PATTERN birth (`d6c725f`). *Threshold / kill:* any post-COST-PATTERN live-path
    fix absent from the module counts as material drift (a kill).
  - The design-time F4 verdict cites all three artifacts.

- **[HARD]** F2 lands by **fixing the text to the code** (orchestrator ruling). The
  inline matrix NOTE admits the Key_A/Key_F divergence consciously; construction-time
  registration is corpus-proven; and — unlike F4 — no parity suite proves a typed-lookup
  alternative was ever built. So REQ-OR-05/06/08 text and doc 10's "Eliminated Key
  Formats" are corrected to describe the actual registrations (Phase 1a Key_A alias,
  Phase 1c Key_F scoped, the construction-time `instance_attr_to_channel` consult). The
  presumption flips to fixing the *code* only if design finds the construction-time dict
  genuinely bypasses the typed-registry validation contract — check `output_registry.py`'s
  guards at design. **Non-negotiable either way:** REQ-ORCH-04's real phase-order
  assertion is RESTORED (the `min(phase1) < min(alias)` weakening was accommodation, not
  intent), and the two test docstrings that misstate their own bodies are fixed.

- **[HARD]** The ~175-row deep-read sweep is leashed, not open-ended (the item budgets
  1.5–2 days total). Concrete D7 heuristics — a row qualifies for deep-read if: its text
  contains a strong word (SHALL / ALL / every / never / exactly), OR it asserts a
  diagnostic fires (a warning/error on a shape), OR it asserts a structural/numeric count.
  Stopping rule: sweep until EITHER the qualifying list is exhausted OR 0 new findings in
  40 consecutive rows after the first 60 examined. Whatever stays unswept is **named in
  the close-out with its count** (register discipline — silent truncation reads as "swept
  everything"). Findings are fixed or filed with a matrix pointer.

- **[HARD]** REQ-PGD-06 (matrix:380, `PENDING-ITEM7 · [ITEM7-PGD06]`): Item 8 confirmed
  `get_default_value` dead and deleted it (verified: zero hits in `src/` and `tests/`),
  landing the doc-17 re-frame. Item 7 re-frames or retires the matrix PASS row (its
  pinning tests are gone) and confirms REQ-PGD-08's `get_default_value` mention (doc-17
  `:28`) was cleared. **[HARD]** REQ-AST-10 (added by Item 8, verified by
  `test_agg_literal_dispatch.py`) is a legitimate new row — the reconciliation sweep
  must not treat it as an orphan.

- **[HARD]** Byte-identity discipline (R3 / SC-G): the matrix is mostly documentation,
  but F2 may touch code (REQ-ORCH-04's real assertion, the registry contract), and F4
  (a) touches an executable path. Every code touch keeps existing corpora
  byte-identical or lands via `scripts/capture_*.py` with a reviewed diff.

- **[HARD]** R1-addition anti-pattern ban: any test this item re-anchors carries an
  independently-anchored expectation (never one computed by the code under test). Item 7
  must not reintroduce the REQ-EXT-09 anti-pattern in the rows it strengthens.

- **[NEED]** After this item, a reader who sees a PASS row can trust that a test pins
  the requirement's actual claim, that the counts add up, and that no green row is
  propped up by a weakened assertion or a dead-code pin.

- **[INFERRED]** The summary block, footer file count, and index counts are **derived**
  and are reconciled to row reality last — recount from rows (memory note
  `verification-matrix-drift-modes`), then regenerate the derived numbers to match.

- **[INFERRED]** Rows owned by concurrently-implementing Items 2 and 5 will move
  (whole-plant resolution changes IR/RES/LVP-adjacent rows; silent-failure hardening
  adds diagnostics with their own rows). Note which rows are theirs and re-verify the
  divergent/untested lists at implement start rather than fighting their churn.

## Non-Goals

- **New feature work surfaced by a re-framed REQ.** If re-framing a row exposes a real
  gap (the likeliest is the inherited-attr classifier behind the 5 xfails), file it with
  a matrix pointer; do not build it here.
- **The self-referential test fixes.** Item 6 owns the 25 flagged tests (including
  REQ-REG-02's mis-anchor and the MF-07 pass-or-skip). Item 7 owns the matrix rows, not
  the test-body re-anchoring, except where a divergent-PASS row's fix is a
  matrix/REQ-text change.
- **Constraint serialization / the from-snapshot constraint report.** Item 4's decision.
- **The Strategy D dedup as a new capability** beyond honoring documented intent —
  implement-or-delete only, not a feature expansion.
- **Deletion of dead symbols other than the F4 module** — Item 8's scope.

## Open Questions / Deferred to design

- **The F4 verdict itself.** Presumption, per the epic: **land the cutover (a)** — the
  design rationale was deliberate, doc 24 defines the structural boundary it honors
  (post-DFS resolution is consolidatable), the 12-test parity suite is the safety net,
  and excising enshrines the less-clean inline implementation at greater doc-surgery
  cost. The verdict is **recorded at design, after the three kill-condition probes run
  and produce their named artifacts** (parity run log; Strategy-D key-set diff vs
  catf_mfe/solar_battery; module-drift commit-list), which the verdict cites. The
  parity-suite extension is testable now, over Item 1's fixtures. This spec fixes the
  presumption, the probes, and the artifacts; design fixes the answer.
- **Whether the cutover splits into its own item.** The epic budgets Item 7 at 1.5–2
  days and allows design to split the F4 cutover out if it grows past that. Decide at
  design once the both-directions diff sizes the rewire.
- **The 5 xfails: fix vs re-frame.** Recommendation: **re-frame** — the
  misclassification produces a *loud* EXPOSE_COMPUTED rejection (not silent wrong
  output), no fusion-tea model hits it, and the classifier fix (supertype-namespace QN
  vs the Step-2b prefix check) is out of proportion to a matrix-truth item. Re-frame the
  REQ + document the xfails as a known contract, and file the classifier fix as its own
  backlog item. Confirm at design.
- **F2 is no longer open — presumption fix-text-to-code (orchestrator ruling), see the
  HARD requirement above.** The one thing design still checks: does the construction-time
  `instance_attr_to_channel` dict genuinely bypass the typed-registry validation contract
  (`output_registry.py`'s guards)? If yes, the presumption flips to fixing the code; if
  no (the expected case), the text is corrected to describe the registrations. ORCH-04's
  assertion is restored and the two lying docstrings fixed regardless.
- **Per-row disposition of the ~175 unswept PASS rows.** The sweep runs at implement
  under the leash (concrete heuristics + the 40-in-60 stopping rule, see the HARD
  requirement). What it finds is fixed or filed; the unswept residue is named with its
  count in the close-out. The exact findings cannot be known until the sweep runs — the
  leash bounds the effort regardless.

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_pipeline_truth.md` (Item 7 full section; R1/R4; SC-F)
- **Required Reading:**
  - `.project/research/20260706_pipeline-truth-discovery.md` §D7 (matrix truth), §D5
    (cleared non-findings), adversarial pass
  - `docs/architecture/verification-matrix.md` (the artifact under repair)
  - `docs/architecture/reference/10-output-registry.md` (F2)
  - `docs/architecture/reference/03-resolution-overview.md`,
    `04-input-resolver.md`, `05-module-factory.md` (F4 intent prose — deliberately left
    pending this reconciliation)
  - `tests/conformance/test_input_resolver.py` (22 skipifs, recount at implement),
    `test_dual_resolution.py`
    (the 12-test parity suite)
  - BACKLOG: DOCS-SCRUB-F2, DOCS-SCRUB-F4, [ITEM7-PGD06]
  - memory notes `verification-matrix-drift-modes`, `verify-then-fix-protocol`
- **Landed-state to re-verify at implement start:** Item 4 (REQ-EXT-09 part-usage leg),
  Item 6 (REQ-REG-02 re-anchor; factory-count recount), Item 8 (`get_default_value`
  deleted ✓, REQ-AST-10 added ✓, matrix:380 breadcrumb ✓), Items 2/5 (moving rows).
- **Design:** `.project/active/matrix-truth/design.md` (to be created)

---

**Next Steps:** After approval, proceed to `/_my_design` — where the three F4
kill-condition probes run (parity-suite extension over Item 1's fixtures first) and the
F4 verdict is recorded.
