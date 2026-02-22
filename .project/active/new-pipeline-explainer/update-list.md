# Update List: Pipeline Explainer HTML

**Purpose:** Catalog every delta between the explainer `design.md` (written at commit `59b29b0`) and the current codebase state (`edee000`). Organized by explainer section so implementation can apply updates incrementally.

**Commits since design.md:** 20 commits spanning refactors C23-C26, 7.1-7.7, X01, Bug-11, and docs D1-D6.

---

## 1. Global: Documentation References

The design.md references `.project/concepts/refactor-design-intent/` (27 documents) as the design source. That folder is now **ARCHIVED**. Canonical documentation is in `docs/architecture/`.

| design.md Reference | Update To |
|---------------------|-----------|
| `.project/concepts/refactor-design-intent/` (27 docs) | `docs/architecture/reference/` (27 docs, renumbered 00-26) |
| Individual ADR files (ADR-001 through ADR-008) | `docs/architecture/modeling-assumptions.md` (consolidated) or specific reference docs |
| No architecture overview existed | `docs/architecture/overview.md` now exists (canonical 7-step pipeline description) |
| No verification matrix existed | `docs/architecture/verification-matrix.md` — 204 REQs across 29 families, 192 PASS |

**Action:** Update the "Related Artifacts" section (design.md line 20) and any narrative text that points to concept docs.

---

## 2. Data Models Table (design.md lines 69-86)

### 2a. PipelineModule — 7 new metadata fields (C26: `441f566`)

The `PipelineModule` model in `resolution/models.py:160-190` gained metadata fields after the design was written. These don't affect pipeline wiring but are available for the explainer's module detail panels.

| New Field | Type | Source |
|-----------|------|--------|
| `calc_def_name` | `str \| None` | Name of source CalcDef |
| `calc_def_qualified_name` | `str \| None` | Full SysML qualified name |
| `doc_comment` | `str \| None` | Documentation from CalcDef |
| `calc_expressions` | `list[str] \| None` | Raw SysML calc expressions |
| `source_file` | `str \| None` | Path to source .sysml file |
| `source_line` | `int \| None` | Line number in source |
| `auto_impl_context` | `dict \| None` | Auto-implementation template context |

**Action:** Add these to the Data Models table (Resolution layer, PipelineModule row). Consider showing `calc_def_name` and `source_file` in Act 4's module detail panel.

### 2b. ModuleInput — 2 new fields (C26)

| New Field | Type | Source |
|-----------|------|--------|
| `description` | `str \| None` | From CalcDef input attribute |
| `default_value` | `float \| int \| str \| bool \| None` | From CalcDef default |

**Action:** Add to Data Models table. Consider showing `description` in Act 2 Step 5 data panels and Act 4 expanded module view.

### 2c. ModuleOutput — 3 new fields (C26)

| New Field | Type | Source |
|-----------|------|--------|
| `description` | `str \| None` | From CalcDef output attribute |
| `default_value` | `float \| int \| str \| bool \| None` | From CalcDef (note: stripped to `None` in generated schemas per Bug-11/REQ-OSR-05) |
| `unit` | `str \| None` | Physical unit annotation |

**Action:** Add to Data Models table. The `unit` field is especially useful for the explainer — show units alongside output channel names in module detail panels.

### 2d. New Data Model Row: PipelineContext

The orchestration refactor (7.1: `bd80342`) created `PipelineContext` as the orchestration-layer container. File: `orchestration/pipeline_context.py:59-105`.

Key fields: `extractor`, `calc_defs`, `calc_usages`, `design_attributes`, `group_deriver`, `backtracker`, `backtracking_result`, `computation_graph`, plus optional `compilation_results`, `computed_attributes`, `hierarchy_data`, `aggregation_expressions`, `channel_aliases`, `output_registry`.

**Action:** Add PipelineContext to the Data Models table under a new "Orchestration" layer. This is what `build_pipeline_context()` returns — useful for showing the full pipeline data flow.

---

## 3. Act 1: No Changes Required

Hierarchy diagram, "Big Question" animation, and part hierarchy data are unchanged. The solar battery model fixtures (`tests/fixtures/solar_battery_model/`) have not been modified.

---

## 4. Act 2: Pipeline Steps

### 4a. Pipeline Overview Diagram — Add Step 6.5

The actual pipeline has a sub-step the design omits:

| Step | Name | What |
|------|------|------|
| 6.5 | Compile Expressions | Compile CalcDef expressions to Python (`compile_calc_def()` loop in `pipeline_builder.py:536-576`) |

This happens between backtracking (Step 6) and graph building (Step 7). It produces `compilation_results: dict[str, CalcDefCompilationResult]` which determines `compilability` and `compiled_expression` on each PipelineModule.

**Action:** Add Step 6.5 to the pipeline overview strip as a sub-step below Step 6 (same pattern as 3.5, 4.5, 5.5). Update sidebar navigation. This is the step that decides whether a module gets auto-implemented or needs a handwritten stencil.

### 4b. Step 2: Build Registry — Reference 4-Phase Protocol

The design's Step 2 description (lines 445-468) is correct but can now reference the canonical documentation. The 4-phase build happens in `orchestration/output_registry_builder.py:34-220`.

**Action:** Add REQ-OR-01 through REQ-OR-08 references to callouts. Reference `docs/architecture/reference/10-output-registry.md` for the full typed registry design. Note the elimination of 5 ambiguous key formats (Key_A, Key_D, Key_E_full, Key_F, bare) — zero resolution hits across 6 production models.

### 4c. Step 3: Trace Dependencies — Actual Function Location

The backtracker is in `analysis/dependency_backtracker.py`. The design's DFS tree visualization (lines 473-511) is accurate.

**Action:** Add REQ-BT-01 through REQ-BT-08 references. Note that the backtracker uses type-directed dispatch: CHAIN bindings → scoped registry, REFERENCE bindings → SysML QN registry.

### 4d. Step 5: Build Modules — Confirm Pure Returns

Refactor 7.7 (`fd119ba`) confirmed the design's anticipated tuple-return pattern. All three factories now return `tuple[PipelineModule, dict[str, EntryPoint]]`:

- `_build_pipeline_module()` → `(module, {})` (CalcUsage never creates new EPs)
- `_build_computed_attr_module()` → `(module, new_eps)`
- `_build_aggregation_module()` → `(module, new_eps)`

Caller merges: `entry_points.update(new_eps)`.

**Action:** The design already shows this pattern (§4i, lines 579-631). Mark as CONFIRMED. Add note that CalcUsage factory always returns empty EP dict (all its EPs were classified in Step 4).

### 4e. Step 5.5: Build OutputRegistry — Actual Location

The 4-phase build function is now in `orchestration/output_registry_builder.py` (refactor 7.1), not in `resolution/`.

**Action:** Update any code-path references. The phase table (design lines 637-648) is accurate. Add Phase 1a/1b/1c sub-phases (the code separates Phase 1 into three loops: CalcUsage outputs, Aggregation outputs, FORMULA outputs).

### 4f. Step 6: Sort + Validate — Add Compilation Sub-Step

The design's Step 6 (lines 654-700) correctly describes topological sort + validation. But it should note Step 6.5 (expression compilation) as a sub-step that produces the `compilability` verdict and `compiled_expression` for each module.

**Action:** Add Step 6.5 content. Show how `compile_calc_def()` produces `CalcDefCompilationResult` with verdict (FULLY_COMPILABLE, PARTIALLY_COMPILABLE, MANUAL_REQUIRED) and compiled Python expression string. This feeds into `auto_impl_context` on PipelineModule.

### 4g. Step 7: Render — _from_graph() Generator Variants

Refactor C26 (`441f566`) created `_from_graph()` variants of every generator that work exclusively from `ComputationGraph` without requiring source extraction data:

| New Function | In | Purpose |
|-------------|-----|---------|
| `generate_teax_module_from_graph()` | `generation/modules.py` | Module wrapper from PipelineModule fields |
| `generate_multioutput_model_from_graph()` | `generation/schemas.py` | Schema from PipelineModule outputs |
| `generate_implementation_from_graph()` | `generation/stencils.py` | Stencil/auto-impl from PipelineModule |
| `generate_registry_from_graph()` | `generation/registry.py` | Registry from ComputationGraph.modules |

Refactor 7.6 (`6523521`) enforced the boundary: generation imports **zero** extraction/analysis classes. Verified by AST analysis test.

**Action:** Update Step 7 narrative to reference `_from_graph()` variants. Strengthen the "ComputationGraph as boundary" callout (§4k, lines 682-702) — it's now enforced by tests, not just convention. Reference REQ-PIPE-07.

### 4h. Step 7: Render — Auto-Implementation Dispatch

The `auto_impl_context` field on PipelineModule enables a new dispatch pattern:
- If `module.auto_impl_context` is populated → generate auto-implementation (no handwritten stencil needed)
- Otherwise → generate stub stencil for manual implementation

**Action:** Add a note to Step 7 showing this dispatch. It completes the story: "The pipeline doesn't just wire modules — for FULLY_COMPILABLE modules, it generates the implementation too."

---

## 5. Act 3: Why The Hard Parts Work

### 5a. Template Instantiation — No Changes Required

The virtual binding rewrite mechanism is unchanged. The design's 3-panel layout (§5a, lines 748-763) is accurate.

### 5b. Aggregation Decomposition — No Changes Required

SumTerm/SingletonTerm/LocalTerm terminology and the 4-tier visualization are accurate.

### 5c. Dual Resolution Architecture — Clarify 2-Path vs 3-Mechanism Framing

The architecture overview (`docs/architecture/overview.md`) describes **two** resolution paths:
- Path 1 (CalcUsage): Backtracker DFS
- Path 2 (FORMULA + Aggregation): `resolve_input()` with strategy chain

The design's Act 3c (lines 799-860) shows **three** mechanisms (Backtracker, Attribute Map, resolve_input). This is a more detailed decomposition of the same architecture — the overview groups FORMULA and Aggregation as "Path 2" since both are post-DFS, while the explainer correctly separates them because their resolution mechanics differ (attribute map vs. strategy chain).

**Action:** Add a framing note: "The architecture describes two resolution *paths* (DFS-integrated vs. post-DFS). Within the post-DFS path, FORMULA and Aggregation use distinct *mechanisms* — pre-computed attribute map vs. runtime strategy chain."

### 5d. Dual Resolution — Strategy B Removed

Refactor 7.4 (`ef7abc9`) removed Strategy B (Normalized Fallback) from both the input resolver and backtracker. This was dead code — the normalized `::` → dotted-key fallback had zero hits across all models.

The design already shows AGG_STRATEGIES as A, C, D (skipping B), which matches the post-removal state. No content change needed, but confirm the design doesn't reference Strategy B elsewhere.

**Action:** Verify no stale Strategy B references exist in the design. Add a note to the strategy chain detail: "Strategy B (Normalized Fallback) was removed — empirical analysis across 6 models showed zero resolution hits."

### 5e. Dual Resolution — Actual Function Names

The design references `resolve_input(ref, ctx, strategies)` (line 845). Verify this matches the actual function signature in `resolution/input_resolver.py`. The current source research found `_resolve_aggregation_input_channel()` in `graph_builder.py:882-993` — this may be a separate function that queries the registry directly rather than going through the strategy chain.

**Action:** Verify whether `resolve_input()` in `input_resolver.py` is still the primary API, or whether aggregation resolution has been inlined into `_resolve_aggregation_input_channel()`. Update Act 3c accordingly.

---

## 6. Act 4: Full Graph

### 6a. DAG Diagram — Module Count Still 35

No changes to module count or topology. The solar battery model produces the same 35 modules (14 F1 + 1 F2 + 20 F3).

### 6b. Module Detail Panel — Show New Fields

With C26's PipelineModule expansion, the module detail panel (design lines 893-899) can now show:

| Field | Value for Traced Module |
|-------|------------------------|
| `calc_def_name` | `"PVModuleCostCalc"` |
| `doc_comment` | (from CalcDef doc comment) |
| `source_file` | `"models/library/solar_battery_library.sysml"` |
| `source_line` | (line number) |
| `compilability` | `FULLY_COMPILABLE` |
| Input descriptions | From CalcDef input_attributes |
| Output units | From CalcDef output_attributes |

**Action:** Add these fields to the module detail panel specification. Show `source_file:source_line` as a clickable reference. Show `description` and `unit` alongside input/output ports.

### 6c. Generated Code Samples — Bug-11 Fix

Bug-11 (`4c214d1`) fixed output schema generation: output fields in Pydantic `MultiOutput` schemas no longer render with `Field(default=0.0)`. Per REQ-OSR-05, output fields are always required (no defaults).

**Action:** If the generated code samples in Act 4 (§6b, lines 902-906) show MultiOutput schemas, ensure they reflect the fix: no `default=` on output fields.

---

## 7. MODEL_DATA Structure (design.md lines 908-1150)

### 7a. pipelineTrace.step5_module — Add New Fields

The traced module's Step 5 data (lines 1013-1033) should include the new PipelineModule fields:

```js
step5_module: {
  // ... existing fields ...
  calc_def_name: "PVModuleCostCalc",                              // NEW
  calc_def_qualified_name: "SolarBatteryLibrary::PVModuleCostCalc", // NEW
  doc_comment: "...",                                               // NEW
  source_file: "models/library/solar_battery_library.sysml",       // NEW
  source_line: 42,                                                  // NEW
  auto_impl_context: { /* execution_steps, output_expressions */ }, // NEW
  inputs: [
    { param: "wattage", source_type: "entry_point", ...,
      description: "Peak wattage per module",  // NEW
      default_value: null },                   // NEW
    // ...
  ],
  outputs: [
    { field_name: "root", channel: "...",
      description: "Total module cost",  // NEW
      unit: "USD" }                      // NEW
  ]
}
```

### 7b. modules[] — Add Metadata to DAG Module Entries

Each module in the `modules[]` array (lines 1036-1055) should include the new metadata fields for the module detail panel:

```js
{
  // ... existing fields ...
  calcDefName: "PVModuleCostCalc",     // NEW
  docComment: "...",                    // NEW
  sourceFile: "models/library/...",     // NEW
  sourceLine: 42,                       // NEW
  compilability: "FULLY_COMPILABLE",    // (existed but not shown in MODEL_DATA)
}
```

### 7c. Add pipelineTrace.step65_compile

New step data for the expression compilation sub-step:

```js
step65_compile: {
  tracedModule: {
    calcDef: "PVModuleCostCalc",
    verdict: "FULLY_COMPILABLE",
    compiledExpression: "wattage * cost_per_watt * (1 + fab_factor) * (1 + install_factor)",
    outputExpressions: [
      { name: "material_cost", expression: "wattage * cost_per_watt" },
      { name: "total_cost", expression: "material_cost * (1 + fab_factor) * (1 + install_factor)" }
    ]
  },
  summary: {
    fullyCompilable: 12,
    partiallyCompilable: 2,
    manualRequired: 0,
    unknown: 21
  }
}
```

---

## 8. Package Structure Reference

### 8a. New orchestration/ Package (7.1)

The design's file architecture (§1, lines 91-146) shows JS class organization but doesn't list the Python package structure. The architecture overview in `docs/architecture/overview.md` now provides the canonical package layout:

```
sysml_codegen/
  orchestration/           NEW (refactor 7.1)
    pipeline_builder.py    build_pipeline_context(): 7-step coordination
    output_registry_builder.py  build_output_registry(): 4-phase protocol
    pipeline_context.py    PipelineContext dataclass
  core/                    Centralized (refactor 7.3)
    identifier_types.py    SysMLQN, EQN, PQN, CanonicalChannel, ScopedKey
    output_registry.py     OutputRegistry class
    qualified_names.py     Name construction helpers
  generation/              Boundary-enforced (refactor 7.6)
    type_mapping.py        NEW (refactor X01) — consolidated SysML→Python mapping
```

**Action:** If the explainer includes a "codebase map" or package structure visualization, use this layout. It's authoritative.

### 8b. Naming Shims Deleted (7.3)

`analysis/qualified_names.py` and `resolution/identifier_types.py` shims were deleted. All imports now go to `core/`. No impact on explainer content, but any code references should use `core/` paths.

---

## 9. Verification Matrix Integration

### 9a. REQ IDs for Narrative Callouts

The verification matrix (`docs/architecture/verification-matrix.md`) provides specific REQ IDs that the explainer's callouts can reference. Key mappings:

| Explainer Section | Callout Topic | REQ IDs |
|-------------------|---------------|---------|
| Step 2 (Registry) | Typed registry prevents ambiguity | REQ-OR-01, REQ-OR-05, REQ-OR-08 |
| Step 2 (Registry) | Phase ordering enforced | REQ-OR-04 |
| Step 3 (Trace) | DFS + resolution inseparable | REQ-DRA-01 |
| Step 3.5 (Rewrite) | Must precede Step 4 | REQ-ORCH-02 |
| Step 4 (Classify) | Three EP types, precedence | REQ-EPC-01 through REQ-EPC-03 |
| Step 4.5 (Computed) | Must precede Step 5 | REQ-ORCH-03 |
| Step 5 (Factories) | Pure return, no mutation | REQ-MF-01 |
| Step 5 (Factories) | Single-output uses "root" | REQ-MF-08 |
| Step 5.5 (Registry Build) | Must precede Step 6 | REQ-ORCH-04 |
| Step 6 (Sort) | Kahn's O(V+E) | REQ-GA-07 |
| Step 6 (Sort) | Self-reference guard | REQ-GA-04, REQ-IR-03 |
| Step 6 (Validate) | Channel validation | REQ-GA-03 |
| Step 6 boundary | ComputationGraph only | REQ-PIPE-07 |
| Act 3c (Dual Res) | Both paths same wiring | REQ-DRA-04 |
| Act 3c (Dual Res) | Shared typed registries | REQ-DRA-03 |
| Act 3c (Strategies) | Strategy chain order | REQ-IR-05 |
| Act 3c (Strategies) | Self-reference guard | REQ-IR-03 |

**Action:** Add REQ IDs as small badges or footnotes in the relevant callout boxes. These provide traceability to the verification matrix for readers who want to verify claims.

---

## 10. Summary: Priority-Ordered Update List

### Must-Do (affects correctness of explainer content)

1. **Add Step 6.5** (expression compilation) to pipeline overview, sidebar nav, and step sections
2. **Update documentation references** — archived concept folder → `docs/architecture/`
3. **Verify `resolve_input()` vs `_resolve_aggregation_input_channel()`** — confirm which is the actual API for aggregation resolution in Act 3c

### Should-Do (improves accuracy and completeness)

4. **Add PipelineModule metadata fields** to Data Models table and MODEL_DATA
5. **Add ModuleInput/ModuleOutput new fields** to Data Models table and data panels
6. **Add PipelineContext** to Data Models table (Orchestration layer)
7. **Add `_from_graph()` generator variants** to Step 7 narrative
8. **Add `auto_impl_context` dispatch** to Step 7 (auto-impl vs stencil)
9. **Strengthen ComputationGraph boundary callout** — now test-enforced (REQ-PIPE-07)
10. **Confirm factory tuple-return pattern** — now implemented, not just anticipated
11. **Add Phase 1a/1b/1c sub-phases** to Step 5.5 registry build table

### Nice-to-Have (enriches the explainer)

12. **Add REQ ID badges** to callout boxes (traceability to verification matrix)
13. **Show module metadata** in Act 4 detail panel (calc_def_name, source_file, units)
14. **Note Strategy B removal** in dual resolution strategy chain
15. **Add 2-path vs 3-mechanism framing note** in Act 3c intro
16. **Fix output schema display** if showing MultiOutput (no defaults per Bug-11)
17. **Reference `type_mapping.py`** consolidation in Step 7 (SysML→Python type map)

---

**Next Step:** Apply these updates to the design.md before beginning implementation, or treat this list as a diff-spec that the implementer applies while building each section.
