# Design: Semantic Identity and Occurrence Foundation

**Status:** Superseded (2026-08-07; archived 2026-08-10) — approved for planning earlier the
same day, then the Item-4 architecture was stopped after Phases 1–2 and replaced by the
elaborate-first front end (`.project/backlog/epic_elaborate_first_architecture.md`)
**Owner:** Reid W
**Created:** 2026-08-07
**Updated:** 2026-08-07
**Branch:** `source-identity-epic`
**Commit:** `224bfa6`

---

## Overview

Establish one extraction-owned declaration-plus-occurrence identity for every supported source-bearing
demand before producer resolution. Carry that evidence unchanged through live and snapshot routes,
reuse the existing occurrence index to repair the nested override, and leave the resolver cutover to
Item 5.

## Related Artifacts

- [Spec](./spec.md)
- [Spec review](./spec-review.md)
- [Product lens](./product-lens.md)
- [Design review](./design-review.md)
- [SOURCE-IDENTITY epic](../../backlog/epic_semantic_source_identity.md)
- [Route and evidence findings](../source-identity-route-evidence-spike/findings.md)
- [Adjacent-work register](../source-identity-route-evidence-spike/adjacent-work-register.md)
- [Authoritative lifecycle contract](../../concepts/constraint-execution-authoritative-lifecycle-contract.md)
- [Lifecycle requirements companion](../../concepts/constraint-execution-lifecycle-requirements.md)
- [Nested-override tripwire evidence](../../completed/20260724_nested-override-tripwire/evidence.md)
- [Producer-completeness design](../../completed/20260720_constraint-lifecycle-producer-completeness/design.md)

No decision-record index exists at `.project/adr/INDEX.md`; there are no indexed ADRs to reconcile.

## The Point

**[OWNER]** One semantic source occurrence must become exactly one runtime source across all of its
calculation, constraint, and aggregation consumers: one public input for an externally supplied value
or one producer channel for a computed value. Item 4 must make that result derivable from the modeled
declaration and concrete occurrence before any consumer selects a runtime source. It must not invent
identity from a consumer's owner, parameter name, written leaf, or current value. Source: SOURCE-
IDENTITY epic mission invariant and lifecycle invariants 55–56.

## Research Findings

- Calc extraction already receives the resolved SysIDE referent. `BindingInfo` carries two live AST
  element pointers plus mutable path/name hints, but deep chains omit the target AST, snapshots clear
  the pointers, and the chain parser silently drops an indexed first operand
  (`src/sysml_codegen/extraction/usage_extractor.py:55`, `:768`, `:887`, `:998`).
- Virtual-binding rewrite can replace a reference with a literal and clear `source_path`. The new
  evidence must be immutable and independent of these legacy fields
  (`src/sysml_codegen/orchestration/pipeline_builder.py:285`).
- Constraint leaves already preserve the SysIDE target and chain segments in `FeatureReferenceFact`.
  They lack concrete occurrence only because one usage fact may expand under several owners
  (`../agentic-mbse/src/agentic_mbse/sysml/expression_facts.py:66`,
  `src/sysml_codegen/analysis/constraint_lowering.py:692`).
- Aggregation terms currently retain names and paths, not resolved targets. Their scoped records are
  concrete enough to receive identities after occurrence scoping
  (`../agentic-mbse/src/agentic_mbse/sysml/data_models.py:88`,
  `src/sysml_codegen/extraction/data_models.py:295`).
- `PartInstanceIndex` already supplies deterministic structured occurrences, multiplicity expansion,
  specialization closure, and atomic cycle/non-finite failures. The older calc-oriented path finder
  and current aggregation scoping flatten these facts and are not suitable identity authorities
  (`src/sysml_codegen/analysis/part_instance_index.py:26`, `:190`, `:249`, `:321`;
  `src/sysml_codegen/orchestration/pipeline_builder.py:692`).
- The live pipeline builds that index only when constraints exist. Its snapshot table is the exact
  constraint-preparation query transcript, often `{}`, rather than a general occurrence table
  (`src/sysml_codegen/orchestration/pipeline_builder.py:971`, `:1023`;
  `src/sysml_codegen/orchestration/pipeline_context.py:133`).
- The nested override compares definition-relative and occurrence-relative owner strings. The
  unmatched-warning path is the precise missing bridge, and the current test pins the defect
  (`src/sysml_codegen/resolution/supplied_values.py:213`, `:327`, `:623`;
  `tests/unit/test_supplied_values.py:407`).
- All runtime consumers already enter one producer-resolution function through a declared request.
  Item 4 can attach identity evidence at this boundary without changing key-table selection
  (`src/sysml_codegen/resolution/producer_resolution.py:99`, `:527`, `:616`).
- Snapshot loading already gates the version before deserialization, and frozen occurrence lookup
  fails closed on an absent queried owner. These are the right migration and replay patterns
  (`src/sysml_codegen/snapshot/loader.py:722-736`,
  `src/sysml_codegen/analysis/part_instance_index.py:435`).
- The upstream self-binding check is intentionally rescue-aware today. Its same-named outer-feature
  exemption and two negative-oracle tests directly contradict the revised contract
  (`../agentic-mbse/src/agentic_mbse/validation/level2_structure.py:309`, `:358`;
  `../agentic-mbse/tests/test_validation/test_item12_checks.py:73`).

## Core Concept

Treat source identity as a fact produced once, not as a successful lookup. Extraction first preserves
the exact SysIDE referent, source form, bound formal, and redefinition relationships before mutable
legacy rewrites run. One source-identity authority then combines those facts with a structured
`PartInstanceIndex` occurrence and publishes an immutable manifest. Each manifest record keeps the
semantic referent separate from an identity made of the applicable declaration and concrete feature
occurrence. Calc, constraint, aggregation, and supplied-value code may locate a record by an exact
consumer or value-site coordinate, but may not derive identity from that coordinate. Live generation
uses a live index; replay validates and consumes the stored manifest plus the same index's frozen query
transcript. Item 4 threads the record into the existing producer request but deliberately leaves the
current lookup table in control until Item 5.

## Key Bets

- **B1.** SysIDE's resolved referent and `owned_redefinitions` relationships contain the declaration
  evidence needed for every supported form. *If false → extraction cannot produce exact identity and
  the design must stop rather than add name reconstruction.*
- **B2.** `PartInstanceIndex` represents every concrete occurrence needed by calc, constraint, and
  aggregation source bindings. *If false → the “one bridge” premise fails and the index must be
  extended before identity finalization can ship.*
- **B3.** Every source-bearing demand has a stable concrete consumer coordinate before producer
  resolution: calc usage plus formal, expanded constraint owner plus formal, or scoped aggregation
  plus structural term position. *If false → the manifest cannot be joined without an ordinal or
  heuristic key, so capture must add a stable coordinate at extraction instead.*
- **B4.** Current graph topology can remain unchanged when identity is attached but ignored by the
  key table, except for the explicitly owned C19 repair and fail-closed unsupported forms. *If false →
  the change has crossed into Item 5 and requires an explicit scope review.*
- **B5.** Every structural query replay can issue is present in the successful live route's sealed
  transcript. The shared replay/live phases issue the same owner-query sets. *If false → a valid v6
  snapshot can fail closed during replay, so capture/replay sequencing must be reconciled before the
  snapshot format ships.*

## Key Decisions

- **D1. Immutable structural identity.** `SemanticSourceIdentity` contains an immutable declaration
  identity and an immutable occurrence identity. Declaration records element kind and qualified
  identity. Occurrence records a structured `InstanceOccurrence` anchor plus the relative member path
  to the source feature; the rendered `instance_path` is display data only. *Rejected: a qualified
  string alone (it loses multiplicity, definition, and specialization distinctions).*
- **D2. One manifest, not three route ledgers.** `SourceIdentityManifest` contains sorted records for
  source demands and modeled value sites. A record contains its typed coordinate, semantic referent,
  source identity or `ABSENT_REFERENT`, and no supplied value. `ABSENT_REFERENT` is reserved for a
  genuine unresolved term so later strict/lenient policy has an honest input; missing occurrence and
  ambiguity abort the manifest. A modeled value site is a model location that supplies a value before
  producer resolution: a definition default, an occurrence `:>>` override, or a usage-authored
  literal. Its coordinate is `(site kind, exact value-bearing element identity, structured
  occurrence)`. Its manifest record carries that coordinate, the contract `value_state`, and the
  semantic source identity. The supplied value and provenance stay on the original extraction record,
  joined by the same coordinate; computed producer outputs do not create value-site records.
  *Rejected: fields or maps owned independently by calc, constraint, and aggregation routes (they
  recreate three authorities and make snapshot parity depend on three join conventions).*
- **D3. Consumer coordinates locate; they never identify.** A coordinate names a calc formal, an
  expanded constraint formal, an aggregation term, or a captured value site. It is excluded from
  `SemanticSourceIdentity` equality and hashing. *Rejected: deriving source identity from consumer
  EQN, formal name, or term spelling (the measured 40-of-75 failure mode).*
- **D4. One authority also records occurrence queries.** A `SourceIdentityAuthority` wraps the one
  live or frozen `OccurrenceIndex`, implements its `occurrences_of` surface for constraint
  preparation, and projects semantic evidence. Manifest finalization does not seal the recorder. The
  recorder stays open through aggregation scoping, identity finalization, constraint preparation,
  and C19 value adaptation. It seals only after all live query-producing phases succeed, immediately
  before the completed `PipelineContext` publishes the table and snapshot capture can serialize it.
  A query after sealing is a programming error. *Rejected: a second walker, a second bridge, or a
  constraint-only transcript alongside a source-identity table.*
- **D5. Contextual projection, not global uniqueness.** Occurrence projection uses the concrete
  consumer anchor, the resolved referent, the authored path form, and redefinition relationships.
  It returns exactly one of unique, missing, or ambiguous with sorted candidate occurrences.
  *Rejected: `occurrences_of(definition)` followed by first-pick or global `len == 1` (both ignore the
  consumer's structural context).*
- **D6. Snapshot v6 stores the completed manifest.** Version 6 serializes the manifest and broadens
  the existing `part_occurrences` section to the union transcript shared by identity and constraint
  work. Replay consumes the stored identities; it does not rerun semantic projection. *Rejected: an
  additive optional field on v5 or a loader compatibility shim (either silently reconstructs missing
  authority).*
- **D7. C19 is an identity-derived value repair, not a resolver cutover.** Supplied-value matching may
  use manifest value-site records to match a definition-relative override to the exact occurrence-
  relative demand. Once that identity join is the applicable existing precedence outcome, zero or
  multiple matching value sites fail with `SI_VALUE_SITE_MISSING` or
  `SI_VALUE_SITE_AMBIGUOUS`. The existing precedence ladder remains unchanged for all other outcomes.
  *Rejected: changing producer key forms or all materialization behavior in Item 4 (Item 5 owns it).*
- **D8. Unsupported forms fail before registry construction.** The authority reports machine-
  checkable `SI_SELF_BINDING`, `SI_INDEXED_SOURCE_UNSUPPORTED`,
  `SI_EXPRESSION_SOURCE_UNSUPPORTED`, `SI_OCCURRENCE_MISSING`, and
  `SI_OCCURRENCE_AMBIGUOUS` failures. C19 value-site joins use `SI_VALUE_SITE_MISSING` and
  `SI_VALUE_SITE_AMBIGUOUS`. Snapshot shape/query failures use `SI_SNAPSHOT_CORRUPT`. Same-named
  outer features are diagnostic context only. *Rejected: rescue, path flattening,
  warning-and-continue, or letting strict/lenient policy decide whether identity exists.*
- **D9. Upstream validation lands independently.** Keep `L2_SELF_NAMED_BINDING` but correct its
  oracle; add `L6_INDEXED_SOURCE_UNSUPPORTED` for a valid indexed source outside the executable
  subset. Codegen uses its own failure codes and does not trust an upstream validation result.
  *Rejected: passing validation decisions into codegen or coupling the upstream commit to the atomic
  v6 snapshot recapture.*

## Architecture

The live route builds the authority once after model load and uses it anywhere an occurrence query is
needed. Extraction records immutable semantic evidence while legacy path/value fields remain available
to the current pipeline. After calc expansion, constraint owner preparation, and aggregation scoping
have exposed all concrete consumers, the authority finalizes the complete manifest atomically. The
manifest is then attached to requests before any producer lookup.

Building the index for every model adds indexing cost even when no constraints exist. Construction
alone does not enumerate cyclic or non-finite paths. A source-identity projection that queries such a
path now fails closed even in a constraint-free model. That is an intentional Item-4 readiness change,
not a C19 topology change.

```text
SysIDE referents + redefinitions + concrete consumer coordinates
                              │
PartInstanceIndex ──> SourceIdentityAuthority ──> immutable manifest
       │                      │                         │
       └── shared queries ────┴──> union transcript    ├──> C19 value adapter
                                                        └──> ProducerRequest
                                                             (ignored by Item-4 key table)

snapshot v6 = extraction records + manifest + union transcript
replay      = validated manifest + FrozenOccurrenceIndex; no identity reconstruction
```

The authority maps a def-level referent through the consumer's occurrence context and maps an
occurrence-level referent directly to its structured anchor. When a redefinition applies, the source
declaration is the redefining feature in that context while the original semantic referent remains
recorded separately. A calc output uses its containing part occurrence plus its calc-usage/output
member path. Authored literals and calculation-definition defaults retain distinct declaration and
per-usage occurrence identities; Item 4 preserves their current runtime topology but does not claim
Item 6's mutation certification.

Aggregation scoping keeps today's eligibility boundary: the existing extracted calculation usages
still decide which aggregation instances are eligible. The authority replaces only the dotted-path
source for those eligible instances with structured occurrences. The required set of
`(aggregation expression, instance_path)` records must remain identical; Item 4 does not widen
aggregation participation.

On replay, loader shape validation checks every nested declaration, path step, member segment,
coordinate kind, disposition, and duplicate coordinate before graph code runs. The replay authority
may answer structural queries from the frozen union transcript for constraints and value adaptation,
but the stored manifest is the only source of binding identity. Replay does not rerun live-only
aggregation scoping. Its overall owner-query set must be a subset of the sealed live transcript, and
the constraint-preparation and C19 value-adaptation phases shared by both routes must have exactly
equal owner-query sets.

## Required Invariants

- **I1. Referent fidelity:** a reference record contains the exact SysIDE-resolved target; no same-
  named substitute is accepted.
- **I2. Identity shape:** identified sources always have both declaration and concrete occurrence;
  neither half is nullable.
- **I3. Separation:** referent, applicable declaration/redefinition, occurrence, value, provenance,
  and legacy binding type remain distinct fields.
- **I4. Immutability:** VBR stamping, rescue code, enrichment, and backtracking cannot mutate or
  replace extracted evidence or manifest identity.
- **I5. One bridge:** all new occurrence projection and aggregation scoping use
  `PartInstanceIndex`; `_find_instantiation_paths` is never consulted for source identity.
- **I6. Atomicity:** cycle, non-finite cardinality, missing occurrence, ambiguity, corrupt manifest,
  or absent frozen query aborts before any partial manifest or runtime source is published.
- **I7. Distinctness:** two structured occurrences of one declaration compare unequal even when
  their values are equal; all consumers of one occurrence compare equal.
- **I8. Policy boundary:** strict/lenient policy applies only after a genuine absent referent is
  established. It cannot create identity or convert ambiguity into a miss.
- **I9. Route parity:** live, in-place replay, and relocated replay compare equal on the complete
  manifest, not only rendered paths or graph bytes.
- **I10. Replay query coverage:** every replay owner query is covered by the sealed live transcript;
  phases executed on both routes have exactly equal owner-query sets.
- **I11. Item boundary:** only C19 and fail-closed readiness behavior may change foundation runtime
  results. The latter includes a source-identity query exposing a cyclic or non-finite occurrence in
  a constraint-free model. C14/C26 remain explicit current-defect pins for Item 5.

## Component Overview

- **Reference evidence** — extraction models in `extraction/usage_extractor.py`, hierarchy facts, and
  aggregation decomposition. Preserve source form, semantic target, bound formal, and redefinition
  edges before strings are normalized.
- **Source identity model and authority** — new focused module under `analysis/`. Own immutable value
  types, projection outcomes, manifest construction/lookup, query recording, and deterministic
  serialization order. It does not know channels, entry points, or resolver policy.
- **Occurrence index** — `analysis/part_instance_index.py`. Remains the only structural walker. Add
  exact reverse/path lookup only if projection needs it; do not add another model scan.
- **Pipeline orchestration** — `orchestration/pipeline_builder.py` and `pipeline_context.py`. Build one
  authority early, pass it to aggregation scoping and constraint preparation, finalize before the
  output registry, and publish manifest plus transcript after success.
- **Snapshot boundary** — `snapshot/serializer.py`, `loader.py`, `capture.py`, and `graph_rebuild.py`.
  Write and require v6 identity evidence, reconstruct immutable values, and establish the replay
  authority before rescue, enrichment, constraint lowering, or backtracking.
- **C19 adapter** — `resolution/supplied_values.py`. Replace the string-scope tripwire miss with an
  exact manifest identity/value-site match while leaving existing precedence and collision behavior
  intact.
- **Producer boundary** — `resolution/producer_resolution.py` and its five call sites. Carry the
  manifest record on `ProducerRequest`; Item 4 asserts presence/disposition but does not use it to
  select a channel or entry point.
- **Authoring validation** — sibling `agentic-mbse` validation types, L2/L6 checks, fixtures, and tests.
  Provide actionable author feedback; remain independent from codegen enforcement.

## Non-Goals

- Switching producer resolution, backtracking, aggregation materialization, VBR, or parameter-group
  repair to identity-based source selection. Item 5 owns that cutover and deletion register.
- Deleting the now-unreachable self-binding rescue in this item. The codegen readiness gate prevents
  it from running on a self-binding; Item 5 removes superseded routes together.
- Correcting C14/C26 public topology or certifying final per-source mutation. Item 5 flips topology;
  Item 6 performs the census, mutation proof, and downstream artifact review.
- Supporting indexed `#(i)` sources or general expression sources. They remain valid SysML outside
  the executable subset and fail with distinct readiness outcomes.
- Replacing all existing part-structure utilities. Only source identity and new occurrence consumers
  must use the shared index; broader walker consolidation stays in `[CONSTRAINT-ARCH-UNIFY]`.
- Changing committed graph baselines, parameter schemas, generated packages, or customer models as a
  side effect of adding foundation evidence.

## Implementation Notes

- Capture indexed/expression form before `FeatureChainExpression` normalization. Preserve the target
  AST for chains of every length; never infer indexed form from the flattened `source_path`.
- Capture both sides of a binding: the bound formal identity and the RHS referent. Self-binding is an
  exact semantic comparison between them, not `param_name == leaf` and not an outer-scope search.
- Build the occurrence authority before `_scope_aggregation_expressions`. Keep the helper's current
  extracted-calc-usage eligibility rule, but replace its calc-derived dotted paths with structured
  index occurrences and assert identical scoped records.
- Keep immutable reference evidence through `_rewrite_virtual_bindings`. Literal stamping may change
  the value carrier but cannot reclassify a reference-derived source as an authored literal.
- Finalize the manifest only after rerouted aggregations and prepared constraint owner instances
  exist, and before output-registry construction, self-binding rescue, supplied-value enrichment,
  constraint resolution, or backtracking. Keep occurrence recording open through later C19 value
  adaptation and seal it only when all query-producing phases have succeeded, immediately before
  publishing the completed context.
- Manifest lookup must reject duplicate or missing typed coordinates. Diagnostic text may show
  rendered paths, but equality and candidate sorting use structured steps and member paths.
- Bump `SNAPSHOT_FORMAT_VERSION` from 5 to 6. Make `source_identity_manifest` and the broadened
  `part_occurrences` shape load-bearing. Version 5 must fail at the existing first gate with recapture
  guidance.
- Recapture all 37 registered fixtures in one codegen change. Review non-`captured_at` diffs by
  section: version, manifest, occurrence transcript, and unrelated extraction data.

## Potential Risks

- **Referent evidence is lost in one extractor.** Deep chains and aggregation decomposition are the
  likely gaps. Mitigation: extraction-level tests assert resolved target identity before testing the
  manifest.
- **Consumer-coordinate drift breaks replay joins.** Mitigation: typed coordinate constructors live
  with the authority, coordinates are serialized, duplicates fail, and live/replay manifest equality
  is tested directly.
- **The broadened occurrence transcript becomes a full-model dump.** Mitigation: keep query-driven
  recording. Serialize only successful owners actually queried by scoping, identity, value repair,
  or constraint preparation.
- **Replay asks for an owner live capture did not record.** Mitigation: compare the overall replay
  owner-query set as a subset of the sealed live set and require exact set equality for phases shared
  by both routes.
- **Universal indexing adds cost and exposes structural failures earlier.** Mitigation: benchmark the
  37-fixture capture set, keep recording query-driven, and test that only source-identity queries into
  cyclic or non-finite structure produce the intended new fail-closed result.
- **Item 4 accidentally changes topology.** Mitigation: compare every maintained graph/schema/package
  baseline and require an explicit review for any diff. Keep C14/C26 defect pins named.
- **Cross-repository diagnostic landing creates a temporary mismatch.** Mitigation: codegen is
  independently fail-closed. The upstream leg may land first or second without changing semantics.
- **C19 repair selects a wrong same-named override.** Mitigation: join only on complete source
  identity/value-site records. If the value site is zero, multiple, or disagrees across demand
  contexts, retain a blocking diagnostic instead of using the old leaf/scope fallback.

## Integration Strategy

1. Land the `agentic-mbse` validation leg with corrected positive/negative self-binding oracles and a
   distinct indexed-source readiness check. This leg does not carry codegen semantic decisions.
2. Land the codegen identity model, extraction evidence, shared authority, v6 serializer/loader,
   capture/rebuild changes, and all 37 recaptured snapshots as one atomic unit.
3. Enable the C19 value-site join and flip its defect test only after live and replay identity parity
   is proven. Preserve the flat sibling and all unrelated outputs.
4. Hand the manifest and request field to Item 5 as the only accepted resolver input for the later
   materialization/backtracking cutover.

## Validation Approach

- **Identity unit tests:** structural equality/hash, declaration/redefinition separation, deterministic
  sorting, duplicate coordinates, unique/missing/ambiguous projection, and exact failure codes.
- **Occurrence controls:** reuse multiplicity, Cartesian expansion, specialization, deterministic
  ordering, recursive containment, and non-finite cardinality tests in
  `tests/conformance/test_part_instance_index.py`.
- **Extraction/readiness tests:** deep-chain target preservation, indexed `#(i)` detection before
  flattening, exact formal-vs-referent self-binding, expression-source blocking, and same-named outer
  controls that still produce the self-binding failure.
- **Foundation coordinates:** use one supported mixed-consumer fixture for C8, C11–C13, C15, C24,
  and C25; separate blocking fixtures for C9/C10 ambiguity and C18 genuine miss; extend existing
  `nested_occurrence_override_probe` for C19, `shadowed_reference` for C20, specialization/per-child
  fixtures for C21, `expression_binding_probe` for 22a, and solar-battery controls for C17/C26.
  C14 and C26 assert canonical manifest identity plus an explicit current-defect topology pin.
- **C19 acceptance:** calculation and constraint demands carry the same identity, both observe
  `80.0`, the unmatched-override warning is absent, and the flat sibling remains byte/semantic
  identical.
- **Aggregation-scope equivalence:** compare legacy and structured scoping on all maintained
  aggregation fixtures and require the exact same sorted `(aggregation expression, instance_path)`
  set before removing the legacy path source.
- **Snapshot contract:** v5 rejection, required nested shape checks, corruption and absent-query
  failures, exact 37-snapshot gate, live/in-place/relocated manifest equality, and graph rebuild with
  no identity projection call. A named live/replay coverage test requires every replay owner query to
  occur in the sealed live transcript and exact query-set equality for constraint preparation and C19
  value adaptation.
- **Recapture review:** classify every snapshot diff and record identity correctness, transcript
  correctness, relocated parity, and unrelated drift. `captured_at` churn alone is expected.
- **Regression gates:** focused unit/conformance tests, project lint/type checks, and zero unreviewed
  diff in computation graphs, parameter schemas, or generated-package baselines.

## Next-Stage Handoff

The plan must treat D1–D9 and I1–I11 as fixed. In particular, it must preserve a completed immutable
manifest in v6, use `PartInstanceIndex` as the only walker, keep consumer coordinates out of identity,
fail unsupported forms before resolution, and leave the producer key table unchanged except for
threading evidence.

Item 4 does not fix the customer-visible fan-out defect. The legacy producer key table remains in
control until Item 5, and C14/C26 must stay pinned to the current defective public topology. Item-4
completion means the identity foundation and C19 repair are ready, not that the resolver cutover has
occurred.

The first implementation risk to retire is extraction completeness: prove that calc chains,
constraint leaves, aggregation terms, and redefinitions all retain exact target evidence. If any
supported route lacks that evidence, stop and extend extraction rather than falling back to a name.
The second risk is the contextual occurrence projection for C9/C10/C19; implement and test its three
outcomes before snapshot migration. Only then recapture the 37 snapshots and enable the C19 repair.

The plan may choose exact filenames for the new `analysis/` module and fixture grouping. It may not
change the identity shape, split authority by consumer, add a compatibility window, or pull Item 5's
resolver/materialization changes into this work without returning for design review.

---

Next Step: After approval → `my-plan`
