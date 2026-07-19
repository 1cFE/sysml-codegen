# Spec: Snapshot Portability and Shape Gates

**Status:** Certified
**Owner:** Reid W
**Created:** 2026-07-18 19:55 PDT
**Complexity:** MEDIUM
**Branch:** constraint-exec-epic
**Epic:** CONSTRAINT-WAVE-REMEDIATION — Item 4 (R-6, R-11)

---

## Problem

Snapshot v3 has two boundary defects.

First, the portable source-referent policy applies only to anonymous excluded constraints. A named
excluded constraint keeps the parser's absolute file path. That path enters the excluded record,
catalog fingerprint, model contract, semantic fingerprint, and generated report-aggregator bytes.
Equivalent models therefore disclose the capture machine's checkout path and produce different
semantic bytes after relocation. The current committed corpus demonstrates the leak in
`catf_mfe_model` and `constraint_non_numerical`.

Second, the v3 loader checks that its three load-bearing constraint sections exist, but it does not
validate their container and item shapes before typed reconstruction. Wrong containers and missing
item keys can escape as `AttributeError`, `KeyError`, or `TypeError`; some wrong empty containers
silently deserialize as empty. This breaks the existing v3 promise that malformed load-bearing data
is rejected through a snapshot-domain error with recapture guidance.

The correction must close both boundaries without creating snapshot v4, changing executable-profile
semantics, or using broad fixture churn to hide the affected bytes.

## Success Criteria

- [x] Named and anonymous excluded constraints with source locations use the same portable
      root-slot-relative referent at live lowering, snapshot capture, and snapshot replay. Affected
      warnings, excluded records, catalogs, contracts, fingerprints, and generated report bytes
      contain no absolute checkout or capture-machine prefix.
- [x] Both relocation scenarios pass the exact manifest below: equivalent live model trees under two
      roots, and replay of one moved snapshot/source tree. Every listed excluded-location projection,
      warning, catalog value, contract byte, report-aggregator byte, and targeted artifact hash is
      identical with no permitted path or timestamp normalization. The moved replay and licensed
      live A/live B/replay A routes pass.
- [x] Existing named constraint IDs remain byte-identical. Existing anonymous excluded IDs retain
      their current canonical file/line/column identity and width. Eligible named and anonymous
      records retain their current IDs, locations, grouping, and serialized bytes.
- [x] A malformed JSON root or malformed `constraint_facts`, `part_occurrences`, or
      `constraint_lowering_mode` shape fails as `SnapshotFormatError`. The message names the section
      and structural path, states the expected shape or missing field, and tells the operator to
      recapture. No raw `AttributeError`, `KeyError`, or `TypeError` escapes, and a wrong empty
      container cannot be mistaken for a valid empty list or mapping.
- [x] A table-driven malformed-shape matrix covers the field policy below, including aggregate,
      usage, occurrence, and step items. Required, nullable, optional, and degradable cases retain
      their stated v3 behavior. No legacy extraction section is silently promoted into this gate.
- [x] Fixture review identifies exactly the semantic consequences of R-6. At the current corpus,
      only `catf_mfe_model/extraction_snapshot.json` and
      `constraint_non_numerical/extraction_snapshot.json` change; timestamp-only churn is reverted,
      derived committed baselines remain byte-identical, and every other fixture byte is unchanged.
- [x] Focused normal and optimized tests, existing live/snapshot parity tests, snapshot v3 gates,
      fixture manifests, and relevant fingerprint/contract tests pass without changing remote or PR
      state.

## Known Requirements

### Portable excluded locations

- **[NEED]** Named and anonymous excluded locations must be portable at the canonical boundary and
  remain portable through relocated byte/fingerprint parity. Owner-stated in the Item 4 stage input.
- **[INHERITED]** The portable spelling is the existing lexical
  `root-<ordered-slot>/<canonical-percent-encoded-relative-path>` referent. Exact file inputs win;
  otherwise the most-specific containing directory wins, with ordered-root position preserving
  distinct roots. Live input maps through supplied model roots and replay validates the stored
  grammar. Sources: `.project/backlog/epic_constraint_pr_wave_remediation.md`, Item 4 scope 1;
  `.project/active/gap-lowering-integrity/design.md`, D4-D6.
- **[INFERRED]** The canonicalization selector expands from anonymous excluded usages to every
  excluded usage with a location, and no further. R-6 invalidates GAP-CLOSE's agent-grade premise
  that named bytes had no demonstrated portability defect. Eligible usages remain outside this
  correction because R-6 provides no evidence against their current identity contract.
- **[INFERRED]** Canonicalization must happen before an excluded location is rendered into live
  warnings or records and before the snapshot serializes its copied facts. Live and replay must use
  explicit routes; a path string must not self-select whether it is raw or canonical. This preserves
  the existing GAP-CLOSE route-safety boundary while making named and anonymous results agree.
- **[INFERRED]** Named excluded ID inputs remain unchanged. Their current mint tuple does not contain
  location, so R-6 requires location, catalog, fingerprint, contract, and generated-byte changes but
  does not justify named-ID churn. The current anonymous excluded mint continues to include canonical
  referent, line, and column with its 128-bit suffix.
- **[INFERRED]** A named excluded usage with no `LocationFact` retains the existing explicit
  no-location representation. A usage with a present location that cannot map on the live route or
  cannot validate on replay fails loudly rather than leaking or accepting a raw path. Anonymous
  exclusions continue to require a location because it is part of their identity.
- **[NEED]** Relocation proof must compare bytes and fingerprints, not only behavior or generated
  success. Owner-stated in the Item 4 stage input; the epic success criterion requires the same
  snapshot to generate byte-identical semantic artifacts from two checkout roots.

#### Exact relocation comparison manifest

- **[INFERRED]** Two scenarios are mandatory:
  1. **Equivalent live roots:** capture/lower equivalent model trees at absolute roots A and B with
     the same ordered model-root layout, package name, and generation options, then compare live A,
     live B, and replay of A's snapshot.
  2. **Moved replay:** copy A's exact snapshot and source tree to root B, then compare replay at A
     with replay of that unchanged snapshot/tree at B using the same package name and options.
- **[INFERRED]** In both scenarios, the following manifest is the complete affected semantic
  projection. “Canonical JSON bytes” means sorted keys, compact separators, ASCII escaping, and no
  other transformation.

| Compared output | Exact path or JSON pointer | Comparison |
|---|---|---|
| Serialized excluded-facts projection | Ordered array of `/constraint_facts/usages/<i>` objects, where `<i>` is returned by the production excluded-usage selector | Canonical JSON bytes equal. The full `constraint_facts` object is deliberately not compared because eligible usage locations remain raw. |
| Excluded warning stream | Ordered lowering logger messages for selected `NON_NUMERICAL` usages | Exact string-list equality. No path substitution. |
| Excluded catalog records | `/excluded_records` from `ConstraintCatalog.model_dump(mode="json")` | Canonical JSON bytes equal. |
| Catalog fingerprint | `/fingerprint` from the same catalog dump | Exact string equality. |
| Model contract | `contracts/model_contract.json` | Full file bytes equal; additionally assert equality at `/constraint_catalog/excluded_records`, `/constraint_catalog/fingerprint`, and `/semantic_fingerprint`. |
| Generated report aggregator | `modules/constraints/constraintreportaggregatormodule.py` | Full file bytes equal, including the embedded catalog fingerprint. |
| Package contract consequences | `contracts/package_contract.json` | Exact equality only at `/artifact_hashes/contracts~1model_contract.json` and `/artifact_hashes/modules~1constraints~1constraintreportaggregatormodule.py` (JSON Pointer escaping shown). The package-wide `/executable_fingerprint` is outside this projection because it covers unrelated generated files whose source headers are not changed by R-6. |
| Root-leak scan | Every value/file above | Neither absolute root A nor root B, including redundant-leading-separator spellings, occurs in the compared bytes or strings. |

- **[INFERRED]** There are no permitted normalizations in the manifest. In particular,
  `captured_at` is not rewritten, blanked, or compared: the whole snapshot is not a relocation
  parity claim. Fixture review restores each affected snapshot's pre-change `captured_at` byte and
  permits changes only at the excluded location pointers named below. Eligible usage objects remain
  byte-pinned before/after within each fixture, but are intentionally outside cross-root comparison.

### Snapshot v3 shape boundary

- **[NEED]** Malformed v3 section, container, and item shapes must raise contextual snapshot-domain
  errors. Owner-stated in the Item 4 stage input.
- **[INFERRED]** The R-11 gate is limited to the JSON root needed to reach the versioned boundary and
  the three v3-added load-bearing constraint sections: `constraint_facts`, `part_occurrences`, and
  `constraint_lowering_mode`. It covers their actual nested reconstruction shapes and normalizes
  failures from their typed reconstructors. `calc_defs`, `calc_usages`, `design_attributes`,
  `hierarchy_data`, `aggregation_expressions`, `computed_attributes`, `channel_aliases`, and
  `compilation_results` keep their existing legacy loader behavior. Wider schema hardening requires
  a separate evidence-backed item. Sources: primary review R-11; snapshot v3 design D5/INV-8;
  `.project/active/constraint-wave-snapshot-portability/spec-review.md`, L2-1.
- **[INFERRED]** Pre-validation must reject wrong containers even when Python iteration would produce
  an empty result. Any residual companion parser/model validation failure at this boundary is
  normalized to `SnapshotFormatError` with section/path context and recapture guidance; raw container
  exceptions are never the public contract.

#### In-scope field policy

The policy labels are exact:

- **Required:** the key must be present and the value must have the stated non-null shape.
- **Required, nullable:** the key must be present; explicit JSON `null` is valid, but absence is not.
- **Optional with default:** absence retains the current stated default. A present non-null value
  must have the stated shape.
- **Degradable:** absence retains the current warning and fallback. No in-scope v3 constraint field
  is degradable.

- **[HARD]** Envelope and occurrence policy:

| Path | Policy | Accepted value |
|---|---|---|
| JSON document root | Required | mapping |
| `/constraint_facts` | Required | mapping |
| `/part_occurrences` | Required | mapping; `{}` is valid |
| `/part_occurrences/<owner>` | Required when owner key exists | list of occurrence mappings; `[]` is valid |
| `/part_occurrences/<owner>/<n>/part_def_qn` | Required | string |
| `/part_occurrences/<owner>/<n>/steps` | Required | list of step mappings; `[]` is accepted by the current deserializer and remains valid at this shape gate |
| `/part_occurrences/<owner>/<n>/steps/<m>/owning_def_qn` | Required | string |
| `/part_occurrences/<owner>/<n>/steps/<m>/feature_name` | Required | string |
| `/part_occurrences/<owner>/<n>/steps/<m>/occurrence_index` | Required, nullable | integer or `null` |
| `/constraint_lowering_mode` | Required | string equal to `applied` or `grandfathered_off` |

- **[HARD]** Constraint-facts aggregate and item policy. Every list below may be empty; when an item
  exists it must be a mapping.

| Object | Required fields | Required, nullable fields |
|---|---|---|
| `/constraint_facts` | `schema_version` (exact `constraint-facts/v1` string); `definitions`, `usages`, `contexts`, `diagnostics` (lists) | none |
| definition item | `identity` (non-null identity mapping), `formals` (formal mappings list) | `predicate` (ExpressionIR mapping or `null`) |
| usage item | `identity` and `scope` (non-null identity mappings); `source` and `owner` (mappings); `actuals` (actual mappings list); `omitted_default_formals` and `inherited_into` (string lists) | `location` (location mapping or `null`), `membership_kind` (string or `null`), `is_negated` (boolean or `null`), `predicate` (ExpressionIR mapping or `null`) |
| context item | `identity` (non-null identity mapping); `general_types`, `types`, `inherited_constraints` (string lists); `redefinitions` (redefinition mappings list) | none |
| diagnostic item | `kind`, `message` (strings) | `operand_source` (string or `null`), `location` (location mapping or `null`) |
| identity mapping | `kind`, `name`, `qualified_name` keys | each value is string or `null`; the containing field decides whether the whole mapping may be `null` |
| location mapping | `file` (string), `line` and `column` (integers) | none |
| source mapping | `form` (string) | `effective_predicate_source`, `constraint_definition`, `referenced_feature_target`, `asserted_constraint` (identity mapping or `null`) |
| owner mapping | `owning_definition` (mapping) | `owner` (identity mapping or `null`) |
| owning-definition mapping | `kind`, `qualified_name` (strings) | none |
| formal item | `types` (string list), `has_default` (boolean) | `name`, `qualified_name` (string or `null`), `default` (ExpressionIR mapping or `null`) |
| actual item | `formal_targets` (string list) | `name`, `direction` (string or `null`), `value` (ExpressionIR mapping or `null`) |
| redefinition item | none | `feature`, `redefines` (string or `null`), `value` (ExpressionIR mapping or `null`) |

- **[HARD]** Non-null ExpressionIR values retain this `expression-ir/v1` field policy. Child node
  lists contain mappings. This item wraps codec shape/version failures with the parent
  `constraint_facts...` path; it does not redefine ExpressionIR.

| Node/object | Required fields | Required, nullable fields | Optional with default |
|---|---|---|---|
| every ExpressionIR node | `schema_version` (exact `expression-ir/v1` string), `kind` (recognized string) | none | none |
| literal node | `literal` (mapping) | none | `operand_type` (mapping or `null`, absent → `null`) |
| literal fact | `kind` (string), `value` (any JSON value, including `null`) | `result_type` (string or `null`) | none |
| feature-reference node | `reference` (mapping) | none | `operand_type` (mapping or `null`, absent → `null`) |
| feature-reference fact | `target_types`, `chain_segments` (string lists) | `source_name` (string or `null`), `target` (identity mapping or `null`) | none |
| operator node | `operator` (string), `operands` (ExpressionIR mappings list) | `operand_type` (mapping or `null`) | none |
| unit node | `value` (ExpressionIR mapping) | `unit_text` (string or `null`) | `operand_type` (mapping or `null`, absent → `null`) |
| invocation node | `arguments` (ExpressionIR mappings list) | `function_qn` (string list or `null`), `operand_type` (mapping or `null`) | none |
| unsupported node | `node_kind`, `diagnostic` (strings) | `source_text` (string or `null`) | none |
| operand-type mapping | `category` (string) | `enumeration` (string or `null`), `unit` (unit mapping or `null`) | none |
| unit mapping | none | `unit`, `dimension` (string or `null`) | none |

  Unknown extra keys continue to be ignored as they are today. Fields the codec directly indexes
  remain required even when their value is nullable.
- **[INFERRED]** No in-scope field is degradable. Outside scope,
  `/compilation_results` remains absent-with-warning degradation to `{}`, and all legacy `.get(...)`
  defaults and warnings remain unchanged. This explicit negative rule prevents R-11 from promoting a
  compatibility default into an error.

### Controlled fixture consequences

- **[NEED]** Fixture churn is limited to reviewed, provenance-recorded R-6 consequences. Owner-stated
  in the Item 4 stage input.
- **[INFERRED]** The current affected-fixture inventory is exactly two snapshots:
  `tests/fixtures/catf_mfe_model/extraction_snapshot.json` (65 named exclusions) and
  `tests/fixtures/constraint_non_numerical/extraction_snapshot.json` (one named exclusion). The
  implementation records per-fixture before/after semantic diffs, reverts `captured_at`-only churn,
  and proves all other fixture and committed-baseline bytes unchanged. This inventory is derived
  from the current v3 corpus and executable-profile selector, not presumed from path-string grep
  alone. It was independently repeated across all 30 committed extraction snapshots by
  `.project/active/constraint-wave-snapshot-portability/spec-review.md` (Reality Check and L1-1),
  which found exactly 65 + 1 affected named exclusions and no others.
- **[INFERRED]** Re-capture or a mechanically equivalent reviewed fixture update is allowed only for
  those affected snapshots. Absolute paths in eligible facts, document metadata, or unrelated legacy
  fields are not permission for wider churn.
- **[INFERRED]** The allowed fixture diff is an auditable pointer allowlist: only
  `/constraint_facts/usages/<i>/location/file` for the 65 + 1 selector-confirmed named exclusions may
  change, each from a raw absolute path to the canonical root-slot referent. `/captured_at`, every
  eligible usage object, and every other JSON pointer must be byte-identical. The sorted fixture
  manifest may report only the two snapshot paths as changed; the complete committed-baseline
  manifest must be identical.

## Non-Goals

- Snapshot schema v4, v2/v3 coexistence, in-place migration, or unrelated serializer/loader
  restructuring.
- Shape-gating legacy extraction sections outside `constraint_facts`, `part_occurrences`, and
  `constraint_lowering_mode`.
- Changing profile v3 decisions, constraint-facts/expression-IR schemas, exclusion kinds, catalog
  models, constraint ID formats, or ordered-model-root semantics.
- Canonicalizing eligible constraint locations or implementing `[ANON-ELIGIBLE-KEY]`.
- Rewriting historical snapshots that contain no affected named excluded record, or accepting
  timestamp and unrelated extraction drift as part of R-6.
- Implementing R-4/R-5/R-7 occurrence and demand corrections owned by Item 3.
- Commit, push, PR comment, merge, or any other remote-state change.

## Open Questions / Deferred to design

- Choose the validator structure that gives every error an exact JSON-style structural path without
  duplicating the companion schema or changing which fields are optional.
- Choose the exact message grammar and table organization. The outcome is fixed: section/path,
  expected shape or missing key, `SnapshotFormatError`, and recapture guidance.
- Choose the per-fixture diff/evidence record format and whether the two affected snapshots are
  licensed re-captures or reviewed mechanical corrections. The two-file scope and byte gates are
  fixed.

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_constraint_pr_wave_remediation.md` (Item 4)
- **Required Reading:**
  - `.project/research/20260718-192048_constraint-exec-pr-wave-code-review.md` (R-6, R-11)
  - `.project/active/constraint-wave-snapshot-portability/spec-review.md`
  - `.project/completed/20260713_snapshot-v3/spec.md`
  - `.project/completed/20260713_snapshot-v3/design.md`
  - `.project/completed/20260713_snapshot-v3/audit.md`
  - `.project/active/gap-lowering-integrity/spec.md`
  - `.project/active/gap-lowering-integrity/design.md`
  - `.project/active/gap-lowering-integrity/evidence.md`
- **Snapshot contract:** `docs/architecture/reference/27-snapshot-generation.md`
- **Current implementation:** `src/sysml_codegen/snapshot/serializer.py`,
  `src/sysml_codegen/snapshot/loader.py`, `src/sysml_codegen/analysis/source_referent.py`,
  `src/sysml_codegen/analysis/constraint_lowering.py`, and
  `src/sysml_codegen/analysis/part_instance_index.py`
- **Current tests:** `tests/unit/test_snapshot_v3_gate.py`, `tests/unit/test_source_referent.py`,
  `tests/conformance/test_constraint_snapshot_identity.py`,
  `tests/conformance/test_constraint_non_numerical.py`, and
  `tests/conformance/test_fingerprint_stability.py`
- **Design:** `.project/active/constraint-wave-snapshot-portability/design.md` (to be created)

---

**Next Steps:** After approval, proceed to `my-spec-review`, then `my-design`.
