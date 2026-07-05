# Implementation Plan: Baseline Repair & Silent-Failure Diagnostics

**Status:** Draft
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

- [ ] Author `tests/fixtures/expose_pure_shape_a/` — a library part def owning a calc usage plus an EXPOSE attribute (`attribute total_cost : Real = cost_calc.total_cost;`), instantiated by a separate design part. Model on `tests/fixtures/chain_spike_model/`'s library/design split.
- [ ] Author `tests/fixtures/zero_output_calc/` — one calc def with an `in` attribute and **no** `out attribute` (body-only or empty), instantiated once. Must load and reach the zero-output condition without Item 3.
- [ ] Run Probe 1 (SC-7) and Probe 2 (constraints) against the live models.
- [ ] Capture extraction snapshots this session via `scripts/capture_extraction_snapshots.py` where applicable. **Note:** `zero_output_calc` extraction *raises* once D3 lands (Phase 1), so it may have no committed snapshot — its REQ-EXT-08 test invokes the extractor live and asserts `ValueError`. Decide and record whether a pre-D3 snapshot is committed (implementer's call per `design.md#next-stage-handoff` "final fixture file contents").
- [ ] Record both probe outcomes in this plan's Implementation Notes (Phase 0) **and** confirm/adjust the constraint-detection code path and the final `ConstraintUsage` metaclass string in `design.md#implementation-notes`.

### Validation
**Automated:**
- [ ] Full suite still green (no source changed) → confirms fixtures load and don't perturb the corpus.

**Manual:**
- [ ] Probe 1 result recorded → SC-7 branch chosen (primary vs. fallback).
- [ ] Probe 2 result recorded → constraint mechanism chosen (`elements_of_type` vs. `owned_members`) and metaclass string pinned.

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

- [ ] **D3 zero-output fail-fast** — guard raising `ValueError` right after `output_attributes` is populated, before the calc-def return (`extraction/extractor.py`, ~line 214). Message is the D3 string verbatim from `design.md#implementation-notes`.
- [ ] **D2 constraint pass** — new `SysMLDataExtractor.report_dropped_constraints()` (`extraction/extractor.py`): scan the loaded model for every `ConstraintUsage` (mechanism per Phase 0 outcome), `logger.info` per constraint (`owner_kind` = calc def | part def | part usage), one `logger.warning` summary with the model-wide total. Call it once from `orchestration/pipeline_builder.py` after `load_models()`, near the calc-def extraction step. Strings verbatim from `design.md#implementation-notes`. No per-constraint WARN.
- [ ] **D4 EXPOSE wording** — reword the two name-drop warnings only: `resolution/graph_builder.py:683-687` (key-not-found) and `orchestration/output_registry_builder.py:182-186` (Phase-3). **Leave `graph_builder.py:672-675` (malformed-refs) untouched.** Strings verbatim from `design.md#implementation-notes`.
  - If Phase 0 chose the **fallback**: still apply both wording edits (correct regardless), but defer the REQ-CA-09 real-fixture test to Item 8 and note the deferral in the verification matrix (Phase 4). Do **not** reword malformed-refs to force a green test.
- [ ] **Dead-code deletion** — remove `extraction/constraints.py` and `templates/constraint_validator.py.jinja2`; keep `constraint_extractor.py` and `PartDefinitionData.constraints` (`design.md#non-goals`, spec D2). Update `tests/conformance/test_dead_code_removal.py` if it references the deleted paths.
- [ ] Tag new behavior with REQ-EXT-08, REQ-EXT-09, REQ-CA-09 in code/test docstrings (matrix rows land in Phase 4).

### Validation
**Automated:**
- [ ] New D3/D2/D4 tests pass.
- [ ] Full suite green (no baseline touched by this phase).
- [ ] `mypy src/` and `ruff check src/` clean.

**Manual:**
- [ ] Run generation on `catf_mfe` → eyeball exactly one summary WARN + the per-constraint INFO lines; confirm no per-constraint WARN noise (`design.md#validation-approach`, "Manual").

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

- [ ] `resolution/graph_builder.py` — reassign `param_groups = sorted(param_groups, key=lambda g: g.name)` immediately before `ComputationGraph(...)` (line ~364), scoped to that list only. Do **not** sort modules, module inputs, or exit points (spec review L3-2).
- [ ] Add the I1 parametrized test above.
- [ ] Tag REQ-BASE-06.

### Validation
**Automated:**
- [ ] I1 test passes for every baseline.
- [ ] Full suite green **except** the expected red: `test_factory_purity.py::test_computation_graph_identical` and `test_gen_pipeline_yaml.py` for `solar_battery` (byte-exact comparisons against the not-yet-recaptured baseline). This is the **single documented exception** — closed in Phase 3. `test_pipeline_e2e.py` / `test_graph_assembly.py` normalize group order and stay green (`design-review.md`, C1 note).

**Manual:**
- [ ] Confirm the only failing tests are the two `solar_battery` byte-exact comparisons — nothing else red.

**What We Know Works After This Phase:**
The graph is deterministic (I1 holds corpus-wide). The only remaining red is the intended, ordering-only `solar_battery` baseline mismatch.

---

## Phase 3: Baseline Re-Capture (reviewed diff, live license)

### Goal
Re-capture `solar_battery`'s three baseline artifacts via the capture scripts and prove — by reviewed diff — that nothing else changed. Closes the Phase 2 red; suite goes fully green.

### Assumption Under Test
- **I2 (per model):** only `solar_battery` changes, and only in ordering; every other model's YAML, `computation_graph.json`, `registry_init.py`, and extraction snapshots are byte-identical (`design.md#required-invariants`, I2).

### Changes Required

**See `design.md` for:** the re-capture set and why (`design.md#implementation-notes`, "Baseline re-capture (C1)").

- [ ] Run `scripts/capture_baseline_yaml.py` (regenerates the four `baseline_yaml/*.yaml`).
- [ ] Run `scripts/capture_pipeline_baselines.py` (regenerates `baseline_outputs/<model>/{computation_graph.json,registry_init.py}`).
- [ ] **Reviewed-diff gate.** Inspect `git diff`:
  - `baseline_yaml/solar_battery.yaml`, `baseline_outputs/solar_battery/computation_graph.json`, `baseline_outputs/solar_battery/registry_init.py` → **ordering-only** diffs (entry-group reorder), no content change.
  - Every other model (`attr_expr_probe`, `chain_spike`, `sample_model`, `catf_mfe`) across both scripts → **no diff**.
- [ ] Stage and commit **only** the three `solar_battery` files (never hand-edit — R3).

### Validation
**Automated:**
- [ ] `git diff --stat` on the re-capture commit touches `solar_battery` paths only.
- [ ] **Full suite green**, including `test_factory_purity.py::test_computation_graph_identical`.

**Manual:**
- [ ] Read the three `solar_battery` diffs — confirm reorder-only (same keys/values, different order).

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

- [ ] `docs/architecture/modeling-assumptions.md` — add a "Constraints are not executable" section (what's dropped, why, what a modeler needing a viability gate should do). Add the zero-output rule as a **V7** row in the "Validation Rules" table.
- [ ] `docs/architecture/reference/01-extraction.md` — rows for REQ-EXT-08 (zero-output fail-fast) and REQ-EXT-09 (constraint drop diagnostic).
- [ ] `docs/architecture/reference/16-computed-attributes.md` — row for REQ-CA-09 (EXPOSE_PURE name-drop wording).
- [ ] `docs/architecture/verification-matrix.md` — five rows: REQ-BASE-05, REQ-BASE-06, REQ-EXT-08, REQ-EXT-09, REQ-CA-09 (mapping the table in `design.md#validation-approach`). If Phase 0 chose the SC-7 fallback, mark REQ-CA-09's fixture test as deferred to Item 8 with a note.
- [ ] Confirm every new REQ tag in code/tests matches its matrix row.
- [ ] **agentic-mbse impact** — record in the item close-out: endorse the A-1 constraint-non-executability WARN check; the new "Constraints are not executable" section becomes the canonical reference the agentic-mbse guidance points at. **No agentic-mbse code change in this item** (executed in Item 12). Nothing else in this item changes what models should look like (`spec.md#agentic-mbse-impact`).

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
**Probe 1 (SC-7) result:** _(record: which warning fired → primary or fallback)_
**Probe 2 (constraints) result:** _(record: metaclass string; elements_of_type model-wide? or owned_members fallback)_
**Fixture decisions:** _(zero_output_calc snapshot committed? shape-A final contents)_
**Completed:** _
**Deviations:** _

### Phase 1 Completion
**Completed:** _
**Actual Changes:** _
**Issues / Deviations:** _

### Phase 2 Completion
**Completed:** _
**Confirmed red set:** _(should be exactly the two solar_battery byte-exact comparisons)_

### Phase 3 Completion
**Completed:** _
**Diff review:** _(solar_battery ordering-only across 3 files; all other models byte-identical — confirm)_

### Phase 4 Completion
**Completed:** _
**agentic-mbse impact recorded:** _

---

**Status:** Draft → In Progress → Complete
