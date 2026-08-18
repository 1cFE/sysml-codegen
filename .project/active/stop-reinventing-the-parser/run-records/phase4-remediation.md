# Phase 4 audit remediation — 2026-08-18

**Source finding:** [phase4-audit.md](phase4-audit.md), verdict **Needs Work — bounded**.

**Scope:** Phase 4 verification and evidence records only. No shipped source changed. Phase 5 did not
start, Agentic remained read-only at `3f8bd58`, and the retired Agentic PDF/HTML suite was not run.

## Result

The two blocking audit findings are implemented on `stop-parser-impl-r2` at
`571ed39b8059860206be57e3509cecc85bfbfac5`. This is an implementation response, not a replacement
audit verdict. An independent re-audit remains the next gate.

| Commit | Purpose |
|---|---|
| `9da3d842bd4f3b2b204c8df1ebc7ca59d4b0a9ba` | Add the current-fixture mutation proof, per-cell consumer-route accounting, the deep-override parser probe, snapshot refusal arm, and graph-driven registry render tests. |
| `f95166370afb3cddbc3d65fe18ed197ef3064bb6` | Restore current fixture-byte validation, own the intentional comment transition, and correct stale registry documentation. |
| `571ed39b8059860206be57e3509cecc85bfbfac5` | Record the verification-code hash transition and state the repaired coverage honestly. |

The original auditor artifacts were preserved separately on the project branch at
`fef32842cb32c53825d1cc83dc0c873a2f1ab534` before this response changed any project record.

## Finding responses

### `audit-phase4-F1` — current fixture bytes

`verification/capture_baseline.py::validate_manifest` now runs an independent current-source guard
after reconstructing the immutable manifest from P_seed. The two accounts have distinct jobs:

- historical reconstruction reads P_seed and proves the frozen manifest;
- current validation reads all 110 SysML/KerML files in all 43 current roots and compares them with
  their frozen hashes.

Every difference requires exactly one transition-ledger row naming the path, frozen hash, and current
hash. The six `ADDED_ROOTS` are counted explicitly: six roots, seven source files. The only current
difference is the comment-only edit to
`tests/fixtures/deep_cross_scope_probe/design.sysml`; its row carries hashes `02e39c…` → `45c944…`
and owner `1ce8638ff62aae4f991890e652fd7ad28a683c28`.

The kept mutation test changes a fixture after an initially green check and requires
`unowned current fixture source transition`. Rebuilding from P_seed cannot satisfy it. The
verification-code row was corrected to say that `8919232` preserved historical reconstruction but
dropped current-byte coverage, and that `f951663` restored it separately. The row pins
`capture_baseline.py` at current SHA-256
`442dbf96484149a74576eab372cd3e8caa627e951417706b9a8844330828e6bc`.

### Universality claim and `audit-phase4-F2`

The Phase 4 validation bullet now limits the six-part assertion claim to the parameterized public
matrix and records the actual narrower assertion set of each targeted/backstop row. No weaker test is
presented as a full matrix row.

The consumer-closure table now records public arms per cell. The two deep-literal-override exception
cells have empty public-arm sets, a required reason, and a named kept proof:

- indexed override: a licensed real-parser probe authors
  `:>> deep_rig.cells#(2).mass = 7.0;` and proves SysIDE rejects it at parse with
  `Unexpected 'DECIMAL_VALUE'`;
- operand/depth failure: the retained real-model structural probe proves parsed deep-override paths
  contain only `Feature` segments and never enter expression acquisition.

The table no longer accepts the prose placeholder `"not an expression route"` as proof. Its tests
require every cell to name a real test, require the per-cell arm keys to be complete, and require one
reason for every cell with no public arm.

## Non-blocking audit notes handled

- `generate --from-snapshot` now reaches the same unsupported-exit-type refusal test as `--models`;
  both preserve a pre-seeded output tree byte-for-byte.
- The old direct-template registry tests now call `generate_registry(graph, ...)`; changing graph
  root-output types changes the asserted wrapper imports.
- `docs/architecture/reference/08-generation.md` now describes the emitted `create_registry`
  function rather than the nonexistent `MODULE_REGISTRY` dictionary.
- `[INHERITED: product-lens.md#audit-phase3-F2]` is now an explicit unchecked Phase 5 obligation,
  required before that phase names `C_prod`.

## Tests-first signal

The first targeted run at tests-first commit `9da3d84` stopped during collection because importing
the verifier eagerly loaded SysIDE without a license. That exposed an unrelated coupling in the
verification module. `f951663` defers the SysIDE import to capture and resolves the declared Git
history only in checks that consume history. The current-byte guard can therefore run without a
license or artifact-history manifest. Its kept mutation test supplies the deterministic red signal:
an unowned byte edit raises before any historical reconstruction can hide it.

## Fresh-extraction validation

Validation ran from
`/tmp/stop-parser-rev2/phase4-fix-extraction.jyhBwP/extracted/codegen/sysml-codegen`, extracted from
the exact `571ed39` archive. All **2,582 tracked paths** are byte-identical to the implementation
commit, including an exact comparison of the tracked symlink entry.

| Artifact | SHA-256 |
|---|---|
| Codegen source archive | `c5e96f00b53650df9bd112dff7ec7e38e08e295923a4dd4314fbb0e0a9516fa1` |
| Agentic source archive | `c2924387d6d91360b951d5c9e17386b192148e2d719628feaec38fd41347afb2` |
| Codegen history bundle | `ae0e4678444c863f369af9b53679cd21fadc9a04b31a142ebc79e722b531083c` |

Results:

- complete default suite: **2,496 passed, 34 skipped, 94 deselected** in one run; the four added
  selected nodes are the two fixture-lock tests, parser probe, and second CLI source arm;
- focused Phase 4 natural-route/registry selection: **206 passed**, zero skips;
- historical/current lock, documentation contract, and snapshot inventory: **32 passed**;
- reconciliation: 14 captured / 23 refused; batch hashes unchanged; 23 metadata-only and 22
  maintained snapshots; exactly the two existing record transitions and two golden rows;
- D1–D4 and retained harness: the 162 non-wheel nodes passed in the scoped run; its one offline-wheel
  node was blocked only by sandbox access to the existing uv cache, then passed independently. The
  complete suite rerun with that cache available includes all 163 green;
- public TEAx occurrence mutation lane with a temporary pandas target: **6 passed**;
- scoped strict mypy: **success, 2 files**; repository mypy: unchanged **30 errors in 8 files** across
  76 source files;
- Ruff on every changed Python file: clean; `git diff --check`: clean;
- `src/sysml_codegen/elaboration/occurrence.py` remains byte-identical to `C_base` `78a9beb9`.

Setup-only failures before the final run were an incorrectly nested Agentic extraction root and the
sandboxed uv-cache access above. Both were corrected without a source change. Agentic was not
re-audited because no Agentic byte changed. Phase 5 and item-level certification remain unrun.
