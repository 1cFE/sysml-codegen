# Spec: Matrix Sweep Residue (17 strengthens + 11 reframes + 5 citations + the ~46-row sweep decision)

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-07-07 01:47
**Complexity:** MEDIUM-HIGH
**Branch:** truth-debt-epic
**Epic:** TRUTH-DEBT, Item 5 (SC-E)

---

## Problem

PIPELINE-TRUTH Item 7 ran a leashed ~175-row deep-read of the verification matrix and found a
named residue of rows where the cited test **passes but pins less than the requirement text**
(the INV-B failure mode). It filed them rather than fix them in-budget: 17 rows needing a new or
widened assertion (**strengthen**), 11 where the text over-claims and should be softened to what
the test checks (**reframe**), and 5 where the behavior is pinned under a different REQ/test and
only the citation is wrong (**cite**). It also left **~46 qualifying rows un-deep-read** and said
so out loud (register discipline — no silent truncation). That residue has now been deferred
twice (filed at Item 7, carried into this epic).

This item retires that ledger with the same honesty discipline: no PASS row left pinning less than
its text, and the unswept remainder either completed or re-filed with a **named count**, never
silently dropped.

**Why now, and the drift risk this spec had to clear first.** The epic sequenced this item after
Items 1 and 4 precisely because those items move matrix rows, and a disposition filed at Item 7's
commit is a static-read verdict, not a fact at HEAD (R4). The re-verification below (this spec's
mandated first act, re-run against post-Item-3 HEAD) confirms the risk is real and ongoing: Items
3 and 4 have both landed since the original filing and moved rows the sweep never touched — but
**REQ-CA-01 itself is still live work, not discharged.** Every disposition below is a *candidate*
the plan must reproduce at HEAD before acting, not a settled instruction.

## Re-verification at HEAD (`9f37790`) — the mandated first act

- **Row count:** 256 REQ rows (Item 4 added REQ-CA-12; matches the epic's expected recount).
- **Status column: 255 PASS + 1 UNTESTED + 0 DEFERRED — 255 + 1 = 256, no discrepancy.** Item 3
  landed (`9f37790`) and flipped REQ-DM-08 and REQ-RES-08 to PASS with new dedicated tests
  (`test_dm08_enforced_surface.py`, `test_res08_consumer_scope_paths.py`) and REQ-RES-05 to PASS
  (`test_orchestrator.py::TestInnerStepOrdering`). The **only** remaining UNTESTED row is
  REQ-PGD-06 (`:397`, dead accessor, nobody's item). The 256-vs-255 summary gap this spec
  originally flagged (251+4=255≠256, under Item 1/4-era HEAD) is **resolved** — Item 3's PASS
  flips corrected the undercounted PASS column. The end-of-item recount below stays as a
  verification step (confirm the row-by-row total still reconciles after this item's own edits),
  not a discrepancy hunt.
- **All 33 dispositioned rows still exist at HEAD** (grep-confirmed by REQ id at line start).
- **Item 3 coordination confirmed — no double-touch.** Item 3 (`matrix-test-gaps/spec.md`) landed
  DM-08, RES-05, RES-08 with their own new tests and text reframes. **None of those three REQ ids
  appears in any of Item 5's 33 rows** — checked directly against the current disposition table
  (17 strengthen + 11 reframe + 5 cite lists below); clean boundary holds post-landing, not just
  pre-landing.
- **Item 4 coordination — CA-01 re-checked, reframe still needed.** Item 4 (classifier) landed and
  touched the CA family (added CA-12; CA-01's text now reads "exactly one of the 5 stable values …
  the transient sixth, `EXPOSE_CHAIN_TENTATIVE`, never survives the Phase-3b confirm pass to a
  reader — INV-F"). That INV-F clause is **not a no-op** — no cited test asserts the transient
  value is absent from reader-facing output after the confirm pass, and
  `test_classification_exhaustive` (`test_computed_attributes.py:85`) treats
  `EXPOSE_CHAIN_TENTATIVE` as a *valid* classification member, not an excluded one. **CA-01 stays
  in the 11-reframe batch, unchanged from the original disposition: drop the INV-F over-claim,
  reframe to "assign each attr exactly one enum member."** CA-06/07/11 read unchanged at HEAD; the
  plan re-verifies them same as the rest.

## Success Criteria

- [ ] **The high-value pair is strengthened and mutation-proven.** REQ-EC-04 (the expression
  compiler's internal parse-and-raise gate, `expression_compiler.py:217-223`, currently unpinned)
  and REQ-AS-06 (resolve-before-register gate; 40 of 41 aliases could be unresolvable and still
  pass) each gain an assertion that **fails under a deliberate mutation of the gate it now pins**
  (delete the gate / make an alias unresolvable → red).
- [ ] **The 17-strengthen list is fully judged and dispositioned** per the table below — each row
  either strengthened (assertion truly missing) or reframed (text over-claims), re-verified at
  HEAD, with byte-identity-gate flags on the fixture/regen-touching ones.
- [ ] **The 11 reframes land as one byte-safe batch** (text-only edits, no code, baselines
  byte-identical) — with CA-01 re-checked for already-discharged.
- [ ] **The 5 citation fixes land** (`# REQ-*` markers added / re-cited to the test that actually
  pins the claim).
- [ ] **The ~46 unswept rows are decided:** the sweep's *read* is completed under the D7 leash +
  stopping rule (see the sweep decision below); every row is dispositioned inline (reframe/cite in
  the same batch) or, where a real strengthen exceeds this item's budget, re-filed **with a named
  count and a matrix pointer**. No row left "not asserted swept."
- [ ] **Matrix recounted from rows** after everything lands, confirming the row-by-row total still
  reconciles with the summary/index/footer counts (the pre-Item-3 256-vs-255 gap is already
  resolved — this is a verification step, not a discrepancy hunt); no PASS row pins less than its
  text (INV-B).
- [ ] **Suite green; baselines byte-identical** except where a strengthen deliberately adds a
  fixture, which lands under the byte-identity gate as a reviewed capture diff.

## The disposition table (THIS IS THE CONTRACT for the plan)

Legend: **STR** = strengthen (add/widen a real assertion). **REF** = reframe REQ text to what the
test checks. **CITE** = fix citation/marker only. **⚠BI** = touches or may regenerate a
baseline/fixture → run under the byte-identity gate. **↺HEAD** = row text moved since the filing;
re-verify whether the disposition is still needed. Every row is re-reproduced at implement (R4);
the "disposition" column is the spec's judgment, the "action" column is the contract.

### A. The 17 strengthens — judged

| REQ | Line | Disposition | What the test pins now vs. its text | Action (contract) | Flags |
|-----|------|-------------|-------------------------------------|-------------------|-------|
| REQ-EC-04 | 194 | **STR** (high-value) | Tests call `python_ast.parse` on the compiler's *output*; the compiler's own internal parse-and-raise gate (`expression_compiler.py:217-223`) is unpinned — delete it and every EC-04 test still passes. | Add a case that forces invalid *emitted* Python and asserts `CompilationError` from the internal gate. Mutation: delete the gate → red. | |
| REQ-AS-06 | 80 | **STR** (high-value) | Resolve-before-register gate wrapped in `if result is not None:` + a `resolved_count > 0` floor; 40 of 41 aliases could be unresolvable and the test still passes. | Assert **every** registered redefinition alias resolves (enumerate the registered set, assert each resolves). Mutation: make one alias unresolvable → red. | ⚠BI (touches aggregation-scoping surface; confirm no baseline churn) |
| REQ-EPC-07 | 211 | **STR** | Purity test deep-compares only 2 of the 5 inputs. | Deep-compare all five inputs against fresh copies. | |
| REQ-ORCH-05 | 368 | **STR** | `len(scoped) >= len(expr)` aggregate count — one over-producing expression masks another scoping to zero. | Assert every expression id appears in the scoped output (set membership, not a count floor). | |
| REQ-ORCH-02 | 365 | **STR** | Source call-order only; the in-place `binding_type` mutation-visible-to-backtracker half is unpinned. | Assert a virtual binding's `binding_type` is actually mutated (observe the mutation, not just call order). | |
| REQ-ORCH-06 | 369 | **STR / CITE** | Source-order proof only; the "computation_graph is SSOT / generation boundary" half is really pinned under **REQ-PIPE-07**'s `TestGenerationBoundary`. | Cheapest honest fix: re-cite REQ-PIPE-07 **and** assert `ctx.computation_graph` identity in the ORCH-06 test. Judgment: STR (add the identity assertion) so the row pins its own text; CITE alone would leave ORCH-06's body still source-order-only. | |
| REQ-OR-02 | 349 | **STR** | Named `test_no_single_resolve_method` but never asserts `not hasattr(registry, "resolve")`; also omits the 4th lookup `scoped_alias_lookup`. | Add the negative `hasattr` assertion and cover the 4th lookup. | |
| REQ-OR-03 | 350 | **STR** | Wraps `caplog.at_level(WARNING)` but never asserts a warning record for the first-wins alias collision. | Assert the warning record is emitted. | |
| REQ-PGD-03 | 394 | **STR** | "One group per file" pinned only as a `>=` lower bound; over-grouping passes. | Assert `== distinct source-file count`. | |
| REQ-REG-06 | 453 | **STR** (R1 anti-vacuity) | Circular expected-set: derives the expected types from the SUT helper `_collect_exit_point_primitive_types`. | Derive the expected set **independently** from the graph (R1 independent-anchoring ban on self-derived expectations). | |
| REQ-CA-07 | 149 | **STR** | Self-reference exclusion is vacuous — no self-referencing fixture; the test checks a downstream string. | Add an `x = x + 1` fixture; assert on `input_names` directly. Re-verify against post-Item-4 CA text. | ⚠BI (new fixture may regenerate conformance data) |
| REQ-CA-11 | 152 | **STR** | Pins the registered→silent case only, not the unregistered→warns-naming-real-cause case. | Add the unregistered shape-A case; assert the warning names the real cause. Re-verify against post-Item-4 CA-11 text (unchanged at HEAD). | ⚠BI (new fixture) |
| REQ-EPC-05 | 209 | **STR** | "Exactly one ParameterGroup" — no cross-group uniqueness check. | Add the cross-group uniqueness assertion. | |
| REQ-BASE-04 | 110 | **STR** | Parametrizes 4 models, but 10 baseline dirs have `computation_graph.json`. | Glob all baseline dirs (read-only compare — widens coverage, does not change baselines). | (read-only; no churn) |
| REQ-DM-09 | 169 | **STR + CITE** | Pins the 4 field names, not serialization-non-exclusion / INV-5 sort / INV-3 validation; **and** its `test_graph_assembly.py` citation has no `# REQ-DM-09`-marked method (docstring only). | Strengthen to pin the sort/validation/non-exclusion, **and** add the `@pytest.mark.req`/`# REQ-DM-09` marker so tooling binds it. | |
| REQ-SR-05 | 508 | **STR** | Backup mechanism tested in isolation, not the "before every regen/upgrade" ordering. | Drive the regen path and assert the backup-before-regen ordering. | ⚠BI (drives regen) |
| REQ-PMM-02 | 422 | **STR** | Pins ModuleInput desc/default + ModuleOutput desc/unit, but not `ModuleOutput.default_value` (a real field). | Add the `ModuleOutput.default_value` assertion. | |

**Judgment note on the 17.** The epic invited flipping any filed-as-strengthen to a reframe where
the text over-claims. After reading each finding's evidence, **none flips to a pure reframe** —
in every case the behavior is real and the honest fix is to *add the missing assertion*, not to
soften the text. Two carry a citation component (ORCH-06, DM-09). Four touch fixtures or regen and
run under the byte-identity gate (AS-06, CA-07, CA-11, SR-05). The plan re-reproduces each before
strengthening (R4); if reproduction shows a text that already over-claims *and* can't be
strengthened without new production behavior, that row is re-routed to reframe + a filed feature
entry (the escape valve in Non-Goals), not force-strengthened.

### B. The 11 reframes — one byte-safe text-only batch

| REQ | Line | Disp | Reframe target (text → what the test checks) | Flags |
|-----|------|------|----------------------------------------------|-------|
| REQ-CA-01 | 142 | **REF** | "assign each attr exactly one enum member" (drop the INV-F over-claim — "the transient sixth… never survives… to a reader" — which is CA-10's job and is unpinned; `test_classification_exhaustive` even treats `EXPOSE_CHAIN_TENTATIVE` as a valid member). | Live work, confirmed at post-Item-3/4 HEAD — not a no-op. Re-verified in the Re-verification section above. |
| REQ-CA-06 | 148 | **REF** | LITERAL path is never exercised (only FORMULA/EXPOSE_ALIAS); reframe to those two, note LITERAL is the design-attr/entry-point path. | Re-verify against post-Item-4 CA text (unchanged at HEAD per spot-check). |
| REQ-AST-03 | 92 | **REF** | Cited test pins only the FCE<OE<FRE ordering clause, not literal-before-catch-all (that's AST-08). Reframe to the ordering clause. | |
| REQ-DM-03 | 163 | **REF** | Compares field-NAME sets only. Reframe to "field name lists" (or strengthen — see below). | |
| REQ-DM-04 | 164 | **REF** | Checks source file only, not parent class. Reframe to "importable from documented source file." | |
| REQ-OSR-03 | 380 | **REF** | Template-fidelity only (both sides from same graph), not SysML-source match. Reframe, or add the output-registry PQN test to the citation. | |
| REQ-SR-06 | 509 | **REF** | Grep-only static. Reframe to "all module types route through the single `_generate_stencils()`." | |
| REQ-SNAP-18 | 495 | **REF** | Vacuous grep — no production render site under `src/sysml_codegen` still passes `generation_timestamp` (the token survives only in the test itself, the matrix row, and `.project/` history; the template that once carried it, `pydantic_schema.py.jinja2`, is deleted); the template-var premise is stale. Reframe to a regression guard. | |
| REQ-PMM-04 | 424 | **REF** | Asserts valid non-empty Python, not byte-identity vs a pre-migration baseline (that gate ran once at cutover). Reframe to the testable property. | |
| REQ-PMM-05 | 425 | **REF** | Phased-sequence (add/create/deprecate/remove) is process, not a testable module property. Reframe to importable-variants + unchanged-fields. | |
| REQ-AS-02 | 76 | **REF** | Strategy-1-before-2 short-circuit shown only via a disjoint fixture (no dual-match partdef); precedence inferred. Reframe, or add a dual-match case. | |

**Two rows are reframe-OR-strengthen judgment calls (DM-03, AS-02).** The filing marked them as
reframe candidates but noted a strengthen alternative. Spec judgment: **reframe** both (byte-safe,
keeps this batch text-only) unless implement finds the stronger assertion falls out trivially on
an existing fixture. Do not manufacture a new fixture for these two — that would move them out of
the cheap batch for marginal gain.

### C. The 5 citation fixes — marker/traceability only

| REQ | Line | Disp | The claim IS pinned — by | Action |
|-----|------|------|--------------------------|--------|
| REQ-BASE-01 | 107 | **CITE** | `test_graph_assembly.py::TestBaselineComparison` (marked REQ-GA-01); the cited `test_baselines.py` only checks 3 keys exist. | Re-cite / add the marker to the real full-JSON compare. |
| REQ-NC-08 | 339 | **CITE** | `test_formula_quoted_owner.py` pins the FORMULA module_eqn/channel leg (not cited). | Add it to the citation. |
| REQ-VBR-10 | 538 | **CITE** | `test_self_named_binding_trap.py::test_self_named_binding_resolves_to_own_param` pins the "else leave it as-is" clause (not cited). | Add it. |
| REQ-HR-08 | 277 | **CITE** | `test_virtual_binding_rewrite.py::TestChainOverrideFixtureCoverage` (marked REQ-VBR-04) pins the "`part redefines` keeps all RHS types" leg. | Add a `# REQ-HR-08` marker there. |
| REQ-PY-08 | 440 | **CITE** | Cited method carries the REQ only in a docstring, no `@pytest.mark.req` — matrix tooling may not bind it. | Add the marker. (REQ-DM-09's docstring-only marker is fixed in its STR row above, not double-counted here.) |

## The ~46-row sweep — DECISION: complete the read under the leash, file only the fix-overflow

**Decision: complete the sweep's *read* at implement under the D7 heuristics + stopping rule.
Disposition every qualifying row. Land the cheap dispositions (reframe/cite) in the same batches.
Re-file only the rows that need a genuine new-assertion strengthen exceeding this item's budget —
with a NAMED count and a matrix pointer.** Do not re-file the residue wholesale.

**The argument.**
- **This residue has been deferred twice** (filed at PIPELINE-TRUTH Item 7, carried into this
  epic). A third blanket re-file is exactly the silent-truncation-shaped debt this epic exists to
  retire. The epic's SC-E names "completed OR re-filed with a named count" — but re-filing is the
  *fallback*, and completing is the charter ("discharge … with the same honesty discipline").
- **The sweep's obligation is a READ, and the read is cheap.** The deep-read produces, per row,
  either "adequate as-is" or "add to reframe/cite/strengthen." Reframe and cite dispositions are
  byte-safe text/marker edits that fold into the batches this item already lands. Only a *new
  assertion* costs real implement time — and the prior sweep found **every** finding across 167
  rows was PASS-pins-narrower, none a correctness lie, none feature work, so the tail is expected
  to be thin.
- **The stopping rule bounds the cost.** D7's leash: sweep until the qualifying list is exhausted
  OR 0 new findings in 40 consecutive rows after the first 60 examined. That caps the read
  regardless of what the tail holds.
- **Fix-scope, not read-scope, is the real budget risk** — and it is handled honestly: any row
  whose only faithful fix is a substantial new assertion+fixture beyond budget is re-filed with a
  named count, so the ledger stays truthful without forcing the whole residue open.

**The named residue anchor (for the plan to enumerate exactly).** The filing named the ~46 as
"primarily the EPC diagnostics, LVP literal-propagation, and GA topo-sort internals." At HEAD
those three families are EPC 8 + LVP 9 + GA 8 = **25 rows**; the balance (~21) is spread across
other families' rows the ~167-row pass did not line-by-line read. **The plan's first sweep step
is to produce the exact qualifying-row list** by applying the D7 qualifier grep (text contains
SHALL/ALL/every/never/exactly, OR asserts a diagnostic fires, OR asserts a numeric/structural
count) to all 256 rows, subtracting the ~167 already swept (the Item-7 register) and the 33
already dispositioned here. That yields the concrete residue set; the ~46 is the estimate, the
grep is the contract.

## Known Requirements

- **[HARD]** **INV-B — no PASS row pins less than (or other than) its text.** Every strengthen
  makes the row pin its full text; every reframe narrows the text to what the test checks; every
  cite points the marker at the real pin. This is the item's whole charter.
- **[HARD]** **R1 independent anchoring.** No strengthened test computes its expected value from
  the code under test. REQ-REG-06 is the named offender (derives its expected set from the SUT
  helper) — its strengthen *is* the de-circularization. Every new assertion's expectation is
  hand-authored/independently derived.
- **[HARD]** **R1 fires-on-shape + silent-on-clean for any new diagnostic assertion.** Where a
  strengthen pins a warning/error (OR-03, CA-11), it asserts the diagnostic fires on its shape and
  (where a clean sibling is cheap) stays silent on clean input.
- **[HARD]** **Mutation-provable strengthens.** Each strengthened row fails under a deliberate,
  realistic production mutation of the thing it now pins (spot-check recorded in close-out, then
  reverted). Named for EC-04 (delete the gate) and AS-06 (make an alias unresolvable); required
  for all 17.
- **[HARD]** **Byte-identity gate on fixture/regen-touching strengthens (R3).** AS-06, CA-07,
  CA-11, SR-05 (and any new residue strengthen that adds a fixture) land byte-identically or as a
  reviewed `scripts/capture_*.py` diff. Text-only reframes and marker-only citations must leave
  baselines byte-identical.
- **[HARD]** **R4 reproduce-before-fix at HEAD.** Every disposition in the table is a static-read
  candidate. The plan reproduces each finding against HEAD code/tests before acting; a finding
  that does not reproduce (e.g. CA-01 already discharged) is reclassified in the table, not
  force-applied.
- **[HARD]** **Recount from rows, last (memory `verification-matrix-drift-modes`).** The
  summary/index/footer counts are regenerated from the row-by-row reality *after* all dispositions
  land, confirming the total still reconciles (Item 3 already landed the DM-08/RES-05/RES-08 flips
  and fixed the summary undercounting — this item's own edits must not reopen that gap). Anchor
  the STATUS count on the status column, not a loose substring (many rows mention other REQ ids /
  "UNTESTED" in prose).
- **[INFERRED]** **DM-09 is one row with two defects, not two.** It appears in both the strengthen
  list (under-pins its text) and the citation list (docstring-only marker). Fix both in its single
  STR row; do not double-count it in the recount or re-file it as a separate citation.
- **[INFERRED]** **CA family re-judged post-Item-4.** CA-01/06/07/11 are re-verified against the
  Item-4 text at HEAD; CA-01 is confirmed drifted (reframe likely already discharged).

## Non-Goals

- **Item 3's rows** (DM-08, RES-05, RES-08) and **Item 4's classifier rows** (CA-12 etc.) — out of
  scope, confirmed non-overlapping with the 33.
- **New feature work surfaced by a reframed REQ** — if a reframe or a residue-sweep row exposes a
  behavior gap (the text describes something the code should do but doesn't), **file it with a
  matrix pointer**, do not build it here. This is the escape valve that keeps the 11-reframe batch
  byte-safe and the strengthens bounded.
- **Re-deriving the ~167 already-swept rows** — the Item-7 register is trusted for what it swept;
  this item completes the *un*swept remainder, it does not re-audit the swept set.
- **PGD-06** — stays UNTESTED (dead accessor); not this item's row.

## Open Questions / Deferred to design/plan

- **DM-03 and AS-02: reframe vs. strengthen** — spec judgment is reframe (keep the byte-safe
  batch text-only). The plan confirms at implement whether the stronger assertion falls out
  trivially on an existing fixture; if it needs a new fixture, it stays a reframe.
- **ORCH-06: the exact assertion for the SSOT/generation-boundary half** — re-cite REQ-PIPE-07 vs.
  assert `ctx.computation_graph` identity in-body vs. both. Spec leans "both" (pin its own text +
  cross-cite); the plan picks the minimal mutation-provable form.
- **The residue fix/re-file split** — the *count* of residue rows that need a budget-exceeding
  strengthen is unknown until the read runs. The plan sets the budget line (how many strengthens
  this item absorbs vs. re-files) after the D7 read produces the qualifying list. The decision to
  complete the *read* is fixed; the fix/re-file boundary is a plan-time budget call.

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_truth_debt.md` (Item 5; SC-E; R1–R4; the risk-table mandate to
  re-verify divergent/untested lists at pickup).
- **Required Reading:**
  - BACKLOG `[ITEM7-MATRIX-SWEEP-RESIDUE]` (`.project/backlog/BACKLOG.md:328`) — the full
    row-by-row list this table is built from.
  - `.project/active/matrix-truth/design.md` — the leashed-sweep D7 heuristics + stopping rule
    (`§The ~175-Row Sweep`) and the count-recount method.
  - Memory `verification-matrix-drift-modes` — recount-from-rows discipline; the drift modes
    (summary off-by-one, index counts, PASS-pins-narrower).
  - `docs/architecture/verification-matrix.md` @ `9f37790` — recounted here.
- **Coordinated sibling:** `.project/active/matrix-test-gaps/spec.md` (Item 3) — owns DM-08,
  RES-05, RES-08; boundary confirmed disjoint.
- **Plan:** `.project/active/matrix-sweep-residue/plan.md` (to be created — Item 5 skips design per
  the epic deliverables: `{spec,plan}.md`).

---

**Next Steps:** After approval, proceed to `/_my_plan`. The plan must (1) produce the exact D7
qualifying residue list by grep-minus-swept-minus-dispositioned; (2) sequence the 17 strengthens
with their mutation spot-checks and byte-identity-gate captures; (3) batch the 11 reframes
(including CA-01, confirmed live work, not a no-op) and the 5 citations as byte-safe edits; (4) set
the residue fix/re-file budget line; (5) recount from rows last, confirming the total still
reconciles after this item's own edits (the pre-Item-3 256-vs-255 gap is already resolved).
