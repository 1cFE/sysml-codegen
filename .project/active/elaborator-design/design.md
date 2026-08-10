# Design: Production Elaborator + Exact Identity Bridge

**Date:** 2026-08-08
**Status:** Owner-approved architecture — all design-review corrections incorporated
**Owner:** Reid W
**Branch:** `source-identity-epic`
**Base commit:** `6bed968`

## Overview

The elaborator resolves each SysIDE semantic reference to a concrete graph value exactly once,
while the live AST and occurrence context are available. SysIDE element UUIDs identify declarations;
structured occurrence IDs identify concrete instances; graph edges store the resulting node or
output-port IDs directly. Names are rendered only after semantic identity is settled.

This revision replaces the prior D1/D5/D6 mechanics that used rendered occurrence paths and
resolved member names as lookup keys.

## Related Artifacts

- Spec: `.project/active/elaborator-design/spec.md`
- Epic: `.project/backlog/epic_elaborate_first_architecture.md`
- Architecture research: `.project/research/20260807-145336_elaborate-first-instance-graph-architecture.md`
- Governing source-identity contract:
  `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md:287-368`
- Breadth audit (rendered-path, superseded):
  `.project/active/elaborator-breadth/audit-20260808-rendered-path.md`
- Independent design review: `.project/active/elaborator-design/design-review.md`
- SysIDE identity/redefinition probe record:
  `.project/research/20260808-103243_syside-identity-and-redefinition-probe-record.md`
- SysIDE identity contract:
  `../agentic-mbse/docs/syside/v0.8.1/api/metamodel/KerML/Element.md:13,55-57,99-101,143`

## The Point

**[OWNER] (2026-08-08):** SysIDE has already resolved which semantic element a reference denotes.
Codegen must use that exact identity. It must not replace it with a non-unique name and later try to
recover the target.

**[INHERITED: source-identity contract invariants 54–60]** One semantic source occurrence becomes
exactly one runtime source across calculation, constraint, and aggregation consumers. Reconstruction
from owner/name fields is not an accepted authority. Missing or ambiguous occurrence context produces
a named diagnostic, never a guess.

The bridge exists to perform the one legitimate conversion the parser cannot perform for codegen:
an exact declaration referent, interpreted in an exact concrete occurrence, becomes an exact graph
value. Once that edge exists, no downstream stage resolves the reference again.

## Research Findings

1. **SysIDE already exposes the identifier and relationships we need.** `Element.element_id` is a
   UUID documented as globally unique and immutable during the element's lifetime
   (`.venv/lib/python3.12/site-packages/syside/core/__init__.pyi:5875-5905`). The live expression
   surface exposes exact object relationships: `FeatureReferenceExpression.referent`
   (`.venv/lib/python3.12/site-packages/syside/core/__init__.pyi:7798-7835`),
   `FeatureChainExpression.target_feature` and `Feature.chaining_features`
   (`.venv/lib/python3.12/site-packages/syside/core/__init__.pyi:7480-7542`), and the
   `Redefinition.redefined_feature` / `redefining_feature` endpoints
   (`.venv/lib/python3.12/site-packages/syside/core/__init__.pyi:14795-14833`).
2. **Qualified names cannot be the authority.** SysIDE documents `qualified_name` as nullable when
   an ownership chain is incomplete or same-named elements collide in one namespace
   (`.venv/lib/python3.12/site-packages/syside/core/__init__.pyi:5998-6014`).
3. **We currently throw the UUID away.** `ResolvedTargetFact` stores qualified names, kinds, names,
   owner QNs, and redefinition QNs, but not `element_id`
   (`../agentic-mbse/src/agentic_mbse/sysml/data_models.py:53-69`). `feature_chain_facts` likewise
   converts live root and target elements into QN/name tuples
   (`../agentic-mbse/src/agentic_mbse/sysml/expression.py:636-747`).
4. **Current occurrence identity is still presentation-shaped.** `PathStep` contains
   `(owning_def_qn, feature_name, occurrence_index)` and `instance_path` joins those names
   (`src/sysml_codegen/analysis/part_instance_index.py:26-37,249-270`).
5. **The graph is only superficially typed.** `NodeRef`, `ProducerRef`, graph keys, output names,
   and computed-expression input keys remain strings
   (`src/sysml_codegen/elaboration/graph.py:83-105,108-178`). Distinct semantic dependencies can
   overwrite under one sanitized key (`src/sysml_codegen/elaboration/elaborate.py:483-525,943-995`).
6. **The UUID behavior is sufficient only inside a pinned boundary.** On SysIDE 0.8.4, probes found
   33/33 named elements stable across independent loads, relocated directories, source shifts, and
   model edits; a resolved referent's ID equaled the declaration's ID. Those stable generated IDs
   were UUIDv5 values derived from qualified names. Codegen still does not resolve by a QN: SysIDE
   resolves the object and codegen consumes its UUID. However, cross-load stability transitively
   depends on SysIDE's current QN-based generation. The stub also says `element_id` may be deprecated
   and promises reload stability only for QN-bearing elements and their owning memberships
   (`.venv/lib/python3.12/site-packages/syside/core/__init__.pyi:5890-5905`).
7. **Null-QN objects mark the unsupported identity boundary.** Collision victims, anonymous usages,
   expressions, and relationship objects received random UUIDv4 values across loads. Executable or
   containment declarations without a proven stable declaration or owning-membership coordinate
   must fail closed. Expression and relationship objects need no identity of their own: semantic
   edges key from resolved endpoint declaration IDs. In particular, a `Redefinition` relationship
   object's ID is never a slot key.
8. **SysIDE materializes ordinary implied redefinitions.** In `spec_chain_twolevel`, the usage-side
   parameter authored as `in drive_power = ...` owns a real `Redefinition` edge to the definition
   formal with `is_implied=True`; authored `:>>` has the same endpoint shape with
   `is_implied=False`. `is_implied_included` is true for both and cannot be an inclusion filter.
   The persisted probe record above carries the complete observations.
9. **The snapshot should contain the answer, not the question.** The current snapshot rebuilds
   extraction facts and reruns semantic machinery (`src/sysml_codegen/snapshot/graph_rebuild.py:39-227`).
   The elaborate-first architecture instead serializes the resolved instance graph
   (`.project/research/20260807-145336_elaborate-first-instance-graph-architecture.md:180-188`).

## Core Concept

The identity bridge is a transient index owned by the elaborator. It is built from the live SysIDE
model, maps exact parser element UUIDs into concrete occurrence and graph identity, and is discarded
after the graph is complete. It is not a persisted manifest and not a second semantic authority.

There are three identities:

1. A **declaration ID** says which exact SysIDE element this is.
2. An **occurrence ID** says which concrete instantiation of a part usage this is.
3. A **node or output-port ID** says which value in that occurrence a consumer reads.

Every SysIDE-materialized redefinition relationship, authored or implied, connects declaration IDs
that fill the same logical feature slot. Same-named declarations without that relationship remain
different slots.

```text
SysIDE resolved element UUID
        + consumer occurrence ID
        ↓
exact node/output-port ID
        ↓
stored graph edge
```

## Proven Assumptions and Remaining Bet

- **B1 — probe-confirmed for the named-element boundary.** SysIDE 0.8.4 provides reload-stable
  element IDs for the supported QN-bearing executable declarations, and resolved referents carry
  those same IDs. The boundary is deliberately narrower than “every element”: null-QN executable
  or containment forms fail closed unless a stable owning-membership coordinate is separately
  proven. *If a supported SysIDE release changes this behavior → stop the identity foundation,
  review the upstream identity surface, and decide the snapshot-version consequence before any
  breadth work continues.*
- **B2 — probe-confirmed.** SysIDE materializes both authored and implied `Redefinition` edges, and
  their `redefined_feature` / `redefining_feature` endpoint IDs define feature-slot membership.
  *If a future supported form lacks those semantic edges → surface that form as unsupported; never
  reconstruct the family from equal names.*
- **B3 — remaining bet.** A fully resolved instance graph contains every semantic decision needed by
  projection and generation. *If false → the snapshot would need the live AST again, contradicting
  the approved elaborate-once architecture.*

## Key Decisions

### D1 — Declaration identity is SysIDE `element_id`

Wrap the UUID in a frozen `DeclarationId` dataclass. The adapter is the only code that reads
`element.element_id`; it validates presence, supported stability, and type and returns the wrapper.
All semantic identity values use frozen dataclasses because the runtime must distinguish identity
namespaces, validate UUIDs, and serialize them canonically. The repository's existing `NewType`
wrappers in `core/identifier_types.py` protect presentation strings at type-check time only;
`ScopedAliasKey` shows a structured `NewType`, but it provides no runtime namespace or validation.
That convention is therefore not strong enough for this invariant.

This accessor is new `agentic-mbse` API on the unmerged `elaborate-first-salvage` branch. Its change,
the codegen evidence type, and the first identity-foundation consumer land as one coordinated
cross-repository unit. Codegen never reaches around the adapter to read the property.

Rejected alternatives:

- Qualified names: nullable under collisions and already the source of reconstruction bugs.
- Python `id`, hash, or object identity: valid only inside one parser session and not serializable.
- Source coordinates or dense sequence numbers: require another identity to assign consistently.

### D2 — Feature slots follow all materialized redefinition edges

A base feature and every declaration that SysIDE says redefines it belong to one `FeatureSlotId`.
This includes authored edges (`is_implied=False`) and SysIDE-materialized implicit edges
(`is_implied=True`). `is_implied_included` does not distinguish those forms and is not a filter.
The semantic endpoints are `redefined_feature` and `redefining_feature`; generic relationship
`source`/`target` fields are not used. The relationship object's own `element_id` is never used
because null-QN relationship IDs are not stable across loads.

The slot ID is the unique root declaration ID reached by following endpoint IDs along the actual
redefinition edges. Cycles or multiple unrelated roots block elaboration. A same-named declaration
with no such edge is a different slot.

Each concrete node records both its slot and its effective declaration/value site. This preserves
referent fidelity while allowing definition-level and usage-level references to converge on the
same runtime source.

### D3 — The new front end owns a clean exact-ID occurrence walker

An occurrence step contains the `FeatureSlotId` derived from the exact containment `PartUsage`
declaration and its multiplicity index. The occurrence record separately retains the effective
`PartUsage` declaration ID. It does not contain an owner QN or feature name.

```text
OccurrenceStep = (containment_slot_id, occurrence_index)
OccurrenceId   = tuple[OccurrenceStep, ...]
```

The new walker lives under `elaboration/` and constructs a new typed occurrence index directly from
live SysIDE declarations. It consumes `Usage.usages` as SysIDE's canonical effective child-
declaration view, then filters supported composite `PartUsage`s and applies codegen's finite-
cardinality policy. It does not reconstruct the inherited/redefined child set from names or global
owner grouping. Codegen owns multiplicity fan-out, parent/index context, structured `OccurrenceId`,
supported-containment filtering, and cycle detection. It does not wrap or import
`PartInstanceIndex`, `PathStep`, `InstanceOccurrence`, or their rendered `instance_path`. A human-
readable occurrence path is derived metadata after the typed index exists.

The 2026-08-09 live boundary probe confirmed this split. SysIDE 0.8.4 returns effective semantic
declarations, not contextual concrete occurrences; see
`.project/active/spike-syside-occurrence-authority/findings.md`.

The old walker remains frozen inside the old front end until cutover. It may run only as part of the
legacy black-box route used for shipped behavior and dual-run comparison. New elaborator code never
consumes an old occurrence, and no graph may contain occurrences or edges from both walkers. Item 7
switches the complete front-end boundary, then deletes the old walker with its consumers.

### D4 — Node identity is structured and opaque

```text
ScopeId     = OccurrenceId | PackageScopeId
NodeId      = (node_kind, ScopeId, FeatureSlotId | DeclarationId)
OutputPortId = (calculation NodeId, output DeclarationId)
```

Semantic code compares these typed values and never parses their wire encoding. Graph nodes carry
display path, display name, QN, and source location separately for diagnostics and projection.

### D5 — One resolver accepts exact semantic paths

Binding and expression evidence carries a `ResolvedSemanticReference`:

```text
root_id: DeclarationId
segment_ids: tuple[DeclarationId, ...]
leaf_id: DeclarationId
```

The bridge contextualizes the exact root against the consumer scope, follows child/member indexes
by exact segment IDs, and returns a `NodeId` or `OutputPortId`. Zero candidates is
`SI_OCCURRENCE_MISSING`; multiple candidates is `SI_OCCURRENCE_AMBIGUOUS` unless the caller
explicitly requests plural expansion.

```text
resolve(reference, consumer_scope, cardinality=ONE)
    -> ResolvedEdge | ResolutionFailure
```

`ALL` cardinality is available only to explicitly plural operations such as aggregation.

### D6 — Redefinition precedence is one ordered candidate model

Every literal, chain, and expression redefinition retains its declaring definition/usage ID and
target slot ID. The effective writer for an occurrence is:

1. Occurrence redefinition, deepest occurrence first.
2. Most-specific applicable definition redefinition.
3. Definition default.

Model traversal order is never a tiebreaker. Incomparable applicable writers are ambiguous.

### D7 — Graph edges use consumer-port and target identity

Calculation and constraint inputs use their exact formal declaration ID as the consumer port.
Computed-expression dependencies retain structural operand/reference identity rather than sanitized
text. Aggregations retain one exact edge per expanded target occurrence. Each edge keeps the exact
referent-path IDs as provenance, but its already-resolved target ID is the semantic authority; no
downstream code replays that provenance to select a target.

A producer output is identified by its exact output declaration ID. `output_name` is projection
metadata, not edge identity.

Constraint nodes use the same edge model for their actuals. The constraint catalog is assembled
from those resolved consumer-port/target edges. It does not run a separate occurrence or actual-
resolution ladder.

### D8 — Projection owns strings and implements the complete generation seam

Only projection converts semantic IDs into module names, channel names, schema keys, filenames, and
diagnostic labels. Projection is mechanical over a validated graph:

- Calculation, FORMULA, aggregation, constraint, and report-aggregator nodes become
  `PipelineModule`s. ADR-003 helpers render module types, module names, channel names, and Python
  paths from display metadata after identity is settled. Calculation-definition QNs remain registry
  template metadata, never lookup keys.
- Each externally suppliable consumed attribute node becomes exactly one `EntryPoint`. A definition
  parameter default is `LIBRARY_DEFAULT`; a modeled design attribute or occurrence override is
  `DESIGN_ATTRIBUTE`; a literal authored directly at a calculation usage is `USAGE_LITERAL` and is
  consumer-local because that literal is itself the source. The graph's value-site record decides
  the class. Projection never infers it from a rendered name or value equality.
- Parameter groups derive from the source file recorded on the source node/value site.
- Execution order is a topological sort of direct producer edges.
- Projection emits `entry_point_groups` as a list, attaches `output_aliases` and the complete
  `constraint_catalog`, and preserves the registry renderer's text return contract.
- `fallback_entry_points` is retired. The V11 coverage assertion remains and requires every module
  input to be accounted for by one direct producer edge or one projected entry point.

A rendering collision blocks before output with `SI_RENDERING_COLLISION`. It never merges semantic
graph nodes. Automatic public-name disambiguation would change the generated API and requires a
separate owner-approved design.

### D9 — Snapshot payload is the resolved instance graph

The snapshot contains declarations needed for display/provenance, structured occurrences, nodes,
direct edges, diagnostics, neutral expression IR, schema versions, and a canonical fingerprint.
Snapshot loading validates and projects the graph. It never reruns name resolution, occurrence
contextualization, alias chasing, backtracking, or registry lookup.

### D10 — Unsupported identity fails closed through a fixed diagnostic catalog

The inherited extraction codes remain: `SI_SELF_BINDING`, `SI_INDEXED_SOURCE_UNSUPPORTED`, and
`SI_EXPRESSION_SOURCE_UNSUPPORTED`. Contextual elaboration uses
`SI_OCCURRENCE_MISSING`, `SI_OCCURRENCE_AMBIGUOUS`, `SI_MULTIPLICITY_UNRESOLVED`,
`SI_MULTIPLICITY_UNSUPPORTED`, `SI_MULTIPLICITY_INVALID`, `SI_CONTAINMENT_RECURSIVE`, and
`OVERRIDE_TARGET_MISSING`.
The exact-ID graph adds these blocking codes:

- `SI_ID_MISSING` — an identity-bearing supported element has no usable parser ID.
- `SI_ID_UNSTABLE` — an executable or containment element lacks a reload-stable exact coordinate.
- `SI_REDEFINITION_INVALID` — a slot family cycles, has unrelated roots, or has missing endpoints.
- `SI_ALIAS_CYCLE` — a typed alias cycle prevents a unique target.
- `SI_EDGE_DANGLING` — a stored edge refers to a missing port, node, or output.
- `SI_CONSTRAINT_BLOCKED` — the exact profile classified a constraint as `BLOCK`; strict
  elaboration and every projection halt while lenient inspection retains the typed node and named
  diagnostic.
- `SI_RENDERING_COLLISION` — distinct semantic identities render to one public identifier.
- `SI_SNAPSHOT_INVALID` — schema, identity, fingerprint, or referential validation fails on load.

Strict and lenient modes may change halt-versus-report behavior, never identity. Lenient mode may
collect findings for the internal corpus diff; a graph with any blocking finding cannot project for
generation.

## Architecture

### Live construction

1. **Identity capture.** The adapter validates every executable element UUID. Evidence builders
   capture formal, referent, chain-segment, owner, typing, and redefinition endpoint IDs directly
   from the live objects. QNs and names are retained only as diagnostic metadata.
2. **Occurrence expansion.** The new-front-end occurrence index walks actual part usages and
   constructs `OccurrenceId`s from exact containment slot IDs and multiplicity indices. It records
   parent/child, effective usage declaration, effective type, and ancestor relationships.
3. **Slot and node construction.** All SysIDE-materialized redefinition edges, authored and implied,
   form feature slots through their endpoint IDs. The elaborator creates all attribute,
   calculation, computed, and constraint nodes and registers exact lookup keys before resolving any
   binding.
4. **Contextual resolution.** The bridge resolves every simple reference, feature chain,
   expression dependency, constraint actual, EXPOSE alias, and aggregation term through the same
   ID-based indexes.
5. **Graph validation.** Referential integrity, one-edge-per-port, redefinition ordering, alias
   acyclicity, and blocking diagnostics are checked before the graph becomes projectable.
6. **Projection.** The graph is mechanically rendered into the existing `ComputationGraph` seam.

### Exact contextualization rules

- **Definition-owned feature:** walk the consumer's occurrence ancestors, innermost first. Select
  the first occurrence whose effective type closure contains the exact owner definition ID and whose
  slot index contains the referent. Do not search by leaf.
- **Usage-owned feature or part usage:** select occurrences produced by the exact usage declaration
  ID. Prefer the exact occurrence on the consumer ancestor chain; otherwise require one unique
  candidate in the permitted scope.
- **Feature chain:** contextualize its exact root once, then transition through exact part-usage,
  calculation-usage, and feature-slot IDs. Each transition must be unique unless the authored form
  explicitly permits plural expansion.
- **Aggregation:** resolve the exact repeated part-usage/definition segment in the owning scope,
  enumerate its concrete occurrence IDs, then resolve the exact leaf slot on each occurrence.
- **Package-scoped element:** use an explicit package `ScopeId`; never encode package scope as an
  empty or partial occurrence path.

## Required Invariants

1. Every supported semantic declaration has exactly one `DeclarationId`.
2. Declaration equality uses only the SysIDE UUID, never QN, name, source location, or value.
3. Occurrence equality uses only exact containment slot IDs and multiplicity indices.
4. Nodes are keyed only by typed scope plus declaration/slot identity.
5. Different declarations share a slot only when materialized redefinition relationships unify
   them; same names never do.
6. Every supported reference produces one edge, a permitted plural edge set, or a named failure.
7. Names, QNs, sanitized spellings, rendered paths, and generated identifiers never select an edge.
8. Renaming or adding a nearer same-named declaration cannot change an edge while SysIDE's resolved
   referent UUID is unchanged.
9. Reordering files, declarations, candidates, or redefinitions cannot change semantic edges.
10. Strict and lenient modes can change halt-versus-report behavior, never identity.
11. The snapshot contains direct graph edges; offline projection performs no semantic resolution.
12. A graph with blocking identity diagnostics is not projectable.
13. One graph is built by one occurrence authority. Legacy and new-front-end occurrences are never
    adapted into each other or combined.
14. Redefinition and expression relationship-object IDs never key semantic slots or edges; resolved
    endpoint declaration IDs do.

## Component Overview

- **SysIDE identity adapter** (`agentic-mbse/sysml/syside_adapter.py`): one strict UUID access point
  and the upstream-version assumption boundary.
- **Resolved semantic evidence** (`agentic-mbse/sysml/data_models.py`, `sysml/expression.py`,
  `sysml_codegen/extraction/source_evidence.py`): exact element/formal/chain/redefinition IDs plus
  diagnostic metadata. This replaces the QN/name-only identity contract; it is not a second record.
- **New-front-end occurrence index** (`elaboration/occurrence.py`, new): the sole occurrence walker
  for the exact-ID elaborator. It returns typed occurrences only and has no dependency on the legacy
  index or rendered-path surface.
- **Identity bridge** (`elaboration/identity.py`, new): transient slot, occurrence, node, and output
  indexes plus the single contextual resolver. It knows nothing about generated names.
- **Instance graph** (`elaboration/graph.py`): typed nodes, consumer ports, output ports, direct edges,
  value sites, expression IR, and projectability diagnostics.
- **Elaborator** (`elaboration/elaborate.py`): orders graph construction, applies value tiers, and
  invokes the bridge for all consumer forms. It contains no path parsing or name matching.
- **Projection** (`elaboration/project.py`): renders the validated graph onto `ComputationGraph` and
  owns all public naming/collision checks.
- **Graph snapshot** (`snapshot/`): canonical instance-graph serialization, validation, fingerprint,
  and round-trip. It replaces extraction reconstruction at cutover.
- **Legacy front end** (existing analysis/orchestration/resolution path): frozen as a complete
  black-box comparator and shipped route until cutover. Its old occurrence walker, public rendering,
  and v5 snapshot bytes remain unchanged. No new semantic fix lands there.

## Non-Goals

- Making generated Python names themselves semantic identifiers.
- Supporting unresolved or unbounded multiplicity. Finite constant integer expressions are in
  scope; ordered, nonunique, range, and invalid finite shapes fail with their named outcomes.
- Preserving the legacy resolver, OutputRegistry namespaces, or extraction-snapshot rebuild path
  after cutover.
- Serializing live SysIDE objects or Python object identity.
- Inventing a second persistent identity manifest beside the instance graph.
- Resolving invalid or ambiguous models by first-match policy.
- Refactoring the legacy walker into the new identity model or building a compatibility view between
  old and new occurrences.
- Switching semantic authority consumer-by-consumer. The cutover boundary is the complete front end.

## Deletion Ledger

Item 7 executes this ledger atomically with the complete-front-end cutover. Until then, these
mechanisms are frozen inside the legacy route; they are not reusable substrate for the new route.

- The legacy `PartInstanceIndex`, `PathStep`, rendered `instance_path`, and every consumer that
  parses the rendered path back into structure (`analysis/part_instance_index.py`, constraint scope
  and namespace derivation in `analysis/constraint_lowering.py`, and aggregation scope parsing in
  `orchestration/output_registry_builder.py`).
- Value-binding resolution, specialized-chain rewriting, and the self-named rescue path
  (`orchestration/pipeline_builder.py:204-645`).
- Aggregation scope re-derivation (`orchestration/pipeline_builder.py:646-877`).
- Virtual calculation-usage expansion (`extraction/usage_extractor.py:248-626`).
- The dependency backtracker's semantic resolution ladder. Producer-edge topological ordering is
  retained in projection, but edge discovery is replaced by the resolved graph.
- The 21-key-form producer lookup table (`resolution/producer_resolution.py`).
- The supplied-value materializer (`resolution/supplied_values.py`).
- OutputRegistry identity namespaces and the group-deriver value backfill
  (`resolution/graph_builder.py:618-632`).
- Extraction-snapshot graph reconstruction and the v5 snapshot schema. The replacement snapshot is
  the resolved instance graph, not an encoding of legacy occurrence types.
- Wrong-oracle tests that require the legacy resolver's guessed identity behavior. Replace them with
  contract and public-mutation oracles; do not disable them without replacement.

## Implementation Notes

- Replace the current chain five-tuple with one exact semantic-reference value. If compatibility
  requires a staged API change, QN/name fields remain diagnostic-only and no new elaborator code may
  consume them semantically.
- The design implements self-binding with exact declaration-ID equality. Spec R3 states the
  semantic same-declaration rule, and ratified R9 now requires declaration-ID equality and prohibits
  QN/name lookup. The inherited self-binding behavior does not change.
- The bridge may keep a transient `DeclarationId -> live Element` map. No live object or Python hash
  enters the graph or snapshot.
- The new walker puts typed and untyped part usages into the same occurrence model. It does not
  modify the old walker's rendered-path sidecar; that sidecar disappears with the legacy route.
- Do not flatten EXPOSE aliases during consumer resolution. Store and validate direct typed alias
  edges, then resolve their target value without a name lookup.
- Neutral expression IR must bind operands to consumer-port IDs. The snapshot must not store an AST
  that needs semantic reference resolution after loading.
- UUIDs use canonical lowercase hyphenated strings only at JSON and diagnostic boundaries. The
  generic serializer currently does not support raw UUID values and must not silently emit `null`
  (`src/sysml_codegen/snapshot/serializer.py:195-258`).
- Keep SysIDE pinned to 0.8.4 for the identity-foundation landing. A dependency update cannot ride
  through as routine lockfile churn; it reruns the identity kill probes and reopens the snapshot
  decision if observed IDs change.

## Potential Risks

- **SysIDE changes or removes ID generation.** SysIDE documents `element_id` as potentially
  deprecated. Pin the supported version and keep cross-load, file-order, harmless-edit,
  path-spelling, and relocated-root identity tests. A version change requires explicit review and a
  snapshot-version decision. Falling back to Python hashes or QNs is not an option.
- **QN-derived UUID stability is narrower than live uniqueness.** A UUID can be exact for one live
  document while changing on reload. The graph/snapshot boundary accepts only declarations with a
  proven stable parser coordinate. This keeps codegen from resolving by names, but it makes the
  upstream QN-derived implementation an explicit versioned dependency.
- **Null-QN executable or containment elements.** Same-name collision victims and anonymous usages
  fail with `SI_ID_UNSTABLE` unless a stable owning-membership coordinate is proven. Null-QN
  expression and relationship objects do not block merely for lacking stable IDs because codegen
  keys their semantic effect from resolved endpoint declaration IDs.
- **Complex redefinition families.** Detect cycles, multiple unrelated roots, and incomparable
  applicable writers. Block them unless the contract supplies a semantic disposition.
- **Identity-safe graph, colliding public names.** Projection performs a separate deterministic
  output-name collision check and blocks before writing. Semantic uniqueness does not imply
  Python/filesystem uniqueness.
- **Partial lenient graphs mistaken for valid output.** Graph validation records projectability;
  production projection refuses any graph with blocking findings.

## Integration Strategy

This correction reopens Item 5 before projection and corpus grind continue. During migration there
are two complete front ends, never two occurrence authorities inside one front end:

1. The legacy route remains the shipped authority and produces byte-identical legacy
   `ComputationGraph` and v5 snapshot surfaces. Its walker and semantic resolver are frozen.
2. The new route captures exact identity through the new `agentic-mbse` adapter surface, builds its
   own typed occurrence index, resolves one instance graph, and projects that graph. It never imports
   a legacy occurrence type or calls a legacy semantic resolver.
3. The dual-run harness invokes both complete routes independently and compares their public
   `ComputationGraph` results and generated output. It does not adapt one route's intermediate state
   into the other or combine their nodes.

The first coordinated landing unit spans both repositories and changes the adapter accessor,
identity evidence, the new occurrence walker, graph IDs, and the new resolver together. It removes
leaf/name selection paths from the new route in that same unit. The legacy route stays untouched; an
ID rider does not make it authoritative by accident.

Subsequent breadth work ports supported consumer forms inside the new route only, then completes
projection and graph-snapshot round-trip. Semantic authority does not switch one consumer at a time.
Item 7 switches the shipped front-end entry point atomically, changes the snapshot format, and
executes the deletion ledger, including the old walker and front end.

## Validation Approach

Validation is ordered so an upstream identity failure stops the work before more shape breadth is
built:

1. **Identity-foundation kill probe.** Land the kept tests from the persisted probe record first:
   parser-ID stability, referent-ID equality, null-QN fail-closed behavior, implied/authored
   redefinition endpoint families, and guards against relationship IDs or string lookup. Failure
   stops the implementation slice.
2. **New-route semantic probes.** Prove one exact chain, definition-owned reference, usage-owned
   reference, redefinition, expression operand set, and sum term under adversarial same-name and
   reversed-order conditions.
3. **Route isolation and legacy freeze.** Assert that no new elaborator module imports legacy
   occurrence types, no graph mixes routes, and the legacy route plus v5 snapshots remain
   byte-identical while it is the shipped authority.
4. **Breadth and snapshot gates.** Run the 29-cell matrix, 37-fixture corpus, malformed-graph
   fail-closed tests, canonical instance-graph round-trip, and live/snapshot projection parity.
5. **Public outcome gate.** Mutate one modeled source occurrence off default and observe every and
   only its intended generated consumers change. This landed-code observation, not the approved
   design, is what can clear breadth ledger findings `audit-F1`, `audit-F2`, and `audit-F3`.

Appendix A lists the required cases. Friendly fixture output alone is not identity evidence.

## Next-Stage Handoff

The implementation plan must treat these as fixed:

- SysIDE `element_id` is declaration identity.
- Occurrence identity is exact containment slots derived from usage UUIDs plus multiplicity indices.
- Every SysIDE-materialized redefinition edge, authored or implied, forms feature slots through its
  endpoint declaration IDs.
- Every semantic edge is decided during elaboration and stored by typed ID.
- Projection owns names; snapshots contain the resolved graph.
- The new front end has its own exact-ID occurrence walker. The old walker is frozen as part of the
  black-box legacy route and is deleted at atomic cutover.

The first risk to de-risk is the identity-foundation kill probe, followed by the coordinated slice:
exact evidence through one chain, one definition-owned reference, one usage-owned reference, one
redefinition, and one sum term, all under adversarial same-name collisions. No further shape breadth
should build on the current leaf-name resolver.

## Next Steps

All design-review findings are incorporated. The owner selected M3 Option A on 2026-08-08, and spec
R9 now requires exact declaration/occurrence identity and prohibits semantic name lookup. The
rewritten Item-5 plan is at `../elaborator-breadth/plan.md`; its five-phase strategy is owner-approved
and awaits implementation approval.

## Appendix A — Required Adversarial Identity Cases

1. Declaration UUID stability and referent-ID equality across independent loads, reversed file
   order, relative/absolute paths, relocated roots, source shifts, and harmless model edits.
2. A nearer same-named chain root cannot capture a reference resolved to an outer root.
3. Same-named siblings remain distinct under reversed iteration order. A null-QN executable or
   containment declaration either uses a separately proven stable owning-membership coordinate or
   fails with `SI_ID_UNSTABLE`; it never falls back to a name.
4. Two declarations that sanitize to the same output key remain distinct internally; projection
   reports the rendering collision before writing output.
5. Base, implied usage-parameter, and authored `:>>` redefining declarations converge on one slot
   through endpoint IDs; an unrelated same-named feature does not. Reverse relationship and subtype
   enumeration. The relationship object's own ID cannot affect the result.
6. Two expression operands with colliding rendered names retain two edges and correct operand order.
7. Aggregation uses the exact resolved root under a local same-name shadow and retype.
8. Live graph → canonical JSON → reconstructed graph equality; live and offline projection parity;
   relocated snapshot produces byte-identical output.
9. Malformed IDs, duplicate identities, dangling edges, alias cycles, invalid slot families, wrong
   schema versions, and fingerprint mismatches all fail before projection.
10. An identity-package guard forbids `sanitize_name`, leaf extraction, rendered-path parsing,
    prefix matching, and first-match selection inside the bridge.
11. Changing only display metadata cannot change graph IDs or edges.
12. Public off-default mutation still reaches every and only the consumers of one source occurrence.
13. The new elaborator imports no `PartInstanceIndex`, `PathStep`, `InstanceOccurrence`, or rendered-
    path parser; the dual-run harness compares only complete-route public results.
14. The frozen legacy route and v5 snapshot bytes remain unchanged before cutover; the cutover test
    switches the complete front end and removes every deletion-ledger owner together.

---

Next step: approve and run `$my-implement` from Item-5 Phase 1, the identity-foundation kill probes.
