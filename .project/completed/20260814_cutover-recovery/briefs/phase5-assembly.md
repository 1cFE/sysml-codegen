# Stage brief — Phase 5: assemble the repeatable candidate

**You are executing the candidate assembly** of the recovery plan:
`/home/reid/1cfe/sysml-codegen-item7-rebuild/.project/active/cutover-recovery/plan.md` — Phase 5,
"Changes required", EXCEPT the independent audit (separate stage follows you) and the owner stop
(the orchestrator composes that). Read first: Phase 5's plan text, the Phase 4 completion +
runbook records, `evidence/baseline.json` (the Phase 2 inventory you reconcile against), and
the audit records. Environment discipline binding: assert all three import paths, license
sourcing, scratch placement rule.

## The candidate's shape (be exact)

The candidate is the CURRENT tree pair: codegen `item7-rebuild` HEAD + agentic-mbse
`item7-rebuild` `cc6c7a7`. It contains: the exact route as sole public authority (since 3E),
the legacy stack present-but-unreachable with its retirement proven mechanical and gated on
owner acceptance (the runbook + 55 patches + PROPOSED v6 batch), and seven owner-gated items.
The candidate record must present that state truthfully — it is a certification of what IS,
plus a priced decision surface for the owner.

## Required

1. **Candidate record** `.project/active/cutover-recovery/evidence/candidate.json` (+ readable
   `candidate.md`): both repo OIDs, branch names, full `git diff --stat` vs the Item 6 bases,
   path inventories, test inventories (vs the Phase 2 baseline, every delta explained by ledger
   authority — the reconciliation the plan demands), corpus outcomes, environment (interpreter,
   resolved import paths, teax HEAD `fa0e06a9`, syside/producer versions), performance numbers,
   and SHA-256 hashes of every evidence artifact (batch manifest, patches, audit records,
   baseline.json).
2. **Three consecutive complete runs**, identical results required: full licensed codegen
   suite, agentic suite (from the paired worktree), 37-path corpus with both error classes and
   exact multisets vs the amended ledger, `--verify` 15/22/0, execution lane incl. real TEAx
   live + relocated at the anchor values, the checker modes, doc distinctness, ruff/mypy.
   Record each run's numbers separately — identical means identical, and a flake is a finding,
   not a re-roll.
3. **Scale measurement:** warm-up + repeated (≥3) timed runs of the public generation path on
   fusion_tea and the two D-5 scale variants; declare the budget you measure against (the Item
   7 design's scale budget if recorded in the shaping artifacts, else record measured numbers
   as the new declared baseline with no pass/fail claim).
4. **Residue and boundary checks:** import-boundary tests, the single-authority pins, no
   forensic-branch import anywhere (grep for the forensic OIDs/paths), `git diff --check`,
   clean status both repos at recorded OIDs.
5. **The owner decision surface, assembled in `candidate.md`:** the PROPOSED batch (with the
   revision price), the retirement runbook state (mechanical, conditions), the seven gated
   items each with its measurement and cost, and the accumulated named residuals from Phases
   3–4 (the offline-provenance limit, module source_file divergence, d38_caret/
   unresolvable_attr_probe ledger amendments, zero-constraint mechanism, V11 structural
   coverage, units-gap story, S4/Item-10 cross-reference, fingerprint residual). Each entry:
   what it is, the evidence pointer, what accepting/deferring costs. No new decisions — this
   collates recorded ones.

## Rules

No production or test changes. If any run diverges from the recorded expectations: rule-10
STOP with the divergence (do not re-run until it passes). Batteries are the runs themselves.
Commit the record + any run artifacts; OID-record commit after.

## Report back

The three-run table, scale numbers, reconciliation summary (counts + the explained deltas),
the decision-surface table of contents, hashes, commit OIDs.
`ARTIFACT: .project/active/cutover-recovery/evidence/candidate.md`
