# Spec: Multi-Entry Candidate Bridge (Lifecycle Item 9)

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-07-20
**Complexity:** MEDIUM
**Branch:** constraint-exec-epic

Epic authority: `epic_constraint_execution_lifecycle_remediation.md`, Item 9 / register row 11
(absorbs backlog CE-F2). **TEAx-owned** item; artifacts live in this repo for register continuity,
deliverable code lands in `/home/reid/1cfe/teax`. Chain pinned for this spec: codegen `589c8c4`,
teax `0a49b89`, fusion-tea `8eb010f4` (branch `item8-fusion-embedded-catalog`).

This spec inventories first and specifies second: the single-entry-assumption inventory below is
file:line-grounded because a missed assumption becomes a broken deletion.

---

## Problem

TEAx's study bridge can only feed a candidate to a package that has **exactly one** entry channel.
A real package has more than one, and today the gap is patched by a consumer-side wrapper that has
already gone stale and stopped running.

Three facts define the problem:

1. **The stock bridge is single-channel by construction.** `CandidateBridge.build` returns a
   one-key mapping — `{self.channel_name: self.entry_model(**selected_fields)}`
   (`teax .../study/bridge.py:25-26`). It cannot express many channels (several typed models with
   the candidate's fields partitioned across them) or zero channels (an empty complete mapping).
   The single-channel shape is duplicated up through the definition and config layers
   (`study/definition.py:34-35`, `study/config.py:51-55`).

2. **The real package needs three channels.** The regenerated IFE package
   (`fusion-tea/exploration/ife_e2e/generated`) declares one `EntryPoint` module `entry_fusion`
   emitting **three** typed channels — `hif_plant_params`/`HifPlantParams` (5 fields),
   `ife_plant_params`/`IfePlantParams` (8 fields), `system_design`/`SystemDesign` (14 fields)
   (`generated/pipelines/pipeline.yaml:12-17`). The stock bridge builds one; the evaluator's
   entry-source then rejects the run because two channels are missing.

3. **The consumer wrapper that bridged the gap is now the live counterexample.** Fusion's
   `MultiChannelEvaluator` (`fusion-tea/.../study/run_viability_study.py:68`) loaded the
   non-swept channels out-of-band from committed JSON templates and merged them in
   (`merged = {**self._fixed_channels, **typed_inputs}`, lines 95-97). Item 8's IFE regeneration
   collapsed the entry decomposition from four groups to three and removed `hif_driver_params`.
   The wrapper still hardcodes the four-group shape — `package.HifDriverParams(...)` and
   `inputs/hif_driver_params.json` (lines 84-85) — so its `__init__` now raises `AttributeError`
   on the current package and the study's full sweep does not run. An Item-9 breadcrumb marks it
   for deletion (lines 73-78, fusion commit `d7f7492d`). A second consumer,
   `study/bench_prepare_once.py`, imports the same class and points at the removed
   `pipelines/ife_hif.yaml` (lines 17, 36, 60) — stale for the same reason.

The cost: a real study cannot run through public TEAx seams, and the only thing that made it run
was a hand-rolled wrapper that duplicates entry-channel knowledge, guesses defaults from template
files, and breaks silently whenever codegen re-decomposes the entry groups. The owner's decision:
the stock bridge constructs complete typed mappings for zero, one, or many entry channels itself,
and the wrapper is deleted.

### The structural fact that scopes the work

The evaluate boundary is **already** multi-channel. `Evaluator.evaluate` takes a
`Mapping[str, BaseModel]` over an arbitrary channel set (`evaluation/evaluator.py:30-31`);
`MappingEntrySource.validate` already computes missing/extra/wrong-typed over the full expected
channel set (`evaluation/entry_source.py:44-66`); `PreparedEvaluator.entry_models` already exposes
the complete `channel → model` map (`evaluation/evaluator.py:119-123`). The single-channel collapse
happens entirely *above* this seam. **Item 9's work is concentrated in the bridge, definition, and
config; the evaluate seam does not change.**

Keep two distinct assumptions separate:

- **Single entry *channel*** (the target) — bridge/definition/config assume one channel, one model,
  one flat field set.
- **Single entry *module*** (not the target) — the pipeline layer hard-requires exactly one
  `EntryPoint` module (`core/pipeline_validator.py:83-87`). IFE has one module emitting three
  channels, so this gate is correct and stays. Do not collapse it.

---

## Success Criteria

Outcomes, testable. Acceptance coordinates follow the epic's row-11 line and the contract's row 11
(`constraint-execution-lifecycle-contract.md:519`) and acceptance row
(`...:457`, "Zero/one/multiple typed channel mappings validate completely").

- [ ] **RED first.** A test drives the real three-channel IFE package (`generated/`) through the
      stock TEAx bridge and fails at the pinned chain before any production change — the current
      bridge omits two channels, or the fusion wrapper raises. The failure is captured, not
      narrated.
- [ ] **"Many" validates and runs.** The stock bridge builds a complete typed mapping for all three
      IFE channels (`HifPlantParams`, `IfePlantParams`, `SystemDesign`); the IFE viability study
      runs green end to end through public TEAx APIs with no consumer wrapper.
- [ ] **"One" validates.** A single-entry-channel package bridges and validates completely through
      the same stock path (a single-channel spike package exists in fusion-tea, e.g.
      `codegen_chain_spike`; `exp_toy`).
- [ ] **"Zero" validates.** A zero-entry-channel shape produces a complete (empty) mapping and
      validation passes with nothing missing and nothing extra. **The concrete coordinate for this
      case is unresolved — see Open Questions.**
- [ ] **Baseline + override.** Every channel gets a complete typed baseline; a candidate changes
      only its selected fields and omits no unrelated channel (contract invariant 47).
- [ ] **Validation before evaluation.** Missing, extra, malformed (bad field *inside* a model), and
      wrong-typed channel mappings are rejected as a graceful, classified failure before evaluation
      — not as an uncaught `pydantic.ValidationError` from `bridge.build`.
- [ ] **Ordinary design inputs are not missing producers.** A declared design-attribute input is
      supplied as its ordinary typed entry channel, never reported as a missing channel/producer.
- [ ] **Wrapper deleted, not shimmed.** Fusion's `MultiChannelEvaluator` and its second consumer
      (`bench_prepare_once.py`) are removed; the stock bridge owns the public route. Single-channel
      duplicate paths in bridge/definition/config are consolidated, not layered behind a guard.

---

## Known Requirements

### Structural constraints (forced by the existing code and the real package)

- **[HARD]** The evaluate boundary is fixed and already multi-channel: `evaluate(Mapping[str,
  BaseModel])` (`evaluation/evaluator.py:30-31`) and `MappingEntrySource.validate`
  (`entry_source.py:44-66`). The bridge must produce a complete channel-keyed mapping; the solution
  does not change the evaluate seam.
- **[HARD]** The IFE "many" package declares exactly three channels through one `EntryPoint` module
  (`generated/pipelines/pipeline.yaml:12-17`). Any mapping the bridge builds must carry all three
  or `MappingEntrySource` raises `ENTRY_VALIDATION` for the missing channels.
- **[HARD]** The one-`EntryPoint`-module gate (`core/pipeline_validator.py:83-87`) is a real
  invariant and is preserved. "Multi-entry" means multiple channels from that one module, not
  multiple entry modules.
- **[HARD]** The channel-partition and per-field baseline data the bridge needs already exists in
  the embedded catalog and is parsed by the Item-8 seam, but is **untapped**: `model_contract.json`
  carries `parameters[*]` with `param_group` (= entry channel name), `entry_type`, and
  `default_value` — for IFE, 27 fields grouped exactly `hif_plant_params:5 / ife_plant_params:8 /
  system_design:14` — plus `outputs[*].channel_name`. `load_model_contract`/`ModelContractData`
  (`study/model_contract.py:27-38`) surfaces `semantic_fingerprint`, `concrete_entries`,
  `usage_records`, and `raw`, but does **not** expose `parameters`/`outputs` as named fields; they
  are reachable only via `.raw`. No current caller reads them.

### Behavioral requirements (from the ratified contract)

- **[INHERITED]** The study bridge supplies every typed entry channel; a candidate changes selected
  fields in a complete typed baseline and does not omit unrelated channels.
  (`constraint-execution-lifecycle-contract.md:258`, invariant 47.)
- **[INHERITED]** Zero, one, and multiple typed channel mappings validate completely; legitimate
  external design inputs remain ordinary typed entry channels rather than missing producers.
  (`...:457` acceptance row; `...:190-195` invariant 26; register row 11 at `...:519`.)
- **[INHERITED]** The stock codegen/TEAx path carries the study with no alternate materializer or
  consumer wrapper (D-3; `...:455` acceptance row).

### Owner-stated requirements (brief, 2026-07-20)

- **[NEED]** Validation rejects missing, extra, malformed, and wrong-typed channel mappings *before*
  evaluation. The malformed case is a real gap today: a bad field value inside a model raises a raw
  `pydantic.ValidationError` in `bridge.build` (`bridge.py:26`), which runs at `runner.py:94`
  *outside* the runner's failure switch (`runner.py:95-102` catches only `EvaluationFailed`), so it
  propagates uncaught instead of becoming a classified case.
- **[NEED]** An ordinary declared design input is never treated as a missing graph producer. The
  risk locus is `entry_source.py:44-52`: `missing = expected − supplied`; if a channel that is in
  fact a plain declared design input is not emitted, it surfaces as a missing channel.
- **[OWNER]** No LOC metrics or accounting. Simplicity is qualitative: delete the superseded
  single-entry paths and the fusion wrapper rather than add a compatibility shim; no parallel
  authority or route replaces them. (See [[loc-gates-retired-simplicity-qualitative]].)

### Inferred (confirm at review)

- **[INFERRED]** The natural source for both the channel partition and the per-channel baseline is
  the catalog `parameters` array (`param_group` + `default_value`), which already covers every IFE
  field. This would let the stock bridge build complete baselines from the catalog alone, replacing
  the fusion wrapper's read of committed `inputs/*.json` templates. The exact default source is a
  design choice — parked in Open Questions.
- **[INFERRED]** `bench_prepare_once.py`'s use of `MultiChannelEvaluator` and the removed
  `ife_hif.yaml` must be deleted or repointed alongside the primary wrapper deletion; it is a second
  stale consumer the brief did not name.
- **[INFERRED]** IFE entry-model field names are globally unique PQNs
  (e.g. `hif_plant_pkg__hif_plant__gain`), so a flat candidate namespace can still route each field
  to its channel via `param_group` without channel-qualifying the config grid. Whether the config
  schema (`study/config.py:51-55`) needs any change, or only the bridge, is a design question.

---

## Non-Goals

- Model-derived late fill or graph mutation of any kind (epic firewall).
- Constraint-free report / empty-constraint-evidence semantics — owned by Item 11. A package with no
  constraint report is a different axis from a package with zero entry channels; do not solve the
  evidence side here.
- Stellarator producer representation — owned by Item 10.
- Changing the evaluate seam or `MappingEntrySource`'s core missing/extra/wrong-typed logic; it is
  already zero/one/many-shaped and only needs to be *driven* by a multi-channel bridge.
- Relaxing the one-`EntryPoint`-module gate.

---

## Open Questions / Deferred to design

- **[SURFACED — premise conflict, owner decision needed] The "zero" acceptance coordinate.**
  The brief says use "a constraint-free package as 'zero'". Two problems:
  (a) constraint-free report semantics is explicitly firewalled to Item 11, and a constraint-free
  package can still declare entry channels — so it does not necessarily exercise the zero-*channel*
  bridge path; and (b) **no zero-entry-channel package exists anywhere in fusion-tea** — every
  generated package declares at least one `EntryPoint` channel (surveyed: IFE=3, solar spikes=3/1,
  toy spikes=1). Options for what "zero" tests at Item 9's layer:
  - *A. Real end-to-end zero-channel package.* Requires a codegen-generated zero-channel fixture —
    a cross-repo dependency into codegen, even though Item 9 is TEAx-owned. Do not absorb this into
    the TEAx item silently.
  - *B. Unit-level empty-mapping proof.* Drive the bridge/entry-source on an empty expected-channel
    set with a synthetic spec in TEAx tests — proves the zero code path (bridge builds `{}`,
    `validate` passes with nothing missing/extra) without a real package.
  - *C. Reinterpret "zero" as the constraint-free package* and accept overlap with Item 11.
  Recommendation: **B** for the bridge-shape proof (cheap, in-repo, exercises the real path); if
  Item 13's composed matrix needs a real end-to-end zero coordinate, file that as an explicit
  codegen-fixture dependency (A), owned where the fixture is generated. This sets a success
  criterion and possibly a cross-repo dependency, so it is an owner call, not a design default.
- **Baseline default source.** Catalog `parameters[*].default_value` (covers every IFE field) vs the
  committed `inputs/*.json` templates (what the wrapper used) vs the entry-model's own Pydantic
  field defaults. The catalog route removes the wrapper's template read entirely; confirm it is
  authoritative and complete for non-IFE packages.
- **Where the channel partition is computed.** Surface `parameters`/`param_group` as named fields on
  `ModelContractData`, or read `.raw["parameters"]` at the bridge? (Design; the data is present
  either way.)
- **Config schema shape.** Does the multi-channel bridge require any change to `StudyConfig`'s flat
  `grid`/`fixed` namespace, or does field-name-to-channel routing via `param_group` keep the config
  layer flat? (Depends on whether field names are guaranteed channel-unique across all packages, not
  just IFE.)
- **"One" coordinate — must it be constraint-bearing?** IFE is the only constraint-bearing package;
  the single-channel spikes are not. Confirm whether the "one" case needs a constraint or is purely
  a channel-shape proof.

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_constraint_execution_lifecycle_remediation.md` (Item 9, row 11).
- **Stage brief:** `.project/active/constraint-lifecycle-multi-entry/briefs/spec.md`.
- **Ratified authority:** `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md`
  — invariants 26, 47; acceptance rows at `:455`, `:457`; register row 11 at `:519`.
- **Upstream seam (Item 8):** `.project/active/constraint-lifecycle-catalog-store/` — the
  `load_model_contract` / `ACCEPTED_CATALOG_SCHEMA_VERSIONS` seam this bridge reads from.
- **Real package (many):** `fusion-tea/exploration/ife_e2e/generated/` at `8eb010f4`.
- **Live counterexample:** `fusion-tea/.../study/run_viability_study.py:68` (`MultiChannelEvaluator`)
  and `study/bench_prepare_once.py`.
- **Design:** `.project/active/constraint-lifecycle-multi-entry/design.md` (to be created).

---

**Next Steps:** After the "zero"-coordinate decision, proceed to `/_my_spec_review` (fresh session),
then `/_my_design`.
