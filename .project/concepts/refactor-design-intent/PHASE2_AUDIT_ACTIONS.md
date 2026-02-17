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

- [ ] **B1** — `04-input-resolver.md`: Add `CanonicalChannel` to resolution strategy return types.
  Currently 0 occurrences of `CanonicalChannel` in this doc. Strategies resolve inputs to
  upstream output channels — the return type should be `CanonicalChannel | None`, not bare `str`.
  All other TRR-amended docs (03, 09, 10, 11, 15, 24, 27) use this type.

- [ ] **B2** — `04-input-resolver.md:238`: Review Key_A reference. Determine if it's retained
  rationale ("scoped registry should not contain Key_A") or stale text. If rationale, add
  context note. If stale, remove.

- [ ] **B3** — `27-typed-registry-refactor.md`: Add `_compat` bridge dict to §Typed Registries
  or a new §Transitional Architecture section. C08 Learning #1 identified this as a needed
  update. The `_compat` dict holds legacy keys (Key_A, Key_D, Key_F, bare) visible only to
  the deprecated `resolve()`, invisible to typed lookups. Eliminated in C11.

- [ ] **B4** — Add a Design Doc Amendments entry in IMPLEMENTATION_PLAN.md for the `_compat`
  deviation: `| 27-typed-registry-refactor.md | Add _compat bridge dict note | C08 conformance — dead keys load-bearing through backtracker (2026-02-17) | No |`

---

## C. Fixture Coverage Gaps — Require New SysML Fixture Models

> These gaps were identified across C03–C10. Each represents a code path that exists in
> production but has zero exercise from real SysML data. Currently tested only with
> constructed/synthetic data or not tested at all.

### C1. EXPRESSION Binding Type (identified in C03)

- **Gap**: `BindingType.EXPRESSION` absent from all 6 fixture models. Code path at
  `usage_extractor.py:557-564` has zero fixture coverage.
- **What it means**: An `in x = a + b` style inline expression binding in SysML. The extractor
  recognizes `OperatorExpression` nodes and classifies them as EXPRESSION, but no fixture model
  contains one.
- **Risk**: Medium — if the classification logic has a latent bug, it won't surface until a
  real model uses inline expression bindings.
- [ ] **Action**: Create a new fixture model (e.g., `expression_binding_probe`) containing at
  least one CalcUsage with an `OperatorExpression` binding (e.g., `in cost = material + labor`).
  Capture extraction snapshot. Add parametrized conformance tests to `test_extractor.py` verifying
  EXPRESSION classification.
- **Affected REQs**: REQ-EXT-02
- **Affected components**: C03 (extractor), C09 (VBR — EXPRESSION overrides silently skipped),
  C11 (backtracker — EXPRESSION binding dispatch path)

### C2. CHAIN Design Overrides (identified in C09)

- **Gap**: Zero `RedefinitionType.CHAIN` entries in `design_overrides` across all 6 fixture models.
  All overrides are LITERAL. C09 tested CHAIN override path with constructed data only.
- **What it means**: A design-level `:>>` that redirects a binding's source (e.g., override a
  template's `efficiency` input to read from a different upstream calc) rather than setting a
  literal value.
- **Risk**: Medium — the CHAIN override mutation path (`source_path` replacement at
  `initialization.py:328-331`) is only verified with synthetic data using real names.
- [ ] **Action**: Create a fixture model (could be added to `expression_binding_probe` or a
  separate `chain_override_probe`) containing a template CalcDef with a REFERENCE binding, a
  design PartUsage that instantiates it, and a `:>>` override of type CHAIN pointing to a
  different upstream output. Capture snapshot. Add conformance tests to
  `test_virtual_binding_rewrite.py`.
- **Affected REQs**: REQ-VBR-04
- **Affected components**: C09 (VBR)

### C3. UNRESOLVABLE Computed Attribute Classification (identified in C05)

- **Gap**: `ComputedAttributeClassification.UNRESOLVABLE` absent from all 6 fixture models. Code
  path exists and is unit-tested with mock data, but no real SysML model produces it.
- **What it means**: A PartDef attribute expression where the expression compiler cannot determine
  whether it references a CalcUsage output or a sibling attribute — the expression is structurally
  ambiguous.
- **Risk**: Low — UNRESOLVABLE is a fallback/error classification. The code correctly logs a
  warning and skips module/alias creation. The risk is that the detection heuristic has false
  negatives (classifying ambiguous expressions as something else).
- [ ] **Action**: Create a fixture model attribute expression that is genuinely ambiguous (e.g.,
  references a name that exists as both a CalcUsage output and a sibling attribute, or references
  a non-existent name). Add to `expression_binding_probe` or `attr_expr_probe`. Capture snapshot.
  Add conformance test to `test_computed_attributes.py`.
- **Affected REQs**: REQ-CA-05
- **Affected components**: C05 (computed attributes)

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

| Priority | New Fixture Model | Gaps Closed | Effort |
|----------|-------------------|-------------|--------|
| 1 (High) | `expression_binding_probe.sysml` | C1 (EXPRESSION binding), potentially C3 (UNRESOLVABLE) | Medium — needs SysML authoring + JVM extraction |
| 2 (High) | `chain_override_probe.sysml` | C2 (CHAIN design override) | Medium — needs design-level `:>>` with CHAIN type |
| 3 (Medium) | Extend `attr_expr_probe` or new fixture | C3 (UNRESOLVABLE), C5 (HR-07 aliases) | Medium |
| 4 (Low) | Defer | C4 (EXPOSE_COMPUTED), C6 (deep cross-scope) | N/A |

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
- [ ] **Action**: Update IMPLEMENTATION_PLAN §3.1 description to note expanded scope. Add a
  note that C11 may need to be split into C11a (conformance tests on current behavior) and C11b
  (typed dispatch migration + `_compat` removal).

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
