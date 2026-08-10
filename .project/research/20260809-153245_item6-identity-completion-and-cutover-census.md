---
date: 2026-08-09 15:32:45 PDT
researcher: Codex
branch: source-identity-epic
commit: b9c22c0
topic: Item 6 identity completion and atomic-cutover census
tags: [elaborator, identity, syside, projection, snapshot, cutover]
status: complete
last_updated: 2026-08-09
---

# Item 6 Identity Completion and Atomic-Cutover Census

## Research Question

**[INHERITED: `/tmp/handoff-20260809-151737.md`]** Before planning ELABORATE-FIRST Item 6:

1. find any semantic or executable payload still joined by name, QN, or rendered string;
2. prove whether SysIDE or codegen owns concrete occurrence expansion;
3. audit render-then-parse selectors and the audit-F30/F31 residues;
4. produce a fresh `PipelineContext` consumer and deletion census; and
5. decide whether the approved spec/design must change before a reviewable cutover plan is written.

This is research and planning input. It does not authorize the atomic cutover. On 2026-08-09 the
owner inserted identity completion as Item 6 and moved the atomic cutover to Item 7.

## Answer

The current exact route is not safe to cut over. Edge resolution is exact-ID based,
but executable payload attachment is not yet exact. Calculation metadata and compilation are
joined by definition QN, input/output metadata is joined by normalized member name, and constraint
profile decisions are joined by usage QN. A miss can silently become `UNKNOWN`, `float`, null
metadata, or even `ADMIT`. These are pre-cutover correctness defects, not presentation-only debt
(`src/sysml_codegen/elaboration/elaborate.py:219-234,657-681,796-857,872-921,978-1027`).

SysIDE 0.8.4 owns the effective semantic child-declaration view. It does not materialize concrete
parent/index contexts. Codegen must retain `OccurrenceIndex`, but it should consume
`Usage.usages` instead of re-deriving inheritance and redefinition selection through global owner
grouping. Codegen remains responsible for supported-containment filtering, finite multiplicity,
parent/index context, structured occurrence identity, and cycle detection. The design was amended
narrowly to record this boundary; no architecture was reopened
(`.project/active/elaborator-design/design.md:180`).

Projection also reconstructs executable structure after rendering. Constraint and alias ownership
are parsed from `display_path`, and module topological order is rebuilt by joining rendered channel
and module names. The graph codec omits the occurrence records needed to render public ancestry
without parsing node display strings. Expression and predicate IR are serialized during elaboration
and reparsed during projection. D8 and D9 already prohibit these patterns; implementation has not
finished the approved design (`src/sysml_codegen/elaboration/project.py:469-547,626-697,789-820,846-895`;
`src/sysml_codegen/elaboration/graph.py:193-198`).

**[AGENT] Decision:** keep the approved spec. R1 and R9 already require one-way, exact-ID
resolution and fail-closed missing identity. Amend D3 only for the newly proven SysIDE/codegen
responsibility split. Item 6 owns identity completion before Item 7 switches the route, recaptures
snapshots, or deletes the legacy front end.

## Finding 1: Exact edges, inexact executable payloads

The exact resolver and graph indexes use `DeclarationId`, `FeatureSlotId`, `OccurrenceId`,
`NodeId`, consumer-port IDs, and output-port IDs. No name, QN, prefix, suffix, regex, or rendered
path selects a graph edge on the current route
(`src/sysml_codegen/elaboration/elaborate.py:1093-1362`;
`src/sysml_codegen/elaboration/graph.py:193-296`).

That claim does not extend to payload attachment:

| Payload join | Current key | Failure behavior | Required key |
|---|---|---|---|
| Calc definition data | definition QN | collision overwrites; miss removes docs/expressions and falls back to live source | exact calc-definition `DeclarationId` |
| Calc compilation | definition QN | miss becomes `Compilability.UNKNOWN` and no auto implementation | exact calc-definition `DeclarationId` |
| Output metadata | raw/display member name | last match wins; miss becomes `float` plus null metadata | exact output declaration ID |
| Bound input metadata | first raw/display member-name match | first match wins; miss becomes `float` plus null metadata | exact formal declaration/slot ID |
| Unbound input metadata | raw/display member-name dictionary | last match wins; miss loses extracted default/type/unit | exact formal declaration/slot ID |
| Constraint decision | usage QN | null QNs dropped; collisions overwrite; miss falls back to local predicate and `ADMIT` | exact constraint-usage `DeclarationId` |

The calc defects are codegen-local. `CalculationDefinitionData` and codegen's `AttributeInfo` are
created from the live calc definition and owned member objects, but neither record preserves the
source element ID (`src/sysml_codegen/extraction/data_models.py:59-87,135-174`;
`src/sysml_codegen/extraction/extractor.py:205-341`). The validated ID already exists through
`SysideAdapter.element_id()`.

The constraint defect crosses the repository boundary. `IdentityFact` preserves only kind, name,
and QN, and `UsageDecision` carries that flattened identity unchanged
(`../agentic-mbse/src/agentic_mbse/sysml/expression_facts.py:24-35`;
`../agentic-mbse/src/agentic_mbse/sysml/constraint_extraction.py:191-205`;
`../agentic-mbse/src/agentic_mbse/sysml/executable_profile.py:131-142`). Anonymous constraints are
supported upstream, so dropping null-QN decisions is not an acceptable simplification.

**[AGENT] Recommended payload shape:**

- Add exact calc-definition identity to `CalculationDefinitionData`.
- Add exact member identity to codegen `AttributeInfo` and key calc input/output payload by that ID.
- Compile and attach each calculation by exact definition ID. Assert that compiled output identity
  matches exact output-port identity.
- In `agentic-mbse`, return an ID-bearing live association around the neutral constraint fact, or
  otherwise preserve the exact usage ID through profile evaluation. Keep the parser UUID out of
  `IdentityFact` if that neutral, tool-independent contract must remain unchanged.
- Key decisions by exact constraint-usage ID in codegen. Missing, duplicate, `BLOCK`,
  `UNASSESSED`, and `NON_NUMERICAL` outcomes must have explicit projection behavior.

Graph validation must also require payload totality and vocabulary. Today it checks graph keys and
edge targets, but not input-name/metadata totality, output metadata, compilation consistency, or
constraint eligibility (`src/sysml_codegen/elaboration/graph.py:204-296`). Snapshot decoding must
stop defaulting a missing eligibility field to `"admit"`
(`src/sysml_codegen/snapshot/instance_graph.py:454-514`).

## Finding 2: The occurrence boundary is split, not transferred

The generated SysIDE API describes `nested_usages` as owned usage features,
`nested_occurrences` as the occurrence-usage subset of those declarations, and `usages` as usage
features including non-owned/inherited features. These are abstract-syntax declaration views, not
runtime occurrence populations (`.venv/lib/python3.12/site-packages/syside/core/__init__.pyi:20043,
20074,20150`).

The kept licensed probe compared those native surfaces with codegen's exact index across five
fixtures. No native surface returned contextual clones. The two strongest cases were:

- `d38_caret`: one native `cell` declaration became four codegen occurrences with indices 0-3.
- `nested_occurrence_override_probe`: native `nested_occurrences` did not instantiate
  definition-owned `panel/source`, while codegen produced the concrete contextual tree.

Retyping kept the same split: SysIDE supplied the effective/redefined declaration set; codegen added
the containment slot, parent context, and effective declaration to the concrete occurrence. The
reproducible probe and full finding are in
`.project/active/spike-syside-occurrence-authority/probe.py` and
`.project/active/spike-syside-occurrence-authority/findings.md`.

The current walker still rebuilds effective children from definition closures, global owner maps,
slot grouping, and most-specific-owner selection
(`src/sysml_codegen/elaboration/occurrence.py:402-466`). That duplicates SysIDE's declaration
authority. Replace it with, or first parity-pin it against, `Usage.usages`. Retain codegen's
multiplicity evaluation and structured occurrence creation
(`src/sysml_codegen/elaboration/occurrence.py:468-516`).

## Finding 3: Projection is not yet one-way

Public names are allowed to be strings after identity is settled. The defect is using those strings
to recover structure that already existed:

| Residue | Current behavior | Required structure |
|---|---|---|
| Constraint ownership | `display_path.rsplit()` and `split()` recover owner and namespace | stored occurrence/package scope plus public render metadata |
| Output alias ownership | `display_path.rsplit()` recovers instance path | stored alias owner occurrence/scope |
| Module order | exact edges render to channels, then channels join back to module names | typed projected-module dependencies derived from `ProducerRef`/node IDs |
| Computed expression | neutral IR serializes to text, then projection parses it | structured graph IR; serialize only at snapshot boundary |
| Constraint predicate identity | predicate serializes to text, then projection parses it for formal metadata | structured predicate IR/leaf identity retained in graph |

The graph currently stores only attrs, calcs, constraints, and diagnostics. It does not retain the
`ExactOccurrence` records that carry parent identity and display metadata
(`src/sysml_codegen/elaboration/graph.py:193-198`). Scope IDs preserve semantic occurrence identity,
but not enough public ancestry metadata to render constraint and alias paths without parsing a node
display string. D9 already requires structured occurrences in the snapshot, so the plan should add
them to `InstanceGraph` and its canonical codec rather than invent a second sidecar.

The public renderer may still split or sanitize authored display metadata to produce the public API.
It may not use a rendered output string to rediscover owner, dependency, alias, or semantic source.
Collision guards remain required.

## Finding 4: F30 is a guard gap; F31 is live code without a valid-model witness

The F30 AST guard inspects only `_resolve_leaf`. Other functions on every multi-segment route are
outside the guard, and the broader file-token check misses `qualified_name`, `display_path`,
`split`, `rsplit`, `startswith`, `endswith`, and `next(generator, fallback)`
(`tests/unit/test_elaboration_import_boundaries.py:11-59`). Current exact selector bodies are clean;
the protection is incomplete.

The F31 global plural fallbacks are statically reachable:

- deep literal redefinitions call plural resolution;
- `sum(...)` marks descendant references plural;
- package plural resolution returns every occurrence of the exact declaration; and
- occurrence plural resolution can return model-wide candidates after lineage/descendant misses
  (`src/sysml_codegen/elaboration/elaborate.py:549-596,1209-1242,1431-1547`).

A mirror case also exists: a plural chain rooted at `CalculationUsage` becomes scalar in
`_select_calc_nodes` (`src/sysml_codegen/elaboration/elaborate.py:1180-1191,1244-1276`). No kept
fixture proves a SysML model can reach either branch. Item 6 should author both halves in one
learning fixture. If the parser rejects the shape, delete the unreachable fallback and record the
named diagnostic. If accepted, scope plural resolution explicitly and remove the global fallback.

The root/slot scaffolding also contains traversal-order fallbacks when an expected slot root is
absent (`src/sysml_codegen/elaboration/elaborate.py:356-366,625-646`). Exact population should make
that state impossible; validation should fail closed instead of choosing the first alternative.

## Finding 5: `PipelineContext` can collapse to the generation seam

Both current constructors populate a legacy extraction bundle. Except for `computation_graph`, the
only non-snapshot production read is a CLI log of `calc_defs`. `constraint_lowering_mode` carries a
real safety obligation, but that obligation belongs to the new snapshot envelope/version gate after
cutover (`src/sysml_codegen/orchestration/pipeline_context.py:75-153`).

| Field or group | Remaining production role | Item 7 disposition |
|---|---|---|
| `computation_graph` | generation and CLI seam | retain, or return `ComputationGraph` directly |
| `calc_defs` | CLI count log; old snapshot capture | replace log from graph/module data; delete field |
| `constraint_lowering_mode` | old snapshot certifiability gate | move to new envelope/version validation; delete field |
| extractor, calc usages, design attrs, group deriver, backtracker/result | old capture or no production consumer | delete fields and field-oracle tests |
| compilation, computed attrs, hierarchy, aggregations, aliases, registry | old capture or no production consumer | delete fields; preserve extraction tests outside context where still useful |
| concrete constraints, constraint facts, part occurrences | old capture or no production consumer | delete; use exact graph/catalog or extraction APIs in tests |

`PipelineContext` is publicly re-exported from orchestration and generation, so shrinking or
deleting it is an intentional API cutover. In-repo generation already consumes only the computation
graph. The field-level test census is recorded in the implementation-plan inputs below; those tests
must be classified as wrong-oracle deletion, extraction-unit coverage, or migrated exact-graph
coverage, never mechanically rewritten to another private field.

## Finding 6: Fresh deletion map

| Legacy responsibility | Delete or rewrite | New owner | Preserved public oracle |
|---|---|---|---|
| occurrence walking/rendered path reconstruction | `analysis/part_instance_index.py`; path parsing in constraint lowering and registry builder | `elaboration/occurrence.py` plus stored graph occurrences | exact occurrence/multiplicity tests |
| VBR, specialized-chain rewrite, self-named rescue | legacy pipeline-builder rewrite helpers and exports | value writers, aliases, exact resolver | C19, self-binding, contract matrix |
| aggregation scope re-derivation | legacy pipeline-builder aggregation stages; registry path splitting | plural exact references and concrete occurrences | aggregation conformance tests |
| virtual calc-usage expansion | template/virtual expansion in usage extractor | exact calc population over occurrence scopes | twin-occurrence and same-name tests |
| backtracker resolution ladder and DFS discovery | dependency backtracker and context fields | direct graph edges | projection and generation-boundary tests |
| 21-key producer table | `resolution/producer_resolution.py` | single exact resolver | contract matrix and public mutation |
| supplied-value materializer | `resolution/supplied_values.py` and calls | value-site selection and entry-point projection | one-source mutation and value-site tests |
| `OutputRegistry` namespaces | registry class/builder and construction | typed graph maps plus projector collision indexes | collision and expose tests |
| group value backfill and old graph assembly | legacy graph-builder semantic assembly | graph value sites plus projection | value-site and coverage tests |
| extraction snapshot rebuild/v5 payload | old loader/serializer/rebuilder; rewrite capture/context | graph snapshot envelope plus graph codec and projection | round-trip, relocation, old-version rejection |
| dual-run scaffolding | diff, parallel entry point, harness/corpus tests | canonical builder owns load/elaborate/project | live and relocated public acceptance |

Two traps belong in the plan:

1. The parallel wrapper returns only `ComputationGraph`, while snapshot capture needs the
   `InstanceGraph`. The canonical builder needs one shared load/elaborate result before projection;
   calling the wrapper is insufficient (`src/sysml_codegen/orchestration/elaborated_pipeline.py:41-47`).
2. The exact route still imports `resolve_modeled_default` and `mint_constraint_id` from the legacy
   constraint module. Move those reusable helpers to neutral owners before deleting the ledger-owned
   lowering code (`src/sysml_codegen/elaboration/elaborate.py:26`;
   `src/sysml_codegen/elaboration/project.py:27`).

The graph codec also lacks the shipped snapshot envelope's model name, capture timestamp,
source-staleness manifest, and certifiability/version marker. Item 7 must define that envelope around
the graph payload before replacing capture/load (`src/sysml_codegen/snapshot/instance_graph.py:54-77,
566-632`; `src/sysml_codegen/orchestration/snapshot_context.py:53-76`).

## Plan Inputs and Acceptance Gates

**[AGENT] Recommended order:**

1. Finish exact identity before switching authority: calc/port payload IDs, constraint-decision ID
   association, occurrence child-view boundary, no first-match fallback, structured graph
   occurrences/IR, and graph payload validation.
2. Make projection one-way: typed dependency ordering and structured public ancestry. Add the full
   F30 guard and the F31 fixture/removal.
3. Define the new graph snapshot envelope and fail closed on every old/unknown version. Prove
   canonical bytes, fingerprint tampering, live/offline parity, and relocation.
4. Switch the canonical builder atomically to load -> elaborate -> validate -> project. Keep the
   graph available to snapshot capture without exposing a second shipped route.
5. Execute the deletion ledger and collapse `PipelineContext`. Move the two neutral constraint
   helpers first. Delete wrong-oracle tests with their mechanisms; retain public and exact-graph
   oracles.
6. Run the public acceptance routes, a realistic scale budget, real TEAx package generation, and the
   full maintained quality gates.
7. Recapture all 37 fixtures once. Use the timestamp-churn protocol and classify every real output
   change against the Item 5 ledger. Delete the dual-run scaffolding in the same landing.

Required adversarial tests before cutover:

- duplicate/mismatched calc QNs and normalized member-name collisions cannot poison payload;
- missing or wrong calc/compilation/port payload fails by exact ID;
- anonymous, duplicate, missing, `BLOCK`, and `UNASSESSED` constraint decisions fail or project by
  their explicit contract, never by `ADMIT` fallback;
- missing input/output metadata and invalid eligibility fail graph/snapshot validation;
- exact compiled output identity agrees with exact output ports;
- occurrence child selection matches native `Usage.usages` on retyping, inheritance, and explicit/
  implied redefinition fixtures;
- projection output is invariant under display-string mutations that leave typed ancestry and edges
  unchanged;
- scale fixture records occurrence/node/edge counts, elaboration time, projection time, snapshot
  size, and peak memory under a pre-recorded budget;
- customer composition has one public input whose off-default mutation reaches every bound consumer
  live and from a relocated snapshot;
- C19 applies `80.0` on both paths after the legacy tripwire and mechanism are deleted;
- real TEAx package generation/seal/execute uses stock public APIs;
- old snapshots and unknown future schema versions fail before projection;
- canonical graph/envelope bytes are stable across repeat capture and relocation; and
- all 37 recaptured fixtures have zero unclassified real changes.

## Design/Spec Disposition

- **[AGENT] Spec:** no amendment. R1, R8, and R9 already cover all discovered defects.
- **[AGENT] Design:** D3 amended to assign effective semantic child selection to SysIDE
  `Usage.usages` and concrete occurrence creation to codegen. D8/D9 already require direct-edge
  toposort, structured occurrences/IR, and no later resolution from strings; record the current
  implementation gaps in the plan rather than accreting duplicate design prose.
- **[AGENT] Cross-repo ownership:** no change. `agentic-mbse` already owns live constraint
  extraction and the validated SysIDE ID boundary. Codegen owns calc extraction, compilation,
  elaboration, projection, and the graph snapshot envelope.

## Artifacts Consulted

- `.project/backlog/epic_elaborate_first_architecture.md:351-382`
- `.project/active/elaborator-design/spec.md:8-54`
- `.project/active/elaborator-design/design.md:143-316,355-428`
- `.project/completed/20260809_elaborator-breadth/plan.md`
- `.project/completed/20260809_elaborator-breadth/audit_v3.md`
- `.project/completed/20260809_elaborator-breadth/diff-ledger.md`
- `.project/research/20260808-103243_syside-identity-and-redefinition-probe-record.md`
- `.project/research/20260807-145336_elaborate-first-instance-graph-architecture.md`
- `.project/research/20260807-170356_elaborator-specialization-retypes.md`
- `.project/active/spike-syside-occurrence-authority/findings.md`
