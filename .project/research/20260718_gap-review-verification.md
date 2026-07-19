---
date: 2026-07-18
verifier: Claude (5 parallel verification subagents, independent reproductions)
topic: "Verification of the final constraint-expression gap review"
source_report: .project/research/20260718-123558_constraint-expression-final-gap-review.md
status: complete
---

# Verification: Final Constraint-Expression Gap Review

Every finding was independently re-verified against HEAD (sysml-codegen `6db3212`, agentic-mbse
`4ed2a07` — same code as the reviewed PR tips). Probes were fresh, not replays of the report's;
scripts live in the session scratchpad, repos untouched. **Verdict: the report is sound. All 10
findings confirmed; 3 carry material corrections; every hygiene note checks out.**

## Verdict table

| # | Finding | Verdict | Severity (report → verified) | Correction / sharpening |
|---|---|---|---|---|
| F1 | Admitted arithmetic raises (`ZeroDivisionError`, `OverflowError`) | **CONFIRMED** | High → **High** | Both shapes proven ADMIT under v3 (profile has no value-domain reasoning); Kleene guard catches non-finite values, not exceptions producing them. Direct INV-3 violation. |
| F2 | Sanitized predicate names collide → wrong predicate executes | **CONFIRMED** | High → **High (impact)** | Three collision classes reachable from plain legal SysML (case-fold, `_`-run collapse, quoted hyphen). No guard trips anywhere (`assert_same_ir`, ID mint, compiler check all pass). Likelihood low; silence is what keeps it High. |
| F3 | Metadata can't select the required companion | **CONFIRMED-WITH-CORRECTION** | High → **High-latent** | Imports SUCCEED on pre-v3; failure is the runtime v3 pin + `AttributeError` on `Eligibility.NON_NUMERICAL`. Zero evidence agentic-mbse is ever installed non-sibling (answers report OQ3): latent trap, not today-broken. |
| F4 | Mixed BLOCK+NON_NUMERICAL suppresses warnings | **CONFIRMED** | High → **Medium** | I2's NON_NUMERICAL clause is unsatisfiable on any halting run (no catalog exists) — drafted for generating runs. L6 still reports independently (D7). Real gap vs "never silent" within codegen + untested combination. |
| F5 | Anonymous excluded statements collide | **CONFIRMED** (incl. live end-to-end via syside) | High → **High (latent)** | All three exclusion kinds collide; eligible path is safe (keeps location). Corpus has zero anonymous constraints. Bonus defect: the collision error misdiagnoses a legal model as broken. |
| F6 | Transactional assignment skips defaulted fields | **CONFIRMED** | Medium → **Medium** | Sharpened: production eligible-path constructor omits `exclusion`, so that half is live on real lowered objects. `ConstraintCatalogEntry` has no hole (all fields required). |
| F7 | xor/implies arity malformations warn | **CONFIRMED** | Medium → **Low-Medium** | 0-operand xor round-trips the snapshot codec (reachable shape); live extraction can't produce it. Policy inconsistency vs the adjacent v2 arity gates, not an unsound ADMIT. |
| F8 | Contradictory quantity facts bypass ratio gate | **CONFIRMED** | Medium → **Medium** | Silent ADMIT, zero diagnostics — worst outcome class, inside the profile's own D-R3 malformed-snapshot responsibility. Not live-reachable (both `UnitFact` fields derive from one referent). `_quantity_ratio_fact`'s docstring claims to mirror `unit_compatibility`'s guard order and doesn't. |
| F9 | Verifier ignores unrecorded directory symlinks | **CONFIRMED** | Medium → **Medium, leaning High in the seal's threat model** | Unrecorded dir symlink smuggles an importable tree with `ok=True`; identical payload as a real dir is fatal; unrecorded FILE symlinks are caught. Internal dir symlinks also invisible. |
| F10 | Durable docs teach v2 | **CONFIRMED (every citation)** | Medium → **Medium** | `constraints.md` (wheel-shipped) teaches three outcomes / admitted equality / always-blocked xor; doc 28 lacks `excluded_records`; doc 27's "no lockstep surface" is contradicted by the loader's own pins. |

## Hygiene notes — all nine CONFIRMED, two with corrections

1. C901 complexity real (3 codegen + 4 companion hits) — **but C901 is in neither project's
   configured lint gate**, so it fails no repo-own check.
2. `tests/execution/conftest.py` hard-codes `/home/reid/1cfe/...`; lane excluded by default. ✓
3. No CI checks on either PR (no `.github/` in either repo). ✓
4. `ConstraintExclusion` / `ConstraintCatalogExcludedRecord` missing from `__all__`. ✓
5. `ConstraintCatalog` fingerprint docstring omits `excluded_records` (code hashes all three). ✓
6. Loader comment cites `constraint_lowering.py:463`; pin is at `:747`. ✓
7. Codegen warnings join reason codes only; design D5 promises the actionable message. ✓
8. `git diff --check` hits are real but **confined to `.project/` markdown** — zero in src/tests. ✓
9. Containment promotion flips only `force`; a halting error keeps the `warn_non_numerical_predicate`
   reason and "is not executed" prose — and our own halt test pins that misleading text. ✓

## Owner ruling — F1 policy (report OQ1)

**[OWNER]** Resolved 2026-07-18: a raised exception in constraint arithmetic (divide-by-zero,
overflow) is an **execution failure**, never a verdict — keep it small and clean. Rationale:
constraints check feasibility; a divide-by-zero is evidence of failure, not of an infeasible
design. This matches the concept's existing line ("thrown predicate code [is an] execution
failure"; Design Principle 4) — the Kleene machinery keeps only its value job: a non-finite
*value* → indeterminate; an *exception* → failure. Accepted consequences, stated at ruling
time: (1) Python's operator quirks draw the line (silent-`inf` overflow → indeterminate;
raising overflow → failure) — document, don't fight; (2) one failing constraint module means
that candidate yields no constraint report (execution_failed case), not a partial one.

F1's fix shape under this ruling: NO arithmetic guards in generated predicates. Normalize the
raise into the evaluator's phase-tagged failure outcome naming the constraint; tighten the
template docstring to the narrow DP4 promise ("never raises *because the verdict went against
the assertion*"); add divide-by-zero/overflow tests asserting **failure**, not indeterminate.

## Disposition recommendation (verified severities)

- **Merge-gating (fix before the wave merges):** F1 (per the owner ruling above), F2
  (post-sanitization collision rejection or hash suffix), F5 (keep the location component when
  minting excluded IDs).
- **Cheap, ride the same fix wave:** F4 (warn before the blocking raise), F6 (initialization-state
  guard instead of `fields_set`), F3 (version bump + floor — latent but one-line), F7/F8 (profile
  default-deny patches; arguably v3-defect fixes under its own documented default-deny rule, not
  semantic changes needing v4 — confirm at fix time), F9 (dir-symlink policy).
- **Docs/metadata closeout:** F10 + hygiene 4–7, 9.
- Report OQ2 (are anonymous executable assertions supported?) needs an owner ruling — F5's fix
  shape depends on it only for the *eligible* compile-key limitation, which is pre-existing and
  separately bookable.

Probe scripts: session scratchpad (`probe_f1.py`, `probe_f2.py`, `probe_f4_f5.py`,
`probe_live_anon*.py`, `probe_f6.py`, `probe_f9.py`, `probe_f7_f8.py`). No repo modifications
were made during verification.
