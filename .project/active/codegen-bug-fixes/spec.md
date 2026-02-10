# Spec: Codegen Bug Fixes (E2E Validation Findings)

**Status:** Complete
**Owner:** Reid Westwood
**Created:** 2026-02-10 04:31 UTC
**Complexity:** MEDIUM
**Branch:** cost-pattern

---

## Business Goals

### Why This Matters

During E2E validation of Phases 1+2 (EXPR-CODEGEN + ATTR-EXPR) in the fusion-tea project, 7 codegen bugs were discovered requiring manual workarounds to produce correct pipeline output. These bugs mean that codegen cannot produce clean, executable pipelines without human intervention — defeating the purpose of automated code generation.

These fixes are a **blocking prerequisite** for the COST-PATTERN epic (P1), which will introduce deeper hierarchy, multiplicity, and aggregation patterns. If the existing computed attribute and module generation paths have bugs, Phase 3 work will compound them.

### Success Criteria

- [ ] Running codegen on the e2e_attr_expr model produces a correct, executable pipeline with **zero manual workarounds** — all 16 ground truth values pass
- [ ] Running codegen on the solar_battery model produces correct output with **zero manual workarounds** — all 7 verification metrics pass
- [ ] All 7 bugs verified fixed through automated tests (unit + integration)
- [ ] All existing tests pass with zero regressions (285+ baseline)

### Priority

**P0** — Blocking prerequisite for COST-PATTERN epic. Must be completed before Item 1 of the COST-PATTERN backlog begins implementation.

---

## Problem Statement

### Current State

Codegen produces structurally incomplete or incorrect output for models using computed attributes (FORMULA, EXPOSE_PURE) and multi-output CalcUsages. The E2E validation on e2e_attr_expr required 4 manual workarounds (modified schema, pipeline YAML, module wrappers, and exit point configuration). The solar_battery regeneration required 3 additional manual fixes (missing `__init__.py`, broken Python identifiers, stubs not upgraded).

All 7 bugs are documented with root cause analysis:
- `.project/research/20260210-040346_e2e-codegen-bug-root-cause-analysis.md` (Bugs 1-4)
- `.project/research/20260210-042253_phase4-additional-bugs-root-cause-analysis.md` (Bugs 5-7)

### Desired Outcome

Codegen produces correct, complete, executable pipeline output for all existing model patterns — including FORMULA computed attributes, EXPOSE_PURE aliases, multi-output CalcUsages, and models with special characters in SysML names — without any manual intervention.

---

## Scope

### In Scope

All 7 bugs identified during E2E validation, organized by subsystem:

**Backtracker / Graph Builder (Bugs 1-2):**
1. **Bug 1: FORMULA entry point omission** — FORMULA module inputs MUST appear in DesignParams schema and JSON
2. **Bug 2: FORMULA/EXPOSE backtracker wiring** — CalcUsage bindings to FORMULA/EXPOSE attributes MUST resolve as MODULE_OUTPUT, not ENTRY_POINT

**Module Generation (Bug 3):**
3. **Bug 3: FORMULA module input type mismatch** — FORMULA module input types MUST use `float` (matching CalcUsage convention), not `Float` (RootModel[float])

**Exit Point / Output Serialization (Bug 4):**
4. **Bug 4: ExitPoint float write handler missing** — Multi-output CalcUsage `float` channels MUST be serializable to JSON by the generated pipeline

**Smart Regeneration (Bug 5):**
5. **Bug 5: `--smart-regen` stub-to-auto-impl upgrade** — When a stub (`raise NotImplementedError`) exists and an auto-implementation is available (FULLY_COMPILABLE), `--smart-regen` MUST upgrade the stub rather than preserving it

**Name Sanitization (Bug 6):**
6. **Bug 6: Special characters in Python identifiers** — `sanitize_name()` MUST produce valid Python identifiers for all SysML names, including those with `&`, `$`, `@`, `-`, and other special characters

**Package Structure (Bug 7):**
7. **Bug 7: Missing intermediate `__init__.py`** — All intermediate directories in generated package paths MUST contain `__init__.py` files

### Out of Scope

- COST-PATTERN epic work (hierarchy, multiplicity, aggregation, `:>>` chains)
- TEAx runtime changes
- agentic-mbse / SysIDE changes
- New model creation (use existing e2e_attr_expr and solar_battery models for validation)
- Performance optimization

### Edge Cases & Considerations

- Bug 2 has two distinct failure modes (FORMULA bindings via `::` key mismatch, EXPOSE_PURE bindings via missing index) — both MUST be fixed
- Bug 4 has prior art in fusion_modeling (2024-12-24) establishing that multi-output channels carry bare primitives and the fix is a primitive write handler — design SHOULD validate this approach still applies
- Bug 5 must distinguish stubs from hand-written implementations — `raise NotImplementedError` is the definitive stub marker vs `AUTO_IMPLEMENTED = True` for machine-generated code
- Bug 6 underscore collapsing MUST NOT affect the `__` ADR-003 hierarchy separator (sanitization applies to individual name segments, not qualified names)
- Bug 7 fix SHOULD address all 4 namespace-creating functions (including latent bugs in `_generate_modules` and `_generate_stencils` that will manifest during COST-PATTERN)

---

## Requirements

### Functional Requirements

> Requirements below are from the fusion-tea E2E validation findings and root cause analysis reports.

**Bug 1: FORMULA Entry Point Omission**

1. **FR-1**: Entry points created by FORMULA computed attribute modules MUST be included in the appropriate `ParameterGroup` and appear in generated schema files and JSON templates.
2. **FR-2**: The generated `DesignParams` schema for e2e_attr_expr MUST contain all 7 FORMULA module input parameters (e.g., `quantity`, `unit_cost`, `area_m2`, etc.) without manual addition.

**Bug 2: FORMULA/EXPOSE Backtracker Wiring**

3. **FR-3**: CalcUsage bindings that reference FORMULA computed attributes (e.g., `energy.power_mw`, `lcoe.annual_om`) MUST resolve as MODULE_OUTPUT references to the upstream FORMULA synthetic module, not as ENTRY_POINT parameters.
4. **FR-4**: CalcUsage bindings that reference EXPOSE_PURE attributes (e.g., `financial.total_capex`) MUST resolve as MODULE_OUTPUT references (directly or transitively), not as ENTRY_POINT parameters.
5. **FR-5**: The binding resolution MUST work regardless of SysML qualified name format (`::` separators, dotted paths, bare names).

**Bug 3: FORMULA Module Input Type Mismatch**

6. **FR-6**: FORMULA computed attribute module wrappers MUST use `float` (Python primitive) for input types, consistent with CalcUsage module conventions.
7. **FR-7**: FORMULA module output types MUST remain `Float` (RootModel[float]) — the bug is input-only.

**Bug 4: ExitPoint Float Write Handler**

8. **FR-8**: Generated pipelines with multi-output CalcUsage modules MUST include a primitive write handler capable of serializing bare `float` (and `int`) values to JSON files.
9. **FR-9**: Single-output modules MUST continue to use `RootModel[float]` with the existing JSON model writer — the type asymmetry is correct by design.

**Bug 5: Smart-Regen Stub Upgrade**

10. **FR-10**: When `--smart-regen` is active and an existing stencil is a stub (contains `raise NotImplementedError`), AND a FULLY_COMPILABLE auto-implementation is available, the stub MUST be upgraded to the auto-implementation.
11. **FR-11**: Hand-written implementations (no `raise NotImplementedError`, no `AUTO_IMPLEMENTED = True`) MUST continue to be preserved by `--smart-regen`.
12. **FR-12**: Auto-implemented files (containing `AUTO_IMPLEMENTED = True`) MUST continue to be preserved when signatures are unchanged.

**Bug 6: Special Character Sanitization**

13. **FR-13**: `sanitize_name()` MUST replace all non-alphanumeric, non-underscore characters with underscores, producing valid Python identifiers for any SysML name.
14. **FR-14**: The solar_battery model's `Racking_&_Mounting` part MUST produce importable Python code after codegen (no SyntaxError).
15. **FR-15**: The duplicate `_sanitize_name()` method in `extraction/extractor.py` MUST be eliminated. All call sites MUST use the canonical `sanitize_name()` from `core/qualified_names.py`.

**Bug 7: Intermediate `__init__.py` Files**

16. **FR-16**: All directories in generated module and stencil package paths MUST contain `__init__.py` files, including intermediate directories created by `mkdir(parents=True)`.
17. **FR-17**: The fix MUST apply to all 4 namespace-creating functions (`_generate_modules`, `_generate_computed_attr_modules`, `_generate_stencils`, `_generate_computed_attr_stencils`) to prevent latent bugs from manifesting during COST-PATTERN.

---

## Acceptance Criteria

### Per-Bug Verification

- [ ] **Bug 1**: e2e_attr_expr codegen produces `design_params.py` schema containing all 7 FORMULA input parameters without manual addition
- [ ] **Bug 2**: e2e_attr_expr pipeline.yaml shows `energy.power_mw`, `lcoe.annual_om`, and `financial.total_capex` inputs wired to upstream module outputs (not entry points)
- [ ] **Bug 3**: All FORMULA module wrapper Input classes use `float` type for inputs (not `Float`/`RootModel[float]`)
- [ ] **Bug 4**: e2e_attr_expr pipeline executes end-to-end including multi-output channel serialization to JSON (no manual exit_point workarounds)
- [ ] **Bug 5**: Solar battery `--smart-regen` upgrades stubs to auto-impl when FULLY_COMPILABLE; hand-written files preserved
- [ ] **Bug 6**: `sanitize_name("Racking_&_Mounting")` produces a valid Python identifier; solar_battery schema generates importable code; duplicate `_sanitize_name()` in extractor.py eliminated
- [ ] **Bug 7**: Solar battery codegen produces `__init__.py` in `modules/solarbatterydesign/` (intermediate directory)

### E2E Validation (Zero Manual Workarounds)

- [ ] e2e_attr_expr model: codegen → pipeline execution → all 16 ground truth values pass — with zero manual file modifications
- [ ] solar_battery model: codegen → pipeline execution → all 7 verification metrics pass — with zero manual file modifications

### Quality & Integration

- [ ] All existing tests pass with zero regressions (285+ baseline)
- [ ] New unit tests for each bug fix
- [ ] `uv run mypy src/` passes
- [ ] `uv run ruff check src/` passes

### Design Phase Validation

- [ ] Design phase MUST validate each proposed fix from the root cause analysis reports against the actual codebase before implementation (the reports were written by an AI researcher and may contain line number drift or incorrect assumptions)
- [ ] Design phase MUST identify any inter-bug dependencies (e.g., Bug 2 fix may affect Bug 1 behavior)

---

## Related Artifacts

- **Research (Bugs 1-4):** `.project/research/20260210-040346_e2e-codegen-bug-root-cause-analysis.md`
- **Research (Bugs 5-7):** `.project/research/20260210-042253_phase4-additional-bugs-root-cause-analysis.md`
- **Fusion-tea validation plan:** `/home/reid/1cfe/fusion-tea/.project/active/e2e-attr-expr-validation/plan.md`
- **Epic (downstream):** `.project/backlog/epic_costed_component_pattern.md`
- **Design:** `.project/active/codegen-bug-fixes/design.md` (to be created)

---

**Next Steps:** After approval, proceed to `/_my_design`
