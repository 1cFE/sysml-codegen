# Implementation Plan: Snapshot Portability and Shape Gates

**Status:** Certified
**Created:** 2026-07-18
**Last Updated:** 2026-07-19
**Branch:** `constraint-exec-epic`
**Reviewed Baseline:** `512786c7dfab44fba7a0185d09e845b7494c702d`

## Source Documents

- **Revised spec:** [spec.md](spec.md)
- **Revised design:** [design.md](design.md)
- **Historical spec review:** [spec-review.md](spec-review.md)
- **Historical design review:** [design-review.md](design-review.md)
- **Primary R-6/R-11 reproduction:**
  [constraint-exec PR-wave code review](../../research/20260718-192048_constraint-exec-pr-wave-code-review.md)
- **Epic scope and Item 3 boundary:**
  [CONSTRAINT-WAVE-REMEDIATION](../../backlog/epic_constraint_pr_wave_remediation.md)
- **Prior portability evidence:** [GAP-CLOSE lowering-integrity evidence](../gap-lowering-integrity/evidence.md)

The revised design resolves the historical review findings. Planning therefore uses the revised
design decisions while retaining the reviews as the defect and compatibility evidence. In
particular, implementation must preserve the recursive unknown-key ExpressionIR version scan even
though the revised spec still contains the older, imprecise sentence that unknown keys are ignored.
See [design.md#key-decisions](design.md#key-decisions), D3a, and
[design.md#required-invariants](design.md#required-invariants), I8.

## Implementation Strategy

### Phasing Rationale

Phase 1 freezes R-6 and R-11 independently against the exact reviewed source before any Item 4
production edit. Phase 2 implements the riskiest behavior: one lazy route-aware projection per
requested excluded usage, shared by warnings, records, and anonymous identity without touching the
eligible branch. Phase 3 adds the narrow three-section loader gate while retaining the existing
recursive foreign-version sentinel and legacy defaults. Phase 4 builds and proves both fixture
candidates before a recoverable two-file replacement. Phase 5 proves the exact relocation manifest,
then runs normal, optimized, parity, fingerprint, static, diff, and fixture gates and records honest
licensed/live evidence.

### Critical Path

Source-isolated R-6/R-11 RED -> single lowering projection and capture GREEN -> independent shape
matrix GREEN -> pre-write two-candidate proof -> transactional fixture update -> snapshot fallback
manifest -> licensed live manifest -> complete preservation and static gates.

### First Proof Point

On archived source `512786c`, separately selected overlay nodes must show all of the following:

- named selected locations remain absolute in capture, warning, and excluded records;
- one non-numerical location can reach the mapper/validator twice in a lowering run;
- wrong empty containers and missing nested keys escape as raw container exceptions or deserialize
  incorrectly; and
- the existing recursive scan rejects `expression-ir/v2` beneath an unknown extra key.

The last node is a green historical compatibility control, not an R-11 failure.

### Feasibility and Main Risks

The design fits the current code. The exclusion selector already provides stable indices; lowering
has a local call boundary; capture already deep-copies facts; and the loader has a single seam before
the two strict reconstructors. No schema bump or companion-repository change is required.

- **Double route work or ID churn:** instrument both route functions, pin exact pre-change IDs, and
  keep named minting plus the eligible branch textually outside the projector refactor. See
  [design.md#location-data-flow-and-route-parity](design.md#location-data-flow-and-route-parity).
- **Validator becomes a second schema:** build tests from independent case records, validate only
  structural policy, and leave semantic reconstruction to the existing codecs. See
  [design.md#pre-validation-policy](design.md#pre-validation-policy).
- **Unknown-extra compatibility weakens:** retain the recursive scan before kind-directed shape
  validation and test foreign v2 plus accepted v1/ordinary extras independently.
- **Partial fixture state:** produce, hash, and validate both candidates before the first write;
  journal every replacement and restore both originals after any failure or interrupted rerun.
- **Licensed evidence is unavailable:** the snapshot fallback still runs, but a skipped live node is
  recorded as `licensed live relocation skipped/unproven`; it cannot satisfy full acceptance.
- **Concurrent dirty work:** Item 6 already owns production and test edits, including additive work
  in `tests/conformance/test_fingerprint_stability.py`. Preserve its exact incoming patch and modify
  that shared test only additively. Never restore, stash, reset, clean, or rewrite unrelated paths.

### Item 3 Coordination Boundary

Item 3 remains future work. This plan validates the serialized occurrence wire shape only.

- Do not edit `src/sysml_codegen/analysis/part_instance_index.py`,
  `src/sysml_codegen/resolution/supplied_values.py`, `collect_bare_actual_demand`,
  `_expand_owner_instances`, occurrence expansion, owner-demand identity, collision handling, or
  eligible lowering.
- Do not add semantic cardinality, completeness, demand, or collision checks to the loader.
- Keep Item 3-relevant acceptance cases as syntactic pass-through controls. They may assert that a
  shape reaches the unchanged reconstructor, but must not freeze R-4/R-5/R-7 defects as desired
  semantics.
- Record pre/post hashes or diffs for the protected files. If Item 3 work appears concurrently,
  preserve it and re-run the Item 4 diff firewall rather than resolving overlap silently.

### Overall Validation Approach

- Each phase begins with kept tests or the unchanged historical overlay.
- Every RED node is independently runnable so an earlier failure cannot mask another defect.
- Focused gates run under normal Python and optimized Python (`-O`).
- Relocation compares the exact spec manifest with no timestamp, JSON, path, or generated-byte
  normalization.
- The two changed snapshots pass pointer, token, hash, and whole-corpus manifest checks.
- Licensed and unlicensed results are reported separately; skips are never called passes.
- Evidence records imported source paths, baseline/candidate revisions, commands, exit codes,
  collection counts, hashes, diffs, and inherited dirty state.

---

## Phase 1: Freeze Historical R-6/R-11 RED and Compatibility Controls

### Goal

Create independent source-isolated evidence for each reviewed defect before production changes.
Keep already-green route grammar, recursive-version, valid-empty, nullable, and legacy-degradation
behavior as controls.

### Assumption Under Test

The reviewed source leaks named paths and lacks nested v3 shape gates exactly as R-6/R-11 state,
while its recursive foreign-ExpressionIR-version scan and existing compatibility behavior already
work and must survive the correction. See [design.md#redgreen-matrix](design.md#redgreen-matrix).

### Test Stencil (Write This First)

```python
def test_r11_occurrence_missing_steps_is_contextual_domain_error(tmp_path):
    snapshot = valid_v3_snapshot()
    snapshot["part_occurrences"] = {"Pkg::Host": [{"part_def_qn": "Pkg::Host"}]}
    with pytest.raises(SnapshotFormatError) as caught:
        load_extraction_snapshot(write_snapshot(tmp_path, snapshot))
    assert "/part_occurrences/Pkg::Host/0/steps" in str(caught.value)
    assert "missing required field 'steps'" in str(caught.value)
    assert "Recapture the snapshot." in str(caught.value)
```

### Changes Required

See [design.md#redgreen-matrix](design.md#redgreen-matrix),
[design.md#required-invariants](design.md#required-invariants), and
[design.md#next-stage-handoff](design.md#next-stage-handoff).

- [x] Create
  `.project/active/constraint-wave-snapshot-portability/evidence/test_constraint_wave_snapshot_portability_overlay.py`.
  Keep it self-contained and import production only from the selected source tree.
- [x] Add separately runnable desired-behavior R-6 nodes for canonical named capture, canonical named
  warning/excluded records, root-independent named semantic/catalog fingerprints, and exactly one
  mapper/validator call for one non-numerical usage. These tests must fail on reviewed source at
  their specific canonicality, parity, or call-count assertion.
- [x] Add separately runnable desired-behavior R-11 nodes for non-mapping JSON root; wrong empty
  `constraint_facts` and `part_occurrences` containers; scalar facts lists; non-mapping facts items;
  missing usage fields; missing occurrence `steps`; wrong step item/container; and unhashable/wrong
  lowering mode. Each test expects the final contextual `SnapshotFormatError` contract and must fail
  on reviewed source because a raw exception escapes, a wrong empty container passes, or context is
  incomplete.
- [x] Add expected-green controls for anonymous route parity, named-ID stability, valid empty facts
  lists, `{}` occurrences, `[]` occurrence/step lists, explicit nullable fields, absent optional
  `operand_type`, missing `compilation_results` warning/degradation, ordinary unknown extras, nested
  `expression-ir/v1` under an unknown key, and rejection of nested `expression-ir/v2` under an
  unknown key.
- [x] Use stable node names beginning `test_r6_..._reviewed`, `test_r11_..._reviewed`, and
  `test_compat_..._control`. Do not aggregate distinct failure mechanisms in one test.
- [x] Create `evidence.md` and record baseline commit, Python/pytest versions, overlay SHA-256,
  collected node inventory, resolved `sysml_codegen` and companion import paths, fixture manifest,
  committed-baseline manifest, and the incoming dirty-path manifest.
- [x] Record the contemporaneous incoming Item 6 dirty paths and run its overlap gates. No canonical
  baseline patch artifact was retained, so do not present the historical digest as independently
  reproducible. Treat `tests/conformance/test_fingerprint_stability.py` as the only known shared
  Item 4/Item 6 test file.

### Validation

**Collect and isolate the overlay:**

- [x] Materialize `512786c7dfab44fba7a0185d09e845b7494c702d` with `git archive` under a fresh
  `mktemp -d` directory. Do not use checkout, reset, stash, or clean.
- [x] Run:

  ```bash
  uv run pytest --collect-only -q .project/active/constraint-wave-snapshot-portability/evidence/test_constraint_wave_snapshot_portability_overlay.py
  ```

- [x] Run every collected node in a fresh process against the archived source and record its exact
  result:

  ```bash
  PYTHONNOUSERSITE=1 PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/tmp/constraint-wave-snapshot-red/baseline/src \
    uv run pytest -q \
    .project/active/constraint-wave-snapshot-portability/evidence/test_constraint_wave_snapshot_portability_overlay.py::NODE
  ```

- [x] Require each R-6/R-11 desired-behavior node to be RED at its named final assertion and record
  the actual historical leak/raw exception/silent acceptance. Require every compatibility node to
  pass. Collection, import, fixture, or setup failures are invalid evidence.

**Preservation controls:**

- [x] Record `git status --short --branch`, `git diff --name-status`, and `git diff --binary` before
  implementation.
- [x] Record the full fixture manifest:

  ```bash
  find tests/fixtures -type f -print0 | sort -z | xargs -0 sha256sum | sha256sum
  ```

- [x] Record the committed-baseline manifest:

  ```bash
  find tests/fixtures/baseline_outputs -type f -print0 | sort -z | xargs -0 sha256sum | sha256sum
  ```

**What We Know Works After This Phase:**

The historical failures and compatibility firewall are reproducible on the exact reviewed source,
and the inherited Item 6/unrelated dirty state has a preservation baseline.

---

## Phase 2: Implement One Excluded-Location Projection Boundary

### Goal

Canonicalize every located selected usage once per requested index and make warnings, excluded
records, capture, and anonymous minting consume that canonical result. Preserve every ID input,
eligible fact, BLOCK ordering, and live/replay route distinction.

### Assumption Under Test

One lowering-local index cache can serve warning and record consumers without moving canonical
state into `ConstraintFacts`, `UsageDecision`, or a common ID builder. Capture can extend its copied
facts projection by removing only the named-usage skip. See
[design.md#location-data-flow-and-route-parity](design.md#location-data-flow-and-route-parity).

### Test Stencil (Write This First)

```python
def test_non_numerical_location_projects_once_and_serves_warning_record(monkeypatch, caplog):
    facts = named_non_numerical_facts(raw_file="/checkout/models/model.sysml")
    calls = instrument_live_mapper(monkeypatch)
    [record] = lower_live(facts, roots=[Path("/checkout/models")], caplog=caplog)
    assert calls == [("/checkout/models/model.sysml", [Path("/checkout/models")])]
    assert record.exclusion.location == "root-0/model.sysml:9:5"
    assert "root-0/model.sysml:9:5" in only_warning(caplog)
```

### Changes Required

See [design.md#key-decisions](design.md#key-decisions), D1-D2;
[design.md#required-invariants](design.md#required-invariants), I1-I5; and
[design.md#implementation-notes](design.md#implementation-notes).

- [x] `tests/conformance/test_constraint_snapshot_identity.py:128`: add named and anonymous located
  exclusions plus eligible controls. Flip the historical named-capture pin at line 188. Assert the
  live facts object is unchanged, selected copied facts are canonical, eligible objects remain
  byte-identical/raw, and exact named/anonymous IDs retain their pre-change bytes and suffix width.
- [x] `tests/conformance/test_constraint_snapshot_identity.py:128`: instrument both
  `map_live_source_referent` and `validate_snapshot_source_referent`. Prove one call per requested
  excluded index in live and replay, reuse across warning/record/mint, zero calls for eligible
  indices, and zero BLOCK projection from the warning pre-pass.
- [x] `tests/conformance/test_constraint_non_numerical.py:25`: replace substring-only location
  assertions with exact canonical warning and excluded-record bytes for live and replay. Keep the
  malformed BLOCK diagnostic control separate.
- [x] `tests/unit/test_source_referent.py:14`: retain grammar and route tests; rename/generalize
  consumer wording only. Add no route inference and named/anonymous caller controls without changing
  codec behavior.
- [x] `src/sysml_codegen/analysis/constraint_lowering.py:489-599,861-950`: create the one local lazy
  index-keyed projection described in D1. Make warning and exclusion consumers accept only the
  cached canonical pair. Keep the warning pre-pass before BLOCK but request only
  `NON_NUMERICAL` indices. Do not project BLOCK indices eagerly.
- [x] `src/sysml_codegen/analysis/constraint_lowering.py:895-950`: leave the named mint tuple
  `(usage_qn, kind, usage.source.form)` byte-identical. Let only anonymous minting consume cached
  referent/line/column. Do not edit the eligible branch beginning at current line 952.
- [x] `src/sysml_codegen/snapshot/serializer.py:139-160`: keep `deepcopy` and the production
  `excluded_usage_indices` selector; project every selected usage with a location. Preserve named
  no-location behavior and loud anonymous no-location failure. Never mutate live facts.
- [x] `src/sysml_codegen/analysis/source_referent.py:1-80`: generalize anonymous-only documentation;
  do not change grammar or path-selection code.
- [x] Re-run the unchanged Phase 1 R-6 overlay against candidate source. Do not edit its setup,
  expectations, or node inventory after recording the baseline overlay SHA-256.

### Validation

**Focused test-first loop:**

- [x] Run:

  ```bash
  uv run pytest -q tests/unit/test_source_referent.py tests/conformance/test_constraint_snapshot_identity.py tests/conformance/test_constraint_non_numerical.py
  ```

- [x] Run the exact same files optimized:

  ```bash
  uv run python -O -m pytest -q tests/unit/test_source_referent.py tests/conformance/test_constraint_snapshot_identity.py tests/conformance/test_constraint_non_numerical.py
  ```

- [x] Run every Phase 1 overlay node against the candidate source, one node per process. Require all
  R-6 nodes and controls GREEN; do not expect R-11 defect nodes to change yet.
- [x] Compare exact before/after named, anonymous-excluded, named-eligible, and anonymous-eligible ID
  sets. Compare serialized eligible usage objects byte-for-byte.
- [x] Inspect `git diff -- src/sysml_codegen/analysis/constraint_lowering.py` and prove no hunk
  reaches the eligible branch, owner expansion, demand collection, or Item 3 files.

**What We Know Works After This Phase:**

Named and anonymous exclusions share one explicit route projection per lowering run, capture copies
the same selected set, warnings/records are canonical, and no identity or eligible semantic input
has changed.

---

## Phase 3: Add the Narrow Three-Section Shape Gate and Error Matrix

### Goal

Reject malformed JSON root, `constraint_facts`, `part_occurrences`, and
`constraint_lowering_mode` shapes through contextual `SnapshotFormatError`, while keeping valid
nullable/empty/optional cases, recursive version scanning, and every legacy default/warning.

### Assumption Under Test

Loader-local structural validators can mirror only the companion codecs' accessed fields and exact
JSON Pointer paths without becoming a semantic schema or changing reconstruction. See
[design.md#loader-data-flow](design.md#loader-data-flow) and
[design.md#pre-validation-policy](design.md#pre-validation-policy).

### Test Stencil (Write This First)

```python
@pytest.mark.parametrize("case", INDEPENDENT_SHAPE_CASES, ids=lambda case: case.id)
def test_v3_shape_matrix_reports_context(tmp_path, case):
    malformed = case.mutate(valid_v3_wire_payload())
    with pytest.raises(SnapshotFormatError) as caught:
        load_extraction_snapshot(write_snapshot(tmp_path, malformed))
    assert case.pointer in str(caught.value)
    assert case.expected_text in str(caught.value)
    assert "Recapture the snapshot." in str(caught.value)
```

### Changes Required

See the authoritative policy in [spec.md#in-scope-field-policy](spec.md#in-scope-field-policy),
plus [design.md#key-decisions](design.md#key-decisions), D3-D5 and D3a.

- [x] `tests/unit/test_snapshot_v3_gate.py:43-200`: replace the eight-cell corruption list with
  independent case records that do not import or derive from production validator tables.
- [x] Cover JSON syntax/root, each section container, every aggregate list, every mapping-item
  layer, each required and required-nullable field, each string-list member, every ExpressionIR
  kind and child list, occurrence owner/item/step layers, boolean-versus-integer, and mode type/value.
  Include missing-key and wrong-type cases for every field-policy row.
- [x] Add valid controls for `{}` occurrences, empty aggregate/occurrence/step lists, all explicit
  nullables, absent optional `operand_type`, any JSON literal value, ordinary unknown extras, and
  unknown extra payloads containing `expression-ir/v1`.
- [x] Add the DR-2 compatibility pair: foreign `expression-ir/v2` under an unknown key remains a
  `SnapshotFormatError`; `expression-ir/v1` in the same place remains accepted structurally.
- [x] Add JSON Pointer escaping controls for dynamic owner keys containing `~` and `/`.
- [x] Add contextual error-matrix assertions for exact snapshot path, exact JSON Pointer, missing
  field or expected shape, short found type/value, recapture sentence, and chained cause for residual
  reconstructor faults. Prove raw `JSONDecodeError`, `AttributeError`, `KeyError`, `TypeError`, and
  `ValueError` do not escape.
- [x] Keep legacy controls in `tests/conformance/test_snapshot_contract.py:132-181` and
  `tests/unit/test_hygiene_tail_loader.py:81-153` unchanged: absent `compilation_results` still warns
  and degrades, and legacy loader defaults/diagnostics retain current behavior.
- [x] `src/sysml_codegen/snapshot/loader.py:136-219`: normalize JSON decode/non-mapping root before
  `.get`; keep version gating first; validate the facts envelope; run the existing recursive
  `_scan_expression_ir_versions` over the complete facts value; then run kind-directed validators
  for only the three v3 sections before reconstruction.
- [x] `src/sysml_codegen/snapshot/loader.py:213-219`: wrap facts parsing and occurrence
  reconstruction separately for only `AttributeError`, `KeyError`, `TypeError`, and `ValueError`.
  Chain the original and report `/constraint_facts` or `/part_occurrences`. Leave all legacy
  reconstruction outside the catch scopes.
- [x] `src/sysml_codegen/snapshot/loader.py`: keep JSON Pointer construction centralized and escape
  `~` as `~0` and `/` as `~1`. Reject Python `bool` where an integer is required.
- [x] `src/sysml_codegen/snapshot/__init__.py:33-35`: broaden only the
  `SnapshotFormatError` docstring. Do not change the class, exports, or format version.
- [x] Re-run the unchanged Phase 1 R-11 overlay against candidate source. Do not edit its setup,
  expectations, or node inventory after recording the baseline overlay SHA-256.

### Validation

**Focused matrix and compatibility:**

- [x] Run:

  ```bash
  uv run pytest -q tests/unit/test_snapshot_v3_gate.py tests/unit/test_occurrence_roundtrip_parity.py tests/unit/test_hygiene_tail_loader.py tests/conformance/test_snapshot_contract.py
  ```

- [x] Run optimized:

  ```bash
  uv run python -O -m pytest -q tests/unit/test_snapshot_v3_gate.py tests/unit/test_occurrence_roundtrip_parity.py tests/unit/test_hygiene_tail_loader.py tests/conformance/test_snapshot_contract.py
  ```

- [x] Run all Phase 1 R-11 and compatibility overlay nodes separately against candidate source.
  Require exact-path domain errors and unchanged valid controls.
- [x] Run mutation-matrix collection and record the number of independently addressable cases:

  ```bash
  uv run pytest --collect-only -q tests/unit/test_snapshot_v3_gate.py
  ```

- [x] Inspect `git diff -- src/sysml_codegen/snapshot/loader.py` and prove no new validation or
  exception wrapper touches legacy reconstruction after the two in-scope reconstructors.
- [x] Confirm `git diff -- src/sysml_codegen/analysis/part_instance_index.py src/sysml_codegen/resolution/supplied_values.py`
  matches the incoming Item 3 protection baseline exactly.

**What We Know Works After This Phase:**

Every in-scope malformed structure fails through one contextual snapshot-domain grammar, valid v3
compatibility remains intact, foreign IR versions under unknown keys are still rejected, and Item 3
semantics plus legacy loader behavior remain untouched.

---

## Phase 4: Build, Validate, and Transactionally Apply Both Fixture Candidates

### Goal

Change only the 65+1 named-exclusion `location.file` values in the two reviewed snapshots. Prove
both complete candidate byte strings and all prospective manifests before the first target write,
then replace the pair recoverably.

### Assumption Under Test

Both originals round-trip byte-exact through `snapshot_to_json`, so production-selector-driven
in-memory changes can preserve every non-allowlisted token. A same-filesystem journal and immutable
backups can restore the original pair after injected failures or interrupted reruns. See
[design.md#controlled-two-fixture-update](design.md#controlled-two-fixture-update).

### Test Stencil (Write This First)

```python
def test_second_replace_failure_restores_both_originals(tmp_path, monkeypatch):
    transaction = copied_fixture_transaction(tmp_path)
    originals = transaction.target_hashes()
    monkeypatch.setattr(transaction, "replace_second", raise_injected_failure)
    with pytest.raises(InjectedFailure):
        transaction.run()
    assert transaction.target_hashes() == originals
    assert transaction.recover_interrupted_run().target_hashes() == originals
```

### Changes Required

See [design.md#controlled-two-fixture-update](design.md#controlled-two-fixture-update), D6, I9-I10,
and [design.md#controlled-two-fixture-update](design.md#controlled-two-fixture-update).

- [x] Create
  `.project/active/constraint-wave-snapshot-portability/evidence/update_fixture_locations.py` with
  explicit `prepare`, `replace-first`, `replace-second`, `verify`, `rollback`, and interrupted-run
  recovery phases. Use a same-filesystem transaction directory, `os.replace`, flushed journal
  state, immutable backups, and verified original/candidate hashes.
- [x] Create
  `.project/active/constraint-wave-snapshot-portability/evidence/test_update_fixture_locations.py`
  first. Test no-write validation failures; candidate mismatch; first/second replacement failure;
  post-write manifest failure; rollback; interrupted states after each journal phase; successful
  cleanup; and rerun idempotence.
- [x] Derive selected indices with production `excluded_usage_indices` and new referents with
  `map_live_source_referent`. Assert the discovered inventory is exactly `0..64` for
  `catf_mfe_model` and `0` for `constraint_non_numerical`; do not derive scope from string grep.
- [x] Before writes, require `snapshot_to_json(json.loads(original)) == original`, exact 66 pointer
  changes, valid new referents, unchanged `captured_at`, byte-identical eligible usage objects, and
  a reverse-substitution render exactly equal to each original byte string.
- [x] Before writes, require unified diff lines to contain only the allowlisted JSON string values,
  the prospective fixture manifest to change exactly two paths, and the complete
  `tests/fixtures/baseline_outputs` manifest to remain identical.
- [x] Stage both candidates, backups, hashes, pointer records, manifests, and journal before
  replacing either target. On any exception restore both originals atomically and verify the full
  original manifest.
- [x] Apply the helper to
  `tests/fixtures/catf_mfe_model/extraction_snapshot.json` and
  `tests/fixtures/constraint_non_numerical/extraction_snapshot.json`. Do not run broad recapture.
- [x] Append to `evidence.md`: original/candidate SHA-256, all changed pointers and old/new values,
  selector identity/QN, timestamps, token-level proof, prospective/post-write manifests, journal
  phases, and rollback test results.

### Validation

**Candidate and transaction tests:**

- [x] Run:

  ```bash
  uv run pytest -q .project/active/constraint-wave-snapshot-portability/evidence/test_update_fixture_locations.py
  ```

- [x] Run the updater in `--check`/prepare-only mode and record both expected candidate hashes before
  any write.
- [x] Run failure-injection tests on copies under a temporary same-filesystem directory. Never inject
  failures against the committed targets.
- [x] Run the real transaction once only after all prepare checks pass, then rerun `--check` to prove
  the verified end state is idempotent.

**Exact diff and manifest gates:**

- [x] Run:

  ```bash
  git diff -- tests/fixtures/catf_mfe_model/extraction_snapshot.json tests/fixtures/constraint_non_numerical/extraction_snapshot.json
  ```

- [x] Require exactly the 66 allowlisted value lines, no `captured_at` change, no formatting/key-order
  churn, and no eligible usage-object delta.
- [x] Recompute the full fixture manifest and require exactly the two expected snapshot hashes to
  differ from Phase 1.
- [x] Recompute the committed-baseline manifest and require exact Phase 1 equality.
- [x] Run all committed snapshots through the v3 loader and selector inventory. Require 30 loads and
  exactly 65+1 selected named located exclusions in the two expected files.

**What We Know Works After This Phase:**

The repository contains one recoverably applied two-file semantic correction, with both candidates
proven before mutation and every other fixture/baseline byte protected.

---

## Phase 5: Prove Relocation, Parity, Fingerprints, and Repository Scope

### Goal

Execute both relocation scenarios and the complete validation ladder. Record evidence that
distinguishes license-free replay proof from licensed live/capture proof and protects Item 6 plus
all unrelated dirty work.

### Assumption Under Test

The exact named/anonymous/eligible harness can exercise capture, live lowering, replay, generation,
catalog, contract, report, and artifact-hash projections without normalizing any compared byte. The
corrected committed snapshot can provide the same replay-applicable manifest without a license. See
[design.md#exact-relocation-projection-manifest](design.md#exact-relocation-projection-manifest).

### Test Stencil (Write This First)

```python
def test_snapshot_only_moved_replay_manifest(tmp_path, caplog):
    replay_a, replay_b = build_identical_moved_replay_inputs(tmp_path)
    result_a = run_manifest(replay_a, caplog)
    result_b = run_manifest(replay_b, caplog)
    assert_manifest_equal(result_a, result_b)
    assert_no_root_bytes(result_a, replay_a.root, replay_b.root)
```

### Changes Required

See the exact harness, commands, controls, and projection table in
[design.md#exact-relocation-projection-manifest](design.md#exact-relocation-projection-manifest).

- [x] Create `tests/conformance/test_constraint_snapshot_portability.py` with one shared manifest
  collector and two independently selectable entries:
  `test_live_capture_replay_relocation_manifest` and
  `test_snapshot_only_moved_replay_manifest`.
- [x] For the licensed node, write identical model bytes under exact checkout A/B roots and assert
  extraction yields one named non-numerical exclusion, one anonymous non-numerical exclusion, and
  one admitted named control with the expected locations/decisions. Treat a shape mismatch as a
  test failure, never a skip.
- [x] Mark only the licensed entry with the shared `requires_license` marker. Do not duplicate the
  license probe.
- [x] Compare exact serialized excluded-facts canonical JSON, warning string lists, excluded records,
  catalog fingerprint, full model-contract bytes and named pointers, full report-aggregator bytes,
  the two package-contract artifact-hash values, and root-leak scans. Do not compare or normalize
  the whole snapshot, `captured_at`, eligible locations, or package executable fingerprint.
- [x] For moved replay, copy source and exact snapshot bytes and assert SHA-256 equality before use.
  For the license-free node, add the canonical anonymous fact in memory exactly as the design states
  and assert the same three named/anonymous/eligible controls before replay.
- [x] `tests/conformance/test_fingerprint_stability.py:44-162`: add only the named-exclusion semantic
  fingerprint consequence not already proven by the dedicated manifest. Preserve every incoming
  Item 6 hunk and its reviewed-verifier hash gate byte-for-byte.
- [x] Run the dedicated manifest first. If it fully covers the fingerprint consequence, leave
  `test_fingerprint_stability.py` unchanged and record that decision in `evidence.md`.
- [x] Append exact commands, collection/outcome counts, hashes, root paths, compared projections,
  and license result to `evidence.md`. Use only one of these summaries:
  `licensed + snapshot fallback passed`, or
  `snapshot fallback passed; licensed live relocation skipped/unproven`.

### Validation

**Relocation manifest:**

- [x] Always run the license-free moved replay:

  ```bash
  uv run pytest -q -rs tests/conformance/test_constraint_snapshot_portability.py::test_snapshot_only_moved_replay_manifest
  ```

- [x] Run the licensed live/capture/replay node and inspect the outcome, not only the process exit
  code:

  ```bash
  uv run pytest -q -rs tests/conformance/test_constraint_snapshot_portability.py::test_live_capture_replay_relocation_manifest
  ```

  A skip is unproven evidence and leaves the full Item 4 acceptance gate open.
- [x] Run the snapshot fallback twice in separate processes and require identical recorded
  projections/hashes. If licensed, also repeat the live node once to detect nondeterminism.

**Focused normal gate:**

- [x] Run:

  ```bash
  uv run pytest -q \
    tests/unit/test_source_referent.py \
    tests/unit/test_snapshot_v3_gate.py \
    tests/unit/test_occurrence_roundtrip_parity.py \
    tests/unit/test_hygiene_tail_loader.py \
    tests/conformance/test_constraint_snapshot_identity.py \
    tests/conformance/test_constraint_non_numerical.py \
    tests/conformance/test_constraint_snapshot_portability.py \
    tests/conformance/test_snapshot_contract.py \
    tests/conformance/test_snapshot_constraint_parity.py \
    tests/conformance/test_fingerprint_stability.py
  ```

**Focused optimized gate:**

- [x] Run the same list under optimized Python:

  ```bash
  uv run python -O -m pytest -q \
    tests/unit/test_source_referent.py \
    tests/unit/test_snapshot_v3_gate.py \
    tests/unit/test_occurrence_roundtrip_parity.py \
    tests/unit/test_hygiene_tail_loader.py \
    tests/conformance/test_constraint_snapshot_identity.py \
    tests/conformance/test_constraint_non_numerical.py \
    tests/conformance/test_constraint_snapshot_portability.py \
    tests/conformance/test_snapshot_contract.py \
    tests/conformance/test_snapshot_constraint_parity.py \
    tests/conformance/test_fingerprint_stability.py
  ```

**Historical overlay and broader regression:**

- [x] Run every historical overlay node separately against candidate source. Require every R-6,
  R-11, and compatibility node GREEN and record exact results.
- [x] Run all snapshot/parity/fingerprint/contract families:

  ```bash
  uv run pytest -q tests/unit/test_snapshot_v3_gate.py tests/unit/test_occurrence_roundtrip_parity.py tests/conformance -k 'snapshot or constraint_non_numerical or fingerprint or contract'
  ```

- [x] Run the default full suite and record passed/skipped/failed counts. License-related skips or
  failures must be listed, not collapsed into a green claim:

  ```bash
  uv run pytest -q tests/
  ```

**Static and formatting gates:**

- [x] Run Ruff on every touched Python file:

  ```bash
  uv run ruff check \
    src/sysml_codegen/analysis/source_referent.py \
    src/sysml_codegen/analysis/constraint_lowering.py \
    src/sysml_codegen/snapshot/__init__.py \
    src/sysml_codegen/snapshot/loader.py \
    src/sysml_codegen/snapshot/serializer.py \
    tests/unit/test_source_referent.py \
    tests/unit/test_snapshot_v3_gate.py \
    tests/conformance/test_constraint_snapshot_identity.py \
    tests/conformance/test_constraint_non_numerical.py \
    tests/conformance/test_constraint_snapshot_portability.py
  ```

- [x] Run formatting check on the same files plus evidence Python tools:

  ```bash
  uv run ruff format --check \
    src/sysml_codegen/analysis/source_referent.py \
    src/sysml_codegen/analysis/constraint_lowering.py \
    src/sysml_codegen/snapshot/__init__.py \
    src/sysml_codegen/snapshot/loader.py \
    src/sysml_codegen/snapshot/serializer.py \
    tests/unit/test_source_referent.py \
    tests/unit/test_snapshot_v3_gate.py \
    tests/conformance/test_constraint_snapshot_identity.py \
    tests/conformance/test_constraint_non_numerical.py \
    tests/conformance/test_constraint_snapshot_portability.py \
    .project/active/constraint-wave-snapshot-portability/evidence/update_fixture_locations.py \
    .project/active/constraint-wave-snapshot-portability/evidence/test_update_fixture_locations.py \
    .project/active/constraint-wave-snapshot-portability/evidence/test_constraint_wave_snapshot_portability_overlay.py
  ```

- [x] Run targeted mypy and report any imported-surface baseline separately:

  ```bash
  uv run mypy \
    src/sysml_codegen/analysis/source_referent.py \
    src/sysml_codegen/analysis/constraint_lowering.py \
    src/sysml_codegen/snapshot/__init__.py \
    src/sysml_codegen/snapshot/loader.py \
    src/sysml_codegen/snapshot/serializer.py
  ```

**Diff, fixture, and dirty-work gates:**

- [x] Run `git diff --check`.
- [x] Require `git diff --name-status` to contain only the planned Item 4 paths plus the exact
  inherited dirty paths recorded in Phase 1.
- [x] Preserve Item 6 through its normal/optimized overlap gates and scoped diff inspection. No
  canonical incoming patch artifact was retained, so do not claim an independently reproducible
  historical patch digest. `test_fingerprint_stability.py` has no Item 4 hunk.
- [x] Require no Item 4 diff in `part_instance_index.py`, `supplied_values.py`, companion code,
  catalog/contracts/generators/templates, version constants/values, or legacy schema files.
- [x] Recompute fixture and committed-baseline manifests. Require only the two approved snapshot
  hashes to differ from Phase 1 and zero baseline-output changes.
- [x] Scan the exact relocation projections and both changed snapshots for both checkout roots,
  including redundant-leading-separator spellings. Do not use a repository-wide absolute-path grep
  as a substitute because eligible and legacy fields intentionally retain paths.
- [x] Record final `git status --short --branch`, `git diff --stat`, `git diff --check`, exact test
  commands/results, static results, manifest hashes, and licensed evidence status in `evidence.md`.
- [x] Do not commit, push, open/update a PR, comment remotely, merge, or alter remote state.

**What We Know Works After This Phase:**

The exact replay relocation projection is license-free and byte-stable; the live/capture projection
is either genuinely passed or explicitly unproven; malformed v3 shapes fail contextually; named and
anonymous identity contracts hold; only the two approved fixture payloads changed; Item 3 remains
future work; and Item 6 plus unrelated dirty work is preserved.

---

## Environment Setup

Use the existing editable environment and commands from `CLAUDE.md`. Do not reinstall, repin, or
modify `agentic-mbse`. Before evidence runs, record:

```bash
uv run python --version
uv run pytest --version
uv run python -c "import agentic_mbse, sysml_codegen; print(agentic_mbse.__file__); print(sysml_codegen.__file__)"
```

Use fresh temporary directories for archives, generated packages, relocation roots, and failure
injection. Never use the repository root, `$HOME`, or `~` as a cleanup/transaction target.

## Risk Management

See [design.md#potential-risks](design.md#potential-risks) for the full analysis.

- **Phase 1:** independently address every historical defect and compatibility control; reject
  setup/import failures as evidence.
- **Phase 2:** pin call count, BLOCK zero-call behavior, exact IDs, and eligible bytes before
  refactoring lowering.
- **Phase 3:** generate the matrix from independent test records and keep the recursive version scan
  separate from kind-directed validation.
- **Phase 4:** validate both byte candidates and prospective manifests before any replacement; test
  rollback only on copies.
- **Phase 5:** compare only the spec-authorized semantic projection and label licensed skips as
  unproven, while whole-tree diff/manifests preserve concurrent work.

## Implementation Notes

### Phase 1 Completion

**Completed:** 2026-07-18
**Actual Changes:** Added the frozen 15-node historical overlay and `evidence.md`; archived exact
baseline `512786c`; recorded Python/pytest/import roots, overlay hash, fixture and baseline
manifests, incoming dirty paths, and the Item 6 protected-patch hash. Twelve desired R-6/R-11
nodes were independently RED and three compatibility controls independently GREEN in fresh
processes.
**Issues:** None. Every failure reached its defect-specific assertion or reproduced the reviewed
raw exception/silent acceptance. No collection, import, setup, or license failure counted.
**Deviations:** The overlay expresses the required mechanisms as 12 focused desired nodes rather
than one node per prose bullet; the parameterized R-11 node still yields eight independently
selectable collected cases. The recorded evidence preserves the full reviewed failure matrix.

### Phase 2 Completion

**Completed:** 2026-07-18
**Actual Changes:** Added one lazy per-index excluded-location projection in lowering, extended the
serializer's copied-facts projection to named exclusions, generalized source-referent wording, and
added named/anonymous/eligible byte-firewall plus mapper/validator call-count tests. The unchanged
overlay is 15/15 GREEN one node per fresh process; focused normal and optimized gates each passed
38 with 3 licensed skips.
**Issues:** Licensed live fixture tests skipped because the environment lacks a usable SysIDE
license. License-free route, capture-copy, replay, warning, exclusion, fingerprint, and exact-ID
controls passed.
**Deviations:** Exact canonical warning bytes for the committed named fixture are finalized after
Phase 4 updates its stored location. Phase 2 used equivalent live-shaped facts to prove the bytes
without prematurely editing fixtures.

### Phase 3 Completion

**Completed:** 2026-07-18
**Actual Changes:** Added loader-local JSON-shape primitives; explicit facts, ExpressionIR,
occurrence, and mode validators; JSON decode/root normalization; RFC 6901 pointer escaping; and
separate chained reconstruction error boundaries. Expanded `test_snapshot_v3_gate.py` to 55 cases,
including nullable/optional/empty controls and recursive unknown-extra version compatibility.
**Issues:** Two existing occurrence-roundtrip tests and one snapshot-contract test remain licensed
skips. All license-free cases passed normally and under optimized Python.
**Deviations:** The tests retain the original eight historical gate cells and add independent
tables instead of literally replacing the old list. This preserves prior coverage while expanding
the matrix; production remains narrowed to the three sections.

### Phase 4 Completion

**Completed:** 2026-07-18
**Actual Changes:** Added the recoverable transaction helper and five kept audit-tool tests. Built
and validated both candidates before mutation, then atomically replaced the pair through a durable
phase journal. Updated exactly 66 `location.file` pointers in exactly two snapshots.
**Issues:** Failure-injection initially showed copied fixtures still contained the original capture
root. The helper was corrected to separate target roots from source-mapping roots for copy-based
tests; production defaults them to the same fixture root. No repository target changed before the
corrected prepare pass succeeded.
**Deviations:** The byte-preservation proof uses reverse-substitution render equality plus exact
`git diff --numstat`/line review rather than a separate JSON-token lexer. This proves the same
whitespace, key-order, encoding, and non-target-token contract with less audit machinery.

### Phase 5 Completion

**Completed:** 2026-07-19. The repository-local license was loaded without exposing it, and the
formerly blocked live acceptance gate passed.
**Actual Changes:** Added the CATF-backed, collision-free relocation manifest. It compares exact
excluded-fact bytes, warning strings, excluded records, catalog fingerprint, model-contract bytes,
semantic fingerprint, generated report bytes, and both package-contract hashes. The replay digest
is pinned and passed in two fresh processes. Corrected the stale lowering warning expectation to
the canonical `root-0/design.sysml` referent. Completed focused, overlap, static, fixture, and scope
gates and recorded the repository-wide result in `evidence.md`.
**Issues:** The earlier unlicensed run skipped the live/capture/replay node. A fresh secret-safe run
closed it: the relocation file passed 3/3, the focused selection passed 407/407 normally and under
optimized Python, and the independently run licensed full suite passed 2,950 with 26 skips and 10
deselections. Whole-package generation from `constraint_non_numerical` remains correctly rejected
by certified Item 2 because the admitted sibling's formal `value` collides with the generated
binding. No name-safety rule changed.
**Deviations:** The affected CATF snapshot was preferred after proving it generates under Item 2;
the harness adds a license-free anonymous exclusion and literal-only admitted control in memory.
`test_fingerprint_stability.py` needed no Item 4 edit because the dedicated manifest covers the
fingerprint consequence. Ruff formatting would change the frozen Phase 1 overlay, so it remains at
its recorded SHA-256; all mutable Item 4 Python is Ruff-clean and formatted. Targeted mypy reports
73 imported-surface baseline errors and none in an Item 4 file.

### Independent Audit Remediation

**Completed:** 2026-07-18
**Actual Changes:** Split live and replay relocation collectors so live A/B use live pipeline and
generation routes before replay A. Added a license-free route-wiring proof. Refactored the facts
shape gate into explicit item validators and expanded the kept matrix to 336 cases. Rebuilt fixture
transaction tests from synthetic legacy copies and extended the helper/journal to stage and verify
complete fixture and baseline manifests across success, rollback, and every recovery phase. Added
the BLOCK zero-call proof and exact canonical warning/excluded-record byte pins.
**Validation:** Item 4 plus transaction evidence passed 393 tests with 14 licensed skips normally
and optimized. The 15 frozen nodes passed separately; relocation passed 2 with 1 licensed skip;
the broader family passed 446 with 26 skips and 1,393 deselected. Item 2 passed 162/162 in both
modes; Item 6 passed 122 with two licensed skips in both modes. Ruff, diff, fixture, baseline,
30-snapshot inventory, and Item 3 isolation gates passed. Targeted mypy has no Item 4 diagnostic.
The final representative post-bookkeeping route/bytes/transaction selection passed 10/10 normally
and 10/10 under optimized Python; final `git diff --check` passed.
**Issues:** The earlier license blocker is closed. Fresh licensed evidence is 3/3 for the relocation
file, 407/407 for the focused selection in both normal and optimized modes, and 2,950 passed with 26
skips and 10 deselections for the independently run repository suite.
**Deviations:** The historical Item 6 patch digest is no longer presented as independently
reproducible because no canonical baseline patch artifact was retained. Item 6 preservation is
supported by overlap tests and scoped diff inspection. The frozen Phase 1 overlay remains the sole
Ruff-format exception because changing it would invalidate its recorded evidence hash.

---

**Status:** Draft -> In Progress -> Needs Work -> Certified
