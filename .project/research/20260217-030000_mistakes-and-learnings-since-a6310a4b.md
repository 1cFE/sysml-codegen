---
date: 2026-02-17T03:00:00-05:00
researcher: Claude
topic: "Mistakes and learnings since a6310a4b to inform refactored design"
tags: [research, refactor, retrospective, design-lessons]
status: complete
last_updated: 2026-02-17
---

# Research: Mistakes and Learnings Since a6310a4b

**Date**: 2026-02-17 03:00 EST
**Researcher**: Claude
**Research Type**: Retrospective / Architecture
**Scope**: 37 commits, 19 bugs, 22 design review issues, 9 empirical spikes, ~20 research reports

## Research Question

What mistakes and learnings from all work since commit a6310a4b should inform the
refactored design, and what patterns must the new design prevent?

## Summary

- **19 cataloged bugs** across 7 RCA reports; 8 of 19 (42%) are naming/resolution failures from incompatible key formats across indexes
- **22 design review issues** across 3 iterations; the core theme is key-format contracts must be defined before building resolution logic
- **9 invalidated assumptions** -- the most costly being that `expression_text` is parseable, that `::` -> `__` normalization works, and that bare names exist in bindings
- **5 hotspot files** modified 7-10 times each: `initialization.py`, `graph_builder.py`, `data_models.py`, `dependency_backtracker.py`, `cli/__init__.py` -- these are the primary refactor targets
- **3 architecture smells** recur across all bug categories: multiple name formats with no canonical form, parallel module generation code paths, and shared mutable state across pipeline phases

---

## 1. The Top 10 Lessons (Ranked by Impact on Refactored Design)

### L1: Define a canonical name type and use it everywhere
**Impact**: Eliminates 8 of 19 bugs (42%).
**Evidence**: Bugs 2, 6, 9, 11, 12, 13, 16, 19 all stem from index key format mismatches --
dotted vs `::` vs `__` vs bare vs case-normalized. The system uses at least 5 name formats
with ad-hoc conversion at each lookup site. The OutputRegistry redesign initially replicated
this problem.
**Refactor rule**: Introduce a `CanonicalName` type. Raw SysML names convert at the
extraction boundary. All downstream indexes, lookups, and registrations use only canonical form.

### L2: Probe SysIDE output formats before designing resolution logic
**Impact**: Would have prevented 7 of 22 design review issues and 3 design iterations.
**Evidence**: Spikes 1-8 each invalidated an assumption about SysIDE output. The spikes
were simple logging scripts that took hours; the design iterations they triggered took days.
Issues 1, 2, 3, 7, 9, 11, 12 all trace back to untested assumptions about parser output.
**Refactor rule**: Run format probes before writing any resolution logic. Document exact
formats with example data, not assumed formats.

### L3: One code path per concern, not one code path per module type
**Impact**: Eliminates 5 of 19 bugs (Bugs 1, 3, 14, 15 + Bug 5 partially).
**Evidence**: CalcUsage, FORMULA, and aggregation modules each have separate generation
paths in `cli/__init__.py` that duplicate type mapping, directory creation, stencil
generation, and entry point registration -- with subtle inconsistencies. Bug 3 (hardcoded
`"Float"` vs `"float"`) is a direct consequence. Bug 14 (missing aggregation compilation)
happened because the new module type didn't go through the existing compilation path.
**Refactor rule**: Single `ModuleFactory` with shared type mapping, compilation, and
output generation. Module-type-specific logic is minimal and isolated.

### L4: Entry points are a consequence of resolution, not a side effect of construction
**Impact**: Eliminates Bugs 1, 15 and the shared mutable `entry_points` dict smell.
**Evidence**: The `entry_points` dict is created early, then silently mutated as a side
effect by `_build_computed_attr_module()` and `_build_aggregation_module()`, then re-read
later. Param_groups freeze before FORMULA entry points are created (Bug 1). Multiplicity
entry points never reach param_groups (Bug 15).
**Refactor rule**: Module factory functions are pure -- they return a PipelineModule and
a list of entry points, touch nothing else. Param_groups are computed after all modules
are constructed.

### L5: The OutputRegistry is correct architecture; use it for ALL resolution
**Impact**: Eliminates the aggregation wiring failure that required 4 analysis rounds.
**Evidence**: The algorithm spec explicitly said "the OutputRegistry is NOT for aggregation
inputs" (two separate sections). This was wrong. The registry already contained the correct
mappings via Phase 1b and Phase 2. The graph builder's direct-construction approach failed
for 62 of 70 aggregation inputs. Only 8 resolved through the CHAIN redef search fallback.
**Refactor rule**: The OutputRegistry is the single resolution mechanism for all binding
types. No parallel resolution paths that bypass it.

### L6: AST type dispatch must be ordered by specificity, enforced structurally
**Impact**: Eliminates 3 of 19 bugs (Bugs 8, 10, 18) and the 28 misclassified aggregation terms.
**Evidence**: `FeatureChainExpression` is a subtype of `OperatorExpression`. `hasattr(node, "function")`
matches `FeatureReferenceExpression`, `FeatureChainExpression`, AND `InvocationExpression`.
SysIDE wraps `sum()` operands in `InvocationExpression(Evaluation)`. The same semantic
construct (`child.attribute`) produces different AST types depending on syntactic context
(inside `sum()` vs outside).
**Refactor rule**: Extract a shared `dispatch_ast_node()` with mandatory type-priority
ordering. No if/elif chains on `is_instance()` at individual call sites.

### L7: Distinguish PartDef-level from PartUsage-level processing at every stage
**Impact**: Eliminates Design Issue 21 (PartDef EXPOSE_PURE), Phase 3+4 filter requirements,
and the aggregation scoping mismatch (Bug 12).
**Evidence**: PartDefinitions are templates. Their attributes lack instance scope. Registering
PartDef-level attributes in instance-scoped indexes produces silent failures. This error
was made independently in Phase 3 (EXPOSE_PURE), Phase 4 (transitive defaults), and
aggregation scoping (name matching).
**Refactor rule**: Every extraction and registration function must explicitly handle or
filter PartDef-level data. The type system should make this distinction visible.

### L8: Test with real model outputs, not simplified synthetic data
**Impact**: Would have caught Bug 17 (the persistent EXPOSE wiring failure) and likely
prevented the 4-round aggregation investigation.
**Evidence**: Bug 17's unit test passed by coincidence with concrete instance names but
the real model produces virtual/template-expanded names. The aggregation investigation
trusted spike output without cross-referencing against SysML source. 664+ unit tests
did not catch combinatorial interactions that real models expose.
**Refactor rule**: At minimum, one integration test per model validates specific wiring
decisions for known-tricky bindings. Unit tests for resolution must use actual name
formats from the extraction pipeline.

### L9: Specify ALL methods in the design, including legacy ones kept unchanged
**Impact**: Would have prevented Design Issues 10, 13, 17, 18, 19 (5 of 22).
**Evidence**: `_resolve_to_design_attribute()`, `_get_parent_part_for_usage()`, and
`owning_part_short_name` were all referenced without specification. FORMULA synthetic
CalcUsage construction was left in a separate document. Implementers had to guess or
cross-reference.
**Refactor rule**: The design document is self-contained. Every method it references
has a specification with inputs, outputs, and algorithm.

### L10: Kill dead code paths identified by probes
**Impact**: Reduces maintenance burden and confusion risk.
**Evidence**: Spikes identified: bare-name handling in resolve(), SYSML_QN normalization,
virtual binding rewrite for bare names, Step 3.6 alias enrichment heuristic, bare-name
registration keys. Each is code that can never execute in any tested model.
**Refactor rule**: If a spike proves code can't execute, remove it immediately. Don't
keep "defensive" code for hypothetical scenarios.

---

## 2. Bug Pattern Taxonomy

### Category A: Naming/Resolution (8 of 19 bugs -- 42%)

| Bug | Key Format Mismatch | Root Cause |
|-----|---------------------|------------|
| 2 | dotted vs `::` QN | Index keyed by dotted, binding uses `::` |
| 6 | invalid Python chars | `sanitize_name()` allowlist incomplete |
| 9 | case mismatch | Dict keyed lowercase, lookup mixed-case |
| 11 | PartDef scope vs instance scope | File path from PartDef QN, not instance EQN |
| 12 | abbreviated vs full name | `site_infrastructure` vs `site_infra` |
| 13 | underlying name vs alias | `capital_cost` vs `total_capex` |
| 16 | same as 13 (composition failure) | Aggregation index + EXPOSE_PURE alias don't compose |
| 19 | bare vs dotted | LocalTerm bare name vs registry dotted key |

**Prevention**: Canonical name type, single normalization function, registry-based resolution
for all module types.

### Category B: Data Flow / Sequencing (5 of 19 bugs -- 26%)

| Bug | Missing Propagation | Root Cause |
|-----|---------------------|------------|
| 1 | Late entry points not in param_groups | Param_groups frozen before FORMULA phase |
| 3 | Type mapping bypassed | FORMULA path hardcodes `"Float"` |
| 4 | Primitive write handler not ported | Multi-output exit point pattern incomplete |
| 14 | No aggregation expression compilation | New module type skips expression compiler |
| 15 | Multiplicity entry points not surfaced | Deriver has no catch-all path |

**Prevention**: Single module factory, late-binding param_groups, required compilation phase
for all module types.

### Category C: AST Dispatch (3 of 19 bugs -- 16%)

| Bug | Dispatch Error | Root Cause |
|-----|---------------|------------|
| 8 | `Evaluation` wrapper not unwrapped | Spike didn't probe operand depth |
| 10 | Cascade from Bug 8 | `has_unsupported_nodes` blocks all generation |
| 18 | FCE before OE check ordering | Subtype matches both; generic first |

**Prevention**: Shared `dispatch_ast_node()` with type-priority ordering, wrapper
unwrapping as a standard pre-processing step.

### Category D: Architecture / Infrastructure (3 of 19 bugs -- 16%)

| Bug | Missing Infrastructure | Root Cause |
|-----|----------------------|------------|
| 5 | Smart-regen incomplete | Signature-only check misses stub detection |
| 7 | `__init__.py` missing (intermediate) | mkdir decoupled from package init |
| 7b | `__init__.py` missing (top-level) | Fix scope too narrow |

**Prevention**: Coupled directory + package init, smart-regen semantic awareness.

---

## 3. Invalidated Assumptions

| # | Assumption | Reality | Source |
|---|-----------|---------|--------|
| 1 | Bare-name source_paths exist | Zero across 94 bindings, 3 models | Spike 1 |
| 2 | `expression_text` is parseable dotted path | Raw AST text `".(component_cost)"` | Spike 3 |
| 3 | `::` -> `__` normalization works | Fails 100% of exercised cases | Spike 5 |
| 4 | All CHAIN RHS values are channel refs | 24% are CAS code literals | Spike 6 |
| 5 | OutputRegistry handles everything | Aggregation needs it but was explicitly excluded | Spike 8+ |
| 6 | 46 LocalTerms are correctly classified | 28+ are misclassified dotted refs (FCE vs FRE) | Full scope analysis |
| 7 | Phase 1 keys automatically match Phase 2+ | Virtual CalcUsage `__` keys don't match `.` aliases | Spike 8 |
| 8 | EXPOSE_PURE on PartDefs produces valid aliases | PartDef-local names lack instance scope | Spike 8 |
| 9 | `:>>` creates AttributeUsage | It creates ReferenceUsage | COST-PATTERN spike |

---

## 4. Architecture Smells That Enabled Bugs

### Smell 1: Multiple name formats, no canonical form
5 formats coexist: SysML `::`, dotted `.`, bare names, `__`-separated EQN, sanitized Python.
Each index picks its own format. Each lookup converts differently. Adding a new index
(aggregation outputs, FORMULA channels) requires finding the right format by trial and error.
**Bugs enabled**: 2, 6, 9, 11, 12, 13, 16, 19 (8 bugs).

### Smell 2: Parallel code paths for module types
CalcUsage, FORMULA, and aggregation each have:
- Separate generation functions (`_generate_modules`, `_generate_computed_attr_modules`, `_generate_aggregation_modules`)
- Separate type mapping (shared `_map_input_type` vs hardcoded `"Float"`)
- Separate directory/package init logic (4 nearly identical patterns)
- Separate resolution paths in the backtracker
**Bugs enabled**: 3, 7, 7b, 14 (4 bugs).

### Smell 3: Shared mutable state across pipeline phases
The `entry_points` dict is created in one phase, mutated as a side effect by
module construction functions, and read later by param_group derivation.
`param_groups` is frozen early, then patched by Step 6.6. The pipeline has implicit
ordering dependencies not enforced by data flow.
**Bugs enabled**: 1, 15 (2 bugs).

### Smell 4: God module `graph_builder.py`
1282 lines, 13 functions, 8 logical phases, 3 module construction paths. Each module
construction function independently reimplements "create InputSource, handle entry point
fallback, register new entry points" with subtle differences. ~216 possible interactions,
~40 tested.
**Bugs enabled**: Hard to trace specific bugs, but it's the primary source of difficulty
in reasoning about the pipeline.

### Smell 5: Resolution cascade in backtracker
`_resolve_binding_to_usage()` has 5+ strategies tried in sequence. Each handles a
different name format. Adding a new feature requires adding new strategies and ensuring
they compose with existing ones. The strategy chain is brittle and order-dependent.
**Bugs enabled**: 2, 13, 16, 17 (4 bugs).

---

## 5. Empirical Data Points That Must Not Be Forgotten

These are hard-won findings from spikes that the refactored design must preserve:

1. **Zero bare-name references** in any tested model (94 bindings, 3 models). Skip bare-name handling.
2. **Key_C is load-bearing** -- all 41 Phase 2 CHAIN aliases resolve exclusively via Key_C (dotted hierarchy path, design-prefix-stripped).
3. **`expression_text` is raw AST text**, not parseable. Use `references` field for EXPOSE_PURE.
4. **Virtual CalcUsage outputs consumed only through aggregation**, never through CHAIN bindings.
5. **SYSML_QN normalization fails 100%** of exercised cases. Don't attempt `::` -> `__` string replacement.
6. **`instance_path` includes design prefix** as first `__`-separated segment. Always strip.
7. **`:>>` creates `ReferenceUsage`, not `AttributeUsage`.**
8. **`cached_upper_bound` is N+1** (exclusive). Use `cached_lower_bound`.
9. **24% of CHAIN RHS values are string literals** (CAS codes), not channel references.
10. **`FeatureChainExpression` is a subtype of `OperatorExpression`**. Dispatch order matters.
11. **`segments[-2]` gives the correct parent** for REFERENCE secondary resolution (validated 4/4 cases).
12. **EXPOSE_PURE on PartDefs must be filtered** -- CHAIN aliases handle the same semantics.

---

## 6. Hotspot Files (from git analysis)

| File | Modifications | Role | Refactor Priority |
|------|-------------|------|-------------------|
| `generation/initialization.py` | 10 | Pipeline orchestration (860 lines) | HIGH -- move to `orchestration/` |
| `resolution/graph_builder.py` | 9 | Graph construction (1282 lines, god module) | HIGH -- decompose |
| `extraction/data_models.py` | 7 | Shared data models | MEDIUM -- stabilize with canonical types |
| `analysis/dependency_backtracker.py` | 7 | Dependency tracing | HIGH -- simplify with OutputRegistry |
| `cli/__init__.py` | 6 | Module generation | HIGH -- extract to ModuleFactory |
| `generation/stencils.py` | 4 | Stencil generation | MEDIUM |
| `extraction/usage_extractor.py` | 4 | CalcUsage extraction | LOW -- mostly stable |
| `extraction/hierarchy_resolver.py` | 4 | Hierarchy processing | MEDIUM -- fix AST dispatch |
| `extraction/expression_utils.py` | 4 | Expression reconstruction | MEDIUM -- consolidate |

**Rework indicators**: 10 commits with "fix" or "bug" in the message out of 37 total (27%).
The backtracker was modified by 7 commits spanning all 4 work phases.

---

## 7. Open Issues Carried Forward

1. **16 of 20 aggregation impls produce invalid Python** -- `.()` FeatureReferenceExpression
   syntax in singleton terms. Marked AUTO_IMPLEMENTED but not executable.
2. **EXPOSE_COMPUTED pattern deferred** -- `attribute x = calc.output * 0.95`.
3. **`agentic-mbse` V2 validation rejects valid FORMULA patterns** -- blocking upstream fix.
4. **28+ ADR references point to nonexistent documents** in sysml-codegen repo.
5. **Two BindingInfo classes** remain un-consolidated between agentic-mbse and sysml-codegen.
6. **Three expression reconstruction implementations** remain un-consolidated.
7. **Deeply-nested cross-scope REFERENCE resolution** (CalcUsage on child PartDef referencing
   grandparent aggregation) is a known limitation, not observed but not handled.
8. **`sum()` is the only recognized aggregation function** -- no `min()`, `max()`, `mean()`.

---

## 8. Recommendations for the Refactored Design

### Must-Have (prevent repeat mistakes)

1. **Canonical name type** -- single representation for all lookups (L1)
2. **Unified input resolver** with explicit strategy chain (L5)
3. **Single module factory** with shared type mapping and compilation (L3)
4. **Late-binding param_groups** computed after all modules exist (L4)
5. **Shared `dispatch_ast_node()`** with type-priority ordering (L6)
6. **PartDef/PartUsage distinction** enforced at type level (L7)
7. **Self-contained design document** with all method specs (L9)

### Should-Have (improve quality)

8. **Integration tests on real models** for wiring validation (L8)
9. **Spike-before-design** as standard workflow (L2)
10. **Dead code removal** for all probe-invalidated paths (L10)
11. **Consolidate expression reconstruction** to single implementation
12. **Consolidate BindingInfo** classes across packages

### Nice-to-Have (architectural cleanup)

13. **Move orchestration out of `generation/`** to `orchestration/`
14. **Decompose `graph_builder.py`** god module
15. **Contract tests for SysIDE AST assumptions**
16. **Composition testing** for resolution indexes

---

## Code References

- `src/sysml_codegen/generation/initialization.py` -- 860-line orchestrator, 10 modifications
- `src/sysml_codegen/resolution/graph_builder.py:1-1282` -- god module, 3 construction paths
- `src/sysml_codegen/analysis/dependency_backtracker.py` -- 5+ strategy cascade
- `src/sysml_codegen/cli/__init__.py` -- parallel generation paths with type mapping divergence
- `src/sysml_codegen/extraction/hierarchy_resolver.py` -- AST dispatch ordering bug site
- `src/sysml_codegen/extraction/expression_utils.py` -- 1 of 3 expression reconstruction impls
- `src/sysml_codegen/core/output_registry.py` -- correct architecture, under-utilized

## Intermediate Artifacts

The following files contain detailed per-investigation raw findings:
- `.project/concepts/refactor-design-intent/_intermediate_bugs.md` -- 19 bugs, full catalog
- `.project/concepts/refactor-design-intent/_intermediate_design_reviews.md` -- 22 issues, 3 rounds
- `.project/concepts/refactor-design-intent/_intermediate_registry_redesign.md` -- 9 spikes, 10 recommendations
- `.project/concepts/refactor-design-intent/_intermediate_expression_learnings.md` -- phase evolution, 8 known gaps
