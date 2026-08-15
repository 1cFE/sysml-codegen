# Stage brief — Independent audit of Slice 3B (defensive context + exact public projection)

Fresh, independent auditor; you did not implement this. Audit commit `d91431b` (+ OID record
`3f13f2f`) on `item7-rebuild` at `/home/reid/1cfe/sysml-codegen-item7-rebuild`, against the slice
contract: plan Slice 3B + "Validation for every Phase 3 slice" + Non-Negotiable Execution Rules,
plus the mid-slice orchestrator ruling recorded in the plan (group-identity option C) and the
prior audit record `evidence/audit-3a.md`. Do not trust the implementer's notes — read code and
run checks yourself. You have full permissions.

Environment: venv `/home/reid/1cfe/item7-rebuild-venv` (re-assert import paths — F2 trap in
`evidence/baseline.json`); license `set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a`;
proof = zero `no live syside license` skip lines. Scratch under `/tmp/claude-audit3b/`.
Read-only `git -C /home/reid/1cfe/sysml-codegen show 07531e64:<path>` approved for forensic
parts-bin checks. Never modify tracked files except writing
`.project/active/cutover-recovery/evidence/audit-3b.md`; never commit; never touch originals,
archive, or forensic branches.

## Verify (minimum; add your own judgment)

1. **Receipt-bound immutability is real.** Adversarially attack `ExactPipelineContext`
   (`orchestration/exact_pipeline_context.py`): mutate returned collections, rebind attributes,
   reach the underlying graph and edit it after build — confirm refusal or copy-isolation, and
   that the receipt actually detects a graph/context disagreement rather than comparing a copy
   to itself (the forensic candidate's projection-receipt test had exactly that defect).
2. **Option-C measurement claims.** Re-measure yourself: (a) exactly one projecting fixture's
   group identity changed vs `a7c13a6` (`elab_constraint_formal_identity`); (b) on stem-named
   fixtures, exact matches legacy except `d38_caret` + the legacy-only `system_design` group;
   (c) live / in-place v6 / relocated v6 entry-point group payloads are byte-equal, and the
   routes test asserts strict equality (no masked fields beyond the named provenance comments).
3. **The generated-package comparison is honest.** The claim: live vs relocated-v6 packages
   differ only in `SysML Source:` provenance comments, every differing file named and checked.
   Regenerate both yourself and diff the trees; confirm the test enumerates differences rather
   than allowlisting directories wholesale. Confirm the aggregation package really carries the
   `5.0` operand (B37-01 product surface).
4. **d38_caret pin honesty.** Confirm the divergence is genuinely pre-existing (reproduce at
   `a7c13a6`), that the pin test encodes it as a defect-to-disposition (not a passing
   guarantee), and that the implementer's no-second-stop judgment holds (i.e. option C neither
   caused nor could fix it).
5. **Rejected forensic material did not leak.** The three `orchestration/` files must be
   untouched vs `a7c13a6` except as declared; diff the new `exact_pipeline_context.py` against
   the forensic candidate's versions and confirm it is a reimplementation, not a rename-import
   of rejected hunks (especially the 13 deleted `pipeline_context` fields and the
   `snapshot_context` replacement).
6. **Gates re-run:** slice tests; full licensed suite (3519/47/18 claimed; delta must be exactly
   the 46 new tests, zero Item 6 tests removed); execution lane; ruff byte-identical; mypy set
   identical; `git diff --check`; changed paths ⊆ the declared set in the plan's 3B notes;
   legacy CLI smoke unchanged (48 files, `hif_plant_params.json`, `0.35`).
7. **Test quality** per the 3A bar: independently derived expectations, no self-comparison, no
   monkeypatching away the subject, tautology check on the new receipt/selection/mutation tests.

## Verdict

CERTIFY (nothing blocks 3C) / FINDINGS (numbered, severity, file:line evidence, concrete
resolution) / BLOCK (rule-10 conflict). State explicitly what you did not verify.
`ARTIFACT: .project/active/cutover-recovery/evidence/audit-3b.md`
