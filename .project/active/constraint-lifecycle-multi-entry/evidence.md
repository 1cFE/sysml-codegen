# Evidence: Multi-Entry Candidate Bridge (Lifecycle Item 9)

**Status:** Implementation complete; stop for independent audit.
**Date:** 2026-07-20
**Owner:** Reid W
**Candidate revs (pre-commit at write time):** codegen `589c8c4` (untouched), teax working tree on
`0a49b89`, fusion-tea working tree on `8eb010f4`. Commit hashes recorded in §7 after commit.

Item 9 is TEAx-owned: the deliverable code lives in `/home/reid/1cfe/teax` and
`/home/reid/1cfe/fusion-tea`; the spec/design/evidence live here for register continuity
(epic row 11 / CE-F2).

---

## 1. What landed

The stock TEAx bridge now builds a complete typed mapping for **zero, one, or many** entry channels,
and fusion's consumer wrappers are deleted. The evaluate seam is unchanged (it was already
multi-channel); all work is in the bridge/definition/config plus the runner failure-switch
relocation.

**teax** (`packages/teax-simkit/simkit/`):
- `study/bridge.py` — `CandidateBridge(entry_models)`: partitions candidate fields to owning channels
  via `model_fields`, builds a complete typed model per channel over its own defaults, fails closed
  (`EvaluationFailed(ENTRY_VALIDATION)`) on unknown/malformed fields, and raises at construction on a
  field two channels declare (A2 guard).
- `study/runner.py` — bridge built from `definition.entry_models`; **`bridge.build` relocated inside
  the failure switch (R1)** so a field-level bridge failure is recorded as `StudyBridgeDefect`, not
  an uncaught crash.
- `study/definition.py` — scalar `entry_channel`/`entry_model` replaced by `entry_models` map.
- `study/config.py` — scalar `entry_channel`/`entry_model` deleted from `StudyConfig`, from the
  study fingerprint, and from `build_definition` (which now carries `evaluator.entry_models`).

**fusion-tea** (`exploration/ife_e2e/study/`):
- `run_viability_study.py` — `MultiChannelEvaluator` **deleted**; study wired to the stock bridge
  (`StudyDefinition(entry_models=prepared.entry_models)`, plain `PreparedEvaluator`).
- `prove_catalog_seam.py` — its own `ThreeChannelEvaluator` wrapper **deleted** (R3 migration off the
  config scalars); uses the stock bridge.
- `bench_prepare_once.py` — off `MultiChannelEvaluator` and the removed `ife_hif.yaml`; uses the
  stock bridge + `pipeline.yaml`.
- `findings.md` — R4 resolution note on the stale multi-channel-gap finding.

---

## 2. Phase 0 — codegen gap found and routed (not shimmed)

A3 ("codegen emits one EntryPoint even at zero channels") was **falsified** against the real CLI. A
minimal zero-entry model generates a package with a real module + ExitPoint but **no EntryPoint**
(`pipeline_yaml.jinja2:11` gates it behind `{% if entry_points %}`), and stock TEAx rejects it:

```
$ entry_point_validate(".../zero_channel/pipelines/pipeline.yaml")
REJECTED: ValidationError -> Pipeline must declare exactly one EntryPoint module
```

Per A3 discipline this **routes to codegen — no TEAx shim** (no relaxed validator, no fake fixture).
Full finding + reproduction model: `codegen-gap-zero-entry.md`, `evidence/zero_entry_model/`. Item 9
proves the **zero bridge shape** at the unit level instead (see §4); the end-to-end zero *package*
coordinate is parked on the codegen fix (candidate owner: Item 13 / a codegen fixup).

## 3. RED-first (R1)

With `bridge.build` outside the runner's failure switch, the malformed-mapping and unknown-field
runner tests fail with an **uncaught `EvaluationFailed`** escaping the runner — proving the call
site, not the exception type, is the defect:

```
FAILED test_malformed_mapping_is_recorded_classified_failure
FAILED test_bridge_defect_is_loud
  E  simkit.evaluation.failure.EvaluationFailed: entry_validation: Unknown entry field ... (bridge.py:57)
```

After relocating `bridge.build` inside the `try` (R1 fix), both are GREEN
(`StudyBridgeDefect`, no case committed).

## 4. Acceptance coordinates

| shape | coordinate | result |
|---|---|---|
| **many** | real 3-channel IFE package (`generated/`), eta in `ife_plant_params` + gain in `hif_plant_params` | **2301/2301 cases** carry a verdict; 100% agreement vs the retiring hand rule (7 boundary rows flagged); no wrapper. `run_viability_study.py` exit 0. |
| **one** | toy single-channel fixture (`sealed_package`) | bridge builds + validates completely (`test_bridge_one_*`). |
| **zero (bridge shape)** | empty channel set | `CandidateBridge({}).build({}) == {}`; `MappingEntrySource(expected_types={}).validate({})` passes (`test_bridge_zero_channels_builds_empty_mapping`). |
| **zero (end-to-end package)** | — | **blocked on codegen gap (§2), routed.** |

Field-level fail-closed (both A1 arms + guards), all GREEN:
- unknown field → `ENTRY_VALIDATION` (`test_bridge_unknown_field_fails_closed`)
- malformed value → `ENTRY_VALIDATION` (`test_bridge_malformed_value_fails_closed`)
- defaultless required field unselected → `ENTRY_VALIDATION`, never invented
  (`test_bridge_defaultless_unselected_field_fails_closed` — A1 arm 2)
- fully-defaulted baseline builds (`test_bridge_one_defaults_unselected`, IFE 2301-point run — A1 arm 1)
- ambiguous field across channels → construction-time raise (`test_bridge_ambiguous_field_across_channels_fails_at_construction` — A2)
- no unrelated channel omitted (`test_bridge_many_omits_no_unrelated_channel` — invariant 47)
- ordinary design input supplied via its channel default, never "missing" (falls out of the complete
  baseline; IFE run supplies all three channels).

## 5. Batteries

- **teax full simkit suite:** `298 passed in 12.70s` (agentic-mbse venv + teax-simkit on path).
- **teax study+evaluation focused:** 121 passed.
- **R5 store no-silent-rebind:** `test_compatibility.py` + all compat/rebind/fingerprint/resume
  tests GREEN — the dropped `entry_channel`/`entry_model` fingerprint keys start a new lineage, never
  a silent rebind. The study's channel/model binding is carried by `model_contract_fingerprint`.
- **teax ruff:** clean on all changed files. **teax mypy:** zero errors added in the four changed
  source files (the 17 errors mypy reports are pre-existing baseline in `config/`+`core/`, none in
  `study/bridge|config|definition|runner.py`).
- **fusion seam proof:** `prove_catalog_seam.py` GREEN — schema 2.0.0, 1 eligible entry, def→usage
  join `fusion_cycle::'Viability Threshold'`, verdict satisfied (Item-8 seam intact).
- **fusion study:** `run_viability_study.py` GREEN (2301/2301, exit 0). `bench_prepare_once.py`
  compiles and uses the same stock bridge+evaluate path the two green runs exercise.
- **codegen:** source **untouched** (`git status` shows no `src/`/`templates/` changes); only
  `.project/` artifacts + the zero-entry probe model.

## 6. Deletion inventory verified gone (no shim)

- `MultiChannelEvaluator` (fusion `run_viability_study.py`) — deleted.
- `ThreeChannelEvaluator` (fusion `prove_catalog_seam.py`) — deleted.
- `bench_prepare_once.py` use of the wrapper + `ife_hif.yaml` — gone.
- single-channel `CandidateBridge(channel_name, entry_model)` — replaced by `CandidateBridge(entry_models)`.
- `StudyDefinition.entry_channel`/`entry_model`, `StudyConfig.entry_channel`/`entry_model`, the
  `getattr(evaluator.package, config.entry_model)` resolution, and the two fingerprint keys — deleted.
- No parallel authority or compatibility route replaces them; the stock bridge owns the public path.
- Residual `MultiChannelEvaluator`/`ife_hif`/`hif_driver_params` strings remaining anywhere in the
  live fusion study dir: only the R4 resolution note in `findings.md` (historical record) — no code.

## 7. Success criteria (spec)

- [x] Zero/one/multiple mappings validate completely; no unrelated channel omitted (zero end-to-end
      package parked on the codegen gap, §2).
- [x] Candidate overrides change only selected typed fields.
- [x] Stock TEAx replaces the fusion wrapper through public APIs (2301-point study green, no wrapper).
- [x] Single-entry duplicate paths consolidated/deleted; stock TEAx owns the public route.

## 8. Open / carried forward

- **Codegen zero-entry-EntryPoint gap** (§2) — routed, owner TBD (Item 13 or a codegen fixup).
- Item 9 does not touch the `FileBackedEvaluator` route (Item 11) or constraint-free report
  semantics (Item 11 firewall).

Commit hashes (Item 9): teax `96578a4`, fusion-tea `2422e715` (branch item8-fusion-embedded-catalog), codegen artifacts `0f20e09`. Codegen source-pin candidate unchanged at `589c8c4` (source untouched).
