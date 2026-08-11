# Stage brief — Independent composite audit of Phase 4

Fresh, independent auditor; you implemented none of this. Audit Phase 4 of the recovery plan:
`/home/reid/1cfe/sysml-codegen-item7-rebuild/.project/active/cutover-recovery/plan.md` — from
the Gate 4A commit (`804d8a2`) through the current head. Contract: the plan's Phase 4 (as
amended by the recorded orchestrator rulings, including the retirement resequencing), the
approved ledger `ledger-4a.md`/`.json`, the runbook, and the prior audit records
`evidence/audit-3*.md`. Full permissions; environment discipline is binding (venv
`/home/reid/1cfe/item7-rebuild-venv`, paired worktree `agentic-mbse-item7-rebuild`, ASSERT
import paths before any measurement — a 4D session lost hours to that trap; license `set -a;
source /home/reid/1cfe/agentic-mbse/.env; set +a`, proof = zero license-skip lines). Write only
`.project/active/cutover-recovery/evidence/audit-4.md`; no commits.

Phase 4's failure mode in the original run was self-certification at scale. Your job: verify
the recovery's Phase 4 did not repeat it in subtler form. Sample adversarially — the volume is
too large for full re-verification, so pick the highest-risk claims and go deep.

## Verify (minimum)

1. **The executed deletions (G0+G1).** Re-verify the C1 evidence chain yourself
   (preservation.py owns the responsibility; its tests pass; the deleted module was genuinely
   dead). Re-run the C2 specimen and confirm fail-before-mutate on the collision path. Confirm
   the error-class moves preserved exception identity for existing catchers.
2. **The checker machinery is sound.** `check_ledger_4a.py` (paths/surface/groups/replacements)
   and `check_proof_integrity.py`: read the code, then try to defeat each — e.g. a row whose
   proof node exists but is vacuous, a file importing a delete-row surface through an alias the
   AST walk misses, a fixture-data read through an indirection the textual scan misses. Report
   what the machinery would and would not catch; run their own test suites.
3. **Disposition sampling, 25+ rows across all classes** (retire-with-owner / repoint /
   archive-with-findings / defer resolved in part 7): for each sampled row, check the
   responsibility statement is true (the named replacement actually covers the behavior — read
   both tests), the node accounting is accurate, and import-localization claims hold. Weight
   toward: the execution-lane restoration (15 nodes vs the legacy 15 — per-node accounting),
   the part-6 re-derivations (mechanism citations real?), and chunk 17-19 (the last, most
   fatigued work).
4. **The dual measurements.** Re-run at least two of the eight dry-run probes (one codegen, one
   agentic) and confirm the recorded failure classes; verify the two unrowed agentic call sites
   (`level4_constraints.py:55`, `level6_architecture.py:620`) are real and that the runbook's
   owner-gated fifth entry carries them.
5. **The runbook's "mechanical" claim.** Walk step 1's per-node edit table against the tree:
   would executing it as written actually leave the suite green and every pin satisfied?
   Identify anything the runbook underspecifies (you cannot execute it — desk-check with
   targeted measurements).
6. **The proposed v6 batch.** Re-run `--verify`; spot-check three snapshots against live
   capture; confirm PROPOSED marking everywhere it should be and that nothing in the tree
   treats the batch as accepted authority.
7. **4D docs.** Read the 10 rewritten docs in full against the code at HEAD (claim-by-claim for
   00, 27, and CLAUDE.md at minimum); spot-check the banners' three-part content; run the
   distinctness check; confirm the two stale production docstrings noted at 4D are still the
   only ones (sweep for siblings).
8. **The gates.** Full licensed suite (expect 3840/47/53, zero license lines — assert paths
   first); corpus ledger; execution lane 53; `--verify`; ruff/mypy; the batteries recorded at
   each Phase 4 commit spot-checked for internal consistency (numbers that changed without
   explanation).
9. **Cross-cutting honesty check:** grep the Phase 4 records for claims marked measured and
   sample-verify 5; find any claim that was carried forward without re-measurement (the 3D
   audit's F1 class).

## Verdict

CERTIFY (Phase 5 assembly may start) / FINDINGS (numbered, severity, evidence, resolution) /
BLOCK. State explicitly what you did not verify — the Phase 5 auditor inherits your record.
`ARTIFACT: .project/active/cutover-recovery/evidence/audit-4.md`
