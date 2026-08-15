---
date: 2026-08-07T14:36:15-07:00
researcher: Codex
topic: "Recovery assessment after SOURCE-IDENTITY Item 4 phases 1–2"
tags: [research, source-identity, recovery, architecture, backtracking, simplification]
status: complete
last_updated: 2026-08-07
branch: source-identity-epic
base_commit: 224bfa6
---

# Recovery assessment: SOURCE-IDENTITY Item 4 after phases 1–2

## Research question

**[OWNER-VERBATIM]** (2026-08-07): “I swear to god our signal backtracing should have
been doing this already -- why is this so much new code and not just a fix??”

The owner reports that phases 1–2 took roughly three hours and probably hundreds of dollars to
produce. The work is uncommitted across `sysml-codegen` and `agentic-mbse`. The immediate question is
what happened, what work is worth preserving, what should stop, and how to recover without either
throwing everything away reflexively or continuing a flawed architecture because it is already
expensive.

## Executive conclusion

The research premise was correct. The design and decomposition were not.

- The library must preserve an exact modeled source reference before virtual-binding rewrite or
  another mutable stage destroys it. Current evidence cannot reconstruct that reference reliably.
- The existing `DependencyBacktracker` does not perform semantic source backtracing. It walks
  calculation dependencies and resolves already-normalized, sometimes already-damaged bindings
  through consumer-relative string keys.
- Item 4 and Item 5 were split at the wrong boundary. Item 4 was required to build, test, snapshot,
  and certify a new identity system while leaving the legacy resolver in control. Item 5 was expected
  to use the new system and delete the old paths later.
- That split directly produced a 742-line `source_identity.py` plus supporting extraction,
  occurrence, orchestration, sibling-repository, fixture, and test changes. This was not accidental
  agent embellishment. The approved artifacts prescribed it.
- The current phases 1–2 implementation does not establish the promised foundation. Its audit is
  `Needs Work`: the C24 calculation and aggregation consumers cannot identify the same source,
  authored spelling changes identity, aggregation still joins through legacy rendered strings, and
  unsupported invocation expressions bypass readiness.
- Continuing to phases 3–5 would deepen a parallel semantic architecture before proving that it can
  replace the actual runtime selector. Snapshot v6 and 37 fixture recaptures would then make the
  speculative architecture expensive to unwind.

**[AGENT] Recommendation:** stop Item 4 at the current dirty worktree. Preserve the work for review.
Do not proceed to phase 3 or snapshot v6. Reopen the epic/spec/design boundary and replace Items 4–5
with one vertical, replacement-oriented implementation unit. The first accepted slice must make a
valid modeled reference drive the real runtime-source decision and remove the corresponding legacy
decision path. A production identity representation that the resolver ignores is not a foundation.

## Current state and cost already incurred

### Repository state

- `sysml-codegen` branch: `source-identity-epic`
- Base commit: `224bfa6`
- Item 4 phases 1–2: dirty and uncommitted
- Item 4 phases 3–5: unstarted
- Snapshot v6: not implemented
- The 37 snapshot fixtures: not recaptured
- Customer-visible fan-out: intentionally unchanged by the Item-4 plan
- Current implementation audit: `Needs Work`
- Current dirty tree after the audit: internally inconsistent; it is not a green salvage base

No recovery deletion, reset, revert, commit, or snapshot recapture was performed while writing this
report.

### Physical Python line counts

These are physical `.py` lines, not an estimate of logical statements.

| Repository / surface | Base | Current dirty tree | Net change |
|---|---:|---:|---:|
| `sysml-codegen/src` | 23,047 | 24,218 | **+1,171** |
| `sysml-codegen/tests` | 62,956 | 64,437 | **+1,481** |
| `agentic-mbse/src` | 54,914 | 55,156 | **+242** |
| `agentic-mbse/tests` | 57,696 | 57,712 | **+16** |
| Combined production Python | 77,961 | 79,374 | **+1,413** |
| Combined test Python | 120,652 | 122,149 | **+1,497** |

The work also adds about 451 non-Python fixture/provenance lines in four untracked codegen fixture
directories. The combined phases 1–2 change therefore adds roughly 3,361 net lines across
production Python, test Python, and those new fixtures, before phases 3–5 or snapshot v6 begin.
Measured as additions/deletions rather than net change: production is `+1,428/-15`, executable tests
are `+1,507/-10`, and fixture/provenance evidence is `+451`.

Load-bearing file sizes in the current `sysml-codegen` tree:

| File | Lines |
|---|---:|
| `analysis/source_identity.py` | **742** |
| `analysis/dependency_backtracker.py` | 747 |
| `resolution/producer_resolution.py` | 713 |
| `resolution/supplied_values.py` | 715 |
| `orchestration/pipeline_builder.py` | 1,262 |
| `resolution/graph_builder.py` | 1,977 |
| `analysis/parameter_groups.py` | 912 |

The new identity module is effectively the size of the entire existing backtracker. It has not yet
been threaded into producer selection, snapshots, or C19 value application.

## What the existing “backtracker” actually does

The owner's intuition is correct at the product level: backtracing a consumed signal to its one
modeled source should already be the core of this library. It is not what the existing class does.

`DependencyBacktracker` owns calculation dependency traversal. Its result is keyed by each consumer:

```text
binding_resolutions["{usage_qualified_name}|{param_name}"]
```

That model is documented as the “single source of truth,” but it represents one decision per
consumer binding, not one identity per modeled source
(`src/sysml_codegen/analysis/dependency_backtracker.py:128-163`).

During traversal:

- A literal binding immediately becomes `{consumer_usage_qn}__{param_name}`. It never enters
  producer resolution (`dependency_backtracker.py:421-457`).
- A non-literal binding becomes a `ProducerRequest` made of strings and consumer context:
  `reference`, `consumer_eqn`, `param_name`, scopes, written reference, and occurrence-owner path
  (`dependency_backtracker.py:571-608`; `resolution/producer_resolution.py:100-129`).
- The shared producer resolver returns another string identity after trying ordered key forms.
- A lenient miss becomes a consumer-local entry point (`dependency_backtracker.py:619-630`).

Before that traversal, virtual-binding rewrite can turn a reference-derived binding into a literal,
copy in a value, and clear `source_path`. The backtracker cannot recover an identity it never
receives. Constraints and aggregations reach the shared resolver at other pipeline stages, so the
class named “backtracker” is also not the universal consumer path.

The accurate description is:

> `DependencyBacktracker` is a calculation dependency walker plus a consumer-local adapter to a
> heuristic runtime resolver. It is not a semantic source tracer.

This mismatch between the class name, architecture claims, and actual data model is part of the
original defect. Fixing it requires carrying one exact source reference into the runtime selector.
It does not, by itself, require a second manifest-driven semantic engine.

## What the prior research actually established

The prior investigations remain useful and should not be discarded.

1. Virtual-binding rewrite destroys route identity and snapshot capture persists the destruction
   (`.project/research/20260805-054752_source-identity-route-evidence.md:21-31`).
2. Written-form plus consumer-owner evidence cannot reconstruct the source across the route matrix:
   35 of 75 measured cells reconstruct and 40 do not (`:43-62`).
3. SysIDE exposes resolved referents and redefinition edges at extraction, so exact evidence can be
   preserved rather than guessed (`:55-62`).
4. The corpus contains 75 model-derived per-consumer mints among 277 public entry points (`:64-76`).
5. The parameter-group value backfill independently repairs values while leaving identity broken
   (`:88-96`).
6. Live, snapshot, and relocated routes reproduce the same fan-out. The defect is a pipeline
   semantic, not snapshot drift (`:180-191`).

The evidence-sufficiency verdict said an extraction-owned semantic source ID **or preservation of
the resolved referent through rewrite** was required. It did not demonstrate that a global manifest,
four consumer coordinate types, a query recorder, a wrapper index protocol, and a separate authority
were necessary.

That unsupported jump occurred during design.

## How the artifact chain caused the new subsystem

### 1. The epic split identity from runtime authority

Item 4 was assigned a production identity implementation, snapshot schema, and 37 recaptures. It was
also forbidden from changing VBR, materialization, or backtracking. Item 5 would later route consumers
through the identity and delete old mechanisms
(`.project/backlog/epic_semantic_source_identity.md:604-703`, `:707-770`).

This created a mergeable production “foundation” whose output was not authoritative over the thing
it modeled.

### 2. The spec required current customer defects to survive

The Item-4 spec says it does not perform the resolver cutover. Its success criteria require C14/C26
identity records while retaining current-defect pins. It also requires graph, schema, and package
outputs to remain unchanged (`.project/active/source-identity-occurrence-foundation/spec.md:32-36`,
`:52-75`).

The non-goals leave VBR, consumer-local minting, and resolver cutover to Item 5 (`:170-178`). A
runtime fix to the customer shape would therefore have violated Item-4 scope.

### 3. Review sharpened the wrong boundary instead of rejecting it

The spec review explicitly asked whether Item 4 should reroute synthesis and whether C14/C26 should
assert correct topology. The resolution chose “feed the existing route” plus current-defect pins
(`spec-review.md:45-52`, `:100-108`, `:166-185`).

That was the last requirements-stage opportunity to say a production identity system may not be
accepted while the real selector ignores it.

### 4. The design made “attach but ignore” an invariant

The Core Concept says the manifest record is attached to `ProducerRequest` while the current lookup
table deliberately remains in control. Bet B4 assumes graph topology stays unchanged when identity
is attached but ignored. Decision D7 prevents the new identity from changing resolver outcomes
outside C19 (`design.md:86-113`, `:160-165`).

The design diagram labels the request identity as ignored by the Item-4 key table. Its component
boundary says the new authority knows nothing about channels, entry points, or resolver policy
(`:192-203`, `:253-274`).

The handoff is unambiguous: Item 4 does not fix the customer defect, and pulling Item-5 resolution
changes into the work requires another design review (`:384-404`).

### 5. The design review certified the duplication as necessary complexity

The design review calls the approach sound, says leaving the cutover out is exactly correct, and
states that the manifest/authority/typed-coordinate complexity is required. It treats the continued
customer defect as a sequencing note rather than a defect
(`.project/active/source-identity-occurrence-foundation/design-review.md:23-55`).

Its abstraction review counts duplication only inside the new subsystem. It does not apply “one
authority” across the full source-to-runtime decision. The new authority can describe semantic truth
while the old resolver independently decides runtime truth.

### 6. The plan made runtime use of identity a stop condition

The plan says the legacy key table remains in control. Its critical path uses the manifest only for
C19. It requires returning to design review if Item 4 uses the identity for producer-key selection
(`.project/active/source-identity-occurrence-foundation/plan.md:25-27`, `:42-48`, `:57-65`).

Final validation was supposed to confirm that the resolver still ignored the new identity and all
Item-5 deletion targets remained present (`:500-503`).

The implementation followed the plan.

## Why the review system did not stop it

The reviews checked whether each artifact faithfully implemented the previous artifact. They did not
re-derive whether the chosen work-item boundary could deliver a coherent production architecture.

- “One authority” was scoped to the newly introduced identity layer, not the system-wide runtime
  decision.
- “No second walker” checked structural traversal duplication, not semantic authority duplication.
- Product success was weakened from “one modeled source becomes one runtime source” to “the correct
  result is derivable for Item 5 later.”
- Customer mutation was assigned to later items, so Item 4 could pass without improving the reported
  customer behavior.
- Snapshot durability was demanded before the representation was proven load-bearing in the real
  resolver.
- The product lens accepted an owner-grade mission remaining violated “by design” because the epic
  declared the sequencing.
- The phase audit correctly found implementation defects, but praised the implementation for
  respecting the non-goal that kept the actual resolver unchanged.

This is another instance of the same failure mode identified by the original forensics: artifact
consistency substituted for proving the governing product invariant.

## What phases 1–2 built

The 742-line `analysis/source_identity.py` contains several independent responsibilities:

- readiness codes and findings;
- declaration, occurrence, and composite identity types;
- calc, constraint, aggregation, and value-site coordinate types;
- demand and value-site records;
- an immutable manifest and lookup/sorting rules;
- an occurrence-query recorder with phase tracking and sealing;
- a new occurrence-index protocol;
- a source-identity authority with contextual projection and redefinition selection;
- adapters from calculation bindings and aggregation terms;
- readiness screening.

The file is not merely an identity value type. It is a new semantic compiler pass, intermediate
representation, replay transcript, policy surface, and route adapter collected in one module
(`src/sysml_codegen/analysis/source_identity.py:65-742`).

The current phase audit demonstrates that this machinery does not yet supply one stable source
identity across the required routes:

- C24 loses the aggregation chain root and fails calculation/aggregation convergence.
- `authored_segments`, documented as diagnostic evidence, changes identity.
- Missing consumer context can fall back to global uniqueness.
- Aggregation eligibility still originates in the legacy string path finder and joins to structured
  occurrences by rendered path.
- Invocation expressions can bypass readiness and become ordinary unbound inputs.
- Redefinition lookup is an optional compatibility fallback rather than a required capability.

See `.project/active/source-identity-occurrence-foundation/audit.md:18-166`.

The implementation is therefore both too additive and not yet correct. More work on the same
architecture would not answer whether the architecture should exist.

### The dirty tree moved after the audit and is presently broken

A read-only salvage check found an apparent post-audit chain-evidence edit that is not reconciled
across the two repositories:

- `feature_chain_facts()` now returns five values, while callers in `agentic-mbse` aggregation and
  codegen usage extraction still unpack four (`agentic_mbse/sysml/expression.py:670-747`,
  `aggregation.py:249,405`, `sysml_codegen/extraction/usage_extractor.py:1055`). A licensed
  extraction route raises `ValueError: too many values to unpack`.
- Aggregation term models now include chain-root and resolved-member fields, while field-contract
  tests in both repositories still assert the earlier shape.
- Codegen term construction still copies only the resolved leaf and drops the new chain root/member
  evidence (`sysml_codegen/extraction/hierarchy_resolver.py:269-324`). The C24 audit failure therefore
  remains even after the upstream type change.
- `SourceReferenceEvidence` still lacks resolved member-name data, and
  `demand_from_binding()` still derives `member_path` from diagnostic `authored_segments`
  (`extraction/source_evidence.py:83-91`, `analysis/source_identity.py:574-603`).

The green test counts in `audit.md` describe the audited state, not the current dirty tree. Before
any salvage commit, the exact cross-repository state must be made internally consistent or preserved
as a forensic checkpoint with its failures recorded.

## Salvage assessment

This is an **[AGENT]** assessment, not an instruction to delete files. Preserve the dirty worktree
until the salvage pass is reviewed.

### Strong salvage candidates

These findings and tests remain valuable under a simpler vertical repair:

1. **Exact referent extraction.** `ResolvedTargetFact` and exact chain/redefinition evidence in
   `agentic-mbse` address the real first-loss site. The aggregation chain root currently drops before
   the codegen term and must be completed, not guessed.
2. **Immutable binding evidence.** Keeping exact RHS referent, bound formal, source form, and
   redefinition evidence independent of mutable `source_path` is directly supported by the
   forensics.
3. **Authored-literal versus reference-derived distinction.** This prevents a supplied value from
   changing reference identity into an independent literal.
4. **Exact `PartInstanceIndex` reverse queries.** Definition and part-usage occurrence queries may
   be needed to attach the concrete occurrence to a valid reference. They reuse the existing walker
   and have strong atomicity tests. The current `redefining_target_on()` depends on earlier query
   order populating an internal producer map, so it requires redesign before reuse
   (`analysis/part_instance_index.py:333-339`, `:374-380`, `:432-462`).
5. **Semantic fixtures and red tests.** Mixed consumers, ambiguity, indexed-source, occurrence
   overrides, C24, C25, and the original fan-out pins are reusable evidence. Tests tied only to the
   rejected manifest API are not automatically salvageable, but their model shapes and expected
   semantic outcomes are.
6. **Audit reproductions.** C24 aggregation failure and authored-spelling identity instability are
   valuable falsifiers for any replacement design.

### Salvage only after simplification

These concepts may be necessary, but their current form assumes the rejected shadow subsystem:

- `SemanticSourceIdentity` as a small immutable value;
- redefinition-to-applicable-declaration logic;
- unique/missing/ambiguous occurrence outcomes;
- exact unsupported-form codes;
- snapshot serialization of the identity actually consumed by the resolver.

They should be reintroduced only at the smallest existing seam that needs them. They should not
require a global manifest merely to be passed from extraction to producer selection.

### Presumptive rewrite or removal candidates

These pieces exist primarily because Item 4 had to be independently complete while runtime selection
ignored it:

- `SourceIdentityManifest` as a parallel ledger of all demands and value sites;
- four consumer/value-site coordinate classes used to join that ledger back to existing route data;
- `OccurrenceQueryRecorder` and its phase/sealing lifecycle;
- a wrapper `SourceOccurrenceIndex` protocol around the existing index;
- `SourceIdentityAuthority` as a second production semantic authority detached from channels and
  entry points;
- pipeline-wide authority construction whose output does not control producer selection;
- unit tests whose only subject is the rejected manifest/recorder API;
- a v6 snapshot schema dedicated to persisting that shadow representation.

This classification must be verified in a file-by-file salvage review before any cleanup. Sunk cost
is not evidence that these abstractions are needed. It is also not a reason to delete useful evidence
or tests without examination.

## Recovery architecture

This section is an **[AGENT] recommendation**. It deliberately defines a direction and falsifiers,
not another large detailed design.

### Product behavior first

The first vertical acceptance must cover both authoring semantics and runtime behavior:

1. Bare `in R = R` resolves to the calculation formal under KerML and must fail as self-binding. It
   must never be reinterpreted as an outer reference.
2. The migrated valid owner-qualified definition reference and the valid occurrence-rooted feature
   chain must retain the distinct referents SysIDE supplies.
3. Two consumers of one valid modeled source occurrence must resolve to one public input or one
   producer channel.
4. Off-default mutation of that one runtime source must reach every and only its consumers.
5. Independently authored literals with equal values must remain distinct.
6. C19's definition-relative override and occurrence-relative demand must meet through the same
   identity used for runtime selection.

No production implementation item should be accepted while those valid-reference runtime outcomes
remain intentionally pinned as defective.

### Smallest plausible data flow

```text
SysIDE resolved referent + redefinition + concrete occurrence
                         │
                         v
            small immutable SemanticSourceRef
                         │
       existing binding / constraint / aggregation records
                         │
                         v
                 existing ProducerRequest
                         │
                         v
     existing resolver + OutputRegistry source-identity map
                         │
              ┌──────────┴──────────┐
              v                     v
       one producer channel   one public input
```

The exact type and field names require design work. The architectural constraint is simpler:
semantic identity must ride the existing consumer records into the existing runtime selector. The
selector must use it. A consumer coordinate may locate a record, but it must not become the source
identity.

The likely runtime shape is one identity-first registry surface:

```text
channel_by_source_identity[source_ref] -> canonical channel
public_input_by_source_identity[source_ref] -> public input
```

Registration rejects two different runtime sources for one identity. A modeled-reference miss is a
named error. Only an explicit external-input contract may mint a new public field. Existing string
registries may remain for rendering or aliases, but not as the authority that decides modeled source
identity.

### Replacement, not coexistence

When one valid modeled-reference path begins using `SemanticSourceRef`, the corresponding old path
must leave runtime decision-making in the same landing unit. The deletion targets already identified
by the forensics are:

- VBR conversion of a reference-derived binding into a source-less literal;
- consumer-local minting for a bound modeled reference;
- self-named outer-reference rescue;
- name/leaf/scoped fallback forms used to invent identity after exact evidence exists;
- parameter-group value backfill that masks identity failure;
- supplied-value/source-QN synthesis that remains a parallel identity authority.

Some compatibility adapters may remain temporarily inside one unmerged atomic change. No completed
production item may certify old and new semantic authorities as independently live.

### Snapshot sequencing

Do not design or recapture snapshot v6 first.

First prove that the minimal identity representation drives a real live runtime-source decision and
fixes a customer-shaped valid-reference mutation. Then serialize that exact load-bearing evidence on
the existing route records. Recapture only after live behavior and deletion boundaries are known.

A replay transcript or global manifest must be justified by a demonstrated replay need. It is not a
default consequence of requiring route parity.

## Corrective changes to the epic and quality gates

These are **[AGENT] recommendations** pending owner disposition.

1. **Collapse Items 4 and 5 as a completion boundary.** Internal phases may remain, but the identity
   addition, first runtime cutover, and corresponding legacy deletion must be one atomic production
   landing. A shadow foundation cannot be independently completed or merged.
2. **Invalidate the current Item-4 spec/design/plan.** The current audit's `Needs Work` verdict is
   insufficient because it treats the architecture as valid and only the implementation as flawed.
3. **Invert the plan's stop condition.** Stop if the real runtime selector still ignores the new
   identity. Do not stop because identity begins controlling producer selection.
4. **Require a deletion/authority ledger.** For referent, occurrence, value application,
   producer-versus-input choice, and public key selection, name the single owner after the change and
   the predecessor removed. Any old+new live row blocks completion.
5. **Use a customer-shaped valid-reference mutation as the first proof.** Manifest completeness and
   snapshot parity cannot substitute for it.
6. **Treat simplicity as an architectural requirement.** New identity code must state which existing
   inference, rescue, or reconstruction code it deletes. Net line count is a warning signal, not a
   semantic oracle, but a backtracker-sized additive subsystem requires explicit owner approval.
7. **Change the product-lens falsifier.** A production item cannot receive a clear/disposed gate when
   the owner-grade mission remains violated after the item “by design.” Such work must either be a
   throwaway prototype or include a load-bearing vertical cutover.

## Immediate recovery sequence

1. **Freeze work at phases 1–2.** Do not begin phase 3, snapshots, or additional identity APIs.
2. **Preserve the dirty state recoverably.** Before cleanup, record both repositories' exact diffs
   in a safety commit or equivalent owner-approved recovery point. Do not mix unrelated local state.
3. **Mark the architecture blocked.** Update the epic and active Item-4 artifacts to point to this
   report and state that the current design is under recovery review.
4. **Perform one bounded salvage review.** Classify each changed production file and new test as
   keep, adapt, or remove against the vertical data flow above.
5. **Write a replacement design no larger than the decision it needs to carry.** It must name the
   existing types and functions to change and delete. It must not introduce a manifest, transcript,
   or second authority without a failing test that requires it.
6. **Implement one thin end-to-end path first.** Use a valid migrated model form. Make the exact
   source reference drive `resolve_producer`, prove one runtime source and off-default propagation,
   and delete the old path for that shape.
7. **Only then generalize across constraints, aggregations, occurrence overrides, and snapshots.**
   Reuse the same identity and selector. Do not build route-specific ledgers.
8. **Re-run the corpus audit and migration after the cutover.** This remains necessary because 75 of
   277 public entry points are currently model-derived per-consumer mints.

## What not to do

- Do not continue because the work was expensive.
- Do not discard the whole worktree without a salvage review.
- Do not “fix” the current authority by adding more coordinate types or fallback arms.
- Do not snapshot a representation before it controls live runtime behavior.
- Do not reinterpret `in R = R` as an outer reference.
- Do not deduplicate emitted keys by value or spelling.
- Do not preserve old and new semantic authorities across separately completed production items.
- Do not treat green broad suites as evidence against the current architectural block.

## Open questions that remain legitimate

1. What is the smallest exact `SemanticSourceRef` shape the existing resolver needs?
2. Can the existing `OutputRegistry` be keyed directly by that reference, or does it need one new
   semantic-source namespace?
3. Which exact `PartInstanceIndex` reverse queries are necessary after the first vertical path is
   chosen?
4. Which current phase 1 extraction changes preserve genuine SysIDE facts, and which merely support
   the rejected manifest joins?
5. What snapshot fields are required once the live load-bearing representation is proven?
6. Which old key forms remain legitimate rendering/lookup adapters, and which are identity guesses
   that must be deleted?

These questions belong to the bounded replacement design. They do not reopen the already-settled
KerML ruling or the owner product invariant.

## Bottom line

The three hours were not worthless. They produced useful extraction evidence, structural queries,
fixtures, tests, and two decisive architectural falsifiers. They also demonstrated that the approved
Item-4 design creates a large shadow semantic system without controlling runtime behavior.

The correct response is neither “keep going” nor “delete everything.” It is:

> Preserve the evidence. Stop the architecture. Salvage the exact source facts and tests. Replace the
> Item-4/Item-5 split with one vertical repair of the existing runtime backtracing path, and require
> every new semantic mechanism to remove the old mechanism it supersedes.

## Primary references

- `.project/research/20260803-202453_backtracking-fanout-forensics.md`
- `.project/research/20260803-203011_entry-surface-fanout-forensics.md`
- `.project/research/20260805-054752_source-identity-route-evidence.md`
- `.project/backlog/epic_semantic_source_identity.md`
- `.project/active/source-identity-occurrence-foundation/spec.md`
- `.project/active/source-identity-occurrence-foundation/spec-review.md`
- `.project/active/source-identity-occurrence-foundation/design.md`
- `.project/active/source-identity-occurrence-foundation/design-review.md`
- `.project/active/source-identity-occurrence-foundation/product-lens.md`
- `.project/active/source-identity-occurrence-foundation/plan.md`
- `.project/active/source-identity-occurrence-foundation/audit.md`
- `src/sysml_codegen/analysis/dependency_backtracker.py`
- `src/sysml_codegen/analysis/source_identity.py`
- `src/sysml_codegen/resolution/producer_resolution.py`
- `src/sysml_codegen/orchestration/pipeline_builder.py`
