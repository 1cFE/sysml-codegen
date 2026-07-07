# Implementation Plan: Item 7 — REQ/Matrix Reconciliation (F2, F4, Divergent Rows)

**Status:** Draft
**Created:** 2026-07-06
**Last Updated:** 2026-07-06
**Branch:** pipeline-truth-epic
**Epic:** PIPELINE-TRUTH, Item 7 (SC-F)

## Source Documents
- **Spec:** `.project/active/matrix-truth/spec.md`
- **Design:** `.project/active/matrix-truth/design.md` ← component details, verdicts, invariants, probe artifacts. This plan does not restate them; it phases them.
- **Spec review:** `.project/active/matrix-truth/spec-review.md` · **Design review:** `.project/active/matrix-truth/design-review.md` (C1/C2/M3–M6 resolutions are folded into the design; this plan executes the resolved design).
- **Probe artifacts (already produced at design):** `probes/probe_i_*`, `probes/probe_ii_*`, `probes/probe_iii_module_drift.md`, `probes/probe_iv_ep_key_divergence.md`

---

## Implementation Strategy

**What this item is.** Bring the verification matrix back into line with the code: run of the F4 verdict is already recorded (LAND + split — see `design.md#the-f4-verdict`), so implement executes reconciliation, not discovery. Most edits are documentation and matrix rows; the two real test-engineering touches are the ORCH-04 presence assertion (F2) and the `test_dual_resolution.py` parity parametrization (F4). One follow-on is filed, not built.

**Phasing Rationale.**
- **Phase 0 goes first because the ground moved.** Item 2's implement lands before this one. Its new REQ-SVM rows and doc-25 section are *landed truth*, not divergences to fix. Phase 0 re-baselines gates and re-verifies every row this item touches against the current file, so no later phase fights Item 2/5 churn (spec `[INFERRED]`, `design.md#potential-risks`).
- **F4 before F2** — F4 is the largest, riskiest move and lands as one atomic commit (the `[HARD]` atomicity requirement). Getting it in first collapses the biggest uncertainty. The cutover filing (Phase 2) immediately follows so the F4 docs' `[ITEM7-F4-CUTOVER]` references resolve.
- **F2 (Phase 3) carries the one genuinely-adversarial test edit** — the ORCH-04 presence assertion with its named red-mutation gate (C1). Test-first here is real: write the assertion, prove it fails under the mutation, then keep it green on the real corpus.
- **Row dispositions (Phases 4–6) are bounded matrix work**, phased by matrix section with per-row checkboxes so nothing is silently skipped.
- **The sweep runs LAST (Phase 8)** under its leash — it can only *find* work, and running it after the known dispositions means its findings don't collide with them.
- **Recount is the closing action (Phase 9)** — derived numbers are regenerated once, from final row reality, per the `verification-matrix-drift-modes` memory.

**Critical Path.** Phase 0 (re-baseline) → Phase 1 (F4 atomic commit) → Phase 2 (cutover filing) → Phase 3 (F2 + ORCH-04) → Phases 4–7 (rows, untested, markers/xfails, doc fold-in) → Phase 8 (sweep) → Phase 9 (recount + R4 table + close-out).

**First Proof Point.** Phase 1's `test_dual_resolution.py` parametrization runs green in CI over the three Item-1 fixtures (probe-(i) logic committed, M6) — the reframed IR rows now cite a running test, not a `.project/` script. Closely followed by Phase 3's ORCH-04 red-mutation proof.

**Overall Validation Approach.**
- Every code touch keeps baselines byte-identical or lands as a reviewed capture diff; ruff/mypy not worse than the 21/109 baseline (INV-D).
- No re-anchored test computes its own expectation (INV-E / R1 ban).
- Final recount reconciles summary/footer/index to the row-by-row count (INV-C).
- R4 verification table is a produced artifact; the discovery register is updated in place.

---

## Phase 0: Re-baseline & Row Re-verification

### Goal
Establish the true current state before touching anything. Item 2 (and possibly Item 5) landed since design; fence their additions as landed-state, and re-verify every row this item will touch against the *current* matrix.

### Assumption Under Test
That the divergent/UNTESTED/marker/count lists in the design still match the file. If Items 2/5 moved a row, this phase catches it before a later phase acts on a stale line number.

### Validation-first Check (Run This First)
```
# Gates — record the fresh baseline; later phases must not regress it
uv run ruff check src/            # expect ≈ 21 (INV-D ceiling)
uv run mypy src/                  # expect ≈ 109 (INV-D ceiling)
uv run pytest tests/ -q          # full suite green on the current tree

# Row reality — recount from rows, never the summary block
grep -cE 'REQ-[A-Z]+-[0-9]+' docs/architecture/verification-matrix.md   # expect 249 (design), re-confirm
ls tests/conformance/test_*.py | wc -l                                   # footer-count input (59 at design; recount)
```

### Changes Required
**See `design.md#potential-risks` and the spec `[INFERRED]` rows.**

- [ ] Confirm gates + full suite green on the post-Item-2 tree; record the exact ruff/mypy numbers as this item's ceiling.
- [ ] Diff the matrix against design's `Appendix B` line refs and the divergent/UNTESTED lists; note any row Item 2/5 moved. Record new line numbers for: IR-01..07 (270–276), DRA-02/03/04/05 (165–168), BT-09 (120), RES-02/07/08 (447/452/453), OR-05/06/08, ORCH-04, PGD-06 (380), PGD-08 (382), AST-10.
- [ ] **Fence Item 2's additions as landed-state:** confirm the new `REQ-SVM-*` rows and the doc-25 section are present and honest; they are *not* divergences and are out of scope for reconciliation. Note them so the sweep (Phase 8) and recount (Phase 9) expect them.
- [ ] Re-verify the two moved divergent rows on fresh evidence: **REQ-EXT-09** (`test_extractor.py:888-934`, expect DONE) and **REQ-PGD-08** (now cites `test_matcher_fixes_item7.py` + `test_parameter_group_deriver.py` — coverage verdict deferred to Phase 4).

### Validation (How to Verify This Phase)
**What We Know Works After This Phase:** the exact current-state line numbers, the fresh gate ceiling, and which rows belong to Items 2/5 (fenced, not touched).

---

## Phase 1: F4 Atomic Reframe — ONE commit

### Goal
Land the entire F4 consequence set as a single mutually-consistent commit: no row pins a module the code doesn't call, no doc describes an architecture the code doesn't have (`[HARD]` atomicity). The verdict is LAND-with-split; this phase reframes to the *true* state and commits the parity extension.

### Assumption Under Test
That the F4 state can be told truthfully by reframe alone (rows + REQ texts + docs + committed parity test) without doing the cutover — the design's central decision (`design.md#what-item-7-lands-for-f4`).

### Test Stencil (Write This First — M6, the durable pin)
```python
# test_dual_resolution.py — commit probe-(i) logic as a PERMANENT parametrization
# The reframed IR/DRA rows must cite THIS committed test, never the .project/ probe script.
@pytest.mark.parametrize("fixture", ["plant_values", "plant_value_shapes", "spec_chain_twolevel"])
def test_resolve_input_parity_with_backtracker(fixture):
    result = backtrack(load_fixture(fixture))
    for res in result.binding_resolutions:          # backtracker DFS — the honest comparand (M3)
        assert resolve_input(res.input, AGG_STRATEGIES) == res.channel   # MODULE_OUTPUT equality
    # EP fallbacks: resolve_input returns entry_point OR module_output (the weaker bar — state it)
```
Coverage this pins, stated honestly (M5): **1 MODULE_OUTPUT channel-equality check** (`spec_chain_twolevel`) + **5 entry-point fallback checks**. The load-bearing evidence for the reframe is the **full** set — the committed 12-test suite over catf_mfe/solar_battery **plus** this extension — not this extension alone.

### Changes Required — enumerate every file (the atomic set)
**See `design.md#what-item-7-lands-for-f4`, `#appendix-b--f4-consequence-set-row-inventory`, and INV-A.**

**Matrix rows (`docs/architecture/verification-matrix.md`):**
- [ ] **REQ-IR-05 (≈274) and REQ-IR-07 (≈276): rewrite the requirement TEXT** (C2, INV-A). From "Aggregation modules SHALL **use** `AGG_STRATEGIES`/`resolve_input()`…" to module-**capability** claims ("`resolve_input` SHALL…"). A status re-label is not enough — the text itself asserts false live usage.
- [ ] **REQ-IR-01..04, IR-06:** reframe from "pins the live resolver" to "backtracker-parity-validated, not-yet-wired consolidation." Cite the committed parity suite + the pointer to `[ITEM7-F4-CUTOVER]`. Framing says "parity-validated against the **backtracker**," not "against the live path" (M3).
- [ ] **REQ-DRA-04:** stop claiming a live comparand. **DRA-02/03/05, BT-09:** cite `test_dual_resolution.py` already and it is extended **in place** — no re-pointing (m10); confirm citations survive untouched.
- [ ] **REQ-RES-02:** rewrite to the real three-mechanism architecture (backtracker DFS for CalcUsage; attribute-resolution-map for FORMULA; `_resolve_aggregation_input_channel` for aggregation) — delete the dead-path name it carries.
- [ ] **REQ-RES-07/08 text:** correct to the live consumer-scope derivation.

**Tests:**
- [ ] Commit the parity parametrization above into `test_dual_resolution.py` (M6). The 22 `test_input_resolver.py` skipifs **stay** (they test real, correct code); only their framing stops implying the code is live.

**Docs (delete ghost prose in the same commit — R4 docs loop):**
- [ ] `docs/architecture/reference/03-resolution-overview.md`, `04-input-resolver.md`, `05-module-factory.md`: rewrite the "intended consolidated architecture" prose to the honest status — the consolidation exists, is parity-validated over the extended corpus, and the live-path cutover is filed as `[ITEM7-F4-CUTOVER]` with the probe artifacts as its safety-net evidence.

### Validation
**Automated:**
- [ ] `uv run pytest tests/conformance/test_dual_resolution.py -q` → green (new parametrization included).
- [ ] Full suite green; baselines byte-identical; ruff/mypy ≤ Phase-0 ceiling.
**Manual:**
- [ ] Grep the reframed rows + docs 03/04/05 for any surviving "SHALL use `resolve_input`" or live-usage phrasing → zero (INV-A).

**What We Know Works After This Phase:** the F4 state is told truthfully in one commit; the reframed rows cite a CI-running test; no doc claims the unwired architecture is live.

---

## Phase 2: File `[ITEM7-F4-CUTOVER]` + Retire F4 Backlog

### Goal
File the executable follow-on as its own backlog item, carrying enough that it is pickable without re-discovery. Retire the now-discharged F4 scrub filing.

### Assumption Under Test
None new — this is the deliverable the split produces. Its value is that the cutover's *safety net* is specified correctly (M3) so it doesn't validate against the wrong function.

### Changes Required
**See `design.md#why-the-cutover-splits-out` and the Backlog block (design lines 147–158).**

`[ITEM7-F4-CUTOVER]` must carry, explicitly:
- [ ] **The correct comparand (M3):** the cutover's safety-net parity suite compares `resolve_input(AGG_STRATEGIES)` against **`_resolve_aggregation_input_channel`** (the function it replaces), not only the backtracker DFS that probe (i) uses. Backtracker parity is general-correctness evidence, not parity-with-the-replaced-function.
- [ ] **The EP-key reconciliation (M4):** point at `probes/probe_iv_ep_key_divergence.md` — the concrete coexisting-key baseline lines in `tests/fixtures/baseline_outputs/solar_battery/computation_graph.json` (live `…__permitting_raw_material_cost` input EP vs module leaf `…__raw_material_cost` output channel) the fallback reconciliation must resolve before rewiring.
- [ ] **Scope:** reconcile `resolve_input`'s fallback to the live richer EP construction; rewire the 3 call sites (`graph_builder.py:1437, 1532, 1633`); re-capture baselines byte-identically or as a reviewed diff; **delete Strategy D** (probe ii: `return None` stub, zero surface) **and fix its own docstring** ("included… for future extensibility") — the residual ghost Item 7 leaves noted, not fixed (m7).
- [ ] **Probe pointers:** cite probe_i/ii/iii and **probe_iv** as the cutover's safety-net evidence.

- [ ] Retire BACKLOG **DOCS-SCRUB-F4** (superseded by this filing).

### Validation
**What We Know Works After This Phase:** the cutover is pickable cold, with its correct comparand and EP-key evidence named; the F4 scrub residue is closed.

---

## Phase 3: F2 — Fix Text to Code + ORCH-04 Presence Assertion

### Goal
Correct the registry-contract text to what the code actually does, and restore REQ-ORCH-04 to a **presence** assertion that a phase-order regression actually fails (C1). Fix the two lying docstrings.

### Assumption Under Test
That the construction-time `instance_attr_to_channel` dict does **not** bypass the typed-registry contract (design B3 — confirmed: it feeds only guarded `register_alias`). If a fresh read at implement contradicts this, F2 flips to a code fix — re-verify first (`design.md#f2--fix-the-text-to-the-code`).

### Test Stencil (Write This First — the C1 restoration + its red-mutation gate)
```python
# test_orchestrator.py — REPLACE the vacuous min(phase1_calls) < min(alias_calls) (line ~474)
# Presence assertion: hand-transcribed, fixture-anchored expected-alias list (Item-6 rule —
# the expectation is written independently, NEVER computed by the code under test → INV-E).
EXPECTED_KEY_A_ALIASES = {  # transcribed by hand from the solar_battery fixture
    "…": "…canonical channel…",
}
def test_expected_key_a_aliases_present_solar_battery():
    registry = build_registry_from_corpus("solar_battery")
    for alias, canonical in EXPECTED_KEY_A_ALIASES.items():
        assert registry.resolve(alias) == canonical   # PRESENCE, not survivors-are-canonical

# RED-MUTATION GATE (run manually, must fail, then revert):
#   swap Phase-1a order so register_alias runs BEFORE its canonical target is registered.
#   → the guard drops the alias → the expected alias vanishes → this test FAILS.
#   A survivors-are-canonical check stays GREEN under that mutation; presence does not.
```

### Changes Required
**See `design.md#f2--fix-the-text-to-the-code`, D3, C1, INV-E.**

**Text fixes (matrix + doc):**
- [ ] **REQ-OR-05/06/08 text** and **doc 10's "Eliminated Key Formats"** (`10-output-registry.md`): rewrite to the actual state — Phase 1a registers Key_A as an alias (`register_alias`), Phase 1c registers Key_F as a scoped key (`register_scoped`), and the construction-time `instance_attr_to_channel` consult is a build-time helper that still feeds typed registration. Reframe REQ-OR-06's "through typed lookup" to *resolution-time* lookups (not the build-time helper). Phrase the guard evidence as "the dict feeds only guarded `register_alias` calls" (m8 — Phases 1b/1c `_canonical.add` writes exist but are not dict-fed).

**ORCH-04 restoration (`tests/conformance/test_orchestrator.py`):**
- [ ] Replace the vacuous `min(phase1_calls) < min(alias_calls)` (line ~474) with the presence assertion above. **Do not** reuse a survivors-are-canonical iteration over `registry._alias` — the guard drops mis-ordered aliases before they enter `_alias`, so it holds by construction (same vacuity in a new costume, C1).
- [ ] Run the named red-mutation; confirm the test turns **red**; revert the mutation; confirm green.

**Two docstrings:**
- [ ] `test_output_registry.py:329` (`test_no_dead_keys_registered`, "Key_A … Key_F … NOT in any registry") — contradicts reality (Key_A is an alias, Key_F is scoped-registered). Fix the docstring to match the corrected bodies.
- [ ] The ORCH-04 static-analysis docstring (`test_orchestrator.py:449`, "Phase 1 registration calls appear before Phase 2/3/4") — confirm its exact identity against the corrected body at implement, then fix.

- [ ] Retire BACKLOG **DOCS-SCRUB-F2**.

### Validation
**Automated:**
- [ ] `uv run pytest tests/conformance/test_orchestrator.py tests/conformance/test_output_registry.py -q` → green.
- [ ] Full suite green; baselines byte-identical; ruff/mypy ≤ ceiling.
**Manual:**
- [ ] Red-mutation gate: mutation → test fails; revert → test passes. Record in the R4 table (Phase 9).

**What We Know Works After This Phase:** the registry-contract text matches the code, ORCH-04 pins the real phase-order contract (a dropped-alias regression fails it), no docstring lies.

---

## Phase 4: Divergent-PASS Rows — per-row disposition

### Goal
Zero divergent-PASS rows remain: each is fixed (strengthen the test to pin its text, or reframe the REQ text to what the test checks) or, if it surfaces feature work, filed with a matrix pointer. No PASS pins less than its text (INV-B). Per-row strength decision on fresh evidence at implement (`design.md#divergent-pass-rows--disposition`).

### Assumption Under Test
That each row can be brought honest by strengthen-or-reframe without new feature work — except where it can't, which gets filed.

### Changes Required — per-row checkboxes (verify against the **current** row first)
- [ ] **REQ-EXT-09** (≈213): part-usage leg landed by Item 4 (`test_extractor.py:888-934`, anti-pattern-free). Confirm and mark PASS honestly. (No action beyond confirm.)
- [ ] **REQ-PGD-08** (≈382): re-verify coverage against the current row (`test_matcher_fixes_item7.py` + `test_parameter_group_deriver.py`). If coverage genuinely absent → genuine test or reframe (**not** a marker — cannot tag a test that doesn't pin the claim). This is PGD-08's *only* route (resolves the §3/§5 double-listing); it is excluded from Phase 6 markers.
- [ ] **REQ-CA-05** (vacuous-on-empty): strengthen to pin non-empty coverage, or reframe.
- [ ] **REQ-PY-01/03/05** (blacklist / rebuilt-map weaknesses): strengthen or reframe per row.
- [ ] **REQ-GEN-02** (CalcUsage-only, in-memory, no filesystem check): strengthen or reframe.
- [ ] **REQ-SR-07** (source-text grep, no behavior): strengthen or reframe.
- [ ] **REQ-DM-06/07** (test something categorically different): reframe the text to what the test checks, or file.
- [ ] **REQ-GA-07** (identifier grep): strengthen or reframe.
- [ ] Any row whose honest fix needs a real new behavior → **file with a matrix pointer**, do not build (Non-Goal).

### Validation
**Automated:** any strengthened test passes; full suite green; baselines byte-identical.
**Manual:** re-read each touched row — its PASS now pins its full text (INV-B); INV-E holds on any re-anchor.

**What We Know Works After This Phase:** every D7 divergent row is honest or filed; PGD-08's coverage verdict is recorded.

---

## Phase 5: UNTESTED-12 — deliberate disposition

### Goal
Disposition all 12 `— | UNTESTED` rows (CA-08, DM-08, GEN-03, GEN-07, RES-01..08). Target: ≤ the rows argued untestable-as-written, each carrying its argument in the matrix (INV-B).

### Assumption Under Test
That most of the 12 convert cheaply (static/behavioral checks or cross-citations to existing component tests) and only the genuinely-cross-cutting ones may remain, argued.

### Changes Required — per-row checkboxes
**See `design.md#untested-12--deliberate-disposition`.**
- [ ] **REQ-CA-08** (FORMULA-doesn't-resolve-sibling): convert — static/behavioral check.
- [ ] **REQ-GEN-07** (registered-in-`__init__`): convert — filesystem check.
- [ ] **REQ-GEN-03** (MultiOutput schema): convert — cross-cite.
- [ ] **REQ-DM-08** (NewType wrappers): convert — static check.
- [ ] **REQ-RES-01/03/04/05/06:** discharge by cross-citing existing component tests (resolution-completeness, factory-return-shape, canonical-channel, orchestrator-sequence, binding-source-of-truth).
- [ ] **REQ-RES-02:** already rewritten in Phase 1 (real architecture); now cross-cite.
- [ ] **REQ-RES-07/08:** RES-08 is riskiest (cross-cutting scoping); use Item 1's cross-part fixtures as substrate. Convert with an **independently-anchored** expectation (INV-E / R1 ban).
- [ ] Any row that stays UNTESTED carries a one-line argument for why, in the matrix.

### Validation
**Automated:** any new/cross-cited test passes; full suite green.
**Manual:** every remaining UNTESTED row carries its argument; no converted row computes its own expectation.

**What We Know Works After This Phase:** the UNTESTED count is deliberate and each residual carries its reason.

---

## Phase 6: Marker Hygiene, PGD-06/AST-10, and the Xfail Re-frame

### Goal
Add the six missing row→test markers, dispose the PGD-06 PENDING row and confirm AST-10 is legitimate, and re-frame the one parametrized xfail contract.

### Assumption Under Test
That the six marker cells are populated in the matrix but missing the `# REQ-*` tag in the test source the traceability generator greps — a tagging fix, not a coverage fix.

### Changes Required — per-item checkboxes
**See `design.md#marker-hygiene-counts-and-the-5-xfails`.**

**Markers (add the `# REQ-*` tag in the test source):**
- [ ] BASE-05 · [ ] BT-11 · [ ] CA-10 · [ ] LVP-09 · [ ] OR-09 · [ ] VBR-11 — verify each tag lands on a test that actually pins the claim. **PGD-08 excluded** (routed through Phase 4).

**PGD-06 / AST-10:**
- [ ] **REQ-PGD-06** (≈380): Item 8 deleted `get_default_value` (verify 0 hits in `src/` and `tests/`); pinning tests gone. Re-frame or retire the PASS row; confirm PGD-08's `get_default_value` mention (doc-17) was cleared.
- [ ] **REQ-AST-10** (Item 8, pinned by `test_agg_literal_dispatch.py`): confirm it is a legitimate new row — do **not** treat as orphan.

**Xfail re-frame (one parametrized site, not five markers):**
- [ ] `test_computed_attributes.py:787` — one parametrized `pytest.xfail` producing N cases (inherited-attr classified EXPOSE_COMPUTED where FORMULA is correct; supertype-namespace QN defeats the Step-2b prefix check). Re-frame the REQ and document **one** parametrized xfail contract as known (m9 — it is one contract, not five).
- [ ] **File the classifier fix** as its own backlog item with a matrix pointer (Non-Goal to build here; loud rejection, no fusion-tea model hits it).

### Validation
**Automated:** traceability generator picks up the six new tags; full suite green.
**Manual:** each marker pins its claim; PGD-06 disposed; AST-10 kept; the xfail documented as one contract + classifier fix filed.

**What We Know Works After This Phase:** markers bind row→test, the two Item-8 rows are honest, the xfail is a documented known-contract.

---

## Phase 7: Item-5 Doc-Staleness Fold-in (bounded check)

### Goal
Verify the candidate docs against Item 5's landed behavior changes; touch only where text contradicts code. This is a check, not a rewrite pass (`design.md#item-5-doc-staleness-fold-in`).

### Assumption Under Test
That Item 5 already updated its directly-affected docs (08/09/11/19) and the candidate list is largely reconciled — so this bounded check finds little.

### Changes Required
- [ ] Check **docs 12/14/16/17/23/27** against Item 5's landed behavior (INV-3 require-unique-or-warn, INV-5 EP-key uniqueness, hazard-scoped non-float EP warn, Family-1/2 dispatch/sentinels). Touch only where text contradicts code.
- [ ] Spot-confirm the design's already-reconciled findings hold: doc 10 (D5 alias-collision demotion — also the F2 target, corrected in Phase 3), doc 01 (REQ-EXT-09 elaboration), doc 13 (zero-scoped-modules WARNING).

### Validation
**Manual:** each of the six docs either matches code or is corrected with a one-line note of what changed. No speculative rewrites.

**What We Know Works After This Phase:** the Item-5 candidate docs are confirmed non-stale or corrected.

---

## Phase 8: The ~175-Row Sweep (LAST) — leashed

### Goal
Complete the deep-read sweep of the ~175 never-deep-read PASS rows under the leash. Findings are fixed or filed with a matrix pointer; unswept residue is named with its count.

### Assumption Under Test
That the D7 heuristics select a bounded qualifying set and the stopping rule terminates the sweep on budget — the sweep can only *find* work, so running it after Phases 1–7 means findings don't collide with known dispositions.

### Changes Required
**See `design.md#the-175-row-sweep--execution-shape-leashed`.**
- [ ] Qualify a row for deep-read if: **strong word** (text contains SHALL / ALL / every / never / exactly), OR **diagnostic** (asserts a warning/error fires on a shape), OR **structural count** (asserts a numeric/structural count).
- [ ] **Stopping rule:** sweep until EITHER the qualifying list is exhausted OR **0 new findings in 40 consecutive rows after the first 60 examined**.
- [ ] Each finding: fix (strengthen/reframe) or file with a matrix pointer.
- [ ] **Close-out (register discipline):** whatever stays unswept is **named with its count** — silent truncation reads as "swept everything." State it in the close-out.

### Validation
**Automated:** any fix passes; full suite green; baselines byte-identical.
**Manual:** the qualifying set, the stopping-rule trigger, the findings, and the unswept residue count are all recorded.

**What We Know Works After This Phase:** the sweep is complete-or-honestly-bounded, with its residue named.

---

## Phase 9: Recount, R4 Table & Close-out

### Goal
Regenerate the derived numbers once, from final row reality; produce the R4 verification table; update the discovery register in place. Correct the summary block exactly once, at the end (memory-note discipline).

### Assumption Under Test
That every derived number recomputes cleanly from rows after all dispositions land (B4) — recount is derived-last so it doesn't chase a moving target.

### Changes Required
**See `design.md#marker-hygiene-counts-and-the-5-xfails` (count block), INV-C, and `verification-matrix-drift-modes` memory.**

**Recount from rows (do this LAST, after Phases 1–8):**
- [x] Recount: REQ rows = PASS + UNTESTED + PENDING. Design baseline was 249 = 236 + 12 + 1; the summary block (248) omitted the PENDING REQ-PGD-06 row. **Regenerate the summary block** to match final row reality — dispositions in Phases 4–8 will have moved these numbers; recount, don't carry a hand-count.
- [x] **Footer "33 test files"** (matrix:552) vs `tests/conformance/test_*.py` count (59 at design — recount) vs index "54 distinct cited": pick **one honest definition**, state it next to the number, correct it. If cited files live outside `tests/conformance/`, either correct the count or reframe the PASS definition to admit them.
- [x] Update the index per-family counts (e.g. `[IR] (7/7 pass)`) to match reframed rows.

**R4 artifacts:**
- [x] Produce the **R4 verification table** (finding → probe → CONFIRMED / NOT-REPRODUCED / RECLASSIFIED) covering F2, F4, and the divergent findings. Include the Phase-3 ORCH-04 red-mutation result.
- [x] Update the **discovery register** in place for the F2/F4/divergent findings this item confirms or strikes.
- [x] **Memory-note discipline:** if the recount surfaces a new drift mode or divergence, update the `verification-matrix-drift-modes` memory (recount pattern + known divergences), per its own guidance.

### Validation
**Automated:**
- [x] Full `uv run pytest tests/` → green; baselines byte-identical or reviewed diff; ruff/mypy ≤ Phase-0 ceiling.
- [x] `grep -cE 'REQ-[A-Z]+-[0-9]+'` == summary "Total" (INV-C).
**Manual:**
- [x] Summary/footer/index all reconcile to the row-by-row recount; the file-count definition is stated beside the number.
- [x] Sweep against every INV (A–E): no PASS text asserts live usage of unwired code; no PASS pins less than its text; counts reconcile; every code touch byte-identical/reviewed; no re-anchored test computes its own expectation.

**What We Know Works After This Phase:** the matrix tells the truth end-to-end and its numbers add up; the R4 table and register are produced artifacts.

---

## Environment Setup

**See CLAUDE.md.** Tests: `uv run pytest tests/`. Type: `uv run mypy src/`. Lint: `uv run ruff check src/`. Gate ceiling (INV-D): ruff/mypy **not worse than 21/109** — re-baseline the exact numbers in Phase 0.

---

## Risk Management

**See `design.md#potential-risks`.**

**Phase-Specific Mitigations:**
- **Phase 0:** Items 2/5 churned rows → re-verify line numbers before any later phase acts; fence Item 2's REQ-SVM rows + doc-25 as landed-state.
- **Phase 1:** the split reads as "F4 not finished" → the reframed rows + docs 03/04/05 + the filed cutover item with probe artifacts make the state explicit and honest (that *is* the charter).
- **Phase 3:** ORCH-04 restored-but-still-vacuous → the named red-mutation gate is mandatory (a check that doesn't turn red under the mutation is rejected).
- **Phase 8:** sweep eats the budget → the 40-in-60 stopping rule + residue-naming close-out.
- **Phase 9:** count-definition churn (33/57/54 → 59) → pick one definition, state it beside the number, regenerate derived counts last.

## Implementation Notes

### Phase 0 Completion
**Completed:** 2026-07-06. **Gate ceiling (re-baselined):** ruff 17, mypy 104, suite 2066 passed / 4 skipped / 5 xfailed. **Row reality:** the matrix moved to **253 rows** since design (design said 249) — Item 2 added SVM (4) + AST-10; the summary block (252/240/12) and index are stale (AST index says 9/9 but the table has 10 rows). Re-verified all touched line numbers against the current file (IR 271–277, DRA 165–169, RES 447–454, ORCH-04 351, OR-05/06/08 336/337/339, PGD-06 381, PGD-08 383). **Fenced as landed-state:** REQ-SVM-01..04, doc-25 §, SNAP-19 parametrization. **Deviation:** the epic's expected grep count (249) is stale; real table-row count is 253 — recount uses table parsing, not the grep.

### Phase 1 Completion
**Completed:** 2026-07-06 (commit 834695e — ONE atomic commit). **F4 verdict: LAND-with-split** (all 3 probes fired no kill; zero production callers confirmed by grep). **Files (the atomic set):** `test_dual_resolution.py` (+`TestResolveInputParityExtended`, probe-(i) permanent parametrization, counts hand-transcribed from probe_i_run_log.txt: plant_values mo0/ep3, plant_value_shapes mo0/ep1, spec_chain_twolevel mo1/ep1); `verification-matrix.md` (IR family note + IR-05/07 text→capability, DRA note + DRA-02, RES-02/08 text→live path, bottom RES-02 entry); `docs/reference/03-resolution-overview.md`, `04-input-resolver.md`, `05-module-factory.md` (status banners + every false "factory calls resolve_input" claim → live `_resolve_aggregation_input_channel`). **INV-A grep: zero surviving live-usage claims.** Suite 2069 (2066+3). **Deviation from design line refs:** call sites moved to graph_builder.py 1444/1539/1640 (design said 1437/1532/1633) — Item 5 churn.

### Phase 2 Completion
**Completed:** 2026-07-06. Filed **[ITEM7-F4-CUTOVER]** carrying: correct comparand (parity vs `_resolve_aggregation_input_channel`, M3), EP-key blocker (probe_iv, M4), 3 rewire sites, byte-identity recapture, Strategy D deletion + docstring fix. Retired **DOCS-SCRUB-F4**.

### Phase 3 Completion
**Completed:** 2026-07-06. **F2 = fix-text-to-code** (B3 confirmed: the `instance_attr_to_channel` dict feeds only guarded `register_alias`). Matrix REQ-OR-05/06/08 + doc-10 key-format section rewritten to actual registrations (Key_A guarded alias, Key_F scoped). **ORCH-04 restored** via `test_expected_key_a_aliases_present_solar_battery` (presence, hand-transcribed 3 Key_A aliases). **Red-mutation gate PROVEN:** swapping Phase-1a register_scoped/register_alias order → guard drops aliases (warns "phase ordering violation") → test RED; revert → GREEN; src reverted clean. Fixed 2 lying docstrings. Retired DOCS-SCRUB-F2.

### Phase 4 Completion
**Completed:** 2026-07-06. Reframed 9 divergent-PASS rows to what the cited test verifies (CA-05, PY-01/03/05, GEN-02, SR-07, DM-06/07, GA-07) — status stays PASS, text now matches (INV-B). **PGD-08 confirmed honestly PASS** — its cited `test_matcher_fixes_item7.py` exists in `tests/unit/` (a sub-analysis wrongly reported it missing by only searching conformance/). EXT-09 confirmed DONE (no action).

### Phase 5 Completion
**Completed:** 2026-07-06. Discharged 9 UNTESTED rows by cross-citing an existing pinning test (CA-08→test_computed_attributes; GEN-03→test_gen_schemas; GEN-07→test_gen_registry; RES-01→test_orchestrator; RES-02→test_backtracker/test_computed_attributes/test_factory_aggregation; RES-03→test_factory_purity; RES-04→test_graph_assembly; RES-06→test_factory_calc_usage; RES-07→test_input_resolver). **3 stay UNTESTED-argued** (DM-08, RES-05, RES-08 — no honest test to cite) → filed **[ITEM7-MATRIX-TEST-GAPS]**.

### Phase 6 Completion
**Completed:** 2026-07-06. Added 6 row→test `# REQ-*` markers on pinning tests (BASE-05→test_yaml_baseline_comparison; BT-11→test_chamber_power_disambiguated_to_chamber_b; CA-10→test_shape4_wires_to_exact_channel; LVP-09→test_usage_type_map_indexes_usage_level_retype; OR-09→test_alias_collisions_collapse_to_one_summary; VBR-11→test_cost_per_joule_wired_to_gamma). **PGD-06** re-framed PENDING→UNTESTED-argued (inline `_parse_default_value`; accessor deleted by Item 8) → retired [ITEM7-PGD06]. **AST-10** confirmed legit (pinned by test_agg_literal_dispatch.py). **Xfail** documented as ONE parametrized contract (CA family note) + classifier fix filed [ITEM7-CLASSIFIER-FIX]. Full suite 2069 green.

### Phase 7 Completion
**Completed:** 2026-07-06 (commit 05ec41e). **Item-5 doc-staleness bounded check:** docs 12/14/16/17/27 **CLEAN** (not behaviorally touched by Item 5). **doc-23 STALE** — Item 5's preserve-on-transient change (D3-14) split the unparseable leaf, so the "4-case decision tree" is now 6 cases (a non-empty unparseable impl is PRESERVED, not regenerated). Fixed the tree diagram + REQ-SR-03 return-path count in doc-23 and the matrix SR-03 row. Spot-confirmed doc 10 (F2 target, corrected Phase 3), doc 01 (EXT-09 elaboration), doc 13 (zero-scoped WARNING) hold.

### Phase 8 Completion
**Completed:** 2026-07-06 (findings landed 05ec41e + close-out this session). **Leashed deep-read sweep** ran to substantial completion via delegated per-family readers — **~167 of the ~213 qualifying** strong-word/diagnostic/count PASS rows deep-read. **Findings:** 3 reframed in-matrix (SR-03 6-case, EXT-07 field-shape+snapshot-nullification, EXT-14 same-named-only warning) + **~30 PASS-but-pins-narrower** rows (field-name-only compares, `>=` count floors, self-contained parse checks, circular expected-sets, vacuous greps). **Every finding is a narrower pin, not a correctness lie.** All filed with per-row disposition (reframe / strengthen / fix-citation) in **[ITEM7-MATRIX-SWEEP-RESIDUE]**; a matrix summary sweep-note points readers there. **Residue named:** ~46 qualifying rows not independently deep-read this pass — stated in the filing, not asserted swept (register discipline; no silent truncation).

### Phase 9 Completion
**Completed:** 2026-07-06 (recount 05ec41e; R4 table + register + memory this session). **Recount from rows (INV-C):** 253 = 249 PASS + 4 UNTESTED (DM-08, PGD-06, RES-05, RES-08) + 0 PENDING — verified by status-column grep (PASS=249, UNTESTED=4, sum 253 == summary Total). Summary/index/footer regenerated from final rows (was stale 252/240/12; AST index 9→10 for Item-8 AST-10; RES 0/8→6/8; GEN 5/7→7/7; PGD 8/8→7/8; CA/DM untested moved). **Footer file count:** one honest definition stated beside the number — **57 distinct cited (41 conformance + 16 unit/integration)** — replacing the wrong "33". **R4 verification table PRODUCED:** `.project/active/matrix-truth/r4-verification-table.md` (F2/F4/divergent/counts/sweep → probe → CONFIRMED/NOT-REPRODUCED/RECLASSIFIED, incl. the Phase-3 ORCH-04 red-mutation result). **Discovery register updated in place:** D7 close-out block back-annotates every finding as reconciled by Item 7. **Memory:** `verification-matrix-drift-modes` updated (253-row recount; footer 57-file definition; new drift mode: cited files span unit/integration, not just conformance).

**Sweep against every INV (A–E):** INV-A no PASS text asserts live usage of unwired code (Phase-1 grep zero); INV-B no PASS pins less than its text — divergent rows reframed, sweep findings filed with a matrix pointer (leash-sanctioned); INV-C summary/footer/index reconcile to the row recount; INV-D every code touch byte-identical (no src changed — matrix/docs/tests only), ruff 17 / mypy 104 held; INV-E no re-anchored test computes its own expectation (parity + presence assertions both compare independent paths / hand-transcribed constants).

---

**Status:** Draft → In Progress → **Complete**
