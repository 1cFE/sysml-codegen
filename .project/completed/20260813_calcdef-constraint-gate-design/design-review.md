# Design Review: Calc-Definition Constraint Gates

**Design:** `.project/completed/20260813_calcdef-constraint-gate-design/design.md`
**Spec:** `.project/completed/20260813_calcdef-constraint-gate-design/spec.md`
**Follow-on item:** `.project/completed/20260813_calcdef-constraint-gate-design/implementation-item.md`
**Review File:** `.project/completed/20260813_calcdef-constraint-gate-design/design-review.md`
**Date:** 2026-08-13

---

## The Point

Physics constraints must make design search trustworthy. For this capability, one asserted
calculation-definition constraint must execute once per concrete calculation occurrence, while the
authored usage remains one coverage member. Repeated uses of one definition must not collapse, and
one failed occurrence must remain visible in the complete result population.

Authority: the design-search obligation is owner-originated in
`.project/active/constraint-semantics-contract/rulings-20260812.md` (owner-stated frame). The
one-check-per-occurrence and usage-versus-result rules are `[AGENT] (ratified by owner, 2026-08-12)`
in Q2 and Q5, not owner-originated settled rules.

Falsifier: two sibling calculations use one definition, one gate fails, and generation emits one
collapsed check, orders a gate before its real producer, or reports satisfaction without the failed
occurrence.

## Fundamental Assessment

**Assessment: Concerns. Overall approach is sound; the design is not implementation-ready.**

The right architecture is present: expand inside elaboration, retain one usage authority, key each
gate by the authored usage plus exact calculation occurrence, and make projection render rather
than rediscover semantics. The probe reran successfully on 2026-08-13 and confirmed exact 0/1/2
definition matches, two distinct calculation IDs in one shared scope, exact literal and attribute
actuals, and modeled-default recovery. No rendered-name lookup or second inventory is needed
(`probes/probe_calcdef_attachment.py`; `probes/findings.md`, “Executable observations”).

The handoff still has three load-bearing technical gaps. The proposed recursive `NodeId` wire form
does not define an exact sortable grammar. `CalculationInputRef` is absent from dependency and
selection semantics, so a producer-backed gate can be ordered before its producer. The formal-join
algorithm works for the probe's inline predicate but does not define the different identity path for
a definition-typed constraint. These are corrections to the chosen approach, not reasons to add a
second authority or replace the architecture.

### Product-lens result

**Gate: DISPOSE-and-proceed after revision; not BLOCKED.**

- **design-review-F1 [DO, agent/ratified]:** the design intends canonical source reuse but omits
  how `CalculationInputRef` participates in dependency closure. As written, a gate can consume a
  producer channel absent from its semantic dependency set. Source: Q2 and the spec's inherited
  positive-resolution law.
- **design-review-F2 [DO, agent/inferred]:** the design does not carry the spec's challengeable
  definition-typed binding case into an algorithm or acceptance test. Source:
  `spec.md:164-167` (`[INFERRED]`).
- **Disposition required:** revise the design and follow-on item as specified below. Neither
  finding contradicts an owner-originated or `[HARD]` product obligation; the design's intended
  behavior serves the owner-stated point.

Neither design smell fires. The gate does not compensate for a producer guarantee; it is meant to
reuse the calculation port's already-decided source. The intended invariant owner also remains the
instance graph. The missing dependency traversal is an incomplete implementation contract, not an
undeclared transfer of semantic authority.

---

## Confirmed Findings

### F1 — Critical: `CalculationInputRef` is missing from graph and projector dependency semantics

The design adds `CalculationInputRef` to `InputRef` and says projection looks up the source already
projected for the referenced calculation port (`design.md:80-115`, `:246`). That lookup can preserve
literal, design-attribute, modeled-default, and defaultless sources. It is not sufficient for a
producer-backed source.

Current dependency code recognizes only `ProducerRef`:

- graph cycle validation traverses only `ProducerRef` edges
  (`src/sysml_codegen/elaboration/graph.py:860-892`);
- edge validation has branches only for `NodeRef` and `ProducerRef`
  (`src/sysml_codegen/elaboration/graph.py:905-929`);
- projector topological ordering adds dependencies only for `ProducerRef`
  (`src/sysml_codegen/elaboration/project.py:1015-1027`);
- projection selection closure likewise follows the existing edge union
  (`src/sysml_codegen/elaboration/project.py:1260-1300`);
- the codec's closed edge union currently has no calculation-port case
  (`src/sysml_codegen/snapshot/instance_graph.py:192-220`).

If a calculation port resolves to `ProducerRef(P.output)`, the gate's projected `ModuleInput` also
names `P.output`, but its graph edge remains `CalculationInputRef`. The current topological graph
therefore has no gate-to-`P` dependency. Calculation modules being *constructed* before constraint
modules (`project.py:225-227`, `:734-803`, `:847-921`) does not fix final topological order. The
ready queue is sorted independently. The result is order-dependent and can consume a channel before
its producer runs.

This also leaves cycle validation, target selection, semantic-edge inspection, and decoded-graph
validation incomplete. It directly fails review focus 2 and the producer-backed part of the public
acceptance contract.

**Required cure:** define one graph-native dereference law for `CalculationInputRef` and use it at
every edge consumer. Validation must prove that the target is an input port on the gate's attached
calculation. Dependency and selection closure must follow the target calculation port's resolved
state: add its upstream calculation when that state is a `ProducerRef`, and add no artificial
dependency on the matched calculation module for literal, attribute, default, or defaultless
states. Add a kept producer-backed topology test that would fail if the gate is ordered before the
real producer, plus cycle, selection, cross-occurrence, and missing-port mutations.

### F2 — Critical: the qualified `NodeId` shape is not an exact frozen identity contract

The information content is correct: `(constraint usage DeclarationId, full CalcNode.node_id)` is
the minimum identity supported by the probe. Reusing `NodeId` also keeps `InstanceGraph` maps,
`ConsumerPortId`, dependency keys, and module maps on one key type. The proposed representation can
be hashable and acyclic if construction enforces a one-level constraint-to-calculation
qualification.

The design does not define that contract precisely enough to implement or review:

- Current `NodeId` is `@dataclass(frozen=True)` and is hashable but not orderable
  (`src/sysml_codegen/elaboration/identity.py:149-184`). Sorting two current IDs raises
  `TypeError`. The design nevertheless specifies `matches(U) = sorted(calc.node_id ...)`
  (`design.md:160-170`) and says ordering will be added without defining a total key.
- Adding dataclass field ordering is not enough. `scope` is a union of `OccurrenceId` and
  `PackageScopeId`; cross-variant comparison needs an explicit tag. `NodeKind` and the optional
  nested node also need stable ordering rules.
- “The current three-element node tuple plus a fourth nested full node tuple”
  (`design.md:66-69`) is ambiguous. Current `NodeId.to_wire()` returns a JSON *string*. The review
  cannot tell whether the fourth value is a nested JSON array or another encoded string, whether
  unqualified v4 nodes have exactly three values or a fourth null, or which extra/missing shapes
  are refused.
- A recursive type is acyclic only if construction and decode both require the attached node to be
  an unqualified `CALCULATION` ID. The prose states kind restrictions, but it does not specify the
  constructor invariant, maximum depth, exact decoder grammar, or canonical re-encoding check.
- Catalog 4 stores the calculation identity as another JSON string (`design.md:253-263`). Without
  one named canonical parser/encoder shared with graph v4, graph identity and catalog identity can
  become two manually synchronized serializations.

Status against review focus 1: hashability is conditionally sound; sortability and exact
serialization fail as specified; acyclicity is only asserted; use in maps and ports is structurally
sufficient once those gaps are fixed. Receipt, catalog, and seal propagation cannot certify an
ambiguous wire grammar.

**Required cure:** publish the exact v4 grammar and one total `NodeId.sort_key()`. State the exact
array arity and type at each position, whether the nested value is structured data or a string,
and the canonical compact encoding. Enforce in `NodeId.__post_init__` and decode that only a
`CONSTRAINT` may attach exactly one unqualified `CALCULATION` with the same scope; all other nested
or extra shapes fail. Use the one encoder for catalog `calculation_node_id`. Add hash/map,
cross-scope-variant sort, `ConsumerPortId`, dependency-map, recursive/malformed decode, canonical
re-encode, and catalog round-trip tests before freezing v4.

### F3 — Critical: the formal-join law does not cover definition-typed calc-def constraints

The probe proves one inline predicate whose referenced leaves are the owning calculation
definition's own input formals. In that case, the live `FeatureSlotIndex` can map an occurrence
input declaration to the calculation formal and a gate can lawfully reference the matching
calculation port (`probes/findings.md:131-181`).

The design generalizes that evidence too far. It says to recover “the predicate leaf's root formal”
and find a calculation input with the same root provenance, and that the gate always stores a
`CalculationInputRef` (`design.md:137-146`). For a definition-typed constraint, the predicate leaf
is a **constraint-definition formal**. Its actual binding may reference a calculation formal, a
literal, or another already-supported source. The constraint-formal declaration ID is not the
calculation-formal declaration ID, so equality of their root identities is not a lawful join.

The spec explicitly leaves this as challengeable `[INFERRED]` behavior: definition-typed actuals
continue through the existing constraint-formal resolver, and only an actual that refers to a
calculation formal is redirected to the matched calculation port (`spec.md:164-167`). The probe
also lists definition-typed assertions as unproven (`probes/findings.md`, “Open Questions /
Follow-ups”). The design silently hardens the inference and has no definition-typed public
acceptance case.

**Required cure:** specify two paths. Inline calc-formal references join directly by exact root
calculation formal. Definition-typed constraint formals first use the existing exact
constraint-actual resolution; only a resolved actual whose semantic referent is a calculation
formal becomes `CalculationInputRef`. Literal, attribute, producer, default, and other supported
actuals retain their existing typed source law. Add positive and negative definition-typed
fixtures, including mismatched, duplicate, and cross-occurrence formal identities. If
definition-typed calc-def gates are intentionally unsupported, state that as a visible disposition
and reconcile it with Q2 before implementation.

### F4 — Critical: the follow-on item's owner provenance is manufactured

`implementation-item.md` contains three owner grades that are not supported by owner-originated
source material:

- The Delivery boundary labels the orchestration/stage-prompt sentence as `[OWNER-VERBATIM]`
  (`implementation-item.md:15`). It was not spoken by the owner. This is the known concern and is
  a direct capture-fidelity violation.
- “Production implementation in the current design-stage delivery” is `[OWNER]`
  (`implementation-item.md:84`). The actual boundary in epic Item 6 is `[AGENT] (ratified by
  owner, 2026-08-12)` (`epic_constraint_semantics_contract.md:872-880`).
- “The parked BLOCK denominator/build-halt premise conflict remains parked” is `[OWNER]`
  (`implementation-item.md:196`). Its authority is inherited from the child spec, Item 3, and the
  agent-ratified rulings. No owner-originated statement was found.

These grades would turn challengeable stage boundaries into settled owner commands at the next
artifact hop. This is an ownership ambiguity and directly prevents Item 6's success criterion at
`epic_constraint_semantics_contract.md:930` from passing.

**Required cure:** remove the false grades rather than preserving them in explanatory prose.
Regrade the stage sentence as `[INHERITED: orchestration stage input]` or omit it in favor of the
epic boundary. Regrade the current-delivery boundary as `[INHERITED:
epic_constraint_semantics_contract.md Item 6]` while preserving its agent/ratified source grade.
Regrade the parked conflict as `[INHERITED: spec.md; Item 3; rulings Q5]`. Do not mark any of these
settled or owner-originated.

### F5 — Major: Item 8 owns a prerequisite seam, but the design and pins omit it

The current epic added Item 8 after Item 6 was first shaped. Item 8 owns the unit metadata lane for
constraint formals and explicitly names Item 6 as a consumer
(`epic_constraint_semantics_contract.md:1038-1078`). Its characterization is required input to this
design, and Item 8 may itself cause fingerprint churn and a snapshot recapture.

The design neither cites Item 8 nor orders it before Item 6's graph-v4 freeze and 21-fixture
recapture. Its codegen starting pin `cc14cf0...` predates Item 8. That leaves two owners deciding
constraint-port metadata and recapture order independently. It also undermines the claim that no
agentic-mbse or port-metadata premise can change during implementation.

**Required cure:** add Item 8's characterization/landing as an explicit prerequisite to the
follow-on item, or state the exact reviewed descendant commit that contains it. Put Item 8 before
the v4 codec freeze and final recapture so the 21 fixtures are not recaptured twice. Name the unit
agreement/disagreement tests that Item 6 consumes. If the two items must remain independent, state
which item owns the final `PortMetadata` invariant and which owns the single final-schema
recapture.

### F6 — Major: the file and test manifest contains stale paths and omits required version surfaces

Confirmed stale paths:

- `src/sysml_codegen/elaboration/exact_pipeline_context.py` does not exist
  (`design.md:360`; `implementation-item.md:167`). The landed file is
  `src/sysml_codegen/orchestration/exact_pipeline_context.py`.
- `src/sysml_codegen/generation/seal.py` does not exist (`design.md:362`;
  `implementation-item.md:169`). The landed file is `src/sysml_codegen/contracts/seal.py`.
- `.project/completed/20260813_calcdef-constraint-gate-design/probes/scratch/` does not exist
  (`design.md:488`; `implementation-item.md:285`). The models are in `probes/models/`.
- TEAx tests do not live at `packages/teax-simkit/tests/...` (`design.md:406-407`;
  `implementation-item.md:180-182`). The existing test root is
  `packages/teax-simkit/simkit/tests/`.

Required production surfaces omitted from the manifest:

- `src/sysml_codegen/elaboration/diagnostics.py`, where the three new diagnostic enum values must
  be declared (`diagnostics.py:10-27`);
- `src/sysml_codegen/elaboration/__init__.py`, which currently exports the graph input vocabulary;
- the actual receipt file, `src/sysml_codegen/orchestration/exact_pipeline_context.py`;
- `src/sysml_codegen/contracts/seal.py` if sealing assertions or pins change.

Required codegen tests omitted or under-specified:

- `tests/conformance/test_exact_pipeline_context.py` hard-codes `instance-projector/v1` and tests
  receipt disagreement;
- `tests/conformance/test_elaboration_graph_roundtrip.py` pins graph v3;
- `tests/conformance/test_catalog_schema_version.py` and
  `tests/conformance/test_runtime_contract_version.py` pin catalog 3.0.0;
- `tests/conformance/test_v6_recapture_batch.py` and
  `tests/fixtures/v6_recapture_batch/batch.json` own the reviewed recapture batch;
- dependency/selection coverage must name the existing topology/selection surface, not only the new
  identity unit file.

The TEAx manifest is much too small for a replace-not-extend catalog bump. The consumer currently
accepts only 3.0.0 (`simkit/evaluation/package_load.py:33-50`), and five committed TEAx fixture
packages embed catalog 3.0.0 under `simkit/tests/evaluation/fixtures/{constraint_free,
excluded_only,zero_channel,sealed_package,f1_arithmetic}/...`. Updating acceptance to 4.0.0 makes
all five stale. Existing model-contract skew, package-load, query, and no-reconstruction tests must
also move; one new standalone fixture cannot cover this blast radius.

**Required cure:** replace the stale paths, add the omitted production/version/recapture tests, and
enumerate the TEAx fixture packages and existing test modules that must be regenerated or revised.
Make the cross-repository acceptance home an actual `simkit/tests/...` path. Record the final
producer and consumer SHAs only after those baselines pass.

### F7 — Major: catalog and public-order checks need one explicit oracle at each tier

The intended report behavior is compatible with Item 3. Current projection walks constraints by
`node_id.to_wire()` and preserves that list into aggregator inputs
(`src/sysml_codegen/elaboration/project.py:847-921`). `EXPECTED_IDS` then drives a complete result
list (`src/sysml_codegen/templates/report_aggregator.py.jinja2:18-53`). Item 3's worst-state
precedence ensures one violation cannot be hidden. Adding `calculation_node_id` to catalog
occurrence rows provides a lawful result-to-usage-to-calculation join without changing
`ConstraintEvaluation` or `ConstraintReport`.

The design nevertheless names three close but distinct orders: “full canonical `NodeId`,”
“canonical full-node-ID order,” and rendered `constraint_id` order. It does not state which list is
the sealed oracle or require the catalog occurrence rows, aggregator inputs, `EXPECTED_IDS`, and
TEAx drill-down to agree in exactly that order. It also does not say that TEAx's current silent
join omission must be removed: `study/query.py` filters out a result whose catalog lookup returns
`None` instead of refusing (`query.py`, `_case_view`).

**Required cure:** define one occurrence order as the explicit `NodeId.sort_key()` from F2. Derive
catalog occurrence order, wrapper order, aggregator inputs, and `EXPECTED_IDS` from it. At
generation preflight, compare exact ordered identities as well as sets/counts. At TEAx load or
query construction, reject every missing, duplicate, malformed, or extra `constraint_id` join;
never filter it out. Keep the report schemas and headline vocabulary unchanged. Add the many-case
test with one failure in the first, middle, and last occurrence so no ordering position can hide
it.

### F8 — Minor: the acceptance set does not prove all source categories it claims

The public acceptance section asks for literal and producer source sharing
(`design.md:422-429`), while the promoted probe models currently cover literal, design attribute,
and modeled default only. Defaultless, producer-backed, definition-typed, negated, BLOCK, and a
failed sibling are promised additions rather than existing evidence. That is acceptable for a
design, but the fixture ownership needs to be explicit so an implementation cannot satisfy the
cases with unrelated models or internal graph assertions.

**Required cure:** assign each source category and failure to `zero`, `one`, `many`, or one named
mutation/variant, and state which public entry point observes it. In particular, keep one model
where the **same formal** is producer-backed for the calculation and gate, and one where a
defaultless formal is supplied by the generated public input. Assert source identity, generated
field count, execution order, and report drill-down together.

---

## Dimensional Review

### 1. Spec Compliance

**Assessment: Fail.**

The high-level behavior matches Q2/Q3/Q5, preserves zero/one/many and the parked BLOCK build halt,
and does not change Item 3's report schema. F1 and F3 leave producer-backed and definition-typed
source reuse incomplete. F4 violates capture fidelity. F5 leaves a named prerequisite owner
unresolved.

The parked BLOCK conflict is handled faithfully: the design pins the existing build halt and does
not fabricate a post-halt report. It remains an explicit contract/documentation conflict, not an
implemented denominator rule. The design must continue to surface it until its assigned owner
disposes it.

### 2. Pattern Consistency

**Assessment: Concerns.**

One graph, exact declaration IDs, graph validation, exact codec refusal, one-way projection,
catalog-by-value, and producer-first version rollout follow landed patterns. The incomplete edge
visitor in F1 and duplicated/ambiguous identity serialization in F2 would depart from those
patterns unless corrected.

### 3. Abstraction Quality

**Assessment: Concerns.**

Extending `NodeId` and adding one typed port reference are smaller than a parallel occurrence type
or inventory and earn their existence. `CalculationInputRef` needs one centralized dereference
operation; scattered special cases in validation, projection, selection, and ordering would create
the very drift this abstraction is meant to avoid.

### 4. Duplication Avoidance

**Assessment: Concerns.**

The design avoids copied literals/defaults and a second usage inventory. Catalog JSON and graph
wire identity risk becoming two encoders (F2). Source dereference also risks parallel logic unless
one helper owns it (F1).

### 5. Data Structure Clarity

**Assessment: Fail.**

The recursive ID information is sufficient, but its ordering, exact wire grammar, maximum depth,
and catalog encoding are not fixed. The definition-typed input mapping is also not representable by
the stated “every gate input is a calculation-port reference” rule.

### 6. Route Safety

**Assessment: Concerns.**

No HTTP-style route surface exists. For generation routes, outer v6 with embedded graph v4 is
internally consistent because the v6 authority block already pins graph and projector tokens
(`src/sysml_codegen/snapshot/envelope.py:115-126`, `:423-451`). Exact v3 refusal, relocated replay,
and recapture guidance are appropriate. F5 and F6 leave the actual recapture and pin route
under-specified.

### 7. Bets & Decisions Integrity

**Assessment: Fail.**

The riskiest stated bet—one calculation port can be the source join—is plausible and supported for
attribute, literal, and modeled-default inputs by the probe. The hidden bets are that every edge
consumer will dereference the new reference consistently, that definition-typed formals share the
same root ID as calculation formals, and that Item 8 cannot change port metadata or recapture
ordering. The first and second are false as written; the third is contradicted by the epic.

Version decisions themselves are sound after cures: graph v4, outer envelope v6, projector v2,
catalog 4.0.0, and runtime 2.0.0 describe the changed surfaces correctly. The receipt already
seals projector semantics and computation/catalog content
(`src/sysml_codegen/orchestration/exact_pipeline_context.py:101-117`, `:179-204`). The model
contract includes catalog schema and catalog values in its semantic fingerprint
(`src/sysml_codegen/contracts/model_contract.py:60-79`), and the package seal retains runtime
2.0.0 because no runtime/report schema changes (`src/sysml_codegen/contracts/seal.py:111-121`).

### 8. Reader Comprehension

**Assessment: Concerns.**

The core mental model is clear. The document becomes misleading where precise terms stand in for
missing rules: “canonical,” “full node tuple,” “same source,” and “atomic” do not define ordering,
encoding, dependency traversal, or the definition-typed join. Correcting F1-F3 will make the prose
implementation-ready without adding new layers.

---

## Issues by Severity

### Critical

- **F1:** `CalculationInputRef` is absent from dependency, selection, cycle, and validation laws.
- **F2:** qualified `NodeId` lacks an exact total ordering and frozen v4 wire grammar.
- **F3:** the formal join does not cover definition-typed constraint actuals.
- **F4:** `implementation-item.md` manufactures `[OWNER-VERBATIM]` and `[OWNER]` authority.

### Major

- **F5:** Item 8's port-metadata and recapture ownership is missing from dependencies and pins.
- **F6:** multiple named paths are stale; version, recapture, diagnostic, export, and TEAx fixture
  surfaces are missing.
- **F7:** deterministic occurrence order and fail-closed TEAx drill-down lack one explicit oracle.

### Minor

- **F8:** public fixtures are not assigned to every claimed source and failure category.

## Required Revision Order

1. Correct provenance in `implementation-item.md`; no later stage should consume manufactured
   owner authority.
2. Freeze the exact `NodeId` grammar and sort key, then define the catalog encoding from that one
   codec.
3. Define centralized `CalculationInputRef` dereference semantics across validation, cycles,
   selection, topology, projection, and codec.
4. Split inline and definition-typed formal resolution and add their public cases.
5. Resolve Item 8 sequencing and final recapture ownership.
6. Correct and complete the file/test/fixture manifest, then restate the producer-first pins.
7. Pin ordered catalog/aggregator/result agreement and TEAx fail-closed drill-down.

## Owner / `[HARD]` Contradiction and Ownership Statement

No confirmed substantive design decision contradicts an owner-originated or `[HARD]` requirement.
The design obeys the hard graph/catalog version changes, preserves the hard defaultless public input
behavior in intent, and keeps the existing profile-BLOCK build halt. The lower-authority coverage
wording that describes a BLOCKed gate in a report remains visibly parked because no such report
exists after the hard halt; this review does not silently resolve it.

There **is unresolved ownership ambiguity**, so Item 6's success criterion is not met. The false
owner grades in F4 assign authority to statements the owner did not originate. F5 also leaves Item
8 and Item 6 with overlapping ownership of constraint-port metadata and snapshot recapture order.
Both must be corrected before this review can approve the handoff.

## Resolutions

None recorded. This is the independent first-pass review.

---

**Overall: Revise.** The graph-native direction is the right one and does not need architectural
replacement. Implementation must not start from the current artifacts. Once F1-F7 are incorporated,
return the revised design and follow-on item to an independent design review; the reviewer does not
edit those source artifacts.

## Resolution Round 2 — 2026-08-13

### Major — F5 remains: Item 8 cannot be certified independently

The revision assigns unit metadata to Item 8 and formal provenance to Item 6, but its recapture rule
still changes Item 8's delivery boundary without matching authority. It says Item 6 owns the only
bulk recapture and Item 8 is not certified until Item 6's graph-v4 recapture passes
(`design.md:194-201`; `implementation-item.md:58-62`). The rollout then requires a reviewed Item 8
descendant before Item 6 starts (`design.md:416-423`; `implementation-item.md:43-50`).

The ratified epic says Item 8 runs independently and owns the reviewed recapture if its churn
assessment fires (`.project/backlog/epic_constraint_semantics_contract.md:1061-1088`). Item 6 is a
design/planning item whose production implementation is outside this epic
(`.project/backlog/epic_constraint_semantics_contract.md:872-880`). The revised rule therefore makes
Item 8 certification depend on a separately authorized follow-on that the epic does not promise.
It also makes epic close depend indirectly on that follow-on because Item 7 requires Item 8 landed
(`.project/backlog/epic_constraint_semantics_contract.md:1138-1152`). Calling the delivery “stacked”
does not resolve that authority and dependency cycle.

**Required cure:** keep Item 8 independently certifiable under its existing contract. If its churn
fires, Item 8 owns the v3 recapture needed for its delivery; a later authorized Item 6 owns its v4
recapture. Avoiding the duplicate recapture requires an explicit amendment by the epic's owning
authority that authorizes the joint delivery and changes the dependency graph. An Item 6 design
decision cannot make that amendment.

### Major — F6/F7 remain: the ordered oracle has no named implementation carrier

The revision requires preflight to compare the graph, catalog, wrappers, aggregator inputs, and the
rendered `EXPECTED_IDS` sequence (`design.md:247-270`; `implementation-item.md:150-159`). Its exact
file manifests name the projector, CLI, and aggregator template, but omit both production owners of
the value: `src/sysml_codegen/generation/modules.py` and
`src/sysml_codegen/generation/constraint_plan.py` (`design.md:293-316`;
`implementation-item.md:182-204`).

Current code derives `EXPECTED_IDS` only inside the renderer from aggregator `module.inputs`
(`src/sysml_codegen/generation/modules.py:354-381`). The generation plan carries only rendered source
and coverage, so the post-build preflight has no structured expected-ID sequence to compare
(`src/sysml_codegen/generation/constraint_plan.py:17-27`, `:55-70`). The CLI builds that plan and then
runs its preflight (`src/sysml_codegen/cli/__init__.py:1250-1260`). As written, implementation must
either parse generated source, compare a fresh derivation and leave the rendered tuple unchecked, or
change an unlisted carrier. None fulfills the claimed exact five-way comparison without a hidden
second authority.

**Required cure:** name the renderer and generation-plan files in both manifests and define the
structured carrier used by the CLI comparison. The carrier must be populated from the same ordered
`G`-derived aggregator inputs used to render `EXPECTED_IDS`; preflight must compare that carried
sequence with the ordered catalog and wrapper identities before output mutation. Name a kept test
that mutates or disagrees this carrier and proves fail-closed behavior, in addition to inspecting the
generated tuple in public acceptance.

### Round 2 verdict and ownership statement

**Overall: Revise.** The product-lens result remains **Concerns**: the consumer-visible identity,
source sharing, definition-typed behavior, ordered drill-down, TEAx refusal, and fixture coverage are
now specified, but delivery cannot proceed from a cyclic prerequisite or an unnamed oracle carrier.

No unresolved owner-originated or `[HARD]` substantive contradiction was found. There is still an
unresolved ownership ambiguity: agent-grade Item 6 text attempts to move Item 8's independent
recapture and certification boundary. F5 therefore still violates Item 6's no-ambiguity success
criterion. F6/F7 is an implementation-ownership gap, not an owner/`[HARD]` contradiction.

## Resolution Round 3 — 2026-08-13

### F5 resolved — independent Item 8 certification restored

Item 8 now owns and completes its reviewed v3 recapture when its churn assessment fires, and it
lands as an independently certified prerequisite (`design.md:194-202`, `:424-428`;
`implementation-item.md:58-63`, `:341-348`). A separately authorized Item 6 owns only its later
graph-v4 recapture (`design.md:200`, `:294`, `:428`;
`implementation-item.md:62`, `:376-383`). Both artifacts say duplicate recapture may be avoided only
after an explicit epic-owner amendment changes the joint delivery and certification boundaries.
They do not assume that amendment. This matches Item 8's independent delivery and conditional
recapture ownership in the ratified epic contract
(`.project/backlog/epic_constraint_semantics_contract.md:1061-1088`).

### F6/F7 resolved — one named expected-ID carrier closes the ordered join

Both manifests now name `src/sysml_codegen/generation/modules.py` and
`src/sysml_codegen/generation/constraint_plan.py` (`design.md:298-311`;
`implementation-item.md:184-199`). The renderer materializes one tuple from aggregator inputs that
already came from the `NodeId.sort_key()`-ordered gate sequence. That same tuple renders
`EXPECTED_IDS` and populates the typed
`ConstraintGenerationPlan.expected_constraint_ids: tuple[str, ...]`; the plan field is a receipt,
not a second derivation (`design.md:248-273`; `implementation-item.md:151-161`). The CLI compares the
carried value with graph, catalog, wrapper, and aggregator order after plan construction and before
output mutation.

The acceptance ownership is also explicit. The kept generation-plan mutation covers stale,
missing, duplicate, extra, and reordered carriers with fail-before-write refusal
(`design.md:335`; `implementation-item.md:223`, `:319`). The public execution test imports the
generated aggregator and compares its rendered tuple with ordered catalog IDs (`design.md:342`;
`implementation-item.md:233`, `:320`). This closes the actual renderer-to-plan-to-preflight seam in
the landed code shape (`src/sysml_codegen/generation/modules.py:354-381`;
`src/sysml_codegen/generation/constraint_plan.py:17-27`, `:55-70`;
`src/sysml_codegen/cli/__init__.py:1250-1260`).

### Round 3 verdict

**Overall: Approve.** The two remaining material findings are objectively resolved. The product-lens
result is now **Pass**: producer ownership, delivery boundaries, deterministic consumer drill-down,
and fail-closed order checking align without a compensating consumer or hidden authority.

No owner-originated or `[HARD]` contradiction remains. No ownership ambiguity remains. Item 8 owns
its independent unit-lane certification and conditional v3 recapture; a separately authorized Item
6 owns formal provenance and its later v4 recapture; only the epic owner may authorize a joint
exception. The ordered-ID invariant likewise has one stated source and one structured receipt.
