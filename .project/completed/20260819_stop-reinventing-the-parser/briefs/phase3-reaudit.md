# Brief — Phase 3 re-audit (independent, fresh): verify the remediation of a Needs Work verdict

You are the independent re-auditor for **Phase 3** of this item. A prior independent audit
returned **Needs Work** with 4 Majors, 15 Minors, and 9 Informationals; a remediation round
claims to have addressed all of them. Your job is to try to break the remediation, by execution,
from your own extractions — not to summarize it. The original verdict stands until you rule.
Phase 4 is blocked on your report.

Read in order:

1. `run-records/phase3-audit.md` — the original audit: findings, severities, and crucially its
   **methods** (the mutation/deletion experiments that exposed M2/M3/M4). You will rerun those
   methods.
2. `run-records/phase3-remediation.md` — the remediation's claimed disposition, finding by
   finding.
3. `plan.md` — Revision 4: the Phase 3 contract and completion record.
4. `design.md` — Revision 8: `#d7-one-codegen-conversion-boundary`, the Codegen-gate manifest
   subsection ("unannotated receiver never qualifies"), `#d8-diagnostic-ownership`,
   `#one-total-inspection-operation`.

## Where the work is

- Codegen worktree `/tmp/stop-parser-rev2/worktrees/sysml-codegen`, branch `stop-parser-impl-r2`:
  remediation commits `c604165` → `41181bd` → `3377cd0` on top of audited `e3e1a39`.
- Agentic worktree `/tmp/stop-parser-rev2/worktrees/agentic-mbse` must be untouched at
  `3f8bd58` — verify, read-only.
- Build your own extraction(s) under `/tmp/stop-parser-rev2/` (`git archive`; Agentic-related
  paths must contain `agentic-mbse`; full-suite numbers come from a declared extraction — see
  plan.md Phase 1 deviations 1-2). Modify nothing, commit nothing, touch no other checkout.
- License: `set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a`; never copy a secret.
- **[OWNER-VERBATIM]** "do not rerun the PDF suite anymore" — the Agentic slow PDF/HTML corpus
  and 15 paid/network cases stay unrun.

## Obligations, in priority order

1. **M1 by live execution.** Author a minimal valid model with an alias-role unit-annotated
   reference — the original crash shape:

   ```sysml
   package M1Check {
       public import ScalarValues::*;
       public import SI::*;
       part def Rig {
           attribute base_len : Real = 2.0;
           attribute mirror_len : Real = base_len [m];
       }
       part rig : Rig;
   }
   ```

   At `e3e1a39` this died out of `sysml-codegen generate` with a bare
   `ExpressionInventoryError` (no code, no reference, no file:line) — reproduce that first at
   the old commit's extraction to anchor the before-state, then prove the after-state: the same
   model must now either generate correctly or refuse with a full public diagnostic (code,
   authored reference, root-relative `file:line`, cause chain). Then probe **around** the fix:
   other role × unit-annotation combinations (computed attribute, predicate, calculation
   dependency, deep override where expressible), operator-wrapped and compound-unit variants of
   the alias shape. The original audit's root cause was a *duplicated role predicate*; verify
   the remediation's claim that role assignment now has exactly one owner (the inventory) — by
   code inspection AND by checking no second predicate survives that could disagree.
2. **M2/M3 by rerunning the deletion experiments.** The original audit deleted the backstop
   from all five consumer adapters: 0 new failures across 2206 tests. Rerun exactly that (in a
   throwaway copy): the new per-consumer bypass tests must now fail per adapter. Same for the
   four union switch arms (including the authored-index-reclassification arm): each deletion
   must now kill at least one kept test. The claim is "the audit's mutations now kill their
   proofs" — hold it to that, mutation by mutation, and record the kill table. Also check the
   new tests are structurally real: each must route through the actual consumer adapter, not a
   shared library call with a role label.
3. **M4 by the second-receiver escape.** Add (in a throwaway copy) a second unannotated
   receiver inside a function that already has a manifest row; both gates must go red. Verify
   the manifest key now includes the receiver and that existing rows still carry the
   design-required proof artifacts.
4. **Minors and Informationals.** Spot-check the 15+9 dispositions against
   `phase3-remediation.md` — verify at least the ones marked "code" or "test" by execution or
   direct read; "honest record correction" ones by comparing record text to measurement. Flag
   any disposition that re-words a finding instead of closing it.
5. **No regression.** Full suite from your fresh extraction (claimed: 2388 passed / 34 skipped /
   94 deselected / 1 expected Phase 4 failure — verify, and confirm the 1 failure is exactly
   `test_every_consumer_cell_names_a_proof`); focused suites (claimed 285/1); scoped strict
   zero; D1-D4 and the retained harness; `git diff C_base --
   src/sysml_codegen/elaboration/occurrence.py` empty; `deep_cross_scope_probe` still refused
   with no captured snapshot; repo-wide mypy/Ruff baselines unchanged; ledger/fingerprint
   topology (claimed 61 passed); both user checkouts matching `run-records/entry-status.md`
   digests.
6. **Vacuity sweep of every remediation-added test** — a test that cannot fail is a finding
   regardless of color, and this item has now produced that failure mode twice.

## Deliverable

Append a dated "Re-audit of the remediation" section to
`run-records/phase3-audit.md` (do not commit): per-finding Confirmed-closed / Not-closed with
your evidence, the M2/M3 kill table, any new findings ranked by severity, and a final ruling —
does the Phase 3 verdict move from Needs Work to Pass (with or without findings), and is the
phase fit for Phase 4? Final message: prose summary ending with
`ARTIFACT: .project/active/stop-reinventing-the-parser/run-records/phase3-audit.md`.
