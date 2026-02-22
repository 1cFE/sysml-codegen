# Phase 2 Checkpoint Audit — Action Items

**Audit date**: 2026-02-17
**Auditor**: Claude Opus 4.6 (Phase 2 checkpoint review)
**Scope**: All Phase 2 components (C08, C09, C10) + TRR validation + forward-looking Phase 3 impact

---

## A. Bookkeeping — Complete Before Committing Phase 2

> These are documentation/status accuracy fixes. No code changes.

- [x] **A1** — Check the Checkpoint 2 box in IMPLEMENTATION_PLAN.md. *(done 2026-02-17)*
- [x] **A2** — Update C08 `plan.md` status from `VALIDATE` to `DONE` *(done 2026-02-17)*
- [x] **A3** — Update TRR `plan.md` status from `VALIDATE` to `DONE` *(done 2026-02-17)*
- [x] **A4** — Check C01 AC7, AC9, AC10 in COMPONENT_CHECKLIST.md (AC8 deferred — field types not yet migrated) *(done 2026-02-17)*
- [x] **A5** — Check C27 ACs (all 9) in COMPONENT_CHECKLIST.md *(done 2026-02-17)*
- [x] **A6** — Stage all changes together for batch commit *(done 2026-02-17)*
- [x] **A7** — Complete the Commit (§7) sections in all 4 plan.md files *(done 2026-02-17)*

---

## B. Design Doc Amendments — Before Phase 3 Starts

> TRR validation found specific gaps in the design intent corpus.

- [x] **B1** — `04-input-resolver.md`: Added `CanonicalChannel` return type to strategy callable
  signature, Strategy A/B code examples, and cross-package alias lookup. *(done 2026-02-17)*

- [x] **B2** — `04-input-resolver.md:238`: Removed stale Key_A reference. Replaced with
  scope-qualification rationale that doesn't reference eliminated key format. *(done 2026-02-17)*

- [x] **B3** — `27-typed-registry-refactor.md`: Added §Transitional `_compat` Bridge subsection
  under §Typed Registries. Documents `_compat` dict purpose, visibility rules, and C11 removal
  timeline. *(done 2026-02-17)*

- [x] **B4** — Added Design Doc Amendments entries in IMPLEMENTATION_PLAN.md for B1/B2 and B3.
  *(done 2026-02-17)*

---

## C. Fixture Coverage Gaps — Require New SysML Fixture Models

> These gaps were identified across C03–C10. Each represents a code path that exists in
> production but has zero exercise from real SysML data. Currently tested only with
> constructed/synthetic data or not tested at all.

### CRITICAL: Expect Failures — Do Not Force Green Tests

**The purpose of closing these gaps is to DISCOVER latent bugs, not to produce passing
tests.** The pre-refactor implementation has known issues, and exercising previously-uncovered
code paths will surface them. C1 proved this pattern: extraction-level tests pass, but
**the full pipeline crashes** because the backtracker has no EXPRESSION dispatch path.

**Rules for agents working on C items:**

1. **Create the fixture model and capture the extraction snapshot.** Verify extraction-level
   conformance tests pass (the extractor is well-tested).
2. **Run the full pipeline** (`build_pipeline_context`) on the new fixture. **Expect it to
   fail.** Document the failure precisely — error message, stack trace location, root cause.
3. **Write conformance tests that verify the extraction-level behavior** (these should pass).
   Write additional tests that **document the pipeline-level failure as a known issue** using
   `pytest.mark.xfail(reason="...")` or `pytest.raises(...)` with a descriptive message.
4. **NEVER work around a pipeline failure to make tests green.** If the backtracker crashes,
   the graph builder produces wrong wiring, or the module factory mishandles a term — that is
   the finding. Document it, link it to the responsible phase (C11, C12, C16, etc.), and move on.
5. **Update IMPLEMENTATION_PLAN.md** with the finding so the responsible phase knows what to fix.
6. **Use `EXTRACTION_ONLY_MODELS`** in the capture script for models that can't complete the
   full pipeline (same pattern as C1's expression_binding_probe).

### C1. EXPRESSION Binding Type (identified in C03)

- **Gap**: ~~`BindingType.EXPRESSION` absent from all 6 fixture models.~~ **CLOSED.**
  Code path at `usage_extractor.py:559-566` now has full fixture coverage.
- **What it means**: An `in x = a + b` style inline expression binding in SysML. The extractor
  recognizes `OperatorExpression` nodes and classifies them as EXPRESSION, but no fixture model
  contained one.
- **Risk**: ~~Medium~~ **Mitigated** — 6 EXPRESSION bindings verified across 5 patterns.
- [x] **Action**: Created `tests/fixtures/expression_binding_probe/` (library.sysml + design.sysml).
  Captured extraction snapshot (extraction-only; full pipeline fails on EXPRESSION — see UPDATE below).
  Added 19 parametrized conformance tests to `test_extractor.py::TestExpressionBindingType`.
  Updated conftest.py, capture script. **1184 tests, 0 failures.**
- **Affected REQs**: REQ-EXT-02
- **Affected components**: C03 (extractor), C09 (VBR — EXPRESSION overrides silently skipped),
  C11 (backtracker — EXPRESSION binding dispatch path)

> **UPDATE (C1)**: The full pipeline (`build_pipeline_context`) crashes on EXPRESSION bindings
> because the backtracker has no dispatch path for `BindingType.EXPRESSION`. The error is:
> `ValueError: ADR-003 VIOLATION: No binding resolution for '...combined_input'`.
> This confirms the C11 scope note in D4 — the backtracker typed dispatch migration (C11)
> must add EXPRESSION binding handling. The capture script was refactored to support
> `EXTRACTION_ONLY_MODELS` for models that can't complete the full pipeline.
>
> **Patterns exercised**: (1) binary op with two refs (`material + labor`), (2) ref * literal
> (`material * 1.2`), (3) 3-term nested binary (`a + b + c`), (4) two EXPRESSION bindings on
> one CalcUsage, (5) subtraction (`material - overhead`). All 6 produce `BindingType.EXPRESSION`
> with `source_path=None`, `literal_value=None`, `expression_ast=None` (in snapshot — serialization boundary).
>
> **Learning**: UNBOUND params go into `CalcUsageData.unbound_params` (string list), not into
> `bindings` as BindingInfo with `BindingType.UNBOUND`. So the bindings list only ever contains
> 4 binding types: CHAIN, REFERENCE, LITERAL, EXPRESSION. All 4 now have fixture coverage.

### C2. CHAIN Design Overrides (identified in C09)

- **Gap**: ~~Zero `RedefinitionType.CHAIN` entries in `design_overrides` across all 6 fixture models.~~
  **CLOSED.** chain_override_probe has 1 CHAIN + 1 LITERAL design override.
- **What it means**: A design-level `:>>` that redirects a binding's source (e.g., override a
  template's `efficiency` input to read from a different upstream calc) rather than setting a
  literal value.
- **Risk**: ~~Medium~~ **Mitigated** — CHAIN override mutation path verified with real SysML data.
- [x] **Action**: Created `tests/fixtures/chain_override_probe/` (library.sysml + design.sysml).
  Model has 'Sensor' PartDef with template CalcUsage, 'Instrument Package' assembly with
  calibration calc, and design with `:>> sensitivity = calibration.calibrated_factor` (CHAIN).
  Captured extraction snapshot. Added 9 conformance tests to
  `test_virtual_binding_rewrite.py::TestChainOverrideFixtureCoverage`. **1194 tests, 0 failures.**
- **Affected REQs**: REQ-VBR-04
- **Affected components**: C09 (VBR)

> **UPDATE (C2)**: The CHAIN override is a flat (non-deep-path) override, unlike solar_battery's
> deep-path LITERAL overrides. SysML v2 `part redefines sensor : 'Sensor' { :>> sensitivity = calibration.calibrated_factor; }`
> produces a FeatureChainExpression at the redefinition level, classified as
> `RedefinitionType.CHAIN` with `source_path="calibration.calibrated_factor"`.
>
> **VBR behavior confirmed**: The rewrite replaces the binding's `source_path` with the override's
> `source_path`. The `binding_type` stays REFERENCE (unchanged). Post-rewrite snapshot shows
> `sensitivity.source_path = "calibration.calibrated_factor"` — exactly matching the code path at
> `initialization.py:329-331`.
>
> **SysML syntax learning**: `calc redefines` with overridden `in` bindings is rejected by SysIDE
> with `error (feature-value-overriding)`. Design-level CalcUsage overrides must use `:>>` on the
> owning PartUsage, not `calc redefines`.
>
> **Limitation**: This fixture exercises flat CHAIN overrides only. Deep-path CHAIN overrides
> (e.g., `:>> child.attr = sibling.output`) would require a 3-level PartDef hierarchy. The VBR
> code handles both via the same `_build_override_index` path, so this is low additional risk.

### C3. UNRESOLVABLE Computed Attribute Classification (identified in C05)

- **Gap**: ~~`ComputedAttributeClassification.UNRESOLVABLE` absent from all 6 fixture models.~~
  **PARTIALLY CLOSED.** UNRESOLVABLE remains untriggered (see UPDATE), but the probe revealed a
  **classifier misclassification bug** for inherited attributes — 5 of 6 patterns are wrongly
  classified as EXPOSE_COMPUTED instead of FORMULA.
- **What it means**: A PartDef attribute expression where the expression compiler cannot determine
  whether it references a CalcUsage output or a sibling attribute — the expression is structurally
  ambiguous.
- **Risk**: ~~Medium~~ **Confirmed** — the classifier has a real bug where inherited attributes
  from supertypes are misclassified because their QNs resolve to the supertype's namespace.
- [x] **Action**: Created `tests/fixtures/unresolvable_attr_probe/` (library.sysml + design.sysml).
  Model exercises PartDef-to-PartDef inheritance (`'Derived Component' :> 'Base Component'`) with
  computed attributes referencing inherited attributes. Captured extraction snapshot (extraction-only).
  Added 17 conformance tests to `test_computed_attributes.py::TestInheritedAttrClassification`
  (12 passed, 5 xfailed). Updated conftest.py, capture script, test_extractor.py expected counts.
  **1250 tests, 0 failures, 5 xfailed.**
- **Affected REQs**: REQ-CA-05, REQ-CA-01 (classification correctness)
- **Affected components**: C05 (computed attributes — classifier bug), C15 (FORMULA module factory
  — misclassified attrs never reach FORMULA path, so no downstream crash, just silent no-op)

> **UPDATE (C3)**: UNRESOLVABLE was NOT triggered. SysIDE always resolves inherited attribute QNs
> (to the supertype's namespace), so the empty-QN fallback path (Step 2d in
> `_classify_attribute_expression`) is never hit for valid SysML with inheritance. The UNRESOLVABLE
> code path may only be reachable through: (a) SysIDE bugs that produce empty QNs, (b) partially
> valid SysML that SysIDE tolerates, or (c) synthetic ExpressionRef data. It is likely **dead code**
> for any well-formed SysML model.
>
> **FINDING: Inherited Attribute Misclassification Bug.**
> - **Root cause**: SysIDE resolves inherited attribute QNs to the **supertype's namespace**
>   (e.g., `UnresolvableAttrProbeLibrary::'Base Component'::base_rate`), not the subtype's
>   (`UnresolvableAttrProbeLibrary::'Derived Component'::base_rate`).
> - **Classifier behavior**: Step 2b checks `qn.startswith(owning_part_qn + "::")`. For inherited
>   attrs, this fails because the QN starts with the supertype's prefix. The ref falls through to
>   Step 2c as a `calc_ref` (different namespace = treated as external CalcUsage output). This
>   pushes classification from FORMULA to EXPOSE_COMPUTED.
> - **Impact**: 5 of 6 test patterns are misclassified as EXPOSE_COMPUTED instead of FORMULA.
>   The 6th (D3: `my_calc.result * base_rate`) is correctly EXPOSE_COMPUTED because it genuinely
>   references a CalcUsage output (`result`).
> - **Practical consequence**: Computed attributes referencing inherited attrs silently produce
>   **no pipeline module** and **no compiled expression**. They appear in `computed_attributes`
>   but EXPOSE_COMPUTED is unhandled (Deferred Issue #2).
> - **Fix scope**: The classifier needs to walk the supertype chain when checking QN prefixes.
>   Instead of `qn.startswith(owning_part_qn + "::")`, check if the QN starts with ANY ancestor
>   PartDef's QN. This is a C05 classifier fix or Phase 7 refactor item.
> - **SysML syntax learning**: `part probe :> 'Base Component'` is INVALID for part usages —
>   `:>` expects a Feature, not a PartDefinition. The correct syntax for PartDef inheritance is
>   `part def 'Derived' :> 'Base'` (definition-to-definition). Part usages use `: 'Type'` typing.
>
> **Patterns exercised**: (L1) only inherited attrs in expression, (L2) mix inherited + local,
> (D1-D4) same patterns on design-side PartDef with CalcUsage. All 6 are on PartDefinitions.
> `owned_members` only includes locally-declared attributes, confirming that inherited attrs are
> NOT in `sibling_attr_names`.

### C4. EXPOSE_COMPUTED Pattern (identified in C05, Deferred Issue #2)

- **Gap**: ~~`ComputedAttributeClassification.EXPOSE_COMPUTED` is defined in the enum and
  documented in Doc 16, but no fixture model exercises it.~~ **PARTIALLY CLOSED.**
  attr_expr_probe D2 (`scaled_area = scale_calc.result * 2.0`) already exercises
  EXPOSE_COMPUTED. 1 genuine pattern verified; additional patterns (calc+sibling,
  multi-calc) remain unexercised.
- **What it means**: A PartDef attribute that mixes a CalcUsage output reference with arithmetic
  or sibling attributes. The expression contains `calc_refs` AND is not a pure
  `FeatureChainExpression` — so it's neither EXPOSE_PURE (simple alias) nor FORMULA
  (sibling-only). Pipeline effect: silent no-op (deferred per Deferred Issue #2).
- **Risk**: Low — ~~explicitly deferred as out-of-scope~~ **Mitigated** — extraction-level
  classification verified with real fixture data. Pipeline no-op is by design.
- [x] **Action**: ~~Defer.~~ Verified existing coverage. No new fixture needed.
- **Affected REQs**: (none currently — pattern is acknowledged but unspecified)
- **Affected components**: C05, C15 (FORMULA module factory)

> **UPDATE (C4)**: The gap description was overstated. `attr_expr_probe` D2
> (`scaled_area = scale_calc.result * 2.0`, line 104 in design.sysml) already produces
> `ComputedAttributeClassification.EXPOSE_COMPUTED` in the extraction snapshot. Existing
> conformance tests verify this:
>
> - `test_computed_attributes.py::test_classification_count` — expects exactly 1
>   EXPOSE_COMPUTED in attr_expr_probe
> - `test_computed_attributes.py::test_expose_computed_no_compilation` — verifies
>   EXPOSE_COMPUTED has `compiled_expression=None` and `compilability=MANUAL_REQUIRED`
> - `test_computed_attributes.py::test_classifications_present` — EXPOSE_COMPUTED in the
>   exercised classification set
>
> Additionally, C3's inherited attribute probe (unresolvable_attr_probe) produces 5
> EXPOSE_COMPUTED instances via misclassification — these are tested as xfailed expectations
> in `TestInheritedAttrClassification`.
>
> **Remaining gap**: Only 1 genuine EXPOSE_COMPUTED pattern exercised (calc output x literal).
> Untested patterns: (a) calc output + sibling attr, (b) calc output x sibling attr,
> (c) two calc outputs combined. These would require a new fixture model. Given the Low
> risk and explicit deferral of pipeline handling, this is acceptable technical debt.
>
> **Classification trace for D2**: `scale_calc.result * 2.0` →
> - `scale_calc` filtered by Step 2a (in `calc_usage_names`)
> - `result` QN resolves to `AttrExprProbeLibrary::ScaleCalc::result` → Step 2c (calc_ref)
> - `2.0` literal → no ref
> - Step 3: calc_refs present, no sibling_refs, but top-level AST is `OperatorExpression`
>   (not `FeatureChainExpression`) → EXPOSE_COMPUTED
>
> **No new fixture model required.** The gap is closed for classification verification
> purposes. Pipeline-level handling remains explicitly deferred (Deferred Issue #2).

### C5. REQ-HR-07 Alias Detection (identified in C06)

- **Gap**: ~~All aggregation expressions across all 6 fixture models have empty `aliases` lists.
  No CHAIN sibling redefinition has `source_path` ending with an aggregation `attribute_name`.
  The alias detection code at `hierarchy_resolver.py:550-557` is never exercised with real data.~~
  **CLOSED.** `alias_agg_probe` exercises the positive case: `:>> reported_cost = total_cost`
  detected as a CHAIN alias for the `sum(widget.total_cost)` aggregation.
- **What it means**: When a PartDef has an aggregation expression AND a sibling `:>>` CHAIN
  redefinition whose target is the aggregation attribute, the hierarchy resolver should detect
  this and populate the `aliases` field.
- **Risk**: ~~Medium~~ **Mitigated** — alias detection confirmed working with real SysML data.
  Full pipeline completes successfully with alias-based CalcUsage resolution.
- [x] **Action**: Created `tests/fixtures/alias_agg_probe/` (library.sysml + design.sysml).
  Model has abstract `'Costed Item'` base with `total_cost` + `reported_cost`, `'Widget'` leaf
  with CalcUsage, `'Widget Assembly'` with `sum()` aggregation + CHAIN alias + two CalcUsages
  (one binding direct, one through the alias). Captured extraction snapshot (full pipeline).
  Added 10 conformance tests to `test_hierarchy_resolver.py::TestAliasAggProbe` + 2 positive-case
  tests to `TestReqHr07AliasDetection`. **1260 tests, 0 failures, 5 xfailed.**
- **Affected REQs**: REQ-HR-07
- **Affected components**: C06 (hierarchy resolver), C10 (aggregation scoping — alias handling)

> **UPDATE (C5)**: The alias detection code at `hierarchy_resolver.py:550-557` works correctly.
> The model structure exercises:
>
> - **Aggregation**: `:>> total_cost = sum(widget.total_cost)` on `'Widget Assembly'`
>   produces `AggregationExpressionData` with `attribute_name="total_cost"`
> - **CHAIN alias**: `:>> reported_cost = total_cost` produces `RedefinitionType.CHAIN`
>   with `source_path="total_cost"` — alias detection matches via
>   `source_path.endswith(agg.attribute_name)` and appends `"reported_cost"` to `agg.aliases`
> - **Direct CalcUsage binding**: `margin_calc { in cost_basis = total_cost; }` binds
>   directly to the aggregation output (REFERENCE binding)
> - **Alias CalcUsage binding**: `report_calc { in cost_input = reported_cost; }` binds
>   through the CHAIN alias (REFERENCE binding to alias attribute)
>
> **Full pipeline succeeds** with 4 modules in correct topological order:
> `cost_model → total_cost (agg) → margin_calc → report_calc`
>
> **Multiplicity note**: `widget : 'Widget' [3]` uses literal multiplicity (no count attribute),
> producing `MultiplicityData(count=3, count_attribute_name=None)`. Same pattern as issue22.
> The `sum()` walker logs a warning about missing multiplicity data but still creates the
> SumTerm (with `multiplicity_attr=None`, `multiplicity_count=None`).
>
> **Potential edge case (not exercised)**: The `endswith()` check in alias detection could
> false-positive on dotted paths like `source_path="child.total_cost"` matching
> `attribute_name="total_cost"`. This would incorrectly alias a child reference as an
> aggregation alias. No fixture exercises this — documented as future edge case for C10 or
> Phase 7 if needed.

### C6. Deeply-Nested Cross-Scope REFERENCE (Deferred Issue #7)

- **Gap**: No fixture model contains a REFERENCE binding that crosses scope boundaries through
  deep nesting (e.g., `Design::SubSystem::Component::calc` referencing
  `OtherDesign::OtherSubSystem::output`). **PARTIALLY ADDRESSED.** Fixture model created with
  3 binding patterns; snapshot capture pending SysIDE validation.
- **What it means**: A binding that references an output deep inside another part's hierarchy
  (4+ levels of containment), using either dotted feature chains (CHAIN) or qualified-name
  `::` paths (REFERENCE). The backtracker's Step 1b normalization extracts only the last 2
  segments of a `::` QN, potentially losing intermediate hierarchy context for deep paths.
- **Risk**: Low → **Medium (conditional)** — if SysIDE accepts the deep `::` syntax (Pattern B),
  the Step 1b normalization will demonstrably fail for 5+ segment QNs. If SysIDE rejects it,
  the risk remains low because deep cross-scope references naturally use `.` chains (CHAIN bindings)
  which don't hit the Step 1b code path.
- [x] **Action**: Created `tests/fixtures/deep_cross_scope_probe/` (library.sysml + design.sysml).
  Model has 3-level producer nesting (Station > Array > Sensor > CalcUsage) and 3 consumer binding
  patterns testing different depths and notations. **Snapshot capture pending** — requires SysIDE
  JVM parser to validate syntax and extract binding types.
- **Affected REQs**: REQ-BT-08 (type-directed dispatch), REQ-DRA-01 (resolution consistency)
- **Affected components**: C11 (backtracker — Step 1b normalization), C12 (input resolver —
  deep ScopedKey construction)

> **UPDATE (C6)**: Created `deep_cross_scope_probe` fixture with 3 binding patterns:
>
> **Pattern A — Deep CHAIN (4-level dot chain):**
> `in data_point = station.array.derived.derived_value;`
> - Expected: `BindingType.CHAIN`, `source_path = "station.array.derived.derived_value"`
> - Tests: Deep dotted path resolution through `scoped_lookup()`. Similar to existing
>   catf_mfe patterns (`catf_tf_system.cooling_power`), but 4 levels instead of 2.
> - **Expected outcome**: May succeed if OutputRegistry ScopedKey includes the full
>   dotted path from design root. The ScopedKey for the `derived` calc's output would be
>   `station.array.derived` (from EQN after design prefix strip). The source_path
>   `station.array.derived.derived_value` includes the attribute suffix — resolution depends
>   on how the backtracker decomposes dotted CHAIN paths.
>
> **Pattern B — Deep REFERENCE (6-segment QN with `::`):**
> `in data_point = measurement_system::station::array::sensor::core::metric_value;`
> - Expected: `BindingType.REFERENCE`, source_path with 6 `::` segments
> - Tests: Step 1b normalization bug. For 6-segment path, Step 1b extracts
>   `parts[-2] = "core"`, `parts[-1] = "metric_value"`, producing `dotted = "core.metric_value"`.
>   The actual ScopedKey in OutputRegistry would be `station.array.sensor.core` (full instance
>   path from design root, prefix-stripped). So `core.metric_value` would NOT match.
> - **Expected outcome**: Resolution FAILS — falls through to entry_point. This demonstrates
>   the Step 1b limitation for deeply nested QNs.
> - **SysIDE syntax risk**: `::` navigation through parts (not just packages) works for
>   2-segment self-refs (catf_mfe: `catf_physics::p_fusion`). 6-segment navigation through
>   nested parts is untested. SysIDE may reject, normalize, or parse it differently.
>
> **Pattern C — Shallow REFERENCE (2-segment self-ref, control):**
> `in data_point = analyzer::baseline_value;`
> - Expected: `BindingType.REFERENCE`, 2-segment self-reference
> - Tests: Baseline — this pattern is known to work (catf_mfe precedent).
> - **Expected outcome**: Resolution succeeds (or falls to entry_point as expected for
>   a self-reference to a non-output attribute).
>
> **Step 1b Normalization Analysis:**
> The current code at `_resolve_binding_via_registry()` does:
> ```python
> parts = source_path.split("::")
> sanitized_part = sanitize_name(parts[-2]).lower()
> dotted = f"{sanitized_part}.{parts[-1]}"
> channel = self._output_registry.resolve(dotted)
> ```
> For a 6-segment path `A::B::C::D::E::F`, this extracts only `E.F`, discarding the
> intermediate nesting `B::C::D`. For typed dispatch (C11b), the fix would be to construct
> a full `ScopedKey` from ALL intermediate segments, not just the last 2.
>
> **Next steps**: Capture extraction snapshot (requires SysIDE JVM). If Pattern B is accepted
> by SysIDE, write conformance tests documenting the Step 1b failure. If rejected, document
> as a SysML syntax limitation and note that deep cross-scope references naturally use `.`
> chains (which bypass Step 1b entirely).
>
> **Learning**: In SysML v2, `::` navigates the ownership/namespace hierarchy while `.`
> navigates feature chains. Cross-scope bindings in catf_mfe use import + `.` (producing
> CHAIN), not deep `::` paths (REFERENCE). The idiomatic SysML v2 pattern for cross-scope
> references is `private import Package::part_instance; in x = part_instance.attr;` —
> which produces CHAIN bindings. Deep `::` REFERENCE bindings may be an edge case that
> only arises from non-idiomatic SysML authoring or programmatic model generation.

### Summary: Fixture Model Creation Plan

| Priority | New Fixture Model | Gaps Closed | Effort | Status |
|----------|-------------------|-------------|--------|--------|
| 1 (High) | `expression_binding_probe.sysml` | C1 (EXPRESSION binding) | Medium | **DONE** |
| 2 (High) | `chain_override_probe.sysml` | C2 (CHAIN design override) | Medium | **DONE** |
| 3 (Medium) | `unresolvable_attr_probe.sysml` | C3 (inheritance misclassification — UNRESOLVABLE untriggered) | Medium | **DONE** |
| 4 (Medium) | `alias_agg_probe` (new fixture) | C5 (HR-07 aliases) | Medium | **DONE** |
| 5 (Low) | N/A — existing attr_expr_probe D2 | C4 (EXPOSE_COMPUTED) | N/A | **CLOSED** (existing coverage) |
| 6 (Low) | `deep_cross_scope_probe` (new fixture) | C6 (deep cross-scope REFERENCE + CHAIN) | Medium | **CREATED** (snapshot pending) |

**Dependency**: Creating new fixture models requires the SysIDE JVM parser (`agentic-mbse`
SysideAdapter). The extraction snapshot capture script (`scripts/capture_extraction_snapshots.py`)
handles serialization once extraction is run. New snapshots must be added to
`tests/fixtures/{model}/extraction_snapshot.json`.

---

## D. Technical Debt — Address in Phase 3 or Phase 7

### D1. `_compat` Bridge and `resolve()` Migration Path

- **Issue**: Three `registry.resolve()` calls in `build_output_registry()` (Phases 2/3/4) depend
  on Key_A-format canonical names living in `_compat`. These cannot simply switch to
  `scoped_lookup()` because the canonical_name values use `instance_name.attr` format (Key_A),
  not the `design_prefix_stripped.path.attr` format (Key_C/ScopedKey).
- **Impact on C11**: The backtracker's typed dispatch migration (C11) must ALSO address these
  `build_output_registry()` calls, or a separate refactoring step is needed.
- [x] **Action**: Added D1 spike question with 3 options (a/b/c) to IMPLEMENTATION_PLAN §3.1b
  C11b scope. Also documented in C11a plan Issue #1. *(done 2026-02-17)*

### D2. Pre-existing Ruff Errors

- **Issue**: 19 ruff errors across `src/` (7 auto-fixable I001 import sorting, 12 E501/UP037).
  None in Phase 2 modified files. Plan.md files claim "lint clean" which is inaccurate for the
  full tree.
- [ ] **Action**: Run `uv run ruff check src/ --fix` to resolve the 7 auto-fixable I001 errors.
  Consider addressing E501 line-length violations in a separate cleanup commit. Update plan.md
  "lint clean" claims to scope them to modified files only.

### D3. Static Analysis Helpers Duplication

- **Issue**: C04, C06, and C07 each have copies of `_find_is_instance_calls_in_function` and
  `_is_*_is_instance_call` helpers. C07 Learning #4 says "if a fourth copy appears, extract to
  `tests/helpers/static_analysis.py`."
- [x] **Action**: Extracted to `tests/helpers/static_analysis.py`. Module exports
  `find_is_instance_calls_in_function` (with configurable predicate parameter),
  `is_syside_is_instance_call`, `is_any_is_instance_call`, `find_comment_near_line`,
  and `find_all_dispatch_functions`. Updated C04, C06, C07 to import from shared module.
  1273 tests pass. *(done 2026-02-17)*

### D4. C11 Scope Expansion Warning

- **Issue**: IMPLEMENTATION_PLAN §3.1 describes C11 as "DependencyBacktracker Conformance" but
  the actual scope now includes: (a) backtracker typed dispatch, (b) `_compat` dict elimination,
  (c) Phase 2/3/4 `resolve()` migration in `build_output_registry()`, (d) catf_mfe cross-package
  resolution patterns.
- [x] **Action**: Split IMPLEMENTATION_PLAN §3.1 into §3.1a (C11a conformance, done) and §3.1b
  (C11b typed dispatch migration + `_compat` removal). Updated Checkpoint 3, TRR impact table,
  and Phase 7.4 to move 3 dead code items to C11b. *(done 2026-02-17)*

---

## E. TRR Validation Criteria — Remaining Items

> Criteria 5–7 from IMPLEMENTATION_PLAN §Phase TRR were not fully audited.

- [ ] **E1** — Criterion 5: Systematic REQ cross-reference audit. For each REQ-XX-NN cited in
  a conformance test or component plan, verify it exists in its home design doc. Spot-check
  found no issues but a full sweep has not been done.
- [ ] **E2** — Criterion 6: Confirm typed identifiers used consistently. `04-input-resolver.md`
  gap found (0 `CanonicalChannel`). Other docs verified clean.
- [ ] **E3** — Criterion 7: No orphan requirement references. Requires comparing all `REQ-*`
  strings in conformance tests against design doc definitions. Not yet done systematically.

---

## Progress Tracking

| Date | Items Completed | By |
|------|----------------|----|
| 2026-02-17 | Audit performed, action items written | Phase 2 checkpoint review |
| 2026-02-17 | Section A complete (A1–A7), committed | Phase 2 checkpoint review |
| 2026-02-17 | C1 — EXPRESSION binding fixture + 19 conformance tests (1184 total) | C1 implementation |
| 2026-02-17 | Section B complete (B1–B4), design docs amended | Phase 2 checkpoint review |
| 2026-02-17 | C3 — Inherited attr misclassification bug found + 17 conformance tests (1250 total, 5 xfail) | C3 implementation |
| 2026-02-17 | C3 design doc amendments: Doc 16 (Known Issues + algorithm annotations), Doc 09 (enum footnote), Doc 01 (supertype chain data gap), COMPONENT_CHECKLIST (C03/C05 new ACs), IMPLEMENTATION_PLAN (Deferred Issues #9/#10 + amendments table) | C3 design doc propagation |
| 2026-02-17 | D1 — Added spike question with 3 options to IMPLEMENTATION_PLAN §3.1b C11b scope | D1 completion |
| 2026-02-17 | C4 — EXPOSE_COMPUTED gap overstated; existing attr_expr_probe D2 already exercises it. 1 genuine pattern verified with existing conformance tests. No new fixture needed. | C4 audit |
| 2026-02-17 | C5 — REQ-HR-07 alias detection: created alias_agg_probe fixture + 10 conformance tests (1260 total). Alias detection works correctly. Full pipeline succeeds with alias-based resolution. | C5 implementation |
| 2026-02-17 | C6 — Deep cross-scope probe: created `deep_cross_scope_probe/` fixture with 3 binding patterns (deep CHAIN, deep REFERENCE, shallow REFERENCE control). Identified Step 1b normalization limitation for 5+ segment QNs. Snapshot pending SysIDE validation. | C6 implementation |
