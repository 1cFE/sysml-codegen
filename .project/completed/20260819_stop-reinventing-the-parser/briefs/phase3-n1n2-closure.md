# Brief — Phase 3 closure round: re-audit findings N1 and N2

Small, sharply-scoped round. The Phase 3 re-audit ruled **Pass with findings**
(`.project/active/stop-reinventing-the-parser/run-records/phase3-audit.md`, "Re-audit of the
remediation" section — read it first, N1 and N2 specifically). Your job is to close those two
findings and nothing else. Do not reopen any confirmed-closed finding, do not refactor beyond
the findings' reach, do not start Phase 4 work.

## Where you work

- Codegen worktree: `/tmp/stop-parser-rev2/worktrees/sysml-codegen`, branch
  `stop-parser-impl-r2` at `3377cd0` — verify clean before starting. Implementation commits go
  here.
- Docs checkout: `/home/reid/1cfe/sysml-codegen` (branch `stop-reinventing-the-parser`) — the
  record corrections and a short closure note, committed as your final act.
- Agentic worktree `/tmp/stop-parser-rev2/worktrees/agentic-mbse` at `3f8bd58`: read-only.
  Touch nothing else — no user checkouts, no stash/reset/switch anywhere.
- License for any licensed test: `set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a`;
  never copy a secret anywhere. Never invoke the Agentic slow PDF/HTML corpus or paid/network
  cases (owner-verbatim standing exclusion).

## N1 — the fourth union-arm proof proves nothing

**The fact (verified by the re-auditor, mutation-run):** deleting the closing `isinstance`
raise in `_resolve_bindings` (`elaborate.py:2571-2572`) produces **zero** test failures,
because `binding_source.py:180` raises an identical `TypeError` one line downstream and the
kept proof's `match="BindingSourceEvidence"` matches both. The arm is unproven; the remediation
record's claim "the four weakenings now each kill a kept proof" is false for this arm.

**Fix — measure first, then take exactly one of these routes:**

- **(a) Discriminate the sites.** Give the `elaborate.py` arm its own failure identity (a
  message naming its seam, distinct from `binding_source.py:180`'s), and pin that exact
  identity in the kept proof so the arm's deletion changes the observed identity and kills the
  test.
- **(b) Delete the redundant arm.** If the closed union's own `require` function is the
  designed single owner of that refusal (design rev 8 D7 spirit — one owner per decision, the
  same shape as the M1 fix) **and** removing the arm still typechecks (check whether that raise
  is what satisfies mypy's exhaustiveness/return analysis on the function), delete the
  `elaborate.py` arm and make the kept proof target `binding_source.py:180` by mutation
  instead.

Decision rule: prefer (b) for single ownership; fall back to (a) if (b) fails the scoped
strict gate or if you find a real behavioral reason the elaborator must refuse at its own seam
(if so, state it). Either way:

- **Prove the kill.** Run the exact mutation the re-auditor ran (delete the surviving arm /
  the new proof target in a throwaway copy) and record that the kept proof now fails, by node
  ID, with the failure output. This is the acceptance criterion.
- Correct the false sentence in `run-records/phase3-remediation.md` to what is now true.

## N2 — untraceable suite figures in the remediation record

`run-records/phase3-remediation.md` (and any echo in plan.md's Phase 3 completion) quotes
"Focused: 285 passed, 1 deselected" and "Ledger/fingerprint topology: 61 passed" with no
recorded file set or command. The re-auditor's reconstructions (303 and 94, both green) did not
match, so the figures cannot be recomputed by a reader.

**Fix (documentation only):** for each figure, either write the exact pytest invocation (the
full file list / deselect expression) beside it and rerun that exact command to confirm the
number as stated, or replace the figure with a command you record plus the count it actually
produces today. Every suite number in the record must be recomputable from what the record
itself says. Do not touch any other number.

## Validation

- The N1 mutation kill, recorded as above (this is the point of the round).
- Focused suites touched by your change green; scoped strict gate
  (`uv run --extra dev mypy --strict src/sysml_codegen/extraction/binding_source.py
  src/sysml_codegen/elaboration/expression_evidence.py`) zero; targeted Ruff clean on changed
  files.
- If you took route (b): rerun the binding-focused conformance/unit tests and confirm no
  behavioral change (the refusal still happens, from the single owner, with the same public
  shape).
- `git diff C_base -- src/sysml_codegen/elaboration/occurrence.py` still empty. Both worktrees
  and both user checkouts clean apart from your intended commits.

## Deliverables

1. One implementation commit on `stop-parser-impl-r2` (or two if test and production split more
   cleanly), no drive-by changes.
2. Record corrections committed in the docs checkout: the corrected N1 sentence, the
   recomputable N2 figures, and a short dated "N1/N2 closure" note appended to
   `run-records/phase3-remediation.md` stating route taken, the mutation-kill evidence, and
   commit SHAs.
3. Final message: prose — which N1 route and why, the kill evidence, what the N2 figures now
   say — ending with
   `ARTIFACT: .project/active/stop-reinventing-the-parser/run-records/phase3-remediation.md`.
   If anything outside this scope turns out to be entangled, stop and say so rather than
   expanding the round.
