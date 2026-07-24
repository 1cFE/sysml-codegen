# Design Review: Lifecycle Remediation Item 1 — Occurrence and Demand Integrity

**Design:** `.project/active/constraint-lifecycle-occurrence-demand/design.md`  
**Spec:** `.project/active/constraint-lifecycle-occurrence-demand/spec.md`  
**Spec Re-review:** `.project/active/constraint-lifecycle-occurrence-demand/spec-rereview.md`  
**Review File:** `.project/active/constraint-lifecycle-occurrence-demand/design-review.md`  
**Date:** 2026-07-19

---

## Fundamental Assessment

**Concerns. Revise, not Rework.**

The overall approach is right. One ordered prepared usage batch can replace the current duplicate
live and replay occurrence queries. One demand merge after `_binding_target` can replace the current
route-counted, last-write-wins materializer. An active recursion stack is the right cycle model.
None of those changes needs a snapshot-format or catalog-schema change.

The design is not ready to implement as written. Five load-bearing boundaries are incomplete:

1. The proposed same-target conflict rule rejects legitimate current multi-scope calc routes.
2. Constraint-only value-source provenance is required before the operation that can discover it.
3. The recording wrapper is owner-query atomic, not prepared-batch atomic.
4. Warning projection can still mask the BLOCK diagnostic that is supposed to follow it.
5. The exact APIs needed to carry one batch through live, replay, and capture are absent, so the
   serializer either evaluates the profile again or requires production files outside the claimed
   six-file union.

These are corrections to the design boundary. They do not require a different architecture.

### Focused judgment

- **One prepared batch:** Correct direction. Source ordering, complete association checking,
  excluded visibility, filter-before-expansion, and strict actual resolution after enrichment are
  all achievable. Warning-before-BLOCK is not yet total.
- **Live and replay threading:** Feasible without a snapshot-format change. Replay can carry the
  ephemeral batch in its existing classifier-input result. The design still needs exact signatures
  and one `Path`-keyed copy-on-write return contract.
- **Association cross-check:** Count plus exact identity and location equality is sufficient for
  current same-batch facts. The profile copies those values directly from each usage
  (`../agentic-mbse/src/agentic_mbse/sysml/executable_profile.py:809-899,996-1008`). It detects
  deletion, duplication, and reorder for legitimate current shapes without inventing durable
  identity. Structurally identical anonymous usages at one location remain outside Item 1, as the
  spec records at `spec.md:284-285`.
- **Cycle model:** Per-recursion-path active-stack membership preserves DAG, diamond, subtype, and
  retype traversal. A global visited set would be wrong. Batch-wide recorder rollback and the
  public exception surface are still unspecified.
- **Demand seam:** `_binding_target` is the correct Item 1 identity seam. The proposed raw-scope
  agreement rule and provenance timing are not correct.
- **Copy-on-write seam:** Returning a new graph-only attribute map from `supplied_values.py` is a
  reasonable shared seam. Its input key types and the scope of its non-mutation claim need to be
  narrowed and typed.
- **Serializer reuse:** No version bump is needed, but the draft hides whether serialization reuses
  the prepared association or independently re-evaluates the profile.
- **Acceptance evidence:** OD-A01–OD-A13 are directionally mapped, but the unchanged RED/GREEN and
  several public fixture observations are not yet executable instructions.
- **Cleanup and LOC:** The five named obsolete paths can be deleted, but the union is not six files
  once load-bearing comments and a true capture-time batch handoff are included. D5 also adds more
  executable concepts than its current deletion budget plausibly offsets.

---

## Required Prepared-Batch Boundary

The revised design must state an exact equivalent of this call order.

### Live generation and capture

1. Build extraction data and the output registry.
2. Create one live occurrence source and one **transactional** recording wrapper.
3. Call `prepare_constraint_usages(...)` once. It must:
   - evaluate and version-check the profile once;
   - verify all usage/decision pairs before warnings or queries;
   - render NON_NUMERICAL warnings with a total projection policy;
   - halt on BLOCK before owner expansion;
   - filter unsupported/excluded owners before queries;
   - expand every supported admitted owner into immutable prepared items; and
   - commit the recording transcript only after the whole batch succeeds.
4. Call shared copy-on-write enrichment with that prepared batch. No strict actual resolution occurs
   before this call returns.
5. Build `ParameterGroupDeriver` from the returned graph-only attribute map.
6. Call `lower_constraints(..., prepared=batch, ...)`. Its production signature must no longer take
   an occurrence index or calc usages for owner expansion. It must not evaluate the profile or query
   occurrences.
7. Build/extend the graph and catalog, then return the context. Publish the committed transcript only
   on this successful path.
8. For capture, either carry the batch's exclusion projection to the serializer or explicitly narrow
   the “evaluate once” claim. The recommended contract is to carry immutable `excluded_indices` (or
   the batch itself) through the context and pass it to `serialize_extraction_snapshot`; the
   serializer must not run warnings, BLOCK handling, or occurrence expansion.

### Same-checkout replay

1. Load and validate the existing v3 snapshot.
2. Create one `FrozenOccurrenceIndex`.
3. Call the same `prepare_constraint_usages(...)` once with snapshot location policy.
4. Call the same enrichment function and receive a new `dict[Path, list[DesignAttributeData]]`.
5. Carry the prepared batch in the classifier-input result.
6. Call `lower_constraints(..., prepared=batch, ...)` without constructing another frozen index or
   querying occurrences again.

At minimum, the design must pin these API properties:

```python
def prepare_constraint_usages(
    facts: ConstraintFacts,
    *,
    occ_index: OccurrenceIndex,
    calc_usages: Sequence[CalcUsageData],
    source_location_mode: Literal["live", "snapshot"],
    source_roots: Sequence[Path],
) -> PreparedConstraintBatch: ...

def enrich_graph_design_attributes(
    real_design_attrs: Mapping[Path | str, Sequence[DesignAttributeData]],
    *,
    calc_usages: Sequence[CalcUsageData],
    prepared: PreparedConstraintBatch,
    redefinitions: Sequence[RedefinitionData],
    design_overrides: Sequence[RedefinitionData],
    usage_type_map: Mapping[tuple[str, str], str],
) -> dict[Path, list[DesignAttributeData]]: ...

def lower_constraints(
    facts: ConstraintFacts,
    *,
    prepared: PreparedConstraintBatch,
    registry: OutputRegistry,
    design_attrs: Mapping[Path, Sequence[DesignAttributeData]],
    source_location_mode: Literal["live", "snapshot"],
    source_roots: Sequence[Path],
) -> list[ConcreteConstraint]: ...
```

Names may change. The ownership, ordering, mutation, and no-requery properties may not.

---

## Dimensional Review

### 1. Spec Compliance

**Assessment: Fail**

The design covers every requirement family and retains the exact OD-A08–OD-A10 QNs, messages, and
counts. It also keeps same-checkout replay non-certifying. No owner-given referent was dropped or
softened.

The following gaps prevent compliance:

- D5 requires same-precedence origins to agree on raw materialization scope
  (`design.md:140-146`). Existing valid snapshots contain absolute `::` bindings that normalize to
  one target while being consumed from distinct scopes. Examples include the two sibling chamber
  bindings in `tests/fixtures/sibling_channel_ambiguity/extraction_snapshot.json:216-270` and the
  two HIF driver consumers in `tests/fixtures/fusion_tea/extraction_snapshot.json:2024-2122`.
  Normalizing all bindings and rejecting scope disagreement before resolution would fail these
  unchanged controls even when value and grouping outcomes agree.
- D5 allows constraint-only grouping from the winning literal override/redefinition source, while
  the demand-merge boundary says missing provenance fails before `_resolve_value`
  (`design.md:143-146,203-205,267`). The winning record is not known until value resolution.
- The live recorder commits each successful owner immediately
  (`src/sysml_codegen/analysis/part_instance_index.py:392-395`). If owner A succeeds and later owner
  B fails, A remains in the local journal. Export suppression is not batch rollback.
- “Warnings, then BLOCK exactly as today” (`design.md:181-185`) retains the known masking path:
  location projection can raise before `_report_non_numerical_warnings` completes
  (`constraint_lowering.py:537-587`). The promised BLOCK diagnostic then never appears.

Capture fidelity also needs correction. The spec marks association, exact target equality, calc
precedence, provenance, ordering, and the LOC gate `[INFERRED]` (`spec.md:80-145,199-215`). The
design acknowledges that status at `design.md:108-109`, then tells planning to treat all of those
choices as fixed at `design.md:442-446`. They remain challengeable agent decisions unless the owner
originates them.

### 2. Pattern Consistency

**Assessment: Concerns**

The design correctly reuses `OccurrenceIndex`, `_binding_target`, `_resolve_value`,
`ParameterGroupDeriver`, graph copy-on-extension, and the existing replay classifier-input carrier.
It does not introduce a new production module or Item 2 resolver.

The unresolved provenance rule risks duplicating the matching logic in
`resolution/graph_builder.py:_find_literal_redefinition`, because that helper returns only a float
(`graph_builder.py:1197-1268`). The revised design must either make the materializer's existing
exact tier-2a match return the matched record locally or define a provenance-bearing materializer
result. It must not add a parallel general resolver.

### 3. Abstraction Quality

**Assessment: Fail**

`PreparedConstraintUsage` earns its existence. A single demand object per normalized target also
earns its existence.

The current `LogicalDemand` description combines identity, several resolution contexts, grouping
provenance, route precedence, conflict diagnostics, and origin sorting without defining the origin
or resolution-result types (`design.md:134-146`). That hides the hardest rule rather than
simplifying it.

The revised design should separate three facts:

1. target identity and ordered origins before value resolution;
2. one logical resolution operation that may compare origin-specific lookup contexts; and
3. a resolution outcome carrying the winning value record/source when one exists.

`resolve_logical_demand(demand, ...)` may internally compare relevant origin contexts and raise if
they yield different values or non-literal dispositions. That is still one resolution operation per
logical demand and does not absorb Item 2. Raw `instance_scope` inequality by itself must not fail.

### 4. Duplication Avoidance

**Assessment: Concerns**

Deleting `collect_bare_actual_demand`, independent exclusion selection, duplicate live/replay
bucketing, route-counted materialization, and last-write-wins synthesis is the right cleanup.

The serializer remains a second profile evaluation unless the prepared exclusion projection is
threaded through capture. Reusing the association helper improves checking but does not make it one
evaluation (`serializer.py:139-160`; `capture.py:47-69`). The design must choose and state one of:

- carry prepared exclusion indices to serialization; or
- explicitly limit “evaluate once” to context construction, keep serializer association pure, and
  test the second evaluation's profile-version and no-warning behavior.

The first option is cleaner but adds `pipeline_context.py` and `snapshot/capture.py` to the
production union.

### 5. Data Structure Clarity

**Assessment: Fail**

The two ellipsis signatures at `design.md:164-175` are not enough for the current call graph.

The design must define:

- the complete `PreparedConstraintBatch` fields, including ordered items and exclusion projection;
- whether and how the live transcript commits atomically;
- the demand-origin fields used for target identity, value lookup, grouping, and diagnostics;
- a provenance-bearing value-resolution result;
- one `Path`-keyed enrichment return type for both routes; and
- the new `lower_constraints` signature that makes a second query impossible by construction.

The key normalization is real, not cosmetic. Live attributes are `dict[Path, ...]`, while the
loader returns string keys (`snapshot/loader.py:814-817`) and replay converts them later
(`snapshot/graph_rebuild.py:128-134`).

### 6. Route Safety

**Assessment: Fail**

Owner routes are explicit and safe: supported admitted owners expand; unsupported/excluded owners
remain visible and query-free; package no longer owns the default arm. The proposed replay route can
use one frozen index and no schema change (`design.md:220-226`).

Three route boundaries remain unsafe:

- warning location failure can replace the intended BLOCK route;
- serializer association has no stated profile-version/no-warning contract; and
- cycle errors are promised both as `RecursiveContainmentError` and as contextual generation errors
  (`design.md:127-133,188-190,264`).

Pin one public error surface. Recommended: the walker raises structured
`RecursiveContainmentError`; preparation raises `CodeGenerationError` from that cause; public tests
assert both the generation context and structured `__cause__` fields.

### 7. Bets & Decisions Integrity

**Assessment: Fail**

B1–B5 are genuine bets and each states what fails if false. Most decisions name rejected
alternatives. B2 is the riskiest and the codebase already supplies counterpressure: exact target QN
can be shared by consumers in distinct scopes. The hidden bet is that those scopes may be rejected
before proving a semantic value conflict. Current fixtures show that belief is false as a general
rule.

The second hidden bet is that serializer exclusion selection can share “the association seam”
without affecting the one-batch claim. The current capture API has no prepared batch input, so this
is false unless the API changes.

No snapshot/profile/catalog version bump is justified by ephemeral batch and demand types. The
design must still centralize the `PROFILE_SEMANTIC_VERSION` guard at preparation and explain how a
direct serializer call is protected if it re-evaluates the profile.

### 8. Reader Comprehension

**Assessment: Concerns**

The core concept is clear and the live/replay narratives are easy to follow. “Two-stage commit” is
misleading while the recorder writes per query and serialization sits outside the batch. The
undefined origin/result structures also hide the most complex behavior. Correcting the APIs and
transaction point will make the mental model match the implementation.

---

## Issues by Severity

### Critical — Must fix before implementation

- **C1 — Same-target conflict rejects legitimate scopes.** Replace raw materialization-scope
  agreement with semantic, form-aware value-context handling. Add unchanged controls for the
  existing sibling, retype, IFE, and fusion absolute-reference shapes. — Spec Compliance,
  Abstraction Quality
- **C2 — Provenance is required before it can be known.** Define a provenance-bearing resolution
  outcome and validate constraint-only fallback after the logical demand's value operation, while
  keeping merge-before-resolution and one operation per target. — Spec Compliance, Data Structures
- **C3 — Recorder transaction stops at one owner.** Stage transcript writes and commit only after
  the complete prepared batch succeeds. A failed batch must expose no partial recorder journal,
  context, snapshot, graph, catalog, or target mutation. — Route Safety
- **C4 — Warning projection can mask BLOCK.** Define a total warning-location policy and test an
  unmappable NON_NUMERICAL sibling followed by BLOCK. The ordered warnings and complete BLOCK
  diagnostic must both be observed with zero queries. — Spec Compliance, Route Safety
- **C5 — Batch APIs do not enforce the claimed call graph.** Pin the prepared-batch, enrichment, and
  lowering signatures and the live/replay/capture order described above. — Data Structures,
  Duplication Avoidance

### Major — Must fix in the design revision

- **M1 — Serializer ownership is ambiguous.** Decide whether capture receives prepared exclusion
  indices or serialization performs a second pure profile association. State the version and warning
  behavior honestly. — Duplication Avoidance, Bets
- **M2 — The six-file union is false if cleanup is complete.** Transcript ownership changes make
  comments stale in `orchestration/pipeline_context.py:133-137` and
  `snapshot/__init__.py:12-18`; moving the profile guard also makes
  `snapshot/loader.py:773-775` stale. A capture-time prepared handoff additionally touches
  `snapshot/capture.py` and `pipeline_context.py`. OD-R41 automatically adds every such production
  path. Replace “six-file union fixed” with the actual union before implementation. — Spec
  Compliance, Cleanup
- **M3 — Non-positive executable LOC is not yet plausible.** D5 adds `LogicalDemand`, implicit origin
  records, multi-field conflict logic, value-source provenance, and a resolution outcome. Batch
  transcript staging and shared enrichment add more. The named deletions remove duplicate loops,
  but the design provides no per-file executable-LOC budget showing that these concepts fit under
  the default gate. Simplify the conflict/origin representation and budget executable additions
  against named deletions before planning. — Abstraction Quality, Duplication Avoidance
- **M4 — OD-A01–OD-A13 are not fully executable yet.** Record exact test files/node IDs, the
  predecessor worktree/overlay command, unchanged-test hashes, fixture source values and expected
  sibling verdicts, cycle exception field values, and exact A08/A09 group/catalog projections.
  Ensure the five RED nodes use public APIs available at both revisions so RED is the named defect,
  not an import/signature failure. — Spec Compliance
- **M5 — Agent bets are hardened in the handoff.** Replace `design.md:442-446` “fixed” treatment for
  `[INFERRED]` mechanisms with language that preserves their agent-grade, evidence-challengeable
  status. — Capture Fidelity, Bets

### Minor — Advisory

- **A1 — Narrow the copy-on-write claim.** The new enrichment function can avoid mutating attribute
  maps, but replay still mutates loaded `CalcUsageData` bindings during self-binding rescue
  (`pipeline_builder.py:572-625`; `graph_rebuild.py:77-80`). Say “attribute enrichment is
  copy-on-write” unless the wider route is also changed.
- **A2 — Address stale snapshot-context defaults deliberately.** The replay context currently omits
  facts, concrete constraints, transcript, and lowering mode (`orchestration/snapshot_context.py:61-76`),
  so it reports default values that do not describe the rebuilt graph. This is existing debt, but a
  prepared-batch context field would make the asymmetry more visible. Either include the file in the
  union or record a bounded follow-up.
- **A3 — Test association mutations with independent values.** Current decisions alias the usage's
  mutable identity/location objects. Mutation tests should clone decision fields before reordering so
  they prove equality cross-checking rather than shared-object identity.
- **A4 — Keep the active-stack key structural.** Use owning-definition QN plus feature/type identity
  and copy the stack per recursion path. Sorting may select deterministic error traversal, but it must
  not become a global visited set or alter final finite occurrence ordering.

---

## Recommendations

1. Revise D5 first. Define target identity, origin value context, grouping provenance, and
   provenance-bearing resolution outcome separately. Add existing multi-scope absolute-reference
   controls.
2. Pin the prepared-batch API and transactional transcript boundary using the call order in this
   review. Remove occurrence/profile inputs from lowering that would permit requery.
3. Make warning rendering total before BLOCK and pin the structured cycle exception/cause contract.
4. Choose the serializer ownership model and update the production union honestly.
5. Turn OD-A01–OD-A13 into exact selectors and commands, then produce an executable-LOC budget that
   includes every added production path.

---

## Resolutions

None recorded. This non-interactive stage review requires the design agent to revise the design and
return it for review.

---

**Overall:** Revise  
**Next Steps:** Re-run `my-design` (or return to the design-agent session) with this review. Do not
begin implementation planning until C1–C5 and M1–M5 are resolved in the design. The reviewer does
not edit `design.md`.
