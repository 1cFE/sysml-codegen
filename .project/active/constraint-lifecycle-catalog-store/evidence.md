# Evidence: Canonical Embedded Catalog and Store Transition (Lifecycle Item 8)

**Status:** Phases 1–2 complete and verified; Phase 3 code-rewired, green-gate + deletion pending IFE package regen (see below).
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
- [ ] **Fusion-tea materializer deleted** — code rewired + green-gate guard added; deletion
      withheld until the IFE package is regenerated to the new schema and the study proves green
      (design phase-3 gate: prove green FIRST). See Phase 3.

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

## Phase 3 — fusion-tea (CODE REWIRED; green-gate + deletion PENDING)

Repo: `/home/reid/1cfe/fusion-tea/exploration/ife_e2e/study/`. Stellarator demo repo untouched.

Done:
- `run_viability_study.py`: `StudyQuery(store, PACKAGE_DIR)` (embedded catalog, not the standalone
  file); zero-entries-is-regression guard added (B4 thin margin — one eligible entry).

**Blocked / withheld (surfaced honestly):**
- The committed IFE package (`exploration/ife_e2e/generated/contracts/model_contract.json`) is
  pre-Item-8 (embedded catalog but no `usage_records`, no `catalog_schema_version`). `load_model_contract`
  correctly **fails closed** on it. Making the study run green requires regenerating the IFE package
  with the new codegen — a **live-license** extraction over `exploration/ife_e2e/models/` (no snapshot
  present) plus a full study run to prove the green gate.
- Per the design's phase-3 discipline (prove green FIRST, then delete), `materialize_constraint_catalog.py`
  and the materialized artifact are **retained** — deleting them before the green gate is proven would
  violate the ordering and leave no fallback if regen surfaces an issue.
- **Recommendation:** a follow-up pass (with license + budget for the study run) regenerates the IFE
  package, proves the study green on the embedded catalog with the zero-entries guard, then deletes the
  materializer + artifact. This is scoped, mechanical, and gated.

## Scope surprise (capture-fidelity law 4)

The design assumed the TEAx `sealed_package` fixture already carried the embedded catalog and only
needed re-sealing (F4a). In fact its `model_contract.json` was ancient (`constraint_catalog_fingerprint`
string, no embedded catalog, older module naming, a different `constraint_id`). Phase 2 therefore
required a full fixture **regeneration**, not a re-seal — done cleanly via the license-free snapshot
path. The same staleness affects the fusion IFE package (Phase 3), which is why its regen is the
remaining gated step.

## Candidate revisions

- sysml-codegen: `CANDIDATE_REV_CODEGEN` (Phase 1)
- teax: `CANDIDATE_REV_TEAX` (Phase 2)
- fusion-tea: `CANDIDATE_REV_FUSION` (Phase 3 code rewire; materializer retained pending regen)
