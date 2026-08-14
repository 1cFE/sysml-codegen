# Implementation Plan: Unit-Lane Port Metadata (CONSTRAINT-SEMANTICS Item 8)

**Status:** Complete
**Created:** 2026-08-13
**Last Updated:** 2026-08-13
**Branch:** `item7-rebuild`

## Source Documents

- **Spec:** `.project/active/unit-lane-port-metadata/spec.md`
- **Spec review:** `.project/active/unit-lane-port-metadata/spec-review.md` (`Approve`)
- **Design:** `.project/active/unit-lane-port-metadata/design.md` — component boundaries,
  declaration-selection law, invariants, and detailed test claims live here
- **Design review:** `.project/active/unit-lane-port-metadata/design-review.md` (`Approve`)
- **Product-lens record:** `.project/active/unit-lane-port-metadata/product-lens.md`
- **Epic scope:** `.project/backlog/epic_constraint_semantics_contract.md`, Item 8
- **Current repository state:** `.project/CURRENT_WORK.md`
- **Repository commands and environment:** `CLAUDE.md`

## The Point

**[INHERITED: `.project/backlog/epic_constraint_semantics_contract.md`, Item 8; source grade
`[AGENT] (ratified by owner, 2026-08-13)`]** One modeled design attribute must remain one public
entry source when calculations, constraint formals, and computed design attributes consume it.
Each consumer must carry the exact authored unit from its own semantic declaration. Equal metadata
must converge to one public entry point. Unequal metadata must refuse rather than being converted,
normalized, erased, copied from another lane, or split into duplicate public keys. The decided
instance graph must preserve the same result through live, in-place snapshot, and relocated
snapshot routes.

This item repairs that promise at the existing graph-v3 metadata seam. It does not add Item 6's
calculation-input provenance or Item 9's CATF model changes.

## Product-Design Disposition

Product design was skipped. The product-lens verdict is `PROCEED`: this is a compiler metadata
defect that restores existing model-author behavior. It adds no syntax, model-author choice,
workflow, CLI/API surface, interaction, or unit meaning. See
[`design.md#related-artifacts`](design.md#related-artifacts) and the final spec-stage verdict in
`product-lens.md`.

## Implementation Strategy

### Phasing rationale

The order protects the only irreversible step, fixture recapture.

1. Build and test the complete tracked-snapshot census, then freeze the pre-change path set,
   semantic digests, unit maps, and repository baselines before any production edit.
2. Add the two customer-shaped failures and the public agreement/refusal/route contract. Record
   their exact red reason while only tests and snapshot-free fixtures differ from the baseline.
3. Prove declaration selection directly, then implement the shared extraction helper and the
   closed unit-source law. This de-risks the pinned SysIDE `definition.usages` premise before the
   helper interface becomes depended on.
4. Make the envelope's existing projectability claim true at build and load. Pin structured
   refusal, atomic no-overwrite behavior, and generated-output non-consumption.
5. Reassess every tracked snapshot at the final behavior. Recapture zero times when no graph/unit
   row is stale, or exactly once for every and only stale path after review. Finish the repository
   gates, publish exact evidence, freeze the implementation SHA, and update the named Item 6
   documentation records.

### Critical path

```text
complete pre-change census and baseline
  -> A9/radius red for SI_RENDERING_COLLISION
  -> direct usages/effective-formal and alias-source proofs
  -> shared exact-unit extraction + closed elaboration selector
  -> A9/radius + agreement/refusal + three routes green
  -> envelope build/load certification + no-overwrite proofs
  -> final census -> zero recapture OR one reviewed final recapture
  -> final gates + verification.md -> immutable Item 8 SHA -> Item 6 citations
```

### First proof point

The first proof point is the direct `BandGuard` selector test. It must return the exact two-row,
non-empty map from the definition's native `usages` view before projection. This proves the design
can reach ordinary constraint formals on the pinned SysIDE build. If it cannot, stop before
extracting or applying the unit helper; a sibling-copy or slot-root fallback would violate the
approved design.

### Overall validation approach

- Every phase starts by adding or extending a kept test before changing the behavior it pins.
- Every phase ends with its focused automated checks and an explicit diff/artifact review.
- Licensed runs use the one task venv and have zero `no live syside license` skip lines.
- The default and all-marker suites are measured before and after. The default lane must pass; the
  all-marker lane must have no new failing nodes beyond the recorded collection-order failure.
- Snapshot recapture is gated by exact instance-graph payload or relevant `PortMetadata.unit`
  movement only. Envelope, projection, computation, generated-output, and count movement are
  review evidence, not recapture triggers.

## Working Rules for the Implementer

### Environment

Run licensed commands only after:

```bash
set -a
source /home/reid/1cfe/agentic-mbse/.env
set +a
```

Use `/home/reid/1cfe/item7-rebuild-venv/bin/python` for Python, pytest, ruff, and mypy. Do not use
`uv run`; `.project/CURRENT_WORK.md` records that it resolves the wrong companion checkout for this
worktree.

The repository's two maintained pytest lanes are:

```bash
/home/reid/1cfe/item7-rebuild-venv/bin/python -m pytest tests/
/home/reid/1cfe/item7-rebuild-venv/bin/python -m pytest tests/ -m ""
```

The first inherits `-m "not execution"` from `pyproject.toml:44-50`. The second clears that marker
filter and is the all-marker licensed suite.

### Progress discipline

- [x] Change this plan's status to `In Progress` before Phase 1's first write.
- [x] Check each action or validation box immediately after it succeeds. Do not bulk-check a phase
      later from memory.
- [x] Fill that phase's completion note immediately with timestamp, actual files, exact command
      results, issues, and deviations. A discovered premise conflict stays visible in the note.
- [x] Do not start the next phase while the current phase has an unchecked required validation.
- [x] Change status to `Complete` only after the Item 6 documentation handoff and final diff check.

### Stop conditions

Stop and surface the conflict instead of widening the item if any of these occurs:

- the direct `BandGuard` selector cannot obtain the exact loaded-user input declarations from
  `definition.usages`;
- the pre-change assessment rows do not exactly equal the tracked snapshot path set, or the dated
  23-path premise has drifted without recorded authority;
- the shared extractor changes existing calculation-formal unit text or precedence;
- implementation would require an instance-graph, envelope, or projector marker change;
- envelope certification exposes an unrelated graph-valid/project-invalid tracked fixture;
- final live elaboration moves graph fields beyond the explained source/formal identity and unit
  changes, or changes generated schema/JSON bytes;
- a new all-marker failure appears, a default-lane failure appears, or a licensed run contains a
  license-skip line; or
- Item 6 production code, calc-input `formal_provenance`, graph v4, or a graph-v4 recapture appears
  necessary.

---

## Phase 1: Freeze Pre-Change Inventory and Repository Baselines

### Goal

Create the tested, read-only census first. Use it to publish the exact pre-production snapshot path
set and every required graph/envelope/projection/generated-output digest, then measure the licensed
and static-analysis baselines. No production file changes in this phase.

### Assumption under test

The current tree has exactly 23 tracked v6 snapshots, every path can receive one complete assessment
row, and any graph-valid/project-invalid row is either the manufactured Item 8 collision already
explained by the approved artifacts or a stop condition. The accepted 15-path recapture manifest is
only a subset gate.

### Test stencil — write this first after the untouched-tree baseline

```python
def test_pre_inventory_rows_equal_exact_tracked_snapshot_set() -> None:
    inventory = load_inventory(PRE_INVENTORY)
    tracked = tracked_snapshots_from_git_literal_pathspec()
    row_paths = [row["path"] for row in inventory["rows"]]
    assert len(row_paths) == len(set(row_paths))
    assert sorted(row_paths) == tracked
    assert inventory["missing_paths"] == []
    assert inventory["extra_paths"] == []
```

### Changes required

See [`design.md#complete-inventory-and-conditional-recapture`](design.md#complete-inventory-and-conditional-recapture),
[`design.md#required-invariants`](design.md#required-invariants), and
[`design.md#validation-approach`](design.md#validation-approach).

#### 1. Untouched-tree repository baseline

- [x] Before the first Item 8 test/script/fixture/production write, record `git rev-parse HEAD`,
      `git status --short --branch`, and the exact pre-existing working-tree changes. The approved
      planning artifacts may already be present; do not absorb unrelated edits into Item 8.
- [x] Run and record both licensed suite baselines, including collected, passed, skipped,
      deselected, xfailed, xpassed, failed, error, and license-skip-line counts.
- [x] Run the known collection-order node in isolation and record exact counts:

  ```bash
  /home/reid/1cfe/item7-rebuild-venv/bin/python -m pytest \
    tests/execution/test_fusion_tea_real_teax.py::test_the_lane_runs_the_real_simkit
  ```

- [x] Run and record exact pre-change static/diff baselines:

  ```bash
  /home/reid/1cfe/item7-rebuild-venv/bin/python -m ruff check src/
  /home/reid/1cfe/item7-rebuild-venv/bin/python -m mypy src/
  git diff --check
  ```

  Preserve the normalized diagnostic sets, not counts alone, so the final zero-new comparison is
  mechanical.

#### 2. Inventory checker and assessment tool — tests first

- [x] Add `tests/conformance/test_v6_snapshot_inventory.py` with kept nodes:
  - `test_inventory_rejects_missing_extra_and_duplicate_rows`
  - `test_inventory_records_required_digests_and_unit_maps`
  - `test_pre_inventory_rows_equal_exact_tracked_snapshot_set`
- [x] Add `scripts/assess_v6_snapshot_churn.py`. It must pass the literal pathspec to
      `git ls-files -z` without shell expansion, sort the result, and refuse output unless the
      assessment rows equal that exact set with zero missing, extra, or duplicate paths.
- [x] Give every row the fields required by the approved design: path/fixture, envelope file SHA,
      outer digest, instance-graph fingerprint, canonical source-manifest fingerprint, relevant
      port/unit map, and, for both the committed snapshot and temporary admitted-live arms,
      projection result/counts or typed refusal, computation digest, and generated schema/JSON
      digest or typed inapplicability. Keep the staleness boolean derived only from exact graph
      payload or relevant unit-map movement.
- [x] Make the script's read-only CLI exact:

  ```bash
  /home/reid/1cfe/item7-rebuild-venv/bin/python \
    scripts/assess_v6_snapshot_churn.py \
    --output .project/active/unit-lane-port-metadata/snapshot-inventory-pre.json
  ```

#### 3. Immutable pre-change evidence

- [x] Generate `.project/active/unit-lane-port-metadata/snapshot-inventory-pre.json` before any
      production edit. Record the current full commit SHA and `git status --short --branch` in it.
- [x] Require the artifact's sorted path list to equal the output of:

  ```bash
  git ls-files 'tests/fixtures/**/instance_graph_snapshot.json'
  ```

  The expected dated count is 23 and the expected paths are recorded at
  [`design.md#appendix-a-current-tracked-snapshot-baseline`](design.md#appendix-a-current-tracked-snapshot-baseline).
  Re-derive them; do not copy the appendix into the artifact.
- [x] Create `.project/active/unit-lane-port-metadata/verification.md` and record the untouched-tree
      repository baseline plus the pre-change
      inventory command/result, exact path list/count, row count, missing/extra/duplicate counts,
      every row disposition, and the fact that v6 has no `captured_at` field.

### Validation

**Automated**

- [x] Run:

  ```bash
  /home/reid/1cfe/item7-rebuild-venv/bin/python -m pytest \
    tests/conformance/test_v6_snapshot_inventory.py \
    tests/conformance/test_v6_recapture_batch.py -q
  ```

  Expect the complete-inventory tests and the separate accepted-batch subset tests to pass. Record
  their counts separately.
- [x] Confirm the inventory artifact says 23 tracked paths, 23 unique rows, and zero missing,
      extra, or duplicate paths.
- [x] Confirm the default licensed lane passes, the all-marker failure set contains only the
      measured pre-existing node, the isolated node passes, and every licensed run has zero
      license-skip lines.

**Manual review**

- [x] Review every typed projection refusal in the pre-change artifact. Classify it as the known
      Item 8 collision or stop for a separate disposition; do not let the script silently omit its
      generated-output digest as though it were projectable.
- [x] Review the artifact's schema/version markers and confirm graph v3, envelope v6, and projector
      v1 are unchanged facts.

**What we know works after this phase:** the implementer has a complete, machine-checked pre-change
authority for every tracked snapshot and every repository baseline needed to judge later movement.

---

## Phase 2: Land the Customer-Shaped Red Contract

### Goal

Add the two kept customer characterizations plus the four agreement/disagreement and three-route
proof interfaces before production changes. Preserve the measured topology in small snapshot-free
fixtures and record the exact pre-fix refusal.

### Assumption under test

The focused A9 and radius models reproduce the customer defect as `ProjectionError` with
`SI_RENDERING_COLLISION` on the exact public keys, rather than failing to parse, selecting a
different topology, or reaching an unrelated readiness diagnostic.

### Test stencil — write this first

```python
def test_a9_constraint_formals_preserve_authored_units() -> None:
    graph = elaborate_model_paths([A9])
    projected = project(graph)  # pre-fix: exact SI_RENDERING_COLLISION
    assert lane_units(graph) == expected_a9_port_units()
    assert entry_units(projected) == expected_a9_entry_units()

def test_radius_derivation_inputs_preserve_authored_units() -> None:
    graph = elaborate_model_paths([RADIUS])
    assert every_radius_source_and_consumer_unit(graph) == "m"
    assert project(graph) has_one_entry_per_shared_source
```

### Changes required

See [`design.md#first-proofs-must-stay-red-for-the-right-reason`](design.md#first-proofs-must-stay-red-for-the-right-reason),
[`design.md#exact-proof-nodes`](design.md#exact-proof-nodes), and
[`design.md#graph-v3-and-three-route-parity`](design.md#graph-v3-and-three-route-parity).

#### 1. Snapshot-free fixtures

- [x] Add `tests/fixtures/unit_lane_a9/model.sysml` with all four authored formal lanes.
- [x] Add `tests/fixtures/unit_lane_radius/model.sysml` with computed `outer_radius` and a shared
      `TorusMinorRadius` source.
- [x] Add `tests/fixtures/unit_lane_constraint_disagreement/model.sysml` with exact `m` versus `cm`.
- [x] Add `tests/fixtures/unit_lane_computed_disagreement/model.sysml` with exact unequal spellings.
- [x] Do not capture snapshots beside any of these fixtures.

#### 2. Kept proof file and exact public interface

- [x] Add `tests/conformance/test_unit_lane_port_metadata.py`, licensed with `requires_license`.
- [x] Add the two characterization nodes first:
  - `test_a9_constraint_formals_preserve_authored_units`
  - `test_radius_derivation_inputs_preserve_authored_units`
- [x] Add the four Item 6-consumed agreement/refusal nodes:
  - `test_constraint_and_calculation_unit_agreement_projects_one_entry`
  - `test_constraint_and_calculation_unit_disagreement_refuses`
  - `test_computed_and_calculation_unit_agreement_projects_one_entry`
  - `test_computed_and_calculation_unit_disagreement_refuses`
- [x] Add `test_live_in_place_and_relocated_routes_preserve_unit_metadata`. It must compare exact
      selected port IDs and complete `PortMetadata` records, graph-v3 `unit` members and marker,
      projected public keys/unit text, and one-entry cardinality. The relocated arm must delete or
      detach the staged source tree before load.

#### 3. Record the red before production changes

- [x] With only fixtures/tests/evidence changed, run exactly:

  ```bash
  /home/reid/1cfe/item7-rebuild-venv/bin/python -m pytest \
    tests/conformance/test_unit_lane_port_metadata.py::test_a9_constraint_formals_preserve_authored_units \
    tests/conformance/test_unit_lane_port_metadata.py::test_radius_derivation_inputs_preserve_authored_units \
    -q
  ```

- [x] Record in `verification.md` the two node IDs, `ProjectionError`,
      `SI_RENDERING_COLLISION`, and exact colliding keys:
  - `CATFMFEVacuum__catf_vacuum_pumping__n_pumps`
  - `CATFMFERadialBuild__catf_radial_build__plasma_region__inner_radius`
- [x] If either node fails for another reason or passes, correct only the focused fixture/test until
      it reproduces the approved shape. Do not weaken the assertions or edit production code during
      this step.

### Validation

**Automated**

- [x] Run the whole new file once and record every node's exact result. The two characterization
      nodes must be red for the recorded collision; proof nodes may be red only where they require
      the absent lane metadata. A disagreement test that passes must still inspect both exact port
      units, so an accidental `m` versus `None` refusal cannot satisfy the planned `m` versus `cm`
      claim.
- [x] Re-run the Phase 1 inventory test and assert that the tracked snapshot path set remains
      exactly 23. The five new fixtures add no snapshot paths.

**Manual review**

- [x] Inspect the fixture diff. Confirm it does not edit `tests/fixtures/catf_mfe_gated`, does not
      change Item 9 model intent, and authors exact `m³/s`, `Dimensionless`, `m`, and `cm` strings.
- [x] Inspect `git diff -- src/sysml_codegen`; it must be empty.

**What we know works after this phase:** both customer failures are preserved as kept tests with
the right diagnostic and the downstream proof interface is fixed before implementation.

---

## Phase 3: Implement the Declaration-Owned Unit Law

### Goal

Prove the selector, redefinition, and alias premises first. Then extract the existing exact unit
algorithm into one helper and apply the approved closed source-selection map to calculation,
constraint, and computed-expression ports. Make every Phase 2 behavior proof green without schema
changes or Item 6 scope.

### Assumption under test

The selected definition's filtered native `usages` view exposes one effective input declaration per
slot, calc payloads can match that exact winner, and a computed expression's referenced declaration
remains available independently from the post-alias data edge.

### Test stencil — write this first

```python
def test_band_guard_base_formals_are_selected_from_definition_usages() -> None:
    selector = selector_for(CONSTRAINT_BINDING_UNIT_ANNOTATION)
    selected = selector.effective_input_formals(definition_named("BandGuard"))
    assert selected == expected_band_guard_slot_to_declaration_ids()
    assert all(item in band_guard.usages for item in selected_objects(selected))

def test_computed_alias_uses_referenced_declaration_unit() -> None:
    graph = elaborate_model_paths([SOURCE_IDENTITY])
    port = expression_port_referencing_alias(graph, "a")
    assert graph.metadata(port).unit == "m"
    assert graph.input_edge(port) == resolved_source_named(graph, "x")
```

### Changes required

See [`design.md#unit-lane-resolution-law`](design.md#unit-lane-resolution-law),
[`design.md#redefinition-and-alias-identity-proofs`](design.md#redefinition-and-alias-identity-proofs),
[`design.md#component-overview`](design.md#component-overview), and
[`design.md#potential-risks`](design.md#potential-risks).

#### 1. Direct selector and identity tests — before implementation

- [x] Add `tests/fixtures/unit_lane_source_identity/model.sysml`. Keep base/redefining calc and
      constraint units distinguishable and keep referenced alias `a` distinct from ultimate source
      `x`. Do not add a snapshot.
- [x] Add these kept nodes to `tests/conformance/test_unit_lane_port_metadata.py`:
  - `test_band_guard_base_formals_are_selected_from_definition_usages`
  - `test_calc_redefinition_uses_selected_effective_formal_unit`
  - `test_constraint_redefinition_uses_selected_effective_formal_unit`
  - `test_computed_alias_uses_referenced_declaration_unit`
- [x] Extend `test_live_in_place_and_relocated_routes_preserve_unit_metadata` so the selected
      base/redefined calculation, base/redefined constraint, and referenced-alias shapes all run
      through the three routes and compare structural port identity as well as metadata/output.
- [x] Make the direct `BandGuard` test fail if the selector is absent, empty, rooted, or draws from
      `definition.features`. Assert the exact two slot/declaration IDs and loaded-user `in`
      declarations specified in
      [`design.md#redefinition-and-alias-identity-proofs`](design.md#redefinition-and-alias-identity-proofs).
- [x] Add shared-helper precedence/exact-text tests to `tests/conformance/test_extractor.py` before
      moving the existing implementation. Cover type, source syntax, documentation syntax, no
      authored unit, and exact superscript/punctuation preservation.

#### 2. Shared exact-unit extraction

- [x] Add `src/sysml_codegen/extraction/feature_metadata.py` with the narrow public helper from
      [`design.md#component-overview`](design.md#component-overview).
- [x] Change `src/sysml_codegen/extraction/extractor.py:536-715` to delegate its existing
      documentation/unit precedence and source-file fallback to that helper. Preserve current
      calculation-definition output byte-for-byte.

#### 3. Closed source selector and port population

- [x] Change `src/sysml_codegen/elaboration/elaborate.py:250-270,367-420` to accept optional model
      paths and precompute the loaded-user input-declaration index needed by the selector.
- [x] Implement the private selector around the existing
      `FeatureSlotIndex.effective_declaration()` authority at
      `src/sysml_codegen/elaboration/occurrence.py:58-100`. Enumerate filtered
      `definition.usages` using the existing loaded-user pattern at
      `src/sysml_codegen/elaboration/occurrence.py:471-502`; do not use the slot root as a winner.
- [x] Update bound and unbound formal construction at
      `src/sysml_codegen/elaboration/elaborate.py:1664-1834` to use the effective declaration for
      unit source and exact calc payload match. Preserve the modeled-default-first outer rule.
- [x] For constraints, use the selected effective formal for both `ConsumerPortId.formal` and the
      existing constraint `formal_provenance`, as required by
      `src/sysml_codegen/elaboration/project.py:543-560`.
- [x] Update computed-expression metadata at
      `src/sysml_codegen/elaboration/elaborate.py:2334-2409` from the exact referenced leaf before
      `_follow_alias()` changes only the edge target.
- [x] Change `src/sysml_codegen/orchestration/elaborated_pipeline.py:45-69,100-126` so the live and
      admitted calls pass their respective model paths to `elaborate()` for source-syntax fallback.
- [x] Do not change `src/sysml_codegen/elaboration/graph.py`,
      `src/sysml_codegen/elaboration/project.py`, or
      `src/sysml_codegen/snapshot/instance_graph.py`. Do not add calculation-input
      `formal_provenance`.

### Validation

**Automated**

- [x] Run the selector alone first. It must pass before the rest of the phase is accepted:

  ```bash
  /home/reid/1cfe/item7-rebuild-venv/bin/python -m pytest \
    tests/conformance/test_unit_lane_port_metadata.py::test_band_guard_base_formals_are_selected_from_definition_usages \
    -q
  ```

- [x] Run the unit-law focused set:

  ```bash
  /home/reid/1cfe/item7-rebuild-venv/bin/python -m pytest \
    tests/conformance/test_unit_lane_port_metadata.py \
    tests/conformance/test_extractor.py \
    tests/conformance/test_constraint_binding_unit_annotation.py \
    tests/conformance/test_elaboration_projection.py \
    tests/conformance/test_elaboration_graph_roundtrip.py -q
  ```

  Expect all Phase 2 and Phase 3 nodes green, including all four exact agreement/disagreement
  nodes and three-route parity, with zero license-skip lines.
- [x] Assert A9's exact units on all four lanes: `observed`/`each_capacity` are `m³/s`, and
      `count`/`rel_tol` are `Dimensionless`. Assert every radius derivation/source entry is `m`.
- [x] Assert calc base/redefinition, constraint base/redefinition, and referenced-alias cases record
      their exact binding member, slot root, selected definition, effective formal, structural port,
      unit, edge, and public key as applicable.
- [x] Run changed-file ruff over every touched Python file in this phase. Expect zero findings.

**Manual review**

- [x] Compare existing calculation-definition extractor outputs before/final for the focused
      precedence fixtures. Confirm the refactor changed no existing unit string.
- [x] Review the production diff against the closed source table in
      [`design.md#unit-lane-resolution-law`](design.md#unit-lane-resolution-law). Confirm there is no
      sibling copy, arithmetic inference, conversion, normalization, graph post-pass, or Item 6
      provenance work.
- [x] Confirm graph-v3, snapshot-v6, and projector-v1 markers remain byte-identical.

**What we know works after this phase:** each repaired port derives exact unit metadata from its own
semantic declaration, effective-formal and alias identity are pinned, valid shared sources
deduplicate, genuine disagreement still refuses, and all three routes preserve the same graph data.

---

## Phase 4: Certify Projectability at the Envelope Boundary

### Goal

Make the v6 envelope own the projectability guarantee it already advertises. Preserve exact
projection diagnostics through build/load refusal, prove public capture and CLI fail before write,
and pin that `EntryPoint.unit_text` does not currently move generated parameter schema/JSON bytes.

### Assumption under test

One private envelope helper can compose graph validation with the existing projector on both build
and decoded-load paths without duplicating comparison policy, changing markers, or moving atomic
write ownership out of `snapshot/capture.py`.

### Test stencil — write this first

```python
def test_resealed_unit_collision_is_not_certifiable(tmp_path, captured_payload) -> None:
    document = reseal_with_two_units_for_one_public_source(captured_payload, "m", "cm")
    with pytest.raises(SnapshotCertifiabilityError) as excinfo:
        load_instance_graph_snapshot(write(tmp_path, document))
    assert excinfo.value.diagnostics[0].code is ElaborationCode.SI_RENDERING_COLLISION
    assert expected_public_key in excinfo.value.diagnostics[0].detail

def test_capture_unit_collision_does_not_replace_destination(tmp_path) -> None:
    destination = write_sentinel(tmp_path)
    with pytest.raises(SnapshotCertifiabilityError):
        capture_instance_graph_snapshot([DISAGREEMENT], destination)
    assert destination.read_bytes() == SENTINEL
```

### Changes required

See [`design.md#envelope-projectability-certification`](design.md#envelope-projectability-certification),
[`design.md#envelope-projectability-proof`](design.md#envelope-projectability-proof), and
[`design.md#complete-inventory-and-conditional-recapture`](design.md#complete-inventory-and-conditional-recapture).

#### 1. Refusal, atomicity, and generation tests — before implementation

- [x] Add
      `tests/conformance/test_elaboration_projection.py::test_unit_text_and_missing_unit_remain_a_rendering_collision`
      to pin the already-correct non-null-versus-`None` policy independently from parsing.
- [x] Add
      `tests/conformance/test_snapshot_v6_envelope.py::test_resealed_unit_collision_is_not_certifiable`.
      Recompute the inner graph fingerprint and outer digest so the test reaches projectability,
      not an earlier integrity refusal.
- [x] Add these public capture nodes to `tests/conformance/test_unit_lane_port_metadata.py`:
  - `test_capture_unit_collision_does_not_replace_destination`
  - `test_capture_unit_collision_does_not_create_destination`
- [x] Extend `tests/conformance/test_cli_snapshot_refusal.py` with
      `test_unit_collision_exits_one_with_exact_diagnostic_and_preserves_destination`. Assert exit
      1, no traceback, exact code/key/detail, and byte-identical sentinel output.
- [x] Add `tests/conformance/test_entry_point_generation.py` with
      `test_entry_point_unit_text_does_not_change_generated_schema_or_json`. Generate both trees
      through the production entry-point schema and JSON generators and compare sorted relative
      paths and exact bytes.

#### 2. One envelope certifier

- [x] Change `src/sysml_codegen/snapshot/envelope.py:152-207,283-301` to add the one private
      `_require_certifiable(graph)` owner specified by the design. It must call existing graph
      validation and then `project(graph)`, discarding the result.
- [x] Call that helper from both `build_envelope()` and `_decode_graph()`.
- [x] Give `SnapshotCertifiabilityError` a public ordered `diagnostics` tuple. Preserve
      `SI_RENDERING_COLLISION`, exact public key/detail, readable message text, and exception
      chaining from `ProjectionError`/graph validation.
- [x] Change `src/sysml_codegen/cli/__init__.py:884-925` so `cmd_snapshot` catches the existing
      snapshot base error and renders the exact certifiability diagnostic before returning 1.
- [x] Leave `src/sysml_codegen/snapshot/capture.py:17-34` structurally unchanged: it builds the
      envelope before `_write_atomically()`. Do not call `project()` from capture.

### Validation

**Automated**

- [x] Run:

  ```bash
  /home/reid/1cfe/item7-rebuild-venv/bin/python -m pytest \
    tests/conformance/test_snapshot_v6_envelope.py \
    tests/conformance/test_snapshot_v6_capture.py \
    tests/conformance/test_cli_snapshot_refusal.py \
    tests/conformance/test_entry_point_generation.py \
    tests/conformance/test_unit_lane_port_metadata.py \
    tests/conformance/test_elaboration_projection.py -q
  ```

  Expect all tests green and zero license-skip lines on licensed nodes.
- [x] Run graph codec and route regression coverage:

  ```bash
  /home/reid/1cfe/item7-rebuild-venv/bin/python -m pytest \
    tests/conformance/test_elaboration_graph_roundtrip.py \
    tests/conformance/test_snapshot_v6_routes.py \
    tests/conformance/test_exact_pipeline_context.py -q
  ```

- [x] Run changed-file ruff across all Python files touched through Phase 4. Expect zero findings.

**Manual review**

- [x] Inspect the re-sealed refusal's ordered diagnostics and CLI log. Confirm code, public key,
      and “conflicting projected metadata” survive; “invalid snapshot” alone is insufficient.
- [x] Confirm missing destinations remain missing, sentinel destinations remain byte-identical,
      and no temporary files remain.
- [x] Confirm the generated-output proof compares exact production bytes and the production diff
      contains no projector equality change, capture-local policy, codec change, or marker bump.

**What we know works after this phase:** envelope build and load certify one existing projection
law, adversarially re-sealed disagreement refuses with structured evidence, capture/CLI never
overwrite on refusal, and unit-text changes alone leave current generated entry-point bytes stable.

---

## Phase 5: Final Census, Conditional Recapture, Verification, and Item 6 Handoff

### Goal

Test and publish the final complete tracked inventory, execute the zero-or-one recapture law, run
all repository gates, record exact results in `verification.md`, freeze a reviewed Item 8
implementation-and-test SHA, and update only the named Item 6 documentation consumers.

### Assumption under test

Final live behavior changes only explained graph/unit data. The assessment can therefore classify
every tracked path mechanically, and any required recapture can be one reviewed final-schema batch
covering every and only stale path.

### Test stencil — write this first

```python
def test_final_inventory_and_recap_receipt_obey_zero_or_one_law() -> None:
    final = load_inventory(FINAL_INVENTORY)
    assert row_paths(final) == tracked_snapshots_from_git_literal_pathspec()
    if not final["stale_paths"]:
        assert not RECAPTURE_RECEIPT.exists()
    else:
        receipt = load_receipt(RECAPTURE_RECEIPT)
        assert receipt["invocation_count"] == 1
        assert receipt["paths"] == final["stale_paths"]
```

### Changes required

See [`design.md#complete-inventory-and-conditional-recapture`](design.md#complete-inventory-and-conditional-recapture),
[`design.md#validation-approach`](design.md#validation-approach), and
[`design.md#item-6-evidence-handoff`](design.md#item-6-evidence-handoff).

#### 1. Final inventory tests and read-only assessment — tests first

- [x] Extend `tests/conformance/test_v6_snapshot_inventory.py` with kept nodes:
  - `test_final_inventory_rows_equal_exact_tracked_snapshot_set`
  - `test_final_inventory_records_every_path_addition_and_removal`
  - `test_final_inventory_classifies_every_digest_and_unit_movement`
  - `test_final_inventory_and_recap_receipt_obey_zero_or_one_law`
  - `test_non_stale_snapshot_bytes_are_unchanged`
- [x] Generate the read-only final assessment after production and focused tests are final:

  ```bash
  /home/reid/1cfe/item7-rebuild-venv/bin/python \
    scripts/assess_v6_snapshot_churn.py \
    --baseline .project/active/unit-lane-port-metadata/snapshot-inventory-pre.json \
    --output .project/active/unit-lane-port-metadata/snapshot-inventory-final.json
  ```

- [x] Require final rows to equal the then-current tracked set exactly. Record the sorted final
      paths/count, pre/final additions and removals, and authority for each path-set change. Expect
      no additions from the snapshot-free characterization fixtures; the check decides.
- [x] Review every row's old/final graph payload, relevant unit map, envelope SHA/digest, source
      manifest, projected counts/refusal, computation digest, and generated-output digest. Stop on
      unrelated graph or generated-byte movement.

#### 2. Execute exactly one recapture branch

- [x] If `stale_paths` is empty: do not run a capture command; do not change any existing snapshot
      or `tests/fixtures/v6_recapture_batch/batch.json`; do not create
      `.project/active/unit-lane-port-metadata/v3-recapture.json`.
- [x] If `stale_paths` is non-empty: review and sign off the exact set first, then run this mutating
      command exactly once:

  ```bash
  /home/reid/1cfe/item7-rebuild-venv/bin/python \
    scripts/assess_v6_snapshot_churn.py \
    --baseline .project/active/unit-lane-port-metadata/snapshot-inventory-pre.json \
    --assessment .project/active/unit-lane-port-metadata/snapshot-inventory-final.json \
    --recapture-reviewed \
    --receipt .project/active/unit-lane-port-metadata/v3-recapture.json
  ```

  The invocation must stage public captures for every and only stale path, promote nothing unless
  all capture/round-trip/projection/route/generated-digest checks pass, update affected historical
  batch records in the same promotion, and emit per-path old/new SHA, graph fingerprint, exact unit
  changes, projected/computation/generated evidence, and marker checks.
- [x] After either branch, run the license-free inventory/receipt tests and the accepted-batch
      subset check. Prove every non-stale pre-existing snapshot stayed byte-identical.

#### 3. Final focused and repository gates

- [x] Run the exact Item 8 focused interface and record every node/count:

  ```bash
  /home/reid/1cfe/item7-rebuild-venv/bin/python -m pytest \
    tests/conformance/test_unit_lane_port_metadata.py \
    tests/conformance/test_extractor.py \
    tests/conformance/test_elaboration_projection.py \
    tests/conformance/test_elaboration_graph_roundtrip.py \
    tests/conformance/test_snapshot_v6_envelope.py \
    tests/conformance/test_snapshot_v6_capture.py \
    tests/conformance/test_cli_snapshot_refusal.py \
    tests/conformance/test_entry_point_generation.py \
    tests/conformance/test_v6_snapshot_inventory.py \
    tests/conformance/test_v6_recapture_batch.py -q
  ```

- [x] Run the default maintained licensed lane. It must pass with zero license-skip lines:

  ```bash
  /home/reid/1cfe/item7-rebuild-venv/bin/python -m pytest tests/
  ```

- [x] Run the all-marker licensed suite and require no new failing node relative to Phase 1:

  ```bash
  /home/reid/1cfe/item7-rebuild-venv/bin/python -m pytest tests/ -m ""
  ```

- [x] Run the known node in isolation again. It must pass, and Item 8 must not claim to have fixed
      its whole-set collection-order behavior:

  ```bash
  /home/reid/1cfe/item7-rebuild-venv/bin/python -m pytest \
    tests/execution/test_fusion_tea_real_teax.py::test_the_lane_runs_the_real_simkit
  ```

- [x] Run changed-file ruff explicitly over the final touched Python set. At minimum this set is:

  ```bash
  /home/reid/1cfe/item7-rebuild-venv/bin/python -m ruff check \
    src/sysml_codegen/extraction/feature_metadata.py \
    src/sysml_codegen/extraction/extractor.py \
    src/sysml_codegen/elaboration/elaborate.py \
    src/sysml_codegen/orchestration/elaborated_pipeline.py \
    src/sysml_codegen/snapshot/envelope.py \
    src/sysml_codegen/cli/__init__.py \
    scripts/assess_v6_snapshot_churn.py \
    tests/conformance/test_unit_lane_port_metadata.py \
    tests/conformance/test_extractor.py \
    tests/conformance/test_elaboration_projection.py \
    tests/conformance/test_snapshot_v6_envelope.py \
    tests/conformance/test_cli_snapshot_refusal.py \
    tests/conformance/test_entry_point_generation.py \
    tests/conformance/test_v6_snapshot_inventory.py
  ```

  Add any other touched Python file to the command. Expect zero findings.
- [x] Run and compare the full static/diff gates:

  ```bash
  /home/reid/1cfe/item7-rebuild-venv/bin/python -m ruff check src/
  /home/reid/1cfe/item7-rebuild-venv/bin/python -m mypy src/
  git diff --check
  ```

  Require zero new ruff/mypy diagnostics against Phase 1, zero findings on touched Python files,
  and zero whitespace errors.

#### 4. Publish exact verification evidence

- [x] Complete `.project/active/unit-lane-port-metadata/verification.md` with every exact invocation
      and its collected/passed/skipped/deselected/xfailed/xpassed/failed/error counts, plus
      license-skip-line count. Do not summarize several runs into one total.
- [x] Record both characterization nodes' pre-fix exception/code/key and post-fix exact unit maps.
- [x] Record the five exact Item 6-consumed proof nodes and claims, the four semantic identity
      nodes, the direct non-null/`None` refusal, the envelope/CLI/no-overwrite proofs, and the
      generated-output boundary proof.
- [x] Record the complete sorted pre/final snapshot path sets and counts, exact row-set equality,
      additions/removals, every per-path digest/unit disposition, and the zero-recapture decision or
      single receipt. Keep the 15-path accepted-batch result separate from complete-set evidence.
- [x] Record exact changed-file ruff, full ruff, mypy, diff-check, focused/default/all-marker,
      isolated-node, inventory, and recapture-batch counts. State the parked full-suite conflict
      plainly; do not relabel the known whole-set failure as a pass.

#### 5. Freeze Item 8 and update Item 6's evidence citations

- [x] Review the implementation/test/fixture/inventory/verification diff. Create one local reviewed
      Item 8 implementation-and-test commit after all preceding gates pass; record its full SHA with
      `git rev-parse HEAD`. This is not `close`, `pre_pr`, a push, or a main-branch operation.
- [x] Make a narrow documentation-only handoff into:
  - `.project/active/calcdef-constraint-gate-design/design.md` — R5, R8, and the component-manifest
    recapture entry;
  - `.project/active/calcdef-constraint-gate-design/implementation-item.md` — Start gate and exact
    dependency pins, Item 8 ownership gate, and Phase 4.
- [x] Cite the immutable full Item 8 SHA, exact kept node IDs and claims, exact disagreement
      exception/code/key, sorted final tracked path set and count, set-equality result, and Item 8's
      v3 recapture disposition/receipt. Replace stale 21-fixture claims with the future rule, not
      with Item 8's current count: Item 6 must re-derive its own pre/final tracked sets and prove its
      graph-v4 rows cover the required union/final sets at its separately authorized baseline.
- [x] Confirm the documentation handoff does not authorize or implement Item 6 and does not cite the
      historical 15-path subset as complete coverage.
- [x] Finish the plan completion notes and checkboxes immediately, run `git diff --check` on the
      documentation-only handoff, and record the result in `verification.md`.

### Validation

**Automated**

- [x] All focused, default, all-marker, isolated-node, inventory, subset-batch, ruff, mypy, and diff
      commands above are recorded with exact final counts.
- [x] The default lane has zero failures; all-marker has zero new failing nodes; all licensed runs
      have zero license-skip lines; touched Python ruff is clean; full ruff/mypy are zero-new;
      `git diff --check` is clean.
- [x] Final row paths equal the final tracked snapshot paths, with no duplicates/missing/extra rows;
      the recapture receipt is absent for an empty stale set or records one invocation over exactly
      the non-empty stale set.

**Manual review**

- [x] Review every snapshot and manifest byte diff, if any, against the final assessment before
      accepting it. Confirm no interim capture was promoted and all markers remain final v3/v6/v1.
- [x] Read the Item 6 edits as a fresh implementer. Confirm the exact Item 8 SHA/nodes/claims are
      sufficient to run its prerequisite gate and its future complete-set obligation cannot be
      mistaken for a fixed number or the accepted-batch subset.
- [x] Review `git status --short --branch` and confirm no Item 9 model, Item 7 documentation, TEAx,
      `main`, push, close, or `pre_pr` work entered the item.

**What we know works after this phase:** Item 8 is fully evidenced at one immutable implementation
SHA; all tracked snapshot churn is reviewed under the zero-or-one law; final repository gates are
recorded exactly; and Item 6 can consume the unit/refusal/route contract without reimplementing it.

---

## Risk Management

See [`design.md#potential-risks`](design.md#potential-risks) for the complete analysis.

- **Phase 1 — incomplete census:** Git's literal tracked path set is the authority; row equality and
  duplicate checks must pass before an artifact is written.
- **Phase 2 — false characterization:** the test must fail with the measured projection exception,
  code, and key. Parser/readiness failures do not count.
- **Phase 3 — wrong declaration:** the direct `BandGuard` map and distinguishable redefinition/alias
  units fail before a rooted or post-alias source can look plausible.
- **Phase 4 — boundary policy duplication:** one envelope helper calls the existing projector;
  capture and graph validation acquire no copied comparison law.
- **Phase 5 — recapture hides churn:** exact payload/unit comparison decides staleness; every other
  digest is reviewed evidence, and unexpected graph/generated movement stops promotion.
- **Repository baseline:** exact pre/final node and diagnostic sets prevent the known all-marker
  failure or existing ruff/mypy debt from hiding a new regression.

## Scope Boundaries

The following are out of scope for this plan:

- Item 9 changes, including any edit to `tests/fixtures/catf_mfe_gated`;
- Item 7 product/reference documentation or verification-matrix work;
- Item 6 production implementation, calculation-input `formal_provenance`, graph v4, catalog 4,
  projector v2, or graph-v4 recapture;
- TEAx or agentic-mbse changes;
- unit conversion, dimensional analysis, arithmetic unit inference, spelling normalization, or new
  unit syntax;
- graph/envelope/projector version changes;
- repair of the existing all-marker collection-order failure;
- `my-close`, `pre_pr`, push, publication, or any `main` operation.

## Implementation Notes

Fill these during implementation. Do not wait until the end of the item.

### Phase 1 completion

**Completed:** 2026-08-13 15:49:59 PDT

**Actual files and changes:**

- Added the test-first complete-set gate in `tests/conformance/test_v6_snapshot_inventory.py`.
- Added the read-only Git-derived assessment in `scripts/assess_v6_snapshot_churn.py`.
- Published `snapshot-inventory-pre.json` and opened `verification.md` before production edits.

**Exact validation results:** Default licensed 2028 passed / 34 skipped / 79 deselected;
all-marker 2106 passed / 34 skipped / 1 known failure; isolated known node 1 passed; inventory plus
accepted-subset tests 63 passed. Inventory is 23 paths / 23 unique rows / zero missing, extra,
duplicate, stale, or projection-refusal rows. Ruff baseline 12; mypy baseline 55 errors in 11 files;
`git diff --check` clean. Every licensed behavioral run had zero license-skip lines.

**Issues / premise conflicts:** The plan's isolated execution-node command deselected the node under
the default marker, so the exact attempt is recorded and the behavioral run added `-m ""`. The
sandbox initially caused 13 unrelated scratch-directory errors in the all-marker lane; the approved
filesystem rerun removed them and reproduced only the known failure. V6 has no `captured_at` field,
as the approved design already surfaced.

**Deviations and authority:** No scope or semantic deviation. The marker override and sandbox rerun
make the required baseline executable without changing tests or product behavior.

### Phase 2 completion

**Completed:** 2026-08-13 15:54 PDT

**Actual files and changes:** Added four snapshot-free focused models and
`tests/conformance/test_unit_lane_port_metadata.py` with the two customer characterizations, four
agreement/disagreement proof nodes, and one parameterized three-route proof.

**Exact validation results:** The exact two-node red command collected 2 and failed 2 with
`ProjectionError` / `SI_RENDERING_COLLISION` on the required `n_pumps` and `inner_radius` keys.
The whole new file collected 8 and failed 8 only at the absent constraint/computed unit contract.
The exact tracked-set node passed 1/1; Git remained at 23 tracked snapshots; production diff empty.
All licensed runs had zero license-skip lines.

**Issues / premise conflicts:** The initial focused A9 declaration order surfaced
`pumping_speed_total` first. Reordering only the new fixture's constraint formals reproduced Item
5's required `n_pumps` collision while preserving the same four-lane topology.

**Deviations and authority:** No scope or contract deviation. The pre-production fixture correction
is expressly allowed by Phase 2's “correct the focused fixture until it reproduces” instruction.

### Phase 3 completion

**Completed:** 2026-08-13 16:08:25 PDT. All Phase 3 test-first, implementation, focused validation,
and manual review work is complete.

**Actual files and changes:** Added the snapshot-free source-identity fixture and its exact selector,
redefinition, alias, and three-route proofs. Added the shared `extract_feature_unit()` helper,
delegated legacy extraction to it, selected effective input declarations from filtered native
`definition.usages`, populated formal/expression units from their exact declarations, and passed
live/admitted model paths into elaboration. Graph, projector, and graph codec files were untouched.

**Exact validation results:** The selector red node failed 1/1 before implementation, then passed
1/1. The shared helper red run failed 2/2 on the absent module, then passed 2/2. The final licensed
unit-lane file passed 13/13. The prescribed focused set passed 101/101 with zero skips and zero
license-skip lines. Changed-file ruff passed with zero findings; `git diff --check` passed. Exact
commands and intermediate counts are in `verification.md`.

**Issues / premise conflicts:** The focused A9 fixture's binding order initially disagreed with the
parser's exact redefinition slots after Phase 2 reordered its definition formals; the binding order
was aligned without changing the required topology or first `n_pumps` collision. A specialized
derived constraint cannot own a second result expression, so the source-identity fixture uses
explicit cross-definition formal redefinitions. This exercises the approved slot/effective-formal
law while giving each selected definition one valid predicate. No production premise conflict.

**Deviations and authority:** No contract or scope deviation. Python scalar type lookup retains its
existing slot-root rule; only the Item 8 unit source moved to the selected/referenced declaration.
No calculation `formal_provenance`, schema marker, conversion, normalization, sibling lookup, or
Item 6 production behavior was added.

### Phase 4 completion

**Completed:** 2026-08-13 16:15:00 PDT. Envelope certification, atomic refusal, CLI rendering, and
generated-output independence are implemented and verified.

**Actual files and changes:** Added one envelope `_require_certifiable()` helper used by build and
decoded load. It composes existing graph validation with `project(graph)`. Structured ordered
diagnostics now survive through `SnapshotCertifiabilityError`; the snapshot CLI catches the public
snapshot base error and renders exact certifiability evidence. Added re-sealed load, public capture
no-create/no-replace, CLI sentinel, non-null/`None`, and production generated-byte tests. Capture,
projector equality, graph codec, and schema marker owners were untouched.

**Exact validation results:** The six test-first nodes initially produced 2 passes and 4 expected
failures: load/capture accepted project-invalid graphs and CLI returned 0. After implementation,
the same six passed 6/6. The prescribed Phase 4 focused gate passed 98/98 with zero skips. The graph
codec and route gate passed 36/36. Changed-file ruff passed with zero findings and
`git diff --check` passed. Exact commands are in `verification.md`.

**Issues / premise conflicts:** None. The re-sealed collision reaches projection after inner and
outer digests are recomputed, and returns `SI_RENDERING_COLLISION` with the exact public key and
“conflicting projected metadata” detail.

**Deviations and authority:** No deviation. `snapshot/capture.py` remains structurally unchanged and
owns atomic write timing. Entry-point schema/JSON generation was tested through its production
generators and was not changed. Graph v3, snapshot v6, and projector v1 remain fixed.

### Phase 5 completion

**Completed:** 2026-08-13 16:50:34 PDT

**Actual files and changes:** Added the five final inventory gates and published the complete final
assessment. Added three constraint-population expectation records required by the new snapshot-free
fixtures. Final-suite compatibility corrections preserved direct elaborator construction,
definition-typed constraint selection, semantic-boundary rules, and license-free snapshot replay.
Published exact final evidence, froze Item 8, and made only the named Item 6 documentation handoff.

**Exact validation results:** Authoritative final assessment 23 tracked / 23 assessed / zero stale,
missing, extra, or duplicate, with empty additions/removals. No capture command ran and no receipt
exists. Inventory plus historical batch passed 68/68. The plan-focused gate passed 244/244 and the
expanded focused gate 273/273. Default licensed passed 2066 / 34 skipped / 79 deselected; all-marker
was 2144 / 34 / exactly 1 known failure; the known node passed 1/1 with `-m ""`. All licensed runs
had zero license-skip lines. Touched-file ruff was clean; full ruff retained the exact 12-finding
baseline; mypy had zero added and three removed diagnostics (52 final versus 55 baseline);
`git diff --check` passed. Exact commands and intermediate failed-gate counts are in
`verification.md`.

**Implementation-and-test SHA:** `62a07e5c870158672eb100f1cba73adfe4c9df28`.

**Item 6 handoff result:** Updated only design R5, R8, and the recapture manifest entry plus
implementation-item status/start pin, ownership gate, and Phase 4. The records cite the full SHA,
five exact nodes/claims, both disagreement keys, this item's sorted 23-path evidence, exact set
equality, and zero v3 recaptures. They require Item 6 to derive its future path sets from Git and do
not authorize Item 6 production, graph v4, calc-input `formal_provenance`, or TEAx work.

**Issues / premise conflicts:** The first final assessment exposed false unit text `From` from
provenance comments in `catf_mfe_gated`; this was surfaced, proved red, and corrected before any
capture. The first two maintained final-suite attempts exposed five then two genuine compatibility
failures; each was fixed in scope and all final gates/census were rerun. The known all-marker
collection-order failure remains parked exactly as at baseline. The plan's literal isolated command
remains marker-deselected; the marker-cleared isolated node passes.

**Deviations and authority:** No semantic or scope deviation. Output piping only limited terminal
capture; pytest arguments remained exact. The approved filesystem route was used where hard-coded
fixture scratch paths required it and sandbox errors were never treated as behavior. Graph v3,
envelope v6, projector v1, exact-text/no-conversion refusal, envelope-owned certification, and the
graph-bytes/unit-only recapture trigger are preserved. No Item 9 derivative/model, Item 7
documentation, Item 6 production, TEAx, `main`, push, close, or `pre_pr` work occurred.

---

**Status progression:** Draft -> In Progress -> Complete
