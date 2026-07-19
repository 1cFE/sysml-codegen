# Design: Generated Constraint Name-Safety Boundary

**Status:** Certified (license-free scope) — external execution evidence unavailable
**Owner:** Reid W
**Created:** 2026-07-18 20:13 PDT
**Branch:** `constraint-exec-epic`
**Commit:** `512786c`
**Epic:** CONSTRAINT-WAVE-REMEDIATION — Item 2 (R-3)

---

## Overview

Generated constraint formals are accepted only when their final Python bindings are injective,
do not overlap codegen-owned bindings, and describe the same source identity in the predicate and
wrapper scopes. One structured mechanism performs those checks at package preflight and at direct
compiler/render boundaries, while preserving every collision-free emitted byte.

## Related Artifacts

- Revised spec: `.project/active/constraint-wave-name-safety/spec.md`
- Historical spec review: `.project/active/constraint-wave-name-safety/spec-review.md`
- Epic Item 2: `.project/backlog/epic_constraint_pr_wave_remediation.md:188`
- Primary R-3 review:
  `.project/research/20260718-192048_constraint-exec-pr-wave-code-review.md:67`
- GAP-CLOSE predicate collision precedent:
  `.project/active/gap-runtime-contract/{spec,design}.md`
- Naming reference: `docs/architecture/reference/15-naming-conventions.md`
- Current implementation:
  `src/sysml_codegen/generation/{predicate_compiler,modules}.py`,
  `src/sysml_codegen/templates/constraint_{module,predicates}.py.jinja2`,
  `src/sysml_codegen/analysis/constraint_lowering.py`,
  `src/sysml_codegen/resolution/models.py`,
  `src/sysml_codegen/orchestration/pipeline_builder.py`, and
  `src/sysml_codegen/cli/__init__.py`

## Research Findings

- The predicate compiler collects `FeatureReferenceFact.source_name` directly and deduplicates by
  that string before rendering parameters. It checks identifier legality but not collisions with
  its generated locals `value` and `status`
  (`src/sysml_codegen/generation/predicate_compiler.py:202`, `:240`, `:262`). The same leaf fact
  already carries an optional resolved target identity, so direct compilation can distinguish two
  resolved formals before string deduplication
  (`../agentic-mbse/src/agentic_mbse/sysml/expression_facts.py:66`).
- Definition formals still have both raw name and qualified identity during lowering. Lowering
  currently sanitizes the name and discards that identity before constructing
  `ConcreteConstraintInput` (`src/sysml_codegen/analysis/constraint_lowering.py:702`, `:980`). The
  graph then copies only `formal_name` into `ModuleInput.param_name`
  (`src/sysml_codegen/analysis/constraint_lowering.py:1209`, `:1237`). This is the one provenance
  loss that must be repaired.
- The wrapper binds generated parameter `self`, model-derived `ModuleInput.param_name` values, and
  local `verdict` (`src/sysml_codegen/templates/constraint_module.py.jinja2:32`). Rendering only
  checks that each predicate argument appears somewhere in the wrapper inputs. It neither rejects
  duplicate inputs nor proves identity correspondence (`src/sysml_codegen/generation/modules.py:188`).
- GAP-CLOSE F2 established the right orchestration shape: a pure validator runs after both live and
  snapshot routes have built one graph but before overwrite clearing; the lower generation seam
  rechecks direct callers (`src/sysml_codegen/cli/__init__.py:968`,
  `src/sysml_codegen/generation/modules.py:131`). In `run_codegen`, overwrite clearing begins at
  `src/sysml_codegen/cli/__init__.py:990`; the first direct `_generate_modules` mutation is its
  constraint namespace `mkdir` at `:357`, before wrapper rendering at `:379`. Both boundaries need
  full preflight.
- `PipelineModule` is the generation-side source of truth. `PipelineContext` already transports the
  extended graph without rewriting module inputs, so orchestration needs no parallel identity map
  (`src/sysml_codegen/orchestration/pipeline_builder.py:996`, `:1016`).
- Constraint catalog entries carry predicate IR but not resolved inputs
  (`src/sysml_codegen/resolution/models.py:443`). A package check can join a catalog entry to its
  existing constraint module by `constraint_id.lower()`, the same join rendering already uses
  (`src/sysml_codegen/generation/modules.py:198`). It can therefore inspect predicate leaves and
  wrapper input metadata together without expanding the catalog schema or fingerprint.
- Existing offline tests already render the whole constraint surface and parse every emitted
  Python artifact with `ast.parse`
  (`tests/conformance/test_constraint_generation_integration.py:141`). Existing CLI tests also have
  a complete path-kind/byte/symlink manifest for preflight rejection
  (`tests/unit/test_cli_generation.py:145`). These are the right homes to extend.
- ADR-003 documents general sanitization and output-path collision policy. This item does not need
  to change either (`docs/architecture/reference/15-naming-conventions.md:5`, `:14`).
- Snapshot v3 already serializes the complete `ConstraintFacts` aggregate through its own codec
  (`src/sysml_codegen/snapshot/serializer.py:98`, `:103`). That payload includes `FormalFact.name` /
  `qualified_name`, `ActualFact.formal_targets`, omitted-formal QNs, and each predicate leaf's
  `source_name` and target identity
  (`../agentic-mbse/src/agentic_mbse/sysml/{constraint_facts.py:103,expression_facts.py:66}`). The
  loader restores those typed facts (`src/sysml_codegen/snapshot/loader.py:154`, `:217`), and
  snapshot graph rebuild calls the same `lower_constraints()` and graph extension used live
  (`src/sysml_codegen/snapshot/graph_rebuild.py:211`, `:225`). No new snapshot metadata is needed.
- Constraint-aware graph renderers exist below the CLI: pipeline YAML
  (`src/sysml_codegen/generation/pipeline.py:26`), registry source
  (`src/sysml_codegen/generation/registry.py:185`), and the pure model-contract projection
  (`src/sysml_codegen/contracts/model_contract.py:27`). Direct filesystem writers also exist for
  schemas, modules, pipeline, registry, entry points, and sealing
  (`src/sysml_codegen/cli/__init__.py:290`, `:333`, `:488`, `:511`, `:538`, `:610`). Each can be
  called independently in tests and must defend its own first write.

## Core Concept

Treat each model-derived function parameter as a binding fact with two independent properties:
its source identity and its final Python name. Predicate leaves and wrapper inputs derive their
names through their existing paths, then enter the same validator under different scope policies.
The predicate policy owns `value` and `status`; the wrapper policy owns `self` and `verdict`.
Package validation joins the two inventories by source identity and requires a one-to-one,
same-name correspondence. It rejects the first deterministically ordered violation before output
mutation. Every constraint-aware renderer rechecks before returning source, and every direct package
writer preflights before its first filesystem operation. Accepted inputs continue through the
existing render path unchanged.

The key is that the shared mechanism is a collision vocabulary and validation algorithm, not a
shared sanitizer. The two name derivations remain explicit because they are genuinely different.

## Key Bets

- **B1. Resolved source identity is available before constraint inputs are created.** Definition
  formals carry qualified identities, and inline predicate leaves carry their resolved target when
  extraction has one. *If false → package validation would have to reconcile some distinct
  formals by emitted name alone, violating the spec's identity requirement.*
- **B2. Python's symbol-table analysis reports every binding in the exact generated function scope
  under the supported project interpreter.** *If false → the completeness guard could miss a
  generated binding even though the source compiles.* This bet is checked with mutation tests over
  every current Python binding form; unsupported nested scopes fail loudly.

## Key Decisions

- **D1. Reject collisions; do not rename.** Rejection preserves accepted names, wiring, signatures,
  and bytes while stopping silent evidence corruption. *Rejected: stable or collision-only suffixes
  (add a second public mapping and churn generated interfaces); sanitizer changes (general ADR work
  outside this item).*
- **D2. Add one narrow name-safety module with two scope policies.**
  `generation/constraint_name_safety.py` owns immutable binding/violation records, the fixed scope
  order, deterministic formatting, predicate-leaf inventory, wrapper-input inventory, and pure
  validators. Predicate and wrapper callers supply their existing final names; this module never
  sanitizes them. *Rejected: duplicate deny lists in compiler, renderer, and CLI (drift); one union
  deny list with one derivation (misstates the two scopes and cannot check correspondence).*
- **D3. Preserve only raw name and qualified identity on constraint inputs.** Add an immutable
  `ConstraintFormalIdentity(raw_name, qualified_name)` record in `resolution/models.py`. Carry it on
  `ConcreteConstraintInput` and `ModuleInput` in an optional field used only for constraint
  modules. Mark both carrier fields excluded from model serialization. The emitted predicate name
  remains in its IR leaf and the wrapper name remains `param_name`; neither is duplicated in
  provenance. *Rejected: add identity to catalog entries (duplicates per-instance graph data and
  changes catalog fingerprints); keep an orchestration side map (can drift from the graph);
  reconstruct identity from sanitized names (cannot distinguish the defect).*
- **D4. Preflight at every graph-aware writer and renderer.** `run_codegen()` validates after either
  context route and before clearing/setup. `_generate_schemas`, `_generate_modules`,
  `_generate_stencils`, `_generate_pipeline`, `_generate_registry`, `_generate_entry_points`,
  `_generate_backlog`, `_generate_tests`, and `_seal_package` repeat the full graph check at function
  entry, before path construction that mutates, `mkdir`, copying, or writing. Graph renderers for
  pipeline YAML, registry source, and model contracts also recheck.
  `_generate_modules` additionally compiles and renders all constraint Python into memory before its
  first `mkdir`/write, so semantic completeness failure cannot leave `predicates.py` or an earlier
  wrapper behind. *Rejected: orchestration-only validation (direct writers bypass it); piecemeal
  wrapper checks after `predicates.py` is written (violates unchanged-tree behavior).*
- **D5. Preserve one immutable violation through public exception adapters.** The pure validator
  returns `ConstraintNameViolation` records and imports neither the generation facade nor public
  exceptions. `PredicateCompileError` and `CodeGenerationError` gain an optional
  `name_safety_violation` attribute. Boundary adapters format but retain the same record object and
  use exception chaining when converting compiler error to package error. *Rejected: message-only
  conversion (loses structured facts); importing public errors in the pure validator (cycle risk);
  exposing an internal validator exception as the public API.*
- **D6. Use Python symbol tables for scope-complete binding inventory.** Production scope policies
  declare generated parameters and locals. A semantic helper runs `symtable.symtable()` over the
  exact emitted source, selects the unique predicate function or class-qualified wrapper `run`
  table, and classifies every symbol that is a parameter or local. That covers ordinary,
  annotated, augmented, tuple/unpacking, loop, `with`, `except`, import, and named-expression
  bindings according to Python itself. Any child symbol table (comprehension, generator expression,
  lambda, nested function, or nested class), `nonlocal`, or declared `global` inside a generated
  function is outside this item's supported subset and fails loudly until policy is reviewed.
  *Rejected: a hand-written partial AST visitor (can miss binding forms); regex/Jinja parsing
  (format-sensitive); allowing nested scopes without an explicit policy (can misattribute names).*
- **D7. Reuse the GAP-CLOSE isolated-overlay method.** One test-only overlay is hashed and copied
  unchanged into detached baseline and candidate worktrees. Each process asserts revision and
  imported source paths before behavior. *Rejected: switching or cleaning the dirty worktree;
  importing candidate-only helpers in the overlay; treating collection/setup failure as RED.*

## Architecture

### Binding and identity model

`ConstraintFormalIdentity` contains:

- `raw_name`: the unsanitized formal name, or the leaf `source_name` for an inline binding.
- `qualified_name`: the extracted qualified identity when present; otherwise `None`.

Identity matching is strict. If both sides carry a QN, the QNs must match. If neither side carries a
QN, the raw names must match. If only one side carries a QN, the package cannot prove identity and
rejects `missing_provenance`; it does not discard the richer fact to make the raw names agree.
Repeated leaves with the same identity key and final name are one binding. The validator rejects one
identity appearing under multiple final names and multiple distinct identities appearing under one
final name.

### Identity construction matrix

The current executable profile admits only `inline` and `definition_typed` forms
(`../agentic-mbse/src/agentic_mbse/sysml/executable_profile.py:720`, `:730`). The defensive
non-definition branches remain explicit because `lower_constraints` contains them and direct tests
can reach them.

| Lowering route | Predicate raw / QN | Wrapper carrier raw / QN | Final names and behavior |
|---|---|---|---|
| Definition, explicit actual | Leaf `reference.source_name`; leaf `reference.target.qualified_name` | `FormalFact.name` (fallback: QN tail); `FormalFact.qualified_name` | Predicate uses source name; wrapper uses `_formal_name(formal)`. Definition indexing already requires the formal QN (`constraint_lowering.py:710`). QNs must match. |
| Definition, omitted default | Same definition predicate leaf fields | Same `FormalFact` returned with `actual=None` by `_decide_definition_formals` | Same identity and final-name rules as explicit actual; default presence changes resolution only. |
| Inline leaf | Leaf `source_name`; leaf target QN when present | The same leaf's `source_name`; the same target QN, captured before `_resolve_formal` | Predicate uses source name; wrapper uses `sanitize_name(source_name)`. A missing target on both sides uses raw fallback honestly. |
| Defensive non-definition actual or omitted-QN branch | Predicate leaf source/target fields | Actual: `ActualFact.name` and its sole `formal_targets[0]` when exactly one exists. Omitted: raw QN tail and the full omitted QN. | Equal QNs prove identity; two absent QNs require equal raw names; one-sided QN or multiple/foreign targets fail closed. No new resolution or form is admitted. |

This matrix uses actual fields already read at `src/sysml_codegen/analysis/constraint_lowering.py:971`
through `:1049`. It does not infer a formal from an actual value's referenced design attribute; that
target is the value source, not the constraint formal.

### Live and snapshot availability

- **Live:** extraction supplies `ConstraintFacts`; `lower_constraints()` constructs the carrier at
  the same point it creates each `ConcreteConstraintInput`, before `_formal_name()` or inline
  sanitization. `extend_graph_with_constraints()` copies it to the matching `ModuleInput`.
- **Snapshot:** current snapshot v3 embeds canonical `constraint-facts/v1`. Its existing codec
  round-trips every matrix field, including expression-leaf target identity
  (`expression_ir.py:172`, `:190`, `:213`). `graph_rebuild.py:211-232` re-runs the same lowering and
  graph extension, so it reconstructs the carrier rather than loading a second representation.
- **Codec decision:** add no snapshot, constraint-facts, expression-IR, or catalog field and do not
  bump a version. Existing accepted v3 snapshots already contain the required facts. A
  `grandfathered_off` snapshot generates no constraint modules and needs no carrier.
- **Backward behavior:** the new carrier field on Pydantic graph models defaults to `None`, so old
  hand-built/non-constraint models still validate. A catalog-backed constraint module with missing
  carrier fails package/render preflight as `missing_provenance`; it never falls back to name-only
  reconciliation. Existing older snapshot formats remain rejected by the loader's current version
  gate (`src/sysml_codegen/snapshot/loader.py:138`).
- **Schema/dump boundary:** the carrier is the only new Pydantic model field and is
  `Field(exclude=True)`. Tests pin omission from `model_dump(mode="python")`,
  `model_dump(mode="json")`, `ComputationGraph.model_dump()`, `ModelContract` payload/bytes, catalog
  fingerprint input, and generated contracts. Because excluded fields can still appear in
  `model_json_schema()`, tests separately pin that the only internal model-schema delta is the two
  optional carrier properties; no generated schema or snapshot schema changes.

### Scope policies

The structured declarations are:

| Scope | Generated parameters | Generated locals | Model binding source |
|---|---|---|---|
| `predicate` | none | `value`, `status` | leaf `source_name` |
| `wrapper` | `self` | `verdict` | `ModuleInput.param_name` |

The validator detects, in this order after global sorting:

1. A model binding overlaps a generated parameter or local in its scope.
2. Distinct source identities share one final binding in that scope.
3. One source identity appears under more than one final binding.
4. At package/render scope, predicate and wrapper identity sets differ.
5. The same identity has different predicate and wrapper names.

Missing wrapper provenance is a correspondence failure, not permission to fall back to name-only
matching. This deliberately requires hand-built constraint graph fixtures to supply the same
metadata production lowering supplies.

Correspondence violations retain the two-scope ordering. A predicate identity with no wrapper or
with a different wrapper name is a `predicate` violation because the predicate binding is the
unsatisfied expectation. A wrapper identity with no predicate is a `wrapper` violation. No third
diagnostic scope is introduced.

### Package data flow

```text
ConstraintCatalog.predicate_ir ----> predicate binding inventory --+
                                                               join by source identity
constraint PipelineModule.inputs --> wrapper binding inventory ----+
                                      |
                                      v
                      sorted violations or unchanged generation
```

The CLI invokes `validate_constraint_graph_name_safety(graph)` immediately after context creation.
It enumerates catalog entries in any order, finds the matching constraint module, parses the stored
IR, creates both inventories, collects all violations, sorts them, and raises one
`CodeGenerationError`. Live and snapshot routes already converge before this point.

### Render and write boundary inventory

Every current constraint-aware path is covered below. “Full” means predicate, wrapper, identity
correspondence, catalog/module join cardinality, and deterministic selection.

| Boundary | I/O | Enforceable check before output |
|---|---|---|
| `compile_predicate()` (`predicate_compiler.py:240`) | Returns one source string | Predicate inventory before body compilation; semantic symbol-table verification before returning source. |
| `compile_shared_predicates()` (`modules.py:131`) | Returns compiled map | Predicate-name F2 guard plus predicate inventory for every distinct definition before compiling any; normalize every `PredicateCompileError`. |
| `render_constraint_predicates_module()` (`modules.py:167`) | Returns shared source string | Verify every supplied function's declared args and symbol-table bindings against predicate policy before returning. A manually forged compiled map cannot bypass completeness. |
| `render_constraint_module()` (`modules.py:188`) | Returns wrapper source string | Full one-module join/wrapper/correspondence check before template render; symbol-table verification before return. |
| `generate_teax_module()` constraint dispatch (`modules.py:280`, `:310`) | Returns wrapper source string | Delegates to the checked constraint renderer; report aggregator has no model-formal `run` inputs in this policy. |
| `generate_pipeline_yaml()` (`generation/pipeline.py:26`) | Returns package YAML | Full graph preflight before context construction. |
| `generate_registry()` (`generation/registry.py:185`) | Returns package Python | Full graph preflight before import/context construction. |
| `build_model_contract()` (`contracts/model_contract.py:27`) | Returns semantic contract | Full graph preflight before projection/fingerprinting. |
| `_generate_schemas()` (`cli/__init__.py:290`) | Writes generic schemas and `constraint_types.py` | Full graph preflight at entry, before the first generic schema write at `:315`. |
| `_generate_modules()` (`cli/__init__.py:333`) | Creates namespaces; writes predicates and wrappers | Full graph preflight at entry. Compile/render/semantic-check all constraint Python in memory before the first `mkdir` at `:357`; only then write. |
| `_generate_stencils()` (`cli/__init__.py:402`) | May create handwritten namespaces and files | Full graph preflight at entry, before the first possible namespace `mkdir` at `:429`, even though its loop skips constraint and report modules. |
| `_generate_pipeline()` (`cli/__init__.py:488`) | Writes YAML | Full graph preflight at entry, before `write_text` at `:505`; renderer repeats it. |
| `_generate_registry()` (`cli/__init__.py:511`) | Writes package `__init__.py` | Full graph preflight at entry, before `write_text` at `:532`; renderer repeats it. |
| `_generate_entry_points()` (`cli/__init__.py:538`) | Lower helpers create schema/input dirs and files | Full graph preflight at entry, before calling writers whose first `mkdir` is `generation/entry_point.py:210`. |
| `_generate_backlog()` (`cli/__init__.py:568`) | May write `IMPLEMENTATION_BACKLOG.md` | Full graph preflight at entry, before `write_text` at `:582`, even though the report excludes fully generated constraint modules. |
| `_generate_tests()` (`cli/__init__.py:587`) | Creates tests dir and writes generated tests | Full graph preflight at entry, before `mkdir` at `:596`, even though test generation skips constraint modules. |
| `_seal_package()` (`cli/__init__.py:610`) | Creates contracts dir, copies verifier, writes contracts | Full graph preflight at entry, before `mkdir` at `:624`; `build_model_contract` repeats it. |
| `run_codegen()` (`cli/__init__.py:929`) | Owns complete target lifecycle | Full graph preflight after live/snapshot context convergence and before overwrite clearing at `:990`, setup, primitives, or any writer. |

`_setup_output_directories` and `_generate_primitives` have no graph input and are not independently
constraint-aware; `run_codegen` guards them. The stencil, backlog, and generated-test renderers skip
`CONSTRAINT`/`REPORT_AGGREGATOR` modules (`cli/__init__.py:420`,
`generation/stencils.py:224`, `generation/test_gen.py:53`), so they do not materialize the bindings
in scope; their graph-aware CLI writers still preflight because those functions can mutate a target
when called directly. The low-level entry-point writers accept only parameter groups and cannot
prove cross-scope identity; `_generate_entry_points`, the graph-aware package writer, preflights
before calling them. Expanding generic lower APIs to accept a graph is rejected as an unrelated
refactor.

For every graph-aware filesystem writer in the table, an unsafe graph has two required outcomes:
an absent output root remains absent, and a pre-existing root retains an identical complete manifest
(relative paths, kinds, directory entries, symlink targets, and regular-file bytes). This is tested
per writer, not inferred from the `run_codegen` test.

### Exception normalization and payload flow

`ConstraintNameViolation` is immutable and contains the complete selected collision group. The pure
validator returns violations; it does not import or raise `PredicateCompileError` /
`CodeGenerationError`. Public errors carry the record in an optional
`name_safety_violation` attribute. Existing non-name constructions remain source-compatible because
the attribute defaults to `None`.

| Boundary | Name-safety outcome | Other failure behavior |
|---|---|---|
| Direct `compile_predicate()` | `PredicateCompileError(message, name_safety_violation=record)` | Existing `PredicateCompileError` cases remain that type with payload `None`. |
| `compile_shared_predicates()` | Catch compiler error and raise `CodeGenerationError` from it, attaching the exact same record object and package context. | Normalize every other `PredicateCompileError` to `CodeGenerationError` with payload `None`; package generation never leaks compiler-private errors. |
| Direct predicate/wrapper renderer and `generate_teax_module()` | `CodeGenerationError` with the selected record; already-normalized errors pass through without rewrapping. | Existing non-name renderer errors keep their present behavior. |
| Graph renderer or direct filesystem writer | Full preflight raises `CodeGenerationError` with record before render/write. | I/O/Jinja failures remain their existing types; this item normalizes name-safety failures only. |
| `run_codegen()` orchestration | The preflight raises that same `CodeGenerationError` inside the existing `try`. The catch logs the formatted message with `extra={"constraint_name_safety": record}` and returns the established `False`; it does not replace or discard the payload before logging. | Existing `SysMLParsingError`, other `CodeGenerationError`, and unexpected-error behavior remains unchanged (`cli/__init__.py:1037`). |
| CLI `cmd_generate` | `False` maps to the existing nonzero exit; stderr contains the deterministic formatted diagnostic. Structured facts remain available on the orchestration log record; the process boundary cannot expose a Python object. | No CLI return-contract change. |

The shared `CodeGenerationError` lives in `orchestration/pipeline_context.py:51`. Its optional payload
is typed without importing generation at runtime. `generation/errors.py` owns the lazy boundary
adapter that formats a violation and constructs the public error, following its existing lazy-import
pattern (`generation/errors.py:12`). `PredicateCompileError` owns the same optional typed payload at
the compiler boundary. Conversion uses `raise ... from ...`; tests assert record object identity,
formatted-message parity, and cause chain.

### Scope-completeness algorithm

The checker analyzes emitted Python, never template text:

1. Compile a symbol table from the exact returned source with `symtable.symtable()`.
2. Locate exactly one target scope: top-level predicate function by exact name, or wrapper class then
   exact `run` method. Missing or duplicate tables fail loudly.
3. Treat every symbol with `is_parameter()` as a parameter. Treat every `is_local()` symbol that is
   not a parameter as a local, including assignment, unpacking, loop/with/except targets, imports,
   named expressions, and function/class namespace bindings as classified by Python.
4. Reject `is_nonlocal()` or `is_declared_global()` declarations in the target. Referenced globals
   are not bindings and remain allowed.
5. Reject any child symbol table. Current generated functions need no comprehension, generator,
   lambda, nested function, or nested class scope; adding one requires an explicit policy update.
6. Subtract only the injected model parameters by exact binding inventory. The remaining parameter
   and local sets must equal the structured policy exactly.

This is an explicit supported subset with fail-loud extension behavior. Mutation tests cover
positional-only/regular/keyword-only/variadic arguments; `Assign`, `AnnAssign`, `AugAssign`, and
tuple/list/starred unpacking; sync/async `for` and `with`; exception aliases; `import` and
`from ... import`; named expressions; plus child-scope and global/nonlocal rejection. A new Python
binding form is classified by the interpreter's symbol table; if it creates a child scope, the
unknown-scope guard rejects it.

### Deterministic diagnostics

An immutable violation carries `scope`, `kind`, final binding, colliding generated binding when
applicable, predicate function name when applicable, constraint ID, usage qualified name, and the
sorted involved identities. It never stores a preformatted sentence. Package adapters enrich the
record before formatting rather than prepending an unstructured context string.

Sort violations by fixed scope rank (`predicate`, then `wrapper`), final binding, then identity key,
constraint ID, usage QN, and kind. Format identities with a fixed field order (`raw_name`, then
`qualified_name`) and `repr` escaping. The message reports the complete selected collision group,
not the first traversed pair. Compiler messages omit unavailable package fields; package messages
include them. Input, catalog, leaf, and module permutations therefore cannot alter the exception
type or text.

## Required Invariants

- **I1.** A model binding never overlaps a codegen-owned parameter or local in its actual Python
  scope.
- **I2.** Within either scope, one final model parameter represents exactly one source identity.
- **I3.** Repeated references to one identity with one name produce one predicate argument in
  first-occurrence order.
- **I4.** Predicate and wrapper inventories for a generated constraint contain exactly the same
  identity keys, and each key has the same final name in both scopes.
- **I5.** Package violations sort `predicate` before `wrapper`; all remaining selection and message
  ordering is independent of input traversal.
- **I6.** Every catalog entry joins exactly one constraint module and every constraint module joins
  exactly one catalog entry. Missing or duplicate joins are checked violations, not a bet or a
  `next()` selection.
- **I7.** Every graph-aware writer rejects before its first filesystem operation. For both that
  direct writer and `run_codegen`, an absent target stays absent and a populated target's complete
  manifest is unchanged.
- **I8.** Direct compiler violations are `PredicateCompileError`. Package, render, and orchestration
  violations are `CodeGenerationError`. Raw `SyntaxError`, `TypeError`, and silent evidence are not
  validation outcomes. Every name-safety public error or orchestration log record carries the same
  immutable violation payload.
- **I9.** The policy's generated-binding declarations equal the parameters and locals reported by
  Python's symbol table after exact model parameters are removed. Unsupported child scopes and
  global/nonlocal declarations fail loudly.
- **I10.** Provenance carrier fields survive in-memory model copies but are excluded from serialized
  graph/catalog/contract payloads.
- **I11.** Current snapshot v3/facts-v1 bytes need no new field or version. Live and snapshot
  re-lowering construct equal carriers and equal violations for equal facts.
- **I12.** If validation succeeds, all existing names, input order, template context, wiring,
  generated files, contracts, fingerprints, and seals are byte-identical to `512786c` for the same
  collision-free input.

## Component Overview and File-Level Changes

- **`src/sysml_codegen/generation/constraint_name_safety.py` (new):** immutable policy binding and
  violation records; IR and module-input inventory builders; pure predicate, wrapper,
  correspondence, graph, symbol-table, sorter, and formatter functions. Resolution owns the formal
  carrier. This module performs no sanitization, filesystem work, public-error construction, or CLI/
  generation-facade import.
- **`src/sysml_codegen/resolution/models.py`:** define the immutable formal identity
  record and add excluded optional provenance fields to `ConcreteConstraintInput` and `ModuleInput`.
  Keep the generic `ModuleInput` default `None`; only constraint construction populates it.
- **`src/sysml_codegen/orchestration/pipeline_context.py`:** extend `CodeGenerationError` with the
  optional data-only `name_safety_violation` payload without importing generation at runtime.
- **`src/sysml_codegen/generation/errors.py`:** add the lazy CodeGenerationError adapter for a
  selected violation; preserve the existing dependency direction.
- **`src/sysml_codegen/analysis/constraint_lowering.py`:** construct identity before name
  sanitization, pass it through `_resolve_formal`, omitted defaults, and inline-leaf construction,
  then copy it into constraint `ModuleInput`. Do not change `sanitize_name()` or resolution order.
- **`src/sysml_codegen/generation/predicate_compiler.py`:** replace string-first leaf deduplication
  with the shared predicate inventory; validate before body compilation; retain the returned
  argument list and collision-free order; normalize to `PredicateCompileError`.
- **`src/sysml_codegen/generation/modules.py`:** invoke unit validators, normalize compiler failures,
  replace name-only reconciliation, and symbol-check both returned generated function scopes. Keep
  predicate function naming and GAP-CLOSE collision behavior unchanged.
- **`src/sysml_codegen/generation/{pipeline,registry}.py` and
  `src/sysml_codegen/contracts/model_contract.py`:** recheck the full graph at direct graph-render
  entry points before constructing output.
- **`src/sysml_codegen/cli/__init__.py`:** add one private full-preflight adapter and call it at
  `run_codegen` plus all nine graph-aware writers listed in the boundary table. `_generate_modules`
  stages all constraint render results in memory before its first write. Retain GAP-CLOSE's
  predicate-function-name guard as part of the shared full check.
- **`src/sysml_codegen/orchestration/pipeline_builder.py`:** no production edit expected. Verify in
  tests that both live and snapshot context builders preserve the excluded input metadata through
  graph construction.
- **Snapshots/codecs/templates:** no production edit expected. Existing facts codecs supply
  provenance; templates remain the emitted truth inspected by the symbol-table guard.
- **`tests/unit/test_predicate_compiler.py`:** predicate reserved-name, identity-collapse,
  same-identity repeat, permutation, exact exception, and argument-order tests.
- **`tests/unit/test_constraint_emission.py`:** wrapper reserved-name, sanitizer-collapse,
  cross-path disagreement/missing/extra identity, deterministic diagnostic, render-boundary
  normalization, and collision-free source tests.
- **`tests/unit/test_cli_generation.py`:** four-name package preflight, scope-order selection, and a
  parameterized direct-writer matrix proving absent/populated target preservation before first I/O.
- **`tests/conformance/test_constraint_generation_integration.py`:** scope-complete symbol-table
  guard, binding-form mutation matrix, and a fully metadata-bearing offline graph.
- **Snapshot/live route tests:** prove the identity construction matrix and diagnostics are equal
  after live lowering and snapshot codec/rebuild, and prove no snapshot version/section changes.
- **`tests/execution/test_constraint_execution.py` or a focused new execution test:** import and run
  one real collision-free generated constraint for satisfied and violated inputs, asserting exact
  evidence and observed values.
- **`.project/active/constraint-wave-name-safety/evidence/` (implementation stage):** immutable
  historical overlay, candidate production patch, hashes, commands, and RED/GREEN outputs.

## Non-Goals

- Changes to either general sanitizer, ADR-003, qualified-name types, or non-constraint naming.
- Renaming accepted or rejected formals, adding aliases, or modifying public pipeline wiring.
- Predicate-function-name collision changes beyond reusing the landed GAP-CLOSE guard.
- Template refactors, generated-runtime guards, executable-profile changes, margin/polarity changes,
  or report aggregation changes.
- Snapshot schema changes, catalog schema expansion, contract/fingerprint churn, or provenance for
  non-constraint modules.
- R-1, R-2, R-4, or the primary review's Medium/Low findings.

## Implementation Notes

- Keep the identity record immutable and data-only in `resolution.models`. The name-safety module
  may import it alongside the graph models already consumed by generation; models must not import
  generation code.
- `Field(exclude=True)` is load-bearing. Test deep-copy retention separately from omission in
  Python-mode and JSON-mode model dumps, the complete graph dump, model-contract payload and bytes,
  catalog fingerprint input, generated contracts, and snapshot sections. Pin the two internal
  Pydantic model-schema property additions separately; do not confuse schema visibility with dump
  inclusion.
- Do not treat `target=None` as a new unique identity per leaf occurrence. With no richer source
  fact, equal raw names are repeated references; inventing occurrence identity would reject valid
  expressions such as `x > 0 and x < 10`.
- Do not sort returned predicate arguments. Deterministic diagnostic sorting is separate from the
  existing first-occurrence signature order, which must remain byte-stable.
- The graph validator must reject duplicate/missing constraint modules before binding comparison,
  naming the catalog entry. It must not silently select `next()` when the join is ambiguous.
- Keep diagnostic formatting centralized. Boundary adapters prepend or populate context fields;
  they do not rebuild messages independently.

## Potential Risks

- **Some inline leaves may lack resolved target identity.** Use the explicit raw-name fallback and
  test it. Do not claim it distinguishes information extraction did not provide.
- **Excluded provenance could disappear during a model copy.** Pin both deep-copy retention and
  dump exclusion. A lost record must fail package preflight, not fall back to names.
- **Hand-built tests and callers currently omit provenance.** Update constraint fixtures. Failing
  closed is intended because name-only reconciliation is the old unsafe behavior.
- **The completeness test could exercise only the current templates.** Run the symbol-table checker
  over production predicate and wrapper output with at least two distinct sentinel inputs. Then
  mutate each supported binding category and each fail-loud category independently. This proves the
  guard follows Python scope semantics instead of merely recognizing today's argument and ordinary
  assignment shapes.
- **Early and lower checks could format different messages.** Use the same structured violation and
  formatter; assert exact parity in tests.
- **A candidate byte comparison could import the wrong editable checkout.** Every historical and
  generated-package process asserts resolved source paths before behavior.

## Integration Strategy

Introduce the identity carrier and validators without changing emitted schemas or templates. First
make lowering populate excluded metadata and update hand-built graph fixtures. Then enable direct
compiler and renderer rechecks. Add full graph preflight to every graph-aware filesystem writer in
the boundary table before its first operation, and retain the earlier `run_codegen()` preflight
before target clearing or setup. Stage all constraint module source in memory before
`_generate_modules()` writes. Collision-free builds traverse the same render functions with the
same context, so the only observable change is deterministic rejection of unsafe graphs.

This complements GAP-CLOSE F2. F2 proves predicate function names are injective across definitions;
this item proves model parameters are injective inside each generated function and correspond
across the two functions used by one constraint. Neither changes the sanitizer.

## Validation Approach

### RED tests at `512786c`

Use one overlay whose imports and fixture builders exist at the baseline. Run each node separately:

- `value`: direct predicate compile is expected to raise; baseline instead executes a violated
  inequality whose margin becomes positive after local rebinding.
- `status`: direct predicate compile is expected to raise; baseline instead returns `margin=None`.
- `verdict`: wrapper render/package preflight is expected to raise; baseline generated `run()`
  raises `TypeError` when `float(verdict)` sees `_PredicateResult`.
- `self`: wrapper render/package preflight is expected to raise; baseline emits a duplicate
  parameter and `ast.parse`/import raises `SyntaxError`.

Separate baseline-pass impact nodes record each old symptom. A RED rejection node counts only when
it reaches the expected public boundary and fails because no typed rejection occurred. Collection,
fixture, import-source, or setup failures invalidate the record.

Additional RED nodes cover two distinct predicate target QNs sharing a leaf name, two definition
formals sanitizing to one wrapper name, and one identity whose predicate and wrapper names disagree.

### GREEN focused tests

- Predicate unit tests prove reserved collisions, duplicate-identity handling, repeat deduplication,
  deterministic messages, and `PredicateCompileError`.
- Emission tests prove wrapper reserved/collapse cases, exact identity correspondence, direct-render
  `CodeGenerationError`, permutation invariance, exact violation-object preservation, cause chaining,
  and message parity across compiler, shared renderer, module renderer, and package adapters.
- CLI tests run every named collision through a synthetic real `run_codegen()` context. A
  parameterized matrix also calls `_generate_schemas`, `_generate_modules`, `_generate_pipeline`,
  `_generate_stencils`, `_generate_registry`, `_generate_entry_points`, `_generate_backlog`,
  `_generate_tests`, and `_seal_package` directly. For every boundary, an absent target remains
  absent and a populated target retains its complete manifest, including directories, regular-file
  bytes, path kinds, and symlink targets. Log capture proves orchestration retains the selected
  structured payload before the process boundary maps failure to a nonzero exit.
- Symbol-table completeness tests compare both production-generated function scopes with the two
  structured policies. Independent mutations cover all argument kinds; ordinary, annotated, and
  augmented assignments; tuple/list/starred unpacking; sync/async loop and `with` targets; exception
  aliases; imports; and named expressions. Comprehensions, generator expressions, lambdas, nested
  functions/classes, and `global`/`nonlocal` declarations prove the fail-loud guard.
- Live and snapshot route tests cover every identity-construction row, including one-sided and
  absent qualified identities. They assert carrier equality, diagnostic equality, codec round-trip
  parity, and no snapshot field or version change. Serialization tests separately pin deep-copy
  retention, all named dump/contract/fingerprint omissions, and the exact internal schema delta.
- A real generated collision-free module runs `x <= limit` once satisfied and once violated. Assert
  exact `actual_value`, `status`, positive/negative signed margin, and
  `observed == {"x": ..., "limit": ...}` for both.

Focused commands for the implementation plan:

```bash
uv run pytest -q tests/unit/test_predicate_compiler.py tests/unit/test_constraint_emission.py tests/unit/test_cli_generation.py tests/conformance/test_constraint_generation_integration.py
PYTHONOPTIMIZE=1 uv run pytest -q tests/unit/test_predicate_compiler.py tests/unit/test_constraint_emission.py tests/unit/test_cli_generation.py tests/conformance/test_constraint_generation_integration.py
```

Add the named execution node to both selections when its final file is chosen. Then run the broader
constraint generation/execution selection and normal project lint/type gates. Optimized Python is
required because validation must not depend on `assert`.

### Historical overlay and byte proof

1. Save and hash the test-only overlay before production changes.
2. Create detached baseline and candidate worktrees under one new `mktemp -d` root at exact revision
   `512786c`. Never checkout, reset, clean, or stash the current dirty worktree.
3. Assert `git rev-parse HEAD`, `sysml_codegen.__file__`, and relevant module source paths inside
   every fresh process. Set `PYTHONNOUSERSITE=1`, `PYTHONDONTWRITEBYTECODE=1`, and put the selected
   worktree first on `PYTHONPATH`.
4. Copy the identical overlay to both worktrees. Apply only the allowlisted candidate production
   patch to the candidate after `git apply --check`; record hashes for overlay and patch.
5. Run each four-name symptom node and rejection node separately at baseline, then the same rejection
   nodes at candidate. Record exact command, exit status, stdout/stderr, revision, paths, and reason.
6. Generate one fixed collision-free snapshot package from both worktrees with identical package
   name and absolute input. Compare sorted relative paths and every file byte. The permitted diff
   set is empty. Run the satisfied/violated control from each generated tree in fresh subprocesses.
7. Remove only the named temporary worktrees after durable evidence has been written. Leave the
   current worktree and user changes untouched.

## Next-Stage Handoff

The plan should implement approved D1–D7 and I1–I12 unless new evidence invalidates a bet or an
inferred premise. De-risk identity retention first: prove the metadata survives lowering and graph
copies while remaining absent from the named payload surfaces. Then land predicate and wrapper unit
RED/GREEN behavior, followed by every writer preflight and the symbol-table completeness guard. The
highest-risk gate is exact before/after bytes because even excluded metadata can accidentally enter
a dump or fingerprint. The second is cross-path identity coverage for inline leaves without a
qualified target.

No technical decision remains open. If implementation finds a valid production path where neither
a qualified identity nor an honest raw identity reaches lowering, surface that premise conflict
before weakening correspondence or inventing provenance.

## Next Steps

After design approval, use `my-plan` to sequence the RED overlay, provenance threading, validators,
preflight, execution control, and byte gates. After implementation, use `my-audit` in a fresh stage.

---

Next Step: After approval → `my-plan`
