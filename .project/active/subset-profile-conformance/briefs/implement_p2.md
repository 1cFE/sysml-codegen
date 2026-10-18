# Brief: /_my_implement Phase 2 of EXEC-SUBSET-CONTRACT Item 2a

Implement **Phase 2 only** (steps 2.1–2.4) of `.project/active/subset-profile-conformance/plan.md`, then stop and report. Phase 1 is done (see its notes in the plan). Read `design.md` (rev 3) and `spec.md` for the why; owner gates in `briefs/align.md`.

**First, tighten the agentic-mbse baseline.** The orchestrator ran `uv sync --all-extras` in the agentic-mbse worktree (2026-10-18). Its suite now has 5 failures instead of 129: `test_check.py::TestProbePandoc` ×2 and `TestRunCheck::...[identified-with-html]` (no Pandoc binary), and `test_index.py::TestScriptBackwardCompat` ×2 (hardcoded `/home/reid/1cfe/agentic-mbse`). Re-record the agentic-mbse baseline with `--all-extras` in `evidence/baseline.md`, confirm those 5 also fail at `ccd57d83` with all extras, and use the 5-ID set for this and every later phase gate. Keep the 129-ID record as history. Note the extras requirement in the phase gate.

Phase 1's note applies: add Phase 2's `tests/fixtures/subset_profile/` (or whatever collection directory you create) to `MODEL_COLLECTIONS` in codegen's constraint population oracle test.

Repositories:
- sysml-codegen: this worktree, branch `subset-conformance`.
- agentic-mbse: `/home/reid/src/subset-conformance/agentic-mbse`, branch `subset-conformance`. Never touch `/home/reid/src/agentic-mbse` or `/home/reid/src/sysml-codegen`.

Rules (same as Phase 1):
- Commit at the plan's commit points, on the `subset-conformance` branches only. Never push, merge or open PRs. End commit messages with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- Engineering bar: clean, well-factored code in each repo's idioms. No placeholders, no TODOs standing in for work, no screen-checks-itself tests. Stored expectations are hand-reviewed facts, not regenerated from either side; `disagreements.json` is hand-edited only.
- Never change what the generator accepts or refuses (RG-1). Record candidates and continue.
- If a plan premise proves false, stop at that point and report.
- Check off steps and add notes in `plan.md`.

End with a short report: commits, phase-gate results, deviations, decisions for me. End with `ARTIFACT: <path>`.
