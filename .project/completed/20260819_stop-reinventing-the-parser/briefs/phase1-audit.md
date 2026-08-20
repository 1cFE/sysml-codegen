# Brief — Phase 1 audit (dedicated, fresh)

You are the independent auditor for **Phase 1 only** of this item. The implementing agent's claims
are recorded in plan.md's "Phase 1 completion" section; your job is to try to break them, not to
summarize them. Reproduce what can be reproduced; verify the rest against artifacts. Trust
nothing that is only asserted.

Read in order:

1. `.project/active/stop-reinventing-the-parser/plan.md` — Revision 3: the Phase 1 contract
   (checklist, validation boxes, Global Execution Contract) and the completion record you are
   auditing.
2. `design.md` Revision 7 — `#what-the-lock-is-verified-against`,
   `#the-missing-committed-check--phase-1-adds-it`,
   `#the-indexed-red-set--both-cases-are-required-kept-tests`, `#current-code-facts`,
   `#checked-consumer-and-ownership-manifests`, `#occurrence-and-producer-matrix`.
3. `run-records/phase1-stop-report.md` — the ruled history, so you know what was already settled.

## Where the work is

- Codegen worktree `/tmp/stop-parser-rev2/worktrees/sysml-codegen`, branch `stop-parser-impl-r2`:
  audit commit `e4e2693` against base `C_base` = `78a9beb9…`.
- Agentic worktree `/tmp/stop-parser-rev2/worktrees/agentic-mbse`, branch
  `stop-parser-evidence-r2`: audit commit `85c7758` against `A_base` = `2171016d…`.
- You may run tests and read anything in those worktrees. You must not modify them, commit, or
  touch any other checkout. License: `set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a`
  (never copy a secret into output). Codegen: `uv run --extra dev`; Agentic: `uv run`.
- **[OWNER-VERBATIM]** "do not rerun the PDF suite anymore" — the slow PDF/HTML corpus and the 15
  paid/network cases are outside validation; do not invoke or report them.

## Audit obligations

1. **Diff-level scope check.** The commits must contain only tests, manifests, fixtures for those
   tests, and ledger/manifest rows the plan places in Phase 1. Any production-source byte change in
   either repo is a Critical finding. Confirm `git diff C_base -- src/` and the Agentic equivalent
   are empty, and that `occurrence.py` is byte-identical to `C_base`.
2. **Reproduce the three-leg lock verification** yourself: leg 1 from the lock file's own
   `probe_fixture_commit` field (118/118 against `20f9e60a`'s tree), leg 2 through the committed
   validators, leg 3 current-byte pinning with the single ledger-owned `capture_baseline.py`
   difference. Then audit the new kept check
   (`tests/conformance/test_probe_fixture_lock.py`) against the design's five bullet obligations —
   including that it reads the field rather than hard-coding `43edf9bd`, and that its anti-vacuity
   assertions are real (would a truncated lock file or an unread row actually fail it?).
3. **Red-set quality.** For each recorded red node ID: run it; confirm it is red for its **exact
   stated reason** (Case 1: zero-diagnostic graph silently binding occurrence zero, sealed by the
   capture arm; Case 2: `SI_OCCURRENCE_AMBIGUOUS` under strict — not a fixture/license/import
   failure, not an incidental error). Audit the test bodies: when Phases 2-4 make them green, do
   the assertions then demand the full contract (exact code, authored reference, refusal before
   consumers, no graph, no snapshot bytes) — or could a weak implementation slip through? Softened
   or tautological assertions are Major findings.
4. **D1-D4 preservation.** Rerun the occurrence/producer matrix named by the design; confirm zero
   regressions and that `deep_cross_scope_probe` still refuses (`SI_OCCURRENCE_MISSING`) with no
   captured snapshot present.
5. **Completion-record accuracy.** Every claim in the Phase 1 completion section (counts, node
   IDs, hashes, "identical at phase start and end") must be true or the record corrected. An
   overstated record is a finding even when the underlying work is sound.
6. **The three surfaced items.** Assess each (the artifact-source manifest import constraint; the
   extraction-only default suite at `C_base`; the strict/lenient delivery gap in the design's
   behavior matrix for Case 2). For each: is the implementer's characterization accurate, is it
   pre-existing or introduced, and does it need an owner/design decision before Phase 2? Do not
   fix them.
7. **Vacuity sweep.** Any new test that cannot fail (asserts on empty iteration, catches too-broad
   exceptions, compares a value to itself) is a finding regardless of its color today.

## Deliverable

Write `.project/active/stop-reinventing-the-parser/run-records/phase1-audit.md` (do not commit):
verdict `Pass` / `Pass with findings` / `Fail` for Phase 1, findings ranked with severity and
exact locations, your reproduction results (commands + outcomes), and a short "fit for Phase 2?"
judgment. Final message: prose summary ending with
`ARTIFACT: .project/active/stop-reinventing-the-parser/run-records/phase1-audit.md`.
