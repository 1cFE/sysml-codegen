# Design: Aggregation Wiring Fix

**Status:** Draft
**Owner:** Reid Westwood
**Created:** 2026-02-15T23:45:37Z
**Branch:** cost-pattern

## Overview

Three coordinated changes across two files fix the aggregation input
wiring pipeline so that the OutputRegistry is the primary resolution
mechanism, replacing the broken unscoped key lookup and wrong-order
SingletonTerm resolution.

## Related Artifacts

- **Spec:** `.project/active/aggregation-wiring-fix/spec.md`
- **Research:** `.project/research/20260215-225131_aggregation-wiring-gap-analysis.md`
- **Spike Report:** `.project/active/aggregation-fix-validation/spike_report.md`
- **Spike Script:** `scripts/spike_aggregation_validation.py`
- **Epic:** COST-PATTERN (`.project/backlog/epic_costed_component_pattern.md`)

---

## Research Findings

### Files Analyzed

| File | Lines | Role |
|------|-------|------|
| `resolution/graph_builder.py` | 740-976 | Bug 1 (line 816), Bug 2 (lines 930-941), resolution entry points |
| `generation/initialization.py` | 550-574 | Bug 3 (Phase 1b registration), Key_D/Key_E formats |
| `generation/initialization.py` | 400-453 | `_build_chain_aliases()` — correctly scoped alias production |
| `generation/initialization.py` | 597-613 | Phase 2 CHAIN alias registration (no changes needed) |
| `core/output_registry.py` | 28-164 | `_index`, `_canonical`, `resolve()`, `register()`, `register_alias()` |
| `extraction/data_models.py` | 273-363 | `SumTerm`, `SingletonTerm`, `ScopedAggregationData.module_eqn` |
| `core/qualified_names.py` | 13-100 | `sanitize_name()`, `get_channel_name()` |
| `tests/unit/test_graph_builder_aggregation.py` | 1-865 | Existing test patterns, helper factories |

### Key Patterns Found

1. **Key_C derivation** (output_registry.py:126-148): Strips design prefix
   (segments[0]), joins remaining segments with `"."`, appends output attr.
   This is the exact algorithm needed for the scoped aggregation key — the
   fix reuses this logic inline.

2. **Phase 2 CHAIN aliases** (initialization.py:438-443): Built by
   `_build_chain_aliases()` using `find_instance_paths_for_partdef()` to
   produce fully-scoped dotted keys like
   `solar_battery_plant.solar_array.pv_module.capital_cost`. These are the
   keys the scoped lookup will match.

3. **Test helpers** (test_graph_builder_aggregation.py:45-84):
   `_make_scoped_agg()` and `_make_chain_redef()` — reuse for new tests.

4. **Registry collision policy** (output_registry.py:53-62): Refuse
   overwrite, log warning, keep first registration. New Key_E_stripped
   keys follow this policy automatically.

5. **`canonical_channels` property** (output_registry.py:161-164): Returns
   `frozenset(self._canonical)` for O(1) membership checks. Used in
   graph_builder.py:777 and 925.

### Resolution Flow (Current vs Fixed)

**Current flow** (graph_builder.py:740-976):
```
SumTerm "pv_module.capital_cost"
  → CHAIN search (lines 790-813): match attr + sanitize_name(PartDef).lower() == PartUsage.lower()
    → Found? Build channel directly, verify in canonical_channels → SUCCESS
    → Not found? Fall through
  → Registry lookup (lines 815-820): key = "pv_module.capital_cost" (UNSCOPED)
    → Always MISS (registry has scoped keys only)
  → Return None → caller creates ENTRY_POINT

SingletonTerm "solar_array.capital_cost"
  → Direct construction (lines 930-937): get_channel_name(instance__solar_array, capital_cost)
    → Builds "...solar_array__capital_cost" (WRONG — aggregation uses "...solar_array__capital_cost__capital_cost")
    → Not in canonical_channels → fall through
  → CHAIN fallback (lines 943-945): same broken registry lookup
  → Return None → ENTRY_POINT
```

**Fixed flow**:
```
SumTerm "pv_module.capital_cost"
  → CHAIN search (unchanged): still works for 8/12 cases
    → Not found? Fall through
  → Scoped registry lookup (NEW): key = "solar_battery_plant.solar_array.pv_module.capital_cost"
    → HIT (matches Phase 2 CHAIN alias) → SUCCESS
  → Unscoped Key_D fallback: key = "pv_module.capital_cost"
    → Fallback for edge cases
  → Return None

SingletonTerm "solar_array.capital_cost"
  → Registry-first via _resolve_aggregation_input_channel (NEW)
    → CHAIN search + scoped registry → resolves to aggregation output
  → Direct construction fallback (CalcUsage targets only)
  → Return None → ENTRY_POINT
```

---

## Proposed Design

### Change 1: Scoped Registry Lookup (FR-1 — Bug 1 Fix)

**File:** `resolution/graph_builder.py`
**Function:** `_resolve_aggregation_input_channel()` (lines 814-821)
**What changes:** Replace the single unscoped registry lookup with a
scoped-then-unscoped lookup sequence.

**Current code** (lines 814-821):
```python
    # Fall back to output registry lookup (handles agg-to-agg references)
    catalog_key = f"{part_usage}.{attr}"
    channel = output_registry.resolve(catalog_key)
    if channel is not None:
        return channel

    return None
```

**New code:**
```python
    # Fall back to output registry lookup with scoped keys.
    # The instance_path provides full hierarchy scope; stripping the design
    # prefix (segments[0]) produces the dotted format that Phase 2 CHAIN
    # aliases and Phase 1b aggregation keys are registered under.
    # Strip design prefix and dot-join — same algorithm as
    # OutputRegistry.derive_key_c() and Phase 1b Key_E_stripped.
    instance_parts = instance_path.split("__")
    if len(instance_parts) > 1:
        dotted_scope = ".".join(instance_parts[1:])
        scoped_key = f"{dotted_scope}.{part_usage}.{attr}"
        channel = output_registry.resolve(scoped_key)
        if channel is not None:
            logger.debug(
                "Aggregation input '%s.%s' resolved via scoped registry key '%s'",
                part_usage, attr, scoped_key,
            )
            return channel

    # Unscoped Key_D fallback (e.g., "solar_array.capital_cost")
    catalog_key = f"{part_usage}.{attr}"
    channel = output_registry.resolve(catalog_key)
    if channel is not None:
        logger.debug(
            "Aggregation input '%s.%s' resolved via unscoped Key_D '%s'",
            part_usage, attr, catalog_key,
        )
        return channel

    logger.debug(
        "Aggregation input '%s.%s' unresolved (tried scoped '%s', unscoped '%s')",
        part_usage, attr,
        f"{'.'.join(instance_parts[1:])}.{part_usage}.{attr}" if len(instance_parts) > 1 else "N/A",
        catalog_key,
    )
    return None
```

**Algorithm:**

1. Split `instance_path` on `"__"` → e.g., `["SolarBatteryDesign", "solar_battery_plant", "solar_array"]`
2. Strip segments[0] (design prefix), join rest with `"."` → `"solar_battery_plant.solar_array"`
3. Append `".{part_usage}.{attr}"` → `"solar_battery_plant.solar_array.pv_module.capital_cost"`
4. `output_registry.resolve(scoped_key)` — exact match against Phase 2 CHAIN aliases
5. If miss, try unscoped `"{part_usage}.{attr}"` → `"pv_module.capital_cost"` (Key_D fallback)

**Why scoped-before-unscoped:** Key_D can collide across assemblies (Spike A
confirmed `solar_array.capital_cost` and `battery_system.capital_cost` share
the same short pattern). Scoped keys are unambiguous.

**Guard:** `len(instance_parts) > 1` ensures we don't try to scope with an
empty prefix (single-segment instance paths have no design prefix to strip).

**No changes above line 814:** The CHAIN redefinition search (lines 779-813)
is untouched. It remains the first resolution path — 8 of 12 inputs succeed
there and will continue to do so.

---

### Change 2: Key_E_stripped Registration (FR-2 — Bug 3 Fix)

**File:** `generation/initialization.py`
**Function:** `build_output_registry()`, Phase 1b block (lines 550-573)
**What changes:** Add a design-prefix-stripped dotted key alongside existing
Key_D and Key_E.

**Current code** (lines 560-572):
```python
        key_d = f"{part_usage}.{agg.expression.attribute_name}"
        key_e = ".".join(instance_parts + [agg.expression.attribute_name])
        keys = [key_d, key_e]

        # Bare key
        keys.append(agg.expression.attribute_name)

        # BF-7 alias variants (from agg.expression.aliases)
        for alias_name in agg.expression.aliases:
            keys.append(f"{part_usage}.{alias_name}")
            keys.append(alias_name)
            keys.append(".".join(instance_parts + [alias_name]))
```

**New code:**
```python
        key_d = f"{part_usage}.{agg.expression.attribute_name}"
        key_e = ".".join(instance_parts + [agg.expression.attribute_name])
        keys = [key_d, key_e]

        # Key_E_stripped: scoped dotted key without design prefix.
        # Required for plant-level → sub-assembly aggregation resolution
        # where the scoped lookup strips segments[0] from instance_path.
        if len(instance_parts) > 1:
            key_e_stripped = ".".join(instance_parts[1:] + [agg.expression.attribute_name])
            keys.append(key_e_stripped)

        # Bare key
        keys.append(agg.expression.attribute_name)

        # BF-7 alias variants (from agg.expression.aliases)
        for alias_name in agg.expression.aliases:
            keys.append(f"{part_usage}.{alias_name}")
            keys.append(alias_name)
            keys.append(".".join(instance_parts + [alias_name]))
            # Alias Key_E_stripped
            if len(instance_parts) > 1:
                keys.append(".".join(instance_parts[1:] + [alias_name]))
```

**Key formats produced (example: solar_array capital_cost aggregation):**

| Key | Format | Example | Purpose |
|-----|--------|---------|---------|
| Key_D | `{part_usage}.{attr}` | `solar_array.capital_cost` | Short unscoped |
| Key_E | `{all_parts}.{attr}` | `SolarBatteryDesign.solar_battery_plant.solar_array.capital_cost` | Full with design prefix |
| Key_E_stripped (NEW) | `{parts[1:]}.{attr}` | `solar_battery_plant.solar_array.capital_cost` | Scoped without design prefix |
| Bare | `{attr}` | `capital_cost` | Bare name |

**Why Key_E_stripped is needed:** When a plant-level aggregation
(`instance_path = "SolarBatteryDesign__solar_battery_plant"`) references
sub-assembly `"solar_array.capital_cost"`, Change 1 constructs scoped key
`"solar_battery_plant.solar_array.capital_cost"`. Neither Key_D
(`solar_array.capital_cost`) nor Key_E (includes design prefix) matches
this. Key_E_stripped is the intermediate form.

**Collision safety:** `registry.register()` enforces refuse-overwrite
(output_registry.py:53-62). If Key_E_stripped collides with an existing
key, the collision is logged and the first registration is kept.

---

### Change 3: SingletonTerm Registry-First Resolution (FR-3 — Bug 2 Fix)

**File:** `resolution/graph_builder.py`
**Function:** `_build_aggregation_module()`, SingletonTerm processing (lines 924-976)
**What changes:** Try `_resolve_aggregation_input_channel()` before direct
channel construction, not after.

**Current code** (lines 929-951):
```python
        s_source: InputSource | None = None
        if "." in s_term.source_path:
            # Direct channel build: dots -> __ path
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
            else:
                # Fall back to chain resolution
                resolved = _resolve_aggregation_input_channel(
                    s_term.source_path, agg.instance_path, redefinitions, output_registry,
                )
                if resolved:
                    s_source = InputSource(
                        source_type="module_output",
                        producer_channel=resolved,
                    )
```

**New code:**
```python
        s_source: InputSource | None = None
        if "." in s_term.source_path:
            # Try 1: Registry-first resolution (handles both CalcUsage and
            # aggregation targets via Phase 1/2 keys and aliases).
            resolved = _resolve_aggregation_input_channel(
                s_term.source_path, agg.instance_path, redefinitions, output_registry,
            )
            if resolved:
                s_source = InputSource(
                    source_type="module_output",
                    producer_channel=resolved,
                )
            else:
                # Try 2: Direct channel construction (CalcUsage targets only).
                # Builds instance_path__prefix__output_name — correct for CalcUsage
                # EQN format but wrong for aggregation outputs (double-attr).
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

**Why registry-first:** The direct construction assumes CalcUsage EQN
format where `source_path = "calc_instance.output_attr"` maps to channel
`instance_path__calc_instance__output_attr`. This works for CalcUsage
targets (e.g., `allocation_model.total_allocation`) but fails for
aggregation targets where `module_eqn = instance_path__attr`
(the attribute IS the calculation name — see
`ScopedAggregationData.module_eqn` at data_models.py:357-363) and
`get_channel_name(module_eqn, attr)` appends the attribute again as the
output field name, producing `instance_path__attr__attr`. This
double-appearance is by-design, not a bug.

`_resolve_aggregation_input_channel()` (with Change 1) handles both
target types via registry lookup. Direct construction is kept as a
fallback for CalcUsage targets that may not have CHAIN aliases
registered.

**Behavioral note for CalcUsage targets:**
When CHAIN redefs or Phase 2 CHAIN aliases exist for a CalcUsage target,
`_resolve_aggregation_input_channel` resolves it via those paths and
direct construction never fires. When neither exists (e.g., a CalcUsage
output registered only as canonical with no alias keys),
`_resolve_aggregation_input_channel` returns None and direct
construction fires as the fallback — this is the correct behavior.
The existing test `test_singleton_term_direct_channel` (line 265)
exercises exactly this fallback path: no redefs, no aliases, resolution
returns None, direct construction succeeds via canonical membership
check.

---

### Change 4: Diagnostic Logging (FR-4)

**File:** `resolution/graph_builder.py`
**What changes:** Add DEBUG-level logging to resolution paths (integrated
into Change 1 code above). Add a WARNING-level log on final failure
in `_build_aggregation_module()`.

The existing `logger` (graph_builder.py imports `logging.getLogger`) is
used. No new logger setup needed.

**SumTerm failure log** (in `_build_aggregation_module`, around line 873):
```python
        if channel:
            source = InputSource(...)
        else:
            logger.warning(
                "Aggregation SumTerm '%s' in '%s' unresolved → ENTRY_POINT",
                symbolic_ref, agg.instance_path,
            )
            compilability = Compilability.MANUAL_REQUIRED
            ...
```

**SingletonTerm failure log** (around line 953):
```python
        if s_source is None:
            logger.warning(
                "Aggregation SingletonTerm '%s' in '%s' unresolved → ENTRY_POINT",
                s_term.source_path, agg.instance_path,
            )
            compilability = Compilability.MANUAL_REQUIRED
            ...
```

---

## Testing Strategy

### Existing Tests (No Changes Expected)

All existing tests in `test_graph_builder_aggregation.py` use CHAIN
redefinitions that match via `sanitize_name().lower()`. Change 1 adds
a new path AFTER the CHAIN search, so these tests continue to follow
the CHAIN path and produce identical results. The test
`test_agg_to_agg_falls_back_to_registry` (line 114) uses Key_D
(`solar_array.capital_cost`) which still resolves via the unscoped
fallback in Change 1.

### New Tests

**File:** `tests/unit/test_graph_builder_aggregation.py`

Add to `TestResolveAggregationInputChannel`:

**Test 1: `test_scoped_registry_resolves_when_chain_fails` (AC-2)**
```
Setup: No CHAIN redefs. Registry has scoped Phase 2 alias
       "plant.array.pv_module.capital_cost" → canonical channel.
       instance_path = "Design__plant__array"
Call:  _resolve_aggregation_input_channel("pv_module.capital_cost", ...)
Assert: Returns canonical channel (scoped key hit)
```

**Test 2: `test_scoped_registry_resolves_chain_part_mismatch` (AC-2)**
```
Setup: CHAIN redef exists on "Lib__String_Inverter" for "capital_cost"
       but sanitize_name("String_Inverter").lower() = "string_inverter" ≠ "inverter"
       Registry has scoped alias "plant.array.inverter.capital_cost" → channel.
       instance_path = "Design__plant__array"
Call:  _resolve_aggregation_input_channel("inverter.capital_cost", ...)
Assert: Returns canonical channel (CHAIN fails, scoped key succeeds)
```

**Test 3: `test_scoped_before_unscoped_avoids_collision` (AC-7)**
```
Setup: No CHAIN redefs.
       Registry has BOTH:
         scoped: "plant.array.child.cost" → correct_channel
         unscoped Key_D: "child.cost" → wrong_channel (collision)
       instance_path = "Design__plant__array"
Call:  _resolve_aggregation_input_channel("child.cost", ...)
Assert: Returns correct_channel (scoped key wins over Key_D)
```

**Test 4: `test_agg_to_agg_via_key_e_stripped` (AC-3, AC-6)**
```
Setup: No CHAIN redefs.
       Registry has Key_E_stripped "plant.array.cost" → agg_channel.
       instance_path = "Design__plant" (plant-level looking up array)
Call:  _resolve_aggregation_input_channel("array.cost", ...)
Assert: Returns agg_channel
```

Add to `TestBuildAggregationModule`:

**Test 5: `test_singleton_term_registry_first_for_aggregation_target` (AC-5)**
```
Setup: Aggregation output channel = "Design__plant__array__cost__cost"
       (double-attr format). Register with scoped key.
       SingletonTerm source_path = "array.cost"
       instance_path = "Design__plant"
Call:  _build_aggregation_module(agg, [], registry, entry_points, None)
Assert: SingletonTerm input wired to aggregation output channel
        (NOT entry point, NOT wrong direct-construction channel)
```

**Test 6: REMOVED** — The existing `test_singleton_term_direct_channel`
(line 265) already covers AC-4. With Change 3, that test exercises the
direct-construction fallback path (registry-first returns None because
no CHAIN redefs or scoped aliases are registered, then direct
construction succeeds via canonical membership check). No new test
needed; the existing test implicitly validates the fallback fires.

**Test 7: `test_sum_term_scoped_resolution_no_chain` (AC-2)**
```
Setup: SumTerm "pv_module.capital_cost", no CHAIN redefs.
       Registry has scoped alias. instance_path = "Design__plant__array"
Call:  _build_aggregation_module(agg, [], registry, entry_points, None)
Assert: SumTerm input source_type == "module_output"
        (not entry_point, not MANUAL_REQUIRED)
```

### Integration Validation

After implementation, run:
```bash
uv run pytest tests/ -v
```

Optionally re-run the spike script to verify the fix with the real model:
```bash
uv run python scripts/spike_aggregation_validation.py
```

---

## Potential Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Key_E_stripped collides with existing registrations | Low | Low | Registry collision policy logs warning and keeps first registration. No silent mis-wiring. |
| SingletonTerm registry-first changes behavior for CalcUsage targets | Low | Medium | When CHAIN redefs or Phase 2 aliases exist, registry-first resolves them. When neither exists, registry returns None and direct construction fires as fallback. Existing test `test_singleton_term_direct_channel` (line 265) exercises exactly this fallback path. |
| Scoped key construction assumes segments[0] is design prefix | Very Low | Medium | `_scope_aggregation_expressions()` (initialization.py:470-478) derives design prefix from virtual CalcUsage QNs. Guard `len(instance_parts) > 1` prevents index error. |
| CHAIN search short-circuits before scoped lookup for correctly-named parts | None | None | This is desired behavior — CHAIN remains the first path. The scoped lookup only fires when CHAIN fails. |

---

## Integration Strategy

**Fits into existing architecture:** These changes align the aggregation
module builder with the OutputRegistry-first pattern used by the
backtracker for CalcUsage binding resolution. No new abstractions,
no new files, no contract changes.

**Two files modified:**
1. `src/sysml_codegen/resolution/graph_builder.py` — Changes 1, 3, 4
2. `src/sysml_codegen/generation/initialization.py` — Change 2

**One test file extended:**
1. `tests/unit/test_graph_builder_aggregation.py` — 6 new tests

**No other files touched.** No changes to `OutputRegistry`, data models,
CLI, templates, or other pipeline stages.

**Ordering:** Changes can be implemented in any order since they are in
separate functions, but Change 2 (Key_E_stripped registration) should be
in place before Change 1 (scoped lookup) is tested with agg-to-agg
scenarios, because the scoped lookup depends on Key_E_stripped for
plant-level references.

---

## Validation Approach

1. **Unit tests**: 6 new tests covering all acceptance criteria (AC-1
   through AC-7). Run with `uv run pytest tests/unit/test_graph_builder_aggregation.py -v`.

2. **Full test suite**: `uv run pytest tests/` — 454+ tests, 0 failures
   expected (AC-8).

3. **Spike re-run** (optional): Execute the spike script against the real
   solar_battery model to verify 12/12 resolvable inputs now resolve:
   ```bash
   uv run python scripts/spike_aggregation_validation.py
   ```
   Expected: Spike A shows 12/12 current hits (was 0/12).

4. **E2E validation**: Proceed to COST-PATTERN Item 5 with the fix in
   place. Regenerate solar_battery_v3, verify aggregation inputs wire
   to MODULE_OUTPUT.

---

**Next Step:** After approval → `/_my_plan` or `/_my_implement`
