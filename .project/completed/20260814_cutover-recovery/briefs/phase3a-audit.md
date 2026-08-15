# Stage brief — Independent audit of Slice 3A (v6 envelope + source admission)

You are a fresh, independent auditor. You did NOT implement this slice. Audit commit
`fe0b855` (plus its OID-record commit `687f748`) on branch `item7-rebuild` at
`/home/reid/1cfe/sysml-codegen-item7-rebuild`, against the slice contract in
`.project/active/cutover-recovery/plan.md` (Slice 3A + "Validation for every Phase 3 slice" +
Non-Negotiable Execution Rules). Owner-mandated: findings must be resolved before Slice 3B starts.

## Why this audit exists

The original Item 7 run failed precisely because its own gates self-certified (a census that
couldn't see deletions, tests asserting a script's self-report, docs stubbed to pass residue
scans). Your job is to read code and run checks yourself — never trust the implementer's notes or
commit message. The forensic context is in `.project/research/20260810-213932_*.md` and
`20260810-220500_*.md`.

## What to verify (minimum; add your own judgment)

1. **The identity-swap hole is actually closed.** The implementer removed free-form
   `model_name`/`captured_at` from the envelope so a re-labelled snapshot cannot be expressed —
   a deliberate sealed-format semantics change. Adversarially attempt a model-identity swap or
   smuggled identity field against the real loader (write a small probe; re-seal the edited
   document the way a forger would). Confirm refusal, and confirm the residual offline limit is
   documented, not overclaimed.
2. **Envelope matrix completeness** — the plan pins: missing/current/future versions; missing,
   added, wrong-typed outer fields; graph replacement; identity skew; ordinary inner tamper;
   valid inner graph inside a tampered outer envelope. Check each cell has a real test asserting
   on the public loader behavior (not internals), and each refusal is exercised against a
   re-sealed document (else the digest check masks the case).
3. **v5 untouched:** confirm no v5 production/test path changed or was deleted; full-suite delta
   vs baseline (3358/47/18) is exactly the new tests.
4. **Route equality is real:** live vs v6-in-place vs relocated compare the full projected
   surface, not a summary; capture determinism and self-containment tests actually delete/move
   what they claim.
5. **Test quality:** expectations independently derived (hand/model values, exact vocabularies),
   no test that asserts a copy against itself, no monkeypatching away the thing under test, no
   tautological assertions. This was the failed candidate's signature defect.
6. **Gates re-run:** slice tests; `ruff check src`; mypy vs the 72-error baseline;
   `git diff --check`. Full licensed suite if feasible (license:
   `set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a`; venv
   `/home/reid/1cfe/item7-rebuild-venv`; proof = zero `no live syside license` lines). Changed
   paths of `fe0b855` ⊆ the declared set recorded in the plan's 3A notes.
7. **Dispositions honest:** spot-check the per-file Reuse/Reimplement/Reject claims against the
   forensic parts bin (`git -C /home/reid/1cfe/sysml-codegen show 07531e64:<path>`) — e.g. that
   "Reuse with 3 edits" files really differ only as claimed, and Rejected material didn't leak in.

## Rules

- Read-only with two exceptions: you may write throwaway probe scripts under
  `/tmp/claude-*/` or a scratch dir, and run test/lint commands. Do NOT modify tracked files,
  commit, or touch the original worktrees/forensic branches/archive.
- Verdict must be one of: **CERTIFY** (no findings that block 3B), **FINDINGS** (list each with
  severity, exact file:line evidence, and what would resolve it), or **BLOCK** (a rule-10 premise
  conflict). Overclaiming green is the failure mode this recovery exists to fix — if you didn't
  verify something, say so explicitly.

## Report back

Verdict + numbered findings with evidence + what you ran (commands + outcomes) + anything you
could not verify. `ARTIFACT:` your audit record written to
`.project/active/cutover-recovery/evidence/audit-3a.md` — this is the one tracked file you may
create (do not commit it; the orchestrator handles commits).
