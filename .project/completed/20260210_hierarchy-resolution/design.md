# Design: Redefinition Resolution, Multiplicity, & Aggregation Expressions

**Status:** Draft
**Owner:** Reid Westwood
**Created:** 2026-02-10 14:18 UTC
**Branch:** cost-pattern
**Commit:** 93f0a55
**Epic:** COST-PATTERN Item 3

## Overview

Extract `:>>` redefinition data, multiplicity, and `sum()`-based aggregation expressions from PartDefs and design PartUsages, producing standalone data structures that Item 4 consumes for pipeline integration. This is a pure extraction-layer addition — no pipeline, backtracker, or generation changes.

## Related Artifacts

- **Spec:** `.project/active/hierarchy-resolution/spec.md`
- **Item 2 design:** `.project/active/template-detection/design.md`
- **Spike report:** `.project/active/hierarchy-spike/report.md`
- **Epic:** `.project/backlog/epic_costed_component_pattern.md` (Item 3)

---

## Research Findings

### 1. Expression Compiler Architecture (expression_compiler.py)

The Phase 1 expression compiler converts syside AST → `ExpressionAST` IR → Python string. The key function is `build_expression_ast()` (line 290) which dispatches on syside node type:

- `OperatorExpression` → binary/unary tree (line 313)
- `FeatureReferenceExpression` → input_ref or intermediate_ref (line 371)
- `LiteralRational/Integer/Real` → literal (line 385)
- `FeatureChainExpression` → **UNSUPPORTED** (line 395)
- Everything else → **UNSUPPORTED** (line 402) — this is where `InvocationExpression` falls through

The compiler's contract is CalcDef-scoped: `input_names` and `output_names` are CalcDef attributes. It has no concept of PartDef attributes, child PartUsages, or cross-hierarchy references. Aggregation expressions (`:>> capital_cost = sum(pv_module.capital_cost) + ...`) operate in an entirely different context — PartDef-scoped, referencing child parts and sibling attributes.

### 2. Computed Attribute Extractor (computed_attribute_extractor.py)

`extract_computed_attributes()` (line 110) iterates `owned_members` of a PartDef/PartUsage, looking for `AttributeUsage` with `feature_value_expression`. It classifies as FORMULA, EXPOSE_PURE, EXPOSE_COMPUTED, LITERAL, or UNRESOLVABLE.

**Critical gap:** This only scans `AttributeUsage` (line 140: `if not SysideAdapter.is_instance(member, "AttributeUsage"): continue`). But `:>>` creates `ReferenceUsage` (spike Q2, Q8). All `:>>` elements are completely invisible to this extractor.

### 3. Usage Extractor — Item 2 State (usage_extractor.py)

Item 2 added:
- Template detection via `owning_type` check (line 436-444)
- `_build_part_usage_index()` (line 140): maps PartDef QN → list of PartUsage elements
- `_find_instantiation_paths()` (line 169): recursive path resolution
- `_expand_template_calc_usages()` (line 267): replaces templates with virtual instances

The part usage index and instantiation path infrastructure is **directly reusable** for Item 3. Multiplicity detection needs access to the PartUsage AST elements already stored in the index. Redefinition scanning needs to iterate `owned_members` of the same PartDef and design PartUsage elements.

### 4. Expression Reconstruction (expression_utils.py)

`reconstruct_expression()` (line 34) handles `OperatorExpression`, `FeatureReferenceExpression`, `FeatureChainExpression`, and literals. It does NOT handle `InvocationExpression` — it falls through to `str(expr_node)` at line 68. We need to extend this for `sum()` text reconstruction.

### 5. `_extract_single_binding()` Patterns (usage_extractor.py:499-567)

The existing binding extraction classifies RHS expressions by type: `FeatureChainExpression` → CHAIN, `FeatureReferenceExpression` → REFERENCE, literal → LITERAL, `OperatorExpression` → EXPRESSION. This pattern maps directly to the three `:>>` redefinition patterns (LITERAL, CHAIN, EXPRESSION) described in the spec.

The existing `_is_literal_expression()` (line 659) and `_extract_literal_value()` (line 669) are candidates for reuse, but have a gap: `_is_literal_expression()` checks `LiteralInteger`, `LiteralRational`, `LiteralBoolean`, and `LiteralString` — but **NOT `LiteralReal`**. The expression compiler's `build_expression_ast()` (line 385) handles `LiteralReal` alongside `LiteralRational` and `LiteralInteger`. A `:>>` literal redefinition using a `LiteralReal` RHS would be misclassified as EXPRESSION instead of LITERAL. This must be fixed.

### 6. Data Model Patterns (data_models.py + usage_extractor.py)

`ComputedAttributeData` (data_models.py:173) provides the precedent for a PartDef-scoped extraction result: `owning_part_name`, `owning_part_qualified_name`, `expression_ast`, `compiled_expression`, `compilability`. The new `AggregationExpressionData` follows this pattern.

`CalcUsageData` already has `is_template`, `owning_part_def_qn`, `raw_element` (Item 2 fields). No modifications to `CalcUsageData` needed for Item 3.

### 7. Pipeline Step Numbering (initialization.py)

Current steps: 1 (load), 2 (calc defs), 3 (calc usages + template expansion), 4 (design attrs), 4.5 (computed attrs), 5 (param groups), 6 (backtracker), 6.5 (expression compilation), 7 (graph builder).

Item 4 will add Steps 3.5 (redefinition application) and 4.7 (aggregation extraction). Item 3 produces the data structures these steps will consume, but does NOT modify the pipeline itself.

### 8. How Item 4 Will Consume Item 3 Data

Understanding the downstream consumer shapes the data model design:

**For `:>>` literal redefinitions**: Item 4's Step 3.5 will iterate virtual CalcUsages, look up matching `:>>` overrides by path, and either mutate bindings on the virtual CalcUsageData to LITERAL with the resolved value, or add new resolved bindings. The key lookup path is: design PartUsage QN → deep-path target → resolved value.

**For aggregation expressions**: Item 4's Step 4.7 will convert each `AggregationExpressionData` into a synthetic `PipelineModule` via the graph builder, similar to how computed attributes become synthetic modules in Step 7. The data model must provide: the compiled Python expression, input channel names, and multiplicity entry points.

**For multiplicity**: Item 4 needs to look up "what is the multiplicity count attribute for PartUsage X?" when resolving `sum()` terms. The lookup key is the PartUsage name within its owning PartDef.

---

## Design Alternatives

### Decision 1: Data Structure vs In-Place Mutation

**Context**: Should Item 3 produce standalone data structures that Item 4 reads, or directly mutate virtual CalcUsage bindings?

**Option A: Standalone Data Structures (Recommended)**

Produce `RedefinitionData` and `AggregationExpressionData` as new dataclasses. Item 4 reads these and applies them to the pipeline at Steps 3.5/4.7.

- *Pros*: Clean boundary — Item 3 is pure extraction, Item 4 is pipeline integration. Testable independently. No coupling between extraction output and mutable pipeline state. Data can be inspected/logged before application.
- *Cons*: Item 4 needs matching logic to apply data to virtual CalcUsages.

**Option B: In-Place Mutation**

Item 3 modifies virtual CalcUsage bindings directly — e.g., when `:>> pv_module.wattage = 400.0` is found, immediately update the virtual CalcUsage's wattage binding to LITERAL with value 400.0.

- *Pros*: No intermediate data structure. Simpler pipeline — virtual CalcUsages arrive pre-resolved.
- *Cons*: Tight coupling between extraction and virtual CalcUsage lifecycle. Template expansion (Item 2) must complete before redefinition resolution (Item 3). Harder to test: must construct full virtual CalcUsages to test redefinition extraction. Mutation side effects harder to debug.

**Recommendation: Option A.** The codebase pattern is data-out: `CalcUsageData`, `ComputedAttributeData`, `BacktrackingResult` are all immutable data structures flowing through the pipeline. Item 3's output should follow the same pattern. Item 4 applies the data at well-defined pipeline steps.

### Decision 2: New Module vs Extending Existing

**Context**: Where does the new `:>>` extraction code live?

**Option A: New `hierarchy_resolver.py` (Recommended)**

Create `src/sysml_codegen/extraction/hierarchy_resolver.py` with:
- `:>>` redefinition scanning
- Multiplicity detection
- `sum()` transformation
- `AggregationExpressionData` construction

- *Pros*: Clean separation of concerns. `usage_extractor.py` stays focused on CalcUsage extraction. `computed_attribute_extractor.py` stays focused on `AttributeUsage` computed attrs. New module handles `ReferenceUsage` redefinition patterns — a fundamentally different AST element type.
- *Cons*: New file. Needs to import from `expression_utils.py` and `data_models.py`.

**Option B: Extend `computed_attribute_extractor.py`**

Add `:>>` handling alongside existing `AttributeUsage` extraction.

- *Pros*: Both handle PartDef member expressions.
- *Cons*: Mixes two fundamentally different AST element types (`AttributeUsage` vs `ReferenceUsage`). The classification logic is completely different — computed attrs use qualified-name analysis of `ExpressionRef`, while redefinitions use `owned_redefinitions` and `chaining_features`. Would make the file complex and violate SRP.

**Option C: Extend `usage_extractor.py`**

Add `:>>` handling alongside template detection.

- *Pros*: Reuses `_build_part_usage_index()` directly.
- *Cons*: `usage_extractor.py` is already 674 lines with CalcUsage extraction + template detection. Adding redefinition/multiplicity/aggregation would push it to ~1000+ lines. Conceptually different: CalcUsage extraction vs PartDef redefinition analysis.

**Recommendation: Option A.** The new module can import `_build_part_usage_index` from `usage_extractor.py` (or accept the index as a parameter). Clean SRP: `hierarchy_resolver.py` handles the `:>>` redefinition pattern that is invisible to both `computed_attribute_extractor.py` (wrong element type) and `usage_extractor.py` (wrong abstraction level).

### Decision 3: Expression Compiler Extension Strategy

**Context**: Should `build_expression_ast()` be extended with `InvocationExpression` handling, or should `sum()` transformation happen entirely at the extraction layer?

**Option A: Extraction-Layer Only (Recommended)**

Item 3 walks the expression AST directly (using syside attributes like `.function.name` and `.operands`), detects `sum()` patterns, and transforms them to parametric multiply. The Phase 1 expression compiler is NOT modified.

- *Pros*: No risk of breaking the Phase 1 CalcDef compilation contract. `sum()` handling is specific to aggregation expressions in PartDefs — it has no meaning in CalcDef outputs. The expression compiler stays a leaf module with a narrow, well-tested contract.
- *Cons*: Some duplication of AST traversal (but minimal — just the `InvocationExpression` detection).

**Option B: Extend Expression Compiler**

Add an `InvocationExpression` handler to `build_expression_ast()` that produces a new `FUNCTION_CALL` IR node type.

- *Pros*: Centralized expression handling.
- *Cons*: The compiler's contract assumes CalcDef context (input/output names are CalcDef attributes). `sum()` operates in a PartDef context with child PartUsages and multiplicity — fundamentally different. Adding a FUNCTION_CALL node that can't compile (`sum(collection)` has no Python equivalent without the parametric multiply transformation) adds complexity for no gain. The compiler's UNSUPPORTED path already handles this correctly for CalcDefs.

**Recommendation: Option A.** The expression compiler's contract is CalcDef-scoped. Aggregation expressions are PartDef-scoped with entirely different semantics. Handle `sum()` at the extraction layer where the PartDef context (child PartUsages, multiplicity) is available.

### Decision 4: Aggregation Extraction Scope

**Context**: Extract from all PartDefs or only instantiated ones?

**Option A: All PartDefs (Recommended)**

Extract `:>>` EXPRESSION redefinitions from every PartDef that has them. Item 4 can filter to only those with PartUsage instantiations.

- *Pros*: Complete data. Item 4 can decide what to use. Useful for diagnostics/logging.
- *Cons*: Extracts data for PartDefs that may have no instantiations (minor overhead).

**Option B: Only Instantiated PartDefs**

Filter against `_build_part_usage_index()` and only extract for PartDefs that have at least one PartUsage.

- *Pros*: No wasted work.
- *Cons*: Requires the part usage index at extraction time. Tight coupling between "what to extract" and "what's instantiated" — a pipeline concern.

**Recommendation: Option A.** Extract everything, let the pipeline filter. This mirrors how `extract_computed_attributes()` extracts from all PartDefs/PartUsages and the pipeline decides what to use.

---

## Proposed Design

### Component 1: Data Models

**File:** `src/sysml_codegen/extraction/data_models.py`

Add three new dataclasses:

```python
class RedefinitionType(str, Enum):
    """Classification of a :>> redefinition's RHS expression."""
    LITERAL = "literal"       # :>> wattage = 400.0
    CHAIN = "chain"           # :>> capital_cost = cost_model.total_cost
    EXPRESSION = "expression" # :>> capital_cost = sum(pv_module.capital_cost) + ...
```

```python
@dataclass
class RedefinitionData:
    """Extracted data for a single :>> redefinition on a PartDef or design PartUsage.

    Represents the resolution of one ReferenceUsage with owned_redefinitions.
    """
    owning_part_qn: str        # QN of the PartDef/PartUsage this :>> lives on
    attribute_name: str         # The redefined attribute (e.g., "capital_cost")
    redefinition_type: RedefinitionType
    # For LITERAL:
    literal_value: float | int | str | bool | None = None
    # For CHAIN:
    source_path: str | None = None  # e.g., "cost_model.total_cost"
    # For EXPRESSION:
    expression_ast: Any = None      # Raw syside AST for downstream transformation
    expression_text: str = ""       # Display text from reconstruct_expression()
    # Deep-path info (for design-level overrides):
    target_path: list[str] = field(default_factory=list)
    # e.g., ["pv_module", "wattage"] for :>> pv_module.wattage = 400.0
    # Empty for same-level redefinitions
    is_deep_path: bool = False
    source_file: Path = field(default_factory=lambda: Path("unknown"))
    source_line: int = 0
```

```python
@dataclass
class MultiplicityData:
    """Multiplicity information for a PartUsage within a PartDef.

    count is defensively cast to int() at extraction time because
    cached_lower_bound may return a float or other numeric type from syside.
    """
    part_usage_name: str       # e.g., "pv_module"
    owning_part_def_qn: str    # QN of the owning PartDef (e.g., "Lib__Solar_Array")
    count: int | None          # Resolved literal count (e.g., 20), or None if unresolvable
    count_attribute_name: str | None  # Name of the multiplicity attribute (e.g., "module_count")
    default_value: int | None  # Default value of the count attribute
```

```python
@dataclass
class SumTerm:
    """One sum() operand in an aggregation expression."""
    part_usage_name: str       # e.g., "pv_module"
    attribute_name: str        # e.g., "capital_cost"
    multiplicity_attr: str | None  # e.g., "module_count" (None if singleton)
    multiplicity_count: int | None  # e.g., 20

@dataclass
class SingletonTerm:
    """A non-sum child attribute reference in an aggregation expression."""
    source_path: str           # e.g., "allocation_model.total_allocation"

@dataclass
class LocalTerm:
    """A PartDef-local attribute reference in an aggregation expression."""
    attribute_name: str        # e.g., "misc_hardware_cost"

@dataclass
class AggregationExpressionData:
    """Extracted and transformed aggregation expression from a PartDef :>> attribute.

    Produced by hierarchy_resolver after scanning :>> EXPRESSION redefinitions
    that contain sum() calls. The expression has been decomposed into typed terms
    and the sum() calls transformed to parametric multiply.

    compilability is set to UNKNOWN at extraction time because the transformed
    expression still contains symbolic channel references (e.g., "pv_module.capital_cost")
    that Item 4 must resolve to actual pipeline channels. Item 4 promotes to
    FULLY_COMPILABLE after channel resolution succeeds, or MANUAL_REQUIRED if
    resolution fails.

    has_unsupported_nodes signals whether the AST walk encountered any node types
    it could not process. If True, Item 4 should expect MANUAL_REQUIRED after
    channel resolution.
    """
    owning_part_qn: str            # Assembly PartDef QN (e.g., "Lib__Solar_Array")
    owning_part_name: str          # Short name (e.g., "Solar_Array")
    attribute_name: str            # Redefined attribute (e.g., "capital_cost")
    raw_expression_text: str       # Before transformation
    transformed_expression: str    # After parametric multiply (symbolic channel refs)
    sum_terms: list[SumTerm]
    singleton_terms: list[SingletonTerm]
    local_terms: list[LocalTerm]
    input_channels: list[str]      # All upstream channel references (for Item 4 wiring)
    entry_points: list[str]        # Multiplicity count attrs → pipeline entry points
    compilability: Compilability = Compilability.UNKNOWN  # Item 4 promotes after channel resolution
    has_unsupported_nodes: bool = False  # True if AST walk hit unrecognized node types
    source_file: Path = field(default_factory=lambda: Path("unknown"))
    source_line: int = 0
```

**Rationale for term decomposition:** Item 4's graph builder needs to know what each operand in the aggregation expression maps to in the pipeline: sum terms become `count * child_module_output`, singleton terms become direct `child_module_output`, local terms become `entry_point` or `design_attribute`. Decomposing at extraction time (Item 3) means Item 4 has structured data to work with instead of parsing expression strings.

### Component 2: Redefinition Scanner

**File:** `src/sysml_codegen/extraction/hierarchy_resolver.py`
**Function:** `extract_redefinitions(part_element: Any) -> list[RedefinitionData]`

Scans `owned_members` of a PartDef or PartUsage for `ReferenceUsage` elements with non-empty `owned_redefinitions`. Classifies each by RHS expression type.

**Logic:**

```
for member in part_element.owned_members:
    if not is_instance(member, "ReferenceUsage"):
        continue
    if not member.owned_redefinitions:
        continue

    # Get redefined attribute name
    redef = member.owned_redefinitions[0]
    redefined_feature = redef.redefined_feature

    # Check for deep-path (chaining_features)
    chaining = list(redefined_feature.chaining_features)  # spike Q4
    if chaining:
        target_path = [sanitize_name(c.name) for c in chaining]
        attr_name = target_path[-1]
        is_deep_path = True
    else:
        attr_name = sanitize_name(redefined_feature.name) or sanitize_name(member.name)
        target_path = []
        is_deep_path = False

    # Skip if no value expression (type-only redefinition)
    expr = getattr(member, "feature_value_expression", None)
    if expr is None:
        continue

    # Classify RHS — delegates to _extract_single_redefinition() shared helper
    if is_literal_expression(expr):
        → RedefinitionType.LITERAL, extract value
    elif is_instance(expr, "FeatureChainExpression") or is_instance(expr, "FeatureReferenceExpression"):
        → RedefinitionType.CHAIN, extract source path
    else:
        → RedefinitionType.EXPRESSION, capture AST + text
```

**Shared helper:** The per-member extraction logic (from `member.owned_redefinitions` through RHS classification to `RedefinitionData` construction) is identical between Component 2 and Component 3. Extract as `_extract_single_redefinition(member: Any, owning_qn: str) -> RedefinitionData | None`. Components 2 and 3 differ only in their outer loops (PartDef members vs design PartUsage members).

**Reuse:** `is_literal_expression()` and `extract_literal_value()` from `expression_utils.py` (canonical shared versions, also used by `usage_extractor.py`). `reconstruct_expression()` from `expression_utils.py` for text representation.

### Component 3: Deep-Path Resolver

**File:** `src/sysml_codegen/extraction/hierarchy_resolver.py`
**Function:** `extract_design_overrides(model: Any) -> list[RedefinitionData]`

Scans design-level PartUsages (those with `part redefines` — non-empty `owned_redefinitions` on the PartUsage itself) for their `:>>` deep-path overrides.

**Logic:**

```
for usage in SysideAdapter.elements_of_type(model, "PartUsage"):
    if not usage.owned_redefinitions:
        continue  # Not a 'part redefines'

    usage_qn = build_element_qualified_name(usage)

    for member in usage.owned_members:
        if not is_instance(member, "ReferenceUsage"):
            continue
        if not member.owned_redefinitions:
            continue

        redef = member.owned_redefinitions[0]
        chaining = list(redef.redefined_feature.chaining_features)

        if chaining:
            # Deep-path override: :>> pv_module.wattage = 400.0
            target_path = [sanitize_name(c.name) for c in chaining]
            attr_name = target_path[-1]
        else:
            # Same-level override on the part redefines
            attr_name = sanitize_name(redef.redefined_feature.name)
            target_path = []

        expr = getattr(member, "feature_value_expression", None)
        if expr is None:
            continue

        # Classify and emit RedefinitionData with
        # owning_part_qn = usage_qn
        # is_deep_path = bool(chaining)
        # target_path = e.g., ["pv_module", "wattage"]
```

**Key insight from spike Q4:** `member.name` is `None` for deep-path overrides. The path is on `owned_redefinitions[0].redefined_feature.chaining_features`, which returns `[PartUsage 'pv_module', AttributeUsage 'wattage']`. Each component has a `.name`.

### Component 4: Multiplicity Extractor

**File:** `src/sysml_codegen/extraction/hierarchy_resolver.py`
**Function:** `extract_multiplicities(part_element: Any) -> list[MultiplicityData]`

Scans child PartUsages of a PartDef for multiplicity.

**Logic:**

```
for member in part_element.owned_members:
    if not is_instance(member, "PartUsage"):
        continue

    mult = getattr(member, "multiplicity", None)
    if mult is None:
        continue  # Singleton

    # Use cached_lower_bound (correct for [N] syntax) — spike Q5
    count = getattr(mult, "cached_lower_bound", None)

    # Extract attribute name from upper_bound expression chain
    count_attr_name = None
    default_value = None
    upper = getattr(mult, "upper_bound", None)
    if upper and hasattr(upper, "referent"):
        referent = upper.referent
        count_attr_name = getattr(referent, "name", None)
        fve = getattr(referent, "feature_value_expression", None)
        if fve and hasattr(fve, "value"):
            default_value = fve.value

    → MultiplicityData(
        part_usage_name=sanitize_name(member.name),
        owning_part_def_qn=build_element_qualified_name(part_element),
        count=count,
        count_attribute_name=count_attr_name,
        default_value=default_value,
    )
```

**Why `cached_lower_bound`:** Spike Q5 confirmed systematic N+1 behavior on `cached_upper_bound` across all 3 model multiplicities (20→21, 4→5, 8→9). `cached_lower_bound` returns the correct value for `[N]` syntax.

### Component 5: Aggregation Expression Transformer

**File:** `src/sysml_codegen/extraction/hierarchy_resolver.py`
**Function:** `build_aggregation_expression(redef: RedefinitionData, multiplicities: list[MultiplicityData], part_element: Any) -> AggregationExpressionData | None`

The function builds a local lookup dict from the list (keyed by `part_usage_name`) for `sum()` term resolution.

Takes an EXPRESSION-type `:>>` redefinition from an assembly PartDef and:
1. Walks the expression AST
2. Detects `InvocationExpression` nodes with `function.name == 'sum'`
3. Decomposes into `SumTerm`, `SingletonTerm`, `LocalTerm`
4. Transforms `sum()` to parametric multiply
5. Builds the transformed Python expression string

**AST Walk Logic:**

The expression AST for `Solar Array.:>> capital_cost` is (from spike Q6):
```
OperatorExpression(+)
├── OperatorExpression(+)
│   ├── OperatorExpression(+)
│   │   ├── InvocationExpression(sum)  ← pv_module.capital_cost
│   │   └── InvocationExpression(sum)  ← inverter.capital_cost
│   └── FeatureChainExpression         ← allocation_model.total_allocation
└── FeatureReferenceExpression         ← misc_hardware_cost
```

Walk recursively:
- `OperatorExpression`: recurse into operands, collect operator
- `InvocationExpression` with `function.name == 'sum'`:
  - Extract single operand (`FeatureChainExpression`)
  - Decompose to `part_name.attr_name` (e.g., `pv_module.capital_cost`)
  - Look up `multiplicities[part_name]` → get `count_attribute_name` and `count`
  - Emit `SumTerm(part_usage_name="pv_module", attribute_name="capital_cost", multiplicity_attr="module_count", multiplicity_count=20)`
  - Transform text: `module_count * pv_module.capital_cost`
- `FeatureChainExpression`: e.g., `allocation_model.total_allocation`
  - Check if `allocation_model` is a child PartUsage (singleton) → `SingletonTerm`
  - Transform text: `allocation_model.total_allocation` (direct reference)
- `FeatureReferenceExpression`: e.g., `misc_hardware_cost`
  - Check if it's a sibling attribute on the owning PartDef → `LocalTerm`
  - Transform text: `misc_hardware_cost` (local entry point or design attribute)
- Literals: pass through as-is

**Transformed expression text for `Solar Array.capital_cost`:**
```python
"(((module_count * pv_module.capital_cost) + (inverter_count * inverter.capital_cost)) + allocation_model.total_allocation) + misc_hardware_cost"
```

**`input_channels`** collects all non-local references:
- `pv_module.capital_cost` (needs `:>>` chain resolution to get actual MODULE_OUTPUT — deferred to Item 4)
- `inverter.capital_cost` (same)
- `allocation_model.total_allocation` (singleton child CalcUsage output — Item 4 resolves)

**`entry_points`** collects multiplicity attributes: `["module_count", "inverter_count"]`

**`compilability`**: Set to `Compilability.UNKNOWN` at extraction time (the transformed expression still contains symbolic channel references). Set `has_unsupported_nodes = True` if the walker encounters any unrecognized node types. Item 4 promotes to `FULLY_COMPILABLE` after channel resolution succeeds, or `MANUAL_REQUIRED` if resolution fails or `has_unsupported_nodes` is set.

### Component 6: Top-Level Extraction Orchestrator

**File:** `src/sysml_codegen/extraction/hierarchy_resolver.py`
**Function:** `extract_hierarchy_data(model: Any) -> HierarchyExtractionResult`

```python
@dataclass
class HierarchyExtractionResult:
    """Complete extraction result for hierarchy patterns."""
    redefinitions: list[RedefinitionData]
    design_overrides: list[RedefinitionData]
    multiplicities: list[MultiplicityData]
    aggregation_expressions: list[AggregationExpressionData]
    warnings: list[str]
```

Item 4 can build its own lookup index (e.g., by `part_usage_name` or composite key) from the list based on its wiring needs. Keeping this as a list avoids an implicit key-format contract between Item 3 and Item 4.

**Logic:**

```
1. Iterate all PartDefinition elements
   a. For each: extract_redefinitions() → LITERAL, CHAIN, EXPRESSION classified
   b. For each: extract_multiplicities() → MultiplicityData per child PartUsage
   c. For EXPRESSION redefinitions: build_aggregation_expression() using multiplicities

2. extract_design_overrides(model) → deep-path overrides from design PartUsages

3. Return HierarchyExtractionResult with all data
```

### Component 7: Expression Utils Extension

**File:** `src/sysml_codegen/extraction/expression_utils.py`

Add `InvocationExpression` handling to `reconstruct_expression()`:

```python
# After the OperatorExpression check (line 44), before FeatureReference (line 47):
if hasattr(expr_node, "function") and hasattr(expr_node.function, "name"):
    # InvocationExpression (e.g., sum())
    func_name = expr_node.function.name
    operands = list(getattr(expr_node, "operands", []))
    args = ", ".join(reconstruct_expression(op) for op in operands)
    return f"{func_name}({args})"
```

This ensures `reconstruct_expression()` produces readable text for `:>>` expressions containing `sum()`.

### Component 8: Shared Utilities (Completed Pre-Item 3)

**Refactoring (done):** `_is_literal_expression()` and `_extract_literal_value()` were private functions in `usage_extractor.py` that missed `LiteralReal` (the expression compiler handles it at `expression_compiler.py:385`, but the literal detector did not). This was a latent bug: a `:>>` literal redefinition producing a `LiteralReal` AST node would be misclassified as EXPRESSION.

**Resolution:** Canonical `is_literal_expression()` and `extract_literal_value()` now live as public functions in `expression_utils.py` with all five literal types (`LiteralInteger`, `LiteralRational`, `LiteralReal`, `LiteralBoolean`, `LiteralString`). `usage_extractor.py` imports them under private aliases for backward compatibility with existing test patch targets. The hierarchy resolver imports them directly from `expression_utils.py`.

---

## Potential Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| `chaining_features` returns empty iterator on some `:>>` patterns | Low | High | Spike Q4 validated on all 5 deep-path overrides. Use `list()` wrapper to handle empty gracefully. |
| `multiplicity` attribute not populated on some PartUsages | Low | Medium | Spike Q5 validated on all 3 arrayed PartUsages. Use `getattr` with None default. |
| `function.name` not available on `InvocationExpression` | Low | High | Spike Q6 validated `.function.name == 'sum'`. Defensive: check `hasattr`. |
| Expression AST structure varies for different aggregation patterns | Medium | Medium | Solar_battery model has one canonical pattern. Log unrecognized node types as warnings rather than failing. |
| Mixed operand types in aggregation expression not all handled | Low | Medium | Solar_battery has all 4 types (sum, singleton, local, literal). Walk function dispatches on each type with fallback to UNSUPPORTED. |
| `_build_part_usage_index` from Item 2 not yet merged | Medium | High | Item 2 and Item 3 are on the same branch (`cost-pattern`). If Item 2 is incomplete, Item 3 can be developed against the committed Item 2 code. |

---

## Integration Strategy

### What Changes
- **New:** `src/sysml_codegen/extraction/hierarchy_resolver.py` — redefinition scanning, multiplicity extraction, aggregation transformation
- **Modified:** `src/sysml_codegen/extraction/data_models.py` — add `RedefinitionType`, `RedefinitionData`, `MultiplicityData`, `SumTerm`, `SingletonTerm`, `LocalTerm`, `AggregationExpressionData`, `HierarchyExtractionResult` to file and `__all__`
- **Modified:** `src/sysml_codegen/extraction/expression_utils.py` — `InvocationExpression` handling in `reconstruct_expression()` (Component 7). Note: `is_literal_expression()` and `extract_literal_value()` already added pre-Item 3 (Component 8).
- **New:** `tests/unit/test_hierarchy_resolver.py`

### What Does NOT Change
- `usage_extractor.py` — Item 3 produces standalone data, does not modify CalcUsageData. (Note: the literal utility refactoring in Component 8 was a preparatory change already committed; Item 3 implementation does not further modify this file.)
- `computed_attribute_extractor.py` — remains `AttributeUsage`-only
- `expression_compiler.py` — remains CalcDef-scoped
- `initialization.py` — no pipeline changes until Item 4
- `dependency_backtracker.py` — no changes until Item 4
- `graph_builder.py` — no changes until Item 4

### Upstream Dependencies
- `agentic_mbse.sysml.syside_adapter.SysideAdapter` — for `is_instance()` and `elements_of_type()`
- `expression_utils.py` — for `reconstruct_expression()`, `extract_feature_chain_name()`, `is_literal_expression()`, `extract_literal_value()`

### Item 4 Interface
Item 4 will consume `HierarchyExtractionResult` by:
1. Adding it to `PipelineContext` as a new field
2. Calling `extract_hierarchy_data(model)` at a new pipeline step
3. Using `redefinitions` and `design_overrides` to resolve virtual CalcUsage bindings
4. Using `aggregation_expressions` to generate synthetic pipeline modules
5. Using `multiplicities` for entry point generation (multiplicity counts)

---

## Validation Approach

### Unit Tests (`tests/unit/test_hierarchy_resolver.py`)

Tests use mock AST elements following the pattern from `test_template_detection.py`.

**Test Suite 1: Redefinition Scanning**
- `test_literal_redefinition`: `:>> wattage = 400.0` → LITERAL with value 400.0
- `test_chain_redefinition`: `:>> capital_cost = cost_model.total_cost` → CHAIN with path
- `test_expression_redefinition`: `:>> capital_cost = sum(...) + ...` → EXPRESSION with AST
- `test_skip_no_value_expression`: `:>>` with no RHS → skipped
- `test_skip_attribute_usage`: `AttributeUsage` members → not processed (only ReferenceUsage)
- `test_multiple_redefs_per_part`: 3 `:>>` on one PartDef → 3 RedefinitionData

**Test Suite 2: Deep-Path Resolution**
- `test_deep_path_extracts_chaining_features`: `[PartUsage 'pv_module', AttributeUsage 'wattage']` → target_path `["pv_module", "wattage"]`
- `test_deep_path_literal_value`: `:>> pv_module.wattage = 400.0` → LITERAL with value and path
- `test_deep_path_is_deep_path_flag`: `is_deep_path=True` when chaining_features non-empty
- `test_same_level_redef_not_deep_path`: Named `:>>` → `is_deep_path=False`
- `test_design_overrides_collected`: 5 deep-path overrides on mock design solar_array → 5 RedefinitionData

**Test Suite 3: Multiplicity**
- `test_multiplicity_with_attribute_ref`: `[module_count]` default 20 → count=20, attr="module_count"
- `test_singleton_no_multiplicity`: No `.multiplicity` → None (not in results)
- `test_multiplicity_uses_cached_lower_bound`: Verify `cached_lower_bound` used, NOT `cached_upper_bound`
- `test_multiplicity_extracts_default_value`: `module_count default := 20` → default_value=20

**Test Suite 4: Sum Transformation**
- `test_sum_detected`: `InvocationExpression` with `function.name='sum'` → SumTerm
- `test_sum_parametric_multiply`: `sum(pv_module.capital_cost)` → `module_count * pv_module.capital_cost`
- `test_singleton_term`: `FeatureChainExpression` non-sum → SingletonTerm
- `test_local_term`: `FeatureReferenceExpression` sibling attr → LocalTerm
- `test_mixed_expression`: Full solar_array.capital_cost → 2 SumTerms + 1 SingletonTerm + 1 LocalTerm

**Test Suite 5: AggregationExpressionData**
- `test_aggregation_has_correct_terms`: Verify term counts
- `test_aggregation_input_channels`: All child references collected
- `test_aggregation_entry_points`: Multiplicity attrs collected
- `test_aggregation_transformed_expression`: Python expression string correct

**Test Suite 6: Integration**
- `test_extract_hierarchy_data_solar_battery_mock`: Full mock hierarchy → all data structures populated

### Quality Checks
- `uv run mypy src/sysml_codegen/extraction/hierarchy_resolver.py`
- `uv run ruff check src/sysml_codegen/extraction/hierarchy_resolver.py`
- `uv run pytest tests/` — all 313+ existing tests pass

---

Next Step: After approval → `/_my_plan`
