# Phase 3 audit remediation

**Date:** 2026-08-18  
**Status:** [AGENT] Implemented; independent re-audit required  
**Codegen:** `stop-parser-impl-r2` at `3377cd0263ff9ad5699b84537bae03f55d11932a`  
**Agentic:** `3f8bd587af40f05b929dd56645901dada7daea37` (`semantic-evidence/v2`)

This is the implementation response to
[phase3-audit.md](phase3-audit.md). It preserves that audit's **Needs Work** verdict as a historical
record. It does not certify the remediation.

## Blocking findings

- **M1 — fixed at the ownership boundary.** The inventory unwraps unit annotations before assigning
  the alias/computed role and stores one authoritative site per declaration. Consumers retrieve that
  site instead of deciding the role again. `ExpressionInventoryError` is contained at the public
  conversion boundary and becomes `SI_EVIDENCE_INCOMPLETE` with authored reference, root-relative
  location, and cause. Public strict and lenient tests cover both a unit-annotated bare reference and
  a feature chain. Expression-keyed semantic errors also gain authored site context.
- **M2 — real per-consumer bypass tests added.** The tests now invoke the calculation-dependency,
  alias, computed-attribute, constraint-predicate, and binding-wiring adapters with an indexed use
  injected behind the inventory preflight. Each adapter's own backstop refuses it. Replacing all
  three `require_exact` calls with `require`, plus bypassing binding wiring, makes all five proof
  nodes fail.
- **M3 — every closed-union switch is pinned.** Direct tests enumerate the classifier, readiness,
  wiring, and `require_exact_binding_use` arms, including unknown objects. The four weakenings from
  the audit now each kill a kept proof. The last helper-arm proof was added in `3377cd0` after a
  disposable mutation run showed that the first remediation pass still missed it.
- **M4 — ownership identity includes the receiver.** A discovered read is keyed by module, function,
  selector, form, and receiver expression. Adding an unannotated second receiver inside a rowed
  function now leaves an extra discovered row and fails manifest equality.

## Minor and informational findings

| Finding | Disposition |
|---|---|
| m5 | Added a non-`Feature` middle-segment test; changing the raise to `continue` kills it. |
| m6–m8 | Replaced weak disposition nodes, corrected the completion record to say 13 tests pre-existed, and recorded that L-181 landed one commit after deletion. History was not rewritten. |
| m9 | Collision contracts resolve annotation names to import/local declaration origins; substring decoys no longer qualify. |
| m10–m11 | Evasion tests assert exact selector/form/receiver rows. `attrgetter`, `__getattribute__`, and `vars()[…]` are detected. The contract now says explicitly that the gate covers four reviewed selector names in the shipping package. |
| m12–m14 | Expression errors gain authored context; the complete role/site set has a direct test; `ConstraintDefinition.result_expression` is inventoried and an indexed definition body refuses at preflight. |
| m15 | Added a licensed public generation test proving a qualified predicate binds the exact target's safe local Python name. |
| m16–m17 | Reachability starts mechanically from the installed CLI and proves both public arms are reached. Every local `SourceFile.referent` receiver is tied to its annotated collection. |
| m18–m19 | Recorded an exact focused selection; moved `predicate_reference_name` to a module-level import. |
| i20–i21 | Corrected the serialized-key claim and described the gate as production-package-wide. |
| i22–i23 | Proof names must resolve to callable collected-looking tests; fixture metadata is described honestly as one explicit exception. |
| i24–i26 | Named both mypy baselines, added `[μSv/hr]`, and removed the anonymous-only filter from the real deep-override proof. |
| i27–i28 | A bound formal with no qualified identity now refuses by name. The out-of-scope dynamic-`getattr` residual has an explicit kept test. |

The product-lens response is recorded in `product-lens.md` as a candidate resolution of
`audit-phase3-F4`, with its gate still **PENDING INDEPENDENT RE-AUDIT**.

## Mutation evidence

The audit's weakenings were applied to a disposable extraction, not to the implementation worktree.

- Consumer backstop deletion: **5/5 proof nodes failed**.
- Binding union weakenings: classifier, readiness, wiring, and exact-use helper proofs all failed.
- Non-`Feature` deep-segment `raise` → `continue`: the totality proof failed.
- Second unannotated receiver in a reviewed function: the synthetic manifest-equality proof reports
  the added receiver as unreviewed.

## Reproducible source inputs

- Codegen archive SHA-256: `a0b9e138a41d4010f0ea0a450736f4b4e9c4e0d6a1b3af8ce02c1dfc4defd0d1`
- Agentic archive SHA-256: `c2924387d6d91360b951d5c9e17386b192148e2d719628feaec38fd41347afb2`
- Codegen history bundle SHA-256: `39c51da2a35dc44a67a28f4edc6120d26686b2885f5c8e0ef61206efa223e644`
- Source manifest: `/tmp/stop-parser-rev2/phase3-remediation-extraction-r3/artifact-source-inputs.json`

## Validation

- Exact 13-file evidence/binding/ownership/compiler/unit battery: **285 passed, 1 deselected**. The
  deselected node is the declared Phase 4 consumer-cell proof table.
- L-181 replacement gate: every named replacement proof is green.
- Targeted Ruff over changed Python: clean. Strict mypy over the two boundary modules: **0 errors**.
- `compileall` and `git diff --check`: clean.
- Full clean-extraction suite: **1 failed, 2,388 passed, 34 skipped, 94 deselected**. The sole
  failure is the declared Phase 4 consumer-cell proof table. There are no collection errors and no
  other failures. The run used the prepared offline wheel cache and an all-ref history bundle; the
  ledger/fingerprint topology subset is independently green (**61 passed**).

The independent Phase 3 re-audit is next. Phase 4 and Phase 5 remain unstarted; close and pre-PR
remain blocked.
