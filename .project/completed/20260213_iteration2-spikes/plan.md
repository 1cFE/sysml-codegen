# Plan: Iteration 2 OutputRegistry Design Spikes

**Status:** Complete
**Spec:** `.project/active/iteration2-spikes/spec.md`
**Created:** 2026-02-13T18:39:20+00:00

---

## Implementation Strategy

Three independent diagnostic scripts plus a summary document. Unlike iteration 1
spikes which were pure extraction-level probes, Spike 5 requires running the full
pipeline (`build_pipeline_context()`) to access `BacktrackingResult`. Spikes 6 and 7
are extraction-level like iteration 1.

### Execution Order

All three spikes are independent. Write all three, run all three, write findings.

```
Spike 5 (REFERENCE resolution outcomes)  ─┐
Spike 6 (CHAIN redef RHS format)          │── independent, run in any order
Spike 7 (design attr default_value)      ─┘
                                           │
                                           v
                                Summary findings doc
```

**Risk note:** Spike 5 calls `build_pipeline_context()` which runs the FULL pipeline
including the backtracker. This may hit Bug 2 (EXPOSE_PURE two-hop failure) on
e2e_attr_expr. Mitigation: wrap in try/except, fall back to running only the models
that succeed. The cross-tabulation from successful models is still valuable.

---

## Items

### Item 1: Spike 5 -- REFERENCE Binding Resolution Outcomes

**File:** `scripts/spikes/spike_reference_resolution.py`
**Answers:** Issue 11 (SYSML_QN normalization -- dead or broken?)
**Models:** solar_battery, e2e_attr_expr, chain_spike, catf_mfe

**Algorithm:**

```
1. For each model:
   a. Try build_pipeline_context(model_paths) to get full pipeline results
      - If it fails (Bug 2), fall back to manual backtracker construction:
        extract CalcDefs, CalcUsages, design attrs, computed attrs,
        then DependencyBacktracker(...).find_required_modules(...)
   b. Get binding_resolutions from BacktrackingResult

2. Build a CalcUsage lookup: {qualified_name: CalcUsageData}

3. For each (mapping_key, resolution) in binding_resolutions:
   a. Parse mapping_key: "{usage_qn}|{param_name}"
   b. Find the CalcUsage by usage_qn
   c. Find the binding by param_name
   d. Record: (binding_type, resolution_type, source_path)

4. Cross-tabulation:
   binding_type x resolution_type -> count

   Expected shape:
     BindingType    | ENTRY_POINT | MODULE_OUTPUT
     CHAIN          | ?           | ?
     REFERENCE      | ?           | ?    <-- THE KEY QUESTION
     LITERAL        | ?           | 0
     UNBOUND        | ?           | 0

5. For any REFERENCE -> MODULE_OUTPUT cases:
   Print: source_path, resolved channel, source_path format
   Test: does source_path.replace("::", "__") match the channel?
   Test: does source_path.replace("::", "__").lower() match?

6. For all REFERENCE -> ENTRY_POINT cases:
   Count by source_path format (SYSML_QN, DOTTED, BARE)
```

**Key imports:**

```python
from sysml_codegen.generation.initialization import build_pipeline_context
from sysml_codegen.core.models import BindingResolution, BindingResolutionType
from agentic_mbse.sysml.types import BindingType
```

**Fallback path (if `build_pipeline_context` fails):**

```python
from sysml_codegen.analysis.dependency_backtracker import DependencyBacktracker
from sysml_codegen.analysis.parameter_groups import extract_design_attributes
from sysml_codegen.generation.initialization import (
    _extract_and_filter_computed_attributes,
    _extract_hierarchy_and_rewrite_bindings,
    _enrich_aliases_from_bindings,
    _scope_aggregation_expressions,
)
```

Manually construct the backtracker with all the data it needs, skipping the
graph builder step (which is where Bug 2 crashes).

**Output format:**

```
========== SPIKE 5: REFERENCE Binding Resolution Outcomes ==========

--- Model: solar_battery ---

CROSS-TABULATION:
  BindingType   | ENTRY_POINT | MODULE_OUTPUT | Total
  CHAIN         | 0           | 8             | 8
  REFERENCE     | 50          | 0             | 50    <-- KEY ROW
  LITERAL       | 4           | 0             | 4
  UNBOUND       | 0           | 0             | 0
  Total         | 54          | 8             | 62

REFERENCE -> MODULE_OUTPUT CASES: (none)

REFERENCE -> ENTRY_POINT FORMAT DISTRIBUTION:
  SYSML_QN: 50
  DOTTED: 0
  BARE: 0
```

**Verification:** Cross-tab totals match Spike 1 binding counts per model. Every
binding is classified.

**Estimated effort:** Medium. The `build_pipeline_context` call is heavy but the
analysis is straightforward.

### Item 1 Completion

**Completed:** 2026-02-13
**Changes Made:**
- Created `scripts/spikes/spike_reference_resolution.py` with full pipeline + fallback path
- Ran successfully on all 4 models (solar_battery, chain_spike, e2e_attr_expr, catf_mfe)

**Issues Encountered:**
- `build_pipeline_context()` succeeded on ALL 4 models (Bug 2 fallback was not needed)
- Plan expected REFERENCE -> MODULE_OUTPUT = 0 ("none"); actual result = **4 cases**

**Deviations from Plan:**
- Plan's expected cross-tab was wrong. Actual results:

**Key Findings:**
- REFERENCE -> MODULE_OUTPUT: **4 cases** (2 in solar_battery, 2 in e2e_attr_expr)
- REFERENCE -> ENTRY_POINT: **119 cases** (all 4 models)
- All REFERENCE source_paths are SYSML_QN format (100%)
- SYSML_QN normalization (`replace("::", "__")`) does NOT match resolved channels:
  - source_path contains the *consuming* usage's path (e.g., `...annualized_om::p_net_kw`)
  - resolved channel uses the *producing* usage's EQN (e.g., `...p_net_kw__p_net_kw`)
  - The intermediate path segment differs, so naive normalization fails
- **Verdict for Issue 11:** SYSML_QN normalization in resolve() IS exercised (not dead code)
  but is BROKEN -- `replace("::", "__")` produces wrong keys. The current backtracker
  resolves these through computed attribute index lookup, not OutputRegistry.

**Grand Cross-Tabulation (all 4 models, 215 bindings):**
```
BindingType  | entry_point | module_output | Total
CHAIN        | 5           | 39            | 44
LITERAL      | 5           | 0             | 5
REFERENCE    | 119         | 4             | 123
UNBOUND      | 43          | 0             | 43
Total        | 172         | 43            | 215
```

---

### Item 2: Spike 6 -- `:>>` CHAIN Redefinition RHS Content

**File:** `scripts/spikes/spike_chain_redef_rhs.py`
**Answers:** Issue 9 (CHAIN alias canonical_name format)
**Models:** solar_battery, e2e_attr_expr

**Algorithm:**

```
1. For each model:
   a. Load model via load_model()
   b. Call extract_hierarchy_data(model) -> HierarchyExtractionResult
   c. Filter: redefs where redefinition_type == RedefinitionType.CHAIN

2. For each CHAIN redefinition:
   a. Print: owning_part_qn, attribute_name, source_path, expression_text
   b. Classify source_path format: BARE, DOTTED, SYSML_QN, AST_TEXT, NONE
   c. If expression_ast is populated:
      - Print type(expression_ast).__name__
      - Try extract_feature_refs() on it
      - Print any references found
   d. Compare source_path vs expression_text -- are they different?

3. For each CHAIN redefinition, assess:
   a. Is source_path a resolvable key for the OutputRegistry?
      (Would registry.resolve(source_path) work if the target is registered?)
   b. If source_path is bare: what is the target?
      - Is it a sibling attribute on the same PartDef?
      - Is it an aggregation attribute? A CalcUsage output?
   c. Can we construct a scoped dotted path from context?
      - owning_part_qn + source_path -> "part.attr"?
      - Or do we need instance_path from scoping?

4. Also examine design_overrides (the second field on HierarchyExtractionResult)
   for any additional CHAIN-typed overrides.

5. Summary table:
   Model | CHAIN redefs | BARE | DOTTED | SYSML_QN | AST_TEXT | NONE
```

**Key imports:**

```python
from sysml_codegen.extraction.hierarchy_resolver import extract_hierarchy_data
from sysml_codegen.extraction.data_models import (
    RedefinitionData,
    RedefinitionType,
    HierarchyExtractionResult,
)
```

**Output format:**

```
========== SPIKE 6: :>> CHAIN Redefinition RHS Content ==========

--- Model: solar_battery ---

HierarchyExtractionResult:
  redefinitions: 15
  design_overrides: 8
  CHAIN-typed redefinitions: 3

CHAIN REDEFINITIONS:

  #1: owning_part_qn="SolarBatteryLibrary::Solar_Array"
      attribute_name="total_capex"
      source_path="capital_cost"                    <-- BARE? DOTTED?
      expression_text="capital_cost"
      expression_ast type: <type>

      FORMAT: BARE
      RESOLVABLE BY REGISTRY: NO (bare names not registered)
      SCOPING NEEDED: YES -- would become "solar_array.capital_cost"

CHAIN DESIGN OVERRIDES:
  [same format]

SUMMARY:
  Model          | CHAIN redefs | BARE | DOTTED | SYSML_QN
  solar_battery  | 3            | 3    | 0      | 0
  e2e_attr_expr  | 1            | 1    | 0      | 0
```

**Verification:** Every CHAIN redefinition is classified. Format determination is
unambiguous.

**Estimated effort:** Small. Pure extraction, no pipeline run needed.

### Item 2 Completion

**Completed:** 2026-02-13
**Changes Made:**
- Created `scripts/spikes/spike_chain_redef_rhs.py`
- Ran successfully on solar_battery and e2e_attr_expr

**Issues Encountered:**
- e2e_attr_expr has ZERO hierarchy data (no PartDefs with redefinitions). All CHAIN data comes from solar_battery only.
- expression_text is empty for all CHAIN redefs (source_path is the reliable field)
- expression_ast is None for all CHAIN redefs

**Deviations from Plan:**
- Plan expected both models to have CHAIN data; only solar_battery does
- Plan mentioned examining expression_ast; it's always None for CHAIN type

**Key Findings:**
- **54 CHAIN redefinitions** total in solar_battery (0 in e2e_attr_expr)
- **13 BARE** (24%): CAS category codes like `"CAS220101"`, `"CAS22"` -- enum-like literal values, NOT resolvable references
- **41 DOTTED** (76%): All follow pattern `"cost_model.{output_name}"` -- PartDef-local dotted paths referencing sibling CalcUsage outputs
- **0 SYSML_QN, 0 AST_TEXT, 0 NONE**
- **0 CHAIN design_overrides** (all 13 design overrides are LITERAL)
- **Confirms Issue 9:** canonical_name is PartDef-local (bare or dotted), cannot resolve in OutputRegistry without scoping
- **Fix validated:** `canonical_name = f"{instance_path}.{redef.source_path}"` for DOTTED cases
- **BARE cases are NOT references** -- they're CAS category string literals misclassified as CHAIN (the `cas_category` attribute is assigned a string code, not a channel reference). These should be filtered out or classified differently.

**Summary Table:**
```
Model          | CHAIN redefs | BARE | DOTTED
solar_battery  | 54           | 13   | 41
e2e_attr_expr  | 0            | 0    | 0
```

---

### Item 3: Spike 7 -- DesignAttributeData.default_value for Path-Like Defaults

**File:** `scripts/spikes/spike_design_attr_defaults.py`
**Answers:** Issue 12 (Phase 4 transitive alias registration)
**Models:** solar_battery, e2e_attr_expr

**Algorithm:**

```
1. For each model:
   a. Load model via load_model()
   b. Extract CalcDefs and CalcUsages (for building output catalog)
   c. extract_design_attributes(model) -> dict[Path, list[DesignAttributeData]]

2. For each DesignAttributeData:
   a. Classify default_value:
      - None/empty -> NONE
      - Numeric (float/int parseable) -> NUMERIC
      - "true"/"false" -> BOOLEAN
      - Contains "::" -> SYSML_QN
      - Contains "." and not numeric -> DOTTED_PATH
      - Contains "(" or starts with "." -> AST_TEXT
      - Everything else -> STRING_LITERAL (could be bare name)
   b. Print: name, parent_part, default_value, classification

3. Build output catalog (reuse build_output_catalog from Spike 3):
   For each CalcUsage + CalcDef output -> register dotted keys

4. For each DOTTED_PATH or SYSML_QN default_value:
   a. Try output_catalog.get(default_value)
   b. If SYSML_QN: try normalized = default_value.replace("::", "__")
      then output_catalog.get(normalized), output_catalog.get(normalized.lower())
   c. Report: resolved? To which channel?

5. For each STRING_LITERAL default_value that looks like a bare name:
   a. Could this be a reference? (e.g., "capital_cost")
   b. Check if bare name matches any output name in any CalcUsage
   c. Report: potential reference? ambiguous?

6. Summary:
   - Total design attrs per model
   - Classification distribution
   - Number of transitive defaults (DOTTED_PATH/SYSML_QN that resolve)
   - Number of ambiguous bare-name defaults
   - Proposed filter for Phase 4 registration
```

**Key imports:**

```python
from sysml_codegen.analysis.parameter_groups import (
    DesignAttributeData,
    extract_design_attributes,
)
from sysml_codegen.extraction.usage_extractor import extract_calculation_usages
```

**Output format:**

```
========== SPIKE 7: DesignAttributeData.default_value Format ==========

--- Model: e2e_attr_expr ---

DESIGN ATTRIBUTES (15 total):

  name              | parent_part  | default_value                 | classification
  efficiency        | e2e_plant    | 0.92                          | NUMERIC
  total_capex       | e2e_plant    | component_cost.total_cost     | DOTTED_PATH
  plant_lifetime    | e2e_plant    | 25.0                          | NUMERIC
  ...

TRANSITIVE DEFAULT RESOLUTION:
  e2e_plant.total_capex: default="component_cost.total_cost"
    output_catalog.get("component_cost.total_cost") = "component_cost__total_cost"
    RESOLVES: YES -> channel "component_cost__total_cost"

SUMMARY:
  Model          | Total | NUMERIC | BOOLEAN | DOTTED | SYSML_QN | STRING | NONE
  e2e_attr_expr  | 15    | 10      | 0       | 2      | 0        | 3      | 0

TRANSITIVE DEFAULTS: 2 found, 2 resolve successfully
PROPOSED FILTER: default_value contains "." and is not numeric
```

**Verification:** Every design attribute is classified. Transitive defaults are
tested against the output catalog.

**Estimated effort:** Small. Pure extraction + catalog building.

### Item 3 Completion

**Completed:** 2026-02-13
**Changes Made:**
- Created `scripts/spikes/spike_design_attr_defaults.py`
- Ran successfully on solar_battery and e2e_attr_expr

**Issues Encountered:**
- None. Clean run on both models.

**Deviations from Plan:**
- None. Results match expected shape.

**Key Findings:**
- **128 total design attributes** (100 solar_battery, 28 e2e_attr_expr)
- **Classification distribution:** NUMERIC: 58, NONE: 68, DOTTED_PATH: 2, BOOLEAN: 0, SYSML_QN: 0, AST_TEXT: 0, STRING_LITERAL: 0
- **2 DOTTED_PATH transitive defaults found, BOTH resolve successfully:**
  - `e2e_plant.total_capex`: default=`"component_cost.total_cost"` -> channel `component_cost__total_cost`
  - `solar_battery_plant.misc_hardware_cost`: default=`"allocation_model.total_allocation"` -> channel `...allocation_model__total_allocation`
- **0 STRING_LITERAL defaults** -- no bare-name ambiguity concern
- **0 SYSML_QN defaults** -- no `::` normalization needed for Phase 4
- **Confirms Issue 12:** Phase 4 transitive alias registration WORKS with actual data
- **Filter validated:** `"." in default_value and not float(default_value)` correctly identifies both transitive defaults
- default_value is always a clean dotted path (NOT raw AST text like EXPOSE_PURE expression_text)

**Summary Table:**
```
Model          | Total | NUMERIC | NONE | DOTTED_PATH
solar_battery  | 100   | 46      | 53   | 1
e2e_attr_expr  | 28    | 12      | 15   | 1
```

---

### Item 4: Summary Findings Document

**File:** `.project/research/{timestamp}_spike_results_iteration2.md`

Written after running all three spikes. Structure:

```markdown
# Research: Iteration 2 Spike Results

## Spike 5 Findings: REFERENCE Binding Resolution Outcomes
[Cross-tabulation data per model]
[Design implication for SYSML_QN normalization in resolve()]

## Spike 6 Findings: :>> CHAIN Redefinition RHS Content
[Format classification per model]
[Design implication for ChannelAlias canonical_name construction]

## Spike 7 Findings: DesignAttributeData.default_value Format
[Classification distribution per model]
[Design implication for Phase 4 transitive alias registration]

## Design Comment Resolutions
| Comment Issue | Finding | Resolution |
|---|---|---|
| Issue 9 (CHAIN alias bare name) | [spike 6 result] | [fix approach] |
| Issue 11 (REFERENCE -> MODULE_OUTPUT?) | [spike 5 result] | [simplify or fix] |
| Issue 12 (design attr default_value) | [spike 7 result] | [filter criteria] |

## Informed Resolutions (no spike needed)
| Comment Issue | Informed by | Resolution |
|---|---|---|
| Issue 10 (_resolve_to_design_attribute) | Spike 5 | [spec approach] |
| Issue 13 (FORMULA input wiring) | Spike 7 | [approach] |
| Issue 14 (aggregation input resolution) | Spike 6 | [approach] |
```

**Verification:** Every design comment issue has a data-backed resolution or
informed resolution.

### Item 4 Completion

**Completed:** 2026-02-13
**Changes Made:**
- Created `.project/research/20260213_spike_results_iteration2.md`

**Issues Encountered:**
- None.

**Deviations from Plan:**
- None. All sections populated with concrete data from spikes 5-7.

---

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| `build_pipeline_context()` crashes on e2e_attr_expr (Bug 2) | High | Spike 5 loses one model | Fall back to manual backtracker construction (skip graph builder) |
| `build_pipeline_context()` crashes on solar_battery | Low | Spike 5 loses primary model | Manual construction fallback; solar_battery has worked before |
| CHAIN redefs have no `source_path` (only AST) | Medium | Spike 6 needs AST extraction | Examine `expression_ast` and `expression_text` as fallback |
| `default_value` is always literal (no transitive cases) | Medium | Phase 4 is unnecessary | Document finding; simplify OutputRegistry (fewer phases) |
| catf_mfe fixture incomplete | Low | Spike 5 has fewer models | Use solar_battery + chain_spike as primary data |

---

## Definition of Done

- [x] All 3 spike scripts run without errors on their target models
- [x] Each spike produces structured output matching the format specified above
- [x] Summary findings doc is written with concrete data
- [x] Each design_revision_comments_v2.md issue has a data-backed resolution
- [x] Ready to update `08_algorithm_revised.md` in iteration 2 step 3

## Risk Outcomes

| Risk | Outcome |
|------|---------|
| `build_pipeline_context()` crashes on e2e_attr_expr | **DID NOT OCCUR** -- succeeded on all 4 models |
| `build_pipeline_context()` crashes on solar_battery | **DID NOT OCCUR** |
| CHAIN redefs have no `source_path` | **DID NOT OCCUR** -- source_path is populated (DOTTED or BARE) |
| `default_value` is always literal | **PARTIALLY** -- 126/128 are literal, but 2 are transitive paths |
| catf_mfe fixture incomplete | **DID NOT OCCUR** -- catf_mfe ran successfully (136 bindings) |
