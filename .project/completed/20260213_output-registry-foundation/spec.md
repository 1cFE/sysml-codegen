# Spec: OutputRegistry Foundation

**Status:** Complete
**Owner:** Reid Westwood
**Created:** 2026-02-13 21:57 UTC
**Complexity:** MEDIUM
**Branch:** cost-pattern

---

## Business Goals

### Why This Matters

The backtracker currently builds 5 separate indexes (`_computed_attr_index`, `_aggregation_output_index`, `_output_catalog`, `_design_attr_binding_index`, `_usage_by_name`) with incompatible key formats, bridged by a 7-strategy cascade (~200 lines, 12+ lookup attempts, 4+ format conversions). This architecture is the root cause of Bug 2 (EXPOSE_PURE two-hop failure) and a class of key-format-mismatch bugs that silently wire bindings to ENTRY_POINT instead of MODULE_OUTPUT.

The OutputRegistry is the foundational data structure that replaces all 5 indexes with a single exact-match lookup. Every subsequent item in the epic (alias producers, backtracker integration, cut-over) depends on this foundation being correct and thoroughly tested.

### Success Criteria

- [x] `ChannelAlias` Pydantic model exists with all 4 fields
- [x] `OutputRegistry` class exists with `register()`, `register_alias()`, `resolve()` methods
- [x] Key format contract validated by unit tests grounded in Spike 8 data
- [x] 4-phase registration protocol proven by phase ordering tests
- [x] Collision handling proven (refuse overwrite, log warning, keep first)
- [x] "No normalization" contract proven by negative tests
- [x] Bug 2 xfail regression test written and committed (fails now, will pass after Item 3)

### Priority

P0 -- first item in the critical-path OUTPUT-REGISTRY epic, blocking Items 2a, 2b, 3, and 4.

---

## Problem Statement

### Current State

- `ChannelAlias` does not exist. Aliases are represented as `list[str]` on `AggregationExpressionData` with no provenance tracking.
- `OutputRegistry` does not exist. Five separate indexes with incompatible key formats serve as ad-hoc output registries.
- No `_is_transitive_default()` filter exists. Transitive design attribute detection is implicit.

### Desired Outcome

A standalone, thoroughly tested `OutputRegistry` class and `ChannelAlias` data model that:
- Can register channels with multiple lookup keys per the Spike 8 key format contract
- Supports a 4-phase registration protocol with ordered dependencies
- Resolves any source_path to a canonical channel name via exact match (no normalization)
- Rejects collisions explicitly (log + keep first) instead of silently overwriting
- Provides `_is_transitive_default()` for Phase 4 alias filtering

---

## Scope

### In Scope

1. **`ChannelAlias` Pydantic BaseModel** in `core/models.py`
2. **`OutputRegistry` class** in `core/output_registry.py`
3. **`_is_transitive_default()` utility** in `core/output_registry.py`
4. **Comprehensive unit tests** in `tests/unit/test_output_registry.py`
5. **Bug 2 xfail regression test** (integration test, written before implementation)
6. **Test factory fixtures** producing synthetic data grounded in Spike 8

### Out of Scope

- Wiring the OutputRegistry into the pipeline (Item 3)
- Modifying existing extractors or the backtracker (Items 2a, 2b, 3)
- SYSML_QN normalization (proven broken by Spike 5 -- explicitly not implemented)
- Bare-name registration (proven unnecessary by Spike 4 -- explicitly not implemented)
- Expression compiler changes (none needed)

### Edge Cases & Considerations

- **Key_A collision from virtual CalcUsages**: e.g., `cost_model.total_cost` from 9 virtual CalcUsages produces 9 registrations with the same Key_A. Collision policy: first wins, one warning logged per collision.
- **Phase isolation**: Phase 2 `register_alias()` MUST fail/warn if the canonical channel hasn't been registered in Phase 1. Phase 3 resolves against Phase 1+2. Phase 4 resolves against Phase 1-3.
- **`_is_transitive_default()` edge case**: Numeric strings with dots (e.g., `"3.14"`) must NOT be classified as transitive defaults. The `float()` try/except handles this.
- **`None` default values**: `_is_transitive_default()` must handle `None` gracefully (not transitive).

---

## Requirements

### Functional Requirements

> Requirements below are from the epic Item 1 definition and design document (08_algorithm_revised.md).

1. **FR-1**: `ChannelAlias` MUST be a Pydantic `BaseModel` in `core/models.py` with fields: `alias_name: str`, `canonical_name: str`, `owning_part_qn: str`, `source: str`. All fields are scoped dotted keys (no bare names, no SYSML_QN). The `source` field tracks provenance: `"redefinition"` | `"expose_pure"` | `"design_override"`.

2. **FR-2**: `OutputRegistry` MUST be a class in `core/output_registry.py` with the following interface:
   - `register(canonical_channel: str, lookup_keys: list[str]) -> None` -- Register a channel with multiple lookup keys. MUST refuse overwrite on collision (log warning via `logging.warning()`, keep first registration).
   - `register_alias(alias: str, canonical_channel: str) -> None` -- Register an alias pointing to an existing canonical channel. MUST assert/warn if canonical channel is not already registered.
   - `resolve(source_path: str) -> str | None` -- Exact match only. No normalization, no fallback cascade. Returns canonical channel name or `None`.

3. **FR-3**: The `OutputRegistry` MUST support the Spike 8 key format contract:
   - Phase 1 CalcUsage: Key_A (`instance.output`), Key_B (EQN), Key_C (dotted hierarchy path)
   - Phase 1 Aggregation: Key_D (`part_usage.attr`), Key_E (full dotted with prefix)
   - Phase 1 FORMULA: Key_F (`owning_part.python_name`)
   - Phase 2: CHAIN aliases (resolve canonical against Key_C)
   - Phase 3: EXPOSE_PURE aliases (resolve canonical against Key_A, PartUsage-only)
   - Phase 4: Transitive design attr aliases (resolve canonical against Phase 1-3)

4. **FR-4**: `_is_transitive_default(attr)` MUST correctly identify dotted-path defaults (`"cost_model.total_cost"`) and reject numeric defaults (`"3.14"`), `None`, and non-dotted strings. Implementation: `"." in str(val)` AND `float(str(val))` raises `ValueError`.

5. **FR-5**: `resolve()` MUST return `None` for bare names (e.g., `total_cost`), SYSML_QN paths (e.g., `Namespace::Part::calc`), and any unregistered key. This validates the "no normalization" contract.

6. **FR-6**: [INFERRED] `OutputRegistry` SHOULD provide a Key_C derivation utility: `".".join(qn.split("__")[1:]) + "." + output_name`. This is used by Phase 1 CalcUsage registration and is central to Phase 2 CHAIN alias resolution.

7. **FR-7**: A Bug 2 xfail regression test MUST be written and committed as part of this item. It tests that EXPOSE_PURE `financial.total_capex` in e2e_attr_expr resolves to MODULE_OUTPUT. Marked `@pytest.mark.xfail(reason="Bug 2: EXPOSE_PURE two-hop failure")`. When Item 3 completes, the xfail is removed.

---

## Acceptance Criteria

### Core Functionality

- [x] `ChannelAlias` Pydantic BaseModel exists in `core/models.py` with all 4 fields
- [x] `OutputRegistry.register()` correctly indexes multiple keys per channel
- [x] `OutputRegistry.register()` refuses to overwrite on collision (logs warning, keeps first registration)
- [x] `OutputRegistry.register_alias()` asserts/warns if canonical channel is not registered
- [x] `OutputRegistry.resolve()` returns exact match or `None`
- [x] `is_transitive_default()` correctly identifies dotted-path defaults and rejects numeric/None defaults

### Phase Ordering

- [x] Phase 2 alias resolves only after Phase 1 canonical is registered
- [x] Phase 3 alias resolves against Phase 1+2
- [x] Phase 4 alias resolves against Phase 1-3
- [x] Phase isolation: Phase 2 `register_alias()` fails/warns if canonical channel hasn't been registered in Phase 1

### Key Format Contract (Spike 8 data)

- [x] Key_A (dotted short, e.g., `instance.output`) resolves for concrete CalcUsage outputs
- [x] Key_B (EQN) resolves for all CalcUsage outputs
- [x] Key_C (dotted hierarchy) resolves for virtual CalcUsage outputs
- [x] Key_D (`part_usage.attr`) resolves for aggregation outputs
- [x] Key_F (`owning_part.attr`) resolves for FORMULA outputs

### Negative Tests ("No Normalization" Contract)

- [x] `resolve()` returns `None` for bare names (`total_cost`)
- [x] `resolve()` returns `None` for SYSML_QN paths (`Namespace::Part::calc`)
- [x] `resolve()` returns `None` for unregistered keys

### Collision Handling

- [x] When Key_A collision occurs (e.g., `cost_model.total_cost` from 9 virtual CalcUsages), exactly one warning is logged per collision and first registration wins
- [x] Collision test verifiable via log capture

### Bug 2 Regression Test

- [x] xfail integration test exists: `test_total_capex_resolves_to_module_output()`
- [x] Test verifies `financial.total_capex` in e2e_attr_expr resolves to ENTRY_POINT (current broken behavior, xfail expects failure when it eventually resolves to MODULE_OUTPUT)

### Quality & Integration

- [x] All existing tests continue to pass (`uv run pytest tests/`)
- [x] `uv run mypy src/` passes (new code is fully typed)
- [x] `uv run ruff check src/` passes

---

## Test Fixtures (from Spike 8 data)

Factory functions in the test file (or `tests/conftest_output_registry.py`) producing representative data objects for unit testing. These are synthetic, fast, and test one class/function:

1. **1 concrete `CalcUsageData`** with 2 outputs -- validates Key_A, Key_B, Key_C registration
2. **1 virtual `CalcUsageData`** with 1 output -- validates Key_C critical path for Phase 2 CHAIN alias resolution
3. **1 `ScopedAggregationData`** with 1 alias -- validates Key_D, Key_E + alias variant registration
4. **1 FORMULA `ComputedAttributeData`** -- validates Key_F registration

### Smoke Test (real model data)

Build an `OutputRegistry` from real `solar_battery` extracted data (loaded via SysIDE), verify `resolve()` returns non-`None` for a known CHAIN binding `source_path`. This catches failures where synthetic fixtures pass but real data diverges.

---

## Deliverables

| File | Type | Description |
|------|------|-------------|
| `src/sysml_codegen/core/models.py` | Modified | Add `ChannelAlias` Pydantic BaseModel |
| `src/sysml_codegen/core/output_registry.py` | New | `OutputRegistry` class + `_is_transitive_default()` |
| `tests/unit/test_output_registry.py` | New | Comprehensive unit tests (key format, phases, collisions, negatives) |
| `tests/integration/test_bug2_regression.py` | New | Bug 2 xfail regression test |

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_output_registry_backtracker_redesign.md`
- **Design basis:** `.project/reports/08_algorithm_revised.md`
- **Reference spikes:** Spike 4 (zero bare names), Spike 5 (SYSML_QN broken), Spike 8 (key format contract, zero collisions across 250 keys)
- **Design:** `.project/active/output-registry-foundation/design.md` (to be created)

---

**Next Steps:** After approval, proceed to `/_my_design`
