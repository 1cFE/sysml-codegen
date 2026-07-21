# Item 4 Implementation Evidence

## Environment and incoming state

- Reviewed baseline: `512786c7dfab44fba7a0185d09e845b7494c702d`.
- Python: `3.12.3`; pytest: `9.0.2`.
- Codegen import: `/home/reid/1cfe/sysml-codegen/src/sysml_codegen/__init__.py`.
- Companion import: `/home/reid/1cfe/agentic-mbse/src/agentic_mbse/__init__.py`.
- Frozen overlay: `evidence/test_constraint_wave_snapshot_portability_overlay.py`.
- Frozen overlay SHA-256: `2157899a62850027a49c3109154dbca167f6df49f7d0463b7b69d26b52320506`.
- Incoming fixture manifest SHA-256: `01de9728bd7e86ec18ecd3a0c38917b14e4b20362deec5a567a7a4563b6c3284`.
- Incoming committed-baseline manifest SHA-256: `921bbb6a84f95669c8d1a5487b501ee885ce40cc23b67f9d8f1a01150f99bf66`.
- Item 6's incoming dirty paths were recorded contemporaneously, but Item 4 retained no canonical
  baseline patch artifact. Its historical digest is therefore not an independently reproducible
  preservation claim; current preservation evidence is the focused overlap suite and scoped diff.
- The incoming worktree also contains certified Item 2 name-safety and Item 6 seal/verify changes.
  They are inherited state, not Item 4 output. Item 4 may share only
  `tests/conformance/test_fingerprint_stability.py`, and any edit there must be additive.

## Phase 1 — frozen historical evidence

The reviewed source was materialized with `git archive` at exact commit `512786c` under a fresh
`/tmp/constraint-wave-snapshot-red.*` directory. The overlay collected 15 independently selectable
nodes. Each node ran in a fresh process with the archived `src` first on `PYTHONPATH`, user-site and
bytecode disabled, and `EXPECTED_CODEGEN_REPO` pointing at the archive.

- Desired R-6/R-11 nodes: **12 independently RED**.
- Compatibility controls: **3 independently GREEN**.
- R-6 failures were defect-specific: named capture retained an absolute path; named warning and
  exclusion bytes retained the checkout root; anonymous NON_NUMERICAL mapping ran twice; and the
  named record projection differed across equivalent roots while its exact ID stayed stable.
- R-11 failures were defect-specific: non-mapping root raised raw `AttributeError`; malformed facts
  and occurrence containers/items raised raw `AttributeError`, `TypeError`, or `KeyError`, lacked
  JSON Pointer context, or silently passed; list-valued lowering mode raised raw `TypeError`.
- Controls proved anonymous route parity, valid empty/degradable legacy behavior, ordinary/v1
  unknown extras, and recursive rejection of `expression-ir/v2` below an unknown key.
- Collection/import/setup failures did not occur. The historical overlay was frozen before
  candidate validation and is not edited after this record.

## Phase 2 — candidate evidence

- One lowering-local cache projects each requested selected index once. Warnings, excluded records,
  and anonymous ID minting consume the cached immutable referent/rendered pair.
- Named exclusions now take the same explicit live-map or replay-validate route as anonymous
  exclusions. Named no-location records retain `<no location>`.
- Capture retains deep-copy semantics and applies the production selector to every located excluded
  usage. Named and anonymous eligible usage objects remain raw and byte-identical.
- Exact named mint tuples and IDs remain unchanged; anonymous excluded IDs retain their existing
  canonical referent/line/column tuple and 32-hex suffix; named and anonymous eligible IDs remain
  unchanged, with anonymous eligible retaining its 16-hex suffix.
- The unchanged 15-node overlay was re-run one node per fresh process against candidate source:
  **15/15 GREEN**. Its SHA-256 remained
  `2157899a62850027a49c3109154dbca167f6df49f7d0463b7b69d26b52320506`.
- Phase 2 focused normal and optimized selection: **38 passed, 3 licensed skips** in both modes.
- Diff inspection found no Item 4 hunk in the eligible branch, occurrence expansion, demand
  collection, or Item 3 files. Other hunks in `constraint_lowering.py` are inherited certified
  Item 2 changes and were preserved.

## Phase 3 — candidate evidence

- Loader validation is limited to the JSON root, `/constraint_facts`, `/part_occurrences`, and
  `/constraint_lowering_mode`. Legacy reconstruction remains outside the new validators and catches.
- The preflight implements required, required-nullable, optional-with-default, valid-empty, nested
  list/item, boolean-versus-integer, and all six ExpressionIR-kind rules with RFC 6901 pointers.
- The existing recursive version scan still runs across known and unknown keys before kind-directed
  validation. Unknown `expression-ir/v1` extras remain accepted; `expression-ir/v2` remains rejected.
- Residual facts and occurrence reconstruction faults are separately chained into contextual
  `SnapshotFormatError` values. JSON syntax and non-mapping roots use the same domain grammar.
- The expanded shape file collected 53 cases at the first phase gate and 55 after adding two
  residual-reconstructor cases. Phase 3 focused normal and optimized selection: **84 passed,
  3 licensed skips** in both modes before the final two cases; the final matrix alone passed 55/55.
- Protected Item 3 files have no diff.

## Phase 4 — fixture transaction evidence

- The updater uses production `excluded_usage_indices` plus `map_live_source_referent`; it discovered
  exactly indices `0..64` in `catf_mfe_model` and index `0` in
  `constraint_non_numerical`. All are named, located, selected exclusions.
- Candidate preparation proved byte-exact parse/re-render identity, unchanged `captured_at`, exact
  reverse substitution to each original byte string, unchanged unselected/eligible usage objects,
  canonical new referents, and a prospective manifest limited to the two approved paths.
- Original → candidate SHA-256:
  - `catf_mfe_model`: `32e85e60db8c220a0b3e66ca5113027b99d1cedceaa97a6c5524e6a9930016d9`
    → `9ae5cfc48a82a18ef10500909bc6bf4010f811d891cf0c201e02192079e344d6`.
  - `constraint_non_numerical`:
    `be469788d0c8a525130c2438a46d5f0310769665fae075ee47d614cebbd1ca78` →
    `605f549e8995c2ff1e843065f1d357f3ffa2f9bd0e702817e55436b4c96c4c02`.
- The journaled transaction reached `prepared`, `first_replaced`, `second_replaced`, and `verified`,
  then removed its transaction directory. Five transaction tests passed: no-write preparation,
  validation failure, injected second-replace rollback, interrupted-first recovery, and successful
  idempotent rerun.
- The reviewed diff is exactly **65 removed/65 added** lines in `catf_mfe_model` and **1 removed/1
  added** line in `constraint_non_numerical`; every line is an allowlisted `location.file` value.
  Timestamps stayed `2026-07-13T08:24:20.395382+00:00` and
  `2026-07-18T17:48:36.211417+00:00`.
- Post-write fixture manifest SHA-256: `92b9f2da5e5ca15a0fdc710eef9b913925a75fa4edb3d87a1a5fd99f97e73099`.
  The committed-baseline manifest remains exactly
  `921bbb6a84f95669c8d1a5487b501ee885ce40cc23b67f9d8f1a01150f99bf66`.
- All 30 committed extraction snapshots loaded. The selector inventory found exactly 65 + 1
  affected named located exclusions in the two approved snapshots and none elsewhere.

## Phase 5 — final gates

Summary: **snapshot fallback passed; licensed live relocation skipped/unproven**.

### Exact relocation manifest

- `test_snapshot_only_moved_replay_manifest` uses the affected
  `catf_mfe_model/extraction_snapshot.json`, after a direct snapshot-generation probe returned
  `True` under certified Item 2. The in-memory graph adds one anonymous non-numerical assertion and
  one literal-only admitted named control. No reserved formal is introduced.
- Both replay roots receive byte-identical CATF source and snapshot inputs. Before replay, the test
  verifies the snapshot copy SHA-256 values. The manifest compares 12 exact projections: canonical
  excluded-fact bytes, warning strings, excluded-record bytes, catalog fingerprint, full
  model-contract bytes, model-contract excluded-record bytes, model-contract catalog fingerprint,
  semantic fingerprint, full generated report bytes, and the model-contract and report artifact
  hashes from the package contract.
- The manifest contains 65 CATF named exclusions plus the synthetic anonymous exclusion and one
  admitted control. It pins framed manifest SHA-256
  `9efcceac33d8f2638c68ebcc274067609363df9c1875dd1458cf4141159312d8` and scans every compared byte
  for both temporary checkout roots.
- The dedicated replay node passed once with `-rs`, then passed twice in separate processes in
  0.42s and 0.41s. The licensed `test_live_capture_replay_relocation_manifest` was attempted with
  `-rs` and skipped: `no live syside license`. Only that node has the shared `requires_license`
  marker. The live leg is unproven, not passed.
- The dedicated manifest already compares the named-exclusion catalog and semantic fingerprint
  consequences, so Item 4 left `test_fingerprint_stability.py` unchanged.

### Surfaced Item 2 premise conflict

- `constraint_non_numerical` remains valid loader and affected-location fixture evidence: its
  selected index 0 now stores `root-0/model.sysml`, loads through the v3 gate, and has no selected
  root leak. Its unselected admitted sibling deliberately retains the raw historical location under
  the eligible-byte firewall.
- It is unsuitable for whole-package relocation generation. A direct snapshot probe returned
  `False`, preserved an absent output tree, and emitted:
  `constraint_id='constraint_non_numerical__the_host__positive_value__9219eba6b0563fb2'`,
  `scope='predicate'`, `kind='generated_binding_overlap'`, `final_binding='value'`, colliding with
  generated binding `value` for
  `constraint_non_numerical::MixedPurposeHost::value`. This is certified Item 2 behavior. Item 4
  did not weaken, bypass, or rewrite it.
- The first underlying repository-wide suite error is not Item 2. It is the SysIDE import failure
  in `test_bug2_regression.py` while loading `solar_battery_model`: no license key was available.
  Representative cascades then report failed live codegen/setup for `attr_expr_probe`,
  `solar_battery_model`, `chain_spike_model`, `sample_model`, the costed-component fixture, and the
  hierarchy fixture. Item 2's collision is independently reproducible from the committed
  `constraint_non_numerical` snapshot but is masked in live families because model loading fails
  first. Expanding Item 4 into those licensed or historical name-collision fixtures would violate
  scope.

### Test gates

- Focused Item 4 normal: **98 passed, 14 licensed skips**. Focused optimized: **98 passed, 14
  licensed skips**, plus pytest's expected warning that test-module assertions are disabled under
  `-O`.
- Historical frozen overlay on candidate source: **15/15 GREEN**, one node per fresh process. The
  hash remains `2157899a62850027a49c3109154dbca167f6df49f7d0463b7b69d26b52320506`.
- Snapshot/parity/fingerprint/contract family: **162 passed, 26 skipped, 1,393 deselected**.
- The stale full-suite warning test now passes independently with the canonical
  `root-0/design.sysml:line:column` warning referent.
- Default repository suite after that correction: **2,367 passed, 206 skipped, 10 deselected, 23
  failed, 96 errors** in 14.41s. The gate is not green. The saved log is
  `/tmp/item4-full-suite-final.log`; the first underlying and representative cascades are classified
  above.
- Item 2 focused overlap: **162 passed** normally and **162 passed** optimized. Item 6 overlap:
  **122 passed, 2 licensed skips** normally and optimized.

### Static, fixture, and isolation gates

- Ruff check passed on every mutable Item 4 production/test/evidence Python path. Ruff format check
  passed 13 mutable paths and reported only the deliberately frozen historical overlay. Formatting
  it would invalidate the Phase 1 evidence hash, so it was not modified.
- Targeted mypy reports **73 errors in 15 imported baseline files** and zero errors in the five
  requested Item 4 production files.
- `git diff --check` passed. Item 6 preservation is supported by its normal/optimized overlap tests
  and the absence of Item 4-attributable changes in its protected files. No historical patch-digest
  equality is claimed.
- Fixture manifest is exactly
  `92b9f2da5e5ca15a0fdc710eef9b913925a75fa4edb3d87a1a5fd99f97e73099`; committed baselines remain
  exactly `921bbb6a84f95669c8d1a5487b501ee885ce40cc23b67f9d8f1a01150f99bf66`. Only the two approved
  extraction snapshots differ: CATF 65/65 lines and non-numerical 1/1 line.
- Selector-aware scans found zero absolute-root leaks in 65 CATF selected records and one
  non-numerical selected record. The latter fixture's eligible record retains its intentionally raw
  location, so a whole-file grep would be a false portability failure.
- Item 3 files `part_instance_index.py` and `supplied_values.py` have no diff. Item 4 added no hunk
  to companion code, contracts, generators, templates, version values, or legacy schemas. The
  visible changes in those protected areas are inherited certified Item 2/6 work and are covered by
  the exact protected hash and overlap gates.
- Final branch status remains dirty on `constraint-exec-epic`; the reviewed worktree stat is 38
  tracked files with 2,465 insertions and 423 deletions across inherited Item 2/6 plus Item 4. No
  commit, push, PR, remote comment, merge, stash, reset, checkout, or clean occurred.

## Audit remediation — 2026-07-18

- The relocation harness now has distinct route collectors. Live A and live B call
  `build_pipeline_context([models_root])` and `run_codegen(models_path=...)`; replay A calls
  `build_pipeline_context_from_snapshot` and `run_codegen(from_snapshot=...)`. Manifest assembly is
  shared only after those route-specific context and generation operations finish. A license-free
  structural test pins the exact call order and mutually exclusive `models_path`/`from_snapshot`
  configuration. The real licensed node implements live A/live B/replay A followed by moved replay,
  but still skips explicitly with `no live syside license`; SC-2 remains unverified.
- The loader's former 223-line section switch is split into explicit definition, formal, usage,
  source, owner, actual, context, redefinition, and diagnostic validators. The narrow boundary,
  recursive unknown-extra version scan, and separate reconstructor catches are unchanged.
- `test_snapshot_v3_gate.py` now collects **336 cases**. Independent explicit tables cover missing
  keys and wrong non-null types for every identity, location, source, owner, owning-definition,
  formal, actual, context, redefinition, diagnostic, string-list, occurrence, lowering-mode,
  operand-type/unit, and all six ExpressionIR-kind rows. Valid controls cover every nullable field,
  optional operand-type absence, empty lists/maps, all JSON literal value classes, ordinary/v1
  extras, v2 recursive rejection, JSON Pointer escaping, residual chained causes, and absent
  `compilation_results` degradation.
- The transaction tests now reconstruct legacy absolute locations in complete temporary fixture
  copies, so they remain meaningful after the committed fixtures are canonical. The helper stages
  the complete original/candidate fixture manifests and complete `baseline_outputs` manifest in
  the journal, verifies them before writes, after writes, and after rollback/recovery, and validates
  staged candidate hashes before the first replacement. Eleven kept tests cover no-write prepare,
  validation failure, candidate mismatch, first- and second-replace failures, post-write manifest
  failure, interrupted recovery at `prepared`, `first_replaced`, `second_replaced`, and `verified`,
  successful cleanup, and canonical idempotence.
- The route-count suite now proves a BLOCK usage receives zero live mapper and zero replay validator
  calls while both earlier NON_NUMERICAL siblings project exactly once. The committed
  non-numerical fixture pins the complete warning string and canonical excluded-record JSON bytes;
  the replay proof is license-free and the live assertions remain in the licensed tests.

### Remediation validation

- Item 4 plus kept transaction evidence, normal: **393 passed, 14 licensed skips**. Optimized:
  **393 passed, 14 licensed skips**, plus pytest's expected `-O` assertion warning.
- Frozen overlay: **15/15 passed**, one node per fresh process; SHA-256 remains
  `2157899a62850027a49c3109154dbca167f6df49f7d0463b7b69d26b52320506`.
- Dedicated relocation: **2 passed, 1 licensed skip**. Snapshot replay passed twice in separate
  processes (0.41s, 0.42s) with pinned manifest digest
  `9efcceac33d8f2638c68ebcc274067609363df9c1875dd1458cf4141159312d8`.
- Broader snapshot/parity/fingerprint/contract family: **446 passed, 26 skipped, 1,393
  deselected**.
- Item 2 overlap: **162 passed** normally and optimized. Item 6 overlap: **122 passed, 2 licensed
  skips** normally and optimized.
- Default suite: **2,651 passed, 206 skipped, 10 deselected, 23 failed, 96 errors** in 14.91s. The
  first underlying error remains the missing SysIDE license while loading `solar_battery_model`;
  the failure/error families are the inherited live-fixture cascade, not an Item 4 regression.
- Ruff check passed every mutable Item 4 path. Ruff format check passed 13 mutable paths and reports
  only the deliberately frozen historical overlay. Targeted mypy remains at **73 imported-surface
  errors in 15 files**, with zero diagnostics in the five Item 4 production files.
- Canonical updater `--check` is idempotent at exact hashes `9ae5cfc4…44d6` and
  `605f549e…c02`, with 65+1 selector records. Fixture manifest remains
  `92b9f2da…3099`; `baseline_outputs` remains `921bbb6a…bf66`; diff numstat remains exactly 65/65
  plus 1/1. All 30 snapshots load, and no transaction directory remains.
- `git diff --check` passed. Item 3 files remain untouched. No commit, push, PR interaction, merge,
  stash, reset, checkout, clean, or remote mutation occurred.

### Implementation-stage bookkeeping closeout

- At the 2026-07-18 implementation closeout, every material audit code/evidence finding was
  remediated and the implementation awaited independent re-audit.
- At that closeout, the combined relocation criterion remained open: license-free moved replay was
  proven while licensed live A/live B/replay A was unverified. The licensed re-audit below closes
  that criterion.
- A representative post-bookkeeping gate covered moved replay, distinct live/replay route wiring,
  BLOCK zero calls, exact warning/excluded-record bytes, staged-candidate mismatch, post-write
  manifest rollback, and all four journal recovery phases: **10 passed** normally and **10 passed**
  under optimized Python. Optimized mode emitted only pytest's expected assertion warning.
- Final `git diff --check` passed. No commit, push, PR interaction, or remote mutation occurred.

## Licensed re-audit — 2026-07-19

- The earlier skip was caused by plain `uv run` not loading the repo-local `.env`. The re-audit used
  `UV_CACHE_DIR` under `/tmp` with `uv run --env-file .env`; the key was never printed.
- The complete relocation file passed **3/3**, including capture at equivalent roots A and B, live
  A, live B, replay A, and unchanged moved replay. This closes the exact relocation manifest.
- The Item 4 focused selection plus all 11 fixture-transaction tests passed **407/407** normally and
  **407/407** under optimized Python. The re-auditor independently reproduced both focused runs.
- The licensed repository suite independently run during the same turn passed **2,950 tests**, with
  **26 skipped** and **10 deselected**. The re-audit did not rerun the full suite because the fresh
  independent result and proportionate focused reruns agreed.
- Fresh Ruff check, Ruff format check on all mutable Item 4 paths, and `git diff --check` passed.
- Prior remediation findings remain in force: distinct live/replay collectors, the 336-case loader
  matrix, full-manifest fixture transaction and recovery, BLOCK zero-call behavior, and exact
  warning/excluded-record bytes. Item 2's collision boundary and Item 6's lack of a historical
  incoming-patch artifact remain unchanged and are not broadened into Item 4 claims.
