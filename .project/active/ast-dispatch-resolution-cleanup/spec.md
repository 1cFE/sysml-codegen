# Spec: AST Dispatch & Resolution Route Cleanup

**Status:** Draft
**Owner:** Reid Westwood
**Created:** 2026-02-16 17:27 UTC
**Complexity:** MEDIUM
**Branch:** cost-pattern
**Prerequisite:** Aggregation Wiring Bugfix (Bug A + Bug B) must land first

---

## Business Goals

### Why This Matters

Bug A (37 misclassified aggregation inputs) was caused by getting the AST node
type-check ordering wrong in one of seven dispatch sites. A codebase investigation
found that 3 of those 7 sites have the same wrong ordering today. The bug class
is silent — wrong ordering produces plausible-looking data (LocalTerms instead of
SingletonTerms), not crashes. Any developer adding support for a new SysIDE node
type or expression pattern will face the same landmine.

Separately, the aggregation module resolution path is a parallel code path that
independently re-implements resolution strategies also used by the
CalcUsage/backtracker path. This bifurcation meant the aggregation path wasn't
covered by the OutputRegistry redesign validation (8 spikes, 3 models), and bugs
in it were missed. As the Bug B fix adds yet another resolution strategy
(LocalTerm sibling lookup) to the aggregation path, the duplication grows.

Both issues are structural. Fixing them prevents the next instance of these bug
classes rather than waiting to discover them empirically.

### Success Criteria

- [ ] All AST node type dispatch goes through a single shared mechanism that
      enforces correct ordering — no call site can get it wrong independently
- [ ] The shared dispatcher has a clean, intuitive API with good abstractions
      that is reusable across current and future AST-walking code
- [ ] Resolution logic shared between CalcUsage and aggregation paths is
      extracted into common infrastructure, reducing duplication
- [ ] Zero behavioral changes — all existing tests pass, all wiring results
      identical before and after

### Priority

P2 — tech debt cleanup. Not blocking current work, but prevents recurrence of
the bug class that caused the COST-PATTERN aggregation wiring failure.
Should be done soon after the Bug A/Bug B fixes land, before new expression
patterns are added.

---

## Problem Statement

### Current State

**AST Dispatch: 7 sites, 3 wrong.**

SysIDE's type hierarchy has a surprising property: `FeatureChainExpression` is a
subtype of `OperatorExpression`. Both `SysideAdapter.is_instance()` calls return
True on the same node. The correct dispatch order (specific before general) is
documented in the algorithm doc (Section 13), but there's no enforcement
mechanism. Each AST-walking function independently writes its own `is_instance()`
chain, and 3 of 7 get the ordering wrong:

| File | Function | Lines | Ordering | Status |
|------|----------|-------|----------|--------|
| hierarchy_resolver.py | `_extract_single_redefinition()` | 95-136 | FCE before OE | Correct |
| hierarchy_resolver.py | `_unwrap_invocation()` | 278-302 | FCE/FRE before generic | Correct |
| hierarchy_resolver.py | `_walk_aggregation_ast()` | 305-433 | OE before FCE | **Wrong** |
| expression_utils.py | `reconstruct_expression()` | 34-76 | OE before FCE/FRE | **Wrong** |
| expression_compiler.py | `build_expression_ast()` | 290-405 | OE before FCE | **Wrong** |
| usage_extractor.py | `_extract_single_binding()` | 503-571 | FCE/FRE before OE | Correct |
| parameter_groups.py | `_extract_default_value()` | 158-199 | FCE/FRE before OE | Correct |

Note: `_walk_aggregation_ast()` and `build_expression_ast()` will be fixed as
part of the immediate Bug A bugfix. After that, `reconstruct_expression()` is
the only remaining wrong site. But all 7 sites remain independently implemented,
and any new AST-walking code can reintroduce the bug.

**Resolution: two parallel paths answering the same question.**

The pipeline answers "where does this input come from?" in two independent
code paths:

| Aspect | CalcUsage Path | Aggregation Path |
|--------|---------------|-----------------|
| Entry function | `_resolve_binding_via_registry()` | `_resolve_aggregation_input_channel()` |
| File | `dependency_backtracker.py:455` | `graph_builder.py:740` |
| Strategies | registry → REFERENCE secondary → design attr → fallback | CHAIN redef → scoped registry → unscoped registry → None |
| Result type | `BindingResolution` (Pydantic model) | `str | None` (channel name) |
| Fallback | ENTRY_POINT with warning | Caller creates ENTRY_POINT |
| Verification | Trusts registry (None = not found) | Checks `canonical_channels` set |

Both use `OutputRegistry.resolve()` but construct scoped keys independently.
After Bug B lands, the aggregation path will add a third resolution site
(LocalTerm → sibling agg output lookup in `_build_aggregation_module()`).

### Desired Outcome

1. A single shared AST dispatch mechanism that enforces correct node type
   ordering. All 7 current sites and any future AST-walking code go through it.
   The mechanism MUST have a clean API / interface that is intuitive, reusable,
   and maintainable with good abstractions.

2. Shared resolution infrastructure that both paths use for common operations
   (scoped registry lookup, canonical channel verification), reducing duplication
   while preserving domain-specific resolution strategies where they genuinely
   differ.

---

## Scope

### In Scope

**Workstream 1: Shared AST Dispatcher**

- Design and implement a shared AST node dispatch mechanism
- Migrate all 7 existing dispatch sites to use it
- Ensure the mechanism makes wrong ordering impossible (not just documented)
- The API design is deferred to the design phase — the spec requires clean
  abstractions but does not prescribe the approach (tagged enum, callback
  dispatch, visitor pattern, etc.)

**Workstream 2: Resolution Route Cleanup**

- Identify and extract shared resolution utilities used by both paths
- Migrate both paths to use the shared utilities
- Include the new LocalTerm resolution logic (from Bug B fix) in the cleanup
- Two approaches should be evaluated during design:
  - **Option A: Shared utilities** — extract 1-2 common functions
    (scoped registry resolution, canonical channel verification) while keeping
    the CalcUsage and aggregation resolution paths as separate top-level
    functions with different semantics
  - **Option B: Unified resolver** — a single resolution entry point with a
    strategy pattern or configuration that handles both CalcUsage bindings and
    aggregation term resolution

**Both workstreams:**

- Unit tests for the new shared mechanisms
- Migration of all call sites with no behavioral changes

### Out of Scope

- Changes to OutputRegistry or its key registration logic
- Changes to resolution *behavior* (new strategies, new key formats, etc.)
- New SysML expression pattern support
- Architecture doc updates (Section 13, ADR-007, ADR-008) — separate follow-up
- Performance optimization
- Other models beyond those in the existing test suite

### Edge Cases & Considerations

- The shared dispatcher MUST handle the full SysIDE node type set encountered
  in practice: `FeatureChainExpression`, `FeatureReferenceExpression`,
  `OperatorExpression`, `InvocationExpression` (via `hasattr(node, "function")`),
  literal types, and unknown/unrecognized nodes
- Some dispatch sites need different behavior per node type (e.g.,
  `_walk_aggregation_ast` classifies terms while `reconstruct_expression`
  produces text). The dispatcher must support this without forcing all sites
  into the same handler signature
- The `_unwrap_invocation()` function has a different dispatch pattern (it's
  looking for terminal nodes to stop recursion, not dispatching to handlers).
  It may or may not fit the shared mechanism — design should evaluate
- `constraint_extractor.py` and `computed_attribute_extractor.py` delegate to
  `reconstruct_expression()` and `build_expression_ast()` respectively — they
  benefit transitively from fixing those functions
- For resolution cleanup, CHAIN recursive resolution (with cycle detection)
  is aggregation-specific. REFERENCE secondary resolution (leaf name + parent
  scope) is CalcUsage-specific. These domain-specific strategies SHOULD remain
  separate even if common infrastructure is extracted

---

## Requirements

### Functional Requirements

> Requirements below are from user's request unless marked [INFERRED].

1. **FR-1**: All AST node type dispatch MUST go through a single shared
   mechanism that enforces the correct ordering: `FeatureChainExpression`
   before `OperatorExpression` before generic `hasattr`-based detection.

2. **FR-2**: The shared AST dispatch mechanism MUST have a clean, intuitive
   API with good abstractions that is reusable and maintainable. The specific
   API design (tagged enum, callbacks, visitor, etc.) is deferred to the
   design phase.

3. **FR-3**: All 7 existing dispatch sites MUST be migrated to use the shared
   mechanism. No AST-walking code should contain independent `is_instance()`
   ordering chains after migration.

4. **FR-4**: [INFERRED] The shared mechanism MUST handle unknown/unrecognized
   node types explicitly (log warning + return a distinguishable result) rather
   than silently falling through.

5. **FR-5**: Shared resolution infrastructure MUST be extracted from the
   CalcUsage and aggregation resolution paths, covering at minimum: scoped
   registry key construction and resolution, and canonical channel verification.

6. **FR-6**: Both CalcUsage and aggregation resolution paths MUST be migrated
   to use the shared resolution infrastructure for their common operations.

7. **FR-7**: Domain-specific resolution strategies (CHAIN recursive for
   aggregation, REFERENCE secondary for CalcUsage) MAY remain as separate
   functions. The design phase SHOULD evaluate whether unification is
   worthwhile (Option A vs Option B per Scope section).

### Non-Functional Requirements

- All existing tests (647+) MUST continue to pass
- Zero behavioral changes — identical wiring results before and after
- [INFERRED] The shared dispatcher SHOULD be in a location importable by all
  consuming modules (e.g., `extraction/ast_dispatch.py` or `core/`)

---

## Acceptance Criteria

### Core Functionality

- [ ] A shared AST dispatch mechanism exists and enforces correct type ordering
- [ ] All 7 dispatch sites migrated — no independent `is_instance()` ordering
      chains remain in AST-walking code
- [ ] Wrong dispatch ordering is structurally impossible through the shared
      mechanism (not just documented)
- [ ] Shared resolution utilities extracted and used by both paths
- [ ] CalcUsage path produces identical `BindingResolution` results after migration
- [ ] Aggregation path produces identical wiring results after migration
- [ ] Unknown AST node types produce explicit warnings, not silent fallthrough

### Quality & Integration

- [ ] Existing tests pass (`uv run pytest tests/`)
- [ ] Unit tests for the shared AST dispatch mechanism covering: correct
      ordering, all known node types, unknown node handling
- [ ] Unit tests for shared resolution utilities
- [ ] Spike script (`scripts/spike_agg_wiring_h1_h4.py`) produces identical
      results after refactoring

---

## Related Artifacts

- **Prerequisite bugfix:** `.project/active/aggregation-wiring-bugfix/spec.md`
- **Spike results:** `.project/active/aggregation-wiring-spikes/plan.md`
- **Research (full scope):** `.project/research/20260216-001500_aggregation-wiring-full-scope-analysis.md`
- **Research (misclassification):** `.project/research/20260216-aggregation-expression-misclassification.md`
- **Algorithm doc (Section 13):** `.project/reports/08_algorithm_revised.md`
- **Design:** `.project/active/ast-dispatch-resolution-cleanup/design.md` (to be created)

---

**Next Steps:** After approval, proceed to `/_my_design` for implementation design.
