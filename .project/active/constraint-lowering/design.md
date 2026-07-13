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

- **B1 — SETTLED (refuted by probe, adjudication adopted).** The original bet — "the registry
  carries a distinct producer channel per fixed-multiplicity occurrence" — was **refuted**:
  `probe_b1_channels.py` (evidence: `b1-probe-evidence.md`) shows the calc pipeline does not fan
  fixed multiplicity. A `[3]` calc yields **one** canonical channel and **one** de-indexed scoped
  key (`the_design.c.cell.power_calc.p`); occurrence-indexed lookups miss. Item 4's structure
  index still fans `[i]` into three occurrences. The adopted semantics (see D6, INV-3): per-
  occurrence *constraint* identity stands (3 IDs / 3 entries / 3 modules with their own output
  channels); actual resolution binds **whatever the registry actually holds** — trying the
  occurrence-scoped key first, then deliberately binding the shared de-indexed channel when that
  is what exists — and **records the bound channel per catalog entry** so shared-producer verdict-
  equality is visible data, never silence. Growing per-occurrence calc producers is out of scope
  (a calc-pipeline change), a named limitation with a relaxation path.
- **B2. Item 4's `occurrences_of` enumerates exactly the concrete instances a `part_def`-owned
  assertion expands to** (subtype closure + fixed multiplicity, each with its own identity),
  matching what the model author means by "one assertion per instance." *If false → expansion
  cardinality is wrong (missing or phantom instances); every downstream count is off.*
- **B3. Every fact reaching lowering is profile-admitted (Item 3 upstream), asserted, and
  polarity-known.** *If false → lowering meets `requirement_def`/out-of-profile forms or
  `None` polarity on the normal path; the defensive branches (D7, nullable-guard) fire as
  errors, which is correct behavior but means Item 3 has a gap.*
- **B4. The strict ladder (`scoped_lookup` → `alias_lookup` → design-attr-by-QN) covers every
  rung an in-profile constraint actual can hit** — i.e. no in-profile actual needs the
  backtracker's omitted rungs (`scoped_alias_lookup`, CLIMB, self-reference). `FeatureReferenceFact`
  carries enough to form each key (`chain_segments` for chains, `target.qualified_name`/
  `source_name` for plain refs). *If false → a reference the calc path resolves fine will strict-
  error on a valid model. This is the divergence D1's surfacing note bounds; the amendment added
  `alias_lookup` to close the known gap. If a further omitted rung turns out in-profile, add it
  to the strict ladder — the terminal switch stays; the profile coverage grows.*

## Key Decisions

- **D1. Shared *terminal-disposition* seam, not a unified lookup ladder — with an amended
  strict ladder.** Factor the one divergent step — "resolved to nothing" → synthesize-fallback
  (lenient) vs. raise-naming-the-actual (strict) — into a single switch both paths cross. The
  strict path uses its own typed lookup over `FeatureReferenceFact`, not the backtracker's
  `source_path` ladder. **Amendment (adopted, agent-grade — see the surfacing note below):** the
  strict ladder must cover the rungs an in-profile actual can legitimately hit, or a valid
  reference the calc path resolves would strict-*error* (B4's failure mode). So the ordered
  strict procedure is `scoped_lookup` → `alias_lookup` → design-attr-by-QN → terminal. The CLIMB
  and self-reference guard stay out (CLIMB is a deep-chain heuristic; a constraint actual
  resolving to its own owner is a modeling error worth surfacing), justified against the
  executable profile below. *Rejected: fully unifying the backtracker's `_resolve_chain_dispatch`
  ladder — its inputs are untyped `source_path` strings, not `FeatureReferenceFact`, and
  refactoring that tuned path risks the corpus byte-identity gate for zero strict benefit.*

  **Surfacing (capture-fidelity §4) — the spec's `[HARD]` "one code path with an explicit
  switch" is read as "one terminal switch," which is a reinterpretation, adopted per
  orchestrator adjudication.** The spec §Strict-resolution `[HARD]` says strict and lenient
  "should be one code path with an explicit switch so they cannot silently diverge again." This
  design delivers *two* ladders sharing only the terminal branch. That satisfies the load-bearing
  intent (the fallback is structurally unreachable in strict mode — verified by review, not just
  the switch), but two ladders *can* diverge on the lookup rungs. The adjudication (orchestrator,
  agent-grade): fallback structural-unreachability satisfies the intent, and the divergence risk
  is bounded by requiring the strict ladder to cover the rungs in-profile actuals hit (aliases at
  minimum, above). Any rung the strict ladder omits is a decision about the profile, recorded
  here, not a silent narrowing.
- **D2. Lowering lives in a new module `analysis/constraint_lowering.py`** exposing a
  `lower_constraints(...) -> list[ConcreteConstraint]` and a `extend_graph_with_constraints(
  graph, concrete, ...) -> ComputationGraph`, called from `pipeline_builder`. *Rejected:
  inlining into `pipeline_builder` (already 900+ lines; lowering is independently testable and
  Item 7/8 import its data types) and putting it in `resolution/graph_builder` (that module is
  the calc-graph builder; constraint expansion is analysis, not graph construction).*
- **D3. `constraint_id` = human-scannable prefix + `__` + short hash suffix.** Prefix =
  `{instance_path}__{source_local}` sanitized (`source_local` = usage simple name when named,
  else `anon`); suffix = first **16** hex of `sha256` over the canonical tuple `(source_local_full,
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
  `resolution/models.py`,** beside `ComputationGraph`. *Rejected: dataclasses local to the
  lowering module — Item 8 needs a serialization contract and the repo's graph-serializable data
  all lives as Pydantic in `models.py`; S4's dict shape (`s4_lib.py:379`) was throwaway.*

- **D5-IR. The effective predicate is carried *inline* as a serialized `ExpressionIR` string,
  not a reference Item 7 re-hydrates from facts.** `ExpressionIR` is an agentic-mbse dataclass,
  not JSON-native; `ConcreteConstraint.predicate_ir` holds the result of
  `serialize_expression(ir)` (`expression_ir.py:133`) — a canonical, byte-stable JSON string, so
  the Pydantic model is a plain `str` field with no `arbitrary_types_allowed` and round-trips
  through Pydantic's JSON trivially. **Item 7** reads `predicate_ir` and re-parses via
  `parse_expression` (`:220`) to drive the Kleene compiler. **Item 8** round-trips the string
  as-is (canonical form is stable, so snapshot re-derivation is byte-identical). *Rejected: a
  reference (`IdentityFact`/QN) that Item 7 re-hydrates from the constraint facts — the spec's
  own Non-Goal defers snapshot round-trip of constraint facts to Item 8, so offline (Item 7/8)
  the facts may not be present; storing the serialized IR inline makes the graph self-contained.*
  The predicate is selected inline-vs-definition per source-form (below); once selected, the
  *effective* IR is serialized — the source-form axis is resolved at lowering, not deferred.
- **D5. Expansion dispatches on `owning_definition.kind` (all four landed values), routing
  `part_def` through `PartInstanceIndex.occurrences_of`.** *Rejected: reusing the calc-driven
  instance discovery in `usage_extractor` for `part_def` owners — the concept's named risk is
  that a constraint-only part definition has *no* calc-discovered instances; Item 4's
  structure-only index exists precisely for this.*
- **D6. New dedicated fixtures for the unproven surfaces; reuse `instance_index_probe` as a
  cross-check only.** Author `constraint_multi_instance` (a `Cell` with `power_calc`; a
  `Container { part cell : Cell [3] }`; **a package-level design instance** — a def-only model
  drops the template calc, "no PartUsage instantiations", per `b1-probe-evidence.md`; the assert
  checks `cell.power_calc.p`), `constraint_inline` (an assertion owning its predicate inline),
  and `constraint_blocked_owner` (MF2, Appendix B). Per the B1 adjudication, the multi-instance
  fixture asserts **3 `constraint_id`s / 3 catalog entries / 3 constraint modules each with its
  own evaluation channel + the recorded (shared, de-indexed) producer binding per entry** — not
  three distinct producer channels (those don't exist; out of scope). *Rejected: expecting three
  distinct producer channels — refuted by probe. Rejected: extending `instance_index_probe` for
  the primary multi-instance test — its actual is a shared-QN self-attribute (design-attribute
  path); it stays a secondary inheritance/cardinality cross-check and its Item-4 oracle count
  must not move.*
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
   a. `scoped_lookup` keyed by the *occurrence's own scope* + the reference (single-segment or
      `chain_segments`) → producer channel. The occurrence-scoped key is tried first; when only
      the shared **de-indexed** channel exists (the B1 reality for `[N]` calc siblings), that
      channel is bound and **recorded per catalog entry** (`bound_channel` on the input record) —
      shared-producer verdict-equality is visible data, never a silent collapse.
   b. else `alias_lookup` on the reference (D1 amendment: an in-profile actual may resolve via a
      cross-scope alias) → producer channel, recorded the same way.
   c. else design-attribute match on the reference target QN → mint `DESIGN_ATTRIBUTE` EP,
      keyed by the attribute's real QN, deduped by QN (F4-safe). Per-occurrence redefined
      attributes are distinct QNs, so genuinely-differentiated occurrences wire distinctly here
      with no new machinery.
   d. else **terminal disposition** → strict: generation error naming the actual.
2. No actual but in `omitted_default_formals` with `FormalFact.has_default` → overridable
   modeled-default contract parameter (retains `FormalFact.default`).
3. else → generation error.

The terminal disposition (1d/3) is the shared switch (D1): in lenient/calc mode it synthesizes
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
- **INV-3. Each concrete sibling has its own `constraint_id`, catalog entry, and evaluation
  (output) channel, and resolves its actuals in its own occurrence scope.** Siblings may share a
  *producer input* channel when the model itself has one producer for the `[N]` part (the B1
  reality) — this is legitimate, and the shared binding is **recorded per entry**, never hidden.
  What must never collapse is constraint identity or evaluation channels. (Where the model
  differentiates occurrences via redefined attributes, inputs resolve distinctly too.)
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
- **`resolution/models.py`** (extend) — `ConcreteConstraint` (carries `predicate_ir` as a
  serialized `ExpressionIR` string per D5-IR, plus id/identity/membership/polarity/`expected_value`
  and `eligible`), `ConcreteConstraintInput` (resolution-tagged `module_output` |
  `design_attribute` | `modeled_default`, with the recorded `bound_channel` for module-output
  bindings), and an `unassessed` shape. Pydantic `str`/scalar fields only — no
  `arbitrary_types_allowed`; the serialization contract for Items 7/8 is `serialize_expression`
  in, `parse_expression` out.
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
  `expected_value`, the serialized effective-predicate IR (D5-IR), and the resolved inputs. It
  sets the CONSTRAINT node's `name` (= `constraint_id`) and `evaluation_channel`; it leaves
  `module_type`/generated-class identity to Item 7 (sits with Item 7's class-identity
  decision). Confirm this boundary against Item 7's spec (Open Question resolved this way;
  re-check when Item 7 specs).
- **The occurrence-scope→ScopedKey transform is the delicate bit.** `instance_path` renders
  `Owner__feat[i]__...`; the registry key is a design-prefix-stripped *dotted* path with **no**
  occurrence index (probe-confirmed). The transform strips the design-root prefix and joins by
  `.`; the `[i]` occurrence-scoped key is tried first and misses, so resolution binds the shared
  de-indexed channel and records it (§Architecture 1a). **The earlier "errors loud, never
  collapses" claim is retracted**: a missing occurrence key de-indexes to a channel the registry
  *does* hold, so the correct behavior is a recorded shared binding, not an error — visibility
  comes from the per-entry `bound_channel`, not from raising.
- **`constraint_id` hash width is `sha256[:16]` (64 bits), not `[:8]`** (N1). A hard `collision
  = generation error` halt on a valid model needs more than 32 bits of margin; determinism is
  unaffected and `LocationFact` already disambiguates two anonymous asserts on one instance.
- **P3 reuses the same `group_deriver` instance** built at `pipeline_builder.py:831` (N3): P3 is
  additive and post-Step-7, minting each EP into an *existing* derived group — no
  mutation-after-read hazard (matches S4). Do not rebuild the deriver.
- **Guard the call-sites on presence of constraint facts** so INV-7 holds trivially and the
  corpus gate is clean.
- Reuse `_find_usage_for_channel` (`dependency_backtracker.py:466`) unchanged for P2 (S4
  proved it).

## Potential Risks

- **R1 (settled by B1 probe): per-occurrence producer channels do not exist for `[N]` calc
  siblings.** Resolved, not open: resolution binds the shared de-indexed channel and records it
  per entry (§Architecture 1a, INV-3); per-occurrence producers are out of scope. The residual
  risk is that the strict ladder's occurrence-key-first/de-index-fallback transform must be
  pinned to the registry's real dotted keying — caught by `constraint_multi_instance`.
- **R2: byte-identity regression from touching the shared terminal switch.** Mitigation: D1
  keeps the backtracker's ladder untouched; only the terminal branch is extracted, and the
  corpus gate (timestamp-only-diff + revert, memory `byte-identity-captured_at-churn`) runs
  against the exact replaced function.
- **R3: `constraint_id` hash over an unstable canonical tuple.** Mitigation: canonicalize with
  `sort_keys`/fixed separators (the repo's `_canonical_json` idiom); the tuple contains only
  stable fields (name/location, instance identity, membership, polarity); 64-bit suffix (N1).
- **R5: the strict ladder is narrower than the calc ladder (B4).** A valid in-profile reference
  needing an omitted rung would strict-error. Mitigation: `alias_lookup` added (D1 amendment);
  the narrowing is recorded against the profile, and `constraint_multi_instance` +
  `constraint_inline` exercise the in-profile shapes.
- **R4: inline predicate scope-binding differs from definition-typed.** Mitigation: the
  `constraint_inline` fixture; select strictly via `effective_predicate_source`.

## Integration Strategy

Purely additive to `build_pipeline_context`: three guarded insertions, no reordering of the
existing 10-step sequence. The calc corpus path is unchanged when no assertion is admitted
(INV-7). The new module and models are imported by Item 7 (consumer) and Item 8 (serializer);
keeping `ConcreteConstraint` in `resolution/models.py` gives both a stable import.

## Validation Approach

- **S4 reproduction (`wi014_toy`, S4's model, already in `tests/fixtures/`; N2):** under
  **`include_all=False`** (subset mode — the prune only bites there; the corpus runs
  `include_all=True`) the control run prunes `cost_calc`; the lowered run retains it only via the
  resolved constraint input channel joined as a root (not because every output feeds the exit).
- **Strict resolution:** V11 + channel-reference validation pass on the extended graph; a
  probe with an unresolvable actual produces a generation error naming the actual (no
  synthesized EP).
- **Determinism:** `constraint_id`s and catalog ordering byte-identical across repeated live
  loads.
- **Corpus byte-identity:** full fixture corpus regenerates byte-identically (timestamps
  excepted) under the established gate.
- **Multi-instance (`constraint_multi_instance`):** three concrete constraints, three distinct
  `constraint_id`s, three distinct evaluation channels, and the recorded (shared, de-indexed)
  producer binding on each of the three catalog entries — verdict-equality visible as data, not
  three distinct producer channels (B1-settled).
- **Inline (`constraint_inline`):** an `inline`-form assertion lowers, selecting the usage
  predicate.
- **Blocked owner (`constraint_blocked_owner`):** a constraint-owning def reached through a
  non-finite multiplicity (`[*]`/parameterized/ranged) surfaces a named generation error
  (owner + feature, via Item 4's `AllOccurrencesResult.blocked`), never a skip.
- **Inheritance cross-check:** `instance_index_probe`'s inherited `[3]` assert expands
  correctly; its Item-4 oracle count is unchanged.

## Next-Stage Handoff

- **Fixed:** the three threading points and their order; four-value owner dispatch; source-form
  predicate selection; the ordered strict resolution procedure `scoped_lookup` → `alias_lookup` →
  design-attr-by-QN → shared terminal switch (D1, amended); the B1-settled shared-producer
  binding recorded per entry (INV-3); inline serialized `ExpressionIR` predicate carriage
  (D5-IR); `LocationFact`-based source-local identity; `ConcreteConstraint` in
  `resolution/models.py` (D4); `constraint_id` encoding with `sha256[:16]` (D3/N1); the three new
  fixtures + `instance_index_probe` cross-check (D6); defensive-unassessed disposition (D7);
  `tracking_key` read at lowering (D8).
- **Open:** the exact occurrence-scope→ScopedKey transform (pin against the registry's real
  dotted, de-indexed keying — the residual of the settled B1); whether any omitted strict-ladder
  rung beyond `alias_lookup` turns out in-profile (B4 — add it if so); which `ConcreteConstraint`/
  node fields Item 5 sets vs. Item 7 (confirm when Item 7 specs).
- **De-risk first:** B1 is already probe-settled (`b1-probe-evidence.md`); no blocking spike
  remains. The first implementation step is the occurrence→`ScopedKey` transform against
  `constraint_multi_instance`, asserting the recorded shared binding (INV-3), since that pins the
  one transform the resolver depends on.

## Appendix A: Open-Question dispositions (spec → decision)

| Spec Open Question | Disposition |
|---|---|
| Item 5 / Item 7 line | Item 5 = extended `ComputationGraph` (nodes + minted EPs + joined roots) + `ConcreteConstraint` data; Item 7 emits all code. Item 5 sets node `name`/`evaluation_channel`, leaves `module_type`/class identity to Item 7. (D3 note; confirm vs Item 7 spec.) |
| Per-occurrence input-channel resolution | **Settled by B1 probe.** Each sibling gets its own id/entry/evaluation channel; actual resolution tries the occurrence-scoped key first, then binds the shared de-indexed producer channel (the only one that exists for `[N]` calc siblings) and **records it per entry**. Per-occurrence calc producers are out of scope. `constraint_multi_instance` asserts exactly this (D6). |
| `requirement_def` / out-of-profile | Defensively cataloged **unassessed** (D7); record rides the returned list with `eligible=False`; asserted in tests until Item 7's catalog exists. |
| `constraint_id` encoding | Human-scannable `{instance_path}__{source_local}` prefix + `__` + `sha256[:16]` of the canonical `(source_local_full, owner_instance, membership, polarity)` tuple (D3/N1). |
| `tracking_key` surface | Read at lowering from an author annotation surface if present, else `None`; not in Item 1 fact; never in `constraint_id` (D8). |
| Modeled-default representation | Overridable contract parameter retaining `FormalFact.default`; represented as a `ConcreteConstraintInput` tagged `modeled_default`, surfaced as an eligible-for-selection EP, never an automatic study variable. |

## Appendix B: Fixtures

- **`constraint_multi_instance` (new).** `Cell` owning `power_calc { out p; ... }`; `Container {
  part cell : Cell [3]; assert constraint <bound>(cell.power_calc.p) }`; **a package-level design
  instance** (`part def Design { part c : Container; }`) — required for instantiation discovery,
  since a def-only model drops the template calc ("no PartUsage instantiations",
  `b1-probe-evidence.md`); the working skeleton is `probe_b1_channels.py`. Asserts **3 IDs / 3
  catalog entries / 3 constraint modules each with its own evaluation channel + the recorded
  shared (de-indexed) producer binding** on each entry. This is the multi-instance criterion as
  settled by B1 — not three distinct producer channels.
- **`constraint_inline` (new).** An assertion owning its predicate inline
  (`ConstraintSource.form == "inline"`), so the effective predicate is selected from the usage,
  not a definition. Single instance is enough; the point is the source-form axis.
- **`constraint_blocked_owner` (new, MF2).** A constraint-owning part def reached through a
  non-finite multiplicity (`[*]`/parameterized `[n]`/ranged `[0..5]` — the blocking shapes in
  `part_instance_index.py:98-120`). Lowering surfaces a **named generation error** (owner +
  feature), sourced from `AllOccurrencesResult.blocked` / a raised `NonFiniteCardinalityError`,
  never a skip — the committed test for the blocked-owner `[HARD]` and the Item-4 audit cure it
  depends on. (Model-shape note: keep the blocked leaf a disjoint type so the fixture stays
  loadable, mirroring `instance_index_probe`'s `BlockHost`; `nonunique`/`ordered` shapes that
  emit load-error diagnostics are avoided.)
- **`instance_index_probe` (reuse, cross-check).** Already carries `Bank { member :
  ConstrainedLeaf [3] }` + inherited `assert nonnegative`. Proves expansion cardinality +
  inheritance + distinct evaluation channels via a design-attribute actual. Its Item-4 oracle
  count must not move (extend only with disjoint type families if at all).

---
Next Step: After approval → `/_my_plan`. B1 is probe-settled; no blocking spike remains — first
implement the occurrence→`ScopedKey` transform against `constraint_multi_instance`.
