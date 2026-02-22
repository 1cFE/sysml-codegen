# Spec: Iteration 2 OutputRegistry Design Spikes

**Status:** Complete
**Owner:** Reid Westwood
**Created:** 2026-02-13T18:39:20+00:00
**Complexity:** MEDIUM
**Branch:** cost-pattern

---

## Business Goals

### Why This Matters

Iteration 1 resolved 7 of 8 design comment issues via Spikes 1-4, grounding the
OutputRegistry design in empirical SysIDE behavior. Iteration 2 comments
(`design_revision_comments_v2.md`) identified 6 new issues -- 3 of which require
empirical data before the design can be finalized for implementation. Without
resolving these, the OutputRegistry's Phase 2 alias registration, Phase 4
transitive aliases, and SYSML_QN normalization are all unverifiable.

### Success Criteria

- [ ] Each spike question has a definitive, evidence-backed answer
- [ ] Answers are documented with exact values from real models
- [ ] Issues 9, 11, 12 from `design_revision_comments_v2.md` can be closed with data
- [ ] `08_algorithm_revised.md` can be updated with empirically grounded decisions
- [ ] Issues 10, 13, 14 (specification gaps) can be resolved using spike findings

### Priority

Blocks design finalization and all OutputRegistry implementation.

---

## Problem Statement

### Current State

The post-iteration-1 design makes assumptions about three data formats that have
never been empirically verified:

1. **`:>>` CHAIN redefinition RHS content.** The design builds ChannelAlias with
   `canonical_name` from the redefinition's `source_path` field. If `source_path`
   is a bare name (e.g., `"capital_cost"`), the OutputRegistry can't resolve it
   (bare names were eliminated from resolution in iteration 1). If it's a dotted
   path or SYSML_QN, it might resolve. We don't know which format it is.

2. **REFERENCE binding resolution outcomes.** The OutputRegistry has SYSML_QN
   normalization (`::` -> `__` + lowercase) for MODULE_OUTPUT resolution. But if
   REFERENCE bindings always resolve to ENTRY_POINT (never MODULE_OUTPUT), this
   normalization is dead code. If they sometimes resolve to MODULE_OUTPUT, the
   normalization is likely broken (quotes, spaces, casing mismatch with EQN format).

3. **DesignAttributeData.default_value for reference-typed attrs.** Phase 4
   transitive alias registration calls `registry.resolve(attr.default_value)`.
   Spike 3 showed that EXPOSE_PURE `expression_text` was raw AST text
   (`".(component_cost)"`), not a clean dotted path. If `default_value` has the
   same problem, Phase 4 is broken.

### Desired Outcome

Three diagnostic scripts that extract exact values from real SysML models, answering
each question definitively. Results feed directly into design updates and close
iteration 2 comment issues.

---

## Scope

### In Scope

- 3 standalone diagnostic scripts in `scripts/spikes/`
- Each loads real SysML models, extracts specific data, prints structured output
- A summary findings document at `.project/research/`
- Scripts are READ-ONLY -- no pipeline code modifications

### Out of Scope

- OutputRegistry implementation
- Any changes to the codegen pipeline
- Updating `08_algorithm_revised.md` (happens after spike results)
- Resolving Issues 10, 13, 14 (specification gaps -- no empirical data needed)

### Models to Test Against

| Model | Path | Why |
|-------|------|-----|
| solar_battery | `tests/fixtures/solar_battery_model/` | `:>>` CHAIN redefs, aggregation, templates |
| e2e_attr_expr | `~/1cfe/fusion-tea/models/tests/e2e_attr_expr/` | EXPOSE_PURE, concrete CalcUsages, design attrs |
| chain_spike | `tests/fixtures/chain_spike_model/` | Simple baseline -- no hierarchy |
| catf_mfe | `tests/fixtures/catf_mfe_model/` | Large model, many REFERENCE bindings |

---

## Requirements

### Functional Requirements

#### FR-1: Spike 5 -- REFERENCE Binding Resolution Outcomes

**Question:** Do REFERENCE bindings ever resolve to MODULE_OUTPUT, or always ENTRY_POINT?

**Design comment addressed:** Issue 11 (SYSML_QN normalization -- dead code or broken?)

The script MUST:
- Load all 4 models
- Run the full pipeline through `build_pipeline_context()` to get `BacktrackingResult`
- For each entry in `binding_resolutions`:
  - Find the original binding on the CalcUsage (by parsing the mapping key
    `"{usage_qn}|{param_name}"`)
  - Record: `binding_type`, `resolution_type`, `source_path`
- Build a cross-tabulation: binding_type x resolution_type
- For each REFERENCE binding that resolved to MODULE_OUTPUT (if any):
  - Print the full trace: source_path, resolved channel, which format matched
- For each REFERENCE binding that resolved to ENTRY_POINT:
  - Print: source_path, was it matched to a design attribute?

**Pass criteria:**
- Cross-tabulation for all 4 models
- Determine: is "REFERENCE -> MODULE_OUTPUT" a zero-occurrence scenario?
- If zero: SYSML_QN normalization in resolve() can be simplified/removed
- If nonzero: document the exact source_path and channel for each case

#### FR-2: Spike 6 -- `:>>` CHAIN Redefinition RHS Content

**Question:** What does the RHS of `:>>` CHAIN redefinitions contain? Bare name?
Dotted path? SYSML_QN? Raw AST text?

**Design comment addressed:** Issue 9 (CHAIN alias canonical_name is bare)

The script MUST:
- Load solar_battery and e2e_attr_expr models
- Run `extract_hierarchy_data(model)` to get `HierarchyExtractionResult`
- For each `RedefinitionData` where `redefinition_type == RedefinitionType.CHAIN`:
  - Print: `owning_part_qn`, `attribute_name`, `source_path`
  - Classify `source_path` format: BARE, DOTTED, SYSML_QN, AST_TEXT, NONE
  - If `source_path` has raw AST nodes, also print the AST type
- Also examine the raw AST for CHAIN redefinitions:
  - Access `expression_ast` if populated
  - Print `expression_text` if different from `source_path`
- For each CHAIN redefinition, determine:
  - Is `source_path` sufficient to build a ChannelAlias canonical_name?
  - Or do we need to reconstruct from AST/references like EXPOSE_PURE?

**Pass criteria:**
- Every `:>>` CHAIN source_path is classified
- Determine the reliable extraction method for canonical_name
- Determine whether scoping (adding instance path prefix) is needed

#### FR-3: Spike 7 -- DesignAttributeData.default_value for Path-Like Defaults

**Question:** For design attributes whose default_value looks like a reference
(not a numeric/boolean literal), what format does `default_value` have?

**Design comment addressed:** Issue 12 (Phase 4 transitive alias registration)

The script MUST:
- Load solar_battery and e2e_attr_expr models
- Extract design attributes via `extract_design_attributes()`
- For each `DesignAttributeData`:
  - Print: `name`, `parent_part`, `default_value`, `qualified_name`
  - Classify `default_value`: NUMERIC, BOOLEAN, STRING_LITERAL, DOTTED_PATH,
    SYSML_QN, AST_TEXT, NONE
- For path-like default_values (DOTTED_PATH or SYSML_QN):
  - Build a prototype output catalog (same as Spike 3)
  - Check: does `output_catalog.get(default_value)` succeed?
  - This tests whether Phase 4 registration would work with actual data
- Report: how many design attrs have transitive defaults?
  Which ones? What format?

**Pass criteria:**
- Every design attribute default_value is classified
- Determine: are "transitive defaults" identifiable by format?
- Determine: does `registry.resolve(default_value)` work with actual data?
- Propose filter criteria for Phase 4 registration

### Non-Functional Requirements

- **NFR-1:** Scripts MUST follow existing spike conventions (shebang, docstring, `_helpers.py`)
- **NFR-2:** Scripts MUST be independently runnable via `uv run python scripts/spikes/<name>.py`
- **NFR-3:** Output MUST be machine-parseable (consistent formatting)
- **NFR-4:** Scripts MUST NOT modify any pipeline code or data models
- **NFR-5:** Each spike SHOULD complete in <60 seconds per model

---

## Acceptance Criteria

### Core Functionality

- [ ] **AC-1:** Spike 5 produces binding_type x resolution_type cross-tabulation
  for all 4 models, determining whether REFERENCE -> MODULE_OUTPUT ever occurs
- [ ] **AC-2:** Spike 6 classifies every `:>>` CHAIN redefinition source_path format
  and identifies the reliable canonical_name extraction method
- [ ] **AC-3:** Spike 7 classifies every design attribute default_value and determines
  whether Phase 4 transitive aliases work with actual data
- [ ] **AC-4:** A summary research note documents findings with direct design implications

### Quality & Integration

- [ ] All scripts run without errors on the specified models
- [ ] Existing tests continue to pass (scripts don't touch pipeline code)
- [ ] Each finding directly maps to a design_revision_comments_v2.md issue

---

## Related Artifacts

- **Design comments v2:** `.project/reports/design_revision_comments_v2.md`
- **Revised design:** `.project/reports/08_algorithm_revised.md`
- **Iteration 1 spike results:** `.project/research/20260213_spike_results_syside_assumptions.md`
- **Iteration 1 spike spec:** `.project/active/syside-assumption-spikes/spec.md`
- **Plan:** `.project/active/iteration2-spikes/plan.md` (to be created)

---

**Next Steps:** Proceed to plan.
