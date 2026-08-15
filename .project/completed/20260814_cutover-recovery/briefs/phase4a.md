# Stage brief — Phase 4, Gate 4A: Rebuild the responsibility/deletion ledger

**You are executing exactly one gate** of the owner-approved recovery plan:
`/home/reid/1cfe/sysml-codegen-item7-rebuild/.project/active/cutover-recovery/plan.md`.
Read first: rules (esp. 6, 7, 11-as-amended), Phase 4 preamble + Gate 4A, the Phase 3 completion
notes, ALL audit records `evidence/audit-3{a,b,c,d,e}.md`, and the forensic reconciliation in
`.project/research/20260810-220500_item7-cutover-forensic-map.md` (Finding 2).

**This gate deletes NOTHING.** It produces the reviewed ledger that every later deletion must
match exactly. The ledger approval authority is the orchestrator (owner-delegated, recorded in
rule 11); your output goes to the orchestrator for review, so it must be readable and complete —
a reviewer must be able to check any row without re-deriving your work.

## Why this gate exists

The original Item 7 deleted 222 files under a census that could not see deletions: 118 of 327
changed paths omitted, 100 `migrate` rows deleted before replacements existed, 12 files with no
authority at all, and a gate that accepted absence as proof. Gate 4A is the corrective: a ledger
derived from Git truth, closed under exact equality, with per-row replacement proof.

## Inputs (all already in the tree)

- **Deletion proposals:** the forensic candidate's 222 tracked deletions
  (`git -C /home/reid/1cfe/sysml-codegen diff --name-status 1672c57 07531e64` minus the plan's
  own restores), reconciled classes from the forensic map: 54 explicit `delete` rows
  (presumptively valid — recheck authority/reachability/replacement, do not rubber-stamp),
  100 `migrate`-before-replacement, 56 group-covered, 12 hard-unauthorized.
- **The 100 responsibility rows** from the 3E reclassification (16 modules), each already naming
  a Gate 4C owner — these are binding constraints: `replacement_is_green(row)` must hold before
  the production owner a row references may be deleted.
- **Accumulated named ledger inputs from Phase 3:** the 8 retained duals (3C); the
  legacy-named `_CONSTRAINT_LOGGER` (3C F4); the v5 transitive re-export residual via
  `snapshot/__init__.py` (3E); the two v5 residues from 3E F5; ledger row 36's untyped
  clear-then-fail refusal (also a 4C candidate: it contradicts fail-before-mutate on one path);
  `scripts/capture_extraction_snapshots.py` as the last v5 producer; the CLAUDE.md `restore`
  disposition (Phase 2); the `--design-path-filter` flag removal; the 22 architecture docs
  (restore-then-rewrite is Gate 4D's, but the ledger names them).
- Legacy production owners: the census SCR/TEST/PROD families in
  `.project/active/elaborator-cutover/cutover-census.md` (intact, SHA-verified) as EVIDENCE;
  authority is your fresh derivation.

## Requirements (plan Gate 4A, operationalized)

1. Generate the candidate inventory from Git truth: for the rebuild, that is the set of paths
   whose deletion 4B will propose (legacy production owners + their exclusive helpers), the
   test/probe/snapshot families 4C will review, and the doc set 4D owns. Every row: path,
   class (production / test / script / snapshot / probe / doc), disposition
   (delete / migrate / retain / archive), authority (census row, plan rule, Phase 3
   responsibility row, or "new — orchestrator approval required"), replacement proof node
   (exact test id that must collect+pass), and blocking rows.
2. **Exact equality check:** implement a checker asserting the ledger's path set equals the
   Git-derived set (no orphan rows, no uncovered paths). It must be able to SEE deletions
   (operate on the diff, not the worktree — the original's defect).
3. **Implement `replacement_is_green(row)` for real:** resolves the named replacement node,
   asserts it collects and passes in the required suite. Negative tests: missing node,
   deselected node, failing node. Absence checks cannot satisfy it.
4. Unreachability proof for production rows: for each proposed production deletion, show the
   public call graph no longer reaches it (the 3E construction-closure machinery is available)
   and name the kept public test that pins the replacement behavior.
5. Order 4B into small coherent groups (plan: unreachable adapters first, central legacy
   resolver/registry/snapshot owners last), each group listing its rows, its pre-deletion test
   additions if any, and its post-deletion battery.
6. No broad catch-all rows. Every path individually listed. Probes/spikes: preserve-by-default;
   any archive/delete proposal needs a per-path reason (rule 7 — final approval on those lists
   is the orchestrator's, recorded).
7. Ledger lives at `.project/active/cutover-recovery/ledger-4a.md` (+ machine-readable
   `ledger-4a.json` the checker consumes). Commit the ledger + checker + tests once green;
   the orchestrator then reviews before ANY 4B work.

## Hard rules

No production/test/doc changes beyond the ledger, checker, and their tests. Declared path set
first. Suites unaffected (delta = checker tests only). Rule-10 conflicts (a row whose authority
and evidence disagree; a responsibility with no possible replacement) → surface in the ledger
with class CONFLICT, don't resolve silently; the orchestrator rules on those at review.

## Report back

Ledger statistics (rows by class/disposition, CONFLICT count), the 4B group ordering, checker +
replacement_is_green results, unreachability summary, anything you could not derive, commit OIDs.
`ARTIFACT: .project/active/cutover-recovery/ledger-4a.md`
