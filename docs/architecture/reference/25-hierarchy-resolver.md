# 25 - Hierarchy Resolver

> **Status: retiring.** This document describes `extraction/hierarchy_resolver.py`. It is
> present in the tree and importable, and **not reachable from any public caller** — measured:
> the exact route's construction closure reaches `extraction/extractor.py` and
> `extraction/expression_compiler.py`, and not this module. Since Slice 3E the exact route is
> the only public authority; removal is prepared and gated on owner acceptance at the Phase 5
> stop (recovery plan, Gate 4B).
>
> **The structural patterns are still read — by the elaborator, from the model.** `:>>`
> redefinitions become value sites on attribute nodes, multiplicity becomes enumerated
> occurrences, and `sum()` becomes one term per member occurrence. What is gone is the typed
> intermediate structures this module produced for a later resolution pass to match against.
>
> Everything below is accurate about the hierarchy resolver. For the public route, read
> [00-pipeline-overview](00-pipeline-overview.md).

## What Problem It Solves

SysML v2 models express structural patterns — `:>>` redefinitions, child
multiplicity, `sum()` aggregation — that plain CalcUsage extraction ignores.
These patterns define HOW parts are assembled and HOW computed attributes
roll up through the hierarchy. Without extracting them, the pipeline cannot
generate aggregation modules, propagate literal overrides, or wire
parametric-multiply expressions.

The hierarchy resolver (`extraction/hierarchy_resolver.py`) is a **pure
extraction module** — it walks the SysIDE AST, classifies structural
patterns into typed data structures, and returns them for downstream
consumption. It does NOT resolve bindings or build modules.

## Requirements

| ID | Requirement | Verified by |
|----|-------------|-------------|
| REQ-HR-01 | Every `:>>` redefinition SHALL be classified as exactly one [RedefinitionType](09-data-models.md) from {LITERAL, CHAIN, EXPRESSION} | `all(r.redefinition_type in RedefinitionType for r in redefs)` |
| REQ-HR-02 | Both `FeatureChainExpression` and `FeatureReferenceExpression` value expressions SHALL produce `RedefinitionType.CHAIN` | `_extract_single_redefinition`: both the FCE and FRE branches return CHAIN |
| REQ-HR-03 | Deep-path redefinitions SHALL set `is_deep_path=True` and populate `target_path` from `chaining_features` | `_extract_single_redefinition`: `chaining_features` list → target_path segments |
| REQ-HR-04 | Multiplicity extraction SHALL use `cached_lower_bound` (not `cached_upper_bound`) due to SysIDE exclusive upper-bound convention | `extract_multiplicities`: `getattr(mult, "cached_lower_bound", None)` |
| REQ-HR-05 | `_walk_aggregation_ast()` SHALL check `FeatureChainExpression` BEFORE `OperatorExpression` per [AST dispatch invariant](19-ast-dispatch-invariant.md) | `_walk_aggregation_ast`: FCE check precedes OE check |
| REQ-HR-06 | `sum(child.attr)` SHALL be transformed to `(count_attr * child.attr)` using the `mult_lookup` dict | The `sum` branch of `_walk_aggregation_ast`: multiplicity_attr from mult_lookup |
| REQ-HR-07 | CHAIN-type sibling redefinitions that reference the aggregation attribute SHALL be added as aliases | The sibling-alias scan in `extract_hierarchy_data`: `source_path == agg.attribute_name` or `source_path.endswith("." + agg.attribute_name)` |
| REQ-LVP-08 | `usage_type_map` SHALL resolve each `(owning_qn, usage_name)` to the usage's **most-specific owned FeatureTyping target**, not `next(iter(member.types))`; incomparable multi-typings resolve deterministically (sorted-first) with a V10 warning | `test_type_indexing.py` — `(Variant, driver) → HIF Driver` (declared subtype); `(MultiHolder, multi) → IFE Driver` (sorted-first) + V10 |
| REQ-HR-08 | `extract_design_overrides()` SHALL scan `:>>` member overrides on **plain** part usages, not only `part redefines` usages; a newly-scanned **plain**-usage override SHALL be kept only when its RHS is LITERAL (CHAIN/EXPRESSION plain overrides stay out — Item 10's job), while the `part redefines` path keeps all RHS types unchanged | `test_virtual_binding_rewrite.py::test_plain_usage_override_filter_keeps_only_literal`; the alias_agg_probe/issue22/unresolvable_attr_probe collector pins in `test_uncovered_params.py` go empty once the plain-usage literal is captured and rewritten |
| REQ-HR-09 | RELEASED — reserved in Item 9's handoff as mechanism D's tentative home; not used. Mechanism D is homed in REQ-VBR-10 ([12-virtual-binding-rewrite](12-virtual-binding-rewrite.md)) instead (design D5). | n/a — no code; recorded so the ID is not silently skipped |
| REQ-LVP-09 | A second pass (`_index_usage_level_retypes`) SHALL index **usage-level** retypes of inherited part usages, keyed by the container usage's instance QN (`(container_usage_qn, member_name) → retyped_def`), for genuine retypes only — a `:>>` redefinition whose most-specific owned type DIFFERS from the base def's declared type. Value-only `:>>` overrides (same type) are excluded, so no non-two-level fixture gains an entry. | `test_spec_chain_twolevel.py::test_usage_type_map_indexes_usage_level_retype` — `("TwoLevelDesign__hif_plant","driver") → 'HIF Driver'`; committed snapshots stay byte-identical |

## The 4 Extraction Phases

`extract_hierarchy_data()` orchestrates four phases per PartDef:

| Phase | Function | Input | Output |
|-------|----------|-------|--------|
| 1 | `extract_redefinitions()` | PartDef element | `list[RedefinitionData]` |
| 2 | `extract_design_overrides()` | Design PartUsages | `list[RedefinitionData]` (usage-level overrides, flat or deep-path) |
| 3 | `extract_multiplicities()` | PartDef element | `list[MultiplicityData]` |
| 4 | `build_aggregation_expression()` | EXPRESSION redefs + multiplicities | `list[AggregationExpressionData]` |

Additionally, the orchestrator builds two lookup structures:
- `part_usage_names: dict[str, set[str]]` — child PartUsage names per PartDef, used by [aggregation scoping](13-aggregation-scoping.md) for instance discovery
- `usage_type_map: dict[tuple[str, str], str]` — `(owning_qn, usage_name) → type_partdef_qn`, used by [literal value propagation](18-literal-value-propagation.md) to find redefinition defaults. The type is the usage's **most-specific owned FeatureTyping target** (REQ-LVP-08), read from the owned typing relationship — not `next(iter(member.types))`, whose first entry is a *supertype* for a retyped `part :>> driver : 'HIF Driver'`. So a retyped usage resolves its defaults against the declared subtype (the type-aware `target_partdef_qn` branch of `_find_literal_redefinition` in `resolution/graph_builder.py`; since Item 10 the map's second consumer is `_rewrite_specialized_chain`'s instance-first type-select, REQ-VBR-11). When a usage has multiple incomparable owned types the pick is the sorted-first QN plus a V10 warning. A usage with **no** owned FeatureTyping (an untyped `part x {}`, implicit library `Part`, or a redefinition that inherits its typing) keeps the position-0 type — there is nothing to compare, and this holds existing output identical.

### Usage-Level Retype Indexing (Two-Level Specialization, REQ-LVP-09)

The def-level `usage_type_map` above is built only from `PartDefinition` members, so it
keys a retype by the *declaring def*. That misses the two-level specialization the real
fusion-tea model uses: `part hif_plant : 'IFE Power Plant' { part :>> driver : 'HIF Driver' }`
retypes an inherited part usage **on a part usage**, not on any def. A type-select keyed
on the consumer's declaring def then sees only the base type (`'IFE Driver'`) and misses
the retype.

After the def-level map is built, `_index_usage_level_retypes` runs a second pass over the
design-level part usages and appends entries keyed by the **container usage's instance QN**:

```
("TwoLevelDesign__hif_plant", "driver") → "TwoLevelLib__HIF_Driver"
```

**Genuine-retype discriminator (the key to byte-identity).** A member is indexed only
when both hold:

- it is a `:>>` redefinition (`owned_redefinitions` non-empty), and
- its most-specific owned type **differs** from the base def's declared type for that
  member (read from the just-built def-level map).

A value-only `:>>` override that keeps the same type — solar_battery's
`:>> solar_array {...}`, chain_override's sensor — has the same type and is excluded.
Verified across the corpus: exactly one fixture (`spec_chain_twolevel`) gains an entry;
every other committed snapshot stays byte-identical. The consumer is the resolver's
instance-first type-select (REQ-VBR-11,
[12-virtual-binding-rewrite](12-virtual-binding-rewrite.md#three-tier-merge-specialized-def--precedence-req-vbr-10-req-vbr-11)).

## Phase 1: Redefinition Classification

`extract_redefinitions()` scans a PartDef's `owned_members` for
`ReferenceUsage` elements with non-empty `owned_redefinitions`. Each is
classified by its right-hand-side expression via `_extract_single_redefinition()`:

```
:>> wattage = 400.0                    → LITERAL  (is_literal_expression)
:>> total_capex = capital_cost         → CHAIN    (FeatureReferenceExpression)
:>> total_capex = cost_model.total_cost → CHAIN   (FeatureChainExpression)
:>> capital_cost = sum(pv.capex) + bos → EXPRESSION (anything else)
```

Note: both FCE and FRE produce `CHAIN` type (REQ-HR-02). The distinction
between dotted-path and bare-name references is preserved in `source_path`
but the classification is the same.

**Deep-path detection** (REQ-HR-03): When the AST's `redefined_feature` has
`chaining_features`, the redefinition targets a nested attribute. Example:

```sysml
part solar_battery_plant : Solar_Battery_Plant {
    :>> pv_module.wattage = 400.0;   /* deep path: ["pv_module", "wattage"] */
}
```

This sets `is_deep_path=True` and `target_path=["pv_module", "wattage"]`.
Deep-path redefinitions are consumed by [virtual binding rewrite](12-virtual-binding-rewrite.md)
to override inherited values at specific hierarchy positions.

**Type-only redefinitions** (no `feature_value_expression`) are skipped — they
declare type constraints, not value overrides.

## Phase 2: Design Override Extraction

`extract_design_overrides()` scans design-level PartUsages for `:>>` overrides.
Unlike Phase 1 (which scans PartDef members), this scans design PartUsages. Two
shapes carry a `:>>` override (REQ-HR-08):

- **`part redefines` usage** — non-empty `owned_redefinitions` on the usage itself.
  Its members may hold deep-path overrides like `:>> pv_module.wattage = 400.0`.
  **All RHS types** are captured (LITERAL, CHAIN, EXPRESSION) — unchanged behavior.
- **Plain typed usage** — empty `owned_redefinitions`; the override lives on a
  member `ReferenceUsage`, e.g. `part assembly : 'Widget Assembly' { :>> widget.base_cost = 50.0; }`.
  Before REQ-HR-08 the outer per-usage `owned_redefinitions` guard skipped these
  entirely, dropping the literal. Now their members are scanned too, but a
  plain-usage override is kept **only when its RHS is LITERAL**
  (`_keep_plain_usage_override`, D3): CHAIN/EXPRESSION plain overrides (catf_mfe's
  cross-part refs, ife_plant shape 4) are Item 10's job and never enter
  `design_overrides`. Filtering at capture — not at the rewrite — is what keeps
  those overrides from reaching any downstream consumer and churning a baseline
  (INV-1).

Both shapes scan members through `_extract_single_redefinition`, which returns
`None` for non-`ReferenceUsage` / value-less members, so the now-unconditional
member scan is cheap.

**Performance.** Previously the outer loop early-`continue`d on nearly every
usage (all plain typed usages). Now every PartUsage's `owned_members` runs through
`_extract_single_redefinition`. This is O(usages × members), one-shot at extraction
over a corpus of tens of usages — negligible, no caching.

The caller ([orchestration](02-orchestration.md)) is responsible for
providing the PartUsage elements. Design overrides become the
`design_overrides` field on [HierarchyExtractionResult](09-data-models.md), and
drive [virtual binding rewrite](12-virtual-binding-rewrite.md).

## Phase 3: Multiplicity Extraction

`extract_multiplicities()` detects child PartUsages with multiplicity
annotations. This data is CRITICAL for Phase 4: without multiplicity, `sum()`
cannot be transformed to parametric multiply.

**The SysIDE lower-bound convention** (REQ-HR-04): SysIDE's `cached_upper_bound`
is exclusive (N+1 for a `[N]` multiplicity), so we use `cached_lower_bound`
which gives the correct count.

For a SysML declaration like:
```sysml
part def Solar_Array {
    attribute module_count : Integer = 20;
    part pv_module : PV_Module[module_count];
}
```

The extractor produces:
```python
MultiplicityData(
    part_usage_name="pv_module",
    owning_part_def_qn="SolarLib__Solar_Array",
    count=20,
    count_attribute_name="module_count",  # from upper_bound.referent
    default_value=20,                     # from referent's feature_value_expression
)
```

The `count_attribute_name` is extracted from `mult.upper_bound.referent.name` —
the actual attribute that controls the count. This becomes an entry point in the
generated pipeline (the user can change `module_count` at runtime).

Singletons (no multiplicity attribute) are excluded from the output.

## Phase 4: Aggregation Transformation

`build_aggregation_expression()` takes an EXPRESSION-type
redefinition and transforms it into an [AggregationExpressionData](09-data-models.md).

### The mult_lookup Mechanism

First, a lookup dict is built from Phase 3 multiplicities:
```python
mult_lookup = {m.part_usage_name: m for m in multiplicities}
# e.g. {"pv_module": MultiplicityData(count=20, count_attribute_name="module_count")}
```

This is passed to `_walk_aggregation_ast()` which uses it to detect aggregated
parts and transform `sum()` calls.

### AST Walking and Term Classification

`_walk_aggregation_ast()` recursively walks the expression AST.
The dispatch order follows the [AST dispatch invariant](19-ast-dispatch-invariant.md):

| Priority | AST Type | Classification | Example |
|----------|----------|----------------|---------|
| 1 | `FeatureChainExpression` | **SingletonTerm** | `inverter.install_cost` |
| 2 | `OperatorExpression` | recurse into operands | `a + b` |
| 3 | `FeatureReferenceExpression` | **LocalTerm** | `misc_cost` |
| 4 | InvocationExpression (`sum`) | **SumTerm** | `sum(pv.capital_cost)` |
| 4b | InvocationExpression (wrapper) | unwrap and retry | `Evaluation(expr)` |
| 5 | Literal | pass through | `1.05` |

**SumTerm creation** (REQ-HR-06): When `sum(child.attr)` is found, the
`child` part is looked up in `mult_lookup`. If multiplicity exists:
```
sum(pv_module.capital_cost) → (module_count * pv_module.capital_cost)
```
producing `SumTerm(part_usage_name="pv_module", attribute_name="capital_cost",
multiplicity_attr="module_count", multiplicity_count=20)`.

If multiplicity is missing, a warning is logged and an unresolved SumTerm
(with `multiplicity_attr=None`) is emitted.

**Wrapper unwrapping**: SysIDE sometimes wraps expressions in
`Evaluation`, `evaluate`, `collect`, or `select` InvocationExpressions.
The `_unwrap_invocation()` helper peels these off recursively
(max depth 3) to reach the inner FCE/FRE node.

### Alias Detection (REQ-HR-07)

After building an `AggregationExpressionData`, the orchestrator scans sibling
redefinitions for CHAIN-type aliases (in `extract_hierarchy_data`). If a
sibling's `source_path` equals the aggregation's `attribute_name` — or ends
with `"." + attribute_name` for a dotted path — and the sibling has a
different name, it's an alias:

```sysml
:>> capital_cost = sum(pv_module.capital_cost) + bos_cost;  /* aggregation */
:>> total_capex = capital_cost;                              /* alias */
```

Here `total_capex` becomes an alias for the `capital_cost` aggregation,
registered in the [output registry](10-output-registry.md) as a Phase 2
CHAIN alias.

**Edge case**: The `.`-suffix branch matches any dotted `source_path` whose
leaf is the aggregation attribute (e.g., `parent.capital_cost` matches
`attribute_name="capital_cost"`), regardless of which part it references — so it
could produce spurious aliases for hierarchical CHAIN redefinitions. A bare-name
suffix like `total_capital_cost` does NOT match — the dot boundary guards it.
This edge (`_chain_sibling_aliases_aggregation`) is pinned directly by
`tests/unit/test_hierarchy_resolver.py::TestDottedLeafAliasMatch`, which asserts
the current leaf-only, part-blind behavior; no committed fixture triggers it, so
the unit pin is the coverage. *(PIPELINE-TRUTH Item 10 resolved the part-blindness
question: keep the current behavior. No supported model triggers the edge, and the
unit pin makes any future tightening a red-then-green change. Speculative tightening
is filed as BACKLOG `[DOTTED-LEAF-PART-BLIND]` (P3), not done here.)*

## Concrete Example

Given this SysML:
```sysml
part def Solar_Array {
    attribute module_count : Integer = 20;
    part pv_module : PV_Module[module_count];
    :>> capital_cost = sum(pv_module.capital_cost) + inverter.install_cost + misc_cost;
    :>> total_capex = capital_cost;
}
```

**Phase 1** produces 2 redefinitions:
- `RedefinitionData(attribute_name="capital_cost", type=EXPRESSION, expression_ast=<node>)`
- `RedefinitionData(attribute_name="total_capex", type=CHAIN, source_path="capital_cost")`

**Phase 3** produces:
- `MultiplicityData(part_usage_name="pv_module", count=20, count_attribute_name="module_count")`

**Phase 4** transforms the EXPRESSION redefinition:
```python
AggregationExpressionData(
    attribute_name="capital_cost",
    sum_terms=[SumTerm("pv_module", "capital_cost", "module_count", 20)],
    singleton_terms=[SingletonTerm("inverter.install_cost")],
    local_terms=[LocalTerm("misc_cost")],
    transformed_expression="(module_count * pv_module.capital_cost) + inverter.install_cost + misc_cost",
    aliases=["total_capex"],  # from CHAIN sibling detection
)
```

## Supplied-Value Materializer (REQ-SVM-01..04)

**Module:** `resolution/supplied_values.py` (PIPELINE-TRUTH Item 2).

A plant calc reads a subsystem value cross-part (`in driver_efficiency =
driver.efficiency`) or in-part (`in flow_rate = throughput`). The value is in the model,
but on a *redefinition or override*, not on the attribute's base def — so the base def
is valueless and the reference falls to a valueless Step-4 entry point that trips V11.
The design-attribute resolution path (`_resolve_to_design_attribute`, doc 11 Step 3) is
a working value-carrier; it just has no valued attribute to match.

This pre-pass, run **before the backtracker**, reads the two capture buckets this
resolver produces (`redefinitions` ∪ `design_overrides`), resolves the value by
precedence, and emits one synthetic `DesignAttributeData` per supplied source attribute,
keyed by its **source QN** and carrying the literal as a string. Merged into
`design_attributes`, the existing Step-3 path carries it to every consumer and collapses
renamed-consumer fan-out for free (two consumers of one source → one QN → one EP).

**Four supported value shapes:**

| Shape | Example | Bucket | Tier |
|-------|---------|--------|------|
| (a) subtype-def `:>>` via retype | `Hif_Driver.efficiency = 0.35` reached through `:>> driver : 'Hif Driver'` | `redefinitions` | 2a via `usage_type_map` |
| (b) bare override block | `part :>> target_factory { :>> cost_per_target = 10.0; }` | `design_overrides` | 1 |
| (c) dotted usage override | `:>> chamber.cost_per_unit = 7.0` on the instance | `design_overrides` | 1 |
| (d) in-part inherited redefine | `in flow_rate = throughput` + `:>> throughput = 8.0` on the same def | `redefinitions` | 2b direct-owner |

**Precedence (REQ-SVM-01):** usage override (tier 1) > specialized-def `:>>` (tier 2a via
`usage_type_map`, or tier 2b direct-owner match `redef.owning_part_qn ==
calc.owning_part_def_qn`) > base def (tier 3, no synthesis). Tier 2a reuses doc 18's
`_find_literal_redefinition` **Strategy 1 only** (gated on the type key, so the brittle
Strategy-2 name-fallback is never reached); tier 2b is a materializer-local exact match
(doc 18's helper stays aggregation-scoped).

**Distinct from siblings:** not aggregation LVP (doc 18, per-term; doc 18 explicitly
fences CalcUsage-binding literals off from its helper), and not VBR-03 (doc 12,
per-consumer). This mechanism keys by source QN and **collapses across consumers**
(REQ-SVM-02) — the property that makes renamed-consumer fan-out (`efficiency` →
`driver_efficiency` AND `eta`) resolve to one entry point.

**Guards:** a synthetic attribute never overwrites a real captured design attribute
(REQ-SVM-03, real wins + WARN); only LITERAL values apply, and a referenced
non-literal-only binding falls through to V11 with a count-summary WARN, never a silent
drop (REQ-SVM-04). A supplied `0.0` carries as `0.0`, not dropped to `null`
(`_classify_entry_points` uses `is not None`, INV-6).

The synthetic attributes enrich a graph-only copy of `design_attributes`; the pure
extraction boundary is what a snapshot serializes, so the materializer reconstructs the
synthetic attrs at from-snapshot generate time from the raw redefinitions/overrides.

## Data Models

| Type | Location | Role |
|------|----------|------|
| [`RedefinitionData`](09-data-models.md) | `extraction/data_models.py` | Single `:>>` with type, value, target_path |
| [`MultiplicityData`](09-data-models.md) | `extraction/data_models.py` | Child count + count_attribute_name |
| [`AggregationExpressionData`](09-data-models.md) | `extraction/data_models.py` | Decomposed aggregation with SumTerm/SingletonTerm/LocalTerm |
| [`HierarchyExtractionResult`](09-data-models.md) | `extraction/data_models.py` | Top-level container for all hierarchy data |

## Related Documents

- **Upstream**: [00-pipeline-overview](00-pipeline-overview.md) — Step 1 in the pipeline
- **Upstream**: [01-extraction](01-extraction.md) — extraction layer overview; Section 4 references this module
- **Downstream**: [02-orchestration](02-orchestration.md) — consumes HierarchyExtractionResult at Step 3.5
- **Downstream**: [12-virtual-binding-rewrite](12-virtual-binding-rewrite.md) — uses design_overrides for hierarchy overrides
- **Downstream**: [13-aggregation-scoping](13-aggregation-scoping.md) — uses aggregation expressions + part_usage_names
- **Downstream**: [18-literal-value-propagation](18-literal-value-propagation.md) — uses usage_type_map for type-aware defaults
- **Cross-cutting**: [19-ast-dispatch-invariant](19-ast-dispatch-invariant.md) — FCE-before-OE ordering rule
- **Data models**: [09-data-models](09-data-models.md) — full field definitions for all hierarchy types
