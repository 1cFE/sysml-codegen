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

**1. F4 — the whole Input Resolver family pins dead code.** `resolve_input()` /
`AGG_STRATEGIES` (`src/sysml_codegen/resolution/input_resolver.py`) has **zero
production callers** — verified: the only references in `src/` are inside the module
that defines them. The live aggregation path is `_resolve_aggregation_input_channel`
in `resolution/graph_builder.py:1194`. Yet the 7 IR rows (REQ-IR-01..07) read PASS,
pinned by 24 skipif-gated tests in `test_input_resolver.py` that call the bypassed
function directly, and REQ-DRA-02/04/05 partly pin it too (DRA-04 compares the live
backtracker against a function that never runs in production). REQ-RES-02 names the
dead path in its text. This is not a dead-code-deletion call: docs 03/04/05 present
`resolve_input()` as the **intended** consolidated architecture with recorded design
rationale (doc 03's "What Changed vs. What Stayed" table; doc 04's whole existence).
Git-verified: the module and its call site were born in one COST-PATTERN commit
(`d6c725f`); only the final rewire of the factory call sites was skipped, so it
replaced nothing and nothing broke. The matrix, the code, and the docs disagree about
whether this module is the architecture or a corpse.

**2. F2 — the registry contract text contradicts the code, and a test was weakened to
hide it.** REQ-OR-05/08 and doc 10's "Eliminated Key Formats" say Key_A and Key_F are
never registered. The code registers both: Phase 1a registers Key_A via
`register_alias()`, Phase 1c registers Key_F via `register_scoped()`; Phases 3–4 also
consult a construction-time `instance_attr_to_channel` Key_A-format dict before typed
lookups (vs REQ-OR-06's "through typed lookup"). The rows read PASS because
`test_output_registry.py::TestReqOR08` narrowed its own reading (an inline NOTE in the
matrix admits it), and REQ-ORCH-04's phase-order assertion was weakened to
`min(phase1) < min(alias)` (first-call-only) to accommodate the divergence. Two test
docstrings misstate their own bodies.

**3. Divergent-PASS rows — PASS that pins less than the text.** The D7 list: REQ-CA-05
(vacuous on empty coverage), REQ-PY-01/03/05 (blacklist / rebuilt-map weaknesses),
REQ-GEN-02 (CalcUsage-only, in-memory, no filesystem check), REQ-SR-07 (source-text
grep, no behavior), REQ-DM-06/07 (test something categorically different), REQ-GA-07
(identifier grep), REQ-PGD-08 (cited file doesn't cover the claim), REQ-EXT-09's
part-usage-owner leg (Item 4 may have landed it — verify).

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
- D7 named 7 PASS rows with no REQ marker binding row→test (BASE-05, BT-11, CA-10,
  LVP-09, OR-09, PGD-08, VBR-11). Their matrix test-file cells are populated; the
  missing marker is the `# REQ-*` tag in the test **source** that the traceability
  generator greps. Verify and add.

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

- [ ] **F2 and F4 closed by recorded decision.** BACKLOG DOCS-SCRUB-F2, DOCS-SCRUB-F4,
  and [ITEM7-PGD06] retired. The decision and its evidence live in the docs, not just
  in chat.
- [ ] **The F4 verdict is reached by running the three kill-condition probes**, and
  whichever outcome lands, the full consequence set moves in **one change**: the 7 IR
  rows, REQ-DRA-02/04/05, REQ-RES-02/07/08 text, the 24 `test_input_resolver.py`
  skipifs, `test_dual_resolution.py`, and docs 03/04/05 prose all end mutually
  consistent. No row pins a module the code doesn't call; no doc describes an
  architecture the code doesn't have.
- [ ] **Zero divergent-PASS rows from the D7 list remain.** Each is fixed (test
  strengthened or REQ re-framed) or, if it surfaces new feature work, filed with a
  matrix pointer. No PASS row pins less than its text.
- [ ] **UNTESTED count deliberately dispositioned.** Target: ≤ the rows argued
  untestable-as-written, each carrying its argument in the matrix. REQ-RES-02 rewritten
  for the real architecture.
- [ ] **Matrix recount matches row-by-row reality.** Total/PASS/UNTESTED/PENDING counts
  reconcile to the actual rows (the 249-vs-248 gap closed); the footer file count is
  correct or the PASS definition is re-framed honestly; the 7 missing row→test markers
  added.
- [ ] **The 5 xfails decided** (fix classifier or re-frame REQ + document as contract);
  no xfail silently carried.
- [ ] **Suite green; baselines byte-identical.** Any code touched (F2 fix, an F4
  cutover, a Strategy D dedup) keeps existing baselines byte-identical or lands as a
  reviewed capture-script diff (SC-G / R3). ruff/mypy not worse than the 21/109
  baseline.
- [ ] **The R4 verification table is a produced artifact** (finding → probe →
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
  REQ-DRA-02/04/05, REQ-RES-02/07/08 text, 24 skipifs in `test_input_resolver.py`,
  `test_dual_resolution.py` (the 12-test parity suite), and the REQ-mirroring prose in
  docs 03/04/05. A partial move (rows without docs, or docs without skipifs) fails.

- **[HARD]** If F4 lands as the cutover (a), three preconditions gate the swap, in
  order: (1) extend the `test_dual_resolution.py` parity suite over Item 1's plant
  fixtures and any shapes beyond the committed corpus, and it must pass **before** the
  factory call sites are rewired; (2) implement-or-delete Strategy D
  (`DesignAttributeLookup`, a documented no-op at `input_resolver.py:208`) explicitly —
  its promised aggregation-EP dedup churns params-JSON key sets, so it lands with
  reviewed baselines; (3) diff `input_resolver.py` against the live
  `_resolve_aggregation_input_channel` path both directions to confirm the module
  carries every post-COST-PATTERN / UPSTREAM-FINDINGS fix the live path got.

- **[HARD]** The three F4 kill conditions each have a defined test, and the verdict
  turns on their result (presumption: land the cutover; flip to excise only on a kill):
  - **(i) parity fails when extended** — the precondition-1 suite over the plant
    fixtures is the probe. If the two implementations disagree on any new shape, that
    is a kill (the module has diverged from the live path's correctness).
  - **(ii) Strategy D dedup is an unwanted behavior change** — reviewing the
    params-JSON key-set diff Strategy D produces is the probe. If the dedup collapses
    keys a consumer depends on (or is otherwise unwanted), that is a kill.
  - **(iii) the module drifted materially** — the both-directions diff is the probe. If
    re-syncing `input_resolver.py` to the live path's fixes costs more than the cutover
    buys, that is a kill.

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
  cost. The verdict is **recorded at design, after the three kill-condition probes run**
  (the parity-suite extension is testable now, over Item 1's fixtures). This spec fixes
  the presumption and the probes; design fixes the answer.
- **Whether the cutover splits into its own item.** The epic budgets Item 7 at 1.5–2
  days and allows design to split the F4 cutover out if it grows past that. Decide at
  design once the both-directions diff sizes the rewire.
- **The 5 xfails: fix vs re-frame.** Recommendation: **re-frame** — the
  misclassification produces a *loud* EXPOSE_COMPUTED rejection (not silent wrong
  output), no fusion-tea model hits it, and the classifier fix (supertype-namespace QN
  vs the Step-2b prefix check) is out of proportion to a matrix-truth item. Re-frame the
  REQ + document the xfails as a known contract, and file the classifier fix as its own
  backlog item. Confirm at design.
- **F2's three-way.** Fix REQ text, fix code, or both, for the Key_A/Key_F
  registration contract — decide at design against doc 10's intent (is the
  construction-time `instance_attr_to_channel` dict a deliberate optimization to
  document, or a divergence to remove?). REQ-ORCH-04's weakened assertion is restored
  regardless.
- **Per-row disposition of the ~175 unswept PASS rows.** The sweep runs at implement
  using the D7 heuristics; each finding is fixed or filed. The count and character of
  what it finds cannot be known until the sweep runs.

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
  - `tests/conformance/test_input_resolver.py` (24 skipifs), `test_dual_resolution.py`
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
