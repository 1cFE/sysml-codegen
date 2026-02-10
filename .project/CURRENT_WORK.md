# Current Work

**Last Updated**: 2026-02-10

---

## Active Work

### COST-PATTERN: Costed Component Pattern Support

**Status**: In Progress (4/5 items complete)
**Epic**: `.project/backlog/epic_costed_component_pattern.md`
**Started**: 2026-02-10

**Objective**: Support hierarchy-aware codegen for costed component patterns (templates, `:>>` redefinitions, `sum()` aggregation, parametric multiply).

**Current Phase**: Item 4 complete. Item 5 (E2E Validation & Documentation) is next.

**Completed Items**:
- [x] Item 1: Bug fixes from E2E validation (6 bugs fixed)
- [x] Item 2: Template CalcUsage detection & virtual instantiation
- [x] Item 3: Redefinition extraction, multiplicity, & aggregation
- [x] Item 4: Pipeline integration -- hierarchy-aware module generation

**Remaining**:
- [ ] Item 5: E2E Validation & Documentation

**Blockers**: None

**Location**: `.project/active/hierarchy-pipeline/`

---

## Recently Completed

### 2026-02-10: COST-PATTERN Item 4 -- Pipeline Integration
- Integrated hierarchy extraction into full codegen pipeline (4 phases)
- Virtual CalcUsage binding rewriting, aggregation module generation, CLI extensions
- 454 tests, 0 failures, 141 new tests

### 2026-02-10: COST-PATTERN Items 1-3
- Bug fixes, template detection, redefinition extraction
- Foundation for hierarchy-aware codegen

### 2026-02-09: [ATTR-EXPR] Attribute Expression Capture
- FORMULA computed attributes generate synthetic pipeline modules
- 5-way classification scheme, ADR-004/005

---

## Up Next

1. COST-PATTERN Item 5: E2E Validation & Documentation
2. Close COST-PATTERN epic
3. Consider next epic from backlog

---
