# Stage brief — Phase 1: Preserve the Incident

**You are executing exactly one phase** of the owner-approved recovery plan:
`/home/reid/1cfe/sysml-codegen/.project/active/cutover-recovery/plan.md` — Phase 1 only.
Read the whole plan first (especially "Non-Negotiable Execution Rules" and Phase 1), then the two
forensic records it cites for background:
`.project/research/20260810-213932_item7-cutover-incident-forensics.md` and
`.project/research/20260810-220500_item7-cutover-forensic-map.md`.

## Intent (why this phase exists)

The Item 7 cutover left a 327-file uncommitted mixed candidate on top of certified Item 6 work.
Everything later in the recovery depends on this phase making the incident recoverable **by content
hash** before anything changes. Preservation completeness beats speed. If any verification fails,
stop and report — do not improvise a repair.

## Provenance you must respect

- The plan is owner-approved for execution [OWNER 2026-08-10].
- Archive location `/home/reid/1cfe/item7-recovery-archive/` is an owner amendment (durable path;
  never `${TMPDIR}`/`/tmp` for the archive itself).
- `--no-verify` is pre-authorized for the two `FORENSIC SNAPSHOT` commits only, and only if hooks
  actually reject; record in the plan if used. All other commits must pass hooks.
- The two original branch refs must never move: `source-identity-epic` stays at
  `1672c5766f67e7716f3c9f8f636c21e2ea444601` (sysml-codegen), `elaborate-first-salvage` stays at
  `5088b417c9e5453271291d46cd5fb23fc0579b1e` (agentic-mbse, at `/home/reid/1cfe/agentic-mbse`).

## Execution notes (orchestrator guidance, not plan overrides)

1. Re-verify the "Verified Incident Baseline" facts first. Stop if any differ. (Expected: codegen
   105 M / 222 D / 30 untracked — the plan's forensics counted 27 before the three recovery
   artifacts were written; that delta is explained and fine. agentic-mbse 15 M / 1 untracked
   `.orchestrate-logs/`.)
2. Archive before any Git mutation: porcelain status (`-z`), `git diff --binary`, every untracked
   file, `.orchestrate-logs/` from both repos, `/tmp/elaborator-cutover-item7-candidate`,
   `/tmp/handoff-20260810-211932.md`, and `/tmp/item7-forensics-teax2.tJnvOM` (the independent
   forensic TEAx outputs). SHA-256 manifest over every member; then re-verify every digest.
3. Forensic branches: `item7-forensic-20260810` created from the current HEAD in each repo,
   carrying the dirty state; `git add -A` **minus** `.orchestrate-logs/` and OS-temp artifacts;
   commit message exactly `FORENSIC SNAPSHOT: failed Item 7 candidate; do not merge`.
4. **OID recording subtlety:** `.project/active/cutover-recovery/` is untracked, so it will be
   committed to the forensic branch and then removed from the original worktree when you switch
   back to `source-identity-epic`. You cannot leave the OID record in the original worktree.
   Instead write `phase1-results.json` into the archive root containing: both forensic commit
   OIDs, the manifest SHA-256, the archive path, verification outcomes, and whether `--no-verify`
   was needed. Phase 2 will restore the plan into the rebuild worktree and write these values into
   it. Also include the full text you would have added to the plan's Phase 1 completion notes.
5. After the forensic commits: move repository-local untracked orchestration logs into the archive
   (no `git clean`), switch both original directories back to their original branches, and verify:
   clean `git status --porcelain`, refs at the two recorded OIDs, forensic commits local/unpushed.
6. Manual spot-checks from the plan's validation list: open one modified production file, one
   deleted test recovered from the patch, one untracked Item 7 test, one corrupted reference doc
   (they carry SHA `713ecf4c…`), one raw log, and the failed candidate record — confirm the
   archived bytes are real.

## Report back

Finish with a summary of: archive path + manifest digest, both forensic OIDs, every validation
result (pass/fail, including the two ref checks), any deviation, and
`ARTIFACT: /home/reid/1cfe/item7-recovery-archive/phase1-results.json`.
