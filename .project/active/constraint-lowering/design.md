# Design: Concrete Constraint Lowering

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-07-12
**Complexity:** HIGH
**Branch:** constraint-exec-epic (commit b71fe12)
**Epic:** CONSTRAINT-EXEC — Item 5

## Overview

A new lowering phase, threaded into `build_pipeline_context` at three ordered points,
turns each extracted `assert constraint` into concrete graph structure: expand it per
design instance, strictly resolve every actual to a real producer channel or a real design
attribute, keep the producer alive against pruning, and give each concrete assertion a
stable `constraint_id`. It stops at graph structure plus `ConcreteConstraint` catalog data;
Item 7 emits code from it.

## Related Artifacts

- **Spec:** `.project/active/constraint-lowering/spec.md` (review-revised)
- **Spec review:** `.project/active/constraint-lowering/spec-review.md`
- **Concept:** `.project/concepts/constraint-execution-and-design-space-studies-claude.md`
  ("Concrete Lowering"; Required Invariants; Appendix B S3/S4)
- **Proven shape:** `.project/active/spike-vertical-slice-constraint-execution/s4_lib.py`
- **Landed types:** `.project/reference/agentic-mbse-landed/{constraint_facts,expression_ir,expression_facts}.py`
- **Required Reading (epic):** concept "Concrete Lowering" + Required Invariants + S3/S4
  carry-forwards; memory `f4-cutover-fallback-divergence`

## Research Findings

- **The call-site is exactly as the spec pins it.** `build_pipeline_context`
  (`pipeline_builder.py:685`) has a `graph_design_attrs` copy finalized at Step 5.65
  (`:815-827`), the deriver at Step 5.7 (`:831`), the backtracker target list at Step 6
  (`:840`), and `build_computation_graph` at Step 7 (`:888`). The three threading points map
  onto real seams with no restructuring.
- **The fallback that must not leak.** `_resolve_binding_via_registry`
  (`dependency_backtracker.py:520-604`) runs a rich ladder (chain dispatch with a scope
  CLIMB, alias lookups, self-reference guard), then at Step 4 (`:594-604`) *synthesizes*
  `{usage_qn}__{param}` as an entry point and records it in `_fallback_entry_points`. This is
  the F4 collapse surface: the synthesized key is not the design-attribute QN, so distinct
  params collapse and baselines churn (memory `f4-cutover-fallback-divergence`).
- **The strict inputs are typed, not stringly.** Lowering resolves `ActualFact.value`
  (`FeatureReferenceNode` → `FeatureReferenceFact` with `source_name`, `target`,
  `chain_segments` — `expression_facts.py:66-77`). The backtracker resolves untyped
  `source_path` strings. These are genuinely different inputs (see D1).
- **`scoped_lookup(ScopedKey)`** (`output_registry.py:186`) is a plain exact-match dict get;
  keys are design-prefix-stripped dotted instance paths. S4 built the key as
  `{scope}.{dotted-segments}` (`s4_lib.py:288-296`).
- **Item 4's index is ready and un-wired.** `PartInstanceIndex.occurrences_of(qn)`
  (`part_instance_index.py:291`) returns `InstanceOccurrence`s each with a distinct
  `instance_path` (per-step `occurrence_index`), and `all_occurrences()` /
  `all_source_owners()` carry a `blocked: dict[qn→reason]` mapping (`:238-265`). Nothing
  imports it yet — Item 5 wires it in.
- **`instance_index_probe`** (`tests/fixtures/instance_index_probe/model.sysml`) already
  carries `Bank { part member : ConstrainedLeaf [3] }` with an **inherited** `assert
  constraint nonnegative` on `ConstrainedLeaf`. It exercises expansion cardinality +
  inheritance, but its actual (`reading`) is a self-attribute (design-attribute-resolved,
  shared QN across siblings) — it does **not** exercise distinct per-occurrence *producer
  channels*. See D6 and Fixtures.
- **`ModuleKind`** (`models.py:161-171`) already has `CONSTRAINT` and `REPORT_AGGREGATOR`;
  `PipelineModule.module_kind` is required (`:193`); `calc_def_qualified_name` is optional
  (`:198`). Item 6 already made the calc-shaped seams dispatch on `module_kind`.
- **ID idiom.** The repo mints human-scannable `__`-joined EQN/PQN names
  (`qualified_names.py`); it uses `sha256().hexdigest()` only for content fingerprints
  (`extractor.py:804`, `snapshot/loader.py:273`). No existing prefix+hash short-id idiom — so
  the `constraint_id` encoding introduces one, matching both idioms (D3).

## Core Concept

Lowering is a **fact-to-structure expander with a strict resolver at its heart.** One source
assertion fact fans out along the *owner-kind axis* into N concrete instances; each instance
selects its effective predicate along the *source-form axis*; and each formal of each
instance runs through **one ordered resolution procedure** whose only outcomes are a real
producer channel, a real (QN-keyed) design-attribute entry point, an overridable
modeled-default parameter, or a named generation error. The resolved input channels join the
backtracking roots *before* pruning so the producers survive, and the resolved facts become
`ConcreteConstraint` records that Item 5 renders into constraint + aggregator graph nodes.

The key insight the spec forces: **the two classification axes are orthogonal and each rule
dispatches on exactly one.** Owner-kind drives *how many* instances; source-form drives
*which predicate*. Conflating them is the trap. The second insight: **strictness is a
property of the terminal disposition, not a parallel resolver** — the one place the calc path
diverges (synthesize a fallback EP) is the one place strict mode must instead raise, so the
switch lives exactly there and nowhere the byte-identical calc corpus depends on.

This is the productionization of `s4_lib.py`'s proven `lower_constraints` +
`targeted_graph` + `extend_graph` sequence, with three surfaces S4 never ran: four-value
owner dispatch, inline source form, and per-occurrence multi-instance resolution.

## Key Bets

- **B1. The OutputRegistry already carries a distinct producer channel for each
  fixed-multiplicity occurrence, reachable by a `scoped_lookup` keyed from the occurrence's
  own `instance_path`.** *If false → the multi-instance criterion cannot be met by resolution
  alone; sibling constraints either collapse onto one input channel or all error. This is the
  highest-risk bet and the reason the multi-occurrence fixture exists and a spike is
  recommended (Handoff).*
- **B2. Item 4's `occurrences_of` enumerates exactly the concrete instances a `part_def`-owned
  assertion expands to** (subtype closure + fixed multiplicity, each with its own identity),
  matching what the model author means by "one assertion per instance." *If false → expansion
  cardinality is wrong (missing or phantom instances); every downstream count is off.*
- **B3. Every fact reaching lowering is profile-admitted (Item 3 upstream), asserted, and
  polarity-known.** *If false → lowering meets `requirement_def`/out-of-profile forms or
  `None` polarity on the normal path; the defensive branches (D7, nullable-guard) fire as
  errors, which is correct behavior but means Item 3 has a gap.*
- **B4. `FeatureReferenceFact` on a constraint actual carries enough to key both a scoped
  channel lookup and a design-attribute QN match** (via `chain_segments` for chains,
  `target.qualified_name`/`source_name` for plain refs). *If false → resolution cannot form
  lookup keys for some in-profile actual shape; strict resolution raises on a valid model.*

## Key Decisions

- **D1. Shared *terminal-disposition* seam, not a unified lookup ladder.** Factor the one
  divergent step — "resolved to nothing" → synthesize-fallback (lenient) vs. raise-naming-the-
  actual (strict) — into a single switch both paths cross; the strict path uses a narrow,
  typed lookup (occurrence-scoped `scoped_lookup` → design-attr-by-QN) rather than the
  backtracker's `source_path` ladder. *Rejected: fully unifying the backtracker's
  `_resolve_chain_dispatch` ladder (CLIMB, alias, self-ref) with strict resolution — its
  inputs are untyped `source_path` strings, not `FeatureReferenceFact`, and refactoring that
  deeply-tuned path risks the corpus byte-identity gate for zero strict benefit. What the
  spec's "one code path with an explicit switch" [HARD] intent actually protects — the
  fallback never reachable in strict mode — is delivered by unifying the terminal switch, not
  the ladder.*
- **D2. Lowering lives in a new module `analysis/constraint_lowering.py`** exposing a
  `lower_constraints(...) -> list[ConcreteConstraint]` and a `extend_graph_with_constraints(
  graph, concrete, ...) -> ComputationGraph`, called from `pipeline_builder`. *Rejected:
  inlining into `pipeline_builder` (already 900+ lines; lowering is independently testable and
  Item 7/8 import its data types) and putting it in `resolution/graph_builder` (that module is
  the calc-graph builder; constraint expansion is analysis, not graph construction).*
- **D3. `constraint_id` = human-scannable prefix + `__` + short hash suffix.** Prefix =
  `{instance_path}__{source_local}` sanitized (`source_local` = usage simple name when named,
  else `anon`); suffix = first 8 hex of `sha256` over the canonical tuple `(source_local_full,
  owner_instance_identity, membership_kind, polarity)` where `source_local_full` is the name
  or the `LocationFact` triple. The prefix scans; the suffix folds anonymous location +
  membership + polarity in and guarantees determinism and collision-visibility. *Rejected:
  (a) S4's bare `{instance_eqn}__{usage_name}` — omits membership/polarity and has no place
  for an anonymous assertion's location, so two anonymous asserts on one instance collide
  silently; (b) a de-novo ordinal — the spec [HARD]-forbids it while `LocationFact` fills the
  role; (c) hashing the whole ID with no readable prefix — loses scannability the repo values.*
  A post-expansion pass raises a generation error on any duplicate `constraint_id` (concept:
  collision is an error).
- **D4. `ConcreteConstraint` and its input records are Pydantic models in
  `resolution/models.py`,** beside `ComputationGraph`. Graph-serializable by construction
  (Item 8 serializes; Item 7 consumes). *Rejected: dataclasses local to the lowering module —
  Item 8 needs a serialization contract and the repo's graph-serializable data all lives as
  Pydantic in `models.py`; S4's dict shape (`s4_lib.py:379`) was throwaway.*
- **D5. Expansion dispatches on `owning_definition.kind` (all four landed values), routing
  `part_def` through `PartInstanceIndex.occurrences_of`.** *Rejected: reusing the calc-driven
  instance discovery in `usage_extractor` for `part_def` owners — the concept's named risk is
  that a constraint-only part definition has *no* calc-discovered instances; Item 4's
  structure-only index exists precisely for this.*
- **D6. New dedicated fixtures for the two unproven surfaces; reuse `instance_index_probe` as
  a cross-check only.** Author `constraint_multi_instance` (fixed `[N]` siblings each with a
  per-occurrence calc producer the assertion checks — the one shape that exercises B1) and
  `constraint_inline` (an assertion owning its predicate inline). *Rejected: extending
  `instance_index_probe` for the primary multi-instance test — its actual is a shared-QN
  self-attribute (design-attribute path), so it proves expansion + inheritance + distinct
  evaluation channels but NOT distinct per-occurrence producer channels, which the spec names
  the highest-risk surface. It stays a secondary inheritance/cardinality check; its Item-4
  oracle count must not move.*
- **D7. `requirement_def` / out-of-profile forms are defensively cataloged unassessed, not
  assumed-away.** On meeting one, lowering emits an `unassessed` `ConcreteConstraint`
  (kind/form stated, no executable node, no minted EP) rather than trusting Item 3 filtered
  it. *Rejected: assume-and-error-if-surprised — the silence trap and Design Principle 5 want
  a visible record; erroring would also make Item 5 fragile to Item 3 timing. The unassessed
  record rides in the returned `list[ConcreteConstraint]` with `eligible=False`; until Item
  7's catalog runtime exists it is carried on the graph's constraint data and asserted in
  tests.*
- **D8. `tracking_key` is read at lowering from an author-controlled surface, not added to the
  Item 1 fact.** Item 1 is CERTIFIED and carries no `tracking_key` field; re-certifying it for
  a low-leverage correlation aid is not worth it. Lowering reads an optional `tracking_key`
  from the usage's own metadata/annotation surface if present, else `None`; it never
  participates in `constraint_id`. *Rejected: a scoped Item 1 extension — re-certification cost
  exceeds value for the core lowering path (spec Open Question concurs).*

## Architecture

**Data flow (three threading points in `build_pipeline_context`):**

```
Step 5.65  materialize_supplied_values → graph_design_attrs (final)
Step 5.7   group_deriver (final)
  │
  ├─▶ [P1 RESOLVE]  lower_constraints(facts, occ_index, registry, graph_design_attrs,
  │                   group_deriver) → list[ConcreteConstraint]
  │        expand per owner-kind · select predicate per source-form ·
  │        resolve each formal (ordered, strict) · mint constraint_id
  │
Step 6   backtracker.find_required_modules(targets + [P2 constraint root channels])
  │        [P2 INJECT] each module_output-resolved input channel → a backtracking
  │        root via _find_usage_for_channel, BEFORE pruning
  │
Step 7   build_computation_graph → ComputationGraph (calc nodes only)
  │
  └─▶ [P3 EXTEND]  extend_graph_with_constraints(graph, concrete, group_deriver)
           → +1 CONSTRAINT node per concrete assertion (own evaluation channel)
           → +1 REPORT_AGGREGATOR node (one required input per assertion)
           → mint DESIGN_ATTRIBUTE entry points (QN-keyed, deduped) into derived groups
           → re-run _validate_channel_references + collect_uncovered_params (V11)
```

**The resolver seam (P1 heart).** For each `(concrete instance, formal)`:

1. Formal has an actual (`ActualFact` whose `formal_targets` name it):
   a. `scoped_lookup` keyed by the *occurrence's own scope* + the reference (single-segment
      or `chain_segments`) → producer channel.
   b. else design-attribute match on the reference target QN → mint `DESIGN_ATTRIBUTE` EP,
      keyed by the attribute's real QN, deduped by QN (F4-safe).
   c. else **terminal disposition** → strict: generation error naming the actual.
2. No actual but in `omitted_default_formals` with `FormalFact.has_default` → overridable
   modeled-default contract parameter (retains `FormalFact.default`).
3. else → generation error.

The terminal disposition (1c/3) is the shared switch (D1): in lenient/calc mode it synthesizes
the fallback EP; in strict/constraint mode it raises. The synthesis branch is physically
unreachable when `strict=True`.

**Predicate selection (per source-form axis).** Read `source.effective_predicate_source`:
`inline` → `ConstraintUsageFact.predicate`; `definition_typed` →
`ConstraintDefinitionFact.predicate` bound in usage scope. Never inferred from owner-kind.

**Blocked-owner surfacing.** For `part_def` owners, lowering calls `occurrences_of` per owner
(which raises `NonFiniteCardinalityError`) OR consumes the bulk API's `blocked` map. Either
way, a constraint-owning def that is blocked becomes a **named generation error**, never a
skip (Item 4's audit cure exists so this cannot be swallowed).

## Required Invariants

- **INV-1. Every assertion ends visibly.** Each source assertion produces ≥1 of: a lowered
  CONSTRAINT node, an `unassessed` `ConcreteConstraint`, or a named generation error. No path
  drops one (the silence trap).
- **INV-2. No fallback synthesis for a constraint actual.** The strict switch makes the
  `{usage_qn}__{param}` synthesis unreachable; unresolved ⇒ error naming the actual.
- **INV-3. Each concrete sibling has its own evaluation channel AND resolves its actuals in
  its own occurrence scope.** Structurally identical siblings never share an input or output
  channel.
- **INV-4. `constraint_id` is deterministic and collision-checked.** Byte-identical across
  repeated live loads; any duplicate is a generation error. Catalog ordering is by
  `constraint_id`.
- **INV-5. Minted EPs are QN-keyed and QN-deduped.** An attribute already exposed as an EP is
  reused, never re-minted or treated as a collision (F4-safe).
- **INV-6. The extended graph passes `_validate_channel_references` and has zero V11 uncovered
  params.** Constraint consumers must be present to cover the minted EPs.
- **INV-7. Inertness.** When nothing lowers, P1–P3 are no-ops and the corpus regenerates
  byte-identically (timestamps excepted).
- **INV-8. Nullable-fact guard.** A `None` `is_negated` or `membership_kind` reaching lowering
  is a generation error naming the field and usage — never a defaulted guess.

## Component Overview

- **`analysis/constraint_lowering.py`** (new) — `lower_constraints(...)` (expand + select +
  resolve + mint) and `extend_graph_with_constraints(...)` (P3). Owns the strict resolver and
  the `constraint_id` minter. Imports `PartInstanceIndex`, `OutputRegistry`, the landed facts.
- **`resolution/models.py`** (extend) — `ConcreteConstraint`, `ConcreteConstraintInput`
  (resolution-tagged: `module_output` | `design_attribute` | `modeled_default`), and an
  `unassessed` shape. Pydantic; serialization contract for Items 7/8.
- **`orchestration/pipeline_builder.py`** (extend) — three call-sites (P1/P2/P3) guarded so
  they no-op when no constraint facts are present. Threads the resolved root channels into the
  Step 6 target list and the extension after Step 7.
- **The terminal-disposition switch** — a small shared function (home: alongside the
  backtracker's resolution or a shared `analysis` helper) that both the backtracker's Step 4
  and lowering's terminal step call, parameterized by `strict`.
- **Fixtures** — `constraint_multi_instance`, `constraint_inline` (new); `instance_index_probe`
  (reuse, cross-check).

## Non-Goals

Carries the spec's Non-Goals verbatim in force: module/aggregator *emission*, the Kleene
compiler, generated-class identity, and catalog runtime are **Item 7**; snapshot round-trip
and live/snapshot ID parity are **Item 8**; profile eligibility is **Item 3** (lowering only
refuses to silently drop out-of-profile kinds); fingerprint sealing is **Item 9**. This item
wires one *graph node* per concrete assertion — how nodes render to Python classes is Item 7.

## Implementation Notes

- **P3 minting mirrors S4 exactly** (`s4_lib.py:487-525`): dedupe against existing group
  params by QN, place the EP in its derived group via `group_deriver.derive_groups()`, sort
  params by QN and groups by name for determinism.
- **`ConcreteConstraint` fields Item 5 sets vs. leaves for Item 7:** Item 5 sets
  `constraint_id`, source identity/form, owner-instance identity, membership/polarity,
  `expected_value`, effective-predicate IR reference, and the resolved inputs. It sets the
  CONSTRAINT node's `name` (= `constraint_id`) and `evaluation_channel`; it leaves
  `module_type`/generated-class identity to Item 7 (sits with Item 7's class-identity
  decision). Confirm this boundary against Item 7's spec (Open Question resolved this way;
  re-check when Item 7 specs).
- **The occurrence-scope→ScopedKey transform is the delicate bit.** `instance_path` renders
  `Owner__feat[i]__...`; the registry key is a design-prefix-stripped *dotted* path. Define
  one transform (strip the design-root prefix, join by `.`, carry `[i]` occurrence indices in
  whatever form the registry actually keys) and pin it with the multi-instance fixture. If the
  registry has no per-occurrence channel, resolution errors loud (INV-2) — it never collapses.
- **Guard the call-sites on presence of constraint facts** so INV-7 holds trivially and the
  corpus gate is clean.
- Reuse `_find_usage_for_channel` (`dependency_backtracker.py:466`) unchanged for P2 (S4
  proved it).

## Potential Risks

- **R1 (highest): per-occurrence producer channels may not exist in the registry (B1).**
  Mitigation: de-risk first with a spike on `constraint_multi_instance` before building P3;
  design already forces a loud error rather than a silent collapse if absent.
- **R2: byte-identity regression from touching the shared terminal switch.** Mitigation: D1
  keeps the backtracker's ladder untouched; only the terminal branch is extracted, and the
  corpus gate (timestamp-only-diff + revert, memory `byte-identity-captured_at-churn`) runs
  against the exact replaced function.
- **R3: `constraint_id` hash over an unstable canonical tuple.** Mitigation: canonicalize with
  `sort_keys`/fixed separators (the repo's `_canonical_json` idiom); the tuple contains only
  stable fields (name/location, instance identity, membership, polarity).
- **R4: inline predicate scope-binding differs from definition-typed.** Mitigation: the
  `constraint_inline` fixture; select strictly via `effective_predicate_source`.

## Integration Strategy

Purely additive to `build_pipeline_context`: three guarded insertions, no reordering of the
existing 10-step sequence. The calc corpus path is unchanged when no assertion is admitted
(INV-7). The new module and models are imported by Item 7 (consumer) and Item 8 (serializer);
keeping `ConcreteConstraint` in `resolution/models.py` gives both a stable import.

## Validation Approach

- **S4 reproduction:** control run prunes `cost_calc`; lowered run retains it only via the
  resolved constraint input channel joined as a root (not because every output feeds the exit).
- **Strict resolution:** V11 + channel-reference validation pass on the extended graph; a
  probe with an unresolvable actual produces a generation error naming the actual (no
  synthesized EP).
- **Determinism:** `constraint_id`s and catalog ordering byte-identical across repeated live
  loads.
- **Corpus byte-identity:** full fixture corpus regenerates byte-identically (timestamps
  excepted) under the established gate.
- **Multi-instance (`constraint_multi_instance`):** three concrete constraints, three distinct
  `constraint_id`s, three distinct evaluation channels, AND three distinct producer input
  channels resolved each in its own occurrence scope.
- **Inline (`constraint_inline`):** an `inline`-form assertion lowers, selecting the usage
  predicate.
- **Blocked owner:** a constraint-owning def with non-finite multiplicity surfaces a named
  generation error, never a skip.
- **Inheritance cross-check:** `instance_index_probe`'s inherited `[3]` assert expands
  correctly; its Item-4 oracle count is unchanged.

## Next-Stage Handoff

- **Fixed:** the three threading points and their order; four-value owner dispatch; source-form
  predicate selection; the ordered strict resolution procedure with the shared terminal switch
  (D1); `LocationFact`-based source-local identity; `ConcreteConstraint` in
  `resolution/models.py` (D4); `constraint_id` encoding (D3); new fixtures for the two unproven
  surfaces (D6); defensive-unassessed disposition (D7); `tracking_key` read at lowering (D8).
- **Open:** the exact occurrence-scope→ScopedKey transform (pin against the registry's real
  per-occurrence keying); which `ConcreteConstraint`/node fields Item 5 sets vs. Item 7 (D3
  boundary — confirm when Item 7 specs).
- **De-risk first (R1/B1):** run a `/_my_spike` on `constraint_multi_instance` to confirm the
  registry carries a distinct producer channel per fixed-multiplicity occurrence *before*
  building P3. This is the one bet that, if false, blocks the multi-instance criterion.

## Appendix A: Open-Question dispositions (spec → decision)

| Spec Open Question | Disposition |
|---|---|
| Item 5 / Item 7 line | Item 5 = extended `ComputationGraph` (nodes + minted EPs + joined roots) + `ConcreteConstraint` data; Item 7 emits all code. Item 5 sets node `name`/`evaluation_channel`, leaves `module_type`/class identity to Item 7. (D3 note; confirm vs Item 7 spec.) |
| Per-occurrence input-channel resolution | Each sibling resolves via `scoped_lookup` keyed by its own `instance_path` scope; distinct producer channel required; loud error if absent. Highest risk (R1/B1); `constraint_multi_instance` catches it. |
| `requirement_def` / out-of-profile | Defensively cataloged **unassessed** (D7); record rides the returned list with `eligible=False`; asserted in tests until Item 7's catalog exists. |
| `constraint_id` encoding | Human-scannable `{instance_path}__{source_local}` prefix + `__` + `sha256[:8]` of the canonical `(source_local_full, owner_instance, membership, polarity)` tuple (D3). |
| `tracking_key` surface | Read at lowering from an author annotation surface if present, else `None`; not in Item 1 fact; never in `constraint_id` (D8). |
| Modeled-default representation | Overridable contract parameter retaining `FormalFact.default`; represented as a `ConcreteConstraintInput` tagged `modeled_default`, surfaced as an eligible-for-selection EP, never an automatic study variable. |

## Appendix B: Fixtures

- **`constraint_multi_instance` (new).** A part def `Cell` with a per-instance calc producing
  an output (e.g. `power`); a container with `part cell : Cell [3]`; an assert on `Cell`
  checking `power` against a bound. Expands to 3 concrete constraints, each resolving `power`
  to *its own* occurrence's producer channel. Exercises B1 — the one shape S4 never ran.
- **`constraint_inline` (new).** An assertion owning its predicate inline
  (`ConstraintSource.form == "inline"`), so the effective predicate is selected from the usage,
  not a definition. Single instance is enough; the point is the source-form axis.
- **`instance_index_probe` (reuse, cross-check).** Already carries `Bank { member :
  ConstrainedLeaf [3] }` + inherited `assert nonnegative`. Proves expansion cardinality +
  inheritance + distinct evaluation channels via a design-attribute actual. Its Item-4 oracle
  count must not move (extend only with disjoint type families if at all).

---
Next Step: After approval → `/_my_plan` (then de-risk R1 via `/_my_spike` before P3).
