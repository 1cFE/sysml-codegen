# Audit — TRUTH-DEBT Item 4: Inherited-Attr Classifier Fix

**Date:** 2026-07-07
**Auditor:** Orchestrator (direct, live execution). The delegated audit session died at the
account's weekly usage limit ($1.33 spent, barely started); the orchestrator ran the full
audit itself with live execution access. Independence caveat: the orchestrator also routed
the item's stages, but did not write its code — verification below is against code, commits,
and live runs, not the implementer's claims.

**Contract:** `.project/active/classifier-fix/{spec,spec-review,design,design-review,plan}.md`
**Epic:** `epic_truth_debt.md` Item 4 (SC-D) + R1–R4.
**Commits audited:** f5018a9 (P0 gate), d0ffdbc (P1 widen), cb46b08 (P2 re-capture),
266fa43 (P3 honest collapse), fd9e3cd (P4 D5 diagnostic), 05577aa (P5 R1 sweep),
42aad15 (P6 gates).

## Verdict: PASS

## What was verified (all live or against committed state)

1. **Step-2b fix** (`computed_attribute_extractor.py:64-92, 151-166`): transitive
   `_ancestor_part_qns` walk over `heritage`/`Subclassification`; raw `::`-form QNs with
   the `__`-form trap documented in the docstring (the design's single most load-bearing
   note); prefixes carry a `::` suffix, closing the `Base`-matches-`BaseComponent`
   collision; Step-2b is `startswith(own) OR startswith(ancestors)`. The deliberate
   non-unification with `_supertype_closure` is commented with both divergences.

2. **Mutation check — executed live.** Ancestor acceptance removed from Step-2b →
   `test_inherited_ref_with_ancestor_prefix_is_formula` and
   `test_mixed_inherited_and_local_is_formula` FAIL (2 failed / 23 passed); revert →
   25/25 pass. The fix is pinned by live-classifier unit tests, not only the snapshot.

3. **Honest test collapse** (`test_computed_attributes.py:653-782`): 7-row single-column
   table with literal enum expectations; collapse guards `len == 7` and
   `sum(FORMULA) == 6` fail loudly on an empty/short table; D3 `mixed_expose` is the
   EXPOSE_COMPUTED over-correction control; zero `xfail` occurrences remain in the file.
   The spec's test-honesty trap (green empty parametrization) is structurally closed.

4. **Re-capture scope** (cb46b08): exactly one snapshot file
   (`unresolvable_attr_probe/extraction_snapshot.json`) + plan notes. The orthogonal
   `ife_plant` drift was filed, not smuggled in (attribution since corrected by Item 2's
   audit — pre-existing classifier staleness, neither Item 2 nor Item 4).

5. **D5 diagnostic** (`graph_builder.py:289-306`): FORMULA + not-FULLY_COMPILABLE → WARN
   + skip, with the fires-on-shape / silent-on-clean pair
   (`test_graph_builder_computed_attrs.py`, both caplog-asserted). INV-6 holds — full
   suite green including the clean-corpus warning pins.

6. **R1 docs/matrix**: matrix `:138` carries the corrected loud→silent narrative with the
   code citation; REQ-CA-12 added as a PASS row naming both the widened Step-2b contract
   and the D5 loud-no-module contract; epic `:41` corrected; recount **256 == 256** rows
   counted from `^| REQ-` (matches the summary block). Follow-on
   `[TRUTH-DEBT-INHERITED-FORMULA-COMPILE]` filed (P3).

7. **Gates — run live at HEAD**: 2086 passed / 4 skipped / **0 xfailed** (the 5 xfails are
   gone, count movement reconciled: +6 passed from new pins/flips), ruff 17 (≤17),
   mypy 97 (≤97).

## Notes

- The parametrized table pins the committed snapshot; the live classifier is pinned by the
  unit-test layer, and snapshot↔classifier agreement is pinned by the P2 reviewed
  re-capture. The three layers together close the loop; no single test is vacuous.
- SC-D's epic text asked for "the 5 cases PASS" — delivered as 6 FORMULA + 1 control rows
  (the depth-2 case was added to exercise the transitive walk; the design-review demanded
  it). Scope expansion is upward-honest, recorded in the plan.
