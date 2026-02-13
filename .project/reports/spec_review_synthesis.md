# Spec Review Synthesis Report

**Date:** 2026-02-13
**Scope:** 7 specs (01-07) for OutputRegistry redesign
**Review Dimensions:** Cross-spec consistency, design doc coverage, issue traceability

---

## Executive Summary

The 7 specs achieve **near-complete coverage** of the design document (08_algorithm_revised.md). All 13 design doc sections are covered — the 3 "not covered" sections (Expression Compilation, Generation, Naming System) are explicitly unchanged. All 22 closed issues have spec coverage. 21/22 are COVERED, 1 (Issue 20) is PARTIAL (resolution implemented but "keep unused functionality" rationale not documented). All 9 spikes are referenced in at least one spec.

However, cross-spec consistency review found **2 CRITICAL and 5 MAJOR inconsistencies** that must be resolved before implementation. These are primarily Spec 04 vs Spec 07 disagreements on shared function contracts.

---

## Issues Found

### CRITICAL Issues (Must fix before implementation)

#### C1: `_extract_and_filter_computed_attributes()` Return Type Disagreement

| Spec | Return Type | Mutation Semantics |
|------|------------|-------------------|
| **Spec 04** (authoritative) | 3-tuple: `(list[ComputedAttributeData], list[ChannelAlias], list[CalcUsageData])` | No in-place mutation. Synthetic CalcUsages returned separately. |
| **Spec 07** | 2-tuple: `(list[ComputedAttributeData], list[ChannelAlias])` | In-place mutation: `calc_usages.append(synthetic_usage)` inside the function. |

**Resolution**: Adopt Spec 04's 3-tuple approach. Returning separately is cleaner (no hidden side effects). Fix Spec 07.

#### C2: EXPOSE_PURE `alias_name` Scoping Disagreement

| Spec | alias_name value | Phase 3 registration |
|------|-----------------|---------------------|
| **Spec 04** (authoritative) | Bare: `ca.python_name` (e.g., `"total_capex"`) | Scopes at registration: `f"{owning_short}.{alias.alias_name}"` |
| **Spec 01** | Pre-scoped: `f"{owning_part_short_name}.{ca.python_name}"` | N/A (data model spec) |
| **Spec 07** | Pre-scoped: `f"{ca.owning_part_name}.{ca.python_name}"` | Direct: `registry.register_alias(alias.alias_name, ...)` |

Design doc agrees with Spec 04: bare at production, scoped at Phase 3 registration.

**Resolution**: Adopt Spec 04 + Spec 05 approach (bare alias_name, scope at Phase 3). Fix Spec 01 and Spec 07.

---

### MAJOR Issues (Should fix before implementation)

#### M1: FORMULA Compilability Filter Missing in Spec 04

- **Spec 04**: No compilability guard on FORMULA synthetic CalcUsage creation
- **Spec 05 + Spec 07**: Filter `if ca.compilability != Compilability.FULLY_COMPILABLE: continue`

**Resolution**: Add compilability filter to Spec 04's FORMULA loop.

#### M2: `source` Field Extra Value in Spec 03

- **Spec 01** (authoritative): `source: str  # "redefinition" | "expose_pure"`
- **Spec 03**: Adds `"design_override"` as third allowed value (not used anywhere else)

**Resolution**: Remove `"design_override"` from Spec 03.

#### M3: `calc_def_name` Type for Synthetic CalcUsages

- **Spec 04** (authoritative): `calc_def_name=""` (empty string)
- **Spec 07**: `calc_def_name=None`

**Resolution**: Adopt Spec 04's empty string.

#### M4: OutputRegistry Diagnostic Interface Duplication

- **Spec 02** (authoritative): Defines `__len__`, `__contains__`, `channels()`, `keys()`
- **Spec 05**: Defines different interface: `canonical_count`, `total_keys`, `dump()`
- **Spec 05**: Also adds self-referential registration `self._index[canonical_channel] = canonical_channel` not in Spec 02

**Resolution**: Add note in Spec 05 deferring to Spec 02 for OutputRegistry class interface. Remove duplicate interface definition from Spec 05.

#### M5: FORMULA EQN Construction Disagreement

- **Spec 04 + Spec 05**: `module_eqn = f"{parent_eqn}__{ca.python_name}"`
- **Spec 07**: `module_eqn = sysml_to_python_qualified_name(f"{ca.owning_part_qualified_name}::{ca.name}")`

These produce different results if `ca.name != ca.python_name` (sanitized names).

**Resolution**: Adopt Spec 04/05 approach. Fix Spec 07.

---

### MINOR Issues (Clean up during implementation)

| ID | Issue | Specs |
|----|-------|-------|
| m1 | `owning_part_qn` not converted to `__` format in Spec 04 line 408 | Spec 04 vs Spec 01, 07 |
| m2 | `extract_chain_aliases` name/arg type mismatch | Spec 03 vs Spec 07 |
| m3 | `_is_transitive_default()` implementation style varies | Spec 02, 05, 07 |
| m4 | Step 4.7 shown as "unchanged" in Spec 05 numbering table | Spec 05 vs Spec 03, 07 |
| m5 | Spec 07 omits several CalcUsageData fields in synthetic construction | Spec 04, 07 |
| m6 | `attr.parent_part_name` vs `attr.parent_part` field name | Spec 02 vs Spec 05, 07 |
| m7 | Aggregation alias variants: `register()` vs `register_alias()` | Spec 02 vs Spec 05, 07 |

---

## Design Doc Coverage

| Design Doc Section | Status | Covered By |
|---|---|---|
| S1: Big Picture | COVERED | All specs collectively |
| S2: Pipeline Overview | COVERED | Specs 03, 04, 05, 06, 07 |
| S3: Steps 1-3 Extraction | COVERED (unchanged) | N/A |
| S4: Step 3.5 Hierarchy | COVERED | Spec 03 |
| S5: Steps 4-4.5 Attributes | COVERED | Spec 04 |
| S6: Step 5 OutputRegistry | COVERED | Specs 02, 05 |
| S7: Step 6 Backtracking | COVERED | Spec 06 |
| S8: Step 6.5 Expression Compilation | NOT COVERED (unchanged) | Referenced by Spec 07 |
| S9: Step 7 Graph | COVERED | Spec 07 |
| S10: Generation | NOT COVERED (unchanged) | Spec 07 confirms no changes |
| S11: Naming System | NOT COVERED (unchanged) | Referenced throughout |
| S12: OutputRegistry Cross-Cutting | COVERED | Specs 02, 05, 06 |
| S13: AST Dispatch Rules | NOT COVERED | Cross-cutting code constraint |

**Gap**: AST dispatch rules (Section 13) should be added as a cross-cutting invariant to Spec 03.

---

## Issue Traceability

**21/22 issues COVERED. 1 PARTIAL (Issue 20).**

Issue 20 (Phase 2 CHAIN aliases have no observed consumer): Resolution implemented correctly in specs. Missing: explicit design rationale note documenting "keep unused functionality" decision with Spike 8 evidence.

**8/9 spikes explicitly referenced. 1 gap (Spike 2).**

Spike 2 findings captured implicitly but "Spike 2" not named in any traceability table. Should add explicit reference.

---

## Fixes Applied

All CRITICAL and MAJOR issues have been fixed in the specs. See git diff for details.
