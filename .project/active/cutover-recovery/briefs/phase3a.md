# Stage brief — Phase 3, Slice 3A: V6 envelope and source admission

**You are executing exactly one slice** of the owner-approved recovery plan:
`/home/reid/1cfe/sysml-codegen-item7-rebuild/.project/active/cutover-recovery/plan.md`.
Work ONLY in the rebuild worktrees. Read the plan first: the Non-Negotiable Execution Rules,
Phase 3 preamble (recovery import rule, test import rule), Slice 3A, and "Validation for every
Phase 3 slice". Background: the two forensic research records in `.project/research/20260810-*.md`
(restored in this worktree).

## Intent

Recover the v6 snapshot envelope + staged source admission as the first vertical slice, proven by
kept public behavior tests — while v5 production and its tests stay fully intact. The forensic
candidate got this mostly right but its loader **accepts a re-sealed model-identity swap**; your
slice must close that hole. Quality bar: this code becomes the product's snapshot authority —
clean, well-factored, no compatibility shims.

## State you inherit

- Rebuild worktrees: codegen `/home/reid/1cfe/sysml-codegen-item7-rebuild` (branch `item7-rebuild`,
  head `beee0f4`), agentic-mbse `/home/reid/1cfe/agentic-mbse-item7-rebuild` (untouched this slice).
- Venv `/home/reid/1cfe/item7-rebuild-venv` — **re-assert import paths before trusting it**
  (a cached editable wheel once silently pointed at the original worktree; finding F2 in
  `evidence/baseline.json`). License: `set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a`;
  the only license proof is zero `no live syside license` skip lines.
- Measured Item 6 baseline: codegen 3358 passed / 47 skipped / 18 deselected (licensed);
  inventory in `evidence/baseline.json`.
- Parts bin: forensic commit `07531e64…` in the ORIGINAL repo `/home/reid/1cfe/sysml-codegen`
  (`git -C /home/reid/1cfe/sysml-codegen show 07531e64:<path>`). Never merge or cherry-pick;
  read files, review per hunk, and declare Reuse / Reimplement / Reject per the plan's
  recovery import rule. Record dispositions in the slice completion notes.

## Scope (plan Slice 3A)

Candidate production paths from the forensic branch (single-phase-owned per the forensic map,
Phase 1/2 of the failed run):
- `src/sysml_codegen/snapshot/envelope.py` (new), `src/sysml_codegen/snapshot/source_manifest.py`
  (new), changes to `snapshot/instance_graph.py` and `snapshot/capture.py`, plus the MINIMUM
  live/load integration needed for the vertical route. If a candidate hunk drags in
  `orchestration/pipeline_builder.py` (a 6-phase entangled file), prefer Reimplement of the
  minimal seam over importing the forensic rewrite.
- Fast-track test candidates (still need red→green review, not blind import):
  `tests/unit/test_source_admission.py`, `tests/conformance/test_snapshot_v6_routes.py`,
  plus `tests/conformance/test_snapshot_v6_envelope.py`, `test_snapshot_v6_capture.py`,
  `test_source_admission_routes.py` from the forensic tree as material.

## Requirements

1. **Tests first, red.** Write/adopt kept live/v6/relocated public behavior tests before recovering
   production code; show they fail (or fail to collect) at the baseline.
2. **Pin the complete v6 envelope matrix** (plan names it): missing/current/future versions;
   missing, added, wrong-typed outer fields; graph replacement; `model_name` and `captured_at`
   skew; ordinary inner tamper; valid inner graph inside a tampered outer envelope; and the
   must-fail **re-sealed model-identity swap** the failed candidate accepted.
3. **Preserve v5.** All v5 production code and tests stay; the full suite must still collect and
   pass everything it passed at baseline. Explain any collection delta exactly.
4. Declare the expected changed-path set BEFORE editing; stop if an unexpected path changes.
5. Gates before commit: slice tests green; full licensed suite (compare to 3358/47/18 + your new
   tests, zero license-skip lines); one generated-package smoke; `ruff check src`; mypy no-new
   vs the 72-error baseline; `git diff --check`; changed paths ⊆ declared set.
6. One commit on `item7-rebuild` (codegen only), message leading with what the slice proves.
   Update the plan: tick 3A boxes, fill the 3A commit-gate row, write completion notes with the
   per-hunk dispositions. Include this brief and plan updates in the commit.

## Hard rules

- Never modify the original worktrees, the archive, or any ref other than `item7-rebuild`.
- No deletion of legacy production, tests, probes, snapshots, or docs in this slice.
- Rule-10 premise conflict (e.g. the forensic envelope design can't close the identity-swap hole
  without changing sealed-format semantics) → STOP and report.

## Report back

Summary: what the slice proves, per-file dispositions (Reuse/Reimplement/Reject with reasons),
test counts red→green, full-suite result + delta explanation, gate results, commit OID.
`ARTIFACT: <path to updated plan>`
