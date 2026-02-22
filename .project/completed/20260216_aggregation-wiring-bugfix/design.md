# Design: Aggregation Wiring Bugfix (Bug A + Bug B)

**Status:** Draft
**Owner:** Reid Westwood
**Created:** 2026-02-16 17:23 UTC
**Branch:** cost-pattern
**Commit:** 118db97

## Overview

Four surgical fixes — three FCE/OE check reorders across extraction files,
one resolution addition in graph building — to wire 45 additional aggregation
inputs and fix latent FCE mishandling in the expression compiler and
expression reconstructor. Each Bug A fix is a block move. Bug B is a ~15-line
resolution block inserted before the existing entry point fallback.

## Related Artifacts

- **Spec:** `.project/active/aggregation-wiring-bugfix/spec.md`
- **Spike script:** `scripts/spike_agg_wiring_h1_h4.py` (reference code for both fixes)
- **Spike results:** `.project/active/aggregation-wiring-spikes/plan.md`
- **Research (misclassification):** `.project/research/20260216-aggregation-expression-misclassification.md`
- **Research (arch review):** `.project/research/20260215-235500_aggregation-wiring-design-vs-architecture-review.md`

## Research Findings

### Bug A Site: `_walk_aggregation_ast()` Check Ordering

**File:** `src/sysml_codegen/extraction/hierarchy_resolver.py:305-434`

The function has four type-check branches in order:
1. `OperatorExpression` (line 328) — recurses into operands
2. `FeatureChainExpression` (line 351) — classifies as SingletonTerm
3. `FeatureReferenceExpression` (line 358) — classifies as LocalTerm
4. `InvocationExpression` / `sum()` (line 364) — classifies as SumTerm

`SysideAdapter.is_instance()` (`agentic_mbse/sysml/syside_adapter.py:231-257`)
uses `elem.isinstance(sysml_type)` for real SysIDE objects. In SysIDE's type
hierarchy, `FeatureChainExpression` is a subtype of `OperatorExpression`, so
both checks return True. Since OE is checked first (line 328), standalone
dotted refs like `array_bos.capital_cost` enter the OE unary branch, which
recurses into `operands[0]` (a bare `FeatureReferenceExpression("array_bos")`)
and classifies it as `LocalTerm("array_bos")` — losing the `.capital_cost`
target entirely.

**Spike B reference code** (`scripts/spike_agg_wiring_h1_h4.py:326-435`):
`_walk_aggregation_ast_patched()` is a full copy of `_walk_aggregation_ast()`
with the ONLY change being FCE check moved before OE check (lines 341-346
before lines 348-369). Spike B confirmed exactly 37 reclassifications with
zero SumTerm regression.

**Why `sum()` is unaffected:** `sum(pv_module.capital_cost)` wraps the FCE
in an `InvocationExpression`. `InvocationExpression` does NOT match
`is_instance("OperatorExpression")`, so it falls through to the sum handler
at line 364. The FCE inside sum is unwrapped by `_unwrap_invocation()`
(line 369), which has explicit FCE/FRE guards (lines 294-297). The reorder
only affects top-level FCE nodes — those NOT wrapped in `sum()`.

### Bug A2 Site: `build_expression_ast()` Check Ordering

**File:** `src/sysml_codegen/extraction/expression_compiler.py:290-405`

Same bug pattern as A1. The function checks OE (line 313) before FCE
(line 395). A FeatureChainExpression node enters the OE handler, which
extracts `operator = "."` (the dot operator). Since `"."` is not in
`PYTHON_OPERATOR_MAP` (expression_compiler.py:151-159), line 333 returns
`ExpressionAST.unsupported(".", "unsupported operator: .")`.

The intended FCE handler (line 395) would return
`ExpressionAST.unsupported(type_name, "feature chain expression not supported in CalcDef output")`.

**Impact:** Currently **benign** — both paths produce an unsupported node.
But the diagnostic text is wrong/misleading, and the bug could become
dangerous if the OE handler is ever modified to handle `"."` operators.

**Callers:** `build_expression_ast()` is called from the expression compiler
pipeline (Step 6.5) for CalcDef output expressions. FCE nodes in CalcDef
outputs are rare but valid SysML.

### Bug A3 Site: `reconstruct_expression()` Check Ordering

**File:** `src/sysml_codegen/extraction/expression_utils.py:34-75`

Same bug pattern. The function checks OE (line 44) before FCE (line 50).
A FeatureChainExpression node enters `reconstruct_operator_expression()`
(line 45), which:
- Extracts `operator = "."` (the dot operator)
- Extracts `operands` — a single-element list `[FeatureReferenceExpression]`
- Hits unary path (line 94-100): returns `".(array_bos)"`

The intended FCE handler (line 50) calls `extract_feature_chain_name()` →
`"array_bos.capital_cost"`.

**Impact:** **Observable** — FCE nodes get mangled expression text.
`reconstruct_expression()` is called from:
- `hierarchy_resolver.py:133` — `RedefinitionData.expression_text` field
- `extractor.py:179` — CalcDef expression text
- `computed_attribute_extractor.py:177` — computed attribute expression text
- `constraint_extractor.py:100,107,110,115` — constraint expression text

Any FCE node passing through these paths gets wrong display text. The mangled
text (`".(name)"`) is display-only and doesn't affect wiring logic, but it
produces confusing diagnostic output and incorrect `expression_text` fields
on data models.

### Bug B Site: LocalTerm Processing in `_build_aggregation_module()`

**File:** `src/sysml_codegen/resolution/graph_builder.py:1015-1036`

The current code unconditionally creates entry points for all LocalTerms:

```python
for l_term in agg.expression.local_terms:
    ep_qn = f"{agg.module_eqn}__{l_term.attribute_name}"
    if ep_qn not in entry_points:
        # ... creates EntryPoint ...
    # ... creates ModuleInput with source_type="entry_point" ...
```

No resolution is attempted. The `_resolve_aggregation_input_channel()` function
(line 772) has an early return `if "." not in symbolic_ref: return None` which
prevents it from resolving bare LocalTerm attribute names.

**Spike C reference code** (`scripts/spike_agg_wiring_h1_h4.py:561-656`):
`spike_c_sibling_agg_resolution()` queries the OutputRegistry with Key_D
format (`"{part_usage}.{attr}"`) for all 8 idiot_index LocalTerms.
Results: 8/8 resolved, all to double-attr channels
(`*__{attr}__{attr}`). `misc_hardware_cost` correctly unresolved.

**Key insight from Spike C:** The sibling agg outputs are already in the
registry (registered during Phase 1b, before graph building). We don't need
to call `_resolve_aggregation_input_channel()` — a direct
`canonical_channels` membership check on the double-attr channel format is
sufficient, with `output_registry.resolve()` as fallback.

### Resolution Code Path (No Changes Needed)

**File:** `src/sysml_codegen/resolution/graph_builder.py:754-839`

`_resolve_aggregation_input_channel()` already handles SingletonTerms
correctly via its 3-step resolution:
1. CHAIN redef search (lines 790-813)
2. Scoped key lookup (lines 815-829)
3. Unscoped Key_D fallback (lines 831-839)

**Spike D reference code** (`scripts/spike_agg_wiring_h1_h4.py:662-868`):
Confirmed all 12 plant-level SingletonTerms resolve — Step 2 (scoped key)
hits for all 12, Step 3 (Key_D) also hits as fallback. No code changes needed.

### SingletonTerm Processing (No Changes Needed)

**File:** `src/sysml_codegen/resolution/graph_builder.py:954-1013`

Already uses registry-first resolution (lines 961-970), falling back to
direct channel construction (lines 972-984), then entry point (lines 986-1006).
This code was fixed in the prior scoped-registry commit (7256d82). The 37
new SingletonTerms from Bug A will flow through this existing path.

### Existing Test Patterns

**Mock AST classes** (`tests/unit/test_hierarchy_resolver.py:49-79`):
`SysideAdapter.is_instance()` falls back to `type_name in type(elem).__name__`
for mock objects (syside_adapter.py:257). So:
- `MockFeatureChainExpression` matches `"FeatureChainExpression"` but NOT
  `"OperatorExpression"`
- `MockOperatorExpression` matches `"OperatorExpression"` but NOT
  `"FeatureChainExpression"`

This means existing mocks **do not reproduce the subtype relationship** that
causes Bug A. To test the fix, we need a new mock class whose name contains
both strings.

**Graph builder test helpers** (`tests/unit/test_graph_builder_aggregation.py:45-71`):
`_make_scoped_agg()` factory builds `ScopedAggregationData` with customizable
term lists. Tests for `_build_aggregation_module()` construct a registry with
expected channels pre-registered, then assert `source_type` and
`producer_channel` on the resulting `ModuleInput` objects. The existing
`test_local_term_creates_entry_point` (line 421) is the direct baseline for
Bug B's test.

### `get_channel_name` Utility

**File:** `src/sysml_codegen/core/qualified_names.py:98-100`

```python
def get_channel_name(usage_qualified_name: str, output_attr_name: str) -> str:
    return f"{usage_qualified_name}__{output_attr_name}"
```

For aggregation modules, `module_eqn = "{instance_path}__{attr}"` and the
single output is named `"root"` but uses `field_name="root"`. Wait — let me
verify. The output channel is:
`get_channel_name(module_eqn, "root")` = `"{instance_path}__{attr}__root"`.

Actually no. Looking at graph_builder.py:1047-1051, the output is
`ModuleOutput(field_name="root", ...)`. But the channel name is the PQN:
`get_channel_name(module_eqn, "root")`. So the sibling agg channel for
`capital_cost` on `solar_array` would be:
`Design__plant__solar_array__capital_cost__root`.

Wait — Spike C shows the resolved channels end with `__capital_cost__capital_cost`
(double-attr), not `__capital_cost__root`. Let me re-examine.

Actually, looking more carefully at graph_builder.py:1046-1058 and the spike
output, the actual output uses `attr_name` not `"root"`:

```
# graph_builder.py:1046-1058
output = ModuleOutput(
    field_name="root",
    python_type="float",
    channel_name=get_channel_name(
        agg.module_eqn, agg.expression.attribute_name
    ),
)
```

So the channel name is `get_channel_name("Design__plant__solar_array__capital_cost", "capital_cost")` = `"Design__plant__solar_array__capital_cost__capital_cost"`. This is the double-attr format.

For Bug B resolution, we need to construct this same format to check
`canonical_channels`.

---

## Proposed Design

### Change 1 (A1): `_walk_aggregation_ast()` — FCE Before OE

**File:** `src/sysml_codegen/extraction/hierarchy_resolver.py`
**Change:** Move lines 350-355 (FCE block) to immediately after the null
check (line 325), before lines 328-348 (OE block).

**Before** (current ordering, lines 324-355):

```python
    if node is None:
        return ""

    # OperatorExpression: recurse into operands          ← line 328
    if SysideAdapter.is_instance(node, "OperatorExpression"):
        ...  # lines 329-348

    # FeatureChainExpression: child.attr → SingletonTerm  ← line 350
    if SysideAdapter.is_instance(node, "FeatureChainExpression"):
        ...  # lines 351-355
```

**After** (fixed ordering):

```python
    if node is None:
        return ""

    # FeatureChainExpression: child.attr → SingletonTerm
    # MUST be before OperatorExpression — FCE is a subtype of OE in
    # SysIDE's type system, so both is_instance() checks return True
    # on the same node. The more specific check must come first.
    # See: spike_agg_wiring_h1_h4.py spike_a (H1 CONFIRMED: 37/37 dual-match)
    if SysideAdapter.is_instance(node, "FeatureChainExpression"):
        chain_name = extract_feature_chain_name(node)
        ctx.singleton_terms.append(SingletonTerm(source_path=chain_name))
        ctx.input_channels.append(chain_name)
        return chain_name

    # OperatorExpression: recurse into operands
    if SysideAdapter.is_instance(node, "OperatorExpression"):
        ...  # unchanged
```

**Reference:** `scripts/spike_agg_wiring_h1_h4.py:340-369` —
`_walk_aggregation_ast_patched()` is the exact same reorder, validated by
Spike B (37 reclassifications, 0 SumTerm regression).

**What changes:** The 5-line FCE block (check + body) moves up. The OE block
and everything after it stays identical. No new logic, no new branches.

### Change 2 (A2): `build_expression_ast()` — FCE Before OE

**File:** `src/sysml_codegen/extraction/expression_compiler.py`
**Change:** Move lines 394-399 (FCE block) to immediately before line 313
(OE block).

**Before** (current ordering, lines 312-399):

```python
    # --- OperatorExpression ---                          ← line 313
    if SysideAdapter.is_instance(syside_node, "OperatorExpression"):
        operator = ""
        ...  # lines 314-368 (operator handling, returns ExpressionAST)

    # --- FeatureReferenceExpression ---                  ← line 371
    if SysideAdapter.is_instance(syside_node, "FeatureReferenceExpression"):
        ...  # lines 372-382

    # --- Literals ---                                    ← line 385
    ...  # lines 385-392

    # --- FeatureChainExpression ---                      ← line 395
    if SysideAdapter.is_instance(syside_node, "FeatureChainExpression"):
        return ExpressionAST.unsupported(
            type(syside_node).__name__,
            "feature chain expression not supported in CalcDef output",
        )
```

**After** (fixed ordering):

```python
    # --- FeatureChainExpression ---
    # MUST be before OperatorExpression — FCE is a subtype of OE in
    # SysIDE's type system. Without this, FCE nodes enter the OE handler
    # and produce "unsupported operator: ." instead of the correct diagnostic.
    if SysideAdapter.is_instance(syside_node, "FeatureChainExpression"):
        return ExpressionAST.unsupported(
            type(syside_node).__name__,
            "feature chain expression not supported in CalcDef output",
        )

    # --- OperatorExpression ---
    if SysideAdapter.is_instance(syside_node, "OperatorExpression"):
        ...  # unchanged
```

**What changes:** The 5-line FCE block moves up. Everything else stays
identical. No new logic.

### Change 3 (A3): `reconstruct_expression()` — FCE Before OE

**File:** `src/sysml_codegen/extraction/expression_utils.py`
**Change:** Move lines 50-51 (FCE block) to immediately before line 44
(OE block).

**Before** (current ordering, lines 43-51):

```python
    # line 44
    if SysideAdapter.is_instance(expr_node, "OperatorExpression"):
        return reconstruct_operator_expression(expr_node)

    # line 47
    if SysideAdapter.is_instance(expr_node, "FeatureReferenceExpression"):
        return extract_feature_reference_name(expr_node)

    # line 50
    if SysideAdapter.is_instance(expr_node, "FeatureChainExpression"):
        return extract_feature_chain_name(expr_node)
```

**After** (fixed ordering):

```python
    # FeatureChainExpression MUST be before OperatorExpression — FCE is a
    # subtype of OE in SysIDE's type system. Without this, FCE nodes enter
    # reconstruct_operator_expression() and produce ".(name)" instead of
    # "name.attr".
    if SysideAdapter.is_instance(expr_node, "FeatureChainExpression"):
        return extract_feature_chain_name(expr_node)

    if SysideAdapter.is_instance(expr_node, "OperatorExpression"):
        return reconstruct_operator_expression(expr_node)

    if SysideAdapter.is_instance(expr_node, "FeatureReferenceExpression"):
        return extract_feature_reference_name(expr_node)
```

**What changes:** The 2-line FCE block moves up. FRE order relative to OE
is unchanged (FRE is not a subtype of OE, so order doesn't matter there).

### Change 4 (B): LocalTerm Sibling Agg Resolution

**File:** `src/sysml_codegen/resolution/graph_builder.py`
**Change:** In `_build_aggregation_module()`, replace the unconditional
entry point creation for LocalTerms (lines 1015-1036) with a
try-resolve-then-fallback pattern.

**Before** (current, lines 1015-1036):

```python
    # Process LocalTerms (PartDef-local attribute references)
    for l_term in agg.expression.local_terms:
        ep_qn = f"{agg.module_eqn}__{l_term.attribute_name}"
        if ep_qn not in entry_points:
            param_group = group_deriver.classify(ep_qn) if group_deriver else None
            entry_points[ep_qn] = EntryPoint(
                qualified_name=ep_qn,
                simple_name=l_term.attribute_name,
                entry_type=EntryPointType.DESIGN_ATTRIBUTE,
                param_group=param_group,
            )
        ep = entry_points[ep_qn]
        inputs.append(ModuleInput(
            param_name=l_term.attribute_name,
            python_type="float",
            source=InputSource(
                source_type="entry_point",
                qualified_name=ep_qn,
                param_group=ep.param_group,
            ),
        ))
        ref_to_inputs[l_term.attribute_name] = f"inputs.{l_term.attribute_name}"
```

**After** (with sibling resolution):

```python
    # Process LocalTerms (PartDef-local attribute references)
    for l_term in agg.expression.local_terms:
        l_source: InputSource | None = None

        # Try: sibling aggregation output at the same scope.
        # Aggregation modules use double-attr channel format:
        #   get_channel_name("{instance_path}__{attr}", attr) → "{ip}__{attr}__{attr}"
        # Spike C (H3 CONFIRMED): 8/8 idiot_index refs resolve this way.
        sibling_eqn = f"{agg.instance_path}__{l_term.attribute_name}"
        sibling_channel = get_channel_name(sibling_eqn, l_term.attribute_name)
        if sibling_channel in canonical_channels:
            l_source = InputSource(
                source_type="module_output",
                producer_channel=sibling_channel,
            )

        if l_source is None:
            # Genuinely unresolvable → entry point (e.g., misc_hardware_cost)
            ep_qn = f"{agg.module_eqn}__{l_term.attribute_name}"
            if ep_qn not in entry_points:
                param_group = group_deriver.classify(ep_qn) if group_deriver else None
                entry_points[ep_qn] = EntryPoint(
                    qualified_name=ep_qn,
                    simple_name=l_term.attribute_name,
                    entry_type=EntryPointType.DESIGN_ATTRIBUTE,
                    param_group=param_group,
                )
            ep = entry_points[ep_qn]
            l_source = InputSource(
                source_type="entry_point",
                qualified_name=ep_qn,
                param_group=ep.param_group,
            )

        inputs.append(ModuleInput(
            param_name=l_term.attribute_name,
            python_type="float",
            source=l_source,
        ))
        ref_to_inputs[l_term.attribute_name] = f"inputs.{l_term.attribute_name}"
```

**Design decisions in the resolution approach:**

1. **Direct `canonical_channels` check, not `output_registry.resolve()`.**
   We construct the exact expected channel name and check membership in the
   `canonical_channels` frozenset (O(1)). This is more precise than a
   `resolve()` call because it targets the specific aggregation output at
   the same scope — no risk of resolving to a wrong-scope sibling with the
   same short name.

2. **No `_resolve_aggregation_input_channel()` call.** That function's early
   return `if "." not in symbolic_ref: return None` (line 772) would reject
   bare LocalTerm names. We could change it, but per the spec, no changes to
   that function.

3. **Double-attr channel format is the key insight.** Aggregation module EQN
   is `{instance_path}__{attr}` (graph_builder.py:872). Its output channel
   is `get_channel_name(module_eqn, attr)` (graph_builder.py:1049-1051),
   producing `{instance_path}__{attr}__{attr}`. Spike C confirmed this is
   exactly what the registry contains.

4. **`canonical_channels` is already captured** on line 955 (at the start of
   SingletonTerm processing, just above the LocalTerm block). The variable is
   in scope and reusable.

5. **Deliberate FR-3 deviation: Key_D fallback omitted.** The spec says
   resolution SHOULD include Key_D registry fallback (`{part_usage}.{attr}`).
   This design intentionally omits Key_D because the direct
   `canonical_channels` check is both sufficient (Spike C: 8/8 resolved) and
   more precise — it is scope-safe by construction since `agg.instance_path`
   is baked into the channel name. A Key_D `resolve()` call could
   theoretically match a wrong-scope sibling with the same short name. If
   edge cases emerge in other models, Key_D can be added as a second-tier
   fallback between the `canonical_channels` check and the entry point
   creation.

**Reference:** `scripts/spike_agg_wiring_h1_h4.py:561-656` —
`spike_c_sibling_agg_resolution()` validates the Key_D format resolves, but
the design uses the more direct `canonical_channels` membership check instead,
which is more precise and avoids registry key ambiguity.

---

## Testing Strategy

### Why Integration Tests, Not Mocks

The entire Bug A exists because `SysideAdapter.is_instance()` behaves
differently on real SysIDE objects than on Python mock classes. In SysIDE's
type system, `FeatureChainExpression` is a subtype of `OperatorExpression` —
both `is_instance()` checks return True on the same real node. Mock classes
cannot reproduce this: `MockFeatureChainExpression` and
`MockOperatorExpression` are independent Python classes with no inheritance
relationship.

Engineering a mock that artificially reproduces the dual-match (e.g., a class
named `MockFeatureChainExpressionOperatorExpression`) tests our mock
engineering, not the actual fix. The real solar_battery model is in
`tests/fixtures/solar_battery_model/` and `build_pipeline_context()` runs the
full extraction pipeline including `_walk_aggregation_ast()`,
`build_expression_ast()`, and `reconstruct_expression()` against real SysIDE
AST nodes. This is the only way to test that the FCE/OE ordering fix actually
works.

**Existing pattern:** `tests/integration/test_hierarchy_e2e.py` already uses
`build_pipeline_context([solar_battery_model])` with a `scope="class"` fixture
to test extraction and wiring against real data. We follow this pattern.

### Test File Locations

- Bug A tests (all 3 sites): `tests/integration/test_hierarchy_e2e.py`
  (alongside existing extraction + wiring E2E tests). The fixture-based
  `pipeline_context` runs the full pipeline including all 3 Bug A sites.
- Bug B tests: `tests/unit/test_graph_builder_aggregation.py` (alongside
  existing `test_local_term_creates_entry_point` at line 421). Bug B tests
  resolution logic with real data model objects (`OutputRegistry`,
  `_make_scoped_agg()`), not AST dispatch — unit tests are appropriate here.

### Bug A Tests — Integration (Real Solar Battery Fixture)

**File:** `tests/integration/test_hierarchy_e2e.py`

Add a new test class `TestAggregationFCEOrdering` with a `scope="class"`
`pipeline_context` fixture (reusing the existing pattern).

**Test A-1: `test_fce_nodes_classified_as_singleton_terms`** (FR-1, FR-2)

Assert term counts across all aggregation expressions match Spike B results:

```python
def test_fce_nodes_classified_as_singleton_terms(
    self, pipeline_context: PipelineContext,
):
    """Bug A1: FeatureChainExpression nodes must classify as SingletonTerms,
    not LocalTerms. FCE is a subtype of OE in SysIDE's type system — the
    FCE check must run before OE to prevent dotted refs like
    array_bos.capital_cost from entering the OE handler."""
    hierarchy = pipeline_context.hierarchy_data
    assert hierarchy is not None

    total_sum = sum(len(a.sum_terms) for a in hierarchy.aggregation_expressions)
    total_singleton = sum(len(a.singleton_terms) for a in hierarchy.aggregation_expressions)
    total_local = sum(len(a.local_terms) for a in hierarchy.aggregation_expressions)

    # Spike B verified: {sum: 12, singleton: 37, local: 9}
    assert total_sum == 12, f"SumTerm count {total_sum} != 12 (regression)"
    assert total_singleton == 37, f"SingletonTerm count {total_singleton} != 37 (FCE misclassified)"
    assert total_local == 9, f"LocalTerm count {total_local} != 9 (FCE misclassified)"
```

This single test validates:
- FR-1: FCE check runs before OE (37 SingletonTerms prove it)
- FR-2: Zero SumTerm regression (count stays at 12)
- The fix works on real SysIDE AST nodes, not mocks

**Test A-2: `test_singleton_terms_have_dotted_source_paths`**

Assert that SingletonTerms extracted from real FCE nodes have proper dotted
`source_path` values (not truncated bare names from the OE mishandling):

```python
def test_singleton_terms_have_dotted_source_paths(
    self, pipeline_context: PipelineContext,
):
    """Bug A1: SingletonTerms from FCE nodes must have dotted source paths
    (e.g., 'allocation_model.total_allocation'), not bare names."""
    hierarchy = pipeline_context.hierarchy_data
    assert hierarchy is not None

    for agg in hierarchy.aggregation_expressions:
        for st in agg.singleton_terms:
            assert "." in st.source_path, (
                f"SingletonTerm in {agg.owning_part_name}.{agg.attribute_name} "
                f"has bare source_path '{st.source_path}' — FCE misclassified as FRE"
            )
```

**Test A-3: `test_no_unsupported_dot_operator_in_expressions`** (FR-2a)

Assert that no aggregation expression text contains `"unsupported operator: ."`,
which is the signature of Bug A2 (FCE entering the OE handler in
`build_expression_ast()`):

```python
def test_no_unsupported_dot_operator_in_expressions(
    self, pipeline_context: PipelineContext,
):
    """Bug A2: FCE nodes must not produce 'unsupported operator: .' diagnostic.
    This happens when FCE enters the OE handler in build_expression_ast()."""
    # This validates at the CalcDef expression level, where build_expression_ast is called
    for calc_def in pipeline_context.calc_defs:
        for output in calc_def.outputs:
            if hasattr(output, 'expression_text') and output.expression_text:
                assert "unsupported operator: ." not in output.expression_text, (
                    f"CalcDef {calc_def.qualified_name} output has Bug A2 artifact: "
                    f"{output.expression_text}"
                )
```

**Test A-4: `test_no_mangled_dot_parenthesized_expressions`** (FR-2b)

Assert no expression text contains `".(name)"` patterns, which is the
signature of Bug A3 (FCE entering `reconstruct_operator_expression()`):

```python
def test_no_mangled_dot_parenthesized_expressions(
    self, pipeline_context: PipelineContext,
):
    """Bug A3: FCE nodes must not produce '.(name)' mangled text.
    This happens when FCE enters reconstruct_operator_expression()."""
    import re
    mangled_pattern = re.compile(r'\.\([a-zA-Z_]+\)')

    hierarchy = pipeline_context.hierarchy_data
    assert hierarchy is not None
    for agg in hierarchy.aggregation_expressions:
        assert not mangled_pattern.search(agg.transformed_expression), (
            f"Aggregation {agg.owning_part_name}.{agg.attribute_name} "
            f"has Bug A3 artifact in: {agg.transformed_expression}"
        )
```

### Bug B Tests

**Test 4: LocalTerm resolves to sibling aggregation output**

Use `_make_scoped_agg()` with:
- `local_terms=[LocalTerm("capital_cost")]`
- `instance_path="Design__plant__solar_array"`
- `attribute_name="idiot_index"`

Pre-register the sibling agg channel in the registry:
```python
registry = OutputRegistry()
sibling_channel = get_channel_name(
    "Design__plant__solar_array__capital_cost", "capital_cost"
)  # → "Design__plant__solar_array__capital_cost__capital_cost"
registry.register(sibling_channel, ["solar_array.capital_cost"])
```

Call `_build_aggregation_module(agg, [], registry, entry_points, None)`. Assert:
- Input `capital_cost` has `source_type="module_output"`
- `producer_channel == sibling_channel`
- `"capital_cost"` key NOT in `entry_points` (no entry point created)

**Test 5: Unresolvable LocalTerm still becomes entry point**

Use `_make_scoped_agg()` with:
- `local_terms=[LocalTerm("misc_hardware_cost")]`
- Empty registry (no sibling channel exists)

Assert:
- Input `misc_hardware_cost` has `source_type="entry_point"`
- Entry point created with `entry_type=EntryPointType.DESIGN_ATTRIBUTE`

This is the same as the existing `test_local_term_creates_entry_point` (line
421) — it should pass without changes (regression guard).

**Test 6: Mixed LocalTerms — some resolve, some don't**

Use `_make_scoped_agg()` with:
- `local_terms=[LocalTerm("capital_cost"), LocalTerm("raw_material_cost"), LocalTerm("misc_hardware_cost")]`
- Registry with both `capital_cost` and `raw_material_cost` sibling channels
  registered but NOT `misc_hardware_cost`

Assert:
- `capital_cost` → `source_type="module_output"`
- `raw_material_cost` → `source_type="module_output"`
- `misc_hardware_cost` → `source_type="entry_point"`

---

## Potential Risks

| Risk | Likelihood | Mitigation |
|------|-----------|-----------|
| A1 reorder breaks `sum()` terms | Very Low | Spike B empirically verified 0 regression. `InvocationExpression` does not match `is_instance("OperatorExpression")`, so sum handler is unaffected. Test A-1 asserts SumTerm count stays at 12 against real fixture. |
| A2/A3 reorder breaks OE handling | Very Low | OE nodes that are NOT FCE subtypes will fail the FCE check and fall through to OE — no change in behavior. Tests A-3 and A-4 validate no artifacts in real extraction output. |
| Bug B resolves `misc_hardware_cost` incorrectly | Very Low | `misc_hardware_cost` has no sibling agg module, so `canonical_channels` check returns False. Spike C verified this. Test B-5 guards this. |
| Bug B resolves to wrong-scope sibling | Low | Direct channel construction uses `agg.instance_path` (same scope), not a global registry lookup. Two assemblies with same attr name produce different channels because `instance_path` differs. |
| Existing tests break from reorders | Very Low | Existing mock-based unit tests use independent mock classes that don't reproduce the FCE/OE subtype relationship, so they are unaffected by the reorder. Integration tests against real fixture validate the actual behavior. |

## Validation Approach

### Automated

1. `uv run pytest tests/integration/test_hierarchy_e2e.py -v` — Bug A tests (real solar_battery fixture)
2. `uv run pytest tests/unit/test_graph_builder_aggregation.py -v` — Bug B tests + regression
3. `uv run pytest tests/` — full suite (647+ tests)

### Manual Verification

Run the spike script post-fix to confirm the wiring counts match:
```bash
uv run python scripts/spike_agg_wiring_h1_h4.py
```

Expected: Spike B should show `{sum: 12, singleton: 37, local: 9}` in BOTH
before and after (since the fix is now in production code, both orderings
produce the same result).

### Acceptance Criteria Mapping

| AC | Verified By |
|----|-------------|
| `array_bos.capital_cost` → SingletonTerm | Test A-1 (real fixture: count=37), Test A-2 (dotted paths) |
| SumTerm count unchanged at 12 | Test A-1 (real fixture: count=12) |
| SingletonTerm count 0 → 37 | Test A-1 (real fixture: count=37) |
| LocalTerm count 46 → 9 | Test A-1 (real fixture: count=9) |
| FCE diagnostic text correct (A2) | Test A-3 (no `"unsupported operator: ."` in real output) |
| FCE reconstruction correct (A3) | Test A-4 (no `".(name)"` patterns in real output) |
| 8 idiot_index refs → MODULE_OUTPUT | Test B-4, Test B-6 |
| `misc_hardware_cost` → ENTRY_POINT | Test B-5, Test B-6 |
| 57/70 wired | Spike rerun |
| Existing tests pass | Full pytest run |

---

## Implementation Summary

| # | File | Change | Lines Affected |
|---|------|--------|---------------|
| 1 | `src/sysml_codegen/extraction/hierarchy_resolver.py` | A1: Move FCE block (5 lines + comment) before OE block | ~328-355 |
| 2 | `src/sysml_codegen/extraction/expression_compiler.py` | A2: Move FCE block (5 lines + comment) before OE block | ~313-399 |
| 3 | `src/sysml_codegen/extraction/expression_utils.py` | A3: Move FCE block (2 lines + comment) before OE block | ~44-51 |
| 4 | `src/sysml_codegen/resolution/graph_builder.py` | B: Add sibling agg resolution before entry point in LocalTerm loop | ~1015-1036 |
| 5 | `tests/integration/test_hierarchy_e2e.py` | A: 4 integration tests (real solar_battery fixture) | New class at end |
| 6 | `tests/unit/test_graph_builder_aggregation.py` | B: 3 tests (sibling resolution) | New code at end |

Total production code change: ~12 lines moved + ~15 lines added.
Total test code: 7 new tests across 2 files (0 new files).

---

**Next Step:** After approval → `/_my_plan` or `/_my_implement`
