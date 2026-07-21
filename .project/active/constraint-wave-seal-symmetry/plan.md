# Implementation Plan: Seal and Verify Symlink Symmetry

**Status:** Complete
**Created:** 2026-07-18
**Last Updated:** 2026-07-18
**Branch:** `constraint-exec-epic`
**Reviewed Baseline:** `512786c7dfab44fba7a0185d09e845b7494c702d`

## Source Documents

- **Spec:** [spec.md](spec.md)
- **Revised design:** [design.md](design.md)
- **Historical review:** [design-review.md](design-review.md)
- **R-10 reproduction:**
  [constraint-exec PR-wave code review](../../research/20260718-192048_constraint-exec-pr-wave-code-review.md#r-10--sealverify-symlink-gaps-seal-produces-unverifiable-packages-dangling-symlinks-pass-verify-pr-9--reproduced)
- **F9 control/evidence:**
  [GAP-CLOSE boundary-guards plan](../gap-boundary-guards/plan.md#phase-3-reject-directory-symlinks-in-canonical-and-emitted-verifiers)
  and [evidence](../gap-boundary-guards/evidence.md)
- **Package contract:**
  [contracts and sealing](../../../docs/architecture/reference/29-contracts-and-sealing.md)

## Implementation Strategy

### Phasing Rationale

Phase 1 freezes defect-specific RED evidence before production edits. It runs each root, file,
directory, target-class, excluded-path, contract-path, and verifier-route assertion independently
against the exact reviewed commit. Already-green F9 directory-verifier cases remain controls and
are not reported as new RED.

Phase 2 implements the smallest shared behavior at the two canonical boundaries: a duplicated,
AST-pinned, root-first non-following inspector; the seal-side policy error; and verifier preflight
before seal loading. Phase 3 places the same seal-side guard before generation and re-seal route
I/O, then proves no partial contract and unchanged-tree behavior. Phase 4 updates the intentional
verifier hash and executable-fingerprint consequences without weakening byte identity or regular
tree stability. Phase 5 reruns the unchanged historical overlay and package gates, then records
source-isolated evidence, fixture preservation, and dirty-tree scope.

### Critical Path

Independent RED/controls -> canonical inspector and public failure contract -> verifier/seal GREEN
-> CLI guard placement and no-write guarantees -> emitted verifier/fingerprint consequences ->
isolated GREEN and repository gates.

### First Proof Point

On the frozen `512786c` tree, the direct-seal file-link and dangling-link nodes must fail for their
specific R-10 reasons while the historical F9 internal/escaping directory-verifier nodes pass as
controls. This separates newly exposed defects from behavior already fixed before Item 6.

### Feasibility and Main Risks

The revised design fits the current code. `seal_package` owns enumeration and hashing;
`verify_package` can inspect before `_load_seal`; Step 9 and `cmd_seal` have clear pre-I/O seams.
No schema or public verifier signature needs to change. See
[design.md#potential-risks](design.md#potential-risks).

- The highest risk is proving “no follow” rather than merely receiving the right diagnostic.
  Phase 1 patches target-following operations to fail, and Phases 2–3 retain those assertions.
- The second risk is treating the required verifier-byte change as a general fingerprint
  regression. Phase 4 compares the complete hash map and permits only `contracts/verify.py` to
  differ across reviewed and candidate generation.
- Tree mutation between inspection and use remains outside scope under the recorded quiescent-tree
  bet. Do not add locking, filesystem snapshots, or platform-specific traversal.

### Overall Validation Approach

- Every implementation phase starts with kept tests or an unchanged Phase 1 overlay.
- Normal and optimized focused tests exercise explicit error paths without relying on `assert` in
  production.
- Canonical/emitted source equality, inspector/glob AST parity, and stdlib-only imports remain hard
  package gates.
- A source-isolated baseline/candidate comparison and complete fixture manifest protect the shared
  dirty worktree.

---

## Phase 1: Freeze Independent RED Regressions and Controls

### Goal

Capture the reviewed behavior before any production edit. Each defect must be independently
selectable and must fail because of the named R-10 or route-order gap, not setup, import, or a
different assertion. Preserve the historical F9 cases as green overlays.

### Assumption Under Test

The reviewed tree follows or skips links differently by route: direct seal hashes file-link
targets and ignores directory/dangling links; verification reads contract paths before its partial
directory-link check and skips dangling/excluded links; generation and re-seal touch link-bearing
paths before a guard. See [design.md#redgreen-validation-matrix](design.md#redgreen-validation-matrix).

### Test Stencil (Write This First)

```python
def test_direct_seal_rejects_dangling_file_link_without_partial_contract(tmp_path):
    package, link = package_with_link(tmp_path, entry_kind="file", target="dangling")
    before = tree_bytes(package)
    with pytest.raises(PackageSealError) as caught:
        seal_package(package, "pkg")
    assert_error(caught.value, kind="INVALID_PATH", path=link.name)
    assert tree_bytes(package) == before
    assert not (package / "contracts/package_contract.json").exists()
```

### Changes Required

See [design.md#deterministic-failure-precedence](design.md#deterministic-failure-precedence),
[design.md#required-invariants](design.md#required-invariants), and
[design.md#required-route-tests](design.md#required-route-tests).

- [x] Create
  `.project/active/constraint-wave-seal-symmetry/evidence/test_constraint_wave_seal_symmetry_overlay.py`.
  Keep helpers self-contained so the overlay imports production only from the pinned source tree.
- [x] Add separately addressable direct-seal nodes for: symlink package root (`"."`); real
  file/directory controls; file and directory links to internal, escaping, and dangling targets;
  a link under an excluded/runtime-output path; `contracts/`; `contracts/model_contract.json`;
  `contracts/package_contract.json`; and lexical-first multiple links.
- [x] Add separately addressable canonical-verifier nodes for the same root/descendant/target
  matrix, including dangling and excluded links, link-plus-missing/malformed seal precedence, and a
  recorded regular file replaced by a link. Assert one exact `INVALID_PATH`, the canonical POSIX
  path/message, and absence of `MISSING`, `EXTRA`, `TAMPER`, or containment duplicates.
- [x] Add no-follow probes that make `resolve`, `is_file`, `is_dir`, `read_text`, `read_bytes`, and
  descendant target access raise if invoked. Add a walk-`OSError` node that pins verifier
  `ARTIFACT_UNREADABLE` and direct-seal propagation before any partial contract exists.
- [x] Add Step 9, initial-generation-output, re-seal, and emitted-verifier overlay nodes. Snapshot
  the pre-existing package-contract bytes and the external target tree; assert both remain
  byte-identical after failure. For an absent seal, assert no seal file appears.
- [x] Add historical R-10 nodes that reproduce: escaping file links being hashed by seal,
  directory links being skipped by seal, and dangling links passing verification. Retain the two
  F9 internal/escaping directory-verifier nodes as expected-green controls.
- [x] Use these exact independently runnable overlay test names; do not collapse them into one
  aggregate test whose first failure masks later routes:

  ```text
  test_regular_file_and_directory_controls
  test_r10_seal_hashes_escaping_file_link_reviewed
  test_r10_seal_skips_directory_link_reviewed
  test_r10_verify_accepts_dangling_link_reviewed
  test_f9_verify_rejects_internal_directory_link_control
  test_f9_verify_rejects_escaping_directory_link_control
  test_direct_seal_rejects_root_link_without_following
  test_direct_seal_rejects_internal_file_link_without_following
  test_direct_seal_rejects_escaping_file_link_without_following
  test_direct_seal_rejects_dangling_file_link_without_following
  test_direct_seal_rejects_internal_directory_link_without_following
  test_direct_seal_rejects_escaping_directory_link_without_following
  test_direct_seal_rejects_dangling_directory_link_without_following
  test_direct_seal_rejects_excluded_link_before_coverage
  test_verify_rejects_root_link_before_seal_load
  test_verify_rejects_contracts_link_before_seal_load
  test_verify_rejects_linked_seal_file_before_seal_load
  test_verify_rejects_internal_file_link_without_following
  test_verify_rejects_escaping_file_link_without_following
  test_verify_rejects_dangling_file_link_without_following
  test_verify_rejects_dangling_directory_link_without_following
  test_verify_rejects_excluded_link_before_coverage
  test_verify_reports_only_lexical_first_link
  test_verify_link_precedes_missing_extra_and_tamper
  test_preflight_walk_error_precedes_descendant_claim
  test_generation_rejects_existing_root_link_before_output_mutation
  test_step9_link_failure_writes_no_partial_contract
  test_reseal_rejects_contracts_link_before_model_contract_check
  test_emitted_verifier_matches_canonical_link_policy
  ```

- [x] Add kept counterparts first in `tests/unit/test_contract_models.py`,
  `tests/unit/test_verify_package.py`, and `tests/conformance/test_seal_step9.py`. Keep parameter
  IDs stable so every matrix cell can be run independently in baseline and candidate processes.
- [x] Create `.project/active/constraint-wave-seal-symmetry/evidence.md`. Record exact revision,
  Python/pytest versions, resolved imported source paths, overlay SHA-256, fixture-manifest hash,
  inherited dirty-path manifest, command, exit code, and the defect-specific assertion for each
  node.

### Validation

**Pinned source-isolated RED and controls:**

- [x] Materialize `512786c7dfab44fba7a0185d09e845b7494c702d` with `git archive` beneath a fresh
  `mktemp -d` directory. Do not stash, reset, checkout, clean, or alter the shared worktree.
- [x] Run every overlay node in its own fresh process with the baseline `src` first on
  `PYTHONPATH`, `PYTHONNOUSERSITE=1`, and `PYTHONDONTWRITEBYTECODE=1`. Use this exact command shape:

  ```bash
  PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/tmp/constraint-wave-seal-red/baseline/src \
    uv run pytest -q \
    .project/active/constraint-wave-seal-symmetry/evidence/test_constraint_wave_seal_symmetry_overlay.py::NODE
  ```

  Replace `NODE` with one collected node ID at a time and record it verbatim in `evidence.md`.
- [x] Require each new root/file/dangling/excluded/contracts/route node to be RED for its own final
  assertion. Require regular file/directory and historical F9 directory-verifier controls to be
  GREEN. Treat collection/import/setup failures as invalid evidence.
- [x] Run
  `uv run pytest --collect-only -q .project/active/constraint-wave-seal-symmetry/evidence/test_constraint_wave_seal_symmetry_overlay.py`
  and save the exact node inventory before production edits.

**Baseline preservation:**

- [x] Record `git status --short`, `git diff --name-only`, hashes for every inherited dirty path,
  and `find tests/fixtures -type f -print0 | sort -z | xargs -0 sha256sum | sha256sum`. The current
  fixture-manifest control is
  `01de9728bd7e86ec18ecd3a0c38917b14e4b20362deec5a567a7a4563b6c3284`.

**What We Know Works After This Phase:**

The test matrix distinguishes every new R-10/route-order failure from regular-tree and historical
F9 controls, proves the failures on an exact clean reviewed source tree, and records the shared
worktree state that later phases must preserve.

---

## Phase 2: Implement Canonical Root-First Classification in Seal and Verify

### Goal

Make direct seal and canonical verification classify the package root and all descendants before
any route-specific target-following operation. Reuse the inspected clean entries for hashing and
extra detection.

### Assumption Under Test

For a root first proven not to be a symlink, fully materialized Python 3.12 `Path.rglob("*")`
exposes descendant file, directory, and dangling links without descending through a directory
link. The duplicated inspector can therefore enforce one deterministic policy without adding a
project import to the verifier. See [design.md#key-bets](design.md#key-bets) and
[design.md#architecture-and-route-order](design.md#architecture-and-route-order).

### Test Stencil (Write This First)

```python
@pytest.mark.parametrize("entry_kind", ["file", "directory"])
@pytest.mark.parametrize("target", ["internal", "escaping", "dangling"])
def test_seal_and_verify_share_forbidden_link_result(tmp_path, entry_kind, target):
    package, link = package_with_link(tmp_path, entry_kind, target)
    with pytest.raises(PackageSealError) as caught:
        seal_package(package, "pkg")
    assert public_error(caught.value) == expected_invalid_path(link)
    assert public_diagnostic(verify_package(package, "pkg")) == expected_invalid_path(link)
```

### Changes Required

See [design.md#component-overview-and-file-level-changes](design.md#component-overview-and-file-level-changes),
[design.md#failure-behavior](design.md#failure-behavior), and
[design.md#implementation-notes](design.md#implementation-notes).

- [x] `tests/unit/test_contract_models.py:110`: finish the direct-seal matrix, root token, lexical
  order, regular-file/directory controls, excluded paths, walk failure, no-follow probes, exact
  `PackageSealError` fields/string, deterministic ordering, and unchanged-tree/no-contract
  assertions. Add inspector-body parity beside the existing glob-body parity test at line 161.
- [x] `tests/unit/test_verify_package.py:87`: finish the canonical-verifier matrix, sole-diagnostic
  assertions, exact message, root/malformed-seal and descendant/missing-extra precedence, recorded
  link de-duplication, no-follow probes, clean regular controls, and preflight walk failure.
- [x] `src/sysml_codegen/contracts/seal.py:57`: add `PackageSealError`, the root-aware inspector,
  and the public seal-side guard described in
  [design.md#architecture-and-route-order](design.md#architecture-and-route-order). Inspect before
  hashing. Hash only covered regular files from the returned sorted clean list. Do not change the
  coverage matcher, hash formula, artifact ordering, `PackageContract`, or generator/runtime
  version behavior.
- [x] `src/sysml_codegen/contracts/verify.py:340`: add the AST-identical inspector and run it before
  `_load_seal`. Return immediately with sole `INVALID_PATH` or preflight
  `ARTIFACT_UNREADABLE`. Pass inspected entries into the extra-artifact phase; remove the later
  target-dependent directory-link check at lines 279–299. Sort recorded paths explicitly before
  recorded-artifact checks. Keep public function signatures unchanged and imports stdlib-only.
- [x] `src/sysml_codegen/contracts/__init__.py:19`: export only the new seal error and guard needed
  by CLI routes; do not expose verifier internals or introduce another implementation copy.

### Validation

**Focused test-first loop:**

- [x] Run direct-seal nodes after each seal change:
  `uv run pytest -q tests/unit/test_contract_models.py -k 'symlink or fingerprints_are_deterministic or matcher_bodies or inspector_bodies'`.
- [x] Run canonical verifier nodes after each verifier change:
  `uv run pytest -q tests/unit/test_verify_package.py -k 'symlink or preflight or walk_failure or untampered or missing or extra or tamper'`.
- [x] Run both files normally:
  `uv run pytest -q tests/unit/test_contract_models.py tests/unit/test_verify_package.py`.
- [x] Repeat optimized:
  `PYTHONOPTIMIZE=1 uv run pytest -q tests/unit/test_contract_models.py tests/unit/test_verify_package.py`.
- [x] Run `uv run ruff check src/sysml_codegen/contracts tests/unit/test_contract_models.py tests/unit/test_verify_package.py`
  and `uv run ruff format --check` on those same paths.

**Manual code review:**

- [x] Confirm neither inspector calls `resolve`, `is_file`, `is_dir`, `open`, `read_*`, or coverage
  code; both bodies are AST-identical; the root token is never joined back to the filesystem; and
  the canonical verifier imports no project or third-party module.
- [x] Confirm direct policy and walk failures return/write no `PackageContract`, and every
  regular-tree before/after byte snapshot is identical.

**What We Know Works After This Phase:**

Direct seal and canonical verification classify every tested link at the earliest common boundary,
publish the same path/kind/message, do not touch targets, preserve regular-file sealing bytes, and
retain deterministic recorded-before-extra verifier behavior.

---

## Phase 3: Guard Generation, Step 9, Re-Seal, and the Emitted Verifier

### Goal

Move the seal-side guard ahead of each CLI route’s first output-tree access, recheck at Step 9, and
prove command failures preserve any existing package contract and external target tree. Keep the
emitted verifier byte-identical to canonical source.

### Assumption Under Test

The CLI can reuse one seal-side guard without changing package generation semantics: generation
guards after graph validation but before clear/setup, Step 9 guards before `contracts/` writes,
and re-seal guards before its model-contract `is_file()` check. See
[design.md#key-decisions](design.md#key-decisions), D6.

### Test Stencil (Write This First)

```python
def test_reseal_rejects_linked_contracts_before_model_contract_check(tmp_path, monkeypatch):
    package, outside = generated_package_and_outside_tree(tmp_path)
    replace_contracts_with_link(package, outside)
    before_seal, before_outside = seal_bytes(package), tree_bytes(outside)
    forbid_target_following(monkeypatch, outside)
    assert cmd_seal(seal_args(package)) == 1
    assert seal_bytes(package) == before_seal
    assert tree_bytes(outside) == before_outside
```

### Changes Required

See [design.md#architecture-and-route-order](design.md#architecture-and-route-order),
[design.md#required-route-tests](design.md#required-route-tests), and
[design.md#failure-behavior](design.md#failure-behavior).

- [x] `tests/unit/test_cli_generation.py:166`: add output-root and descendant-link guards around
  `run_codegen`. Patch `_clear_output_directory` and `_setup_output_directories` to fail if reached;
  assert pre-existing output and target trees are unchanged. Keep existing collision-preservation
  tests as controls.
- [x] `tests/conformance/test_seal_step9.py:36`: add Step 9 and re-seal matrices for linked
  `contracts/`, model contract, seal file, verifier path, excluded path, and injected walk failure.
  Assert command outcome/log prefix, exact prior-seal bytes, no new seal on absence, unchanged
  external target, and no partial replacement contract. Run root/file/directory and
  internal/escaping/dangling cases through the emitted verifier. Retain regular generation,
  successful re-seal, self-exclusion, and model-contract byte controls.
- [x] `src/sysml_codegen/cli/__init__.py:929`: call the exported guard after graph/name/coverage
  validation and before `_clear_output_directory` or setup. Normalize `PackageSealError` and
  preflight `OSError` into `False` with `Package sealing failed: <error>`.
- [x] `src/sysml_codegen/cli/__init__.py:610`: recheck before `contracts_dir.mkdir`, model-contract
  write, or verifier copy. Let `seal_package` perform its fresh inspection before hashing; write
  `package_contract.json` last only on complete success.
- [x] `src/sysml_codegen/cli/__init__.py:704`: guard before `model_contract_path.is_file()`, catch
  policy/walk/hash failure, return `1`, and preserve the existing package-contract bytes.
- [x] Keep the copy at `src/sysml_codegen/cli/__init__.py:630` verbatim. Do not add a generated
  helper, contract file, schema field, or verifier dependency.

### Validation

**Route and emitted-verifier tests:**

- [x] `uv run pytest -q tests/unit/test_cli_generation.py -k 'preserves or symlink or preflight'`
- [x] `uv run pytest -q tests/conformance/test_seal_step9.py`
- [x] `PYTHONOPTIMIZE=1 uv run pytest -q tests/unit/test_cli_generation.py tests/conformance/test_seal_step9.py`
- [x] Run the exact emitted-byte node independently:
  `uv run pytest -q tests/conformance/test_seal_step9.py::test_emitted_verifier_is_verbatim`.
- [x] Run the stdlib scan independently:
  `uv run pytest -q tests/unit/test_verify_package.py::test_verifier_imports_nothing_from_sysml_codegen`.

**Mutation review:**

- [x] For initial generation failure, compare the entire pre-existing output tree and outside
  target manifest before/after. For Step 9 failure, allow completed Steps 3–8 ordinary files but
  require no new/replacement package contract. For failed re-seal, require the full package tree
  unchanged, including the previous seal bytes.
- [x] Confirm regular snapshot generation and successful re-seal still verify immediately with
  canonical and emitted verifiers.

**What We Know Works After This Phase:**

Every package-integrity CLI route classifies links before its first target-following output-tree
operation, repeats the check at its final integrity boundary, preserves prior contract/target bytes
on failure, and emits a verifier identical to the corrected canonical source.

---

## Phase 4: Pin Verifier Hash and Fingerprint Consequences

### Goal

Prove that the policy update changes only the emitted verifier artifact and the executable
fingerprint derived from it, while direct seal/re-seal over identical link-free bytes and all
non-verifier generated artifacts remain stable.

### Assumption Under Test

The seal algorithm and package layout are unchanged. Therefore the reviewed-to-candidate generated
hash maps may differ only at `contracts/verify.py`, and replacing that one sorted fingerprint input
must change the executable fingerprint. See
[design.md#fingerprint-consequences](design.md#fingerprint-consequences).

### Test Stencil (Write This First)

```python
def test_policy_update_changes_only_verifier_hash_and_derived_fingerprint(reviewed, candidate):
    old, new = generate_same_snapshot(reviewed), generate_same_snapshot(candidate)
    assert without_verifier(old.artifact_hashes) == without_verifier(new.artifact_hashes)
    assert new.artifact_hashes[VERIFY_PATH] == sha256(candidate.canonical_verify_bytes)
    assert candidate.emitted_verify_bytes == candidate.canonical_verify_bytes
    assert old.artifact_hashes[VERIFY_PATH] != new.artifact_hashes[VERIFY_PATH]
    assert old.executable_fingerprint != new.executable_fingerprint
```

### Changes Required

See [design.md#key-decisions](design.md#key-decisions), D7, and
[design.md#required-invariants](design.md#required-invariants), INV-7/INV-8.

- [x] `tests/unit/test_contract_models.py:110`: pin direct seal and re-seal equality for a tiny
  link-free tree, including artifact key order, per-file hashes, and executable fingerprint.
- [x] `tests/conformance/test_fingerprint_stability.py:33`: retain independent-generation and
  live/snapshot parity tests. Add a source-isolated `512786c` reviewed-to-candidate comparison using
  the same snapshot/package/environment. Compare complete artifact maps after removing only
  `contracts/verify.py`; calculate both verifier digests from source bytes; independently recompute
  each executable fingerprint from sorted `path:hash` lines.
- [x] `tests/conformance/test_seal_step9.py:47`: retain exact canonical/emitted byte equality and
  assert the emitted verifier’s recorded hash equals SHA-256 of those exact bytes.
- [x] Record the candidate canonical verifier SHA-256 and generated executable fingerprint in
  `evidence.md`. Do not hardcode either before the candidate source bytes are final.
- [x] Do not update committed model/snapshot fixtures or broad golden outputs. If any non-verifier
  artifact changes, stop and surface a premise conflict instead of refreshing expectations.

### Validation

**Fingerprint and byte gates:**

- [x] `uv run pytest -q tests/unit/test_contract_models.py::test_fingerprints_are_deterministic`
- [x] `uv run pytest -q tests/conformance/test_seal_step9.py::test_emitted_verifier_is_verbatim tests/conformance/test_seal_step9.py::test_seal_ordering_excludes_itself_from_coverage`
- [x] `uv run pytest -q tests/conformance/test_fingerprint_stability.py -k 'independent_generation or policy_update'`
- [x] `PYTHONOPTIMIZE=1 uv run pytest -q tests/unit/test_contract_models.py tests/conformance/test_fingerprint_stability.py`
- [x] If a SysIDE license is available, run
  `uv run pytest -q tests/conformance/test_fingerprint_stability.py`; otherwise record the live
  nodes as skipped/unclaimed and rely only on the license-free reviewed/candidate and snapshot
  evidence.

**Diff review:**

- [x] Save sorted `path:hash` inputs for reviewed and candidate packages. Require one differing
  line, `contracts/verify.py:<digest>`, and verify both executable fingerprints by an independent
  SHA-256 calculation.

**What We Know Works After This Phase:**

The new policy keeps direct and re-seal byte identity for unchanged link-free input, preserves
every non-verifier generated artifact hash, changes the covered verifier hash exactly once, and
changes the executable fingerprint only as the deterministic consequence of that line.

---

## Phase 5: Unchanged Overlay GREEN, Package Gates, and Evidence Closeout

### Goal

Run the frozen Phase 1 overlay unchanged against an isolated candidate, then validate the full
package surface and prove the patch did not absorb or rewrite unrelated dirty work.

### Assumption Under Test

The exact production/test allowlist closes all Item 6 regressions without changing fixtures,
contract schemas, coverage semantics, package layout, snapshots, archives, or unrelated active
items.

### Test Stencil (Write This First)

```python
def test_candidate_scope_and_fixture_manifest_match_baseline(candidate_diff, fixtures):
    assert candidate_diff.production_paths <= EXPECTED_ITEM6_PRODUCTION_PATHS
    assert fixtures.manifest_sha256 == RECORDED_PHASE1_FIXTURE_SHA256
    assert fixtures.git_diff == b""
    assert inherited_dirty_hashes_unchanged(except_for=EXPECTED_ITEM6_TEST_PATHS)
```

### Changes Required

- [x] Materialize a fresh candidate from the same `512786c` archive and apply only these intended
  production files: `src/sysml_codegen/contracts/seal.py`,
  `src/sysml_codegen/contracts/verify.py`, `src/sysml_codegen/contracts/__init__.py`, and
  `src/sysml_codegen/cli/__init__.py`. Apply only the Item 6 tests/evidence needed to run the frozen
  overlay and package gates.
- [x] Run every Phase 1 overlay node unchanged and record GREEN with the same overlay SHA-256,
  environment controls, and independent-process discipline.
- [x] Complete `evidence.md` with baseline/candidate source identities, exact file allowlist,
  binary/scoped diff hash, verifier/fingerprint values, command outputs/counts, license state,
  fixture manifest, and dirty-tree comparison.
- [x] Fill the Implementation Notes below immediately after each phase. Record actual files,
  commands/results, issues, and deviations; do not mark a checkbox from intended work alone.

### Validation

**Focused normal and optimized:**

- [x] `uv run pytest -q tests/unit/test_contract_models.py tests/unit/test_verify_package.py tests/unit/test_cli_generation.py tests/conformance/test_seal_step9.py tests/conformance/test_fingerprint_stability.py`
- [x] `PYTHONOPTIMIZE=1 uv run pytest -q tests/unit/test_contract_models.py tests/unit/test_verify_package.py tests/unit/test_cli_generation.py tests/conformance/test_seal_step9.py tests/conformance/test_fingerprint_stability.py`

**Package gates:**

- [x] `uv run pytest -q tests/unit/test_package_metadata.py tests/unit/test_contract_models.py tests/unit/test_verify_package.py tests/unit/test_cli_generation.py tests/conformance/test_snapshot_contract.py tests/conformance/test_seal_step9.py tests/conformance/test_fingerprint_stability.py`
- [x] `uv run pytest tests/`; record exact pass/skip/fail/error counts and license state. Do not call
  the full suite green if failures/errors are merely known license-dependent families.

**Static, diff, fixture, and scope gates:**

- [x] `uv run ruff check src/sysml_codegen/contracts/seal.py src/sysml_codegen/contracts/verify.py src/sysml_codegen/contracts/__init__.py src/sysml_codegen/cli/__init__.py tests/unit/test_contract_models.py tests/unit/test_verify_package.py tests/unit/test_cli_generation.py tests/conformance/test_seal_step9.py tests/conformance/test_fingerprint_stability.py .project/active/constraint-wave-seal-symmetry/evidence/test_constraint_wave_seal_symmetry_overlay.py`
- [x] Run `uv run ruff format --check` on the same Python paths. Do not format inherited dirty
  files wholesale.
- [x] `uv run mypy src/sysml_codegen/contracts/seal.py src/sysml_codegen/contracts/verify.py src/sysml_codegen/contracts/__init__.py src/sysml_codegen/cli/__init__.py`
- [x] `uv run mypy src/`; compare exact errors with the recorded 76-error project baseline and
  require no new or changed Item 6 error.
- [x] `git diff --check -- src/sysml_codegen/contracts/seal.py src/sysml_codegen/contracts/verify.py src/sysml_codegen/contracts/__init__.py src/sysml_codegen/cli/__init__.py tests/unit/test_contract_models.py tests/unit/test_verify_package.py tests/unit/test_cli_generation.py tests/conformance/test_seal_step9.py tests/conformance/test_fingerprint_stability.py .project/active/constraint-wave-seal-symmetry`
- [x] `git diff -- tests/fixtures` must be empty, and
  `find tests/fixtures -type f -print0 | sort -z | xargs -0 sha256sum | sha256sum` must match the
  Phase 1 manifest.
- [x] Review `git status --short`, `git diff --name-only`, candidate allowlist, and saved inherited
  dirty-path hashes. Preserve all unrelated `.project/` changes and active-item directories. Do not
  commit, push, open/comment on a PR, merge, stash, reset, checkout, or clean.

**What We Know Works After This Phase:**

The unchanged source-isolated overlay is GREEN; normal, optimized, package, static, and scope gates
have recorded evidence; canonical/emitted policy and fingerprints agree; fixtures and unrelated
dirty work are preserved; and Item 6 is ready for independent `my-audit` rather than self-certified.

---

## Environment Setup

Use the repository environment and commands in `CLAUDE.md`. Python 3.12+ behavior is load-bearing.
Historical and candidate overlay runs must disable user site-packages and bytecode and must print
the resolved `sysml_codegen` source paths before recording evidence.

## Scope Firewall

- Allowed production scope: the four files named in Phase 5.
- Allowed kept-test scope: the five test files named in Phase 5.
- Allowed workflow scope: this `plan.md`, the Item 6 overlay, and `evidence.md`.
- No schema/version bump, coverage-policy redesign, package-layout/fixture/snapshot/archive/loader
  change, external F1 work, or whole-generation transactionality.
- The excluded-path rule retains its `[INFERRED]` provenance from the spec. Test and implement it as
  required by this stage; do not relabel it owner-settled in evidence or progress notes.

## Risk Management

See [design.md#potential-risks](design.md#potential-risks).

- **Phase 1:** Independent nodes, exact-source imports, target-operation tripwires, and green F9
  controls prevent false RED claims.
- **Phase 2:** AST equality and reuse of the inspected list prevent standalone-copy and walker
  drift; regular controls protect hash semantics.
- **Phase 3:** Before/after tree manifests and patched next-operation sentinels prove guard order and
  no-partial-contract behavior.
- **Phase 4:** Complete map comparison permits only the designed verifier consequence and catches
  accidental fixture/artifact churn.
- **Phase 5:** Source-isolated GREEN, fixture hashes, scoped diffs, and inherited-dirty hashes keep
  Item 6 separate from concurrent work.

## Implementation Notes

Fill these during implementation. A failed or unavailable gate stays unchecked with the exact
result and scope of the unproved claim. Any non-verifier artifact drift, target access before a
guard, or need to edit outside the scope firewall is a premise conflict to surface before
continuing.

### Phase 1 Completion

**Completed:** 2026-07-18
**Actual Changes:** Added the frozen 29-node overlay and kept defect-specific tests across the five
planned test files. Created `evidence.md` and recorded the fixture and inherited-dirty baselines.
**Validation:** Exact archived HEAD `512786c7…`; overlay SHA-256 `e928cdc6…1fed`; 29 independently
run nodes. Six reviewed controls/characterizations passed. All 23 new policy and route-order nodes
failed at their named assertion. The kept focused RED selection produced seven independent failures.
**Issues / Deviations:** The task-specific uv cache is `/tmp/sysml-codegen-uv-cache` because the
environment's default cache is read-only. The overlay covers no-follow ordering through route
sentinels and exact sole outcomes; deeper target-operation monkeypatches remain in the kept matrix.

### Phase 2 Completion

**Completed:** 2026-07-18
**Actual Changes:** Added `PackageSealError`, the public seal-side guard, and AST-identical
root-first inspectors. Seal hashes from the inspected list. Verification preflights before seal
loading, returns one exact link/walk diagnostic, sorts recorded paths, and reuses entries for extras.
**Validation:** Seal/verifier files passed 55 tests normally and 55 optimized. Focused selections
passed 10 seal and 17 verifier tests. Inspector/glob parity, Ruff, and format checks passed.
**Issues / Deviations:** None. The inspector is mechanical and target-independent; policy remains
at the seal/verifier call sites.

### Phase 3 Completion

**Completed:** 2026-07-18
**Actual Changes:** Guarded generation before clear/setup, Step 9 before integrity writes, and
re-seal before the model-contract check. Policy and filesystem errors use the required command
outcome/log surface. Added emitted dangling-link, Step 9, re-seal, and generation-root regressions.
**Validation:** CLI focus 3 passed; Step 9 conformance 9 passed; combined optimized 19 passed. The
emitted-byte and stdlib-only import nodes passed independently.
**Issues / Deviations:** None. Step 9 can still leave ordinary Steps 3–8 files, as designed, but
never writes a new/replacement package contract after its guard fails.

### Phase 4 Completion

**Completed:** 2026-07-18
**Actual Changes:** Added an independent source-isolated reviewed/candidate generation test,
complete non-verifier map comparison, exact canonical/emitted verifier digest checks, and
independent sorted-line fingerprint recomputation.
**Validation:** Policy-update and independent-generation nodes: 2 passed. Exact byte/hash gates: 3
passed. Optimized contract/fingerprint scope: 19 passed, 2 licensed skips. Only
`contracts/verify.py` differs: `24eb3565…0276` -> `ad0a855a…7284`; executable fingerprint
`493a9caa…aa6e` -> `ccc5efc1…ba3a`.
**Issues / Deviations:** SysIDE licensing is unavailable, so the two live-vs-snapshot nodes are
skipped and unclaimed. License-free snapshot and reviewed/candidate evidence is complete.

### Phase 5 Completion

**Completed:** 2026-07-18
**Actual Changes:** Applied only the four production files to a fresh reviewed archive and ran the
unchanged overlay node-by-node. Completed `evidence.md`, final statuses, scope/fixture comparison,
and repository gates.
**Validation:** Final isolated overlay 29/29 GREEN. Focused normal/optimized 76 passed, 2 licensed
skips each; package 84 passed, 3 skips. Full suite 2,243 passed, 205 skipped, 9 deselected, 23 failed,
96 errors, all license-dependent. Mypy stayed at 76 errors. Diff and fixture gates passed.
**Issues / Deviations:** The exact Ruff/format command reports style-only findings in the immutable
Phase 1 overlay. Editing it would invalidate the required `e928cdc6…1fed` historical/candidate
identity. All nine editable Python files are Ruff/format clean; the frozen overlay passes with only
its recorded `I001,F401,E501` findings excluded. No behavioral gate or production claim is affected.

---

**Status:** Complete
