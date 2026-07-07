# Implementation Plan: Inherited-Attr Classifier Fix (flip the 5 xfails)

**Status:** Draft
**Created:** 2026-07-07
**Last Updated:** 2026-07-07
**Branch:** truth-debt-epic
**Epic:** TRUTH-DEBT, Item 4 (SC-D); R1–R4

## Source Documents
- **Spec:** `.project/active/classifier-fix/spec.md`
- **Spec review:** `.project/active/classifier-fix/spec-review.md`
- **Design:** `.project/active/classifier-fix/design.md` ← component details, bets, decisions, invariants, gotchas
- **Design review:** `.project/active/classifier-fix/design-review.md` (Revise → incorporated)
- **Epic:** `.project/backlog/epic_truth_debt.md` (Item 4 `:323`; SC-D `:67`; SC-F `:73`; R1–R4 `:114`)

## Two reconciliations the implementer must know up front

Both come from the plan brief being slightly older than the reviewed design. The design wins; recorded here so nobody "corrects" back.

- **Table is 7 rows, not 6.** The brief says "6-row single-column table." The design, revised through design-review, adds a depth-2 fixture case (D2/B2) that lands in `INHERITED_ATTR_PATTERNS`, so the post-fix table is **7 rows — 6 FORMULA (L1, L2, D1, D2, D4 + depth-2) and 1 EXPOSE_COMPUTED (D3)** (`design.md` INV-3, Component Overview). The guard is `len(INHERITED_ATTR_PATTERNS) == 7` and `sum(... == FORMULA) == 6`.
- **mypy gate is ≤ 97, not ≤ 104.** The brief's final gate tightens the design/spec's `≤ 104` to **`mypy ≤ 97`**. Use ≤ 97. `ruff ≤ 17` unchanged.

## Implementation Strategy

**Phasing rationale.** The whole item is contingent on one unproven fact — SysIDE must expose the ancestor PartDef chain off `part_element` in `::`-form QNs (design Bets B1/B2). If it doesn't, every downstream phase is dead. So Phase 0 is a pure live probe that costs nothing to throw away and collapses that uncertainty before any code is written. After that the order follows the data: fix the predicate (Phase 1, unit-testable on a crafted ancestor set with no license), re-capture the one fixture so the suite can finally *see* the flip (Phase 2 — the code fix is invisible to conformance until this runs), collapse the now-honest test table (Phase 3), add the D5 loud diagnostic last so a D5 failure is never confounded with a classification miss (Phase 4, per design Next-Stage Handoff), then sweep docs/matrix/epic in the same change (Phase 5) and close the gates (Phase 6).

**Critical path.** Phase 0 probe passes → Phase 1 predicate fix + depth-2 fixture `.sysml` → Phase 2 re-capture (flip becomes observable) → Phase 3 test collapse. Phases 4–5 are parallelizable against 3 but sequenced after for clean failure attribution.

**First proof point.** Phase 0: a live walk of `unresolvable_attr_probe`'s `Derived Component` prints `target.qualified_name == "UnresolvableAttrProbeLibrary::'Base Component'"` (`::`-form, quotes preserved) and that string is a prefix of the inherited `base_rate` ref QN. That single observation confirms B1 + B2-depth-1 and greenlights the mechanism.

**Overall validation.** Each phase starts with a test (or, for Phase 0, *is* a probe). The byte-identity gate (Phase 2) and the `len == 7` table guard (Phase 3) are the two structural tripwires. Final gates in Phase 6.

---

## Phase 0: Reachability & QN-format probe (THE GATE)

### Goal
Confirm — live, before any code — that the owning part's ancestor PartDef QNs are reachable from `part_element.heritage` and come back in `::`-form matching the inherited ref QNs. This is design Bets **B1** (QN format) and **B2** (heritage → Subclassification → target) at depth-1. If it fails, STOP and re-probe format; do not proceed.

### Assumption Under Test
`part_element.heritage` yields `(relationship, target)` pairs; the `:>` one passes `SysideAdapter.is_instance(rel, "Subclassification")`; `target.qualified_name` is the raw `::`-form (`…::'Base Component'`), the same format as `ref.qualified_name` and `owning_part_qualified_name` — **not** the sanitized `__`-form that `build_element_qualified_name` returns (the `::`-vs-`__` trap, `design.md#data-structure-clarity`).

### Probe (Write This First — it is the test)
```
# Throwaway probe run via the license path (capture script or pytest), NOT a bare `python -c`
# (memory: syside-license-via-scripts-not-dashc). Load unresolvable_attr_probe, then for the
# 'Derived Component' PartDef element:
for rel, target in getattr(part_element, "heritage", []):
    if SysideAdapter.is_instance(rel, "Subclassification"):
        print(target.qualified_name)          # EXPECT: UnresolvableAttrProbeLibrary::'Base Component'
        assert "::" in target.qualified_name   # ::-form, quotes preserved
        assert "__" not in target.qualified_name
# Then confirm the inherited ref QN starts with that + "::":
#   ref('base_rate').qualified_name.startswith("…::'Base Component'::")  → True
```

### Changes Required
**See `design.md#research-findings`** (reachability gate PASSES) and **`design.md#key-bets`** (B1, B2).

- [x] Write a temporary probe (a scratch script under `scripts/` or a temporary `-k probe` test) that loads the fixture through the licensed path and prints/asserts the two facts above.
- [x] Run it. Record the exact printed `target.qualified_name` string in this plan's Implementation Notes.
- [x] Delete the scratch probe (it is not a committed artifact; the depth-2 fixture + re-capture in later phases are the durable proof).

### Validation
**Automated:**
- [ ] Probe prints `::`-form supertype QN and both asserts pass.

**Manual:**
- [ ] The printed QN is a literal prefix of the inherited ref QN (`startswith(qn + "::")`).
- [ ] Decision gate: PASS → proceed to Phase 1. FAIL (e.g. `__`-form, empty, or no Subclassification) → STOP, this is B1/B2 failing; re-probe format before writing any code.

**What We Know Works After This Phase:**
The ancestor chain is reachable in a prefix-matchable form. The mechanism is viable; the rest is bookkeeping.

---

## Phase 1: Step-2b classifier fix + depth-2 fixture source

### Goal
Widen the sibling predicate to accept ancestor-PartDef prefixes, compute the ancestor set transiently, and author the depth-2 fixture source that exercises the transitive walk. No snapshot re-capture yet — this phase is provable by a pure unit test on a crafted `ancestor_part_qns` set (no license).

### Assumption Under Test
The predicate `qn.startswith(own_prefix) OR qn.startswith(any ancestor_prefix)` reclassifies inherited-attr refs to siblings **without** swallowing a top-level CalcDef output (D3). The one known over-correction route — a CalcDef nested *inside* an ancestor PartDef — is accepted as non-regression (design D3), and the corpus is checked for it in Phase 2 (B3).

### Test Stencil (Write This First)
```
# Pure unit test on the predicate seam — crafted inputs, no snapshot, no license.
# tests/unit/ (or tests/conformance/) against _classify_attribute_expression.
def test_inherited_ref_with_ancestor_prefix_is_formula():
    ancestors = {"Lib::'Base Component'"}
    refs = [ref(name="base_rate", qn="Lib::'Base Component'::base_rate")]
    cls = _classify_attribute_expression(..., refs, ancestor_part_qns=ancestors)
    assert cls == ComputedAttributeClassification.FORMULA

def test_top_level_calc_output_stays_expose_computed():   # D3 negative control at unit level
    ancestors = {"Lib::'Base Component'"}
    refs = [ref(name="result", qn="Lib::SimpleCalc::result"),   # CalcDef, NOT an ancestor
            ref(name="base_rate", qn="Lib::'Base Component'::base_rate")]
    assert _classify_attribute_expression(..., refs, ancestor_part_qns=ancestors) \
        == ComputedAttributeClassification.EXPOSE_COMPUTED
```

### Changes Required
**See `design.md#component-overview`** (the three edits) and **`design.md#implementation-notes`** (walk pseudocode, `startswith`-tuple widening, `is_instance` static-call style).

#### 1. Test file
**File:** `tests/conformance/test_computed_attributes.py` (or a unit test module) — write first
- [x] Unit tests for the predicate: inherited-ancestor ref → FORMULA; top-level CalcDef output → EXPOSE_COMPUTED (D3 seam); mixed inherited+local → FORMULA. **Landed in `tests/unit/test_computed_attribute_extraction.py::TestClassifyAttributeExpression`** (alongside the existing predicate unit tests — that is the pure-seam home).

#### 2. Classifier
**File:** `src/sysml_codegen/extraction/computed_attribute_extractor.py`
- [x] Add module-private `_ancestor_part_qns(part_element) -> set[str]` — transitive `heritage`/`Subclassification` walk returning raw `::`-form QNs. Recurses on the raw `target` element. **DEVIATION:** dropped the `adapter` param from the design signature — `SysideAdapter.is_instance` is a static method already called statically in this module (`:57`), so no instance is needed. Cleaner; matches surrounding style.
- [x] **Code comment names the deliberate divergence** from `_supertype_closure` (recurses on raw target → descends into library supertypes; returns `::`-form not `__`-form).
- [x] `_classify_attribute_expression`: added `ancestor_part_qns: set[str] | None = None` param; widened Step-2b to `qn.startswith(part_qn_prefix) or qn.startswith(ancestor_prefixes)`. **DEVIATION:** param defaults to `None` (→ empty prefixes) rather than required — ~15 existing direct-call unit tests are genuine no-ancestor shapes; a default keeps them valid without mechanical churn, and empty-set is the semantically correct value for a part with no supertypes (not a fallback masking an error). Production caller always passes it explicitly. Left 2c/2d untouched.
- [x] `extract_computed_attributes`: computes the ancestor set once per part, threads it into each classify call.

#### 3. Depth-2 fixture source
**File:** `tests/fixtures/unresolvable_attr_probe/{library,design}.sysml`
- [x] Added `part def 'Grandchild' :> 'Derived Component'` with computed attr `grandchild_product = base_rate * base_factor` (both **grandparent** attrs on 'Base Component', so classifying it FORMULA requires the walk to reach 2 hops up). Plus a `grandchild_instance` in design.sysml. JSON NOT re-captured yet (Phase 2).

### Validation
**Automated:**
- [x] New unit tests pass (predicate widening + D3 seam) — 25 passed in the module.
- [x] `ruff check` on touched file passes; `mypy` — no new errors (only pre-existing `agentic_mbse` import-untyped).

**Manual:**
- [x] `is_instance` called in the module's existing static style (`SysideAdapter.is_instance`).
- [x] The `.sysml` depth-2 case: full proof deferred to Phase 2 re-capture (all fixture consumers read the snapshot JSON, not live extraction, so committing `.sysml` pre-recapture is inert — confirmed 123 passed / 5 xfailed).

**What We Know Works After This Phase:**
The predicate reclassifies inherited-attr shapes to FORMULA and preserves D3 EXPOSE_COMPUTED — proven on crafted inputs. The snapshot doesn't reflect it yet (that's Phase 2).

---

## Phase 2: Re-capture the one fixture + byte-identity + B3 verification

### Goal
Re-capture `unresolvable_attr_probe` **only** so the committed JSON records the corrected classifications (5 flips + the new depth-2 FORMULA row); prove every other baseline is byte-identical; and verify B3 (no other corpus model latently desyncs).

### Assumption Under Test
Classification is serialized, so the Phase 1 code fix is invisible to conformance until re-capture (spec L1-2). Re-capture scoped to this one fixture moves exactly the intended bytes and nothing else (INV-2). B3: no baseline computed attr references an inherited attr *or* a CalcDef-nested-under-ancestor (D3 route), so scoping re-capture to this fixture cannot leave another baseline stale.

### Test Stencil (the reviewed diff + the gate are the test)
```
# 1. Re-capture, one fixture only:
uv run python scripts/capture_extraction_snapshots.py unresolvable_attr_probe
# 2. git diff the JSON — EXPECT only:
#    - 5 classification strings expose_computed → formula (L1,L2,D1,D2,D4)
#    - D3 unchanged (expose_computed)
#    - compilability/compiled_expression UNCHANGED for all 6 pre-existing rows (all stay
#      manual_required / null — inherited refs aren't in input_names, design.md Research Findings)
#    - NEW depth-2 computed-attr object (formula + manual_required) + its design-attribute entry
#    - captured_at churn → REVERT (timestamp-only; memory byte-identity-captured-at-churn)
```

### Changes Required
**See `design.md` INV-2** (byte-identity carve-out), **`design.md#validation-approach`** steps 1/4/5, **`design.md#key-bets`** B3, and **memory `byte-identity-captured-at-churn`**.

- [x] Run the scoped re-capture (needs syside license via the capture script — not `-c`).
- [x] Review the JSON diff against the expected list above; it is a reviewed R3 diff, not blind.
- [x] Revert `captured_at` timestamp-only churn (run the byte-identity gate: timestamp-only diff check + revert so only the intended content moves).
- [x] **Byte-identity gate:** confirm only `tests/fixtures/unresolvable_attr_probe/` files move (the `{library,design}.sysml` from Phase 1 + `extraction_snapshot.json`); every other baseline byte-identical.
- [x] **B3 verification (record verdict in Implementation Notes):** grep the corpus for (a) computed attrs referencing inherited attrs and (b) a CalcDef nested under an ancestor PartDef; or re-capture-and-diff `fusion_tea` once. R4 says reproduce, don't static-read. If either shape exists, widen scope deliberately and stop to reconsider.

### Validation
**Automated:**
- [x] Byte-identity gate green except the carved-out fixture files.
- [x] `unresolvable_attr_snapshot` now shows 5 FORMULA + D3 EXPOSE_COMPUTED + 1 depth-2 FORMULA = 7 computed attrs (the `test_fixture_has_expected_count` will need its `6` → `7` update in Phase 3).

**Manual:**
- [x] JSON diff matches the expected-only list; nothing extra moved.
- [x] B3 verdict recorded (expected: neither shape present in the corpus; if present, escalate).

**What We Know Works After This Phase:**
The flip is real and observable in the committed snapshot; the depth-2 transitive walk produced a FORMULA row (B2 lifted from "depth-1 proven" to "transitive exercised"); no other baseline desyncs.

---

## Phase 3: Honest test collapse (delete the xfail, single-column 7-row table, re-key pins)

### Goal
Rewrite the conformance table and its consumers to record post-fix truth as real, positively-asserting tests — killing both the empty-parametrization trap and the silent-narrowing trap.

### Assumption Under Test
The five (now six) cases become **real PASSes keyed on a literal `FORMULA` expectation**, never a vacuous xfail or a zero-case parametrization (spec [HARD] no-fake-test; INV-3). The xfail count drops 5 → 0.

### Test Stencil (this phase IS the test edit)
```
# Single authoritative column; 7 rows; guard against collapse:
INHERITED_ATTR_PATTERNS = {  # (owning_part, attr): (classification, description)
    ("Derived_Component", "inherited_product"): (FORMULA, "L1 ..."),
    ... L2, D1, D2, D4 → FORMULA ...
    ("Design_Derived", "mixed_expose"): (EXPOSE_COMPUTED, "D3: calc output + inherited — correct"),
    (<depth-2 owning part>, <attr>): (FORMULA, "depth-2: grandparent attr ref"),
}
assert len(INHERITED_ATTR_PATTERNS) == 7
assert sum(1 for v in INHERITED_ATTR_PATTERNS.values() if v[0] == FORMULA) == 6

def test_inherited_attr_classification(..., key, expected):   # asserts the single literal column
    assert ca.classification == expected_classification
```

### Changes Required
**See `design.md#component-overview`** (table + tests) and **`design.md` INV-3, INV-1, D4**; spec [HARD] no-fake-test (`spec.md:122-140`).

**File:** `tests/conformance/test_computed_attributes.py`
- [x] Collapse `INHERITED_ATTR_PATTERNS` (`:642`) to a **single classification column**, 7 rows (6 FORMULA + D3), add the `len == 7` / `sum(FORMULA) == 6` guard.
- [x] Rewrite `test_inherited_attr_classification` (`:726`) to assert the single literal column for all 7 rows (INV-1 D3 negative control included here as a real row).
- [x] **Delete `test_misclassification_documented`** (`:764`) — its `v[0] != v[1]` filter would collapse to zero cases (D4). This removes the 5 xfails.
- [x] Update `test_fixture_has_expected_count` (`:696`) `6` → `7`.
- [x] **Re-key `test_no_compiled_expressions`** (`:815`): today it iterates EXPOSE_COMPUTED (post-fix narrows silently to D3 only, should-fix #2). Extend it to positively assert the **6 FORMULA cases are `MANUAL_REQUIRED` + `compiled_expression is None`** (and keep D3). This is the honest pin that the flipped attrs produce no module and don't compile.
- [x] Keep `test_inherited_refs_have_supertype_qn` (`:794`) green; reword its docstring to "now treated as sibling" (INV-4 — root cause still true; the fix reinterprets, doesn't change SysIDE).

### Validation
**Automated:**
- [x] `test_inherited_attr_classification` green over 7 literal rows; `test_no_compiled_expressions` green over 6 FORMULA (MANUAL_REQUIRED + None) + D3.
- [x] `test_inherited_refs_have_supertype_qn` green; `test_misclassification_documented` gone.
- [x] Suite summary line: **xfailed 5 → 0** (verify the number actually moves, not just that the suite is green).

**Manual:**
- [x] The collapse guard (`len == 7`) is present so an accidental empty/short table fails loudly.

**What We Know Works After This Phase:**
The contract is positively pinned: a reader points at PASS tests asserting inherited-attr refs classify FORMULA + are MANUAL_REQUIRED, not at an absent xfail. No fake/empty test.

---

## Phase 4: D5 graph-builder loud diagnostic + fires-on-shape / silent-on-clean pair

### Goal
Retire the residual generation-time silence: WARN when a FORMULA computed attribute reaches module-build without being FULLY_COMPILABLE (design must-fix #1 → D5). Land it after the classification flip is green so a D5 failure is never confounded with a classification miss (design Next-Stage Handoff).

### Assumption Under Test
The D5 branch fires exactly on the FORMULA+MANUAL_REQUIRED shape and is silent on clean models (INV-5 / INV-6). The corpus scan says only `deep_cross_scope_probe` (a warns-by-design drift pin) has this shape, so INV-6 (clean fixtures → zero WARNINGs) holds.

### Test Stencil (Write This First — R1 fires-on-shape + silent-on-clean pair)
```
def test_formula_not_compilable_warns_no_module():   # fires-on-shape (INV-5)
    ca = ComputedAttributeData(classification=FORMULA, compilability=MANUAL_REQUIRED, ...)
    graph = build_computation_graph(... with ca ...)
    assert <warning emitted naming the attr, no module produced>

def test_formula_fully_compilable_builds_module_no_warning():   # silent-on-clean (INV-6)
    ca = ComputedAttributeData(classification=FORMULA, compilability=FULLY_COMPILABLE, ...)
    graph = build_computation_graph(... with ca ...)
    assert <module built, no warning>
```

### Changes Required
**See `design.md#architecture`** (Site 2), **`design.md` D5, INV-5, INV-6**, and **`design.md#implementation-notes`** (the `deep_cross_scope_probe` subset-check note).

**File:** `src/sysml_codegen/resolution/graph_builder.py` (Step-6.5 loop, `:269-288`)
- [ ] Add the `FORMULA and not FULLY_COMPILABLE → WARN "no module produced" + skip` branch. Keep the FULLY_COMPILABLE and EXPOSE_CHAIN_TENTATIVE arms untouched. Warning names the attr; it is a runtime log, not serialized.

**File:** D5 test module (crafted `ComputedAttributeData` unit tests — cleaner than routing through a fixture, `design.md#test-doc-surface`)
- [ ] fires-on-shape + silent-on-clean pair (above).

### Validation
**Automated:**
- [ ] D5 pair green.
- [ ] **Full suite green** including `deep_cross_scope_probe` — it gains one new warning; confirm its test uses a subset/`any()` warning check (`test_deep_cross_scope_probe.py:97-99`), not an exact-set/count assertion. If an exact-warning assertion trips, it named a previously-silent drop and should be updated to include the new loud line.
- [ ] `deep_cross_scope_probe` committed `baseline_outputs/` bytes unaffected (warnings aren't generated code).

**Manual:**
- [ ] Confirm no clean corpus model emits the new WARN (INV-6): the only firing fixture is the probe.

**What We Know Works After This Phase:**
The generation-time silent drop is now loud at the exact `graph_builder.py:269-288` site, on both live and from-snapshot generation, proven by the fires-on-shape test; clean models stay zero-WARNING.

---

## Phase 5: R1 docs / matrix / epic sweep (same change)

### Goal
Move the doc/matrix/REQ text to the fixed state and correct the loud→silent severity inversion — in the same change as the code (R1). Leave no ghost.

### Assumption Under Test
Every "loud" claim tied to *this* misclassification is corrected toward "silent no-op," cited to code; the matrix recount holds; the contract is positively pinned by a REQ row.

### Changes Required
**See `design.md#test-doc-surface`** and **`design.md` note #5**; spec [INFERRED] items (`spec.md:181-191`).

**File:** `docs/architecture/reference/16-computed-attributes.md`
- [ ] Known-Issues "Inherited Attribute Misclassification" (`:365-408`) → rewritten to the fixed state.
- [ ] Pseudocode `⚠ KNOWN BUG` (`:133`) and the supertype-namespace note (`~:114-117`) → updated to describe the fixed behavior.
- [ ] Impact section's "silent no-ops" (`:392-395`) → **confirmed correct** (doc 16 was right) and tied to the new D5 diagnostic.

**File:** `docs/architecture/verification-matrix.md`
- [ ] "Known contract (Item 7)" block (`:136`) → rewritten from "confirmed bug / deferred" to fixed; the "**loud** (EXPOSE_COMPUTED rejection)" phrase corrected toward **silent no-op**, cited to `graph_builder.py:269-288` / the e2e test.
- [ ] Flip the classifier rows UNTESTED-family → PASS with citations; add a positive REQ-CA row pinning "inherited-attr ref → sibling → FORMULA."
- [ ] Recount from rows (matrix recount holds).

**File:** `.project/backlog/epic_truth_debt.md`
- [ ] Sweep **every** "loud" tied to this misclassification, not just one line: summary `:16` ("classifier fix behind a loud xfail"), overview `:41` ("Five xfail cases lock a **loud** … misclassification"), and Item-4 `:340` ("The misclassification is **loud** (rejection, not silent…)") — all corrected toward silent, cited.

**File:** `.project/backlog/BACKLOG.md`
- [ ] File the follow-on `[TRUTH-DEBT-INHERITED-FORMULA-COMPILE]` naming the `input_names` enrichment (making inherited-attr FORMULAs actually compile is out of scope here — D1 / Non-Goals).

### Validation
**Automated:**
- [ ] `grep -rn "loud" docs/architecture/verification-matrix.md .project/backlog/epic_truth_debt.md` returns no occurrence tied to the inherited-attr misclassification (other "loud" uses, e.g. 3+-segment chain rejection, are untouched).

**Manual:**
- [ ] The e2e integration suite (`test_computed_attributes_e2e.py:44-48`) did **not** move — confirmed because it runs on `attr_expr_probe` (zero `:>`), not `unresolvable_attr_probe` (spec L3-3). If a check finds an inherited-attr computed attr there, those lists move too, in this change.
- [ ] Matrix recount consistent with the row flips.

**What We Know Works After This Phase:**
Docs, matrix, and epic describe the fixed behavior with the correct severity; the contract is positively pinned; the follow-on is filed. No reader inherits a ghost.

---

## Phase 6: Final gates

### Goal
Prove the whole change is green and within budget.

### Validation
- [ ] Full suite green; **suite summary `xfailed` count 5 → 0** (verify the summary line moved).
- [ ] `ruff check src/` ≤ 17.
- [ ] `mypy src/` ≤ 97  *(tightens the design's ≤ 104 — see reconciliation note at top)*.
- [ ] Byte-identity gate: only `tests/fixtures/unresolvable_attr_probe/` moved (re-confirm after all phases; `captured_at` reverted).
- [ ] Matrix recount from rows holds.

**What We Know Works After This Phase:**
Item 4 debt retired: classifier fixed, snapshot re-captured and reviewed, xfails flipped to real PASSes, D5 loud diagnostic added, docs/matrix/epic corrected — in one change.

---

## Environment Setup

**See CLAUDE.md.** Key: re-capture and any live probe need the **syside license**, which loads via the capture script / full pytest — **not** a bare `python -c` (memory: `syside-license-via-scripts-not-dashc`). Re-capture command: `uv run python scripts/capture_extraction_snapshots.py unresolvable_attr_probe`.

## Risk Management

**See `design.md#potential-risks`.** Phase-specific:
- **Phase 0:** QN-format mismatch (B1) — the probe is the cheap test; a non-`::`-form result is the STOP signal before any code.
- **Phase 2:** latent baseline staleness (B3) — grep both shapes (inherited-attr refs; nested CalcDef under ancestor) and record the verdict; captured_at churn — revert timestamp-only diff.
- **Phase 3:** table-collapse regression (INV-3) — the `len == 7` / `sum(FORMULA) == 6` guard fails loudly on an accidental empty/short table.
- **Phase 4:** D5 warning breaks an unrelated fixture's exact-warning assertion — only `deep_cross_scope_probe` fires; confirm its subset check; run full suite.

## Implementation Notes

[TO BE FILLED DURING IMPLEMENTATION]

### Phase 0 Completion
**Status:** GATE PASSED (2026-07-07). Probe ran via licensed extractor path (`SysMLDataExtractor([unresolvable_attr_probe]).load_models()`), then walked `'Derived Component'.heritage`.
**Recorded fact — the printed `str(target.qualified_name)`:** `"UnresolvableAttrProbeLibrary::'Base Component'"` (`::`-form, quotes preserved, no `__`).
**Prefix confirmation:** inherited ref `base_rate` QN = `"UnresolvableAttrProbeLibrary::'Base Component'::base_rate"` → `startswith(supertype_qn + "::")` TRUE. `base_factor` likewise. Own attr `local_multiplier` QN sits under `'Derived Component'::` and correctly does NOT match Base. B1 (QN `::`-form) + B2-depth-1 (heritage→Subclassification→target) both confirmed.
**DEVIATION (recorded):** `target.qualified_name` returns a `syside.core.QualifiedName` object, not a `str`. The walk must apply `str(...)` before prefix use — the design pseudocode (`design.md:354`) already does (`str(getattr(target, "qualified_name", "") or "")`), so no design change; the classifier's existing `part_qn` at `extractor.py:194` also already `str()`-wraps. Probe deleted (scratch, not committed).

### Phase 2 Completion
**Re-capture command DEVIATION:** the script takes `--fixtures NAME`, not the positional form the plan/design wrote. Ran `uv run python scripts/capture_extraction_snapshots.py --fixtures unresolvable_attr_probe`.

**Snapshot diff (reviewed R3):** Only `unresolvable_attr_probe/extraction_snapshot.json` moved (byte-identity gate GREEN — no other baseline snapshot changed; `git status` confirmed). captured_at reverted (timestamp-only churn → 0 in diff). Content changes, ALL explained and correct:
- **5 classification flips** `expose_computed → formula` (L1,L2 on Derived_Component; D1,D2,D4 on Design_Derived). D3 `mixed_expose` unchanged (expose_computed). ✓
- **1 new computed-attr object** `grandchild_product` (Grandchild) = FORMULA + manual_required + compiled=None — the depth-2 transitive walk PASSED (B2 lifted depth-1→transitive). ✓
- **compilability/compiled_expression** unchanged for all pre-existing rows (all manual_required / null — inherited refs stay outside input_names). ✓
- **DEVIATION from design INV-2 (recorded):** the diff is LARGER than INV-2's literal enumeration ("5 strings + depth-2 row + its design-attr entry"). INV-2 overlooked a correct downstream effect: `_extract_and_filter_computed_attributes` (`pipeline_builder.py:119`) REMOVES FORMULA-classified attrs from `design_attributes` (false-entry-point prevention, per its docstring). So the 5 flipped attrs are correctly REMOVED from the snapshot's `design_attributes` section (they were kept while EXPOSE_COMPUTED). `mixed_expose` (still EXPOSE_COMPUTED) correctly stays. Plus grandchild_instance's 3 `:>>` redefinitions land in the redefinitions section, and SimpleCalc's `source_hash` updates because library.sysml genuinely changed. **Every moved byte is a direct consequence of the flip or the depth-2 fixture — none is unexplained drift.** Verified field-by-field.

**B3 verdict (R4 — reproduced in memory, not static-read):** wrote a throwaway `scripts/_b3_check.py` that re-ran the FIXED classifier LIVE against all 12 `:>`-using baselines and diffed classifications vs their committed snapshots (mutated nothing; deleted after). **NO classification drift attributable to the Item-4 ancestor-prefix fix** — neither shape (a) computed-attr-referencing-inherited-attr nor (b) CalcDef-nested-under-ancestor exists in any baseline; re-capturing only unresolvable_attr_probe cannot desync another. **One orthogonal drift surfaced** (`ife_plant` `radial_build.magnet_volume_total`: committed `expose_pure` → live `expose_chain_tentative`) — CONFIRMED pre-existing by re-running the check with the pre-Phase-1 classifier (`0f75062`): it reproduces without my change. This is Item-2 multi-hop-chain staleness (my ancestor-prefix change cannot produce that transition — it lives in the `not calc_refs` tentative gate I never touch). Filed as a follow-on (Phase 5 BACKLOG); NOT re-captured here (scope discipline — mixing Item-2 drift into the Item-4 change would break the carve-out).

**Post-recapture test state (expected, resolved by Phase 3):** 6 conformance failures — `test_fixture_has_expected_count` (6→7) + 5× `test_inherited_attr_classification` (old `actual_cls=expose_computed` column vs new snapshot `formula`). These are the table-vs-snapshot mismatches Phase 3's collapse fixes.

### Phase 3 Completion
Collapsed `INHERITED_ATTR_PATTERNS` to a single-column 7-row table (6 FORMULA + D3 EXPOSE_COMPUTED) with the `len == 7` / `sum(FORMULA) == 6` module-level guard (fails loudly on collapse). Rewrote `test_inherited_attr_classification` to assert the single literal column (real positive PASSes, no vacuous xfail). **Deleted `test_misclassification_documented`** — removes all 5 xfails (grep confirms zero `xfail` anywhere in tests/). Count 6→7. Re-keyed `test_no_compiled_expressions` to positively assert 6 FORMULA are MANUAL_REQUIRED + compiled=None (+ D3), so it can't silently narrow. Reworded `test_inherited_refs_have_supertype_qn` docstring to "now treated as sibling" (INV-4 kept). Also rewrote the stale C3 FINDING comment block to the fixed CONTRACT (no ghost in the test file). **Result:** this file 50 passed / 0 xfailed (was 26 + 5 xfailed). Other fixture consumers (test_extractor, test_uncovered_params, unit) all green. Test-file ruff unchanged (18 pre-existing, 0 new; not in the `src/` gate).

### Phase 4–6 Completion
_[fill]_

---

**Status:** Draft → In Progress → Complete
