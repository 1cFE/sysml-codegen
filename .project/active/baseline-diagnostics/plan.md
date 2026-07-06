# Implementation Plan: Baseline Repair & Silent-Failure Diagnostics

**Status:** Code complete (Phases 0–2, 4); Phase 3 re-capture pending orchestrator
**Created:** 2026-07-05
**Last Updated:** 2026-07-05
**Epic:** UPSTREAM-FINDINGS — Item 1
**Branch:** upstream-findings-epic (HEAD `81e5082`)

## Source Documents

- **Spec:** `.project/active/baseline-diagnostics/spec.md`
- **Design:** `.project/active/baseline-diagnostics/design.md` ← component sites, decisions (D1–D5), invariants (I1–I4), bets (B1–B3), final diagnostic wording, consumer enumeration. **This plan does not repeat them — it links.**
- **Design review:** `.project/active/baseline-diagnostics/design-review.md` (C1/M1 resolutions, verified against HEAD)
- **Epic R1/R3:** `.project/backlog/epic_upstream_findings.md` (real fixtures not mocks; capture scripts only, reviewed diffs)

---

## Implementation Strategy

**Phasing rationale.** The design is four independent edits (`design.md#core-concept`). The two genuine uncertainties are collapsed first, then the mechanical work follows, then the one deliberate baseline change, then docs:

- **Real risk lives in two bets, not the code.** B2 (which EXPOSE warning a shape-A fixture fires — `design.md#key-bets`) and the constraint metaclass/enumeration question (`design.md#implementation-notes`, "Constraint detection mechanism") both need a **live probe** to settle. They are merged into one Phase 0 session. B2's outcome selects the SC-7 test plan (primary vs. the recorded Item-8 fallback); the metaclass outcome selects the constraint-detection mechanism (`elements_of_type` vs. `owned_members` fallback).
- **Diagnostics before the sort.** The three silent-failure edits (D2/D3/D4) touch no baseline and keep the suite green throughout — and Phase 1 is where B1 ("the constraint pass actually fires against catf_mfe") turns from a bet into a passing test. Do them before the one edit that reddens a baseline.
- **The sort is mechanical but reddens one baseline.** D1 (`design.md#key-decisions`, D1) is a one-line change fully guarded by I2's byte-identical assertion. It goes in its own phase (Phase 2), after which the `solar_battery` byte-exact baseline tests are the **single allowed red** — resolved immediately in Phase 3.
- **Re-capture is its own phase with a reviewed diff.** Per R3 and the design's C1 resolution, Phase 3 runs both capture scripts and gates on a `git diff --stat` that must touch `solar_battery` paths only.
- **Docs/matrix/REQ-tags/agentic-mbse are checklist items, not afterthoughts** (Phase 4).

**Critical path.** Phase 0 probe → its outcome unblocks Phase 1's D4 test path → Phase 2 sort → Phase 3 re-capture (full suite green) → Phase 4 docs. Phase 1 can proceed in parallel with nothing blocking it except the D4 sub-task, which waits on Phase 0.

**First proof point.** End of Phase 0: we know (a) which EXPOSE warning shape A fires, and (b) the exact `ConstraintUsage` metaclass string + whether `elements_of_type` enumerates model-wide. Both are recorded before any production line changes.

**License batching (R3).** Live-syside work (valid to 2026-08-06, in window) happens in exactly **two sessions**: Phase 0 (author both fixtures + capture their snapshots + run both probes) and Phase 3 (baseline re-capture). Do not scatter capture across more sessions.

**Validation approach.** Test-first per phase. Every phase ends with the full suite green **except Phase 2**, whose only red is the `solar_battery` byte-exact baseline comparison — closed in Phase 3. Real fixtures only, no mocks (R1).

---

## Phase 0: Merged De-Risk Probe + Fixture Authoring

### Goal
Author the two new fixtures and, in one live-license session, run the merged probe that selects the SC-7 test path and the constraint-detection mechanism. No production code changes. This is the design's mandated first task (`design.md#next-stage-handoff`).

### Assumption Under Test
- **B2:** a minimal shape-A EXPOSE_PURE fixture fires one of the two *reworded* name-drop warnings (`graph_builder.py:683` key-not-found, or `output_registry_builder.py:182` Phase-3) — not only the malformed-refs warning (`graph_builder.py:672`), which stays unchanged.
- **Metaclass/enumeration:** `self.adapter.elements_of_type(self.model, "ConstraintUsage")` enumerates every constraint usage model-wide (calc-def-, part-def-, and part-usage-owned), with `owner` reachable — or it does not, and the `owned_members` fallback is needed (`design.md#implementation-notes`).

### Probe Stencil (throwaway — do NOT commit as a test)
```python
# scratch probe, run once with live license
from sysml_codegen... import build_pipeline_context, load_models, SysideAdapter

# Probe 1 — SC-7: which EXPOSE warning fires for shape A
import logging; logging.basicConfig(level=logging.WARNING)
build_pipeline_context(load_fixture("expose_pure_shape_a"))
#   → observe: graph_builder.py:683 / output_registry_builder.py:182  → PRIMARY path
#   → observe: only graph_builder.py:672 (malformed-refs)             → Item-8 FALLBACK

# Probe 2 — constraints: metaclass string + model-wide enumeration
model = load_models("catf_mfe_model")
adapter = SysideAdapter()
cu = adapter.elements_of_type(model, "ConstraintUsage")   # try this metaclass string
print(len(cu), [ (c.owner.name, c.name) for c in cu ])    # does it reach RadiusConsistency (part-def) + PositiveRadii (calc-def)?
```

### Changes Required

**See `design.md` for:** fixture shape (`design.md#validation-approach`, "Fixtures"), the probe branch (`design.md#next-stage-handoff`), constraint mechanism (`design.md#implementation-notes`).

- [x] Author `tests/fixtures/expose_pure_shape_a/` — authored, probed, then **removed** (fired the 672 malformed-refs warning, not a reworded one → funds no Item-1 test; see Phase 0 notes).
- [x] Author `tests/fixtures/zero_output_calc/` — one calc def with an `in` attribute and **no** `out attribute`, instantiated once. Loads and reaches the zero-output condition (probe 3: inputs=1, outputs=0).
- [x] Run Probe 1 (SC-7) and Probe 2 (constraints) against the live models. (`scripts/probes/probe_item1_phase0.py`, throwaway.)
- [x] Capture extraction snapshots — **no snapshot committed** for either new fixture. `zero_output_calc` raises once D3 lands; its REQ-EXT-08 test invokes the extractor live and asserts `ValueError`. `expose_pure_shape_a` removed.
- [x] Record both probe outcomes in this plan's Implementation Notes (Phase 0). Constraint mechanism = primary path (`elements_of_type("ConstraintUsage")`), metaclass string `"ConstraintUsage"` — matches `design.md#implementation-notes`; no adjustment needed.

### Validation
**Automated:**
- [x] Full suite still green (no source changed) → confirms fixtures load and don't perturb the corpus. (New fixtures are not in any snapshot/baseline enumeration, so the corpus is untouched.)

**Manual:**
- [x] Probe 1 result recorded → SC-7 **FALLBACK** chosen (shape A fires 672 malformed-refs).
- [x] Probe 2 result recorded → constraint mechanism = **primary** `elements_of_type("ConstraintUsage")` (65 model-wide, owner always reachable); metaclass string pinned to `"ConstraintUsage"`.

**What We Know Works After This Phase:**
The two hardest uncertainties are settled in writing. Phase 1's D4 sub-task and D2 mechanism are now deterministic.

---

## Phase 1: Silent-Failure Diagnostics (D2 + D3 + D4 + dead-code)

### Goal
Land the three "make the silent drop speak" edits and the dead-code deletion. All test-first; the suite stays green throughout (no baseline touched). This phase turns B1 (constraint pass fires against catf_mfe) into a passing structural test.

### Assumption Under Test
- **B1:** `catf_mfe`'s constraint usages are reachable and counted by the dedicated pass (both a calc-def-owned and a part-def-owned constraint), producing exactly one summary WARN.
- D3's guard sits before the `CalculationDefinitionData(...)` return and fires on the `zero_output_calc` fixture (`design.md#key-decisions`, D3).

### Test Stencils (Write First)
```python
# tests/conformance/test_extractor.py  — D3 (REQ-EXT-08)
def test_zero_output_calc_def_raises():
    with pytest.raises(ValueError, match="zero output attributes"):
        extract_calculation_definitions(load_fixture("zero_output_calc"))

# tests/conformance/test_extractor.py  — D2 (REQ-EXT-09), structural, no magic N (I4)
def test_dropped_constraints_reported(caplog):
    model = load_fixture("catf_mfe_model")
    ext = SysMLDataExtractor(model, ...)
    n = count_constraint_usages(model)          # independent count from the loaded model
    with caplog.at_level(logging.INFO):
        ext.report_dropped_constraints()
    warns = [r for r in caplog.records if r.levelno == logging.WARNING and "constraint usage" in r.message]
    infos = [r for r in caplog.records if r.levelno == logging.INFO and "is not executable" in r.message]
    assert len(warns) == 1 and len(infos) == n  # covers a calc-def- AND a part-def-owned constraint

# tests/conformance/test_computed_attributes.py  — D4 (REQ-CA-09), PRIMARY path
def test_expose_pure_name_drop_warning_reworded(caplog):
    with caplog.at_level(logging.WARNING):
        build_pipeline_context(load_fixture("expose_pure_shape_a"))
    msg = "\n".join(r.message for r in caplog.records)
    assert "name is dropped from generated output" in msg and "canonical channel" in msg
```

### Changes Required

**See `design.md` for:** final diagnostic strings (`design.md#implementation-notes`), decisions D2/D3/D4, invariants I3/I4.

- [x] **D3 zero-output fail-fast** — guard raising `ValueError` before the calc-def return (`extraction/extractor.py`, after `references` is set / before `CalculationDefinitionData(...)`). Message is the D3 string verbatim.
- [x] **D2 constraint pass** — new `SysMLDataExtractor.report_dropped_constraints()` + `_constraint_owner_kind()` helper (`extraction/extractor.py`): enumerates every `ConstraintUsage` via `elements_of_type` (primary path, Phase 0), `logger.info` per constraint (owner_kind = calc def | part def | part usage), one `logger.warning` summary with the model-wide total. Called once from `pipeline_builder.py` as **Step 2.5** (after calc-def extraction). Strings verbatim. No per-constraint WARN.
- [x] **D4 EXPOSE wording** — reworded the two name-drop warnings: `graph_builder.py` key-not-found and `output_registry_builder.py` Phase-3. Malformed-refs (`graph_builder.py:672`) untouched. Strings verbatim.
  - Phase 0 chose the **fallback**: both wording edits applied; **no** REQ-CA-09 real-fixture test in Item 1 (deferred to Item 8, marked in Phase 4 matrix). Malformed-refs not reworded.
- [x] **Dead-code deletion** — `git rm` of `extraction/constraints.py` and `templates/constraint_validator.py.jinja2`; kept `constraint_extractor.py` and `PartDefinitionData.constraints`. Added two deletion assertions to `test_dead_code_removal.py::TestDeadFileRemoval`.
- [x] Tag new behavior with REQ-EXT-08, REQ-EXT-09 in code/test docstrings (REQ-CA-09 wording present, its fixture test deferred; matrix rows land in Phase 4).

### Validation
**Automated:**
- [x] New D3/D2 tests pass (REQ-EXT-08, REQ-EXT-09). REQ-CA-09 fixture test deferred (fallback).
- [x] Full suite: 1815 passed, 4 skipped, 5 xfailed, **1 failed** — the single failure is the pre-existing `solar_battery` YAML baseline (`test_e2e_output_registry.py[solar_battery]`), the item's repair target (Phases 2–3). Phase 1 added no new failures and touched no baseline.
- [x] `mypy`/`ruff` — repo baseline is already non-clean (21 ruff + 109 mypy errors on HEAD before this work). My edits introduce **zero** new ruff/mypy findings (verified per-file and by stash-compare). New code matches the file's existing untyped-`elem` convention.

**Manual:**
- [x] Constraint diagnostic verified structurally against live `catf_mfe` (65 constraints → exactly 1 summary WARN + 65 INFO, spanning calc-def and part-def owners); no per-constraint WARN.

**What We Know Works After This Phase:**
All three silent/opaque failures now emit V-rule-style diagnostics against real fixtures. B1 confirmed. Suite green.

---

## Phase 2: Determinism at the Source (D1 sort)

### Goal
Sort `param_groups` by name where the graph is built, so every `entry_point_groups` consumer inherits a stable order (`design.md#key-decisions`, D1). This is the one edit that changes a baseline.

### Assumption Under Test
- **I1:** `entry_point_groups` equals its name-sorted copy in every baseline graph.
- **B3:** the sort is a semantic no-op (serialization order only) — so only `solar_battery` shifts, and only in ordering.

### Test Stencil (Write First)
```python
# tests/conformance/test_graph_assembly.py — I1 / REQ-BASE-06
@pytest.mark.parametrize("model_name", ALL_BASELINE_MODELS)
def test_entry_point_groups_sorted_by_name(model_name):
    graph = build_graph_for(model_name)
    names = [g.name for g in graph.entry_point_groups]
    assert names == sorted(names)
```

### Changes Required

**See `design.md` for:** D1 site/scope (`design.md#component-overview`), the five consumers this stabilizes (`design.md#implementation-notes`, "entry_point_groups consumers").

- [x] `resolution/graph_builder.py` — added `param_groups = sorted(param_groups, key=lambda g: g.name)` as "Step 9" immediately before `ComputationGraph(...)`, scoped to that list only. Modules/inputs/exit points untouched.
- [x] Add the I1 parametrized test (`test_graph_assembly.py::test_entry_point_groups_sorted_by_name`, 5 baseline models). Passes.
- [x] Tag REQ-BASE-06.

### Validation
**Automated:**
- [ ] I1 test passes for every baseline.
- [ ] Full suite green **except** the expected red: `test_factory_purity.py::test_computation_graph_identical` and `test_gen_pipeline_yaml.py` for `solar_battery` (byte-exact comparisons against the not-yet-recaptured baseline). This is the **single documented exception** — closed in Phase 3. `test_pipeline_e2e.py` / `test_graph_assembly.py` normalize group order and stay green (`design-review.md`, C1 note).

**Manual:**
- [ ] Confirm the only failing tests are the two `solar_battery` byte-exact comparisons — nothing else red.

**What We Know Works After This Phase:**
The graph is deterministic (I1 holds corpus-wide). The only remaining red is the intended, ordering-only `solar_battery` baseline mismatch.

---

## Phase 3: Baseline Re-Capture (reviewed diff, live license) — set = solar_battery + catf_mfe

### Goal
Re-capture `solar_battery`'s three baseline artifacts via the capture scripts and prove — by reviewed diff — that nothing else changed. Closes the Phase 2 red; suite goes fully green.

### Assumption Under Test
- **I2 (per model):** only `solar_battery` changes, and only in ordering; every other model's YAML, `computation_graph.json`, `registry_init.py`, and extraction snapshots are byte-identical (`design.md#required-invariants`, I2).

### Changes Required

**See `design.md` for:** the re-capture set and why (`design.md#implementation-notes`, "Baseline re-capture (C1)").

- [ ] **BLOCKED (harness):** Run `scripts/capture_baseline_yaml.py` (regenerates the four `baseline_yaml/*.yaml`).
- [ ] **BLOCKED (harness):** Run `scripts/capture_pipeline_baselines.py` (regenerates `baseline_outputs/<model>/{computation_graph.json,registry_init.py}`).
- [ ] **Reviewed-diff gate (expanded set — approved option 1).** Inspect `git diff`:
  - solar_battery: `baseline_yaml/solar_battery.yaml`, `baseline_outputs/solar_battery/computation_graph.json`, `baseline_outputs/solar_battery/registry_init.py` → **ordering-only**.
  - catf_mfe: `baseline_outputs/catf_mfe/computation_graph.json`, `baseline_outputs/catf_mfe/registry_init.py` → **ordering-only**.
  - `attr_expr_probe`, `chain_spike`, `sample_model` across both scripts → **no diff**.
- [ ] Stage the five ordering-only files (solar_battery ×3 + catf_mfe ×2). Never hand-edit — R3. **Orchestrator/user runs the capture + commit.**

### Validation
**Automated (pending orchestrator capture):**
- [ ] `git diff` on the re-capture commit touches only solar_battery (3 files) + catf_mfe (2 files).
- [ ] **Full suite green** after re-capture (closes the 5 ordering-only reds).

**Manual:**
- [ ] Read the solar_battery (×3) and catf_mfe (×2) diffs — confirm reorder-only (same keys/values, different order).

**What We Know Works After This Phase:**
The item's #1 success criterion — full suite green — is met. No valid model's output changed except `solar_battery`'s reviewed ordering.

---

## Phase 4: Docs, Verification Matrix, REQ Tags, agentic-mbse Impact

### Goal
Land the R1 documentation and traceability, and record the agentic-mbse impact. No production-code behavior change.

### Assumption Under Test
None (documentation). This phase exists so the doc/matrix work is not dropped.

### Changes Required

**See `design.md` for:** the exact doc targets (`design.md#component-overview`, "Docs") and the matrix rows (`design.md#validation-approach`).

- [x] `docs/architecture/modeling-assumptions.md` — added "## 8. Constraints Are Not Executable" (what's dropped, why, what a modeler needing a viability gate should do) and a **V7** row (zero-output) in the Validation Rules table.
- [x] `docs/architecture/reference/01-extraction.md` — added REQ-EXT-08 and REQ-EXT-09 rows.
- [x] `docs/architecture/reference/16-computed-attributes.md` — added REQ-CA-09 row with the Item-8 deferral note.
- [x] `docs/architecture/verification-matrix.md` — added five rows (BASE-05 PENDING RE-CAPTURE, BASE-06 PASS, EXT-08 PASS, EXT-09 PASS, CA-09 DEFERRED TO ITEM 8); updated summary counts + index.
- [x] Confirmed new REQ tags in code/tests match matrix rows: `@pytest.mark.req` on REQ-EXT-08, REQ-EXT-09, REQ-BASE-06; code comments cite REQ-EXT-08/09, REQ-BASE-06, REQ-CA-09.
- [x] **agentic-mbse impact** recorded (Phase 4 Completion below). No agentic-mbse code change in this item.

### Validation
**Automated:**
- [ ] Full suite green (any docs/matrix consistency test passes).

**Manual:**
- [ ] Every new/changed behavior traces: REQ tag ↔ matrix row ↔ reference doc.
- [ ] agentic-mbse impact captured in close-out notes.

**What We Know Works After This Phase:**
The contract docs state the new rules, traceability is complete, and the agentic-mbse follow-up is on record for Item 12.

---

## Environment Setup

**See CLAUDE.md for full environment rules.** Key commands: `uv run pytest tests/`, `uv run mypy src/`, `uv run ruff check src/`. Live-license capture: `scripts/capture_baseline_yaml.py`, `scripts/capture_pipeline_baselines.py`, `scripts/capture_extraction_snapshots.py` (license valid to 2026-08-06 — in window).

---

## Risk Management

**See `design.md#potential-risks` for full analysis.**

**Phase-specific mitigations:**
- **Phase 0 (B2):** if shape A fires only malformed-refs, invoke the recorded fallback — keep the wording edits, defer REQ-CA-09's fixture test to Item 8, note it in the matrix. Never reword malformed-refs to force a pass.
- **Phase 1 (B1):** structural I4 test (independently counted `ConstraintUsage` total) proves the pass fires on both owner kinds; no magic N.
- **Phase 2/3 (B3):** I2's byte-identical assertion catches any non-ordering churn immediately — if a second baseline moves, stop and re-examine before committing.

---

## Implementation Notes

[TO BE FILLED DURING IMPLEMENTATION]

### Phase 0 Completion
**Completed:** 2026-07-05

**Probe 1 (SC-7) result → FALLBACK.** The shape-A fixture (`total_cost : Real = cost_calc.total_cost`
in a library part def owning the `cost_calc` usage) fired **only** the malformed-refs warning at
`graph_builder.py:672` — `"EXPOSE_PURE total_cost: could not identify instance/output from refs
['total_cost', 'cost_calc']"`. Neither the key-not-found (683) nor the Phase-3 warning fired. This
is exactly the Finding-2 mechanism: `ca.references` carry simple names (`cost_calc`), but
`calc_usage_names` holds backtracker EQNs (`ExposePureShapeADesign__costed__cost_calc`), so
`cost_calc ∉ calc_usage_names` → `instance_name` stays `None` → 672. (Part-def shape-A binding
resolution is Item 10/11; the backtracker also logged the cost_calc inputs as unresolved.)
→ **Invoke the recorded fallback:** apply both wording edits (683 + Phase-3, correct regardless),
write **no** Item-1 real-fixture test for REQ-CA-09, defer it to Item 8's WI-014 toy, and mark that
deferral in the verification matrix. Do **not** reword 672.

**Probe 2 (constraints) result → PRIMARY mechanism.** `adapter.elements_of_type(model,
"ConstraintUsage")` enumerated **65** constraint usages model-wide for catf_mfe with the `owner`
attribute always reachable (0 unowned): 51 calc-def-owned, 5 part-def-owned, 9 part-usage-owned.
It reached both `RadiusConsistency` (part-def-owned, `radial_build.sysml:55`) and calc-def-owned
constraints (e.g. `PositiveInputs` on `MagnetCryogenicLoad`). No `owned_members` fallback needed;
metaclass string is `"ConstraintUsage"`.

**Fixture decisions:**
- `zero_output_calc` — committed (library.sysml + design.sysml). **No** extraction snapshot: once
  D3 lands, extraction raises, so REQ-EXT-08 invokes the extractor live and asserts `ValueError`.
  Probe 3 confirmed it extracts inputs=1, outputs=0.
- `expose_pure_shape_a` — authored to run Probe 1, then **removed**. Under the fallback it funds no
  Item-1 test, and it does *not* emit the reworded message (it emits 672), so committing it would be
  dead and misleading. Item 8 brings its own toy for the deferred REQ-CA-09 test.

**Deviations:** SC-7 took the recorded fallback branch (a pre-authorized contingency in
spec/design/plan, not an improvisation). Removing `expose_pure_shape_a` is the one implementation
call not spelled out verbatim by the fallback text — rationale above.

### Phase 1 Completion
**Completed:** 2026-07-05
**Actual Changes:**
- `extraction/extractor.py`: D3 zero-output `ValueError` guard before the calc-def return; `report_dropped_constraints()` + `_constraint_owner_kind()` (D2).
- `orchestration/pipeline_builder.py`: Step 2.5 calls `extractor.report_dropped_constraints()`.
- `resolution/graph_builder.py`: reworded key-not-found EXPOSE_PURE warning (D4).
- `orchestration/output_registry_builder.py`: reworded Phase-3 EXPOSE_PURE warning (D4).
- Deleted `extraction/constraints.py`, `templates/constraint_validator.py.jinja2` (`git rm`).
- Tests: `test_extractor.py` gains `_load_live_extractor` helper + REQ-EXT-08/09 classes; `test_dead_code_removal.py` gains two deletion assertions.
**Issues / Deviations:** REQ-CA-09 real-fixture test deferred to Item 8 (Phase 0 fallback). The one red at the Phase-1 boundary is the pre-existing solar_battery YAML baseline, owned by Phases 2–3.

### Phase 2 Completion
**Completed:** 2026-07-05 (code); **BLOCKED at the Phase 2→3 boundary pending a re-capture-set decision.**

**Confirmed red set after the sort (5 failures):**
1. `test_gen_pipeline_yaml.py::...[solar_battery]` — solar YAML byte-exact ✓ expected
2. `test_graph_assembly.py::TestBaselineComparison::test_baseline_comparison_solar_battery` — solar graph ✓ expected
3. `test_pipeline_e2e.py::...test_baseline_comparison_solar_battery` — solar graph ✓ expected
4. `test_pipeline_e2e.py::...test_baseline_comparison_catf_mfe` — **catf_mfe graph — NOT anticipated by the plan**
5. `test_e2e_output_registry.py::...[solar_battery]` — solar YAML (pre-existing) ✓ expected

**Deviation found — catf_mfe entry_point_groups also reorder (ordering-only).** The design's I2 named
"the three other models (chain_spike, attr_expr_probe, sample_model)" as must-stay-byte-identical and
the success criterion says "no baseline changes beyond solar_battery." But catf_mfe has **8**
entry-point groups committed in discovery order (heating, magnets, blanket, physics, system, tritium,
vacuum, radial_build); the sort reorders them alphabetically. Proven ordering-only:
- same set of 8 group names; per-group content byte-identical
- `modules` identical (order + content); `execution_order` identical
- graphs equal after sorting entry_point_groups on both sides
So B3 (semantic no-op) **holds** — the design merely under-counted which models reorder.
`chain_spike`, `attr_expr_probe`, `sample_model` are byte-identical as the design claimed (they stayed green).

**Corrected re-capture set (pending approval):** solar_battery (YAML + graph + registry, 3 files) **and**
catf_mfe (graph + registry, 2 files — catf_mfe has no baseline_yaml; its `registry_init.py` group order
also follows `entry_point_groups` via `registry.py:185`, though no test asserts it). Three other models
unchanged. Per the plan's own Risk Management ("if a second baseline moves, stop and re-examine before
committing") and the orchestration rule, execution paused here to confirm expanding the committed set to
catf_mfe before running the capture scripts.

### Phase 3 Completion
**Status:** BLOCKED on capture-script execution — the harness gates all filesystem writes and all
`uv run` invocations this session, so `scripts/capture_*.py` cannot be run from here and 400 KB of
byte-exact baselines cannot be reconstructed through the Write tool. **The orchestrator/user must run
the two capture commands and commit the reviewed diff.**

**Exact commands:**
```
uv run --env-file ~/1cfe/agentic-mbse/.env python scripts/capture_baseline_yaml.py
uv run --env-file ~/1cfe/agentic-mbse/.env python scripts/capture_pipeline_baselines.py
```

**Diff review (verified in-memory this session — the capture will reproduce it):**
- solar_battery: YAML + `computation_graph.json` + `registry_init.py` — ordering-only (entry-group reorder).
- catf_mfe: `computation_graph.json` + `registry_init.py` — ordering-only. Proven: `modules`,
  `execution_order`, and per-group content are byte-identical; only the `entry_point_groups` list order
  changes (discovery → alphabetical). New sorted order: blanket, heating, magnets, physics,
  radial_build, system, tritium, vacuum.
- attr_expr_probe, chain_spike, sample_model: **no diff** (stayed green through the sort).

**Post-capture expectation:** the 5 currently-red byte-exact baseline tests go green; full suite green.
Reds to clear: `test_gen_pipeline_yaml.py[solar_battery]`, `test_e2e_output_registry.py[solar_battery]`,
`test_graph_assembly.py::...solar_battery`, `test_pipeline_e2e.py::...solar_battery`,
`test_pipeline_e2e.py::...catf_mfe`.

### Phase 4 Completion
**Completed:** 2026-07-05
**Docs landed:** modeling-assumptions.md (§8 Constraints Are Not Executable + V7 row);
01-extraction.md (REQ-EXT-08/09 rows); 16-computed-attributes.md (REQ-CA-09 row, Item-8 deferral);
verification-matrix.md (5 rows + summary/index updates).

**agentic-mbse impact recorded:** Endorse A-1 — sysml-codegen now warns at extraction when constraints
are dropped (REQ-EXT-09), so agentic-mbse should carry the matching Level-6 (or equivalent) check that
constraints are not executable, with a negative fixture. The new "Constraints Are Not Executable"
section of `modeling-assumptions.md` is the canonical reference that guidance points at. **No
agentic-mbse code change in this item** — that lands in Item 12 (the epic's agentic-mbse sync item).
Nothing else in Item 1 changes what models should look like, so no MODELING_GUIDE / skill-stencil change
is triggered.

### Quality Gate (measured 2026-07-05, before the `uv run` lockout)
- Full suite: 1816 passed, 4 skipped, 5 xfailed, **5 failed** — all five are the ordering-only
  byte-exact baseline comparisons (solar_battery ×4 + catf_mfe ×1) that Phase 3's re-capture closes.
  No other failures. New tests (REQ-EXT-08/09, REQ-BASE-06 I1, dead-code deletion) all green.
- mypy / ruff: repo baseline is already non-clean (109 mypy + 21 ruff errors on HEAD before this work);
  this item's edits introduce **zero** new findings (verified per-file and by stash-compare). New code
  follows the file's existing untyped-`elem` convention.
- Phase 4 changes are docs/artifacts only; no test references the matrix or modeling-assumptions docs,
  so the suite state is unchanged from the measurement above.

### Session note — harness write/`uv run` lockout
The resume session gates **all** filesystem writes (Bash `write_text`/`open(w)`/redirects, even to
/tmp), all `uv run` invocations (including read-only), and Write-tool writes under `.claude/`. Read-only
Bash (`git`, `grep`) and Write/Edit to project files work. Consequences: (1) the capture scripts and the
`pytest/mypy/ruff` re-run could not be executed this session — the gate figures above are from the prior
session; (2) Phase 3 re-capture is handed to the orchestrator (commands in Phase 3 Completion).

---

**Status:** Draft → In Progress → **Code complete; Phase 3 baseline re-capture pending orchestrator (harness write lockout)**

**Phase 3 completed (2026-07-05, orchestrator-executed).** The orchestrator approved the expanded
re-capture set and ran the captures directly (the resume-session harness blocked writes/`uv run`).
Two further deviations surfaced and were resolved:

1. **`capture_pipeline_baselines.py` captured the wrong flavor.** The script built graphs LIVE via
   `build_pipeline_context`, producing absolute `source_file` paths, `compilability=fully_compilable`,
   and populated `auto_impl_context` — but the byte-exact consumers (`test_factory_purity` et al.)
   rebuild graphs **from committed snapshots** (`compilation_results=None` until Item 2), so live
   captures can never match, and the suite went red on attr_expr_probe. **Fix:** the script now
   captures through the snapshot serialization boundary via
   `build_full_graph_from_snapshot` — baselines are by construction what the tests compare. The
   flavor choice (and Item 2's planned deliberate regen when snapshots gain `compilation_results`)
   is documented in the script docstring. The script no longer needs a syside license.
2. **Two stale registry baselines corrected.** `sample_model/registry_init.py` (committed with 5
   modules; the committed graph and YAML both have 0) and `catf_mfe/registry_init.py` (committed
   with 21 modules incl. PlasmaConfinement/TritiumBreedingRatio/ThermalCycleEfficiency — none of
   which exist in the committed 42-module graph) predated the current graphs. No test asserts
   either file. Regenerated from the current graphs; recorded here as stale-baseline repair.

**Reviewed-diff evidence (structural comparison, old vs new JSON):**
- solar_battery: modules identical (order+content), execution_order identical, group set equal,
  groups now name-sorted; within `system_design` the 19 parameters are multiset-equal, reordered
  (assembly-iteration side effect of the group sort). Ordering-only. ✓
- catf_mfe: modules identical, execution_order identical, group set equal, per-group content
  byte-identical, groups name-sorted. Ordering-only. ✓
- attr_expr_probe, chain_spike: byte-identical after the trailing-newline convention fix. ✓
- sample_model: graph gains only the trailing newline; registry corrected per (2). ✓

**Quality gate:** 1821 passed / 4 skipped / 5 xfailed — fully green. ruff: 21 findings (identical
count on main — none new). mypy: 109 errors (main: 109 — none new).

**Probe file ruling:** `scripts/probes/probe_item1_phase0.py` kept — `scripts/probes/` is an
established convention with a README.
