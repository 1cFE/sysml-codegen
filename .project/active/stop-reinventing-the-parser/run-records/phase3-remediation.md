# Phase 3 audit remediation

**Date:** 2026-08-18  
**Status:** [AGENT] Implemented; independent re-audit passed with findings; N1/N2 closure applied
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
- **M3 — each distinct closed-union decision is pinned.** Direct tests enumerate the classifier,
  readiness, and `require_exact_binding_use` arms, including unknown objects. The re-audit showed
  that `_resolve_bindings` repeated the helper's unknown-object refusal with the same identity, so
  that local arm was not a distinct decision and could not be proved independently. Follow-up
  `1451615` deletes the redundant arm, pins wiring's delegation to the helper, and leaves the helper
  as the single owner. Deleting the helper's surviving unknown-object refusal now kills
  `test_require_exact_binding_use_switch_is_exhaustive`.
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
| m18–m19 | The N1/N2 closure section records the exact focused and topology selections; `predicate_reference_name` moved to a module-level import. |
| i20–i21 | Corrected the serialized-key claim and described the gate as production-package-wide. |
| i22–i23 | Proof names must resolve to callable collected-looking tests; fixture metadata is described honestly as one explicit exception. |
| i24–i26 | Named both mypy baselines, added `[μSv/hr]`, and removed the anonymous-only filter from the real deep-override proof. |
| i27–i28 | A bound formal with no qualified identity now refuses by name. The out-of-scope dynamic-`getattr` residual has an explicit kept test. |

The product-lens response is recorded in `product-lens.md` as a candidate resolution of
`audit-phase3-F4`, with its gate still **PENDING INDEPENDENT RE-AUDIT**.

## Mutation evidence

The audit's weakenings were applied to a disposable extraction, not to the implementation worktree.

- Consumer backstop deletion: **5/5 proof nodes failed**.
- Binding union weakenings: the classifier, readiness, and exact-use helper proofs all fail. Wiring
  delegates unknown values to that helper, and its kept proof fails if a local duplicate intercepts
  the delegation.
- Non-`Feature` deep-segment `raise` → `continue`: the totality proof failed.
- Second unannotated receiver in a reviewed function: the synthetic manifest-equality proof reports
  the added receiver as unreviewed.

## Reproducible source inputs

- Codegen archive SHA-256: `a0b9e138a41d4010f0ea0a450736f4b4e9c4e0d6a1b3af8ce02c1dfc4defd0d1`
- Agentic archive SHA-256: `c2924387d6d91360b951d5c9e17386b192148e2d719628feaec38fd41347afb2`
- Codegen history bundle SHA-256: `39c51da2a35dc44a67a28f4edc6120d26686b2885f5c8e0ef61206efa223e644`
- Source manifest: `/tmp/stop-parser-rev2/phase3-remediation-extraction-r3/artifact-source-inputs.json`

## Validation

- Exact 13-file evidence/binding/ownership/compiler/unit battery: **290 passed, 1 deselected**. The
  deselected node is the declared Phase 4 consumer-cell proof table. Exact invocation:

  ```bash
  uv run --offline --extra dev pytest \
    tests/conformance/test_expression_evidence_integrity.py \
    tests/conformance/test_expression_evidence_ownership.py \
    tests/conformance/test_elaboration_aggregations.py \
    tests/conformance/test_usage_owned_reference_anchoring.py \
    tests/conformance/test_constraint_binding_unit_annotation.py \
    tests/conformance/test_predicate_unit_annotation.py \
    tests/conformance/test_unit_annotation_values.py \
    tests/conformance/test_expression_compiler.py \
    tests/conformance/test_exact_compiler_core.py \
    tests/unit/test_expression_evidence_boundary.py \
    tests/unit/test_expression_compiler.py \
    tests/unit/test_predicate_compiler.py \
    tests/conformance/test_upstream_pins.py \
    -k "not test_every_consumer_cell_names_a_proof"
  ```
- L-181 replacement gate: every named replacement proof is green.
- Targeted Ruff over changed Python: clean. Strict mypy over the two boundary modules: **0 errors**.
- `compileall` and `git diff --check`: clean.
- Full clean-extraction suite: **1 failed, 2,388 passed, 34 skipped, 94 deselected**. The sole
  failure is the declared Phase 4 consumer-cell proof table. There are no collection errors and no
  other failures. The run used the prepared offline wheel cache and an all-ref history bundle.
- Ledger/fingerprint topology subset: **83 passed**. Run from
  `/tmp/stop-parser-rev2/phase3-remediation-extraction-r3/extracted/codegen/sysml-codegen` against
  the source manifest and history root recorded above. Exact invocation:

  ```bash
  STOP_PARSER_ARTIFACT_SOURCE_INPUTS=/tmp/stop-parser-rev2/phase3-remediation-extraction-r3/artifact-source-inputs.json \
  PYTHONPATH=/tmp/stop-parser-rev2/phase3-remediation-extraction-r3/extracted/codegen/sysml-codegen/src \
  /tmp/stop-parser-rev2/worktrees/sysml-codegen/.venv/bin/python -m pytest \
    tests/conformance/test_elaboration_corpus_ledger.py \
    tests/conformance/test_exact_route_fingerprint_stability.py \
    tests/conformance/test_evidence_artifact_topology.py \
    tests/unit/test_check_ledger_4a.py -q
  ```

The independent Phase 3 re-audit that followed is recorded in `phase3-audit.md` as **Pass with
findings**. Phase 4 and Phase 5 remain unstarted; close and pre-PR remain blocked.

## N1/N2 closure — 2026-08-18

**N1 — route (b), one refusal owner.** Codegen follow-up
`1451615609e29b1f511c6b8e69fe425d8afe355e` removes `_resolve_bindings`' redundant unknown-value
guard. There is no separate elaborator behavior to preserve: the next call already delegates to
`require_exact_binding_use`, the closed union's owner, and scoped mypy remains clean. The kept wiring
proof now requires that delegation, while the helper's own exhaustive-switch proof pins the public
`TypeError` identity.

The acceptance mutation was run in a throwaway extraction of `1451615`: delete the final
unknown-value `raise TypeError` from `require_exact_binding_use`, then run

```bash
python -m pytest \
  tests/unit/test_expression_evidence_boundary.py::test_require_exact_binding_use_switch_is_exhaustive \
  -q
```

The kept node fails exactly at its unknown-value assertion:

```text
FAILED tests/unit/test_expression_evidence_boundary.py::test_require_exact_binding_use_switch_is_exhaustive
E   Failed: DID NOT RAISE <class 'TypeError'>
1 failed
```

**N2 — commands and counts are explicit.** The two opaque figures are replaced above by the exact
13-file command (**290 passed, 1 deselected**) and the exact four-module command (**83 passed**).
No other validation figure changed in this closure round.

**Commits:** Codegen `1451615609e29b1f511c6b8e69fe425d8afe355e`; documentation corrections
`cd9f3b9bc0d8682ee09a93c1a1a579d8faa86e82`.
