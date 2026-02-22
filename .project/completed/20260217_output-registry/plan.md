# Component: Output Registry (C08)

**Status**: DONE
**Created**: 2026-02-17
**Last updated**: 2026-02-17
**Updated by**: Plan prompt — C08 Output Registry Spike

## Source Documents

- **Checklist entry**: `COMPONENT_CHECKLIST.md` — C08
- **Design intent**: [10-output-registry.md](../../concepts/refactor-design-intent/10-output-registry.md), [27-typed-registry-refactor.md](../../concepts/refactor-design-intent/27-typed-registry-refactor.md)
- **Requirements**: REQ-OR-01 through REQ-OR-08
- **Depends on**: C01 (Data Models), C02 (Naming Conventions) — both complete

---

## 1. Assessment

### What This Component Does

The `OutputRegistry` maps reference keys (dotted paths, SysML qualified names) to canonical
channel names so that the resolver and backtracker can do O(1) lookup regardless of which
format a binding uses. It implements a 4-phase registration protocol: Phase 1 registers
canonical channels (CalcUsage, Aggregation, FORMULA outputs), Phases 2-4 register aliases
(CHAIN, EXPOSE_PURE, transitive design attributes).

### Current State

- **Exists?** Yes — `src/sysml_codegen/core/output_registry.py` (200 lines)
- **Needs extraction/refactoring?** YES — significant. The current implementation uses a
  single flat `dict[str, str]` (`_index`) with a single `resolve(str) -> str | None` method.
  The design intent specifies 3 typed registries with separate typed lookup methods:
  - `_scoped: dict[ScopedKey, CanonicalChannel]`
  - `_sysml_qn: dict[SysMLQN, CanonicalChannel]`
  - `_alias: dict[ScopedKey, CanonicalChannel]`
  - Plus `_canonical: set[CanonicalChannel]` (already exists as `set[str]`)
- **Needs new type definitions?** YES — `ScopedKey`, `CanonicalChannel`, `SysMLQN`, `EQN`, `PQN`
  are specified as `NewType` wrappers in Doc 27 but DO NOT EXIST in the codebase yet. The
  existing `core/identifier_types.py` has `SysMLQualifiedName` (dataclass), `ModuleType`,
  `PythonModulePath`, `ElementQualifiedName` — but NOT the NewType wrappers. This is the
  primary structural gap.
- **Constructor also needs refactoring**: `build_output_registry()` in
  `generation/initialization.py:502-675` currently calls `registry.register(canonical, [key_a, key_c])`
  with a flat list of keys including dead keys (Key_A, Key_D, Key_E full, Key_F, bare).
  It needs to be updated to use typed registration methods.
- **Current test coverage**: 38 tests in `tests/unit/test_output_registry_construction.py` —
  but these test the OLD API (`resolve()`, Key_A, Key_D, Key_F, bare name lookups). Many of
  these tests will need to be updated or superseded by the new conformance tests.

### Design Consistency Check

- [x] All acceptance criteria from COMPONENT_CHECKLIST are testable with real data (no mocks)
- [x] AC are consistent with the requirements in the design intent doc(s)
- [x] No contradictions with other component specs
- [x] Input/output interfaces match what upstream/downstream components expect
- [x] Any ambiguities or gaps identified and resolved (documented below)

**Issues found during review:**

1. **NewType wrappers don't exist yet (BLOCKER for typed tests, but solvable in BUILD).**
   The design docs (09, 27) specify `ScopedKey`, `CanonicalChannel`, `SysMLQN`, `EQN`, `PQN`
   as `NewType` wrappers. These are not in the codebase. They need to be created in
   `core/identifier_types.py` as part of C08 BUILD. This is consistent with the
   IMPLEMENTATION_PLAN which says "If current impl needs changes, make them" for step 2.1.

   **Resolution**: BUILD phase creates the 5 `NewType` wrappers and the `ScopedKey.from_eqn()`
   / `CanonicalChannel.from_eqn()` constructor functions. Since `NewType` produces plain
   callables (not classes), the `from_eqn` constructors will be standalone functions, not
   class methods.

2. **`ScopedKey.from_eqn()` is documented as a method but NewType doesn't support methods.**
   Doc 27 specifies `ScopedKey.from_eqn(usage_eqn, attr_name)` as a constructor. But
   `NewType('ScopedKey', str)` is just a callable — it has no methods. The current equivalent
   is `OutputRegistry.derive_key_c()` (a static method).

   **Resolution**: Create a standalone function `make_scoped_key(usage_eqn, attr_name) -> ScopedKey`
   that replaces `derive_key_c()`. Similarly, `make_canonical_channel(usage_eqn, attr_name) -> CanonicalChannel`
   replaces `get_channel_name()`. The design docs use `ScopedKey.from_eqn()` as shorthand
   for this constructor — the implementation will be a module-level function. Tests should
   use the function, not the shorthand.

3. **Downstream consumers (`_resolve_binding_via_registry` in backtracker, `graph_builder.py`)
   still call `registry.resolve()`.**
   The backtracker at `dependency_backtracker.py:481` calls `self._output_registry.resolve(source_path)`.
   The graph builder at `graph_builder.py:574,843,853` calls `output_registry.resolve(...)`.

   **Resolution**: C08 scope is the OutputRegistry class itself and its construction. Downstream
   consumers will be updated in their own component phases (C11 for backtracker, C12 for
   input resolver). For C08, the old `resolve()` method MAY be kept as deprecated during
   the transition, OR the new typed methods can be added alongside it. The SPIKE will determine
   which approach is safer.

4. **`register()` method takes a flat key list — needs split into typed registration methods.**
   The current `register(canonical, [key_a, key_c])` lumps all keys together. The new design
   splits this into `register_scoped(ScopedKey, CanonicalChannel)` and
   `register_sysml_qn(SysMLQN, CanonicalChannel)`. The existing `register_alias()` is close
   to correct but needs typed parameters.

   **Resolution**: BUILD phase replaces `register()` with 3 typed registration methods. The
   `build_output_registry()` constructor function is updated to call the typed methods and
   stop registering dead keys.

5. **AC says "No `dict[str, str]` — all registry internals use typed keys and values."**
   This means the ENTIRE internal representation changes. Since `NewType` is
   `str`-compatible at runtime, `dict[ScopedKey, CanonicalChannel]` IS `dict[str, str]` at
   runtime — the distinction is purely for mypy. Tests should verify the type annotations
   (via introspection or by confirming mypy passes), not the runtime types.

   **Resolution**: Tests verify the API contract (typed methods exist, accept typed args,
   return typed values). The `dict[str, str]` → `dict[ScopedKey, CanonicalChannel]` change is
   a type annotation change verified by mypy, not by runtime tests. Conformance tests verify
   behavior.

6. **Collision policy: AC says "Scoped and SysML QN registries: unique by construction
   (no collision policy needed)" but also "register raises on duplicate."**
   These aren't contradictory — "unique by construction" means duplicates indicate a bug,
   and "raise on duplicate" is how we catch it. Testable by attempting a duplicate registration
   and asserting it raises.

   **Resolution**: No issue — test with intentional duplicate to verify raise.

7. **Phase ordering enforcement in `register_alias()` already exists.**
   The current code checks `if canonical_channel not in self._canonical: return`.
   This is correct but needs typed parameters.

   **Resolution**: Keep the existing logic, just update parameter types.

### Risks & Unknowns

1. **Breaking downstream consumers?** If `resolve()` is removed, the backtracker and
   graph builder break. The SPIKE should determine whether to keep `resolve()` temporarily
   or update consumers in the same PR.

2. **NewType constructor functions naming**: The design docs use method-style notation
   (`ScopedKey.from_eqn()`) but NewType doesn't support methods. Need a clean naming convention
   for the constructor functions.

3. **`build_output_registry()` scope**: Does C08 also refactor `build_output_registry()`, or
   just the `OutputRegistry` class? The IMPLEMENTATION_PLAN says "If current impl needs changes,
   make them." The constructor is the most important consumer — it MUST be updated to stop
   registering dead keys and to use typed methods. But it lives in `generation/initialization.py`,
   which is shared with the orchestrator (C19). Need to limit scope to registry construction only.

---

## 2. Spike

**Decision**: SPIKE
**Rationale**: Three concrete unknowns must be answered before building:

1. The typed wrappers (`NewType`) don't exist yet. Before building the registry, we need to
   verify that `NewType` constructors work as expected with the existing key derivation
   functions (`derive_key_c`, `get_channel_name`).
2. The current `resolve()` is called by 6+ downstream sites. We need to understand the
   blast radius of removing it and decide on the migration strategy (remove, deprecate, or
   keep alongside typed lookups).
3. We need to verify that `build_output_registry()` can be refactored to use typed methods
   without breaking the 1053 existing tests.

### Spike Questions

1. **Can `NewType` wrappers be created and used with existing key derivation functions?**
   Specifically: does `ScopedKey(derive_key_c(eqn, attr))` work? Does
   `CanonicalChannel(get_channel_name(eqn, attr))` work? Are they `str`-compatible for
   dict keys?

2. **How many call sites use `registry.resolve()`?** What is the minimum set of changes
   needed to keep tests passing while the typed API is introduced?

3. **Can `build_output_registry()` be refactored to use typed registration without changing
   its signature or breaking callers?** Specifically: can we change the internal registry
   methods without changing the function's interface?

### Spike Approach

Write a small script that:
1. Creates the 5 `NewType` definitions
2. Wraps existing key derivation in typed constructors
3. Builds a typed registry from solar_battery snapshot data
4. Verifies lookups work
5. Counts all `registry.resolve()` call sites

This should take ~30 minutes and produce concrete answers.

### Spike Findings

**Q1: Can NewType wrappers work with existing key derivation?**
YES. Confirmed:
- `ScopedKey(derive_key_c(eqn, attr))` works — str-compatible, dict key compatible
- `CanonicalChannel(get_channel_name(eqn, attr))` works
- `make_scoped_key()` and `make_canonical_channel()` produce identical results to `derive_key_c()` and `get_channel_name()`
- Built typed registry from solar_battery snapshot: 56 scoped keys, 77 canonical channels, all 41 CHAIN aliases resolve via scoped registry

**Q2: How many call sites use registry.resolve()?**
8 production call sites:
- `dependency_backtracker.py`: 3 calls (lines 453, 481, 491)
- `initialization.py`: 3 calls (lines 614, 639, 659) — Phases 2-4 canonical_name resolution
- `graph_builder.py`: 2 calls (lines 574, 843/853) — EXPOSE_PURE + aggregation input resolution
- Test files: 150+ calls across 6 test files

**Q3: Can build_output_registry() be refactored without breaking?**
YES for the registry itself, but with a critical constraint:
- Canonical channel counts are IDENTICAL across all 3 tested models (77, 46, 17)
- Dead key elimination removes 98/65/34 keys (solar_battery/catf_mfe/attr_expr_probe)
- Phase 2-4 alias resolution works correctly with typed scoped lookup

**Critical finding: Backtracker dispatch is tightly coupled to Key_A**
- 4 CHAIN bindings in solar_battery resolve via Step 1 `resolve(source_path)` hitting Key_A format
- 10+ CHAIN bindings in catf_mfe resolve the same way
- 12 `minor_calc.a` bindings in catf_mfe expose Key_A collision (first-wins in old registry)
- Type-directed dispatch (scope-prepending) resolves the 4 solar_battery bindings correctly but the catf_mfe cross-package bindings need CHAIN alias lookup, not just scoping
- **Conclusion**: Backtracker dispatch update (C11) CANNOT be done in C08. The complexity is too high — catf_mfe has cross-package resolution patterns that require careful alias registry coordination.

**Migration strategy decision: KEEP `resolve()` as deprecated pass-through.**
- The deprecated `resolve()` checks: scoped → sysml_qn → alias → canonical_set (in order)
- This preserves ALL existing resolution outcomes (zero true mismatches when resolve() checks all 3 registries + canonical set)
- Downstream consumers (backtracker, graph_builder) continue using `resolve()` unchanged
- C11 (backtracker) and C12 (input resolver) will update to typed lookups in their own phases
- The `resolve()` deprecation warning should log which registry actually served the result (diagnostic aid for C11/C12 work)

### Spike Impact on Plan

1. **Build Plan change**: DO NOT update backtracker or graph_builder in C08. Keep `resolve()` as deprecated pass-through. Remove `dependency_backtracker.py` and `graph_builder.py` from Files to Modify.

2. **Build Plan change**: The `build_output_registry()` refactor in `initialization.py` CAN proceed — replace `register()` with typed methods, eliminate dead key registration. The internal resolve() calls in Phases 2-4 can use typed `scoped.get()` directly (since they resolve canonical_name, which is always a scoped key).

3. **Test Plan impact**: Tests should verify:
   - The deprecated `resolve()` still works (backward compat for C11/C12 consumers)
   - Typed lookup methods exist and return correct results
   - Dead keys are NOT registered
   - The deprecated `resolve()` returns the SAME result as typed lookup for all non-dead keys

4. **Existing unit tests**: The 38 tests in `test_output_registry_construction.py` that use `resolve()` will continue to work with the deprecated pass-through. No need to update them in C08.

5. **Scope reduction**: C08 scope is now:
   - (a) Create NewType wrappers in `identifier_types.py`
   - (b) Refactor OutputRegistry class (3 typed dicts, typed methods, deprecated resolve())
   - (c) Refactor `build_output_registry()` (typed registration, dead key elimination)
   - (d) Write conformance tests
   - NOT (e) backtracker update — deferred to C11
   - NOT (f) graph_builder update — deferred to C12

---

## 3. Test Plan

**Test file**: `tests/conformance/test_output_registry.py`
**Fixture data**: solar_battery_model, catf_mfe_model, attr_expr_probe, chain_spike_model extraction snapshots

### Test Cases

> Every requirement (REQ-OR-NN) must have at least one test case.
> Every test uses real data — no mocks. Stubs only at SysIDE adapter boundary.

| Test | Requirement | What it verifies |
|------|-------------|------------------|
| `test_req_or_01_all_reference_formats_resolve[solar_battery]` | REQ-OR-01 | Build registry from solar_battery snapshot; for each CalcUsage output, verify `scoped_lookup(ScopedKey)` returns `CanonicalChannel`; for each FORMULA, verify `sysml_qn_lookup(SysMLQN)` returns `CanonicalChannel`; for each CHAIN alias, verify `alias_lookup(ScopedKey)` returns `CanonicalChannel` |
| `test_req_or_01_all_reference_formats_resolve[catf_mfe]` | REQ-OR-01 | Same as above but with catf_mfe_model (larger model, more aliases) |
| `test_req_or_02_no_single_resolve_method` | REQ-OR-02 | Assert `OutputRegistry` has `scoped_lookup`, `sysml_qn_lookup`, `alias_lookup` methods; optionally assert no `resolve()` method (or that it's deprecated) |
| `test_req_or_02_typed_lookups_return_canonical_channel[solar_battery]` | REQ-OR-02 | Build registry from solar_battery snapshot; call each typed lookup method; verify return type is `CanonicalChannel | None` |
| `test_req_or_03_scoped_duplicate_raises` | REQ-OR-03 | Register a `ScopedKey` via `register_scoped()`; attempt to register the same key with a different channel; assert raises (ValueError or similar) |
| `test_req_or_03_sysml_qn_duplicate_raises` | REQ-OR-03 | Same for `register_sysml_qn()` — duplicate key raises |
| `test_req_or_03_alias_duplicate_warns_first_wins` | REQ-OR-03 | Register an alias; re-register same key with different channel; assert first value retained; assert warning logged |
| `test_req_or_04_alias_phase_ordering_enforced` | REQ-OR-04 | Attempt `register_alias(key, channel)` where `channel` is not yet in `_canonical`; assert alias is rejected (not registered, warning logged) |
| `test_req_or_04_alias_after_canonical_succeeds` | REQ-OR-04 | Register canonical channel via `register_scoped()`; then `register_alias()` with that channel; assert alias registered |
| `test_req_or_05_no_dead_keys_registered[solar_battery]` | REQ-OR-05 | Build registry from solar_battery snapshot using refactored `build_output_registry()`; verify Key_A format (`instance_name.attr`) NOT in scoped registry; verify Key_D, Key_E full, Key_F, bare NOT in any registry |
| `test_req_or_05_no_dead_keys_registered[catf_mfe]` | REQ-OR-05 | Same for catf_mfe — catf_mfe has the most Key_A collisions (10+), so this confirms elimination |
| `test_req_or_05_only_key_c_and_key_e_stripped_in_scoped[solar_battery]` | REQ-OR-05 | Every key in the scoped registry is either a Key_C (from CalcUsage `ScopedKey.from_eqn()`) or a Key_E_stripped (from Aggregation with design prefix stripped); verify by checking format: dotted path, no `::`, no `__` |
| `test_req_or_06_phase2_alias_resolves_through_scoped[solar_battery]` | REQ-OR-06 | Build registry from solar_battery; verify each Phase 2 CHAIN alias has its canonical resolved via scoped lookup before alias registration (check that alias_lookup returns a channel that's also reachable via scoped_lookup) |
| `test_req_or_06_phase3_alias_resolves_through_scoped[attr_expr_probe]` | REQ-OR-06 | Build registry from attr_expr_probe; verify EXPOSE_PURE aliases resolve through scoped lookup before alias registration |
| `test_req_or_07_scoped_key_from_eqn_derivation` | REQ-OR-07 | Parametrize over known EQN+attr pairs from solar_battery snapshot; verify `make_scoped_key(eqn, attr)` produces expected dotted format (design prefix stripped, joined with dots) |
| `test_req_or_07_scoped_key_matches_derive_key_c` | REQ-OR-07 | For every CalcUsage in solar_battery snapshot, verify `make_scoped_key(eqn, attr)` == `OutputRegistry.derive_key_c(eqn, attr)` (backward compatibility) |
| `test_req_or_08_key_a_not_registered[solar_battery]` | REQ-OR-08 | Build registry from solar_battery snapshot; for each CalcUsage, construct Key_A format (`instance_name.attr`); verify none of these are in any registry |
| `test_req_or_08_key_a_not_registered[catf_mfe]` | REQ-OR-08 | Same for catf_mfe (has the most Key_A collision potential) |
| `test_canonical_channels_property_returns_frozenset` | REQ-OR-01 | Verify `canonical_channels` returns `frozenset[CanonicalChannel]` with all registered canonical channels |
| `test_scoped_lookup_miss_returns_none` | REQ-OR-02 | Call `scoped_lookup(ScopedKey("nonexistent.key"))` on populated registry; assert returns `None` |
| `test_sysml_qn_lookup_miss_returns_none` | REQ-OR-02 | Call `sysml_qn_lookup(SysMLQN("NonExistent::key"))` on populated registry; assert returns `None` |
| `test_alias_lookup_miss_returns_none` | REQ-OR-02 | Call `alias_lookup(ScopedKey("nonexistent.key"))` on populated registry; assert returns `None` |
| `test_chain_alias_count_solar_battery` | REQ-OR-01 | Build from solar_battery; count Phase 2 aliases; verify == 41 (known from existing test) |
| `test_expose_pure_alias_resolves[attr_expr_probe]` | REQ-OR-06 | `alias_lookup(ScopedKey("probe_design.scale_result"))` resolves to a `CanonicalChannel` containing "scale_calc__result" |
| `test_phase4_transitive_alias[solar_battery]` | REQ-OR-06 | Build from solar_battery with design attrs; verify transitive design attr aliases registered |
| `test_registry_with_no_inputs` | REQ-OR-01 | Build empty registry; verify len=0; all lookups return None |
| `test_aggregation_key_e_stripped[solar_battery]` | REQ-OR-05 | Build from solar_battery; verify aggregation Key_E_stripped (design prefix stripped, dotted) is in scoped registry |
| `test_formula_sysml_qn_registered[attr_expr_probe]` | REQ-OR-05 | Build from attr_expr_probe; verify FORMULA SysML QN keys are in sysml_qn registry (14 keys per TRR spike) |

### Test Infrastructure Needed

1. **Helper function**: `build_registry_from_snapshot(snapshot_data)` — takes a snapshot dict
   (from `load_extraction_snapshot()`), calls the refactored `build_output_registry()`, returns
   the populated registry. This avoids duplicating construction logic in every test.

2. **The 5 `NewType` wrappers** must exist before tests can use typed parameters.
   If the spike confirms they should be created in C08 (not deferred), the BUILD phase
   creates them first.

3. **Conftest fixture**: Consider adding `output_registry_solar_battery` session-scoped fixture
   to `tests/conformance/conftest.py` or a local conftest, since many tests need the same
   populated registry.

### Gate: Ready for BUILD
- [x] Test file exists with all test cases written (32 tests in `tests/conformance/test_output_registry.py`)
- [x] Tests run: 12 passed, 20 skipped (typed API not yet created — expected)
- [x] No test uses mocking (verified: only match is docstring "no mocks")

---

## 4. Build Plan

### Files to Create

| File | Purpose |
|------|---------|
| `tests/conformance/test_output_registry.py` | Conformance tests for REQ-OR-01 through REQ-OR-08 |

### Files to Modify

| File | Change | Why |
|------|--------|-----|
| `src/sysml_codegen/core/identifier_types.py` | Add 5 `NewType` definitions: `SysMLQN`, `EQN`, `PQN`, `CanonicalChannel`, `ScopedKey`. Add constructor functions: `make_scoped_key(eqn, attr) -> ScopedKey`, `make_canonical_channel(eqn, attr) -> CanonicalChannel` | REQ-OR-07, FR-1, FR-5 — typed wrappers are prerequisite for typed registries |
| `src/sysml_codegen/core/output_registry.py` | Replace `_index: dict[str, str]` with `_scoped: dict[ScopedKey, CanonicalChannel]`, `_sysml_qn: dict[SysMLQN, CanonicalChannel]`, `_alias: dict[ScopedKey, CanonicalChannel]`. Replace `register()` with `register_scoped()`, `register_sysml_qn()`. Update `register_alias()` parameter types. Replace `resolve()` with `scoped_lookup()`, `sysml_qn_lookup()`, `alias_lookup()`. Keep `derive_key_c()` as deprecated alias for `make_scoped_key()`. Update `canonical_channels` property type. | REQ-OR-01 through REQ-OR-08 — core registry refactor |
| `src/sysml_codegen/generation/initialization.py` | Update `build_output_registry()` (lines 502-675): Phase 1a — stop registering Key_A, use `register_scoped(make_scoped_key(...), make_canonical_channel(...))`. Phase 1b — stop registering Key_D, Key_E full, bare; use `register_scoped()` for Key_E_stripped only. Phase 1c — use `register_sysml_qn()` for SysML QN; stop registering Key_F and bare. Phase 2-4 — update `register_alias()` calls to use typed params. Update `resolve()` calls to `scoped_lookup()`. | REQ-OR-05, REQ-OR-08 — eliminate dead keys, use typed registration |
| `tests/unit/test_output_registry_construction.py` | Existing tests continue to work via deprecated `resolve()` pass-through. No changes needed in C08. | Backward compat verified by deprecated resolve() |

### Implementation Notes

1. **Order of changes**: (a) Create NewType wrappers → (b) Refactor OutputRegistry class →
   (c) Update `build_output_registry()` → (d) Write conformance tests. Backtracker (C11)
   and graph_builder (C12) updates deferred — spike confirmed complexity too high for C08.

2. **`resolve()` transition strategy** (SPIKE CONFIRMED): Keep `resolve()` as a deprecated
   pass-through that checks scoped → sysml_qn → alias → canonical_set (in order). This
   preserves all existing resolution outcomes (zero true mismatches verified across 6 models).
   Log a deprecation warning with the serving registry name for diagnostic aid.

3. **`derive_key_c()` backward compatibility**: Keep as a deprecated static method that
   delegates to `make_scoped_key()`. Existing tests and references can be updated incrementally.

4. **`get_channel_name()` in `core/qualified_names.py`**: Keep it. The new
   `make_canonical_channel()` will wrap its output in the `CanonicalChannel` type. Both can
   coexist — `get_channel_name()` returns `str`, `make_canonical_channel()` returns
   `CanonicalChannel`.

5. **Dead key elimination in `build_output_registry()`**: The most impactful change.
   Phase 1a currently registers `[key_a, key_c]` — change to register only Key_C via
   `register_scoped()`. Phase 1b currently registers `[key_d, key_e, key_e_stripped, bare, ...]`
   — change to register only Key_E_stripped via `register_scoped()`. Phase 1c currently
   registers `[key_f, bare, sysml_qn]` — change to register only SysML QN via
   `register_sysml_qn()`.

6. **Backtracker NOT updated in C08** (SPIKE DECISION): The backtracker's resolution dispatch
   is tightly coupled to Key_A format. catf_mfe has 10+ cross-package CHAIN bindings that
   resolve via Key_A, and 12 `minor_calc.a` bindings expose first-wins Key_A collision
   behavior. Type-directed dispatch requires careful alias registry coordination that is C11
   scope. The deprecated `resolve()` pass-through preserves all existing outcomes.

### Gate: Ready for VALIDATE
- [x] All test cases pass (32 conformance tests, all passing)
- [x] No regressions in full test suite (`uv run pytest tests/` — 1080 passed, 0 failures)
- [x] Lint clean (`uv run ruff check src/` — all checks passed)

---

## 5. Validation

- [x] Three typed registries: scoped, SysML QN, alias — verified by `test_req_or_02_no_single_resolve_method`
- [x] No `dict[str, str]` — typed registries use `dict[ScopedKey, CanonicalChannel]` etc. — verified by type annotations
- [x] Each registry has its own typed lookup — `scoped_lookup()`, `sysml_qn_lookup()`, `alias_lookup()` — verified by test
- [x] Key_A, Key_D, Key_E full, Key_F, bare NOT in typed registries — verified by `test_no_dead_keys_registered` and `test_key_a_not_registered` (dead keys are in `_compat` only, invisible to typed lookups)
- [x] Scoped and SysML QN registries: raise on duplicate — verified by `test_scoped_duplicate_raises`, `test_sysml_qn_duplicate_raises`
- [x] Alias registry: first-wins collision policy with warning — verified by `test_alias_duplicate_warns_first_wins`
- [x] `register_alias()` enforces phase ordering — verified by `test_alias_phase_ordering_enforced`
- [x] Phase 2-4 aliases resolve before registering — verified by `test_phase2_alias_resolves_through_scoped`, `test_phase3_alias_resolves_through_registry`, `test_expose_pure_alias_resolves`, `test_phase4_transitive_alias`
- [x] `make_scoped_key()` strips design prefix, joins with dots — verified by `test_scoped_key_from_eqn_derivation` + `test_scoped_key_matches_derive_key_c`
- [x] `canonical_channels` returns `frozenset[CanonicalChannel]` — verified by `test_canonical_channels_property_returns_frozenset`
- [x] Verified with real channels from solar_battery and catf_mfe — parametrized over snapshot data
- [x] Every REQ-OR-NN has at least one passing test (REQ-OR-01 through REQ-OR-08)
- [x] Full test suite passes (1080 tests, 0 failures)
- [x] Cross-check: implementation matches design intent (3 typed registries, phase ordering, collision policies)
- [x] No unresolved TODOs or FIXMEs in new/modified code
- [x] COMPONENT_CHECKLIST and IMPLEMENTATION_PLAN have been updated

### Baseline Impact

The registry refactor separates dead keys into a `_compat` dict visible only to the deprecated
`resolve()` pass-through. The typed registries (`_scoped`, `_sysml_qn`, `_alias`) contain only
the clean keys. Total `len()` includes `_compat` so the overall key count remains similar.
No resolution outcomes change — the deprecated `resolve()` checks all registries including
`_compat`, so the backtracker and graph_builder continue working unchanged.

Channel counts are identical to pre-refactor (77 solar_battery, 46 catf_mfe, 17 attr_expr_probe).
The `_compat` dict will be removed when C11 updates the backtracker to typed dispatch.

---

## 6. Learnings

### Findings

1. **Dead key elimination requires `_compat` bridge**: The plan assumed dead keys could be
   removed from registration entirely because `resolve()` would find them through typed
   registries. In practice, dead keys (Key_A, Key_F, bare) are the primary resolution path
   for the backtracker's Step 1 `resolve(source_path)`. Removing them broke 56 tests including
   integration tests with real solar_battery data. Solution: `_compat` dict holds legacy keys
   visible only to `resolve()`, invisible to typed lookup methods.

2. **EXPOSE_PURE canonical_name is Key_A format**: Phase 3 EXPOSE_PURE aliases have
   `canonical_name` in Key_A format (`instance_name.attr`), not Key_C. The original plan
   assumed Phase 3 could use `scoped_lookup()` directly, but the canonical_name doesn't match
   Key_C format. Phase 3 now uses `resolve()` which finds Key_A via `_compat`.

3. **Phase 4 transitive defaults also need `resolve()`**: Transitive design attribute
   `default_value` fields like `"cost_model.total_cost"` are Key_A format. Phase 4 resolution
   uses `resolve()` to find these via `_compat`.

### Design Doc Updates Needed
| Doc | What to update | Why |
|-----|---------------|-----|
| 27-typed-registry-refactor.md | Add `_compat` dict to registry design; note that dead key elimination is deferred to C11 | Plan assumed dead keys have zero resolution hits but they're load-bearing through backtracker |

### Cross-Component Impact
| Component | Impact | Action needed |
|-----------|--------|---------------|
| C11 (Backtracker) | Must update to typed dispatch AND eliminate `_compat` dict | C11 conformance tests must verify resolution without `_compat` |
| C12 (Input Resolver) | Graph builder's `resolve()` calls updated to typed lookups | C12 conformance tests must use typed API |

### Deviations from Plan

1. **`_compat` dict added**: Plan specified dead key elimination. Implementation adds `_compat`
   bridge dict to preserve backward compat for backtracker. Dead keys ARE excluded from typed
   registries (conformance tests verify this) but remain accessible via deprecated `resolve()`.

2. **Phase 2-4 use `resolve()` instead of `scoped_lookup()`**: Plan specified typed lookups
   for Phases 2-4. Implementation uses deprecated `resolve()` because canonical_names and
   transitive defaults are in Key_A format, not Key_C. The typed registries ARE the source of
   truth for new code, but build-time resolution during Phase 2-4 alias registration uses the
   deprecated path for backward compat.

---

## 7. Commit

**Branch**: `cost-pattern-refactor` (current branch)
**Commit convention**: batched Phase 2 commit with all components

- [x] All validation checks above are green
- [x] Committed as part of Phase 2 batch commit (C08 + C09 + C10 + TRR + audit)
- [x] Committed successfully *(2026-02-17)*

---

## Progress Log

> Each agent context that does work on this component adds an entry here.
> This is how the next context knows where to pick up.

### Session: 2026-02-17 — Initial plan creation
**Phase**: PLANNING
**Work done**:
- Read all design docs: IMPLEMENTATION_PLAN, COMPONENT_CHECKLIST, 10-output-registry.md, 27-typed-registry-refactor.md, 09-data-models.md
- Read current source: `core/output_registry.py` (200 lines), `core/identifier_types.py` (127 lines), `generation/initialization.py:502-675` (build_output_registry)
- Read downstream consumers: `dependency_backtracker.py:462-535` (_resolve_binding_via_registry), `graph_builder.py` (6 resolve() call sites)
- Read existing unit tests: `test_output_registry_construction.py` (38 tests using old API)
- Verified: no conformance test exists yet (`tests/conformance/test_output_registry*.py` — no files found)
- Verified: snapshot fixtures available for all 6 models with all data types needed (calc_usages, calc_defs, aggregation_expressions, computed_attributes, channel_aliases, design_attributes)
- Design consistency review complete: 7 issues identified and resolved
- Decision: SPIKE needed before BUILD (3 concrete unknowns)
**Stopped at**: Plan complete, spike not yet executed
**Next step**: Execute spike (create NewType wrappers, verify they work with existing key derivation, count resolve() call sites, determine migration strategy)
**Blockers**: None — all prerequisites (C01, C02, Phase 0, Checkpoint 1) are complete

### Session: 2026-02-17 — Spike execution and TEST phase entry
**Phase**: SPIKE → TEST
**Work done**:
- Spike Q1 verified: NewType wrappers work perfectly with existing key derivation functions. `ScopedKey(derive_key_c(...))` and `CanonicalChannel(get_channel_name(...))` are str-compatible and work as dict keys. Built typed registries from solar_battery snapshot with full parity.
- Spike Q2 answered: 8 production resolve() call sites (3 backtracker, 3 initialization, 2 graph_builder), 150+ test calls across 6 test files.
- Spike Q3 verified: build_output_registry() can be refactored. Canonical channel counts identical across 3 models. Dead key elimination removes 98/65/34 keys.
- **Critical finding**: Backtracker dispatch is tightly coupled to Key_A format. 4 solar_battery CHAIN bindings + 10+ catf_mfe bindings resolve via Step 1 hitting Key_A. 12 catf_mfe `minor_calc.a` bindings expose Key_A collision (first-wins). Type-directed dispatch requires C11-level work.
- **Migration strategy decided**: Keep resolve() as deprecated pass-through (scoped → sysml_qn → alias → canonical_set). Zero true mismatches when all 4 registries are checked.
- **Scope reduced**: Removed backtracker and graph_builder from C08 Files to Modify. C08 scope is: NewType wrappers, OutputRegistry class refactor, build_output_registry() refactor, conformance tests.
- Updated plan sections: Spike Findings, Spike Impact on Plan, Implementation Notes, Files to Modify
- Advanced status from PLANNING to TEST
**Stopped at**: Spike complete, TEST phase entry. Conformance test file not yet created.
**Next step**: Write `tests/conformance/test_output_registry.py` with all test cases from Section 3. Tests should use current API (will mostly FAIL since typed methods don't exist yet).
**Blockers**: None

### Session: 2026-02-17 — TEST phase, BUILD phase, VALIDATE phase
**Phase**: TEST → BUILD → VALIDATE
**Work done**:
- Wrote 32 conformance tests in `tests/conformance/test_output_registry.py` covering REQ-OR-01 through REQ-OR-08
- TEST gate verified: 12 passed, 20 skipped (typed API not yet created — expected), no mocks
- Created 5 NewType wrappers + 2 constructor functions in `core/identifier_types.py`
- Refactored OutputRegistry class: 3 typed dicts (`_scoped`, `_sysml_qn`, `_alias`), 3 typed lookup methods, `_compat` dict for legacy keys
- Refactored `build_output_registry()`: typed registration via `register_scoped()` / `register_sysml_qn()`, legacy keys via `register()` into `_compat`
- Fixed EXPOSE_PURE Phase 3: canonical_name is Key_A format, resolved via `resolve()` (finds Key_A in `_compat`)
- Fixed Phase 4 transitive: default_value is Key_A format, resolved via `resolve()`
- Updated unit tests: repr format changes (now includes `compat=`), alias collision test
- **Key deviation**: Dead keys NOT fully eliminated — moved to `_compat` dict for backtracker backward compat. Typed registries are clean (REQ-OR-05/08 pass). `_compat` removed in C11.
- All 32 conformance tests pass
- Full suite: 1080 passed, 0 failures
- Lint clean: `ruff check src/` passes
- BUILD gate satisfied, advanced to VALIDATE
- Validation checklist: 15/16 items checked (COMPONENT_CHECKLIST/IMPLEMENTATION_PLAN pending)
**Stopped at**: VALIDATE phase, most validation items checked
**Next step**: Update COMPONENT_CHECKLIST.md and IMPLEMENTATION_PLAN.md, then commit
**Blockers**: None
