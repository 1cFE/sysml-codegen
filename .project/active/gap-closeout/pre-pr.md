# Pre-PR Gate: GAP-CLOSE Local Partial Wave

**Date:** 2026-07-18
**Repository / PR:** `sysml-codegen` PR #9, branch `constraint-exec-epic`
**Certification source:** [audit.md](audit.md)
**Verdict:** Pass for the certified local/in-scope partial wave

## Scope

This gate covers the audited GAP-CLOSE code, tests, documentation, dependency metadata and lockfile,
and project evidence. It preserves `.claude/projects/` and does not include companion orchestration
logs. The commit containing this record is the sysml-codegen candidate for the partial wave.

Companion PR #11 is already updated at `54a95d2ffe18f8e7b437a7f895843e0c89c98c27` and GitHub reports
it mergeable. Merge order is load-bearing: **agentic-mbse PR #11 first, then sysml-codegen PR #9**.

## Gate Results

- Focused GAP-CLOSE selection: **216 passed, 8 skipped, 9 deselected**.
- Default full suite without a SysIDE license: **2,220 passed, 205 skipped, 9 deselected, 23
  failed, 96 errors**. Every failure/error is in the known license-dependent families. The audited
  licensed candidate remains **2,516 passed, 26 skipped, 9 deselected**.
- Ruff source and changed/new GAP-CLOSE files: clean.
- Mypy: the recorded project baseline, **76 errors in 17 files**; no new GAP-CLOSE finding.
- `git diff --check`, debug-artifact, secret-pattern, and large-file scans: clean.
- Pre-PR removed trailing horizontal whitespace from new project artifacts. The two normalized
  evidence patches apply cleanly and regenerate their originally certified production diff hashes;
  both transport and regenerated hashes are retained in the item evidence.
- New GAP-CLOSE Python files pass `ruff format --check`. Four inherited whole-file format findings
  remain in `cli/__init__.py`, `pipeline_builder.py`, `graph_rebuild.py`, and `serializer.py`.
  Their baseline/candidate debt is recorded in the item evidence; bulk-formatting them would add
  unrelated churn and is outside this wave.

## Retained External Blocker

`[GAP-CLOSE-F1-TEAX-NORMALIZATION]` remains open. TEAx end-to-end evaluator normalization and
failed constraint-module identity are outside sysml-codegen and agentic-mbse. This gate certifies a
partial wave only. It does not certify full F1, complete the GAP-CLOSE epic, or authorize archival.
