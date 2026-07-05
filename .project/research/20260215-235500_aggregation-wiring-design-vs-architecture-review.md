---
date: 2026-02-15T23:55:00-06:00
researcher: Claude
topic: "Aggregation Wiring Design vs. Architecture Documents — Bug or Gap?"
tags: [research, aggregation, output-registry, architecture, adr, design-review]
status: complete
last_updated: 2026-02-15
---

# Research: Aggregation Wiring Design vs. Architecture Documents

**Date**: 2026-02-15 23:55 CST
**Researcher**: Claude
**Research Type**: Architecture Compliance Analysis
**Triggered by**: Design review of `.project/active/aggregation-wiring-fix/design.md`

## Research Question

The aggregation wiring fix design proposes three coordinated changes to how
aggregation module inputs are resolved. Do these changes align with or
contradict the project's architecture decision records (ADR-001 through
ADR-008) and the algorithm spec (`08_algorithm_revised.md`)? Are the issues
being fixed best characterized as **bugs** (code inconsistent with intended
design) or **gaps** (not discussed or considered in architecture documents)?

## Summary

- The design's three changes are **consistent with** ADR-003, ADR-006, and
  ADR-007, all of which are either silent or only tangentially relevant.
- The design **directly contradicts** two explicit statements in the algorithm
  spec (`08_algorithm_revised.md` Section 9 and Section 12) that say
  aggregation inputs should be resolved via "direct construction from
  `ScopedAggregationData`," NOT through the OutputRegistry.
- The design **extends** ADR-008 by adding a new key format (Key_E_stripped)
  not defined in the registry's key table, and by expanding the registry's
  role from "binding resolution" to also cover "aggregation input resolution."
- The algorithm spec's stated approach ("direct construction") is the one
  that's broken in practice — it produces wrong channels for aggregation
  targets and fails on PartDef-to-PartUsage name mismatches. The design's
  approach (registry-first) is correct but undocumented.
- Two of three issues are **bugs** (code produces wrong results). One is a
  **gap** (missing key format). All three require architecture doc updates
  after implementation.

---

## ADR Relevance Map

| ADR | Relevance | Position on Design Changes |
|-----|-----------|---------------------------|
| **ADR-008** (OutputRegistry) | Critical | Partially contradicted — registry scope expanded beyond spec |
| **ADR-007** (Aggregation) | High | Silent on input resolution mechanics |
| **08_algorithm_revised.md** | Critical | Explicitly contradicted — says registry NOT for aggregation inputs |
| **ADR-003** (Signal Identifiers) | Medium | Consistent — design operates in registry key space, not ADR-003's EQN space |
| **ADR-006** (Part Hierarchy) | Medium | Consistent — implicitly creates the name-mismatch problem the design fixes |
| **ADR-002** (Calculation Architecture) | Low | Defines aggregation expression rules at modeling level, silent on resolution |
| **ADR-004** (Computed Attributes) | Low | Confirms OutputRegistry as sole binding resolution; does not discuss aggregation |
| ADR-001, ADR-005 | None | Not relevant to aggregation input resolution |

---

## Detailed Findings

### Finding 1: The Algorithm Spec Explicitly Contradicts the Design

The algorithm spec (`08_algorithm_revised.md`) contains two statements that
directly contradict the design's approach of using the OutputRegistry for
aggregation input resolution.

**Section 9, Step 7 sub-step 3** (line 1101-1104):

> 3. **Build aggregation modules** (Family 3) directly from
> `ScopedAggregationData` (NOT through the OutputRegistry -- aggregation
> modules construct their input channels from pre-scoped data. The
> OutputRegistry is for *binding* resolution in Step 6, not for all channel
> construction.)

**Section 12, Scope Clarification** (line 1240-1243):

> **Scope clarification:** The OutputRegistry is the single mechanism for
> *binding* resolution from CHAIN source_paths and alias lookups. It is NOT
> the universal channel construction mechanism. Aggregation modules construct
> their input channels directly from `ScopedAggregationData` (Step 7).
> REFERENCE bindings use the backtracker's secondary resolution + design
> attribute fallback (Step 6).

Both statements say:
1. The OutputRegistry is for **binding resolution** (Step 6), not for
   **aggregation input resolution** (Step 7)
2. Aggregation modules should construct input channels **directly** from
   `ScopedAggregationData`

The design's Change 1 (scoped registry lookup) and Change 3 (SingletonTerm
registry-first) both do the opposite: they make the OutputRegistry the
**primary** resolution mechanism for aggregation inputs.

**Assessment: The algorithm spec is wrong, not the design.** The "direct
construction" approach described in the spec is what the current code
attempts via two mechanisms:

1. **CHAIN redef search** (graph_builder.py:789-813): Searches raw
   `RedefinitionData` objects to find `:>> capital_cost = cost_model.total_cost`
   chains, then directly constructs the channel name. This works for 8/12
   inputs but fails when `sanitize_name(PartDefName).lower() != PartUsageName`
   (the CHAIN_PART_MISMATCH case).

2. **Direct channel construction** (graph_builder.py:930-941): For
   SingletonTerms, builds `get_channel_name(instance_path__prefix, output)`.
   This assumes CalcUsage EQN format and produces wrong channels for
   aggregation targets (where the channel is `module_eqn__attr`, and
   `module_eqn` already includes the attribute name).

Both "direct construction" mechanisms are fragile or incorrect. The registry
already has the correct mappings registered (via Phase 1b and Phase 2) — the
graph builder just doesn't use them.

The prior research report (`20260215-225131_aggregation-wiring-gap-analysis.md`)
identified this contradiction in Recommendation #4:

> Update 08_algorithm_revised.md Section 9 (Step 7) to document that
> aggregation module inputs resolve via the OutputRegistry (scoped keys),
> not via direct RedefinitionData search. The current document's Section 12
> says the registry is "NOT the universal channel construction mechanism"
> for aggregation — that caveat should be narrowed after the fix.

**Impact on the design:** The design is architecturally correct but needs
corresponding doc updates. The algorithm spec's scope clarification was written
during the OutputRegistry cut-over (Item 4) when aggregation module building
was considered a separate, independent subsystem. The spike data proves this
separation doesn't hold — the aggregation builder needs the registry for the
same reasons the backtracker does.

---

### Finding 2: ADR-008 Does Not Define Key_E_stripped

ADR-008 Decision 2 defines the Phase 1 registration key formats in a table:

| Phase | Source | Lookup Keys |
|-------|--------|-------------|
| 1 | CalcUsage outputs | Key_A: `instance.output`, Key_B: EQN, Key_C: dotted hierarchy path |
| 1 | Aggregation outputs | Key_D: `part_usage.attr`, Key_E: full dotted path |

Key_C is defined precisely (line 39):

> Key_C (`".".join(EQN.split("__")[1:]) + "." + output_attr_name`) is
> critical: all Phase 2 CHAIN aliases resolve exclusively via Key_C against
> virtual CalcUsage outputs

Key_C **strips the design prefix** (segments[0]) from the EQN and joins with
dots. This is the exact algorithm the design's Change 2 applies to aggregation
outputs — but ADR-008 only defines this stripped format for CalcUsage outputs,
not for aggregation outputs.

**The asymmetry:**

| Output Type | Full Path Key | Prefix-Stripped Key |
|-------------|---------------|---------------------|
| CalcUsage   | Key_B (EQN) | Key_C (strips segments[0], joins with `.`) |
| Aggregation | Key_E (full dotted, includes design prefix) | **Not defined** |

The design's Key_E_stripped fills the missing cell:

```
Key_E:          "SolarBatteryDesign.solar_battery_plant.solar_array.capital_cost"
Key_E_stripped: "solar_battery_plant.solar_array.capital_cost"
Key_C analogy:   strips segments[0], joins remaining with "."
```

This is needed because:
- A plant-level aggregation (`instance_path = "SolarBatteryDesign__solar_battery_plant"`)
  referencing sub-assembly `"solar_array.capital_cost"` constructs scoped key
  `"solar_battery_plant.solar_array.capital_cost"` (Change 1's algorithm).
- Key_D (`"solar_array.capital_cost"`) is too short — it omits the plant scope
  and can collide across assemblies.
- Key_E (`"SolarBatteryDesign.solar_battery_plant.solar_array.capital_cost"`)
  is too long — it includes the design prefix, which the scoped lookup strips.

**Assessment: This is a gap, not a bug.** ADR-008 defines Key_C for CalcUsage
outputs but nobody defined the analogous format for aggregation outputs. The
code faithfully implements what ADR-008 specifies (Key_D and Key_E only). The
design adds the missing intermediate format.

---

### Finding 3: ADR-007 Is Silent on Input Resolution Mechanics

ADR-007 (Parametric Multiplicity and Aggregation) focuses on the **output
side** of aggregation — how `sum()` expressions are detected, decomposed, and
transformed. On the input resolution side, it provides only a single sentence
in Decision 2 (line 44):

> 3. **Resolve**: Map `part_usage_name.attribute_name` through `:>>`
> redefinition chains to find the upstream MODULE_OUTPUT channel

This describes the conceptual resolution but specifies no mechanism — it
doesn't say whether to use the OutputRegistry, raw RedefinitionData search,
direct channel construction, or what priority order to try them in.

ADR-007 Decision 4 defines the three term types (sum_terms, singleton_terms,
local_terms) but says nothing about how their input channels are resolved at
graph-build time. The word "fallback" does not appear in the document. The
resolution priority logic (CHAIN first, then registry, then direct
construction) is not discussed.

The References section (line 97, updated 2026-02-15) adds:

> The graph builder's `_build_aggregation_module()` receives `OutputRegistry`
> directly for channel verification and lookup.

This cross-reference acknowledges the registry is involved but doesn't specify
how — "verification and lookup" is vague enough to cover both the current
approach (registry as fallback) and the design's approach (registry as primary).

**Assessment: Gap.** ADR-007 should be extended with a section on aggregation
input resolution strategy after the fix is implemented. The spec's Decision 2
step 3 ("Map through `:>>` redefinition chains") could be updated to say
"Map via OutputRegistry scoped lookup (primary) or `:>>` redefinition chain
search (fallback)."

---

### Finding 4: ADR-006 Implicitly Creates the Name-Mismatch Problem

ADR-006 (Part Hierarchy and Template Instantiation) defines how template
CalcUsages are instantiated into virtual CalcUsages with hierarchy-aware
qualified names. Decision 2 (line 41):

> `PV Module.cost_model` (template) + `solar_array.pv_module` (PartUsage)
> -> virtual CalcUsage
> `SolarBatteryDesign__solar_battery_plant__solar_array__pv_module__cost_model`

This establishes that virtual CalcUsage EQNs use **PartUsage names** (from the
design hierarchy), not PartDef names. The CHAIN redef search in the graph
builder (line 795) compares `sanitize_name(redef_part_name).lower()` against
`part_usage.lower()` — where `redef_part_name` comes from the PartDef's
owning_part_qn and `part_usage` comes from the SumTerm's dotted reference.

When these names differ (e.g., PartDef `String_Inverter` vs. PartUsage
`inverter`), the CHAIN search fails. ADR-006 describes what CHAIN should
resolve to but does not describe the mechanism by which CHAIN source paths
(which reference PartDef-scoped names) are translated into registry keys
(which use PartUsage-scoped names).

**Assessment: Gap.** ADR-006 doesn't mention name mismatches or their
consequences. The PartDef-to-PartUsage naming asymmetry is an inherent
property of SysML, and the CHAIN search's `sanitize_name().lower()` comparison
is a best-effort heuristic that breaks for non-trivially-named parts. The
design's scoped registry lookup sidesteps this entirely — Phase 2 CHAIN
aliases are constructed using `find_instance_paths_for_partdef()`, which
correctly maps PartDefs to their actual PartUsage instance paths.

---

### Finding 5: ADR-003 Is Consistent but in a Different Domain

ADR-003 defines the `__`-separated identifier taxonomy (EQN, PQN, module
name, channel name). The design's scoped key construction operates in the
**dot-separated registry key space**, not in ADR-003's `__`-separated
identifier space. These are different domains:

| Domain | Separator | Example | Defined In |
|--------|-----------|---------|------------|
| EQN/PQN | `__` | `SolarBatteryDesign__solar_battery_plant__solar_array__capital_cost` | ADR-003 |
| Registry keys | `.` | `solar_battery_plant.solar_array.capital_cost` | ADR-008 |

The design's scoped key algorithm (strip segments[0], join with `.`) converts
from the EQN domain to the registry key domain — the same transformation that
`OutputRegistry.derive_key_c()` performs for CalcUsage outputs. ADR-003 is
silent on this transformation because it doesn't cover registry key formats.

The "double-attr" channel format for aggregation outputs (e.g.,
`Design__plant__solar_array__capital_cost__capital_cost`) is not discussed
in ADR-003. All ADR-003 examples show standard CalcUsage channels where the
output attribute appears once. The double-attr pattern arises from the
aggregation module EQN convention (`instance_path__attr`) combined with the
standard PQN channel naming (`eqn__output_attr`), producing
`instance_path__attr__attr`. This is correct per ADR-003's rules but is a
non-obvious consequence that ADR-003 doesn't call out.

**Assessment: No conflict.** ADR-003 defines identifiers; the design operates
on registry keys. The double-attr pattern is a valid consequence of ADR-003
+ ADR-007 but is undocumented as a named pattern.

---

### Finding 6: ADR-002 Defines Aggregation at the Modeling Level

ADR-002's "Hierarchy Pattern Relaxations" amendment (lines 691-707) codifies
that PartDef attributes may use `:>>` redefinition with aggregation
expressions combining `sum()` of child costs and direct child attribute
references:

> **Relaxation**: PartDef attributes MAY use `:>>` redefinition with
> aggregation expressions combining `sum()` of child costs and direct child
> attribute references.

This directly corresponds to **SumTerm** and **SingletonTerm** in the
implementation. However, ADR-002 treats aggregation at the modeling-rule level
— it says what SysML patterns are permitted, not how the codegen resolves
them. It does not discuss OutputRegistry key formats, scoped vs. unscoped
keys, or instance_path construction.

**Assessment: No conflict.** ADR-002 is relevant context but doesn't
constrain the design's implementation choices.

---

## Bug vs. Gap Classification

### Issue 1: Unscoped Registry Lookup — BUG

**What happens:** `_resolve_aggregation_input_channel()` constructs Key_D
(`"pv_module.capital_cost"`) for registry lookup. This key never matches any
registry entry (spike data: 0/12 hits).

**Is the code inconsistent with intended design?** Yes, but in a nuanced way.
The algorithm spec says the registry shouldn't even be used here ("direct
construction from ScopedAggregationData"). The code uses the registry anyway,
but with the wrong key format. So:

- **The registry lookup is a bug** — it uses an unscoped key that never
  matches.
- **The algorithm spec is also wrong** — the "direct construction" approach
  it prescribes (the CHAIN redef search) fails for 4/12 inputs due to
  PartDef/PartUsage name mismatches.

The code has a **bug** (broken lookup). The architecture has a **gap** (it
prescribes an approach that doesn't work for all cases and doesn't define
the fallback).

**Relevant docs:**
- `08_algorithm_revised.md` Section 9 (line 1101-1104): Contradicted by fix
- `08_algorithm_revised.md` Section 12 (line 1240-1243): Contradicted by fix
- ADR-008 Decision 5 (line 52-53): Scope needs expansion
- ADR-007 Decision 2 (line 44): Underspecified

### Issue 2: SingletonTerm Resolution Order — BUG

**What happens:** SingletonTerm processing tries direct channel construction
before registry lookup. Direct construction builds
`instance_path__prefix__output` (CalcUsage EQN format), which is wrong for
aggregation targets where the channel is `instance_path__attr__attr`.

**Is the code inconsistent with intended design?** Yes — the direct
construction algorithm doesn't account for the aggregation channel format
that the code itself creates in `_build_aggregation_module()`. When the
target is an aggregation output, the constructed channel doesn't exist in
`canonical_channels`, falls through to the (broken) registry fallback, and
ends up as an entry point.

This is a straightforward bug: the code assumes all targets use CalcUsage EQN
format, but aggregation targets use a different format. The architecture docs
are silent — ADR-007 defines SingletonTerm ("direct attribute reference via
`source_path`") but says nothing about resolution mechanics.

**Relevant docs:**
- ADR-007 Decision 4 (line 64): Defines SingletonTerm, silent on resolution
- `08_algorithm_revised.md` Section 9 (line 1101-1104): Says "direct
  construction" — the approach that's broken

### Issue 3: Missing Key_E_stripped — GAP

**What happens:** Phase 1b registers aggregation outputs with Key_D
(short, unscoped) and Key_E (full, includes design prefix). No intermediate
design-prefix-stripped key is registered.

**Is the code inconsistent with intended design?** No — the code faithfully
implements the key formats defined in ADR-008. ADR-008 defines Key_D and
Key_E for aggregation outputs and does not define a stripped variant. The code
matches the spec. The problem is that the **spec is incomplete** — it defines
Key_C (prefix-stripped) for CalcUsage outputs but not the analogous format for
aggregation outputs.

This is a pure **gap**: the architecture docs never considered the need for a
prefix-stripped aggregation key. The design adds it.

**Relevant docs:**
- ADR-008 Decision 2 (line 33): Defines Key_D and Key_E only
- ADR-008 (line 39): Defines Key_C for CalcUsage — analogous format missing
  for aggregation

---

## Summary Table

| Issue | Classification | Code Broken? | Spec Wrong/Incomplete? | Design Contradicts Spec? |
|-------|---------------|-------------|----------------------|------------------------|
| Unscoped registry lookup | **Bug** + gap | Yes (0/12 hits) | Yes (prescribes approach that fails 4/12) | Yes (expands registry role) |
| SingletonTerm order | **Bug** | Yes (wrong channel for agg targets) | Silent (no resolution mechanism specified) | Yes (registry-first vs direct-first) |
| Missing Key_E_stripped | **Gap** | No (code matches ADR-008) | Yes (missing Key_C analogue for agg) | Yes (new key format not in ADR-008) |

---

## Required Architecture Doc Updates

If the design is approved and implemented, the following documents need
updates to bring the architecture in line with the actual implementation:

### 1. `08_algorithm_revised.md` — Critical

**Section 9, Step 7 sub-step 3** (line 1101-1104): Amend to state that
aggregation input resolution uses the OutputRegistry as the primary path:

> 3. **Build aggregation modules** (Family 3) from `ScopedAggregationData`.
> Input channels are resolved via `_resolve_aggregation_input_channel()`,
> which uses the OutputRegistry (scoped key lookup, then unscoped Key_D
> fallback) as the primary resolution mechanism. CHAIN redefinition search
> and direct channel construction serve as secondary paths for CalcUsage
> targets not covered by Phase 2 aliases.

**Section 12, Scope Clarification** (line 1240-1243): Narrow the caveat:

> **Scope clarification:** The OutputRegistry is the single mechanism for
> *binding* resolution from CHAIN source_paths and alias lookups (Step 6),
> and for *aggregation input* resolution via scoped key lookup (Step 7).
> REFERENCE bindings use the backtracker's secondary resolution + design
> attribute fallback (Step 6).

### 2. ADR-008 — Major

**Decision 2 key table** (line 33): Add Key_E_stripped:

| Phase | Source | Lookup Keys |
|-------|--------|-------------|
| 1 | Aggregation outputs | Key_D: `part_usage.attr`, Key_E: full dotted path, **Key_E_stripped: prefix-stripped dotted path** |

**Decision 5** (line 52-53): Expand scope:

> `build_computation_graph()` receives the OutputRegistry. Channel existence
> checks use `registry.resolve()` and `registry.canonical_channels` (O(1)
> set membership). **Aggregation input resolution uses scoped registry
> lookup via `_resolve_aggregation_input_channel()`.**

### 3. ADR-007 — Minor

**Decision 2** (line 44): Add resolution mechanism detail:

> 3. **Resolve**: Map `part_usage_name.attribute_name` to the upstream
> MODULE_OUTPUT channel via OutputRegistry scoped key lookup (primary),
> CHAIN redefinition search (secondary), or direct channel construction
> (CalcUsage fallback).

**New section or References update**: Document SingletonTerm resolution order
(registry-first, then direct construction, then entry point fallback).

---

## Open Question

The design's spec explicitly puts architecture doc updates **out of scope**
(spec line 86: "Updating `08_algorithm_revised.md` documentation"). This is
pragmatic — the fix should land first, docs follow. But the doc updates
should be tracked as a follow-up work item. The algorithm spec's Section 9
and Section 12 statements will be actively misleading after the fix lands.

---

## Conclusion

The three issues break down as: **two bugs and one gap**. The bugs are in
the code (wrong key format, wrong resolution order). The gap is in the
architecture docs (missing Key_E_stripped definition). The design's fix is
architecturally sound — it aligns the aggregation builder with the same
OutputRegistry-first pattern that the backtracker uses — but it contradicts
explicit statements in the algorithm spec that were written during the
OutputRegistry cut-over before aggregation resolution was fully understood.
The spec was wrong; the design corrects it. Three architecture documents need
post-implementation updates to match.
