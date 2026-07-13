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
- **B4.** teax's scalar-persistence work is merged on the epic branch (memory:
  [[teax-scalar-persistence-fixed]]), so file-backed exit writers persist the report. *If
  false → execution acceptance can construct the report but cannot persist it beside ordinary
  outputs.*

## Key Decisions

- **D1 — Exit-ancestry: explicit exit membership (pinned report channel).** The pipeline
  generator computes exits as `selected_exits ∪ pinned_exits`, where `pinned_exits` =
  `{report channel of each REPORT_AGGREGATOR module}` and `selected_exits` is today's
  capture-everything set. Under capture-everything the pin is redundant, but it is the
  load-bearing mechanism the narrowed-exit test toggles. *Rejected: a generation-time
  ancestry assertion — it only detects absence; under a genuine narrowing it fails generation
  rather than delivering the report, which is the opposite of the falsifiable test's
  "report present under the narrowed exit."*
- **D2 — Kleene compiler home: `src/sysml_codegen/generation/predicate_compiler.py`,**
  porting `s2_ir.compile_predicate`/`margin_expression`/the `_KLEENE_RUNTIME` block. Input is
  `ConcreteConstraint.predicate_ir` re-parsed via `agentic_mbse.sysml.expression_ir.parse_expression`
  (Item 2's landed IR, not the spike's `s2_ir`). *Rejected: evaluating in the module at run
  time — S2 showed raw IEEE returns a confident `False` from `1.0/0.0`; only compiled Kleene
  code carries `unknown`.*
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
  `contracts/constraint_catalog.json` both read that one value. *Rejected: threading `ctx`
  into a standalone catalog emitter — it breaks the "generation reads only the graph"
  invariant the codebase rests on.*
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
  constraint-free model never triggers lowering, so byte-identity is unaffected.

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
- **INV-2 (same-IR guard).** Each generated class's compiled predicate serialization-equals
  its catalog concrete-entry `predicate_ir`; a mismatch is a loud `CodeGenerationError` naming
  the `constraint_id`. Catching criterion: mutate one `predicate_ir` after lowering →
  generation fails, naming that id.
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

- **Reproduce the S4 slice** end-to-end under real simkit: both truth values, identical
  ordinary outputs, correct verdicts/margins, report persisted (spec SC-1).
- **Cover the S4 gaps:** zero-assertion aggregator, indeterminate point, negated + inline
  assertions, multi-instance expansion (N modules, N aggregator fields, one shared predicate).
- **Modeled-default override:** default applies when unset; overriding flips the verdict; the
  default is entry-point-sourced, not baked (INV-6).
- **Falsifiable exit test (D1):** control leg (pin disabled + exit narrowed) drops the report;
  mechanism leg (pin on, same narrowing) keeps it.
- **Break-the-YAML:** rewire an upstream evaluation → missing result surfaces as an execution
  failure *through the executor* (INV-4 end-to-end).
- **Same-IR guard:** mutate one `predicate_ir` → generation fails naming the id (INV-2).
- **Byte-identity:** constraint-free corpus regenerates byte-identically (INV-7).
- **Determinism:** two live loads of a constraint-bearing fixture produce identical catalog
  fingerprints (INV-8, the Item 8 handoff gate — not an Item 7 live/snapshot parity gate).

## Next-Stage Handoff

- **Fixed:** the [OWNER]/[HARD] items — class-per-assertion identity, compile-once bridge,
  same-IR guard, modeled-default-as-EP, Kleene semantics, evidence vocabulary conformance —
  and decisions D1–D11 above.
- **Open for the plan:** exact template text; the `_get_python_path` derivation; the precise
  reconciliation of predicate args vs module inputs in `run()`; test-lane marker/env wiring.
- **De-risk first:** D3's shared-predicates-module import path under a *two-instance-of-one-
  definition* fixture (the case S4 never ran) — it is the one place the compile-once emission
  and the class-per-assertion identity meet, and the most likely to surprise.

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
