# Verification: Unit-Lane Port Metadata (CONSTRAINT-SEMANTICS Item 8)

**Status:** Complete
**Date:** 2026-08-13
**Scope:** Standalone Item 8 only

## Authority and untouched-tree baseline

- Baseline commit: `906ea5c301c0c860f67c132db4e4e82a995ba2a4`.
- Baseline branch/status command: `git status --short --branch`.
- Baseline status: branch `item7-rebuild`; pre-existing modified
  `.project/CURRENT_WORK.md`; pre-existing untracked approved artifacts under
  `.project/active/unit-lane-port-metadata/`; no source, test, fixture, snapshot, Item 6, Item 7,
  Item 9, TEAx, or companion edit.
- Baseline snapshot command: `git ls-files
  'tests/fixtures/**/instance_graph_snapshot.json'`.
- Baseline snapshot result: 23 sorted tracked paths.
- V6 note: `captured_at` is not a v6 field. The format rejects it and deterministic capture has no
  capture timestamp. Envelope SHA/digest movement remains recorded evidence.

## Pre-change repository gates

All licensed commands exported `/home/reid/1cfe/agentic-mbse/.env` first and used
`/home/reid/1cfe/item7-rebuild-venv/bin/python`. Import-path proof resolved `agentic_mbse` from
`/home/reid/1cfe/agentic-mbse-item7-rebuild` and `sysml_codegen` from this worktree. Every licensed
run below contained zero `no live syside license` skip lines.

| Gate | Exact command | Exit | Collected | Passed | Skipped | Deselected | Failed | Errors | Result |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| Default maintained baseline | `python -m pytest tests/` | 0 | 2141 | 2028 | 34 | 79 | 0 | 0 | Genuine licensed pass |
| All-marker first attempt | `python -m pytest tests/ -m ""` | 1 | 2141 | 2093 | 34 | 0 | 1 | 13 | Environment-invalid: sandbox denied the suite's hard-coded `/home/reid/1cfe/item7-*` temporary directories; not used as the behavioral baseline |
| All-marker baseline, required filesystem access | same command | 1 | 2141 | 2106 | 34 | 0 | 1 | 0 | Expected baseline failure only |
| Known node, plan command as written | `python -m pytest tests/execution/test_fusion_tea_real_teax.py::test_the_lane_runs_the_real_simkit` | 5 | 1 | 0 | 0 | 1 | 0 | 0 | Marker-deselected; not a behavioral run |
| Known node, isolated all-marker | same command plus `-m ""` | 0 | 1 | 1 | 0 | 0 | 0 | 0 | Genuine isolated pass |

No xfailed or xpassed nodes appeared in these runs. The genuine all-marker failure set is exactly:

- `tests/execution/test_fusion_tea_real_teax.py::test_the_lane_runs_the_real_simkit`

The inherited unconditional all-marker-pass conclusion remains parked. Item 8 requires zero new
final failing nodes and does not own this collection-order defect.

Static baselines:

| Gate | Exact command | Exit | Exact baseline |
|---|---|---:|---|
| Full-source ruff | `python -m ruff check src/` | 1 | 12 `UP042` findings |
| Full-source mypy | `python -m mypy src/` | 1 | 55 errors in 11 files |
| Whitespace | `git diff --check` | 0 | 0 whitespace failures |

The normalized ruff and mypy diagnostic texts are the command output from this baseline. Final
comparison must add no finding; touched Python files must be clean.

## Pre-change complete snapshot inventory

Exact command:

```text
python scripts/assess_v6_snapshot_churn.py \
  --output .project/active/unit-lane-port-metadata/snapshot-inventory-pre.json
```

Result: `23 tracked, 23 assessed, 0 stale, 0 missing, 0 extra, 0 duplicate`.

- Assessment rows equal the literal Git pathspec result exactly.
- All 23 committed and live arms project.
- Every committed exact graph payload and relevant port-unit map equals its temporary admitted-live
  counterpart at the pre-change behavior.
- Graph marker is `instance-graph/v3`; every envelope is v6 and names
  `instance-projector/v1`.
- No existing graph-valid/project-invalid fixture was found, so the design's unrelated-refusal
  stop condition did not fire.
- Per-path envelope SHA, outer digest, graph fingerprint, source-manifest fingerprint, complete
  port-unit map, projected counts, computation digest, generated entry-point path set/digest, and
  committed/live comparison are published without compression in
  `snapshot-inventory-pre.json`. That JSON is the exact per-path disposition record.

Sorted tracked path set:

1. `tests/fixtures/agg_literal_probe/instance_graph_snapshot.json`
2. `tests/fixtures/attr_expr_probe/instance_graph_snapshot.json`
3. `tests/fixtures/catf_mfe_d5/instance_graph_snapshot.json`
4. `tests/fixtures/catf_mfe_gated/instance_graph_snapshot.json`
5. `tests/fixtures/chain_spike_d5/instance_graph_snapshot.json`
6. `tests/fixtures/constraint_domain_satisfy_calc_def/instance_graph_snapshot.json`
7. `tests/fixtures/constraint_inline/instance_graph_snapshot.json`
8. `tests/fixtures/constraint_multi_instance/instance_graph_snapshot.json`
9. `tests/fixtures/constraint_non_numerical/instance_graph_snapshot.json`
10. `tests/fixtures/constraint_occurrence_demand_overrides_d5/instance_graph_snapshot.json`
11. `tests/fixtures/d38_caret/instance_graph_snapshot.json`
12. `tests/fixtures/deep_cross_scope_probe/instance_graph_snapshot.json`
13. `tests/fixtures/fusion_tea/instance_graph_snapshot.json`
14. `tests/fixtures/gate_a_d5/instance_graph_snapshot.json`
15. `tests/fixtures/modeled_default_fidelity/instance_graph_snapshot.json`
16. `tests/fixtures/nested_occurrence_override_probe/instance_graph_snapshot.json`
17. `tests/fixtures/quoted_owner_formula/instance_graph_snapshot.json`
18. `tests/fixtures/retype_model/instance_graph_snapshot.json`
19. `tests/fixtures/sample_model/instance_graph_snapshot.json`
20. `tests/fixtures/shadowed_reference/instance_graph_snapshot.json`
21. `tests/fixtures/solar_battery_d5/instance_graph_snapshot.json`
22. `tests/fixtures/unresolvable_attr_probe/instance_graph_snapshot.json`
23. `tests/fixtures/wi014_toy/instance_graph_snapshot.json`

Inventory/batch gate: `python -m pytest tests/conformance/test_v6_snapshot_inventory.py
tests/conformance/test_v6_recapture_batch.py -q` collected 63 and passed 63. The complete inventory
contributed 3 passes. The accepted historical subset contributed 60 passes and still covers 15
captured corpus snapshots; it is not complete-set evidence.

## Phase evidence

### Phase 2 red characterizations

The snapshot-free fixtures and kept proof interface landed before any production edit.

Exact red command:

```text
python -m pytest \
  tests/conformance/test_unit_lane_port_metadata.py::test_a9_constraint_formals_preserve_authored_units \
  tests/conformance/test_unit_lane_port_metadata.py::test_radius_derivation_inputs_preserve_authored_units \
  -q
```

Result: 2 collected, 0 passed, 2 failed, 0 skipped/deselected/xfailed/xpassed/errors, zero
license-skip lines. Both fail at `project(graph)` after successful licensed elaboration:

| Node | Pre-fix exception | Code | Exact colliding public key |
|---|---|---|---|
| `test_a9_constraint_formals_preserve_authored_units` | `ProjectionError` | `SI_RENDERING_COLLISION` | `CATFMFEVacuum__catf_vacuum_pumping__n_pumps` |
| `test_radius_derivation_inputs_preserve_authored_units` | `ProjectionError` | `SI_RENDERING_COLLISION` | `CATFMFERadialBuild__catf_radial_build__plasma_region__inner_radius` |

The first A9 fixture draft encountered `pumping_speed_total` first. Reordering only the focused
constraint definition's formal declarations made the kept characterization reproduce Item 5's
named `n_pumps` first collision without changing the A9 topology or expected units. This fixture
correction occurred before production edits.

Whole new proof file: 8 collected, 8 failed, 0 other outcomes, zero license-skip lines. The two
characterizations and both route cases fail on the expected projection collisions. The four
agreement/disagreement nodes fail because the still-absent constraint/computed metadata is `None`
where the kept contract requires exact `Dimensionless`, `cm`, or `m` text. The disagreement tests
inspect the repaired lane before accepting the existing refusal, so `m` versus manufactured `None`
cannot satisfy the planned `m` versus `cm` proof.

Tracked-path regression: the Phase 1 equality node passed 1/1 and Git still reports 23 tracked
snapshot paths. No new fixture has a snapshot. `git diff -- src/sysml_codegen` was empty.

### Phase 3 declaration-owned unit law

The selector and helper were proved red before production changes:

| Gate | Exact command | Result |
|---|---|---|
| Selector red | `python -m pytest tests/conformance/test_unit_lane_port_metadata.py::test_band_guard_base_formals_are_selected_from_definition_usages -q` | 1 collected, 1 failed because `_EffectiveInputFormalSelector` was absent |
| Shared helper red | `python -m pytest tests/conformance/test_extractor.py -k shared_feature_unit -q` | 65 collected, 63 deselected, 2 failed because `feature_metadata` was absent |
| Shared helper green | same command | 65 collected, 63 deselected, 2 passed |
| Selector green | same selector command | 1 collected, 1 passed |

All selector and unit-lane runs exported the licensed companion `.env`; every one had zero
license-skip lines. The final exact selector map is non-empty and exactly:

- `a25d4eca-7e4c-55fd-88af-e2b703d539e4` →
  `a25d4eca-7e4c-55fd-88af-e2b703d539e4` (`ref_value`);
- `8540a49e-c62d-5b4b-b96c-a31d5f85e7ee` →
  `8540a49e-c62d-5b4b-b96c-a31d5f85e7ee` (`tol`).

The source-identity fixture records binding member, slot root, selected definition, effective
formal, structural port, exact unit, resolved edge, and public key in kept assertions. Its derived
calc and constraint formals explicitly redefine base `cm` declarations with `m` declarations. The
computed expression references alias `a` (`m`), while the edge follows to `alias_source` (`cm`).

Focused iteration record for exact command `python -m pytest
tests/conformance/test_unit_lane_port_metadata.py -q`:

| Iteration | Passed | Failed | Skipped/errors | Finding |
|---:|---:|---:|---:|---|
| 1 | 5 | 8 | 0 | Constraint native formals may be `ReferenceUsage`; source fixture output redefinition invalid |
| 2 | 6 | 7 | 0 | Native filter fixed; A9 binding order exposed exact positional slots; source fixture still invalid |
| 3 | 9 | 4 | 0 | A9 green; specialized derived constraint lacked an executable predicate |
| 4 | 9 | 4 | 0 | Repeating an inherited predicate was parser-invalid; no production work accepted from this run |
| 5 | 13 | 0 | 0 | Explicit cross-definition formal redefinitions made all behavior nodes green |
| 6 | 12 | 1 | 0 | Strengthened identity test needed asserted constraint subtypes in its test-only lookup |
| final | 13 | 0 | 0 | All strengthened behavior and identity assertions pass |

The single-node correction command
`python -m pytest tests/conformance/test_unit_lane_port_metadata.py::test_constraint_redefinition_uses_selected_effective_formal_unit -q`
collected 1 and passed 1.

The prescribed focused command was:

```text
python -m pytest \
  tests/conformance/test_unit_lane_port_metadata.py \
  tests/conformance/test_extractor.py \
  tests/conformance/test_constraint_binding_unit_annotation.py \
  tests/conformance/test_elaboration_projection.py \
  tests/conformance/test_elaboration_graph_roundtrip.py -q
```

Its first run collected 101: 89 passed, 9 failed, and 3 errored because exact referenced
redefinitions can inherit their scalar typing from the slot root. Unit ownership does not change
that established Python-type rule. Restoring root-owned scalar-type lookup left exact unit lookup
on the referenced declaration. The final run collected 101 and passed all 101 with zero skips,
deselections, xfails, xpasses, errors, failures, or license-skip lines.

Changed-file ruff command:

```text
python -m ruff check \
  src/sysml_codegen/extraction/feature_metadata.py \
  src/sysml_codegen/extraction/extractor.py \
  src/sysml_codegen/elaboration/elaborate.py \
  src/sysml_codegen/orchestration/elaborated_pipeline.py \
  tests/conformance/test_extractor.py \
  tests/conformance/test_unit_lane_port_metadata.py
```

Result: zero findings. `git diff --check` also passed. Manual diff review found no unit conversion,
normalization, arithmetic inference, sibling consumer lookup, graph post-pass, or calculation
`formal_provenance`. `graph.py`, `project.py`, and `snapshot/instance_graph.py` have no Phase 3
diff. The markers remain `instance-graph/v3`, snapshot v6, and `instance-projector/v1`.

Fixture corrections stayed in the test-first surface. After Phase 2 reordered A9 definition
formals to reproduce `n_pumps` as the first collision, Phase 3 aligned its bound-member order with
the parser's exact redefinition slots. The source-identity fixture uses explicit cross-definition
formal redefinitions because a specialized constraint inherits its sole result expression and may
not own a second one. Both shapes preserve the approved source-selection law; neither changes
production scope.

### Phase 4 envelope certification

The test-first command selected the six new contract nodes:

```text
python -m pytest \
  tests/conformance/test_elaboration_projection.py::test_unit_text_and_missing_unit_remain_a_rendering_collision \
  tests/conformance/test_snapshot_v6_envelope.py::test_resealed_unit_collision_is_not_certifiable \
  tests/conformance/test_unit_lane_port_metadata.py::test_capture_unit_collision_does_not_replace_destination \
  tests/conformance/test_unit_lane_port_metadata.py::test_capture_unit_collision_does_not_create_destination \
  tests/conformance/test_cli_snapshot_refusal.py::test_unit_collision_exits_one_with_exact_diagnostic_and_preserves_destination \
  tests/conformance/test_entry_point_generation.py::test_entry_point_unit_text_does_not_change_generated_schema_or_json -q
```

Before envelope changes it collected 6: 2 passed and 4 failed. The already-correct direct
non-null/`None` rendering collision and production generated-byte independence passed. The
re-sealed load and both public captures did not raise, and CLI returned 0. After adding the single
build/load certifier and public error handling, the same command passed 6/6 with zero skips and
zero license-skip lines.

The re-sealed load changes A9 constraint `count` from `Dimensionless` to `cm`, then recomputes the
graph-v3 fingerprint and v6 outer digest. Its ordered error contains exactly
`SI_RENDERING_COLLISION`, public key
`CATFMFEVacuum__catf_vacuum_pumping__n_pumps`, and “conflicting projected metadata”. Public capture
against the disagreement fixture returns the same structured evidence before atomic write. A
missing destination stays absent, an existing sentinel stays byte-identical, and no matching
temporary file remains. The CLI returns 1, renders the code/key/detail, emits no traceback, and
preserves its sentinel bytes.

The prescribed focused gate was:

```text
python -m pytest \
  tests/conformance/test_snapshot_v6_envelope.py \
  tests/conformance/test_snapshot_v6_capture.py \
  tests/conformance/test_cli_snapshot_refusal.py \
  tests/conformance/test_entry_point_generation.py \
  tests/conformance/test_unit_lane_port_metadata.py \
  tests/conformance/test_elaboration_projection.py -q
```

Result: 98 collected and 98 passed in 4.16 seconds, with zero skips, deselections, xfails, xpasses,
failures, errors, or license-skip lines.

The graph/route regression gate was:

```text
python -m pytest \
  tests/conformance/test_elaboration_graph_roundtrip.py \
  tests/conformance/test_snapshot_v6_routes.py \
  tests/conformance/test_exact_pipeline_context.py -q
```

Result: 36 collected and 36 passed in 19.42 seconds, with zero other outcomes and zero license-skip
lines.

Ruff over every Python file touched through Phase 4 initially found two import-order issues in the
new assessment script and extended CLI test. After formatting those imports, the exact same
changed-file command passed with zero findings. `git diff --check` passed. Diff review confirms no
changes to `snapshot/capture.py`, `elaboration/project.py`, `snapshot/instance_graph.py`, or
`elaboration/graph.py`; no projector equality change, capture-local comparison policy, codec
change, marker bump, or temporary artifact exists. Production entry-point generators emitted the
same sorted two-path set and exact bytes for graphs differing only by `unit_text`.

### Phase 5 final inventory, recapture decision, and gates

The five final-inventory nodes were added first. Before the artifact existed, `python -m pytest
tests/conformance/test_v6_snapshot_inventory.py -q` collected 8: the 3 pre-inventory nodes passed
and the 5 final nodes failed on the intentionally absent final JSON.

The first read-only assessment was run after Phase 4 and reported `23 tracked, 23 assessed, 1
stale, 0 missing, 0 extra, 0 duplicate`. It identified only
`tests/fixtures/catf_mfe_gated/instance_graph_snapshot.json`, with graph/unit/envelope/computation
movement, unchanged source manifest, projected counts, and generated entry-point bytes. Review
found three new computed-port units equal to literal text `From`, taken from provenance comments
such as `// From radial build line 82`. That is not an authored unit. No capture command had run.

A kept helper assertion then proved the issue red: `python -m pytest
tests/conformance/test_extractor.py::test_shared_feature_unit_precedence_and_exact_text -q`
collected 1 and failed 1 because the helper returned `From` instead of `None`. Adding `from` to the
existing non-unit comment-token set made the same node pass 1/1. This preserves exact unit strings
while refusing provenance prose; it does not normalize a unit.

The assessment was rerun after each later production correction. The last run below occurred after
production code had settled, so it is the authoritative final assessment:

```text
python scripts/assess_v6_snapshot_churn.py \
  --baseline .project/active/unit-lane-port-metadata/snapshot-inventory-pre.json \
  --output .project/active/unit-lane-port-metadata/snapshot-inventory-final.json
```

Result: `23 tracked, 23 assessed, 0 stale, 0 missing, 0 extra, 0 duplicate`. The literal Git
pathspec set still has 23 paths. Pre/final additions and removals are both empty. All 23 exact graph
payloads and relevant unit maps match live admitted elaboration. The final JSON records every
committed/live envelope SHA, outer digest, graph fingerprint/payload digest, source fingerprint,
unit row, projection/count/refusal result, computation digest, and generated path-set/digest.

Per-path final disposition follows. Each digest pair is `envelope SHA / outer digest`, `graph
fingerprint / graph payload digest`, and `computation / generated-entry-point digest`. “Identical”
means committed and admitted-live values match for graph bytes, the complete unit map, envelope,
source manifest, projected counts, computation, and generated output. The complete exact unit rows
remain in `snapshot-inventory-final.json`; every row below has an empty unit delta.

| Tracked snapshot | Envelope / outer | Graph fingerprint / payload | Source manifest | Computation / generated | Disposition |
|---|---|---|---|---|---|
| `tests/fixtures/agg_literal_probe/instance_graph_snapshot.json` | `3e4981e072b011179fdabdece93a0ba842917074fdb69fa0e74469b2c58f47c0`<br>`8d1c08706270f02b2df274a5f7086a292aa2fa26916608e0074b6299721f47f4` | `75d2d5822b0ff1be3320488fc9bf8611251464e315106a11f50ceb3fa3100875`<br>`c753826078c11dea750d97d6759fb6d1ab3cd75d841bbab626f2b0a2bde84f16` | `ae812f0768ac3b42c6536842235a637a0df056e6b2c237be394a5fa3abc12a50` | `451fce1552f15420e52ec7cdc6f31c59df532ea0d9e3e938728b4ed2f1b5c648`<br>`fa3639354b191ddf43ce9e90fcb7a6107885cda90b9fa0f77754d94fc2b62428` | Identical; stale `false` |
| `tests/fixtures/attr_expr_probe/instance_graph_snapshot.json` | `293e32caced690d0fb8121dfd6b6de2d23a0123caafc029985c6d519c98aa77e`<br>`51f0b67743d4b743f35a9ba191886216afdb0df8fe853cdf63959d9a358687e9` | `e1c5f182fe5fc3bbba74216ffced3211d33f24b6bc4c7dc9d6e14c1fb3c35239`<br>`c9c7a0e1ee0cbf850574c4dc2f81990b1b3c84b9d95e637a923d021aa37a57ef` | `b22d5423714ab97b6585374988db0340933952a68f215484bfa2b24f1e2f875f` | `774390959fc4f19603bc300bb850069b7a20a017eec9cc8ce4988319cfae69a5`<br>`6df4920eead4141ff15bdf5cf364ac75bf79463aaaf9e0b3ad2d9bc2b8ebf188` | Identical; stale `false` |
| `tests/fixtures/catf_mfe_d5/instance_graph_snapshot.json` | `44bd40f5567611a9d6e8ed3456e8e1c7f22adb6dc35253531e0ad97fb152699a`<br>`b645b88bc6527e1a861a024e9bf02d4c1df8d1f2c2bbc0ebd79332af247d2329` | `bb68fea9c655162cffc293145a880e24c887f0a95f5c12a6f07e58bd567e64fa`<br>`106fd0e8c1b61a3dac56d34ff24d5cf4184d162aafbf5296aa473c698874b9ae` | `5b2464e14d40c3f5ac4e9f12e60213db7ae33c7532f40239b9e38568fd9716fc` | `52ab1029a9b91e4c1c5bfd954b9faff2f502ce0be6001a70c1758647191f54c0`<br>`1a87cbfcaa13f62705f4b7ddcd5751956d153eeb26b66bb72d85bc4cf27aedbc` | Identical; stale `false` |
| `tests/fixtures/catf_mfe_gated/instance_graph_snapshot.json` | `b7b71b2324340b9c5417afbfbb25e5a95c5ba4476ab3ba3d39bf3df2e5037ee9`<br>`494b4a57ff5ea5283d2f757e723d048a636606326280dff669fc9dc609682d1c` | `04765cbf3d76cc401a63c9361683ba3be59b1893fc9bb7c2467ffa32db4451a5`<br>`abeba82c1ab1eda9ee956f0c717fa93a581f8a8fed704edc77cff3cb5d2c62e3` | `90d10b5b75b135ceb0d67e98f7fba4446050e46f377d9edf8c20fad2db4788fc` | `7f709981e4a4c135c906f45abf7a1b70fe69f00b3c68de8cfb5baa55604658d5`<br>`99de25d6c97f88dcb540013a16cd3906c3f587cee6a81612309ca71c58b232d2` | Identical; stale `false` |
| `tests/fixtures/chain_spike_d5/instance_graph_snapshot.json` | `aefe6263f0bba3282f5cffce2426ddfe94259a54935444fcb1bca4ab0342e379`<br>`af4d8a7f6f7d85f06f5bae3b4e66ebfd4a155e7154f19ef947f0fc797e8725e1` | `9a3d4822efdb5e1ffbb8403e2770359c1139139fba481581072bd3827cbfe1b8`<br>`59f5db3b6e4a94c1af399ab08c24f4bf928e1fb460667203fb871b02396a6ab8` | `3efcc6839bc8cd43604216aec217149f9e02b285c93326af4f09d43267c36d6b` | `9140cb642d5b66141bdb7a6d0bd60ac31238b96f2252fa91706c4c1dd60c1e22`<br>`0a6fa215175e1c723bcc2361c015c33bd4d68ab5c338b5353c969a0b2addf419` | Identical; stale `false` |
| `tests/fixtures/constraint_domain_satisfy_calc_def/instance_graph_snapshot.json` | `b7f175a1f19c5dc00bbd3cfdfe2a0340cb3634d10425c26a01d04b2d9e82521e`<br>`064c7a7e0624e8914e76cb89398c63f3f9290d21fc07c03d09794fd6b4e78517` | `1d4593863be6c4ce0773cf5cf04e983786255f514cb29757ed69fd636bc5af35`<br>`37eacd1d31a0189b7eb37d3e32ada3b26e2cdd904ca269b7e44355c689dadb47` | `5270c264c4533c8fb71c8e4485c45e6cc013b7bdc8cfb23ece911302f7fab812` | `ef3ef76c19eaaa6c9a7e85946b4d2e80e035c5413cc40dcfcb372f69f78c6496`<br>`eebc1b9d58ee82735359111ebab16733d43f176451b04a738a736b25e8b3e447` | Identical; stale `false` |
| `tests/fixtures/constraint_inline/instance_graph_snapshot.json` | `09a2c2d23ebf6c1265e645ad7f9a3b73ff967c89d2682c8537dab45954767acc`<br>`cdb72efd2d967a645790290a3c1759e295f7b8e66230f332b2b98d8f7e6f9fb6` | `ad95a7435356b437f56ec1d78633b26a2ae137f3ce58b92590b4ff8529a17500`<br>`8e0607c5b8a611ef51a6e6d685b2ae95f989c97fd245d90c8f3eb5032e6384e9` | `bfe9a4a9fc86e06a1831de3b2664ab52768fb3319627e0d13cd88e027ad9a946` | `6ee6127ba2f32e0fbd90d43e9b7edcfadf9535b8e35788ad6a3d1c63a2d845d0`<br>`804c2a6120b0dec163883390e433f79108a41a164a05c89f554c6fd5edd7d24d` | Identical; stale `false` |
| `tests/fixtures/constraint_multi_instance/instance_graph_snapshot.json` | `dd51d3d6c55bc72bf278ea54cbd0c8288476bceaec77e8171365f30b9da3abe4`<br>`c2acf86b56a1308fdc70adedbe97be16e6957ed877bfb83a86d956940702c4b0` | `f4fe17acad7123e97fa88fd17f435954155a446c205a4f7e180e7d71d8a216c2`<br>`1a091b7d7d9b5541c9fdfab2a454acd3f57d39aaa84ce02868cc519fee5c18f9` | `2b5878c22a1d3132cb46741ba68113c1cc697e05d1073098e080da6dee523ede` | `a414e65ab0717a472433a80ca2c35841ced3925624371ea8a4d48b000f8bd1a2`<br>`a3d6165695576731d9b5b2aac40e5acb369166a2e706ef3f5e32ba44cd8e109d` | Identical; stale `false` |
| `tests/fixtures/constraint_non_numerical/instance_graph_snapshot.json` | `0b77f709f29a661e7d2796d881fbfd9c2720cddc300824dc8dd6f34b5c9261be`<br>`77483745d4842455c4f64326d49e0c68905e8075889002cbde972fe77e594adf` | `08cc2d5e05517cede5e9e6a97588eb09cb6455bbb29e73145e197ed691282da1`<br>`c9c73cacebbeb9d907f03a43d0ff51dcbddc1f78135049575da52c540f137143` | `38954e9f230e859b14c98adee043bb6680ccbab0e53c0361f7e6686c2a991b72` | `ec9109790a4d5563624e894210cfc86d8458052cab34a302436a846e227a5803`<br>`a235040e6de0a8a3b3d533f010af0017fafdde5f1a2053383dce3f84c6cc392b` | Identical; stale `false` |
| `tests/fixtures/constraint_occurrence_demand_overrides_d5/instance_graph_snapshot.json` | `dd42832953c9fb3171ce1933e6ca5d38bc5aa9b0c8dbb06692d16abdb9c606f6`<br>`e70f28a225f2425792da9bbfa85f6cec34a1aab42faf20b83a5b1e38f17b3ebd` | `0804a3ebd4591d620d57c5176276983b90d77971b2b714c4cdcf57d528fd1d82`<br>`ad94803bba95f1340658a489028fdf6553b0ea25e9aff2df3218e4b9b9fbf92f` | `c795ea5a95d101e7a618adc0714457b17b41d6cfdf841967a1ce51828c6678dd` | `df4228c662545b9d497205f98f53a1d3a536c845e3648a8d6000421bbb2dc725`<br>`8520af3b031b39cd885409989aaf8cb6ffffac681e724ee4f964ae163daa4d88` | Identical; stale `false` |
| `tests/fixtures/d38_caret/instance_graph_snapshot.json` | `8df3672d1826b2cb6a883b6514853963b98bc06e1fef90cefc33505e447ba927`<br>`e773be57d13cc9b368a2832652591a8eb490ba86b6f5c01ac3f5ba7ee42b9464` | `38f84931b17190c85c801acda38a09f8cfeae65d901205f19adb7bd9bb2b9830`<br>`b10a34d4a05f6c057be27de86651d15982f8757e872b286fdb4207023fa0c062` | `d9da015a5fee13fbe8a1615e3fd588cbb6da9e405657b144cb07fb12f40be0c4` | `cd9f3075a1f2a99237d353fa23e4270e467c57ebfc6ac5e5b861792e2601a09f`<br>`18c1c643cdaaa924dbd512d30831cb927035c812191a36485d5a8a242af1c808` | Identical; stale `false` |
| `tests/fixtures/deep_cross_scope_probe/instance_graph_snapshot.json` | `1e8274c175349c2415329f057dcabbf683dc476624241ca9bb30b45da278f923`<br>`d60be4bfd02c606e399847d8d77893af0e3fa9d980acfa62b47fa63e64d05789` | `3371955b60fadb7b84724dfd92af04f0b1e97fad0e13942a234bdd56c1294c8f`<br>`88a6d0fac826c86d92a75df424b4024b08e46afbb245add99acb7ac5dd639ff2` | `44e2bd6c466f7545856704d5f6cd16dc9e086f5c7d16434b8b98dbbe7c327864` | `cfb0a15bcf96b6ab7597755a6bfc0b0e2f245a93c81b0e9a4547d314cf27e090`<br>`e577f75c0a9454c27bf9582677d4826357de2bd150d2b4fbfed04830f5f314b1` | Identical; stale `false` |
| `tests/fixtures/fusion_tea/instance_graph_snapshot.json` | `c91a8bf55720cb18cb70ffd16c1442ef4f6aba3a027eeacf300d76abdc2cacd2`<br>`2f0fc3064b1a297f9951a336e7d102d41ac37197971dff617fba264cec5ad1c3` | `f2f448a954b5f7c1f399a4e258ca059fe2ee894335d71edf19f2284246414a5e`<br>`a07ccddf2bbe173508c8c67ca5b8f74ab9d001a9f5be1bdf35d08da4a712d595` | `a024f0cc67cf2d110cdb1c17ca5d7de1ced35b8b374f26e8014da3c3c4cb60b2` | `cd3fa624c46692f85dc0a26d51f521f6362151075d85aea84cbcc8dcdba4a65f`<br>`c4685b6ac4c047cbaa9f6cc3a099bf4ce25237dc2eaf6e38fab21e4246c8846e` | Identical; stale `false` |
| `tests/fixtures/gate_a_d5/instance_graph_snapshot.json` | `3983d074d9523ead7c581aa84abcb834ea9939a97b9a69be732c59a3eedca84f`<br>`9abfc95de8fe8ccd7afd280dfb143ea6b2041de6ce73e03d835383e71e94b314` | `a631fffff8fe521951a121ff67bdd79c43102d73cdc69c912a9de3afb218038d`<br>`57983dba3f754a90557552e72db6e859cd9ff5033dc694e43f5562d8f4c5bc69` | `18252172a6d438f0eaf38cb8063944cc36f4613b85c513b03035b8bcb2ef88df` | `51156527dd4ad1a408523cd9617022b492a6a3fe5bb97936a401bb560bb5c0f9`<br>`5f61a4f6e5c271db522610efbc35de0449d9b20f2b296da00f081a97cf597293` | Identical; stale `false` |
| `tests/fixtures/modeled_default_fidelity/instance_graph_snapshot.json` | `2359d062b6a1c13c3400b837ffe94fb63597f46ba411ceffd4f91b20fd0bb1c7`<br>`28ce95658c3e0a2a14a02bb08a9a361b2b9c7ed82617631c2a9c343e1dca5ae9` | `fe79e1f88d84a3424c6286f3bf604e3b04d87af7897127db044808ca26d82ae5`<br>`a605203c562f85c70741817ef0fea011fca1983e903b331373d5cee716611e20` | `13ae214b3d8fbdf7811fae853d5337bb8d532aaf4ed1f5bb327c0baf952007a7` | `c1d542c94b7303150f81ff82c9cd8792882af83e8fb1635f994d4fb38b408d41`<br>`b388bb94517435e3347e771f874f6f43914b42b2ca78e67d48aa0f20f4ad0abe` | Identical; stale `false` |
| `tests/fixtures/nested_occurrence_override_probe/instance_graph_snapshot.json` | `3b9e1c30b59072642c6ecf0aae1f58c143c758381a036153b5e46f552335f237`<br>`2af823390633e447bc08d23e0ecf58dae1bcca13e65cc11914ea4c64f5cfa0f4` | `dbf2b24b1c89593ff72417b3b2eeb88ec5e805bc5ede1c70e978568c9a7b13eb`<br>`7b59382bb68f9aecb1243e4bec1563f24c1dec2e6e9212540d5ff680413403e9` | `8e6fb6ef5cc16599975a7f809aaa662ca15ee844f488259ac264f8db95889cdd` | `a620958cd4baa78698266a294add6e86833adb8aea419d35d28a267cc61395fa`<br>`1fd3aec762e069acf0ae70621090056f01f225d52afcb3d603aac50af2ba31b0` | Identical; stale `false` |
| `tests/fixtures/quoted_owner_formula/instance_graph_snapshot.json` | `4b92b9183a2e320cbf03ad098727a8eddeadc80358367d31273a25ca60c98971`<br>`72f4a24a99746815f93fabf42bac688c44710bfa75606bb951f63045e1f8e9fd` | `138c04218a746de3aa5047bbd6a5d6fc374113955e59273d514f17b948f7fcd5`<br>`63158543056b3f5640dabdda088105416e2fec88b7c1db02f4fcf8019a7ef7e4` | `b3e469d5fa1d4a74378dad432770c2d1f79bdd46b164eb299c06b3b79cf429aa` | `71e884520d666ec7ed01414fec9ebcd91e54a181818ca3c985ae997f3a0036d6`<br>`addf365cf38c920a697bfac3c999d52f3e63fb3d59639a1e0dbb4ca24c741b88` | Identical; stale `false` |
| `tests/fixtures/retype_model/instance_graph_snapshot.json` | `2d90df17a5b9a71afeb66d7114775826c26219ef33bb5bc9b698cc90cd1ceefb`<br>`507dff827408f43c2770be577623a2d696b5ff3d3ad0ad1c45b291467eea95ce` | `7eb23feb8b0ef9d2ad33a16564411eea2df7e42e38a393391eac7b6cb2ec110b`<br>`ff589fbc02c82f31af98b1287e24e3a7f7a5d14c35dbc1050ea33b3fd048c2b8` | `97860e4c8e54648dd7b7a8d62017409c78f9bc6be3377979af89292d93b67c1b` | `bb124ebb89638068c8eec78683f1b6164c8d0ca5cc0436759dcac4f28e06d464`<br>`9cb01588b80be95a7c8a0780a0de8c2cfc5773b37f3548c1a210e93658a3e8c0` | Identical; stale `false` |
| `tests/fixtures/sample_model/instance_graph_snapshot.json` | `f168bbffa8c252a84ed7a7ebea117ccc7247e61be68f65f579cd4135495523b5`<br>`b8c994533d4480eda363239d988ebf63b29cbfedf1a29287033b220fc54a8bcc` | `e87d5c7af7db93ed2182dd17d0778d7abcef631296b380c1b08b9990c784c894`<br>`318d9f716430482b573bfc9da8d8bcd8b801cbb45e5b12c15ed7d0d2c4d8aee4` | `904ff4a2d7689034e618af1272b6aa03ec4e84944f7299701697ecb8dc51d9ed` | `e76aa4ebdaf9d38d01c244fedfdf0f5d484949549abfc59b676956819f52e1e1`<br>`4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945` | Identical; stale `false` |
| `tests/fixtures/shadowed_reference/instance_graph_snapshot.json` | `1d4da393100ef1b68fc80902a8b50a2a32a9e07e94758ab7709f58940b27393c`<br>`3f1abcf02451348257ef435062c2c02d2e88376766f95120bc6b3516e5cc1d37` | `5f421469dbd58a59ccc7311d89dbaec1f1203539799c4fb875e17b3c6481baae`<br>`47ae83647889423b770eb585d2efb3cde557fe7f31db682479a5c99d11ca4821` | `2707cd1f5807d34a2ad2df8295b5354e56a9089fe7e4c3823044995e7f45cc97` | `a4d6de344b3042f1f133d547ff3d11def44428c7fa56414ad04d96564ba96dcc`<br>`98ca59c0139dd4643d23d254d9c3de1fcfff0f284ef1f22c6ce2000376e7d983` | Identical; stale `false` |
| `tests/fixtures/solar_battery_d5/instance_graph_snapshot.json` | `dc53520a94f0cd16742b449b69d06772ac904096cd1afa14ca83af709d973930`<br>`048547b38393bee5d2824b56f154b9cf4787f7a8b1376d0c3a3637d683a4af18` | `0944544f83ca540071d3dc749e4a1a174f733721f440a3fa02cec00954a80ac5`<br>`3f39ba1de89909671cf3792922061cd91937f7ecbbbf6f3668bb628eed4ec7a3` | `a33b740de5cdd619d33d519adad918fcfd3d8c0bbbc0c7c3f3581e8a0b733094` | `b4355a49867ac1cbe226a2a9ba2ecd6fe0648f3ecac7948dcd1a944491c4f8d3`<br>`4c65cd0dea1fa35702e1a203f926cfa53829faeae764cf8b6f54cbacf51ed289` | Identical; stale `false` |
| `tests/fixtures/unresolvable_attr_probe/instance_graph_snapshot.json` | `17494c69284e80aa0bd7a675c2dcd8d0f92774aee059bacf3b7d937d49069a4e`<br>`2c08e754d6cd1b113d83461398c44ce6aa8c8ad26df28ec885d08fc86e3522f9` | `1108b18382223c46a02f212473531c07391e0cb9877f4d6829961d856c14963a`<br>`8cac285b84d3faf79ed0944f84d444e37944a7b76605cd65d66c8762ac45dc02` | `edca1ee8d3473d7f31e48ac054638fb5fc46a17cbb40a477d2d1147fdd0e3395` | `f02de453a050ad2d81823a816517eb2e0f3dd318d56c53d983804a10e5fd0646`<br>`9c93ecb9d53577aee18a2805425aeff0ad2ab287d6b8c89c3c57609d3dfb8405` | Identical; stale `false` |
| `tests/fixtures/wi014_toy/instance_graph_snapshot.json` | `5caf02bca8169c693c364aab817683448dcfb4596e9cd86c11263d3062d82301`<br>`46e53534b06715bca2f70459ec61bf632d003b64ac902818d3c4d21132a1f061` | `0a00bcfd7061c4a4e753c85acb5be83e3ffe63d5b2e8aafdb24d1fe8ee4bf8b9`<br>`c6d4359f290df6ace5b0d5e6e9c753925ed54691ae1a6f5eb51f713afdd71f0f` | `3b58169c4c4f56b04206af8096036e51d49599a61ecf9aed28329941779d13fa` | `4ad1b28db5c4600ef0b35aed4d3cec1700071608d9188cfc5e3dd6586de6f5c4`<br>`a571b2ed51b5afe1a3436478935f275085e8e7e52eb637a1ab6c1172476b24fa` | Identical; stale `false` |

The stale set is empty, so the zero branch is final. No capture or `--recapture-reviewed` command
was run. No tracked snapshot or `tests/fixtures/v6_recapture_batch/batch.json` changed, and
`.project/active/unit-lane-port-metadata/v3-recapture.json` does not exist.

The license-free complete-inventory plus historical accepted-subset command was `python -m pytest
tests/conformance/test_v6_snapshot_inventory.py tests/conformance/test_v6_recapture_batch.py -q`.
It collected 68 and passed 68 in 0.83 seconds with zero other outcomes. The 8 inventory nodes prove
the complete 23-path set. The separate 60 accepted-batch nodes continue to cover their historical
15-path subset and are not treated as complete-set evidence.

### Final proof interface

The five exact Item 6-consumed nodes passed in the final focused gate:

| Exact node | Final claim |
|---|---|
| `tests/conformance/test_unit_lane_port_metadata.py::test_constraint_and_calculation_unit_agreement_projects_one_entry` | constraint `count` and calculation `pump_count` are exact `Dimensionless`; projection emits one `CATFMFEVacuum__catf_vacuum_pumping__n_pumps` entry with that text |
| `tests/conformance/test_unit_lane_port_metadata.py::test_constraint_and_calculation_unit_disagreement_refuses` | exact `cm` versus `m` refuses the whole projection with `ProjectionError`, `SI_RENDERING_COLLISION`, key `UnitLaneConstraintDisagreement__disagreement__shared_length`, and `conflicting projected metadata` |
| `tests/conformance/test_unit_lane_port_metadata.py::test_computed_and_calculation_unit_agreement_projects_one_entry` | computed and calculation inputs are exact `m`; projection emits one `CATFMFERadialBuild__catf_radial_build__plasma_region__inner_radius` entry with that text |
| `tests/conformance/test_unit_lane_port_metadata.py::test_computed_and_calculation_unit_disagreement_refuses` | exact `cm` versus `m` refuses the whole projection with `ProjectionError`, `SI_RENDERING_COLLISION`, key `UnitLaneComputedDisagreement__disagreement__shared_length`, and `conflicting projected metadata` |
| `tests/conformance/test_unit_lane_port_metadata.py::test_live_in_place_and_relocated_routes_preserve_unit_metadata` | all three parameterized cases preserve exact selected port IDs, complete `PortMetadata`, graph-v3 units, projected keys/text, and one-entry cardinality across live, in-place v6, and relocated v6 routes |

The A9 characterization now admits with constraint inputs `{observed: m³/s, count:
Dimensionless, each_capacity: m³/s, rel_tol: Dimensionless}` and calculation inputs
`{pumping_speed_total_in: m³/s, pump_count: Dimensionless, pump_capacity: m³/s}`. Its four
public lanes retain those exact strings. The radius characterization admits with computed inputs
`{inner_radius: m, thickness: m}` and calculation inputs `{r_inner: m, r_outer: m, r_major: m}`;
the three named public sources are exact `m`.

The four semantic-identity nodes also passed:

- `test_band_guard_base_formals_are_selected_from_definition_usages` proves the exact two non-empty
  slot/declaration UUID rows already recorded in Phase 3 and proves they are native loaded-user
  inputs matching the bound slots.
- `test_calc_redefinition_uses_selected_effective_formal_unit` proves base `cm`, redefining `m`,
  selected definition/formal identity, exact `m`, and no calculation `formal_provenance`.
- `test_constraint_redefinition_uses_selected_effective_formal_unit` proves base `cm`, redefining
  `m`, exact selected formal provenance, and exact `m`.
- `test_computed_alias_uses_referenced_declaration_unit` proves the expression port names the alias
  declaration (`m`) while its resolved edge reaches the aliased source (`cm`), and projection keeps
  the referenced declaration's exact `m`.

The direct `test_unit_text_and_missing_unit_remain_a_rendering_collision` node proves exact `m`
versus `None` still refuses `pkg__shared_length` with `SI_RENDERING_COLLISION`. The re-sealed load,
public capture no-create/no-replace, and CLI nodes prove envelope-owned certification and atomic
refusal. The CLI diagnostic is `SI_RENDERING_COLLISION` on
`UnitLaneConstraintDisagreement__disagreement__shared_length`, with no traceback and unchanged
sentinel bytes. `test_entry_point_unit_text_does_not_change_generated_schema_or_json` proves exact
production bytes and the sorted two-path output set are unchanged by `m` versus `cm` unit text.

### Final repository gates

All licensed commands exported the approved companion `.env`. Every licensed run below had zero
`no live syside license` skip lines and zero xfailed/xpassed outcomes.

| Gate | Exact pytest command | Exit | Collected | Passed | Skipped | Deselected | Failed | Errors | Disposition |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| First maintained final attempt | `python -m pytest tests/` | 1 | 2179 | 2061 | 34 | 79 | 5 | 0 | Found four direct-constructor compatibility regressions and one semantic-boundary regression; not accepted |
| Second maintained final attempt | `python -m pytest tests/` | 1 | 2179 | 2064 | 34 | 79 | 2 | 0 | Found and rejected a direct SysIDE enum import that broke the license-free route/import guard |
| Plan-prescribed focused interface | `python -m pytest tests/conformance/test_unit_lane_port_metadata.py tests/conformance/test_extractor.py tests/conformance/test_elaboration_projection.py tests/conformance/test_elaboration_graph_roundtrip.py tests/conformance/test_snapshot_v6_envelope.py tests/conformance/test_snapshot_v6_capture.py tests/conformance/test_cli_snapshot_refusal.py tests/conformance/test_entry_point_generation.py tests/conformance/test_v6_snapshot_inventory.py tests/conformance/test_v6_recapture_batch.py -q` | 0 | 244 | 244 | 0 | 0 | 0 | 0 | Genuine licensed pass |
| Expanded focused regression gate | same focused set plus `test_constraint_binding_unit_annotation.py`, `test_snapshot_v6_routes.py`, and `test_exact_pipeline_context.py` | 0 | 273 | 273 | 0 | 0 | 0 | 0 | Genuine licensed pass |
| Default maintained final | `python -m pytest tests/` | 0 | 2179 | 2066 | 34 | 79 | 0 | 0 | Genuine licensed pass |
| All-marker final | `python -m pytest tests/ -m ""` | 1 | 2179 | 2144 | 34 | 0 | 1 | 0 | Exact baseline failure set; zero new failures |
| Known node, plan command | `python -m pytest tests/execution/test_fusion_tea_real_teax.py::test_the_lane_runs_the_real_simkit` | 5 | 1 | 0 | 0 | 1 | 0 | 0 | Marker-deselected, as at baseline |
| Known node, isolated all-marker | same command plus `-m ""` | 0 | 1 | 1 | 0 | 0 | 0 | 0 | Genuine isolated pass |
| Complete inventory plus accepted subset | `python -m pytest tests/conformance/test_v6_snapshot_inventory.py tests/conformance/test_v6_recapture_batch.py -q` | 0 | 68 | 68 | 0 | 0 | 0 | 0 | 8 complete-set nodes plus 60 historical 15-path subset nodes |

The all-marker failing node remains exactly
`tests/execution/test_fusion_tea_real_teax.py::test_the_lane_runs_the_real_simkit`. Item 8 does not
claim to repair its collection-order behavior.

Static/diff results:

| Gate | Exact command | Exit | Final comparison |
|---|---|---:|---|
| Touched Python ruff | `python -m ruff check scripts/assess_v6_snapshot_churn.py src/sysml_codegen/cli/__init__.py src/sysml_codegen/elaboration/elaborate.py src/sysml_codegen/extraction/extractor.py src/sysml_codegen/extraction/feature_metadata.py src/sysml_codegen/orchestration/elaborated_pipeline.py src/sysml_codegen/snapshot/envelope.py tests/conformance/test_cli_snapshot_refusal.py tests/conformance/test_elaboration_projection.py tests/conformance/test_entry_point_generation.py tests/conformance/test_extractor.py tests/conformance/test_snapshot_v6_envelope.py tests/conformance/test_unit_lane_port_metadata.py tests/conformance/test_v6_snapshot_inventory.py` | 0 | 0 findings |
| Full-source ruff | `python -m ruff check src/` | 1 | Exact same 12 `UP042` findings as Phase 1; 0 added, 0 removed |
| Full-source mypy | `python -m mypy src/` | 1 | 52 errors in 11 files; 0 added and 3 pre-existing untyped duplicate extractor helpers removed versus the mechanically rerun 55-error baseline |
| Whitespace before freeze | `git diff --check` | 0 | 0 whitespace failures |

For the mypy comparison, the baseline commit was extracted read-only to a temporary directory and
the exact Phase 1 command was rerun there: 55 errors in 11 files over 71 source files. The final
command checks 72 source files and has 52 errors in the same 11 files. Normalizing unchanged
line-number movement leaves no added diagnostic; the removed findings are the old duplicate
extractor helper sites formerly at lines 608, 657, and 727. Ruff's full normalized diagnostic set
is byte-for-byte the same 12 class/code/path findings.

### Immutable freeze and Item 6 handoff

The reviewed implementation/test/fixture/inventory/verification freeze is commit
`62a07e5c870158672eb100f1cba73adfe4c9df28` (`Implement Item 8 unit-lane port metadata`). The
staged review contained 31 Item 8 paths and excluded the pre-existing `CURRENT_WORK.md` edit, every
tracked snapshot, the historical batch, Item 6 documentation, Item 7, Item 9, TEAx, graph/projector
and codec owners, companion repositories, and `main`. `git diff --cached --check` and the unstaged
`git diff --check` both passed immediately before the commit. Two trailing spaces found in the
previously approved Item 8 design during that freeze review were removed before the commit.

After the immutable SHA existed, the documentation-only handoff updated only:

- `.project/active/calcdef-constraint-gate-design/design.md`: R5, R8, and the component-manifest
  graph-v4 recapture entry;
- `.project/active/calcdef-constraint-gate-design/implementation-item.md`: status/start gate and
  exact dependency pin, Item 8 ownership gate, and Phase 4 recapture instruction.

Those records cite the full SHA, all five exact proof nodes and claims, both exact non-null
disagreement keys with `ProjectionError` / `SI_RENDERING_COLLISION`, the final sorted 23-path set
through this evidence bundle, exact pre/final equality, and zero v3 recaptures with no receipt.
They require Item 6 to re-derive its own pre/final tracked sets from Git and explicitly reject the
Item 8 count and historical 15-path batch as future scope authority. The handoff authorizes no
Item 6 production, calculation-input `formal_provenance`, graph-v4 capture, TEAx work, or commit.

Final documentation/handoff command `git diff --check` exited 0 with zero whitespace errors. Final
`git status --short --branch` showed only seven documentation paths: Item 8 plan/spec/verification,
the two named Item 6 records, the epic Item 8 tracking record, and `CURRENT_WORK.md`. No source,
test, fixture, snapshot, batch, Item 9 model, Item 7 documentation, TEAx, companion, or `main` path
was present.

## Deviations and premise conflicts

- The plan's isolated-node command inherited the default `not execution` marker and selected zero
  tests. The evidence record preserves that exit-5 attempt and adds the necessary `-m ""` run; the
  node then passed.
- The managed sandbox initially prevented hard-coded execution-lane scratch directories outside
  the workspace. The invalid 13-error run is preserved above. The approved rerun with the needed
  filesystem access had zero errors and reproduced the single recorded collection-order failure.
- The approved spec's `captured_at` example is inapplicable to deterministic v6, as already surfaced
  in the approved design. No field or marker was added.
- The first two final maintained-suite attempts exposed seven failures across two runs rather than
  being treated as baseline noise. The corrections kept direct `_ExactElaborator` construction
  compatible, limited definition-formal expansion to typed-definition constraints, added the three
  required oracle records for the new constraint fixtures, and compared direction through its own
  enum class without a direct SysIDE import or rendered-string selector. The focused regressions,
  no-license snapshot generation node, import guard, semantic-boundary guard, final census, and all
  repository gates were rerun after production settled.
