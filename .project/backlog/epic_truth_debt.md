# Epic: Truth-Debt Retirement

**Epic ID**: TRUTH-DEBT
**Status**: Draft
**Priority**: P2 (Medium)
**Created**: 2026-07-06
**Estimated Effort**: ~7–9.5 days (6 items; one 2-item critical path, four parallel)

---

## Executive Summary

PIPELINE-TRUTH proved the generated package is the truth and, in doing so, deliberately
filed the follow-on work it chose not to rush under a per-item budget: an executable
aggregation-resolution cutover, a new multi-hop chain capability, a batch of test-coverage
and matrix-honesty rows, a classifier fix for a silent inherited-attr misclassification (behind a xfail), and a hygiene tail of benign
silent sites. This epic retires that ledger in one pass — every item already carries
implement-time evidence (probes, pins, filings with file:line), so it is debt-retirement,
not discovery.

**Critical Success Factor**: the live aggregation path runs through
`resolve_input(AGG_STRATEGIES)` (the F4 cutover lands), and no row, doc, or diagnostic left
open by PIPELINE-TRUTH still misstates what the code does — the matrix and the code agree,
and the deferred capabilities are built, not parked.

---

## Why This Epic?

**Current State**:
- The live aggregation path runs `_resolve_aggregation_input_channel`
  (`resolution/graph_builder.py:1212`). `resolve_input(AGG_STRATEGIES)` is a
  parity-validated consolidation that PIPELINE-TRUTH Item 7 proved correct against the
  backtracker but never wired — the IR matrix rows say "validated, not yet wired," and a
  known EP-key format divergence (`probes/probe_iv_ep_key_divergence.md`) blocks a naive
  drop-in.
- 3+-segment chain bindings (`station.array.calc.output`) are a **loud rejection**, not a
  resolved chain. `extract_feature_chain_segments` already yields every segment; Item 5 of
  the prior epic used it only to COUNT for the reject diagnostic.
- Three matrix rows (REQ-DM-08, REQ-RES-05, REQ-RES-08) are UNTESTED with an argument — no
  honest test pins them. Five xfail cases lock a silent inherited-attr misclassification (an EXPOSE_COMPUTED no-op drop, not loud — corrected and retired by Item 4).
- The leashed matrix sweep left ~46 rows unswept and a named residue of strengthens,
  reframes, and citation fixes. A hygiene tail of four benign silent sites is filed but not
  hardened. Two graph_builder type-ignores guard a genuine double-binding.

**Future State**:
- The aggregation IR family pins live code; `_resolve_aggregation_input_channel` and the
  Strategy-D no-op stub are gone; baselines re-captured byte-identically or as reviewed diffs.
- Multi-hop chains resolve; `deep_cross_scope_probe` Pattern A pins a resolved chain.
- Every matrix row pins its full text or carries an argument; the xfails flip to PASS; the
  sweep completes or re-files with the same honesty discipline.
- The hygiene tail fires-on-shape and stays silent-on-clean (INV-6 zero-WARNINGs preserved);
  the type-ignore cluster is cleared with mypy no worse than 104.

---

## Success Criteria

- [x] **SC-A (F4 cutover)**: the live aggregation path calls `resolve_input(AGG_STRATEGIES)`;
  `_resolve_aggregation_input_channel` deleted; Strategy D deleted and its lying docstring
  fixed; the cutover's parity gate compares against **the replaced function**, not only the
  backtracker; the IR family rows drop the "not-yet-wired" note and pin live code.
- [x] **SC-B (multi-hop chains)**: 3+-segment chain bindings resolve to a wired chain;
  `deep_cross_scope_probe` Pattern A flips from a rejection pin to a resolved-chain pin.
  Done: extraction emits full-path CHAIN (D1); backtracker gains an ancestor-scope climb +
  ambiguity guard (D2/D4/M-1); the loud diagnostic moved to the backtracker Step-4 fallback
  (D3). Both corpus chains wired (data_point via climb, base_metric via Step 1); re-capture
  decomposed; live/offline parity green. See `.project/active/multihop-chain/plan.md`.
- [x] **SC-C (test gaps)**: REQ-DM-08, REQ-RES-05, and REQ-RES-08 each get an
  independently-anchored pinning test; their matrix rows flip UNTESTED→PASS. Audited PASS
  (`.project/active/matrix-test-gaps/audit.md`); gate counts and mutation red→green not
  re-executed (sandbox-blocked), static tracing confirms everything else.
- [ ] **SC-D (classifier)**: the Step-2b owning-part prefix check accepts a
  supertype-namespace QN; the parametrized xfail site (`test_computed_attributes.py:787`)
  flips to PASS (5 cases); REQ text + matrix rows move in the same change.
- [ ] **SC-E (sweep residue)**: REQ-EC-04 and REQ-AS-06 strengthened; the 17-strengthen list
  judged at spec; the 11 REQ-text reframes landed as one byte-safe batch; the 5 citation
  fixes landed; the ~46 unswept rows either completed or re-filed with a named count.
- [ ] **SC-F (hygiene tail)**: the four D3 silent sites hardened family-style (fires-on-shape
  + silent-on-clean); INV-6 "clean fixtures generate with zero WARNINGs" preserved.
- [x] **SC-G (typing)**: the graph_builder `param_groups` double-binding split (dead Step-5
  computation removed if confirmed); the two type-ignores cleared; **mypy ≤ 104**.
- [ ] **SC-H (gates)**: full suite green; ruff ≤ 17; mypy ≤ 104; all baseline churn via
  `scripts/capture_*.py` with reviewed diffs; matrix recounted from rows, not the summary.

---

## Method Note — No Discovery Sweep

Unlike PIPELINE-TRUTH, this epic runs **no discovery phase**. Every item was filed during
the PIPELINE-TRUTH run with implement-time evidence attached: F4 has four committed probes
(`.project/active/matrix-truth/probes/`), the multi-hop and hygiene sites have file:line
pins from the discovery register's D3 family, the classifier root cause is pinned by
`test_inherited_refs_have_supertype_qn`, and the sweep residue carries per-row dispositions.
The work is to execute against that evidence, re-verifying it at pickup (R4 step 2 still
applies — a filed finding is a static-read verdict until reproduced), not to rediscover it.

---

## Mandatory Reading (every item)

1. **This epic's parent ledger** — `.project/backlog/epic_pipeline_truth.md` (the source of
   R1–R4, the item filings, and the Lessons Learned) and the full-scope report
   `.project/reports/20260706_pipeline-truth-epic-report.md` §4 (the complete deferral table).
2. **The BACKLOG filings** — each absorbed entry in `.project/backlog/BACKLOG.md` carries its
   own file:line evidence; read the entry for the item you pick up.
3. **The F4 evidence base** — `.project/active/matrix-truth/{design,design-review}.md` and
   `probes/` (parity, Strategy-D dedup, module drift, and the EP-key divergence blocker).
4. **The matrix** — `docs/architecture/verification-matrix.md` (recount from rows) and memory
   note `verification-matrix-drift-modes`.

---

## Cross-Cutting Requirements (carried forward from PIPELINE-TRUTH — proven, verbatim intent)

These are the R1–R4 requirements the prior two epics established and validated. They stay in
force unchanged; the full text lives in `epic_pipeline_truth.md`. Summarized here so each
item's spec can cite them by number.

### R1 — Design-pattern consistency
ComputationGraph is the sole input to generation (deliberate revs only); typed registries and
NewType keys; compute-once-look-up; diagnostics follow the V1–V11 pattern (nothing dropped
silently); conformance tests use real SysML fixtures, never mocks; REQ tags + docs + matrix
rows move with code. **Addition (proven this-epic-relevant):** every new or changed diagnostic
lands with (a) a test proving it FIRES on the shape it claims, with an **independently-anchored**
expectation (never computed by the code under test), and (b) a test proving it stays silent on
clean input.

### R2 — agentic-mbse lockstep
Every item ends by recording (and where trivial, implementing) matching agentic-mbse changes;
nothing silently dropped. This epic's items are mostly in-repo (resolution, matrix, tests), so
the expected agentic-mbse surface is small — but the multi-hop chain capability (Item 2) and
any new diagnostic land with their MODELING_GUIDE / validation impact recorded, even if the
disposition is "no change needed."

### R3 — Baseline discipline
Baseline/snapshot regeneration through `scripts/capture_*.py` only, with reviewed diffs. The
F4 cutover (Item 1) is the churn item: the EP-key reconciliation reshapes aggregation entry
points, so its baselines land byte-identically or as one reviewed capture diff. One item's
regen at a time. The syside license is on monthly renewal — no expiry pressure.

### R4 — Verify-then-fix protocol (anti-whack-a-mole)
A filed finding is a **static-read verdict, not a confirmed bug**. For every finding an item
picks up, in order: (1) check architectural intent first — read the reference doc and REQ rows
before diagnosing; a code-vs-doc divergence is a decision point, not automatically a bug;
(2) reproduce before fixing — a failing test or live probe against real code (real fixtures,
never mocks); a finding that does not reproduce is reclassified, not fixed; (3) fix at the root,
in the house style — findings cluster into families, fixed at the cleanest choke point, not
site-by-site; (4) close the loop in the docs — reference doc, modeling-assumptions section, and
matrix rows updated in the same change. See memory note `verify-then-fix-protocol`.

---

## Backlog Items

### Item 1: F4 Aggregation-Resolution Cutover (+ graph_builder param-group typing) [2–2.5 days]

**Type**: Implementation
**Effort**: 2–2.5 days (spec 2h, design 3h, plan 1h, execute 10–14h) — fit: high (the module
is parity-validated and the blocker is pinned to a concrete baseline); lift: medium-high
(fallback refactor + baseline re-capture + double-binding split); risk: **medium-high** (EP-key
collision, aggregation baseline churn).
**Dependencies**: None — **lands FIRST** among items touching aggregation resolution (R3
baseline discipline; Item 2's chain-follow logic is adjacent). Folds in `[GB-PARAMGROUPS-TYPING]`
(same graph_builder group-assembly region).

**Objective**: Wire the live aggregation path through `resolve_input(AGG_STRATEGIES)`,
replacing `_resolve_aggregation_input_channel`, so the whole IR family finally pins live code —
and clear the co-located param-group typing debt while in the same region.

**Current State**:
- ✅ `resolve_input(AGG_STRATEGIES)` exists, is parity-validated against the backtracker over
  catf_mfe/solar_battery + the Item-1 plant fixtures (`test_dual_resolution.py`).
- ⚠️ It is **not wired**. The live path runs `_resolve_aggregation_input_channel`
  (`graph_builder.py:1212`); the module's leaf-only fallback mints an EP key
  (`…__raw_material_cost`) that already collides with an output-channel name in the
  solar_battery baseline (`probes/probe_iv_ep_key_divergence.md`).
- ⚠️ Strategy D (`DesignAttributeLookup`, `input_resolver.py:200`) is a `return None` stub
  with a lying docstring ("included in AGG_STRATEGIES for future extensibility").
- ⚠️ `param_groups` is bound twice (`graph_builder.py:408/412`, `[assignment]` +
  `[attr-defined]` ignores); the Step-5 result is likely a removable dead computation
  (the Step-6.6 rebuild discards it).

**Scope**:
1. **Reconcile `resolve_input`'s fallback to the live path's richer EP construction** — the
   load-bearing blocker (design-review M4). The live call sites build
   `{module_eqn}__{part_usage}_{attr}` with `_find_literal_redefinition` defaults, param-group
   classification, `DESIGN_ATTRIBUTE` typing, multiplicity EPs, and the SingletonTerm "Try 2"
   direct-channel construction; the module's fallback emits a bare `{module_eqn}__{leaf}`.
   Reconcile before rewiring so no input EP collides with an output channel.
2. **Prove parity against the replaced function** (design-review M3 — do NOT skip): the
   cutover's safety-net suite compares `resolve_input(AGG_STRATEGIES)` against
   **`_resolve_aggregation_input_channel`**, not only the backtracker. Add this comparand as
   the item's own gate before rewiring.
3. **Rewire the 3 call sites** (`graph_builder.py:1444/1539/1640` per filing; :1437/1532/1633
   per design — re-verify at pickup) and delete `_resolve_aggregation_input_channel`.
4. **Delete Strategy D** from `AGG_STRATEGIES` and fix its docstring (probe ii: zero live
   surface).
5. **Re-capture baselines byte-identically, or land as a reviewed `scripts/capture_*.py` diff**
   (R3 / SC-A).
6. **(Folded `[GB-PARAMGROUPS-TYPING]`)** split the `param_groups` double-binding into two
   distinctly-named variables (remove the dead Step-5 computation if confirmed dead); clear the
   two type-ignores; **mypy must not exceed 104**.

**Out of Scope**:
- Strategy D as a *new* capability (implement-or-delete only; probe ii → delete).
- Any ComputationGraph schema rev beyond the EP-key reconciliation the cutover forces.

**Success Criteria**:
- [ ] IR rows re-pin the live path (drop the "not-yet-wired" family note);
  `_resolve_aggregation_input_channel` deleted; Strategy D gone; docstring fixed.
- [ ] Parity gate runs against the replaced function and is green.
- [ ] Baselines byte-identical or reviewed capture diff; existing non-aggregation baselines
  untouched.
- [ ] `param_groups` double-binding split; two type-ignores cleared; mypy ≤ 104.

**Required Reading**: `.project/active/matrix-truth/{design,design-review}.md` + all four
`probes/` artifacts (esp. `probe_iv_ep_key_divergence.md`); BACKLOG `[ITEM7-F4-CUTOVER]` and
`[GB-PARAMGROUPS-TYPING]`; `reference/07-graph-builder.md`, `reference/03/04/05`
(input_resolver intent, reframed by Item 7); memory notes `f4-cutover-fallback-divergence`,
`byte-identity-captured-at-churn`.

**Deliverables**: `.project/active/f4-cutover/{spec,design,plan}.md`; the rewire + parity gate
+ typing fix; regenerated baselines; docs 03/04/05 + IR rows updated (R1).

---

### Item 2: Resolved Multi-Hop Chain Bindings [1.5–2 days]

**Type**: Implementation (new capability)
**Effort**: 1.5–2 days (spec 2h, design 2h, plan 1h, execute 8–11h) — fit: high (the segment
extractor already exists); lift: medium; risk: medium (new resolution path adjacent to the
chain-follow logic Item 1 just re-touched).
**Dependencies**: Soft — after **Item 1** (both touch aggregation/chain resolution; sequence
deliberately so baseline churn and adjacent-code edits don't overlap).

**Objective**: Build resolved support for 3+-segment chain bindings
(`station.array.calc.output`), flipping `deep_cross_scope_probe` Pattern A from a loud
rejection to a resolved-chain pin.

**Current State**:
- ✅ `extract_feature_chain_segments` (`expression_utils.py`) already yields all segments.
- ⚠️ Item 5 of the prior epic uses it only to COUNT for the loud-reject diagnostic; 3+-segment
  chains hard-diagnose instead of resolving.
- ❌ No resolved multi-hop path exists; `deep_cross_scope_probe` Pattern A is pinned as a
  rejection.

**Scope**:
1. **Build the resolved multi-hop resolution path** — walk the segments the extractor yields,
   resolving each hop to its owning part/channel, terminating at the referenced output.
2. **Flip the loud-reject to a resolved wire** for supported shapes; keep a loud diagnostic for
   the genuinely unresolvable tail (never a silent truncation — the Item-5 contract holds).
3. **Re-pin `deep_cross_scope_probe` Pattern A** as a resolved-chain assertion (fires-on-shape),
   plus a silent-on-clean sibling (R1 addition).
4. **agentic-mbse impact** (R2): record the newly supported chain shape for MODELING_GUIDE.

**Out of Scope**:
- Expression-valued chain RHS beyond what Item 10 of the prior epic already wired.
- Chain shapes no supported model uses (file, don't build).

**Success Criteria**:
- [ ] A 3+-segment chain binding resolves to the correct wired channel, verified by an
  independently-anchored test.
- [ ] `deep_cross_scope_probe` Pattern A pins a resolved chain, not a rejection; the
  unresolvable tail still hard-diagnoses.
- [ ] Existing baselines byte-identical (new capability, no output change for covered models);
  agentic-mbse impact recorded.

**Required Reading**: BACKLOG `[MULTIHOP-CHAIN-PARSE]`; discovery register §D3-2; memory notes
`multihop-expose-offline-parity`, `cross-part-binding-v11-fallthrough`;
`reference/24-binding-resolution.md`.

**Deliverables**: `.project/active/multihop-chain/{spec,design,plan}.md`; the resolution path +
tests; doc updates.

---

### Item 3: Matrix Test-Gap Authoring [0.5–1 day]

**Type**: Testing
**Effort**: 0.5–1 day (spec 1h, plan 0.5h, execute 3–5h) — fit: high (test-authoring, siblings
exist); lift: low; risk: low-medium (RES-08 is a cross-cutting invariant that must be
independently anchored).
**Dependencies**: Soft — RES-08 pins "consumer scoping applies to ALL resolution paths"; author
it **after Item 1** so it reflects the post-cutover aggregation path. DM-08 and RES-05 are
independent.

**Objective**: Give the three UNTESTED-argued matrix rows an honest, independently-anchored
pinning test.

**Current State**:
- ⚠️ REQ-DM-08 (NewType wrappers on name fields) — wrappers exist (`core/identifier_types.py`)
  but no test asserts the target fields are annotated with them.
- ⚠️ REQ-RES-05 (graph builder internal sequence: classify → build modules → rebuild groups →
  toposort → validate) — no test pins `build_computation_graph`'s internal sequence
  (the existing test pins the outer `build_pipeline_context` DAG, a different function).
- ⚠️ REQ-RES-08 (consumer scoping applies to ALL resolution paths) — per-path derivation is
  verified; no single test pins the cross-cutting invariant.

**Scope**:
1. **REQ-DM-08**: a small static test — assert the wrappers are `NewType` and the documented
   model fields use them.
2. **REQ-RES-05**: pin `build_computation_graph`'s internal step sequence (source-order or a
   call-sequence spy on the real function, not the outer orchestrator).
3. **REQ-RES-08**: a new test enumerating the resolution paths and asserting consumer-scope
   derivation applies to each — expectation written **independently** (R1 ban), using the
   Item-1 cross-part fixtures (`plant_values`) as substrate.
4. Flip the three matrix rows UNTESTED→PASS with their new citations (R1, in-item).

**Out of Scope**:
- Behavior changes — if authoring a test EXPOSES a real bug, file/absorb it explicitly.
- The sweep-residue strengthens (Item 5).

**Success Criteria**:
- [ ] Each of the three tests fails under a deliberate production mutation (spot-check noted in
  close-out).
- [x] Matrix rows flip UNTESTED→PASS; recount from rows holds. Verified by audit
  (recount 256 = 255 PASS + 1 UNTESTED, grepped from the row table directly).
- [ ] Suite green; baselines byte-identical.

**Required Reading**: BACKLOG `[ITEM7-MATRIX-TEST-GAPS]`;
`.project/active/matrix-truth/design.md` (UNTESTED-12 disposition); memory note
`verification-matrix-drift-modes`; `reference/07-graph-builder.md`.

**Deliverables**: `.project/active/matrix-test-gaps/{spec,plan}.md`; three tests; matrix rows
updated.

---

### Item 4: Inherited-Attr Classifier Fix (flip the 5 xfails) [0.5–1 day]

**Type**: Implementation
**Effort**: 0.5–1 day (spec 1h, design 1h, plan 0.5h, execute 3–5h) — fit: high (root cause
pinned); lift: low-medium; risk: low-medium (classifier logic + coordinated matrix/xfail flip).
**Dependencies**: None (independent).

**Objective**: Teach the classifier's Step-2b owning-part prefix check to accept a
supertype-namespace (ancestor PartDef) QN for an inherited attribute, so the silent
EXPOSE_COMPUTED no-op misclassification stops and the parametrized xfail flips to PASS.

**Status**: ✅ LANDED. Step-2b widened to prefix-match any ancestor PartDef QN
(`computed_attribute_extractor._ancestor_part_qns`); snapshot re-captured (5 flips + a
depth-2 case); the xfail site deleted for a positively-asserting 7-row table; D5
graph-builder diagnostic added so the residual no-module outcome is loud at generation.

**Current State** (pre-fix, for the record):
- `test_computed_attributes.py` (one parametrized `pytest.xfail` site) produced 5 xfailed
  cases: inherited attributes classified EXPOSE_COMPUTED where FORMULA is correct.
- ✅ Root cause pinned: an inherited attribute's QN resolves to the **supertype** namespace,
  defeating the Step-2b `owning_part_qn` prefix check
  (`test_computed_attributes.py::test_inherited_refs_have_supertype_qn`, kept green).
- The misclassification is a **silent no-op**, not loud: a misclassified inherited-attr
  FORMULA lands EXPOSE_COMPUTED, which the graph builder drops with no module and no
  diagnostic (`graph_builder.py:269-288`; `test_computed_attributes_e2e.py`). Only the
  "not a silent wrong value" half of the old "loud rejection" framing was true. No
  fusion-tea model hits it.

**Scope**:
1. **Fix Step-2b** to accept a supertype-namespace QN when the attribute is inherited.
2. **Flip the xfails** — the parametrized site goes PASS (xfail strict=False); no fake test.
3. **Coordinate the matrix + REQ text in-item** (R1): the rows Item 7 re-framed as
   "documented contract" flip back to PASS; the REQ text is corrected in the same change.
4. **Verify no clean-shape regression** — a fires-on-shape + silent-on-clean pair confirms the
   fix does not reclassify a genuine EXPOSE_COMPUTED attribute.

**Out of Scope**:
- EXPOSE_COMPUTED decomposition (calc output + arithmetic) — still deferred.

**Success Criteria**:
- [ ] The 5 parametrized cases PASS; a genuine EXPOSE_COMPUTED attribute still classifies
  EXPOSE_COMPUTED (no over-correction).
- [ ] Matrix rows + REQ text updated in the same change; recount holds.
- [ ] Suite green; baselines byte-identical.

**Required Reading**: BACKLOG `[ITEM7-CLASSIFIER-FIX]`;
`.project/active/matrix-truth/design.md` (the xfail re-frame); `reference/01-extraction.md` /
the computed-attribute classification doc.

**Deliverables**: `.project/active/classifier-fix/{spec,design,plan}.md`; the Step-2b fix +
flipped xfails; matrix/REQ updates.

---

### Item 5: Matrix Sweep Residue [1.5–2 days] ✅

**Type**: Testing / Documentation
**Effort**: 1.5–2 days (spec 2h, plan 1h, execute 8–11h) — fit: high (every row carries its
disposition); lift: medium (17 strengthens judged + 11 reframes + 5 citations + a sweep
decision); risk: low-medium (strengthens that touch baselines run under the byte-identity gate).
**Dependencies**: Soft — after **Items 1 and 4** so the rows they move have settled (prior-epic
Item 7 sequenced after 4/5/6 for the same reason).

**Objective**: Discharge the ~33 dispositioned sweep rows and decide the ~46 unswept ones with
the same honesty discipline — no row left pinning less than its text, no silent truncation.

**Current State**:
- ⚠️ 17 rows marked "strengthen" (needs a new/expanded assertion); two are high-value and
  named: REQ-EC-04 (the expression compiler's internal parse-and-raise gate,
  `expression_compiler.py:217-223`, is completely unpinned) and REQ-AS-06 (40-of-41 aliases
  could silently fail).
- ⚠️ 11 rows marked "reframe REQ text to what the test checks" (cheap, byte-safe).
- ⚠️ 5 rows marked "fix citation only" (behavior IS pinned under a different REQ/test).
- ❓ ~46 qualifying rows were not deep-read this pass (EPC diagnostics, LVP propagation, GA
  topo-sort internals).

**Scope**:
1. **Strengthen the high-value pair** (REQ-EC-04, REQ-AS-06) and **judge the rest of the
   17-strengthen list at spec** — strengthen where a real assertion is missing, reframe where
   the text over-claims. Strengthens that touch baselines run under the byte-identity gate.
2. **Land the 11 REQ-text reframes** as one cheap byte-safe batch.
3. **Land the 5 citation fixes** (re-cite / add `# REQ-*` markers to the tests that actually
   pin the claim).
4. **Decide the ~46 unswept rows at spec**: either this epic completes the sweep (per the D7
   heuristics + stopping rule) or re-files the remainder with a **named count** (register
   discipline — silent truncation reads as "swept everything").
5. Recount the matrix from rows after all dispositions land.

**Out of Scope**:
- New feature work surfaced by a reframed REQ (file it with a matrix pointer).
- The three test-gap rows (Item 3) and the classifier rows (Item 4).

**Success Criteria**:
- [x] REQ-EC-04 and REQ-AS-06 strengthened (each fails under a deliberate mutation of the gate
  it now pins); the 17-strengthen list fully judged.
- [x] 11 reframes + 5 citation fixes landed; baselines byte-identical.
- [x] The ~46 unswept rows completed OR re-filed with a named count and pointer.
- [x] Matrix recounts from rows; no PASS row pins less than its text.

**Required Reading**: BACKLOG `[ITEM7-MATRIX-SWEEP-RESIDUE]` (the full row-by-row list);
`.project/active/matrix-truth/design.md` (the leashed-sweep heuristics + stopping rule); memory
note `verification-matrix-drift-modes`.

**Deliverables**: `.project/active/matrix-sweep-residue/{spec,plan}.md`; strengthened/reframed
tests + citations; matrix updated; re-file entry if the sweep is not completed.

---

### Item 6: D3 Hygiene Tail [1 day] ✅

**Type**: Implementation
**Effort**: 1 day (spec 1h, plan 0.5h, execute 4–6h) — fit: high (Item-5 family style is the
template; each site has file:line); lift: low; risk: low.
**Dependencies**: None (independent). **Schedule before PUSH-DOWN** (touches extraction
surfaces PUSH-DOWN moves).

**Objective**: Harden the four benign-leaning silent sites as one pass, Item-5 family style —
fires-on-shape + silent-on-clean, INV-6 zero-WARNINGs preserved.

**Current State** (the four sites, from discovery §D3):
- ⚠️ loader `.get` defaults on load-bearing fields (silent fallback).
- ⚠️ naive substring `.replace()` in aggregation compile.
- ⚠️ `type_map` "Any" exit-point skip.
- ⚠️ registry alias-rewrite no-not-found branch.

**Scope**:
1. **Verify-then-fix each site** (R4): reproduce the silent shape with a probe/test before
   hardening; reclassify any that doesn't reproduce.
2. **Harden family-style** at the cleanest choke point (loud skip-with-warning or a diagnostic),
   not site-by-site where a family choke exists.
3. **Every new diagnostic gets a fires-on-shape + silent-on-clean pair** (R1 addition).
4. **Preserve INV-6**: clean fixtures still generate with zero WARNINGs.

**Out of Scope**:
- The already-dispositioned residue (`[SANITIZER-MERGE]`, `[SC11-IMPORT-REWRITE]`,
  `[DOTTED-LEAF-PART-BLIND]`) — those stay filed separately.

**Success Criteria**:
- [x] Each site fires a diagnostic on its silent shape and stays silent on clean input (Site 4
  reclassified with named BACKLOG evidence, an allowed R4/spec.md outcome; audited PASS-with-
  findings — see `.project/active/hygiene-tail/audit.md`).
- [x] INV-6 preserved (clean corpora generate with zero WARNINGs); baselines byte-identical.
- [x] Suite green; ruff/mypy not worse.

**Required Reading**: BACKLOG `[D3-HYGIENE-TAIL]`; discovery register §D3;
`reference/12-usage-extraction.md`, `reference/10-output-registry.md`; RN-7
(`warning-reconciliation/release-notes.md` — the noise-discipline precedent).

**Deliverables**: `.project/active/hygiene-tail/{spec,plan}.md`; the four hardened sites + their
test pairs; doc updates per touched component.

---

## Sequencing Rulings

### PUSH-DOWN (relieves the prior sequencing note)
PUSH-DOWN moves reusable SysML semantics out of `extraction/` (`expression_utils`,
`hierarchy_resolver`). TRUTH-DEBT Item 2 (multi-hop, touches `expression_utils` chain-follow)
and Item 6 (hygiene, touches loader / aggregation-compile / registry extraction surfaces) both
edit code PUSH-DOWN would move; Item 1 finalizes the aggregation resolution path
(`input_resolver` is exactly the kind of consolidation PUSH-DOWN cares about). **Ruling:
TRUTH-DEBT lands before PUSH-DOWN**, so the moved code is born correct — the same spirit as the
prior ruling ("PUSH-DOWN starts after PIPELINE-TRUTH Items 5 and 8 land"). The PUSH-DOWN BACKLOG
note is updated: it now additionally waits on TRUTH-DEBT Items 1, 2, and 6.

### MFE
No item in this epic was hard-assigned to a future MFE epic. The deferrals were
"new-capability" (multi-hop) and "hygiene batch" (D3 tail), parked at the prior epic's item
budgets, not bound to MFE. This epic absorbs them; there is no MFE scope note to relieve.

---

## Dependencies

**External**:
- syside license (monthly renewal, no expiry pressure) — Item 1's baseline re-capture,
  Item 2's fixture captures.

**Internal**:
- PUSH-DOWN (P1) — sequenced **after** this epic (ruling above).

**Item Dependency Graph**:
```
Critical path (aggregation/chain resolution)
Item 1 (F4 cutover + typing) ── first, churns aggregation baselines
  └─> Item 2 (multi-hop chains) ── adjacent chain-follow; after 1

Parallel (matrix / classifier / hygiene truth)
Item 4 (classifier fix) ──┐
Item 1 ───────────────────┼─> Item 3 (test gaps: RES-08 after cutover)
Item 1, Item 4 ───────────┴─> Item 5 (sweep residue: after rows settle)
Item 6 (hygiene tail) ── independent; before PUSH-DOWN
```

---

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| EP-key reconciliation collapses distinct params (input EP collides with output channel) | High | Reconcile `resolve_input`'s fallback to the live richer construction BEFORE rewiring; `probe_iv` names the concrete coexisting keys; parity gate against the replaced function |
| Aggregation baseline churn masks a regression during the cutover | Med | R3: one regen at a time, capture scripts only, reviewed diffs; byte-identity gate on non-aggregation baselines (memory: `byte-identity-captured-at-churn`) |
| Multi-hop resolution silently mis-wires a shape no fixture covers | Med | R4 reproduce-first; keep a loud diagnostic for the unresolvable tail; fires-on-shape + silent-on-clean pins |
| Items 1/4 move matrix rows while Item 5 sweeps | Med | Item 5 sequenced after 1 and 4; re-verify the divergent/untested lists at Item 5 spec (prior-epic Item 7 precedent) |
| A filed finding doesn't reproduce (fixing a non-bug) | Med | R4 protocol: per-finding verification before fix; reclassify in the register, don't fix |
| param_groups double-binding split raises mypy above 104 | Low | The Step-5 result is discarded by the Step-6.6 rebuild (likely dead); split into two named vars rather than a root annotation (which was proven not to clear it) |

---

## Timeline

**Total Effort**: ~7–9.5 days

| Item | Effort | Dependencies |
|------|--------|--------------|
| 1. F4 cutover + param-group typing | 2–2.5 d | None (first) |
| 2. Multi-hop chain bindings | 1.5–2 d | Item 1 (soft) |
| 3. Matrix test-gap authoring | 0.5–1 d | Item 1 (soft, RES-08) |
| 4. Classifier fix (flip 5 xfails) | 0.5–1 d | None |
| 5. Matrix sweep residue | 1.5–2 d | Items 1, 4 (soft) |
| 6. D3 hygiene tail | 1 d | None (before PUSH-DOWN) |

---

## Source Documents

- `.project/backlog/epic_pipeline_truth.md` (parent epic — R1–R4, item filings, Lessons Learned) — *epic*
- `.project/reports/20260706_pipeline-truth-epic-report.md` §4 (the complete deferral table) — *report*
- `.project/backlog/BACKLOG.md` (the seven absorbed filings, each with file:line evidence) — *backlog*
- `.project/active/matrix-truth/{design,design-review}.md` + `probes/` (F4 evidence: parity,
  Strategy-D dedup, module drift, EP-key divergence) — *design + probes*
- `.project/research/20260706_pipeline-truth-discovery.md` §D3 (hygiene tail + multi-hop finding) — *research*
- `docs/architecture/verification-matrix.md` (recount from rows) — *reference*

---

## Lessons Learned (Post-Completion)

*Fill in after epic is complete.*

**What Went Well**: TBD
**What Could Improve**: TBD
**Surprises**: TBD

---

**Last Updated**: 2026-07-06
**Next Action**: User review of scope and decomposition; then spec Item 1 (F4 cutover — the
critical-path head) and, in parallel, Item 4 (classifier) and Item 6 (hygiene) as the
no-dependency items.
