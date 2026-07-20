# Design: Multi-Entry Candidate Bridge (Lifecycle Item 9)

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-07-20
**Spec:** `.project/active/constraint-lifecycle-multi-entry/spec.md`
**Repo (deliverable):** `/home/reid/1cfe/teax` (TEAx-owned); artifacts tracked here for register
continuity. Chain pinned: codegen `589c8c4`, teax `0a49b89`, fusion-tea `8eb010f4`.

Phased plan folded in (§7). All TEAx paths are relative to
`teax/packages/teax-simkit/simkit/`.

---

## 1. The frame

One structural fact from reconnaissance sets the whole design: **the evaluate boundary is already
multi-channel.** `PreparedEvaluator.evaluate` takes a `Mapping[str, BaseModel]` over an arbitrary
channel set (`evaluation/evaluator.py:125,31`); `MappingEntrySource.validate` already computes
missing / extra / wrong-typed over the full expected channel set (`evaluation/entry_source.py:42-70`);
and `PreparedEvaluator.entry_models` (`evaluator.py:120`) already exposes the authoritative
`channel → model` map, "derived from the pipeline spec at prepare time — never a hardcoded generated
class name."

So the work is not to teach TEAx about multiple channels. It is to stop the layer *above* the
evaluate seam from collapsing to one. That layer is the bridge, plus the two definition/config
fields that feed it. The plan changes three files and deletes a consumer wrapper; it does not touch
the evaluator, the entry-source, or the executor.

Keep the two single-entry assumptions apart, because only one is a target:

- **Single entry *channel*** (target): `CandidateBridge` builds one model; `StudyDefinition` /
  `StudyConfig` carry one channel name and one model type.
- **Single entry *module*** (not a target): `core/pipeline_validator.py:83-87` requires exactly one
  `EntryPoint` module. IFE has one module emitting three channels, so this gate is correct and
  stays.

---

## 2. Architecture in one picture

```
StudyConfig(grid, fixed)               # flat field→value namespace; NO entry_channel/entry_model
        │  build_definition(config, prepared)
        ▼
        │  entry_models = prepared.entry_models          # {channel: ModelClass}  (evaluator.py:120)
        ▼
StudyDefinition(entry_models=…)        # carries the map, not a scalar channel/model
        │  StudyRunner.__init__
        ▼
CandidateBridge(entry_models)          # multi-channel
        │  build(selected_fields) →  {channel: Model(**owned_subset)  for every channel}
        ▼                                partition by model_fields ownership; unselected → defaults
PreparedEvaluator.evaluate(mapping)    # UNCHANGED — validate() checks channel keys/types, then runs
```

The bridge produces the complete channel-keyed mapping the evaluate seam already expects. Because
the bridge builds *from* `entry_models`, the mapping's key set is structurally equal to the expected
set — so `MappingEntrySource`'s missing/extra channel check can never trip for the stock path, which
is exactly the "no unrelated channel omitted" guarantee (contract invariant 47).

---

## 3. Key decisions (settling the spec's Open Questions with code evidence)

### D1 — Baseline source is the typed model's own field defaults

**Decision:** A channel's complete baseline is `ModelClass()`. The bridge builds every channel's
model with the candidate's owned fields applied over that default baseline; unselected fields, and
whole unselected channels, keep the model's own defaults.

**Evidence:** Every field on every generated entry model carries a Pydantic default —
`hif_plant_pkg__hif_plant__gain: float = Field(default=80.0, …)` and so on across all 27 IFE fields
(`fusion-tea/exploration/ife_e2e/generated/schemas/{hif_plant_params,ife_plant_params,system_design}.py`).
The stock bridge docstring already promises this: "A field the candidate does not select keeps the
entry model's own modeled default" (`study/bridge.py:16-18`).

**What this deletes:** the fusion wrapper's out-of-band read of committed `inputs/*.json` templates
(`run_viability_study.py:83-93`). The typed model *is* the baseline; nothing reads template files.

**Rejected alternative:** catalog `parameters[*].default_value` (also present, also complete). Not
chosen — it introduces a second baseline authority parallel to the model the bridge actually
constructs and the entry-source actually validates against. The model defaults are the same numbers
with no drift surface.

### D2 — Channel partition is by model-field ownership, not catalog `param_group`

**Decision:** For each selected field name, route it to the channel whose model declares that field,
using `entry_models` (`evaluator.py:120`) and each model's Pydantic `model_fields`. Build each
channel's model from its owned subset. Fail closed when a selected field is owned by **no** channel
(unknown field) or by **more than one** (ambiguous).

**Evidence / why this over the catalog:** `entry_models` and `model_fields` are the executable truth
of what channels exist and which model owns which field — the exact objects the bridge constructs and
the entry-source validates. The catalog also carries the partition (`parameters[*].param_group` =
channel name; IFE groups exactly `hif_plant_params:5 / ife_plant_params:8 / system_design:14`), but
consuming it would mean surfacing `parameters` on `ModelContractData` (`study/model_contract.py:27-38`
does not today) and trusting a description that could drift from the models. Composing with the
Item-8 seam still happens — for identity/compatibility (`_model_contract_fingerprint` at
`study/config.py:86`) — just not for partition. This honors "prefer extending existing types over
new layers": no new `ModelContractData` field, no `param_group` reader.

**Safe because** entry-model field names are globally unique PQNs
(`hif_plant_pkg__hif_plant__driver__meier_cost__beam_energy_mj`, …), so ownership is unambiguous for
real packages; the >1-owner branch is a fail-closed guard, not an expected path (assumption A2).

### D3 — Config stays flat; the scalar channel/model fields are deleted

**Decision:** `StudyConfig.grid` / `fixed` stay a flat field→value namespace (no channel
qualification). Delete `StudyConfig.entry_channel` / `entry_model` (`config.py:51-52`) and
`StudyDefinition.entry_channel` / `entry_model` (`definition.py:34-35`). `build_definition` stops
doing `getattr(evaluator.package, config.entry_model)` (`config.py:115`) and instead carries
`prepared.entry_models` onto the definition.

**Evidence:** field names are globally-unique PQNs (D2), so a flat namespace routes to channels
without a config schema change; and the scalar fields have no remaining consumer once the bridge
builds from `entry_models`. Keeping them would be the "duplicate single-entry path" the success
criterion says to delete.

**Consequence — fingerprint basis:** `config.semantic_fingerprint` digests `entry_channel` /
`entry_model` today (`config.py:63-64`). Replace those two keys with the `entry_models` identity
(sorted channel names + model class names) so the study-definition fingerprint stays meaningful and
richer. This changes the fingerprint, i.e. a new store lineage — safe because the stores are
pre-release (consistent with Item 8's store-transition ruling: no migration, archival invariant
covers old lineage). Assumption A4.

### D4 — Validation split: field-level in the bridge, channel-level unchanged in the entry-source

**Decision:** Two validation sites, both before evaluation:

- **Channel-level** (missing / extra channel key, wrong-typed model) stays in
  `MappingEntrySource.validate` (`entry_source.py:42-70`) — unchanged, now genuinely driven over
  many channels.
- **Field-level** (unknown field name; malformed field value inside a model) moves into the bridge.
  `Model(**subset)` raising `pydantic.ValidationError`, and the "field owned by no channel" case,
  are caught in the bridge and re-raised as `EvaluationFailed(EvaluationPhase.ENTRY_VALIDATION, …)`.

**Evidence — the gap being closed:** today `bridge.build` does a bare `entry_model(**selected_fields)`
(`bridge.py:26`) and is called at `runner.py:94` *outside* the runner's failure switch
(`runner.py:95-102` catches only `EvaluationFailed`). A malformed field therefore propagates as an
uncaught `pydantic.ValidationError` instead of a classified case. Raising `EvaluationFailed` from the
bridge routes it through the existing switch to `StudyBridgeDefect` (`runner.py:111-112`) with no new
failure type — reusing the taxonomy already exercised by
`tests/evaluation/test_failure_taxonomy.py`.

### D5 — Ordinary declared design inputs are structurally never "missing producers"

**Decision:** No special-casing. Because the bridge emits **every** channel (defaults for unselected
fields and unselected channels, D1), a declared design-attribute input the candidate doesn't override
is still supplied through its channel. The spec's risk locus — `missing = expected − supplied` at
`entry_source.py:44-52` — is eliminated because the stock bridge makes `supplied ⊇ expected` by
construction. This falls out of D1+D2; the design records it as a guarantee, and Phase 5 pins it with
a test (a design-attribute-only candidate over the IFE package still validates).

### D6 — Delete the fusion wrapper; the study builds the stock bridge

**Decision:** Delete `MultiChannelEvaluator` from `fusion-tea/.../study/run_viability_study.py`
(class at `:68`) and its second consumer `study/bench_prepare_once.py` (imports/uses at `:17,37,61`;
also repoint or delete its stale `pipelines/ife_hif.yaml` references). The study wires
`StudyRunner`'s bridge straight from `prepared.entry_models`; the `Evaluator` seam it plugs into is
unchanged. Deletion, not a shim — no wrapper survives.

---

## 4. The multi-channel `CandidateBridge`

```python
class CandidateBridge:
    def __init__(self, entry_models: Mapping[str, type[BaseModel]]) -> None:
        self._entry_models = entry_models
        # field name -> owning channel; fail closed on a field two channels declare.
        self._owner: dict[str, str] = _index_fields(entry_models)   # raises on ambiguity (A2)

    def build(self, selected_fields: Mapping[str, Any]) -> dict[str, BaseModel]:
        by_channel: dict[str, dict[str, Any]] = {ch: {} for ch in self._entry_models}
        for name, value in selected_fields.items():
            channel = self._owner.get(name)
            if channel is None:
                raise EvaluationFailed(EvaluationFailure(
                    phase=EvaluationPhase.ENTRY_VALIDATION,
                    cause=f"Unknown entry field {name!r} (declared by no channel)"))
            by_channel[channel][name] = value
        try:
            return {ch: model(**by_channel[ch])            # unselected fields/channels -> defaults
                    for ch, model in self._entry_models.items()}
        except ValidationError as err:                      # malformed field value
            raise EvaluationFailed(EvaluationFailure(
                phase=EvaluationPhase.ENTRY_VALIDATION, cause=str(err))) from err
```

Behavior across the three shapes:

| shape | `entry_models` | `build({})` result | validate outcome |
|---|---|---|---|
| zero | `{}` | `{}` | passes: nothing missing, nothing extra |
| one | `{c: M}` | `{c: M()}` | passes |
| many (IFE) | 3 entries | 3 complete models | passes: all three channels present |

`_index_fields` and `_owner` use Pydantic `model_fields` (the same models the evaluator validates
against), so partition and validation never disagree.

---

## 5. Load-bearing assumptions (stated, verified where cheap, else pinned to a phase)

- **A1 — every entry-channel field has a default.** Verified for IFE (all 27 fields). Rests on
  ADR-001: every entry-point kind (`LIBRARY_DEFAULT`, `DESIGN_ATTRIBUTE`, `USAGE_LITERAL`) carries a
  value, so codegen always emits a Pydantic default. If a field ever lacks one, `Model()` raises and
  the bridge surfaces it as a fail-closed baseline error (a `PREPARATION`/`ENTRY_VALIDATION` failure),
  never a silent zero. Phase 2 asserts the IFE baseline is buildable from defaults.
- **A2 — entry-model field names are globally unique across channels.** Verified for IFE. The bridge
  guards the general case: two channels declaring one field name is a construction-time fail-closed
  error (`_index_fields`). Phase 2 covers this branch with a synthetic two-channel collision.
- **A3 — codegen emits exactly one `EntryPoint` module even at zero channels.** Required by
  `pipeline_validator.py:83-87` and by `MappingEntrySource.from_spec`'s `next(m … is_entry)`
  (`entry_source.py:30`), which raises `StopIteration` if none exists. **Verified in Phase 0 by
  generating the fixture through the real CLI and inspecting the pipeline.** If the real tool instead
  emits *no* `EntryPoint` for a zero-channel model, that is a codegen finding routed to its owner
  (not worked around in TEAx) — discovered against the tool, not assumed away.
- **A4 — the Item-8 seam and `entry_models` remain the identity/model authorities.** No new
  `ModelContractData` field is added; the store fingerprint change (D3) starts a new pre-release
  lineage rather than migrating.

Scope note: the `FileBackedEvaluator` route (`evaluator.py:193`, `evaluate(entry_json_path: Path)`)
is a different input path and is **not** in scope — file-backed evaluation durability is Item 11.
The bridge feeds the `PreparedEvaluator` route only.

---

## 6. Deletion inventory (what this obsoletes — deletion, not shim)

| deleted | location | replaced by |
|---|---|---|
| single-channel `CandidateBridge(channel_name, entry_model)` | `study/bridge.py:21-26` | `CandidateBridge(entry_models)` |
| `StudyDefinition.entry_channel` / `entry_model` | `study/definition.py:34-35` | `entry_models` map |
| `StudyConfig.entry_channel` / `entry_model` + single `getattr` | `study/config.py:51-52,115` | `prepared.entry_models` in `build_definition` |
| `entry_channel`/`entry_model` in the fingerprint payload | `study/config.py:63-64` | `entry_models` identity |
| fusion `MultiChannelEvaluator` | `run_viability_study.py:68-97` | stock bridge from `prepared.entry_models` |
| second consumer + stale `ife_hif.yaml` refs | `bench_prepare_once.py:17,36,60` | stock bridge / `pipeline.yaml` |

No parallel authority or compatibility route may replace them (epic simplification mandate; no LOC
metrics — see [[loc-gates-retired-simplicity-qualitative]]).

---

## 7. Phased plan (RED-first)

**Phase 0 — Author the zero-entry-channel fixture (codegen-generated, committed).**
- Author a minimal SysML model whose package has **no entry channels** — a computation/constraint
  with no unbound entry-point parameters (all operands internally produced or literal). Commit the
  `.sysml` source.
- Generate the package through the **real CLI** (`sysml-codegen generate --models <model>
  --output <fixtures>/zero_channel/package_live --package-name zero_channel`; the `generate`
  subparser is `sysml-codegen/src/sysml_codegen/cli/__init__.py:846-862`), following the existing
  fixture convention: committed `package_live/` tree plus a `generate_fixture.py` regen script, as
  `tests/evaluation/fixtures/f1_arithmetic/` does.
- **Inspect the generated `pipelines/pipeline.yaml`: confirm exactly one `EntryPoint` module with
  zero channel outputs** (A3). If the tool emits none, stop and route a codegen finding.
- Note the "one" coordinate (an existing single-channel spike, e.g. `codegen_chain_spike`) and the
  "many" coordinate (the real IFE `generated/` package) — commit/reference as fixtures per the same
  convention.

**Phase 1 — RED.** Tests that drive zero / one / many through the *stock* bridge and fail at the
pinned chain: the current single-channel bridge omits IFE's other two channels (→ `ENTRY_VALIDATION`
missing), and the fusion wrapper raises `AttributeError` on the regenerated package. Capture the
failures. Extend `tests/study/test_bridge.py` (today single-channel only) with zero/one/many cases.

**Phase 2 — Multi-channel bridge.** Implement §4: construct from `entry_models`; partition by
`model_fields` ownership; defaults baseline; field-level validation raising `EvaluationFailed`.
Unit-cover: many (3 IFE models built, only selected fields changed), one, zero (`{}`), unknown
field, malformed field, and the A2 two-channel collision guard.

**Phase 3 — Definition/config consolidation.** Replace the scalar `entry_channel`/`entry_model` with
`entry_models` on `StudyDefinition`; `build_definition` carries `prepared.entry_models`
(`config.py:110-135`); update the fingerprint basis (D3). Delete the dead scalar fields and the
single `getattr`. Adjust `tests/study/conftest.py` scaffolding and fingerprint-sensitivity tests.

**Phase 4 — Delete the fusion wrapper, wire the study to stock TEAx.** Remove `MultiChannelEvaluator`
and the `bench_prepare_once.py` usage (D6); the IFE study builds the runner's bridge from
`prepared.entry_models`. Run the IFE viability study end to end through public APIs — GREEN, no
wrapper.

**Phase 5 — Validation + guarantee coverage, regression.** Pin the four validation shapes
(missing/extra channel via entry-source; malformed/unknown field via bridge) and the D5 guarantee
(design-attribute-only candidate over IFE still validates; ordinary input never reported missing).
Run the TEAx suite (`tests/study/`, `tests/evaluation/`) plus lint/type; confirm the deletion
inventory (§6) is gone, not shimmed.

---

## 8. Risks

| risk | mitigation |
|---|---|
| The real CLI won't emit a one-`EntryPoint`/zero-channel package (A3) | Phase 0 generates and inspects before any code change; a codegen gap is routed to its owner, not shimmed in TEAx. |
| A non-IFE package has a field with no default (A1) | Bridge fails closed on `Model()` construction rather than inventing a value; pinned by a Phase-2 assertion. |
| Field-name collision across channels in some future package (A2) | `_index_fields` fail-closed guard + a synthetic collision test; not silently resolved by first-pick. |
| Fingerprint change strands a store (D3) | Pre-release stores; new lineage is the intended behavior (Item 8 store ruling), documented in evidence. |
| Deletion leaves a hidden single-entry assumption | §6 inventory is checked for absence in Phase 5; the epic's no-parallel-route mandate applies. |

---

## Related Artifacts

- **Spec:** `.project/active/constraint-lifecycle-multi-entry/spec.md`
- **Epic:** `.project/backlog/epic_constraint_execution_lifecycle_remediation.md` (Item 9, row 11)
- **Contract:** `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md`
  (invariants 26, 47; acceptance rows `:455`, `:457`; register row 11 `:519`)
- **Item-8 seam:** `.project/active/constraint-lifecycle-catalog-store/` (`load_model_contract`)
- **Real package (many):** `fusion-tea/exploration/ife_e2e/generated/`
- **Counterexample:** `fusion-tea/.../study/run_viability_study.py:68`, `study/bench_prepare_once.py`

---

**Next Steps:** Independent `/_my_design_review` in a fresh session, then `/_my_plan` (or execute the
phased plan folded in above).
