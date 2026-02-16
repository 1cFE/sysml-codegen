---
date: 2026-02-15T22:51:31-06:00
researcher: Claude
topic: "Aggregation Wiring Gap — Root Cause Analysis and Fix Design"
tags: [research, aggregation, output-registry, graph-builder, cost-pattern]
status: complete
last_updated: 2026-02-15
---

# Research: Aggregation Wiring Gap

**Date**: 2026-02-15 22:51 CST
**Researcher**: Claude
**Research Type**: Architecture / Bug Analysis
**Triggered by**: Phase 4 of E2E Post-Codegen Validation (fusion-tea)

## Research Question

Phase 4 of the E2E validation found that only 8 of 70 aggregation module
inputs wire to upstream MODULE_OUTPUTs. The remaining 62 are incorrectly
treated as ENTRY_POINTs (user-provided JSON values). Why does this happen,
and how should it be fixed?

## Summary

- The graph builder's `_resolve_aggregation_input_channel()` uses **unscoped
  two-segment keys** (e.g., `"pv_module.capital_cost"`) for OutputRegistry
  lookup, but the registry only contains **fully-scoped dotted keys** (e.g.,
  `"solar_battery_plant.solar_array.pv_module.capital_cost"`).
- The `instance_path` needed to build a scoped key is already available at the
  call site but is not used for registry lookup.
- A secondary bug in SingletonTerm handling constructs channel names that don't
  match the aggregation module naming convention (`module_eqn__attr` vs
  `instance_path__part_usage__attr`).
- A tertiary gap in Phase 1b registration means aggregation outputs lack a
  design-prefix-stripped scoped key, blocking plant-level → sub-assembly
  resolution.
- The 8 inputs that succeed all go through the CHAIN redefinition search path
  (lines 790-813), bypassing the broken registry fallback entirely.
- The fix is three coordinated changes: scope the registry lookup, add a
  missing registration key, and fix SingletonTerm channel construction.

---

## Detailed Findings

### 1. Data Flow Context

Aggregation module inputs flow through this path:

```
hierarchy_resolver.py    Extract :>> EXPRESSION redefinitions
  _walk_aggregation_ast()    Decompose sum() into SumTerm / SingletonTerm / LocalTerm
        |
        v
initialization.py
  _scope_aggregation_expressions()    Scope PartDef-level expressions to design instances
        |                             Produce ScopedAggregationData(expression, instance_path)
        v
  build_output_registry()    Phase 1b: register aggregation OUTPUT channels (Key_D, Key_E)
        |                    Phase 2: register CHAIN aliases from :>> CHAIN redefinitions
        v
graph_builder.py
  _build_aggregation_module()    For each SumTerm/SingletonTerm:
    _resolve_aggregation_input_channel()    Resolve symbolic ref to pipeline channel
```

The symbolic references in SumTerms are **PartDef-local** names like
`"pv_module.capital_cost"` — the child PartUsage name + the attribute name as
they appear in the SysML `:>> EXPRESSION` on the assembly PartDef. These are
NOT globally-scoped.

### 2. Bug 1 — Unscoped Registry Lookup (Primary Cause)

**Location**: `graph_builder.py:815-820`

```python
# Fall back to output registry lookup (handles agg-to-agg references)
catalog_key = f"{part_usage}.{attr}"    # "pv_module.capital_cost"
channel = output_registry.resolve(catalog_key)
if channel is not None:
    return channel
```

The key `"pv_module.capital_cost"` does not match any registry entry:

| Registry Key Format | Example Value | Matches? | Why Not |
|---|---|---|---|
| Key_A (CalcUsage instance.output) | `"cost_model.total_cost"` | No | Wrong first segment (`cost_model` is the CalcUsage instance name, not the PartUsage name `pv_module`) and wrong attr name (`total_cost` is the CalcDef output, not the `:>>` alias `capital_cost`) |
| Key_C (CalcUsage dotted hierarchy) | `"solar_battery_plant.solar_array.pv_module.cost_model.total_cost"` | No | Fully scoped 5-segment path vs. 2-segment lookup key |
| Phase 2 CHAIN alias | `"solar_battery_plant.solar_array.pv_module.capital_cost"` | No | Fully scoped 4-segment path vs. 2-segment lookup key |
| Key_D (Aggregation short) | `"solar_array.capital_cost"` | No | Different PartUsage scope level (`solar_array` is the assembly, `pv_module` is the leaf) |
| Key_E (Aggregation full) | `"SolarBatteryDesign.solar_battery_plant.solar_array.capital_cost"` | No | Full path with design prefix |

The `instance_path` argument (e.g., `"SolarBatteryDesign__solar_battery_plant__solar_array"`)
is available at the call site and contains exactly the scope needed to build a
matching key:

```
instance_path segments[1:] = ["solar_battery_plant", "solar_array"]
dotted_scope = "solar_battery_plant.solar_array"
scoped_key = "solar_battery_plant.solar_array.pv_module.capital_cost"
                                                  ^^^^^^^^^^^^^^^^^^^^
                                                  matches Phase 2 CHAIN alias
```

### 3. Bug 2 — SingletonTerm Direct Channel Construction

**Location**: `graph_builder.py:930-941`

```python
if "." in s_term.source_path:
    prefix, output_name = s_term.source_path.rsplit(".", 1)
    calc_path = prefix.replace(".", "__")
    channel = get_channel_name(
        f"{agg.instance_path}__{calc_path}", output_name,
    )
    if channel in canonical_channels:
        s_source = InputSource(...)
```

This direct channel construction assumes the target is a CalcUsage output
where `source_path = "calc_instance.output_attr"`. It builds:

```
get_channel_name("{instance_path}__{calc_instance}", "output_attr")
→ lowercase("{instance_path}__{calc_instance}") + "__" + "output_attr"
```

This works for CalcUsage targets (e.g., `"allocation_model.total_allocation"`
→ `{instance_path}__allocation_model__total_allocation`). But it fails for
**aggregation output** targets.

Example — plant-level aggregation referencing sub-assembly aggregation
`"solar_array.capital_cost"`:

```
Direct construction:
  get_channel_name("Design__plant__solar_array", "capital_cost")
  → "design__plant__solar_array__capital_cost"

Actual aggregation output channel:
  get_channel_name("Design__plant__solar_array__capital_cost", "capital_cost")
  → "design__plant__solar_array__capital_cost__capital_cost"
                                                ^^^^^^^^^^^^^^
                                                attr appears TWICE in aggregation channels
```

Aggregation modules use `module_eqn = instance_path + "__" + attribute_name`,
so the output channel is `module_eqn + "__" + attribute_name` — the attribute
name appears both in the module's EQN and as the output field name. The
SingletonTerm construction doesn't account for this.

After this mismatch (`channel not in canonical_channels`), the code falls back
to `_resolve_aggregation_input_channel()` — where Bug 1 takes over.

### 4. Bug 3 — Missing Scoped Key in Phase 1b Registration

**Location**: `initialization.py:550-573`

Phase 1b registers aggregation outputs with two key formats:

```python
instance_parts = agg.instance_path.split("__")
part_usage = instance_parts[-1]

key_d = f"{part_usage}.{agg.expression.attribute_name}"
# "solar_array.capital_cost" — short, unscoped

key_e = ".".join(instance_parts + [agg.expression.attribute_name])
# "SolarBatteryDesign.solar_battery_plant.solar_array.capital_cost" — full with design prefix
```

What's **missing** is the intermediate scoped form (design-prefix-stripped):

```
"solar_battery_plant.solar_array.capital_cost"
```

This is exactly what a scoped lookup from the plant-level aggregation would
produce:

```
Plant-level instance_path = "SolarBatteryDesign__solar_battery_plant"
SumTerm: part_usage="solar_array", attr="capital_cost"
Scoped key = "solar_battery_plant" + "." + "solar_array" + "." + "capital_cost"
           = "solar_battery_plant.solar_array.capital_cost"
```

Without this registration, even a corrected scoped lookup would fail for
plant-level → sub-assembly aggregation references.

### 5. Why 8 Inputs Succeed

All 8 successful resolutions go through the **CHAIN redefinition search**
path (lines 790-813), which bypasses the registry entirely:

```python
for redef in redefinitions:
    if redef.redefinition_type == RedefinitionType.CHAIN and redef.attribute_name == attr:
        redef_part_name = redef.owning_part_qn.split("__")[-1]
        if sanitize_name(redef_part_name).lower() == part_usage.lower():
            chain_redef = redef
            break

if chain_redef and chain_redef.source_path:
    if "." in chain_redef.source_path:
        calc_usage, output = chain_redef.source_path.rsplit(".", 1)
        channel = get_channel_name(
            f"{instance_path}__{part_usage}__{calc_usage}", output
        )
        if channel in canonical_channels:
            return channel    # <-- the 8 successes exit here
```

This path:
1. Finds a `:>> capital_cost = cost_model.total_cost` CHAIN redef on the
   child PartDef (e.g., PV_Module)
2. Parses `source_path` into `calc_usage="cost_model"`, `output="total_cost"`
3. Builds channel directly: `get_channel_name("{instance_path}__pv_module__cost_model", "total_cost")`
4. Verifies channel exists in `canonical_channels`

This works because `instance_path` provides the full scope, and the CHAIN
redef provides the CalcUsage→output mapping. The 8 successes are the SumTerms
where:
- The leaf PartDef HAS a `:>> CHAIN` redefinition for that specific attribute
- The PartDef name-to-PartUsage name matching succeeds via `sanitize_name().lower()`
- The CalcUsage exists and its output channel is registered

The 62 failures are SumTerms/SingletonTerms where CHAIN resolution fails
(no redef exists, or name matching fails, or the CalcUsage chain doesn't
exist) and the registry fallback is broken.

### 6. Interaction Between the Three Bugs

```
SumTerm: "pv_module.capital_cost"
     |
     v
[CHAIN redef search]
  Found `:>> capital_cost = cost_model.total_cost` on PV_Module?
     |           |
    YES          NO
     |           |
     v           v
  Build channel  [Registry fallback]  ← Bug 1: unscoped key
  directly         "pv_module.capital_cost" → None
     |                    |
  Verify in              [SingletonTerm direct construction]  ← Bug 2: wrong EQN format
  canonical               channel not in canonical_channels
     |                    |
  SUCCESS (8)            [_resolve_aggregation_input_channel]  ← Bug 1 again
                          "pv_module.capital_cost" → None
                                |
                          ENTRY_POINT fallback (62)
```

For plant-level → sub-assembly aggregation:

```
SumTerm/Singleton: "solar_array.capital_cost"
     |
     v
[CHAIN redef search]
  Solar_Array has `:>> capital_cost = sum(...)` — EXPRESSION, not CHAIN
     |
    NO
     |
     v
[Registry fallback]
  "solar_array.capital_cost" → Key_D match?
     |           |
  Maybe?         If Key_D collides or isn't registered...
     |           |
     v           v
  SUCCESS       [Scoped lookup needed]  ← Bug 3: no scoped key registered
                "solar_battery_plant.solar_array.capital_cost" → None
                         |
                   ENTRY_POINT fallback
```

Note: Key_D (`"solar_array.capital_cost"`) SHOULD match for plant-level
references — it's the correct short form. But if there are Key_D collisions
(multiple aggregation outputs from different assemblies sharing the same
short key pattern), or if the plant-level terms are SingletonTerms (hitting
Bug 2 first), the resolution chain breaks down.

---

## Code References

| File | Lines | What |
|---|---|---|
| `resolution/graph_builder.py` | 740-821 | `_resolve_aggregation_input_channel()` — Bug 1 at line 816 |
| `resolution/graph_builder.py` | 857-894 | SumTerm processing in `_build_aggregation_module()` |
| `resolution/graph_builder.py` | 924-976 | SingletonTerm processing — Bug 2 at lines 932-936 |
| `generation/initialization.py` | 550-574 | Phase 1b aggregation output registration — Bug 3 |
| `generation/initialization.py` | 597-613 | Phase 2 CHAIN alias registration (correctly scoped) |
| `generation/initialization.py` | 400-453 | `_build_chain_aliases()` — produces scoped aliases |
| `core/output_registry.py` | 107-124 | `resolve()` — exact match only, no normalization |
| `core/output_registry.py` | 126-148 | `derive_key_c()` — strips design prefix, dot-joins |
| `extraction/data_models.py` | 274-281 | `SumTerm` — `part_usage_name` + `attribute_name` |
| `extraction/data_models.py` | 283-287 | `SingletonTerm` — `source_path` |
| `extraction/data_models.py` | 344-363 | `ScopedAggregationData` — `module_eqn` property |

---

## Architecture Insight

The OutputRegistry was designed as the **single lookup** for all channel
resolution (08_algorithm_revised.md, Section 12). The backtracker uses it
correctly — CHAIN bindings resolve via `registry.resolve(source_path)` with
dotted keys, REFERENCE bindings use the secondary `segments[-2]` + leaf-name
path.

But `_build_aggregation_module()` was built as a **parallel resolution path**
that largely bypasses the registry:

1. It searches raw `RedefinitionData` objects directly (lines 790-797)
2. It constructs channels by string manipulation (lines 803-805)
3. It falls back to an unscoped registry lookup only as a last resort (line 816-817)

This parallel path duplicates work that the Phase 2 CHAIN alias registration
already does — `_build_chain_aliases()` in initialization.py follows the same
`:>> capital_cost = cost_model.total_cost` chains and registers the results
as scoped aliases. The graph builder just needs to look them up with the
right key.

The fundamental mistake is that the graph builder treats the registry as a
secondary fallback rather than the primary resolution mechanism for
aggregation inputs. The CHAIN redef search should be the fallback (for edge
cases where Phase 2 registration didn't capture the alias), not the other
way around.

---

## Proposed Fix

### Change 1: Scope the registry lookup in `_resolve_aggregation_input_channel`

**File**: `resolution/graph_builder.py`, lines 815-821

Replace the unscoped fallback with a scoped lookup sequence:

```python
# --- current code (broken) ---
# Fall back to output registry lookup (handles agg-to-agg references)
catalog_key = f"{part_usage}.{attr}"
channel = output_registry.resolve(catalog_key)
if channel is not None:
    return channel
return None

# --- proposed fix ---
# Fall back to output registry lookup with scoped keys.
# The instance_path provides full hierarchy scope; stripping the design
# prefix (segments[0]) produces the dotted format that Phase 2 CHAIN
# aliases and Phase 1b aggregation keys are registered under.
instance_parts = instance_path.split("__")
dotted_scope = ".".join(instance_parts[1:])   # strip design prefix
scoped_key = f"{dotted_scope}.{part_usage}.{attr}"
# e.g., "solar_battery_plant.solar_array.pv_module.capital_cost"

channel = output_registry.resolve(scoped_key)
if channel is not None:
    return channel

# Also try unscoped Key_D format (agg-to-agg, e.g., "solar_array.capital_cost")
channel = output_registry.resolve(f"{part_usage}.{attr}")
if channel is not None:
    return channel

return None
```

**Why this works**: Phase 2 CHAIN aliases are registered with fully-scoped
dotted keys (produced by `_build_chain_aliases()` which uses
`find_instance_paths_for_partdef()` to get the scoped prefix). The scoped key
constructed here matches those aliases.

### Change 2: Add design-prefix-stripped key to Phase 1b registration

**File**: `generation/initialization.py`, lines 550-573

Add a `key_e_stripped` alongside existing Key_D and Key_E:

```python
key_d = f"{part_usage}.{agg.expression.attribute_name}"
key_e = ".".join(instance_parts + [agg.expression.attribute_name])
keys = [key_d, key_e]

# Key_E_stripped: scoped dotted key without design prefix.
# Required for plant-level → sub-assembly aggregation resolution
# where the scoped lookup produces "solar_battery_plant.solar_array.capital_cost"
# but Key_D is "solar_array.capital_cost" (too short) and Key_E includes
# the design prefix (too long).
if len(instance_parts) > 1:
    key_e_stripped = ".".join(instance_parts[1:] + [agg.expression.attribute_name])
    keys.append(key_e_stripped)
```

**Why this works**: A plant-level aggregation with `instance_path =
"SolarBatteryDesign__solar_battery_plant"` looking up sub-assembly
`"solar_array.capital_cost"` builds scoped key
`"solar_battery_plant.solar_array.capital_cost"`. Key_E_stripped for the
solar_array aggregation output is exactly this value.

### Change 3: Fix SingletonTerm to use registry-first resolution

**File**: `resolution/graph_builder.py`, lines 924-976

Replace the direct channel construction (which assumes CalcUsage EQN format)
with the same scoped registry lookup used for SumTerms:

```python
# --- current code (broken for aggregation targets) ---
if "." in s_term.source_path:
    prefix, output_name = s_term.source_path.rsplit(".", 1)
    calc_path = prefix.replace(".", "__")
    channel = get_channel_name(
        f"{agg.instance_path}__{calc_path}", output_name,
    )
    if channel in canonical_channels:
        s_source = InputSource(...)
    else:
        resolved = _resolve_aggregation_input_channel(...)

# --- proposed fix ---
if "." in s_term.source_path:
    # Try 1: Registry-first resolution (handles both CalcUsage and
    # aggregation targets via Phase 1/2 keys and aliases)
    resolved = _resolve_aggregation_input_channel(
        s_term.source_path, agg.instance_path, redefinitions, output_registry,
    )
    if resolved:
        s_source = InputSource(
            source_type="module_output",
            producer_channel=resolved,
        )
    else:
        # Try 2: Direct channel construction (CalcUsage targets only)
        prefix, output_name = s_term.source_path.rsplit(".", 1)
        calc_path = prefix.replace(".", "__")
        channel = get_channel_name(
            f"{agg.instance_path}__{calc_path}", output_name,
        )
        if channel in canonical_channels:
            s_source = InputSource(
                source_type="module_output",
                producer_channel=channel,
            )
```

**Why this works**: `_resolve_aggregation_input_channel` (with the Bug 1 fix)
handles both CalcUsage and aggregation targets via registry lookup. The direct
construction is kept as a secondary fallback for CalcUsage targets where the
EQN format matches, but it's no longer the primary path.

---

## Validation Plan

After implementing the three changes:

1. **Unit tests**: Existing `test_graph_builder_aggregation.py` tests should
   still pass (they use CHAIN redefs, which continue to work via the existing
   path). Add new tests for:
   - SumTerm resolution via scoped registry key (no CHAIN redef available)
   - SingletonTerm resolution to aggregation output (double-attr EQN)
   - Plant-level → sub-assembly aggregation via Key_E_stripped
   - Mixed: some terms resolve via CHAIN, others via registry

2. **sysml-codegen test suite**: `uv run pytest tests/` — no regressions

3. **Re-run Phase 4**: Regenerate solar_battery_v3, verify:
   - 70 aggregation inputs: target 55+ MODULE_OUTPUT (multiplicity EPs
     remain as entry points, ~15)
   - 0 "Registry unresolved" warnings for aggregation inputs
   - Codegen log shows Phase 2 CHAIN alias count unchanged

4. **Proceed to Phase 5**: Execute pipeline, verify 7 ground truth values

---

## Open Questions

1. **CHAIN redef coverage**: How many of the 62 failures are due to missing
   CHAIN redefs vs. name matching failures? Logging the CHAIN search
   (`attribute_name` match found but `part_name` match failed) would
   distinguish these cases.

2. **Key_D sufficiency for plant-level**: If Key_D (`"solar_array.capital_cost"`)
   doesn't collide, it should work for plant-level lookups even without the
   scoped fix. Need to verify whether the 15 key collisions reported in
   Phase 4 include Key_D collisions or only bare-name collisions.

3. **Aggregation alias variants**: Phase 1b registers `agg.expression.aliases`
   (e.g., `"total_capex"` aliasing `"capital_cost"`). These also need scoped
   keys for the same reason. The fix should extend to alias variant
   registration in Phase 1b.

---

## Recommendations

1. **Implement the three-change fix** described above. The changes are
   localized (two files, three functions) and don't alter the registry's
   contract or the backtracker's resolution logic.

2. **Add diagnostic logging** to `_resolve_aggregation_input_channel` that
   reports which resolution path succeeded (CHAIN redef, scoped registry,
   unscoped Key_D, direct construction). This makes future debugging trivial.

3. **Consider removing the CHAIN redef search** (lines 790-813) in a future
   cleanup. Phase 2 CHAIN alias registration already does the same work at
   registry construction time. The graph builder searching raw
   `RedefinitionData` is a redundant parallel path. Once the scoped registry
   lookup is confirmed working, the CHAIN search becomes dead code for
   correctly-registered models.

4. **Update 08_algorithm_revised.md** Section 9 (Step 7) to document that
   aggregation module inputs resolve via the OutputRegistry (scoped keys),
   not via direct RedefinitionData search. The current document's Section 12
   says the registry is "NOT the universal channel construction mechanism"
   for aggregation — that caveat should be narrowed after the fix.
