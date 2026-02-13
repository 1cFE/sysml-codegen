# 07: Open Issues — What Is Actually Happening

**Date:** 2026-02-13
**Purpose:** Precise, code-level accounting of design problems in the current pipeline.
Not aspirational. Not hand-wavy. What the code actually does, where it's fragile,
and what would need to change to make it solid.

---

## Table of Contents

1. [The Key Format Problem](#1-the-key-format-problem)
2. [Step 3.5 Rewrite: What It Actually Does (and Doesn't)](#2-step-35-rewrite)
3. [sum() Is Hardcoded, Not Generalized](#3-sum-hardcoded)
4. [Step 3.6 Alias Enrichment: A Patch for a Lookup Bug](#4-step-36-alias-patch)
5. [Bug 2: EXPOSE_PURE Two-Hop Failure (Same Root Cause)](#5-bug-2)
6. [The Backtracker's Index Soup](#6-index-soup)
7. [What a Clean Architecture Would Look Like](#7-clean-architecture)

---

## 1. The Key Format Problem {#1-the-key-format-problem}

Most of the issues in sections 2-6 trace back to a single architectural problem:
**the same logical entity is identified by different key formats in different
indexes, and the code does ad-hoc format conversion to bridge the gaps.**

Here are the formats in play:

| Format | Example | Where It Appears |
|--------|---------|------------------|
| SysML qualified name | `FusionPhysics::NetElectricPower` | Binding source_path (REFERENCE type) |
| Dotted path | `alpha_split.p_alpha` | Binding source_path (CHAIN type) |
| Bare name | `wattage` | Binding source_path (PartDef-scoped ref) |
| EQN (Python QN) | `CATFMFEPhysics__catf_physics__alpha_split` | CalcUsageData.qualified_name |
| PQN (channel) | `...alpha_split__p_alpha` | Output catalog keys, channel names |
| Dotted instance.output | `alpha_split.p_alpha` | Output catalog secondary keys |

The backtracker receives bindings in the first three formats and needs to look them
up in indexes keyed by the last three formats. It bridges the gap with a cascade of
`if "." in source_path` / `if "::" in source_path` / bare-name fallback checks.

**Every time a new module family is added (computed attrs, aggregation), a new index
is created with its own key formats, and new ad-hoc bridging code is added to the
cascade.** This is the fundamental source of bugs.

---

## 2. Step 3.5 Rewrite: What It Actually Does (and Doesn't) {#2-step-35-rewrite}

### What the code does

`_rewrite_virtual_bindings()` in `initialization.py:238-294`:

```python
for usage in calc_usages:
    if usage.is_template:
        continue                    # skip templates (only process virtual copies)

    parts = usage.qualified_name.rsplit("__", 1)
    parent_path = parts[0]          # e.g., "Design__plant__solar_array"

    for binding in usage.bindings:
        if binding.binding_type == BindingType.LITERAL:
            continue                # already has a value
        if not binding.source_path:
            continue                # no source to match against
        if "." not in binding.source_path and "::" not in binding.source_path:
            # BARE NAME binding only
            key = (parent_path, binding.source_path)
            matched = override_index.get(key)
            if matched and matched.redefinition_type == RedefinitionType.LITERAL:
                binding.binding_type = BindingType.LITERAL
                binding.literal_value = matched.literal_value
```

### What this means

The rewrite ONLY fires when ALL of these are true:
1. The CalcUsage is not a template (it's a virtual copy or a normal usage)
2. The binding has a `source_path` (it's not UNBOUND)
3. The `source_path` is a **bare name** -- no dots, no `::`
4. The `(parent_path, bare_name)` matches a LITERAL design override

### Open questions

**Q: When do bare-name bindings actually occur?**

A template CalcUsage like `calc cost_model : SimpleCostCalc { in wattage = wattage; }`
inside a PartDef binds input `wattage` to the PartDef's sibling attribute `wattage`.
The SysIDE parser might produce this as:
- `source_path = "wattage"` (bare name) -- the rewrite would fire
- `source_path = "SomePackage::PV_Module::wattage"` (full SysML QN) -- the rewrite would NOT fire (has `::`)

**We have not verified which format SysIDE actually produces for this case.**
If it produces full QN format, the entire rewrite mechanism is dead code for
template bindings and only fires for some other scenario we haven't identified.

**Q: What about non-LITERAL overrides?**

The code on line 288 checks `matched.redefinition_type == RedefinitionType.LITERAL`.
CHAIN overrides (`:>> capital_cost = cost_model.total_cost`) are silently skipped.
The bare-name binding remains, and the backtracker has to deal with it later.
There is no documented reason for skipping CHAIN overrides -- it may simply be
"LITERAL was easy to implement and CHAIN was deferred."

**Q: What happens if the rewrite doesn't fire?**

The virtual CalcUsage goes to the backtracker with a bare-name binding like
`source_path = "wattage"`. The backtracker's `_resolve_binding_to_usage()` will:
1. Check the output catalog for `"wattage"` -- miss (output catalog keys are `instance.output` or EQN)
2. Check instance name match for `"wattage"` -- miss (it's not a CalcUsage name)
3. Try transitive design attr resolution -- might match if there's a design attribute named `wattage`
4. Fall through to entry point

So if the rewrite doesn't fire, the binding either gets lucky with strategy 3 or
becomes a false entry point. There's no explicit error.

### Verdict

Step 3.5's rewrite is **narrowly scoped to one specific case** (bare-name binding
matched to LITERAL override) and **we haven't verified that the prerequisite condition
(bare-name source_path) actually arises from the SysIDE parser.** The rest of Step 3.5
(redefinition extraction, multiplicities, aggregation) is sound -- it's pure extraction
with well-defined data models.

---

## 3. sum() Is Hardcoded, Not Generalized {#3-sum-hardcoded}

### What the code does

In `hierarchy_resolver.py:363-421`, the aggregation AST walker has this structure:

```python
# Line 364-368
if hasattr(node, "function") and hasattr(node.function, "name"):
    func_name = node.function.name
    operands = list(getattr(node, "operands", []))

    if func_name == "sum" and operands:
        # ... decompose into SumTerm with parametric multiply
    elif func_name in _KNOWN_WRAPPER_FUNCTIONS and operands:
        # ... unwrap Evaluation/collect/select wrappers
    else:
        ctx.has_unsupported = True  # <-- ANYTHING ELSE IS UNSUPPORTED
```

### What this means

1. **Only `sum()` is recognized.** `min()`, `max()`, `mean()`, `product()` would all
   be marked `has_unsupported_nodes = True` and produce empty term lists.

2. **Every `:>>` EXPRESSION containing `sum()` is assumed to be a parametric-multiply
   aggregation.** There's no check that the `sum()` is actually a rollup over child
   parts -- it could be `sum(a, b)` where `a` and `b` are local attributes, and
   the code would still try to decompose it into `SumTerm` with multiplicity lookup.

3. **The parametric-multiply assumption is undocumented outside ADR-007.** The transform
   `sum(child.attr)` -> `count * child.attr` assumes all instances in an array are
   identical (uniform array assumption). This is correct for the solar_battery model
   but not for heterogeneous arrays.

4. **Only `:>>` EXPRESSION redefinitions on PartDefinitions enter this path.**
   `sum()` inside a CalcDef expression body goes through the expression compiler
   (Step 6.5) which reconstructs it as literal `sum(...)` Python -- no multiplicity
   awareness. So there are two completely different code paths for `sum()` depending
   on where in the SysML model it appears. This is not documented.

### What a proper abstraction would look like

The aggregation walker should:
- Accept a registry of known aggregation functions (not just `sum`)
- Validate that the function's operands are child-part attribute references (not arbitrary expressions)
- Have a clear error path when the operands don't match the expected pattern
- Document the uniform-array assumption as a precondition, not bury it in ADR-007

---

## 4. Step 3.6 Alias Enrichment: A Patch for a Lookup Bug {#4-step-36-alias-patch}

### The scenario

```
calc def AnnualizedFinancial {
    in total_capex : Real;           // CalcDef author chose this name
}

calc annualized : AnnualizedFinancial {
    in total_capex = solar_battery_plant.capital_cost;
    //  ^^^^^^^^^^^  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    //  param_name   source_path
}
```

The binding's `param_name` is `"total_capex"`. The binding's `source_path` is
`"solar_battery_plant.capital_cost"`. These are different names because the CalcDef
author and the assembly designer chose different names for the same concept.

### Why this is a problem

The backtracker should resolve this binding by looking up `source_path`
(`"solar_battery_plant.capital_cost"`) in the aggregation output index. And in fact,
the aggregation output index DOES have a key for this -- Key 3 in the index builder
(backtracker.py:183-187):

```python
# Key 3: full instance path dotted
dotted_path = ".".join(instance_parts + [agg.expression.attribute_name])
self._aggregation_output_index[dotted_path] = channel
```

This would produce `"solar_battery_plant.capital_cost"` as a key. So the lookup
`_aggregation_output_index.get("solar_battery_plant.capital_cost")` should
succeed directly at line 472-473:

```python
agg_channel = self._aggregation_output_index.get(binding.source_path)
```

**If the direct lookup works, why do we need aliases at all?**

The answer is that Step 3.6 was added for a different scenario -- where the
binding's `source_path` uses the ALIAS name, not the canonical name. For example,
if the CalcUsage binding says:

```
in total_capex = solar_battery_plant.total_capex;
//                                   ^^^^^^^^^^^
//                                   This is the ALIAS, not "capital_cost"
```

In this case, `source_path = "solar_battery_plant.total_capex"` and the index
only has `"solar_battery_plant.capital_cost"`. The direct lookup fails.

But here's the thing: **if that's the scenario, then the modeler used a `:>>` alias
name in a CHAIN binding.** The `:>>` on the PartDef says `:>> total_capex = capital_cost`,
which creates the alias `total_capex` for `capital_cost`. When a CalcUsage binds
to `solar_battery_plant.total_capex`, it's using the aliased name.

### What Step 3.6 actually does

`_enrich_aliases_from_bindings()` at initialization.py:297-343:

```python
for usage in calc_usages:
    for binding in usage.bindings:
        source_leaf = binding.source_path  # extract leaf after :: or .

        if source_leaf not in agg_by_attr:   # leaf matches an aggregation attr?
            continue
        if binding.param_name == source_leaf: # param name differs from source?
            continue

        for agg in agg_by_attr[source_leaf]:
            agg.aliases.append(binding.param_name)  # add param_name as alias
```

Then in the backtracker constructor (backtracker.py:189-197):

```python
for alias_name in getattr(agg.expression, "aliases", []):
    self._aggregation_output_index[f"{part_usage_name}.{alias_name}"] = channel
    if alias_name not in self._aggregation_output_index:
        self._aggregation_output_index[alias_name] = channel
    dotted_alias = ".".join(instance_parts + [alias_name])
    self._aggregation_output_index[dotted_alias] = channel
```

So it adds `total_capex` as a key in the aggregation output index, mapping to the
same channel as `capital_cost`.

### Why this is a patch, not a design

1. **The alias is derived from CalcUsage binding param_names.** The code scans ALL
   CalcUsage bindings looking for `param_name != source_leaf`. This is fragile --
   it will create spurious aliases whenever a CalcDef input has a different name
   than the attribute it binds to, even if there's no `:>>` redefinition involved.

2. **There's already a first-class alias source that's partially used.** In
   `hierarchy_resolver.py:536-544`, the hierarchy extractor already detects
   `:>> CHAIN` redefinitions and adds aliases:

   ```python
   for sibling in redefs:
       if (sibling.redefinition_type == RedefinitionType.CHAIN
           and sibling.source_path.endswith(agg.attribute_name)
           and sibling.attribute_name != agg.attribute_name):
           agg.aliases.append(sibling.attribute_name)
   ```

   So there are **two independent alias detection systems** for the same purpose:
   - The hierarchy extractor finds aliases from `:>>` CHAIN redefinitions (correct source)
   - Step 3.6 finds aliases from CalcUsage binding param_names (heuristic workaround)

3. **The alias lives on `AggregationExpressionData`, not a general registry.**
   If a non-aggregation output needs an alias (e.g., a CalcUsage output known by
   two names), this mechanism can't help. It's aggregation-specific.

### Verdict

Step 3.6 is a **workaround for bindings that use `:>>` alias names instead of
canonical attribute names.** The correct fix is:
- The hierarchy extractor's `:>>` CHAIN alias detection (already exists) should be sufficient
- If it's not sufficient, the gap is in HOW the alias names get into the aggregation
  output index, not in WHERE the aliases are discovered
- The CalcUsage param_name scan (Step 3.6) is a heuristic that happens to work but
  is semantically wrong -- param_name divergence is not evidence of aliasing

---

## 5. Bug 2: EXPOSE_PURE Two-Hop Failure (Same Root Cause) {#5-bug-2}

### The scenario

From `.project/research/20260213-152845_bug2-expose-calcusage-wiring-persistent-failure.md`:

```
part SolarBatteryDesign {
    attribute total_capex = component_cost.total_cost;
    //        ^^^^^^^^^^   ^^^^^^^^^^^^^^^^^^^^^^^
    //        EXPOSE_PURE   CalcUsage output reference
}

calc annualized : AnnualizedFinancial {
    in total_capex = total_capex;
    //               ^^^^^^^^^^
    //               References the EXPOSE_PURE attribute
}
```

### What should happen

1. `total_capex` is classified as EXPOSE_PURE (Step 4.5): it's a bare alias for
   `component_cost.total_cost`
2. The backtracker sees binding `source_path = "total_capex"` (bare name)
3. The backtracker should resolve: `total_capex` -> EXPOSE_PURE -> `component_cost.total_cost` -> MODULE_OUTPUT

### What actually happens

1. The computed attr index has `total_capex` -> `ComputedAttributeData(classification=EXPOSE_PURE)`
2. The backtracker checks `_computed_attr_index.get("total_capex")` at line 449 -- **HIT**
3. But EXPOSE_PURE attrs don't generate modules. `_build_computed_attr_channel()` builds
   a channel name for a module that doesn't exist.
4. The binding resolves to `MODULE_OUTPUT` pointing to a nonexistent channel.
5. The graph builder crashes or produces broken wiring.

Actually wait -- looking at the code more carefully at lines 458-469:

```python
if ca is not None:
    channel = self._build_computed_attr_channel(ca)
    self._binding_resolutions[mapping_key] = BindingResolution(
        resolution_type=BindingResolutionType.MODULE_OUTPUT,
        qualified_name=channel,
    )
    continue  # No recursive tracing
```

There's **no check for EXPOSE_PURE vs FORMULA classification.** The code treats all
computed attributes identically -- it builds a channel name and wires to it. But only
FORMULA attrs get synthetic modules. EXPOSE_PURE attrs are supposed to be aliases
(channel renames), not modules.

### The root cause

This is a missing classification check in the backtracker. The fix should be:

```python
if ca is not None:
    if ca.classification == ComputedAttributeClassification.FORMULA:
        # Wire to the FORMULA module's output channel
        channel = self._build_computed_attr_channel(ca)
        ...
    elif ca.classification == ComputedAttributeClassification.EXPOSE_PURE:
        # Transitive resolution: follow the alias to its target
        # ca.expression_text is "component_cost.total_cost"
        # Re-resolve THAT as a binding source_path
        ...
```

This is **the same key-format-mismatch problem** from Section 1. The EXPOSE_PURE's
target (`component_cost.total_cost`) is in dotted format. Resolving it requires
looking it up in the output catalog (which uses dotted secondary keys) or the
aggregation output index. The two-hop resolution is just two iterations of the
same format-bridging problem.

---

## 6. The Backtracker's Index Soup {#6-index-soup}

The backtracker constructor builds FIVE separate indexes:

```
1. _computed_attr_index      dict[str, ComputedAttributeData]
   Keys: "part.attr", "attr", "Package::Part::attr"

2. _aggregation_output_index dict[str, str]
   Keys: "part.attr", "attr", "path.part.attr", "part.alias", "alias", "path.part.alias"

3. _output_catalog           dict[str, CalcUsageData]
   Keys: "usage_qn__output" (primary), "instance.output" (secondary)

4. _design_attr_binding_index dict[str, str]
   Keys: dotted paths from design attribute bindings

5. _usage_by_name / _usage_by_qualified  dict[str, CalcUsageData]
   Keys: instance_name (collision-prone), qualified_name (unique)
```

Then `_trace_dependencies()` checks them in this order for each binding:

```
binding.source_path
    |
    v
1. _computed_attr_index.get(source_path)
   miss? try bare name after "." split
   miss? try bare name after "::" split
    |
    v
2. _aggregation_output_index.get(source_path)
   miss? try bare name after "." split
   miss? try sanitized "::" -> dotted conversion
    |
    v
3. _resolve_binding_to_usage(source_path)
   which internally does:
   3a. _output_catalog.get(source_path)
   3b. _usage_by_name.get(instance_name) + output check
   3c. _design_attr_binding_index transitive
   3d. Design attr bare name match across files
   3e. _usage_by_name.get(source_path)
   3f. Normalize :: -> __ and retry design attr
    |
    v
4. Fallback: ENTRY_POINT
```

That's **at least 12 different lookup attempts** with at least 4 different key
format conversions, spread across ~200 lines of code. Each new module family
(computed attrs, aggregation) added its own index and its own set of format
conversions grafted onto the top of the cascade.

### Why this matters

- **No single place defines "how do I resolve a source_path to a channel."**
  The logic is spread across the cascade, and the order matters.
- **Adding a new module family requires modifying the cascade**, adding a new
  index, and figuring out what key formats the new module's outputs will be
  referenced by.
- **Failures are silent.** If none of the 12 lookups match, the binding becomes
  an entry point with no warning. The generated pipeline will have a JSON input
  where it should have module wiring, and the only way to detect it is to
  manually inspect the pipeline YAML.

---

## 7. What a Clean Architecture Would Look Like {#7-clean-architecture}

The issues in sections 1-6 share a common pattern: **multiple indexes with
incompatible key formats, patched together with ad-hoc format conversions.**

A cleaner design would have:

### (A) A single output registry

One data structure that maps ALL possible names for a module output to its
canonical channel name:

```python
class OutputRegistry:
    """Single registry for all pipeline outputs."""

    def register(self, channel: str, aliases: list[str]) -> None:
        """Register a channel with all its lookup aliases."""
        for alias in aliases:
            self._index[alias] = channel

    def resolve(self, source_path: str) -> str | None:
        """Look up any source_path format. Returns canonical channel or None."""
        # Try exact match first
        if source_path in self._index:
            return self._index[source_path]
        # Try known normalizations
        for normalized in self._normalize(source_path):
            if normalized in self._index:
                return self._index[normalized]
        return None
```

Every module family (CalcUsage, computed attr, aggregation) would register its
outputs with ALL the formats a binding might reference them by. The backtracker
would call `registry.resolve(binding.source_path)` once, instead of cascading
through 12 lookups.

### (B) Explicit alias tracking

Instead of inferring aliases from CalcUsage param_name divergence, aliases
would be an explicit first-class concept:

```python
@dataclass
class ChannelAlias:
    alias_name: str          # "total_capex"
    canonical_channel: str   # "...capital_cost__capital_cost"
    source: str              # ":>> redefinition" or "EXPOSE_PURE"
```

The hierarchy extractor and computed attribute classifier would both produce
`ChannelAlias` objects. The output registry would consume them.

### (C) EXPOSE_PURE as transitive alias, not dead classification

EXPOSE_PURE computed attributes should produce `ChannelAlias` entries, not get
stored in `_computed_attr_index` where they're indistinguishable from FORMULA
attrs. The current code treats them identically, which is Bug 2.

### (D) Aggregation function registry

Instead of hardcoding `func_name == "sum"`, a registry of known aggregation
functions would map each to its decomposition strategy:

```python
AGGREGATION_FUNCTIONS = {
    "sum": SumDecomposer,    # parametric multiply
    "max": MaxDecomposer,    # future
    "min": MinDecomposer,    # future
}
```

### These are not blocking today

The current code works for the solar_battery model. These issues become blocking
when:
- A new model uses `max()` or `min()` aggregation (sum-only limitation)
- A new model has EXPOSE_PURE attrs that downstream modules bind to (Bug 2)
- A new model has `:>>` CHAIN overrides that need rewriting (LITERAL-only limitation)
- A new module family is added and needs its own index + cascade modifications

---

## Summary: What's a Patch and What's Principled

| Component | Status | Evidence |
|-----------|--------|----------|
| Template detection (Step 3, `is_template`) | **Principled** | Clear AST check, well-defined expansion |
| Virtual CalcUsage expansion | **Principled** | Deterministic, hierarchy-aware naming |
| Redefinition extraction (Step 3.5 A) | **Principled** | Pure extraction, well-typed data models |
| Multiplicity extraction (Step 3.5 B) | **Principled** | Pure extraction, clear `MultiplicityData` model |
| Aggregation expression decomposition (Step 3.5 C) | **Partial** | `sum()` hardcoded, no validation of operand structure |
| Virtual binding rewrite (Step 3.5 D) | **Uncertain** | Only handles LITERAL overrides, unclear if bare-name bindings arise |
| Alias enrichment (Step 3.6) | **Patch** | Heuristic based on param_name != source_leaf, duplicates hierarchy extractor alias detection |
| Aggregation scoping (Step 4.7) | **Partial** | Two strategies + BF-6 child-walk, heuristic-based |
| Backtracker aggregation index | **Patch** | Ad-hoc key formats bolted onto existing cascade |
| EXPOSE_PURE resolution | **Broken** | No classification check, produces nonexistent channel (Bug 2) |
| Expression compiler type dispatch | **Fixed but fragile** | Requires specific check ordering, no guardrails against regression |
