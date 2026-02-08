# Spec: Pipeline Integration -- CalcDef Expression Compilation

**Status:** Implementation Complete
**Owner:** Reid Westwood
**Created:** 2026-02-07 16:11 UTC
**Complexity:** HIGH
**Branch:** cost-pattern
**Epic:** EXPR-CODEGEN Item 4

---

## Business Goals

### Why This Matters

The expression compiler module (Item 3) can compile SysML expression ASTs into executable Python code, but it isn't wired into the codegen pipeline. Every generated `_impl.py` still contains `raise NotImplementedError(...)` stubs, even for CalcDefs whose math is fully expressed in SysML. This forces manual authoring of implementations that could be auto-generated.

This integration is the critical step that makes Items 1-3 pay off. Without it, the expression compiler is an isolated library with no user-visible effect.

### Success Criteria

- [ ] Running codegen produces auto-implemented `_impl.py` files for compilable CalcDefs
- [ ] Non-compilable CalcDefs still get proper `NotImplementedError` stubs (no regression)
- [ ] Codegen on chain_spike model produces `_impl.py` with actual code for all 3 CalcDefs
- [ ] All existing tests pass with zero regressions
- [ ] Hand-edited auto-impl files are preserved on regeneration (signature match)

### Priority

P1 -- This is the fourth of five sequential items in the EXPR-CODEGEN epic. Item 5 (E2E Validation) depends on this being complete.

---

## Problem Statement

### Current State

- `stencils.py` unconditionally generates `NotImplementedError` stubs via `implementation_stencil.py.jinja2`
- `CalculationDefinitionData` stores expressions as text strings (`calc_expressions: list[str]`) but not as compilable AST nodes
- `PipelineModule` has no `compilability` field -- the resolution layer is unaware of expression compilation
- `PipelineContext` has no `compilation_results` -- compilation has no place in the pipeline
- `usage_extractor._extract_single_binding()` drops `OperatorExpression` bindings to `BindingType.UNBOUND` (known bug)
- `extractor._extract_expression_text()` is a legacy text-only function that doesn't use the shared `expression_utils.py`

### Desired Outcome

- The pipeline has an explicit compilation step (Step 6.5) between backtracking and graph building
- Compilable CalcDefs get auto-generated `_impl.py` with actual Python computation code
- Non-compilable CalcDefs get stubs with accurate `MANUAL_REQUIRED` reasons
- The `OperatorExpression` binding bug is fixed
- Expression text extraction uses the shared `expression_utils.py` utilities

---

## Scope

### In Scope

1. **Extraction layer** (`extraction/`)
   - Add `output_expression_asts: dict[str, Any]` field to `CalculationDefinitionData`
   - Modify `extractor._extract_calculation_definition()` to capture raw SysIDE AST nodes for each output attribute
   - Replace `_extract_expression_text()` with calls to `expression_utils` for `calc_expressions` text population
   - Fix `usage_extractor._extract_single_binding()`: classify `OperatorExpression` as `BindingType.EXPRESSION` and store raw AST on `BindingInfo`

2. **Pipeline orchestration** (`generation/initialization.py`)
   - Add **Step 6.5** to `build_pipeline_context()`: after backtracking (Step 6), before graph building (Step 7)
   - Step 6.5 calls expression compiler to classify and compile all CalcDefs
   - Add `compilation_results: dict[str, CalcDefCompilationResult]` to `PipelineContext`
   - Pass `compilation_results` to `build_computation_graph()`

3. **Resolution layer** (`resolution/`)
   - Add `compilability: Compilability = Compilability.UNKNOWN` to `PipelineModule`
   - `build_computation_graph()` receives `compilation_results` and sets each module's `compilability` from the corresponding `CalcDefCompilationResult.overall_compilability`
   - `compiled_expressions` are NOT added to `PipelineModule` -- expression strings stay on `CalcDefCompilationResult` in `PipelineContext`

4. **Generation layer** (`generation/`)
   - New template `templates/auto_implementation.py.jinja2` for compilable CalcDefs
   - Modify `stencils.py` to accept `compilation_results` and select template based on compilability
   - Auto-generated impls include `AUTO_IMPLEMENTED = True` sentinel for human readability
   - Generator looks up `CalcDefCompilationResult.output_results` for expression strings and `execution_order` for code emission ordering

5. **Preservation interaction** (`generation/preservation.py`)
   - Verify existing signature-based regeneration handles auto-impl lifecycle:
     - auto-gen -> hand-edit -> re-gen: preserves user edit (signature match)
     - auto-gen -> SysML input change -> re-gen: backs up and regenerates (signature mismatch)

### Out of Scope

- Computed Attribute modules (Phase 2)
- Inline expressions in module wrappers (Computed Attribute archetype)
- Synthetic CalcUsage generation from attribute expressions (Phase 2)
- Backtracker changes
- Cost pattern / template instantiation (separate feature)
- End-to-end validation on real models (Item 5)
- CI/CD integration
- Performance benchmarking

### Edge Cases & Considerations

- **Missing ASTs**: CalcDefs where SysIDE doesn't populate `feature_value_expression` on outputs should default to `Compilability.UNKNOWN` and get stub templates
- **Partially compilable CalcDefs**: CalcDefs classified `PARTIALLY_COMPILABLE` (some outputs have ASTs, others don't) -- design must decide whether to auto-implement the compilable outputs and stub the rest, or stub the entire CalcDef
- **`_extract_expression_text()` replacement**: Must not break existing `calc_expressions` text output -- the text strings are used for traceability comments in generated code
- **`OperatorExpression` fix scope**: The fix classifies `OperatorExpression` as `BindingType.EXPRESSION` and stores the raw AST. This is a Phase 1 bug fix; Phase 2 will use the stored AST for inline computation
- **Preservation lifecycle**: Auto-generated files with `AUTO_IMPLEMENTED = True` must behave identically to hand-written stubs for preservation purposes -- signature comparison only, not sentinel inspection
- **Undeclared intermediates**: The expression compiler handles undeclared CalcDef members as local variables in function bodies (discovered in Item 2 spike). The auto-impl template must emit these in topological order before dependent outputs

---

## Requirements

### Functional Requirements

> Requirements below are from the epic definition unless marked [INFERRED] or [FROM INVESTIGATION]

1. **FR-1**: `CalculationDefinitionData` MUST have an `output_expression_asts: dict[str, Any]` field mapping output attribute names to their raw SysIDE AST nodes

2. **FR-2**: `extractor._extract_calculation_definition()` MUST capture raw AST nodes from `feature_value_expression` for each output attribute and populate `output_expression_asts`

3. **FR-3**: `_extract_expression_text()` MUST be replaced with calls to `expression_utils.py` for populating `calc_expressions` text strings

4. **FR-4**: `usage_extractor._extract_single_binding()` MUST classify `OperatorExpression` bindings as `BindingType.EXPRESSION` (not `UNBOUND`) and store the raw AST on `BindingInfo`

5. **FR-5**: `build_pipeline_context()` MUST include a Step 6.5 that compiles expressions after backtracking (Step 6) and before graph building (Step 7)

6. **FR-6**: `PipelineContext` MUST carry `compilation_results: dict[str, CalcDefCompilationResult]` keyed by CalcDef name

7. **FR-7**: `PipelineModule` MUST have a `compilability: Compilability` field defaulting to `Compilability.UNKNOWN`

8. **FR-8**: `build_computation_graph()` MUST receive `compilation_results` and set each module's `compilability` from the corresponding `CalcDefCompilationResult.overall_compilability`

9. **FR-9**: `stencils.py` MUST select the auto-implementation template for `FULLY_COMPILABLE` CalcDefs and the stub template for `MANUAL_REQUIRED` / `UNKNOWN` CalcDefs

10. **FR-10**: A new `auto_implementation.py.jinja2` template MUST generate syntactically valid Python with actual computation code, `AUTO_IMPLEMENTED = True` sentinel, and proper execution ordering for undeclared intermediates

11. **FR-11**: `compiled_expressions` MUST NOT be added to `PipelineModule` -- expression strings live on `CalcDefCompilationResult` in `PipelineContext`, accessed by the generator directly

12. **FR-12**: [INFERRED] `PARTIALLY_COMPILABLE` CalcDefs SHOULD fall through to stub generation (conservative approach; auto-implementing partial CalcDefs is deferred)

13. **FR-13**: [FROM INVESTIGATION] `preservation.py` MUST correctly handle auto-implemented files using existing signature comparison -- no changes to preservation logic expected, but verification is required

---

## Acceptance Criteria

### Core Functionality

- [ ] `CalculationDefinitionData` has `output_expression_asts` field populated during extraction
- [ ] `PipelineContext` has `compilation_results` populated by Step 6.5
- [ ] `PipelineModule` has `compilability` enum field set from compilation results
- [ ] Step 6.5 exists in `build_pipeline_context()` between Steps 6 and 7
- [ ] Codegen on chain_spike model produces `_impl.py` with actual code for all 3 CalcDefs
- [ ] `usage_extractor._extract_single_binding()` classifies `OperatorExpression` as `BindingType.EXPRESSION`
- [ ] Auto-impl template produces syntactically valid Python with `AUTO_IMPLEMENTED = True` sentinel
- [ ] Stub template still used for `MANUAL_REQUIRED` and `UNKNOWN` CalcDefs
- [ ] `_extract_expression_text()` replaced by `expression_utils` calls; `calc_expressions` text output unchanged

### Quality & Integration

- [ ] All existing tests pass with zero regressions
- [ ] `preservation.py` correctly preserves hand-edited auto-impl files on regeneration
- [ ] `uv run mypy src/` passes on all modified files
- [ ] `uv run ruff check src/` passes on all modified files
- [ ] New integration tests verify auto-impl generation for chain_spike CalcDefs

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_expression_aware_codegen.md` (Item 4)
- **Concept:** `.project/concepts/expression-aware-codegen.md`
- **Expression Compiler:** `src/sysml_codegen/extraction/expression_compiler.py` (Item 3 deliverable)
- **Expression Utils:** `src/sysml_codegen/extraction/expression_utils.py` (Item 3 deliverable)
- **Spike Reports:** `.project/active/expr-spike-ast/report.md`, `.project/active/expr-spike-compile/report.md`
- **Design:** `.project/active/expr-pipeline-integration/design.md` (to be created)

### Files Modified (Expected)

| File | Change |
|------|--------|
| `extraction/data_models.py` | Add `output_expression_asts` to `CalculationDefinitionData` |
| `extraction/extractor.py` | Capture raw ASTs; replace `_extract_expression_text()` |
| `extraction/usage_extractor.py` | Fix `OperatorExpression` → `BindingType.EXPRESSION` |
| `resolution/models.py` | Add `compilability` field to `PipelineModule` |
| `resolution/graph_builder.py` | Accept `compilation_results`, set module compilability |
| `generation/initialization.py` | Add Step 6.5, add `compilation_results` to `PipelineContext` |
| `generation/stencils.py` | Accept `compilation_results`, conditional template selection |
| `templates/auto_implementation.py.jinja2` | **New** -- auto-implementation template |

---

**Next Steps:** After approval, proceed to `/_my_design`
