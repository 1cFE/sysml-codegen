# Stage brief — REVISE step 7a: three consecutive gate runs on the retired tree

**You are executing owner step 6 of the REVISE path**: the full licensed suites and real
TEAx against the actual retired tree, under the Phase 5 three-identical-runs protocol.
Plan: `/home/reid/1cfe/sysml-codegen-item7-rebuild/.project/active/cutover-recovery/plan.md`.
Read first: the plan's Phase 5 run protocol and `evidence/phase5-runs/` (the run scripts and
`build_candidate.py`), `owner-disposition-20260811.md` (steps 6–7), and the REVISE stage
notes 6/6b/6c/6d (what changed since the scripts were written).

Work synchronously. Never pause for background agents; finish or stop with questions.

## Intent

Three consecutive complete runs on the retired tree, compared field by field by the builder,
not by eye. This is measurement and record only: ZERO product, test, ledger, or doc changes.
If any gate fails or any field differs between runs, STOP and surface — do not fix and
re-run.

## The environment (absolute; the 6d stage burned itself ignoring this)

The ONLY environment is `/home/reid/1cfe/item7-rebuild-venv` (`$V/bin` on PATH, license
sourced from `/home/reid/1cfe/agentic-mbse/.env`). FIRST ACTION: assert resolved `__file__`
for `sysml_codegen` → `sysml-codegen-item7-rebuild`, `agentic_mbse` →
`agentic-mbse-item7-rebuild`, `simkit` → pinned teax. Never touch
`/home/reid/1cfe/agentic-mbse` or `/home/reid/1cfe/sysml-codegen` (protected originals; the
canonical venv makes them irrelevant). Exec lane invocation: `pytest tests/execution -m
execution` from the codegen worktree. Agentic suite: `pytest tests/` (never `-m ""`).

## Per run (×3, identical)

codegen: licensed suite (zero `no live syside license` lines — the only valid proof), exec
lane, `capture_v6_batch.py --verify` then `--check`, `-k corpus`, ruff src + tree, mypy,
`check_ledger_4a.py` paths/surface/groups/replacements, `check_proof_integrity.py`,
doc-distinctness, `git diff --check`.
agentic: default suite, ruff src + tests, mypy, `git diff --check`.

Adapt the `phase5-runs` scripts to the retired tree if their paths/commands are stale
(script edits under `evidence/phase5-runs/` are record-tooling, allowed; nothing else is).
Expected values (from the stage notes; verify, don't assume): codegen **1705 / 34 / 65**,
exec **65**, `--verify` 15/22/0, corpus 9, ruff **14 / 641** (canonical ruff 0.16.2), mypy
**57 in 11**, paths 304/0, surface 0, groups all-affected-0 READY, replacements 221/81/0,
proof 0/0, distinctness 31/0; agentic **1826 / 1 / 5**, ruff src 1 / tests 120, mypy 108
in 26. Scale/RSS measurement per the Phase 5 protocol if its scripts still apply.

## Report back

The three-run comparison table (every field, three columns, identical or STOP), run
artifacts committed under `evidence/phase5-runs/` (new subdir, e.g. `revise-runs/`), the
HEAD OIDs measured (codegen + agentic), commit OID for the artifacts. Any deviation is a
rule-10 stop, reported with the differing fields. `ARTIFACT:` the run-comparison file you
commit.
