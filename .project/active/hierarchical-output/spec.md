# Spec: Hierarchical Pipeline Output

**Status:** Draft
**Owner:** Reid Westwood
**Created:** 2026-02-22 16:12:01 UTC
**Complexity:** MEDIUM
**Branch:** TBD

---

## Business Goals

### Why This Matters

Pipeline outputs are currently flat — each channel produces a single `.json` file with a long `__`-delimited name, and reading results requires either scanning 15+ individual files or running a post-hoc `combine_results.py` script that merges them into a flat dictionary. Neither representation reflects the hierarchical structure the user designed in their SysML model.

The `__` separators in channel names already encode a part hierarchy (e.g., `E2EAttrExprDesign__e2e_plant__component_cost__fab_cost`). The output should leverage this structure so results are naturally organized and readable.

### Success Criteria

- [ ] Pipeline results are available as a single structured JSON that reflects the SysML part hierarchy
- [ ] A user can open one file and see results grouped by their logical subsystem/component
- [ ] The external `combine_results.py` workaround is no longer needed

### Priority

Quality-of-life improvement for pipeline output readability. Not blocking other work.

---

## Problem Statement

### Current State

The TEAx exit point writes one `.json` file per output channel, each containing a single scalar value. File names are flat `__`-delimited qualified names:

```
E2EAttrExprDesign__e2e_plant__component_cost__fab_cost.json    -> 2250.0
E2EAttrExprDesign__e2e_plant__component_cost__total_cost.json  -> 8750.0
E2EAttrExprDesign__e2e_plant__lcoe__lcoe.json                  -> 18.29
...
```

A `combine_results.py` script in `fusion-tea` works around this by merging all files into a single flat dictionary, but the result is still not hierarchical:

```json
{
  "E2EAttrExprDesign__e2e_plant__component_cost__fab_cost": 2250.0,
  "E2EAttrExprDesign__e2e_plant__component_cost__total_cost": 8750.0,
  "E2EAttrExprDesign__e2e_plant__lcoe__lcoe": 18.29
}
```

### Desired Outcome

A single structured JSON output where `__`-separated channel name segments become nested JSON keys, reflecting the SysML part hierarchy. For example (exact structure to be settled during design):

```json
{
  "e2e_plant": {
    "component_cost": {
      "fab_cost": 2250.0,
      "total_cost": 8750.0
    },
    "lcoe": 18.29
  }
}
```

---

## Scope

### In Scope

- Generating a hierarchical JSON representation of pipeline exit point outputs
- Using the `__`-separated channel name segments as the basis for nesting
- Producing this as part of the generated pipeline (not a post-hoc script)

### Out of Scope

- Changing how TEAx internally writes per-channel files
- Changing the pipeline execution model
- Removing the existing per-channel `.json` files (those MAY continue to exist)
- Changes to pipeline input structure

### Edge Cases & Considerations

- Channels where a name segment is both a leaf value and an intermediate grouping node (to be addressed in design)
- How deeply to nest vs. where to stop (e.g., should the design-part prefix be stripped or retained — to be addressed in design)
- Pipelines with outputs from multiple unrelated part hierarchies

---

## Requirements

### Functional Requirements

1. **FR-1**: The pipeline MUST produce a single structured JSON file containing all exit point output values
2. **FR-2**: The JSON structure MUST use nesting derived from the `__`-separated segments in channel names
3. **FR-3**: The structured output MUST be generated as part of the code-gen pipeline, not require a separate post-processing step
4. **FR-4**: Leaf values in the JSON MUST contain the computed result values (scalars, as currently produced)

### Non-Functional Requirements

- The structured output SHOULD be human-readable (indented JSON)

---

## Acceptance Criteria

### Core Functionality

- [ ] Running a generated pipeline produces a hierarchical JSON output file
- [ ] The nesting reflects the part hierarchy encoded in channel names
- [ ] The output is generated automatically — no manual post-processing step required
- [ ] All exit point channel values are present in the structured output

### Quality & Integration

- [ ] Existing tests continue to pass
- [ ] Existing per-channel output files are not broken

---

## Design Decisions Deferred

The following questions are noted here and MUST be resolved during design:

- **Prefix stripping**: Should the design-part prefix (e.g., `E2EAttrExprDesign`) be stripped from the hierarchy, starting at `e2e_plant`? Or retained?
- **Leaf-node naming**: When a channel name ends with a repeated segment (e.g., `lcoe__lcoe`), should the output collapse to a single key?
- **Output file location and name**: Where the structured JSON lives relative to the run output directory
- **Generation mechanism**: Whether this is a generated aggregator module, a template-emitted script, or another approach

---

## Related Artifacts

- **Current workaround:** `fusion-tea/scripts/combine_results.py`
- **Example outputs:** `fusion-tea/generated/e2e_attr_expr_v3/outputs/`
- **Design:** `.project/active/hierarchical-output/design.md` (to be created)

---

**Next Steps:** After approval, proceed to `/_my_design`
