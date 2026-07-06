# Product Backlog

Prioritized list of epics and features.

**Last Updated**: 2026-07-05

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
| [UPSTREAM-FINDINGS] Upstream Findings Remediation & Plant-Idiom Support | Draft | Fix the 11 fusion-tea findings (SC-1–SC-11) + 6 research-discovered defects: baseline repair, silent-failure diagnostics, return-style/retyping/quoted-name support, snapshot CLI (license mitigation, expires 2026-08-06), staged cross-part wiring (gates fusion-tea MFE epic), agentic-mbse sync throughout. 12 items, ~13–16 days. See `epic_upstream_findings.md`. Items: [ ] 1 baseline+diagnostics [ ] 2 snapshot CLI [ ] 3 SC-2 [ ] 4 SC-3 [ ] 5 SC-4 [ ] 6 SC-6 [ ] 7 SC-8 [ ] 8 plant fixtures [ ] 9 SC-5 pre-fill [ ] 10 SC-5 wiring [ ] 11 SC-7 surfacing [ ] 12 agentic-mbse sync |
| [PUSH-DOWN] agentic-mbse Push-Down Design | Design ready | Move reusable SysML semantics (~875 lines) from sysml-codegen extraction/ into agentic-mbse/sysml/. Phase 1 (LOW risk): expression_utils + qualified_names. Phase 2 (MEDIUM risk): hierarchy + aggregation. **Sequencing note: UPSTREAM-FINDINGS Item 6 (expression reconstruction fix) must land before Phase 1 moves expression_utils.** See `.project/concepts/agentic-mbse-push-down-design.md`. |

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

- **Aggregation-literal dispatch bug (from UPSTREAM-FINDINGS Item 6, SC-6).**
  `hierarchy_resolver._walk_aggregation_ast` (`hierarchy_resolver.py:372,431`) keeps the
  old literal-after-invocation ordering: a literal operand in an aggregation expression is
  mis-dispatched to the invocation catch-all, marked `has_unsupported`, and its
  `reconstruct_expression` delegation (`:433`) is dead. Item 6 fixed the twin in
  `reconstruct_expression` (display path) but left this one — it touches an executable
  aggregation path (`transformed_expression` → `compiled_expression` → `auto_impl_context`),
  so it needs its own item with a byte-identity gate. Inert on today's corpus (no
  literal-bearing aggregation fixture); a future one would expose it. Documented as a
  known deviation from revised REQ-AST-03 in doc 19.
- **Constraint-reconstruction coverage (from UPSTREAM-FINDINGS Item 6, SC-6).**
  `reconstruct_expression` also serves constraint text, but constraint expressions are not
  captured in extraction snapshots (the Item-6 design's Appendix-A #4 wrongly assumed the
  catf_mfe divertor constraint `(surface_area_inner + surface_area_outer)` would appear in
  the snapshot; it does not — 0 occurrences). The paren/literal fix applies to constraint
  text too but has no snapshot-level regression coverage. Add a test that exercises
  constraint reconstruction directly if that coverage is wanted.
- **Stale-fixture snapshot refresh (from UPSTREAM-FINDINGS Item 9).** Three committed
  extraction snapshots drift from current live output but were left untouched by Item 9
  (its live re-capture reverted them to keep INV-5's "exactly four fixtures change"). They
  must be refreshed so the committed corpus ends the epic script-reproducible — deferred,
  not dropped. Run as one stale-fixture-refresh chore in the Item 6 Step-1 style: own
  commit, reviewed diff, and any test updates that assert the stale form. Execute at
  epic close-out.
  - `wi014_toy`, `self_named_binding_trap` — **path canonicalization only.** Last captured
    at Item 8 (`84ae948`) under the old convention; re-capture normalizes `source_file`
    (repo-relative → model-relative), `design_attributes` keys (repo-relative → absolute),
    and `document_path` (`file:…` → `file:///home/…`). No `design_overrides` / binding
    change — provably orthogonal to Item 9 (0 diff lines on those surfaces).
  - `quoted_owner_formula` — **path canonicalization + a classification shift.** Re-capture
    also drops two `design_attributes` (`net_margin`, `total_payout`), which now classify as
    computed attributes instead. Likely cause: post-Item-7 computed-attribute classification
    behavior reaching this Item-6-vintage snapshot (`346cf47`). The refresher should review
    this reclassification deliberately — confirm `net_margin`/`total_payout` SHOULD be
    computed, not design attributes — rather than wave the diff through. The repo already
    flags this fixture's path drift in `scripts/capture_extraction_snapshots.py:56-60`.
- InvocationExpression / function call support (sqrt, min, max whitelist)
- SelectExpression / if-then-else support (piecewise functions)
- EXPOSE_COMPUTED decomposition (calc output + arithmetic, deferred from ATTR-EXPR)
- Non-uniform array instances (flat expansion strategy for arrays with per-element parameters)
- Body-assignment expression capture (P3, M-lift; deferred from UPSTREAM-FINDINGS Item 3 / SC-2). For the `return attribute y : Real; y = expr;` form, wire the direction-None `member_expressions[y]` (the body assignment) into `output_expression_asts[y]` so `y` auto-implements instead of degrading to a `NotImplementedError` stencil. Inline `return y : Real = expr` already auto-implements, and the A-2 stencil fix steers modelers to the inline form, so this is low value — it restores auto-impl only for the deprecated body-assignment pattern.
