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

- **Gap**: `ComputedAttributeClassification.EXPOSE_COMPUTED` is defined in the enum and
  documented in Doc 16, but no fixture model exercises it.
- **What it means**: A PartDef attribute that exposes a computed value from a child PartUsage
  (not a simple alias like EXPOSE_PURE, but an expression over computed values).
- **Risk**: Low — explicitly deferred as out-of-scope (Deferred Issue #2). No production code
  path exercises it either.
- [ ] **Action**: Defer. Document in the fixture gap tracker below. Revisit when a real model
  needs EXPOSE_COMPUTED.
- **Affected REQs**: (none currently — pattern is acknowledged but unspecified)
- **Affected components**: C05, C15 (FORMULA module factory)

### C5. REQ-HR-07 Alias Detection (identified in C06)

- **Gap**: All aggregation expressions across all 6 fixture models have empty `aliases` lists.
  No CHAIN sibling redefinition has `source_path` ending with an aggregation `attribute_name`.
  The alias detection code at `hierarchy_resolver.py:550-557` is never exercised with real data.
- **What it means**: When a PartDef has an aggregation expression AND a sibling `:>>` CHAIN
  redefinition whose target is the aggregation attribute, the hierarchy resolver should detect
  this and populate the `aliases` field.
- **Risk**: Medium — if the alias detection logic has a bug, aggregation inputs could silently
  fail to wire through CHAIN aliases, causing incorrect pipeline wiring for models that use
  this pattern.
- [ ] **Action**: Create a fixture model (could extend `issue22_model`) where a PartDef has
  both an aggregation expression (e.g., `total_cost = sum(children.cost)`) and a CHAIN
  redefinition on a sibling PartUsage that targets the aggregation attribute. Capture snapshot.
  Add conformance test to `test_hierarchy_resolver.py` verifying non-empty `aliases`.
- **Affected REQs**: REQ-HR-07
- **Affected components**: C06 (hierarchy resolver), C10 (aggregation scoping — alias handling)

### C6. Deeply-Nested Cross-Scope REFERENCE (Deferred Issue #7)

- **Gap**: No fixture model contains a REFERENCE binding that crosses scope boundaries through
  deep nesting (e.g., `Design::SubSystem::Component::calc` referencing
  `OtherDesign::OtherSubSystem::output`).
- **Risk**: Low — explicitly out of scope (Deferred Issue #7). Not observed in any tested model.
- [ ] **Action**: Defer. Track in fixture gap list. Only address if a real model triggers this.

### Summary: Fixture Model Creation Plan

| Priority | New Fixture Model | Gaps Closed | Effort | Status |
|----------|-------------------|-------------|--------|--------|
| 1 (High) | `expression_binding_probe.sysml` | C1 (EXPRESSION binding) | Medium | **DONE** |
| 2 (High) | `chain_override_probe.sysml` | C2 (CHAIN design override) | Medium | **DONE** |
| 3 (Medium) | `unresolvable_attr_probe.sysml` | C3 (inheritance misclassification — UNRESOLVABLE untriggered) | Medium | **DONE** |
| 4 (Medium) | Extend `issue22_model` or new fixture | C5 (HR-07 aliases) | Medium | Pending |
| 5 (Low) | Defer | C4 (EXPOSE_COMPUTED), C6 (deep cross-scope) | N/A | Deferred |

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
- [ ] **Action**: Add a spike question to C11 plan: "How do Phase 2/3/4 alias registration
  calls in `build_output_registry()` migrate away from `resolve()` when canonical_name values
  are in Key_A format?" Options: (a) Convert Key_A canonical_names to ScopedKey during alias
  construction, (b) Register Key_A values as scoped keys during Phase 1, (c) Keep `_compat`
  for alias registration only and eliminate it for resolution.

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
- [ ] **Action**: Monitor during Phase 3. If C11 or C12 need static analysis helpers, extract
  to shared location.

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
