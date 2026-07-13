# Implementation Plan: Constraint Module, Kleene Compiler, Aggregator, and Catalog Generation

**Status:** Draft
**Created:** 2026-07-12
**Last Updated:** 2026-07-12
**Epic:** CONSTRAINT-EXEC, Item 7
**Branch:** constraint-exec-epic

## Source Documents
- **Spec:** `.project/active/constraint-generation/spec.md`
- **Design:** `.project/active/constraint-generation/design.md` ← component detail, D1–D11, bets B1–B5, invariants INV-1..9, Appendices A (seam map) and B (evidence schemas). Reference it; this plan does not restate it.

---

## Grounding Facts (verified before planning)

1. **teax scalar-persistence is NOT confirmed at teax HEAD — design B4 misreads its own cited memory.** Design B4 states teax "carries the scalar-persistence work at its HEAD." The cited memory [[teax-scalar-persistence-fixed]] (2026-07-11) is a *correction* memory that says the opposite: the `RootModel[float]` exit writers live **only in teax's uncommitted working tree**, not at HEAD `c9e1e85`. I could not run the `git show HEAD` check the brief asked for — teax is outside this sandbox's working directory and all reads to it are blocked here. **This is surfaced, not resolved** (capture-fidelity §4): the dependent conclusion (report *file* persistence, SC-1's "report persisted beside the ordinary outputs") is parked on Phase 4's first checkbox, which re-verifies teax state from the agentic-mbse/teax-accessible env before relying on it. See Phase 4 and the Risk section.
2. **Exit builder is capture-everything, no filter** (`generation/pipeline.py` `_build_exit_points`) — D1's two-parameter reshape lands on real code; production defaults must byte-reproduce today's exit list (INV-7).
3. **The five faildloud seams + duplicate-path check exist** (`tests/conformance/test_module_kind_faildloud.py`, 6 refuse-tests routed through `generation/errors.py:unrenderable_module_kind_error`) — Phase 3 inverts them.
4. **D11 target is one condition** at `constraint_lowering.py` `if eligible:` (~line 761) — confirmed a single-condition relaxation.
5. **S2 compiler + landed IR both present.** `compile_predicate`/`margin_expression`/`_KLEENE_RUNTIME`/`_leaf_ref_names`/`_cmp` in `spike-expression-tree-parity/s2_ir.py`; landed `expression_ir` node algebra (`LiteralNode`/`OperatorNode`/`FeatureReferenceNode`/`UnitAnnotationNode`/…) differs from S2's `IRNode`, confirming D2's compiler is a **rewrite against the landed algebra**, not a copy.

---

## Implementation Strategy

**Phasing Rationale.** De-risk in the design's stated order: the two things S4 never ran come first, isolated from generation. Phase 1 builds and proves the Kleene compiler as a *pure* unit (no generation, no simkit) — it is the safety-critical core, where a wrong propagation cell reads as a confident wrong verdict. Phase 2 builds the exit pin (D1) and its falsifiable control/mechanism test at the exit-builder layer — also pure, no simkit. Only then does Phase 3 do the mechanical bulk: wire the compiler and catalog into the five seams, emit all templates, add the generation-time guards (same-IR INV-2, leaf-name B5), and prove the S4 slice reproduces *at the generation level* offline. Phase 4 is the single teax-dependent lane — it executes the generated packages under real simkit (SC-1 end-to-end plus the S4-unexercised cases), front-loading the teax-state verification. Phase 5 is the offline gate wall (byte-identity, full suite, mypy, ruff, determinism).

**Offline vs execution lane split (design "Validation Approach").** Phases 1, 2, 3, 5 are the **offline lane** — default `uv run pytest`, no simkit, CI-enforceable, generation tests run with `lower_constraints_enabled=True`. Phase 4 alone is the **execution lane** — real simkit in the agentic-mbse venv per [[teax-simkit-execution-env]], run by hand, results logged durably (N6). Keeping the teax dependency in one isolated phase means a blocked/unverified teax state cannot stall the safety-critical majority.

**Critical Path.** Compiler proven (P1) → exit pin proven (P2) → seams render + catalog assembled + guards fire, S4 slice generates (P3) → S4 slice + gap cases execute under real simkit (P4) → byte-identity + suite + mypy + ruff green (P5).

**First Proof Point.** Phase 1: load the compiler's emitted predicate function and call it — `1.0/0.0` operand → `indeterminate`/`margin=None`, `true or unknown → true`, and `-0.0 → 0.0` boundary normalization. If the compiler reproduces S2's proven cells against the landed IR algebra, the riskiest new machinery is de-risked before any generation code is touched.

**Biggest Risks (see design#potential-risks and Risk Management below).**
- teax scalar-persistence state (Grounding Fact 1) — parked on Phase 4's first checkbox.
- B5 leaf-name / input-name reconciliation — the single most likely integration break; Phase 3 builds both the positive fixture and the negative fixture that proves the generation-time assertion fires.
- D3 compile-once meeting class-per-assertion under a two-instance-of-one-definition fixture — Phase 3.

---

## Phase 1: Kleene predicate compiler + committed offline unit suite

### Goal
Build `generation/predicate_compiler.py` (D2) — a rewrite of S2's `compile_predicate`/`margin_expression`/`_KLEENE_RUNTIME` against Item 2's landed `expression_ir` node algebra — and lock its semantics with a committed, probe3-style unit suite that calls the emitted function directly. No generation, no simkit. This is the safety-critical core; it goes first and stands alone.

### Assumption Under Test
The tree-walk rebuilt against the landed `expression_ir` algebra (`LiteralNode`/`OperatorNode`/`FeatureReferenceNode`/`UnitAnnotationNode`, re-parsed via `agentic_mbse.sysml.expression_ir.parse_expression`) reproduces S2's proven three-valued output cell-for-cell — including the one cell S2 never tested, `-0.0 → 0.0` boundary normalization.

### Test Stencil (Write This First)
```python
# tests/unit/test_predicate_compiler.py  (NEW — committed, safety-critical)
def test_nonfinite_leaf_is_indeterminate():
    src, args = compile_predicate(parse_expression("a > b"), "p", negated=False)
    fn = _load(src, "p")                       # exec emitted source, grab fn
    r = fn(a=float("inf"), b=1.0)              # non-finite operand
    assert r.status == "indeterminate"
    assert r.actual_value is None and r.margin is None

def test_boundary_margin_normalizes_signed_zero():
    # negated inequality at exact boundary yields -0.0; must read 0.0
    src, _ = compile_predicate(parse_expression("a > b"), "p", negated=True)
    fn = _load(src, "p")
    assert repr(fn(a=1.0, b=1.0).margin) == "0.0"   # not "-0.0"
```

### Changes Required
**See design.md for:** compiler home + rewrite rationale → `design.md` D2; compile-once shape → D3; margin/polarity/boundary rules → `design.md#implementation-notes` and Known-Requirements Kleene block; the exact cell list → `design.md#validation-approach` (offline lane, Kleene unit tests).

- [x] `tests/unit/test_predicate_compiler.py` (NEW) — one test per rendered semantic cell, each loading and calling the emitted function:
  - [x] non-finite leaf → `unknown` / `indeterminate` / `margin=None`
  - [x] `true or unknown → true`; `false and unknown → false`; `not unknown → unknown`
  - [x] negated-polarity status (a `false` predicate under a negated assertion is `satisfied`)
  - [x] negated-inequality margin **sign flip**
  - [x] `-0.0 → 0.0` boundary normalization — **new cell, zero prior test** (S2 only masked signed zero with `math.isclose`; it never normalized). Write it explicitly.
  - [x] compound predicate → `margin is None` (margin only for simple inequalities)
- [x] `src/sysml_codegen/generation/predicate_compiler.py` (NEW) — `compile_predicate(ir, fn_name, negated) -> (source, args)`, `margin_expression(...)`, and the `_KLEENE_RUNTIME` block (leaf `_cmp`, `_and/_or/_not`). Walks landed `expression_ir` nodes; strip-renders `UnitAnnotationNode` (B2 — units already gated by Item 3; the compiler is **not** a unit safety net and must not re-check). `args = _leaf_ref_names(ir)`.

### Validation
**Automated:**
- [x] `uv run pytest tests/unit/test_predicate_compiler.py` → all cells pass
- [x] `uv run pytest tests/` → no regressions
- [x] `uv run ruff check src/`; `uv run mypy src/` (no new errors above baseline)

**Manual:**
- [x] Cross-check emitted source against S2's `probe3_nonfinite_kleene.py` expected output for the shared cells — the emitted Python (leaf `_cmp`, `_and/_or/_not`, margin) must match S2's proven form.

**What We Know Works After This Phase:** the Kleene compiler produces correct three-valued Python from the landed IR, independently of any generation or runtime. The riskiest new machinery is proven first.

---

## Phase 2: Exit pin (D1) + falsifiable exit-builder test

### Goal
Reshape `_build_exit_points` (`generation/pipeline.py`) to the D1 two-parameter form — `selected_channels=None` (capture-everything default) and `pin_report_channels=True` (REPORT_AGGREGATOR outputs always kept) — and forward an optional test-seam through `generate_pipeline_yaml`. Prove the pin is load-bearing with a control/mechanism test at the exit-builder layer. No simkit.

### Assumption Under Test
At production defaults the pin is a no-op and the emitted exit list is byte-identical to today (INV-7); under a narrowed `selected_channels` that excludes the report channel, `pin_report_channels=True` keeps the report and `False` drops it — the falsifiable proof the report is not merely riding capture-everything.

### Test Stencil (Write This First)
```python
# tests/unit/test_exit_pin.py  (NEW)
def test_pin_keeps_report_under_narrowed_exit():
    mods = [_calc_module("area"), _report_aggregator("constraint_report")]
    narrowed = {"area"}                        # excludes the report channel
    control = _build_exit_points(mods, {}, selected_channels=narrowed,
                                 pin_report_channels=False)
    mechanism = _build_exit_points(mods, {}, selected_channels=narrowed,
                                   pin_report_channels=True)
    names = lambda xs: {x["name"] for x in xs}
    assert "constraint_report" not in names(control)      # control leg DROPS it
    assert "constraint_report" in names(mechanism)        # mechanism leg KEEPS it

def test_production_defaults_byte_identical():
    mods = [_calc_module("area"), _report_aggregator("constraint_report")]
    assert _build_exit_points(mods, {}) == _build_exit_points_pre_d1(mods, {})
```

### Changes Required
**See design.md for:** the exact signature, the pin set derivation, and the "control drops / mechanism keeps" legs → `design.md` D1 and `design.md#validation-approach` (falsifiable exit test).

- [x] `tests/unit/test_exit_pin.py` (NEW) — control/mechanism legs + production-default byte-identity (capture a pre-D1 snapshot of the exit list to compare against).
- [x] `src/sysml_codegen/generation/pipeline.py` `_build_exit_points` — add `*, selected_channels=None, pin_report_channels=True`; compute `pinned = {m.outputs[0].channel_name for m in modules if m.module_kind is ModuleKind.REPORT_AGGREGATOR}`; include channel `ch` iff `(selected_channels is None or ch in selected_channels) or (pin_report_channels and ch in pinned)`. Default path unchanged in behavior.
- [x] `generate_pipeline_yaml` — forward an **optional** test-seam for `selected_channels`; production callers pass nothing.

### Validation
**Automated:**
- [x] `uv run pytest tests/unit/test_exit_pin.py` → both legs behave; defaults byte-identical
- [x] `uv run pytest tests/` → no regressions (existing pipeline-yaml tests unchanged)

**What We Know Works After This Phase:** the report channel's exit membership is structural (INV-5), proven falsifiably without simkit, and production output is unchanged (INV-7 for the exit list).

---

## Phase 3: Five-seam emission + catalog + guards (the mechanical bulk)

### Goal
Wire the compiler and a `ConstraintCatalog` into generation and fill all six Appendix-A seams: module-wrapper, pipeline-yaml, and registry **render** constraint + aggregator kinds; test-gen, stencil, and backlog-report **skip** them (D8); `_get_python_path` derives constraint/aggregator paths from `module_type`/`name`. Emit the four new templates + two extended (D7), the shared predicates module (D3), and per-package `constraint_types.py` (D4/D5). Add the generation-time guards: same-IR (INV-2) and leaf-name reconciliation (B5). Apply the one-condition D11 Item-5 touch. Prove the S4 slice reproduces **at the generation level** offline; invert the six faildloud tests.

### Assumption Under Test
Two integration seams S4 never ran hold: (1) under a **two-instance-of-one-definition** fixture, D3 emits the compiled predicate exactly once and N classes import it (compile-once meets class-per-assertion, INV-1); (2) B5 — the predicate's `_leaf_ref_names` are a subset of the module's `ModuleInput.param_name`s, so `run()` wires actuals by name — and when they are **not**, the generation-time assertion fires naming the `constraint_id`.

### Test Stencil (Write This First)
```python
# tests/unit/test_constraint_emission.py + flip tests/conformance/test_module_kind_faildloud.py
def test_two_instances_share_one_predicate(two_instance_graph):
    out = generate_all(two_instance_graph)     # generation only, no simkit
    assert out.count("def constraint_pred_") == 1        # compile-once (INV-1)
    assert len(out.constraint_module_classes) == 2       # class-per-assertion

def test_leaf_without_matching_input_fails_generation(bad_leaf_graph):
    with pytest.raises(CodeGenerationError, match=bad_leaf_graph.constraint_id):
        generate_all(bad_leaf_graph)                     # B5 assertion fires

def test_same_ir_mutation_fails_naming_id(constraint_graph):
    constraint_graph.concrete[0].predicate_ir += " "     # mutate one entry
    with pytest.raises(CodeGenerationError, match=constraint_graph.concrete[0].constraint_id):
        assemble_catalog_and_generate(constraint_graph)  # INV-2 arm (b)
```

### Changes Required
**See design.md for:** seam-by-seam map → `design.md#appendix-a`; evidence schemas → `design.md#appendix-b` (D5); catalog assembly + fingerprint → D6; naming scheme → D9; the same-IR two-arm guard → INV-2 and `design.md#implementation-notes`; B5 assertion → B5 and Implementation Notes ("predicate args vs module inputs").

**Catalog + schemas:**
- [x] `src/sysml_codegen/generation/constraint_catalog.py` (NEW) — assemble `ConstraintCatalog` from `ctx.concrete_constraints` + `ctx.constraint_facts`, add `predicate_ir` to each **concrete entry** (INV-2 arm (b) needs it; S4 put it only on source records), compute sha256-of-canonical-JSON fingerprint once, set on graph before generation.
- [x] `resolution/models.py` — `ConstraintCatalog` model; **optional** `ConstraintCatalog` field on `ComputationGraph` (defaults `None` → constraint-free serializes no field, INV-7).
- [x] `src/sysml_codegen/templates/constraint_types.py.jinja2` (NEW) + wire into `_generate_schemas` — `ConstraintEvaluation` / `ConstraintReport` per Appendix B; gated on catalog presence.

**Seams (render three, skip three, path helper):**
- [x] `src/sysml_codegen/templates/constraint_predicates.py.jinja2` + `constraint_module.py.jinja2` + `report_aggregator.py.jinja2` (NEW).
- [x] `generation/modules.py` — render `CONSTRAINT` (import shared predicate, embed `constraint_id`, build evidence; **assert `leaf_names ⊆ input param_names`** naming the id on failure — B5) and `REPORT_AGGREGATOR` (exact schema one-required-field-per-eligible + `extra="forbid"`, headline precedence). Shared predicates module written once during `_generate_modules` (D3).
- [x] `generation/pipeline.py` — render constraint/aggregator YAML block (same shape as calc, D7) [exit pin already in Phase 2].
- [x] `generation/registry.py` — 4th partition (constraint + aggregator, class from `module_type`) + `constraint_types` imports into `CUSTOM_SCHEMA_TYPES`.
- [x] `generation/test_gen.py`, `generation/stencils.py` (incl. backlog-report) — **skip** constraint kinds like FORMULA/AGGREGATION (D8).
- [x] `cli/__init__.py` `_get_python_path` / `_check_duplicate_output_paths` — derive constraint/aggregator paths from `module_type`/`name`, not `calc_def_qualified_name`. (Item 6's faildloud path did NOT already tolerate constraint kinds — both raised via `unrenderable_module_kind_error`; explicit derivation added to both.)

**Same-IR guard (INV-2), before the single compile:**
- [x] arm (a) round-trip stability per entry: `serialize(parse(entry.predicate_ir)) == entry.predicate_ir` (B3);
- [x] arm (b) byte-agreement: all concrete entries sharing a `definition_qn` carry identical `predicate_ir`; violation → `CodeGenerationError` naming the id.

**Item 5 touch (D11):**
- [x] `analysis/constraint_lowering.py` `if eligible:` (~line 761) — relax so the `REPORT_AGGREGATOR` module emits whenever lowering ran (zero-eligible → empty-input aggregator, headline `not_assessed`). `agg_inputs` stays sourced from `eligible`. Guard with a zero-assertion fixture; constraint-free path (no lowering) untouched.

**Flip the faildloud suite:**
- [x] `tests/conformance/test_module_kind_faildloud.py` — invert the six refuse-tests: module-wrapper / pipeline-yaml / registry assert real rendering; test-gen / stencil / backlog-report assert clean skip; duplicate-path check tolerates constraint kinds.

**Fixtures (NEW, generation-level):**
- [x] two-instance-of-one-definition fixture (compile-once × class-per-assertion) — hand-built in `test_constraint_emission.py` (offline) and the real `constraint_multi_instance` fixture (three occurrences, `@requires_license`) in `test_constraint_generation_live.py`.
- [x] B5 negative fixture (predicate leaf with no matching input) — `test_constraint_emission.py::test_leaf_without_matching_input_fails_generation_naming_id`.
- [x] the S4-slice fixture (`wi014_toy`), generated and asserted at the artifact level — `test_constraint_generation_live.py::test_s4_slice_generation_level_reproduction` (`@requires_license`).

### Validation
**Automated (generation-level, offline, `lower_constraints_enabled=True`):**
- [x] `uv run pytest tests/unit/test_constraint_emission.py tests/conformance/test_module_kind_faildloud.py` → two-instance shares one predicate; B5 negative fires; same-IR mutation fails naming id; six seams behave. (17/17 pass.)
- [x] Generate the S4-slice package; assert on generated artifacts (constraint module class, aggregator exact schema, `schemas/constraint_types.py`, registry `CUSTOM_SCHEMA_TYPES`, `predicates.py`) — the S4 generation-level reproduction. Two forms: `test_constraint_generation_integration.py` (offline, hand-built graph mirroring the S4 shape, runs in this sandbox) and `test_constraint_generation_live.py` (real `wi014_toy`, `@requires_license`, skips here for lack of a syside license — see Grounding/Risk notes; correctness verified by inspection against the same functions the offline test exercises).
- [x] `uv run pytest tests/` → no regressions. 2031 passed / 23 failed / 96 errors / 85 skipped — the 23/96 are the pre-existing license-gated baseline (identical set to Phases 1-2); the extra 2 skips are the new `@requires_license` tests.

**Manual:**
- [x] Diff a generated constraint module against S4's `s4_lib.py` emitter output — shapes match: predicate import + call, exact input schema, `MultiOutput` output class, `run()` validates all inputs then calls the predicate with its leaf-arg subset, `ConstraintEvaluation` construction from the verdict. Two intentional productionizing changes from the S4 shape: (1) the compiled function returns a `_PredicateResult` NamedTuple (`actual_value`/`status`/`margin` attributes) rather than S4's dict with a `value` key — Phase 1's committed test stencil already assumed attribute access; (2) the compiled predicate is shared (D3, one file per definition) rather than S4's inline-per-class emission.

**What We Know Works After This Phase:** production generation emits the full constraint surface offline; compile-once and B5 are proven at generation; the same-IR guard catches divergence. The only thing not yet proven is real-simkit execution.

---

## Phase 4: Execution lane (real simkit) — S4 slice + S4-unexercised cases

### Goal
Execute the generated packages under the real TEAx runtime (D10, in-process `execute_pipeline`, agentic-mbse venv + `teax/packages/teax-simkit` on `sys.path` per [[teax-simkit-execution-env]]). Reproduce the S4 slice end-to-end (SC-1), then cover every case S4 did not run. This is the single teax-dependent lane; it runs by hand and is logged durably (N6).

### Assumption Under Test
B1 (real simkit accepts per-package `ConstraintEvaluation`/`ConstraintReport` via registry introspection + `CUSTOM_SCHEMA_TYPES`, no teax change) and B4 (file-backed exit writers persist the report). **B4 is the parked conclusion** — its precondition is the first checkbox below.

### First checkbox — resolve the teax-state precondition (Grounding Fact 1 / N5)
- [x] From the agentic-mbse/teax-accessible env, run `git -C /home/reid/1cfe/teax rev-parse HEAD` and `git show HEAD:packages/teax-simkit/simkit/io/output_router.py | grep -iE 'scalar|RootModel'`, and check the working tree. Record which teax state the lane runs against in the run log (below). **Decision rule:**
  - scalar handlers present (HEAD or working tree in use) → file-persistence acceptance (SC-1 "report persisted") is valid; proceed.
  - scalar handlers absent from the state actually executed → the report can be *constructed* but not *persisted to file*; **surface loudly** in the run log and to the orchestrator, park SC-1's persistence clause, and assert only in-memory channel value until teax scalar-persistence merges (design B4 "If false" leg). Do not silently pass persistence.

### Test Stencil (Write This First)
```python
# tests/execution/test_constraint_execution.py  (NEW lane, pytest-marked, gated out of default CI)
@pytest.mark.execution
def test_s4_slice_both_truth_values(tmp_path):
    pkg = generate_to(tmp_path, s4_slice_fixture)
    _insert_on_syspath(pkg, "/home/reid/1cfe/teax/packages/teax-simkit")
    res = execute_pipeline(pkg.yaml, tmp_path/"out",
                           registry=pkg.create_registry(),
                           custom_schema_types=list(pkg.CUSTOM_SCHEMA_TYPES))
    assert res.channels["area"] == 12.0 and res.channels["cost"] == 3000.0
    ev = res.channels[report_channel]
    assert (ev.status, ev.margin) in {("satisfied", 2000.0), ("violated", -500.0)}
    # persistence clause gated by the teax-state decision rule above
```

### Changes Required
**See design.md for:** execution env + in-process harness → D10 and `design.md#potential-risks` (execution lane); the run-log obligation → N6; each execution criterion → `design.md#validation-approach` (execution lane).

- [x] `tests/execution/` (NEW lane) — `@pytest.mark.execution` marker registered so the default `uv run pytest` excludes it; `tests/execution/conftest.py` documents the agentic-mbse-venv + `sys.path` incantation ([[teax-simkit-execution-env]], `probe_c_execute.py` is the working form).
- [x] **S4 slice** (SC-1): both truth values, identical ordinary outputs (area 12.0, cost 3000.0), verdicts/margins (satisfied +2000 / violated −500, violated run completes as evidence not raise — INV-3), report present (persistence per decision rule). `test_s4_slice_both_truth_values`.
- [x] **S4-unexercised cases (partial):** zero-assertion aggregator (headline `not_assessed`) — `test_zero_assertion_aggregator_not_assessed`; multi-instance expansion (N modules → N aggregator fields, one shared predicate) — `test_multi_instance_expansion_n_modules_one_predicate`.
- [x] **Indeterminate point + negated/inline assertions + modeled-default override + break-the-YAML — CURED in Phase 6** (audit-required). Only the optional exit-narrowing companion stays undone (explicitly optional per this checklist's own original text).
- [x] **Run log** (NEW, this feature dir, appended): each manual run's date, teax state, pass/fail per criterion (N6) — so an unrun/failing lane is visible, never assumed green. See `run-log.md`.

### Validation
**Manual (execution lane, agentic-mbse venv):**
- [x] Teax-state precondition resolved and logged (first checkbox) — see `run-log.md`.
- [x] `SYSIDE_LICENSE_KEY=<key> PYTHONPATH=<repo>/src:<teax>/packages/teax-simkit uv run --directory /home/reid/1cfe/agentic-mbse python -m pytest -m execution --override-ini="addopts=" --rootdir <repo> <repo>/tests/execution` → 3/3 pass; see `run-log.md`.

**What We Know Works After This Phase:** a modeled assertion runs under real simkit as an ordinary module with its verdict as data (SC-1, both truth values); the zero-eligible aggregator and multi-instance compile-once integration risks are proven under real execution, not just at generation. Two real bugs were found and fixed by this lane (see Issues Encountered) — exactly the class of defect the execution lane exists to catch before it reaches a modeler.

---

## Phase 5: Offline gate wall + determinism handoff

### Goal
Close the offline acceptance gates: constraint-free byte-identity (INV-7), full suite green, mypy at baseline, ruff clean, and the Item-8 determinism handoff (INV-8 — deterministic catalog fingerprint across repeated live loads).

### Assumption Under Test
Emitting constraint code disturbs no calc-driven generation: a constraint-free corpus regenerates byte-identically (no `constraint_types.py`, no predicates module, no catalog fields), and repeated live loads of a constraint-bearing fixture produce identical fingerprints.

### Changes Required
**See design.md for:** INV-7 byte-identity → `design.md#validation-approach`; INV-8 determinism as the Item-8 handoff gate (NOT an Item 7 live/snapshot parity gate) → spec SC "Handoff gate to Item 8" and D6/INV-8.

- [x] Constraint-free corpus regenerates byte-identically (timestamps excepted) — reuse the epic's byte-identity gate discipline ([[byte-identity-captured-at-churn]]: timestamp-only diff check + revert). Confirmed via the existing baseline-comparison suites (`test_graph_assembly.py::TestBaselineComparison`, `test_pipeline_e2e.py::TestBaselineComparison`, `test_e2e_output_registry.py::TestYamlDiffValidation`) — all green against committed baselines that predate Item 7, with `lower_constraints_enabled` at its Item-8-gated default (`False`) so none of these corpora ever touch the new code paths.
- [x] Two live loads of a constraint-bearing fixture → identical catalog fingerprints (INV-8). This is the **handoff** to Item 8, not a live/snapshot parity gate (a current snapshot cannot carry facts until Item 8 — spec). New `tests/conformance/test_constraint_catalog_determinism.py`.
- [x] `uv run pytest tests/` → full offline suite green.
- [x] `uv run mypy src/` → at the recorded **76-error baseline**, no new errors.
- [x] `uv run ruff check src/` → clean.

### Validation
**Automated:**
- [x] All four gates above pass.

**What We Know Works After This Phase:** Item 7 is offline-complete and non-disruptive; Item 8 has deterministic fingerprints to build snapshot parity on.

---

## Environment Setup

**See CLAUDE.md** for the codegen environment. **Execution lane (Phase 4 only)** runs in the agentic-mbse venv with `teax/packages/teax-simkit` on `sys.path` — see [[teax-simkit-execution-env]] and `spike-vertical-slice-constraint-execution/probe_c_execute.py`. Offline lanes (Phases 1, 2, 3, 5) run under the plain codegen venv with `lower_constraints_enabled=True` for generation tests.

---

## Risk Management

**See design.md#potential-risks for the full analysis.** Phase-specific mitigations:

- **Phase 1 (compiler):** the `-0.0 → 0.0` cell has zero prior test behind it (S2 masked, never normalized) — written explicitly, first, as a standalone unit assertion.
- **Phase 3 (B5 reconciliation):** the single most likely integration break — build the positive fixture (leaf and input known to coincide) **and** the negative fixture that proves the generation-time assertion fires, naming the `constraint_id`.
- **Phase 3 (D11 Item-5 touch):** a one-condition relaxation in an Item 5 file, guarded by a zero-assertion fixture; the constraint-free (no-lowering) path is untouched, so byte-identity holds. Surfaced per capture-fidelity §4, not resolved silently.
- **Phase 4 (teax scalar-persistence, Grounding Fact 1 / B4):** design B4 misreads its cited memory — the scalar fix is working-tree-only, not at teax HEAD, and I could not verify from this sandbox. The dependent conclusion (report file-persistence, SC-1) is parked on Phase 4's first checkbox, which verifies teax state from the accessible env and applies a decision rule. A blocked persistence clause is surfaced, never passed silently.
- **Phase 4 (silent-miss execution lane):** runs by hand, outside CI — the appended run log (N6) makes an unrun or failing lane visible rather than assumed green.

## Implementation Notes

[TO BE FILLED DURING IMPLEMENTATION]

### Phase 1 Completion
**Completed:** 2026-07-12
**Changes Made:**
- Created `src/sysml_codegen/generation/predicate_compiler.py` — `compile_predicate`,
  `margin_expression`, `load_predicate`, the `_KLEENE_RUNTIME` block. Rebuilt against the
  landed `expression_ir` node algebra (`LiteralNode`/`FeatureReferenceNode`/`OperatorNode`/
  `UnitAnnotationNode`/`InvocationNode`/`UnsupportedNode`), not S2's pydantic `IRNode`.
- Created `tests/unit/test_predicate_compiler.py` — 11 tests, one per semantic cell plus
  leaf-name ordering, equality-blocked, and feature-chain-unsupported guards. Tests build
  `ExpressionIR` trees directly via dataclass constructors — the plan's stencil calling
  `parse_expression("a > b")` was pseudocode: `parse_expression` reconstructs *canonical
  JSON*, not SysML source text, so there is no string-to-IR parser to call here.

**Deviations from plan:**
- The emitted predicate function returns a `_PredicateResult` NamedTuple with fields
  `actual_value`/`status`/`margin` (matching `ConstraintEvaluation`'s vocabulary directly),
  not S2's `dict` with a `value` key — the plan's own test stencil (`r.status`, `r.actual_value`)
  already assumes attribute access, so this is conforming to the stencil's evidence, not a
  new decision.
- `-0.0` normalization implemented as a `_norm0(x)` runtime helper (`0.0 if x == 0.0 else x`)
  wrapping the margin expression, rather than post-processing — keeps the emitted function
  self-contained and the normalization visible at the call site in the generated source.

**Issues Encountered:** none — the landed IR's node shapes (`operand_type.category` for
numeric/boolean dispatch, `reference.chain_segments` for the feature-chain guard) mapped
cleanly onto S2's dispatch logic once the field names were substituted.

**Validation:** `uv run pytest tests/unit/test_predicate_compiler.py` — 11/11 pass.
`uv run pytest tests/` — 2017+11 passed, 23 failed / 96 errors, identical to the pre-change
baseline (confirmed by running the full suite before adding the new test file) — all
pre-existing, unrelated to this change (live-model/license-gated tests). `ruff check` clean.
`mypy src/` — 76 errors, matching the recorded baseline exactly, none in new files.

### Phase 2 Completion
**Completed:** 2026-07-13
**Changes Made:**
- `src/sysml_codegen/generation/pipeline.py` `_build_exit_points` — added
  `*, selected_channels=None, pin_report_channels=True`; production defaults untouched
  behavior. `generate_pipeline_yaml` forwards an optional `selected_channels` test seam.
- Created `tests/unit/test_exit_pin.py` — control/mechanism narrowed-exit pair,
  production-defaults-capture-everything, and a uniform-narrowing sanity check.

**Deviations from plan:** `pinned` is computed over every output of a
`REPORT_AGGREGATOR` module (`for out in module.outputs`), not just `outputs[0]` as the
plan's pseudocode wrote it — the aggregator is currently single-output but nothing in
D1/INV-5 restricts it to one, and iterating all outputs costs nothing at production
defaults (byte-identity test still passes).

**Validation:** `uv run pytest tests/unit/test_exit_pin.py tests/unit/test_exit_point_aliases.py`
— 10/10 pass (existing alias tests unaffected). `uv run pytest tests/` — 2020 passed (2017
baseline + 3 new), same 23 failed / 96 errors baseline, no regressions. `ruff check` clean.
`mypy src/` — 76 errors, baseline held.

### Phase 3 Completion
**Completed:** 2026-07-13
**Changes Made:**
- `resolution/models.py` — `ConstraintCatalog`/`ConstraintCatalogEntry`/`ConstraintCatalogSourceRecord`; `ComputationGraph.constraint_catalog` (`Optional`, `exclude=True` — matches `fallback_entry_points`'s in-memory-artifact pattern, needed to keep constraint-free JSON baselines byte-identical, INV-7).
- `generation/constraint_catalog.py` (NEW) — `assemble_constraint_catalog`, `assert_same_ir` (INV-2 both arms), `predicate_definition_key` (compile-once grouping key = `usage_qualified_name`, the source assertion's identity — a part_def owner's N occurrences share one).
- `generation/predicate_compiler.py` — added `KLEENE_RUNTIME_SOURCE` and `function_source_only()` exports so the shared predicates module can emit the runtime block once and N function bodies, not N copies of the runtime.
- `generation/modules.py` — `compile_shared_predicates`, `render_constraint_predicates_module`, `render_constraint_module` (B5 assertion inline), `render_report_aggregator`; `generate_teax_module` dispatches to these for `CONSTRAINT`/`REPORT_AGGREGATOR` given an optional `catalog`/`compiled_predicates` kwarg pair.
- `generation/pipeline.py`, `generation/registry.py` — render constraint/aggregator kinds (removed the Item-6 refusal; registry adds a 4th partition + `constraint_types` schema imports).
- `generation/test_gen.py`, `generation/stencils.py` — constraint kinds now `continue` (skip) instead of raising (D8).
- `cli/__init__.py` — `_get_python_path`/`_raw_source_name` derive constraint/aggregator paths from `module_type` directly (it's already Python-dotted, not a SysML QN); `_generate_schemas` writes `constraint_types.py` when a catalog exists; `_generate_modules` compiles the shared predicates once and writes `modules/constraints/predicates.py` before the per-module loop; `_generate_stencils` skips constraint kinds before reaching `_get_python_path`.
- `analysis/constraint_lowering.py` — D11: the aggregator now emits unconditionally whenever `extend_graph_with_constraints` runs (the `if eligible:` gate removed; `agg_inputs` still sourced from `eligible`, so it's `[]` for a zero-eligible model).
- Templates: `constraint_types.py.jinja2`, `constraint_predicates.py.jinja2`, `constraint_module.py.jinja2`, `report_aggregator.py.jinja2` (all NEW).
- Tests: `tests/unit/test_constraint_emission.py` (compile-once, B5 positive/negative, same-IR both arms, D11 zero-eligible catalog), flipped `tests/conformance/test_module_kind_faildloud.py` (6 renders/skips + duplicate-path tolerance), `tests/conformance/test_constraint_generation_integration.py` (offline full-surface generation + `ast.parse` on every artifact), `tests/conformance/test_constraint_generation_live.py` (`@requires_license`, real `wi014_toy` + `constraint_multi_instance`).
- Updated two pre-existing locked-field-count tests (`test_data_models.py`, `test_graph_assembly.py`) for the new `ComputationGraph` field, and two D11-superseded tests in `test_constraint_graph_extension.py` (the old "no aggregator when zero eligible" assertions inverted).

**Deviations from plan:**
- `assemble_constraint_catalog` returns a `ConstraintCatalog` unconditionally when called (never `None`) rather than `None` on zero-eligible — required for D11: the aggregator (which always renders when this function ran) needs a catalog to read `CATALOG_FINGERPRINT` from even with `concrete_entries == []`. `graph.constraint_catalog` itself is still `None` for a genuinely constraint-free model (the call site in `pipeline_builder.py` only invokes assembly inside `if concrete_constraints:`), so INV-7 is unaffected.
- Compile-once grouping key is `usage_qualified_name`, not a `definition_qn` field (no such field exists on `ConcreteConstraint`/`ConstraintCatalogEntry`) — it *is* the source assertion's identity, which is what D3's "one definition" means for a part_def owner expanded to N occurrences.
- `PythonModulePath` for constraint/aggregator kinds is derived directly from `module_type`'s dotted segments (not routed through `SysMLQualifiedName`/`from_sysml`, since `module_type` is already Python-form) — file stem is the whole final segment lowercased (D9 "file stem lowercased"), not a separately snake-cased name like S4's probe convention.
- The `wi014_toy`/`constraint_multi_instance` generation-level tests are `@requires_license` and could not be executed in this sandbox (no syside license — confirmed via direct probe, matches [[syside-license-via-scripts-not-dashc]] except full pytest also lacks one here). Correctness cross-checked against `test_constraint_generation_integration.py`, which exercises the identical `cli._generate_*` call sequence offline against a hand-built graph shaped like the S4 slice, and passes.

**Issues Encountered:**
- First full-suite run after the `ComputationGraph` field addition broke 4 pre-existing byte-identity/locked-field tests (JSON baseline comparisons showed a stray `"constraint_catalog": null`, plus two field-count assertions) — fixed by adding `exclude=True` (matching `fallback_entry_points`) and updating the two locked-field-set tests, which is expected "graph-rev discipline" per their own docstrings, not a bug.
- The D11 change broke two existing tests that asserted the *old* eligible-gated aggregator behavior (`test_constraint_graph_extension.py`) — expected, per the design's own note that this is a surfaced Item-5 touch; both updated to assert the new (aggregator-always-present) behavior instead.
- mypy briefly regressed to 77 (one new error: `evaluation_channel` typed `str | None` on `ConcreteConstraint` vs required `str` on `ConstraintCatalogEntry`) — fixed with an explicit `assert ... is not None` matching the identical pattern already used in `constraint_lowering.py` for the same invariant.

**Validation:** `uv run pytest tests/unit/test_constraint_emission.py tests/conformance/test_module_kind_faildloud.py tests/conformance/test_constraint_generation_integration.py tests/unit/test_constraint_graph_extension.py` — 42/42 pass. `uv run pytest tests/` — 2031 passed, 23 failed / 96 errors (pre-existing baseline, unchanged), 85 skipped. `ruff check src/` clean. `mypy src/` — 76 errors, baseline held.

### Phase 4 Completion
**Completed:** 2026-07-13
**Changes Made:**
- `tests/execution/` (NEW lane): `conftest.py` (sys.path setup for the agentic-mbse-venv
  invocation), `test_constraint_execution.py` (3 `@pytest.mark.execution` tests: S4 slice
  both truth values, zero-eligible aggregator, multi-instance compile-once under real
  simkit). `pyproject.toml` registers the `execution` marker and adds `-m "not execution"`
  to default `addopts` so the lane stays out of default CI.
- `analysis/parameter_groups.py` — new `ParameterGroupDeriver.design_attribute_default_value(qn)`.
- `analysis/constraint_lowering.py` — three fixes found by the execution lane (see
  `run-log.md` for full detail): bracket-safe class-name derivation (`_constraint_module_type`),
  sanitized aggregator field names, and real (not hardcoded-`None`) defaults for
  constraint-only design attributes.
- `generation/modules.py::render_report_aggregator` — reads field names from
  `module.inputs` (already sanitized) instead of raw `catalog.concrete_entries` constraint
  IDs, keeping the aggregator's Pydantic schema and its YAML wiring keys in lockstep.
- `.project/active/constraint-generation/run-log.md` (NEW) — the N6 run log.

**Deviations from plan:** the environment-availability premise in the orchestration brief was
wrong, corrected here rather than carried forward: `SYSIDE_LICENSE_KEY` **is** available in
this sandbox (`.env` at the repo root) — it simply isn't exported to ambient shell env, so a
bare `uv run pytest` (no explicit env var) sees no license and every `@requires_license` test
skips, which is what Phases 1-3 observed and mis-attributed to "no license in this sandbox."
Passing `SYSIDE_LICENSE_KEY=<key>` explicitly makes the full live suite (2231 tests) pass,
including the execution lane. This changes nothing about the Phases 1-3 work itself (already
verified correct — see `run-log.md`'s regression-check note) but means the "S4-unexercised
cases (partial)" deferral above is a real budget constraint, not an environment limitation —
worth knowing for whoever picks up the remaining execution-lane coverage.

Five execution-lane items (indeterminate point, negated/inline at execution, INV-6 override,
break-the-YAML, exit-narrowing) are **deferred, not implemented** — see the checklist above
for the capture-fidelity §4 surfacing. SC-1 and the two S4-unexercised integration risks
(zero-eligible aggregator, multi-instance compile-once) are proven; the deferred five are
same-shaped extensions of the now-working harness.

**Issues Encountered:** three real, load-bearing bugs — full detail in `run-log.md`. All
three are `analysis/constraint_lowering.py` (Item 5 file) touches beyond D11's already-surfaced
`if eligible:` relaxation, each a narrow one-function fix the execution lane's actual-import,
actual-pydantic-validation, actual-simkit-load behavior caught and generation-level tests
could not (a `SyntaxError` in an executed import and a JSON schema gap that only bites at
simkit load time are both invisible to `ast.parse`-only generation checks).

**Validation:** execution lane (agentic-mbse venv, real simkit, real syside license) — 3/3
pass, see `run-log.md`. Full offline suite with license present (`SYSIDE_LICENSE_KEY=<key>
uv run pytest tests/`) — 2231 passed, 4 skipped, 3 deselected (execution-marked), **zero
failures, zero errors** — the first fully-green run this session; the prior "23 failed / 96
errors" reading in every earlier phase's validation was the license-unavailable artifact
above, not a real baseline (mypy's 76-error and ruff-clean baselines were never
license-dependent and hold unchanged). `ruff check` clean. `mypy src/` — 76 errors, baseline
held.

### Phase 5 Completion
**Completed:** 2026-07-13
**Changes Made:**
- `tests/conformance/test_constraint_catalog_determinism.py` (NEW) — INV-8 (two live loads of
  `constraint_multi_instance` fingerprint identically; two different fixtures fingerprint
  differently, ruling out a trivially-constant fingerprint).

**Deviations from plan:** none.

**Issues Encountered:** none new — Phase 4 already surfaced and fixed the correctness
issues that would otherwise have shown up here as a determinism or byte-identity failure.

**Validation:**
- Byte-identity (INV-7): `test_graph_assembly.py::TestBaselineComparison`,
  `test_pipeline_e2e.py::TestBaselineComparison`, `test_e2e_output_registry.py::TestYamlDiffValidation`
  — 11/11 pass against pre-Item-7 committed baselines.
- Determinism (INV-8): 2/2 pass.
- `SYSIDE_LICENSE_KEY=<key> uv run pytest tests/` — **2233 passed, 4 skipped, 3 deselected
  (execution-marked), zero failures, zero errors.**
- `uv run ruff check src/` — clean.
- `uv run mypy src/` — 76 errors, baseline held exactly (same count and same files as the
  pre-Item-7 baseline recorded at the start of Phase 1).

**What We Know Works After This Phase:** Item 7 is complete — offline generation, the
execution lane, and the full test suite are all green with no baseline regression. Item 8 has
deterministic catalog fingerprints to build snapshot parity on.

---

## Phase 6: Audit cures

### Goal
`audit.md` certified Item 7 with notes, requiring cures before close: SC-2's execution half
(indeterminate point, negated + inline assertions), SC-3 (modeled-default override), the
Break-the-YAML kept test, and CI regression pins for the three Phase-4 bug fixes (Finding 1 —
those fixes were previously caught only by the manual, non-CI execution lane).

### Changes Required
- [x] **SC-2 execution cases** — `tests/execution/test_constraint_execution.py`:
  `test_indeterminate_point_at_execution` (a non-finite operand overridden via the JSON entry
  file reads as `indeterminate`, `actual_value is None`, `margin is None`);
  `test_negated_inline_assertion_at_execution` (negated inline assertion, correct status and
  sign-flipped margin under real execution).
- [x] **SC-3 modeled-default override** — `test_modeled_default_override_flips_verdict`: the
  defaulted formal (`{constraint_id}__threshold`) is a real JSON entry key; not overriding it
  uses the modeled default (satisfied); overriding it flips the verdict (violated).
- [x] **Break-the-YAML** — `test_break_the_yaml_surfaces_execution_failure`: after a clean
  baseline run, the aggregator's YAML input reference to the constraint's evaluation channel
  is rewired to a nonexistent channel (the constraint module's own output declaration is left
  untouched — a pure wiring gap, not a renamed-everywhere no-op); re-executing raises through
  the executor rather than silently producing a wrong or partial report.
- [x] **CI regression pins** — `tests/unit/test_phase4_bugfix_regressions.py` (NEW, offline,
  no simkit/license needed): `test_occurrence_indexed_constraint_modules_have_valid_class_names_and_parse`
  (bug a: bracket-strip in `_constraint_module_type`), `test_occurrence_indexed_aggregator_fields_are_valid_identifiers_and_parse`
  (bug b: `sanitize_name(c.constraint_id)`), `test_constraint_only_design_attribute_gets_real_default_not_none`
  (bug c: `design_attribute_default_value`). Each was verified to go RED by reverting its fix
  in isolation (`git checkout` afterward to restore) — see `run-log.md`'s Phase-6 entry for
  the exact before/after failure text.

All four cures reuse the existing `_generate_full_package`/`_run` execution harness and the
`extend_graph_with_constraints`/`assemble_constraint_catalog` production machinery — no new
design decisions, no changes to `src/` beyond what Phases 1-5 already landed.

### Validation
**Automated:**
- [x] Execution lane (agentic-mbse venv, real simkit): 7/7 pass (3 prior + 4 new). See
  `run-log.md`.
- [x] `SYSIDE_LICENSE_KEY=<key> uv run pytest tests/` → 2236 passed, 4 skipped, 7 deselected
  (execution-marked), zero failures, zero errors.
- [x] `uv run ruff check src/` → clean.
- [x] `uv run mypy src/` → 76 errors, baseline held exactly.
- [x] Byte-identity (INV-7) re-confirmed: `test_graph_assembly.py::TestBaselineComparison`,
  `test_pipeline_e2e.py::TestBaselineComparison`, `test_e2e_output_registry.py::TestYamlDiffValidation`
  — 11/11 pass.

**What We Know Works After This Phase:** every named spec success criterion (SC-1 through
SC-4, Break-the-YAML) has a passing end-to-end test under real simkit; the three Phase-4 bug
fixes each have an offline CI test that would fail on revert. The audit's two findings are
both closed.

### Phase 6 Completion
**Completed:** 2026-07-13
**Changes Made:** see Changes Required above; full detail in `run-log.md`'s "audit cures
(Phase 6)" entry.
**Deviations from plan:** none — the audit's cure list was followed exactly.
**Issues Encountered:** none — every new test passed on first execution against the
already-fixed Phase-4 code; the regression-pin RED/GREEN verification (revert → fail →
restore → pass) was the only extra step, done once per bug to confirm each pin is load-bearing.
**Validation:** see Automated checklist above.

---

**Status:** Draft → In Progress → Complete → **Audit cures complete**

---

## Orchestrator note: teax scalar-persistence state PINNED (2026-07-12)

Phase 4's first checkbox is pre-discharged. Verified live from the orchestrator shell:
teax `main` HEAD = `7560d65` ("Merge pull request #2 … primitive-persistence-unified"), and the
epic branch carries it; `simkit/io/writers.py:52` has `write_json_primitive` with
`PRIMITIVE_TYPES` validation. The design's B4 tension resolves in favor of the memory
[[teax-scalar-persistence-fixed]]: the old "uncommitted at c9e1e85" caveat (concept Appendix A)
is superseded — the work is merged. Decision rule outcome: **persist-and-assert** (SC-1's
"report persisted" clause is in force; no parking needed).
