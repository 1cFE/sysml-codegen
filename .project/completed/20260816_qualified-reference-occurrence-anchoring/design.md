# Design: Exact Owner Anchoring for Usage-Owned One-Segment References

**Status:** Implemented and certified — D10 resolved by authored route 1; D11 disposed by owner
**Owner:** Reid W
**Created:** 2026-08-15 18:11 PDT
**Complexity:** MEDIUM
**Branch:** main (`2768c68` at design start)

---

## Overview

This design restores occurrence anchoring for every one-segment semantic reference whose exact
leaf is owned by a `PartUsage`. It changes contextual resolution at the shared resolver boundary
while preserving occurrence construction, feature slots, authored-form policy, and snapshot shape.

## Related Artifacts

- **Spec:** `.project/completed/20260816_qualified-reference-occurrence-anchoring/spec.md`
- **Epic:** `.project/backlog/epic_elaborate_first_architecture.md` — ELABORATE-FIRST
- **Required Reading:** none listed for Item 8; inherited occurrence-authority inputs are listed in
  the spec and below.
- **Defect attribution:**
  `.project/reports/20260815-1338_qualified-binding-defect-attribution.md`
- **Independent assessment:**
  `.project/research/20260815-134615_qualified-binding-defect-assessment.md`
- **Qualified corpus scan:**
  `.project/research/20260815-140630_qualified-binding-corpus-scan.md`
- **Bare expression-side measurement:**
  `.project/research/20260815-142743_bare-expression-side-measurement.md`
- **Occurrence-authority findings:**
  `.project/active/spike-syside-occurrence-authority/findings.md`
- **Existing elaborator design:** `.project/active/elaborator-design/design.md`
- **Product lens:** `.project/completed/20260816_qualified-reference-occurrence-anchoring/product-lens.md`
- **Design review:** `.project/completed/20260816_qualified-reference-occurrence-anchoring/design-review.md`
- **Bare-discriminator probe:**
  `.project/completed/20260816_qualified-reference-occurrence-anchoring/spike/bare-discriminator-authorability/findings.md`

## The Point

**[OWNER-VERBATIM, 2026-08-13]** The product obligation is a design search where:

> - engineering design parameters can be freely varied, and viability and outcomes (like LCOE)
>   can be assessed
> - we differentiate from 1costingFE in that we do not embed the engineering logic:
>   predetermining the free variables and backing into all others

That search is only trustworthy when changing one modeled source occurrence changes every and only
the consumers bound to that occurrence. The ELABORATE-FIRST mission states the operational form:
**[OWNER]** every consumed modeled value resolves to exactly one runtime source, and unsupported
forms fail before generation (`.project/backlog/epic_elaborate_first_architecture.md:31-33,84-86`).

This item repairs a violation of that obligation. SysIDE has already resolved a one-segment leaf to
an exact declaration owned by a concrete `PartUsage`, but the elaborator discards the owner and
searches for the leaf slot from the consumer. In the discriminating qualified case, a consumer
inside `comp_b` that names `comp_a::length` can therefore bind silently to `comp_b.length`. The
design must retain the semantic owner through occurrence selection so the graph records the source
the model resolved, not the nearest slot that happens to look compatible.

## Research Findings

### The defect is one branch, not six separate resolver defects

Graph construction builds values and occurrences before resolving references. It then applies deep
overrides, builds calculation and constraint nodes, resolves aliases and expressions, resolves
bindings, and validates once (`src/sysml_codegen/elaboration/elaborate.py:622-634`). Four call sites
feed the same semantic resolver and expose six behavior lanes:

| Call site | Lanes carried through it | Caller-owned behavior after resolution |
|---|---|---|
| Deep literal override (`elaborate.py:1032-1079`) | deep occurrence override | Requests `plural=True`, requires raw `NodeRef`, translates failure to `OVERRIDE_TARGET_MISSING`, and does not follow aliases. |
| Alias resolution (`elaborate.py:2370-2415`) | typed alias | Resolves one target, then follows alias chains in a second pass. |
| Expression resolution (`elaborate.py:2435-2523`) | computed attribute or aggregation; asserted constraint predicate | Creates structural expression or constraint ports, then follows aliases. |
| Binding resolution (`elaborate.py:2575-2602`) | calculation input; typed constraint input | Resolves singularly, follows aliases, and preserves consumer/formal metadata. |

Every lane converges in `_resolve_semantic_reference`. Its one-segment branch immediately calls the
positional leaf resolver, while its multi-segment branch contextualizes an exact root before walking
the remaining IDs (`src/sysml_codegen/elaboration/elaborate.py:2050-2117`). Fixing a single caller
would leave the same identity defect in the others.

### The existing indexes already own the required semantics

- Exact reference evidence contains the leaf declaration ID and its owner declaration ID. Names and
  qualified names are diagnostic metadata (`../agentic-mbse/src/agentic_mbse/sysml/data_models.py:55-89`).
- The live elaborator indexes every stable feature declaration before graph sealing, so it can
  inspect the exact leaf and test its live owner metatype (`src/sysml_codegen/elaboration/elaborate.py:636-659`).
- Part-usage root contextualization already enumerates the usage's concrete occurrences and applies
  the established package, lineage, descendant, and ambiguity rules
  (`src/sysml_codegen/elaboration/elaborate.py:2119-2219`).
- Occurrences are intentionally looked up by the owner's containment-slot family. This lets a base
  usage and its materialized redefinitions share the concrete occurrence population
  (`src/sysml_codegen/elaboration/occurrence.py:223-231`). “Exact owner” therefore means exact
  declaration identity entering the established slot-family bridge. It does not mean bypassing
  redefinition semantics.
- Once an occurrence is fixed, exact slot lookup already returns either an attribute `NodeRef` or a
  computed-value `ProducerRef` (`src/sysml_codegen/elaboration/elaborate.py:2350-2366`).

No new occurrence index, slot index, graph type, or source-text evidence is needed.

### Cardinality and caller boundaries are load-bearing

The current one-segment shortcut is singular even when a caller passes `plural=True`. Only a
multi-segment path honors plural expansion (`src/sysml_codegen/elaboration/elaborate.py:2069-2113`).
Passing the caller's flag into the new owner branch would silently add direct-leaf fan-out to
`sum()` and deep overrides. The tracked corpus has no bare usage-owned leaf under `sum()`, so there
is no evidence for choosing that new policy
(`.project/research/20260815-142743_bare-expression-side-measurement.md:172-177,251-261`).

Alias following must also stay outside the shared resolver. Deep overrides need the raw attribute
node, while aliases, expressions, and bindings deliberately follow alias targets after occurrence
selection (`src/sysml_codegen/elaboration/elaborate.py:1061-1079,2417-2433`).

### Existing tests provide the right acceptance surfaces

- Typed graph helpers locate consumers for readability but assert `NodeRef` and `ProducerRef`
  identities (`tests/helpers/elaboration_graph.py:19-52`).
- Public mutation tests compare live graphs, projected graphs, and an encode/decode round trip while
  proving only one public default moved (`tests/conformance/test_elaboration_public_mutation.py:136-184`).
- Graph round-trip tests compare the rebuilt graph and exact semantic edges
  (`tests/conformance/test_elaboration_graph_roundtrip.py:32-47,202-218`).
- Strict/lenient tests already establish the pattern for a lenient diagnostic graph and a strict
  exception (`tests/conformance/test_elaboration_fail_closed.py:24-37,70-92`).
- The elaboration boundary guard rejects name, qualified-name, prefix, and first-match selection in
  resolver code (`tests/unit/test_elaboration_import_boundaries.py:29-40,189-207`).

Snapshots serialize final edges and alias targets. They cannot rerun live owner selection. A stale
snapshot therefore remains stale until recaptured
(`src/sysml_codegen/snapshot/instance_graph.py:340-377,485-533`). `semantic_edges()` does not include
alias targets, so snapshot comparison must inspect the full decoded graph or add alias-target
comparisons (`src/sysml_codegen/elaboration/graph.py:1002-1010`).

### One spec premise is not yet established

The spec requires an **authored bare** reference where consumer-lineage and owner-based selection
can land on different occurrences (`spec.md:128-130`). The corpus contains no such topology. Its
research report proposed a bare sibling of u6 with a computed attribute inside one sibling
(`.project/research/20260815-142743_bare-expression-side-measurement.md:251-256`).

A retained SysIDE 0.8.4 design probe on 2026-08-15 falsifies that proposed shape. In the u6 sibling
topology, `attribute doubled : Real = length * 2.0` inside `comp_b` resolves exactly to
`comp_b::length`, so both routes select `comp_b`. Moving the same bare reference to the parent makes
the model fail to load with `No Feature named 'length' found`. The model text, reporting script, and
exact outputs are retained at
`.project/completed/20260816_qualified-reference-occurrence-anchoring/spike/bare-discriminator-authorability/`.
This does not prove that no legal discriminating bare topology exists. It proves only that the named
candidate is not one, so the criterion cannot be treated as routine fixture authoring.

**Evidence update, 2026-08-15 (learning test; no status changed here).** The Phase-1 bounded sweep
extended that probe to fourteen candidates and **found affected shapes**: nine legal topologies make
the two routes land on different occurrences, across the computed-attribute, calc-actual, and
constraint-predicate lanes. Two independent families work — an `alias` to the sibling's leaf, and a
`private import` of it that leaves the written reference literally one bare segment. Smallest clean
case: `alias a_len for comp_a::length;` at parent scope, consumed inside `comp_b`, which wires to
`comp_b.length` (7.0) where the model says `comp_a.length` (3.0). Evidence, per-candidate element
IDs, and the recommended fixture are in
[`spike/bare-discriminator-authorability/findings.md`](spike/bare-discriminator-authorability/findings.md).

**Disposition (orchestrated run, 2026-08-15).** D10 route 1 applies on its own terms: the learning
test found an authored discriminator, so the spec criterion SC8 is kept as written and B3 is
confirmed. No route-2 amendment and no `authored bare discrimination unproven` gap record are
created. The owner reserved only the null-result branch of D10, which did not occur.

## Core Concept

Occurrence anchoring is a transient step in one shared resolver, not a new graph object. For a
one-segment reference, the resolver inspects the exact live leaf. If its live semantic owner is a
`PartUsage`, it contextualizes that owner through the existing occurrence selector in singular mode,
then selects the exact leaf slot at that occurrence and returns the existing typed edge. Every other
owner kind keeps the current leaf route. The callers continue to own alias following, port creation,
override application, and diagnostic translation. This is the right seam because it restores the
owner identity SysIDE already supplied while composing the occurrence and slot authorities that
already define the graph.

## Key Bets

- **B1. The live `PartUsage` owner of a resolved one-segment leaf is its occurrence anchor.** This is
  the owner-selected broad invariant and agrees with the ratified usage-qualified rule. *If false →
  the repair would deterministically bind legal references to the wrong semantic occurrence.*
- **B2. The existing containment-slot occurrence population is the correct concrete realization of
  an exact usage declaration.** SysIDE exposes semantic declarations, while codegen owns contextual
  expansion and multiplicity (`.project/active/spike-syside-occurrence-authority/findings.md:3-20`).
  *If false → exact owner selection would begin from the wrong occurrence candidates and the whole
  occurrence bridge would need redesign, not a local repair.*
- **B3. A legal authored bare topology exists in which the exact usage owner and the consumer's
  positional leaf search differ.** The approved spec assumes this can become a kept regression, but
  neither the corpus nor the targeted probe establishes it. *If false → Success Criterion 8 is
  impossible as written, even though the broad resolver predicate remains implementable.*

## Key Decisions

- **D1. Repair the one-segment branch of the shared semantic resolver.** This is the last common
  policy seam before all six lanes diverge. *Rejected: patch each caller (duplicates policy and
  inevitably misses a lane).*
- **D2. Classify the live owner by metatype.** Look up the exact leaf, obtain its live semantic owner,
  and activate the branch only for `SysideAdapter.is_instance(owner, "PartUsage")`.
  *Rejected: `owner_is_definition == false` (packages and other owner kinds also satisfy it), and
  rejected: source spelling or qualified-name tests (diagnostic metadata cannot select identity).*

  **Authority disposition (design-F2):** the live model is the branch's single authority. The
  frozen fact contributes the exact leaf ID; `owner_element_id` and `owner_is_definition` do not
  decide the branch. A planned extraction guard,
  `test_usage_owned_fact_owner_matches_live_part_usage`, will assert that frozen owner identity
  still agrees with the live leaf's owner. This design declines adding an owner-metatype field to
  `ResolvedTargetFact`: that would duplicate a metatype already available from the live authority
  and widen a cross-repository schema without a resolver need. If a future offline resolver must
  decide owner kind without the live model, that new consumer should reopen the producer contract.
- **D3. Compose the existing owner contextualizer with exact leaf-slot targeting.** Owner selection
  uses the current occurrence candidates and ambiguity policy; target selection uses the current
  slot-to-attribute/computed lookup. *Rejected: a new exact-owner index or raw
  `effective_usage_id` filter (both would compete with the redefinition-family authority).*
- **D4. Keep all one-segment owner anchoring singular.** The owner contextualizer receives
  `plural=False` even when the caller passes `plural=True`. *Rejected: forwarding `plural` (would
  change direct `sum()` and deep-override cardinality without an owner decision).*
- **D5. Preserve caller-owned post-resolution behavior.** The shared branch returns the raw typed
  edge. Alias following and diagnostic translation remain where they are. *Rejected: following
  aliases in the shared branch (breaks deep literal override semantics).*
- **D6. Promote the research fixtures by copying, not moving, them.** Their source is
  `.project/active/self-binding-replacement/spike/fixtures/`. The older spike header calls them
  “untracked,” but Git now tracks u1-u7 at commit `991ae1e`; the header is stale on that point. The
  first durable test action copies u1-u7, including u3b, under the same names in `tests/fixtures/`.
  u4-u7 become positive repaired cases; u1-u3b retain their previous edge or named-ambiguity
  behavior. The kept test copies become the conformance authority because the active research path
  will be archived. No synchronization between the two copies is promised. *Rejected: tests that
  load project-management paths (couples the suite to archival state).*
- **D7. Use one combined cross-consumer fixture plus focused topology fixtures.** A symmetric
  `comp_a`/`comp_b` fixture carries a qualified typed alias, computed expression, calculation input,
  typed constraint actual, asserted inline predicate, and direct `sum()` term from one named source.
  u4-u7 keep their minimal topology roles. A deep-override affected shape gets its own fixture if
  authorable; otherwise D11 records a dated coverage gap. A census can describe what was searched;
  it cannot prove the shape impossible. *Rejected: one fixture per consumer lane (obscures the
  one-source fan-out obligation), and
  rejected: one giant fixture for u4-u7 (loses the distinct diagnostic/topology proofs).*
- **D8. Compare typed identities and full graphs, never rendered names.** Corpus evidence records
  exact typed edges, full diagnostics, occurrence records, node IDs, and a named no-edge reason.
  Round-trip acceptance compares the decoded graph so alias targets are included. *Rejected:
  display-path or generated-name equality as the semantic oracle.*
- **D9. Do not add new fixtures to the committed v6 batch only to prove round-trip behavior.** New
  fixtures use temporary capture/relocation routes. Existing committed snapshots are recaptured only
  after an exact live/stored edge difference is exposed and classified. *Rejected: unconditional
  recapture (creates churn with no semantic cause).*
- **D10. Bare-discriminator evidence is an open owner decision.** Two defensible routes remain:
  1. Run a focused learning test across legal SysML scoping/redefinition shapes and keep the spec
     criterion if it finds an authored discriminator.
  2. If the learning test finds no legal discriminator, amend the criterion to pair a legal authored
     bare conformance fixture with a resolver-level constructed-fact discriminator. That route must
     also create and carry a standing `authored bare discrimination unproven` gap record through
     close. The constructed fact proves the branch predicate, not authored reachability.

  **Recommendation:** take route 1 before implementation. *Rejected for now: carrying the current
  criterion as an assumed implementation task; the named topology has already failed its premise.*
- **D11. Deep-override coverage is a separate open evidence decision.** Run a focused authorability
  probe for a one-segment, `PartUsage`-owned deep literal target. If it succeeds, retain the fixture.
  If it finds no shape, record `deep override affected-shape coverage unproven`, including the dated
  search surface and result, and obtain an explicit close disposition. *Rejected: treating corpus
  absence as proof of impossibility or as equivalent acceptance evidence.*

## Architecture

### Resolution flow

All existing producers of `ResolvedSemanticReferenceFact` continue unchanged. The resolver uses the
fact and the already-built live indexes as follows:

1. Validate and convert the exact root, segment, and leaf declaration IDs as today.
2. For paths with more than one segment, keep the current root contextualization and transition
   loop unchanged.
3. For a one-segment path, inspect the exact leaf's live semantic owner.
4. If the owner is not a `PartUsage`, use the existing positional leaf route unchanged.
5. If the owner is a `PartUsage`, contextualize its exact declaration through the existing
   occurrence selector with scalar cardinality.
6. At the selected owner occurrence, map the exact leaf declaration through its existing
   `FeatureSlotId` and obtain its `NodeRef` or `ProducerRef`.
7. Return exactly one edge. If owner contextualization or target selection is empty or multiple,
   raise the existing named occurrence error. Never retry the positional route.
8. Let the caller follow aliases, create ports, apply a literal override, or translate the error
   exactly as it does now.

The owner anchor is not inserted into `ResolvedSemanticReference.segment_ids`, stored on an edge, or
serialized. It is a live resolution input used to choose the already-existing occurrence identity.

### Branch behavior

| Reference shape | Owner kind | Resolution behavior |
|---|---|---|
| One segment | `PartUsage` | Exact owner occurrence, then exact leaf slot; singular. |
| One segment | definition, package, enumeration, calculation, absent/other | Existing leaf resolver, unchanged. |
| Multiple segments | any supported root | Existing root contextualization and segment transitions, including explicit plural behavior. |

Package-scoped `PartUsage` declarations take the first row. Their concrete occurrences are selected
through the existing package-context rule. A package-owned leaf takes the second row and does not
gain an occurrence merely because source text contained `::`.

### Failure behavior

The design adds no diagnostic code. Missing exact owner occurrences, ambiguous owner occurrences,
and absent leaf targets use `SI_OCCURRENCE_MISSING` or `SI_OCCURRENCE_AMBIGUOUS` through the existing
resolver error path. A failure on the owner branch is final. Consumer position, names, qualifier
text, and candidate order are not fallback authorities.

Lenient and strict modes run the same reference resolution. Strict mode can halt on readiness
findings in `_finish_readiness` before `graph.validate()`; when no readiness finding intervenes, it
validates the same graph and then rejects the same blocking graph diagnostics. Owner-resolution
parity tests must therefore use fixtures without unrelated readiness findings, while readiness
controls assert their earlier halt separately (`src/sysml_codegen/elaboration/elaborate.py:622-634,2604-2613`).

### Evidence and snapshot flow

Before the production change, a maintained task-local verifier records each tracked usage-owned
one-segment site, its caller lane, exact leaf and owner IDs, current typed edge or full diagnostic,
and any named structural no-edge reason. After the change, it records the shipped resolver's actual
result for the same site key. The comparison is acceptance evidence, not a second runtime resolver.
Every difference is classified as expected fix or regression.

New fixture graphs travel through live elaboration, encode/decode, relocation where applicable, and
projection. Existing committed snapshots are compared to live typed edges before any recapture.
Only snapshots with a classified changed final edge may change bytes.

## Required Invariants

1. A branch decision uses exact live declaration identity and `PartUsage` metatype only.
2. No name, qualified name, display path, source span, rendered identifier, value, or candidate order
   selects an owner, occurrence, slot, node, or edge.
3. The exact owner is contextualized before the leaf is normalized to its feature slot.
4. Owner occurrence candidates continue to come from the existing containment-slot family.
5. Feature-slot families, occurrence expansion, occurrence records, and serialized occurrence IDs
   are byte-for-byte unchanged by the resolver repair.
6. A usage-owned one-segment reference yields exactly one typed edge or one existing named failure.
7. One-segment references remain scalar even inside a plural caller.
8. Multi-segment feature chains retain their current singular/plural behavior.
9. Definition-owned, package-owned, enumeration, and calculation-owned leaves retain their current
   edges or diagnostics.
10. The owner-aware branch never falls back to positional leaf search after a missing or ambiguous
    exact owner.
11. Alias following remains caller-owned; the shared resolver returns a raw `NodeRef` or
    `ProducerRef`.
12. Strict and lenient modes use the same semantic resolution and differ only in halt versus report.
13. Snapshot loading performs no owner contextualization. Stored edges change only by classified
    recapture.
14. Every corpus difference has a recorded fix/regression disposition; zero differences remain
    unexplained.
15. Public mutation changes one source value and reaches every and only the consumers already bound
    to that source on live and round-trip routes.

## Component Overview

- **Shared semantic resolver** (`src/sysml_codegen/elaboration/elaborate.py:2050-2366`): owns the new
  one-segment owner branch and composes existing occurrence and target selectors. This is the only
  production component that changes.
- **Live semantic evidence** (`../agentic-mbse/src/agentic_mbse/sysml/data_models.py:55-89`,
  `../agentic-mbse/src/agentic_mbse/sysml/expression.py:639-678`): continues to supply exact leaf and
  owner identity. Its schema does not change. The branch recovers owner kind from the exact live
  leaf; frozen owner metadata remains corroborating evidence guarded by D2's extraction test.
- **Occurrence and slot indexes** (`src/sysml_codegen/elaboration/occurrence.py:58-133,205-254`):
  remain the sole authorities for redefinition families and concrete occurrences.
- **Caller lanes** (`src/sysml_codegen/elaboration/elaborate.py:1032-1079,2370-2602`): keep their
  existing port, alias, override, and error behavior while inheriting one owner-aware result.
- **Conformance fixtures and tests** (`tests/fixtures/`,
  `tests/conformance/test_usage_owned_reference_anchoring.py`): pin u1-u7, all affected consumer
  lanes, diagnostics, occurrence identity, and controls.
- **Public mutation tests** (`tests/conformance/test_elaboration_public_mutation.py`): prove the
  repaired topology reaches every and only the intended public consumers across live and rebuilt
  graphs.
- **Task-local corpus verifier**
  (`.project/completed/20260816_qualified-reference-occurrence-anchoring/`): produces the before/after typed-edge
  and diagnostic ledger. It is verification tooling, not a production resolution authority.
- **Snapshot codecs and projection** (`src/sysml_codegen/snapshot/instance_graph.py`,
  `src/sysml_codegen/elaboration/project.py`): remain unchanged and consume the final graph.

## Non-Goals

- Reinterpreting self-binding, weakening `SI_SELF_BINDING`, or changing the fusion-tea migration.
- Recovering occurrence meaning from authored `::` text or threading spelling through callers.
- Changing definition-owned or package-owned leaf semantics.
- Changing feature-chain meaning, direct-reference plural policy, or aggregation expansion policy.
- Adding or replacing the feature-slot index, occurrence walker, occurrence IDs, graph edge types,
  snapshot schema, projection names, or generated public identifiers.
- Moving alias following into the shared resolver.
- Adding name, qualified-name, display-path, source-position, or first-candidate fallbacks.
- Treating display output or generated code as the identity oracle.
- Recapturing unchanged snapshots or rewriting dated research to match the repaired code.

## Implementation Notes

- `_exact_reference` currently drops owner evidence when it builds the smaller internal path object
  (`src/sysml_codegen/elaboration/elaborate.py:2050-2060`). Inspect the live leaf/owner at the
  one-segment boundary instead of broadening `ResolvedSemanticReference` or fabricating a second
  path segment.
- The owner must be derived from the exact live leaf and confirmed with
  `SysideAdapter.is_instance(owner, "PartUsage")`. Do not use `owner_is_definition` as a negative
  proxy.
- Reuse `_contextualize_root`/`_select_occurrences` for the owner and the existing exact target
  lookup for the leaf. Do not duplicate their package, lineage, or ambiguity rules.
- Force scalar owner selection. Add a regression where a direct term is beneath `sum()` and prove
  it still produces one edge; do not infer new plural semantics from the caller flag.
- Require one final `NodeRef` or `ProducerRef`. An empty target becomes `SI_OCCURRENCE_MISSING`; more
  than one becomes `SI_OCCURRENCE_AMBIGUOUS`. Do not call `_resolve_leaf` as recovery.
- Keep `_follow_alias` where each caller currently invokes it. Include raw `AttrNode.alias_target`
  in round-trip comparisons because `semantic_edges()` omits it.
- Treat deep literal overrides as a real shared-resolver lane. First determine whether a one-segment
  PartUsage-owned deep target is authorable. If it is, keep a regression. If a bounded search finds
  none, preserve the models and results as D11's standing coverage gap. Do not call the search proof
  that the lane cannot produce the shape.
- Seed the corpus verifier from the gitignored measurement harness at
  `.project/active/self-binding-replacement/spike/out/bare_expression_side_scan.py` only after
  removing its monkeypatch-as-oracle behavior, adding deep-override accounting, and correcting its
  use of the caller's plural flag. The post-change result must come from the shipped resolver.
- Let the import-boundary AST guard inspect any new helper automatically. Do not add an exemption for
  name-based resolution.

## Potential Risks

| Risk | Consequence | Mitigation |
|---|---|---|
| The authored bare discriminator is not legal SysML. | The approved success criterion cannot be met literally. | Resolve D10 before implementation; route 2 retains a standing authored-reachability gap. |
| Owner lookup and frozen owner evidence disagree. | The branch could activate on the wrong declaration. | Pin leaf ID, live owner ID, and owner metatype in extraction/conformance tests; fail the learning gate on disagreement. |
| Slot-family lookup is mistaken for raw declaration equality. | Redefined usage occurrences disappear or become falsely ambiguous. | Reuse `occurrences_for_declaration`; pin u1-u3b and redefinition controls. |
| `plural=True` leaks into the new branch. | Direct `sum()` or deep override unexpectedly fans out. | Force scalar selection and keep a direct plural-caller regression. |
| Alias following moves into the resolver. | Deep overrides can target computed producers or alias semantics can change twice. | Keep caller boundaries and assert raw alias targets separately. |
| Only named expression lanes are tested. | Deep literal overrides retain an unverified shared path. | Add an affected-shape fixture or carry D11's dated coverage gap to explicit close disposition. |
| Diagnostic codes match but identity/detail differs. | Strict and lenient appear equivalent while reporting different failures. | Compare the full diagnostic tuple and every typed edge. |
| A committed snapshot contains an unmeasured changed edge. | Replay remains stale or unrelated snapshots churn. | Compare live/stored typed edges first, record the stale difference, then recapture only the classified fixture. |
| Tests assert rendered paths as truth. | A rename can hide or create a semantic failure. | Use display paths only to locate nodes; assert typed IDs and edges. |

## Integration Strategy

1. Resolve D10 and D11 before production work. The retained bare probe has falsified the proposed
   shape; focused learning tests must settle the remaining bare and deep-override evidence routes.
2. Copy the tracked u1-u7 research fixtures from
   `.project/active/self-binding-replacement/spike/fixtures/` into the maintained test corpus before
   relying on them, then capture exact pre-repair graph identities and diagnostics.
3. Create the combined cross-consumer fixture and obtain red assertions for u4-u7, the qualified
   alias/computed/constraint/predicate lanes, scalar direct aggregation, and public fan-out.
4. Capture the pre-repair corpus ledger before changing the shared resolver.
5. Land the single shared owner-aware branch. Do not change upstream evidence, occurrence/slot
   construction, graph models, projection, or snapshot codecs.
6. Re-run the corpus verifier and classify every edge and diagnostic difference. Confirm occurrence
   records and node identities are unchanged.
7. Compare live graphs against committed snapshots. Record any stale typed edge before the narrowly
   required recapture; otherwise prove snapshot bytes did not change.
8. At close, verify the bounded self-binding spec locations still name positional selection as F-6
   and retain the established D-5/D-7 modeling advice (`spec.md:148-159`).

## Validation Approach

| Obligation | Acceptance evidence |
|---|---|
| Shared exact-owner branch | Focused tests exercise every affected call site and assert the exact owner occurrence precedes leaf-slot selection. |
| u4 package sibling | Typed edge targets `shared_component.length`; no occurrence diagnostic. |
| u5 named siblings | Typed edge targets `plant.comp_a.length`; former ambiguity is absent. |
| u6 cross-owner | Typed edge moves from `plant.comp_b.length` to `plant.comp_a.length`; no fallback edge exists. |
| u7 paired spellings | Qualified inputs target distinct `comp_a`/`comp_b` nodes and equal their dot-path control edges. |
| u1-u3b and unaffected forms | Exact edges or full diagnostic tuples remain unchanged for usage controls, definition/package owners, enums, and chains. |
| Alias | Raw `alias_target` and alias-followed consumer edge target the named source; encode/decode preserves both. |
| Computed and aggregation | Expression ports carry the named typed source; direct `sum()` remains singular. |
| Constraint actual and predicate | Both `ConsumerPortId` edges target the named source with exact formal provenance where applicable. |
| Deep override | Kept affected-shape regression. If a bounded search finds none, D11 remains a named, dated coverage gap requiring explicit close disposition; absence is not a passing proof. |
| Bare behavior | D10's learning-test outcome: authored discriminator if legal; otherwise an owner-approved split between authored conformance and constructed-fact discrimination plus the standing `authored bare discrimination unproven` record. |
| Corpus compatibility | Every usage-owned direct site has pre/post typed edges, a full diagnostic, or a named structural no-edge reason; every difference is adjudicated. |
| Strict/lenient | Valid graphs have equal typed identity. Occurrence-error controls without readiness findings expose the same full diagnostic multiset; readiness controls separately pin strict's earlier `_finish_readiness` halt. |
| Occurrence and wire stability | Pre/post occurrence records, occurrence wire IDs, slot-derived node IDs, and unaffected consumer edges compare exactly. |
| Public mutation | Changing only `comp_a`'s off-default source changes only its public value and preserves exactly the calculation, alias/computed, constraint, and aggregation consumer set on live and round-trip routes. |
| Snapshot behavior | New fixtures pass temporary capture/decode/relocation. Existing live/stored edges are compared before any classified recapture; unaffected bytes remain unchanged. |
| Documentation tail | Close-time check of `.project/active/self-binding-replacement/spec.md:56,66-70,74-78`. |

The focused licensed conformance file runs first. Then run the existing elaboration, snapshot,
public-mutation, import-boundary, and full project quality suites named in `CLAUDE.md`. Generated
names may be checked as public compatibility output, but typed graph identity remains the semantic
oracle.

## Next-Stage Handoff

The plan must treat these decisions as fixed:

- one production seam in the shared one-segment resolver;
- live exact `PartUsage` owner guard;
- existing occurrence and slot authorities;
- scalar one-segment cardinality;
- no resolver-level alias following or fallback;
- typed/full-graph acceptance and classified snapshot changes only;
- copied u1-u7 controls plus one combined cross-consumer fixture;
- explicit coverage of deep literal overrides.

At design handoff, two evidence questions remained open: B3/D10, the authorability of a
discriminating bare reference, and D11, an affected deep-override shape. The plan resolved D10 with
an authored fixture and carried D11 to the owner's accepted close bound. The implementation then
established the combined consumer fixture before changing production behavior.

---

**Next Step:** Implemented and independently certified 2026-08-16; see `audit.md`.
