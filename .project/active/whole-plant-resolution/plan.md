# Implementation Plan: Whole-Plant Cross-Part Value Resolution (PIPELINE-TRUTH Item 2)

**Status:** Draft
**Created:** 2026-07-06
**Last Updated:** 2026-07-06
**Branch:** pipeline-truth-epic

## Source Documents
- **Spec:** `.project/active/whole-plant-resolution/spec.md`
- **Design:** `.project/active/whole-plant-resolution/design.md` ← component details, D1–D5, INV-1..7, REQ-SVM-01..04, F2–F7, SC-3 runner contract
- **Reviews:** `spec-review.md`, `design-review.md` (same dir)

---

## Sequencing Preconditions (read before Phase 1)

- **This item's implement is LAST in the Track-A tree queue.** It runs *after* Item 4
  (Phase 5 format bump `v1→v2` re-captures ALL snapshots, including `plant_values`,
  `plant_value_shapes`, `spec_chain_twolevel`, and the fusion-tea snapshot), then Item 6,
  then Item 8. **Every snapshot this item reads is at format v2.** Its capture riders
  (renamed-consumer leg, 0.0-valued literal row) capture at v2 with Item 1's `--fixtures`
  tooling. Do not author baseline bytes against v1.
- **Before starting: reconfirm the red state.** Item 1's D6 offender pins are the RED
  fixtures this item flips. Run them first and confirm they still FAIL in the expected way
  (3-offender set on `plant_values`; `'Flow Sub'` DEGRADED on `plant_value_shapes`) at v2,
  since Items 4/6/8 landed between spec-time and now. If the red state drifted, STOP and
  re-baseline before writing any materializer code.
- **(c) anchor number follows the landed Item-1 F1/F2 cure.** The `48.5714…` anchor assumes
  the cure landed `:>> chamber.cost_per_unit = 7.0`. Pull the final chamber literal from the
  committed `plant_values/design.sysml` at implement; if it is not `7.0`, recompute the
  anchor and update the SC-1 test (per spec SC-1).

## Implementation Strategy

**Phasing Rationale.** The mechanism is one pre-pass (the supplied-value materializer) that
populates an index (`design_attributes`) an existing four-step dispatch already reads
(design.md#core-concept, D2). So the phases follow the **data-flow order** the design lays
out: first make the value *reachable* (thread `design_overrides`, fix the `0.0`-drop),
then *materialize* it (precedence + collision + sentinel), then verify the two behaviors
that make this mechanism distinct from its siblings (**source-QN fan-out collapse**, and
the **(d) in-part leg**), then prove it end-to-end (executor runner, fusion-tea proxy),
then lock baselines and docs.

**Critical Path.** Phase 1 (threading) is the **single point of failure** the design calls
out (design.md#next-stage-handoff "de-risk first"): without `design_overrides` reaching
`build_computation_graph`, shapes (b)/(c) have no value source and the whole headline flip
is dead. Prove that thread-through in code before building anything on it.

**First Proof Point.** Phase 1: `design_overrides` arrives at the graph builder (asserted
directly), AND a design attribute valued `0.0` classifies to a `0.0` entry point, not
`null` (the F2 fix, independently testable with a real attribute before the materializer
exists).

**Biggest Risks (see design.md#potential-risks).**
- The **0.0-escapes-V11** hazard (INV-6) has **two** truthiness drop sites, not one — see
  the Phase-1 note on `graph_builder.py:1133`. The design's F2 names only `:482`.
- **Baseline drift** on the four cross-part baselines (SC-5) — gated byte-for-byte in Phase 7.
- **(d) mis-routing** through `_find_literal_redefinition`'s brittle name-fallback instead
  of the direct-owner leg (F4/B4) — Phase 4.

**Validation Approach.** Test-first throughout: the RED before-pins already exist (Item 1);
each mechanism phase flips its slice to a **behavior-observing** green pin (never a
`snapshot == committed` byte-equality — the epic-R1-banned REQ-EXT-09 anti-pattern). New
seams (F2/F3/F5, the runner) get their own written-first pins.

**Environment.** See CLAUDE.md. Tests: `uv run pytest tests/`; single:
`uv run pytest tests/conformance/test_plant_values.py -k NAME`; types `uv run mypy src/`;
lint `uv run ruff check src/`. Snapshot generation is license-free via `--from-snapshot`.

---

## Phase 1: Thread `design_overrides` + the F2 `0.0` fix (de-risk the single point of failure)

### Goal
Make the supplied value *reachable*: (1) thread `design_overrides` into
`build_computation_graph` from both call sites so (b)/(c) have a value source; (2) fix the
truthiness drop so a `0.0` default carries as `0.0`, not `null`. Both are independent of the
materializer and collapse the two highest-impact uncertainties first.

### Assumption Under Test
- `hierarchy_data.design_overrides` actually reaches the graph builder from **both** the
  snapshot path and the live path (design.md#implementation-notes "Thread `design_overrides`
  first").
- `_classify_entry_points` drops a `0.0` design-attribute default today, and `is not None`
  fixes it — **and** whether the parallel FORMULA-input path at `graph_builder.py:1133`
  drops it too.

### Test Stencil (Write This First)
```python
# tests/unit/test_graph_builder_zero_default.py  (NEW)
def test_zero_valued_design_attr_classifies_to_zero_not_null():
    # A real DesignAttributeData with default_value="0.0" wired to a consumer input
    graph = build_computation_graph(..., design_attrs={"P": [attr(name="x", default_value="0.0")]})
    ep = ep_for(graph, "..._x")
    assert ep.entry_type == EntryPointType.DESIGN_ATTRIBUTE
    assert ep.default_value == 0.0          # NOT None — the INV-6 hazard
    assert ep.qualified_name not in graph.fallback_entry_points  # not fell-through → V11 can't miss it

# tests/unit/test_design_overrides_threaded.py  (NEW)
def test_design_overrides_reaches_build_from_snapshot_and_live():
    # assert both graph_rebuild and pipeline_builder pass design_overrides through
    # (spy/assert the param is received non-None when hierarchy_data carries overrides)
```

### Changes Required
**See design.md for:** the threading gap (design.md#the-machinery-to-reuse — "`design_overrides`
is loaded but dropped on the floor"); INV-6; F2.

- [ ] **`build_computation_graph` signature** (`graph_builder.py:156`): add a
  `design_overrides` parameter (default `None`); store/pass it toward the materializer seam
  (Phase 2 consumes it). No behavior change yet beyond availability.
- [ ] **Snapshot call site** (`snapshot/graph_rebuild.py:139`): add
  `design_overrides=hierarchy_data.design_overrides` (sits beside the existing
  `hierarchy_redefinitions`/`usage_type_map` at `:148-149`).
- [ ] **Live call site** (`orchestration/pipeline_builder.py:801`): add
  `design_overrides=hierarchy_data.design_overrides if hierarchy_data else None` (beside the
  same two params).
- [ ] **F2 fix** (`graph_builder.py:482`): `if attr.default_value:` → `if attr.default_value
  is not None:`.
- [ ] **F2 second site — INVESTIGATE + fix if hit** (`graph_builder.py:1133`,
  `if da and da.default_value:` in the FORMULA/constraint input-building path): determine
  whether a supplied `0.0` design attribute can flow through this path. If yes, apply the
  same `is not None` guard and add a pin. If provably unreachable for supplied values,
  record *why* in a one-line comment so the next reader does not re-litigate. **Do not
  silently leave a second `0.0`-drop.**

### Validation
**Automated:**
- [ ] New unit tests pass; `uv run pytest tests/unit/ -k "zero_default or design_overrides_threaded"`.
- [ ] Full suite → no regressions; `uv run mypy src/` clean on the new param.
**Manual:**
- [ ] Grep confirms both call sites now pass `design_overrides`.

**What We Know Works After This Phase:** the override value reaches the graph builder, and
the classify path carries `0.0` faithfully at every drop site. The materializer (Phase 2)
has a value source and a safe classify path to write into.

---

## Phase 2: The materializer core — precedence + collision + non-literal sentinel (REQ-SVM-01..04)

### Goal
Land the supplied-value materializer: for each referenced subsystem-attr binding, resolve
the plain-value precedence (usage override > specialized-def `:>>` > base def), emit a
synthetic `DesignAttributeData` keyed by **source QN** with `default_value` as a **string**,
merge into `design_attrs` before the backtracker. This flips the headline (a)/(b)/(c) set.

### Assumption Under Test
- One pre-pass populating `design_attributes` is enough — Step 3
  (`_resolve_to_design_attribute`) resolves and collapses without any new dispatch branch
  (design.md D2).
- Tier-2a reuse of `_find_literal_redefinition` Strategy 1 (`graph_builder.py:1308`) + a new
  tier-1 `design_overrides` lookup covers (a)/(b)/(c).
- The collision guard (F3) and non-literal sentinel (F5) behave as specified.

### Test Stencil (Write This First)
```python
# Flip the Item-1 RED before-pin to behavior-observing GREEN:
# tests/conformance/test_plant_values.py
def test_plant_values_resolves_all_three_mechanisms():
    graph = generate_from_snapshot("plant_values")
    assert collect_uncovered_params(graph) == []                 # SC-1: zero V11 offenders
    assert ep_value(graph, "...__driver__efficiency") == 0.35    # (a)
    assert ep_value(graph, "...__target_factory__cost_per_target") == 10.0  # (b)
    assert ep_value(graph, "...__chamber__cost_per_unit") == 7.0 # (c), pull final from cure

def test_supplied_zero_literal_emits_zero_not_null():            # F2/INV-6, materializer-side
    ...  # a 0.0-valued supplied literal → ep.default_value == 0.0

def test_synthetic_never_overwrites_real_design_attr(caplog):    # F3/REQ-SVM-03
    ...  # constructed QN collision: real value survives, WARN emitted

def test_non_literal_binding_falls_to_v11_with_count_warn(caplog):  # F5/REQ-SVM-04/INV-7
    ...  # CHAIN/EXPRESSION-only source → still an offender, count-summary WARN
```

### Changes Required
**See design.md for:** the materializer contract (design.md#component-overview,
`materialize_supplied_values` sketch); precedence steps 1–4 (design.md#architecture
"Precedence resolution"); REQ-SVM-01..04 (D3); INV-3, INV-4, INV-7.

- [ ] **New `materialize_supplied_values`** — resolve the location open: `resolution/
  supplied_values.py` (new) vs `extraction/hierarchy_resolver.py`. **Recommend the new
  module** — it is a resolution-time pre-pass, not extraction, and keeps the collision-guard
  dependency on the real `design_attributes` local. Record the choice in the plan notes.
  - [ ] Tier 1 (usage override): look up `design_overrides` by owner QN (shape b) and by
    `target_path` (shape c).
  - [ ] Tier 2a (specialized-def `:>>`): reuse `_find_literal_redefinition` **Strategy 1**
    only (via `usage_type_map`); do NOT rely on its Strategy-2 name-fallback.
  - [ ] Emit `DesignAttributeData(parent_part, name, default_value=str(value),
    qualified_name=source_qn)` — string default to match `parameter_groups.py:51` `str | None`.
  - [ ] **F3 collision guard (REQ-SVM-03):** before emitting, if a real captured design
    attr already covers the source QN or `(name, parent_part)`, **skip + WARN** (real wins).
    Guards the last-wins `design_attr_by_qname` at `graph_builder.py:457-461`.
  - [ ] **F5 non-literal sentinel (REQ-SVM-04):** apply LITERAL only; emit a count-summary
    WARN naming CHAIN/EXPRESSION skips ("scanned N: M literal applied, K non-literal skipped
    (deferred: <list>)"), Item-5 sentinel style. Zero skipped → INFO-only (silent-on-clean).
- [ ] **`build_computation_graph`** (`graph_builder.py:156`): run the materializer on the
  threaded inputs, merge the synthetic attrs into `design_attrs` **before** constructing the
  backtracker. `_resolve_to_design_attribute` (`dependency_backtracker.py:673`) is unchanged.

### Validation
**Automated:**
- [ ] `plant_values` flip pin green (SC-1 minus the anchor, below); F2/F3/F5 pins green.
- [ ] **INV-1 regression guard:** `test_spec_chain_channel.py` / `test_spec_chain_twolevel.py`
  stay green (a synthetic attr must not shadow a calc-output channel; registry Steps 1–2 run
  first per B3).
- [ ] `uv run mypy src/` / `uv run ruff check src/` clean.

**What We Know Works After This Phase:** (a)/(b)/(c) resolve on `plant_values` to filled
DESIGN_ATTRIBUTE entry points; the three seams (0.0, collision, non-literal) behave; the
calc-output edge is untouched.

---

## Phase 3: EP source-QN keying — the renamed-consumer fan-out leg (INV-2 / B2)

### Goal
Prove the property that makes this mechanism distinct from VBR-03: differently-named
consumers of one source attribute collapse to **one** entry point, keyed by source QN.

### Assumption Under Test
`_resolve_to_design_attribute` keys on the binding's `source_path` and ignores the
consumer's `param_name` (design.md B2, `:701-710`), so two *renamed* consumers of one
attribute produce one synthesized QN → one EP. The existing
`test_fanout_collapses_to_one_producer_channel` proves only the *same*-name case.

### Test Stencil (Write This First)
```python
# tests/conformance/test_spec_chain_twolevel.py  (extend)
def test_renamed_consumers_collapse_to_one_source_ep():
    graph = generate_from_snapshot("spec_chain_twolevel")
    # one source attr feeding two DIFFERENTLY-named inputs
    eps = [ep for ep in graph.entry_points if source_qn(ep) == "...__scale"]
    assert len(eps) == 1            # collapse, not N keys — the EP-keys-by-source-QN [HARD]
```

### Changes Required
**See design.md for:** INV-2; B2; the spec's Must-Fix 3 renamed-consumer rider (spec.md
Known Requirements, "renamed-consumer leg").

- [ ] **Capture rider** (Item-1 style, own commit): extend `spec_chain_twolevel` (or a
  sibling fixture) with one source attribute feeding two differently-named inputs. Capture at
  **v2** with `scripts/capture_extraction_snapshots.py --fixtures spec_chain_twolevel`.
- [ ] Add the collapse pin above.

### Validation
**Automated:**
- [ ] Renamed-consumer pin green; the existing same-name
  `test_fanout_collapses_to_one_producer_channel` stays green.
**Manual:**
- [ ] Reviewed diff on the extended `spec_chain_twolevel/extraction_snapshot.json` — only the
  new source/consumer rows change.

**What We Know Works After This Phase:** the source-QN fan-out collapse holds for the
fusion-tea renamed-consumer shape (`efficiency` → `driver_efficiency` AND `eta`), not just
the same-name case.

---

## Phase 4: The (d) in-part direct-owner leg (F4 / B4)

### Goal
Resolve shape (d) — in-part consumption of an inherited attr the def redefines — via the
**direct-owner** leg, flipping `'Flow Sub'` to `8.0` (SC-1d). This is the offender-#9/#10
mechanism and a fourth [HARD] target.

### Assumption Under Test
`flow_calc.owning_part_def_qn == redef.owning_part_qn == Flow_Sub` is an exact match (B4),
and `plant_value_shapes`' `usage_type_map` is **empty** — so (d) must NOT route through
`_find_literal_redefinition`'s Strategy-2 name-fallback (F4).

### Test Stencil (Write This First)
```python
# tests/conformance/test_plant_value_shapes.py  (flip 'Flow Sub')
def test_flow_sub_in_part_redefine_resolves_to_8():
    graph = generate_from_snapshot("plant_value_shapes")
    ep = ep_for(graph, "...flow_calc...flow_rate")
    assert ep.default_value == 8.0           # was DEGRADED valueless EP
    assert ep.qualified_name not in graph.fallback_entry_points
```

### Changes Required
**See design.md for:** F4; B4; precedence tier 2b (design.md#architecture "Precedence
resolution", leg 2b); data-flow for (d).

- [ ] **Tier-2b direct-owner leg** in the materializer: match a LITERAL redef by
  `redef.owning_part_qn == calc.owning_part_def_qn`. **Resolve the open** — add it as a new
  strategy inside `_find_literal_redefinition` vs a materializer-local exact match.
  **Recommend materializer-local** (keeps `_find_literal_redefinition`'s doc-18-fenced scope
  intact; the direct-owner match is this mechanism's operation, not aggregation LVP's).
  Record the choice.
- [ ] Bare-name (d) safety (INV-4): scope the synthesis to attrs actually referenced by an
  in-part binding; prefer same-instance to avoid a second unrelated `throughput` cross-wiring
  (reuse the existing `_resolve_to_design_attribute` same-instance preference).

### Validation
**Automated:**
- [ ] `'Flow Sub'` flip pin green (SC-1d); bare-name (d) does not cross-wire (INV-4).
- [ ] Full suite green.

**What We Know Works After This Phase:** all four value shapes resolve; the fusion-tea
in-part offenders #9/#10 have a working mechanism.

---

## Phase 5: The 48.5714 anchor test + three-tier precedence fixture (SC-1 / SC-2)

### Goal
Pin the arithmetic end-to-end at graph level, and prove the precedence order with distinct
values at each tier (the usage-override tier is unexercised by any existing fixture — this
item authors it).

### Assumption Under Test
- The carried values compose to the hand-derived anchor `(target_cost + chamber_cost) /
  driver_efficiency = (10 + 7) / 0.35 = 48.5714…`, and the anchor is **hand-transcribed**,
  never read back from the resolver (INV-5).
- Tier 1 (usage override) beats tier 2 (specialized-def `:>>`) beats tier 3 (base def),
  deterministically (INV-3).

### Test Stencil (Write This First)
```python
def test_plant_cost_anchor():
    # graph-level: the three EP values compose to the hand-derived constant
    assert ep_value(g, driver_eff) == 0.35 and ep_value(g, target) == 10.0 and ep_value(g, chamber) == 7.0
    # 48.5714 is hand-transcribed, NOT resolver-read
    assert abs((10.0 + 7.0) / 0.35 - 48.5714285714) < 1e-9

def test_precedence_usage_override_beats_specialized_def():
    # fixture: base valueless / Hif_Driver :>> efficiency=0.35 (tier2) / usage :>> driver.efficiency=0.99 (tier1)
    assert ep_value(g, driver_eff) == 0.99   # tier1 wins; reorder/skip → fails
```

### Changes Required
**See design.md for:** the anchor derivation (design.md#implementation-notes "Anchor");
the precedence fixture recipe (design.md#implementation-notes "Precedence fixture (SC-2)");
INV-3, INV-5.

- [ ] **Precedence fixture** (author, resolve its home — recommend a dedicated
  `plant_value_precedence` fixture, not overloading `plant_values`): base `efficiency`
  valueless / `Hif_Driver` `:>> efficiency = 0.35` / plant usage `:>> driver.efficiency =
  0.99` → resolves `0.99`. Capture at v2.
- [ ] The anchor test; pull the final chamber literal from the landed cure commit and update
  if not `7.0` (SC-1 provenance).

### Validation
**Automated:**
- [ ] Anchor pin green; precedence pin green; a deliberate tier-reorder in the fixture fails
  the precedence pin (prove it bites).

**What We Know Works After This Phase:** the values compose correctly and the precedence
contract is total and loud.

---

## Phase 6: SC-3 executor runner + tolerance test

### Goal
Stand up the minimal in-repo pipeline runner (a deliverable, reusable by Item 3) and prove
`spec_chain_twolevel` computes its lcoe-analog **by execution**, within `rel 1e-6`.

### Assumption Under Test
The generated package (modules + pipeline YAML + JSON inputs) executes to the hand-computed
value — graph inspection is not enough (spec Must-Fix 5).

### Test Stencil (Write This First)
```python
# tests/runtime/test_pipeline_runner.py  (NEW)
def test_twolevel_executes_to_hand_value(tmp_path):
    pkg = generate_package("spec_chain_twolevel", tmp_path)
    out = run_pipeline(pkg)                      # dict[str, float]
    assert out[LCOE_CHANNEL] == pytest.approx(HAND_VALUE, rel=1e-6)
```

### Changes Required
**See design.md for:** the pinned runner contract (design.md#sc-3-runner-interface-pinned-for-item-3,
`run_pipeline(package_dir, inputs) -> dict[str, float]`); F7.

- [ ] **`pipeline_runner.py`** (`tests/runtime/` or `src/.../runtime/`): read the pipeline
  YAML for execution order + per-module input wiring; import each generated module; feed
  entry-point inputs from `inputs` (falling back to emitted JSON) and module_output inputs
  from prior outputs; execute in order; return every channel's value. **Resolve the open:**
  teax-driven vs fixture-local driver — keep it minimal and YAML-driven; the fixture-local
  form is the D4-split follow-on candidate if it over-runs. Pin the signature verbatim (Item
  3 consumes it sight-unseen).

### Validation
**Automated:**
- [ ] Executor test green within `rel 1e-6`.
**Manual:**
- [ ] Signature matches the design's pinned contract exactly.

**What We Know Works After This Phase:** the generated package runs and produces the right
number by execution, not inspection.

---

## Phase 7: SC-4 fusion-tea proxy + baselines regen + V11 re-anchor (SC-4 / SC-5)

### Goal
Prove **true zero** V11 offenders on the committed fusion-tea snapshot; regenerate the two
touched fixtures' baselines as reviewed diffs; hold the four cross-part baselines
byte-identical; re-anchor the V11 raise-proof to a genuinely-deferred shape.

### Assumption Under Test
- All ten offenders clear (offender-arithmetic table: 8 cross-part a/b/c + 2 in-part d, #9
  canonical + #10 workaround-instance) → SC-4 true zero.
- The materializer causes **zero** unintended baseline drift on the four cross-part baselines.
- `plant_value_shapes` Shape 1 (`rated_cost__rate`) stays valueless (its value lives in a
  nested attribute-def bundle the materializer does not read) → valid new V11 raise-proof (D5).

### Test Stencil (Write This First)
```python
def test_fusion_tea_snapshot_zero_offenders():                 # SC-4
    graph = generate_from_snapshot(FUSION_TEA_SNAPSHOT)
    assert collect_uncovered_params(graph) == []               # all 10 cleared

def test_shape1_still_trips_v11():                             # SC-5 raise-proof re-anchor
    graph = generate_from_snapshot("plant_value_shapes")
    assert any(u.qualified_name.endswith("rated_cost__rate") for u in collect_uncovered_params(graph))
```

### Changes Required
**See design.md for:** SC-4/SC-5; D5 (Shape-1 re-anchor); the baseline-drift risk
(design.md#potential-risks).

- [ ] **Regenerate touched baselines** (reviewed diffs), scoped by `--fixtures`:
  - `uv run python scripts/capture_extraction_snapshots.py --fixtures plant_values,plant_value_shapes,spec_chain_twolevel`
  - `uv run python scripts/capture_pipeline_baselines.py --fixtures plant_values,plant_value_shapes`
  - `uv run python scripts/capture_baseline_yaml.py` (scoped equivalently if it supports `--fixtures`)
- [ ] **Four-cross-part byte-identity gate** — name the fixtures and the command explicitly.
  The two with committed computation-graph baselines are `catf_mfe` and `ife_plant`;
  `spec_chain_channel`/`spec_chain_twolevel`'s untouched pins are guarded by their conformance
  tests staying green (INV-1). Gate:
  ```bash
  uv run python scripts/capture_pipeline_baselines.py --fixtures catf_mfe,ife_plant
  git diff --exit-code tests/fixtures/baseline_outputs/catf_mfe tests/fixtures/baseline_outputs/ife_plant
  ```
  A non-empty diff must be a deliberately justified reviewed change (expected: none).
- [ ] Re-anchor the V11 raise-proof pin to `plant_value_shapes` Shape 1 (`rated_cost__rate`),
  replacing the now-cleared `'Flow Sub'` as the raise-proof.

### Validation
**Automated:**
- [ ] SC-4 zero-offender pin green; Shape-1 raise-proof green; `git diff --exit-code` on the
  four cross-part baselines is clean (or every hunk justified in the commit body).
**Manual:**
- [ ] Walk each regenerated diff on `plant_values`/`plant_value_shapes`/`spec_chain_twolevel`
  — every changed field is a resolved-value or fan-out reshape flowing from this mechanism,
  nothing incidental.

**What We Know Works After This Phase:** the epic CSF (zero V11 offenders on the fusion-tea
snapshot) is met; no collateral baseline drift; V11 still fires.

---

## Phase 8: Docs, matrix, Item-9 impact, close-out (SC-6)

### Goal
Record the new mechanism where the code that names it lives; add the REQ-SVM matrix block;
accumulate the Item-9 agentic-mbse impact; run close-out checks.

### Changes Required
**See design.md for:** SC-6; F1/D3 (REQ-SVM placement); the doc cross-ref map
(design.md#implementation-notes "New REQ family").

- [ ] **New doc 25 section "Supplied-Value Materializer"** (REQ-SVM-01..04), cross-referencing
  doc 18's shared `_find_literal_redefinition` helper and doc 12's VBR-03 sibling. **Do NOT**
  file under REQ-LVP-10 (contradicts doc 18's `18:163-167` fence) and leave REQ-LVP-*/
  REQ-VBR-* rows unchanged — the code they name does not change.
- [ ] Docs 11 (backtracker) + 12 (virtual-binding-rewrite) + modeling-assumptions §5: record
  the four supported value shapes and the fan-out-by-source-QN rule.
- [ ] **Matrix:** new `### SVM` block (4-col: REQ ID | Requirement | Test File | Status),
  cross-refs to doc 18's helper and doc 12's VBR-03.
- [ ] **Item-9 impact block:** the four supported whole-plant value shapes for the
  agentic-mbse MODELING_GUIDE, concrete-block style (Item-1 precedent).
- [ ] **Register/CURRENT_WORK update:** mark Item 2 implemented; note the offender-arithmetic
  table verified (true zero on committed fusion-tea snapshot), Shape-1 raise-proof green,
  materializer location + leg-2b home decisions recorded.

### Validation
- [ ] Matrix REQ-SVM rows each cite a green test file.
- [ ] Doc cross-refs resolve (doc 18 helper, doc 12 VBR-03).
- [ ] Suggest `/_my_audit` (do not self-certify — per workflow-accountability).

**What We Know Works After This Phase:** the mechanism is documented where its code lives,
the matrix moves with the code, and Item 9 has its impact block.

---

## D4 Split Fallback (documented, not pre-emptive)

Per design D4, **do not split**. If the runner (Phase 6) + renamed-fan-out leg (Phase 3)
push past budget, the fallback line is: **core** = Phases 1–2, 4–5, 7 (materializer +
(a)/(b)/(c)/(d) + precedence + headline flips + SC-4) as the shipped item; **follow-on** =
Phase 6 (SC-3 executor runner) + Phase 3 (renamed-consumer leg) + any deep-chain edge. The
core alone delivers the epic CSF (SC-4 is graph-level); only SC-3's execution gate slips.
If shape (d) proves un-landable within budget, invoke the **(d) escalation rule** (spec Open
Questions): return to the orchestrator, do not silently re-scope (d) out.

## Open Questions Resolved in This Plan (design's plan-time opens)

- **Materializer home:** new `resolution/supplied_values.py` (Phase 2) — recommendation,
  confirm at implement.
- **Leg 2b home:** materializer-local exact match, not a new `_find_literal_redefinition`
  strategy (Phase 4) — recommendation.
- **Precedence fixture home:** dedicated `plant_value_precedence` fixture (Phase 5).
- **0.0 capture row:** lands on `plant_values` or `plant_value_shapes` as an Item-2 rider
  (Phase 1/2) — the design leaves it open; place it where the 0.0 literal reads most naturally.
- **SC-3 runner form:** YAML-driven, fixture-local unless teax imports cleanly in-repo (Phase 6).

## Implementation Notes

[TO BE FILLED DURING IMPLEMENTATION — leave empty now]

### Phase 1 Completion
### Phase 2 Completion
### Phase 3 Completion
### Phase 4 Completion
### Phase 5 Completion
### Phase 6 Completion
### Phase 7 Completion
### Phase 8 Completion

---

**Status:** Draft → In Progress → Complete
