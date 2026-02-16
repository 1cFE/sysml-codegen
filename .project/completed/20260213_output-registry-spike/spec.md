# Spec: Spike 8 -- OutputRegistry End-to-End Key Format Validation

**Status:** Complete
**Owner:** Reid Westwood
**Created:** 2026-02-13T19:30:51+00:00
**Complexity:** MEDIUM
**Branch:** cost-pattern

---

## Business Goals

### Why This Matters

The OutputRegistry design (08_algorithm_revised.md Section 12) replaces 5 ad-hoc
backtracker indexes with a single 4-phase registration/resolution protocol.
Design review iteration 3 (design_revision_comments_v3.md) identified that the
exact string format of registration keys at Phase 1 may not match the resolution
keys used by Phase 2-4 aliases and backtracker resolve() calls.

This is the same "key format mismatch" root cause (Report 07) that produced the
current bug stream. If the OutputRegistry ships with mismatched key formats,
we replace 5 broken indexes with 1 broken registry.

### Success Criteria

- [ ] Phase 1 registration key formats documented for every CalcUsage type
      (concrete vs virtual), aggregation output, and FORMULA computed attribute
- [ ] Phase 2 CHAIN alias canonical_name format validated against Phase 1 keys
- [ ] Phase 3 EXPOSE_PURE alias canonical_name format validated against Phase 1+2
- [ ] Phase 4 transitive default resolution validated against Phase 1-3
- [ ] REFERENCE secondary resolution parent_part logic validated for all 4
      REFERENCE -> MODULE_OUTPUT cases (Spike 5)
- [ ] Any format mismatches have a documented fix with the exact key that
      WOULD work
- [ ] `instance_path` format is empirically documented (separators, scope, derivation)

### Priority

Blocks OutputRegistry implementation. This is the final spike before coding begins.

---

## Problem Statement

### Current State

The design document specifies Phase 1-4 registration in pseudocode, but uses
ambiguous terms like `instance_path`, `owning_part_short_name`, and
`_get_parent_part_for_usage()` without defining their exact output format.

Key uncertainties:
1. `ScopedAggregationData.instance_path` uses `__` separators (confirmed in
   `initialization.py:375`). The aggregation output index converts `__` to `.`
   when building dotted keys (line 184). But the design's CHAIN alias construction
   uses `instance_path` directly in `f"{instance_path}.{redef.source_path}"` --
   mixing `__` and `.` in the same key.

2. Virtual CalcUsage `instance_name` is the full qualified name with `__`
   (confirmed in `usage_extractor.py:255`). Phase 1 registers
   `f"{instance_name}.{output}"` which produces hybrid `__`+`.` keys for
   virtual CalcUsages. Phase 2 CHAIN aliases use converted dotted paths.
   These formats are incompatible.

3. REFERENCE binding secondary resolution uses `_get_parent_part_for_usage()`
   which is unspecified. The 4 known REFERENCE -> MODULE_OUTPUT cases
   (Spike 5) all involve design-root-level CalcUsages. The correct parent_part
   extraction logic is unknown.

### Desired Outcome

A single diagnostic script that builds a prototype OutputRegistry from real model
data, following the Phase 1-4 protocol, and validates that every alias and
backtracker resolution produces the correct result. Mismatches are diagnosed with
the exact key format needed to fix them.

---

## Scope

### In Scope

- One spike script: `scripts/spikes/spike_output_registry_e2e.py`
- Tests against solar_battery and e2e_attr_expr models
- Builds prototype OutputRegistry (dict-based, no new production code)
- Validates all 4 registration phases
- Validates backtracker CHAIN and REFERENCE resolution paths
- Documents `instance_path` format empirically

### Out of Scope

- Production OutputRegistry implementation (that's the NEXT task)
- Modifications to any pipeline code or data models
- Testing chain_spike or catf_mfe (they lack hierarchy/aggregation data)

---

## Requirements

### Functional Requirements

#### FR-1: Extract All Data Through Step 4.5+Scoping

The script MUST run the existing extraction pipeline to produce:
- CalcDefs via `extractor.extract_calculation_definitions()`
- CalcUsages via `extract_calculation_usages(expand_templates=True)`
- Hierarchy data via `_extract_hierarchy_and_rewrite_bindings()`
- Design attributes via `extract_design_attributes()`
- Computed attributes via `_extract_and_filter_computed_attributes()`
- Scoped aggregation data via `_scope_aggregation_expressions()`
- Backtracking result via `DependencyBacktracker.find_required_modules()`
  (needed to compare prototype registry results against ground truth)

#### FR-2: Build Prototype OutputRegistry (Phase 1)

The script MUST build a Phase 1 registry following Section 12 of the design:

**CalcUsage outputs:**
```python
for usage in calc_usages:
    if usage.is_template:
        continue
    calc_def = calc_def_by_name.get(usage.calc_def_name)
    for output_attr in calc_def.output_attributes:
        channel = get_channel_name(usage.qualified_name, output_attr.name)
        keys = [
            f"{usage.instance_name}.{output_attr.name}",       # Key A
            f"{usage.qualified_name}__{output_attr.name}",      # Key B
        ]
        # EXPERIMENTAL: dotted hierarchy path (Issue 15 fix candidate)
        segments = usage.qualified_name.split("__")
        dotted_path = ".".join(segments[1:])  # drop design prefix
        key_c = f"{dotted_path}.{output_attr.name}"
        if key_c != keys[0]:  # only add if different from Key A
            keys.append(key_c)
        registry[key] = channel for each key
```

**Aggregation outputs:** (following existing backtracker index logic, lines 160-197)
```python
for agg in scoped_aggregation_data:
    channel = get_channel_name(agg.module_eqn, agg.expression.attribute_name)
    instance_parts = agg.instance_path.split("__")
    part_usage_name = instance_parts[-1]
    keys = [
        f"{part_usage_name}.{agg.expression.attribute_name}",             # Key D
        ".".join(instance_parts + [agg.expression.attribute_name]),       # Key E
    ]
    # Also register aliases from hierarchy extractor
    for alias_name in agg.expression.aliases:
        keys.append(f"{part_usage_name}.{alias_name}")
        keys.append(".".join(instance_parts + [alias_name]))
```

**FORMULA computed attribute outputs:**
```python
for ca in computed_attrs:
    if ca.classification != FORMULA or ca.compilability != FULLY_COMPILABLE:
        continue
    module_eqn = f"{ca.owning_part_qualified_name}__{ca.python_name}"
    channel = get_channel_name(module_eqn, ca.python_name)
    keys = [
        f"{ca.owning_part_name}.{ca.python_name}",  # Key F
    ]
```

For EACH registration, log: channel, all keys, CalcUsage type (concrete/virtual/agg/formula).

The script MUST report:
- Total channels registered
- Total keys registered
- Key collisions (same key -> different channels)

#### FR-3: Validate Phase 2 (CHAIN Alias Resolution)

For each CHAIN-type redefinition from `hierarchy_data.redefinitions`:
- Filter: skip BARE non-reference (no `.` in source_path -- CAS codes)
- Build the alias per design:
  ```python
  instance_parts = instance_path.split("__")
  alias_name = ".".join(instance_parts + [redef.attribute_name])
  canonical_name = ".".join(instance_parts + [redef.source_path.split(".")...])
  ```
  Wait -- `redef.source_path` is already dotted (`cost_model.total_cost`). So:
  ```python
  canonical_parts = instance_parts + redef.source_path.split(".")
  canonical_name = ".".join(canonical_parts)
  ```

- Attempt: `registry.get(canonical_name)`
- Report: success/failure, the canonical_name, the closest Phase 1 key if failure

The script MUST also test the Issue 15 fix: if canonical_name fails, try it
against the experimental Key C (dotted hierarchy path) and report whether the
fix would make it resolve.

#### FR-4: Validate Phase 3 (EXPOSE_PURE Alias Resolution)

For each EXPOSE_PURE computed attribute:
- Build canonical_name from `references` field (NOT expression_text):
  ```python
  instance_name = ca.references[1].name   # CalcUsage instance
  output_name = ca.references[0].name     # output attribute
  canonical_name = f"{instance_name}.{output_name}"
  ```
- Attempt: `registry.get(canonical_name)`
- Build scoped alias key: `f"{ca.owning_part_name}.{ca.python_name}"`
- Report: success/failure for canonical resolution + the scoped alias key

#### FR-5: Validate Phase 4 (Transitive Default Resolution)

For each design attribute with a dotted-path default_value:
- Filter: `"." in val and not float(val)`
- Attempt: `registry.get(attr.default_value)`
- Report: success/failure, the default_value, matched channel

#### FR-6: Validate Backtracker CHAIN Binding Resolution

For each CHAIN binding across all CalcUsages:
- Attempt: `registry.get(binding.source_path)`
- Compare against ground truth: `binding_resolutions[f"{usage.qn}|{param}"]`
- Report: match/mismatch with ground truth
- If mismatch: print both prototype and ground truth resolution

#### FR-7: Validate REFERENCE Secondary Resolution

For each REFERENCE binding that resolves to MODULE_OUTPUT in the ground truth:
- Extract leaf_name: `source_path.rsplit("::", 1)[-1].strip("'")`
- Try multiple parent_part candidates:
  - `segments[-2]` (immediate parent from CalcUsage QN)
  - `segments[1]` (design root part, second segment after design prefix)
  - ALL intermediate segments
- For each candidate: `registry.get(f"{candidate}.{leaf_name}")`
- Report: which candidate produces the correct result (matching ground truth)
- This empirically determines `_get_parent_part_for_usage()` logic

#### FR-8: Document instance_path Format

For each `ScopedAggregationData`:
- Print: `instance_path`, `module_eqn`, `expression.attribute_name`
- Print: `instance_path.split("__")` (the instance_parts)
- Print: the dotted form `".".join(instance_parts)`
- Print: whether any Phase 1 CalcUsage key starts with the dotted form

This empirically documents the `instance_path` format and its relationship to
CalcUsage qualification paths.

### Non-Functional Requirements

- **NFR-1:** Script follows existing spike conventions (shebang, docstring, `_helpers` import)
- **NFR-2:** Runnable via `uv run python scripts/spikes/spike_output_registry_e2e.py`
- **NFR-3:** Output is structured with clear section headers and tables per model
- **NFR-4:** Script MUST NOT modify any pipeline code
- **NFR-5:** Should complete in <60 seconds total (both models)

---

## Acceptance Criteria

### Core Functionality

- [ ] **AC-1:** Phase 1 registration completes for both models with all keys logged
- [ ] **AC-2:** Phase 2 validation reports success/failure rate for CHAIN alias resolution
      (solar_battery has 41 DOTTED CHAIN redefs per Spike 6)
- [ ] **AC-3:** Phase 3 validation reports success/failure for all EXPOSE_PURE aliases
      (e2e_attr_expr has `total_capex` EXPOSE_PURE per Spike 3)
- [ ] **AC-4:** Phase 4 validation reports success/failure for both transitive defaults
      (Spike 7: 2 total across both models)
- [ ] **AC-5:** CHAIN binding resolution matches ground truth for all CHAIN bindings
      (Spike 1: 8 DOTTED in solar_battery, 4 in e2e_attr_expr)
- [ ] **AC-6:** REFERENCE secondary resolution identifies the correct parent_part
      extraction for all 4 REFERENCE -> MODULE_OUTPUT cases (Spike 5)
- [ ] **AC-7:** instance_path format documented with exact separators and scope
- [ ] **AC-8:** Every Phase 2/3/4 failure has a "would-fix" key documented

### Quality & Integration

- [ ] Script runs without errors on both models
- [ ] Existing tests continue to pass (script doesn't touch pipeline code)
- [ ] Results directly resolve Issues 15, 16, 17, 20 from design_revision_comments_v3.md

---

## Related Artifacts

- **Design comments (v3):** `.project/reports/design_revision_comments_v3.md`
- **Revised design:** `.project/reports/08_algorithm_revised.md`
- **Prior spike results:** `.project/research/20260213_spike_results_syside_assumptions.md`
- **Prior spike results (iter 2):** `.project/research/20260213_spike_results_iteration2.md`
- **Prior spike spec:** `.project/active/syside-assumption-spikes/spec.md`
- **Backtracker source:** `src/sysml_codegen/analysis/dependency_backtracker.py`
- **Initialization source:** `src/sysml_codegen/generation/initialization.py`

---

**Next Steps:** Proceed to plan.
