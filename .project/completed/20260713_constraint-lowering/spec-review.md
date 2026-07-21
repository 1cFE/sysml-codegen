# Spec Review: Concrete Constraint Lowering (Item 5)

**Spec:** `.project/active/constraint-lowering/spec.md`
**Contract:** `claude-pack/commands/_my_spec.md`
**Review File:** `.project/active/constraint-lowering/spec-review.md`
**Date:** 2026-07-12
**Reviewer posture:** adversarial; verified against code and the landed-type reference copies, not the spec's word.

---

## Reality Check

**Sound — Revise.** The spec is about the right work item, and it is directionally correct on all five scope axes. It correctly names the two traps (strict-resolution EP-key collapse; the silence trap), it productionizes S4's proven shape faithfully, and every code seam it cites is real and at the line it claims (`scoped_lookup` `output_registry.py:186`; `_find_usage_for_channel` `dependency_backtracker.py:466`; `_validate_channel_references` `graph_builder.py:641`; `collect_uncovered_params` `graph_builder.py:800`; `module_kind` required at `models.py:193`, `CONSTRAINT`/`REPORT_AGGREGATOR` at `160-170`). The blocked-multiplicity `[HARD]` (spec §"ConcreteConstraint", the non-finite requirement) is well-specified and matches `part_instance_index.py` exactly (`AllOccurrencesResult.blocked`, `SourceOwnersResult.blocked`, `occurrences_of` raising `NonFiniteCardinalityError`) — this is a genuine strength; the Item 4 swallow the audit killed cannot recur under this spec.

The concerns are not about direction. They cluster in one place: **the spec author could not read the landed `agentic-mbse` Item 1 types, and the real fact shapes diverge from the spec's mental model in several load-bearing ways.** The spec explicitly punts "design must read the real shapes." That is fine for field names, but three of the divergences change *spec-level semantics* — the expansion taxonomy, the resolution taxonomy, and the anonymous-assertion identity source — so they cannot be left for design to discover without risking a mis-build. Those are the must-fixes below.

---

## Audit

### Lens 1 — Faithfulness

**L1-1 · Direct claim (must-fix):** The expansion taxonomy does not match the landed discriminant, and its provenance tag over-claims.

The spec (§"ConcreteConstraint", second bullet) lists **three** expansion sources — "part-def-owned," "calc-def-owned," "direct-usage-owned expand once" — tagged `[INHERITED: concept; epic §2]`. Two problems:

- **The tag is wrong.** Concept "Concrete Lowering" (line 94) gives expansion rules for *only* part-def-owned and calc-def-owned. Epic §2 (`epic_constraint_execution.md:259`) likewise names only those two. "Direct-usage-owned expand once" appears in *neither* — it came from the review brief (`briefs/spec.md:22`), an `[AGENT]`-grade orchestration artifact. Per capture-fidelity Law 1, this should be `[INFERRED]` (from the concept's ownership taxonomy at line 268), not `[INHERITED: concept; epic §2]`.
- **The categories don't map to the real field.** The landed `OwningDefinitionFact.kind` (`constraint_facts.py:52-63`) has **four** values — `part_def`, `calc_def`, `requirement_def`, `package` — resolved by walking `owner` up to the first enclosing definition/package. There is no `direct_usage` kind: a top-level (directly-owned) constraint resolves to `kind == "package"`. So the spec's "direct-usage-owned" is prose for what the fact calls `package`, and `requirement_def` is a fourth kind the spec never mentions. Design dispatching on the real field will find four cases and a taxonomy that names three, one of them by a label the field doesn't use.

**What needs to be true:** the expansion rule dispatches on `owning_definition.kind`, enumerates all four values, and states the disposition of each — including whether `requirement_def`-owned and `package`-owned assertions reach lowering at all (see L1-6: the profile likely filters require/assume/satisfy upstream, leaving `part_def`, `calc_def`, and `package`), and which kind is the "expand once" case.

**L1-2 · Direct claim (must-fix):** The strict-resolution outcome list mis-frames how references resolve, and S4's own code contradicts it.

The spec (§"Strict resolution", legal-outcomes bullet) bifurcates: a **chain actual** (`cost_calc.cost`) resolves via `scoped_lookup` to a producer channel; a **reference actual** resolves "against design attributes, minting a `DESIGN_ATTRIBUTE` entry point." This chain-vs-reference split is a false dichotomy. A single-segment *owner-scope reference* (a bare feature name that names a sibling calc output) also resolves to a producer channel — the concept's executable profile explicitly admits "owner-scope references" (concept line 90, 96), and S4's own `_resolve_actual_strict` (`s4_lib.py:319-326`) tries a scoped-channel lookup for plain references *after* the design-attribute miss. Under the spec as written, a design reading only this list would route every non-dotted reference to a design attribute and never attempt channel resolution, breaking in-profile owner-scope references.

**What needs to be true:** frame resolution as one ordered decision over a feature reference — attempt owner-scope producer-channel resolution; else a design-attribute entry point; else a generation error — with the precedence pinned (S4 tried design-attribute first for plain refs, channel-only for dotted chains; design must choose deliberately, not inherit S4's incidental ordering). A "chain" is just a multi-segment reference, not a separate category.

**L1-3 · Question to the user (fact-shape):** Where do "modeled default" and "omitted formal" actually live in the landed facts?

The spec's coverage rule ("a formal that has neither an actual nor a modeled default is a generation error"; "a defaulted formal with no actual becomes an overridable contract parameter") is correct in outcome. But the landed shapes it must read against are: defaults live on `ConstraintDefinitionFact.formals[*]` (`FormalFact.has_default`, `FormalFact.default: ExpressionIR`), while the *usage* carries an explicit `omitted_default_formals: list[str]` (`ConstraintUsageFact`, `constraint_facts.py:135`). So "omitted defaulted formal" is a direct read of a landed field, not a diff S4 had to compute — and "no actual, no default" is the residue after subtracting `actuals` (keyed by `formal_targets`) and `omitted_default_formals` from the definition's formals. This is mostly design mechanism, but the spec should at least point the coverage rule at these fields so design doesn't re-derive S4's name-diff approach and miss the explicit `omitted_default_formals` signal. **Is `omitted_default_formals` the intended source of truth for the contract-parameter case?**

**L1-4 · Direct claim (must-fix):** Anonymous-assertion identity ignores the landed `LocationFact`, which Item 1 shipped as the identity source.

The spec's Open Question on `constraint_id` string encoding proposes "the anonymous-assertion ordinal scheme within a source-local part" and defers it to design. But Item 1 already landed the answer: `LocationFact` (`constraint_facts.py:42-49`) is documented `[HARD]` as "an anonymous assertion's only identity," carried on every `ConstraintUsageFact.location`. The spec never mentions it. Location is stable across repeated live loads of the same source (satisfying the determinism criterion) and moves on edits (satisfying the no-cross-version-stability caveat) — it *is* a source-local identity. Design should not be inventing an ordinal scheme de novo while a certified `[HARD]` field already claims this role.

**What needs to be true:** the identity requirement reconciles "source-local identity" with the landed `LocationFact` — is source-local identity the usage name when named and `LocationFact` when anonymous, or something else? Pin the relationship rather than leaving design to choose between an ordinal and a field Item 1 built for exactly this.

**L1-5 · Direct claim:** `tracking_key` is not on the certified Item 1 fact — the Open Question understates the constraint.

The spec's Open Question on `tracking_key` says whether it "arrives on the Item 1 fact or is read at lowering" is a "design + Item 1 coordination question." Stronger fact: the landed `ConstraintUsageFact` (`constraint_facts.py:124-138`) has **no** `tracking_key` field. Item 1 is CERTIFIED. So "arrives on the Item 1 fact" is not a live option without reopening a certified item — the realistic space is (a) read at lowering from some other authoring surface, or (b) a scoped Item 1 extension with its own re-certification cost. The Open Question is fine to keep, but it should name this so design doesn't cost the wrong option.

**L1-6 · Question to the user (fact-shape / effective predicate):** The spec never addresses the `ConstraintSource.form` axis or where the effective predicate lives.

The landed `ConstraintSource` (`constraint_facts.py:73-91`) tags each usage with a `form` (`inline` / `definition_typed` / `named_usage_reference` / `requirement_constraint` / `satisfy` / `plain_usage`) and an `effective_predicate_source` pointer — because inline and definition-typed put the predicate in *different places* (on the usage vs. on the definition), which the concept calls out (line 88, 94). The executable profile admits **both inline and definition-typed** asserts (concept line 90). S4 handled only `definition_typed` (`s4_lib.py` captures `source_form="definition_typed"` hard-coded). The spec's `ConcreteConstraint` carries "source facts" but never says lowering must select the effective predicate per `form`, nor that inline is in scope. A design reading only the spec + S4 would build a definition-typed-only lowering and silently fail the inline half of the profile.

**What needs to be true:** state that lowering resolves the effective predicate per `source.form` (usage predicate for inline; definition predicate for definition-typed), that both are in the first-scope profile, and — tying to L1-1 — that this `form` axis is *orthogonal* to the `owning_definition.kind` axis (the two are conflated nowhere-named today; see L5-1).

### Lens 2 — Problem & Approach

**L2-1 · Direct claim (must-fix):** Multi-instance part expansion — a whole success criterion — rests on a path S4 explicitly did not exercise, and the spec doesn't flag it.

The "Deterministic identity" success criterion demands "Fixed-multiplicity siblings are independently wired — three occurrences are three wired nodes with three distinct channels, not copies." But S4 ran on `wi014_toy`, which has a single instance (`demo_plant`); the concept's S4 result explicitly lists "**Not exercised: … multi-instance expansion**" (concept line 297). The spec flags calc-def-owned and direct-usage-owned as "new paths this item builds" but does *not* flag that multi-occurrence part expansion — and, critically, per-occurrence *input-channel* resolution (does each sibling's actual resolve to a distinct producer channel in its own occurrence scope, or do siblings share one input channel while only their evaluation channels differ?) — is unproven by the vertical slice. This is the item's highest-risk new surface and it reads as already-proven.

**What needs to be true:** the spec should mark multi-instance expansion as new/unproven (S4 didn't do it), and pin the per-occurrence input-resolution question: distinct evaluation channels are necessary but not sufficient; the spec should say whether input channels are resolved per-occurrence scope. S3's `[3]`-expansion fixture (concept line 287) is the natural evidence base — see L3-3.

### Lens 3 — Pipeline Risk

**L3-1 · Rewrite request:** Phase placement is an accurate ordering but not a call-site, and it undersells that lowering threads through three points, not one.

The spec describes the seam as "a new pipeline phase that runs after aliases, the output registry, and supplied-value materialization … and before dependency backtracking." That ordering is *correct* — I traced it: `pipeline_builder.build_pipeline_context()` (`pipeline_builder.py:685`) runs the alias step (~`793`), `_rescue_self_named_bindings` (~`800`), then Step 5.65 `materialize_supplied_values` (~`808-817`), then Step 6 creates the backtracker and calls `find_required_modules` (~`834-840`), then `build_computation_graph` (~`889`). But the spec names none of this, while its Related Artifacts list cites many *other* exact seams — an asymmetry that leaves design to relocate the one seam that matters most. And the "before backtracking" framing hides that lowering is not a single pre-backtracking block: it (1) resolves actuals after `materialize_supplied_values`, (2) injects the resolved channels as roots *into* the `find_required_modules` target list (§"Roots before pruning"), and (3) extends the graph *after* `build_computation_graph` (§"Extended graph"). S4's `generate_s4_package` shows exactly this three-part threading. The spec's sections collectively cover all three, but the "one new phase before backtracking" prose obscures it.

**What needs to be true:** cite the insertion call-site (`pipeline_builder.build_pipeline_context`, the Step 5.65 → Step 6 boundary) and state that lowering threads through three points (resolve → inject roots into `find_required_modules` → extend post-build), not a single pre-backtracking block.

**L3-2 · Question to the user (F4 lesson):** The minted `DESIGN_ATTRIBUTE` EP-key collision discipline is gestured at but not pinned.

The spec forbids the backtracker's bare-`{module_eqn}__{leaf}` synthesis (correctly — that is the F4 collapse) and says minted EPs go "in their derived parameter group." But it never states the *positive* rule that makes minting collision-safe: S4 keys the EP by the design-attribute's real qualified name and deduplicates against existing group parameters by QN (`s4_lib.py:496,504` — an already-present QN is *reused*, not re-minted or collided). That is precisely why it avoids the F4 bare-key collapse: the key is a globally-unique attribute QN, and a design attribute already exposed as an entry point (because a calc consumes it) is the *same* parameter, not a collision. The "Deterministic identity" criterion covers `constraint_id` collision (→ generation error) but is silent on minted-EP-key collision.

**What needs to be true:** state the minting key (design-attribute QN), the dedup-by-QN rule (same attribute ⇒ reuse the existing EP, not an error), and that this is the F4-safe alternative to synthesized keys.

**L3-3 · Question to the user:** The multiplicity-sibling half of the identity criterion has no named test fixture.

`wi014_toy` (S4's and the criterion-1 fixture) has one instance, so it cannot exercise "three occurrences are three wired nodes." S3 built a `[3]`-expansion fixture that "found all nine expected occurrences with byte-identical IDs and catalog ordering" (concept line 287). The spec asserts the sibling-wiring criterion but names no fixture that would catch a violation. **Is the S3 `[3]` fixture (or a promoted form of it) the intended committed test for this criterion, and is it in scope to land here?** Without it, criterion 3's second half is untestable and L2-1's risk goes unverified.

**L3-4 · Question to the user (nullable fields):** `is_negated` and `membership_kind` are nullable in the landed fact — what does lowering do when they're `None`?

`ConstraintUsageFact.is_negated: bool | None` and `.membership_kind: str | None` (`constraint_facts.py:132-133`); the concept notes today's type-level classification "collapses [membership] to 'plain'" (line 88). The spec derives `expected_value` from negation ("a negated assertion expects false") and folds membership kind + polarity into `constraint_id`. Both are undefined if the field is `None`. Presumably the profile guarantees an asserted, polarity-known usage — but the spec should say so (or name the error), because a `None` here silently poisons both the expected value and ID determinism.

### Lens 4 — Hygiene

None material. (The agentic-mbse path in Related Artifacts, `~/1cfe/agentic-mbse`, is correct and matches the wired-in install; no finding.)

### Lens 5 — Reader Comprehension

**L5-1 · Rewrite request:** The two orthogonal classification axes are never named as such, which is the root of L1-1 and L1-6.

The landed facts classify a usage on two independent axes: **who owns it** (`owning_definition.kind` — drives expansion cardinality) and **where its predicate lives** (`source.form` — drives effective-predicate selection). The spec's prose ("part-def-owned," "chain vs reference," "definition-typed") mixes both axes without ever telling the reader they are two axes. A tired engineer — and the design agent — will conflate "direct usage" (a `form`/authoring notion) with "package-owned" (a `kind` notion), which is exactly the L1-1 slip. Naming the two axes once, up front, and dispatching each rule against the axis it belongs to would remove three of the findings above at once.

---

## Engagement Summary

**Overall take:** The work item is right and the spec is a faithful productionization of a proven spike, with genuinely strong handling of the blocked-multiplicity trap. It is held back by one thing: the author was blind to the landed Item 1 types, and the real fact shapes diverge from the spec's model on three semantic points — the expansion taxonomy, the resolution taxonomy, and anonymous-assertion identity — plus one unflagged risk (multi-instance expansion was never exercised by S4). These are targeted edits, not a re-think. Verdict: **Approved-with-must-fixes (= Revise).**

**Here's what I need you to weigh in on:**

1. **[L1-1]** Expansion must dispatch on the real `owning_definition.kind` (four values: `part_def`/`calc_def`/`requirement_def`/`package`), not the three prose categories. Confirm the mapping — is "direct-usage-owned = `package`, expand once," and what happens to `requirement_def`? Also fix the provenance tag (it's `[INFERRED]`/from-brief, not `[INHERITED: concept; epic §2]`).
2. **[L1-2]** Reframe strict resolution as one ordered decision over a feature reference (owner-scope channel → design-attribute EP → error), not chain-vs-reference. S4's own code resolves plain owner-scope references to channels; the current list would break in-profile references.
3. **[L1-4]** Reconcile anonymous-assertion identity with the landed `LocationFact` (Item 1 shipped it `[HARD]` as "an anonymous assertion's only identity"). The Open Question proposes an ordinal and ignores it.
4. **[L1-6, L5-1]** Address the `source.form` axis: inline and definition-typed put the predicate in different places, both are in-profile, S4 did only definition-typed. Name the two orthogonal axes (owner kind vs source form) so design doesn't conflate them.
5. **[L2-1, L3-3]** Flag multi-instance part expansion as new/unproven (S4 explicitly didn't do it), pin per-occurrence input-channel resolution, and name the fixture (S3 `[3]`) that tests the sibling-wiring criterion.
6. **[L3-2]** Pin the minted-EP collision discipline (key = design-attr QN, dedup-by-QN = reuse, not collide) — the positive rule that makes minting F4-safe.

Lower-stakes: **[L1-3]** point the formal-coverage rule at `omitted_default_formals` / `FormalFact.default`; **[L1-5]** note `tracking_key` is absent from the certified Item 1 fact; **[L3-1]** cite the `build_pipeline_context` Step 5.65→Step 6 seam and the three-point threading; **[L3-4]** define behavior when `is_negated`/`membership_kind` are `None`.

---

## Resolutions

_To be filled in as the owner resolves findings. Keyed by ID; this is what the spec agent reads to incorporate the review. The reviewer records resolutions here and does not edit `spec.md`._

---

**Verdict:** Approved-with-must-fixes (**Revise**). The work item is sound; the must-fixes are fact-shape reconciliations the author could not do without the landed `agentic-mbse` types, plus one unflagged risk. None require re-thinking the approach.

**Next Steps:** Record resolutions above, then re-run `/_my_spec` (or return to the spec-agent session) pointed at this review to incorporate. The reviewer does not edit the spec. After the spec is revised, proceed to `/_my_design`.
