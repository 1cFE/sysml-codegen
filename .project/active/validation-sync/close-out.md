# Close-out: agentic-mbse Sync — Guidance & Validation (UPSTREAM-FINDINGS Item 12)

**Status:** COMPLETE
**Date:** 2026-07-06
**Implementation repo:** `~/1cfe/agentic-mbse` (branch `upstream-findings-sync`)
**Artifacts repo:** `~/1cfe/sysml-codegen` (branch `upstream-findings-epic`)

Item 12 was the epic's final item: sweep the drift between what codegen now accepts and
what agentic-mbse teaches and checks. The validated-subset contract is enforceable again —
a model the auditor passes is a model codegen accepts, and the teaching surfaces match the
supported subset.

## Result in one line

All four non-fileable checks landed (C1–C4); the three high-value fileable corrections
landed (C5, C6, C2b); two candidate WARNs were filed (C7, C8); all eight doc rows landed
(D1–D8); the skill sweep found nothing else stale (V2); both acceptance gates are green.

## What landed (agentic-mbse commits on `upstream-findings-sync`)

| Commit | Phase | Content |
|--------|-------|---------|
| `9db5ede` | 1 | C1 (self-named FAIL, L2), C2a (anonymous-return FAIL, L6), C3 (constraint WARN, L6), C4 (calc-bearing-no-instantiation FAIL, L6) + fixtures + 8 tests |
| `87f9bc8` | 2 | C5 (`^` removal + function-invocation WARN), C6 (L6 false-positive corrections), C2b (body-assignment WARN) + fixtures + 5 tests |
| `f68d1cb` | 3 | D1–D8 docs + plant-idiom.md + index registration; V1 confirmed, V2 sweep |
| `08cd595` | 4 | F1/F2/C7/C8 backlog filings + syside vendor-note draft |

## Acceptance gates (both green)

**Gate 1 — agentic-mbse own suite:** `1218 passed, 1 skipped` (baseline was 1212; +6 new
Item-12 tests). ruff clean; mypy adds 0 new errors.

**Gate 2 — run_all_checks over the sysml-codegen fixture corpus:** the three plant fixtures
pass L1–L5 with no regression; Item-12 L6 changes are exactly the designed ones. Enumerated:

| Fixture | L1–L5 | L6 | Item-12 findings (expected) |
|---------|-------|-----|------------------------------|
| ife_plant | PASS | PASS | none (no false positives) |
| wi014_toy | PASS | PASS | none |
| self_named_binding_trap | PASS | **PASS** | C6 fix: was L6 FAIL (V2_DYNAMIC_EXPRESSION + L6_INVALID_QUALIFIED_NAME), now 0 of each; C1 does not fire (covering attribute) |
| self_named_rescue | PASS | PASS | C1 does not fire (covering EXPOSE) |
| return_styles | PASS | PASS | C2b WARN on StyleD (WARN keeps L6 passing) |
| anonymous_return | PASS | FAIL | C2a FAIL (by design — this fixture is the negative) |
| spec_chain_channel / twolevel / sibling_channel_ambiguity | PASS | PASS | none |

`retype_model` L2=FAIL is a pre-existing `UNBOUND_INPUT` (`check_unbound_inputs`), not an
Item-12 code — confirmed not a regression.

## Traceability 1 — impact-list row → disposition → evidence

| Row | Disposition | Evidence |
|-----|-------------|----------|
| C1 self-named FAIL (L2) | BUILT | `level2_structure.py` `check_self_named_bindings` + `_owner_covers_name`; fixture `item12/self_named_deadend` FAILs, `self_named_trap`/`self_named_rescue` do not; ife_plant L2 PASS. Reframed vs spec (see amendment). |
| C2a return-style / anonymous FAIL (L6) | BUILT | `level6_architecture.py` `check_anonymous_returns`; `item12/anonymous_return` FAILs, `return_styles` does not. |
| C2b body-assignment WARN (L6) | BUILT | `check_body_assignment_impl_loss`; `item12/body_assignment` WARNs once on BodyCalc, InlineCalc does not. |
| C3 constraint WARN (L6) | BUILT | `check_constraint_executability`; `item12/constraint_model` WARNs, L6 passes. |
| C4 no-instantiation FAIL (L6) | BUILT | `check_calc_bearing_instantiation`; `item12/no_instantiation` FAILs, `retype_instantiation` does not (retype counts). |
| C5 operator-set + function WARN | BUILT | `adr002.py`: `^` removed from `SUPPORTED_OPERATORS`; `check_static_function_invocations`; `item12/static_operators` fires V4_UNSUPPORTED_OPERATOR + V4_STATIC_FUNCTION_INVOCATION. |
| C6 L6 false-positive corrections | BUILT | (a) V2 skips calc-def-owned attrs; (b) `check_qualified_names` accepts quoted segments; `item12/c6_false_positives` + real trap now L6 PASS. |
| C7 attribute-`:>>`-expr WARN | FILED | agentic-mbse backlog `ITEM-SYNC-C7`; reason logged (subtle trigger boundary). Doc D5 lands. |
| C8 two-names-one-identifier WARN | FILED | agentic-mbse backlog `ITEM-SYNC-C8`; reason logged (needs shared sanitizer). |
| D1 plant-idiom patterns | BUILT | `docs/patterns/plant-idiom.md` (references the 5 fixtures). |
| D2 retyping | BUILT | plant-idiom.md §retyping. |
| D3 quoted names | BUILT | SKILL.md naming note. |
| D4 no-loops (A-3) | BUILT | adr002-calculations.md §No Loops. |
| D5 bare-`:>>` idiom + attr-`:>>` warning + precedence | BUILT | semantic-operators.md. |
| D6 EXPOSE surfacing | BUILT | expose-pattern.md §EXPOSE surfacing. |
| D7 constraint pointer | BUILT | constraints.md (points at modeling-assumptions §8). |
| D8 def-owned design attrs | BUILT | plant-idiom.md §def-owned (kept as a cheap line, not downgraded). |
| V1 A-2 spot-check | CONFIRMED | `references/stencils.md:39` teaches inline `return result : Real = ...` (A-2 committed `6dbdf1b`). |
| V2 skill sweep | DONE — nothing else stale | Operator taxonomy already matched C5; only stale stencil (A-2) already fixed; usage-based-dataflow output forms are not the C2b anti-pattern. |
| F1 syside vendor note | FILED (agentic-mbse) | backlog `ITEM-SYNC-F1` + draft `.project/research/20260706_syside-self-named-recursion-vendor-note.md`. |
| F2 V11 model-side mirror | FILED (agentic-mbse) | backlog `ITEM-SYNC-F2`. |
| F3 shape-B leaf collision | FILED (sysml-codegen) | `.project/backlog/BACKLOG.md` `SYNC-F3`. |
| F4 redefinition name surfacing | FILED (sysml-codegen) | `SYNC-F4`. |
| F5 unresolvable-warning test | FILED (sysml-codegen) | `SYNC-F5`. |

## Traceability 2 — fusion-tea trap → covering check / rule

Source: `~/1cfe/fusion-tea/.project/reports/2026-07-05-upstream-findings-register.md`
(SC-1..SC-11 + A-1/A-2/A-3) and `work/learnings/RAW_LEARNINGS.md` (WI-014 traps).

| Trap | Covered by | Kind |
|------|-----------|------|
| SC-1 constraints silently dropped | C3 (WARN) + D7 (doc) | check + rule |
| SC-2 return-style outputs invisible / anonymous crash | C2a (FAIL) + V1/A-2 stencil | check + rule |
| SC-3 retype subtype looks uninstantiated, calcs dropped | C4 (FAIL, retype counts) + D2 (doc) | check + rule |
| SC-4 quoted names leak into Python identifiers | C6b (correction) + D3 (doc) | check + rule |
| SC-5 cross-part refs drop / self-named binding (mechanism D) | C1 (FAIL) + D1 (plant idiom) + D5 (bare-`:>>`) | check + rule |
| SC-6 expression reconstruction corrupts literals | codegen-side (Item 6, no agentic-mbse impact) | noted, owned by codegen |
| SC-7 derived attr loses name (EXPOSE_PURE drop) | codegen FIX (Item 11) + D6 (EXPOSE surfacing doc) | fixed + rule |
| SC-8 warning noise that looks like failure | codegen-side (Item 7) + F5 (test) | noted / filed |
| SC-9 no snapshot-input path | codegen CLI (Item 2), out of scope | noted |
| SC-10 compilation_results not rebuildable from snapshot | codegen, out of scope | noted |
| SC-11 module class-name collisions via aliasing | C8 (FILED) | filed |
| A-1 validation stack catches no traps | the C1–C6 floor | checks |
| A-1 operator envelope (`exp()`, conditionals, `**`) | C5 | check |
| A-2 skill stencil teaches broken return | V1 (confirmed `6dbdf1b`) | rule |
| A-3 no-loops rule undocumented | D4 | rule |

Every SC/A trap maps to a check, a documented rule, a codegen fix, or an explicit filing.
Nothing from any per-item recording is dropped.

## Spec amendment (C1 reframing — recorded for the R2 trail)

C1's spec floor treated any self-named binding as the error and named the
`self_named_binding_trap` fixture as its negative. **Evidence at the agentic-mbse layer
refuted that floor**, and the orchestrator reframed C1:

- C1's floor was written pre-Items-9/10. Item 9's rescue made a self-named binding **with a
  covering attribute** (even a bare literal) a SUPPORTED pattern — the plant design-attribute
  idiom (`in radius = radius` with an outer `attribute radius`). ife_plant carries ~21 of
  these legitimately.
- So the check FAILs only a **true dead-end**: a self-named binding whose owner carries no
  feature named `P` at all (owned OR inherited). The old trap fixture (which carries a
  covering literal) flipped to negative-of-the-negative; the new negative is
  `item12/self_named_deadend`.
- Coverage scans `owner.features` (owned + inherited) — a retyped subtype binding against an
  inherited attribute (`in bank_energy = bank_energy`, Item 4) is covered and not flagged.

**One-line amendment for the codegen spec:** C1's negative fixture is a *dead-end*
self-named binding (no covering feature), not the `self_named_binding_trap` shape — the trap,
which carries a covering attribute, is now the supported plant idiom (Items 9/10) and is
C1's negative-of-the-negative.

## Follow-ups (filed, not done here)

- agentic-mbse: `ITEM-SYNC-F1` (vendor report), `ITEM-SYNC-F2` (V11 mirror), `ITEM-SYNC-C7`,
  `ITEM-SYNC-C8`.
- sysml-codegen: `SYNC-F3`, `SYNC-F4`, `SYNC-F5`.
