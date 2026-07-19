# Audit: CONSTRAINT-WAVE Item 4 — Snapshot Portability and Shape Gates

**Verdict:** Certify
**Audited:** 2026-07-19
**Branch:** constraint-exec-epic
**Commit:** 512786c (candidate changes are uncommitted)

---

## Summary

Every prior Needs Work finding remains remediated in the current worktree. The newly available
license closes the last open acceptance leg: the real harness captured equivalent roots A and B,
then passed the exact live A/live B/replay A and moved-replay manifest without normalization or root
leakage. Item 4 is fully certified; the earlier license-free findings and Item 2/6 boundaries remain
unchanged.

## Findings

### Plan completion

- **Prior finding 1 — live/replay route structure: remediated.** The live collector builds a live
  context and generates with `models_path`; the replay collector rebuilds from the snapshot and
  generates with `from_snapshot` (`tests/conformance/test_constraint_snapshot_portability.py:184`,
  `tests/conformance/test_constraint_snapshot_portability.py:204`). A license-free wiring test pins
  the mutually exclusive configurations and call sequence (`tests/conformance/test_constraint_snapshot_portability.py:294`).
  The real licensed node captures A and B, then collects live A, live B, and replay A in that order
  before moved replay (`tests/conformance/test_constraint_snapshot_portability.py:367`).
- **Prior findings 2–3 — reproducible complete fixture transaction: remediated.** Tests first
  reconstruct legacy absolute locations in temporary copies of the canonical corpus
  (`evidence/test_update_fixture_locations.py:21`). Preparation computes complete fixture and
  `baseline_outputs` manifests; staging records original/candidate manifests and hashes; commit
  verifies staged candidates and post-write manifests; recovery restores and verifies the complete
  originals (`evidence/update_fixture_locations.py:129`,
  `evidence/update_fixture_locations.py:143`,
  `evidence/update_fixture_locations.py:273`,
  `evidence/update_fixture_locations.py:305`). Eleven kept cases cover prepare, validation failure,
  staged mismatch, both replacement failures, post-write failure, all four journal phases, success,
  cleanup, and canonical idempotence (`evidence/test_update_fixture_locations.py:51`).
- **Prior finding 4 — BLOCK calls and exact bytes: remediated.** The route-count regression proves
  the two earlier NON_NUMERICAL siblings map/validate once while the following BLOCK record receives
  zero route calls (`tests/conformance/test_constraint_snapshot_identity.py:286`). The committed
  fixture pins the complete canonical warning string and canonical excluded-record JSON bytes, with
  a license-free replay assertion (`tests/conformance/test_constraint_non_numerical.py:16`,
  `tests/conformance/test_constraint_non_numerical.py:97`).
- Phases 1–5 and the audit-remediation phase are verified complete. The formerly open licensed live
  acceptance gate passed with the repository-local license loaded through `uv run --env-file .env`.

### Spec conformance

- **SC-1 — portable excluded-location projection: verified.** Live lowering owns one lazy selected-
  index projection cache and passes canonical values to warnings, exclusions, and anonymous minting
  (`src/sysml_codegen/analysis/constraint_lowering.py:872`). Snapshot capture deep-copies facts and
  applies the same production selector to every located exclusion
  (`src/sysml_codegen/snapshot/serializer.py:139`). Exact warning, record, catalog, contract, report,
  fingerprint, and root-leak projections pass on moved replay.
- **SC-2 — both relocation scenarios: verified.** The three-node relocation file passed with a
  licensed SysIDE process. Its real node captured equivalent model trees at A and B, collected live
  A, live B, and replay A through their distinct routes, compared the complete specified manifest,
  then replayed the unchanged moved snapshot/tree. The earlier moved-replay digest and route-wiring
  controls remain valid (`tests/conformance/test_constraint_snapshot_portability.py:144`,
  `tests/conformance/test_constraint_snapshot_portability.py:367`).
- **SC-3 — ID and eligible-byte stability: verified.** Named exclusion minting remains location-free;
  anonymous exclusion minting retains canonical referent/line/column and its 32-hex suffix
  (`src/sysml_codegen/analysis/constraint_lowering.py:920`). Named and anonymous eligible controls,
  repeated live-shaped lowering, and replay controls pass.
- **SC-4/SC-5 — total contextual v3 gate and field-policy matrix: verified.** The former 223-line
  switch is split into named definition, formal, usage, source, owner, actual, context,
  redefinition, diagnostic, ExpressionIR, occurrence, and envelope validators
  (`src/sysml_codegen/snapshot/loader.py:181`, `src/sysml_codegen/snapshot/loader.py:387`,
  `src/sysml_codegen/snapshot/loader.py:619`). Validation precedes reconstruction, and only the two
  in-scope reconstructors have narrow chained normalization boundaries
  (`src/sysml_codegen/snapshot/loader.py:788`, `src/sysml_codegen/snapshot/loader.py:792`). The independently declared missing-field,
  wrong-type, nullable, optional, empty-list, JSON-literal, compatibility, pointer, and residual-
  cause tables collect 336 cases (`tests/unit/test_snapshot_v3_gate.py:600`,
  `tests/unit/test_snapshot_v3_gate.py:612`, `tests/unit/test_snapshot_v3_gate.py:806`). All pass in
  normal and optimized modes.
- **SC-6 — controlled fixture consequences: verified.** The updater is idempotent at
  `9ae5cfc4…44d6` and `605f549e…c02`. The complete fixture and baseline manifest digests reproduce
  `92b9f2da…3099` and `921bbb6a…bf66`. The only fixture diff is 65 removed/65 added location lines in
  CATF and 1 removed/1 added location line in the non-numerical snapshot; all 30 snapshots load and
  no transaction directory remains.
- **SC-7 — validation ladder: verified.** The full focused Item 4 and transaction selection passed
  407/407 normally and 407/407 under optimized Python with the license loaded. The licensed full
  repository suite independently passed 2,950 tests with 26 skips and 10 deselections. The earlier
  overlay, broader families, Item 2/6 overlaps, fixture/inventory, and Item 3 isolation evidence is
  preserved; fresh Ruff, format, and diff checks pass.
- **Requirements and non-goals:** R-6 and R-11 are delivered without a schema bump, legacy-section
  promotion, eligible-location rewrite, Item 3 implementation, companion edit, commit, push, PR
  interaction, or remote-state change.

### Design conformance

The implementation follows D1–D7 and I1–I11 in the inspected live and replay flows. Projection is
selected, lazy, route-explicit, and separate from ID minting. The loader retains the recursive
unknown-extra version sentinel and confines normalization to the two specified reconstructors. The
fixture updater stages and verifies full manifests before and after replacement and during every
recovery phase. No undocumented design deviation remains.

### Code integrity

No issues found. The loader contract is now readable through explicit item validators instead of
an implicit section-mode function. Production catches are limited to the documented reconstructor
exception types and preserve chained causes. The evidence transaction catches broadly only to
restore both files, then re-raises; it does not convert failures into success. No placeholder,
silent fallback, compatibility shim, or Item 4-specific type diagnostic was found.

---

## Certification

- Fresh licensed relocation file: **3/3 passed**, including live A/live B/replay A and unchanged
  moved replay.
- Focused Item 4 plus kept transaction tests: **407/407 passed** normally and **407/407 passed**
  under optimized Python.
- Licensed repository-wide suite, independently run during this turn: **2,950 passed, 26 skipped,
  10 deselected**.
- Broader snapshot/parity/fingerprint/contract family: **446 passed, 26 skipped, 1,393 deselected**.
- Frozen historical overlay: **15/15 passed**; SHA-256 remains `2157899a…0506`.
- Earlier moved replay: **1/1 passed twice** in separate processes. The fresh licensed run closes
  the previously skipped live A/live B/replay A node.
- Item 2 overlap: **162/162 passed** normally and optimized. Item 6 overlap: **122 passed, 2
  skipped** normally and optimized.
- Loader matrix: **336 collected and passed** in both focused modes. Transaction suite: **11/11
  passed** in both focused modes.
- Ruff check, Ruff format on all mutable Item 4 paths, and `git diff --check` pass. Targeted mypy
  reports the existing **73 errors in 15 imported files** and no diagnostic in the five Item 4
  production files.
- Fixture/baseline manifests, exact 65+1 diff, 30-snapshot inventory, absent transaction directory,
  and zero Item 3 diff all reproduce.
- Tracking is updated to **Certified**. The combined relocation criterion, Phase 5 completion,
  epic Item 4 success criterion, and backlog Item 4 checkbox are closed.

**Not checked:** Exact live TEAx evidence tuples from Item 2's separate execution scope; historical
Item 6 incoming-patch equality, which
has no retained canonical baseline artifact and remains unclaimed; and a new historical RED replay
of the frozen overlay. The overlay's preserved prior evidence remains 12 independently RED desired
nodes plus three GREEN controls at `512786c`, followed by 15/15 GREEN on the candidate. This pass
did not rerun the broader 446-test family, Item 2/6 overlap selections, mypy, or the fixture updater;
their prior certified evidence is preserved and no new claim is derived from them.
