# Product Backlog

Prioritized list of epics and features.

**Last Updated**: 2026-02-08

---

## Priority Legend

- **P0**: Critical - Blocking, do immediately
- **P1**: High - Important, do soon
- **P2**: Medium - Valuable, do when possible
- **P3**: Low - Nice to have, do eventually

---

## In Progress

| Epic | Priority | Status | Started | Notes |
|------|----------|--------|---------|-------|
| [None yet] | - | - | - | - |

---

## P1 - High Priority

### [ATTR-EXPR] Attribute Expression Capture

**Priority**: P1
**Effort**: ~6-8 days
**Status**: Draft

Enable attribute-level expressions (`attribute volume = pi * r^2 * h`) to generate pipeline modules automatically, eliminating the CalcDef+CalcUsage ceremony for simple formulas. Builds on Phase 1 expression compiler.

**Items**:
- [ ] Item 1: Spike -- Attribute Expression AST Discovery & Architecture Evaluation (1 day)
- [ ] Item 2: Computed Attribute Extraction & Data Models (1.5 days)
- [ ] Item 3: Pipeline Integration -- Computed Attribute Modules (2-2.5 days)
- [ ] Item 4: E2E Validation on Real Models (1 day)

**File**: `epic_attribute_expression_capture.md`

---

## P2 - Medium Priority

*No epics yet*

---

## P3 - Low Priority

*No epics yet*

---

## Completed

| Epic | Completed | Duration | Notes |
|------|-----------|----------|-------|
| [EXPR-CODEGEN] Expression-Aware Code Generation | 2026-02-08 | ~8.5 days | 15/15 solar_battery, 19/21 CATF auto-implemented. 167 tests, 0 xfail. |

---

## Ideas / Future Considerations

- Phase 3: Hierarchy, multiplicity, aggregation (native nested CalcUsage-in-PartDef patterns)
- InvocationExpression / function call support (sqrt, min, max whitelist)
- SelectExpression / if-then-else support (piecewise functions)
