# Design: SysIDE AST Discovery for Hierarchy Patterns

**Status:** Draft
**Owner:** Reid Westwood
**Created:** 2026-02-10T03:32:36Z
**Updated:** 2026-02-10T03:32:36Z
**Branch:** cost-pattern
**Commit:** 009b076

## Overview

Design a probe script that loads the solar_battery model via SysIDE and systematically inspects the AST for the 10 hierarchy patterns identified in the spec (Q1-Q10). The script produces structured output answering each question with concrete attribute names, node types, and traversal code.

## Related Artifacts

- **Spec:** `.project/active/hierarchy-spike/spec.md`
- **Epic:** `.project/backlog/epic_costed_component_pattern.md` (COST-PATTERN, Item 1)
- **Research (gap analysis):** `.project/research/20260109-205122_cost-modeling-codegen-changes.md`
- **Model fixture:** `tests/fixtures/solar_battery_model/` (library.sysml, costing.sysml, design.sysml)
- **Prior spike scripts:** `scripts/spike_extract_expression_asts.py`, `scripts/spike_classify_compilability.py`, etc.

## Research Findings

### Existing Script Pattern (5 prior spikes)

All spike scripts in `scripts/` follow a consistent structure:
- **Model loading:** `SysMLDataExtractor(model_paths)` + `.load_models()` + `.adapter.elements_of_type()`
- **Multi-suite support:** `DEFAULT_SUITES` list with CLI arg override
- **Output:** Structured text with per-question sections, tables, and code-like dumps
- **Error handling:** Graceful skip on load failure, try/except around attribute access

Reference: `scripts/spike_extract_expression_asts.py:71-80` for `load_and_extract()` pattern.

### SysIDE/Syside Metamodel API (from docs)

**Key attributes for this spike:**

| Concept | Syside Attribute | Returns | Doc Reference |
|---------|-----------------|---------|---------------|
| Redefinition | `Feature.owned_redefinitions` | `LazyIterator[Redefinition]` | `Feature.md` |
| Redefined feature | `Redefinition.redefined_feature` | `Feature \| None` | `Redefinition.md` |
| Redefining feature | `Redefinition.redefining_feature` | `Feature \| None` | `Redefinition.md` |
| Specialization chain | `Type.owned_specializations` | list of `Specialization` | `Type.md` |
| General type | `Specialization.general` | `Type` | `Specialization.md` |
| Specific type | `Specialization.specific` | `Type` | `Specialization.md` |
| Multiplicity | `Type.multiplicity` | `Multiplicity \| None` | `Type.md` |
| MultiplicityRange bounds | `MultiplicityRange.lower_bound`, `.upper_bound` | `Expression \| None` | `MultiplicityRange.md` |
| Cached bounds | `MultiplicityRange.cached_lower_bound`, `.cached_upper_bound` | `int`, `int \| None` | `MultiplicityRange.md` |
| Owned features | `Type.owned_features` | iterator | `Type.md` |
| Owned members | `Namespace.owned_members` | iterator | `Namespace.md` |
| Feature value expr | `Feature.feature_value_expression` | `Expression \| None` | `Feature.md` |
| Feature typing | `Feature.owned_typings` | `LazyIterator[FeatureTyping]` | `Feature.md` |
| Owner | `Element.owner` | `Element` | `Element.md` |
| Owning type | `Feature.owning_type` | `Type \| None` | `Feature.md` |
| Types of a feature | `Feature.types` | `LazyIterator[Type]` | `Feature.md` |
| Inherited features | `Type.inherited_features` | iterator | `Type.md` |
| Abstract flag | `Type.is_abstract` | `bool` | `Type.md` |

### SysideAdapter Type Map

Current type map supports: `CalculationDefinition`, `CalculationUsage`, `AttributeUsage`, `PartDefinition`, `PartUsage`, `FeatureTyping`, `FeatureChainExpression`, `FeatureReferenceExpression`, `OperatorExpression`, `LiteralInteger`, `LiteralRational`, `LiteralString`, `LiteralBoolean`, `LiteralInfinity`.

**Not in type map** (may need raw isinstance or `type(elem).__name__` checks): `Redefinition`, `Specialization`, `Multiplicity`, `MultiplicityRange`, `InvocationExpression`.

This is expected -- the spike probes these types directly on elements (e.g., `elem.owned_redefinitions`) rather than using `elements_of_type()`.

### Solar Battery Model Structure

The model has a clear 4-level hierarchy perfect for probing all patterns:

```
costing.sysml:    abstract part def 'Costed Component' { cas_category, capital_cost, ... }
library.sysml:    9 leaf PartDefs :> 'Costed Component' with embedded cost_model CalcUsages
                  3 assembly PartDefs with sum() aggregation + multiplicity
                  1 top-level PartDef ('Solar Battery Plant')
design.sysml:     1 design instance (solar_battery_plant) with `part redefines` + deep :>>
```

**Probe targets per question:**

| Q | Target Elements | SysML Source |
|---|----------------|-------------|
| Q1 | `PV Module.cost_model`, `Solar Array.allocation_model`, `solar_battery_plant.energy_production` | library:378, library:607, design:68 |
| Q2 | `PV Module.:>> capital_cost`, `Solar Array.:>> capital_cost`, `PV Module.:>> idiot_index`, `PV Module.:>> cas_category` | library:384, library:615, library:388, library:371 |
| Q3 | `part redefines solar_array` vs `part solar_array` | design:25, library:738 |
| Q4 | `:>> pv_module.wattage = 400.0` | design:26 |
| Q5 | `part pv_module : 'PV Module' [module_count]` | library:602 |
| Q6 | `sum(pv_module.capital_cost)` | library:616 |
| Q7 | Full chain: `solar_battery_plant` → ... → `cost_model` → `PVModuleCostCalc` | design:18 through library:378 |
| Q8 | `attribute misc_hardware_cost` vs `:>> capital_cost` in `Solar Array` | library:612 vs library:615 |
| Q9 | `default := 1.07` on CalcDef param vs `default := 20` on part attr | library:39 vs library:598 |
| Q10 | `in total_capex = capital_cost` on `annualized_financial` | design:85 |

### agentic-mbse Capabilities Assessment

**Already provides:**
- `SysideAdapter.elements_of_type()` -- iterate by type name
- `SysideAdapter.is_instance()` -- type check with mock support
- `helpers.get_parent_part_name()` -- immediate parent PartUsage name
- `binding.extract_bindings()` / `classify_binding()` -- binding extraction
- `expression.traverse_expression()` -- generic AST walk
- `expression.extract_feature_refs()` -- feature reference extraction

**Does NOT provide (Items 2-4 may need):**
- `Redefinition` type in type map
- `Specialization` type in type map
- `Multiplicity` / `MultiplicityRange` in type map
- Specialization chain traversal
- Redefinition resolution helpers
- Full hierarchy path traversal (only immediate parent)
- `InvocationExpression` handling in expression.py

## Proposed Design

### Architecture: Single Script, 10 Probe Functions

The script follows the established spike pattern: a single Python file with one function per question, structured output, and a summary report section. No production code is modified.

```
scripts/spike_hierarchy_ast.py
├── Model loading (shared with prior spikes)
├── Utility functions (safe_attr, dump_element, type_name)
├── probe_q1_template_ownership(model, adapter)
├── probe_q2_redefinition_ast(model, adapter)
├── probe_q3_part_redefines(model, adapter)
├── probe_q4_deep_path_redefinition(model, adapter)
├── probe_q5_multiplicity(model, adapter)
├── probe_q6_sum_invocation(model, adapter)
├── probe_q7_specialization_chain(model, adapter)
├── probe_q8_new_vs_redefined_attr(model, adapter)
├── probe_q9_default_value(model, adapter)
├── probe_q10_binding_to_redefined(model, adapter)
├── assess_agentic_mbse_reuse(model, adapter)
└── main() → load model, run all probes, print summary
```

### Component 1: Model Loading and Utilities

**Location:** `scripts/spike_hierarchy_ast.py` (top of file)

**Loading pattern** (reuse from prior spikes):
```python
from sysml_codegen.extraction.extractor import SysMLDataExtractor

def load_model(model_paths: list[Path]):
    extractor = SysMLDataExtractor(model_paths)
    if not extractor.load_models():
        return None, None, None
    return extractor.model, extractor.adapter, extractor
```

**Utility functions:**

```python
def safe_attr(obj, attr: str, default="<missing>"):
    """Safely access attribute, returning default if missing."""

def type_name(obj) -> str:
    """Return type(obj).__name__ for AST node identification."""

def sanitize_name(name: str | None) -> str:
    """Strip quotes, replace spaces (matches extractor._sanitize_name)."""

def find_element_by_name(model, adapter, type_name: str, name: str):
    """Find a specific element by type and name.
    Normalizes quoted names: strips ' and \", replaces spaces with _.
    Matches against both elem.name and sanitize_name(elem.name) so
    quoted SysML names ('PV Module') are found regardless of input form."""

def dump_owned_members(elem, indent=0, max_depth=2):
    """Recursively dump owned_members for AST inspection."""

def dump_owned_relationships(elem, indent=0, max_depth=2):
    """Recursively dump owned_relationships for AST inspection."""

def dump_redefinitions(elem):
    """List all owned_redefinitions on an element."""
```

These utilities enable safe probing without crashing when an expected attribute doesn't exist on a given syside element.

### Component 2: Probe Functions (Q1-Q10)

Each probe function:
1. Finds the target element(s) by name
2. Inspects specific attributes documented in the syside metamodel docs
3. Prints structured output showing what was found
4. Returns a result dict with `{question_id, status, findings, code_example}`

**Per-question output format** (satisfies NFR-2: concrete Python code snippets):

```
=== Q2: :>> Redefinition AST Representation ===

Target: 'PV Module' :>> capital_cost  (library.sysml:384)
  Element type:     AttributeUsage
  Name:             capital_cost
  owned_redefinitions: 1 found
    [0] type=Redefinition
        redefined_feature.name = 'capital_cost'
        redefined_feature.owning_type.name = "'Costed Component'"
  feature_value_expression: FeatureChainExpression
    operands: [FeatureReferenceExpression(cost_model), FeatureReferenceExpression(total_cost)]

  Code example:
    redef = elem.owned_redefinitions[0]
    redef.redefined_feature.name                # => 'capital_cost'
    redef.redefined_feature.owning_type.name    # => "'Costed Component'"
    expr = elem.feature_value_expression
    type(expr).__name__                         # => 'FeatureChainExpression'

  Status: ✓ Redefinition link found, points to abstract interface
```

Each question section follows this pattern: target identification, attribute inspection dump, a concrete `Code example:` block showing the Python access path with `# =>` annotations, and a status line.

#### Q1: Template CalcUsage Ownership

**Strategy:** Find `cost_model` CalcUsage on `PV Module` PartDef. Walk the ownership chain from the CalcUsage upward using `elem.owner` / `elem.owning_type`. Compare with `energy_production` CalcUsage on `solar_battery_plant` (PartUsage). The key differentiator should be whether the owner chain hits a `PartDefinition` or `PartUsage`.

**Attributes to probe:**
- `calc_usage.owner` -- the membership/relationship
- `calc_usage.owning_type` -- the owning Type (should be PartDef or PartUsage)
- `calc_usage.owning_namespace` -- the namespace
- Walk: `owner.owning_related_element` chain (existing pattern from `_get_parent_part_path`)
- Check `type(owning_elem).__name__` to distinguish PartDefinition vs PartUsage

**Test targets:**
- `PV Module.cost_model` → expect PartDefinition owner
- `Solar Array.allocation_model` → expect PartDefinition owner
- `solar_battery_plant.energy_production` → expect PartUsage owner

#### Q2: `:>>` Redefinition AST Representation

**Strategy:** Find `:>> capital_cost = cost_model.total_cost` on `PV Module`. Probe `owned_redefinitions` on the element. For each redefinition, inspect `redefined_feature` (should point to `Costed Component.capital_cost`) and the expression RHS via `feature_value_expression`.

**Attributes to probe on each `:>>` element:**
- `elem.owned_redefinitions` → list of `Redefinition` objects
- Each `Redefinition.redefined_feature` → the abstract attribute being redefined
- Each `Redefinition.redefined_feature.name` → e.g., "capital_cost"
- Each `Redefinition.redefined_feature.owning_type.name` → e.g., "'Costed Component'"
- `elem.feature_value_expression` → the RHS expression node
- `type(rhs).__name__` → OperatorExpression, FeatureChainExpression, etc.

**Test all 4 patterns:**
- Enum literal: `:>> cas_category = CASCategory::CAS220101`
- EXPOSE: `:>> capital_cost = cost_model.total_cost`
- Aggregation: `:>> capital_cost = sum(pv_module.capital_cost) + ...`
- FORMULA: `:>> idiot_index = capital_cost / raw_material_cost`

#### Q3: `part redefines` vs Plain `part`

**Strategy:** Find `part redefines solar_array` in design and `part solar_array` in library. Compare `owned_redefinitions` on both. The `redefines` keyword should produce an explicit `Redefinition` relationship.

**Attributes to probe:**
- `part_usage.owned_redefinitions` → should be non-empty for `redefines`
- `redefinition.redefined_feature` → should point to `Solar Battery Plant.solar_array`
- `part_usage.types` → should reference `Solar Array` PartDef in both cases
- `part_usage.owned_specializations` → check if `redefines` adds extra specializations

#### Q4: Deep-Path `:>>` Resolution

**Strategy:** Find `:>> pv_module.wattage = 400.0` in design. Probe the element's structure -- is `pv_module.wattage` encoded as a chained feature (via `owned_feature_chainings`)? Or is it a single feature with dots in its name?

**Attributes to probe:**
- `elem.name` → is it "pv_module.wattage" or just "wattage"?
- `elem.owned_feature_chainings` → `FeatureChaining` objects
- `elem.chaining_features` → iterator of chained features
- `elem.first_chaining_feature` / `elem.last_chaining_feature`
- `elem.owned_redefinitions` → is there a redefinition back to a PartDef attribute?
- `elem.feature_value_expression` → should be a `LiteralRational` with value 400.0

#### Q5: Multiplicity Representation

**Strategy:** Find `part pv_module : 'PV Module' [module_count]` on `Solar Array`. The multiplicity should appear on the PartUsage element.

**Attributes to probe:**
- `part_usage.multiplicity` → should return a `Multiplicity` or `MultiplicityRange` object
- If `MultiplicityRange`: `upper_bound`, `lower_bound`, `cached_upper_bound`, `cached_lower_bound`, `has_cached_bounds`, `bounds`
- The bounds expression: is `module_count` a `FeatureReferenceExpression` pointing to the sibling attribute?
- Follow the reference: can we resolve `module_count` → `attribute module_count : Integer default := 20` → literal 20?

#### Q6: `sum()` InvocationExpression Structure

**Strategy:** Find the `:>> capital_cost` on `Solar Array` (which has the `sum()` expression). Inspect the `feature_value_expression` tree.

**Attributes to probe:**
- `expr = elem.feature_value_expression` → root expression
- Walk the expression tree using `traverse_expression()`
- Look for nodes where `type(node).__name__` contains "Invocation"
- For invocation nodes: inspect `operands`, check for function name reference
- For `pv_module.capital_cost` operand: is it a `FeatureChainExpression`?
- How does `NumericalFunctions::sum` appear (as a type reference on the invocation)?

#### Q7: Specialization Chain Traversal

**Strategy:** Start from `solar_battery_plant` PartUsage in design. Navigate through:
1. `solar_battery_plant.types` → `Solar Battery Plant` PartDef
2. PartDef's `owned_features` → find `solar_array` PartUsage
3. `solar_array.types` → `Solar Array` PartDef
4. ... continue to `pv_module` → `PV Module` → `cost_model` → `PVModuleCostCalc`

**Attributes at each level:**
- `Feature.types` → `LazyIterator[Type]` (the typing chain)
- `Type.owned_features` → iterator of owned features
- `Type.owned_specializations` → `Specialization` list (for `:>` chains)
- `Specialization.general` → the general type

#### Q8: New Attribute vs Redefined Attribute Distinction

**Strategy:** On `Solar Array`, compare:
- `attribute misc_hardware_cost : Real = allocation_model.total_allocation;` (new attribute)
- `:>> capital_cost = sum(...) + ...;` (redefined inherited attribute)

Both live on the same PartDef. The key differentiator should be `owned_redefinitions` -- the `:>>` element will have them; the plain `attribute` will not.

**Attributes to probe:**
- `elem.owned_redefinitions` → empty for new attr, non-empty for `:>>`
- `type(elem).__name__` → check if both are `AttributeUsage`
- `elem.feature_value_expression` → both should have one (RHS expression)
- `elem.direction` → check if direction differs

#### Q9: `default :=` Representation

**Strategy:** Compare:
- `in attribute cost_per_watt : Real default := 1.07` (CalcDef param, library:39)
- `attribute module_count : Integer default := 20` (part attr, library:598)

**Attributes to probe:**
- `elem.feature_value` → the `FeatureValue` relationship
- `elem.feature_value.is_default` or similar flag
- `elem.feature_value_expression` → the default value expression
- `type(expr).__name__` → should be `LiteralRational` or `LiteralInteger`

#### Q10: Binding to Inherited/Redefined Attribute

**Strategy:** Find `in total_capex = capital_cost` on `annualized_financial` CalcUsage in design. The `capital_cost` reference points to the top-level plant's `:>> capital_cost`, which is itself a `:>>` aggregation expression.

**Attributes to probe:**
- The binding's RHS expression → is it a `FeatureReferenceExpression`?
- The referenced feature → does it point to the redefined `capital_cost` on `Solar Battery Plant`?
- Or does it resolve to `Costed Component.capital_cost` (abstract)?
- Check `referenced_feature.owning_type` to determine resolution target

### Component 3: agentic-mbse Reuse Assessment (FR-11)

**Strategy:** After probing all 10 questions, systematically review each agentic-mbse module required by the spec (FR-11) and assess reusability for Items 2-4.

**Modules to review** (per spec lines 170-177):

| Module | File | What to Check | Reuse Question |
|--------|------|---------------|----------------|
| `syside_adapter.py` | `~/agentic-mbse/src/agentic_mbse/sysml/syside_adapter.py` | Type map entries: has `PartDefinition`, `PartUsage`, `FeatureTyping`; missing `Redefinition`, `Specialization`, `Multiplicity` | Are new type map entries needed, or can we access these via element attributes directly? |
| `binding.py` | `~/agentic-mbse/src/agentic_mbse/sysml/binding.py` | `classify_binding()` handles CHAIN, REFERENCE, LITERAL, EXPRESSION; no redefinition awareness | Can `classify_binding()` handle `:>>` RHS expressions, or does it need a new BindingType? |
| `expression.py` | `~/agentic-mbse/src/agentic_mbse/sysml/expression.py` | `extract_feature_refs()`, `traverse_expression()` work; don't handle `InvocationExpression` | Does `traverse_expression()` visit `InvocationExpression` nodes? What `type(node).__name__` appears for `sum()`? |
| `helpers.py` | `~/agentic-mbse/src/agentic_mbse/sysml/helpers.py` | `get_parent_part_name()` gets immediate parent only; no full chain traversal | Is chain traversal a sysml-codegen concern, or should a `get_parent_chain()` helper live in agentic-mbse? |
| `types.py` | `~/agentic-mbse/src/agentic_mbse/sysml/types.py` | `BindingInfo`, `ExpressionRef` exist; no hierarchy/redefinition data models | Do Items 2-4 need new shared data models (e.g., `RedefinitionInfo`), or are sysml-codegen-local models sufficient? |

**Output format:**
```
=== agentic-mbse Reuse Assessment (FR-11) ===

Module: syside_adapter.py
  Type map entries present:  PartDefinition ✓, PartUsage ✓, FeatureTyping ✓
  Type map entries missing:  Redefinition, Specialization, Multiplicity, MultiplicityRange
  Assessment: [needed / not needed / TBD based on probe results]

Module: binding.py
  classify_binding() BindingTypes: UNBOUND, CHAIN, REFERENCE, LITERAL, EXPRESSION
  Redefinition awareness: None
  Assessment: [can reuse as-is / needs extension / N/A for spike]

Module: expression.py
  traverse_expression(): [visits InvocationExpression / does not visit]
  extract_feature_refs(): [handles sum() operands / does not]
  Assessment: [...]

Module: helpers.py
  get_parent_part_name(): immediate parent only
  Full chain traversal: not available
  Assessment: [...]

Module: types.py
  Existing models: BindingInfo, ExpressionRef
  Hierarchy/redefinition models: none
  Assessment: [...]

Extension Recommendations:
  - [specific recommendations based on findings]
```

### Component 4: Report Generation

The script prints structured output that can be captured to a report file. The `main()` function:

1. Loads the model suite (default: solar_battery; supports CLI override via standard multi-suite pattern)
2. Runs all 10 probe functions + reuse assessment
3. Collects results into a summary table
4. Prints metamodel type population report (NFR-3)
5. Prints a go/no-go recommendation based on findings

**Multi-suite support** (standard pattern from prior spikes):
```python
DEFAULT_SUITES: list[tuple[str, list[Path]]] = [
    ("solar_battery_model", [Path("tests/fixtures/solar_battery_model")]),
]

# CLI override: uv run python scripts/spike_hierarchy_ast.py path/to/model
if len(sys.argv) > 1:
    suites = [(arg, [Path(p) for p in arg.split(",")]) for arg in sys.argv[1:]]
else:
    suites = DEFAULT_SUITES
```

Default is solar_battery only (per spec scope), but the standard CLI pattern is preserved for reusability.

**Output structure:**
```
╔══════════════════════════════════════════════════════╗
║  SysIDE AST Discovery Spike -- solar_battery model  ║
╚══════════════════════════════════════════════════════╝

=== Q1: Template CalcUsage Ownership ===
[probe output with Code example: blocks]

=== Q2: :>> Redefinition AST Representation ===
[probe output with Code example: blocks]

...

=== Q10: Binding to Inherited/Redefined Attribute ===
[probe output]

=== agentic-mbse Reuse Assessment (FR-11) ===
[per-module assessment]

=== Metamodel Type Population (NFR-3) ===
Syside types probed on solar_battery model elements:

  Type                  | Available in API | Populated on Model Elements
  ----------------------|------------------|----------------------------
  Redefinition          | [yes/no]         | [yes: N elements / no]
  Specialization        | [yes/no]         | [yes: N elements / no]
  Multiplicity          | [yes/no]         | [yes: N elements / no]
  MultiplicityRange     | [yes/no]         | [yes: N elements / no]
  InvocationExpression  | [yes/no]         | [yes: N elements / no]
  FeatureChainExpression| [yes/no]         | [yes: N elements / no]
  FeatureValue          | [yes/no]         | [yes: N elements / no]

  Note: "Available in API" = attribute accessible on element without error.
  "Populated" = attribute returned non-empty/non-None value on at least one
  solar_battery model element during probing.

=== Summary ===
Q1: ✓ / ✗ / ⚠  [one-line finding]
Q2: ✓ / ✗ / ⚠  [one-line finding]
...
Q10: ✓ / ✗ / ⚠  [one-line finding]

=== Go/No-Go Recommendation ===
[analysis]
```

After running the script, the output will be captured and formatted into `.project/active/hierarchy-spike/report.md` manually.

## Potential Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Syside attributes use camelCase instead of snake_case | Low | Low | The docs say snake_case; probe both forms if one fails |
| `owned_redefinitions` is empty on `:>>` elements | Medium | High | This is the core question -- if empty, try `owned_relationships` and filter by type |
| `MultiplicityRange.cached_lower_bound` not populated | Medium | Medium | Fall back to evaluating `upper_bound` expression manually |
| `InvocationExpression` not exposed by syside | Medium | High | Check `type(node).__name__` for any invocation-like nodes in the expression tree |
| Quoted names (`'PV Module'`) break name matching | Low | Low | Match using both quoted and unquoted forms |
| Model loading fails (syside not installed) | Low | High | Script uses same load path as codegen tests; if tests pass, spike will load |

## Integration Strategy

This is a standalone probe script with no production code integration. The output feeds into:
1. **Spike report** (`.project/active/hierarchy-spike/report.md`) -- formatted findings
2. **Items 2-4 specs/designs** -- concrete attribute names used in implementation

## Validation Approach

1. Run `uv run python scripts/spike_hierarchy_ast.py` and verify it loads the model
2. Verify each Q section produces output (no crashes / empty sections)
3. Manually verify a few attribute paths against the syside metamodel docs
4. Run `uv run pytest tests/` to confirm no production code was touched

---

Next Step: After approval → implement the probe script, run it, and capture the report.
