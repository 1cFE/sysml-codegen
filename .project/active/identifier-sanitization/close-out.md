# Close-out: Identifier Sanitization (SC-4 + SC-11 riders) — Item 5

**Status:** Implementation complete, gates green. Awaiting audit.
**Completed:** 2026-07-05 · **Branch:** upstream-findings-epic

## What landed

Every emitted Python identifier is now a sanitized function of the raw SysML QN,
via one new helper (`sanitize_qualified_name`) at the FORMULA module_eqn sites and
inline sanitize in the two `from_sysml` methods. Two silent-overwrite hazards
became loud errors: duplicate output paths (three write key spaces) and the SC-11
residual grandparent collision. Byte-identical on every existing model.

## Verification matrix

| REQ | What | Where | Test |
|---|---|---|---|
| REQ-NC-08 | Derivation-layer per-segment sanitize (class name, module path, FORMULA module_eqn/channel) | `core/qualified_names.py` `sanitize_qualified_name`; `core/identifier_types.py` `from_sysml`; `graph_builder.py` :275/:745/:789/:818; `output_registry_builder.py` :124 | `test_alias_agg_probe_generation`, `test_formula_quoted_owner`, `test_sanitize_invariance` |
| REQ-NC-09 | Fail fast on duplicate output path (modules/stencils + schemas), names both sources | `cli/__init__.py` `_check_duplicate_output_paths` (Step 1.5, before `_clear_output_directory`) | `test_duplicate_path_failfast` (3) |
| REQ-REG-08 | Post-alias class-name uniqueness re-check, hard fail-fast | `generation/registry.py` `_resolve_class_name_collisions` | `test_sc11_recheck` (2) |

**Gate:** 1880 passed / 4 skipped / 5 xfailed; ruff 21; mypy 109 (all at or better than the
1870/21/109 baseline; +10 tests). Invariance: all existing snapshots + baselines byte-identical.

## SC-11 closure

Confirmed **intended, documented, tested**: first-class design decision (doc 20 §Design
Constraints), REQ-REG-03/04/07 PASS, direct conformance tests, aliased baseline parseable. The
residual grandparent-collision hole (parent-segment-only alias) is now a **hard fail-fast**
(REQ-REG-08) — the Phase 0 static scan proved no committed model hits it (CLEAN gate). The
AST-based import rewrite (substring, first-match) was called a "filed follow-up" here but was in
fact filed **nowhere**. PIPELINE-TRUTH Item 8 (§G / SC-11) assessed it and filed a real P3 BACKLOG
entry (`[SC11-IMPORT-REWRITE]`): the size judgment is **not small** — done correctly it is a
cross-module AST rework, not the 1–2-site local change the registry alias-rewrite's no-not-found
branch (a D3 hygiene site) is. So it is filed, not built. This corrects the earlier false claim.

## ⚠️ Item 7 lockstep obligation (must reach Item 7's spec author)

`output_registry_builder.py:130` (the FORMULA registration key) stays **raw** — a temporary
state, deliberately. When Item 7 sanitizes the REFERENCE lookup at
`dependency_backtracker.py:595` (reusing `sanitize_qualified_name`), it MUST flip `:130` to
sanitized **in the same change** — raw→raw becomes sanitized→sanitized atomically — or the FORMULA
REFERENCE match breaks. The `pipeline_builder.py:70` FORMULA-twin match set moves with it.

Implementation note reinforcing this: a probe during Phase 1 showed a **calc-usage** consumer of a
same-part FORMULA attribute on a quoted owner routes through exactly these raw match sites
(`dependency_backtracker.py:473/:595`) and stays **unresolved** today. Item 5's fixture uses a
**computed-attribute** consumer (the `resolution_map` path) precisely because that is the
Item-5-independent wire; the calc-usage-under-quoted-owner case is Item 7's to fix.

## fusion-tea coordination note

`sanitize_names.py` in fusion-tea becomes dead once this lands — flag for **coordinated, reviewed
retirement**, not a silent drop. Its post-processor's rules may differ subtly from `sanitize_name`,
so retiring it can shift some downstream names; treat as a one-time reviewed name migration.

## agentic-mbse impact (recorded for Item 12 — not built here)

- **Guidance (MODELING_GUIDE / sysml-conventions):** "quoted names are fine — identifiers are
  derived." Modelers may use `'Fusion Power Plant'` freely.
- **Validation warning candidate (Level-2/6):** two distinct SysML names that sanitize to one
  Python identifier — warn before generation fails on the duplicate-path error.
- The fusion-tea retirement note and the Item 7 lockstep obligation above.

## Deviations from plan (see plan.md Implementation Notes for detail)

1. **INV-1 scan reformulated** — the corpus intentionally contains quoted names, so the literal
   "identity on every segment" is false. The scan proves the load-bearing property: no
   already-identifier-safe segment changes (accidental forms absent); every changed segment is a
   quoted name off the byte-identity path.
2. **FORMULA fixture consumer is a computed attribute, not a calc usage** — a calc-usage consumer
   routes through Item-7 raw match sites and cannot be fixed by Phase 1. The design's appendix/site
   list already described the computed-attribute (`resolution_map`) path; the design left the
   concrete fixture SysML to the plan. INV-5 is proven exactly by this fixture.
3. Fail-fast raises `CodeGenerationError` (established precedent), not the plan stencil's loose
   `GenerationError`; SC-11 re-check raises `ValueError` (registry convention).
