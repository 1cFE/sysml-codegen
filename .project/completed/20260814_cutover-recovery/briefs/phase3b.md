# Stage brief — Phase 3, Slice 3B: Defensive context and exact public projection

**You are executing exactly one slice** of the owner-approved recovery plan:
`/home/reid/1cfe/sysml-codegen-item7-rebuild/.project/active/cutover-recovery/plan.md`.
Read first: Non-Negotiable Execution Rules, Phase 3 preamble (recovery import rule, test import
rule), Slice 3B, "Validation for every Phase 3 slice", and the Slice 3A completion notes +
`.project/active/cutover-recovery/evidence/audit-3a.md` (CERTIFY, with facts you inherit).

## Intent

Make the exact route's public construction defensive and its projection into the generation DTOs
exact — selection, receipts, mutation, aggregation — proven by kept public tests, while the old
builder and registry remain fully available as the shipped authority. The old route is a recovery
oracle; do not turn it into a second shipped route and do not delete any of it.

## State you inherit

- Worktree `/home/reid/1cfe/sysml-codegen-item7-rebuild`, branch `item7-rebuild`, head `a7c13a6`,
  clean. agentic-mbse rebuild worktree untouched this slice.
- Venv `/home/reid/1cfe/item7-rebuild-venv` — re-assert import paths before trusting (F2 trap in
  `evidence/baseline.json`). License: `set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a`;
  proof = zero `no live syside license` skip lines.
- Suite baseline after 3A: **3473 passed / 47 skipped / 18 deselected** licensed.
- Parts bin: forensic commit `07531e64…` via `git -C /home/reid/1cfe/sysml-codegen show`.
  Per-hunk review; Reuse / Reimplement / Reject recorded per file. The forensic map says
  `orchestration/pipeline_builder.py` (6 phases + full rewrite) and `elaboration/project.py`
  (3 phases) are the two worst multi-phase entanglements — per-hunk review or clean
  reimplementation is REQUIRED for them; never file-level import.

## Known defect you must fix (3A handoff — a 3B blocker pinned by test)

`_group_identity` (`elaboration/project.py:164`) names entry-point groups from the source path.
On the v6 route the source is a staging referent, so a generated package would ship
`inputs/root_0_params.json` / `Root0Params`. The pin is
`test_the_two_routes_diverge_only_on_source_derived_naming` (tests/conformance/
test_snapshot_v6_routes.py) — its docstring says 3B must fix it. Group identity must derive from
model semantics (the owning part/def identity already in the graph), not the file path; live,
v6-in-place, and relocated routes must then produce identical group names, and that test flips to
asserting equality.

## Scope (plan Slice 3B)

- Kept public tests FIRST (red at `a7c13a6`): selection, receipt, mutation, aggregation, and
  route-equality behavior through public entry points.
- Selectively recover `orchestration/{pipeline_context,pipeline_builder,snapshot_context}.py` and
  `elaboration/project.py` changes WITHOUT deleting the old builder/registry. Forensic test
  material to review (not blind-import): `tests/conformance/test_cutover_projection_receipt.py`,
  `test_cutover_target_selection.py`, `test_elaboration_occurrence.py` — note the forensic map
  found the projection-receipt test compared the run's own copy to itself (diluted); yours must
  compare against independently derived expectations.
- Old/new recovery comparison: run both routes on maintained fixtures and compare; hand/model
  values define correctness, the old route only detects change.

## Requirements

1. Tests red → production → green. Declare the expected path set BEFORE editing; stop on any
   unexpected changed path.
2. No deletion of legacy production, tests, probes, snapshots, docs. The 3473-test surface must
   survive intact; explain any collection delta exactly.
3. Defensive context: the public builder returns a receipt-bound context; mutations after build
   are refused or copy-isolated (follow the plan's language for 3B and the Item 7 spec's C-row
   intent as evidence, not authority).
4. Gates before commit: slice tests green; full licensed suite (zero license-skip lines; delta =
   exactly your new tests); execution lane; one generated-package smoke on live AND
   v6-snapshot routes (group names must now match); `ruff check src` byte-identical;
   `mypy src` no-new vs baseline; `git diff --check`; changed paths ⊆ declared set.
5. One slice commit on `item7-rebuild` + the OID-record commit, plan 3B boxes/notes/commit-gate
   updated, this brief committed with the slice.

## Hard rules

Unchanged from 3A: originals/archive/forensic untouched; no ref moves besides `item7-rebuild`;
rule-10 conflicts STOP the slice. If a hunk you want drags unrelated Phase 7 deletion behavior
into scope, Reimplement instead.

## Report back

What the slice proves, per-file dispositions with reasons, the `_group_identity` fix approach and
the route-equality flip, red→green counts, full-suite result + exact delta, gate results, old/new
comparison outcome, commit OIDs. `ARTIFACT:` the updated plan.
