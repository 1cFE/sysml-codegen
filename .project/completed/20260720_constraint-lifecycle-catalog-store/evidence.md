# Evidence: Canonical Embedded Catalog and Store Transition (Lifecycle Item 8)

**Status:** Phases 1–3 complete and verified. Catalog seam proven green on the regenerated IFE package; materializer deleted. Full multi-channel sweep deferred to Item 9 (out-of-scope divergence, surfaced).
**Date:** 2026-07-20
**Owner:** Reid W
**Branch:** constraint-exec-epic

Design revisions F1–F6 + Minors applied to `design.md` before implementation (audit verifies fixes).

## Supported-surface checkboxes

- [x] Each eligible catalog entry carries the five identity fields (source form, usage short
      name/QN, real owner QN, definition QN, entry-level def→usage join).
- [x] Admitted per-usage tier (`ConstraintCatalogUsageRecord`) deduped by full usage identity.
- [x] `definition_qualified_name` non-None **iff** `source_form == "definition_typed"` (F1); FK
      resolves to a `source_records` row, no dangle (INV-1).
- [x] `CATALOG_SCHEMA_VERSION` in `contracts/versions.py`, inside the fingerprinted payload.
- [x] TEAx consumes the embedded catalog via one seam (`load_model_contract`); real
      `semantic_fingerprint` replaces the byte-hash stand-in.
- [x] Fail-closed catalog-schema skew, both directions (INV-4).
- [x] Alternate schema (`CatalogView`/`_Catalog` reconstruction), standalone `constraint_catalog.json`,
      and byte-hash stand-in removed from TEAx.
- [x] Store no-silent-rebind preserved (eight-field `_check_compatibility`, unchanged).
- [x] **Fusion-tea materializer deleted** — IFE package regenerated to the new schema (live
      license), catalog seam proven green (≥1 eligible entry), then `materialize_constraint_catalog.py`
      and the standalone artifact removed. See Phase 3.

## Phase 1 — codegen additive (COMPLETE, verified)

Changes:
- `resolution/models.py`: `ConcreteConstraint.definition_qualified_name`; four projected fields on
  `ConstraintCatalogEntry`; new `ConstraintCatalogUsageRecord`; `ConstraintCatalog.usage_records`.
- `analysis/constraint_lowering.py`: record `definition_qualified_name` at lowering, gated strictly
  on `definition_typed` via `_referenced_definition` (F1).
- `generation/constraint_catalog.py`: project entry fields; `_assemble_usage_records` deduped by
  `(usage_qualified_name, source_local_identity)` (F2); usage tier in the fingerprint payload.
- `contracts/versions.py`: `CATALOG_SCHEMA_VERSION = "2.0.0"`.
- `contracts/models.py` + `contracts/model_contract.py`: `ModelContract.catalog_schema_version`,
  inside the fingerprinted payload.

RED-first surface:
- `tests/unit/test_catalog_usage_tier.py` (6 tests): projection, usage tier, F2 anonymous dedup,
  D2a no-predicate_ir-on-usage, fingerprint coverage. Confirmed RED (6 failed) before impl, GREEN after.
- `tests/conformance/test_catalog_definition_join.py`: F1 FK gate + INV-1 no-dangle + INV-2, against
  real fixtures (`constraint_multi_instance` definition-typed, `wi014_toy`).
- `tests/conformance/test_catalog_schema_version.py`: the deliberate-bump pin.

Fingerprint re-pin (F6): the **one** moved codegen pin, `SNAPSHOT_MANIFEST_SHA256`
(`test_constraint_snapshot_portability.py:54`): `bf6b36b1…` → `4325ce51d180a5e28af1679896113a754644bad47263796ec1b0b054f1e2c5a3`.
Graph baselines did not move (catalog is `exclude=True`), confirmed.

Battery: `uv run pytest tests/` → **3080 passed, 44 skipped** (license-loaded). `ruff check` clean on
changed files. `mypy src/` unchanged (72 pre-existing errors, 0 new — baseline confirmed by stash diff).

## Phase 2 — TEAx cutover + deletion (COMPLETE, verified)

Repo: `/home/reid/1cfe/teax` (`packages/teax-simkit/simkit/`).

Changes:
- New `study/model_contract.py`: `load_model_contract` + `ModelContractData` + `IncompatibleCatalogSchema`.
- `evaluation/package_load.py`: vendored `ACCEPTED_CATALOG_SCHEMA_VERSIONS = frozenset({"2.0.0"})`.
- `study/config.py`: `_model_contract_fingerprint` now returns the real `semantic_fingerprint`
  (byte-hash stand-in deleted).
- `study/query.py`: `_Catalog` reads the embedded catalog; `CatalogView` built from the entry
  directly (owner_qn/definition_qn/source_form/predicate_ir on the entry); `source_records` join gone.
  `StudyQuery(store, package_dir)`.
- `study/cli.py`: `cmd_inspect` reads the package dir, not the standalone file.
- Fixture: `sealed_package/package_live` regenerated license-free from `wi014_toy` snapshot (new
  schema, embedded catalog with `usage_records`, filled auto-implementations, sealed). The
  hand-authored `constraint_catalog.json` is absent by construction (deletion realized).
- `tests/study/test_query.py`: reads the package dir; `AFFORDABLE` is the real generated
  constraint_id; the join test asserts real values (the fixture had fabricated
  `membership_kind="assert"`; the true extracted value is `None`) and the new `definition_qn` join.

RED-first surface:
- `tests/study/test_model_contract_skew.py` (5 tests): accepted loads; newer/older/missing versions
  fail closed (INV-4); real fingerprint read, not a byte hash.

Battery: `python -m pytest simkit/tests` (agentic-mbse venv, `PYTHONPATH` = teax-simkit) →
**286 passed** (281 baseline + 5 new). `test_f1_arithmetic_fixture.py` embedded-shape guard preserved.

## Phase 3 — fusion-tea (COMPLETE, gate sequence honored)

Repo: `/home/reid/1cfe/fusion-tea/exploration/ife_e2e/`. Stellarator demo repo untouched.

Gate sequence (design phase-3: regenerate → prove green → THEN delete):

1. **IFE package regenerated (live license).** `sysml-codegen generate --models
   exploration/ife_e2e/models --output exploration/ife_e2e/generated --package-name ife_tea` (the
   grounded incantation; 8 modules, sealed). The new `contracts/model_contract.json` carries
   `catalog_schema_version: 2.0.0`, one `usage_records` row, one `concrete_entries` row. The viability
   `constraint_id` is `hif_plant_pkg__hif_plant__viability__81ddf10fb1d1749b` — identical to the study's
   `CONSTRAINT_ID` (no test change needed). Handwritten impls are auto-implemented (filled); the
   package's 6 runnable tests pass. `SPEC_PATH` updated to `pipelines/pipeline.yaml` (the generated
   spec name).

2. **Catalog seam proven green.** `study/prove_catalog_seam.py` — a representative run (one real
   evaluation through `StudyRunner`/store, then `StudyQuery(store, PACKAGE_DIR)` reading the embedded
   catalog). Result:
   ```
   schema_version : 2.0.0
   eligible entries carrying a verdict: 1   (zero-entries guard: satisfied, B4)
   constraint_id  : hif_plant_pkg__hif_plant__viability__81ddf10fb1d1749b
   source_form    : definition_typed
   definition_qn  : fusion_cycle::'Viability Threshold'   (Item-8 def->usage join, from the entry)
   verdict        : satisfied
   ```
   **Scope, labelled honestly:** this proves exactly Item 8's deliverable — the embedded-catalog seam
   (`load_model_contract` + embedded `StudyQuery`) and the def→usage FK join, on the real regenerated
   package. The full 2,301-point (eta, gain) acceptance sweep is **Item 13's** bar, not this phase's.

3. **Materializer deleted.** `git rm study/materialize_constraint_catalog.py`. No code imported it;
   the standalone `constraint_catalog.json` is absent by construction after regen (codegen emits only
   `model_contract.json`). `run_viability_study.py` rewired to `StudyQuery(store, PACKAGE_DIR)` +
   zero-entries guard.

**Out-of-scope divergence, surfaced (not forced):** the regen's entry-channel decomposition evolved
(4 groups → 3; the old single-param `hif_driver_params` group is gone). `run_viability_study.py`'s
full-sweep `MultiChannelEvaluator` hardcodes the older four channels, so the full sweep does not run
as-is. That bridge is **Item 9's** target (multi-channel `CandidateBridge` for zero/one/many channels;
the study's own docstring flags it as the Item-0/Item-12 single-channel gap), independent of Item 8's
catalog seam. `prove_catalog_seam.py` fills the regen's actual three channels directly to prove the
Item-8 gate without that stale wiring. Not an Item-8 defect; recorded for Item 9.

**Candidates unchanged (verified):** codegen `19b74ac`, teax `a5594e1` — the IFE regen required no
codegen fix.

## Scope surprise (capture-fidelity law 4)

The design assumed the TEAx `sealed_package` fixture already carried the embedded catalog and only
needed re-sealing (F4a). In fact its `model_contract.json` was ancient (`constraint_catalog_fingerprint`
string, no embedded catalog, older module naming, a different `constraint_id`). Phase 2 therefore
required a full fixture **regeneration**, not a re-seal — done cleanly via the license-free snapshot
path. The same staleness affects the fusion IFE package (Phase 3), which is why its regen is the
remaining gated step.

## Audit close (Certify — pass with notes)

- **F-A closed** (codegen `82ad686`): `constraint_inline` added to the FK test + a dedicated
  named-inline test — the `definition_qn=None` branch now executes non-vacuously. 6 passed.
- **F-B closed**, both sides:
  - **Consumer scan** (teax `8286893`): `tests/study/test_no_reconstruction.py` — INV-6 source-scan
    guard over teax `study`/`evaluation` product source (QN-split, predicate-text search, hardcoded
    `source_form` absent; scoped per F5). 4 study-scan tests.
  - **Producer scan** (codegen, this pass): `tests/conformance/test_catalog_no_reconstruction.py`
    added alongside the other conformance scans — guards the codegen catalog producer
    (`generation/constraint_catalog.py`, `analysis/constraint_lowering.py`, `resolution/models.py`)
    against re-deriving semantics from strings (splitting `predicate_source_key`, searching
    `predicate_ir`, hardcoding `source_form`). Covers the codegen half of spec SC-2, which the
    teax-only scan did not reach.
  - **Symbols deleted, not surviving** (teax, this pass): the alternate-schema names `CatalogView`/
    `_Catalog` are renamed to `EmbeddedCatalogView`/`_EmbeddedCatalog` (6 code sites, all in
    `study/query.py`), with an explicit rename record in the module docstring citing the spec
    deletion table. No name survives from the deletion table; the spec deletion rows now read
    "deleted (renamed → …)".
- **Minors** (fusion): Item-9 breadcrumb on the stale `MultiChannelEvaluator` (`d7f7492d`); the
  seam proof now sweeps stale `.pytest_cache` from the package tree before load (audit N1, this
  pass) so a reproducer starts clean; its `_work`/cache output stays untracked.
- Spec SC-2 and RED-first checkboxes `[x]`.

## Candidate revisions

- sysml-codegen: `CANDIDATE_REV_CODEGEN = 19b74ac` (Phase 1) — unchanged since
- teax: `CANDIDATE_REV_TEAX = a5594e1` (Phase 2) — unchanged since
- fusion-tea: `CANDIDATE_REV_FUSION = 667136fa` (Phase 3: IFE regen + catalog-seam proof + materializer
  deletion; branch `item8-fusion-embedded-catalog`)
