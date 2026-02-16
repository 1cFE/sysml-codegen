# Plan: Spike 8 -- OutputRegistry End-to-End Key Format Validation

**Status:** Complete
**Spec:** `.project/active/output-registry-spike/spec.md`
**Created:** 2026-02-13T19:30:51+00:00

---

## Implementation Strategy

One spike script with three logical sections, plus a findings document.
The script is diagnostic-only (read-only against the pipeline). No production
code changes.

**Phasing rationale:** Data extraction first (reuse existing pipeline), then
prototype registry build (the new thing), then validation (the payoff). Each
section produces structured output that feeds the findings doc.

```
Item 1: Spike script -- data extraction + prototype registry
Item 2: Spike script -- phase 2/3/4 alias validation
Item 3: Spike script -- backtracker resolution comparison + instance_path docs
Item 4: Findings document
```

All items are in a single script file. Items 1-3 are sequential sections within
it. Item 4 is a separate markdown file written after running the script.

---

## Items

### Item 1: Data Extraction + Phase 1 Registry Build

**File:** `scripts/spikes/spike_output_registry_e2e.py`

**Goal:** Load both models, run extraction through Step 4.5+scoping, build the
prototype OutputRegistry (Phase 1 only), and report all registered keys.

**Algorithm:**

```python
for model_name, paths in [("solar_battery", ...), ("e2e_attr_expr", ...)]:
    # 1. Load model
    model, adapter, extractor = load_model(paths)
    calc_defs = extractor.extract_calculation_definitions()
    calc_def_by_name = {cd.name: cd for cd in calc_defs}

    # 2. Extract CalcUsages (expanded)
    calc_usages = extract_calculation_usages(model, calc_defs=calc_defs, expand_templates=True)

    # 3. Hierarchy extraction + binding rewrite
    hierarchy_data = _extract_hierarchy_and_rewrite_bindings(model, calc_usages)

    # 4. Design attributes
    design_attrs = extract_design_attributes(model, adapter)

    # 5. Computed attributes
    computed_attrs = _extract_and_filter_computed_attributes(
        model, adapter, calc_usages, design_attrs
    )

    # 6. Scoped aggregation
    scoped_agg = _scope_aggregation_expressions(hierarchy_data, calc_usages)

    # 7. Run backtracker for ground truth
    backtracker = DependencyBacktracker(
        calc_usages, calc_defs,
        design_attributes=design_attrs,
        computed_attributes=computed_attrs,
        aggregation_data=scoped_agg,
    )
    bt_result = backtracker.find_required_modules(...)

    # 8. Build prototype registry (Phase 1)
    registry = {}       # key -> channel
    key_source = {}     # key -> description of where it came from
    collisions = []     # (key, channel_old, channel_new)

    # Phase 1A: CalcUsage outputs
    for usage in calc_usages:
        if usage.is_template:
            continue
        cd = calc_def_by_name.get(usage.calc_def_name)
        if not cd:
            continue
        for out_attr in cd.output_attributes:
            channel = get_channel_name(usage.qualified_name, out_attr.name)

            key_a = f"{usage.instance_name}.{out_attr.name}"
            key_b = f"{usage.qualified_name}__{out_attr.name}"

            # Issue 15 fix candidate: dotted hierarchy path
            segments = usage.qualified_name.split("__")
            dotted_path = ".".join(segments[1:])  # drop design prefix
            key_c = f"{dotted_path}.{out_attr.name}"

            register(registry, key_source, collisions, channel,
                     key_a, "CalcUsage.Key_A(instance.output)",
                     key_b, "CalcUsage.Key_B(EQN__output)",
                     key_c, "CalcUsage.Key_C(dotted_hierarchy.output)")

    # Phase 1B: Aggregation outputs
    for agg in scoped_agg:
        channel = get_channel_name(agg.module_eqn, agg.expression.attribute_name)
        instance_parts = agg.instance_path.split("__")
        part_usage_name = instance_parts[-1]

        key_d = f"{part_usage_name}.{agg.expression.attribute_name}"
        key_e = ".".join(instance_parts + [agg.expression.attribute_name])
        register(...)

        for alias_name in agg.expression.aliases:
            key_alias_d = f"{part_usage_name}.{alias_name}"
            key_alias_e = ".".join(instance_parts + [alias_name])
            register(...)

    # Phase 1C: FORMULA computed attribute outputs
    for ca in computed_attrs:
        if ca.classification != FORMULA:
            continue
        if ca.compilability != FULLY_COMPILABLE:
            continue
        module_eqn = f"{ca.owning_part_qualified_name}__{ca.python_name}"
        channel = get_channel_name(module_eqn, ca.python_name)
        key_f = f"{ca.owning_part_name}.{ca.python_name}"
        register(...)
```

**Output:**

```
========== SPIKE 8: OutputRegistry E2E Key Format Validation ==========

--- Model: solar_battery ---

PHASE 1 REGISTRATION:

  CalcUsage Outputs (concrete):
    annualized_financial | channel: ...annualized_financial__annualized_capital_cost
      Key_A: annualized_financial.annualized_capital_cost
      Key_B: SolarBatteryDesign__...annualized_financial__annualized_capital_cost
      Key_C: solar_battery_plant.annualized_financial.annualized_capital_cost
      Key_A == Key_C? NO (Key_C adds parent scope)

  CalcUsage Outputs (virtual):
    SolarBatteryDesign__...pv_module__cost_model | channel: ...cost_model__total_cost
      Key_A: SolarBatteryDesign__...pv_module__cost_model.total_cost  (LONG!)
      Key_B: SolarBatteryDesign__...pv_module__cost_model__total_cost
      Key_C: solar_battery_plant.solar_array.pv_module.cost_model.total_cost
      Key_A == Key_C? NO (different formats)

  Aggregation Outputs:
    solar_battery_plant__solar_array__capital_cost | channel: ...
      Key_D: solar_array.capital_cost
      Key_E: solar_battery_plant.solar_array.capital_cost

  FORMULA Outputs:
    p_net_kw | channel: ...p_net_kw__p_net_kw
      Key_F: solar_battery_plant.p_net_kw

  SUMMARY:
    Channels: N, Keys: M, Collisions: K
    Key_A != Key_C for N virtual CalcUsages (Issue 15 relevant)
```

**Key imports:**

```python
from _helpers import load_model, print_section, print_subsection, print_table
from sysml_codegen.extraction.usage_extractor import extract_calculation_usages
from sysml_codegen.generation.initialization import (
    _extract_hierarchy_and_rewrite_bindings,
    _extract_and_filter_computed_attributes,
    _scope_aggregation_expressions,
    _enrich_aliases_from_bindings,
)
from sysml_codegen.analysis.parameter_groups import extract_design_attributes
from sysml_codegen.analysis.dependency_backtracker import DependencyBacktracker
from sysml_codegen.core.qualified_names import get_channel_name
from sysml_codegen.extraction.data_models import (
    ComputedAttributeClassification,
    ScopedAggregationData,
    RedefinitionType,
)
from sysml_codegen.extraction.expression_compiler import Compilability
from agentic_mbse.sysml.types import BindingType
```

**Verification:** Phase 1 completes for both models. All channels and keys printed.
Collision count reported.

---

### Item 2: Phase 2/3/4 Alias Validation

**Same file, next section.**

**Goal:** Attempt Phase 2/3/4 alias resolution against the Phase 1 registry.
Report success/failure per alias. For failures, compute the "would-fix" key.

**Algorithm:**

```python
# ── Phase 2: CHAIN alias validation ──
phase2_results = []  # (model, alias_name, canonical_name, resolved, would_fix_key)

for redef in hierarchy_data.redefinitions:
    if redef.redefinition_type != RedefinitionType.CHAIN:
        continue
    if not redef.source_path or "." not in redef.source_path:
        continue  # Skip BARE CAS codes

    # Find instance_paths for this PartDef (from scoped_agg or virtual CalcUsages)
    instance_paths = find_instance_paths_for_partdef(redef.owning_part_qn, ...)

    for inst_path in instance_paths:
        inst_parts = inst_path.split("__")
        alias_key = ".".join(inst_parts + [redef.attribute_name])

        # canonical_name: scope the PartDef-local dotted source_path
        source_parts = redef.source_path.split(".")
        canonical_key = ".".join(inst_parts + source_parts)

        resolved_channel = registry.get(canonical_key)

        # If failed, check what WOULD work
        would_fix = None
        if resolved_channel is None:
            # Try with Key_C format (the proposed Issue 15 fix)
            for key, ch in registry.items():
                if key.endswith("." + redef.source_path.split(".")[-1]):
                    # Check if the path matches structurally
                    ...

        phase2_results.append((alias_key, canonical_key, resolved_channel, would_fix))

# ── Phase 3: EXPOSE_PURE alias validation ──
phase3_results = []

for ca in computed_attrs:
    if ca.classification != ComputedAttributeClassification.EXPOSE_PURE:
        continue
    if len(ca.references) < 2:
        continue

    instance_name = ca.references[1].name
    output_name = ca.references[0].name
    canonical_name = f"{instance_name}.{output_name}"

    resolved_channel = registry.get(canonical_name)
    scoped_alias = f"{ca.owning_part_name}.{ca.python_name}"

    phase3_results.append((scoped_alias, canonical_name, resolved_channel))

# ── Phase 4: Transitive default validation ──
phase4_results = []

for file_path, attrs in design_attrs.items():
    for attr in attrs:
        if attr.default_value is None:
            continue
        val = str(attr.default_value)
        if "." not in val:
            continue
        try:
            float(val)
            continue
        except ValueError:
            pass

        resolved_channel = registry.get(val)
        scoped_key = f"{attr.parent_part}.{attr.name}" if attr.parent_part else attr.name

        phase4_results.append((scoped_key, val, resolved_channel))
```

**Output:**

```
PHASE 2 VALIDATION (CHAIN aliases):

  Model: solar_battery
  Total CHAIN redefs (DOTTED): 41
  Instance paths found: N
  Alias attempts: M
  Resolved: R / M
  Failed: F / M

  FAILURES:
    alias: solar_battery_plant.solar_array.pv_module.capital_cost
    canonical: solar_battery_plant.solar_array.pv_module.cost_model.total_cost
    registry has: (none matching)
    would-fix key: solar_battery_plant.solar_array.pv_module.cost_model.total_cost
      -> needs Key_C registration: YES/NO

PHASE 3 VALIDATION (EXPOSE_PURE aliases):

  Model: e2e_attr_expr
  EXPOSE_PURE attrs: N
  Resolved: R / N

  e2e_plant.total_capex -> component_cost.total_cost -> RESOLVED: channel_X

PHASE 4 VALIDATION (transitive defaults):

  Model: e2e_attr_expr
  e2e_plant.total_capex -> component_cost.total_cost -> RESOLVED: channel_X

  Model: solar_battery
  solar_battery_plant.misc_hardware_cost -> allocation_model.total_allocation -> RESOLVED: channel_Y
```

**Verification:** Success/failure rates reported per phase per model.
Every failure has a would-fix key.

---

### Item 3: Backtracker Resolution Comparison + instance_path Documentation

**Same file, final section.**

**Goal:** Compare prototype registry resolve() against ground truth
backtracker results. Validate REFERENCE secondary resolution parent_part logic.
Document instance_path format.

**Algorithm:**

```python
# ── CHAIN binding validation ──
chain_results = []

for usage in calc_usages:
    if usage.is_template:
        continue
    for binding in usage.bindings:
        if binding.binding_type != BindingType.CHAIN:
            continue
        if not binding.source_path:
            continue

        mapping_key = f"{usage.qualified_name}|{binding.param_name}"
        ground_truth = bt_result.binding_resolutions.get(mapping_key)

        prototype_channel = registry.get(binding.source_path)

        gt_type = ground_truth.resolution_type if ground_truth else "MISSING"
        gt_channel = ground_truth.qualified_name if ground_truth else "MISSING"

        match = False
        if gt_type == BindingResolutionType.MODULE_OUTPUT:
            match = (prototype_channel == gt_channel)
        elif gt_type == BindingResolutionType.ENTRY_POINT:
            match = (prototype_channel is None)  # correct: not a module output

        chain_results.append((usage.qualified_name, binding.param_name,
                              binding.source_path, gt_type, gt_channel,
                              prototype_channel, match))

# ── REFERENCE secondary resolution validation ──
ref_results = []

for usage in calc_usages:
    if usage.is_template:
        continue
    for binding in usage.bindings:
        if binding.binding_type != BindingType.REFERENCE:
            continue
        if not binding.source_path:
            continue

        mapping_key = f"{usage.qualified_name}|{binding.param_name}"
        ground_truth = bt_result.binding_resolutions.get(mapping_key)

        if not ground_truth or ground_truth.resolution_type != BindingResolutionType.MODULE_OUTPUT:
            continue  # only care about the 4 REF -> MODULE_OUTPUT cases

        # Try multiple parent_part candidates
        leaf_name = binding.source_path.rsplit("::", 1)[-1].strip("'")
        segments = usage.qualified_name.split("__")

        candidates = {}
        for i in range(1, len(segments)):
            candidate_part = segments[i]
            candidate_key = f"{candidate_part}.{leaf_name}"
            resolved = registry.get(candidate_key)
            candidates[candidate_part] = (candidate_key, resolved)

        # Also try dotted combinations (e.g., "solar_battery_plant.p_net_kw")
        for i in range(1, len(segments)):
            candidate_part = ".".join(segments[1:i+1])
            candidate_key = f"{candidate_part}.{leaf_name}"
            resolved = registry.get(candidate_key)
            candidates[f"dotted({i}):{candidate_part}"] = (candidate_key, resolved)

        ref_results.append((usage.qualified_name, binding.param_name,
                            binding.source_path, leaf_name,
                            ground_truth.qualified_name, candidates))

# ── instance_path documentation ──
for agg in scoped_agg:
    inst_parts = agg.instance_path.split("__")
    dotted_form = ".".join(inst_parts)
    print(f"  instance_path: {agg.instance_path}")
    print(f"  split('__'):   {inst_parts}")
    print(f"  dotted form:   {dotted_form}")
    print(f"  module_eqn:    {agg.module_eqn}")
    print(f"  attribute:     {agg.expression.attribute_name}")
```

**Output:**

```
CHAIN BINDING VALIDATION:

  Model: solar_battery
  Total CHAIN bindings: 8
  Matches ground truth: 8/8

  Binding                              | GT Type       | GT Channel        | Proto Channel    | Match
  annualized_financial|total_capex     | MODULE_OUTPUT | ...capital_cost   | ...capital_cost  | YES
  ...

REFERENCE SECONDARY RESOLUTION:

  Model: solar_battery (2 REF -> MODULE_OUTPUT cases)

  Usage: annualized_om | Param: p_net_kw | Leaf: p_net_kw
  Ground truth channel: ...p_net_kw__p_net_kw
  Candidate parent_parts:
    segments[-2] = "solar_battery_plant" -> "solar_battery_plant.p_net_kw" -> RESOLVED: ...p_net_kw__p_net_kw  ✓
    segments[-3] = "..." -> ... -> None
    ...
  WINNER: segments[-2] (immediate parent of CalcUsage)

INSTANCE_PATH DOCUMENTATION:

  Model: solar_battery
  ScopedAggregation #1:
    instance_path: SolarBatteryDesign__solar_battery_plant__solar_array
    split('__'):   ['SolarBatteryDesign', 'solar_battery_plant', 'solar_array']
    dotted form:   SolarBatteryDesign.solar_battery_plant.solar_array
    module_eqn:    SolarBatteryDesign__solar_battery_plant__solar_array__capital_cost
    attribute:     capital_cost

  OBSERVATION: instance_path INCLUDES design prefix (first segment).
               Aggregation index Key_E drops first segment? Let me check...
               Backtracker line 165: instance_parts = agg.instance_path.split("__")
               Backtracker line 184: ".".join(instance_parts + [attr])
               -> "SolarBatteryDesign.solar_battery_plant.solar_array.capital_cost"
               Does this match any CHAIN binding source_path? Check...
```

**Critical detail to verify:** Does `instance_path` include the design prefix
(e.g., `SolarBatteryDesign__solar_battery_plant__solar_array`) or start from
the first PartUsage (e.g., `solar_battery_plant__solar_array`)? The aggregation
index at backtracker.py:165-187 uses `instance_path.split("__")` directly.
If it includes the design prefix, the dotted aggregation key would be
`SolarBatteryDesign.solar_battery_plant.solar_array.capital_cost` which would
NOT match a CHAIN binding source_path like
`solar_battery_plant.capital_cost`.

This is a key empirical question the spike must answer.

**Verification:** All CHAIN bindings match ground truth. REFERENCE secondary
resolution identifies winning parent_part logic. instance_path format fully
documented.

---

### Item 4: Findings Document

**File:** `.project/research/YYYYMMDD_spike_results_output_registry_e2e.md`

**Written after running the spike script.** Structure:

```markdown
# Research: Spike 8 -- OutputRegistry E2E Key Format Validation

## Phase 1 Findings: Registration Key Formats
- CalcUsage concrete keys: [formats]
- CalcUsage virtual keys: [formats, Key_A vs Key_C difference]
- Aggregation keys: [formats]
- FORMULA keys: [formats]
- instance_path includes design prefix? [YES/NO]

## Phase 2 Findings: CHAIN Alias Resolution
- Resolution rate: R/M
- Failure pattern: [description]
- Issue 15 fix (Key_C) would fix: [count]
- instance_path -> dotted conversion needed: [YES/NO, details]

## Phase 3 Findings: EXPOSE_PURE Alias Resolution
- Resolution rate: R/N
- references field reliable: [YES/NO]

## Phase 4 Findings: Transitive Default Resolution
- Both transitive defaults resolve: [YES/NO]

## Backtracker Comparison
- CHAIN binding match rate: [count]
- REFERENCE secondary resolution: parent_part = segments[???]

## Design Comment Resolutions
| Issue | Finding | Resolution |
|---|---|---|
| 15 | Key format mismatch | [fix: Key_C + dotted conversion] |
| 16 | instance_path format | [includes/excludes prefix, uses __] |
| 17 | _get_parent_part_for_usage() | [segments[-2] or other] |
| 20 | Phase 2 consumers | [resolution rate data] |

## Key Format Specification (for design doc update)
[The authoritative key format contract to add to 08_algorithm_revised.md]
```

**Verification:** Every Issue (15-17, 20) has a finding-backed resolution.

---

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| `find_required_modules()` needs target args we don't know | Medium | Blocks ground truth | Use empty targets or `find_all_modules()` if available; else build binding_resolutions from backtracker constructor indexes directly |
| `instance_path` includes design prefix making ALL aggregation dotted keys wrong | Medium | Changes aggregation key format understanding | That's exactly what the spike is for -- discovery |
| `_extract_and_filter_computed_attributes` signature changed | Low | Import error | Check current signature in initialization.py before writing |
| e2e_attr_expr model path not accessible | Low | Lose one model | solar_battery is the primary model for Phase 2 (41 CHAIN redefs) |

---

## Definition of Done

- [x] Spike script runs on both models without errors
- [x] Phase 1 registration produces structured key inventory
- [x] Phase 2 reports CHAIN alias resolution rate with failure analysis
- [x] Phase 3 reports EXPOSE_PURE alias resolution (expect: success)
- [x] Phase 4 reports transitive default resolution (expect: success)
- [x] CHAIN binding resolution matches ground truth 100%
- [x] REFERENCE secondary resolution identifies correct parent_part logic
- [x] instance_path format documented (prefix inclusion, separator)
- [x] Findings document written with Issue 15-17, 20 resolutions
- [x] Ready to update `08_algorithm_revised.md` with key format spec

---

## Implementation Notes

### Item 1 Completion
**Completed:** 2026-02-13
**Changes Made:**
- Created `scripts/spikes/spike_output_registry_e2e.py` with Phase 1 registration
- Followed existing spike conventions (shebang, _helpers imports, DEFAULT_SUITES filtering)
- Used manual pipeline construction sequence (matching spike_reference_resolution.py)

**Results:**
- solar_battery: 77 channels, 217 keys, 0 collisions (6 concrete + 50 virtual + 20 agg + 1 FORMULA)
- e2e_attr_expr: 15 channels, 33 keys, 0 collisions (9 concrete + 0 virtual + 0 agg + 6 FORMULA)
- Key_C (dotted hierarchy path) differs from Key_A for ALL CalcUsages (both models)
  - This confirms Issue 15: Key_A uses instance_name which != dotted path for concrete CalcUsages

**Deviations from Plan:**
- FORMULA module_eqn: Plan used `ca.owning_part_qualified_name` directly (SysML :: format).
  Actual backtracker uses `sysml_to_python_qualified_name()` to convert :: to __. Fixed to match.
- `extract_design_attributes()` takes only `(model)`, not `(model, adapter)` as plan implied. Used correct signature.

### Item 2 Completion
**Completed:** 2026-02-13
**Changes Made:**
- Added `find_instance_paths_for_partdef()` mirroring `_scope_aggregation_expressions` logic
- Added `validate_phase2_chain_aliases()` with resolved_via tracking
- Added `validate_phase3_expose_pure()` with EXPOSE_PURE alias resolution
- Added `validate_phase4_transitive_defaults()` with dotted-path default resolution

**Results:**
- Phase 2 (CHAIN aliases): solar_battery 41/41 resolved (100%), ALL via Key_C(virtual)
  - Conclusively validates Issue 15 fix: Key_C is REQUIRED for Phase 2 resolution
  - e2e_attr_expr: 0 CHAIN redefs (no hierarchy)
- Phase 3 (EXPOSE_PURE): solar_battery 0/1 FAILED, e2e_attr_expr 1/1 resolved
  - solar_battery failure: `Solar_Array.misc_hardware_cost -> allocation_model.total_allocation`
  - Root cause: EXPOSE_PURE on PartDef produces PartDef-local canonical name (unscoped)
  - This is Issue 21: EXPOSE_PURE on PartDefs needs instance scoping or filtering
  - e2e_attr_expr succeeds because EXPOSE_PURE is on design-root PartUsage (scope matches)
- Phase 4 (transitive defaults): solar_battery 0/1 FAILED, e2e_attr_expr 1/1 resolved
  - Same root cause as Phase 3: `allocation_model.total_allocation` is PartDef-local
  - The attribute was originally EXPOSE_PURE before being reclassified as design attr

**Deviations from Plan:**
- Plan expected Phase 3+4 to succeed on both models. solar_battery Phase 3+4 fails due to
  Issue 21 (EXPOSE_PURE on PartDefs). This is a genuine finding, not a spike bug.
- Plan's `find_instance_paths_for_partdef()` was pseudocode; implemented matching
  `_scope_aggregation_expressions` Strategy 1+2 with dotted output (design prefix stripped).

### Item 3 Completion
**Completed:** 2026-02-13
**Changes Made:**
- Added `validate_chain_bindings()` comparing prototype registry vs backtracker ground truth
- Added `validate_reference_secondary_resolution()` testing all parent_part candidates
- Added `document_instance_paths()` with format analysis

**Results:**
- CHAIN binding validation: 4/4 match on solar_battery, 2/2 match on e2e_attr_expr (100%)
- REFERENCE secondary resolution: 4/4 cases (2 per model), ALL resolve via segments[-2]
  - segments[-2] IS the immediate parent PartUsage of the CalcUsage
  - For solar_battery: segments[-2] = "solar_battery_plant" (design root, which IS the immediate parent)
  - For e2e_attr_expr: segments[-2] = "e2e_plant" (design root, same)
  - segments[1] also wins (happens to equal segments[-2] for these CalcUsages at depth 3)
  - Pattern: `_get_parent_part_for_usage()` = `segments[-2]` is correct (Issue 17 resolved)
- instance_path format:
  - INCLUDES design prefix (first segment is PascalCase PartDef name)
  - Separator: `__` (double underscore)
  - Phase 1 aggregation Key_E includes prefix in dotted form
  - Phase 2 alias scoping strips prefix -> compatible with Key_C
  - Key finding: the backtracker's aggregation index (lines 165-187) uses instance_parts
    DIRECTLY, so Key_E includes the design prefix. But CHAIN source_paths do NOT include
    the design prefix. This is why Phase 2 alias resolution works (it uses stripped paths)
    but Key_E would not match CHAIN source_paths directly (Issue 16 resolved).

**Deviations from Plan:**
- Plan expected 8 CHAIN bindings for solar_battery; actual is 4 (only DOTTED CHAIN bindings
  on concrete CalcUsages are counted; virtual CalcUsage bindings use different binding types).
- Plan referenced `binding.source_path` containing `"." in source_path` for CHAIN filtering;
  actual CHAIN bindings all have dotted source_paths, so no filtering was needed.

### Item 4 Completion
**Completed:** 2026-02-13
**Changes Made:**
- Created `.project/research/20260213_spike_results_output_registry_e2e.md`

**Contents:**
- Phase 1-4 findings with data tables
- Backtracker comparison results
- Design comment resolutions (Issues 15, 16, 17, 20 all resolved with spike data)
- Additional finding: Issue 21 confirmed (EXPOSE_PURE on PartDefs)
- Key Format Specification ready for 08_algorithm_revised.md update
- Summary statistics table
