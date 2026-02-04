# Epic: Expression-Aware Code Generation

**Epic ID**: EXPR-CODEGEN
**Status**: In Progress (Items 1-2 complete, Item 3 next)
**Priority**: P1
**Created**: 2026-02-03
**Estimated Effort**: ~8.5-10.5 days

---

## Executive Summary

Transform codegen from generating `NotImplementedError` stubs to generating **executable calculation code** for CalcDefs whose math is fully expressed in SysML. This eliminates the manual `_impl.py` authoring bottleneck for the majority of generated modules and lays the foundation for Phase 2 (attribute-level expression capture).

**Critical Success Factor**: Running codegen on a real model (solar_battery) auto-implements >=10 of 15 CalcDefs, with outputs matching handwritten implementations within `1e-10` tolerance.

---

## Why This Epic?

**Current State**:
- Every generated `_impl.py` contains `raise NotImplementedError(...)` -- the "GAP" comment in every module wrapper acknowledges this
- SysML expressions ARE extracted as text strings (`calc_expressions: list[str]`) but never compiled to executable Python
- Expression reconstruction code exists in 3 places (`extractor._extract_expression_text`, `constraint_extractor._reconstruct_expression`, `agentic_mbse.sysml.expression`) but none produce executable Python
- `BindingType.EXPRESSION` exists in the enum but is never classified in `usage_extractor._extract_single_binding()` -- falls through to `UNBOUND`
- Modelers must create full CalcDef+CalcUsage+module+impl for every arithmetic formula, including trivial ones like `volume = pi * r^2 * h`

**Future State**:
- CalcDefs with fully-resolvable expressions get auto-generated `_impl.py` with actual computation code
- Non-compilable CalcDefs still get proper `NotImplementedError` stubs (no regression)
- `IMPLEMENTATION_BACKLOG.md` shrinks dramatically (only lists genuinely manual work)
- Expression reconstruction code is consolidated (one path for SysML text display, one path for Python compilation)
- Foundation exists for Phase 2: attribute-level expressions without CalcDef overhead

---

## Success Criteria

- [ ] Codegen on chain_spike model produces `_impl.py` files with actual code for all 3 CalcDefs
- [ ] Codegen on solar_battery model auto-implements >=10 of 15 CalcDefs
- [ ] Auto-implemented code produces outputs matching handwritten implementations within `1e-10` tolerance
- [ ] Non-compilable CalcDefs still get proper `NotImplementedError` stubs
- [ ] All existing tests pass with zero regressions
- [ ] `Compilability` enum and `ExpressionNodeType` enum defined (not bare strings); `UNKNOWN` value included as default-before-compilation state
- [ ] Expression reconstruction consolidated: `extractor._extract_expression_text()` no longer called for CalcDef compilation; Python code generation uses `expression_compiler` exclusively; shared AST-to-text logic extracted into `expression_utils.py`
- [ ] Compilation runs as explicit Step 6.5 in `build_pipeline_context()`, between backtracking (Step 6) and graph building (Step 7)
- [ ] `compiled_expressions` carried on `CalcDefCompilationResult` via `PipelineContext`, NOT on `PipelineModule`
- [ ] `OperatorExpression` fallthrough in `usage_extractor._extract_single_binding()` fixed to classify as `BindingType.EXPRESSION`

---

## Backlog Items

### Item 1: Spike -- SysIDE Expression AST Extraction & Reference Resolution ✅

**Status**: Complete
**Type**: Research
**Dependencies**: None

**Objective**: Prove (or disprove) that we can extract expression ASTs from CalcDef outputs and resolve all feature references to declared inputs or sibling outputs, using real SysML models.

**Result**: **GO.** Tested across 4 model suites (chain_spike, sample_model, solar_battery, CATF). 95.8% AST coverage (92/96 outputs; 100% on fixtures, 86.7% on CATF). 98.6% reference resolution (212/215 refs; 3 unresolvable in CATF are undeclared intermediates -- a scoping adjustment for the compiler, not an architectural flaw). Node types limited to 3 (`OperatorExpression`, `FeatureReferenceExpression`, `LiteralRational`). Operator set is 5: `+`, `-`, `*`, `/`, `**`. Concept's Pattern C (`**` in CRF formula) confirmed. Zero cross-check mismatches, zero std_lib filtering.

**Carry-forward to Item 2**: The 3 unresolvable CATF refs (`thermal_load_cryo`, `pump_power_per_unit`, `thermal_load`) are same-CalcDef members not classified as input or output. The compiler's reference resolution needs to handle undeclared CalcDef members beyond `input_attributes`/`output_attributes`.

**Report**: [`.project/active/expr-spike-ast/report.md`](.project/active/expr-spike-ast/report.md)

---

### Item 2: Spike -- Expression Compilation & Compilability Classification ✅

**Status**: Complete
**Type**: Research
**Effort**: 1 day (spec 1h, design 0h, plan 0h, execute 5-6h)
**Dependencies**: Item 1 (needs AST findings to know what node types to handle)

**Objective**: Prove that we can compile SysIDE expression ASTs into syntactically valid, semantically correct Python, and that the compilability classifier's boundaries match reality.

**Result**: **GO.** Tested across 4 model suites (chain_spike, sample_model, solar_battery, CATF). 96.1% compilation rate (98/102 outputs including 6 discovered undeclared intermediates). 5/5 ground truth CalcDefs match handwritten implementations at exact 0.00e+00 relative error. Zero false positives in classifier (0/44). All 5 operators validated (`+`, `-`, `*`, `/`, `**`). Topological ordering correct for all multi-output CalcDefs including undeclared intermediate chains.

Key findings:
- 42/44 CalcDefs classified FULLY_COMPILABLE, 2 PARTIALLY_COMPILABLE (PlasmaConfinement, TritiumBreedingRatio -- missing ASTs on physics outputs)
- 3 CATF undeclared intermediates (thermal_load_cryo, pump_power_per_unit, thermal_load) fully resolved via extended resolution -- discovered, compiled, and emitted as local variables in function bodies
- MagnetCryogenicLoad required 4 undeclared intermediates emitted before its single declared output
- LiteralRational.value is Python float (no string conversion needed)
- SysIDE represents n-ary expressions as multi-operand OperatorExpression nodes (not nested binary trees); left-fold compilation produces correct parenthesized Python

**Caveats**:
- 37/42 FULLY_COMPILABLE verdicts are syntax-validated only (no ground truth). 5 are semantically validated.
- Pattern B (multi-step intermediate) has zero runtime ground truth -- all 10 cost CalcDef handwritten impls are NotImplementedError stubs. Item 5 (E2E validation) should prioritize executing Pattern B.

**Carry-forward to Item 3**:
- Undeclared intermediates require end-to-end handling: reference resolution AND code emission (extract expression, compile, emit as local variable before dependent outputs, exclude from return statement)
- `INTERMEDIATE_REF` definition should expand to include undeclared same-CalcDef members
- Include defensive unary negation handling (not encountered but trivial to implement)

**Report**: [`.project/active/expr-spike-compile/report.md`](.project/active/expr-spike-compile/report.md)

**Deliverables**:
- `scripts/spike_compile_expressions.py`
- `scripts/spike_classify_compilability.py`
- `.project/active/expr-spike-compile/spec.md`
- `.project/active/expr-spike-compile/report.md`

---

### Item 3: Expression Compiler Module

**Type**: Implementation
**Effort**: 1.5 days (spec 2h, design 2h, plan 1h, execute 6-8h)
**Dependencies**: Item 2 (needs validated compilation logic and operator mapping)

**Objective**: Build the `expression_compiler.py` module with clean data models, compilation logic, and comprehensive unit tests -- all independent of the pipeline.

**Current State**:
- ✅ Spike scripts provide validated compilation logic and operator mapping
- ✅ `constraint_extractor._reconstruct_expression()` provides AST traversal patterns to draw from
- ❌ No `ExpressionAST` intermediate representation exists
- ❌ No `CompilationResult` data model exists
- ❌ No `Compilability` enum exists (design review: must be enum, not bare string)
- ❌ No formal expression-to-Python compiler exists

**Scope**:
1. **Data models** (per concept Section 3.3, addressing design review findings):
   - `Compilability(str, Enum)` with `FULLY_COMPILABLE`, `PARTIALLY_COMPILABLE`, `MANUAL_REQUIRED`, `UNKNOWN`. The `UNKNOWN` value is the default state before compilation runs (Step 6.5). It is not in the concept's three-verdict classification but is needed as a sentinel: `PipelineModule.compilability` defaults to `UNKNOWN` at construction time in `build_computation_graph()`, then gets overwritten by the compiler's verdict. Without it, modules that were never compiled (e.g., due to missing ASTs) would need a `None` or implicit value.
   - `ExpressionNodeType(str, Enum)` with `BINARY_OP`, `UNARY_OP`, `LITERAL`, `INPUT_REF`, `INTERMEDIATE_REF`, `UNSUPPORTED`
   - `ExpressionAST` dataclass using `ExpressionNodeType` (not bare string)
   - `CompilationResult` dataclass with `compilability: Compilability` field (aligned vocabulary -- no separate "verdict" terminology)
   - `CalcDefCompilationResult` dataclass: aggregates per-output `CompilationResult`s for an entire CalcDef, carries `overall_compilability`, `output_results`, and `execution_order` (topological order of outputs). This model is what gets passed to generation via `PipelineContext`, keeping `compiled_expressions` off `PipelineModule`.
2. **Compiler functions**:
   - `build_expression_ast(syside_node, input_names, output_names) -> ExpressionAST` -- converts syside AST to clean IR
   - `compile_expression(ast: ExpressionAST) -> str` -- produces Python expression string
   - `classify_compilability(calc_def, expression_asts) -> Compilability` -- determines overall verdict
   - `compile_calc_def(calc_def, expression_asts) -> CalcDefCompilationResult` -- orchestrator for all outputs, returns aggregate result
3. **Expression reconstruction consolidation** (per concept Section 3.5):
   - Create `extraction/expression_utils.py`: extract the core recursive AST-to-text dispatcher, `OPERATOR_MAP`, and helper functions from `constraint_extractor.py` into this shared utility
   - Refactor `constraint_extractor.py` to import `_reconstruct_expression`, `_reconstruct_operator_expression`, `_extract_feature_reference_name`, `_extract_feature_chain_name` from `expression_utils.py`
   - `expression_compiler.py` imports from `expression_utils.py` for AST traversal and from `agentic_mbse.sysml.expression` for semantic analysis
   - Post-consolidation: `extractor._extract_expression_text()` is replaced; `constraint_extractor.py` delegates to shared utility; `agentic_mbse` module unchanged
4. **Unit tests**: Test against manually constructed `ExpressionAST` objects (no syside dependency). Cover all patterns A-F from concept. Test edge cases 1-6.

**Out of Scope**:
- Wiring into the pipeline -- no changes to `initialization.py`, `graph_builder.py`, `stencils.py`, or `resolution/models.py` (Item 4)
- Modifying `extractor.py` or `usage_extractor.py` (Item 4)
- Attribute expression handling (Phase 2)
- `InvocationExpression` / function call support

**Success Criteria**:
- [ ] `expression_compiler.py` exists in `extraction/` with 5 data models (`Compilability`, `ExpressionNodeType`, `ExpressionAST`, `CompilationResult`, `CalcDefCompilationResult`)
- [ ] All enums defined (no bare strings for compilability or node types)
- [ ] `expression_utils.py` exists in `extraction/` with shared AST-to-text logic extracted from `constraint_extractor.py`
- [ ] `constraint_extractor.py` imports from `expression_utils.py` (no duplicated reconstruction logic)
- [ ] Unit tests cover patterns A-F (simple binary, multi-step intermediate, parenthesized, literals, pi-as-literal, unit annotation)
- [ ] Unit tests cover edge cases 1-6 (unresolved ref, circular intermediate, missing AST, unsupported operator, FeatureChain in CalcDef, EXPOSE-with-operators)
- [ ] `uv run pytest tests/unit/test_expression_compiler.py` passes
- [ ] `uv run mypy src/sysml_codegen/extraction/expression_compiler.py` passes
- [ ] Existing `constraint_extractor` tests still pass after refactor

**Deliverables**:
- `src/sysml_codegen/extraction/expression_compiler.py`
- `src/sysml_codegen/extraction/expression_utils.py`
- Modified: `src/sysml_codegen/extraction/constraint_extractor.py` (imports from expression_utils)
- `tests/unit/test_expression_compiler.py`
- `.project/active/expr-compiler-module/spec.md`
- `.project/active/expr-compiler-module/design.md`
- `.project/active/expr-compiler-module/plan.md`

---

### Item 4: Pipeline Integration -- CalcDef Expression Compilation

**Type**: Integration
**Effort**: 2-2.5 days (spec 2h, design 3h, plan 2h, execute 9-12h)
**Dependencies**: Item 3 (expression compiler module must be built and tested)

**Objective**: Wire the expression compiler into the full extraction→resolution→generation pipeline so that codegen produces auto-implemented `_impl.py` files for compilable CalcDefs.

**Current State**:
- ✅ Expression compiler module exists with unit tests (Item 3)
- ✅ `expression_utils.py` provides shared AST-to-text utilities (Item 3)
- ✅ `PipelineModule` exists in `resolution/models.py` (no compilability field yet)
- ✅ `stencils.py` generates `NotImplementedError` stubs (unconditionally)
- ✅ `preservation.py` handles signature-based regeneration detection (body-agnostic)
- ❌ `CalculationDefinitionData` has no `output_expression_asts` field
- ❌ `PipelineModule` has no `compilability` field
- ❌ `PipelineContext` has no `compilation_results` field
- ❌ `stencils.py` has no conditional auto-impl path
- ❌ No auto-implementation Jinja2 template exists
- ❌ `usage_extractor._extract_single_binding()` drops `OperatorExpression` to `UNBOUND`

**Scope**:
1. **Extraction layer** (`extraction/`):
   - Add `output_expression_asts: dict[str, Any]` to `CalculationDefinitionData`
   - Modify `extractor._extract_calculation_definition()` to capture raw AST nodes for each output
   - Replace `_extract_expression_text()` with calls to `expression_utils` for `calc_expressions` text population
   - **Fix `usage_extractor._extract_single_binding()`**: The `OperatorExpression` fallthrough at line 327-332 currently returns `BindingType.UNBOUND`. Fix to classify as `BindingType.EXPRESSION` and store the raw AST on `BindingInfo`. This is a Phase 1 fix per concept Section 3.5: while CalcDef output compilation doesn't depend on usage-level EXPRESSION bindings, the fix is small (4-5 lines), corrects a known bug, and unblocks Phase 2 without requiring a second pass through `usage_extractor`.
2. **Pipeline orchestration** (`generation/initialization.py`):
   - Add **Step 6.5** to `build_pipeline_context()`: after `backtracker.find_required_modules()` (Step 6) and before `build_computation_graph()` (Step 7), call `classify_and_compile_expressions(calc_defs, backtracking_result) -> dict[str, CalcDefCompilationResult]`. This runs after backtracking because the compiler needs resolved binding information to verify that all expression refs map to declared inputs.
   - Add `compilation_results: dict[str, CalcDefCompilationResult]` to `PipelineContext` (keyed by `calc_def.name`)
   - Pass `compilation_results` to `build_computation_graph()` so it can set `PipelineModule.compilability`
3. **Resolution layer** (`resolution/`):
   - Add `compilability: Compilability = Compilability.UNKNOWN` field to `PipelineModule`
   - `compiled_expressions` are NOT added to `PipelineModule` -- expression strings live on `CalcDefCompilationResult` in `PipelineContext`, per concept Section 3.2. The resolution model carries only the compilability verdict; actual expression strings are passed directly from `PipelineContext.compilation_results` to the generator.
   - `build_computation_graph()` receives `compilation_results` dict and sets each module's `compilability` from the corresponding `CalcDefCompilationResult.overall_compilability`
4. **Generation layer** (`generation/`):
   - Add new template `templates/auto_implementation.py.jinja2` for compilable CalcDefs
   - Modify `stencils.py` to accept `compilation_results` and select auto-impl template vs stub template based on `compilability`
   - Generator looks up `CalcDefCompilationResult.output_results` for expression strings and `execution_order` for code emission ordering
   - Auto-generated impls include `AUTO_IMPLEMENTED = True` sentinel (human-readable convention per concept Section 3.6; preservation system uses signature comparison, not this flag)
   - Verify `preservation.py` interaction per concept Section 3.6 lifecycle scenarios: auto-gen -> hand-edit -> re-gen preserves user edit (signature match); auto-gen -> SysML input change -> re-gen backs up and regenerates (signature mismatch)

**Out of Scope**:
- Computed Attribute modules (Phase 2)
- Inline expressions in module wrappers (Computed Attribute archetype)
- Synthetic CalcUsage generation from attribute expressions (Phase 2)
- Backtracker changes

**Success Criteria**:
- [ ] All existing tests pass with zero regressions
- [ ] Codegen on chain_spike model produces `_impl.py` with actual code for all 3 CalcDefs
- [ ] `PipelineModule` has `compilability` enum field (no `compiled_expressions` -- that's on `CalcDefCompilationResult`)
- [ ] `PipelineContext` has `compilation_results: dict[str, CalcDefCompilationResult]`
- [ ] Step 6.5 exists in `build_pipeline_context()` between backtracking and graph building
- [ ] `CalculationDefinitionData` has `output_expression_asts` field
- [ ] `usage_extractor._extract_single_binding()` classifies `OperatorExpression` as `BindingType.EXPRESSION`
- [ ] Auto-impl template produces syntactically valid Python with `AUTO_IMPLEMENTED = True` sentinel
- [ ] Stub template still used for `MANUAL_REQUIRED` CalcDefs
- [ ] `preservation.py` correctly preserves hand-edited auto-impl files on regeneration

**Deliverables**:
- Modified: `extraction/data_models.py`, `extraction/extractor.py`, `extraction/usage_extractor.py`
- Modified: `resolution/models.py`, `resolution/graph_builder.py`
- Modified: `generation/initialization.py`, `generation/stencils.py`
- New: `templates/auto_implementation.py.jinja2`
- `.project/active/expr-pipeline-integration/spec.md`
- `.project/active/expr-pipeline-integration/design.md`
- `.project/active/expr-pipeline-integration/plan.md`

---

### Item 5: End-to-End Validation on Real Models

**Type**: Testing
**Effort**: 1 day (spec 1h, design 0h, plan 1h, execute 5-6h)
**Dependencies**: Item 4 (pipeline integration must be complete)

**Objective**: Validate that expression-aware codegen produces correct, executable auto-implementations for real-world SysML models, and that the generated code matches existing handwritten implementations.

**Current State**:
- ✅ Pipeline integration complete (Item 4)
- ✅ Chain_spike model verified in Item 4
- ❓ Unknown: how solar_battery model's 15 CalcDefs classify
- ❓ Unknown: whether auto-generated code matches handwritten impls numerically
- ❓ Unknown: whether IMPLEMENTATION_BACKLOG.md accurately reflects only manual work

**Scope**:
1. **Solar_battery model validation**:
   - Run codegen on solar_battery model
   - Verify: >=10 of 15 CalcDefs auto-implemented
   - For each auto-implemented CalcDef: execute with test inputs and compare against handwritten impl output. Assert `1e-10` tolerance.
   - For each non-compilable CalcDef: verify stub is correct and reason is accurate
2. **CATF model validation** (if available):
   - Run codegen on CATF model
   - Verify auto-implementation count
   - Verify non-compilable stubs have accurate reasons
3. **Backlog report validation**:
   - Verify `IMPLEMENTATION_BACKLOG.md` only lists genuinely manual CalcDefs
   - Verify auto-implemented modules are NOT in the backlog
4. **Regression suite**:
   - Add integration test that runs codegen on chain_spike and asserts auto-impl content
   - Add integration test fixtures for expression patterns A-F

**Out of Scope**:
- Performance benchmarking
- Phase 2 (attribute expression) validation
- CI/CD integration

**Success Criteria**:
- [ ] Solar_battery: >=10 of 15 CalcDefs auto-implemented
- [ ] Auto-implemented code matches handwritten impls within `1e-10` tolerance
- [ ] Non-compilable CalcDefs have accurate `MANUAL_REQUIRED` reasons
- [ ] `IMPLEMENTATION_BACKLOG.md` lists only genuinely manual work
- [ ] Integration tests added and passing
- [ ] Validation report documents per-CalcDef results

**Deliverables**:
- `tests/integration/test_expression_compilation_e2e.py`
- `.project/active/expr-e2e-validation/spec.md`
- `.project/active/expr-e2e-validation/report.md` (per-CalcDef results table)

---

## Dependencies

**External**:
- `agentic-mbse` package: SysIDE adapter, `BindingType` enum, `expression` module utilities
- SysIDE: Must populate `feature_value_expression` on CalcDef output attributes (validated in Item 1)
- Solar_battery model: Must be accessible for end-to-end validation (Item 5)

**Internal**:
- Concept document: `.project/concepts/expression-aware-codegen.md` (design reference)
- Research: `.project/research/20260202-180000_expression-compilation-and-inline-math-strategy.md`

**Item Dependency Graph**:
```
Item 1: Spike -- AST Extraction (no dependencies)
  └─> Item 2: Spike -- Compilation Proof (needs AST findings)
        └─> Item 3: Expression Compiler Module (needs validated logic)
              └─> Item 4: Pipeline Integration (needs compiler module)
                    └─> Item 5: E2E Validation (needs integrated pipeline)
```

All items are sequential. Each spike gates the next item: if a spike reveals a fundamental assumption is wrong, subsequent items are re-scoped or cancelled before investing in implementation.

---

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| <80% of CalcDef outputs have extractable ASTs | High | Item 1 spike validates before any implementation. If coverage is low, re-scope to only compile what's available. |
| Feature references don't all resolve to inputs/intermediates | High | Item 1 Q2 validates the core assumption. If false, the ExpressionAST model needs a new node type. |
| Compiled expressions produce subtly wrong results | High | Item 2 compares against handwritten ground truth. Item 5 repeats at integration level. Two validation gates. |
| SysIDE AST structure varies across expression types | Medium | Duck-typing pattern (already used in constraint_extractor). Item 1 inventories all node types encountered. |
| Preservation.py interaction with auto-generated files is incorrect | Medium | Item 4 explicitly tests the transition: auto-gen -> hand-edit -> re-gen. Existing signature comparison logic should handle this. |
| Expression compilation changes break existing tests | Low | Each item runs full test suite before and after. Item 4 specifically requires zero regressions. |

---

## Design Review Issues Addressed

The following issues from the design review are resolved by specific items:

| Review Issue | Severity | Addressed In | How |
|--------------|----------|--------------|-----|
| Compilation timing unspecified in 7-step pipeline | Major | Item 4 | Compilation runs as explicit Step 6.5 in `build_pipeline_context()`, per concept Section 3.2. After backtracking (Step 6), before graph building (Step 7). |
| `compilability` should be Enum, not bare string | Major | Item 3 | `Compilability(str, Enum)` defined in expression_compiler.py |
| Expression reconstruction consolidation missing | Major | Item 3 | `expression_utils.py` created; `constraint_extractor.py` refactored to import from it; `_extract_expression_text()` replaced |
| `compiled_expressions` mixes resolution/generation | Minor | Item 4 | Follows concept Section 3.2: expression strings live on `CalcDefCompilationResult` in `PipelineContext`, NOT on `PipelineModule`. Resolution model carries only `compilability` verdict. |
| `ExpressionAST.node_type` should be Enum | Minor | Item 3 | `ExpressionNodeType(str, Enum)` defined |
| `CompilationResult.verdict` vocabulary misaligned | Minor | Item 3 | No "verdict" terminology -- `CompilationResult.compilability` uses `Compilability` enum consistently |
| Preservation.py interaction unspecified | Minor | Item 4 | Follows concept Section 3.6 lifecycle scenarios. `AUTO_IMPLEMENTED = True` sentinel for human readability; preservation uses signature comparison exclusively. |

### Concept Deviations

| Deviation | Rationale |
|-----------|-----------|
| `Compilability.UNKNOWN` added (not in concept's three-verdict classification) | Needed as default sentinel on `PipelineModule.compilability` at construction time, before Step 6.5 runs compilation. Without it, modules that were never compiled (e.g., missing ASTs) would need `None` or an implicit value. |

---

## Timeline

**Total Effort**: ~8.5-10.5 days (sequential)

| Item | Effort | Dependencies | Gate |
|------|--------|--------------|------|
| Item 1: Spike -- AST Extraction | 1 day | None | Go/no-go on AST coverage |
| Item 2: Spike -- Compilation Proof | 1 day | Item 1 | Go/no-go on compilation accuracy |
| Item 3: Expression Compiler Module | 1.5 days | Item 2 | Unit tests pass |
| Item 4: Pipeline Integration | 2-2.5 days | Item 3 | Existing tests + chain_spike pass |
| Item 5: E2E Validation | 1 day | Item 4 | Solar_battery validation pass |

**Critical path**: All items are sequential. Each spike is a gate: failure means re-scope before investing in implementation.

**Phase 2 (future epic)**: Computed Attribute extraction and synthetic CalcUsage generation. Requires separate spikes (Q5+Q6 from concept). Not included in this epic.

---

## Lessons Learned (Post-Completion)

*Fill in after epic is complete*

**What Went Well**:
- TBD

**What Could Improve**:
- TBD

**Surprises**:
- TBD

---

**Last Updated**: 2026-02-04
**Next Action**: Begin Item 3 -- create `.project/active/expr-compiler-module/spec.md` and design the expression compiler module
