# agentic-mbse Boundary Analysis: Push-Down Candidates After Refactor

**Date**: 2026-02-20
**Branch**: cost-pattern-refactor
**Scope**: Cross-package analysis of sysml-codegen extraction layer vs agentic-mbse API surface
**Trigger**: The 7-phase refactor (Phases 0-7, 1780+ tests) clarified which extraction logic is
"understanding SysML models" vs "preparing for code generation." This report investigates whether
agentic-mbse should absorb reusable SysML model analysis that currently lives in sysml-codegen.

---

## Questions

1. Does the refactor change how `agentic-mbse` should work (e.g., parsing methods, reuse)?
2. Are there new patterns to enforce in the agentic-mbse layer?

## Answers (Summary)

**Q1: Yes, selectively.** The refactor exposed a clear stratification: several chunks of logic in
`sysml-codegen/extraction/` are pure SysML model understanding — not codegen-specific — and belong
in `agentic-mbse`. But other pieces (OutputRegistry, typed identifiers, FORMULA/EXPOSE classification)
are genuinely codegen-specific and should stay.

**Q2: Yes, six patterns.** Mock-safe type checking, standard library filtering defaults, Pydantic
for data models, AST field exclusion, lazy syside imports, and visitor-pattern composition.

---

## Current State of agentic-mbse.sysml

The package provides element-level building blocks but stops before composition analysis:

| Module | What it offers |
|--------|---------------|
| `syside_adapter.py` | Lazy syside loading, `is_instance()`, `elements_of_type()`, `get_source_location()` |
| `types.py` | `BindingType`, `BindingInfo`, `CalcUsageInfo`, `ExpressionRef`, `ValidationIssue` |
| `binding.py` | `classify_binding()`, `extract_bindings()`, cross-file detection |
| `expression.py` | `traverse_expression()`, `extract_feature_refs()`, `evaluate_true_static_expression()`, `is_literal_expression()` |
| `helpers.py` | `get_calc_def_name()`, `get_document_url()`, `get_parent_part_name()` |
| `graph.py` | `detect_cycles()`, `topological_sort()` |

**Gap**: Everything about how elements **compose** — template instantiation, redefinition
resolution, aggregation decomposition, expression text reconstruction — lives entirely in
sysml-codegen. These are consumed by 11 source files across extraction/, analysis/, and
orchestration/.

---

## How sysml-codegen Consumes agentic-mbse

11 source files import from agentic-mbse (the boundary surface):

| Module | Key Imports | Purpose |
|--------|-------------|---------|
| `extraction/extractor.py` | `SysideAdapter` | Model parsing, element iteration |
| `extraction/expression_utils.py` | `SysideAdapter` | AST-to-text reconstruction |
| `extraction/expression_compiler.py` | `SysideAdapter`, `extract_feature_refs` | Expression compilation + ref extraction |
| `extraction/usage_extractor.py` | `SysideAdapter`, `BindingType`, helpers | CalcUsage extraction + binding classification |
| `extraction/hierarchy_resolver.py` | `SysideAdapter` | Redefinition, multiplicity, aggregation |
| `extraction/constraint_extractor.py` | `SysideAdapter` | Constraint block extraction |
| `extraction/computed_attribute_extractor.py` | `SysideAdapter`, `extract_feature_refs`, `ExpressionRef` | Computed attribute classification |
| `extraction/data_models.py` | `AttributeInfo`, `BindingType`, `ExpressionRef` | Data model inheritance |
| `analysis/dependency_backtracker.py` | `BindingType`, `BindingInfo` (TYPE_CHECKING) | Binding resolution |
| `analysis/parameter_groups.py` | `SysideAdapter`, `evaluate_true_static_expression`, helpers | Design attribute extraction |
| `orchestration/pipeline_builder.py` | `SysideAdapter`, `BindingType` | Pipeline orchestration |

**Key pattern**: All syside access gates through `SysideAdapter.is_instance()` — never direct
`isinstance()`. This is enforced via comment: "CRITICAL: Import syside adapter from agentic-mbse,
NOT direct syside import" (constraint_extractor.py:13).

---

## Push-Down Analysis: What Should Move

### Tier 1: Strong Candidates (pure SysML semantics, no codegen coupling)

#### 1.1 Hierarchy Resolution — Redefinition & Multiplicity Extraction

**Current location**: `sysml-codegen/extraction/hierarchy_resolver.py` (~576 lines)

**Functions**: `extract_redefinitions()`, `extract_design_overrides()`, `extract_multiplicities()`

**What it does**:
- Parses `:>>` redefinitions from PartDefs and design PartUsages
- Classifies each as LITERAL (`:>> cost = 400.0`), CHAIN (`:>> cost = subsystem.cost`),
  or EXPRESSION (`:>> total = sum(pv_module.cost)`)
- Extracts `[N]` multiplicity constraints from PartUsage children
- Data models: `RedefinitionData`, `MultiplicityData` — no codegen concepts referenced

**Why it's SysML-general**: Any SysML consumer needs to understand redefinitions. Validation,
documentation generators, simulation tools all need this. The data structures don't depend on
OutputRegistry, ComputationGraph, or TEAx concepts.

**Proposed target**: `agentic_mbse.sysml.hierarchy` module

**Risk**: Medium — needs test coverage migration. Currently tested by 38 conformance tests (C09)
and 47 aggregation scoping tests (C10) that use sysml-codegen data models.

#### 1.2 Expression Text Reconstruction

**Current location**: `sysml-codegen/extraction/expression_utils.py` (~202 lines)

**Functions**: `reconstruct_expression()`, `extract_feature_chain_name()`,
`extract_feature_reference_name()`, `extract_literal_value()`

**What it does**: Pure AST-to-text serialization of syside nodes. Dispatches on node type
(FeatureChainExpression, OperatorExpression, FeatureReferenceExpression, literals) and
reconstructs human-readable text.

**Why it's SysML-general**: agentic-mbse already has `traverse_expression()` and
`extract_feature_refs()` for analysis, but **no way to get text back from an AST node**.
This is the missing inverse operation. Not codegen-specific — any tool displaying SysML
expressions needs this.

**Proposed target**: `agentic_mbse.sysml.expression` (alongside existing traversal functions)

**Risk**: Low — already modular, minimal dependencies.

#### 1.3 Qualified Name Construction

**Current location**: `sysml-codegen/core/qualified_names.py` (134 lines)

**Functions**: `sanitize_name()`, `build_element_qualified_name(elem)`,
`sysml_to_python_qualified_name()`, `python_to_sysml_qualified_name()`

**What it does**: Traverses ownership chain to build full qualified names. Converts between
`::` (SysML) and `__` (Python-safe) separators. Sanitizes names (spaces, reserved words, Unicode).

**Why it's SysML-general**: `sanitize_name()` and `build_element_qualified_name()` are generic
SysML utilities. The `::` ↔ `__` conversion is useful beyond codegen. Currently enforced as
single source of truth: "All identifier construction MUST use these functions. Do NOT construct
qualified names via inline f-strings." (line 3-4).

**Proposed target**: `agentic_mbse.sysml.qualified_names` or extend `helpers.py`

**Risk**: Low — pure functions with no state.

### Tier 2: Partial Push-Down (extract SysML-general core, keep codegen wrapper)

#### 2.1 Aggregation Expression Decomposition

**Current location**: `hierarchy_resolver.py:305-436` (~132 lines)

**Functions**: `_walk_aggregation_ast()`, `_unwrap_invocation()`, `build_aggregation_expression()`

**What to push down**: The **detection and decomposition** layer — recognizing `sum()` calls,
resolving multiplicity, decomposing into SumTerm/SingletonTerm/LocalTerm.

**What to keep in sysml-codegen**: The **text transformation** to parametric multiply
(`count * attr`) and `compiled_expression` field — these are codegen-specific.

**Proposed target**: `agentic_mbse.sysml.aggregation` or extend `hierarchy` module

#### 2.2 Virtual Binding Rewrite Algorithm

**Current location**: `orchestration/pipeline_builder.py:_rewrite_virtual_bindings()` (~70 lines)

**What to push down**: Override index construction (keyed by `(parent_path, leaf_attr)`) and
matching algorithm. This is fundamentally about SysML semantics — design `:>>` redefinitions
override template bindings.

**What to keep in sysml-codegen**: Mutation of `CalcUsageData.bindings` — tightly coupled to
sysml-codegen's specific binding data model.

#### 2.3 Template Detection / Virtual Instantiation Path Finding

**Current location**: `usage_extractor.py:271-341` (~71 lines)

**What to push down**: Template detection (is owning type a PartDefinition?) and instantiation
path finding (recursive DFS from design root through intermediate PartDefs).

**What to keep in sysml-codegen**: `CalcUsageData` construction with codegen-specific fields
(`module_type`, `is_template`, `owning_part_def_qn`).

### Tier 3: Should Stay in sysml-codegen

| Area | Why it stays |
|------|-------------|
| **OutputRegistry + typed identifiers** (ScopedKey, CanonicalChannel, EQN, PQN) | Purely codegen — maps SysML references to TEAx channel names |
| **Computed attribute classification** (FORMULA/EXPOSE_PURE/EXPOSE_COMPUTED) | Classification driven by codegen: "generate a module or an alias?" |
| **Expression compiler** (AST → Python source, compilability assessment) | Python-specific operator mapping and compilation |
| **All generation/, analysis/, resolution/** | Consumers of extraction for code generation |
| **Two `BindingInfo` classes** (Deferred Issue #5) | Different packages, different fields, different purposes |

---

## Patterns to Enforce in agentic-mbse

Six patterns emerged from the refactor that should become hard rules:

### P1: Mock-Safe Type Checking

`SysideAdapter.is_instance()` handles both real syside objects and mocks via string-matching fallback.
All new modules MUST use `SysideAdapter.is_instance(elem, "TypeName")` — never
`isinstance(elem, syside.TypeName)` directly.

**Evidence**: All 11 consuming files in sysml-codegen follow this. The mock conftest in agentic-mbse
(`tests/test_sysml/conftest.py`) implements `MockElement.isinstance()` to match.

### P2: Standard Library Filtering as Default

`expression.py` filters `SI::`, `ISQ::`, `ScalarValues::`, `UnitsAndScales::` prefixes from
feature refs. Any new expression analysis function should accept `ignore_std_lib=True` as default.

**Rationale**: Unit annotations like `3.0 [m]` contain `SI::metre` references but must NOT count
as "dynamic expressions" per ADR-002. Consistent default prevents false positives.

### P3: Pydantic BaseModel for Data Models

agentic-mbse uses Pydantic for `BindingInfo`, `CalcUsageInfo`, `ExpressionRef`. If data models
move down from sysml-codegen (which uses dataclasses for `RedefinitionData`, `MultiplicityData`),
standardize on Pydantic `BaseModel` for serialization compatibility.

**Exception**: `AttributeInfo` is already a dataclass — maintain backward compatibility.

### P4: Expression AST Fields Excluded from Serialization

Both packages learned this the hard way: syside Java objects can't serialize.

```python
expression_ast: Any = Field(default=None, exclude=True)
```

Any field holding raw syside AST nodes MUST use `Field(exclude=True)`. This is already the pattern
in `BindingInfo.expression_ast` and `ExpressionRef.element`.

### P5: Lazy syside Import Boundary

`get_syside()` in `syside_adapter.py` is critical — allows CLI usage without a JVM license key.
No new module in `agentic_mbse.sysml` should import syside at module level. All syside access
goes through `SysideAdapter`.

### P6: Visitor-Pattern for AST Traversal

`traverse_expression(expr, visitor, max_depth=100)` is the canonical pattern. New AST analysis
functions should compose with it rather than implementing custom recursion.

**Exception**: `_walk_aggregation_ast()` needs custom recursion because it accumulates stateful
term lists — but this should be documented as an explicit deviation.

---

## Recommended Execution Order

If acting on these findings, execute in dependency order (each builds on the prior):

| # | What | Lines moved | Risk | Enables |
|---|------|-------------|------|---------|
| 1 | Expression reconstruction → `agentic_mbse.sysml.expression` | ~200 | Low | Text display for any SysML tool |
| 2 | Qualified name utilities → `agentic_mbse.sysml.qualified_names` | ~134 | Low | Name construction for any consumer |
| 3 | Hierarchy resolution → `agentic_mbse.sysml.hierarchy` | ~300 | Medium | Redefinition/multiplicity for validation, docs |
| 4 | Aggregation analysis core → `agentic_mbse.sysml.aggregation` | ~100 | Medium | sum() decomposition for analysis tools |
| 5 | Template detection + virtual binding matching | ~140 | Medium | Most coupled; do last |

**Total**: ~875 lines of SysML-general logic could move. sysml-codegen would keep thin wrappers
that adapt the returned data into codegen-specific models.

---

## What NOT to Change

- Don't move OutputRegistry or typed identifiers (ScopedKey, CanonicalChannel, EQN, PQN)
- Don't consolidate the two `BindingInfo` classes — different packages, different purposes
- Don't move expression compilation (Python-specific operator mapping)
- Don't change `SysideAdapter`'s current API surface — it's stable and well-tested
- Don't move computed attribute classification — FORMULA/EXPOSE_PURE is codegen-driven

---

## Evidence Base

### Import Audit

11 files in sysml-codegen import from agentic-mbse. Breakdown:
- `SysideAdapter`: 10 files (every extraction module + orchestration + parameter_groups)
- `BindingType`: 4 files (usage_extractor, data_models, backtracker, pipeline_builder)
- `extract_feature_refs`: 2 files (expression_compiler, computed_attribute_extractor)
- `ExpressionRef`: 2 files (data_models, computed_attribute_extractor)
- Helper functions: 2 files (usage_extractor, parameter_groups)

### Test Coverage for Push-Down Candidates

| Area | Conformance tests | Unit tests | Total |
|------|-------------------|------------|-------|
| Hierarchy resolution (C09, C10) | 85 | 12 | 97 |
| Expression utils | 0 (tested indirectly via C04, C06) | 8 | 8 |
| Qualified names (C02) | 46 | 6 | 52 |
| Aggregation decomposition (C10, C16) | 79 | 4 | 83 |
| Virtual binding rewrite (C09) | 38 | 6 | 44 |

### agentic-mbse Current Test Suite

- `tests/test_sysml/test_binding.py`: 15 tests (classify_binding, extract_bindings)
- `tests/test_sysml/test_expression.py`: 12 tests (traverse_expression, extract_feature_refs, evaluate)
- `tests/test_sysml/conftest.py`: Mock infrastructure (MockElement, MockFeatureChainExpression, etc.)
- All tests use mocks — no JVM dependency

### Code Volume

- sysml-codegen extraction/: 3,877 lines across 8 .py files
- agentic-mbse sysml/: ~800 lines across 6 .py files (adapter, types, binding, expression, helpers, graph)
- Proposed push-down: ~875 lines (~23% of extraction layer)

---

## Open Questions (for future spikes)

1. **Data model ownership**: If `RedefinitionData` and `MultiplicityData` move to agentic-mbse,
   should sysml-codegen re-export them or import directly? Current pattern is direct import
   (e.g., `from agentic_mbse.sysml.types import BindingType`).

2. **Test migration**: Conformance tests in sysml-codegen use extraction snapshots that
   include syside-specific fields. If hierarchy resolution moves down, should agentic-mbse
   have its own snapshot fixtures, or should it accept the same serialized format?

3. **Versioning coupling**: agentic-mbse is installed from `../agentic-mbse` (editable).
   If APIs move, both packages change simultaneously. Is this acceptable long-term, or
   should there be a versioned interface contract?

4. **`build_element_qualified_name()` depends on SysideAdapter**: The function traverses
   `elem.owning_type` chains, which requires duck-typed syside objects. Moving it to
   agentic-mbse means it stays close to SysideAdapter (natural fit), but the `__` separator
   default is a codegen convention. Should the function default to `::` in agentic-mbse?
