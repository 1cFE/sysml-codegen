# Audit: agentic-mbse Sync (PIPELINE-TRUTH Item 9)

**Verdict:** PASS
**Audited:** 2026-07-06
**Branch (artifacts):** `pipeline-truth-epic` (sysml-codegen) — commit `c5356ef`
**Branch (implementation):** `pipeline-truth-item4` (agentic-mbse) — commits `fa3b706`, `1fab4d6`, `9cc7ab4`

---

## Summary

Item 9 delivers what it specified. Every claim in the close-out I could execute, I
executed — and it held. The one must-land check (C7) fires exactly once on its negative
fixture and is silent on all three supported shapes; run over the codegen plant fixtures it
fires **0** times, so it cannot flag a shape codegen accepts (the STOP-gate the prior epic
filed C7 to avoid). The teaching surface teaches the four whole-plant mechanisms accurately
and — the thing most likely to be wrong — does **not** overclaim expression-RHS as
supported. Cross-repo: the agentic-mbse suite is green at 1240/1/33 and the L6 error counts
are byte-identical (10/18/9) to the recorded baseline. All 18 traceability rows map to a
real, verified disposition. No findings.

## Findings

### Plan completion — all phases verified

All six phases (0–5) are marked done and each is backed by evidence I reproduced live:

- **Phase 0 (survey / STOP-gate):** the C7 build site (`level6_architecture.py:797`) and
  the discriminator claim hold — see the C7 finding below.
- **Phase 1 (C7 + D1):** C7 tests pass; the negative/silent-on-clean fixtures exist and do
  what the plan says; D1 section present and accurate.
- **Phase 2 (D2/D3/D4/I5 + V1/V2/V3):** doc sections present (`plant-idiom.md` §Secondary
  shapes / §Keep cross-part chains shallow; `constraints.md` §Subtype-aware); the D4
  decision table is published (`docs/subtype-enumeration-decision-table.md`, from Item-4
  `bc196df`).
- **Phase 3 (dispositions):** every backlog entry landed with a recorded, sound decision
  (see Prior-epic residue below).
- **Phase 4 (companion audit):** `companion-audit.md` carries a written verdict per
  primitive; verdicts are internally consistent and match the source anchors
  (`extract_feature_refs` at `sysml/expression.py:119`; `str(direction)` keying).
- **Phase 5 (close-out):** 18-row table complete; both acceptance gates reproduced green.

No placeholder code, no TODOs, no partial implementation found.

### Spec conformance — all success criteria met

- **SC-1 (consolidated impact list built + dispositioned):** MET. 18/18 rows in the
  close-out table, each with a disposition and evidence; nothing from the per-item
  recordings dropped.
- **SC-2 (new check has negative fixture + catches trap on Item-1 shapes):** MET. C7 fires
  on `attribute :>> gain = 2.0 * 3.0` (exactly 1 WARN) and is silent on the bare
  `:>> gain = 7.0`, bare `:>> rate = 2.0 * 4.0`, and `attribute :>> level = 5.0` forms.
  `tests/test_validation/test_item9_checks.py` — 2 passed.
- **SC-3 (teaching surfaces match the supported subset):** MET. `plant-idiom.md` teaches
  four mechanisms + precedence + QN-keying + LITERAL-only; the Item-4 subtype semantics and
  Item-5 diagnostics are folded in. No overclaim.
- **SC-4 (prior-epic residue closed/re-filed):** MET. PR #7 OPEN/base `main` recorded; C7
  built; C8 keep-filed; F6 verified; vendor note declined-with-reasoning.
- **SC-5 (SYNC-F3/F4/F5 each get a decision):** MET. F3/F4 keep-filed, F5 discharged — all
  recorded in this repo's `BACKLOG.md`.
- **SC-6 (companion audit complete):** MET. `extract_feature_refs` COVERED, `str(direction)`
  STABLE — written verdict per primitive, no silent pass.
- **SC-7 (both suites green; nothing teaches/checks a pattern codegen accepts):** MET.
  agentic-mbse 1240/1/33; C7 count 0 over the plant fixtures.

Non-goals held: no codegen production change; PR #7 not merged; Item-4 work verified not
redone; no new V-code; no vendor report written.

### Design conformance — follows the spec's 18-row contract

There is no design.md (epic budget: spec + plan + execute). The 18-row impact table is the
contract; the implementation follows it row for row, and the filing-homes split (agentic-mbse
concerns in agentic-mbse backlog, sysml-codegen concerns in this repo's BACKLOG) is honored —
no filing crosses a boundary its session couldn't reach.

### Code integrity — no issues

C7 (`check_attr_redef_expression_dropped`, `level6_architecture.py:797`) is a clean, single-
purpose check: it iterates `AttributeUsage` elements, skips type-only and literal
redefinitions, and warns on a non-literal RHS. The literal-detection helper `_is_literal_rhs`
mirrors codegen's `is_literal_expression` (5 literal types + `NullExpression`) rather than
reinventing it. No god-function, no policy-in-utility, no silent fallback — the WARNING
severity is deliberate (keeps L6 passing while surfacing the drop). No slop or
failure-honesty issues.

---

## Spot-check evidence (the 8 requested, all reproduced live)

1. **C7 fixtures + WARN.** `test_item9_checks.py` 2 passed: fires exactly once on the
   expression fixture, zero on the three supported forms.
2. **C7 discriminator (the STOP-gate).** The check iterates only `AttributeUsage`; the bare
   `:>>` form parses as `ReferenceUsage` and is therefore **structurally unreachable** by
   C7, independent of literal-vs-expression. The Phase-0 live probe table
   (`plan.md:388`) records the four-way disjointness (AttributeUsage+expr → dropped;
   AttributeUsage+literal → dropped-but-taught; ReferenceUsage+literal → mechanism b;
   ReferenceUsage+expr → CHAIN). The passing `test_c7_bare_and_literal_redefs_do_not_fire`
   is the live confirmation: all three non-target shapes stay silent. **Cross-repo run over
   the codegen plant fixtures: C7 count = 0** on `plant_values`, `plant_value_shapes`,
   `spec_chain_twolevel`. The check cannot fire on the supported bare-literal form.
3. **D1 plant-idiom content.** `plant-idiom.md:95–166` teaches all four mechanisms (a/b/c/d)
   with worked SysML, the precedence rule (usage `:>>` > specialized-def `:>>` > base def),
   source-QN keying (rename-per-consumer collapses; N-consumers-one-channel), and LITERAL-
   only propagation. It explicitly states a chain/expression RHS falls to the uncovered-
   parameter diagnostic, and flags `attribute :>> attr = <expr>` as dropped. **No overclaim.**
4. **R-F6 verified-closed.** Ran `test_f6_formula_computed_attrs_not_flagged` and
   `test_f6_calc_output_ref_still_fires` — both pass under the post-Item-4 validators.
5. **S-F5 discharge evidence.** All four cited tests exist and pass: the two loud-on-gap
   (`test_collector_pins_chain_override_probe`, `test_reconcile_raises_v11_on_wired_gap`) and
   the two INV-6 silent-on-clean (`test_d34_clean_report_no_warn`, `test_d313_all_known_no_warn`).
6. **A1/A2 verdicts.** The committed `companion-audit.md` records COVERED / STABLE with probe
   output; the close-out table rows match. Source anchors confirmed present
   (`extract_feature_refs` at `expression.py:119`; `str(direction)` substring keying).
7. **Keep-filed entry, agentic-mbse side.** `ITEM-SYNC-C8` marked KEEP FILED with sound
   reasoning (codegen SC-4 sanitizer backstop; pre-warn needs shared sanitizer, ~0.5–1 day);
   `ITEM-SYNC-C7` marked ✅ BUILT; `ITEM-SYNC-F1` vendor note DECLINED (evaluation-time, not
   extraction-time — no codegen path).
8. **Keep-filed entry, this-repo side.** `SYNC-F3`/`SYNC-F4` KEEP FILED, `SYNC-F5`
   DISCHARGED — all three carry an Item-9 disposition note in this repo's `BACKLOG.md`.

## Cross-repo zero-regression (priority 3)

- agentic-mbse full suite: **1240 passed, 1 skipped, 33 deselected** (baseline 1238 + 2 C7
  tests). Reproduced live.
- `validate_architecture` over the codegen plant fixtures: **L6 errors 10 / 18 / 9** — exact
  match to the recorded stash-verified counts. Because C7 is WARNING-only and fires 0 times
  on the supported subset, the ERROR set is byte-identical with or without it; the
  no-regression claim holds by construction, not just by observation.

## COMPANION_PR_BODY.md (priority 5)

Covers all **7** commits on `pipeline-truth-item4` over base `7f77510` — Item 4's four
(`64a097e`/`cc64b1d`/`bc24ae3`/`bc196df`) + Item 9's three
(`fa3b706`/`1fab4d6`/`9cc7ab4`) — matching `git log 7f77510..pipeline-truth-item4` exactly.
The B1 base-then-retarget instruction is present (base `upstream-findings-sync` while PR #7
is open → `main` on merge). No false claims; the acceptance numbers match reality.

## Branch hygiene (priority 7)

`pipeline-truth-item4` is pushed and tracking `origin/pipeline-truth-item4`, 0/0 divergence.

- **Minor note (not a finding against Item 9):** the agentic-mbse working tree has two
  untracked files — `.project/backlog/epic_command-refresh.md` and a `20260703-…command-refresh`
  research note. These belong to an unrelated command-refresh epic (dated 2026-07-03),
  predate this work, and were not touched by Item 9's three commits. Item 9 disturbed
  nothing else in the repo; the two files are simply pre-existing untracked scratch. Worth a
  glance before the human opens the companion PR so they aren't swept in, but not a defect in
  this item.

---

## Certification

Verified and marked:

- **Spec success criteria SC-1 … SC-7** — all met, marked `[x]`.
- **Epic Item 9 success criteria** (impact-list/traceability, negative-fixture-catches-trap,
  prior-epic residue) — all met; heading gets ✅.
- **Plan phases 0–5** — already marked complete by the implement session; each re-verified
  against live evidence above.

Everything checked reproduced. No open items, no findings requiring rework. This item is
certified PASS.

ARTIFACT: .project/active/pipeline-truth-sync/audit.md
