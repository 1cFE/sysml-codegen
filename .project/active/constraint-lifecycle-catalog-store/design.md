# Design: Canonical Embedded Catalog and Store Transition (Lifecycle Item 8)

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-07-20
**Branch:** constraint-exec-epic
**Commit:** 7c52c86

## Overview

Add the identity fields TEAx reconstructs today onto codegen's embedded catalog (five per eligible
entry + a new admitted-usage tier), make TEAx consume that catalog directly as on-disk data, and
delete the alternate schema, the fusion materializer, and the byte-hash fingerprint stand-in. One
schema authority, consumed — not mirrored.

## Related Artifacts

- **Spec:** `.project/active/constraint-lifecycle-catalog-store/spec.md`
- **Epic:** `.project/backlog/epic_constraint_execution_lifecycle_remediation.md` (Item 8 / row 10)
- **Contract (D-3, LC-G07/G07A/H02A):** `.project/active/constraint-execution-lifecycle-contract/spec.md`
- **Item 7 trust machinery:** `.project/active/constraint-lifecycle-package-trust/`
- **Orchestrator rulings (2026-07-20):** fusion-tea confirmed as deletion target; no active store
  migration (pre-release stores; archival invariant + existing gate suffice).

## Research Findings

**Codegen catalog at HEAD** (`src/sysml_codegen/resolution/models.py`):
- `ConstraintCatalog` (`:509-523`): `source_records[]` (per-definition), `concrete_entries[]`
  (per eligible occurrence), `excluded_records[]`, `fingerprint`.
- `ConstraintCatalogEntry` (`:467-496`) carries `owner_instance_path` and `usage_qualified_name` but
  **drops** `source_form`, `owner_qualified_name`, `source_local_identity`, `definition_qualified_name`.
- The underlying `ConcreteConstraint` (`:340-394`) **has** `source_form`, `owner_qualified_name`,
  `owner_kind`, `source_local_identity` — but **not** a definition QN field.
- Definition QN is computed in lowering: `_verified_predicate_source_key` builds
  `f"definition:{effective_source.qualified_name}"` for `definition_typed`, `inline:…` otherwise
  (`analysis/constraint_lowering.py:647-649`). That `effective_source.qualified_name` is exactly the
  `source_records[].definition_qualified_name` value (assembled from `facts.definitions`,
  `generation/constraint_catalog.py:77-83`). So the join exists structurally, encoded in a string.
- Assembly: `assemble_constraint_catalog` (`generation/constraint_catalog.py:57-140`); catalog +
  `semantic_fingerprint` embedded by `build_model_contract` (`contracts/model_contract.py:59-77`);
  serialized to `contracts/model_contract.json` (`cli/__init__.py:655`).

**TEAx alternate system** (`/home/reid/1cfe/teax/packages/teax-simkit/simkit/`):
- Alternate schema + reader: `study/query.py:20-28` (`CatalogView`), `:46-65` (`_Catalog`,
  joins `concrete.source_usage → source_record.usage_name`), `:68-116` (`StudyQuery`).
- Byte-hash stand-in: `study/config.py:79-84` (hashes `constraint_catalog.json` bytes), used at `:135`.
- `cmd_inspect` reads the standalone file: `study/cli.py:24,98,101`.
- Hand-authored fixture: `tests/…/sealed_package/…/contracts/constraint_catalog.json`.
- Store to **preserve**: `study/store.py` (crash-safe SQLite), `study/compatibility.py` (eight-field
  binding), `study/store.py:147-151` (`_check_compatibility` → `IncompatibleStore`), the new-lineage
  UX (`study/cli.py:40-59`), the real `executable_fingerprint` via seal (`evaluation/package_load.py:136`).
- **Cross-repo constraint:** TEAx does not import `sysml_codegen` (B3); it vendors codegen constants
  by copy (`evaluation/package_load.py:33-43`, `ACCEPTED_RUNTIME_CONTRACT_VERSIONS`).

**Version-pin precedents to compose with:** `contracts/versions.py` (central version + trust-anchor
constants + drift test); `_upstream_pins.py` (one-place pins, conformance test, "bump is a deliberate
act"); Item 7 manifest/anchor authenticates **bytes**, not schema shape (`contracts/manifest.py`).

**Fusion consumer** (`/home/reid/1cfe/fusion-tea/exploration/ife_e2e/study/`): materializer
`materialize_constraint_catalog.py` (QN split `:54-55`, predicate-text search `:57-66`, hardcoded
`source_form` `:71`); `run_viability_study.py:146` consumes the materialized file. (Item 9's
`MultiChannelEvaluator` is out of scope.)

No `.project/adr/` directory exists — no prior decision records to reconcile.

## Core Concept

TEAx built a parallel catalog because codegen's catalog *entry* hides four fields the model already
knows. Every workaround — QN splitting, predicate-text search, hardcoded source form — is TEAx
recovering owner QN, definition QN, usage short name, or source form that codegen computed and threw
away at the projection boundary.

The fix is not new machinery; it is **stopping the information loss at that boundary**. Project the
fields onto the entry, add one deduplicated per-usage tier that is a 1:1 replacement for TEAx's
`source_records`-by-usage index, and let TEAx read the embedded catalog straight from
`model_contract.json`. The definition→usage join stops being a text search because the entry now
carries a real `definition_qualified_name` foreign key into `source_records`. Identity stops being a
byte hash because the real `semantic_fingerprint` is already in the same file. The alternate schema,
the materializer, and the fixture then have nothing left to do, so they are deleted.

This composes with what Items 4 and 7 already built: a central version pin plus a vendored-and-checked
accepted set is how codegen and TEAx already agree across the no-import boundary; the catalog schema
version rides that same rail. Item 7's manifest/anchor keeps guarding bytes; this adds one shape check.

## Key Bets

- **B1.** For a `definition_typed` usage, `effective_source.qualified_name` (the value already inside
  `predicate_source_key`) equals a `source_records[].definition_qualified_name`. *If false → the new
  `definition_qualified_name` FK points at no source record; TEAx's join breaks and the reconstruction
  we deleted was doing something real.* (Grounded: `constraint_lowering.py:647-649` +
  `constraint_catalog.py:77-83` read the same `facts.definitions` identities.)
- **B2.** The five identity fields are invariant across a usage's concrete occurrences (they come from
  the `ConstraintUsageFact`, not the per-instance expansion). *If false → the admitted-usage record
  can't be one row per usage; usage identity would have to stay per-occurrence.*
- **B3.** Only the alternate readers consume the standalone `constraint_catalog.json`; no hidden
  consumer exists in TEAx or fusion. *If false → deleting the file/materializer breaks an unaudited
  path.* (Grounded: repo-wide grep found no other importers of `query`/`_Catalog`/the file.)
- **B4.** The real fusion-tea IFE package emits at least one eligible catalog entry, so the IFE study
  can run GREEN on the embedded catalog before the materializer is deleted. *If false → phase 3's
  RED can't go green; deletion is blocked upstream (a Gate B / Item 10 concern, not this item's).*

## Key Decisions

- **D1. Record the definition QN on `ConcreteConstraint` at lowering, then project it.** Add
  `definition_qualified_name: str | None` set from `effective_source.qualified_name` where
  `_verified_predicate_source_key` already has it (`None` for inline). *Rejected: parsing it out of
  `predicate_source_key` at assembly (splitting our own `definition:` prefix — the exact QN-splitting
  pattern we're deleting).*
- **D2. Denormalize the five fields onto the entry AND add a deduplicated admitted-usage tier.** The
  entry gains `source_form`, `source_local_identity`, `owner_qualified_name`,
  `definition_qualified_name` (with the existing `usage_qualified_name`, that is the entry-level
  definition→usage join). A new `ConstraintCatalogUsageRecord` list carries one row per admitted usage
  for direct enumeration — a 1:1 replacement of TEAx's `_source_records[usage_name]` index. *Rejected:
  identity only on the usage tier with the entry as a bare FK (DRY, but the owner specified per-entry
  fields for direct per-occurrence consumption; the small duplication is the chosen trade).*
- **D3. Skew guard = one `catalog_schema_version` on the model contract, pinned centrally, vendored
  and checked in TEAx.** Add the constant to `contracts/versions.py`; TEAx vendors an accepted set
  beside `ACCEPTED_RUNTIME_CONTRACT_VERSIONS` and checks it before reading fields, failing closed with
  a named error. A codegen drift test guards the pin. *Rejected: a brand-new version module (violates
  "no duplicated version machinery"); Pydantic-only field validation (catches missing fields but gives
  no legible version-skew error and can't distinguish benign old from incompatible).*
- **D4. TEAx reads the catalog through one new `load_model_contract(package_dir)` seam.** config,
  query, and CLI all consume it; it owns the version check and typed parse. *Rejected: each consumer
  reading and validating JSON itself (three copies of the skew guard).*
- **D5. No active store migration (orchestrator ruling).** Switching the fingerprint value lets the
  existing `_check_compatibility` gate treat any pre-release store as a new lineage; document
  "old lineage archived, new store starts." *Rejected: an equivalence-proof/migration ceremony over
  stores that carry no production history.*

## Architecture

Three tiers in the embedded catalog, one authority:

- **Definition tier** — `source_records[]` (unchanged): the reusable `constraint def` vocabulary,
  keyed by `definition_qualified_name`.
- **Usage tier** — `usage_records[]` (**new**): one row per admitted usage, projecting usage-invariant
  identity, with `definition_qualified_name` joining up to the definition tier (`None` for inline).
- **Occurrence tier** — `concrete_entries[]` (**+5 fields**): per eligible occurrence, now carrying its
  own copy of the identity fields + the definition FK for direct per-entry reads.

Data flow (codegen): lowering records `definition_qualified_name` on `ConcreteConstraint` → assembly
projects the entry fields and dedups the usage tier → fingerprint over the enlarged payload →
`build_model_contract` embeds it + `semantic_fingerprint` → serialized to `model_contract.json`.

Data flow (TEAx): `load_model_contract(package_dir)` reads `model_contract.json`, checks
`catalog_schema_version` ∈ accepted (fail closed), parses typed structures → study config binds
compatibility to the real `semantic_fingerprint` → query/CLI read identity straight from the usage +
occurrence tiers. No standalone file, no join-by-text, no byte hash.

Data flow (fusion): `run_viability_study.py` rewired to `load_model_contract` → study runs GREEN on
the embedded catalog → materializer and materialized artifact deleted.

## Required Invariants

- **INV-1.** Every eligible `concrete_entries[]` entry resolves its `definition_qualified_name` to a
  `source_records[]` row, or carries `None` (inline). No dangling FK.
- **INV-2.** Exactly one `usage_records[]` row per distinct admitted `usage_qualified_name`; its
  identity fields equal those on every occurrence sharing that usage.
- **INV-3.** The catalog `fingerprint` and `semantic_fingerprint` cover the new fields and tier
  (payload change ⇒ both recompute; all byte-identity baselines re-captured, not exempted).
- **INV-4.** TEAx fails closed on `catalog_schema_version` mismatch (either direction) before any field
  read or verdict — a named error, never a `KeyError` or silent default.
- **INV-5.** A store bound to the old byte-hash fingerprint fails closed against a package carrying the
  real `semantic_fingerprint` (existing `_check_compatibility`; no silent rebind).
- **INV-6.** No product path splits a QN, searches predicate text, or hardcodes `source_form` (source-
  scan test).

## Component Overview

- **`resolution/models.py`** — `ConcreteConstraint` gains `definition_qualified_name`;
  `ConstraintCatalogEntry` gains the four projected fields; new `ConstraintCatalogUsageRecord`;
  `ConstraintCatalog` gains `usage_records`.
- **`analysis/constraint_lowering.py`** — set `definition_qualified_name` where
  `_verified_predicate_source_key` computes `effective_source` (`:643-649`).
- **`generation/constraint_catalog.py`** — project entry fields; build the deduped usage tier;
  fingerprint over the enlarged payload.
- **`contracts/versions.py`** — add `CATALOG_SCHEMA_VERSION`; embed it on the model contract.
- **TEAx `evaluation/…` / `study/…`** — new `load_model_contract` seam + vendored accepted set;
  rewire config/query/cli; delete `CatalogView`/`_Catalog`/`cmd_inspect` alt path/stand-in/fixture.
- **fusion-tea `study/`** — rewire `run_viability_study.py`; delete `materialize_constraint_catalog.py`
  + the materialized artifact.

## Non-Goals

- Reopening D-3 (settled; embedded catalog is sole authority).
- Any standalone catalog export (CE-F1 standalone-emission framing is superseded by direct embedded
  consumption; a later export must be mechanically identical).
- Item 9 (`CandidateBridge`/`MultiChannelEvaluator`) and Item 10 (stellarator, `-stellarator-mbse-demo`).
- Active migration of any persisted store (D5).

## Implementation Notes (phased plan folded in)

Phasing is load-bearing: a consumer can't read a field codegen hasn't shipped, and fusion drives TEAx.

**Phase 1 — codegen additive (lands first, independently green).**
- RED: a `build_model_contract`/`assemble_constraint_catalog` test asserting the new fields + usage
  tier + FK resolution on a real fixture graph — fails before, passes after.
- Add the model fields (D1, D2), populate at lowering + assembly, bump `CATALOG_SCHEMA_VERSION`.
- Re-capture all byte-identity baselines (fingerprints change, INV-3); this is generator-owned churn.

**Phase 2 — TEAx cutover + deletion.**
- RED: study config/query over a real `model_contract.json` fixture (no standalone file) — fails today.
- Add `load_model_contract` + vendored accepted catalog-schema set (D3, D4); replace the stand-in
  fingerprint with `semantic_fingerprint`; rewire config/query/cli.
- Delete `CatalogView`/`_Catalog`, `cmd_inspect`'s alt path, the hand-authored fixture, the stand-in.
- Store new-lineage behavior falls out of the changed fingerprint value (D5) — assert the fail-closed.

**Phase 3 — fusion-tea deletion last, with its own RED.**
- RED/GREEN gate: rewire `run_viability_study.py` to `load_model_contract` and prove the IFE study
  runs GREEN on the embedded catalog (B4) **before** deleting anything.
- Then delete `materialize_constraint_catalog.py` + the committed materialized artifact.

Interface sketch (schema, not implementation):

```python
class ConstraintCatalogUsageRecord(BaseModel):        # NEW — admitted usage tier
    usage_qualified_name: str
    source_local_identity: str                        # usage short name
    source_form: str
    owner_kind: str
    owner_qualified_name: str
    definition_qualified_name: str | None             # FK → source_records; None for inline
# ConstraintCatalogEntry gains: source_form, source_local_identity,
#   owner_qualified_name, definition_qualified_name (usage_qualified_name already present)
```

Skew guard: read `model_contract.json` → `if version not in ACCEPTED_CATALOG_SCHEMA_VERSIONS: raise IncompatibleCatalogSchema(...)` before any typed read.

## Potential Risks

- **IFE package emits no eligible catalog entry (B4).** The stellarator demo is Gate-B-blocked with no
  catalog; if fusion-tea's IFE package is the same, phase 3 can't go green. **De-risk first:** before
  building anything, confirm the real IFE package produces ≥1 eligible entry. If not, phase 3 is
  blocked upstream and should be surfaced, not forced.
- **Baseline churn masking a real diff.** Re-capturing every fingerprint baseline (INV-3) is large;
  a real regression could hide in the churn. Mitigate with the timestamp-only diff-check discipline
  and by landing Phase 1's field additions in one reviewable re-capture.
- **Two identity copies drift (D2).** Entry vs. usage-tier identity could diverge if assembly is
  buggy. INV-2 asserts equality; make it a test, not a comment.
- **Vendored version set goes stale (B3/no-import).** TEAx's accepted set is a hand-copied constant;
  a codegen bump not mirrored in TEAx fails closed (correct) but noisily. The drift test on the codegen
  side plus the named error keep it legible.

## Integration Strategy

Replaces the alternate schema and materializer with direct consumption; reuses the store, the
compatibility gate, the seal's `executable_fingerprint`, and the version-pin/vendored-set rail from
Items 4/7. Names the seams Items 9/11 consume: the admitted-usage tier, the entry FK, and the real
fingerprints on `model_contract.json`.

## Validation Approach

- Codegen: RED-first unit tests on assembly/contract for the fields, usage tier, FK resolution (INV-1),
  usage uniqueness (INV-2); fingerprint re-baseline verified; full pytest + mypy.
- TEAx: config/query/cli over a real `model_contract.json` fixture; skew fail-closed both directions
  (INV-4); store new-lineage fail-closed (INV-5); source-scan test for INV-6; full teax suite.
- Fusion: IFE study runs GREEN on the embedded catalog before deletion (B4); materializer + artifact
  removed; drivers green after.
- Cross-repo: one pinned artifact thread (codegen through Item 7 `280a2bd`, agentic-mbse `4c18d61`,
  teax `98a6d07`) exercises generate → embed → TEAx consume → study.

## Next-Stage Handoff

- **Fixed:** three-tier catalog shape (D2); definition QN recorded at lowering (D1); TEAx reads via one
  seam with version-checked fail-closed (D3, D4); no store migration (D5); phase order 1→2→3.
- **Open for plan:** exact new-fixture selection for each phase's RED; whether `catalog_schema_version`
  is a fresh constant or a bump of an existing contract version; the precise teax accepted-set location.
- **De-risk first:** B4 — confirm the real IFE package yields an eligible catalog entry before Phase 3.

---
**Next Step:** After approval → `/_my_design_review` (fresh session), then `/_my_plan`.
