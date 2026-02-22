# Validation: 05-module-factory.md -- Section 4 (Aggregation Modules)

Validated against: `src/sysml_codegen/resolution/graph_builder.py` (branch: cost-pattern)

## Validation Scope

Section 4 and subsections 4a, 4b, 4c of doc 05-module-factory.md -- the aggregation
module factory description.

---

## 1. Function Signature: `_build_aggregation_module()`

**Doc claims** (line 110-111):
> Additional inputs: `expose_aliases` (EXPOSE_PURE alias map for LocalTerms),
> `usage_type_map` (type-aware PartDef QN resolution -- see doc 18).

**Actual signature** (graph_builder.py lines 922-930):
```python
def _build_aggregation_module(
    agg: ScopedAggregationData,
    redefinitions: list[RedefinitionData],
    output_registry: OutputRegistry,
    entry_points: dict[str, EntryPoint],
    group_deriver: ParameterGroupDeriver | None,
    expose_aliases: dict[tuple[str, str], str] | None = None,
    usage_type_map: dict[tuple[str, str], str] | None = None,
) -> PipelineModule:
```

**Verdict: ACCURATE.** Both `expose_aliases` and `usage_type_map` are parameters
on the function. The doc correctly identifies them as additional inputs and
accurately describes their purposes.

---

## 2. Section 4a: SumTerm Resolution Chain

**Doc claims** (lines 122-129):
1. `_resolve_aggregation_input_channel()` -- CHAIN redefinition tracing + registry
2. LITERAL fallback -- `_find_literal_redefinition()` checks for `:>> attr = value`
   on the child PartDef. If found, the value becomes the entry point's `default_value`
   and the module stays `FULLY_COMPILABLE`.
3. Entry point (no default) + `MANUAL_REQUIRED` compilability.

**Actual code** (graph_builder.py lines 960-1018):
```python
# Step 1: _resolve_aggregation_input_channel()
channel = _resolve_aggregation_input_channel(
    symbolic_ref, agg.instance_path, redefinitions, output_registry,
)
if channel:
    source = InputSource(source_type="module_output", producer_channel=channel)
else:
    # Step 2: LITERAL fallback
    literal_default = _find_literal_redefinition(
        term.part_usage_name, term.attribute_name, redefinitions,
        usage_type_map, agg.expression.owning_part_qn,
    )
    # Step 3: Entry point (MANUAL_REQUIRED if no literal)
    if literal_default is None:
        compilability = Compilability.MANUAL_REQUIRED
    # ... creates entry point with literal_default as default_value
```

**Verdict: ACCURATE.** The three-step fallback chain is exactly as documented. One
nuance the doc omits: when a LITERAL redefinition IS found, compilability is NOT
downgraded to MANUAL_REQUIRED. The doc's phrasing "the module stays FULLY_COMPILABLE"
correctly implies this. And when the literal is found, the value becomes the EP
default_value, exactly as stated.

**Minor detail:** The doc says "entry point (no default)" for step 3, but in the
code, the entry point is always created (whether literal is found or not) when the
channel resolution fails. The `literal_default` becomes the default_value on the EP.
When `literal_default is None`, you get an EP with no default AND MANUAL_REQUIRED.
When `literal_default` has a value, you get an EP with a default and compilability
stays as-is. So the doc's shorthand "Entry point (no default) + MANUAL_REQUIRED" is
describing only the final-fallback case where no literal was found, which is correct.

---

## 3. Section 4b: SingletonTerm Resolution Chain

**Doc claims** (lines 137-141):
1. `_resolve_aggregation_input_channel()` -- registry (scoped keys, unscoped keys)
2. Direct channel construction -- `instance_path__prefix__output_name`
3. LITERAL fallback -- same as SumTerm, found value becomes EP default
4. Entry point (no default) + `MANUAL_REQUIRED` compilability.

**Actual code** (graph_builder.py lines 1048-1124):
```python
# Step 1: Registry-first resolution
resolved = _resolve_aggregation_input_channel(
    s_term.source_path, agg.instance_path, redefinitions, output_registry,
)
if resolved:
    s_source = InputSource(source_type="module_output", producer_channel=resolved)
else:
    # Step 2: Direct channel construction
    prefix, output_name = s_term.source_path.rsplit(".", 1)
    calc_path = prefix.replace(".", "__")
    channel = get_channel_name(f"{agg.instance_path}__{calc_path}", output_name)
    if channel in canonical_channels:
        s_source = InputSource(source_type="module_output", producer_channel=channel)

if s_source is None:
    # Step 3: LITERAL fallback
    literal_default: float | None = None
    if "." in s_term.source_path:
        s_part_usage, s_attr = s_term.source_path.rsplit(".", 1)
        literal_default = _find_literal_redefinition(
            s_part_usage, s_attr, redefinitions,
            usage_type_map, agg.expression.owning_part_qn,
        )
    # Step 4: Entry point
    if literal_default is None:
        compilability = Compilability.MANUAL_REQUIRED
    # ... creates entry point with literal_default as default_value
```

**Verdict: ACCURATE.** The four-step chain matches exactly.

**Nuance the doc slightly mischaracterizes:** The doc says step 1 is "registry
(scoped keys, unscoped keys)" but the actual step 1 calls
`_resolve_aggregation_input_channel()` which is the FULL resolution function including
CHAIN redefinition tracing AND then registry fallback. This is the same function used
for SumTerms. The doc for 4a correctly says "CHAIN redefinition tracing + registry"
but for 4b it says only "registry (scoped keys, unscoped keys)". Both call the exact
same `_resolve_aggregation_input_channel()` function, so the 4b description
undersells the first step -- it also includes CHAIN tracing, not just registry lookup.

**DISCREPANCY (minor):** Doc 4b step 1 should say "CHAIN redefinition tracing +
registry" (identical to 4a step 1), not just "registry (scoped keys, unscoped keys)".

---

## 4. Section 4c: LocalTerm Resolution Chain

**Doc claims** (lines 149-156):
1. Sibling aggregation output -- another aggregation module at the same scope
   produces a channel with the double-attr format `{ip}__{attr}__{attr}`.
2. EXPOSE_PURE alias -- the `expose_aliases` map provides a dotted expression path
   that is then resolved through `_resolve_aggregation_input_channel()`.
3. Entry point fallback -- user-provided value.

**Actual code** (graph_builder.py lines 1133-1189):
```python
# Step 1: Sibling aggregation output
sibling_eqn = f"{agg.instance_path}__{l_term.attribute_name}"
sibling_channel = get_channel_name(sibling_eqn, l_term.attribute_name)
if sibling_channel in canonical_channels:
    l_source = InputSource(source_type="module_output", producer_channel=sibling_channel)

# Step 2: EXPOSE_PURE alias
if l_source is None and expose_aliases:
    alias_key = (agg.expression.owning_part_qn, l_term.attribute_name)
    alias_source = expose_aliases.get(alias_key)
    if alias_source:
        channel = _resolve_aggregation_input_channel(
            alias_source, agg.instance_path, redefinitions, output_registry,
        )
        if channel:
            l_source = InputSource(source_type="module_output", producer_channel=channel)

# Step 3: Entry point fallback
if l_source is None:
    ep_qn = f"{agg.module_eqn}__{l_term.attribute_name}"
    ...
```

**Verdict: ACCURATE.** All three strategies are correctly described and in the correct order.

**Double-attr channel format:** The doc says `{ip}__{attr}__{attr}`. The code builds:
```python
sibling_eqn = f"{agg.instance_path}__{l_term.attribute_name}"
sibling_channel = get_channel_name(sibling_eqn, l_term.attribute_name)
```
This produces `{instance_path}__{attr}__{attr}` which matches the doc's `{ip}__{attr}__{attr}`.
**ACCURATE.**

**EXPOSE_PURE alias key:** The doc says the expose_aliases map is keyed and the alias
provides a "dotted expression path" resolved via `_resolve_aggregation_input_channel()`.
The code uses `(agg.expression.owning_part_qn, l_term.attribute_name)` as key and the
value is `alias_source` (e.g., `"allocation_model.total_allocation"`) which is passed
to `_resolve_aggregation_input_channel()`. **ACCURATE.**

**Notable omission in 4c:** Unlike SumTerm and SingletonTerm, LocalTerm does NOT have
a LITERAL fallback step before the entry point. The code goes directly from
EXPOSE_PURE alias failure to entry point creation. The doc does not claim there is a
LITERAL step for LocalTerm, so this is not a discrepancy, but it is a notable
behavioral difference compared to the other two term types. The doc's three-strategy
list is exhaustive for LocalTerm.

**Another notable omission in 4c:** LocalTerm entry point creation does NOT set
`compilability = MANUAL_REQUIRED`. The code just silently creates the entry point
without downgrading compilability:
```python
if l_source is None:
    ep_qn = f"{agg.module_eqn}__{l_term.attribute_name}"
    # ... creates entry point, no compilability change
```
This differs from SumTerm and SingletonTerm where unresolved terms trigger
`compilability = Compilability.MANUAL_REQUIRED`. The doc does not explicitly say
LocalTerm fallback triggers MANUAL_REQUIRED (it just says "Entry point fallback --
user-provided value"), so the doc is technically not wrong, but the asymmetry
compared to 4a and 4b is worth noting.

---

## 5. Step 6.6b: `expose_aliases` Map Construction

**Doc claims** (line 152):
> the `expose_aliases` map (built in Step 6.6b from EXPOSE_PURE ComputedAttributes)

**Actual code** (graph_builder.py lines 176-188):
```python
# Step 6.6b: Build EXPOSE_PURE alias map for aggregation LocalTerm resolution.
expose_aliases: dict[tuple[str, str], str] = {}
for ca in (computed_attributes or []):
    if ca.classification == ComputedAttributeClassification.EXPOSE_PURE:
        segments = ca.owning_part_qualified_name.split("::")
        normalized_qn = "__".join(sanitize_name(seg) for seg in segments)
        expose_aliases[(normalized_qn, ca.python_name)] = ca.expression_text
```

**Verdict: ACCURATE.** The code comment literally says "Step 6.6b" and it builds
the map from EXPOSE_PURE ComputedAttributes, exactly as documented. The map keys
are `(normalized_owning_part_qn, python_name)` tuples and values are
`expression_text` strings.

---

## 6. Section 5 ("The Key Insight: Pure Data Transformers")

**Doc claims** (lines 192-196):
> No graph walking, no registry mutation, no entry point discovery inside these
> functions. Resolution is done upstream.

**Code reality:** This is an aspirational description, not the current state. The
`_build_aggregation_module()` function DOES perform resolution internally:
- It calls `_resolve_aggregation_input_channel()` (graph walking via CHAIN tracing)
- It mutates the `entry_points` dict (adds new entry points)
- It calls `_find_literal_redefinition()` for default discovery

The doc describes the post-refactoring target design, not the current implementation.
This is consistent with the doc being in the `concepts/refactor-design-intent/` directory
-- it describes the intended factored-out architecture. However, Section 4 describes
the CURRENT behavior accurately, which creates an internal tension within the document.

---

## Summary of Discrepancies

| # | Severity | Location | Issue |
|---|----------|----------|-------|
| 1 | Minor | 4b step 1 | Says "registry (scoped keys, unscoped keys)" but the function also does CHAIN redefinition tracing first, same as 4a. Should say "CHAIN redefinition tracing + registry" for consistency with 4a. |
| 2 | Informational | 4c | LocalTerm entry-point fallback does NOT downgrade compilability to MANUAL_REQUIRED, unlike SumTerm (4a) and SingletonTerm (4b). Doc is not wrong (it doesn't claim MANUAL_REQUIRED) but the asymmetry is undocumented. |
| 3 | Informational | Section 5 | "Pure data transformers" framing conflicts with Section 4's accurate depiction of resolution happening inside the factory. Section 5 describes the post-refactoring goal; Section 4 describes current behavior. |

**Overall assessment:** Section 4 is highly accurate. The resolution chains for all
three term types are correctly documented with the right ordering and behaviors. The
only concrete discrepancy is the 4b step 1 description being less precise than 4a's
(omitting CHAIN tracing). The `expose_aliases` and `usage_type_map` parameters, the
Step 6.6b construction, and the double-attr channel format are all verified correct.
