# Design Revision Comments v3 on 08_algorithm_revised.md

**Date:** 2026-02-13
**Reviewer:** Claude
**Iteration:** 3 (follows spike-backed iterations 1+2 and two design updates)
**Document under review:** `.project/reports/08_algorithm_revised.md` (post-iteration-2 update)
**Context:** All 14 issues from iterations 1+2 are CLOSED with spike data. This review
reads the updated design from an **implementer's perspective**: if I sat down to code this
tomorrow, what would block me or produce silent bugs?

---

## What Iteration 2 Resolved Well

All v2 changes were applied cleanly to the design document:

- OutputRegistry.resolve() is now exact-match only (no SYSML_QN normalization)
- REFERENCE binding secondary resolution path is specified (leaf-name extraction + parent-scoped resolve)
- `_resolve_to_design_attribute()` has a specification
- CHAIN alias construction filters BARE CAS codes and scopes DOTTED with instance_path
- FORMULA modules documented as synthetic CalcUsages through normal backtracking
- Aggregation modules documented as direct from ScopedAggregationData (not OutputRegistry)
- OutputRegistry scope clarified: binding resolution only

The design is now empirically grounded (7 spikes, 215 bindings, 4 models). The
remaining issues are about **internal format consistency** -- the kind of bug that
only surfaces when you wire the phases together.

---

## The Overarching Theme: Key Format Contract

Iterations 1+2 established WHAT data goes into the OutputRegistry. This review finds
that the design doesn't nail down the **exact string format** of registration keys
tightly enough to guarantee that Phase 2/3/4 alias resolution matches Phase 1
canonical keys. This is the same root cause as Bug 2 and Report 07's "key format
problem" -- just moved from the backtracker indexes into the OutputRegistry.

The OutputRegistry was the right architectural move. But it needs a **key format
specification** that all producers and consumers follow, tested by a spike that builds
the actual registry from real model data and verifies every alias resolves.

---

## Issue 15: Phase 1 CalcUsage output keys vs Phase 2 CHAIN alias canonical_names -- format mismatch

**Severity: Phase 2 alias registration silently fails for virtual CalcUsages.**

Phase 1 registers CalcUsage output keys as:

```python
f"{usage.instance_name}.{output_attr.name}"   # "dotted (short)"
f"{usage.qualified_name}__{output_attr.name}"  # EQN (full)
```

For virtual CalcUsages, `instance_name` is the full qualified name (per
`usage_extractor.py:255`). So the "dotted (short)" key is actually:

```
"SolarBatteryDesign__solar_battery_plant__solar_array__pv_module__cost_model.total_cost"
```

This uses `__` between hierarchy segments and `.` only between the CalcUsage
and its output attribute.

Phase 2 resolves CHAIN alias canonical_names constructed in Step 3.5(D):

```python
canonical_name = f"{instance_path}.{redef.source_path}"
# redef.source_path = "cost_model.total_cost" (PartDef-local dotted path, from Spike 6)
```

The canonical_name uses `.` throughout:

```
"solar_battery_plant.solar_array.pv_module.cost_model.total_cost"
```

**These formats don't match.** Phase 2 `registry.resolve()` would return `None`
for every CHAIN alias that targets a virtual CalcUsage output. The warning fires,
the alias is silently dropped.

**Why it hasn't bitten us yet:** Spike 2 showed virtual CalcUsage outputs are consumed
exclusively via aggregation (ScopedAggregationData, not OutputRegistry). No CHAIN
binding targets them. So the Phase 2 aliases are technically dead registrations for
virtual CalcUsage targets. But the design INTENDS them to work, the warning log would
be noisy, and a future model that does reference a virtual CalcUsage's aliased
attribute through a CHAIN binding would silently fail.

**Comparison with aggregation output keys:** Phase 1 aggregation registration uses:

```python
".".join(instance_parts + [agg.expression.attribute_name])  # "solar_battery_plant.solar_array.capital_cost"
```

This is fully dotted. So aggregation keys ARE compatible with CHAIN alias format.
CalcUsage keys are NOT.

**Proposed fix:** Add a dotted-path registration key for all CalcUsages:

```python
for usage in calc_usages:
    for output_attr in calc_def.output_attributes:
        channel = get_channel_name(usage.qualified_name, output_attr.name)
        keys = [
            f"{usage.instance_name}.{output_attr.name}",       # existing key 1
            f"{usage.qualified_name}__{output_attr.name}",      # existing key 2
        ]
        # NEW: dotted hierarchy path (compatible with Phase 2 alias format)
        dotted_path = _qualified_name_to_dotted_path(usage.qualified_name)
        keys.append(f"{dotted_path}.{output_attr.name}")
        registry.register(channel, keys)
```

Where `_qualified_name_to_dotted_path()` strips the design part prefix and converts
`__` to `.`:

```python
def _qualified_name_to_dotted_path(qualified_name: str) -> str:
    """Convert EQN 'DesignPart__part1__part2__calc' to 'part1.part2.calc'.

    Strips the first segment (design PartDef namespace) and replaces __ with .
    This produces the same format that aggregation scoping and CHAIN alias
    construction use for instance paths.
    """
    segments = qualified_name.split("__")
    return ".".join(segments[1:])  # drop design part prefix
```

For concrete CalcUsages, this produces the same key as key 1 (since qualified_name
minus the prefix is the instance_name). For virtual CalcUsages, it produces the
dotted path that Phase 2 aliases expect.

**Spike needed:** Spike 8 (below) to validate this fix against real model data.

> **UPDATE (2026-02-13, Spike 8 results):** Fix **confirmed and necessary**.
>
> All 41 Phase 2 CHAIN aliases in solar_battery resolve **exclusively via Key_C**
> (the dotted hierarchy path). Without Key_C, all 41 fail. Key_A for virtual
> CalcUsages produces a hybrid `__`+`.` format that never matches Phase 2's fully
> dotted canonical names.
>
> Key_C derivation validated:
> ```python
> Key_C = ".".join(usage.qualified_name.split("__")[1:]) + "." + output_attr.name
> ```
>
> For concrete CalcUsages, Key_A and Key_C are always different (Key_C includes
> the parent PartUsage scope, Key_A is just the instance name). Both are useful:
> Key_A matches short CHAIN binding source_paths, Key_C matches Phase 2 alias
> canonical names.
>
> Zero collisions across both models (217 keys in solar_battery, 33 in e2e_attr_expr).
>
> **CLOSED -- add Key_C to Phase 1 CalcUsage registration.**

---

## Issue 16: `instance_path` format is unspecified

**Severity: Blocks Phase 2 alias construction and aggregation scoping interop.**

`instance_path` is used in Step 3.5(D) for CHAIN alias scoping:

```python
alias_name = f"{instance_path}.{redef.attribute_name}"
canonical_name = f"{instance_path}.{redef.source_path}"
```

And implicitly in aggregation scoping (to build `instance_parts` for Phase 1
aggregation registration).

**The design never defines what `instance_path` IS.** Specifically:

1. **Format:** Does it use `.` separators (`solar_battery_plant.solar_array.pv_module`)
   or `__` separators (`solar_battery_plant__solar_array__pv_module`)?

2. **Scope:** Does it include the design PartDef namespace prefix
   (`SolarBatteryDesign__solar_battery_plant.solar_array`) or start from the
   first PartUsage (`solar_battery_plant.solar_array`)?

3. **Derivation:** How is it computed? From virtual CalcUsage qualified_name?
   From the hierarchy extraction result? From aggregation scoping data?

This matters because every Phase 2 alias key is prefixed with `instance_path`.
If `instance_path` uses `__` separators, the alias keys mix `__` and `.`:
`"solar_battery_plant__solar_array__pv_module.capital_cost"`. If it uses `.`,
they're fully dotted: `"solar_battery_plant.solar_array.pv_module.capital_cost"`.
Only the dotted format would be compatible with the proposed Issue 15 fix.

**Proposed specification:**

```python
# instance_path: The dotted hierarchy path from design root to a specific
# part usage. Does NOT include the design PartDef namespace.
#
# Derivation: strip design PartDef prefix from a virtual CalcUsage's
# qualified_name, replace __ with ., remove the CalcUsage name at the end.
#
# Example:
#   CalcUsage QN: "SolarBatteryDesign__solar_battery_plant__solar_array__pv_module__cost_model"
#   instance_path: "solar_battery_plant.solar_array.pv_module"
#   (design prefix dropped, CalcUsage name dropped, __ -> .)
#
# For direct children of the design root:
#   CalcUsage QN: "SolarBatteryDesign__solar_battery_plant__annualized_financial"
#   instance_path: "solar_battery_plant"
```

This definition ensures:
- `instance_path` format is dotted (compatible with Phase 1 aggregation keys)
- `f"{instance_path}.{redef.source_path}"` produces a fully dotted canonical_name
  (compatible with the Issue 15 fix's dotted-path registration key)
- `instance_parts` (for aggregation) can be derived as `instance_path.split(".")`

> **UPDATE (2026-02-13, Spike 8 results):** Format **empirically documented**.
>
> `ScopedAggregationData.instance_path` uses `__` separator and **INCLUDES** the
> design PartDef prefix as the first segment:
>
> ```
> instance_path:      SolarBatteryDesign__solar_battery_plant__solar_array
> split('__'):        ['SolarBatteryDesign', 'solar_battery_plant', 'solar_array']
> dotted form:        SolarBatteryDesign.solar_battery_plant.solar_array
> dotted (no prefix): solar_battery_plant.solar_array
> ```
>
> The design prefix is PascalCase (PartDef name); subsequent segments are
> snake_case (PartUsage names).
>
> For consumer-facing dotted keys (Phase 2 alias construction, Phase 1
> aggregation Key_D/E): strip first segment (`__`-split, drop index 0), then
> join with `.`. Phase 2 alias resolution works because it uses this stripped
> dotted form, which matches Key_C format from Issue 15 fix.
>
> **Key_E (full dotted including prefix)** would NOT match CHAIN binding
> source_paths (which lack the design prefix). Key_D (last segment only) is
> the practical lookup key. Key_E is for uniqueness guarantee only.
>
> **Proposed spec update:** Replace the prose definition with the exact
> derivation:
> ```python
> # instance_path from ScopedAggregationData: uses __ separator, includes design prefix
> # Consumer-facing dotted path: strip prefix, replace __ with .
> def instance_path_to_dotted(instance_path: str) -> str:
>     parts = instance_path.split("__")
>     return ".".join(parts[1:])  # drop design prefix
> ```
>
> **CLOSED -- add instance_path format specification to design.**

---

## Issue 17: `_get_parent_part_for_usage()` is unspecified

**Severity: Blocks REFERENCE binding secondary resolution implementation.**

Section 7 shows the REFERENCE binding resolution path:

```python
leaf_name = binding.source_path.rsplit("::", 1)[-1].strip("'")
parent_part = self._get_parent_part_for_usage(usage)
if parent_part:
    channel = self._output_registry.resolve(f"{parent_part}.{leaf_name}")
```

`_get_parent_part_for_usage()` determines what to use as the scoping prefix
when constructing the dotted key for secondary resolution. It's used for the
4 REFERENCE -> MODULE_OUTPUT cases (Spike 5: all computed attributes on the
same parent part as the consuming CalcUsage).

**The method is referenced but never defined.** What does it return?

From the 4 Spike 5 cases:
- CalcUsage `annualized_financial` has binding to `...annualized_om::p_net_kw`
  -> should resolve `"solar_battery_plant.p_net_kw"`
  -> parent_part must be `"solar_battery_plant"`
- CalcUsage `lcoe` has binding to `...lcoe::annual_om`
  -> should resolve `"e2e_plant.annual_om"`
  -> parent_part must be `"e2e_plant"`

**Pattern:** parent_part is the **immediate parent PartUsage** of the CalcUsage
(not the grandparent, not the design root).

**Proposed specification:**

```python
def _get_parent_part_for_usage(self, usage: CalcUsageData) -> str | None:
    """Get the parent PartUsage name for scoping secondary resolution.

    For concrete CalcUsages: extract the second-to-last segment of
    the qualified_name (split on __).

    For virtual CalcUsages: same rule (parent is the PartUsage that
    contains the CalcUsage, not the design PartDef namespace).

    Example:
      QN: "SolarBatteryDesign__solar_battery_plant__annualized_financial"
      -> "solar_battery_plant"

      QN: "SolarBatteryDesign__solar_battery_plant__solar_array__pv_module__cost_model"
      -> "pv_module"

    Returns None if QN has < 2 segments (shouldn't happen in practice).
    """
    segments = usage.qualified_name.split("__")
    if len(segments) < 2:
        return None
    return segments[-2]
```

**Wait -- this gives `"pv_module"` for the virtual CalcUsage, but the computed
attribute `p_net_kw` is registered as `"solar_battery_plant.p_net_kw"`.** The
secondary resolution would try `"pv_module.p_net_kw"` which wouldn't match.

Looking at Spike 5 more carefully: the 4 REFERENCE -> MODULE_OUTPUT cases are
all CalcUsages whose parent is the **design root** PartUsage, not a child part.
The parent_part IS the design root:
- `annualized_financial` is under `solar_battery_plant` (design root)
- `lcoe` is under `e2e_plant` (design root)

For virtual CalcUsages deep in the hierarchy (like `pv_module__cost_model`),
REFERENCE bindings resolve to ENTRY_POINT (design attributes), not MODULE_OUTPUT.
They don't hit the secondary resolution path.

**So the question is:** should `_get_parent_part_for_usage()` return the
immediate parent or the design root? For the observed data, only the design
root works. But the immediate parent is more semantically correct.

**The tension:** computed attributes are scoped to a specific PartUsage (their
`owning_part_name`). The Phase 1 registration key is
`f"{owning_part_name}.{python_name}"`. For the secondary resolution to match,
`parent_part` must equal `owning_part_name`. Since all observed computed attributes
are on the design root, and all consuming CalcUsages are also on the design root,
`segments[-2]` gives the design root. But this is coincidental, not by design.

**Spike needed:** Spike 8 (below) should verify what parent_part value produces
correct secondary resolution for all 4 REFERENCE -> MODULE_OUTPUT cases.

> **UPDATE (2026-02-13, Spike 8 results):** Logic **empirically validated**.
>
> All 4 REFERENCE -> MODULE_OUTPUT cases resolve with `segments[-2]`
> (immediate parent of CalcUsage):
>
> | Model | Usage | Param | Leaf | segments[-2] | Resolves? |
> |-------|-------|-------|------|-------------|-----------|
> | solar_battery | annualized_om | p_net_kw | p_net_kw | solar_battery_plant | YES |
> | solar_battery | annualized_financial | total_capex | capital_cost | solar_battery_plant | YES |
> | e2e_attr_expr | energy | power_mw | power_mw | e2e_plant | YES |
> | e2e_attr_expr | lcoe | annual_om | annual_om | e2e_plant | YES |
>
> For all 4 cases, the consuming CalcUsage sits at depth 3
> (`Design__root_part__calc_usage`), so `segments[-2]` == `segments[1]` (both
> are the design root). The algorithm `segments[-2]` is semantically correct
> (immediate parent) and coincidentally equals the design root for these cases.
>
> No alternative candidate (deeper hierarchy segments, dotted combinations)
> produced correct results for all 4 cases. Only the immediate parent works.
>
> **Spec:**
> ```python
> def _get_parent_part_for_usage(self, usage: CalcUsageData) -> str | None:
>     segments = usage.qualified_name.split("__")
>     if len(segments) < 2:
>         return None
>     return segments[-2]
> ```
>
> **CLOSED -- add `_get_parent_part_for_usage()` specification to Section 7.**

---

## Issue 18: `owning_part_short_name` on ChannelAlias is used but not defined

**Severity: Minor -- naming inconsistency, easy to fix.**

The `ChannelAlias` dataclass (Section 4, Step 3.5D) defines:

```python
@dataclass
class ChannelAlias:
    alias_name: str
    canonical_name: str
    owning_part_qn: str      # <-- qualified name
    source: str
```

But Phase 3 EXPOSE_PURE registration (Section 6) uses:

```python
scoped_alias = f"{alias.owning_part_short_name}.{alias.alias_name}"
```

`owning_part_short_name` doesn't exist on the dataclass. Is it:
- A property derived from `owning_part_qn` (e.g., last segment after `__`)?
- A separate field that needs to be added?
- A typo for `owning_part_qn`?

Similarly, Phase 1 FORMULA registration uses `ca.owning_part_name` (not
`ca.owning_part_short_name` or `ca.owning_part_qualified_name`). The naming is
inconsistent across Phases 1 and 3.

**Proposed fix:** Add `owning_part_short_name` as a derived property or specify
the derivation inline:

```python
# At alias construction time:
owning_part_short_name = owning_part_qn.rsplit("__", 1)[-1]
```

Or add it as an explicit field on `ChannelAlias`. Either way, the design should
be explicit.

> **UPDATE (2026-02-13):** No spike data needed. This is a naming consistency fix.
>
> Spike 8 used `ca.owning_part_name` (from `ComputedAttributeData`) for Phase 3
> registration and it resolved correctly. The `ChannelAlias` dataclass should
> either:
> - Add `owning_part_short_name` as a field populated at construction time, OR
> - Use `owning_part_qn.split("__")[-1]` inline at Phase 3 registration
>
> **Recommendation:** Compute inline at registration. Keep `ChannelAlias` simple
> with just `owning_part_qn`. Phase 3 code derives the short name:
> ```python
> short_name = alias.owning_part_qn.split("__")[-1]
> scoped_alias = f"{short_name}.{alias.alias_name}"
> ```
>
> **CLOSED -- update Phase 3 code in Section 6 to derive short name inline.**

---

## Issue 19: FORMULA synthetic CalcUsage construction is not self-contained

**Severity: Specification gap -- detail is in a different document.**

Section 5 (Step 4.5) says FORMULA computed attributes produce synthetic
`CalcUsageData` that flow through normal backtracking. Section 9 (Step 7) says
Family 2 modules originate as synthetic CalcUsages.

But the **construction rules** for synthetic CalcUsages are only in
`expression-aware-codegen.md` (Section 3, Pattern J), not in
`08_algorithm_revised.md`. Since 08 is supposed to be the authoritative
desired-state design, implementers would need to cross-reference a separate
concept document to build this.

**Key construction details needed:**
1. What is the synthetic CalcUsage's `qualified_name`? (e.g.,
   `"{parent_part}__{attr_name}"` or `"{parent_part}__{attr_name}__{attr_name}"`?)
2. What is its `instance_name`?
3. What bindings does it have? (One CHAIN binding per referenced sibling attribute?)
4. What is the source_path format for those bindings? (Dotted, like
   `"sibling_attr_name"`, or scoped like `"{parent_part}.{sibling_attr_name}"`)
5. What is the CalcDef name? (Synthetic CalcDef or None?)

**Proposed fix:** Add a subsection to Step 4.5 specifying synthetic CalcUsage
construction:

```
FORMULA Synthetic CalcUsage Construction:

  For each FORMULA-classified computed attribute:
    qualified_name = f"{parent_eqn}__{attr_name}"
    instance_name = attr_name
    calc_def_name = None (inline expression, no CalcDef)
    bindings = [
        BindingInfo(
            param_name=ref.name,
            binding_type=BindingType.CHAIN,
            source_path=f"{parent_short_name}.{ref.name}",  # scoped dotted
        )
        for ref in ca.references
        if ref.name != attr_name  # exclude self-reference
    ]
    is_computed_attribute = True
```

This makes the design self-contained.

> **UPDATE (2026-02-13):** No spike data needed. This is a specification
> completeness fix. The synthetic CalcUsage construction rules should be
> inlined into Section 5 (Step 4.5) of the algorithm document, replacing the
> cross-reference to `expression-aware-codegen.md`.
>
> Spike 8 confirmed that FORMULA outputs register with Key_F
> (`{owning_part_name}.{python_name}`) and resolve correctly via the
> OutputRegistry. The channel construction uses
> `sysml_to_python_qualified_name(owning_part_qn) + "__" + python_name`.
>
> **CLOSED -- inline synthetic CalcUsage construction spec into Step 4.5.**

---

## Issue 20: Who consumes Phase 2 CHAIN aliases?

**Severity: Design clarity -- potential dead code.**

Phase 2 registers CHAIN aliases from `:>>` redefinitions. These map aliased
attribute names to CalcUsage output channels. For example:

```
":>> capital_cost = cost_model.total_cost" on PartDef Solar_Array
->  alias: "solar_battery_plant.solar_array.pv_module.capital_cost"
    target: "solar_battery_plant.solar_array.pv_module.cost_model.total_cost"
```

**Who resolves this alias?**

1. **CHAIN bindings?** No -- Spike 2 showed no CHAIN binding targets virtual
   CalcUsage outputs. All CHAIN bindings use short instance names referencing
   concrete CalcUsages.

2. **REFERENCE bindings?** No -- REFERENCE bindings go through secondary
   resolution (leaf-name + parent-scoped), not through alias lookup.

3. **Phase 3 EXPOSE_PURE aliases?** Possibly -- an EXPOSE_PURE might have
   `canonical_name = "solar_battery_plant.capital_cost"` which could itself be
   a Phase 2 alias. But Spike 3 showed EXPOSE_PURE canonical targets reference
   concrete CalcUsage outputs directly.

4. **Aggregation?** No -- aggregation modules construct channels directly from
   ScopedAggregationData.

5. **Phase 4 transitive defaults?** Possibly -- a design attribute with
   `default_value = "solar_battery_plant.capital_cost"` would resolve through
   the registry, hitting the Phase 2 alias. Spike 7 found 2 transitive
   defaults, but both resolved to Phase 1 CalcUsage outputs directly.

**It appears that Phase 2 CHAIN aliases have no consumer in any observed model.**

This isn't necessarily wrong -- they're defensive registration for future models
that might reference aliased attributes through CHAIN bindings or transitive
defaults. But if they silently fail (Issue 15), the design should acknowledge
this.

**Proposed resolution options:**

**(A) Keep Phase 2 but fix the format mismatch (Issue 15 fix).** Phase 2 aliases
become functional even if currently unused. This is the conservative choice.

**(B) Defer Phase 2 registration.** Document that CHAIN aliases are not consumed
by any observed binding pattern. Add Phase 2 when a model actually needs it.
This follows the project guideline "don't design for hypothetical future
requirements."

**(C) Keep Phase 2, add a diagnostic.** Register the aliases and also log
statistics: "Phase 2: N aliases registered, M resolved, K failed." This makes
the unused-but-present state visible.

**Recommendation:** Option (A). The fix for Issue 15 is small (one additional
registration key). With the fix, Phase 2 aliases work correctly. Even if
currently unused, they complete the design's invariant that "every `:>>`
CHAIN redefinition creates a resolvable alias." If we defer, we'll forget
the format issue and re-encounter it later.

> **UPDATE (2026-02-13, Spike 8 results):** Consumer analysis **quantified**.
>
> Phase 2 CHAIN aliases have **no direct consumer** in either tested model.
> No CHAIN binding source_path targets a virtual CalcUsage output or its alias.
> However:
>
> - Key_C registration (Issue 15 fix) is already needed for Phase 2 alias
>   resolution to work. Zero additional implementation cost to keep Phase 2.
> - Phase 2 aliases create a complete alias chain: `:>>` attribute name ->
>   CalcUsage output channel. This is correct semantically even if no current
>   binding exercises it.
> - Removing Phase 2 would break the design's invariant that every `:>>`
>   CHAIN redefinition is resolvable.
>
> **Decision: Keep Phase 2 with Issue 15 fix (Option A).** Zero cost, correct
> semantics, defensive for future models.
>
> **CLOSED.**

---

## Issue 21: EXPOSE_PURE on PartDefinitions vs PartUsages -- scope of Step 4.5 scanning

**Severity: Low (theoretical based on available models).**

Step 4.5 says "Scans all `AttributeUsage` elements with expressions." This
presumably includes attributes on BOTH PartDefinitions (templates) and
PartUsages (concrete design instances).

If a PartDef has an EXPOSE_PURE attribute like:
```sysml
part def Solar_Array {
    attribute total_capex = cost_model.total_cost;
}
```

Then after template expansion, there are multiple design instances of
`Solar_Array`. The EXPOSE_PURE ChannelAlias would have:
- `alias_name = "total_capex"` (unscoped)
- `canonical_name = "cost_model.total_cost"` (PartDef-local)
- `owning_part_qn = "...Solar_Array"` (the PartDef QN)

At Phase 3 registration, the scoped alias would be:
`"Solar_Array.total_capex"` -> resolve `"cost_model.total_cost"`.

But `"cost_model.total_cost"` is the PartDef-local dotted path. In the
OutputRegistry, each virtual CalcUsage's output is registered with instance-
scoped keys (e.g., `"pv_module__cost_model.total_cost"` or the dotted equivalent).
The PartDef-local path has NO instance scoping, so it won't match any Phase 1 key.

**In practice:** Spike 7 showed solar_battery handles this case via Phase 4
transitive defaults (`solar_battery_plant.misc_hardware_cost` has
`default_value = "allocation_model.total_allocation"` which resolves). And
Spike 6 showed CHAIN aliases handle the capital_cost case. So EXPOSE_PURE on
PartDefs may not arise or may be handled by alternative paths.

**The question:** Does Step 4.5 scan PartDef attributes, or only PartUsage
attributes? If both, should EXPOSE_PURE on PartDefs produce per-instance
aliases (requiring virtual expansion)? Or should they be filtered out?

**Proposed resolution:** Add a note to Step 4.5 specifying the scan scope. If
PartDef attributes are scanned, EXPOSE_PURE on PartDefs should either:
- Be filtered out (since CHAIN aliases from Step 3.5 handle the same semantics), OR
- Be expanded per design instance (like CalcUsage template expansion in Step 3)

Filtering is simpler and consistent with the observation that CHAIN aliases
handle this role for PartDefs. EXPOSE_PURE would only fire for PartUsage
(concrete design) attributes.

> **UPDATE (2026-02-13, Spike 8 results):** Issue **confirmed with data**.
>
> Phase 3 (EXPOSE_PURE) fails on solar_battery:
> ```
> Solar_Array.misc_hardware_cost -> allocation_model.total_allocation -> FAILED
> ```
>
> Root cause: The EXPOSE_PURE is on PartDef `Solar_Array`, not a design
> PartUsage. The `references` field gives PartDef-local names
> (`allocation_model.total_allocation`), but registry keys are instance-scoped
> (e.g., `solar_battery_plant.solar_array.pv_module.allocation_model.total_allocation`
> via Key_C).
>
> Phase 4 (transitive defaults) fails on solar_battery for the same root cause:
> `misc_hardware_cost` on `Solar_Array` has `default_value =
> "allocation_model.total_allocation"` which is PartDef-local and can't resolve
> against instance-scoped registry keys.
>
> e2e_attr_expr succeeds (1/1 Phase 3, 1/1 Phase 4) because its EXPOSE_PURE
> is on the design-root PartUsage where scope already matches.
>
> **Resolution: Filter EXPOSE_PURE on PartDefs.** CHAIN aliases from Step 3.5
> already handle the same semantics for PartDefs (all 41 CHAIN aliases on
> solar_battery resolve correctly). EXPOSE_PURE should only fire for PartUsage
> (concrete design) attributes. Add a guard:
>
> ```python
> # In Step 4.5, skip EXPOSE_PURE on PartDefs:
> if ca.classification == EXPOSE_PURE and ca.is_on_part_definition:
>     continue  # CHAIN aliases from Step 3.5 handle PartDef aliases
> ```
>
> Similarly, Phase 4 transitive defaults on PartDef attributes should be
> skipped (same root cause). Or handle by filtering design attributes that
> belong to PartDefs rather than PartUsages.
>
> **CLOSED -- add PartDef filter to Step 4.5 EXPOSE_PURE and Phase 4.**

---

## Issue 22: EXPRESSION-type `:>>` override interaction with binding resolution

**Severity: Low -- design has the right intuition but should be explicit.**

Step 3.5(E) says:

```python
# EXPRESSION overrides are aggregation formulas -- don't rewrite
# the binding; the aggregation module will be created in Step 7.
```

Consider the scenario:

```sysml
part def Solar_Array {
    :>> capital_cost = sum(pv_module.cost, inverter.cost)  // EXPRESSION override
    calc cost_model : SimpleCostCalc {
        in capital_cost = capital_cost;  // REFERENCE binding to sibling attr
    }
}
```

The CalcUsage `cost_model` has a REFERENCE binding to `capital_cost`. After
template expansion, this binding still points to `capital_cost` (the sibling
attribute on Solar_Array). But `capital_cost` is now an EXPRESSION-type
`:>>` that produces an aggregation module output.

**Question:** How does the backtracker resolve this REFERENCE binding?

1. OutputRegistry exact match? `source_path` is SYSML_QN, so no.
2. Secondary resolution? Extract leaf `"capital_cost"`, try
   `resolve("solar_battery_plant.capital_cost")`. This hits the aggregation
   output Phase 1 key. -> MODULE_OUTPUT. Correct!
3. But: does secondary resolution work here? `parent_part` for the virtual
   CalcUsage `pv_module__cost_model` would be `"pv_module"`, not
   `"solar_battery_plant"`. The aggregation output is at the parent level,
   not the pv_module level. So `resolve("pv_module.capital_cost")` would MISS.

**This depends on Issue 17 (what does `_get_parent_part_for_usage()` return).**
If it returns `"pv_module"` (immediate parent), the resolution fails. If it
returns `"solar_battery_plant"` (design root), it might work. If it returns
`"solar_array"` (the PartUsage where the `:>>` lives), it would try
`"solar_array.capital_cost"` which might or might not be registered.

**This scenario may not occur in practice** (the SysML model structure might
not allow CalcUsages on a PartDef to reference the PartDef's own `:>>`
EXPRESSION attributes). But the design should document the expected behavior.

**Proposed resolution:** Add a note that EXPRESSION overrides are consumed
exclusively through the aggregation module output channel (registered in Phase 1
aggregation). If any CalcUsage binding references an aggregation attribute,
the backtracker resolves it through the OutputRegistry (Phase 1 aggregation
key). The aggregation key format is `"{parent_instance_path}.{attr_name}"`,
so the secondary resolution must use the correct parent scope.

> **UPDATE (2026-02-13, Spike 8 results):** Partially informed by data.
>
> Spike 8 confirmed that `_get_parent_part_for_usage()` returns `segments[-2]`
> (immediate parent). For virtual CalcUsages deep in the hierarchy (e.g.,
> `pv_module__cost_model`), `segments[-2]` = `"pv_module"`, not
> `"solar_array"` or `"solar_battery_plant"`.
>
> Aggregation outputs are registered with Key_D as
> `"{part_usage_name}.{attribute_name}"` (e.g., `"solar_array.capital_cost"`).
> A virtual CalcUsage under `pv_module` would try
> `resolve("pv_module.capital_cost")` which would miss `"solar_array.capital_cost"`.
>
> **UPDATE (2026-02-13, Spike 9 results):** Empirically verified -- same-scope
> case **works**.
>
> Created a minimal test model (`tests/fixtures/issue22_model/`) with the
> exact Issue 22 pattern: `WidgetAssembly` PartDef has both
> `:>> total_cost = sum(widget.total_cost)` (aggregation) and
> `calc margin_calc : MarginCalc { in component_total = total_cost; }`
> (REFERENCE binding to the aggregation attribute).
>
> After virtual expansion:
> - `margin_calc` QN: `Issue22Design__plant__assembly__margin_calc`
> - `segments[-2]` = `assembly` (the WidgetAssembly instance)
> - Aggregation Key_D = `assembly.total_cost`
> - `resolve("assembly.total_cost")` -> **SUCCESS** (via Aggregation.Key_D)
>
> The binding `component_total` is REFERENCE type with SYSML_QN source_path
> `Issue22Library::WidgetAssembly::total_cost`. Secondary resolution extracts
> leaf `total_cost`, scopes with `segments[-2]` = `assembly`, and resolves
> against the aggregation output's Key_D.
>
> Note: the **current** backtracker resolves this as ENTRY_POINT (false entry
> point) because it lacks secondary resolution. The proposed OutputRegistry
> design with secondary resolution would correctly resolve this as
> MODULE_OUTPUT. This is a concrete example of the bug the OutputRegistry fixes.
>
> The deeply-nested cross-scope case (CalcUsage on child PartDef referencing
> grandparent aggregation) remains a theoretical limitation -- not observed
> in any model.
>
> **Resolution: Empirically verified for same-scope case.** CalcUsage and
> aggregation share the same instance scope after virtual expansion.
> `segments[-2]` produces the correct parent_part. Deeply-nested cross-scope
> case documented as known limitation in Section 7.
>
> **CLOSED -- verified by Spike 9.**

---

## Proposed Spike for Iteration 3

### Spike 8: OutputRegistry End-to-End Key Format Validation

**Question:** Do the registration keys (Phase 1) and resolution keys (Phase 2/3/4
aliases + backtracker resolve calls) actually match in practice?

**Addresses:** Issues 15, 16, 17, 20

**Script:** `scripts/spikes/spike_output_registry_e2e.py`

**Algorithm:**
1. Load solar_battery and e2e_attr_expr models
2. Run extraction through Step 4.5 (CalcUsages, hierarchy, computed attrs)
3. Build the OutputRegistry following the exact Phase 1-4 protocol from Section 12
4. **Phase 1 validation:** For every CalcUsage output, confirm the registration
   key matches expected format. Log concrete vs virtual CalcUsage key formats.
5. **Phase 2 validation:** For every CHAIN alias from Step 3.5(D):
   - Call `registry.resolve(alias.canonical_name)`
   - Log success/failure
   - If failure: print the canonical_name and list the closest Phase 1 keys
6. **Phase 3 validation:** For every EXPOSE_PURE alias from Step 4.5:
   - Call `registry.resolve(alias.canonical_name)`
   - Log success/failure
7. **Phase 4 validation:** For every transitive design attribute default:
   - Call `registry.resolve(attr.default_value)`
   - Log success/failure
8. **Backtracker validation:** For every CHAIN binding, call
   `registry.resolve(source_path)`. For every REFERENCE binding, simulate
   secondary resolution. Compare results vs current backtracker outcomes.

**Pass criteria:**
- 100% Phase 3+4 alias resolution (these work in current models per Spikes 3+7)
- Document Phase 2 resolution rate (expected: some failures due to Issue 15)
- 100% CHAIN binding resolution matches current backtracker MODULE_OUTPUT outcomes
- Document any REFERENCE secondary resolution mismatches (Issue 17)
- Identify the exact `_get_parent_part_for_usage()` logic that produces correct
  results for all 4 REFERENCE -> MODULE_OUTPUT cases

**Additional output:** Print the exact dotted-path key that WOULD match each
Phase 2 failure, confirming the Issue 15 fix is viable.

---

## Summary

### New issues (iteration 3)

| # | Issue | Severity | Action |
|---|-------|----------|--------|
| 15 | Phase 1 CalcUsage keys vs Phase 2 CHAIN alias format mismatch | Blocks Phase 2 for virtual CalcUsages | Add dotted-path registration key; spike to validate |
| 16 | `instance_path` format unspecified | Blocks Phase 2 alias construction | Specify as dotted, stripped of design prefix |
| 17 | `_get_parent_part_for_usage()` unspecified | Blocks REFERENCE secondary resolution | Specify + spike to validate against 4 cases |
| 18 | `owning_part_short_name` inconsistency | Minor naming | Specify derivation from `owning_part_qn` |
| 19 | FORMULA synthetic CalcUsage construction not self-contained | Specification gap | Inline construction rules from expression-aware-codegen.md |
| 20 | Phase 2 CHAIN aliases have no observed consumer | Design clarity | Fix Issue 15 so they work; keep as defensive registration |
| 21 | EXPOSE_PURE on PartDefs scope | Low (theoretical) | Clarify Step 4.5 scan scope; filter PartDef EXPOSE_PURE |
| 22 | EXPRESSION override binding resolution | Low (theoretical) | Document expected behavior for `:>>` EXPRESSION attrs |

### Classification

**Blocks implementation (must resolve before coding):**
- Issue 15: key format mismatch (core OutputRegistry correctness)
- Issue 16: instance_path specification (needed for alias construction)
- Issue 17: `_get_parent_part_for_usage()` (needed for REFERENCE resolution)

**Should resolve before coding (specification completeness):**
- Issue 18: naming inconsistency (quick fix)
- Issue 19: synthetic CalcUsage spec (copy from expression-aware-codegen.md)

**Can resolve during implementation (low risk):**
- Issue 20: Phase 2 consumer analysis (addressed by Issue 15 fix)
- Issue 21: PartDef EXPOSE_PURE scope (filter rule)
- Issue 22: EXPRESSION override semantics (document expected behavior)

### Spike needed

| Spike | Question | Addresses |
|-------|----------|-----------|
| 8 | Do Phase 1 registration keys match Phase 2/3/4 resolution keys in practice? | Issues 15, 16, 17, 20 |

### Expected iteration 3 outcome

After Spike 8:
- Issue 15 has validated fix (dotted-path registration key for CalcUsages)
- Issue 16 has validated instance_path format specification
- Issue 17 has empirically correct `_get_parent_part_for_usage()` implementation
- Issue 20 has quantified Phase 2 consumer data
- Issues 18, 19, 21, 22 are specification text changes (no spike needed)

---

## Relationship to Prior Iterations

| Iteration | Theme | Issues | Status |
|-----------|-------|--------|--------|
| 1 | Empirical grounding | 1-8 | CLOSED (Spikes 1-4) |
| 2 | Specification gaps | 6, 9-14 | CLOSED (Spikes 5-7) |
| 3 | Key format consistency | 15-22 | OPEN (Spike 8 needed) |

The progression is natural: iteration 1 asked "what does the parser produce?",
iteration 2 asked "what does the resolution chain look like?", and iteration 3
asks "do the registration keys actually match the resolution keys?" Each
iteration narrows the gap between design and implementation.

---

## Post-Spike Status (2026-02-13)

All 8 issues from iteration 3 now have UPDATE notes with spike-backed or
informed resolutions. All issues are **CLOSED**.

### Resolution Summary

| # | Issue | Resolution | Evidence |
|---|-------|-----------|----------|
| 15 | Phase 1 key format mismatch | **Add Key_C** (dotted hierarchy path) to Phase 1 CalcUsage registration. All 41 Phase 2 CHAIN aliases resolve exclusively via Key_C. | Spike 8: 41/41 via Key_C |
| 16 | `instance_path` format | **Documented.** Uses `__` separator, includes design prefix. Strip prefix and replace `__` with `.` for consumer-facing keys. | Spike 8: format analysis |
| 17 | `_get_parent_part_for_usage()` | **`segments[-2]`** (immediate parent). All 4 REFERENCE->MODULE_OUTPUT cases confirmed. | Spike 8: 4/4 via segments[-2] |
| 18 | `owning_part_short_name` | **Derive inline** from `owning_part_qn.split("__")[-1]`. | No spike needed |
| 19 | FORMULA synthetic CalcUsage spec | **Inline into Step 4.5.** Cross-reference to expression-aware-codegen.md is insufficient. | No spike needed |
| 20 | Phase 2 consumers | **Keep Phase 2 (Option A).** No direct consumers, but zero cost with Issue 15 fix and semantically correct. | Spike 8: 0 direct consumers |
| 21 | EXPOSE_PURE on PartDefs | **Filter out.** PartDef EXPOSE_PURE produces unscoped canonical names. CHAIN aliases handle this role. Phase 3+4 fail on solar_battery for this root cause. | Spike 8: 0/1 Phase 3 fail, 0/1 Phase 4 fail |
| 22 | EXPRESSION override binding | **Empirically verified (same-scope).** `segments[-2]` works for CalcUsages sharing instance scope with aggregation (Spike 9). Deeply-nested cross-scope case remains theoretical limitation. | Spike 9: same-scope PASS, Spike 8: depth-3 confirmed |

### Key Algorithm Document Changes Needed

1. **Phase 1 CalcUsage registration:** Add Key_C = `".".join(qn.split("__")[1:]) + "." + output`
2. **instance_path specification:** Add format definition with derivation formula
3. **`_get_parent_part_for_usage()`:** Add implementation spec (`segments[-2]`)
4. **Phase 3 EXPOSE_PURE:** Derive `owning_part_short_name` inline; filter PartDef attributes
5. **Step 4.5:** Inline FORMULA synthetic CalcUsage construction rules; add PartDef EXPOSE_PURE filter
6. **Phase 4 transitive defaults:** Filter PartDef-level design attributes
7. **Section 7 REFERENCE resolution:** Add known limitation note for deep hierarchy
8. **Key format specification:** Add the authoritative key format contract from spike report

### All Iterations Complete

| Iteration | Theme | Issues | Status |
|-----------|-------|--------|--------|
| 1 | Empirical grounding | 1-8 | CLOSED (Spikes 1-4) |
| 2 | Specification gaps | 6, 9-14 | CLOSED (Spikes 5-7) |
| 3 | Key format consistency | 15-22 | CLOSED (Spike 8) |

**The design is now ready for implementation.** All 22 issues across 3 iterations
are closed with spike data or informed resolutions. 8 spikes total, covering
215+ bindings across 4 models. The OutputRegistry key format contract is
empirically validated end-to-end.
