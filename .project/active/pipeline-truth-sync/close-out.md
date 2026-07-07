# Close-Out: agentic-mbse Sync (PIPELINE-TRUTH Item 9)

**Status:** COMPLETE — 2026-07-06
**Branch (artifacts):** `pipeline-truth-epic` (this repo)
**Branch (implementation):** `pipeline-truth-item4` (`/home/reid/1cfe/agentic-mbse`)
**agentic-mbse commits (Item 9):** `fa3b706` (C7+D1), `1fab4d6` (D2/D3/D4/I5), `9cc7ab4` (dispositions)

The validated-subset contract is enforceable again: a model the auditor passes is a model
codegen accepts. The one unbuilt check (C7) now WARNs before generation on the silent-drop
shape without flagging anything codegen accepts; the teaching surface matches the newly
supported subset; every cross-repo thread from two epics is closed, kept-filed, or declined.

## Acceptance gates (both green)

- **agentic-mbse own suite:** baseline **1238 passed / 1 skipped**; final **1240 passed /
  1 skipped / 33 deselected** (+2 C7 tests). ruff clean; 0 new mypy errors.
- **Cross-repo (no regression):** `validate_architecture` over sysml-codegen's
  `plant_values` / `plant_value_shapes` / `spec_chain_twolevel` — C7 count **0** on all three;
  stash-verified the L6 error counts (10 / 18 / 9) are byte-identical with and without C7 (C7 is
  WARNING-only and fires 0 times on the supported subset, so it cannot change the error set).

## 18-row traceability table

Every row from the spec's consolidated impact list → disposition → evidence. Zero rows silently
dropped (SC-1). Dispositions: **DONE** (built/written), **VERIFIED** (confirmed a prior change),
**DISCHARGED** (residue closed), **KEEP-FILED** / **DECLINED** (recorded decision), **COVERED**
(audit clean).

| # | Impact | Disposition | Evidence |
|---|--------|-------------|----------|
| **D1** | Whole-plant value idiom (four mechanisms a/b/c/d, precedence, QN-keying, LITERAL-only) | DONE (BUILD-DOC) | `docs/patterns/plant-idiom.md` §"The whole-plant value idiom"; agentic-mbse `fa3b706` |
| **D2** | Secondary supported-subset shapes with CORRECT/DEGRADED labels | DONE (BUILD-DOC) | `plant-idiom.md` §"Secondary shapes and their limits"; `1fab4d6` |
| **D3** | Keep cross-part chains shallow (multi-hop truncates `source_path`) | DONE (BUILD-DOC) | `plant-idiom.md` §"Keep cross-part chains shallow"; ref `deep_cross_scope_probe`; `1fab4d6` |
| **D4** | Subtype-aware validation semantics note **+ VERIFY** decision table published | DONE + VERIFIED | `docs/patterns/constraints.md` §"Subtype-aware validation"; table `docs/subtype-enumeration-decision-table.md` (Item-4 `bc196df`, confirmed present); note `1fab4d6` |
| **C7** | `attribute :>> attr = <expr>` WARN (the one unbuilt check) | DONE (BUILD-CHECK) | `check_attr_redef_expression_dropped` + `L6_ATTR_REDEF_EXPR_DROPPED` (level6_architecture.py); fixtures `tests/fixtures/item9/{attr_redef_expr,attr_redef_literal}`; tests `test_item9_checks.py`; `fa3b706`. Discharges `ITEM-SYNC-C7`. |
| **V1** | Stencil still teaches inline `return` (not body-assignment) | VERIFIED | `claude/skills/sysml-conventions/references/stencils.md:39` (inline expression form) |
| **V2** | Skill + `docs/patterns/` sweep — no surface teaches a now-rejected pattern | VERIFIED (nothing stale) | Phase 2 sweep: the one risk surface (`attribute :>>` value form) already taught as DROPPED (semantic-operators.md); `^` hits are ASCII unit notation |
| **V3** | Item 3 — no new agentic-mbse impact | VERIFIED (no-op) | `.project/active/fusiontea-acceptance/run-report.md` §Item-9/R2 |
| **R-PR7** | Companion PR #7 (`upstream-findings-sync`) merge status | VERIFIED | OPEN, base `main`; stays the human's — not merged. `pipeline-truth-item4` stacks on it (B1) |
| **R-C8** | Two-names-one-identifier WARN | KEEP-FILED | Codegen SC-4 sanitizer-injectivity backstop; pre-warn needs a shared sanitizer (not small). agentic-mbse `ITEM-SYNC-C8` updated (`9cc7ab4`) |
| **R-F6** | Static-expression false-FAIL fix still correct post-Item-4 | VERIFIED (closed) | `test_item12_checks.py::test_f6_formula_computed_attrs_not_flagged` + `::test_f6_calc_output_ref_still_fires` green under current validators |
| **R-VENDOR** | syside self-named-recursion vendor note | DECLINED | Evaluation-time, extraction finite/degenerate (Item-8 probe exit 0). Note kept as durable record. agentic-mbse `ITEM-SYNC-F1` (`9cc7ab4`) |
| **S-F5** | Positive unresolvable-warning test (INV-6 leg) | DISCHARGED | Absorbed by Item 9's plain-usage-override fix; loud-on-gap proof re-anchored on `chain_override_probe` (`test_uncovered_params.py::test_collector_pins_chain_override_probe` + `::test_reconcile_raises_v11_on_wired_gap`); INV-6 silent-on-clean in `test_silent_failure_family2.py`. This-repo `BACKLOG.md` `SYNC-F5` |
| **S-F3** | Shape-B leaf-collision filename edge | KEEP-FILED | No model hits it. This-repo `BACKLOG.md` `SYNC-F3` |
| **S-F4** | Redefinition / design_override name surfacing | KEEP-FILED | No consumer needs it. This-repo `BACKLOG.md` `SYNC-F4` |
| **A1** | `extract_feature_refs` traversal coverage | COVERED (AUDIT) | `companion-audit.md` §A1 — multi-segment chain / cross-part ref / self-named binding all traverse, none dropped |
| **A2** | `str(direction)` repr stability | STABLE (AUDIT) | `companion-audit.md` §A2 — syside 0.8.4 `FeatureDirectionKind.In/.Out`; codegen substring keys resolve it, resilient to `<…>` drift |
| **I5** | Item 5 diagnostics → guidance | DONE (BUILD-DOC, derived) | `plant-idiom.md` — non-float EP diagnosed; `^`→`**` operator-map; multi-hop D3-2 loud-reject; `1fab4d6` |

**Coverage:** 18/18 rows dispositioned, 0 silently dropped.

## Filing homes (all reachable)

- **agentic-mbse backlog** (`9cc7ab4`): `ITEM-SYNC-C7` discharged (built), `ITEM-SYNC-C8`
  keep-filed, `ITEM-SYNC-F1` declined.
- **This-repo `BACKLOG.md`:** `SYNC-F3` / `SYNC-F4` keep-filed, `SYNC-F5` discharged (Item-9
  disposition notes appended).

## Non-goals held

PR #7 not merged (the human's). No PR created for `pipeline-truth-item4` (branch pushed only;
PR creation stays with the human, prior-epic precedent). No codegen production change. No new
V-code. The syside vendor *report* not written (R-VENDOR declined the filing).

## Companion PR

Draft body: `.project/active/pipeline-truth-sync/COMPANION_PR_BODY.md` — covers Item 4's four
commits + Item 9's three, with the B1 base-then-retarget instruction (base
`upstream-findings-sync` while PR #7 is open; retarget to `main` on merge).
