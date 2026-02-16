# Design: Hierarchy E2E Fixes — Probe-Validated AST Dispatch Corrections

**Status:** Draft
**Owner:** Reid Westwood
**Created:** 2026-02-12 06:08 UTC
**Branch:** cost-pattern
**Commit:** f49005c

## Overview

Five surgical fixes to the extraction and initialization layers to correct AST type dispatch ordering and data-flow gaps, enabling all 10 hierarchy E2E tests to pass against the real solar_battery SysIDE model.

## Related Artifacts

- **Spec:** `.project/active/hierarchy-e2e-fixes/spec.md`
- **Synthesis Report:** `.project/reports/05_synthesis_and_fixes.md`
- **E2E Tests:** `tests/integration/test_hierarchy_e2e.py`
- **Probe Scripts:** `scripts/probes/probe_*.py`

## Research Findings

### Files Analyzed

| File | Lines | Role |
|------|-------|------|
| `extraction/expression_utils.py` | 1-197 | AST-to-text reconstruction; `reconstruct_expression()`, `extract_feature_chain_name()`, `extract_feature_reference_name()` |
| `extraction/hierarchy_resolver.py` | 1-542 | Hierarchy extraction; `_unwrap_invocation()`, `_walk_aggregation_ast()`, `build_aggregation_expression()`, `extract_hierarchy_data()` |
| `extraction/data_models.py` | 330-362 | `HierarchyExtractionResult` dataclass, `ScopedAggregationData` |
| `generation/initialization.py` | 296-515 | `_scope_aggregation_expressions()`, `build_pipeline_context()` orchestration |
| `extraction/usage_extractor.py` | 500-616 | `BindingInfo` population — `source_path` for REFERENCE bindings is a SysML **qualified_name** (contains `::`) |
| `analysis/dependency_backtracker.py` | 180-197 | BF-7 alias propagation code — already reads `agg.expression.aliases` into `_aggregation_output_index` |

### Key Codebase Patterns

1. **Type dispatch pattern**: The codebase consistently uses `SysideAdapter.is_instance(node, "TypeName")` for AST type checks. Both `_extract_single_redefinition()` (hierarchy_resolver.py:66-136) and `_parse_binding_expression()` (usage_extractor.py:521-571) check specific types before falling through to generic handling. The current bug is that `reconstruct_expression()` and `_walk_aggregation_ast()` violate this pattern by checking `hasattr(node, "function")` before specific types.

2. **Extraction/generation boundary**: The codebase strictly separates AST access (extraction layer) from pipeline logic (generation layer). `_scope_aggregation_expressions()` in `initialization.py` only receives pre-extracted data structures — it has no AST element access. This is confirmed by its signature: `(hierarchy_data: HierarchyExtractionResult, calc_usages: list[CalcUsageData])`.

3. **Binding source_path format**: For REFERENCE bindings, `source_path` is the referent's `qualified_name` — a SysML path with `::` separators (e.g., `"'Solar Battery Plant'::capital_cost"`). For CHAIN bindings, it's a dotted path (e.g., `"instance.attribute"`). This is critical for the RC5 alias matching logic.

### Verified Fix Feasibility

I verified each proposed fix against the actual source code:

- **FR-1 (RC1):** `_unwrap_invocation()` at line 278-298 — currently has no type guards, just `hasattr(node, "function")`. Adding `SysideAdapter.is_instance()` guards is correct and consistent with the pattern used throughout the file.

- **FR-2 (RC2):** `reconstruct_expression()` at line 34-75 — the `FeatureReferenceExpression` check (line 54) and `FeatureChainExpression` check (line 57) are clearly after the `hasattr(function)` check (line 47). Moving them before line 47 is a safe position swap.

- **FR-3 (RC3):** `_walk_aggregation_ast()` at line 301-429 — the `FeatureChainExpression` handler (lines 407-411) and `FeatureReferenceExpression` handler (lines 414-417) contain correct logic and just need to be moved before the `hasattr(function)` check at line 347. The existing handler code is exactly right — no rewrite needed.

- **FR-4 (RC4):** `HierarchyExtractionResult` at line 331-338 has no `part_usage_names` field. `extract_hierarchy_data()` already iterates PartDefinition members at line 501 and already calls `extract_multiplicities()` which scans `owned_members` for PartUsage. Adding a parallel scan for ALL PartUsage names is straightforward. `_scope_aggregation_expressions()` Strategy 2 at line 332-346 currently filters only multiplicity children — widening to all children naturally handles all-singleton assemblies.

- **FR-5 (RC5):** The spec's description needs a nuance correction. For REFERENCE bindings, `source_path` is a SysML qualified name (contains `::`), not a bare name. The matching logic must extract the **leaf segment** from `source_path` (after the last `::`) to compare against `agg.attribute_name`. This is a design clarification, not a spec change — the intent is the same.

## Proposed Design

### Implementation Order

FR-2 → FR-1 → FR-3 → FR-4 → FR-5 (respecting dependency chain per spec).

---

### Fix 1: FR-2 — Reorder checks in `reconstruct_expression()`

**File:** `src/sysml_codegen/extraction/expression_utils.py:44-58`
**Change type:** Block relocation (no logic changes)

Move the `FeatureReferenceExpression` and `FeatureChainExpression` type checks from after the `hasattr(function)` check to before it. The three blocks are:

1. `SysideAdapter.is_instance(expr_node, "OperatorExpression")` — stays at line 44 (already first)
2. `SysideAdapter.is_instance(expr_node, "FeatureReferenceExpression")` — move from line 54 to after OperatorExpression
3. `SysideAdapter.is_instance(expr_node, "FeatureChainExpression")` — move from line 57 to after FeatureReferenceExpression
4. `hasattr(expr_node, "function")` — stays but is now 4th instead of 2nd

No code inside any block changes. The function signature and return types are unchanged.

**Integration:** `extract_feature_chain_name()` at line 133-161 calls `reconstruct_expression(operands[0])` on the chain's first operand (line 141). After this fix, that call will correctly return the referent name (e.g., `"array_bos"`) instead of `"Evaluation()"`.

---

### Fix 2: FR-1 — Type guards in `_unwrap_invocation()`

**File:** `src/sysml_codegen/extraction/hierarchy_resolver.py:278-298`
**Change type:** Add 4 lines (early returns)

Add two `SysideAdapter.is_instance()` checks at the top of the function body, before the existing `hasattr(node, "function")` check:

```python
def _unwrap_invocation(node: Any, _depth: int = 0) -> Any:
    if _depth >= 3:
        return node
    if SysideAdapter.is_instance(node, "FeatureChainExpression"):
        return node
    if SysideAdapter.is_instance(node, "FeatureReferenceExpression"):
        return node
    if hasattr(node, "function") and hasattr(node.function, "name"):
        operands = list(getattr(node, "operands", []))
        if operands:
            return _unwrap_invocation(operands[0], _depth + 1)
    return node
```

**Why not `_KNOWN_WRAPPER_FUNCTIONS`:** As the spec notes, `"Evaluation"` is in `_KNOWN_WRAPPER_FUNCTIONS` (line 275) AND is the `function.name` on `FeatureReferenceExpression`. Using the name-set would create a fragile collision where FeatureReferenceExpression nodes with operands would be incorrectly unwrapped. The `is_instance()` guard is explicit and immune to name collisions.

**Integration with FR-3:** After this fix, when `_walk_aggregation_ast()` calls `_unwrap_invocation(operands[0])` at line 352 (inside the `sum` handler), FeatureChainExpression nodes will be returned intact rather than being stripped down to their inner FeatureReferenceExpression. This means the subsequent `SysideAdapter.is_instance(operand, "FeatureChainExpression")` check at line 353 will correctly match.

---

### Fix 3: FR-3 — Relocate handlers in `_walk_aggregation_ast()`

**File:** `src/sysml_codegen/extraction/hierarchy_resolver.py:301-429`
**Change type:** Block relocation (no logic changes)

Move the existing `FeatureChainExpression` handler (lines 407-411) and `FeatureReferenceExpression` handler (lines 414-417) to appear between the `OperatorExpression` block (ends at line 344) and the `hasattr(node, "function")` block (starts at line 347).

The relocated code is exactly:

```python
# FeatureChainExpression: child.attr → SingletonTerm
if SysideAdapter.is_instance(node, "FeatureChainExpression"):
    chain_name = extract_feature_chain_name(node)
    ctx.singleton_terms.append(SingletonTerm(source_path=chain_name))
    ctx.input_channels.append(chain_name)
    return chain_name

# FeatureReferenceExpression: local attribute → LocalTerm
if SysideAdapter.is_instance(node, "FeatureReferenceExpression"):
    ref_name = extract_feature_reference_name(node)
    ctx.local_terms.append(LocalTerm(attribute_name=ref_name))
    return ref_name
```

After relocation, the original block locations (lines 406-417) become dead code and must be removed to prevent duplicates.

**Depends on FR-2:** `extract_feature_chain_name()` internally calls `reconstruct_expression(operands[0])`. Without FR-2's reorder, the chain name would contain `"Evaluation()"` artifacts.

---

### Fix 4: FR-4 — Add `part_usage_names` to `HierarchyExtractionResult`

**Files:** 3 files modified

#### 4a. `src/sysml_codegen/extraction/data_models.py:331-338`

Add a new field to `HierarchyExtractionResult`:

```python
@dataclass
class HierarchyExtractionResult:
    redefinitions: list[RedefinitionData]
    design_overrides: list[RedefinitionData]
    multiplicities: list[MultiplicityData]
    aggregation_expressions: list[AggregationExpressionData]
    warnings: list[str]
    part_usage_names: dict[str, set[str]] = field(default_factory=dict)
```

The field maps `owning_part_def_qn` → set of ALL child PartUsage names (both multiplicity and singleton children). Default factory ensures backward compatibility.

#### 4b. `src/sysml_codegen/extraction/hierarchy_resolver.py:483-541`

In `extract_hierarchy_data()`, populate `part_usage_names` during the existing `for part_def in ...` loop at line 501. The scan runs alongside the existing `extract_multiplicities()` call:

```python
# Build part_usage_names: ALL child PartUsage names per PartDef
part_usage_names: dict[str, set[str]] = {}
for part_def in SysideAdapter.elements_of_type(model, "PartDefinition"):
    owning_qn = build_element_qualified_name(part_def)
    names: set[str] = set()
    for member in getattr(part_def, "owned_members", []):
        if SysideAdapter.is_instance(member, "PartUsage"):
            name = sanitize_name(getattr(member, "name", ""))
            if name:
                names.add(name)
    if names:
        part_usage_names[owning_qn] = names
    # ... existing redefs, mults, aggregation code ...
```

Since `extract_hierarchy_data()` already iterates `owned_members` in `extract_multiplicities()`, this adds a parallel scan in the same loop. The iteration is not duplicated — it runs on the same `part_def` element in the same loop iteration.

Practically, this means integrating the `part_usage_names` collection into the existing `for part_def in SysideAdapter.elements_of_type(model, "PartDefinition"):` loop body, not adding a second loop.

Pass the collected dict to the constructor:

```python
return HierarchyExtractionResult(
    redefinitions=all_redefinitions,
    design_overrides=design_overrides,
    multiplicities=all_multiplicities,
    aggregation_expressions=all_aggregations,
    warnings=warnings,
    part_usage_names=part_usage_names,
)
```

#### 4c. `src/sysml_codegen/generation/initialization.py:332-346`

Modify Strategy 2 in `_scope_aggregation_expressions()` to use `part_usage_names` instead of filtering `multiplicities`:

**Before (line 332-346):**
```python
if not instance_paths:
    children = {
        m.part_usage_name.lower()
        for m in hierarchy_data.multiplicities
        if m.owning_part_def_qn == agg_expr.owning_part_qn
    }
    if children:
        for _partdef_qn, qns in virtual_qns_by_partdef.items():
            ...
```

**After:**
```python
if not instance_paths:
    children = {
        name.lower()
        for name in hierarchy_data.part_usage_names.get(
            agg_expr.owning_part_qn, set()
        )
    }
    if children:
        for _partdef_qn, qns in virtual_qns_by_partdef.items():
            ...  # rest of Strategy 2 logic unchanged
```

This naturally handles assemblies with only singleton children (Site Infrastructure, Solar Battery Plant) because `part_usage_names` includes ALL child PartUsages, not just those with multiplicity.

**No new Strategy 3 needed.** The simpler approach of widening Strategy 2's data source is sufficient.

---

### Fix 5: FR-5 — Alias enrichment from CalcUsage bindings

**File:** `src/sysml_codegen/generation/initialization.py`
**Change type:** New function + one call site

#### New function: `_enrich_aliases_from_bindings()`

```python
def _enrich_aliases_from_bindings(
    hierarchy_data: HierarchyExtractionResult,
    calc_usages: list[CalcUsageData],
) -> int:
    """Enrich aggregation aliases from CalcUsage binding parameter names.

    Scans CalcUsage bindings for parameters that reference aggregation
    attribute names. When a binding's source resolves to an aggregation
    attribute with a different param_name, that param_name becomes an alias.

    Returns count of aliases added.
    """
    if not hierarchy_data.aggregation_expressions:
        return 0

    # Build lookup: attribute_name -> list of AggregationExpressionData
    agg_by_attr: dict[str, list[AggregationExpressionData]] = {}
    for agg in hierarchy_data.aggregation_expressions:
        agg_by_attr.setdefault(agg.attribute_name, []).append(agg)

    added = 0
    for usage in calc_usages:
        for binding in usage.bindings:
            if not binding.source_path or not binding.param_name:
                continue

            # Extract leaf name from source_path
            # REFERENCE bindings: "Package::PartDef::attr" -> "attr"
            # CHAIN bindings: "instance.attr" -> "attr"  (use last segment)
            source_leaf = binding.source_path
            if "::" in source_leaf:
                source_leaf = source_leaf.rsplit("::", 1)[-1]
            elif "." in source_leaf:
                source_leaf = source_leaf.rsplit(".", 1)[-1]

            if source_leaf not in agg_by_attr:
                continue
            if binding.param_name == source_leaf:
                continue

            # Add alias to all matching aggregation expressions
            for agg in agg_by_attr[source_leaf]:
                if binding.param_name not in agg.aliases:
                    agg.aliases.append(binding.param_name)
                    added += 1

    return added
```

**Key design decisions:**

1. **Leaf extraction from source_path:** For REFERENCE bindings, `source_path` is a SysML qualified name like `"'Solar Battery Plant'::capital_cost"`. We extract the leaf after the last `::`. For CHAIN bindings, it's a dotted path like `"instance.attr"` — we extract after the last `.`. For bare names (no separators), the full string is used. This handles all three binding formats.

2. **Match against all aggregation expressions with that attribute_name:** Multiple PartDefs may have a `capital_cost` aggregation (Solar Array, Battery System, Solar Battery Plant). We add the alias to all matching aggregations. This is conservative but correct — the backtracker only consumes aliases from expressions that were actually scoped to the relevant design instance.

3. **Deduplication:** The `if binding.param_name not in agg.aliases` guard prevents duplicates.

#### Call site in `build_pipeline_context()`

Insert between Step 3.5 (line 419) and Step 4.7 (line 430):

```python
# Step 3.5: Extract hierarchy data and rewrite virtual CalcUsage bindings
hierarchy_data = _extract_hierarchy_and_rewrite_bindings(
    extractor.model, calc_usages
)

# Step 3.6: Enrich aggregation aliases from CalcUsage bindings
alias_count = _enrich_aliases_from_bindings(hierarchy_data, calc_usages)
if alias_count:
    logger.info("Step 3.6: Enriched %d aggregation alias(es) from CalcUsage bindings", alias_count)

# Step 4: Extract design attributes ...
```

**Why between Step 3.5 and Step 4.7:** Aliases must be populated on `AggregationExpressionData` before:
1. `_scope_aggregation_expressions()` (Step 4.7) creates `ScopedAggregationData` that wraps the expression
2. `DependencyBacktracker.__init__()` (Step 6) reads `agg.expression.aliases` at lines 189-197

**No backtracker changes needed:** The existing BF-7 code at `dependency_backtracker.py:189-197` already propagates `agg.expression.aliases` into `_aggregation_output_index`. If aliases are populated on the data model before the backtracker runs, wiring works automatically.

---

## Potential Risks

| Risk | Mitigation |
|------|-----------|
| FR-2/FR-3 reorder changes behavior for InvocationExpression nodes that happen to also match `is_instance("FeatureChainExpression")` | Impossible — InvocationExpression, FeatureChainExpression, and FeatureReferenceExpression are distinct SysML types with no inheritance overlap |
| FR-4 `part_usage_names` field breaks existing code that constructs `HierarchyExtractionResult` directly | Default factory (`field(default_factory=dict)`) ensures backward compatibility — all existing callers work unchanged |
| FR-5 alias enrichment adds false-positive aliases when multiple PartDefs share an `attribute_name` | Low risk — the backtracker only uses aliases from expressions scoped to the correct design instance, so extra aliases on unrelated PartDefs are harmless |
| FR-5 leaf extraction from `source_path` is fragile if qualified_name format varies | SysML qualified names consistently use `::` as separator. The `rsplit("::", 1)[-1]` pattern handles any depth of nesting |
| Unit test regressions from mock-based tests that assume the old dispatch order | The unit tests use synthetic mocks that explicitly set AST node types. The `is_instance()` checks will still match correctly because mock types are configured to respond to `is_instance()` |

## Integration Strategy

All fixes are confined to the extraction layer (`expression_utils.py`, `hierarchy_resolver.py`, `data_models.py`) and initialization orchestration (`initialization.py`). No changes to:
- Analysis layer (`dependency_backtracker.py`, `parameter_groups.py`)
- Resolution layer (`graph_builder.py`, `models.py`)
- Generation layer (templates, entry_point.py)
- CLI layer

The fixes compose linearly: FR-2 unblocks FR-3, FR-4 provides data for correct scoping, FR-5 provides data for alias propagation. No circular dependencies.

## Validation Approach

### Per-fix verification

1. After FR-2: `reconstruct_expression()` on a FeatureReferenceExpression returns referent name, not `"Evaluation()"`
2. After FR-1+FR-3: `_walk_aggregation_ast()` correctly classifies SumTerm, SingletonTerm, LocalTerm
3. After FR-4: `_scope_aggregation_expressions()` produces ScopedAggregationData for all-singleton assemblies
4. After FR-5: `agg.aliases` contains `"total_capex"` for Solar Battery Plant's capital_cost

### Test commands

```bash
# Run only the 4 failing E2E tests
uv run pytest tests/integration/test_hierarchy_e2e.py -k "no_unsupported or sum_terms or aliases_extracted or total_capex_wired" -v

# Run full E2E suite
uv run pytest tests/integration/test_hierarchy_e2e.py -v

# Full regression
uv run pytest tests/ -v
```

### Success criteria

- All 10 E2E tests pass (4 currently failing → pass, 6 currently passing → no regression)
- Full test suite passes with zero regressions
- No `"Evaluation"` string artifacts in pipeline output

---

Next Step: After approval → `/_my_implement` or `/_my_plan`
