# Stage brief — REVISE step 6d: matrix re-citation + dead-surface dispositions

**You are closing the step-6c surfacings** so the step-7 final audit reads no known-stale
artifact and no undispositioned dead surface.
Plan: `/home/reid/1cfe/sysml-codegen-item7-rebuild/.project/active/cutover-recovery/plan.md`.
Read first: the 6c stage note (its rule-10 surfacing list is this stage's worklist),
`docs/architecture/verification-matrix.md` (the measurement banner), the deletion ledger's
per-row `replacement_proof_node` map, and `audit.md` "Product Judgment" (smell 1 — two
synchronized representations — is what the dead-surface items feed).

Work synchronously. Never pause for background agents; finish or stop with questions.

## Worklist

1. **Re-cite the verification matrix.** 56 of 81 cited test modules no longer exist. The
   ledger's replacement map records where each deleted module's responsibility went
   (`replacement_proof_node`, the step-3 repoints, the part-6 replacements). Re-cite row by
   row: each REQ's verification points at the kept node(s) that actually prove it on the
   retired tree. A REQ whose proof genuinely ended (subject deleted with its shape) gets the
   per-row note naming the recorded disposition, not a dangling citation. Recount the
   index/counts (auto-memory: index counts and missing REQ families are the real drift
   mode). The banner comes off only when every row is either re-cited or dispositioned.
2. **The duplicate catalog assembler.** `assemble_constraint_catalog` has no `src/` caller;
   three unit modules keep it alive beside the live assembler `generation/modules.py:157`
   path. Measure, then dispose: if it is a true duplicate representation, ledger row +
   delete + per-node test dispositions with named replacement (the live assembler's pins);
   if a test-only seam with a real distinct subject, record that and rename/re-home so it
   stops reading as a second authority. Smell 1 is the bar — two synchronized
   representations may not survive to the audit unexplained.
3. **The two extraction modules with no public caller** (6c note names them — re-measure).
   Same treatment: measure reachability from the shipped route and from kept tests; dispose
   via ledger (delete with replacements, or record the retained-subject reason inline where
   the checker can see it).
4. **`core/graph_algorithms.py`** (carried forward from pre-recovery notes): same
   measure-and-dispose.
5. **Docs 16/18** (owners deleted, shipped equivalents unwritten): author the two shipped
   equivalents IF the subject is a live shipped mechanism the reference set should describe
   (derive from what the docs' rows in `doc-update-list-4d.md` say the subject is); if the
   subject died with its owner, the historical banner is the correct end state — say so in
   the row and keep the banner. Do not write filler.

## Boundaries

- No R8/qualifier work; audit-F4 stays open; no batch/corpus/sealed-bytes changes.
- Deletions go through the ledger with `check_paths`-clean rows and per-node test
  dispositions (named replacements). The part-6 bar applies.
- Rule 10 stands.

## Environment

As prior stages. Clean start at codegen `610eca8` / agentic `3fbda2f`: suite
**1705 / 34 / 65**, exec lane **65** (invoke as `pytest tests/execution -m execution`),
`--verify` 15/22/0, corpus 9, ruff src **14** / tree **643**, mypy **57 in 11**, paths
304/0, surface 0, groups all-affected-0, proof 0/0, distinctness 31/0.

## Battery before each commit

Full licensed suite (delta named), exec lane if touched, `--verify`, distinctness,
ruff/mypy deltas explained, `git diff --check`, ledger paths/surface/groups +
`check_proof_integrity.py` + replacements if rows moved. Plan stage note updated.

## Report back

Matrix: rows re-cited / dispositioned counts and the final index numbers, banner state.
Each dead-surface item: the measurement, the disposition, the commit. Docs 16/18 outcomes.
Battery numbers; commit OIDs. Any rule-10 surfacing. `ARTIFACT:` the updated plan.
