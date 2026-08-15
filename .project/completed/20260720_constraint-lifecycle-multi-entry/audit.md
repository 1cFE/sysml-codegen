# Audit: Multi-Entry Candidate Bridge (Lifecycle Item 9)

**Verdict:** Certify
**Audited:** 2026-07-20
**Branch:** constraint-exec-epic (codegen); item8-fusion-embedded-catalog (fusion-tea)
**Commits audited:** codegen `240d170` · teax `07eb0ac` (over `96578a4`) · fusion-tea `2422e715`

---

## Summary

The item delivers what the spec and design specify, and every executable gate reproduced
first-hand across all three repos. The stock TEAx bridge builds a complete typed mapping for
zero, one, and many entry channels; the fusion wrappers (`MultiChannelEvaluator`,
`ThreeChannelEvaluator`, bench usage, config scalars) are deleted with no shim; the codegen
zero-entry gap was fixed at root with a single, byte-identity-preserving template change. The
three design-review Majors (R1 runner relocation, R2 both baseline arms, R3 seam migration) all
verified — R1 by reproducing the RED (uncaught `EvaluationFailed`) and the GREEN
(`StudyBridgeDefect`). One honesty note keeps this from being a clean bill: the evidence and
CURRENT_WORK cite codegen commit `5a72366`, but the actual audited HEAD is `240d170` (the value
the stage brief names). That is a stale-hash record, not a code defect.

## Findings

### Plan completion (design §7 phased plan)

All five phases verified complete.

- **Phase 0 (codegen gap).** A3 falsified against the real CLI and fixed in the same landing
  unit rather than parked. Reproduced: production delta vs the `589c8c4` source pin is exactly
  two files — `templates/pipeline_yaml.jinja2` (+5 lines) and the `sample_model.yaml` baseline.
- **Phase 1–2 (RED + multi-channel bridge + R1 relocation).** `test_bridge.py` 9 passed;
  runner RED/GREEN reproduced (see R1 below).
- **Phase 3 (definition/config consolidation).** Scalar `entry_channel`/`entry_model` gone from
  `StudyConfig` and `StudyDefinition`; no `getattr(evaluator.package, config.entry_model)`
  survives; store no-silent-rebind + fingerprint tests green.
- **Phase 4 (wire study, prove green, delete wrapper).** `run_viability_study.py` runs green
  through the stock bridge (2301/2301) with no wrapper; deletion done after the green gate.
- **Phase 5 (validation + regression).** Field-level fail-closed shapes and the D5 guarantee
  pinned; full teax suite green.

### Spec conformance

All eight success criteria reproduce green.

- **RED first** — verified. With `bridge.build` outside the failure switch, the runner tests
  fail with an uncaught `EvaluationFailed` escaping (`bridge.py:74`); restored, they classify.
- **"Many" validates and runs** — `run_viability_study.py` exit 0, `2301 cases carry a verdict
  (of 2301 grid points)`, `100% agreement (modulo 7 flagged boundary rows)`, no wrapper.
- **"One" validates** — `test_bridge_one_*` (single-channel fixture) pass.
- **"Zero" validates** — end-to-end committed fixture
  `tests/evaluation/fixtures/zero_channel/package_live` (real codegen-generated) +
  `test_zero_channel_package.py` (3 passed): `entry_models=={}`, `build({})=={}`, full
  `PreparedEvaluator.evaluate` returns evidence. Fixture is **constraint-bearing** — its
  `pipeline.yaml` carries an `entry_fusion` EntryPoint with zero channels plus a
  `constraint_report_aggregator` (Item 11 firewall labeling verified: "zero" = zero *entry
  channels*, not constraint-free report).
- **Baseline + override** — `test_bridge_one_defaults_unselected` (unselected field keeps
  modeled default), `test_bridge_many_omits_no_unrelated_channel` (invariant 47).
- **Validation before evaluation** — unknown field → `ENTRY_VALIDATION`, malformed value →
  `ENTRY_VALIDATION`, ambiguous field across channels → construction-time raise. All classified
  before/at bridge construction, none escaping as raw `pydantic.ValidationError`.
- **Ordinary design inputs not missing producers** — falls out of the complete baseline; the
  defaultless-arm test proves the honest fail-closed rather than an invented value.
- **Wrapper deleted, not shimmed** — deletion reality confirmed (below).

### Design conformance

Implementation follows the design. One documented nuance, non-blocking:

- **D3 fingerprint basis.** Design prose says the config `semantic_fingerprint` payload moves to
  an "`entry_models` identity (sorted channel names + model class names)." As implemented, the
  config payload simply *drops* the two scalar keys; the study's concrete channel/model binding
  is carried by the separate `model_contract_fingerprint` field
  (`config.py:81-88`), derived from codegen's real `semantic_fingerprint`. The design's actual
  goal — a changed fingerprint that starts a new lineage and cannot silently rebind — is met
  (R5 gate green). Evidence §5 describes the implemented form accurately; only the design's D3
  wording is ahead of the code. No action required.

### Code integrity

- **R1 (route safety) — CONFIRMED closed.** `runner.py`: `bridge.build` is inside the
  `try/except EvaluationFailed` switch; the except routes to `_commit_execution_failure` →
  `StudyBridgeDefect`. RED reproduced by relocating the call back outside (uncaught
  `EvaluationFailed` escapes both `test_bridge_defect_is_loud` and
  `test_malformed_mapping_is_recorded_classified_failure`); GREEN restored; working tree clean
  after. This is the "call site, not exception type" fix the review demanded.
- **R2 (failure honesty) — CONFIRMED.** Both A1 arms tested: fully-defaulted baseline builds;
  defaultless required field unselected → recorded `ENTRY_VALIDATION`, never an invented value.
- **A2 guard** is a genuine fail-closed construction-time raise (`ValueError(match="ambiguous")`),
  not silent first-pick.
- No `try/except Exception` swallow, no back-compat shim, no parallel authority. The deletion is
  real (below), not layered behind a guard.

### Deletion reality (§6 inventory)

Verified zero code survivors across both consumer repos.

- teax: single-channel `CandidateBridge(channel_name, entry_model)`, `StudyConfig`/
  `StudyDefinition` scalars, the `getattr` resolution, and the two fingerprint keys — gone.
- fusion-tea live study dir: no `ThreeChannelEvaluator`, `_fixed_channels`, `HifDriverParams`,
  `ife_hif.yaml`. `MultiChannelEvaluator` / `hif_driver_params` appear only in prose — the
  `findings.md` historical note **and** a `run_viability_study.py:13-14` docstring that explains
  the deletion. Both are documentation, not code.

---

## Discrepancies (all minor, none blocking certification)

1. **Stale commit hash in the record.** Evidence §7 and CURRENT_WORK cite codegen `5a72366`;
   the actual repo HEAD and the brief's named candidate is `240d170`. Capture-fidelity fix:
   the recorded hash should be `240d170`. (teax `07eb0ac` and fusion `2422e715` match.)
2. **Codegen suite count.** Evidence claims `3083 passed`; reproduced `3084 passed / 44 skipped /
   17 deselected`, exit 0, **zero** `no live syside license` skips (license genuinely loaded).
   The +1 is favorable and non-blocking.
3. **teax suite count.** Evidence §5 (`301 passed`) reproduces exactly; CURRENT_WORK's `298
   passed` is a stale pre-fixture figure.
4. **Zero-fixture test strength.** `test_zero_channel_package.py`'s third assertion is `evidence
   is not None`, weaker than "a ConstraintReport is produced." The fixture yaml is genuinely
   constraint-bearing, so the underlying claim holds; the assertion could be tightened.
5. **"Only residual in findings.md."** Evidence §6 says the sole prose residual is in
   `findings.md`; there is also a harmless deletion-explaining docstring at
   `run_viability_study.py:13-14`. Substance (zero code survivors) holds.

---

## Certification

Reproduced first-hand and certified:

- **Codegen production delta** = `pipeline_yaml.jinja2` + `sample_model.yaml` only (git
  name-status `589c8c4..240d170`, excluding `.project/`); Items 1–8 source surfaces untouched.
- **Byte-identity** structurally airtight: the `{% else %}` (template:20) attaches to
  `{% if entry_points %}` (template:11); the true-branch is byte-for-byte unchanged, so only
  zero-entry packages hit the new branch; `sample_model.yaml` is the single tracked delta.
- **Codegen full licensed suite** at `240d170`: 3084 passed / 44 skipped, license loaded (0
  license skips).
- **teax:** R1 RED+GREEN; R2 both arms; `test_bridge.py` (9) zero/one/many + unknown/malformed/
  A2 guards; zero-channel end-to-end fixture (3); scalar deletion + fingerprint no-silent-rebind
  (R5); full simkit suite 301 passed. Working tree clean after RED reverts.
- **fusion-tea:** R3 `prove_catalog_seam.py` migrated + green (schema 2.0.0, verdict satisfied);
  IFE study 2301/2301 100% agreement through the stock bridge, no wrapper; `bench_prepare_once.py`
  migrated + parses; deletion inventory verified.
- **Evidence honesty:** the Item-11 firewall (zero entry channels ≠ constraint-free report) is
  *recorded* in spec Non-Goals and the zero fixture is deliberately constraint-bearing — surfaced,
  not absorbed.

**Not checked:**
- The `2301/2301` acceptance numbers and "7 boundary rows" were taken from the study's own
  reproduced stdout; the acceptance table rows were not independently recomputed against the
  retiring hand rule.
- The codegen byte-identity claim was verified by template-structure reasoning and the committed
  name-status diff, not by a fresh full licensed regeneration of every channel-bearing baseline.
- mypy/ruff on the teax changed files were not re-run this pass (evidence claims clean/zero-added);
  the reproduction focused on functional gates.
- Nothing was pushed; push ordering and the cross-repo v3 PR wave (Item 13) are out of this
  item's scope and unaudited here.
