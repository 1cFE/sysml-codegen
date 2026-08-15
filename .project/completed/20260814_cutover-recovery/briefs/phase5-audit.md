# Stage brief — Phase 5 final independent audit of the Item 7 recovery candidate

You are the recovery's final independent auditor. You implemented none of it. Your record is
what the owner reads beside the candidate; overclaiming green is the failure that caused this
entire recovery — your job is to be the person who would have caught the original incident.

## What you audit

The candidate: sysml-codegen `item7-rebuild` at `c4e9b76` (+ evidence commits `013d6a1`,
`3a6532d`) at `/home/reid/1cfe/sysml-codegen-item7-rebuild`, paired with agentic-mbse
`item7-rebuild` at `cc6c7a7` at `/home/reid/1cfe/agentic-mbse-item7-rebuild`. Everything is
available to you, per the plan's audit clause:

- The plan (`.project/active/cutover-recovery/plan.md`) — the authority, with every orchestrator
  ruling recorded inline.
- The candidate record `evidence/candidate.{json,md}` and all evidence artifacts (hashes in the
  record).
- The full commit series on `item7-rebuild` (from `4e6a116`), each commit's claims.
- The forensic branch `item7-forensic-20260810` (codegen `07531e64`, agentic `ed5b8b02`) in the
  ORIGINAL repos — read-only.
- The clean Item 6 bases (`1672c57`, `5088b41`) and the Phase 2 `evidence/baseline.json`.
- All prior audit records `evidence/audit-*.md` — inherit their stated not-verified lists; those
  are your highest-value targets.
- The external archive `/home/reid/1cfe/item7-recovery-archive/` (read-only).

Environment: venv `/home/reid/1cfe/item7-rebuild-venv`; ASSERT all three import paths first;
license `set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a` (zero license-skip lines is
the only proof); scratch worktrees beside the repos, never in `/tmp` (recorded path-resolution
trap). Write only `.project/active/cutover-recovery/evidence/audit-5-final.md`; no commits.

## Method (read code and run checks; never trust notes)

1. **Re-run the acceptance battery once yourself**, from your own shell: both suites, corpus
   with exact multisets, `--verify`, execution lane incl. real TEAx live + relocated (the
   anchor values), checker modes, distinctness. Compare against the three-run table.
2. **Attack the recovery's central claims,** sampling where volume forbids completeness:
   - single public authority + present-but-unreachable legacy (hunt an escape hatch);
   - the v6 envelope's identity model incl. the ACCEPTED residual (re-run a forgery probe);
   - hand-arithmetic anchors re-derived from the SysML (not the transcription module);
   - the runbook's mechanical claim (replay at least step 1 in scratch from the patches alone,
     following only the runbook text — you are the fresh-agent test);
   - the ledger's closure (invent a deletion the three axes might miss; check unrowed);
   - the reconciliation (independently diff test inventories vs Item 6 and vs baseline.json);
   - the decision surface's honesty (each of the 7 gated items and 11 residuals: is the
     measurement real and the cost stated fairly? sample at least half).
3. **Inherited not-verified items** from audit-3a..3e and audit-4: sweep them; anything still
   unverified either gets verified now or named in your record.
4. **Read the commit series** as a reviewer would (subjects vs contents, every OID-record
   chain); flag any commit whose message claims more than its diff.
5. **The original incident's four owner complaints** (deleted spikes/docs stubs/broken
   extraction/no progressive commits): verify each is affirmatively remedied in the candidate.

## Verdict

CERTIFY (with the accepted-residual list restated) / FINDINGS (numbered, severity, evidence,
resolution) / BLOCK. State what you did not verify. Your record closes with a one-page summary
written for the owner — plain language, the working-voice rule.
`ARTIFACT: .project/active/cutover-recovery/evidence/audit-5-final.md`
