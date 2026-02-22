# Spec: Typed Registry Refactor

**Status:** COMPLETE
**Owner:** Reid Westwood
**Created:** 2026-02-17 06:16 UTC
**Complexity:** HIGH
**Branch:** cost-pattern-refactor

---

> **DELIVERABLE: DESIGN INTENT DOCUMENTS ONLY.**
>
> This spec targets the design intent corpus in
> `.project/concepts/refactor-design-intent/`. The deliverables are updated
> design documents (10, 11, 15, 24, 03) and a new design intent document
> (`27-typed-registry-refactor.md`).
>
> **DO NOT edit production source code.** The codebase is being refactored
> against these design docs. Editing current source is pointless — the code
> will be rewritten to match the design intent. Update the design intent
> first; implementation follows separately.

---

## Business Goals

### Why This Matters

The OutputRegistry is a `dict[str, str]` with ~12 key formats mashed into one
namespace. Resolution is a cascade of `dict.get()` calls against this pile,
hoping to hit the right key. The type system enforces nothing: a Key_A string,
a canonical channel name, a SysML QN, and a bare attribute name are all `str`.
Constructors in `qualified_names.py` return `str`, so format information
evaporates at the call site. The design docs that describe the key formats
(10-output-registry.md, 15-naming-conventions.md) were proven wrong in multiple
places by the Key_A fallback spike.

This is bad software. It hides bugs behind fallback chains instead of surfacing
them, and it makes it structurally impossible to distinguish a correct resolution
from an accidental collision.

### Success Criteria

- [ ] Every identifier format (EQN, PQN, SysML QN, ScopedKey, channel name) has a distinct type
- [ ] Constructors enforce format invariants; you cannot create a malformed key
- [ ] Registries are separate and typed; a lookup requires knowing which registry to query
- [ ] Ambiguous keys (Key_A, Key_D, Key_E, Key_F, bare) are eliminated
- [ ] mypy catches format mismatches at type-check time (e.g., passing a SysML QN where a ScopedKey is expected)
- [ ] All 6 model snapshots produce identical pipeline output before and after

### Priority

Blocks any further resolution work. The current registry design makes it
impossible to reason about correctness — you cannot tell whether a resolution
succeeded because it found the right key or because it found a wrong key that
happened to map to the same channel.

---

## Problem Statement

### Current State

1. **All identifiers are `str`.** `OutputRegistry._index` is `dict[str, str]`.
   `resolve()` takes `str`, returns `str | None`. `get_channel_name()` returns
   `str`. `BindingInfo.source_path` is `str | None`. No type distinguishes
   formats.

2. **One flat registry.** 12+ key formats in one dict. Step 1 in the
   backtracker does `registry.resolve(source_path)` — a blind `dict.get()`
   against everything. It doesn't know whether it hit a Key_A, a Phase 3
   EXPOSE_PURE alias, or a SysML QN key.

3. **Ambiguous keys pollute the namespace.** Key_A (`instance_name.attr`)
   collides when two scopes have the same instance name. Key_D, Key_F have the
   same problem. Bare keys (`total_capex`) are maximally ambiguous. The spike
   proves these keys have **zero** correct resolution hits across all 6 models.

4. **Design docs are wrong about the mechanism.** REQ-BT-08 says "Step 1
   (unscoped Key_A fallback) SHALL raise." Step 1 is a `dict.get()` against
   the entire index — it hits EXPOSE_PURE aliases and SysML QN keys that are
   correct resolutions, not Key_A. Implementing REQ-BT-08 as written breaks 12
   bindings. (See `.project/research/20260217-060000_key-a-fallback-spike.md`)

### Desired Outcome

Typed keys, typed registries, no ambiguity. When you look something up, the
types tell you what format the key is in, what registry to query, and what
format the result is in. If a key is in the registry, it's unique — no
"first registration wins" collision policy needed because collisions cannot
occur.

---

## Scope

### In Scope

- Typed wrappers for all identifier formats
- Separate typed registries replacing the flat `OutputRegistry`
- Elimination of ambiguous key formats
- Updates to backtracker resolution cascade
- Updates to `resolve_input()` strategy chain
- Updates to design intent docs (10, 11, 15, 24)
- Regression validation against all 6 model snapshots

### Out of Scope

- Changing the DFS-during-resolution architecture (doc 24)
- Expression compiler changes
- Aggregation scoping changes
- New resolution strategies

### Edge Cases & Considerations

- If any eliminated key turns out to be load-bearing in a model not currently
  tested, FR-6 applies: it MUST be made unique, not re-added as ambiguous.
- Phase 2 CHAIN aliases and Phase 4 transitive aliases resolve through existing
  keys before registering. The typed registries must support this cross-registry
  resolution chain.

---

## Requirements

### Functional Requirements

> All requirements are from user's explicit request unless marked [INFERRED].

#### FR-1: Typed identifier wrappers

All identifier formats SHALL have distinct types. At minimum:

| Type | Format | Separator | Example |
|------|--------|-----------|---------|
| `SysMLQN` | `Package::Element` | `::` | `SolarBatteryLibrary::BatteryPackCostCalc` |
| `EQN` | `Package__Element` | `__` | `SolarBatteryDesign__solar_battery_plant__lcoe` |
| `PQN` | `EQN__param` | `__` | `SBD__sbp__lcoe__lcoe_per_mwh` |
| `CanonicalChannel` | PQN of output | `__` | `SBD__sbp__lcoe__lcoe_per_mwh` |
| `ScopedKey` | dotted hierarchy, prefix stripped | `.` | `solar_battery_plant.lcoe.lcoe_per_mwh` |

Implementation MAY use `NewType` for zero-runtime-cost wrappers or thin
dataclasses for constructor validation. The choice is deferred to design.

Each type SHALL have a constructor that enforces format invariants (e.g.,
`ScopedKey` constructor rejects strings containing `::`; `SysMLQN` constructor
rejects strings containing `__`). Ad-hoc f-string construction of these values
outside the constructors SHALL be prohibited.

#### FR-2: Separate typed registries

The single `OutputRegistry._index: dict[str, str]` SHALL be replaced with
separate typed dictionaries. The resolver MUST know which registry it is
querying. At minimum:

| Registry | Key type | Value type | Contents |
|----------|----------|------------|----------|
| Scoped registry | `ScopedKey` | `CanonicalChannel` | Key_C (CalcUsage), Key_E_stripped (Aggregation) |
| SysML QN registry | `SysMLQN` | `CanonicalChannel` | Phase 1c `::` keys |
| Alias registry | `ScopedKey` | `CanonicalChannel` | Phase 2 CHAIN aliases, Phase 3 EXPOSE_PURE aliases, Phase 4 transitive aliases |

The exact number and names of registries are deferred to design. The
requirement is: **no single untyped dict that accepts any string format.**

`resolve()` as a single method taking `str` and returning `str | None` is
PROHIBITED. Each registry SHALL have its own typed lookup method.

#### FR-3: Eliminate ambiguous keys

The following key formats SHALL NOT be registered:

| Key | Format | Reason for elimination |
|-----|--------|----------------------|
| Key_A | `{instance_name}.{attr}` | Scope-ambiguous. Zero hits across 6 models. |
| Key_D | `{part_usage}.{attr}` | Same ambiguity as Key_A for aggregations. |
| Key_E | `{full_dotted_with_design_prefix}` | Redundant with Key_E_stripped. Nothing constructs a lookup that includes the design prefix. |
| Key_F | `{owning_part}.{python_name}` | Same ambiguity as Key_A for FORMULAs. |
| bare | `{attr_name}` alone | Maximally ambiguous. Zero documented resolution path depends on it. |

#### FR-4: Resolution uses binding type as discriminant

The backtracker's `_resolve_binding_via_registry()` SHALL dispatch on
`BindingType` to select the correct registry:

- `CHAIN` bindings: scoped registry (Step 0), then alias registry (for
  cross-package EXPOSE_PURE). No other registries consulted.
- `REFERENCE` bindings: SysML QN registry, then scoped registry with
  normalization. No other registries consulted.

The current "try everything in order" cascade (Steps 0 -> 1 -> 1b -> 2)
against a single dict SHALL be replaced with type-directed lookup against
the appropriate typed registry.

[INFERRED] `resolve_input()` in `input_resolver.py` SHALL apply the same
principle: strategies select the appropriate typed registry based on the
term type.

#### FR-5: Constructors are the single source of truth

Key construction SHALL happen through typed constructors only:

- `ScopedKey.from_eqn(usage_eqn, attr_name)` replaces `derive_key_c()` and
  inline Key_E_stripped construction
- `CanonicalChannel.from_eqn(usage_eqn, attr_name)` replaces
  `get_channel_name()`
- `SysMLQN(owning_part_qn, name)` replaces inline `f"{qn}::{name}"`

The existing functions in `qualified_names.py` that return bare `str` SHALL
either be updated to return the typed wrapper or be replaced by the wrapper's
constructor.

#### FR-6: If a key must exist, it MUST be unique

If any key format eliminated by FR-3 turns out to be load-bearing for a
model not currently in the test suite, the key format SHALL NOT be
re-introduced in its ambiguous form. Instead, the key MUST be made unique
by incorporating sufficient scope information. There is no situation where
a unique key cannot be constructed from available data.

This requirement has no exceptions. "First registration wins" collision
policy is a symptom of ambiguous keys and SHALL be eliminated for all
registries covered by FR-2.

### Non-Functional Requirements

- **NFR-1: Zero runtime cost.** `NewType` wrappers add no runtime overhead.
  If dataclasses are used, they SHOULD use `__slots__` and construction SHOULD
  be benchmarked against current string operations.
- **NFR-2: mypy strict mode.** All typed registries and constructors SHALL
  pass `mypy --strict` without `type: ignore` comments.
- **NFR-3: Incremental adoption.** [INFERRED] The refactor MAY be staged
  (e.g., types first, then registry split, then key elimination) as long as
  each stage is independently correct.

---

## Acceptance Criteria

### Core Functionality

- [ ] All identifier types from FR-1 exist with validated constructors
- [ ] `OutputRegistry._index: dict[str, str]` is gone; replaced by FR-2 registries
- [ ] Key_A, Key_D, Key_E, Key_F, and bare keys are not registered anywhere
- [ ] Backtracker dispatches on `BindingType` per FR-4
- [ ] No f-string key construction outside typed constructors (grep-verifiable)
- [ ] `mypy --strict` passes on all modified files

### Regression

- [ ] All 6 model snapshots produce identical `ComputationGraph` output
- [ ] All existing tests pass
- [ ] Key_A fallback spike (`tests/spikes/test_key_a_fallback_usage.py`) confirms 0 regressions

### Design Doc Updates

- [ ] `10-output-registry.md` updated: typed registries, no ambiguous keys
- [ ] `11-analysis-backtracker.md` updated: type-directed resolution, REQ-BT-08 corrected
- [ ] `15-naming-conventions.md` updated: REQ-NC-07 corrected (SysML QN keys exist), type wrappers authoritative
- [ ] `24-dual-resolution-architecture.md` updated: strategy tables reflect typed registries
- [ ] REQ-OR-08 rewritten: no longer references "Key_A fallback" as synonym for Step 1

---

## Supersedes / Amends

This spec supersedes the following design intent requirements:

| Requirement | Document | What changes |
|-------------|----------|-------------|
| REQ-OR-02 | 10-output-registry.md | `resolve()` replaced by typed lookup methods |
| REQ-OR-05 | 10-output-registry.md | Key_A/D/E/F/bare eliminated |
| REQ-OR-08 | 10-output-registry.md | Rewritten: Key_A not registered at all, no need for guard |
| REQ-BT-08 | 11-analysis-backtracker.md | Eliminated: Step 1 no longer exists as a generic fallback |
| REQ-NC-07 | 15-naming-conventions.md | Corrected: SysML QN keys exist in their own typed registry |
| REQ-DRA-03 | 24-dual-resolution-architecture.md | Rewritten: scoped resolution uses typed registry, not Key_A guard |
| REQ-RES-07 | 03-resolution-overview.md | Amended: unscoped Key_A fallback eliminated (not guarded, removed) |

This spec extends RB-01 (CanonicalName type wrappers) from `revision_backlog.md`.
RB-01 recommended `NewType` wrappers for names. This spec goes further:
typed keys, typed registries, and elimination of ambiguous key formats.

---

## Evidence Base

- **Key_A fallback spike**: `.project/research/20260217-060000_key-a-fallback-spike.md`
  - Zero Key_A hits across 6 models
  - 12 Step 1 hits are all EXPOSE_PURE aliases (10) or SysML QN keys (2)
  - REQ-BT-08 as written would break 12 correct resolutions
  - Key_A collisions observed in catf_mfe (10+ collisions), all resolved by Step 0

- **Binding type is known at resolution time**: `BindingInfo.binding_type` is
  set at extraction from the AST node type. CHAIN = dotted local path,
  REFERENCE = SysML QN with `::`. The resolver already branches on this
  (Step 0 skips `::`, Step 2 is REFERENCE-only) but then throws both types
  into one `dict.get()`.

- **RB-01 revision backlog**: Already identified `NewType` wrappers as critical
  (prevents 42% of historical bugs). This spec is the full execution of that
  recommendation plus registry separation.

---

## Related Artifacts

- **Research:** `.project/research/20260217-060000_key-a-fallback-spike.md`
- **Design intent:** `.project/concepts/refactor-design-intent/10-output-registry.md`
- **Design intent:** `.project/concepts/refactor-design-intent/11-analysis-backtracker.md`
- **Design intent:** `.project/concepts/refactor-design-intent/15-naming-conventions.md`
- **Design intent:** `.project/concepts/refactor-design-intent/24-dual-resolution-architecture.md`
- **Revision backlog:** `.project/concepts/refactor-design-intent/revision_backlog.md` (RB-01, RB-07)
- **Production code:** `src/sysml_codegen/core/output_registry.py`
- **Production code:** `src/sysml_codegen/core/qualified_names.py`
- **Production code:** `src/sysml_codegen/analysis/dependency_backtracker.py`
- **Production code:** `src/sysml_codegen/generation/initialization.py` (lines 502-675)
- **Spike test:** `tests/spikes/test_key_a_fallback_usage.py`
- **Design:** `.project/active/typed-registry-refactor/design.md` (to be created)

---

**Next Steps:** After approval, proceed to `/_my_design`
