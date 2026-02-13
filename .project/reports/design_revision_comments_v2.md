# Design Revision Comments v2 on 08_algorithm_revised.md

**Date:** 2026-02-13
**Reviewer:** Claude
**Iteration:** 2 (follows spike-backed iteration 1 and design update)
**Document under review:** `.project/reports/08_algorithm_revised.md` (post-iteration-1 update)
**Context:** Iteration 1 resolved Issues 1-5, 7-8 via Spikes 1-4. Issue 6 remains open.
This review focuses on implementation-blocking gaps discovered during deeper analysis.

---

## What Iteration 1 Resolved Well

The design document was updated to incorporate all four spike results cleanly:

- OutputRegistry.resolve() now handles only DOTTED and SYSML_QN (no bare names)
- EXPOSE_PURE alias construction correctly uses `references` field
- 4-phase registration protocol is explicit and ordered
- Aggregation scoping runs in Step 3.5, Step 5 only registers
- Source_path formats are empirically grounded (94 bindings, 3 models)

The design is now much stronger than before iteration 1. The remaining issues are
specification gaps that would surface during implementation -- better to find them now.

---

## Issue 9: `:>>` CHAIN alias canonical_name is bare -- can't resolve in OutputRegistry

**Severity: Blocks Phase 2 alias registration.**

Section 4, Step 3.5(D) shows `:>>` CHAIN redefinitions producing ChannelAlias objects:

```python
ChannelAlias(
    alias_name="total_capex",       # the alias
    canonical_name="capital_cost",   # the target -- BARE NAME
    owning_part_qn=...,
    source="redefinition",
)
```

Then in Section 6 (Step 5), Phase 2 registration does:

```python
canonical_channel = registry.resolve(alias.canonical_name)
# registry.resolve("capital_cost")
```

But `"capital_cost"` is a bare name. The OutputRegistry doesn't register or resolve
bare names (Spike 4 finding, correctly implemented). So this returns `None`, and the
alias silently fails to register with a warning.

**The problem:** `:>>` CHAIN redefinitions like `:>> total_capex = capital_cost`
reference sibling attributes by **bare name** (as written in SysML). But the
OutputRegistry only contains dotted and EQN keys. `"capital_cost"` doesn't match
`"solar_array.capital_cost"` (dotted) or any EQN format.

**Why it wasn't caught in iteration 1:** The spikes tested binding source_paths
(which ARE always dotted or SYSML_QN). `:>>` redefinition RHS values come from a
different parser path -- they're hierarchy-level attributes, not binding source_paths.

**Two possible fixes:**

**(A) Scope the canonical_name at ChannelAlias construction time (recommended):**

When building the ChannelAlias in Step 3.5(D), use the design instance context to
construct a scoped dotted path:

```python
# During Step 3.5, we know the owning PartDef and the design instance path.
# For each :>> CHAIN redefinition:
ChannelAlias(
    alias_name=f"{instance_path}.{redef.attribute_name}",    # "solar_array.total_capex"
    canonical_name=f"{instance_path}.{redef.source_path}",   # "solar_array.capital_cost"
    owning_part_qn=...,
    source="redefinition",
)
```

This requires knowing the design instance path at Step 3.5 time. Since aggregation
scoping already maps PartDef -> instance paths in Step 3.5, this information is available.

**(B) Expand resolve() to do suffix matching:**

Add a resolution step that strips leading segments and tries suffix match. This is
fragile and reintroduces the ambiguity problem we just eliminated.

**Recommendation:** Option (A). The canonical_name should be a resolvable key at
construction time, not left as a bare name for the registry to guess about.

**Spike needed:** Spike 6 (below) to verify what `:>>` CHAIN redefinition RHS
values actually contain.

> **UPDATE (2026-02-13, Spike 6 results):** Confirmed. CHAIN redefinition
> source_paths come in two formats:
>
> - **DOTTED (76%, 41/54):** PartDef-local dotted paths like `cost_model.total_cost`.
>   These reference sibling CalcUsage outputs and need instance_path scoping.
> - **BARE (24%, 13/54):** CAS category codes like `CAS220101`. These are **string
>   literal values** assigned to `cas_category` attributes, NOT channel references.
>   They are misclassified as CHAIN by the hierarchy resolver.
>
> Key additional facts:
> - `expression_text` is **empty** for all CHAIN redefs (source_path is reliable)
> - `expression_ast` is **None** for all CHAIN redefs
> - Zero CHAIN design_overrides exist (all 13 design overrides are LITERAL)
> - e2e_attr_expr has **zero** hierarchy data (no PartDefs with redefinitions)
>
> **Resolution: Adopt Option (A) with two additions:**
> 1. **Filter out BARE non-reference redefs** at alias construction time:
>    `if "." not in redef.source_path: continue` (skips CAS codes, enums, etc.)
> 2. **Scope DOTTED canonical_names** with instance_path prefix:
>    `canonical_name = f"{instance_path}.{redef.source_path}"`
>    `alias_name = f"{instance_path}.{redef.attribute_name}"`
>
> Instance path is available from aggregation scoping (already runs in Step 3.5).
> **CLOSED -- ready to implement.**

---

## Issue 10: `_resolve_to_design_attribute()` is unspecified

**Severity: Blocks backtracker refactoring.**

The design shows the backtracker flow (Section 7):

```python
channel = self._output_registry.resolve(binding.source_path)
if channel is not None:
    ... # MODULE_OUTPUT
else:
    design_attr = self._resolve_to_design_attribute(binding.source_path)
    if design_attr:
        ... # ENTRY_POINT with design attribute default
    else:
        ... # ENTRY_POINT (unresolved, with warning)
```

The `_resolve_to_design_attribute()` method is referenced but never specified.
The current backtracker has ~4 strategies for design attribute resolution
(strategies 3-6 in the cascade from Section 6 of Report 06). Which survive?

**Key questions:**

1. **What index does it use?** The current code has `_design_attr_binding_index`
   (dotted paths from design attribute bindings). Does this survive? Is it part
   of the backtracker or the OutputRegistry?

2. **What key formats does it handle?** REFERENCE bindings arrive as SYSML_QN
   (e.g., `SolarBatteryLibrary::'PV Module'::cost_model::wattage`). The current
   code normalizes `::` to `.`, strips quotes, tries bare-name fallback across
   all design files. Which of these survive?

3. **Is it design attribute -> ENTRY_POINT only?** Or can design attributes
   transitively resolve to MODULE_OUTPUT (the two-hop case from Issue 3)?
   Issue 3's resolution was to handle transitive cases via Phase 4 aliases
   in the OutputRegistry. If Phase 4 works correctly, then
   `_resolve_to_design_attribute()` only needs to handle true entry points
   (literal-valued design attrs). This simplifies it significantly.

**Proposed specification:**

```python
def _resolve_to_design_attribute(self, source_path: str) -> DesignAttributeData | None:
    """Resolve source_path to a literal-valued design attribute.

    This is the ENTRY_POINT fallback. It only fires when the OutputRegistry
    returns None (not a module output or alias).

    Transitive design attrs (whose default_value is a dotted path pointing to
    a module output) are handled by Phase 4 OutputRegistry aliases and never
    reach this method.

    Resolution:
    1. Extract leaf name from source_path (last segment after :: or .)
    2. Search design_attrs by (parent_path, leaf_name) match
    3. If match and default_value is a literal -> return it
    4. If no match -> return None (becomes unresolved ENTRY_POINT with warning)
    """
```

**This needs to be added to Section 7 of the design.**

> **UPDATE (2026-02-13, Spike 5 results):** Spike 5 provides the data to
> complete this specification.
>
> - **119 REFERENCE -> ENTRY_POINT** cases across all models, all use SYSML_QN
>   source_path. These are the primary consumer of `_resolve_to_design_attribute()`.
> - **4 REFERENCE -> MODULE_OUTPUT** cases exist (computed attributes). These
>   resolve through the computed attribute index in the current backtracker,
>   NOT through design attribute resolution.
>
> The proposed specification is correct with one refinement: transitive design
> attributes (Phase 4 aliases) are already handled by the OutputRegistry before
> `_resolve_to_design_attribute()` fires. So this method only needs to handle
> literal-valued design attrs.
>
> **Resolution algorithm:**
> 1. Extract leaf name from SYSML_QN source_path (last segment after `::`)
> 2. Strip quotes from leaf name (SysIDE uses `'PV Module'` format)
> 3. Search design_attrs by `(parent_path, leaf_name)` match
> 4. If match with literal default_value -> return it (ENTRY_POINT)
> 5. If no match -> return None (becomes unresolved ENTRY_POINT with warning)
>
> The 4 REFERENCE -> MODULE_OUTPUT cases must be handled BEFORE this fallback
> (see Issue 11 update for mechanism).
>
> **CLOSED -- add specification to Section 7.**

---

## Issue 11: Do REFERENCE bindings ever resolve to MODULE_OUTPUT?

**Severity: Determines whether SYSML_QN normalization in resolve() is exercised.**

The OutputRegistry's `resolve()` method has a SYSML_QN normalization step:

```python
if "::" in source_path:
    normalized = source_path.replace("::", "__")
    if normalized in self._index:
        return self._index[normalized]
    if normalized.lower() in self._index:
        return self._index[normalized.lower()]
```

This code assumes that some binding source_paths in SYSML_QN format need to resolve
to MODULE_OUTPUT channels. But from Spike 1:

- All CHAIN bindings use DOTTED format -> resolved by exact match (step 1)
- All REFERENCE bindings use SYSML_QN format -> resolved by... what?

**The key question:** Do REFERENCE bindings ever point to CalcUsage outputs
(MODULE_OUTPUT), or do they always point to design attributes (ENTRY_POINT)?

If REFERENCE bindings **always** resolve to ENTRY_POINT:
- The `::` normalization in `resolve()` is dead code for MODULE_OUTPUT resolution
- It would only be useful for Phase 4 transitive aliases (if design attrs have SYSML_QN defaults)
- The OutputRegistry could be simplified

If REFERENCE bindings **sometimes** resolve to MODULE_OUTPUT:
- The `::` normalization is critical
- But `source_path.replace("::", "__")` produces strings like
  `SolarBatteryLibrary__'PV Module'__cost_model__wattage` (with quotes and spaces)
- These won't match EQN-format registered keys (which use snake_case, no quotes)
- The normalization is **broken** for this case

**Either way, there's a problem.** If REFERENCE -> MODULE_OUTPUT never happens, the
normalization is dead code. If it does happen, the normalization is insufficient.

**Spike needed:** Spike 5 (below) to trace every REFERENCE binding through the
current backtracker and record whether it resolves to MODULE_OUTPUT or ENTRY_POINT.

> **UPDATE (2026-02-13, Spike 5 results):** SYSML_QN normalization is
> **exercised but broken**.
>
> - **4 REFERENCE -> MODULE_OUTPUT cases** exist (2 solar_battery, 2 e2e_attr_expr)
> - All 4 are **computed attributes** (`p_net_kw`, `capital_cost`, `power_mw`, `annual_om`)
> - Naive `replace("::", "__")` produces **wrong keys** in all 4 cases because:
>   - source_path contains the *consuming* usage's path (e.g., `...annualized_om::p_net_kw`)
>   - resolved channel uses the *producing* attribute's EQN (e.g., `...p_net_kw__p_net_kw`)
>   - Intermediate path segments differ
> - The current backtracker resolves these through the **computed attribute index**,
>   a parallel mechanism that won't exist in the new design.
>
> **Resolution: Remove SYSML_QN normalization from `resolve()`.**
>
> The 4 cases must be handled by a different mechanism. Two options:
>
> **(A) EXPOSE_PURE alias registration with scoped keys (recommended):**
> Phase 3 EXPOSE_PURE aliases should register with scoped dotted keys
> (e.g., `e2e_plant.p_net_kw`, not bare `p_net_kw`). The backtracker then
> handles REFERENCE bindings by extracting the leaf name from the SYSML_QN
> source_path and trying `resolve(f"{parent_context}.{leaf_name}")` as a
> secondary attempt before falling back to `_resolve_to_design_attribute()`.
>
> **(B) Keep a lightweight computed attribute lookup in the backtracker:**
> A `dict[(parent_qn, attr_name), channel]` populated from computed attribute
> data during backtracker construction. This is the closest to the current
> approach but preserves a parallel lookup outside the OutputRegistry.
>
> Option (A) keeps resolution in the OutputRegistry. Option (B) is simpler
> to implement. Either way, `resolve()` itself becomes exact-match only.
>
> **CLOSED -- remove SYSML_QN normalization, adopt (A) or (B) for 4 cases.**

---

## Issue 12: DesignAttributeData.default_value format for reference-typed attrs

**Severity: Blocks Phase 4 transitive alias registration.**

Phase 4 of the OutputRegistry does:

```python
for attr in design_attrs_with_transitive_defaults:
    canonical_channel = registry.resolve(attr.default_value)
```

This assumes `attr.default_value` is a resolvable key (dotted path like
`"component_cost.total_cost"`). But:

1. **How do we identify "design attrs with transitive defaults"?** The design doesn't
   specify the filter. A default_value of `"0.92"` is a literal. A default_value of
   `"component_cost.total_cost"` is a path. How do we distinguish them? By checking
   for `.` in the string? That would also match `"3.14"`.

2. **What format does default_value actually have?** Spike 3 showed that EXPOSE_PURE
   `expression_text` was `".(component_cost)"` (raw AST text), NOT a clean dotted path.
   If `default_value` comes from a similar parser path, it might also be raw AST text.

3. **Spike 3 showed `design_attr_binding_index` works for e2e_attr_expr:**
   `e2e_plant.total_capex -> component_cost.total_cost`. This suggests `default_value`
   IS a clean dotted path in some cases. But is this reliable across models?

**Proposed fix:** Add a filter function:

```python
def _is_transitive_default(attr: DesignAttributeData) -> bool:
    """Check if this design attribute's default_value is a module output path."""
    if attr.default_value is None:
        return False
    # Must look like a dotted path (instance.output), not a literal
    val = str(attr.default_value)
    if "." not in val:
        return False
    # Reject numeric literals like "3.14"
    try:
        float(val)
        return False
    except ValueError:
        pass
    # Attempt registry resolution -- only transitive if it resolves
    return True
```

**Spike needed:** Spike 7 (below) to check `default_value` format across models.

> **UPDATE (2026-02-13, Spike 7 results):** Phase 4 **works with actual data**.
>
> - **128 total design attributes** across 2 models
> - Classification: NUMERIC (58), NONE (68), DOTTED_PATH (**2**), everything else (0)
> - **2 transitive defaults found, both resolve successfully:**
>   - `e2e_plant.total_capex` -> default=`"component_cost.total_cost"` -> resolves
>   - `solar_battery_plant.misc_hardware_cost` -> default=`"allocation_model.total_allocation"` -> resolves
> - **0 SYSML_QN defaults** -- no `::` normalization needed for default_value
> - **0 STRING_LITERAL or AST_TEXT** -- default_value is always clean (NUMERIC, NONE, or DOTTED_PATH)
>
> The proposed filter correctly identifies both transitive defaults:
> ```python
> def _is_transitive_default(attr: DesignAttributeData) -> bool:
>     if attr.default_value is None:
>         return False
>     val = str(attr.default_value)
>     if "." not in val:
>         return False
>     try:
>         float(val)
>         return False
>     except ValueError:
>         return True
> ```
>
> **Resolution: Phase 4 works as designed. Use proposed filter. No SYSML_QN
> normalization needed for default_value resolution. CLOSED.**

---

## Issue 13: FORMULA computed attribute module input wiring is unspecified

**Severity: Important specification gap.**

Section 5 (Step 4.5) shows FORMULA computed attributes becoming pipeline modules.
Section 9 (Step 7) shows them as "Family 2: Computed Attribute Modules." But the
design never specifies **how their inputs are resolved**.

A FORMULA attribute like:

```sysml
attribute p_net_kw = p_net_mw * 1000.0
```

References sibling attributes (`p_net_mw`). When this becomes a pipeline module,
`p_net_mw` is an input. Where does it come from?

**Possible resolution paths:**

1. **`p_net_mw` is another computed attribute** -> MODULE_OUTPUT (from that attr's module)
2. **`p_net_mw` is a CalcUsage output alias** -> MODULE_OUTPUT (via EXPOSE_PURE -> registry alias)
3. **`p_net_mw` is a design attribute** -> ENTRY_POINT (user provides it)
4. **`p_net_mw` is a literal attribute** -> ENTRY_POINT (with literal default)

The design doesn't say whether FORMULA module inputs go through the OutputRegistry,
through the backtracker, or through a separate mechanism. The current implementation
creates synthetic CalcUsages for FORMULA attrs (see `expression-aware-codegen.md`
Section 3, Pattern J), which then flow through the normal backtracker pipeline. Does
the revised design preserve this approach?

**Proposed specification:**

FORMULA computed attributes produce synthetic CalcUsageData objects (as specified in
`expression-aware-codegen.md`). These synthetic CalcUsages:
- Have bindings for each referenced sibling attribute
- Use CHAIN binding type with dotted source_path (`{sibling_name}`)
- Flow through Step 6 (backtracking) like any other CalcUsage
- The OutputRegistry resolves their bindings normally

If this is the intended approach, it should be stated explicitly in the design.
If a different approach is intended, it needs specification.

> **UPDATE (2026-02-13, informed by Spikes 5+7):** Spike 5 shows all binding
> types route correctly through the backtracker pipeline. Spike 7 shows design
> attributes are simple (NUMERIC or NONE). The synthetic CalcUsage approach
> from `expression-aware-codegen.md` is the right mechanism.
>
> **Resolution: Preserve synthetic CalcUsage approach.** FORMULA computed
> attributes produce synthetic `CalcUsageData` that flow through normal
> backtracking. Their bindings use CHAIN type with dotted source_paths to
> sibling attributes. No special input wiring mechanism needed -- the
> OutputRegistry resolves their bindings normally.
>
> Add explicit statement to Section 9 (Step 7, Family 2) that FORMULA modules
> originate as synthetic CalcUsages created during Step 4.5 and their inputs
> resolve through the standard backtracker pipeline.
>
> **CLOSED -- add clarification to Section 9.**

---

## Issue 14: Aggregation module input channel resolution needs specification

**Severity: Medium. Partially specified but key details missing.**

Section 9 (Step 7) shows aggregation modules with SumTerm inputs like
`count * pv_module.cost`. The `pv_module.cost` reference needs to resolve to a
virtual CalcUsage output channel. But:

1. **`pv_module.cost` is a short dotted path.** The virtual CalcUsage output is
   registered with a full_key like
   `SolarBatteryDesign__solar_battery_plant__solar_array__pv_module__cost_model.total_cost`.
   Does `pv_module.cost` match?

2. **The short key `cost_model.total_cost` collides** (Spike 2: 9 producers).
   So the aggregation module can't resolve via short key.

3. **Aggregation modules are built from `ScopedAggregationData`** which already has
   the full instance path. So the resolution doesn't go through the OutputRegistry --
   it's built directly in Step 7 using the scoped data.

**Question:** Does the aggregation module builder use the OutputRegistry to resolve
its input channels, or does it construct them directly from ScopedAggregationData?

If directly: the OutputRegistry is NOT the single resolution mechanism (the design
says it is). If via registry: the resolution path needs to be specified for the
hierarchy-path-to-channel case.

**My read of the design:** The aggregation module builder constructs input channels
directly from the scoped data (which already has `module_eqn` and instance paths).
The OutputRegistry is used by the **backtracker** (Step 6) for CalcUsage binding
resolution. Aggregation module construction happens in Step 7 **after** the
backtracker runs, using the scoped data from Step 3.5.

If this is correct, the design should state it explicitly. The OutputRegistry is not
universal -- it's the single mechanism for **binding** resolution, not for all
channel construction.

> **UPDATE (2026-02-13, informed by Spike 6):** Spike 6 confirms aggregation
> expressions are extracted with full scoped data from Step 3.5.
> `ScopedAggregationData` already has instance paths and module EQNs.
>
> **Resolution: Aggregation module builder constructs input channels directly
> from `ScopedAggregationData`, NOT through OutputRegistry.**
>
> The OutputRegistry is the single mechanism for *binding* resolution (Step 6),
> not for all channel construction. Aggregation modules are built in Step 7
> using pre-scoped data from Step 3.5. This is analogous to how CalcUsage
> modules use `binding_resolutions` from Step 6 -- the graph builder consumes
> pre-resolved data, it doesn't re-derive.
>
> Clarify in Section 6 and Section 12: the OutputRegistry's guarantee is
> about **binding source_path resolution**, not universal channel lookup.
>
> **CLOSED -- add scope clarification to Sections 6, 9, 12.**

---

## Issue 6 (carried from v1): AggregationDecomposer Protocol

**Severity: Over-engineering. Resolution: Drop it.**

No new data from spikes. The project guidelines say "Don't create abstractions for
one-time operations." There is exactly one aggregation function (`sum`). Drop the
`AggregationDecomposer` Protocol and `SumDecomposer` class. Keep direct `sum()`
handling code with the validation the design correctly specifies (verify operands
are child-part attribute references, document uniform-array assumption as
precondition).

**Recommended resolution: CLOSED. Drop the Protocol.**

> **UPDATE (2026-02-13):** No new spike data. Iteration 2 spikes focused
> on binding resolution, not aggregation decomposition. Resolution stands
> unchanged from v1: drop the Protocol, keep direct `sum()` code with
> validation (verify operands are child-part attribute references, document
> uniform-array assumption as precondition).
>
> **CLOSED -- drop the Protocol.**

---

## Proposed Spikes for Iteration 2

### Spike 5: REFERENCE Binding Resolution Outcomes

**Question:** Do REFERENCE bindings ever resolve to MODULE_OUTPUT, or always to ENTRY_POINT?

**Addresses:** Issue 11 (SYSML_QN normalization in resolve() -- dead code or broken?)

**Script:** `scripts/spikes/spike_reference_binding_outcomes.py`

**Algorithm:**
1. Load solar_battery, e2e_attr_expr, catf_mfe, chain_spike
2. Run the full pipeline through Step 6 (backtracking)
3. For each binding in `binding_resolutions`:
   - Get the original binding's `binding_type`
   - Get the resolution's `resolution_type` (MODULE_OUTPUT or ENTRY_POINT)
   - Build a cross-tabulation: binding_type x resolution_type
4. For each REFERENCE binding that resolved to MODULE_OUTPUT (if any):
   - Print: source_path, resolution channel, which strategy resolved it

**Pass criteria:**
- Cross-tabulation for all 4 models
- Determine: is "REFERENCE -> MODULE_OUTPUT" a real scenario or zero-occurrence?
- If zero: SYSML_QN normalization in resolve() can be simplified or removed
- If nonzero: the normalization needs fixing (quotes, spaces, casing)

### Spike 6: `:>>` CHAIN Redefinition RHS Content

**Question:** What does the RHS of `:>>` CHAIN redefinitions contain? Bare name?
Dotted path? SYSML_QN? Raw AST text?

**Addresses:** Issue 9 (CHAIN alias canonical_name format)

**Script:** `scripts/spikes/spike_chain_redef_rhs.py`

**Algorithm:**
1. Load solar_battery, e2e_attr_expr
2. Run hierarchy extraction (Step 3.5)
3. For each CHAIN-type redefinition in the HierarchyExtractionResult:
   - Print: attribute_name, source_path, redefinition_type
   - Classify source_path format: BARE, DOTTED, SYSML_QN, AST_TEXT
4. Also extract the raw AST node for each CHAIN redefinition and print:
   - Type of the RHS expression
   - Referenced names from `extract_feature_refs()` (if available)

**Pass criteria:**
- Every `:>>` CHAIN RHS is classified
- Determine whether canonical_name needs scoping at alias construction time
- Determine the reliable extraction method (source_path vs references field)

### Spike 7: DesignAttributeData.default_value for Path-Like Defaults

**Question:** For design attributes whose default_value looks like a reference
(not a literal), what format does `default_value` have?

**Addresses:** Issue 12 (Phase 4 transitive alias registration)

**Script:** `scripts/spikes/spike_design_attr_defaults.py`

**Algorithm:**
1. Load solar_battery, e2e_attr_expr
2. Extract design attributes via `extract_design_attributes()`
3. For each DesignAttributeData:
   - Print: name, parent_part, default_value, sysml_type
   - Classify default_value: NUMERIC_LITERAL, STRING_LITERAL, DOTTED_PATH,
     SYSML_QN, AST_TEXT, NONE
4. For path-like default_values (DOTTED_PATH or SYSML_QN):
   - Check: does `OutputRegistry.resolve(default_value)` succeed?
   - This tests whether Phase 4 registration would work with the actual data

**Pass criteria:**
- Every design attribute default_value is classified
- Determine: are transitive defaults identifiable? What format are they in?
- Determine: does the proposed filter function work?

---

## Summary

### New issues (iteration 2)

| # | Issue | Severity | Action |
|---|-------|----------|--------|
| 9 | CHAIN alias canonical_name is bare | Blocks Phase 2 | Scope at construction time; spike RHS format |
| 10 | `_resolve_to_design_attribute()` unspecified | Blocks backtracker refactoring | Add specification to Section 7 |
| 11 | REFERENCE -> MODULE_OUTPUT? | Determines resolve() feature need | Spike 5 |
| 12 | Design attr default_value format | Blocks Phase 4 | Spike 7 |
| 13 | FORMULA module input wiring | Specification gap | Clarify synthetic CalcUsage approach |
| 14 | Aggregation module input resolution | Medium | Clarify: direct construction vs. registry |

### Carried from iteration 1

| # | Issue | Resolution |
|---|-------|-----------|
| 6 | AggregationDecomposer Protocol | **CLOSED: Drop the Protocol.** Keep direct sum() code. |

### Spikes needed

| Spike | Question | Addresses |
|-------|----------|-----------|
| 5 | Do REFERENCE bindings ever resolve to MODULE_OUTPUT? | Issue 11 |
| 6 | What format is `:>>` CHAIN redefinition RHS? | Issue 9 |
| 7 | What format is DesignAttributeData.default_value for paths? | Issue 12 |

### Expected iteration 2 outcome

After spikes 5-7 complete:
- Issue 9 has a concrete fix for CHAIN alias canonical_name construction
- Issue 11 determines whether SYSML_QN normalization in resolve() is needed/broken/dead
- Issue 12 determines whether Phase 4 transitive aliases work with actual data
- Issues 10, 13, 14 are specification gaps that can be resolved by adding text to
  the design document (no new empirical data needed)

---

## Post-Spike Status (2026-02-13)

All 6 issues from iteration 2 (plus carried Issue 6) now have UPDATE notes
with spike-backed or informed resolutions. All issues are **CLOSED**.

### Resolution Summary

| # | Issue | Resolution | Evidence |
|---|-------|-----------|----------|
| 6 | AggregationDecomposer Protocol | **Drop.** Direct sum() code with validation. | Project guidelines (no premature abstraction) |
| 9 | CHAIN alias canonical_name bare | **Scope at construction time.** Filter BARE CAS codes (no `.`), scope DOTTED with `instance_path` prefix. | Spike 6: 41 DOTTED, 13 BARE CAS codes |
| 10 | `_resolve_to_design_attribute()` unspec | **Add specification.** Extract leaf from SYSML_QN, search by (parent, leaf). Literal-valued attrs only. | Spike 5: 119 REFERENCE->ENTRY_POINT, all SYSML_QN |
| 11 | REFERENCE -> MODULE_OUTPUT? | **4 cases exist.** Remove SYSML_QN normalization from resolve() (broken). Handle via scoped EXPOSE_PURE aliases or lightweight computed attr lookup. | Spike 5: 4/123 REFERENCE->MODULE_OUTPUT, all computed attrs |
| 12 | Design attr default_value format | **Phase 4 works.** 2 transitive defaults, both DOTTED_PATH, both resolve. Filter: `"." in val and not float(val)`. | Spike 7: 128 attrs, 2 transitive |
| 13 | FORMULA input wiring | **Synthetic CalcUsage approach.** FORMULA attrs produce synthetic CalcUsageData, flow through normal backtracking. | Spikes 5+7 (indirect) |
| 14 | Aggregation input resolution | **Direct from ScopedAggregationData.** OutputRegistry is for *binding* resolution, not all channel construction. | Spike 6 (indirect) |

### Key Algorithm Document Changes Needed

1. **OutputRegistry.resolve():** Remove SYSML_QN normalization (step 2). Exact-match only.
2. **Step 3.5(C):** Drop `AggregationDecomposer` Protocol. Direct sum() code.
3. **Step 3.5(D):** CHAIN alias construction: filter BARE non-references, scope DOTTED with instance_path.
4. **Section 7 backtracker:** Add `_resolve_to_design_attribute()` specification. Add REFERENCE binding secondary resolution (leaf-name extraction + parent-scoped resolve).
5. **Section 9 (Step 7):** Clarify FORMULA modules come from synthetic CalcUsages. Clarify aggregation modules use ScopedAggregationData directly.
6. **Section 12 OutputRegistry:** Clarify scope: *binding* resolution only. Remove SYSML_QN normalization. EXPOSE_PURE aliases registered with scoped dotted keys.
7. **Migration path:** Reorder to reflect resolved issues. Remove AggregationDecomposer step.
