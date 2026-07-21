# Design: Constraint Module, Kleene Compiler, Aggregator, and Catalog Generation

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-07-12
**Branch:** constraint-exec-epic
**Commit:** ef55bb7
**Epic:** CONSTRAINT-EXEC, Item 7

## Overview

Fill the five generation seams Item 6 left failing loud so a modeled assertion emits
real, runnable Python: a Kleene predicate function, a class-per-assertion constraint
module, an exact-schema report aggregator, per-package evidence schemas, and an embedded
catalog — productionizing the proven S4 shapes.

## Related Artifacts

- **Spec:** `.project/active/constraint-generation/spec.md`
- **Epic:** `.project/backlog/epic_constraint_execution.md` (Item 7)
- **Required Reading:** concept `constraint-execution-and-design-space-studies-claude.md`
  ("Catalog, Evaluation, and Report", Required Invariants, Appendix B); S2 findings
  (`spike-expression-tree-parity/findings.md`); S4 findings + emitters
  (`spike-vertical-slice-constraint-execution/`)
- **Owner-gate evidence:** `identity-gate-evidence.md`, `bench_aggregator_scale.py`

## Research Findings

**The generation pipeline is graph-driven and step-orchestrated.** `run_codegen`
(`cli/__init__.py:851-877`) runs `_generate_schemas` → `_modules` → `_stencils` →
`_pipeline` → `_registry` → `_entry_points` → `_backlog` → `_tests`, each handed the
`PipelineContext` (`ctx`) which carries `computation_graph`, `concrete_constraints`, and
`constraint_facts`. Per-module seams receive a `PipelineModule` or the `ComputationGraph`,
not `ctx` — so anything a seam reads must live on the graph.

**Item 5 already builds the constraint graph nodes.** `extend_graph_with_constraints`
(`analysis/constraint_lowering.py:656`) appends one `CONSTRAINT` `PipelineModule` per
eligible `ConcreteConstraint` (output on `c.evaluation_channel`) and one
`REPORT_AGGREGATOR` module — but **only `if eligible:`** (line 761). `module_type` is a
deterministic placeholder Item 7 owns (`_constraint_module_type`, line 609). Modeled-default
formals are already minted as `LIBRARY_DEFAULT` entry points keyed `{constraint_id}__{formal}`
and sourced as ordinary `entry_point` `ModuleInput`s (lines 731-739). `ConcreteConstraint`
carries `predicate_ir` as a serialized string (`resolution/models.py:318`); nothing consumes
it yet — it is parked for Item 7.

**The five fail-loud seams** all route through `unrenderable_module_kind_error`
(`generation/errors.py:12`). See Appendix A for the exact per-seam map. Two behave as
`else`-fallthrough (module-wrapper, stencil); three are explicit membership guards
(pipeline-yaml, registry, test-gen). `_get_python_path`/`_check_duplicate_output_paths`
(the S4 "fourth calc-shaped seam") assume `calc_def_qualified_name` and need constraint
awareness too.

**Exits are capture-everything today.** `_build_exit_points` (`generation/pipeline.py:228`)
emits one exit per surviving module output with no membership filter — the report channel
reaches the exit only incidentally (confirmed in the S4 `pipeline.yaml`, exit_point captures
`constraint_report`). No narrowing mechanism exists in production.

**S4 executed the whole surface under real simkit with zero runtime changes.** The generated
constraint module (`out/package_live/modules/toy_plant/demo_plant_affordable.py`), aggregator,
`schemas/constraint_types.py`, and registry `CUSTOM_SCHEMA_TYPES` are the concrete productionization
base. `s2_ir.compile_predicate` (`spike-expression-tree-parity/s2_ir.py:276`) is the semantic
oracle for the Kleene compiler.

## Core Concept

A modeled assertion becomes an ordinary graph module whose *verdict is data*, never an
exception. Item 5 has already lowered each assertion to a `ConcreteConstraint` and placed
`CONSTRAINT`/`REPORT_AGGREGATOR` nodes in the graph. Item 7 supplies the missing emission:
it teaches each of the five seams (plus the module-path helper) to render those two kinds
instead of refusing them.

The one genuinely new piece of machinery is the **Kleene predicate compiler** — a
codegen-owned function that turns a definition's serialized `predicate_ir` into readable
Python implementing three-valued logic (a non-finite operand makes its own leaf comparison
`unknown`; `unknown` propagates only where a connective needs it). It compiles **once per
definition** with formal-named arguments; the N class-per-assertion modules each embed their
own `constraint_id`, wire their resolved actuals into the shared function, and package the
result as a `ConstraintEvaluation` on one structured channel. The aggregator collects those
evaluations against a generated exact schema — one required field per assertion — and emits
a `ConstraintReport` whose channel is a *guaranteed* exit member.

Everything the seams read is on the graph: Item 7 assembles a `ConstraintCatalog` from the
concrete records plus the source facts and embeds it as a graph field, so "generation reads
only the graph" holds. This composes with existing pieces rather than paralleling them: it
reuses the entry-point deriver (modeled defaults, already minted), the pipeline-yaml and
registry templates (same block shape), the `MultiOutput` single-field channel idiom, and
`_resolve_class_name_collisions`.

## Key Bets

- **B1.** The real simkit runtime accepts a per-package-generated `ConstraintEvaluation`/
  `ConstraintReport` via registry introspection + `CUSTOM_SCHEMA_TYPES`, with no teax change
  (S4 proved this on `c9e1e85`+working-tree). *If false → structured channels are rejected and
  the whole emission approach is wrong, not just retuned.*
- **B2.** The profile gate (Item 3) strictly precedes compilation, so the compiler can
  strip-render units and never re-check safety. *If false → a unit-mismatched comparison
  compiles to a bare-float comparison and returns a confident, wrong verdict — the exact
  failure the Kleene work exists to prevent.*
- **B3.** Item 5's serialized `predicate_ir` round-trips stably through
  `parse_expression` → `serialize_expression`. *If false → the same-IR generation guard
  cannot distinguish a real mutation from serializer noise, and either false-fails or lets a
  class/catalog divergence through.*
- **B4.** teax now carries the scalar-persistence work at its HEAD (memory
  [[teax-scalar-persistence-fixed]]: the `RootModel[float]` exit writers no longer reproduce
  as missing), so file-backed exit writers persist the report. *If false → execution
  acceptance can construct the report but cannot persist it beside ordinary outputs.* Note the
  source tension: S4's findings describe these as **uncommitted** teax working-tree changes
  absent from HEAD `c9e1e85`; the memory says they are fixed at teax HEAD and the S4-era
  finding is stale. B4 rides on the memory being current — the plan pins which teax state the
  execution lane runs against before relying on it (N5).
- **B5.** The compiled predicate's leaf names (`_leaf_ref_names(predicate_ir)`) are a subset of
  the module's `ModuleInput.param_name`s, so `run()` can wire resolved actuals into the
  predicate **by name**. Item 5 sets input names from `actual.name` /
  `sanitize_name(formal local)` (`constraint_lowering.py:548-566, 738`); the predicate's leaf
  names come from the same IR, so they *should* coincide — but nothing proves it, and it is the
  single most likely integration break. *If false → `run()` raises a `TypeError`/missing-kwarg
  at execution (or silently drops a formal), and no module runs.* Asserted at generation: the
  module-wrapper emitter checks `leaf_names ⊆ input param_names` and errors naming the
  `constraint_id` on any predicate leaf without a matching input.

## Key Decisions

- **D1 — Exit-ancestry: explicit exit membership (pinned report channel), with a test-only
  narrowing seam.** `_build_exit_points` (`generation/pipeline.py:228`) is unconditional
  capture-everything: it appends every output of every module, with no `selected`/`targets`
  filter anywhere in `src/`. There is no production surface that can drop the report channel,
  so the falsifiable control leg cannot be built against the code as-is. Fix: give
  `_build_exit_points` two keyword parameters whose **production defaults reproduce today's
  output byte-for-byte** —

  ```python
  def _build_exit_points(modules, alias_filenames, *,
                         selected_channels=None,       # None ⇒ capture-everything (default)
                         pin_report_channels=True):    # REPORT_AGGREGATOR outputs always kept
      pinned = {m.outputs[0].channel_name for m in modules
                if m.module_kind is ModuleKind.REPORT_AGGREGATOR}
      # include channel ch iff:
      #   (selected_channels is None or ch in selected_channels)
      #   or (pin_report_channels and ch in pinned)
  ```

  With `selected_channels=None` every channel passes the first clause, so the pin is a no-op
  and the emitted YAML is identical to today (INV-7). The pin only does work when a *narrowed*
  `selected_channels` is supplied. `generate_pipeline_yaml` forwards an optional test-seam so a
  kept test can drive the full render narrowed; production callers pass nothing. The two legs
  (Validation Approach) inject a narrowed set that excludes the report: control = narrowed +
  `pin_report_channels=False` → report **absent**; mechanism = same narrowed set +
  `pin_report_channels=True` → report **present**. *Rejected: a generation-time ancestry
  assertion — it only detects absence; under a genuine narrowing it fails generation rather
  than delivering the report, the opposite of "report present under the narrowed exit."*
  There is **no** production exit-narrowing feature — the pin guarantees membership
  structurally; narrowing exists only in the test (restated in Non-Goals).
- **D2 — Kleene compiler home: `src/sysml_codegen/generation/predicate_compiler.py`.** It
  re-authors S2's `compile_predicate`/`margin_expression`/`_KLEENE_RUNTIME` semantics **against
  Item 2's `expression_ir` node algebra** — this is a rewrite, not a copy: the landed
  `expression_ir` has different node kinds/fields than the spike's pydantic `IRNode`, so the
  tree-walk is rebuilt while the emitted Python (leaf `_cmp`, `_and/_or/_not`, margin) matches
  S2's proven output. Input is `ConcreteConstraint.predicate_ir` re-parsed via
  `agentic_mbse.sysml.expression_ir.parse_expression`. *Rejected: evaluating in the module at
  run time — S2 showed raw IEEE returns a confident `False` from `1.0/0.0`; only compiled
  Kleene code carries `unknown`.*
- **D3 — Compile-once emitted once: a shared per-package predicates module.** The compiled
  function + one Kleene-runtime block are emitted a single time per definition into
  `modules/constraints/predicates.py`; each class-per-assertion module imports its function.
  *Rejected: inline-per-class emission (S4's shape) — with N instances of one definition it
  duplicates the compiled predicate, violating the [HARD] "the classes multiply, the compiled
  predicate does not."*
- **D4 — Evidence types: per-package generated `schemas/constraint_types.py`,** registered in
  `CUSTOM_SCHEMA_TYPES`. *Rejected: importing shared types from simkit — Item 10 owns the
  evidence *vocabulary*, not the pydantic models; a self-contained sealed package (Item 9)
  cannot depend on runtime-side model definitions.*
- **D5 — `ConstraintEvaluation` field schema: the S4 split is production.** `actual_value:
  Optional[bool]` (three-valued predicate result, `None` = indeterminate) plus `observed:
  dict[str, float]` (the operands that explain the case). *Rejected: a single numeric
  "actual value" — it loses the "violated without the values that violated it is not
  evidence" requirement.* Full schemas in Appendix B.
- **D6 — Catalog: a `ConstraintCatalog` pydantic model embedded on `ComputationGraph`.**
  Item 7 assembles it from `ctx.concrete_constraints` (concrete entries) + `ctx.constraint_facts`
  (source records), computes the fingerprint once (sha256 of canonical JSON), and sets it on
  the graph before generation; the aggregator's `CATALOG_FINGERPRINT` and the
  `contracts/constraint_catalog.json` both read that one value. Each concrete entry carries its
  `predicate_ir` (so INV-2's arm (b) can run). Response metadata (the margin's sign) is
  **derived at generation** from predicate structure — the simple-inequality shape that fixes a
  sign — and is **optional**: absent for a compound predicate that reports status only. It is
  never carried from upstream and never a required field. *Rejected: threading `ctx` into a
  standalone catalog emitter — it breaks the "generation reads only the graph" invariant the
  codebase rests on.*
- **D7 — Templates: new for the constraint-specific bodies, reuse for the structural ones.**
  New: `constraint_module.py.jinja2`, `report_aggregator.py.jinja2`,
  `constraint_predicates.py.jinja2`, `constraint_types.py.jinja2`. Reuse (extended context
  only): `pipeline_yaml.jinja2`, `registry_function.py.jinja2`. *Rejected: branching the calc
  `teax_module.py.jinja2` — a constraint body (compiled predicate, evidence construction) shares
  almost nothing with a calc wrapper; branching would obscure both.*
- **D8 — Seam behavior: three render, three skip.** Module-wrapper, pipeline-yaml, and
  registry render constraint/aggregator kinds. Test-gen, stencil, and backlog-report **skip**
  them (like FORMULA/AGGREGATION already skip) — constraint modules are fully generated, so
  there is no handwritten implementation to stencil, unit-test, or backlog. *Rejected:
  emitting stencils/tests — they would "test" generated code against nothing.*
- **D9 — Naming: adopt Item 5's placeholder scheme as production.** Class/module type
  `{namespace}.{Pascal(instance_local + source_local)}ConstraintModule`, file stem lowercased,
  collisions resolved by `_resolve_class_name_collisions`. `name`, `evaluation_channel`, and
  the aggregator names stay as Item 5 sets them. *Rejected: deriving class names from
  `constraint_id` — it now carries a 16-char sha suffix (Item 5 `mint_constraint_id`),
  producing unreadable class names.*
- **D10 — Execution tests: in-process `execute_pipeline`, a marked test lane.** The harness
  generates a package to a tmp dir, inserts it + `teax/packages/teax-simkit` on `sys.path`,
  and calls `execute_pipeline(..., custom_schema_types=CUSTOM_SCHEMA_TYPES)` directly, asserting
  channel values and persisted artifacts. *Rejected: subprocess — env plumbing is fragile and
  it forfeits direct assertion access; S4's `probe_c` proved the in-process form.* Env per
  memory [[teax-simkit-execution-env]]: runs in the agentic-mbse venv, not the codegen venv.
- **D11 — Zero-assertion aggregator: relax Item 5's `if eligible:` gate.** The aggregator must
  emit whenever the constraint pathway is active (lowering ran), even with zero eligible
  constraints, so a model that asserts nothing still produces the `not_assessed` report
  surface. This is a one-condition change at `constraint_lowering.py:761`. **Surfaced** as an
  Item 5 touch-point (see Potential Risks) rather than resolved silently — a truly
  constraint-free model never triggers lowering, so byte-identity is unaffected. The
  aggregator's `agg_inputs` stays sourced from `eligible` (not `concrete`): a zero-eligible
  model yields an empty-input aggregator (headline `not_assessed`), never a validation failure
  on a non-eligible record's `evaluation_channel=None`.

## Architecture

Three data flows, all converging on the graph:

1. **Predicate flow.** `ConcreteConstraint.predicate_ir` (string) → `parse_expression` →
   compiler → `(function_source, arg_names)`. The compiler runs once per distinct definition
   (keyed by `definition_qn`); the source is emitted once into the shared predicates module.
2. **Module flow.** Each eligible `ConcreteConstraint`'s `PipelineModule` (already in the
   graph) → module-wrapper seam → a class importing its predicate, embedding `constraint_id`,
   validating inputs in `run()`, and emitting a `ConstraintEvaluation`. The `REPORT_AGGREGATOR`
   module → aggregator seam → exact-schema collector emitting a `ConstraintReport`.
3. **Catalog flow.** `concrete_constraints` + `constraint_facts` → `ConstraintCatalog` on the
   graph → the fingerprint into the aggregator constant + the catalog contract file.

Integration points (by seam) are the six functions in Appendix A. Generation order is
unchanged; the shared predicates module and `constraint_types.py` are written during
`_generate_modules` and `_generate_schemas` respectively, gated on the presence of a
`ConstraintCatalog` on the graph.

## Required Invariants

- **INV-1.** One compiled predicate function per definition; N classes per assertion; classes
  import the shared function (never inline-duplicate it).
- **INV-2 (same-IR generation guard).** Under D3 there is one compiled function per
  `definition_qn`, so the guard is a *data-level* check on the catalog concrete entries, not a
  per-class re-compile-and-compare. Two arms, both before the single compile: (a) round-trip
  stability per entry — `serialize(parse(entry.predicate_ir)) == entry.predicate_ir` (B3); and
  (b) byte-agreement — all concrete entries sharing a `definition_qn` carry the identical
  `predicate_ir` string. A violation of either is a loud `CodeGenerationError` naming the
  `constraint_id`. Catching criterion: mutate one entry's `predicate_ir` after lowering →
  arm (b) fails, naming that id. This is Item 7's *generation-time* arm; it does not
  re-implement or contradict Item 5's *lowering-time* same-IR guard
  (`constraint_lowering.py:524-536`), which already checks the profile-walked predicate against
  the lowered one — a different arm at a different stage. **Note:** the catalog's concrete
  entries must carry `predicate_ir` for arm (b) to run; S4 put it only on the source records
  (`s4_lib.py:883-898`), so Item 7's `ConstraintCatalog` (D6) adds it to each concrete entry.
- **INV-3.** A constraint module never raises on an adverse verdict. Only missing inputs,
  schema-validation failure, thrown predicate code, or a missing aggregator field are
  execution failures.
- **INV-4.** The aggregator input schema has one *required* field per eligible constraint with
  `extra="forbid"`; it exists even for zero eligible (headline `not_assessed`).
- **INV-5.** The report channel is a pinned exit member, present independent of capture-everything.
- **INV-6.** A modeled-default formal is an entry-point-sourced input field carrying the
  default; the default is never baked into the compiled predicate as a constant.
- **INV-7.** A constraint-free corpus (no constraint facts) generates byte-identically: no
  `constraint_types.py`, no predicates module, no catalog fields in any artifact.
- **INV-8.** Deterministic `constraint_id`s (Item 5) + catalog ordering by `constraint_id` →
  a stable catalog fingerprint across repeated live loads (the Item 8 handoff gate).
- **INV-9.** Producer/consumer channel types match exactly; every constraint and report schema
  is registered in `CUSTOM_SCHEMA_TYPES`.

## Component Overview

- **`generation/predicate_compiler.py`** (new) — Kleene compiler: `compile_predicate(ir,
  fn_name, negated)` → `(source, args)`, plus `margin_expression` and the runtime block.
  Consumes Item 2's `expression_ir`.
- **`generation/constraint_catalog.py`** (new) — assembles `ConstraintCatalog`, computes the
  fingerprint; `ConstraintCatalog` model added to `resolution/models.py` and an optional field
  on `ComputationGraph`.
- **`generation/modules.py`** — module-wrapper seam renders `CONSTRAINT` (import shared
  predicate, embed id, evidence) and `REPORT_AGGREGATOR` (exact schema, headline precedence).
- **`generation/pipeline.py`** — renders the constraint/aggregator YAML block (same shape as
  calc) + the exit pin (D1).
- **`generation/registry.py`** — a fourth partition (constraint + aggregator, class name from
  `module_type`), plus `constraint_types` imports into `CUSTOM_SCHEMA_TYPES`.
- **`generation/test_gen.py`, `stencils.py`** — skip constraint kinds (D8).
- **`cli/__init__.py` `_get_python_path`** — derive a deterministic path for constraint/
  aggregator modules from `module_type`/`name` (not `calc_def_qualified_name`).
- **Templates** — four new, two extended (D7).
- **`tests/execution/`** (new lane) — the real-simkit acceptance harness (D10).

## Non-Goals

Per spec: contracts/sealing (Item 9); making facts load-bearing in the snapshot and flipping
`lower_constraints_enabled` (Item 8); calc-side IR rendering (Item 13); drop-manifest/IFE
(Item 14); new expression capability (Item 3 owns the profile); owning the evidence vocabulary
(Item 10). This design also does not add a production exit-*narrowing* feature — the pin (D1)
guarantees membership; narrowing is exercised only by the kept test's seam.

## Implementation Notes

- **Predicate args vs module inputs must reconcile.** The compiler's arg list =
  `_leaf_ref_names(ir)` (formals referenced in the predicate). The module's `ModuleInput`s
  (Item 5) = every formal, bound or modeled-default. `run()` validates all inputs, then calls
  the predicate with its own arg subset. A modeled-default formal that the predicate references
  appears in both — the natural, INV-6-satisfying path. Flag any formal present as an input but
  absent from predicate args (dead formal) at generation.
- **Same-IR guard shape (INV-2).** For each concrete entry, assert `serialize(parse(
  entry.predicate_ir)) == entry.predicate_ir` (round-trip stability, B3) and that all entries
  sharing a `definition_qn` agree byte-for-byte before compiling once.
- **Boundary margin.** Normalize `-0.0` → `0.0` so an exact boundary reads as zero, not a
  signed near-miss ([HARD]; S2 carry-forward 3).
- **`ConstraintCatalog` field is `Optional`, defaults `None`.** When `None` (constraint-free),
  no constraint artifact is written and no field serializes — preserving INV-7.

## Potential Risks

- **D11 touches Item 5 code.** Relaxing the `if eligible:` gate is small but is an Item 5
  file. Mitigation: a focused change guarded by a zero-assertion fixture; the constraint-free
  path (no lowering) is untouched, so byte-identity holds. Surfaced here per capture-fidelity
  §4 rather than resolved silently.
- **Execution lane needs a non-default environment.** The acceptance tests cannot run under the
  plain codegen venv (no simkit; teax `.venv` broken — memory [[teax-simkit-execution-env]]).
  Mitigation: a pytest marker gates them out of the default suite; document the agentic-mbse-venv
  + `sys.path` incantation. "Suite green" (byte-identity, offline) stays in the default lane.
  Because the execution lane runs by hand and outside CI, a regression there is silently missed
  unless recorded: the plan writes each manual run's result (date, teax state, pass/fail per
  criterion) durably — an appended log in this feature directory — so an unrun or failing lane
  is visible, not assumed green (N6).
- **`_get_python_path` runs before the module-wrapper guard.** If it assumes
  `calc_def_qualified_name` it crashes before the seam. Verify it already tolerates constraint
  kinds (Item 6's faildloud test reaches the guard, so likely yes) and add explicit derivation
  if not.

## Integration Strategy

Item 7 fills seams inside the existing step orchestration — no new top-level flow. The five
faildloud unit tests (`tests/conformance/test_module_kind_faildloud.py`) invert from
"asserts refuse" to positive tests: three assert real rendering, three assert clean skip.
Item 5's graph nodes and entry points are consumed as-is; the only Item 5 change is D11.

## Validation Approach

Two lanes. The **offline lane** (default `uv run pytest`, no simkit) is CI-enforceable and
carries the safety-critical compiler tests and every generation-time check. The **execution
lane** (D10, agentic-mbse venv + teax-simkit on `sys.path`) runs the real-simkit end-to-end
criteria and is not in default CI (see N6 note).

Offline lane:

- **Compiler-level Kleene unit tests (M2), committed, probe3-style — the safety-critical
  core.** Assert directly on `compile_predicate`'s emitted-function output (load and call it),
  one case per rendered semantic, because end-to-end tests exercise happy paths and will not
  catch a wrong propagation cell — a wrong cell reads as a *confident wrong verdict*, the exact
  failure the feature exists to prevent. Cells: non-finite leaf → `unknown` /
  `indeterminate` / `margin=None`; `true or unknown → true`; `false and unknown → false`;
  `not unknown → unknown`; negated-polarity status (a `false` predicate under a negated
  assertion is `satisfied`); negated-inequality margin **sign flip**; and the **`-0.0 → 0.0`
  boundary normalization** — new code S2 never tested (S2 only *masked* signed zero with
  `math.isclose`; it performs no normalization), so this cell is written with zero prior test
  behind it and must be covered explicitly.
- **Same-IR guard:** mutate one concrete entry's `predicate_ir` → generation fails naming the
  id (INV-2, arm (b)); a serializer-noise round-trip failure trips arm (a).
- **Leaf-name reconciliation (B5):** a fixture whose predicate leaf lacks a matching
  `ModuleInput` → generation errors naming the `constraint_id`.
- **Byte-identity:** constraint-free corpus regenerates byte-identically (INV-7); the D1 exit
  parameters at their production defaults change no bytes.
- **Falsifiable exit test (D1), at the exit-builder layer:** drive `_build_exit_points` with a
  narrowed `selected_channels` that excludes the report channel. Control leg
  (`pin_report_channels=False`) → the emitted exit list **omits** the report; mechanism leg
  (`pin_report_channels=True`, same narrowed set) → it **includes** it. This is the load-bearing
  proof the pin is not riding capture-everything; it needs no simkit.
- **Determinism:** two live loads of a constraint-bearing fixture produce identical catalog
  fingerprints (INV-8, the Item 8 handoff gate — not an Item 7 live/snapshot parity gate).

Execution lane (real simkit):

- **Reproduce the S4 slice** end-to-end: both truth values, identical ordinary outputs,
  correct verdicts/margins, report persisted (spec SC-1).
- **Cover the S4 gaps:** zero-assertion aggregator, indeterminate point, negated + inline
  assertions, multi-instance expansion (N modules, N aggregator fields, one shared predicate).
- **Modeled-default override:** default applies when unset; overriding flips the verdict; the
  default is entry-point-sourced, not baked (INV-6).
- **Break-the-YAML:** rewire an upstream evaluation → missing result surfaces as an execution
  failure *through the executor* (INV-4 end-to-end).
- **End-to-end exit narrowing (optional companion to the exit-builder test):** render a full
  narrowed `pipeline.yaml` via the `generate_pipeline_yaml` test-seam and execute it; the
  control leg writes no `constraint_report.json`, the mechanism leg writes it.

## Next-Stage Handoff

- **Fixed:** the [OWNER]/[HARD] items — class-per-assertion identity, compile-once bridge,
  same-IR guard, modeled-default-as-EP, Kleene semantics, evidence vocabulary conformance —
  and decisions D1–D11 above.
- **Open for the plan:** exact template text; the `_get_python_path` derivation; the precise
  reconciliation of predicate args vs module inputs in `run()`; test-lane marker/env wiring.
- **De-risk first:** two things S4 never ran. (1) D3's shared-predicates-module import path
  under a *two-instance-of-one-definition* fixture — the one place compile-once emission and
  class-per-assertion identity meet. (2) The leaf-name / input-name reconciliation (B5) — the
  single most likely integration break; a fixture where the predicate leaf and the module input
  are known to coincide, plus the negative fixture that proves the generation-time check fires.

---

## Appendix A — The five seams (+ module-path helper)

| Seam | Entry / guard | Today | Item 7 |
|---|---|---|---|
| module-wrapper | `modules.py:86` / else `:50` | calc/formula/agg | **render** constraint + aggregator |
| pipeline-yaml | `pipeline.py:25` / `:130` | calc/formula/agg | **render** block + exit pin |
| registry | `registry.py:185` / `:224` | 3-way partition `:228` | **render** 4th partition + schema imports |
| test-gen | `test_gen.py:22` / `:52` | calc only | **skip** (like formula/agg) |
| stencil | `stencils.py:156` / else `:52` | calc/formula/agg | **skip**; backlog-report `:225` also skip |
| module-path | `_get_python_path` (cli) | `calc_def_qualified_name` | derive from `module_type`/`name` |

Shared error helper: `generation/errors.py:12` `unrenderable_module_kind_error`. `ModuleKind`
enum: `resolution/models.py:161` (CALCULATION, FORMULA, AGGREGATION, CONSTRAINT,
REPORT_AGGREGATOR). Templates live in `src/sysml_codegen/templates/`.

## Appendix B — Evidence schemas (pinned, D5)

```python
class ConstraintEvaluation(BaseModel):
    constraint_id: str
    actual_value: Optional[bool] = None          # three-valued; None = indeterminate
    status: Literal["satisfied", "violated", "indeterminate"]
    margin: Optional[float] = None               # signed; simple-inequality only; -0.0→0.0
    observed: dict[str, float]                    # operands that explain the verdict

class ConstraintReport(BaseModel):
    catalog_fingerprint: str
    assessed_count: int
    headline: Literal["violation", "indeterminate", "all_satisfied", "not_assessed"]
    results: list[ConstraintEvaluation]
```

Headline precedence: any `violated` → `violation`; else any `indeterminate` →
`indeterminate`; else any results → `all_satisfied`; else → `not_assessed`. Aggregator input
schema: one required `ConstraintEvaluation` field per eligible `constraint_id`,
`extra="forbid"`.

---
Next Step: After approval → `/_my_plan`.
