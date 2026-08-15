---
date: 2026-08-15T14:27:43-07:00
researcher: Claude
topic: "The 126 bare expression-side usage-owned references, joined to graph edges"
tags: [research, elaboration, source-identity, bare-reference, corpus]
status: complete
last_updated: 2026-08-15
measured_commit: 1244288
---

# Research: The bare expression-side measurement

**Date:** 2026-08-15
**Researcher:** Claude
**Research Type:** Licensed semantic corpus / prospective behavior comparison

## Research Question

`[INHERITED: .project/active/self-binding-replacement/briefs/06-bare-expression-side-measurement.md]`
For each of the 126 bare expression-side usage-owned direct references the qualified corpus scan
left unjoined, join it to a prospective graph edge and compare current versus owner-aware at the
level of exact typed wire edges.

## Verdict

- `[AGENT]` **Nothing changes. Not one bare usage-owned direct reference in the tracked corpus
  produces a different typed wire edge under owner-aware resolution.** 189 bare sites; 153 join to
  a concrete edge; all 153 compare byte-for-byte equal on the wire. 36 do not join, each for a
  named structural reason.
- `[AGENT]` **The corpus cannot distinguish the two routes for a bare reference, so this is a
  no-cost result rather than a certification.** Every one of the 153 joined sites has a leaf-slot
  fan-out of exactly one — there is a single occurrence in the whole model carrying the referenced
  feature slot. With one candidate, the consumer-lineage walk and the owner-anchored walk are
  forced to land on the same node. The qualified corpus does contain discriminating topologies
  (four sites at fan-out two, and they are four of the five changed sites); the bare corpus
  contains none.
- `[AGENT]` **The broad predicate is the right choice, and the narrow alternative buys nothing
  measurable.** Extending the owner-aware branch to all usage-owned one-segment leaves costs zero
  edge changes today. The narrow option's price is threading authored-form evidence through three
  additional resolver callers to protect against a difference that does not exist on the corpus.
- `[AGENT]` **The brief's composition of the 126 is wrong in a way that matters.** Only 76 of them
  are genuinely new resolver-caller coverage (computed-attribute expression terms). 15 are
  *constraint bindings*, which run the same `_resolve_bindings` caller as the 63 calc bindings.
  Zero are typed aliases. Zero are inline constraint predicates. The remaining 35 reach no edge.
- `[AGENT]` **Two shared callers named in the repair's justification have zero usage-owned coverage
  in the corpus: typed aliases and inline constraint predicates.** That absence is a finding, and
  it is the same absence the qualified scan reported — measuring the bare side did not fill it.

## Scope and Method

Measured at codegen `1244288`, which is `c599cfb` plus one documentation-only commit; no source
file differs from the qualified scan's measured tree. The SysIDE license was loaded from
`/home/reid/1cfe/agentic-mbse/.env` and confirmed present in the process environment before any
run. Licensed paths executed; nothing skipped.

The harness is a companion to the qualified scan's, kept deliberately close so the numbers compare:

- **Root set identical to the census's.** Every `tests/fixtures/<family>` root plus every
  `self-binding-replacement/spike/fixtures/<group>` plus the source-identity probe model
  directory — 140 roots, each loaded separately, matching normal fixture admission.
- **Authored text recovered from CST byte spans**, not from a rendered name.
- **Owner-aware simulation only where the resolved leaf's owner is a real `PartUsage`**: select the
  exact owner's occurrence with the live `_select_occurrences` policy, take the exact leaf slot
  inside that occurrence, then **follow typed aliases** through the live `_follow_alias`.
- **Exact typed wire edges compared**, never display names.

The join method differs from the qualified scan's, because expression-side references never appear
in extraction's binding records. The harness instantiates `_ExactElaborator` directly, runs it, and
then walks the elaborator's own `_pending_aliases`, `_pending_expressions` and `_pending_bindings`,
re-deriving each reference through the live `_expression_references` walk and the live
`_resolve_semantic_reference`. Each authored expression is identified by its CST byte span —
`id()` is unusable because the SysIDE bindings hand back a fresh Python wrapper on every traversal.

Two independent checks say the harness is measuring the real thing:

1. **Cross-check against the live graph.** For all 77 binding sites the harness recomputes the
   current edge; it matches the edge actually stored on the consumer node in every case. Zero
   mismatches.
2. **Self-test against the known answer.** Run with qualified references admitted, the same harness
   finds 445 usage-owned direct references and reports exactly five changed — the u4–u7 probes,
   with the same expected edges the qualified scan recorded (`shared_component.length`,
   `plant.comp_a.length` twice, `plant.comp_b.length`, and the u6 rewire from `comp_b` to
   `comp_a`). Everything else, including all 246 CATF variant edges, compares equal. The alias trap
   the brief warned about is handled: without the alias-following step the CATF layer sites would
   have read as changes.

Harness and raw output are gitignored, under
`.project/active/self-binding-replacement/spike/out/` (`bare_expression_side_scan.py`,
`consumer_kind_probe.py`, and their JSON). No tracked source, test, fixture, model, or baseline was
changed.

## 1. Headline Count

The census reproduces the qualified scan's figure exactly: **189** bare direct
`FeatureReferenceExpression` sites whose resolved leaf is owned by a real `PartUsage`.

| Outcome | Sites |
|---|---:|
| Calculation-input bindings (the scan's 63; the brief's out-of-scope half) | 63 |
| **Expression-side and constraint-side subject sites** | **126** |
| — joined to an exact typed wire edge, **compare equal** | **91** |
| — joined to an exact typed wire edge, **change** | **0** |
| — could not be joined | **35** |

Within the 63 calc bindings, 62 join and compare equal; the 63rd is in `non_finite_literal`, a root
that refuses elaboration, so it has no edge to compare. That is the whole of the difference between
the scan's extraction-level 63 and this run's graph-level 62 — not a contradiction, a different
measurement point.

**The 35 unjoinable sites, by reason:**

| Reason | Sites | Where |
|---|---:|---|
| Inline constraint predicate on a `plain_usage` constraint — not asserted, so no constraint node walks the predicate | 18 | `catf_mfe_model` 9, `catf_mfe_d5` 9 |
| Compound expression binding — refused today with `SI_EXPRESSION_SOURCE_UNSUPPORTED`, so no edge is ever minted | 12 | `expression_binding_probe` 11, `invocation_binding_probe` 1 |
| Root refuses elaboration by design | 4 | `constraint_name_collision_probe` 2 (`SI_ID_UNSTABLE`), `elab_unresolved_multiplicity` 1 (`SI_MULTIPLICITY_UNRESOLVED`), `non_finite_literal` 1 (blocking extraction diagnostic) |
| Reference sits in a `MultiplicityRange`, not in a value position | 1 | `elab_finite_expression_multiplicity:18` (`count`) |

None of the 35 is an omission. The first group is the CONSTRAINT-SEMANTICS assert-only rule doing
its job: all 65 constraint usages in `catf_mfe_model` are `plain_usage` and disposition as
`non_reaching` or `excluded`, so their predicates are never walked. The `catf_mfe_gated` derivative
is the asserted variant, and its equivalent sites do join — they are 4 of the 15 constraint
bindings below.

## 2. Every Changed Site

There are none. Zero of the 126 sites, and zero of the 189 bare sites overall, produce a different
typed wire edge, a different diagnostic, or a different edge count under owner-aware resolution.

The structural reason is measurable, not merely argued. Two properties hold for all 153 joined
bare sites:

- **Lexical containment.** Every one of the 189 bare sites is authored lexically inside its exact
  owning `PartUsage`. Verified independently of the join, by walking each expression's owner chain
  and matching qualified names: 189 inside, 0 outside. This confirms the qualified scan's claim.
- **Leaf-slot fan-out of one.** For every joined site, exactly one occurrence in the entire model
  carries the referenced leaf's feature slot. The consumer-lineage walk has one place to land and
  the owner-anchored walk has the same place.

That second property is what the equality actually rests on, and it is why the result is weaker
than the count suggests. Compare the qualified side, measured by the same harness: 252 qualified
sites at fan-out one, **4 at fan-out two** — and those four are u5, u6 and the two u7 sites, three
of the five that change. (u4 changes at fan-out one for a different reason: its single occurrence
is a package sibling outside the consumer's lineage, so the current route misses it entirely.) The
bare corpus contains no site of either shape.

**The alias hop is exercised, and it matters.** 17 joined sites resolve to something other than the
named leaf's own attribute node — a typed alias or a computed producer. 14 of them are
expression-side, in `catf_mfe_gated`'s radial build: each layer writes
`attribute inner_radius : Real = <previous_layer>.outer_radius;` and then
`attribute outer_radius : Real = inner_radius + thickness;`, so the bare `inner_radius` term
resolves through the alias to the previous layer's computed `outer_radius`
(`tests/fixtures/catf_mfe_gated/designs/catf_mfe/radial_build.sysml:594,599`). The prospective
route follows the same alias and lands on the same producer. Skipping that step would have
manufactured 14 false positives on the expression side, exactly as it manufactured 13 on the
qualified side.

## 3. Per-Consumer-Kind Breakdown

The brief named four kinds. The measured composition is different, and the difference changes the
blast radius.

| Consumer kind | Resolver caller | Sites | Joined | Changed | New coverage vs the qualified scan? |
|---|---|---:|---:|---:|---|
| Computed-attribute expression term | `_resolve_computed_expressions` (`elaborate.py:2435-2523`) | 76 | 76 | 0 | **Yes — this is the only genuinely new caller** |
| Constraint binding | `_resolve_bindings` (`elaborate.py:2575-2602`) | 15 | 15 | 0 | No — same caller as the 63 calc bindings |
| Inline constraint predicate | `_resolve_computed_expressions` | 18 | 0 | — | No; all 18 are unreachable |
| Typed alias | `_resolve_aliases` (`elaborate.py:2370-2394`) | 0 | 0 | — | No; **zero usage-owned examples exist** |
| Compound expression binding | none — refused before resolution | 12 | 0 | — | A fifth kind the brief did not name |
| Multiplicity-range reference | none | 1 | 0 | — | Not a value consumer |

**Computed-attribute terms (76).** All 76 are *sub-terms* of a larger expression, never the whole
value — because a computed attribute whose value is a single reference is minted as a typed alias
instead, not a computed node (`elaborate.py:893-918`). None is under a `sum()`, so plural
aggregation over a bare usage-owned leaf is unexercised in the corpus. By root: `attr_expr_probe`
36, `catf_mfe_gated` 30, `quoted_owner_formula` 3, `costed_cart_d5` 2, `unit_lane_radius` 2,
`solar_battery_d5` 1, `solar_battery_model` 1, `unit_lane_computed_disagreement` 1.

**Constraint bindings (15).** By root: `catf_mfe_gated` 4, `modeled_default_fidelity` 3,
`unit_lane_a9` 3, `constraint_name_collision_control` 2, `gate_a_d5` 1,
`source_identity_mixed_consumers` 1, `unit_lane_constraint_disagreement` 1.

**Corpus-wide caller census.** A second probe counted every direct and chained reference each
resolver caller carries, by the kind of element owning the leaf. The usage-owned direct column is
the one the repair touches:

| Caller | direct / `PartUsage` | direct / `PartDefinition` | chained / `PartUsage` |
|---|---:|---:|---:|
| Calculation binding | 318 | 171 | 53 |
| Computed attribute | 76 | 116 | 5 |
| Constraint binding | 15 | 20 | 1 |
| Inline constraint predicate | **0** | 17 | 0 |
| Typed alias | **0** | 9 | 19 |

The 318 calc bindings are the 256 qualified plus the 62 bare, which closes the accounting against
the qualified scan.

## 4. Affected Snapshots and Baselines

**None.** No committed instance-graph snapshot, computation-graph baseline, YAML baseline, or
generated package needs recapture for the bare behavior measured here, because no final edge moves.

For the record, these committed snapshots do contain bare usage-owned sites and were therefore in
scope for the comparison: `attr_expr_probe` (36 computed-attribute terms), `catf_mfe_gated` (30
computed-attribute terms, 4 constraint bindings, 5 calc bindings), `quoted_owner_formula` (3),
`solar_battery_d5` (1 computed, 11 calc), `modeled_default_fidelity` (3 constraint, 1 calc),
`gate_a_d5` (1 constraint), `catf_mfe_d5` (5 calc). Three baseline families carry the corresponding
edges: `attr_expr_probe`, `catf_mfe`, and `solar_battery`. All compare unchanged.

The qualified scan's caveat still applies verbatim: snapshots serialize final input edges, not
semantic reference evidence, so a future fixture with a changed topology would need recapture even
though none does today.

## 5. Which Sites Should Become Kept Regressions

The corpus has good carriers for two of the four recommended regressions and **no carrier at all**
for the other two.

**Computed attribute — carriers exist, pick these.**

- `tests/fixtures/attr_expr_probe/design.sysml:85` — `area * rate`, where `area` resolves through a
  producer and `rate` to a plain attribute. Two term kinds in one line, and the fixture has both a
  snapshot and a baseline family.
- `tests/fixtures/catf_mfe_gated/designs/catf_mfe/radial_build.sysml:599` —
  `inner_radius + thickness`, the alias-hop shape. This is the one that would break first if the
  repair dropped alias following, so it is the highest-value pin of the set. 13 sibling layers
  carry the same shape.
- `tests/fixtures/quoted_owner_formula/design.sysml:25` — `'net margin'`, the quoted-name variant.

**Constraint binding — carriers exist, pick these.**

- `tests/fixtures/modeled_default_fidelity/model.sysml:63,67,71` — three bindings on three
  constraints in one part, snapshot-backed.
- `tests/fixtures/catf_mfe_gated/designs/catf_mfe/physics.sysml:131` — `p_electric_net_out`, which
  resolves to a computed producer rather than an attribute.

**Typed alias — the corpus has no usage-owned example. This is a finding.** All 9 direct alias
leaves are `PartDefinition`-owned (`alias_agg_d5`, `alias_agg_probe`, `d38_caret`); the 19
usage-owned alias references are two-segment chains, which take the contextual path and are not
affected by the repair. Nothing in the tracked corpus exercises `_resolve_aliases` with a
usage-owned one-segment leaf, on either the bare or the qualified spelling. A regression here has
to be authored.

**Inline constraint predicate — the corpus has no usage-owned example. Same finding.** All 17
direct predicate leaves are `PartDefinition`-owned (`constraint_blocked_profile`,
`constraint_coverage_violation_partial`, `constraint_domain_block_non_reaching`,
`constraint_domain_containment`). The 18 usage-owned predicate references that do exist, in
`catf_mfe_model` and `catf_mfe_d5`, sit on unasserted constraints and reach no node. A regression
here has to be authored too.

**Two more gaps worth authoring, both surfaced by this measurement and neither in the scan's list:**

- **A discriminating bare topology.** Every bare site in the corpus has leaf-slot fan-out one, so
  no kept test can currently tell the two routes apart on a bare spelling. The u4–u7 probes prove
  the qualified spelling; a bare sibling of u6 (two same-named children, bare reference from a
  computed attribute inside one of them) would prove the predicate the repair actually implements.
- **Plural fan-out.** None of the 76 computed-attribute terms is under a `sum()`. The one-segment
  path currently ignores the plural flag entirely — `_resolve_semantic_reference` short-circuits to
  `_resolve_leaf`, which is singular by construction (`elaborate.py:2070-2076`). Whether the
  owner-aware branch preserves that or fans out to every owner occurrence is an unforced design
  choice with no test pressure on it.

## 6. The Two Things the Brief Asked Us to Weigh

### Narrow versus broad: take the broad predicate

The narrow option — "honor an authored qualified usage-owned direct reference," with authored-form
evidence threaded into every shared resolver caller — is available. The brief is right that its own
earlier impossibility argument was falsified: the scan recovered exact authored text from CST byte
spans, and this run did the same for all 189 bare sites, so the qualified/bare distinction is
recoverable at the resolver boundary.

It is available and it is not worth it. The whole purpose of the narrow option is to protect the
bare sites from a behavior change. The measurement says there is no behavior change to protect them
from: 0 of 189. The narrow option's cost is real and recurring — authored-form evidence has to
reach `_resolve_aliases`, `_resolve_computed_expressions` and `_resolve_bindings`, three callers
that today share one `_resolve_semantic_reference` and know nothing about spelling, and it has to
keep reaching them as those callers change. Paying that to guard a difference of zero is the wrong
trade.

One honest qualifier, and it cuts against a strong reading of this result: **the broad predicate is
cheap on this corpus, not proven safe in general.** With leaf-slot fan-out one everywhere, the bare
sites could not have shown a difference. The measurement removes the regression objection; it does
not substitute for the authored probes named in §5.

### Bare and qualified: the edges do not contradict the KerML argument, and they do not confirm it

The brief's argument is that a bare name resolving to a usage-owned redefinition denotes that
usage's feature by the same KerML §7.3.4.5 reasoning that settled the qualified case, so the bare
case is the same defect rather than scope creep.

The edges are consistent with that and cannot test it. Every bare site in the corpus is authored
inside its owning usage, and every one has a single candidate occurrence, so "resolve from the
consumer's lineage" and "anchor on the owner" name the same node by construction. The two readings
of the language are behaviourally identical everywhere the corpus can look.

What the measurement does establish is that adopting the KerML reading for bare references costs
nothing today. What it cannot establish is that the reading is right where it would matter — and
the corpus contains no bare site where it would matter. If the owner wants that settled by
evidence rather than by argument, the bare sibling of u6 in §5 is the cheapest way to get it.

## Code and Test References

- `src/sysml_codegen/elaboration/elaborate.py:2062-2076` — the one-segment shortcut the repair
  would change.
- `src/sysml_codegen/elaboration/elaborate.py:2299-2348` — `_resolve_leaf`, today's
  consumer-lineage walk.
- `src/sysml_codegen/elaboration/elaborate.py:2158-2219` — `_select_occurrences`, reused verbatim
  by the prospective route.
- `src/sysml_codegen/elaboration/elaborate.py:2417-2433` — `_follow_alias`, the step that must not
  be skipped.
- `src/sysml_codegen/elaboration/elaborate.py:2370-2394` — the alias caller (zero usage-owned
  direct coverage).
- `src/sysml_codegen/elaboration/elaborate.py:2435-2523` — the computed-attribute and predicate
  caller (76 sites and 0 sites respectively).
- `src/sysml_codegen/elaboration/elaborate.py:1780-1792` — where a compound expression binding is
  refused before it can reach any resolver.
- `src/sysml_codegen/elaboration/elaborate.py:1219-1226` — why an unasserted inline predicate is
  never walked.
- `src/sysml_codegen/elaboration/elaborate.py:893-918` — why a whole-value single reference becomes
  an alias rather than a computed attribute.
- `.project/research/20260815-140630_qualified-binding-corpus-scan.md` — the qualified half of this
  pair.

## Limitations

- This is a prospective route composition at `1244288`, not an implementation diff. It reuses the
  live owner identity, occurrence-selection policy, slot transition and alias-following semantics,
  but there is no patched before/after full-graph fingerprint.
- The prospective route's behavior under `plural=True` is a harness choice, not a specified one.
  No bare usage-owned site in the corpus is plural, so the choice is untested either way.
- 35 of the 126 sites reach no edge today. Their comparison is deferred, not decided: if a future
  change makes unasserted predicates or compound expression bindings resolvable, those 30 sites
  become live and want re-measuring. All 35 are lexically owner-local, so the same fan-out argument
  suggests they would also compare equal, but that is inference, not measurement.
- Adjacent customer trees were not re-scanned. The qualified scan established that every `::` site
  in `fusion-tea` and the stellarator demo is an enumeration literal; bare references in those trees
  were not inventoried here, and a whole-plant regeneration should not assume this result covers
  them.
