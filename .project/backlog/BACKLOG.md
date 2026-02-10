# Product Backlog

Prioritized list of epics and features.

**Last Updated**: 2026-02-10

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
| [COST-PATTERN] Costed Component Pattern Support | P1 | In Progress (4/5 items) | 2026-02-10 | Items 1-4 complete. Item 5 (E2E Validation & Documentation) remaining. |

---

## P1 - High Priority

*No epics -- COST-PATTERN moved to In Progress*

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
| [ATTR-EXPR] Attribute Expression Capture | 2026-02-09 | ~2 days (Items 1-5) | FORMULA computed attributes generate synthetic pipeline modules. 5-way classification scheme. ADR-004/005 formalized. 285 tests, 0 failures. |
| [EXPR-CODEGEN] Expression-Aware Code Generation | 2026-02-08 | ~8.5 days | 15/15 solar_battery, 19/21 CATF auto-implemented. 167 tests, 0 xfail. |

---

## Ideas / Future Considerations

- InvocationExpression / function call support (sqrt, min, max whitelist)
- SelectExpression / if-then-else support (piecewise functions)
- EXPOSE_COMPUTED decomposition (calc output + arithmetic, deferred from ATTR-EXPR)
- Non-uniform array instances (flat expansion strategy for arrays with per-element parameters)
