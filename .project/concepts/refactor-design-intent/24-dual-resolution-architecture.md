# 24 -- Why Resolution Has Two Paths (and Must Stay That Way)

## The Structural Constraint

Resolution answers one question for every input: "where does this value come
from?" ([03-resolution-overview](03-resolution-overview.md)). It would be
cleaner to answer it with one function. But a structural constraint prevents
full unification: **CalcUsage resolution must happen during DFS traversal.**

The [backtracker](11-analysis-backtracker.md)'s DFS discovers which modules are
needed by tracing bindings. To trace a binding, it must resolve it -- only then
can it know whether to recurse into an upstream module (MODULE_OUTPUT) or stop
(ENTRY_POINT). Resolution and discovery are inseparable:

```python
# dependency_backtracker.py, _trace_dependencies (line 364):
resolution = self._resolve_binding_via_registry(binding, usage)
if resolution.resolution_type == MODULE_OUTPUT:
    producing_usage = self._find_usage_for_channel(resolution.qualified_name)
    self._trace_dependencies(producing_usage, visited, path)  # RECURSE
```

FORMULA and Aggregation modules are discovered differently -- not by tracing
bindings but by scanning computed attributes and aggregation expressions. They
are built AFTER the DFS completes. Their resolution CAN be extracted into a
standalone [`resolve_input()`](04-input-resolver.md).

This gives us two resolution paths. Not by accident, but by necessity.

## Requirements

| ID | Requirement | Verified by |
|----|-------------|-------------|
| REQ-DRA-01 | CalcUsage resolution SHALL happen during backtracker DFS; the DFS decision (recurse vs stop) depends on the resolution result. | `_trace_dependencies` calls `_resolve_binding_via_registry` at line 364; branch on `resolution_type` at line 367 |
| REQ-DRA-02 | FORMULA SHALL use pre-computed [attribute resolution map](16-computed-attributes.md). Aggregation SumTerm/SingletonTerm SHALL use [`resolve_input()`](04-input-resolver.md) with `AGG_STRATEGIES`. LocalTerm SHALL use factory-specific cascade. | Factory call sites use appropriate resolution mechanism |
| REQ-DRA-03 | Both paths SHALL implement [scoped resolution](03-resolution-overview.md#the-scope-problem) (REQ-RES-07): consumer scope prepended before any unscoped lookup. Unscoped Key_A fallback is prohibited ([REQ-OR-08](10-output-registry.md), [REQ-BT-08](11-analysis-backtracker.md)). | Backtracker: Step 0 (line 512), Step 1 raises on Key_A hit. resolve_input(): Strategy C first in chain, Strategy A flagged for same guard. |
| REQ-DRA-04 | Both paths SHALL produce the same wiring for the same reference. A binding `"cost_model.total_cost"` in scope `"plant.battery_pack"` SHALL resolve to the same channel regardless of path. | Integration test: same reference through both paths → identical `InputSource` |
| REQ-DRA-05 | The backtracker SHALL produce `BindingResolution` objects; `resolve_input()` SHALL produce `InputSource` objects. Both encode the same two-valued answer (module_output or entry_point). | `BindingResolution.resolution_type` maps to `InputSource.source_type` |

---

## Path 1: CalcUsage Resolution (Backtracker)

**When**: During DFS traversal, before graph construction.
**File**: `analysis/dependency_backtracker.py`, `_resolve_binding_via_registry()` (line 477).
**Input**: `BindingInfo` from [CalcUsageData](09-data-models.md#extraction-models).
**Output**: `BindingResolution` stored in `binding_resolutions` dict.

### Resolution cascade (6 stages)

*Stages 0-3 are resolution steps; stage 4 is a guaranteed fallback.
Stage 1b is a sub-step of stage 1 (same goal: direct registry hit, different key format).*

```
Stage 0: Scoped registry lookup (REQ-RES-07)
         consumer_scope + "." + source_path → Key_C
         → channel or None

Stage 1: Unscoped Key_A guard (REQ-BT-08)
         registry.resolve(source_path)
         → RAISES UnscopedResolutionError if match found (Key_A is diagnostic-only)

Stage 1b: SysML QN normalization          REMOVAL_CANDIDATE — 0% success rate
          "Package::Part::attr" → "part.attr"
          → channel or None

Stage 2: REFERENCE secondary (leaf + parent scope)
         Only for REFERENCE bindings
         → channel or None

Stage 3: Design attribute transitive
         Match source_path to DesignAttributeData
         → ENTRY_POINT

Stage 4: Fallback entry point
         → ENTRY_POINT with warning
```

Stage 0 includes a **self-reference guard**: if the resolved channel belongs to
the current usage, the resolution is discarded. Stage 1 now raises
`UnscopedResolutionError` if the unscoped lookup matches ([REQ-BT-08](11-analysis-backtracker.md)),
so the self-reference guard is no longer reached there.

**Result**: `BindingResolution(resolution_type, qualified_name, source_path, is_transitive)`.
Stored in `BacktrackingResult.binding_resolutions` keyed by
`"{usage_qn}|{param_name}"`. Consumed by `_build_pipeline_module()` in the
[module factory](05-module-factory.md#2-calcusage-modules).

---

## Path 2: FORMULA/Aggregation Resolution

**When**: During graph construction, after DFS.
**File**: `resolution/input_resolver.py`, `resolve_input()`.
**Input**: Symbolic reference string + [ResolutionContext](04-input-resolver.md#resolutioncontext).
**Output**: `InputSource` (consumed immediately by the factory).

### Strategy chain

FORMULA uses a pre-computed [attribute resolution map](16-computed-attributes.md),
not `resolve_input()`. Aggregation SumTerm/SingletonTerm inputs use:

```
AGG_STRATEGIES:
  C: ScopedRegistryLookup
  D: ChainRedefinitionFollow
  A: DirectRegistryLookup
  B: SysmlQnNormalization       # REMOVAL_CANDIDATE — 0% success (Research §5.#5)
  E: DesignAttributeLookup
```

`ChainRedefinitionFollow` (D) is promoted because aggregation inputs almost
always resolve through `:>>` chains. LocalTerm uses a factory-specific cascade
(see [05](05-module-factory.md#4c-localterm)).
See [04-input-resolver](04-input-resolver.md) for strategy details.

---

## Strategy Overlap Between Paths

Both paths solve the same problem with overlapping (but not identical) strategies:

| Strategy | Backtracker (CalcUsage) | Agg resolve_input() / FORMULA attr map |
|----------|:-:|:-:|
| Scoped lookup (Key_C) | Stage 0 | Strategy C |
| Direct lookup (Key_A guard) | Stage 1 (RAISES on hit — [REQ-BT-08](11-analysis-backtracker.md)) | Strategy A (flagged for same guard — [REQ-OR-08](10-output-registry.md)) |
| SysML QN normalization (removal candidate) | Stage 1b | Strategy B |
| CHAIN redefinition follow | -- | Strategy D |
| REFERENCE secondary | Stage 2 | Strategy C secondary form |
| Design attr transitive | Stage 3 | Strategy E |
| LITERAL :>> fallback | -- | In factory (REQ-MF-06) |
| Self-reference guard | After Stage 0/1 | After each strategy |

The overlap is intentional. Both paths must reach the same answer for the same
reference (REQ-DRA-04). The difference is which strategies are relevant:
- CHAIN redefinition follow is aggregation-specific (`:>>` chains through part hierarchy)
- REFERENCE secondary is CalcUsage-specific (FeatureReferenceExpression bindings)
- LITERAL fallback is aggregation-specific (`:>> attr = 42.0` defaults)

---

## Concrete Trace: Same Reference, Both Paths

**Reference**: `"cost_model.total_cost"` in scope `"plant.battery_pack"`.
**Registry**: Key_C `"plant.battery_pack.cost_model.total_cost"` →
canonical `"Design__plant__battery_pack__cost_model__total_cost"`.

**CalcUsage** (backtracker): Stage 0 scoped lookup →
`"plant.battery_pack.cost_model.total_cost"` → HIT →
`BindingResolution(MODULE_OUTPUT, canonical)`.

**Aggregation** (resolve_input with AGG_STRATEGIES): Strategy C scoped lookup →
`"plant.battery_pack.cost_model.total_cost"` → HIT →
`InputSource(module_output, canonical)`.

**Result**: Identical wiring. Different objects, same answer (REQ-DRA-04).

---

## Data Models

| Model | File | Role |
|-------|------|------|
| `BindingResolution` | `core/models.py` | CalcUsage resolution result (backtracker) |
| `InputSource` | `resolution/models.py` | FORMULA/Agg resolution result (resolve_input) |
| `BindingInfo` | `extraction/data_models.py` | CalcUsage binding input |
| `SumTerm` / `SingletonTerm` / `LocalTerm` | `extraction/data_models.py` | Aggregation term inputs |
| `ResolutionContext` | `resolution/input_resolver.py` | Immutable context for resolve_input() |
| `OutputRegistry` | `core/output_registry.py` | Shared lookup table (both paths) |

## Related Documents

- **Architecture**: [03-resolution-overview](03-resolution-overview.md) -- consolidated design and why CalcUsage stays separate
- **Backtracker**: [11-analysis-backtracker](11-analysis-backtracker.md) -- DFS algorithm and CalcUsage cascade
- **Resolver**: [04-input-resolver](04-input-resolver.md) -- resolve_input() strategies for FORMULA/Agg
- **Factories**: [05-module-factory](05-module-factory.md) -- how each path feeds module construction
- **Registry**: [10-output-registry](10-output-registry.md) -- shared O(1) lookup
- **Scope**: [15-naming-conventions](15-naming-conventions.md) -- Key_C format for scoped resolution
- **Data models**: [09-data-models](09-data-models.md) -- BindingResolution, InputSource, BacktrackingResult
