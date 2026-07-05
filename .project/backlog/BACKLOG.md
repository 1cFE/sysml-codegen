# Product Backlog

Prioritized list of epics and features.

**Last Updated**: 2026-02-22

---

## Priority Legend

- **P0**: Critical - Blocking, do immediately
- **P1**: High - Important, do soon
- **P2**: Medium - Valuable, do when possible
- **P3**: Low - Nice to have, do eventually

---

## In Progress

| Item | Priority | Status | Started | Notes |
|------|----------|--------|---------|-------|
| generation-boundary | P1 | In Progress (BUILD phase) | 2026-02-20 | Step 7.6 — enforcing generation/ only consumes ComputationGraph. Phases 1-2-4 done. |
| hierarchical-output | P2 | Draft (spec only) | 2026-02-22 | Convert flat JSON output to hierarchical structure reflecting SysML part hierarchy. |
| new-pipeline-explainer | P2 | Draft (active) | 2026-02-22 | Interactive HTML explainer for refactored 7-step pipeline architecture. |

---

## P1 - High Priority

| Epic | Status | Notes |
|------|--------|-------|
| [PUSH-DOWN] agentic-mbse Push-Down Design | Design ready | Move reusable SysML semantics (~875 lines) from sysml-codegen extraction/ into agentic-mbse/sysml/. Phase 1 (LOW risk): expression_utils + qualified_names. Phase 2 (MEDIUM risk): hierarchy + aggregation. See `.project/concepts/agentic-mbse-push-down-design.md`. |

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
| [COST-PATTERN] Costed Component Pattern Support | 2026-02-22 | ~12 days | 41 items completed: full conformance test suite (C01-C27, X01-X02), Phase 7 structural refactors, bug fixes (7, 11), docs consolidation. |
| [ATTR-EXPR] Attribute Expression Capture | 2026-02-09 | ~2 days (Items 1-5) | FORMULA computed attributes generate synthetic pipeline modules. 5-way classification scheme. ADR-004/005 formalized. 285 tests, 0 failures. |
| [EXPR-CODEGEN] Expression-Aware Code Generation | 2026-02-08 | ~8.5 days | 15/15 solar_battery, 19/21 CATF auto-implemented. 167 tests, 0 xfail. |

---

## Ideas / Future Considerations

- InvocationExpression / function call support (sqrt, min, max whitelist)
- SelectExpression / if-then-else support (piecewise functions)
- EXPOSE_COMPUTED decomposition (calc output + arithmetic, deferred from ATTR-EXPR)
- Non-uniform array instances (flat expansion strategy for arrays with per-element parameters)
