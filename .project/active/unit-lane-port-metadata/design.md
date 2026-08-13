# Design: Unit-Lane Port Metadata

**Status:** Draft — revised after design re-review
**Owner:** Reid W
**Created:** 2026-08-13
**Updated:** 2026-08-13
**Branch:** `item7-rebuild`
**Commit at design:** `906ea5c`
**Epic:** CONSTRAINT-SEMANTICS, Item 8

## Overview

Populate every calculation, constraint-formal, and computed-expression input port from the unit
metadata of its own exact semantic declaration. Do this before the `InstanceGraph` crosses a
projection or snapshot boundary, so valid shared design attributes deduplicate and genuine unit
disagreement continues to refuse.

This is a narrow elaboration repair. It reuses the existing unit extraction precedence, graph-v3
field, projection collision check, v6 codec, and three-route test patterns.

## Related Artifacts

- Approved contract: `.project/active/unit-lane-port-metadata/spec.md`
- Approved review: `.project/active/unit-lane-port-metadata/spec-review.md`
- Design review: `.project/active/unit-lane-port-metadata/design-review.md` (`Rework`)
- Product lens: `.project/active/unit-lane-port-metadata/product-lens.md`
- Epic: `.project/backlog/epic_constraint_semantics_contract.md`, Item 8
- Customer-shape evidence: `.project/completed/20260813_catf-constraint-policy-acceptance/design.md`,
  especially P3/P3b/P4a/P5 and D-S1/D-S2
- Item 6 consumer: `.project/active/calcdef-constraint-gate-design/design.md`
- Item 6 execution contract: `.project/active/calcdef-constraint-gate-design/implementation-item.md`
- Current research: `.project/research/20260812-101200_constraint-semantics-end-to-end.md`
- Architecture: `docs/architecture/modeling-assumptions.md` §§3 and 8,
  `docs/architecture/reference/16-computed-attributes.md`, and
  `docs/architecture/reference/27-snapshot-generation.md`

Product design was deliberately skipped. The product-lens verdict is `PROCEED`: this restores an
existing compiler promise and introduces no model-author choice, syntax, workflow, API, or unit
meaning (`.project/active/unit-lane-port-metadata/product-lens.md`).

## The Point

**[INHERITED: `.project/backlog/epic_constraint_semantics_contract.md`, Item 8; source grade
`[AGENT] (ratified by owner, 2026-08-13)`]** One modeled design attribute must remain one public
entry source when calculations, constraint formals, and computed design attributes consume it.
Each consumer must carry the exact authored unit from its own semantic declaration. Equal metadata
must converge to one public entry point. Unequal metadata must refuse rather than being converted,
normalized, erased, copied from another lane, or split into duplicate public keys. The decided
instance graph must carry the same result through live, in-place snapshot, and relocated snapshot
routes.

## Research Findings

- Calculation bindings already locate one calculation-definition input record, but the lookup
  treats a slot root as the record identity (`src/sysml_codegen/elaboration/elaborate.py:1806-1834`).
  A slot root only groups a redefinition family. The separate
  `FeatureSlotIndex.effective_declaration()` operation selects the declaration that redefines every
  other candidate (`src/sysml_codegen/elaboration/occurrence.py:58-100`).
- Bound constraint ports take no extracted metadata branch, so their units are always `None`
  (`src/sysml_codegen/elaboration/elaborate.py:1664-1695`). Unbound constraint formals only retain a
  modeled-default unit and otherwise also lose the declaration unit
  (`src/sysml_codegen/elaboration/elaborate.py:1716-1754`).
- Computed-expression ports already retain the exact referenced declaration in their port identity,
  then independently follow the data edge through aliases. Their `PortMetadata` omits `unit`
  (`src/sysml_codegen/elaboration/elaborate.py:2270-2332,2334-2409`;
  `src/sysml_codegen/elaboration/identity.py:208-220`). The referenced declaration and ultimate
  data producer are therefore intentionally distinct identities.
- The existing extractor resolves units in a fixed order: feature typing, source syntax, then
  supported documentation syntax. It returns exact text and performs no conversion
  (`src/sysml_codegen/extraction/extractor.py:551-715`).
- `PortMetadata.unit` is already part of the graph model
  (`src/sysml_codegen/elaboration/graph.py:117-125`). Graph-v3 writes and reads it as an optional
  string and fingerprints the resulting payload
  (`src/sysml_codegen/snapshot/instance_graph.py:71,222-291,1020-1061`).
- Projection builds `EntryPoint.unit_text` directly from `PortMetadata.unit`. Candidates for the
  same public key must compare equal or projection raises `SI_RENDERING_COLLISION`
  (`src/sysml_codegen/elaboration/project.py:363-400`). That policy is correct and needs no repair.
- Constraint projection already requires `ConsumerPortId.formal` and
  `formal_provenance.declaration_id` to be identical (`src/sysml_codegen/elaboration/project.py:543-560`).
  A redefined constraint formal must therefore put the selected effective formal in both places;
  retaining the root in one of them is not a compatible option.
- On pinned SysIDE, the existing `constraint_binding_unit_annotation::BandGuard` definition exposes
  no input formals through `definition.features`; its native `definition.usages` contains exact
  loaded-user `ref_value` and `tol` declarations. Occurrence construction already establishes the
  applicable pattern: native `usages`, loaded-user filtering, slot grouping, then
  `effective_declaration()` (`src/sysml_codegen/elaboration/occurrence.py:471-502`;
  `tests/fixtures/constraint_binding_unit_annotation/model.sysml:45-47`).
- The live and admitted routes both extract calculation definitions and call the same elaborator
  (`src/sysml_codegen/orchestration/elaborated_pipeline.py:40-78,100-134`). Existing route-parity
  tests independently compare live elaboration with captured, in-place, and relocated replay
  (`tests/conformance/test_snapshot_v6_routes.py:131-153,201-243`).
- The tracked inventory contains 23 snapshot paths on 2026-08-13. The accepted recapture manifest
  covers only 15 captured members, so its corpus gate cannot prove complete tracked-path coverage
  (`tests/conformance/test_v6_recapture_batch.py:52-54,99-113`).
- Generated entry-point schemas and JSON use name, type, description, and default, but do not read
  `EntryPoint.unit_text` (`src/sysml_codegen/generation/entry_point.py:220-317`). A kept proof and a
  deterministic generated-output digest must still pin that current non-consumption; source search
  alone is not durable evidence.

### Surfaced premise conflicts

Two approved-spec premises conflict with current code. They are explicit here rather than silently
resolved.

1. The spec names `captured_at` as envelope-movement evidence (`spec.md:72-78,194-205`). V6 is
   intentionally deterministic, its exact outer field set excludes `captured_at`, and conformance
   rejects that field (`src/sysml_codegen/snapshot/envelope.py:36-45,114-116`;
   `tests/conformance/test_snapshot_v6_envelope.py:204-224`). This design does not add the field or
   change the envelope. The inventory records envelope SHA movement; the `captured_at` example is
   inapplicable and must not be claimed literally in verification.
2. The v6 envelope promises that any graph it builds or loads is projectable, but both boundary
   paths currently call only graph validation. Metadata collision is detected by `project()`, so a
   correctly re-sealed, diagnostic-free graph with disagreeing units can pass the loader
   (`src/sysml_codegen/snapshot/envelope.py:14-22,171-182,283-301`;
   `src/sysml_codegen/elaboration/graph.py:894-898`). The boundary owner is the envelope, not public
   capture. One envelope certification path must invoke the existing projector during both build
   and load; capture then consumes that guarantee before its atomic write.

The known all-marker suite conflict remains as recorded in the spec. Item 8 requires zero new
failures and an isolated pass for the named TEAx node; it does not claim that the inherited
unconditional full-suite-pass conclusion is true.

## Core Concept

A port does not own a unit and does not borrow one from another consumer. It points to one semantic
feature that owns the unit. Elaboration first selects that feature from a closed identity mapping,
then one shared feature-unit extractor applies the existing precedence and places the exact result
in `PortMetadata.unit`. Projection sees only complete graph metadata and remains responsible for
agreement and disagreement. The v6 envelope uses that projector as its single projectability
certifier on build and load, so capture and replay consume the same boundary guarantee.

This separates three concerns cleanly: elaboration decides declaration-owned metadata, graph-v3
preserves it, and projection enforces equality. No route re-extracts or repairs units.

## Key Bets

- **B1. Exact source declarations are available at elaboration.** On the pinned SysIDE build, a
  selected definition's native `usages` view exposes its inherited and owned input declarations;
  the same loaded-user declaration filter used by occurrence construction removes foreign library
  declarations, the slot index selects the effective declaration within each family, and an
  expression fact retains the exact referenced leaf before alias traversal. *If false → a lane
  would need heuristic or sibling-based metadata, violating the contract.*
- **B2. The current extraction precedence recognizes the customer-authored strings.** The focused
  models can author `m³/s`, `Dimensionless`, and `m` through already-supported forms. *If false →
  this is an extraction-capability defect, and the planned delegation would not make the
  characterizations green.*
- **B3. Graph-v3 is structurally sufficient.** The existing required `unit` key can carry newly
  populated values without changing key shape or interpretation. *If false → the hard no-schema-
  bump premise conflicts with implementation reality and work must stop before any version edit.*
- **B4. Focused models reproduce the same semantic collision as the customer shapes.** They retain
  the shared-source topology without editing `catf_mfe_gated`. *If false → they cannot discharge
  the A9/radius characterization requirement and must be corrected before production work.*

## Key Decisions

- **D1. Use one declaration-owned unit-lane law with a closed source-selection map.** Formal lanes
  map a binding member's slot into the selected definition's effective formal; expression lanes use
  the exact referenced leaf. The resulting declaration goes through one unit extractor. *Rejected:
  treating slot root as effective declaration, following a data edge for metadata, or adding unit
  assignments independently without a closed selection rule.*
- **D2. Extract the existing feature-unit algorithm into a small shared extraction helper.** Both
  `SysMLDataExtractor` and the elaborator call it. *Rejected: importing and instantiating the full
  extractor from elaboration (wrong lifecycle), and passing a new all-feature metadata payload
  through every `elaborate()` caller (a wider API and fixture migration than the defect needs).*
- **D3. Centralize selection in elaboration and extraction in the shared helper.** Private
  elaboration helpers own effective-formal and referenced-leaf selection; the calc, constraint, and
  expression builders call them while constructing ports. No post-pass mutates metadata. *Rejected:
  claiming the extraction helper also selects semantics, and a graph-wide repair pass that would
  have to rediscover them.*
- **D4. Keep the projector's complete-candidate comparison unchanged.** Agreement deduplicates and
  disagreement raises the existing `ProjectionError`. *Rejected: first-wins, unit erasure,
  conversion, normalization, or separate public keys (all lose model meaning).*
- **D5. Enforce projectability at the v6 envelope boundary.** One shared envelope certifier runs
  graph validation and the existing projector. Both `build_envelope()` and decoded-graph validation
  call it. Capture relies on `build_envelope()` and adds no parallel policy. Projection diagnostics
  are preserved structurally on `SnapshotCertifiabilityError`, and CLI paths render their exact
  codes and details. *Rejected: capture-only certification, strengthening graph validation through
  a circular projector dependency, or copying projector comparison rules into snapshots.*
- **D6. Keep instance-graph/v3, snapshot v6, and `instance-projector/v1`.** This change populates an
  existing value and invokes existing projection semantics. *Rejected: precautionary version bumps
  without a shape or interpretation change.*
- **D7. Use five small, snapshot-free licensed fixtures.** Separate A9, radius, constraint mismatch,
  computed mismatch, and source-identity models keep each proof independently addressable.
  *Rejected: editing the Item 9 CATF fixture, and one large model whose first collision hides later
  lanes.*
- **D8. Use a complete tracked-path assessment, then one conditional recapture batch.** Git's
  tracked path set is the scope authority. *Rejected: the historical 15-path batch subset, a count-
  only check, or unconditional recapture.*
- **D9. Record generated entry-point output as evidence, not as a staleness trigger.** Each
  projectable assessment arm hashes the deterministic schema/JSON file set produced from its
  entry-point groups. *Rejected: assuming no movement from a source search, hashing only projected
  population counts, or widening recapture beyond the exact graph-payload rule.*

## Architecture

### Unit-lane resolution law

For every consumer input port `p`:

`unit(p) = authored_default_unit(p) ?? exact_feature_unit(source_declaration(p))`

`authored_default_unit(p)` is non-null only for an unbound selected formal with a modeled unit
annotation. A bound actual never supplies this value; its unit still comes from the consumer
declaration. `??` means first non-null exact string, with no normalization or conversion.

The source declaration is determined by semantic identity, never by route or by another consumer.
A slot root is only a family key; it is never accepted as the effective declaration merely because
it is the root.

| Consumer shape | `source_declaration(p)` | Selection evidence |
|---|---|---|
| Base formal on the selected calculation definition | The base formal itself, because it is the sole effective input candidate in its slot | selected definition's filtered native `usages` view |
| Redefined formal on the selected calculation definition | The unique redefining formal selected from that definition's candidates for the binding member's slot | `FeatureSlotIndex.effective_declaration()` |
| Base formal on the selected effective constraint definition | The base formal itself, because it is the sole effective input candidate in its slot | selected definition's filtered native `usages` view |
| Redefined formal on the selected effective constraint definition | The unique redefining formal selected from that definition's candidates for the binding member's slot | `FeatureSlotIndex.effective_declaration()` |
| Computed input that names a design attribute, including an alias | The exact referenced leaf declaration before alias traversal | `ExpressionPortId.referenced_declaration` / resolved leaf fact |

For either formal lane, elaboration first identifies the definition selected by the usage's exact
`FeatureTyping`. It enumerates `definition.usages`, then applies the occurrence builder's existing
loaded-user rule: retain only supported directed input declarations whose exact IDs occur in the
precomputed loaded-user input-declaration index, analogous to occurrence construction's
`usages_by_id`. This excludes inherited standard-library declarations that do not belong to the
loaded user model. The selector groups the retained IDs by
`FeatureSlotId` and calls `FeatureSlotIndex.effective_declaration()` exactly as occurrence
construction does (`src/sysml_codegen/elaboration/occurrence.py:471-502`). A bound usage member maps
its slot to that winner. An unbound port iterates those winners directly. No winner, multiple
effective winners, a direction mismatch, or a winner outside this filtered native view is
`SI_REDEFINITION_INVALID`/`SI_EDGE_DANGLING`, not a fallback to the root.

The private elaboration interfaces are deliberately small:

- `_effective_input_formals(definition) -> dict[FeatureSlotId, DeclarationId]` builds and validates
  the selected definition's closed slot-to-effective-formal map from `definition.usages` filtered
  by the elaborator's precomputed loaded-user input-declaration index.
- `_unit_source_for_formal(definition, bound_or_unbound) -> DeclarationId` resolves through that map.
- `_unit_source_for_reference(referenced) -> DeclarationId` validates and returns the exact leaf.

All unit lookups then call `extract_feature_unit(feature, *, model_paths=()) -> str | None`. The
first three functions select identity; the last function extracts exact text. This is the honest
centralization boundary.

Structural port identity and metadata source are recorded and tested as distinct facts where the
current graph model makes them distinct. A bound calculation keeps its existing usage-member port
identity, while the exact calc-definition payload match and unit source use the selected effective
formal ID rather than re-rooting it. Item 8 does not add calc-input `formal_provenance`; Item 6 owns
that later schema work. A bound constraint uses the selected effective formal for both
`ConsumerPortId.formal` and existing `formal_provenance`, as the projector already requires those
identities to agree. Port and metadata schemas remain unchanged; exact IDs, metadata values, and
fingerprints may change as the contract requires.

Alias traversal answers where the value comes from; it does not answer which declaration owns the
computed consumer's metadata. If an expression names alias declaration `a` and `a` resolves to
source `x`, the expression port retains `a`, takes its unit from `a`, and its input edge follows to
`x`. This follows the spec's “exact referenced design attribute” rule. The alias must therefore
author metadata that agrees with other consumers of the eventual public source; if it does not,
projection refuses. Treating `x` as the metadata owner would silently erase the alias's authored
contract and couple metadata selection to dataflow traversal.

`exact_feature_unit` preserves the existing precedence and exact return string. It neither follows
the resolved data edge to a sibling consumer nor inspects arithmetic. Existing unbound-formal
modeled-default handling remains a common outer rule: an authored unit carried by the resolved
modeled default wins, otherwise the exact feature unit is used. This applies equally to unbound
calculation and constraint formals; it is not a route exception.

The elaboration-local lookup refuses a missing or non-feature declaration through the existing
exact-ID invariant error family. It must not silently return `None` for an identity failure. A real
selected feature with no authored unit legitimately resolves to `None`.

### Data flow

1. The loader provides the live SysIDE model, source paths, and extracted calculation definitions.
2. Formal port construction selects the effective declaration within the chosen definition; an
   expression port retains its exact referenced leaf before following aliases.
3. The shared helper reads feature typing, source syntax, and documentation in the current order.
4. Elaboration stores the returned string or real `None` on the port's `PortMetadata`.
5. Graph validation completes; graph-v3 serialization writes the existing `unit` key.
6. The v6 envelope certifies the graph by invoking the existing projector at build and load.
7. Live projection and both snapshot replay routes read `metadata.unit` into
   `EntryPoint.unit_text`.
8. Equal complete candidates become one entry point. Any unequal candidate pair refuses the whole
   projection with `SI_RENDERING_COLLISION`.

### Envelope projectability certification

`snapshot/envelope.py` owns one certifier used by both `build_envelope()` and `_decode_graph()`.
It first runs `InstanceGraph.require_projectable()` for graph validation and diagnostics, then calls
the existing `project(graph)` and discards the computation graph. It copies no comparison rule.
Its private interface is `_require_certifiable(graph: InstanceGraph) -> None`.

Graph-validation and projection failures are mapped to `SnapshotCertifiabilityError`. That error
retains the original ordered `Diagnostic` tuple on a public `diagnostics` attribute and renders each
exact code and detail in its message. A unit mismatch therefore remains auditable as
`SI_RENDERING_COLLISION`, the conflicting public key, and “conflicting projected metadata”; it is
not reduced to “invalid snapshot.” Exception chaining retains the original `ProjectionError`.

`capture_instance_graph_snapshot()` performs admission, elaboration, envelope construction, and
atomic write as it does today. It does not call `project()` directly. A build-time certification
failure occurs before envelope encoding and `_write_atomically()`, so a missing destination remains
missing and a sentinel destination remains byte-identical. The snapshot CLI catches the existing
snapshot base error and prints the structured certifiability detail before exiting 1. Generation
from a snapshot already catches that public base; it receives the same exact diagnostic after load.

Both envelope entry points use the same helper. A correctly re-sealed envelope cannot bypass it:
after outer integrity and graph fingerprint checks, the loader decodes graph-v3 and certifies the
decoded graph. The check does not serialize a computation graph or create a new authority marker.
It makes the current `projectable-instance-graph/v1` claim true without changing its meaning.

### Graph-v3 and three-route parity

The route proof starts from licensed live elaboration, captures the same fixture through public v6
capture, loads it in place, copies it to a different directory, removes access to the staged source
tree, and loads it again. It compares:

- the exact selected calc, constraint, and expression `PortMetadata` records, including `unit`;
- the graph-v3 payload's existing `unit` members and schema marker;
- the projected public key set and exact `EntryPoint.unit_text` values; and
- one-entry cardinality for each shared design attribute.

The test does not hide unit differences behind the existing source-path mask. In-place and
relocated loading never call the feature-unit resolver; their sole authority is decoded graph-v3
metadata.

## Required Invariants

1. Every consumer port has exactly one semantic source declaration before unit resolution.
2. A slot root groups redefinitions; only effective-declaration selection chooses a formal source.
3. A formal source belongs to the definition selected by the usage's exact typing and is the unique
   effective input declaration for the bound slot.
4. A computed port's referenced declaration owns metadata even when its data edge follows an alias.
5. The closed source mappings above are the only unit-lane mappings.
6. A missing declaration is an elaboration invariant failure; an authored-unit absence is `None`.
7. Unit extraction preserves exact case, symbols, superscripts, punctuation, and spelling.
8. No unit is copied from a sibling port, inferred from an expression, converted, or normalized.
9. Equal complete entry candidates, including all-`None`, deduplicate to one public entry.
10. `m` versus `cm`, `m` versus another spelling, and non-null versus `None` all refuse with
   `SI_RENDERING_COLLISION`; no partial computation graph or generated package is returned.
11. `PortMetadata.unit` is final before the graph is encoded or projected.
12. Graph-v3 round-trip preserves the unit string exactly on every relevant port.
13. Envelope build and load both certify projectability through the same existing projector.
14. Certifiability errors retain exact ordered projection diagnostics and their public keys.
15. Live, in-place, and relocated routes project identical public unit text.
16. Failed public capture performs no destination replacement.
17. Each projectable census row records deterministic computation and generated entry-point output
    digests; these are movement evidence, not staleness triggers.
18. The tracked inventory and assessment row sets are exactly equal and contain no duplicates.
19. Recapture is zero times for an empty stale set; otherwise it is one reviewed batch containing
    every and only stale path after code and tests are final.
20. Item 8 never changes schema/version markers unless contradictory evidence is surfaced and the
    contract is revisited first.

## Component Overview

### Production files likely to change

- `src/sysml_codegen/extraction/feature_metadata.py` — new small owner for exact feature
  documentation and unit extraction. Its public interface is
  `extract_feature_unit(feature, *, model_paths=()) -> str | None`; it contains the current
  type/source/documentation precedence and source-file fallback.
- `src/sysml_codegen/extraction/extractor.py` — delegates its current documentation/unit work to
  the shared helper so calculation-definition extraction remains the reference behavior rather
  than a parallel implementation.
- `src/sysml_codegen/elaboration/elaborate.py` — accepts source paths as an optional keyword for
  the existing source-syntax fallback; selects effective formals from the selected definition's
  native `usages` view with a precomputed loaded-user input-declaration index and the existing
  slot/effective selector; matches calc payloads by that exact winner; keeps alias metadata on the
  referenced leaf; and applies the shared extractor to all three lanes.
- `src/sysml_codegen/orchestration/elaborated_pipeline.py` — supplies live or admitted staged model
  paths to `elaborate()` in its two production calls.
- `src/sysml_codegen/snapshot/envelope.py` — adds the one projectability certifier used by envelope
  build and decoded-graph load; preserves structured graph/projection diagnostics on
  `SnapshotCertifiabilityError`.
- `src/sysml_codegen/cli/__init__.py` — handles build-time snapshot certifiability refusal in
  `cmd_snapshot` and renders exact diagnostic codes/details. Its generate-from-snapshot path keeps
  using the existing `InstanceGraphSnapshotError` base.

### Existing authorities that should not change

- `src/sysml_codegen/elaboration/graph.py` — `PortMetadata` and graph validation stay structurally
  unchanged.
- `src/sysml_codegen/elaboration/project.py` — equality, `unit_text`, and
  `SI_RENDERING_COLLISION` behavior stay unchanged.
- `src/sysml_codegen/snapshot/instance_graph.py` — graph-v3 codec shape and marker stay unchanged.
- `src/sysml_codegen/snapshot/capture.py` — continues to consume `build_envelope()` before its
  existing atomic write; no direct projection policy is added.

### Tests and fixtures likely to change

- `tests/fixtures/unit_lane_a9/model.sysml` — four constraint lanes with the A9 shared-source shape.
- `tests/fixtures/unit_lane_radius/model.sysml` — computed `outer_radius` reads authored length
  attributes also consumed by `TorusMinorRadius`.
- `tests/fixtures/unit_lane_constraint_disagreement/model.sysml` — same source with calc/constraint
  formal unit disagreement (`m` versus `cm`).
- `tests/fixtures/unit_lane_computed_disagreement/model.sysml` — same source with calc/computed
  disagreement using exact unequal spellings. None of these fixtures gets a committed snapshot.
- `tests/fixtures/unit_lane_source_identity/model.sysml` — selected base and derived calc/constraint
  definitions carry distinguishable base/redefining units, and a computed expression references an
  alias whose unit differs from its ultimate source. It has no committed snapshot.
- `tests/conformance/test_unit_lane_port_metadata.py` — customer characterizations, four agreement/
  disagreement proofs, base/redefinition/alias identity proofs, three-route parity, and public
  capture no-overwrite proof.
- `tests/conformance/test_extractor.py` — shared-helper precedence and exact-text regression coverage.
- `tests/conformance/test_elaboration_projection.py` — a direct non-null-versus-`None` collision
  invariant, independent of parser behavior.
- `tests/conformance/test_snapshot_v6_envelope.py` — a correctly re-sealed, graph-valid envelope
  with colliding port metadata is refused on load with exact structured diagnostics.
- `tests/conformance/test_cli_snapshot_refusal.py` — capture certifiability becomes exit 1 with an
  exact typed message and no output replacement.
- `tests/conformance/test_entry_point_generation.py` — changing only `EntryPoint.unit_text` leaves
  the deterministic generated entry-point schema/JSON tree unchanged, pinning the current generator
  boundary.

### Census and evidence files likely to change

- `scripts/assess_v6_snapshot_churn.py` — read-only complete inventory/assessment plus a guarded
  `--recapture-reviewed` mode. It derives scope from `git ls-files`, never from the accepted batch.
- `tests/conformance/test_v6_snapshot_inventory.py` — license-free checks for exact tracked-set row
  equality, duplicate rejection, and assessment/receipt shape.
- `.project/active/unit-lane-port-metadata/snapshot-inventory-pre.json` — immutable pre-production
  measurement.
- `.project/active/unit-lane-port-metadata/snapshot-inventory-final.json` — final live assessment
  and stale-set decision.
- `.project/active/unit-lane-port-metadata/verification.md` — exact commands, counts, proof nodes,
  conflicts, and Item 6 citation bundle.
- `.project/active/unit-lane-port-metadata/v3-recapture.json` — created only if the stale set is
  non-empty; records the one reviewed batch and per-path before/after evidence.
- `tests/fixtures/v6_recapture_batch/batch.json` and tracked snapshot JSON files — conditional only;
  only affected accepted-batch records and every/only stale snapshot may change.

## Non-Goals

- Item 9 model migration or any edit to `tests/fixtures/catf_mfe_gated`.
- Item 7 product/reference documentation work.
- Item 6 production code, calc-input `formal_provenance`, graph v4, catalog 4, TEAx changes, or a
  graph-v4 recapture.
- New unit syntax, unit conversion, dimensional analysis, arithmetic inference, or spelling
  normalization.
- Changes to executable-profile operand categories or constraint policy.
- A new public API, snapshot envelope field, or schema/version bump.
- Repairing the pre-existing all-marker collection-order failure.

## Implementation Notes

### First proofs must stay red for the right reason

Land these two tests and fixtures before production changes:

- `tests/conformance/test_unit_lane_port_metadata.py::test_a9_constraint_formals_preserve_authored_units`
- `tests/conformance/test_unit_lane_port_metadata.py::test_radius_derivation_inputs_preserve_authored_units`

The pre-change record must name exception type `ProjectionError`, code
`SI_RENDERING_COLLISION`, and the exact public keys already measured by Item 5:

- `CATFMFEVacuum__catf_vacuum_pumping__n_pumps`
- `CATFMFERadialBuild__catf_radial_build__plasma_region__inner_radius`

After repair, A9 must inspect all four lanes: `observed` and `each_capacity` are `m³/s`; `count`
and `rel_tol` are `Dimensionless`. Radius must inspect every minted derivation input entry and the
shared `TorusMinorRadius` source as `m`. A first-collision-only green result is insufficient.

### Exact proof nodes

The kept proof interface is fixed for later citation:

| Proof | Exact node | Required claim |
|---|---|---|
| Constraint/calc agreement | `tests/conformance/test_unit_lane_port_metadata.py::test_constraint_and_calculation_unit_agreement_projects_one_entry` | both ports carry the same non-null unit; one public key has that exact text |
| Constraint/calc disagreement | `tests/conformance/test_unit_lane_port_metadata.py::test_constraint_and_calculation_unit_disagreement_refuses` | `m` versus `cm` refuses the whole projection with exact code and key; no conversion |
| Computed/calc agreement | `tests/conformance/test_unit_lane_port_metadata.py::test_computed_and_calculation_unit_agreement_projects_one_entry` | referenced-attribute and calc-formal ports agree; one public key remains |
| Computed/calc disagreement | `tests/conformance/test_unit_lane_port_metadata.py::test_computed_and_calculation_unit_disagreement_refuses` | unequal exact strings refuse with exact code and key; no normalization |
| Three-route parity | `tests/conformance/test_unit_lane_port_metadata.py::test_live_in_place_and_relocated_routes_preserve_unit_metadata` | exact port records and projected unit text agree through graph-v3 on all routes |

`tests/conformance/test_elaboration_projection.py::test_unit_text_and_missing_unit_remain_a_rendering_collision`
separately pins non-null versus `None`. The two disagreement fixtures pin distinct non-null text.
Together they cover every disagreement class without teaching elaboration to compare units itself.

### Redefinition and alias identity proofs

These additional kept nodes close the semantic-selection boundary; they are not substituted for the
five Item 6-consumed proofs:

- `tests/conformance/test_unit_lane_port_metadata.py::test_band_guard_base_formals_are_selected_from_definition_usages`
- `tests/conformance/test_unit_lane_port_metadata.py::test_calc_redefinition_uses_selected_effective_formal_unit`
- `tests/conformance/test_unit_lane_port_metadata.py::test_constraint_redefinition_uses_selected_effective_formal_unit`
- `tests/conformance/test_unit_lane_port_metadata.py::test_computed_alias_uses_referenced_declaration_unit`

The direct base-formal test loads the existing
`tests/fixtures/constraint_binding_unit_annotation/model.sysml` `BandGuard` definition and invokes
the selector before projection. It asserts the candidate map is non-empty and exactly contains:

- slot `a25d4eca-7e4c-55fd-88af-e2b703d539e4` → effective `ref_value` declaration with that ID; and
- slot `8540a49e-c62d-5b4b-b96c-a31d5f85e7ee` → effective `tol` declaration with that ID.

It also asserts both selected objects come from `BandGuard.usages`, are loaded-user `in`
declarations, and match the two bound `band` member slots. This test fails directly if candidate
enumeration is empty, even if a later projection shape would happen not to collide.

The calc case selects a derived calculation definition whose base formal is `cm` and redefining
formal is `m`; the design attribute and comparison consumer expect `m`. The constraint case uses
the same distinguishable base/redefining units on a selected derived constraint definition. Each
test records the binding member ID, slot root ID, selected definition ID, effective formal ID,
structural port ID, metadata unit, and one public entry key. Correct convergence on `m` proves the
root was used only for grouping. A companion assertion exercises the selected base definition and
proves its unredefined base formal remains the source.

The alias case gives referenced alias `a` unit `m` and its ultimate source `x` unit `cm`. A computed
expression names `a`; a calculation formal for the shared public source is `m`. The test asserts the
`ExpressionPortId` names `a`, the resolved edge reaches `x`, the port unit is `m`, and projection
mints one entry for `x`. Choosing the post-alias source would produce `cm` and the exact collision,
so this shape distinguishes the two policies without conversion. The existing computed mismatch
fixture separately confirms that genuinely unequal consumer declarations remain fail-closed.

All three shapes are included in the live/in-place/relocated unit parity test. Their route check
compares structural port identity and metadata, not only projected output.

### Envelope projectability proof

`tests/conformance/test_snapshot_v6_envelope.py::test_resealed_unit_collision_is_not_certifiable`
starts from a valid captured v6 document, changes two ports for one public source to unequal units,
recomputes the graph-v3 fingerprint and outer digest, and loads the result. It must raise
`SnapshotCertifiabilityError` whose first diagnostic is `SI_RENDERING_COLLISION` and whose detail
names the public key and conflicting projected metadata. This proves refusal survives a coherent
adversarial re-seal.

`tests/conformance/test_unit_lane_port_metadata.py::test_capture_unit_collision_does_not_replace_destination`
and
`tests/conformance/test_unit_lane_port_metadata.py::test_capture_unit_collision_does_not_create_destination`
retain the public capture guarantee. The CLI proof checks exit 1, no traceback, no replacement, and
the same code/key in the logged message.

### Complete inventory and conditional recapture

The assessment command passes the Git pathspec as a literal argument, equivalent to
`git ls-files -z 'tests/fixtures/**/instance_graph_snapshot.json'`, without shell expansion. It sorts
that set and refuses to emit an assessment
unless row paths equal it exactly and duplicate, missing, and extra counts are all zero. Each row
records:

- path and fixture root;
- envelope SHA-256, instance-graph fingerprint, and canonical source-manifest fingerprint;
- projected counts or typed projection refusal and the deterministic computation-graph digest;
- for every projectable arm, a generated entry-point output digest over sorted relative paths and
  exact bytes for production-generated parameter schema and JSON files;
- every relevant port identity with null/non-null unit text; and
- a temporary admitted live elaboration comparison against the committed exact graph payload.

The live comparison uses admission plus elaboration in a temporary workspace without writing the
tracked destination. A row is stale if and only if the final live encoded instance-graph payload
differs from the committed `instance_graph` document, or its relevant unit map differs. Source
manifest, envelope SHA, computation digest, generated entry-point digest, and projected counts are
recorded diagnostics. They do not decide staleness. A projection refusal records the exact type,
ordered codes, and details and marks generated output inapplicable rather than inventing a digest.
Unrelated graph or generated-output movement is a review stop, not accepted churn.

A committed graph that is structurally valid but fails projection is named in the pre-change
assessment. If its refusal is the manufactured missing-unit collision repaired by Item 8, final
live metadata differs and the exact graph-payload rule makes it stale. If the refusal is unrelated
and final live payload is unchanged, recapture cannot cure it and projected output is inapplicable;
the review stops for a separate disposition rather than expanding the stale trigger or weakening
envelope certification.

The generated digest uses the production entry-point schema and JSON generators in a temporary
directory with a fixed package name. It hashes a canonical sequence of sorted relative path, byte
length, and file bytes. An empty but projectable entry-point file set has the canonical empty-set
digest; it is not omitted. The kept node
`tests/conformance/test_entry_point_generation.py::test_entry_point_unit_text_does_not_change_generated_schema_or_json`
projects two otherwise identical graphs whose only difference is `unit_text`, generates both file
sets, and requires byte identity. This pins the current code fact that entry-point generation does
not consume unit text (`src/sysml_codegen/generation/entry_point.py:220-317`).

The pre-production artifact must show the dated 23-path set. The final artifact re-derives the
then-current tracked set, lists its exact count, and names every addition/removal with authority.
The new characterization fixtures remain snapshot-free, so this design expects no path additions;
the check, not that expectation, decides.

If the final stale set is empty, `--recapture-reviewed` refuses to run and no existing snapshot or
batch record changes. If non-empty, review first confirms production and focused tests are final,
row/tracked set equality, the exact stale set, only explained graph/unit movement, and graph-v3/v6
markers. The review also classifies old/new computation and generated entry-point digests for every
projectable row; expected derived movement is named, and unexpected generated bytes stop the
recapture. Then one invocation stages public captures for all and only stale fixtures. It promotes
nothing unless every candidate captures, round-trips, projects, reproduces its reviewed generated
digest, and passes route parity. The same invocation updates affected historical batch
digests/outcomes and emits `v3-recapture.json`.

After promotion, a read-only verification proves every stale path changed as reviewed, every
non-stale existing snapshot stayed byte-identical, affected batch records match, and final rows
still equal the tracked set. A schema or envelope marker difference aborts instead of bumping it.

## Potential Risks

- **Resolver drift while extracting the helper.** Mitigation: run existing extractor coverage before
  and after; require calculation formal units to remain byte-for-byte equal; add precedence tests.
- **Rooting the wrong declaration.** Mitigation: lane tests inspect port identity as well as unit;
  the slot root only keys the selected definition's candidate family, and focused tests make base
  and redefining units distinguishable.
- **Following an alias for metadata.** Mitigation: the alias proof distinguishes referenced and
  ultimate declarations by unit, then separately asserts expression-port identity and resolved edge.
- **A shared source-file fallback behaves differently in admitted staging.** Mitigation: pass the
  same model-path set used by each loader and exercise source-syntax units on live and admitted
  routes.
- **Envelope certification exposes existing graph-valid/project-invalid fixtures.** Mitigation: run
  the complete pre-change assessment and envelope/capture/CLI tests before accepting production
  changes; distinguish Item 8-repaired refusal from unrelated contract violations, and surface any
  unrelated path rather than weakening certification or recapturing identical invalid content.
- **A recapture hides unrelated graph churn.** Mitigation: exact payload diffs and per-field review
  precede the sole mutating batch; computation and generated-output digests expose downstream
  movement, and unrelated movement is a stop.
- **The existing full-suite failure obscures regressions.** Mitigation: compare exact pre/final node
  sets, require default tests to pass, and run the known node in isolation at both baselines.

## Integration Strategy

The shared helper becomes the single owner of existing feature-unit extraction. The elaborator
separately owns the closed semantic-declaration selection map. It retains current ordering, binding
evidence, expression identity, and graph validation while correcting constraint provenance and calc
payload lookup to the selected effective formal. The projector and codec remain stable consumers.
The envelope composes existing graph validation and projection into the build/load guarantee;
public capture consumes it before its existing atomic write.

The work lands standalone. Only after final verification and an immutable reviewed Item 8 commit
does a documentation-only handoff update the named Item 6 records. No Item 7 or Item 9 file is part
of integration.

## Validation Approach

Validation proceeds in gates:

1. **Pre-change gate.** Record the complete 23-path inventory, the two red characterizations, the
   focused baseline, default maintained suite, all-marker suite, known failing node in isolation,
   static checks, and license-skip-line count.
2. **Unit-law gate.** Prove the direct `BandGuard` base-formal selector from filtered
   `definition.usages`; shared-helper precedence; base and redefining formal selection for calc and
   constraint definitions; referenced-alias versus ultimate-source behavior; the A9 four-lane
   strings; and all radius strings.
3. **Agreement/refusal gate.** Run the four exact proof nodes. Assert one public entry on agreement;
   assert `ProjectionError`, `SI_RENDERING_COLLISION`, exact key/detail, and no returned graph/package
   on disagreement. Add direct non-null/`None` coverage.
4. **Persistence gate.** Assert graph-v3 encode/decode and exact live/in-place/relocated port and
   entry-point parity. Delete or detach source staging before relocated replay.
5. **Envelope/capture gate.** Correctly re-seal colliding metadata and prove envelope load refuses
   with exact structured diagnostics. Assert public API and CLI refuse before write, preserve a
   sentinel destination byte-for-byte, and never create a missing destination.
6. **Generated-output gate.** Prove changing only entry-point unit text leaves production-generated
   parameter schemas and JSON byte-identical; record computation and generated-output digests for
   both committed and final-live arms of each applicable inventory row.
7. **Churn gate.** Produce and review the final exact-set assessment. Run zero recaptures for an
   empty set or one guarded final-schema batch for every/only stale path, then verify the receipt.
8. **Repository gate.** Run focused licensed tests, graph codec tests, affected batch checks,
   default `pytest tests/`, all-marker `pytest tests/ -m ""`, the known node in isolation, changed-
   file and full-source ruff, mypy, license-free snapshot checks, and `git diff --check` with the
   exact interpreter and environment required by the spec.

Final `verification.md` records invocations and exact collected/passed/skipped/deselected/xfailed/
xpassed/failed/error counts. A license skip is not a licensed pass. The all-marker result is zero-
new against its pre-change node set, not silently relabeled as an unconditional pass.

## Item 6 Evidence Handoff

Before any downstream edit, Item 8 `verification.md` publishes:

- the five exact proof nodes in the table above and the claim/result for each;
- both customer characterization nodes with pre-fix exception/code/key and post-fix exact strings;
- both disagreement classes, exact exception type, code, public key, and metadata values;
- the base/redefined calc-formal, base/redefined constraint-formal, and alias-reference proof nodes,
  including structural port, source declaration, chosen unit, and resolved edge where applicable;
- graph-v3 live/in-place/relocated port records and projected unit text;
- sorted pre and final tracked snapshot path sets, counts, set-equality results, additions/removals,
  and every per-path disposition;
- per-path computation and generated entry-point output movement, including typed inapplicability;
- the zero-recapture decision or the reviewed v3 recapture receipt and affected batch evidence; and
- the exact test/static command results, known baseline conflict, and license evidence.

After review produces a full immutable Item 8 implementation-and-test SHA, make one narrow
documentation-only handoff into:

- `.project/active/calcdef-constraint-gate-design/design.md`, R5, R8, and the component-manifest
  recapture entry; and
- `.project/active/calcdef-constraint-gate-design/implementation-item.md`, Start gate and exact
  dependency pins, Item 8 ownership gate, and Phase 4.

Those records cite the full SHA, exact nodes, exact claims, Item 8 final sorted path set and count,
and v3 recapture disposition. They must say that Item 6 re-derives its own graph-v4 path set from
the tracked repository at its immutable baseline. They must not replace a stale number with Item
8's count, cite the 15-path batch subset as complete, or implement/authorize Item 6.

## Next-Stage Handoff

The implementation plan should treat these as fixed:

- the declaration-owned unit-lane law and source table;
- slot root as family identity, selected effective formal as formal metadata source, and exact
  referenced leaf as alias metadata source;
- the shared extraction helper plus the closed elaboration source selector rather than
  consumer-specific repairs;
- red A9 and radius characterizations before production edits;
- unchanged projection refusal and no conversion/normalization;
- graph-v3/v6/projector-v1 markers unless a surfaced conflict stops work;
- shared envelope build/load projectability certification before capture can write;
- exact five-node Item 6 proof interface;
- exact tracked-path census with computation/generated-output evidence and conditional zero-or-one
  recapture; and
- the standalone ownership boundary.

The first implementation risk to de-risk is declaration selection: prove base, redefining, and alias
cases before freezing the helper interface. The second is envelope certification: measure which
current fixtures are graph-valid but projection-invalid before accepting any recapture disposition.
The shared extractor refactor must separately prove the calc lane's existing base-formal output is
unchanged.

No technical design question remains open. The stale snapshot set is intentionally unknown until
the final machine assessment.

## Design Review Disposition

Review source: `.project/active/unit-lane-port-metadata/design-review.md` (`Rework`, 2026-08-13).
Every must-fix finding is resolved in this revision:

| Finding | Disposition | Auditable correction |
|---|---|---|
| **DR-1 — projectability at the wrong boundary** | **Resolved.** | D5 and Envelope projectability certification now give `snapshot/envelope.py` one certifier used by build and load. Capture consumes `build_envelope()` and carries no direct projector policy. `SnapshotCertifiabilityError.diagnostics` retains the exact `SI_RENDERING_COLLISION` code/key/detail. The required re-sealed-loader, missing-destination, sentinel no-overwrite, and CLI mapping proofs are named. No marker changes. |
| **DR-2 — redefinition and alias identity unresolved** | **Resolved.** | D1/D3 and the unit-lane table distinguish slot root from effective declaration. Base and redefining calc/constraint formals are selected within the usage's exact selected definition. Computed metadata stays on the referenced alias declaration while data edges follow aliases. Three exact kept identity nodes assert port/source IDs, distinguishable units, convergence/refusal, and three-route parity. Calc `formal_provenance` remains Item 6-owned. |
| **DR-3 — projected/generated movement omitted** | **Resolved.** | D9 and Complete inventory add computation digest plus a deterministic production-generated entry-point schema/JSON digest to every projectable row, with typed inapplicability on refusal. Pre/final classification and recapture review include both surfaces, while exact graph payload/unit movement remains the only stale trigger. A kept generation-boundary proof pins current non-consumption of `unit_text`. |
| **RDR-1 — wrong SysIDE collection for effective formals** | **Resolved.** | The selector now enumerates the selected definition's live `definition.usages`, applies the same loaded-user declaration filter used by occurrence construction, groups by slot, and calls the existing `effective_declaration()` selector. It never substitutes the slot root for the winner. The exact `BandGuard` base-formal node asserts the non-empty two-row map and its known declaration IDs before projection; the planned calc/constraint redefinition and referenced-alias proofs remain. |

The review's pressure-tested decisions remain unchanged: exact-text/no-conversion refusal, existing
projector comparison, graph-v3 and v6 markers, red A9/radius characterizations, exact tracked-set
census, conditional single v3 recapture, and the documentation-only Item 6 handoff. The review's
product-lens finding is answered structurally by moving certification to the envelope owner; this
revision does not edit or rerun product-lens work.

RDR-1 changes only candidate enumeration. It does not reopen the accepted DR-1 through DR-3
mechanisms: the envelope still owns certification, computed metadata still belongs to the referenced
alias declaration, calc-input `formal_provenance` remains Item 6 scope, downstream computation and
generated-entry-point evidence remains complete, and only exact graph/unit movement triggers
recapture.

## Next Steps

Run `my-design-review` in a fresh review stage. After approval, use `my-plan` to sequence the red
characterizations, narrow production changes, validation, conditional recapture, and Item 6
documentation handoff. Do not begin implementation from this design stage.

## Appendix A: Current Tracked Snapshot Baseline

The dated pre-design command `git ls-files 'tests/fixtures/**/instance_graph_snapshot.json'`
returned these 23 paths. The implementation gate must re-derive rather than copy this list:

1. `tests/fixtures/agg_literal_probe/instance_graph_snapshot.json`
2. `tests/fixtures/attr_expr_probe/instance_graph_snapshot.json`
3. `tests/fixtures/catf_mfe_d5/instance_graph_snapshot.json`
4. `tests/fixtures/catf_mfe_gated/instance_graph_snapshot.json`
5. `tests/fixtures/chain_spike_d5/instance_graph_snapshot.json`
6. `tests/fixtures/constraint_domain_satisfy_calc_def/instance_graph_snapshot.json`
7. `tests/fixtures/constraint_inline/instance_graph_snapshot.json`
8. `tests/fixtures/constraint_multi_instance/instance_graph_snapshot.json`
9. `tests/fixtures/constraint_non_numerical/instance_graph_snapshot.json`
10. `tests/fixtures/constraint_occurrence_demand_overrides_d5/instance_graph_snapshot.json`
11. `tests/fixtures/d38_caret/instance_graph_snapshot.json`
12. `tests/fixtures/deep_cross_scope_probe/instance_graph_snapshot.json`
13. `tests/fixtures/fusion_tea/instance_graph_snapshot.json`
14. `tests/fixtures/gate_a_d5/instance_graph_snapshot.json`
15. `tests/fixtures/modeled_default_fidelity/instance_graph_snapshot.json`
16. `tests/fixtures/nested_occurrence_override_probe/instance_graph_snapshot.json`
17. `tests/fixtures/quoted_owner_formula/instance_graph_snapshot.json`
18. `tests/fixtures/retype_model/instance_graph_snapshot.json`
19. `tests/fixtures/sample_model/instance_graph_snapshot.json`
20. `tests/fixtures/shadowed_reference/instance_graph_snapshot.json`
21. `tests/fixtures/solar_battery_d5/instance_graph_snapshot.json`
22. `tests/fixtures/unresolvable_attr_probe/instance_graph_snapshot.json`
23. `tests/fixtures/wi014_toy/instance_graph_snapshot.json`

---

Next Step: After design approval, run `my-design-review`, then `my-plan`.
