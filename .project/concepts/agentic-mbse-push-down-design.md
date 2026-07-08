# agentic-mbse Push-Down Design: Abstraction Boundary & Execution Plan

**Date**: 2026-02-20
**Based on**: `.project/research/20260220-163000_agentic-mbse-boundary-analysis.md`
**Branch**: cost-pattern-refactor (1821 tests as of review)
**Status**: Design — awaiting approval
**Refreshed**: 2026-07-06 against HEAD `a2cdc18` (branch `truth-debt-epic-plan`) — see the
Refresh Verdict below. Strategy stands; inventory re-verified per section. Gated on TRUTH-DEBT
Items 1/2/6. Test-count anchor "1821" is stale (≥1636 test *functions* on HEAD before
parametrization; recount at epic_plan).

---

## Refresh Verdict — 2026-07-06 (HEAD `a2cdc18`, branch `truth-debt-epic-plan`)

**What this block is.** A verification pass, not a redesign. Every section below now
carries a dated `> **[REFRESH 2026-07-06]**` callout with the corrections. The original
analysis is left in place; read the callout for what changed. This doc was written on
2026-02-20, before the PIPELINE-TRUTH epic (merged as PR #5) and before the just-defined
TRUTH-DEBT epic. Both reshaped the exact files it inventories.

**How much survives.** The *strategy* survives; the *inventory* is stale.

- **Strategy — STANDS (~90%).** The two-tier split (pure SysML vs codegen), the phasing
  (do expression reconstruction + qualified names first, hierarchy/aggregation second, defer
  template detection), the re-export containment pattern, and the dataclass-not-Pydantic
  ruling are all still the right shape. Nothing in PIPELINE-TRUTH invalidated the direction.
- **Inventory — STALE (~40% of specific facts wrong).** Every line count is off (the files
  grew 8–35%). Two files the doc treats as push-down inputs no longer exist
  (`constraint_extractor.py`, `constraints.py`). The `snapshot_loader.py` test helper that
  the whole R1 blast-radius argument rests on is gone. Four functions the doc names by hand
  (`is_literal_expression`→still there but doc mis-names `extract_feature_ref_name`;
  `_is_template_usage` deleted; `RedefinitionKind` is actually `RedefinitionType`) are wrong.
  The biggest single correction: **`qualified_names.py` is no longer a pure-SysML file** — it
  grew codegen-specific name builders (`get_module_name`, `get_channel_name`,
  `build_parameter_qualified_name`), so Tier 1b changes from "whole file moves, 0 blast
  radius" to "split the module, move only the general subset."

**New governance the move must respect** (did not exist on 2026-02-20):

- **INV-1..INV-5 dispatch/lookup invariants** (`reference/19-ast-dispatch-invariant.md` — note
  the filename; it is not `19-expression-reconstruction.md`). INV-1 names
  `hierarchy_resolver` `AGG_PYTHON_OPS` and `_extract_single_binding`; INV-5 names
  `sanitize_name`. All three are inside the push-down set. Per R1, their fires-on-shape +
  silent-on-clean tests MUST move with the code.
- **Adapter hard-error (`TYPE_MAP` whitelist)** in `agentic-mbse/sysml/syside_adapter.py`.
  Moved code that calls `SysideAdapter.is_instance("SomeType")` needs its type names in the
  whitelist BEFORE the move, or extraction hard-errors. **Could not byte-verify** — the
  agentic-mbse repo is outside this session's sandbox. Confirm at epic-plan pickup.
- **Snapshot format v2** with a loader hard-gate (`SnapshotFormatError`, INV-2); baseline
  churn runs under the `--fixtures` byte-identity discipline (memory `byte-identity-captured-at-churn`).
- **Editable-install lockstep**: a mid-move state in agentic-mbse breaks the sysml-codegen
  suite instantly (memory `orchestrated-run-gotchas`). The execution plan needs per-move
  branch-parking so the two repos never sit half-migrated.

**Gate status.** PUSH-DOWN is **blocked** on TRUTH-DEBT Items 1, 2, and 6 landing
(`.project/backlog/epic_truth_debt.md`, "Sequencing Rulings"). Those items edit the exact
surfaces this doc moves: Item 1 finalizes the aggregation-resolution path
(`input_resolver.py` / `AGG_STRATEGIES`), Item 2 builds multi-hop chain resolution on
`extract_feature_chain_segments` (a NEW `expression_utils` function), and Item 6 hardens the
D3 silent sites (loader, aggregation compile) that overlap the moved code. Moving before they
land means moving code that is about to change under you.

**Recommended epic_plan timing.** Do NOT run the PUSH-DOWN epic_plan against this doc as-is —
the stale inventory would seed wrong line counts, wrong blast-radius numbers, and a wrong
Tier 1b plan. Either (a) run epic_plan **after TRUTH-DEBT closes**, re-verifying the
now-doubly-changed files at that point, or (b) if epic_plan must be drafted sooner, drive it
from the per-section callouts below, not the original tables. The callouts are the current
truth; the original prose is preserved for provenance only.

---

## Problem Statement

The 7-phase refactor exposed a stratification in `sysml-codegen/extraction/`: some logic is
pure SysML model understanding, some is codegen-specific. Today these are mixed in the same
files and the same package. This creates two problems:

1. **Reuse blocked** — other tools that need SysML model understanding (validation, docs,
   simulation) can't access it without depending on sysml-codegen
2. **Unclear ownership** — contributors can't tell whether a function belongs to "understanding
   the model" or "preparing for code generation"

The goal: move reusable SysML semantics into `agentic-mbse/sysml/` with minimal blast radius
to the 1821-test sysml-codegen suite.

---

## Current State: The Boundary Today

```
┌─────────────────────────────────────────────────────────────────────┐
│                        sysml-codegen                                │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │ generation/        resolution/       analysis/              │    │
│  │ (templates,        (graph_builder,   (backtracker,          │    │
│  │  YAML, stencils)   ComputationGraph) param_groups)          │    │
│  └──────────────────────────┬──────────────────────────────────┘    │
│                             │ consumes                              │
│  ┌──────────────────────────▼──────────────────────────────────┐    │
│  │ core/                   extraction/                          │    │
│  │ ┌──────────────────┐   ┌──────────────────────────────────┐ │    │
│  │ │ output_registry  │   │ extractor.py          (653 ln)   │ │    │
│  │ │ identifier_types │   │ usage_extractor.py    (664 ln)   │ │    │
│  │ │ qualified_names  │   │ expression_compiler   (619 ln)   │ │    │
│  │ │ models           │   │ hierarchy_resolver    (575 ln) <--- MIXED│
│  │ └──────────────────┘   │ data_models           (367 ln)   │ │    │
│  │    0 imports from      │ computed_attr_extr    (275 ln)   │ │    │
│  │    agentic-mbse        │ constraint_extr       (261 ln)   │ │    │
│  │                        │ expression_utils      (201 ln) <--- PURE SYSML
│  │                        │ constraints           (262 ln)   │ │    │
│  │                        └──────────────────────────────────┘ │    │
│  └─────────────────────────────────────────────────────────────┘    │
│         │ 9 files import SysideAdapter                              │
│         │ 5 files import BindingType/ExpressionRef                  │
│         v                                                           │
├ - - - - - - - - - - PACKAGE BOUNDARY - - - - - - - - - - - - - - - ┤
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                    agentic-mbse/sysml/                       │    │
│  │                                                              │    │
│  │  syside_adapter.py  (302 ln)   THE gate to syside           │    │
│  │  types.py           (273 ln)   BindingType, ExpressionRef   │    │
│  │  expression.py      (510 ln)   traverse, extract_refs       │    │
│  │  binding.py         (264 ln)   classify, extract bindings   │    │
│  │  helpers.py         (136 ln)   name/location lookups        │    │
│  │  graph.py           (132 ln)   cycles, topo sort            │    │
│  │  data_models.py      (39 ln)   AttributeInfo base           │    │
│  │                                                              │    │
│  │  TOTAL: ~1,700 lines -- element-level only                  │    │
│  │  GAP: No composition, no hierarchy, no expression text      │    │
│  └─────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
```

The problem is visible: the extraction layer is a mix of pure SysML semantics and
codegen-specific logic, all in the same directory.

---

## Per-File Decomposition: What Is SysML-General vs Codegen-Specific

### Tier 1: Pure SysML (zero codegen concepts referenced)

> **Sequencing (UPSTREAM-FINDINGS Item 6 lands first).** The expression-reconstruction
> fidelity fix (literal-before-invocation dispatch + precedence-aware parens, plus the new
> `RANK`/`binary_op_of`/`needs_parens` helpers and the `str(operator)` enum-normalization)
> travels with this move. Landing Item 6 before Phase 1 means the pushed-down
> `reconstruct_expression` / `reconstruct_operator_expression` are born correct and the mass
> baseline churn was reviewed once, in Item 6 — not re-litigated during the move.

> **[REFRESH 2026-07-06]** — expression_utils.py is now **356 lines** (was 201).
> Function inventory verified against HEAD:
> - **STANDING**: `reconstruct_expression`, `extract_feature_chain_name`,
>   `extract_literal_value`, `is_literal_expression`, `OPERATOR_MAP`.
> - **NAME CORRECTION**: the doc's `extract_feature_ref_name` is actually
>   `extract_feature_reference_name` (`expression_utils.py:225`). Fix in any epic_plan.
> - **NEW** (PIPELINE-TRUTH Item 6 precedence work + Item 5 chain work):
>   `binary_op_of` (`:121`), `needs_parens` (`:143`), `reconstruct_operator_expression`
>   (`:162`), `extract_feature_chain_segments` (`:279`), plus constants `RANK`, `UNARY_RANK`,
>   `RIGHT_ASSOC`. These are the precedence-aware parenthesization helpers and the
>   segment-yielder. **They ALL move with the file** — same reasoning as the original rows.
> - **LOAD-BEARING NEW FUNCTION**: `extract_feature_chain_segments` is what TRUTH-DEBT Item 2
>   (multi-hop chains) and Item 5 build on. It is being actively changed in TRUTH-DEBT. This
>   is a direct reason PUSH-DOWN must wait for Item 2 (gate confirmed).
> - **Callers now 5, not 6**: `hierarchy_resolver`, `expression_compiler`, `extractor`,
>   `usage_extractor`, `computed_attribute_extractor`. The 6th (`constraint_extractor`) is
>   GONE (see Tier 3 callout).
> - **New governance**: `reconstruct_operator_expression`'s dispatch is an INV-1 totality site
>   (`reference/19-ast-dispatch-invariant.md`). Its fires-on-shape test
>   (`test_ast_dispatch_invariant.py`, `test_expression_paren_helper.py`,
>   `test_expression_reconstruction_fidelity.py`) MUST move with the code (R1).

#### expression_utils.py (201 lines) -- ALL MOVES

```
  reconstruct_expression()      AST node -> "a + b * c" text
  extract_feature_chain_name()  FeatureChain -> "part.attr" text
  extract_feature_ref_name()    FeatureRef -> qualified name
  extract_literal_value()       LiteralInteger -> 42
  is_literal_expression()       type check for literal AST nodes
  OPERATOR_MAP                  SysML ops -> text symbols

  Imports: SysideAdapter only
  Depends on: nothing codegen-specific
  Callers: 6 files (hierarchy_resolver, expression_compiler, extractor,
           usage_extractor, constraint_extractor, computed_attribute_extractor)
  Risk: LOW -- already a self-contained module
```

This is the missing inverse operation to agentic-mbse's `traverse_expression()` and
`extract_feature_refs()`. agentic-mbse can analyze AST nodes but has no way to get
text back from them. Any tool displaying SysML expressions needs this.

**Target**: Extend `agentic_mbse.sysml.expression` (alongside existing traversal functions)

**Naming hazards to resolve during push-down**:

- **`is_literal_expression()` semantic divergence**: This file's version uses
  `SysideAdapter.is_instance()` against 5 specific literal type names (structural type
  check). agentic-mbse `expression.py` already has `is_literal_expression()` that checks
  `len(extract_feature_refs(expr)) == 0` (semantic: "has no feature refs"). These are NOT
  equivalent. **Resolution**: rename the sysml-codegen version to `is_literal_node()` when
  pushing into agentic-mbse to avoid silent behavioral change.

- **`extract_literal_value()` duplication**: `agentic_mbse.sysml.binding` has a private
  `_extract_literal_value()` with identical logic. **Resolution**: Phase 1 should fold
  `binding._extract_literal_value` into the new public `expression.extract_literal_value`
  and update `binding.py` to call it.

- **`extract_feature_chain_name()` vs `get_reference_name()` overlap**: The existing
  `get_reference_name()` in `expression.py` returns only the terminal name (`"attr"`),
  while this function builds dotted paths (`"instance.attr"`). Both are valid but serve
  different purposes. **Resolution**: add explicit docstring cross-references when
  extending `expression.py` to prevent caller confusion.

> **[REFRESH 2026-07-06]** — **BIGGEST CORRECTION IN THE DOC.** qualified_names.py is now
> **181 lines** (was 133) and is **no longer a pure-SysML file**. It grew codegen-specific
> name builders. "ALL MOVES" is now WRONG — this must be a **split**, not a whole-file move.
>
> Function inventory against HEAD:
> - **SysML-general → push-down eligible**: `sanitize_name` (`:14`),
>   `build_element_qualified_name` (`:48`, now takes a `use_double_underscore` param — this
>   partially answers Open Question #1 on the separator default), `sysml_to_python_qualified_name`
>   (`:112`), `python_to_sysml_qualified_name` (`:133`), `sanitize_qualified_name` (`:117`),
>   `extract_simple_name` (`:138`).
> - **CODEGEN-SPECIFIC → STAY in sysml-codegen** (ADR-003 PQN/EQN/channel format, not SysML
>   semantics): `build_parameter_qualified_name` (`:97`), `get_module_name` (`:102`),
>   `get_channel_name` (`:107`), `owning_part_leaf` (`:149`).
> - **NEW helper**: `_build_owner_chain_with_packages` (`:74`, private, supports
>   `build_element_qualified_name`).
> - **Hardened contract**: `sanitize_name` now carries the INV-5 guarantee — the result
>   ALWAYS satisfies `.isidentifier()` and is never a keyword, and sibling names that collide
>   on one EP/channel key **fail fast** at registration. Its fires-on-shape tests
>   (`test_sanitize_invariance.py`, `test_silent_failure_sc4a1.py`) must move with it (R1).
>
> **Consequence for Tier 1b**: the "core/qualified_names.py becomes a 2-line re-export →
> 0 files, NONE blast radius" claim is void. The general subset can re-export from
> agentic-mbse, but the codegen builders stay behind, so `core/qualified_names.py` becomes a
> mixed file (some local defs, some re-exports) — small blast radius, but not zero, and the
> split point must be designed. Re-verify at epic_plan.

#### core/qualified_names.py (133 lines) -- ALL MOVES

```
  sanitize_name()                  "my attr" -> "my_attr"
  build_element_qualified_name()   elem -> "Pkg::Part::calc"
  sysml_to_python_qualified_name() "A::B" -> "A__B"
  python_to_sysml_qualified_name() "A__B" -> "A::B"

  Imports: ZERO from agentic-mbse (pure string functions)
  Callers: 10 files (see Tier 1b blast radius)
  Risk: LOW -- pure functions, no state
```

Currently enforced as single source of truth in sysml-codegen: "All identifier construction
MUST use these functions. Do NOT construct qualified names via inline f-strings." Any SysML
consumer needs qualified name construction.

**Target**: New `agentic_mbse.sysml.qualified_names` module

**P1 exception**: `build_element_qualified_name()` traverses the syside AST ownership chain
by reading `.owner`, `.owning_related_element`, and `.name` attributes via duck-typing. It
has zero imports but is architecturally dependent on the syside ownership model — it is NOT
purely string manipulation despite having no import of syside classes. This violates pattern
P1 (mock-safe type checking via `SysideAdapter.is_instance()`). Accept as a deliberate
P1 exception: the function predates the pattern and remediation would require threading a
`SysideAdapter` parameter through callers. Document in the new module's docstring.

**Tier 1 total: ~334 lines, LOW risk**

---

### Tier 2: Partially SysML (extract the core, keep codegen wrapper)

> **[REFRESH 2026-07-06]** — hierarchy_resolver.py is now **742 lines** (was 575). The
> SPLIT strategy STANDS, but two facts in the decomposition box are wrong:
> - **Data models do NOT live here.** `RedefinitionData`, `MultiplicityData`, `SumTerm`,
>   `SingletonTerm`, `LocalTerm`, `HierarchyExtractionResult`, and the enum live in
>   `extraction/data_models.py` (`:237`–`:344`), not in hierarchy_resolver. The MOVES/STAYS
>   box treats them as co-located; they are not. Any push-down of the models is a
>   `data_models.py` edit.
> - **Enum name**: it is `RedefinitionType` (`data_models.py:237`), not `RedefinitionKind`.
> - **Function inventory** verified against HEAD. STANDING: `extract_redefinitions` (`:175`),
>   `extract_multiplicities` (`:252`), `_walk_aggregation_ast` (`:386`), `_unwrap_invocation`
>   (`:335`), `build_aggregation_expression` (`:523`, STAYS), `extract_design_overrides`
>   (`:209`, STAYS). NEW: `AGG_PYTHON_OPS` (`:60`), `_agg_operator_str` (`:362`),
>   `_AggregationContext` class (`:311`, stateful — note P6), `_chain_sibling_aliases_aggregation`
>   (`:63`), `_extract_single_redefinition` (`:85`), `_keep_plain_usage_override` (`:198`),
>   `_index_usage_level_retypes` (`:574`), `extract_hierarchy_data` (`:632`, top-level entry).
> - **New governance**: `AGG_PYTHON_OPS` / `_agg_operator_str` is an **INV-1 totality site**
>   (D3-8, named in `reference/19-ast-dispatch-invariant.md`) AND a TRUTH-DEBT Item 6 hygiene
>   surface. Its fires-on-shape test must move with the aggregation code (R1), and Item 6 is a
>   PUSH-DOWN gate for exactly this overlap.
> - **Wider model coupling**: `RedefinitionData`/`RedefinitionType` are now imported across
>   four layers — extraction, resolution (`input_resolver.py`, `supplied_values.py`),
>   orchestration (`pipeline_builder.py`), and snapshot (`loader.py`). Moving the models
>   multiplies the re-export surface well beyond what the original R1 row assumed.

#### hierarchy_resolver.py (575 lines) -- SPLIT

```
  MOVES (~300 ln):                       STAYS (~275 ln):
  +----------------------------+        +-------------------------------+
  | extract_redefinitions()    |        | HierarchyExtractionResult     |
  | extract_multiplicities()   |        | (codegen data model)          |
  | RedefinitionData model     |        |                               |
  | MultiplicityData model     |        | build_aggregation_            |
  | RedefinitionKind enum      |        |   expression() text output    |
  |                            |        | compiled_expression field     |
  | _walk_aggregation_ast()    |        | "count * attr" rewrite        |
  | _unwrap_invocation()       |        |                               |
  | SumTerm/SingletonTerm      |        | extract_design_overrides()    |
  | (decomposition models)     |        | (depends on OutputRegistry    |
  |                            |        |  for scoped key lookups)      |
  | "What IS the model?"       |        | "How do we GENERATE from      |
  |                            |        |  the model?"                  |
  +----------------------------+        +-------------------------------+
```

**Target**: New `agentic_mbse.sysml.hierarchy` + `agentic_mbse.sysml.aggregation` modules

**Risk**: MEDIUM -- 93 tests across C09/C10 conformance suites reference these data models,
plus ~424 tests transitively via `snapshot_loader.py`. Mitigated by keeping models as
dataclasses (not forcing Pydantic conversion) and maintaining re-exports in `data_models.py`.

> **[REFRESH 2026-07-06]** — usage_extractor.py is now **911 lines** (was 664) and the
> template-detection surface was **refactored**, so the MOVES box is stale:
> - **`_is_template_usage()` NO LONGER EXISTS** anywhere in src/ or tests/. Template handling
>   is now `_find_instantiation_paths` (`:313`, STANDING), `_create_virtual_calc_usage`
>   (`:372`, NEW), `_expand_template_calc_usages` (`:416`, NEW), backed by
>   `_build_part_usage_index` (`:272`, NEW).
> - NEW type-indexing helpers also landed here: `user_partdef_types` (`:173`),
>   `_supertype_closure` (`:197`), `most_specific` (`:221`), `user_partdef_lookup` (`:256`)
>   (covered by `test_type_indexing.py`, `test_type_mapping_consolidation.py`).
> - `BindingInfo` (dataclass) STILL at `usage_extractor.py:55` — the R3 naming-collision with
>   `agentic_mbse.sysml.types.BindingInfo` stands on the codegen side (the agentic-mbse side
>   could not be byte-verified this pass; the repo is outside the sandbox).
> - **Net**: Tier 2c (template detection) is still correctly DEFERRED, but its function
>   inventory must be re-derived from the refactored names before any epic_plan touches it.

#### usage_extractor.py (partial, ~71 lines) -- SPLIT

```
  MOVES:                                STAYS:
  +----------------------------+       +-------------------------------+
  | _is_template_usage()       |       | CalcUsageData construction    |
  | _find_instantiation_       |       | module_type, is_template,     |
  |   paths() (DFS)            |       | owning_part_def_qn fields     |
  | "Is this a template?"      |       | All codegen-specific fields   |
  +----------------------------+       +-------------------------------+
```

**Risk**: MEDIUM -- interleaved with CalcUsageData construction

#### pipeline_builder.py (partial, ~70 lines) -- SPLIT

```
  MOVES:                                STAYS:
  +----------------------------+       +-------------------------------+
  | Override index building    |       | CalcUsageData.bindings        |
  | (parent_path, leaf_attr)   |       | mutation logic                |
  | matching algorithm         |       | Pipeline context wiring       |
  | "Which redef wins?"        |       | "How does codegen use it?"    |
  +----------------------------+       +-------------------------------+
```

**Risk**: MEDIUM -- coupled to CalcUsageData binding model

**Tier 2 total: ~441 lines move, ~275 lines stay, MEDIUM risk**

---

### Tier 3: Stays in sysml-codegen (codegen-specific, does NOT move)

```
  expression_compiler.py  (619 ln)  AST -> Python source code
  extractor.py            (653 ln)  CalcDefData / PartDefData assembly
  computed_attr_extr.py   (275 ln)  FORMULA / EXPOSE classification
  constraint_extractor.py (261 ln)  Constraint block -> codegen models  <--- SEE NOTE
  constraints.py          (262 ln)  Constraint data structures
  data_models.py          (367 ln)  CalcDefData, CalcUsageData, etc.
  core/output_registry.py (194 ln)  ScopedKey, CanonicalChannel
  core/identifier_types.py(198 ln)  EQN, PQN typed identifiers

  TOTAL: ~2,829 lines -- ALL codegen-coupled, zero ambiguity
```

> **[REFRESH 2026-07-06]** — the Tier 3 table is **stale on constraints**:
> - **`constraint_extractor.py` (261 ln) and `constraints.py` (262 ln) NO LONGER EXIST.**
>   `ConstraintData` is gone. The successor is `extraction/constraint_report.py` (**176 ln**,
>   NEW): a manifest/report renderer (`ConstraintManifestEntry`, `render_constraint_report`,
>   `manifest_to_records` / `manifest_from_records`). This is a **codegen reporting artifact,
>   not a SysML-general extractor** — it does NOT belong in the push-down set.
> - **R7 is void.** The "constraint_extractor is a missed Tier 1 candidate" risk points at a
>   file that no longer exists and a successor that is codegen-specific. Strike R7 at epic_plan.
> - Other Tier 3 line counts drifted: `extractor.py` 653→**798**, `computed_attr_extr.py`
>   275→**351**, `expression_compiler.py` 619→**618** (stable), `data_models.py` 367→**379**,
>   `core/output_registry.py` 194→**266**, `core/identifier_types.py` 198→**215**. The Tier 3
>   *conclusion* (all codegen-coupled, stays) is unchanged; only the numbers moved.
> - **`expression_compiler._sanitize_name` STANDING** at `expression_compiler.py:167` (doc
>   said 167-184). No `# INTENTIONAL DIVERGENCE` comment present yet, so the R8 pre-flight is
>   still open, not done.

**NOTE on `constraint_extractor.py`**: This file is more purely SysML than its Tier 3
placement suggests. It imports only `SysideAdapter` from agentic-mbse and
`reconstruct_expression` from `expression_utils`. Its `ConstraintData` dataclass contains
only generic SysML fields (name, expression text, doc_comment, owner_name). Once Phase 1
moves `reconstruct_expression` to agentic-mbse, `constraint_extractor.py` would have zero
sysml-codegen dependencies — making it a natural Tier 1 candidate for a future phase.
Not included in this plan because there is no second consumer yet, but it should be first
in line when one appears.

---

## New Modules Since 2026-02-20 (do they change the boundary?) — [REFRESH 2026-07-06]

Two modules landed after this doc was written. Neither is in the push-down set, but both
affect the boundary analysis:

- **`extraction/constraint_report.py` (176 ln)** — the successor to the deleted
  `constraint_extractor.py`. Codegen reporting/manifest, **stays**. Answers a new open
  question directly: *no*, it does not belong in the push-down set.

- **`resolution/supplied_values.py` (302 ln)** — NEW resolution-layer module
  (`materialize_supplied_values`, `_match_override`, `_resolve_value`, `_binding_target`). It
  consumes `RedefinitionData` / `RedefinitionType` and materializes design/override values for
  entry points. It lives in `resolution/`, **outside** the `extraction/` push-down scope, so
  it does not move. But it matters for two reasons:
  1. It **deepens the codegen coupling of `extract_design_overrides`** — the doc already keeps
     that function in sysml-codegen (STAYS), and supplied_values is now a downstream consumer
     of the same design-override data. Reinforces the "STAYS" call.
  2. It is a **fourth importer** of the hierarchy data models (with graph_builder,
     pipeline_builder, input_resolver), widening the re-export surface if the models push down.

  Does supplied_values change what "codegen-specific" means for hierarchy code? **No** — it
  confirms the existing line. The SysML-general half of hierarchy_resolver (what a redefinition
  *is*) is still general; the design-override *materialization* is codegen resolution, now with
  a dedicated module proving the point.

- **`resolution/input_resolver.py` (279 ln)** — the `AGG_STRATEGIES` consolidation. Not new to
  this pass, but it is the TRUTH-DEBT Item 1 (F4 cutover) surface and the "consolidation
  PUSH-DOWN cares about" the epic's sequencing ruling names. Its aggregation-resolution path is
  in flux until Item 1 lands — another reason for the gate.

---

## Target State: After Push-Down

```
┌──────────────────────────────────────────────────────────────────────────┐
│                          sysml-codegen                                    │
│                                                                          │
│  generation/ --> resolution/ --> analysis/ --> orchestration/             │
│       |               |              |              |                     │
│       +---------------+--------------+--------------+                    │
│                          |                                               │
│  +-----------------------------------------------+                      │
│  | extraction/ (CODEGEN-ONLY after push-down)     |                      │
│  |                                                |                      │
│  |  extractor.py ---------- CalcDefData assembly  |                      │
│  |  usage_extractor.py ---- CalcUsageData + fields|                      │
│  |  expression_compiler.py  AST -> Python exprs   |                      │
│  |  computed_attr_extr.py - FORMULA/EXPOSE classif |                      │
│  |  constraint_extractor.py Constraint -> codegen |                      │
│  |  data_models.py -------- All codegen data cls  |                      │
│  |  hierarchy_resolver.py - THIN WRAPPER:         |                      │
│  |                          calls agentic-mbse,   |                      │
│  |                          adapts to codegen     |                      │
│  |                                                |                      │
│  |  ~2,600 lines (down from ~3,877)               |                      │
│  +-----------------------------------------------+                      │
│                                                                          │
│  core/ (UNCHANGED -- zero impact)                                        │
│  +-----------------------------------------------+                      │
│  |  output_registry, identifier_types, models     |                      │
│  |  qualified_names.py -> RE-EXPORT from          |                      │
│  |                        agentic-mbse            |                      │
│  +-----------------------------------------------+                      │
│                                                                          │
|- - - - - - - - - - - PACKAGE BOUNDARY - - - - - - - - - - - - - - - - - |
│                                                                          │
│  +-----------------------------------------------+                      │
│  |              agentic-mbse/sysml/               |                      │
│  |                                                |                      │
│  |  EXISTING (unchanged):                         |                      │
│  |  +- syside_adapter.py   (302 ln)              |                      │
│  |  +- types.py            (273 ln)              |                      │
│  |  +- binding.py          (264 ln)              |                      │
│  |  +- data_models.py       (39 ln)              |                      │
│  |  +- graph.py            (132 ln)              |                      │
│  |  +- helpers.py          (136 ln)              |                      │
│  |                                                |                      │
│  |  NEW (from push-down):                         |                      │
│  |  +- expression.py       (712 ln) EXTENDED:    |                      │
│  |  |    + reconstruct_expression()              |                      │
│  |  |    + extract_literal_value()               |                      │
│  |  |    + extract_feature_chain_name()          |                      │
│  |  |    (was 510 lines, +202 from push-down)    |                      │
│  |  |                                             |                      │
│  |  +- qualified_names.py  (134 ln) NEW:         |                      │
│  |  |    sanitize_name()                         |                      │
│  |  |    build_element_qualified_name()          |                      │
│  |  |    sysml_to_python_qualified_name()        |                      │
│  |  |    python_to_sysml_qualified_name()        |                      │
│  |  |                                             |                      │
│  |  +- hierarchy.py        (300 ln) NEW:         |                      │
│  |  |    extract_redefinitions()                  |                      │
│  |  |    extract_multiplicities()                 |                      │
│  |  |    RedefinitionData, MultiplicityData       |                      │
│  |  |    RedefinitionKind enum                    |                      │
│  |  |                                             |                      │
│  |  +- aggregation.py      (100 ln) NEW:         |                      │
│  |       _walk_aggregation_ast()                  |                      │
│  |       SumTerm, SingletonTerm, LocalTerm        |                      │
│  |       (decomposition only, no text rewrite)    |                      │
│  |                                                |                      │
│  |  TOTAL: ~2,430 lines (up from ~1,700)          |                      │
│  +-----------------------------------------------+                      │
└──────────────────────────────────────────────────────────────────────────┘
```

After the push-down, each package answers a clean question:

| Package | Answers |
|---------|---------|
| **agentic-mbse/sysml/** | "What does this SysML model **mean**?" -- elements, expressions, hierarchy, names |
| **sysml-codegen/extraction/** | "How do we **transform** it for code generation?" -- CalcDefData, CalcUsageData, FORMULA, Python compilation |

---

## Blast Radius Analysis

> **[REFRESH 2026-07-06]** — read before trusting any number in this section.
> - **The R1 mechanism changed.** `tests/helpers/snapshot_loader.py` — the test helper the
>   whole "~424 tests transitive" argument rests on — **no longer exists**. Snapshot loading is
>   now a **production module**, `src/sysml_codegen/snapshot/loader.py` (format v2, hard-gated
>   by `SnapshotFormatError`, INV-2). The hierarchy data models are imported by production code
>   (graph_builder, pipeline_builder, input_resolver, supplied_values, snapshot/loader), not by
>   a test helper. The re-export requirement in `data_models.py` **still stands**, but for
>   production-import reasons, and the "~424 tests" figure is void — recount at epic_plan.
> - **The conformance suite was restructured.** The `C09` / `C10` / `C16` suite names are gone;
>   conformance tests are now descriptively named (`test_hierarchy_resolver.py`,
>   `test_aggregation_scoping.py`, `test_virtual_binding_rewrite.py`, `test_type_indexing.py`,
>   etc.). **Every per-suite test count below (93, 79, 46, 32, ...) is STALE** and must be
>   recounted against the new files. The *shape* of the risk (which files carry it) is still
>   right; the *magnitudes* are unverified.
> - **`EXPRESSION_UTILS_PATH` shim-path risk STANDS.** Still asserted by
>   `tests/conformance/test_expression_compiler.py` and `test_ast_dispatch_invariant.py`. The
>   "shim must persist" containment note holds.
> - **Tier 1a callers are 5, not 6** (constraint_extractor deleted): computed_attribute_extractor,
>   expression_compiler, hierarchy_resolver, usage_extractor, extractor.

### Tier 1a: expression_utils -> agentic-mbse expression.py

```
  WHO CALLS IT TODAY (6 files, not 3 as originally stated):
    hierarchy_resolver.py ---- extract_feature_chain_name, extract_feature_reference_name,
                               reconstruct_expression, is_literal_expression,
                               extract_literal_value, OPERATOR_MAP
    expression_compiler.py --- extract_feature_reference_name
    extractor.py ------------- reconstruct_expression (absolute import)
    usage_extractor.py ------- is_literal_expression, extract_literal_value
    constraint_extractor.py -- reconstruct_expression (relative import)
    computed_attr_extractor.py reconstruct_expression (relative import)

  IF MOVE BREAKS:
    x 6 files need import path change (not 3)
    x 8 unit tests need direct path update
    x ~67 tests across 4 test files carry path risk if shim is later removed:
      - test_hierarchy_resolver (8 direct unit tests)
      - test_extractor (1 test asserts exact import string in source)
      - test_ast_dispatch_invariant (26 tests, uses EXPRESSION_UTILS_PATH)
      - test_expression_compiler (31 tests, uses EXPRESSION_UTILS_PATH)
    . Zero signature changes -- same functions, same args
    . Zero data model changes
    . Zero behavior changes

  CONTAINMENT: Re-export shim in old location during migration.
    The shim file MUST persist indefinitely -- conformance tests assert
    against the filesystem path and import strings. Step 4 ("optional
    cleanup") is NOT optional unless those tests are also updated.
  ROLLBACK: Move file back, delete shim. 5-minute revert.

  BLAST RADIUS: ########............  6 files  (SMALL-MEDIUM)
```

### Tier 1b: qualified_names -> agentic-mbse qualified_names.py

```
  WHO CALLS IT TODAY:
    hierarchy_resolver.py, extractor.py, usage_extractor.py,
    expression_compiler.py, constraint_extractor.py,
    computed_attribute_extractor.py, core/__init__.py,
    analysis/parameter_groups.py, orchestration/pipeline_builder.py,
    resolution/graph_builder.py

  IF MOVE BREAKS:
    x 10+ files need import path change
    . Zero signature changes -- pure string functions
    . Zero state -- no side effects possible

  CONTAINMENT: core/qualified_names.py becomes a 2-line re-export:
    from agentic_mbse.sysml.qualified_names import *
    --> ZERO import changes needed in consuming files!
  ROLLBACK: Delete new file, restore old. 2-minute revert.

  BLAST RADIUS: ....................  0 files* (NONE)
  * if using re-export pattern
```

### Tier 2a: hierarchy resolution -> agentic-mbse hierarchy.py

```
  WHO CALLS IT TODAY:
    extractor.py -------- extract_redefinitions()
    usage_extractor.py -- extract_multiplicities()
    pipeline_builder.py - RedefinitionData (type only)
    + 93 tests across C09 (46), C10 (47) conformance suites

  IF MOVE BREAKS:
    x Data models change package (RedefinitionData, MultiplicityData
      may become Pydantic from dataclass)
    x 93 conformance tests may need fixture updates
    x Serialization format could shift (dataclass -> Pydantic)

  *** CRITICAL TRANSITIVE RISK ***
    tests/helpers/snapshot_loader.py imports RedefinitionData,
    MultiplicityData, SumTerm, SingletonTerm, LocalTerm, and
    HierarchyExtractionResult from sysml_codegen.extraction.data_models.
    This helper is used by 14 test files covering ~424 tests.
    If data models move WITHOUT a re-export shim in data_models.py,
    nearly a quarter of the test suite breaks silently.

  CONTAINMENT:
    Option A: Keep as dataclass in agentic-mbse (P3 exception)   <-- RECOMMENDED
    Option B: Pydantic but with same field names -> compat
    hierarchy_resolver.py becomes thin wrapper calling
    agentic-mbse functions and adapting to codegen models.

    REQUIRED: extraction/data_models.py MUST keep re-exports for ALL
    moved models indefinitely (not just during migration). The
    snapshot_loader transitive dependency makes this a permanent
    constraint unless all 14 test files are also updated.

  ROLLBACK: Harder -- need to undo data model migration.

  BLAST RADIUS: ############........  3 files + 93 tests direct,
                                      ~424 tests transitive (MEDIUM-HIGH)
```

### Tier 2b: aggregation decomposition

```
  WHO CALLS IT TODAY:
    hierarchy_resolver.py -- build_aggregation_expression()
    + 79 tests across C10 (47), C16 (32) conformance suites

  IF MOVE BREAKS:
    x SumTerm/SingletonTerm/LocalTerm models change package
    x Aggregation tests need import updates
    x snapshot_loader.py also imports SumTerm, SingletonTerm, LocalTerm
      (same transitive risk as Tier 2a -- covered by data_models re-exports)

  CONTAINMENT: hierarchy_resolver.py keeps the text rewrite layer
    ("count * attr"), calls agentic-mbse for raw decomposition only.
  ROLLBACK: Merge aggregation back into hierarchy_resolver. 15-min revert.

  BLAST RADIUS: ############........  1 file + 79 tests direct,
                                      ~424 tests transitive (MEDIUM)
```

### Tier 2c: template detection + virtual binding

```
  WHO CALLS IT TODAY:
    usage_extractor.py -- _is_template_usage(), _find_instantiation_paths()
    pipeline_builder.py -- _rewrite_virtual_bindings()
    + 32 dedicated unit tests (template_detection=26, rewrite=6)
    + 46 C09 conformance tests exercise rewrite end-to-end

  IF MOVE BREAKS:
    x Interleaved with CalcUsageData construction
    x Coupled to sysml-codegen's binding data model
    x 32 unit tests + 46 conformance tests

  BLAST RADIUS: ################....  Most coupled (HIGH)
```

---

## Risk / Reuse Quadrant

```
                     HIGH REUSE VALUE
                          |
       +------------------+---------------------------+
       |                  |                            |
       |   DO FIRST       |     DO (carefully)         |
       |                  |                            |
       |   Tier 1a        |     Tier 2a                |
       |   expression     |     hierarchy              |
       |   reconstruction |     redefinition +         |
       |   (201 lines)    |     multiplicity           |
       |                  |     (300 lines)            |
       |   Tier 1b        |                            |
       |   qualified      |     Tier 2b                |
       |   names          |     aggregation            |
       |   (133 lines)    |     decomposition          |
       |                  |     (100 lines)            |
  LOW  ------------------+------------------------  HIGH
  RISK                    |                         RISK
       |                  |                            |
       |                  |     DEFER                  |
       |                  |                            |
       |                  |     Tier 2c                |
       |                  |     template detection     |
       |                  |     virtual binding        |
       |                  |     (141 lines)            |
       |                  |                            |
       |                  |     Too coupled to         |
       |                  |     CalcUsageData today    |
       |                  |                            |
       +------------------+---------------------------+
                          |
                     LOW REUSE VALUE
```

---

## Import Graph: Before vs After

### Before (today)

```
  sysml-codegen extraction/                     agentic-mbse/sysml/
  +----------------------+                      +------------------+
  | hierarchy_resolver   |---SysideAdapter----->| syside_adapter   |
  |  (SysML + codegen)   |                      |                  |
  | expression_utils     |---SysideAdapter----->| expression       |
  |  (pure SysML)        |                      |  (traverse only) |
  | expression_compiler  |---SysideAdapter+---->|                  |
  |  (codegen-specific)  |   refs               | types            |
  | extractor            |---SysideAdapter----->| binding          |
  | usage_extractor      |---SysideAdapter+---->| helpers          |
  |                      |   types              |                  |
  | computed_attr_extr   |---SysideAdapter+---->|                  |
  |                      |   refs               |                  |
  | constraint_extr      |---SysideAdapter----->|                  |
  +----------------------+                      +------------------+

  9 cross-boundary arrows. Mixed concerns in extraction/.
```

### After (Phase 1+2 complete)

```
  sysml-codegen extraction/                     agentic-mbse/sysml/
  +----------------------+                      +------------------+
  | hierarchy_resolver   |--wrapper calls------>| hierarchy     NEW|
  |  (codegen wrapper)   |                      |  extract_redefs  |
  |                      |                      |  extract_mults   |
  | expression_compiler  |---SysideAdapter+---->|                  |
  |  (codegen-specific)  |   refs               | expression   EXT|
  |                      |                      |  + reconstruct() |
  | extractor            |---SysideAdapter----->|  + literal_val() |
  |                      |                      |                  |
  | usage_extractor      |---SysideAdapter+---->| qualified_   NEW|
  |                      |   types              |   names          |
  | computed_attr_extr   |---SysideAdapter+---->|                  |
  |                      |   refs               | aggregation  NEW|
  | constraint_extr      |---SysideAdapter----->|                  |
  +----------------------+                      | syside_adapter   |
                                                | types, binding   |
  core/qualified_names.py --re-export---------->| helpers, graph   |
                                                +------------------+

  7 cross-boundary arrows.
  ALL extraction/ files are now codegen-specific.
  No mixed concerns.
```

---

## Execution Plan

> **[REFRESH 2026-07-06]** — the phase *ordering* stands, but five constraints that did not
> exist on 2026-02-20 now bind every phase. Fold these in at epic_plan:
>
> 1. **Gate: TRUTH-DEBT Items 1, 2, 6 land first.** Not optional. Item 1 finalizes the
>    aggregation-resolution path (`input_resolver.py`), Item 2 changes
>    `extract_feature_chain_segments` (a Phase-1 move target), Item 6 hardens loader /
>    aggregation-compile silent sites (Phase-1/2 move targets). Moving before they land moves
>    code that is about to change. (`epic_truth_debt.md`, "Sequencing Rulings".)
> 2. **TYPE_MAP pre-mapping step (new Phase-0).** Before any code that calls
>    `SysideAdapter.is_instance("TypeName")` moves into agentic-mbse, the type names must be in
>    the adapter's `TYPE_MAP` whitelist — the adapter now **hard-errors** on unknown names.
>    Enumerate the type-name literals in each moving function and confirm the whitelist first.
>    (Orchestrator-verified 2026-07-06 against the `pipeline-truth-item4` checkout: the hard-error
>    contract is live — `_get_type_map` + ValueError-on-unmapped at `syside_adapter.py:156/296`,
>    `EXCLUDED_CONSTRAINT_TYPES = ("RequirementUsage",)` single-sourced at `:43`. Also verified:
>    the second `BindingInfo` exists at `agentic_mbse/sysml/types.py:189` — the dataclass
>    reconciliation in the move plan is a real task, not a stale suspicion. Re-confirm only if
>    the companion PR has not merged by pickup.)
> 3. **Invariant-test migration (R1).** The moving code carries INV-1 sites
>    (`reconstruct_operator_expression` dispatch, `AGG_PYTHON_OPS`) and the INV-5 site
>    (`sanitize_name`). Their fires-on-shape + silent-on-clean tests move **with** the code,
>    cross-repo — they cannot be left pointing at a shimmed path.
> 4. **Per-move branch-parking.** Editable installs mean a half-migrated agentic-mbse breaks
>    the sysml-codegen suite instantly (memory `orchestrated-run-gotchas`). Each move is: land
>    in agentic-mbse on a branch → re-export in sysml-codegen → green suite → merge, never
>    leaving the pair half-done between sessions.
> 5. **v2 capture discipline.** Any baseline churn runs through `scripts/capture_*.py` with the
>    `--fixtures` selective-capture byte-identity gate (memory `byte-identity-captured-at-churn`);
>    snapshots are format v2 and the loader hard-gates the version.
>
> **Phase-specific:** Phase 1 Step-2's re-export target for qualified_names must be the
> **general subset only** (see the qualified_names callout) — the codegen name builders stay,
> so this is a split, not a whole-file re-export.

### Phase 1: Do Now (LOW risk, HIGH value) -- ~334 lines

| # | Move | Lines | Blast radius | Rollback |
|---|------|-------|-------------|----------|
| 1 | `expression_utils.py` functions -> extend `agentic_mbse.sysml.expression` | ~200 | 6 files (or 0 with shim) | 5 min |
| 2 | `core/qualified_names.py` -> new `agentic_mbse.sysml.qualified_names` | ~133 | 0 files (re-export in core/) | 2 min |

**Migration strategy**:
- Step 1: Copy functions into agentic-mbse, add tests there (mock-based, no JVM)
  - **Rename `is_literal_expression()` to `is_literal_node()`** to avoid collision with
    the existing `is_literal_expression()` in agentic-mbse `expression.py` (different
    semantics — structural type check vs feature-ref-count check)
  - **Fold `binding._extract_literal_value()`** into the new public
    `expression.extract_literal_value()` — these are functionally identical. Update
    `binding.py` to call the public version instead of its private copy.
  - Add explicit docstring cross-references between `extract_feature_chain_name()` (dotted
    path: `"instance.attr"`) and existing `get_reference_name()` (terminal: `"attr"`)
- Step 2: In sysml-codegen, replace implementations with re-exports.
  - The `expression_utils.py` shim file MUST persist — conformance tests
    (`test_ast_dispatch_invariant`, `test_expression_compiler`) assert against its
    filesystem path. Step 4 cannot proceed without updating those tests first.
- Step 3: Run full test suite (1821 tests) -- expect zero failures
- Step 4: In a later PR, update import paths in sysml-codegen to point directly to
  agentic-mbse. **Not optional-cleanup** — requires updating 4 test files (~67 tests)
  that reference `EXPRESSION_UTILS_PATH` or assert exact import strings. Do this only
  when ready to commit to the path change.

**Why this is safe**: Pure functions. No state, no data models, no Pydantic-vs-dataclass
debate. The re-export pattern means zero import changes in sysml-codegen. If anything goes
wrong, copy a file back.

### Phase 2: Do Next (MEDIUM risk, HIGH value) -- ~400 lines

| # | Move | Lines | Blast radius | Key risk |
|---|------|-------|-------------|----------|
| 3 | `RedefinitionData` + `extract_redefinitions()` -> `hierarchy.py` | ~200 | 93 direct + ~424 transitive | Serialization format, snapshot_loader |
| 4 | `MultiplicityData` + `extract_multiplicities()` -> `hierarchy.py` | ~100 | Same tests | Same |
| 5 | Aggregation decomposition core -> `aggregation.py` | ~100 | 79 direct + ~424 transitive | Stateful AST walk, snapshot_loader |

**Key decision**: Keep `RedefinitionData` and `MultiplicityData` as **dataclasses** in
agentic-mbse (not Pydantic). This is an explicit exception to pattern P3 from the research.
Rationale: avoiding serialization format changes eliminates the largest risk factor. The
existing `AttributeInfo` in agentic-mbse is already a dataclass, so there is precedent.

**Migration strategy**:
- Step 1: Create `agentic_mbse.sysml.hierarchy` with data models + extraction functions
- Step 2: Create `agentic_mbse.sysml.aggregation` with decomposition models + walk
- Step 3: `hierarchy_resolver.py` becomes thin wrapper:
  - Calls `agentic_mbse.sysml.hierarchy.extract_redefinitions()` for raw data
  - Adapts results into `HierarchyExtractionResult` (codegen model stays)
  - Calls `agentic_mbse.sysml.aggregation.decompose()` for raw terms
  - Applies codegen-specific text rewrite ("count * attr") locally
- Step 4: Add re-exports in `extraction/data_models.py` for ALL moved models:
  ```python
  # Re-exports for backward compatibility (snapshot_loader + 14 test files)
  from agentic_mbse.sysml.hierarchy import RedefinitionData, MultiplicityData, RedefinitionType
  from agentic_mbse.sysml.aggregation import SumTerm, SingletonTerm, LocalTerm
  ```
  These re-exports are **permanent** — `tests/helpers/snapshot_loader.py` is imported by
  14 test files (~424 tests). Removing these re-exports requires updating snapshot_loader
  and all its consumers first.
- Step 5: Run full test suite (1821 tests) -- expect zero failures if dataclass fields match

**Pre-flight for Phase 2**: Before starting, add a comment to `expression_compiler.py`'s
private `_sanitize_name()` (lines 167-184) documenting its intentional divergence from
`qualified_names.sanitize_name()` (omits reserved-word suffixing). This prevents someone
from "deduplicating" these during the push-down and breaking expression compilation.

### Phase 3: Defer -- ~141 lines

Template detection (`_is_template_usage()`, `_find_instantiation_paths()`) and virtual
binding matching (`_rewrite_virtual_bindings()` override index) are **high-value but
high-coupling**. The functions are interleaved with `CalcUsageData` construction.

**Wait until**: A second consumer of agentic-mbse actually needs template detection. Then
the right abstraction will be obvious from real usage rather than speculation.

---

## Patterns to Enforce in New Modules

Six patterns from the research that apply to all new agentic-mbse code:

| # | Pattern | Rule |
|---|---------|------|
| P1 | Mock-safe type checking | Use `SysideAdapter.is_instance(elem, "TypeName")`, never `isinstance()` |
| P2 | Standard library filtering | Accept `ignore_std_lib=True` as default in expression analysis |
| P3 | Pydantic for new data models | Exception: pushed-down dataclasses keep their format |
| P4 | AST field exclusion | `expression_ast: Any = Field(default=None, exclude=True)` for syside objects |
| P5 | Lazy syside imports | No module-level syside imports; all access through SysideAdapter |
| P6 | Visitor pattern for AST | Compose with `traverse_expression()` unless stateful accumulation required |

---

## Open Questions

> **[REFRESH 2026-07-06]** — dispositions against HEAD:
> - **Q1 (separator default): PARTIALLY ANSWERED.** `build_element_qualified_name` now takes
>   `use_double_underscore: bool = True` (`qualified_names.py:48`). The parameterization the
>   question asked for exists; the only remaining decision is which default agentic-mbse ships
>   (recommendation `::` still holds — flip the default, keep the param).
> - **Q4 (two `BindingInfo` classes): STANDS.** Codegen side confirmed at
>   `usage_extractor.py:55`; agentic-mbse side unverified (repo outside sandbox). Pre-flight
>   rename still recommended.
> - **Q5 (`is_literal_expression` divergence): STANDS.** Both functions still exist; the rename
>   to `is_literal_node()` on push-down is still required.
> - **Q6 (`_sanitize_name` divergence): STANDS, pre-flight NOT done.** Still at
>   `expression_compiler.py:167`; no `# INTENTIONAL DIVERGENCE` comment present.
>
> **NEW open questions raised by this refresh:**
> - **Q7. Where is the split line inside qualified_names.py?** The module is now mixed
>   (SysML-general + codegen name builders). The push-down must move only the general subset
>   and leave `get_module_name` / `get_channel_name` / `build_parameter_qualified_name` behind.
>   Design the split — a new `agentic_mbse.sysml.qualified_names` for the general functions, and
>   `core/qualified_names.py` keeps the codegen builders and re-exports the rest. Answer at design.
> - **Q8. Does `constraint_report.py` belong in the push-down set?** ANSWERED: no — codegen
>   reporting artifact, stays. (Strike R7 accordingly.)
> - **Q9. Does `supplied_values.py` change what "codegen-specific" means for hierarchy code?**
>   ANSWERED: no — it confirms the existing line (design-override *materialization* is codegen
>   resolution; what a redefinition *is* stays SysML-general). But it is a 4th importer of the
>   hierarchy data models — factor into the re-export surface for any model push-down.
> - **Q10. Adapter TYPE_MAP whitelist coverage.** Which `is_instance` type-name literals do the
>   moving functions use, and are they all whitelisted? Blocked this pass (repo outside sandbox);
>   MUST be answered before Phase 1, since the adapter hard-errors on a miss.

1. **`build_element_qualified_name()` separator default**: This function traverses
   `elem.owning_type` chains. In sysml-codegen, the default separator is `__` (ADR-003).
   In agentic-mbse, `::` (SysML native) is more appropriate. Recommendation: default to
   `::` in agentic-mbse, let sysml-codegen call `sysml_to_python_qualified_name()` after.

2. **Test migration for Phase 2**: Conformance tests in sysml-codegen use extraction
   snapshots that include hierarchy fields. Two options:
   - (A) agentic-mbse gets its own mock-based unit tests; sysml-codegen conformance
     tests remain unchanged (they test the wrapper layer)
   - (B) Some conformance tests migrate to agentic-mbse
   Recommendation: Option A -- keeps conformance tests stable, adds focused unit tests.

3. **Versioning**: Both packages are editable installs (`../agentic-mbse`). Acceptable
   for now since they change together. Long-term: consider a versioned interface contract
   if agentic-mbse gets external consumers.

4. **Two `BindingInfo` classes**: `agentic_mbse.sysml.types.BindingInfo` (Pydantic
   `BaseModel` with `binding_type`, `source_attr`, `target_attr` fields) and
   `sysml_codegen.extraction.usage_extractor.BindingInfo` (dataclass with different field
   set) share the same name but are different types. The push-down doesn't directly move
   either, but it narrows the conceptual boundary between the packages — making the
   collision more confusing over time. Recommendation: rename the sysml-codegen version
   to `ExtractedBindingInfo` (or similar) as a pre-flight cleanup before Phase 2.

5. **`is_literal_expression()` semantic divergence**: The sysml-codegen version
   (structural: `SysideAdapter.is_instance()` against 5 literal types) and the
   agentic-mbse version (semantic: `len(extract_feature_refs(expr)) == 0`) are NOT
   equivalent — a computed expression with no feature refs passes the agentic-mbse check
   but fails the sysml-codegen check. Phase 1 must rename the sysml-codegen version to
   `is_literal_node()` when pushing to avoid silent behavioral change. See Phase 1
   migration strategy Step 1.

6. **`expression_compiler._sanitize_name()` intentional divergence**: This private
   function (lines 167-184) deliberately omits reserved-word suffixing that
   `qualified_names.sanitize_name()` applies. It is imported cross-module by
   `computed_attribute_extractor.py`. Moving `sanitize_name()` to agentic-mbse creates
   a risk that someone "deduplicates" these two sanitizers. Recommendation: add a
   `# INTENTIONAL DIVERGENCE` comment to `_sanitize_name()` before Phase 1, explaining
   that it must NOT be replaced by the public version.

---

## Summary Table

> **[REFRESH 2026-07-06]** — the two tables below keep their *rows* but several cells are stale:
> - **R1** ("snapshot_loader.py transitive dependency, ~424 tests"): the mechanism changed —
>   `snapshot_loader.py` is gone, loading is now the production module `snapshot/loader.py`. The
>   re-export requirement stands; the "~424 tests" count is void (recount at epic_plan).
> - **R7** ("constraint_extractor is a missed Tier 1 candidate"): **VOID** — the file no longer
>   exists; the successor `constraint_report.py` is codegen-specific. Strike R7.
> - **R2, R5, R6, R8** stand (verified this pass where in-repo). **R3, R4** stand on the
>   codegen side; the agentic-mbse side is unverified (repo outside sandbox).
> - **Line counts in the summary** ("~200", "~133", "~300", "~100", "~261", "~71", "~70") are
>   all pre-PIPELINE-TRUTH. Current: expression reconstruction ~356 (whole file, incl. new
>   precedence helpers), qualified-names general subset only (module split, not ~181), hierarchy
>   ~742 file. The "Total moving ~875" figure is stale — re-derive from the callouts.

| What | Lines | Risk | Phase | Reuse unlocked |
|------|-------|------|-------|---------------|
| Expression reconstruction | ~200 | LOW | 1 | Any SysML tool can display expressions |
| Qualified name utilities | ~133 | LOW | 1 | Any SysML consumer can build names |
| Hierarchy resolution | ~300 | MEDIUM | 2 | Validation, docs, simulation tools |
| Aggregation decomposition | ~100 | MEDIUM | 2 | Analysis tools, constraint checkers |
| Constraint extraction | ~261 | LOW | Future | Natural Tier 1 after Phase 1 completes |
| Template detection | ~71 | HIGH | Deferred | Wait for second consumer |
| Virtual binding matching | ~70 | HIGH | Deferred | Wait for second consumer |
| **Total moving (Phase 1+2)** | **~875** | | | |
| **Stays in sysml-codegen** | **~2,829** | | | |

### Review-Identified Risks (tracked)

| # | Risk | Severity | Phase | Resolution |
|---|------|----------|-------|------------|
| R1 | `snapshot_loader.py` transitive dependency (~424 tests) | HIGH | 2 | Permanent re-exports in `data_models.py` |
| R2 | `binding._extract_literal_value` duplication | LOW | 1 | Fold into public `expression.extract_literal_value` |
| R3 | Two `BindingInfo` classes (naming collision) | LOW | Pre-2 | Rename sysml-codegen version to `ExtractedBindingInfo` |
| R4 | `build_element_qualified_name` duck-types syside AST (P1 violation) | LOW | 1 | Accept as P1 exception, document |
| R5 | `is_literal_expression` semantic divergence | MEDIUM | 1 | Rename to `is_literal_node()` on push-down |
| R6 | `extract_feature_chain_name` vs `get_reference_name` overlap | LOW | 1 | Docstring cross-references |
| R7 | `constraint_extractor.py` is a missed Tier 1 candidate | LOW | Future | Move when second consumer appears |
| R8 | `expression_compiler._sanitize_name` intentional divergence | MEDIUM | Pre-1 | Add `# INTENTIONAL DIVERGENCE` comment |
