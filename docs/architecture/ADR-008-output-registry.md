# ADR-008: OutputRegistry for Binding Resolution

## Status
**Accepted** - 2026-02-15

## Context

The backtracker previously maintained five ad-hoc indexes for resolving binding source_paths to upstream module outputs: `_computed_attr_index`, `_aggregation_output_index`, `_output_catalog`, `_design_attr_binding_index`, and `_usage_by_name`. Each used a different key format. A 7-strategy cascade in `_resolve_binding_to_usage()` attempted 12+ lookup patterns across these indexes.

This design was fragile, hard to extend, and comprised ~550 lines of resolution code. Bug 2 (EXPOSE_PURE `total_capex` resolved as a false entry point instead of wiring to a module output) was a direct consequence of the cascade failing to find a valid key across incompatible indexes.

Bindings arrive in two formats:
- **DOTTED/CHAIN**: `"alpha_split.p_alpha"` -- used by `:>>` redefinition bindings
- **SYSML_QN/REFERENCE**: `"FusionPhysics::GrossEfficiency::eta"` -- used by reference bindings

The cascade tried to normalize between them, but SYSML_QN normalization (`::` to `__`) was broken: the consuming path differs from the producing path (Spike 5). Bare names were never observed across 94 bindings in 3 models (Spike 4).

## Decision

### Decision 1: Single Exact-Match Registry

Introduce `OutputRegistry` as the single lookup for binding resolution. It is a pure `dict[str, str]` mapping lookup keys to canonical channel names. `resolve(source_path)` performs exact match only -- no normalization, no `::` to `.` conversion, no bare-name fallback. If a key is not registered, `resolve()` returns `None`.

All keys are dotted format. No SYSML_QN keys are registered.

### Decision 2: 4-Phase Registration Protocol

The registry is populated in strict phase order. Each phase may only reference names from prior phases:

| Phase | Source | Canonical Channel | Lookup Keys |
|-------|--------|-------------------|-------------|
| 1 | CalcUsage outputs | `{usage_eqn}__{output_name}` | Key_A: `instance.output`, Key_B: EQN, Key_C: dotted hierarchy path |
| 1 | Aggregation outputs | `{scoped_eqn}__{attr_name}` | Key_D: `part_usage.attr`, Key_E: full dotted path |
| 1 | FORMULA outputs | `{part_eqn}__{attr}__{attr}` | Key_F: `part.attr` |
| 2 | `:>>` CHAIN aliases | resolved against Phase 1 | scoped `instance_path.attr` |
| 3 | EXPOSE_PURE aliases | resolved against Phase 1+2 | scoped `parent_part.attr` |
| 4 | Transitive design attr aliases | resolved against Phase 1-3 | `parent_part.attr_name` |

Key_C (`".".join(EQN.split("__")[1:]) + "." + output_attr_name`) is critical: all Phase 2 CHAIN aliases resolve exclusively via Key_C against virtual CalcUsage outputs (Spike 8, validated across 41 aliases in solar_battery).

### Decision 3: Collision Policy

If a key already maps to a different canonical channel, the registry logs a warning and keeps the first registration. This prevents silent mis-wiring from duplicate keys.

Phase ordering violations (aliasing to an unregistered channel) produce a warning and skip, rather than an assertion crash. This is intentional: a warning with diagnostic context is more actionable than a pipeline crash on data issues.

### Decision 4: REFERENCE Bindings Handled by Backtracker

The registry does NOT handle SYSML_QN resolution. REFERENCE bindings use a secondary resolution path in the backtracker: extract the leaf name from the `::` path, scope it to the parent part, and call `registry.resolve("{parent_part}.{leaf_name}")`. This sidesteps the broken SYSML_QN normalization entirely.

### Decision 5: Graph Builder Uses Registry

`build_computation_graph()` receives the OutputRegistry. Channel existence checks use `registry.resolve()` and `registry.canonical_channels` (O(1) set membership). The three output catalog construction functions previously duplicated in the graph builder are removed.

## Consequences

### Positive
- ~720 lines of resolution code removed (5 indexes + 7-strategy cascade)
- Bug 2 fixed: EXPOSE_PURE attributes correctly resolve via Phase 3 aliases
- O(1) resolution for all binding lookups (single dict get)
- Single source of truth for channel existence and naming
- Extensible: new output types register additional keys in Phase 1 without touching resolution logic
- Empirically validated: zero collisions across 217 keys in solar_battery and 33 keys in e2e_attr_expr

### Negative
- Phase ordering is an implicit contract enforced by warnings, not types -- a mis-ordered `build_output_registry()` call would silently drop aliases
- Registry must be built before the backtracker runs, introducing an initialization ordering dependency (Step 5.5 before Step 6)
- Secondary resolution for REFERENCE bindings still lives in the backtracker, so binding resolution is split across two components

## References

- **Algorithm spec**: `.project/reports/08_algorithm_revised.md` Section 12 -- full design and key format contract
- **ADR-003**: `docs/architecture/ADR-003-signal-identifiers.md` -- identifier taxonomy and naming conventions
- **ADR-004**: `docs/architecture/ADR-004-computed-attribute-pipeline-integration.md` -- computed attribute registration
- **Implementation**: `src/sysml_codegen/core/output_registry.py`
- **Registration**: `src/sysml_codegen/generation/initialization.py` (`build_output_registry()`)

## Changelog

| Date | Change |
|------|--------|
| 2026-02-15 | Initial version |
