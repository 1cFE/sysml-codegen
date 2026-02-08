# Epic: Attribute Expression Capture

**Epic ID**: ATTR-EXPR
**Status**: Active (Items 1-2 complete, Items 3-5 ready)
**Priority**: P1
**Created**: 2026-02-08
**Estimated Effort**: ~6.5-8.5 days (Item 1 complete; ~5.5-7.5 remaining)

---

## Executive Summary

Enable SysML modelers to express computations as attribute-level expressions (`attribute volume = pi * r^2 * h`) instead of requiring full CalcDef+CalcUsage ceremony for every formula. Codegen detects computed attributes on PartDefs, generates synthetic pipeline modules, and auto-implements them using the Phase 1 expression compiler -- eliminating the biggest remaining source of SysML modeling overhead.

**Critical Success Factor**: A PartDef attribute with an arithmetic expression generates a correct, executable pipeline module without any CalcDef, CalcUsage, or handwritten `_impl.py`.

---

## Why This Epic?

**Current State**:
- Every arithmetic formula requires: CalcDef (library.sysml) + CalcUsage (design.sysml) + generated TEAx module wrapper + generated/handwritten `_impl.py` + pipeline YAML wiring
- For `volume = pi * r^2 * h`, this is ~100 lines of infrastructure for 1 line of math
- Phase 1 (EXPR-CODEGEN) eliminated the `_impl.py` bottleneck for CalcDefs (15/15 solar_battery, 19/21 CATF auto-implemented), but the CalcDef ceremony itself remains mandatory
- Attribute-level expressions exist in models today but are NOT captured as pipeline computations:
  - `attribute p_net_kw : Real = p_net_mw * 1000.0;` (solar_battery `design.sysml:60`) -- lost, not compiled
  - `attribute p_alpha_out : Real = alpha_neutron_split.p_alpha;` (CATF `physics.sysml:114-122`) -- EXPOSE pattern, not wired
- Modelers must create aggregation CalcDefs for `total_cost = comp_a.cost + comp_b.cost + comp_c.cost` when a simple attribute expression would suffice (Approach E Rule 3)
- The Phase 1 expression compiler is CalcDef-agnostic -- `build_expression_ast()` and `compile_expression()` work on any SysIDE AST node -- but are only invoked for CalcDef outputs

**Future State**:
- Attribute-level expressions (`attribute volume = pi * r^2 * h`) automatically generate pipeline modules
- No CalcDef, CalcUsage, or `_impl.py` needed for computed attributes
- Aggregation CalcDefs become optional -- `attribute total = a + b + c` on a PartDef suffices
- The expression compiler processes both CalcDef outputs AND attribute expressions
- Approach E Rule 3 ("aggregation is an explicit CalcDef") and Rule 5 ("every formula is a CalcDef") become optional for modelers
- Foundation exists for Phase 3: hierarchy, multiplicity, and nested CalcUsage-in-PartDef patterns

---

## Success Criteria

- [ ] PartDef attributes with arithmetic expressions generate synthetic pipeline modules
- [ ] Auto-implemented code for computed attributes produces correct values
- [ ] Solar_battery `p_net_kw = p_net_mw * 1000.0` pattern works end-to-end (module generated, downstream calcs wired correctly)
- [ ] Computed attributes referencing other computed attributes (chains) resolve correctly
- [ ] All existing tests pass with zero regressions (167+ baseline from Phase 1)
- [ ] `ComputedAttributeData` model defined with expression AST, classification, and compiled expression
- [ ] Computed attribute extraction runs as Step 4.5 in `build_pipeline_context()`
- [ ] Backtracker resolves CalcUsage bindings to FORMULA computed attributes as MODULE_OUTPUT
- [ ] Synthetic modules visible in pipeline YAML and `IMPLEMENTATION_BACKLOG.md`
- [ ] Phase 1 expression compiler reused with zero changes
- [ ] ADRs drafted capturing architectural decisions

---

## Architectural Decisions

Key decisions are captured in `.project/concepts/attr-expr-architectural-decisions.md`. Summary:

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Integration architecture | **Option C: Direct graph integration** | ComputedAttributeData is first-class; no phantom CalcDef/CalcUsage synthesis. FORMULA and EXPOSE get different treatment naturally. |
| Classification scheme | **5-way: FORMULA, EXPOSE_PURE, EXPOSE_COMPUTED, LITERAL, UNRESOLVABLE** | Replaces original FORMULA/EXPOSE/MIXED/LITERAL/UNRESOLVABLE. Splits EXPOSE into alias (PURE) and deferred (COMPUTED). Drops MIXED (never observed). |
| EXPOSE handling | **EXPOSE_PURE = alias, EXPOSE_COMPUTED = deferred** | EXPOSE_PURE doesn't generate a module; provides wiring context. EXPOSE_COMPUTED deferred until a concrete modeling need arises. |
| Pipeline placement | **Step 4.5** (after design attributes, before parameter groups) | Removes FORMULA attributes from design_attributes dict to prevent false entry points in Step 5. |
| Module naming | **`{part_name}__{attr_name}`** per ADR-003 | Consistent with CalcUsage module naming convention. |
| Reference resolution | **Qualified names mandatory** | Prevents misclassification when CalcDef output names collide with sibling attribute names (19 CATF misclassifications in v1 spike). |
| Backtracker awareness | **Backtracker receives computed attributes** | When a CalcUsage binds to a FORMULA computed attribute, backtracker resolves as MODULE_OUTPUT from synthetic module. |

---

## Backlog Items

### Item 1: Spike -- Attribute Expression AST Discovery & Architecture Evaluation

**Status**: Complete (GO)
**Type**: Research
**Effort**: ~1 day (actual)
**Dependencies**: None

**Objective**: Verify that SysIDE populates `feature_value_expression` on PartDef attributes, inventory attribute expression patterns across real models, and evaluate architecture options.

**Results Summary** (v1 + v2):
- **AST availability**: 35/35 attributes have `feature_value_expression` across probe fixture; confirmed on solar_battery and CATF real models
- **FORMULA compilation**: 14/14 FORMULA patterns compile with Phase 1 compiler, zero changes needed. Includes simple binary, 3-term product, parenthesized grouping, 7-ref deep nesting, constant fractions.
- **Chain handling**: Compiler treats computed attributes identically to literal attributes. `cost = area * rate` compiles to `(inputs.area * inputs.rate)` whether `area` is literal or computed. Chain resolution is purely a graph-ordering concern.
- **EXPOSE patterns**: Produce `FeatureChainExpression` nodes, fail compilation as expected (`unsupported operator: .`). Pure EXPOSE is an alias, not a computation.
- **Cross-part references**: 0 found across all models. Phase 3 concern.
- **Architecture recommendation**: Option C (direct graph integration)
- **Classification refinement**: MIXED never observed; D2 pattern (`scale_calc.result * 2.0`) revealed EXPOSE_PURE / EXPOSE_COMPUTED split
- **Qualified name resolution**: Mandatory for classification (19 CATF misclassifications with simple names)
- **`reconstruct_expression()` loses parentheses**: AST compilation is the only correct path for semantics

**Key finding**: The compiler's chain-blindness is a feature, not a bug. Each computed attribute compiles independently. The graph builder handles ordering.

**Deliverables** (complete):
- `scripts/spike_attribute_expressions.py`
- `tests/fixtures/attr_expr_probe/design.sysml`
- `tests/fixtures/attr_expr_probe/library.sysml`
- `.project/active/attr-expr-spike/report.md` (v1)
- `.project/active/attr-expr-spike/findings_v2.md` (v2 probe)
- `.project/active/attr-expr-spike/spec.md`
- `.project/active/attr-expr-spike/design.md`
- `.project/active/attr-expr-spike/plan.md`
- `.project/concepts/attr-expr-architectural-decisions.md`

---

### Item 2: Computed Attribute Extraction & Data Models

**Status**: Complete
**Type**: Implementation
**Effort**: ~1 day (spec 0.5h, design 1h, plan 0.5h, execute 4-6h)
**Dependencies**: Item 1 (complete)

**Objective**: Build the computed attribute extraction module with data models, classification logic, and unit tests -- all independent of pipeline integration.

**Current State**:
- ✅ Expression compiler exists with `build_expression_ast()`, `compile_expression()`, `Compilability` enum (Phase 1)
- ✅ `expression_utils.py` provides shared AST-to-text utilities (Phase 1)
- ✅ `_extract_attribute()` in `extractor.py` (lines 339-371) captures literal defaults via `_extract_default_value()`
- ✅ `DesignAttributeData` in `parameter_groups.py` tracks attribute metadata including `parent_part`, `qualified_name`
- ✅ Item 1 spike proved: ASTs available, 14/14 FORMULA compile, qualified names reliable
- ❌ No AST capture for attribute expressions -- `AttributeInfo` stores only `default_value` as string
- ❌ No distinction between computed vs. data attributes at extraction time
- ❌ No `ComputedAttributeData` model

**Scope**:

1. **Data models** (in `extraction/data_models.py`):
   - `ComputedAttributeClassification(str, Enum)`:
     - `FORMULA` -- arithmetic on sibling attributes only (generates synthetic module)
     - `EXPOSE_PURE` -- single FeatureChainExpression, no operators (channel alias, no module)
     - `EXPOSE_COMPUTED` -- FeatureChainExpression inside arithmetic (deferred)
     - `LITERAL` -- pure constants, no feature references (not a computed attribute)
     - `UNRESOLVABLE` -- references that can't be resolved (warning, skip)
   - `ComputedAttributeData` dataclass:
     - `name: str` -- attribute name
     - `python_name: str` -- sanitized Python identifier
     - `owning_part_name: str` -- owning PartDef/PartUsage name
     - `owning_part_qualified_name: str` -- qualified name for resolution
     - `expression_ast: Any` -- raw SysIDE AST node (source of truth for compilation)
     - `expression_text: str` -- human-readable SysML via `reconstruct_expression()` (display only, does NOT preserve parenthesization)
     - `reference_names: list[str]` -- resolved reference names
     - `reference_qualified_names: list[str]` -- qualified names for each reference
     - `classification: ComputedAttributeClassification`
     - `compilability: Compilability`
     - `compiled_expression: str | None` -- Python expression from compiler
     - `source_file: Path`
     - `source_line: int`

2. **Extraction logic** (new file `extraction/computed_attribute_extractor.py`):
   - `extract_computed_attributes(adapter, part_element, calc_usage_names) -> list[ComputedAttributeData]`
   - Iterates part's `owned_members`, filters `AttributeUsage` with `feature_value_expression`
   - Classifies each attribute using `ref.qualified_name` (NOT `ref.name`) to distinguish sibling attribute refs from calc output refs:
     - All refs share owning part's namespace → FORMULA
     - Any ref has CalcDef output namespace → EXPOSE_PURE (if no operators) or EXPOSE_COMPUTED (if operators)
     - No refs (pure constants) → LITERAL
     - Unresolvable refs → UNRESOLVABLE
   - Compiles FORMULA expressions using Phase 1's `build_expression_ast()` + `compile_expression()` with sibling attribute names as `input_names`
   - No chain-awareness needed -- compiler treats computed attr refs identically to literal attr refs

3. **Unit tests** (`tests/unit/test_computed_attribute_extraction.py`):
   - Simple FORMULA: `area = length * width` → compiled `(inputs.length * inputs.width)`, classification FORMULA
   - Complex FORMULA: `p_blanket = m_n * p_f + p_in + eta * (f_p * eta_p + f_sub) * (m_n * p_f)` → correct nested compilation
   - Chain FORMULA: `cost = area * rate` where `area` is also computed → compiled `(inputs.area * inputs.rate)`, classification FORMULA (no special handling)
   - EXPOSE_PURE: `p_alpha_out = alpha_split.p_alpha` → classification EXPOSE_PURE, `compiled_expression = None`
   - EXPOSE_COMPUTED: `scaled_area = scale_calc.result * 2.0` → classification EXPOSE_COMPUTED, `compiled_expression = None`
   - LITERAL: `length = 10.0` → classification LITERAL (skipped, not a `ComputedAttributeData`)
   - UNRESOLVABLE: `broken = length * mystery` → classification UNRESOLVABLE
   - Qualified name resolution: verify that a ref named `p_alpha` with CalcDef qualified name is NOT classified as sibling ref even when a sibling named `p_alpha` exists

**Out of Scope**:
- Pipeline integration (Item 3)
- Backtracker changes (Item 3)
- Graph builder changes (Item 3)
- EXPOSE_COMPUTED compilation (deferred)
- `InvocationExpression` / function call support
- Cross-part attribute references (Phase 3)

**Success Criteria**:
- [x] `ComputedAttributeData` model defined with all fields
- [x] `ComputedAttributeClassification` enum with 5 values
- [x] Extraction correctly classifies FORMULA, EXPOSE_PURE, EXPOSE_COMPUTED, LITERAL, UNRESOLVABLE
- [x] Classification uses `ref.qualified_name` -- test proves simple-name collision is handled
- [x] Compilation produces valid Python for FORMULA patterns (EXPOSE patterns return None)
- [x] `expression_text` populated via `reconstruct_expression()` with caveat that it's display-only
- [x] Unit tests pass covering all 8 test patterns above (15 total including graceful degradation)
- [x] `uv run mypy` passes on new code
- [x] `uv run pytest tests/` -- all existing tests unaffected (182 total, 0 failures)

**Deliverables**:
- New: `src/sysml_codegen/extraction/computed_attribute_extractor.py`
- Modified: `src/sysml_codegen/extraction/data_models.py` (new models)
- New: `tests/unit/test_computed_attribute_extraction.py`
- `.project/active/attr-expr-extraction/spec.md`
- `.project/active/attr-expr-extraction/design.md`
- `.project/active/attr-expr-extraction/plan.md`

---

### Item 3: Pipeline Integration -- Computed Attribute Modules

**Status**: Not Started
**Type**: Integration
**Effort**: ~2-2.5 days (spec 2h, design 3h, plan 2h, execute 9-12h)
**Dependencies**: Item 2 (extraction module must be built and tested)

**Objective**: Wire computed attribute extraction into the full extraction-resolution-generation pipeline so that codegen produces synthetic modules and auto-implementations for FORMULA computed attributes.

**Architecture**: Option C (direct graph integration) per `.project/concepts/attr-expr-architectural-decisions.md`

**Current State** (after Item 2):
- ✅ `ComputedAttributeData` and classification exist with unit tests
- ✅ Expression compiler handles FORMULA attribute ASTs
- ✅ Auto-implementation templates exist from Phase 1
- ✅ `build_pipeline_context()` has 7 steps + Step 6.5 for expression compilation
- ❌ Pipeline doesn't extract or process computed attributes
- ❌ Backtracker doesn't recognize FORMULA attributes as MODULE_OUTPUT sources
- ❌ Graph builder doesn't generate modules for computed attributes
- ❌ FORMULA attributes in design_attributes dict may produce false entry points

**Scope**:

1. **Pipeline orchestration** (`generation/initialization.py`):
   - Add Step 4.5: `extract_computed_attributes()` on each PartDef/PartUsage
   - Store `list[ComputedAttributeData]` on `PipelineContext` (new field)
   - **Remove FORMULA attributes from design_attributes dict** before Step 5 (ParameterGroupDeriver) to prevent false entry point derivation. EXPOSE_PURE and LITERAL attributes remain in design_attributes.
   - Pass computed attributes to backtracker (Step 6) and graph builder (Step 7)

2. **Backtracker awareness** (`analysis/dependency_backtracker.py`):
   - Accept `computed_attributes: list[ComputedAttributeData]` as new parameter to `find_required_modules()`
   - Build lookup dict keyed by `(owning_part_qualified_name, attribute_name)` for O(1) resolution
   - When tracing a CalcUsage binding that targets a part attribute:
     - **If FORMULA**: resolve as `MODULE_OUTPUT` from synthetic module `{part_name}__{attr_name}`. This is the critical path for solar_battery `annualized_om` binding `in p_net_kw = p_net_kw`.
     - **If EXPOSE_PURE**: follow the alias to the upstream calc output and resolve as `MODULE_OUTPUT` from that calc's module. (Verify first whether existing transitive resolution already handles this -- if so, document and skip.)
     - **If neither**: fall through to existing logic (literal → ENTRY_POINT, etc.)

3. **Graph building** (`resolution/graph_builder.py`):
   - Accept `computed_attributes: list[ComputedAttributeData]` as new parameter to `build_computation_graph()`
   - For each FORMULA computed attribute, generate a `PipelineModule`:
     - Module name: `{part_name}__{attr_name}` (ADR-003)
     - Module type: PascalCase derived from module name
     - Inputs: one `ModuleInput` per reference in the expression, wired using per-part attribute resolution map:
       - Literal sibling attribute → entry point
       - Another FORMULA computed attribute → upstream synthetic module output
       - EXPOSE_PURE attribute → aliased upstream calc output channel
     - Output: single `ModuleOutput` named after the attribute
     - `is_computed_attribute = True`
     - `compilability = FULLY_COMPILABLE`
   - Topological ordering: computed attribute modules ordered after their dependencies (other computed attrs or calc modules) and before their consumers (downstream calcs or computed attrs). Same topological sort already used for CalcUsage modules.

4. **Generation** (`generation/stencils.py` and templates):
   - Reuse Phase 1 `auto_implementation.py.jinja2` template for FORMULA computed attribute modules
   - Generate module wrapper, auto-impl, and pipeline YAML entries
   - Include in `IMPLEMENTATION_BACKLOG.md` (show as auto-implemented, "0 functions to implement")
   - Include in module registry `__init__.py`
   - Computed attribute modules marked with `# source: computed_attribute` comment in YAML for debuggability

5. **Entry point handling**:
   - FORMULA module inputs that are literal sibling attributes become entry points, classified as `DESIGN_ATTRIBUTE` (existing type)
   - FORMULA module inputs that are upstream module outputs (other FORMULA or CalcUsage outputs) do NOT become entry points
   - The Step 4/4.5 overlap resolution ensures ParameterGroupDeriver only sees non-FORMULA attributes

**Secondary investigation** (within Item 3, not blocking completion):
- Does the backtracker already handle EXPOSE_PURE transitively when a CalcUsage binds to an EXPOSE attribute? Test with CATF `in p_alpha = physics.p_alpha_out` pattern.
- If yes: document as already handled, no additional code needed for EXPOSE_PURE.
- If no: implement alias resolution in the backtracker's new computed attribute lookup.

**Out of Scope**:
- EXPOSE_COMPUTED decomposition (deferred -- known UX gap, documented in concept doc)
- Hierarchy/multiplicity (Phase 3)
- Cross-part attribute references (Phase 3)
- `InvocationExpression` / function calls
- Changes to TEAx runtime or module base classes
- Inline expressions in module wrappers (future optimization)

**Success Criteria**:
- [ ] Step 4.5 integrated into `build_pipeline_context()`
- [ ] FORMULA attributes removed from design_attributes before Step 5
- [ ] Backtracker resolves CalcUsage→FORMULA bindings as MODULE_OUTPUT
- [ ] Graph builder generates PipelineModule for each FORMULA computed attribute
- [ ] Computed attribute modules have correct inputs wired from resolution map
- [ ] Topological ordering correct for chains (A→B→C all computed)
- [ ] EXPOSE_PURE behavior documented (already handled by backtracker OR alias added)
- [ ] Pipeline YAML includes computed attribute modules in correct order
- [ ] `IMPLEMENTATION_BACKLOG.md` shows computed attribute modules as auto-implemented
- [ ] Module registry includes computed attribute modules
- [ ] All existing tests pass with zero regressions (167+ baseline)
- [ ] Integration tests for: simple FORMULA, chain, FORMULA→EXPOSE_PURE input wiring

**Deliverables**:
- Modified: `src/sysml_codegen/generation/initialization.py` (Step 4.5, PipelineContext)
- Modified: `src/sysml_codegen/analysis/dependency_backtracker.py` (computed attr awareness)
- Modified: `src/sysml_codegen/resolution/graph_builder.py` (FORMULA module generation)
- Modified: `src/sysml_codegen/resolution/models.py` (`is_computed_attribute` flag on PipelineModule)
- Modified: `src/sysml_codegen/generation/stencils.py` (if template adjustments needed)
- New: `tests/integration/test_computed_attribute_pipeline.py`
- `.project/active/attr-expr-pipeline/spec.md`
- `.project/active/attr-expr-pipeline/design.md`
- `.project/active/attr-expr-pipeline/plan.md`

---

### Item 4: E2E Validation on Real Models

**Status**: Not Started
**Type**: Testing
**Effort**: ~1 day (spec 0.5h, design 1h, plan 0.5h, execute 4-5h)
**Dependencies**: Item 3 (pipeline integration must be complete)

**Objective**: Validate that computed attribute pipeline modules produce correct, executable outputs on real SysML models, and that the full pipeline remains correct end-to-end including all Phase 1 CalcDef auto-implementations.

**Scope**:

1. **Solar_battery validation** (primary real-model proof point):
   - `p_net_kw = p_net_mw * 1000.0` generates a synthetic pipeline module `solar_battery_plant__p_net_kw`
   - Module is auto-implemented with correct expression (`inputs.p_net_mw * 1000.0`)
   - Downstream CalcUsage `annualized_om` binding `in p_net_kw = p_net_kw` resolves as MODULE_OUTPUT from synthetic module (not ENTRY_POINT)
   - Full pipeline produces correct outputs matching existing results

2. **Spike probe fixture validation** (`tests/fixtures/attr_expr_probe/`):
   - Reuse the existing probe fixture (14 FORMULA + 3 chain + 4 EXPOSE + 2 CalcUsages) as the primary E2E validation fixture. Do NOT create a new fixture.
   - Extend with numerical ground-truth assertions (exact values, no tolerance needed):

     | Attribute | Expression | Expected Value |
     |-----------|-----------|----------------|
     | area | 10.0 * 5.0 | 50.0 |
     | volume | 10.0 * 5.0 * 3.0 | 150.0 |
     | cost | 50.0 * 12.0 | 600.0 |
     | marked_up_cost | 600.0 * 1.15 | 690.0 |
     | cost_density | 600.0 / 150.0 | 4.0 |
     | q_scientific | 2600.0 / 50.0 | 52.0 |
     | perimeter | 2.0 * 10.0 + 2.0 * 5.0 | 30.0 |
     | minor_radius | (4.2 + 4.4) / 2.0 - 3.0 | 1.3 |
     | p_alpha | 2600.0 * 3.52 / 17.58 | ~520.36... |

   - Verify chain resolution: `cost` depends on `area`, `marked_up_cost` depends on `cost`, `cost_density` depends on both `cost` and `volume`
   - Verify EXPOSE_PURE attributes classified but no modules generated for them
   - Verify EXPOSE_COMPUTED attributes classified but deferred (no module, no error)

3. **Phase 1 regression validation**:
   - Re-run all Phase 1 E2E tests (solar_battery CalcDef validation, CATF CalcDef validation)
   - Verify all 167+ existing tests still pass with zero xfail
   - Verify auto-implemented CalcDef modules unchanged (Phase 1 output not affected by Phase 2)

4. **Backlog accuracy**:
   - `IMPLEMENTATION_BACKLOG.md` correctly lists computed attribute modules as auto-implemented
   - Manual-required count unchanged from Phase 1 (only genuinely manual CalcDefs remain)
   - New computed attribute modules shown with "0 functions to implement"

**Out of Scope**:
- Performance benchmarking
- Phase 3 patterns (hierarchy/multiplicity/aggregation)
- EXPOSE_COMPUTED validation (deferred)

**Success Criteria**:
- [ ] Solar_battery `p_net_kw` synthetic module generates correct output
- [ ] Solar_battery downstream wiring correct (`AnnualizedOMCalc` receives `p_net_kw` from computed attribute module, not as entry point)
- [ ] Probe fixture: all FORMULA computed attributes produce correct numerical values
- [ ] Probe fixture: chain patterns (cost→area, marked_up_cost→cost, cost_density→cost+volume) resolve and execute correctly
- [ ] All existing tests pass (167+ total, 0 xfail, 0 failures)
- [ ] New E2E integration tests added and passing
- [ ] Validation report documents per-pattern results with pass/fail and numerical accuracy

**Deliverables**:
- New or extended: `tests/integration/test_computed_attributes_e2e.py`
- Modified (if needed): `tests/fixtures/attr_expr_probe/` (add ground truth data)
- `.project/active/attr-expr-e2e/report.md` (per-pattern results table)

---

### Item 5: Documentation -- ADRs and Epic Closure

**Status**: Not Started
**Type**: Documentation
**Effort**: ~0.5-1 day (draft 3-4h, review 1-2h)
**Dependencies**: Item 4 (must be validated before documenting decisions)

**Objective**: Formalize the architectural decisions from the concept document into ADRs, update existing ADRs, and close the epic with lessons learned.

**Scope**:

1. **ADR-004: Computed Attribute Pipeline Integration**
   - Captures: Decision 1 (Option C -- direct graph integration), Decision 4 (Step 4.5 pipeline placement), Decision 5 (module naming `{part}__{attr}`), Decision 7 (backtracker computed attribute awareness)
   - Format: follows existing ADR-001/002/003 structure
   - References concept doc for detailed rationale and spike findings for empirical grounding

2. **ADR-005: Computed Attribute Classification**
   - Captures: Decision 2 (5-way classification scheme), Decision 3 (EXPOSE handling strategy), Decision 6 (qualified name resolution requirement)
   - Includes the classification table with definitions, SysML examples, and pipeline treatment
   - Documents the EXPOSE_COMPUTED deferral and UX gap with guidance for modelers

3. **ADR-002 Amendment: Relaxation of Rules 3 and 5**
   - Rule 3 ("aggregation is an explicit CalcDef") → optional for same-part attribute aggregation
   - Rule 5 ("every formula is a CalcDef") → optional for simple attribute-level formulas
   - Conditions: expression must reference only sibling attributes (FORMULA classification); calc output references still require CalcDef or EXPOSE pattern
   - Documents the known UX gap: `attribute x = calc.output * factor` does NOT work (EXPOSE_COMPUTED deferred)

4. **Modeling guidance update**:
   - Clear statement: "Attribute expressions can reference sibling attributes on the same part. To reference a calc output, use the EXPOSE pattern (pure alias, no arithmetic) or create a CalcDef."
   - Examples of what works (FORMULA) and what doesn't yet (EXPOSE_COMPUTED)
   - When to use CalcDefs vs. attribute expressions (reusable/complex → CalcDef; one-off/simple → attribute)

5. **Epic closure**:
   - Fill in Lessons Learned section
   - Update epic status to Complete
   - Archive active work items to `.project/completed/`

**Out of Scope**:
- Changes to CLAUDE.md (defer until PR review)
- External documentation beyond ADRs
- Phase 3 planning

**Success Criteria**:
- [ ] ADR-004 drafted and self-consistent with implementation
- [ ] ADR-005 drafted with classification examples
- [ ] ADR-002 amendment drafted with clear before/after rules
- [ ] Modeling guidance includes concrete examples of what works and what doesn't
- [ ] All ADRs reference concept doc and spike findings
- [ ] Epic Lessons Learned filled in
- [ ] Active work items archived

**Deliverables**:
- New: `docs/architecture/ADR-004-computed-attribute-pipeline-integration.md` (or location per project convention)
- New: `docs/architecture/ADR-005-computed-attribute-classification.md`
- Modified: `docs/architecture/ADR-002-calculation-architecture.md` (amendment)
- Modified: This epic doc (Lessons Learned, status → Complete)

---

## Dependencies

**External**:
- `agentic-mbse` package: SysIDE adapter, `BindingType` enum, expression utilities. **No changes expected** -- Phase 2 reuses existing extraction and expression APIs.
- ~~SysIDE: Must populate `feature_value_expression` on PartDef attributes~~ **CONFIRMED** by Item 1 spike (35/35 attributes, all models).
- Solar_battery model: Must be accessible for E2E validation (Item 4)

**Internal**:
- **Epic EXPR-CODEGEN (Phase 1)**: Complete. Provides expression compiler (`expression_compiler.py`), auto-implementation template (`auto_implementation.py.jinja2`), Step 6.5 pipeline integration, and `Compilability`/`CalcDefCompilationResult` data models.
- Research report: `.project/research/20260202-180000_expression-compilation-and-inline-math-strategy.md` (Phase 2 roadmap, Approach F Use Case 2)
- Concept doc: `.project/concepts/attr-expr-architectural-decisions.md` (7 architectural decisions)

**Item Dependency Graph**:
```
Item 1: Spike -- AST Discovery & Architecture (COMPLETE)
  └─> Item 2: Extraction & Data Models (needs architecture decisions from Item 1)
        └─> Item 3: Pipeline Integration (needs extraction module from Item 2)
              └─> Item 4: E2E Validation (needs integrated pipeline from Item 3)
                    └─> Item 5: Documentation & ADRs (needs validated implementation from Item 4)
```

Items 2-5 are sequential. Item 1's GO gate has been passed.

---

## Risks

| Risk | Original Rating | Updated Rating | Mitigation |
|------|----------------|----------------|------------|
| SysIDE does not populate `feature_value_expression` on PartDef attributes | High | **RETIRED** | Item 1 confirmed: 35/35 attrs across probe fixture, solar_battery, CATF. |
| Attribute references cannot be resolved to sibling attributes via AST | High | **RETIRED** | Item 1 confirmed: all 14 FORMULA patterns resolve refs to siblings. |
| EXPOSE pattern already handled by backtracker transitive resolution | Low (positive) | **Unchanged** | Item 3 secondary investigation. Either outcome is good. |
| Synthetic module approach creates excessive pipeline modules | Medium | **Low** | FORMULA attrs map 1:1 to modules. EXPOSE_PURE = alias (no module). TEAx designed for many small modules. |
| Cross-part attribute references require hierarchy support | Medium | **Low** | 0 cross-part refs found in any model. Phase 3 concern. |
| Existing CalcDef auto-implementations regress | Low | **Unchanged** | Item 3 requires zero regression. Item 4 re-validates all Phase 1 E2E tests. |
| Architecture decision wrong | Medium | **Low** | Probe data strongly supports Option C. FORMULA/EXPOSE split maps naturally to module/alias. |
| Backtracker changes introduce regressions | -- | **Medium (new)** | Item 3 adds computed attribute awareness to backtracker. Existing tests are the safety net. Run full suite after every backtracker change. |
| Step 4/4.5 overlap creates false entry points | -- | **Medium (new)** | Item 3 removes FORMULA attrs from design_attributes dict before ParameterGroupDeriver. Unit test verifies. |
| EXPOSE_COMPUTED deferral surprises modelers | -- | **Low (new)** | Documented as known UX gap. Workaround: use CalcDef (Phase 1 auto-implements). ADR-002 amendment includes guidance. |
| CATF MIXED misclassification from simple-name collision | -- | **Low (new)** | Item 2 MUST use qualified name resolution. Unit test validates collision scenario. |

---

## Relationship to Research Roadmap

This epic implements **Phase 2** from the research report's phased roadmap:

| Research Roadmap | Epic Item | Notes |
|------------------|-----------|-------|
| "Extract computed attributes with expression ASTs" | Item 1 (verified), Item 2 (implement) | Spike confirmed ASTs available. Item 2 builds extraction. |
| "Generate synthetic CalcUsages from attribute expressions" | Item 3 | Architecture decision: **Option C (direct graph integration), NOT synthetic CalcUsages**. ComputedAttributeData is first-class. |
| "Auto-implement the synthetic modules" | Item 3 | Reuses Phase 1 expression compiler + auto-impl template. Zero compiler changes. |
| "Reduce need for explicit CalcDefs for simple formulas" | Item 4 (validate) | Solar_battery p_net_kw is the proof point. |
| Document decisions as ADRs | Item 5 (new) | ADR-004, ADR-005, ADR-002 amendment. |

**Research Open Questions addressed**:

| Question (from research Section 7) | Addressed In | How |
|-------------------------------------|-------------|-----|
| Q3: Should synthetic CalcUsages be visible in pipeline YAML? | Item 1, Concept doc | Synthetic **modules** (not CalcUsages) are visible in YAML. Provenance marked with `# source: computed_attribute`. |
| Q5: Should compiler handle `if-then-else` (SelectExpression)? | Out of scope | Classify as UNRESOLVABLE if encountered. Defer to future enhancement. |
| Q4 (partial): What about function calls (InvocationExpression)? | Out of scope | Classify as UNRESOLVABLE. Zero occurrences in any model. |

**Deferred to Phase 3 (future epic)**:

| Phase 3 Scope | Why Deferred |
|---------------|-------------|
| Part hierarchy extraction with multiplicity | Requires `:>>` redefinition chain resolution -- separate spike needed |
| Tree-to-DAG flattening with synthetic rollup modules | Significant architecture change to graph builder |
| Per-instance parameter context | TEAx runtime may need changes |
| Approach E Rules 1-4 becoming optional | Only triggered when verbosity measurably impedes productivity |
| EXPOSE_COMPUTED decomposition | Tractable but no concrete modeling need yet. Trigger: multiple modelers hitting the UX gap. |

---

## Timeline

**Total Effort**: ~6.5-8.5 days (Item 1 complete; ~5.5-7.5 days remaining)

| Item | Effort | Dependencies | Gate | Status |
|------|--------|--------------|------|--------|
| Item 1: Spike -- AST Discovery & Architecture | 1 day | None | Go/no-go on AST availability | **Complete (GO)** |
| Item 2: Extraction & Data Models | ~1 day | Item 1 | Unit tests pass, mypy passes | **Complete** |
| Item 3: Pipeline Integration | ~2-2.5 days | Item 2 | Existing tests pass + solar_battery computed attribute works | Not Started |
| Item 4: E2E Validation | ~1 day | Item 3 | Full validation pass on real models | Not Started |
| Item 5: Documentation & ADRs | ~0.5-1 day | Item 4 | ADRs drafted, epic closed | Not Started |

**Critical path**: Items 2-5 are sequential. Item 1's GO gate has been passed.

---

## Lessons Learned (Post-Completion)

*Fill in after epic is complete*

**What Went Well**:
- Item 1 spike de-risked the entire epic. The v2 probe with a purpose-built fixture answered every open question with concrete data.
- TBD (Items 2-5)

**What Could Improve**:
- TBD

**Surprises**:
- Chain handling is a non-issue for the compiler (biggest simplification)
- `reconstruct_expression()` loses parentheses -- AST is the only correct path
- MIXED classification never occurs naturally; EXPOSE_PURE/EXPOSE_COMPUTED split is more precise
- TBD (Items 2-5)

---

**Last Updated**: 2026-02-08
**Next Action**: Execute Item 3 -- pipeline integration (computed attribute modules)
