# Spec: Canonical Embedded Catalog and Store Transition (Lifecycle Item 8)

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-07-20
**Complexity:** HIGH
**Branch:** constraint-exec-epic

Epic authority: `epic_constraint_execution_lifecycle_remediation.md`, Item 8 / register row 10.
Operationalizes owner decision **D-3** (settled; see Non-Goals). This spec inventories first and
specifies second — the deletion inventory below is file:line-grounded because a missed consumer
becomes a broken deletion.

---

## Problem

Two schema authorities exist for one set of facts, and TEAx trusts the wrong one.

Codegen already assembles a real constraint catalog, embeds it in the model contract, and ships it
in every generated package as `contracts/model_contract.json` (with a real `semantic_fingerprint`).
But TEAx does not read it. Instead it consumes a **separately-shaped** `contracts/constraint_catalog.json`
that a hand-authored fixture and a fusion-side "materializer" produce, and it reconstructs — by
string-splitting qualified names, substring-searching serialized predicate text, and hardcoding
`source_form` — semantic fields codegen already knows but does not expose on the catalog *entry*.

The gap is concrete. Codegen's `ConstraintCatalogEntry` (`src/sysml_codegen/resolution/models.py:467-496`)
carries `owner_instance_path` and `usage_qualified_name` but **drops** the entry's `source_form`,
`owner_qualified_name`, usage short name, and any `definition_qn` — even though the underlying
`ConcreteConstraint` (`models.py:340-394`) has all of them. So a consumer that needs owner QN,
definition QN, source form, or the definition→usage join has to invent them. That invention is the
alternate system.

Compounding it: TEAx binds study-store compatibility to a **stand-in fingerprint** that hashes the
alternate catalog file's *bytes* (`teax .../study/config.py:79-84`, docstring: "standing in for a
`ModelContract` fingerprint until Item 9") rather than to codegen's real `semantic_fingerprint`.
Identity is a placeholder over a file that only exists in one fixture shape.

The cost is a maintained parallel schema, three reconstruction workarounds that silently guess when
the model shape violates their assumptions (e.g. one-usage-per-definition), and a package identity
that is not the model's identity. The owner's decision: purge it. Codegen's embedded catalog is the
sole schema authority; TEAx consumes it directly; the alternate system is deleted, not shimmed.

## Success Criteria

Outcomes, testable. Acceptance coordinates follow the epic's row-10 line and the contract's row 10
(`constraint-execution-lifecycle-contract/spec.md:498`).

- [ ] **Catalog totality.** Every field a TEAx consumer needs is present on codegen's embedded
      catalog, across all five record kinds — source definition, admitted usage, concrete eligible
      occurrence, excluded occurrence, and result — with no consumer-side reconstruction. Verified by:
      TEAx reads owner QN, definition QN, source form, usage identity, and the definition→usage join
      straight from `model_contract.json`; no code splits a QN, searches predicate text, or hardcodes
      a source form.
- [ ] **The named alternate system is gone, not shimmed.** The deletion inventory (below) is fully
      removed. A source-scan test asserts no surviving symbol of the alternate catalog schema
      (`CatalogView`, `_Catalog`), no standalone `constraint_catalog.json` reader/writer in product
      paths, and no reconstruction workaround (`rsplit("::")` on a QN, predicate-text search,
      hardcoded `source_form`) in codegen, TEAx, or the fusion consumer.
- [ ] **Real identity, consumed as data.** TEAx binds store compatibility to codegen's real
      `semantic_fingerprint` (read from `model_contract.json`), the sealed package's real
      `executable_fingerprint`, and the catalog `fingerprint` — never a byte-hash stand-in. Consumed
      as on-disk JSON data, not by importing `sysml_codegen` (see [HARD] below).
- [ ] **Store transition never silently rebinds.** Switching the fingerprint provenance either proves
      an existing store artifact-equivalent and migrates it, or preserves it as archived lineage and
      starts a new store. A store bound to the old stand-in fingerprint fails closed against a package
      carrying the real fingerprint (surfaces as an explicit new-lineage message, not a silent reuse).
- [ ] **Catalog/schema skew fails closed, both directions.** A package whose embedded catalog is
      missing a field a consumer requires, and a consumer that expects a field the catalog does not
      carry, each fail with a named pre-semantic error before any verdict is computed — never a
      `KeyError`, a silent default, or a guessed value.
- [ ] **RED-first public surface.** The new catalog fields, the admitted-usage record, the
      direct-consumption path, and the skew guard each land against a test that fails before the
      change and passes after, exercised through public seams only (codegen `generate`/`build_model_contract`;
      TEAx study config/query/CLI over the real `model_contract.json`).

## Known Requirements

### Catalog additions (the one recognized additive class)

- **[INHERITED: epic Item 8 §Scope.1; LC-G07]** Each eligible concrete catalog entry gains five
  fields codegen already holds on `ConcreteConstraint` but does not currently project: **source form**
  (`source_form`), **usage short name and QN** (`source_local_identity` + the existing
  `usage_qualified_name`), **real owner QN** (`owner_qualified_name`, distinct from the existing
  `owner_instance_path`), **definition QN** (`definition_qualified_name`), and an **entry-level
  definition→usage join** so a consumer never recovers the link by searching predicate text.
- **[INHERITED: epic Item 8 §Scope.1]** The catalog gains an **admitted per-usage record** — one
  record per admitted constraint usage, a mid-tier between the existing per-definition `source_records`
  and per-occurrence `concrete_entries` (`models.py:454-464`, `:467-496`). It carries the usage's
  identity (short name, QN), its owner QN, source form, and its definition join, so a consumer can
  enumerate usages directly.
- **[INFERRED]** The additive fields and the usage record are populated at catalog *assembly*
  (`generation/constraint_catalog.py:57` `assemble_constraint_catalog`) from the validated
  `ConcreteConstraint` set and `ConstraintFacts.definitions` — the same source that already feeds
  `source_records`. No new extraction or resolution stage.
- **[INFERRED]** Adding fields changes the catalog payload, so the catalog `fingerprint`
  (`constraint_catalog.py:129-134`) and the model contract's `semantic_fingerprint`
  (`contracts/model_contract.py:59-69`) change. All byte-identity baselines and the pinned artifact
  thread must be re-captured, not exempted. (Coordinate with the generated-baseline format-exempt gate.)

### Direct consumption and identity

- **[NEED]** Codegen's embedded catalog is the sole catalog schema authority; TEAx consumes source
  form, usage identity, owner QN, definition QN, the explicit join, and occurrence data directly, and
  binds compatibility to the real semantic/catalog identity rather than a standalone-byte stand-in.
  Source: owner, 2026-07-19, "100% Option A. We need to purge this mess." (contract LC-G07).
- **[HARD]** TEAx consumes codegen identity and catalog data as **on-disk JSON**, not by importing
  `sysml_codegen`. The TEAx runtime deliberately does not depend on codegen (B3): it vendors codegen
  constants by copy (`teax .../evaluation/package_load.py:33-43`) and reads the seal/model-contract as
  data. The real `executable_fingerprint` is already consumed this way from `package_contract.json`
  (`package_load.py:136`); the real `semantic_fingerprint` is available the same way from
  `model_contract.json`. Forced by the existing cross-repo architecture.
- **[INFERRED]** The stand-in fingerprint is one function (`teax .../study/config.py:79-84`,
  consumed at `:135`). The replacement reads `model_contract.json["semantic_fingerprint"]`; everything
  downstream already carries a `model_contract_fingerprint` string (`study/definition.py`,
  `study/compatibility.py`, the store `compatibility` column) and needs no shape change — only the
  value's provenance changes.

### Store transition

- **[INHERITED: contract LC-G07A]** The catalog-identity transition either proves an old store
  artifact-equivalent and migrates it, or preserves it as archived lineage and starts a new store;
  identity is never silently reassigned. (Contract grade is [INFERRED]; carried here, not
  independently re-validated.)
- **[INFERRED]** The "never silent rebind" half is already structurally enforced: TEAx's
  `_check_compatibility` (`teax .../study/store.py:147-151`) raises `IncompatibleStore` on any
  mismatch of the eight-field compatibility binding (`study/compatibility.py`), surfaced as a
  new-lineage message (`study/cli.py:40-59`). Changing the fingerprint value automatically forces a
  new lineage for any pre-existing store. Item 8 preserves this gate and the crash-safe SQLite store
  (`study/store.py`); it does not reimplement them.

### Skew fails closed

- **[INHERITED: contract row 10 / brief]** Catalog/schema skew fails closed before semantic use, both
  directions: a catalog missing a required field and a consumer expecting an absent field each raise a
  named pre-semantic error, never a `KeyError` or a silent default.

### Deletion completeness

- **[NEED]** The named alternate system is removed, not shimmed: the alternate TEAx catalog schema,
  the fusion catalog materializer, the hand-authored schema fixture, the stand-in fingerprint, QN
  splitting, predicate-text search, hardcoded source form, and semantic reconstruction. Source: owner
  decision D-3, 2026-07-19 (contract LC-H02A). See the grounded inventory below.

### Compose with Item 7 (do not duplicate)

- **[HARD]** Identity work reuses Item 7's landed trust machinery. `executable_fingerprint` is already
  produced by the seal (`src/sysml_codegen/contracts/models.py:135`) and authenticated by the
  generation manifest / re-seal gate (`contracts/manifest.py`). Item 8 adds semantic/catalog identity
  consumption on top; it does not add a second sealing, manifest, or hash-anchor mechanism.

---

## Deletion inventory (file:line-grounded)

Completeness is the requirement; a missed consumer becomes a broken deletion.

### Codegen (`src/sysml_codegen/`) — additive, not deletion, but the projection changes

- `resolution/models.py:467-496` `ConstraintCatalogEntry` — gains the five fields + join.
- `resolution/models.py` — new admitted per-usage record model.
- `generation/constraint_catalog.py:57-140` `assemble_constraint_catalog` — populates the new fields
  and the usage record; fingerprint recomputes.
- `contracts/model_contract.py:59-69` — payload/fingerprint recompute follows automatically.

### TEAx (`/home/reid/1cfe/teax/packages/teax-simkit/simkit/`) — DELETE / rewire

| File | Lines | Role | Action |
|---|---|---|---|
| `study/query.py` | 20-28 | `CatalogView` alternate-schema dataclass | delete |
| `study/query.py` | 46-65 | `_Catalog` standalone-file reader + definition→usage join | delete |
| `study/query.py` | 43, 68-116 | `CaseView.catalog` field + `StudyQuery` consumer | rewire to read the embedded catalog from `model_contract.json` |
| `study/cli.py` | 24, 98, 101 | `cmd_inspect` builds/reads the standalone `constraint_catalog.json` | rewire to the embedded catalog |
| `study/config.py` | 79-84 (used at 135) | `_model_contract_fingerprint` byte-hash stand-in | replace with `model_contract.json["semantic_fingerprint"]` |
| `tests/study/test_query.py` | 12, 16, 42, 56-62, 66, 74 | tests over the alternate join | rewrite against the real embedded catalog |
| `tests/evaluation/fixtures/sealed_package/package_live/contracts/constraint_catalog.json` | whole file | hand-authored alternate fixture | delete; fixtures use real `model_contract.json` |
| `tests/evaluation/fixtures/f1_arithmetic/generate_fixture.py` | 222 (`source_form="inline"`), 242 (`.split("__")[-1]`) | fixture-generator hardcode + QN split | fix to carry real fields |

Notes: predicate-text search — **none in TEAx** (`predicate_ir` is only ever an opaque string;
`evaluation/projection.py:28-30` classifies by `constraint_id`/`status`). `constraint_catalog.json`
exists only in the `sealed_package` fixture; `f1_arithmetic` already ships only the real
`model_contract.json`, so the stand-in and `cmd_inspect` are fixture-shape-dependent today.

**Preserve (store identity — do not delete):** `study/store.py` (crash-safe SQLite store),
`study/compatibility.py` (eight-field binding), `study/store.py:147-151` (`_check_compatibility`
new-lineage gate), `study/cli.py:40-59` (new-lineage UX), `evaluation/package_load.py:136` (real
`executable_fingerprint` via seal). These change value provenance, not shape.

### Fusion consumer — SURFACED conflict, see Open Questions

Grounded location: `/home/reid/1cfe/fusion-tea/exploration/ife_e2e/study/` (NOT the brief's
`-stellarator-mbse-demo`, which has no such code — see Open Questions).

| File | Lines | Role | Action |
|---|---|---|---|
| `materialize_constraint_catalog.py` | whole file | the fusion catalog materializer (reads real embedded catalog, re-emits standalone alternate-shape file) | delete |
| `materialize_constraint_catalog.py` | 54-55 | QN splitting (`usage_qn.rsplit("::", 1)`) for usage_name/owner_qn | delete with file |
| `materialize_constraint_catalog.py` | 57-66 | predicate-text search to recover `definition_qn` (substring in `predicate_ir`) | delete with file |
| `materialize_constraint_catalog.py` | 71 | hardcoded `source_form="definition_typed"` | delete with file |
| `materialize_constraint_catalog.py` | 74-75 | owner/definition QN reconstruction | delete with file |
| `run_viability_study.py` | 146 | `StudyQuery` reads the materialized standalone catalog | rewire to embedded catalog |
| `generated/contracts/constraint_catalog.json` | whole file | committed materialized artifact | delete |

Out of this item (Item 9): `MultiChannelEvaluator` (`run_viability_study.py:68`,
`bench_prepare_once.py`) — flagged, not deleted here.

## Non-Goals

- **D-3 is settled owner authority; this spec operationalizes it and does not reopen it.**
  `[INHERITED: owner decision D-3 — settled]` `[OWNER-VERBATIM]` "100% Option A. We need to purge this
  mess." (contract `constraint-execution-lifecycle-contract/spec.md:525-530`). The choice of
  embedded-catalog-as-sole-authority (Option A) over a codegen-owned standalone canonical catalog
  (Option B, rejected) is not in scope to revisit.
- A differently-shaped standalone catalog export. Any later export must be **mechanically identical**
  to the embedded schema and independently justified (epic Item 8 Out of Scope). This item adds no
  standalone `constraint_catalog.json` emission (CE-F1's standalone-emission framing is superseded by
  direct embedded consumption).
- Items 9/11 TEAx bridge/evidence work. Name the seams they consume (the admitted-usage record, the
  entry-level join, the real fingerprints), but do not build the multi-entry `CandidateBridge` (Item 9)
  or evidence work here.
- Fusion stellarator modeling (Item 10). The `-stellarator-mbse-demo` repo and its uncommitted Gate B
  filing are left untouched.
- CE-F3 (PreparedEvaluator fixture class) — already fixed (teax `0d606a4`); the `ToyPlantParams` alias
  is already absent from the fusion driver scripts.

## Open Questions / Deferred to design

- **[SURFACED — premise conflict, parked on evidenced default] Fusion deletion-target repo.** The
  brief pins the fusion consumer at `../fusion-tea-stellarator-mbse-demo` (bceaf40a). The grounded
  inventory finds that repo has **no** study layer, materializer, QN-splitting, or predicate-text
  search — its constraint path delegates to codegen's real embedded catalog and is Gate-B-blocked.
  Every actual deletion target the brief names lives in a different checkout,
  `/home/reid/1cfe/fusion-tea/exploration/ife_e2e/study/`, which the WI-027/IFE docs consistently cite
  as the IFE-acceptance home. This spec's fusion inventory targets `fusion-tea` on that evidence and
  treats `-stellarator-mbse-demo` as the untouched Item 10 workspace. **Owner: confirm the target repo
  before the deletion lands** — a wrong target means the deletion inventory points at the wrong tree.
  Dependent conclusion (which fusion files are deleted) is parked on this answer.
- **Concrete store migration vs. forward-looking invariant.** LC-G07A requires prove-equivalence-or-
  archive. The "no silent rebind" half is already enforced by `_check_compatibility`. Open for design:
  does Item 8 actively migrate a specific existing persisted store (the IFE runs produce real stores,
  requiring the artifact-equivalence proof path), or is the deliverable "switch the fingerprint +
  rely on the existing new-lineage gate + document archival," treating legacy stores as archived by
  default? Deferred to design unless the owner names a production store that must survive the cutover.
- **New catalog record/field names and exact shape.** The five fields and the admitted-usage record
  are required outcomes; their exact field names, whether the usage record is a new list on
  `ConstraintCatalog` or a nesting, and how the entry→definition join is keyed (definition QN vs. an
  index) are design decisions. Deferred to design.
- **Skew-guard mechanism.** That skew fails closed is a requirement; where the guard lives (a catalog
  schema-version field, a required-field validator at TEAx load, or Pydantic-model validation on
  read) is a design choice. Deferred to design.
- **Cross-repo phasing.** The change spans codegen (add fields) → TEAx (consume + replace fingerprint)
  → fusion (delete materializer). The ordering, the compatible commit pins, and whether a transitional
  window tolerates both shapes are design/plan concerns. Deferred to design. (Note the pinned chain:
  codegen through Item 7 `280a2bd`, agentic-mbse `4c18d61`, TEAx `98a6d07`.)

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_constraint_execution_lifecycle_remediation.md` (Item 8, register row 10)
- **Required Reading:**
  - Ratified contract + D-3: `.project/active/constraint-execution-lifecycle-contract/spec.md`
    (LC-G07, LC-G07A, LC-H02, LC-H02A, LC-F05; D-3 at `:525-530`)
  - Backlog CE-F1 recorded scope: `.project/backlog/BACKLOG.md:745-748`
  - Item 7 landed trust machinery: `.project/active/constraint-lifecycle-package-trust/` (manifest,
    hash anchor, executable fingerprint)
- **Stage brief:** `.project/active/constraint-lifecycle-catalog-store/briefs/spec.md`
- **Design:** `.project/active/constraint-lifecycle-catalog-store/design.md` (to be created)

---

**Next Steps:** After approval, `/_my_spec_review` (fresh session), then `/_my_design`.
