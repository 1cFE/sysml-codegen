# Stage brief — REVISE step 6: execute the retirement, for real, no trim

**You are executing owner step 5 of the REVISE path**: the actual retirement, on the actual
tree. Plan: `/home/reid/1cfe/sysml-codegen-item7-rebuild/.project/active/cutover-recovery/plan.md`.
Read first: `owner-disposition-20260811.md` (step 5), the plan's
"The retirement runbook — post-acceptance execution" section (~line 4612) IN FULL — every
order-critical fact below is stated there with its measured failure mode — and the REVISE
step 2/3 stage notes (they moved rows and regenerated patches).

Work synchronously. Never pause for background agents; finish or stop with questions.

## Intent

Execute runbook steps 1–4 in order on the real tree. Every prior simulation ran in scratch
worktrees; nothing has retired yet. The owner ruled: no provisional trim —
`runbook-patches/provisional-trim.txt` is a historical record and MUST NOT be passed to any
run. All 113 formerly-trimmed nodes are repointed or dispositioned (step 3); the batteries
must go green without deselection.

## The mechanics (from the runbook; the failure modes are measured, not hypothetical)

Per step N:
1. Ledger + work-list patches FIRST: for step 2 that is `ledger__L-011.patch`,
   `ledger__replacement-proof-nodes.patch`, then `scripts__retirement_worklist.patch`
   (`scripts__`, not `tests__`). `retire_step.py` reads the ledger and work-list to decide
   what to delete — a patch that changes either must land before it runs.
2. `$PY scripts/retire_step.py apply N` (git rm deletions, git mv archives).
3. Remaining patches: exclude the already-applied ones **by exact filename, not substring**
   (a substring exclude on `retirement_worklist` also drops
   `tests__unit__test_retirement_worklist.patch`, an ordinary test edit — measured: one red
   node).
4. Commit the step.
5. `$PY scripts/retire_step.py close N <oid>`, commit the ledger close — the checker fails
   on state claims otherwise.
6. Full battery (plan ~line 4731): licensed suite (delta explained row by row), execution
   lane, `capture_v6_batch.py --verify`, corpus `-k corpus`, ruff src + tree, mypy,
   `check_ledger_4a.py` paths/surface/groups/replacements, `check_proof_integrity.py`,
   `git diff --check`. On the REAL tree the scratch-only env vars (TEAX_SIMKIT_PATH,
   PYTHONPATH) are NOT needed — the venv is wired.

Step counts at HEAD (re-derive with `retirement_worklist.py check` / `step N` before
starting; the plan table says 102 / 153 / 1 / 5 with L-304 and the three `*_e2e.py` rows
pulled forward).

## Also inside this stage (each with its recorded authority)

- **Gated item 7 [OWNER 2026-08-11]:** the dead v5 exports in codegen
  `snapshot/__init__.py` (`SNAPSHOT_FORMAT_VERSION`, `CONSTRAINT_LOWERING_MODE_*`,
  `VALID_CONSTRAINT_LOWERING_MODES`, `SnapshotFormatError`, `GrandfatheredSnapshotError`,
  `assert_snapshot_certifiable`) go inside steps 1–2. No ledger row names them (the fifth
  entry, item 7); mint the row(s) under the orchestrator's delegated ledger authority,
  citing the owner ruling, before deleting.
- **The agentic legacy members** (step-2 ruling 5 and the L-036/L-037 records): after
  codegen step 2 removes the retirement-owned stack (the last codegen readers), delete in
  `/home/reid/1cfe/agentic-mbse-item7-rebuild` the neutral route — `extract_constraint_facts`,
  `evaluate_profile`, `ProfileResult`, `preflight`, their `sysml/__init__.py` publication
  surface — and realign `test_public_api_exports.py` to the identified names. Paired
  commits: agentic first, codegen references the OID if any codegen bookkeeping accompanies
  it. Run the agentic default suite (`pytest tests/`, never `-m ""`) + ruff/mypy after.
  Expected pre-state: agentic 1826 / 1 / 5, ruff src 1, tests 120, mypy 108 in 26.
- **Stale docstrings (audit, code-integrity):** `orchestration/elaborated_pipeline.py:1`,
  `orchestration/exact_pipeline_context.py:1`, `snapshot/instance_graph.py:1` still call the
  exact route Item-5-only/absent from the CLI. Amend to the current authority state in the
  step that touches their modules (or a final doc commit).
- **3E pins in amended forms:** where a step's patch amends a 3E pin, the amended form must
  still assert the present-tense truth of the retired tree (the plan's Gate 4C part 4 and
  step-3 notes list the touched pins).

## Non-negotiables

- Original repos and forensic branches untouched; archive read-only; no pushes/tags.
- No deselection lists anywhere in the final batteries.
- The v5 typed refusal must stay typed (loading a v5 snapshot fails with the typed error,
  not `KeyError`).
- Rule 10: any battery result the runbook did not predict, any file the work-list does not
  name, any patch that fails to apply → STOP with the evidence. Do not improvise a fix to
  keep a step moving. (If a patch is merely stale against a doc line, regenerating it from a
  scratch worktree at HEAD is the recorded procedure, not an improvisation.)

## Environment

Worktrees/venv/license/PATH as recorded in the plan Environment Setup; assert resolved
`__file__` first. Scratch worktrees (for patch regeneration only) beside the repos.
Expected clean start (post step 5-partial, HEAD c394640): licensed suite
**3870 / 47 / 83**, execution lane **83**, corpus `--check` 15/22/0, ruff src **16**, mypy
**69 in 16**, paths 304/0, surface 0, groups READY, replacements 221 green /
81 not-required / 0 fail, runbook patches 4 passed.

## Report back

Per step: rows executed (counts by action), battery table, commit OIDs (step + close).
The agentic deletion commit OID. The minted gated-item-7 row ids. Any pin amendments made.
Final tree state: suite numbers, and the grep evidence that the legacy surface is gone
(`build_pipeline_context`, v5 loaders, `legacy_route.py`, dual-run diff, the agentic neutral
route). Any rule-10 surfacing. `ARTIFACT:` the updated plan.
