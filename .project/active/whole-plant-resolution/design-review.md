# Design Review: Whole-Plant Cross-Part Value Resolution (PIPELINE-TRUTH Item 2)

**Design:** `.project/active/whole-plant-resolution/design.md`
**Spec:** `.project/active/whole-plant-resolution/spec.md`
**Review File:** `.project/active/whole-plant-resolution/design-review.md`
**Date:** 2026-07-06

---

## Fundamental Assessment

**Sound.** Value-fill — materialize the supplied literal as a synthetic design
attribute keyed by source QN, merge it into the `design_attributes` map, and let the
existing Step-3 resolution carry it — is the right call, and the design argues it well
against the two adversarial findings the epic raised:

- **Fan-out staying N keys:** the collapse is real and free. `_resolve_to_design_attribute`
  matches on the binding's `source_path`, not on the consumer input name
  (`dependency_backtracker.py:701-710` for the dotted case, `:748-760` for bare). Two
  consumers on different modules that both bind `= driver.efficiency` produce the same
  `source_path` and therefore resolve to the same synthesized QN → one EP. This is exactly
  what the epic's renamed-consumer [HARD] needs, and it holds by construction (see the B2
  caveat below on the *evidence* cited, which is weaker than the claim).
- **Deep re-redefinition divergence:** scoped out with INV-3 requiring loudness, not silent
  wrongness. Acceptable.

The choke-point framing (one pre-pass that only populates an index Step 3 already reads;
zero new dispatch branches) is genuinely simpler than the rejected "Step 3.5" parallel
resolver (D2), and the reuse is honest at the top level. The registry-before-design-attr
ordering that protects RN-10 / VBR-10 is confirmed (`dependency_backtracker.py:547-570`:
channel lookups return first; design-attribute match is reached only on fall-through), so
B3 / INV-1 holds.

This is not a Rework. It is a Revise: the *foundation* is right, but the design leans on
"reuse the existing path unchanged" in four places where the existing path does not, in
fact, do what the design needs — two of them latent silent-failure surfaces, which is the
one thing this epic exists to kill. Those are the must-fixes.

---

## Dimensional Review

### 1. Spec Compliance
**Assessment:** Concerns

Every spec [HARD] has a design element: all four shapes (a)/(b)/(c)/(d) route through the
one materializer; source-QN keying is the fan-out contract; the new REQ is assigned;
the SC-3 runner is a named deliverable; precedence lives in one place; the (d) escalation
rule is honored (d is landable, so no escalation). The offender arithmetic (10 → true
zero) is carried faithfully.

Two compliance gaps:

- **The precedence REQ home may violate the spec's own instruction.** The spec's Must-Fix 4
  says the new REQ must not *silently* overload an existing REQ, and that a reasoned
  extension is fine "if design finds the plain-value path genuinely IS a VBR-10 extension."
  The design files it under **LVP** instead — but doc 18 explicitly fences CalcUsage-binding
  literals off from LVP (see Finding 1). Filing under LVP is the same category of muddying
  the spec's ban targets, just aimed at a different doc. Not resolved by the D3 prose.
- **SC-3 runner interface not pinned for Item 3 reuse** (see Finding 7).

### 2. Pattern Consistency
**Assessment:** Concerns

The design reuses the right seams: `_resolve_to_design_attribute` (Step 3),
`_classify_entry_points`, the `design_attributes` map, `_find_literal_redefinition`. This
is the correct instinct — no parallel dedup path.

But "reuse unchanged" is asserted more strongly than the code supports in two places:

- `_classify_entry_points` does **not** handle a 0.0 default (Finding 2).
- `_find_literal_redefinition` does **not** have a matching strategy that fits (d) cleanly;
  it works for `'Flow Sub'` only via the brittle name-fallback (Finding 4).

### 3. Abstraction Quality
**Assessment:** Pass (with Finding 4 caveat)

The single-materializer abstraction earns its place: it collapses four shapes onto one
choke point with uniform source-QN keying, and it adds no new dispatch branch. The
rejected Step-3.5 alternative (D2) would have been the over-engineered choice; the design
correctly avoids it. The one wrinkle is the (d) lookup reuse (Finding 4) — the abstraction
is right, but the claim that `_find_literal_redefinition` covers (d) as-is is not.

### 4. Duplication Avoidance
**Assessment:** Pass

The design's whole point is to avoid a second EP-keying-and-dedup path (D2). It reuses the
design-attribute index rather than forking one. No parallel structure introduced.

### 5. Data Structure Clarity
**Assessment:** Concerns

`DesignAttributeData` (`parameter_groups.py:47`) is a clear target: the materializer emits
`(name, parent_part, default_value, qualified_name)` and the existing path consumes it. But:

- `DesignAttributeData.default_value` is typed **`str | None`** (`parameter_groups.py:51`),
  not float — the synthetic attr must carry the literal as a *string* (e.g. `"0.35"`) to
  match how real design attributes serialize (`"2.0"` in the twolevel snapshot). The design
  says "carrying the resolved literal" without stating the type; state it, because the 0.0
  truthiness bug (Finding 2) bites at the `str`→`float` conversion in classification.
- The synthetic QN derivation rule (INV-2) is stated as a principle but the collision case
  against a *real* attr sharing that QN or (name, parent_part) is not (Finding 3).

### 6. Route Safety
**Assessment:** Concerns

Two silent-route risks, both in an epic that bans silent failure:

- **Non-literal skip is silent by omission** (Finding 5). "Reads LITERAL only" reads as a
  silent skip; the design must state that a referenced non-literal surfaces loudly (V11 /
  warn), not quietly.
- **0.0 default escapes V11** (Finding 2). A synthesized EP resolves at Step 3, so it is not
  in `_fallback_entry_points`; V11 keys on fell-through (`graph_builder.py:810`,
  `dependency_backtracker.py:580-584`), so a 0.0-dropped-to-None default emits `null`
  silently rather than being caught. This is the exact failure mode the epic targets.

### 7. Bets & Decisions Integrity
**Assessment:** Concerns

The four stated bets (B1 literals, B2 source-QN keying, B3 registry-first, B4 (d) needs no
usage_type_map) are all genuine reality-claims with a stated "if false," and B3/B4 are
verified true against the code and snapshot. Good.

But there are **two hidden bets** the design does not state:

- **Hidden bet H1: `_classify_entry_points` carries a synthesized default faithfully.** It
  does not for 0.0 — `if attr.default_value:` (`graph_builder.py:482`) is a truthiness test.
  The design's "consume the merged attributes exactly as they consume real design attributes
  today" (Component Overview) rests on this unstated bet, and it is false for a falsy literal.
- **Hidden bet H2: `_find_literal_redefinition` has a matching strategy that fits (d).** It
  has two — usage_type_map (Strategy 1) and name-fallback (Strategy 2). (d) has no
  usage_type_map, so it depends on Strategy 2's last-segment name match, which is not the
  same operation as (d)'s natural "redef owner == calc's `owning_part_def_qn`" match
  (Finding 4).

B2's *evidence* is also weaker than its claim: `test_fanout_collapses_to_one_producer_channel`
uses `in s = scale` **twice — the same input name** (`spec_chain_twolevel/library.sysml:75-80`),
so it proves same-name collapse only. The renamed-consumer property is real but rests on the
matcher keying on `source_path` and ignoring `param_name`; cite that code, not this test
(Finding 6).

D1 (value-fill vs wiring) and D4 (no split) are well-reasoned decisions with named,
costed alternatives. D5 (Shape 1 raise-proof) is **verified**: the `plant_value_shapes`
snapshot has `redefinitions = [throughput 8.0]` and `design_overrides = []`, so Shape 1's
`0.70` sits in neither bucket the materializer reads — it stays valueless, V11 keeps firing.

### 8. Reader Comprehension
**Assessment:** Pass

The Core Concept states the model plainly before mechanism ("the value already exists; put
it where the resolver looks"), the shape/bucket/keying table is legible, and the pipeline
diagram anchors the one new step. A tired engineer can get the model in one read. No voice
finding blocks comprehension.

---

## Issues by Severity

### Critical
- None that block the headline flips (the four headline values are non-zero). But **Finding 2**
  is a latent silent-failure the epic bans, and would be Critical the moment a 0.0 supplied
  literal is in scope — which the mechanism's general "carry each supplied literal" claim and
  the existing `raw_material_cost = 0.0` LVP shape both admit.

### Major
- **F1 — REQ-LVP-10 placement contradicts doc 18's stated boundary.** [Dim 1, 7]
- **F2 — 0.0 supplied literal silently escapes V11** via `_classify_entry_points:482`
  truthiness + Step-3 resolution not being fell-through. [Dim 6, 7]
- **F3 — Synthetic-attribute collision handling under-specified** (QN-level last-wins;
  unscoped first-match). [Dim 5, 6]
- **F4 — (d)'s `_find_literal_redefinition` reuse is overstated**; works for the fixture
  only via the brittle name-fallback. [Dim 2, 3, 7]
- **F5 — Non-literal skip loudness not stated.** [Dim 6]

### Minor
- **F6 — B2's cited evidence (same-name test) is weaker than its renamed-consumer claim.** [Dim 7]
- **F7 — SC-3 runner's reuse interface for Item 3 is unpinned.** [Dim 1, 3]
- **F8 — Baseline-drift argument ("expected zero") is thin** but adequately mitigated by
  capture-diff review (SC-5). Concern, not must-fix.

---

## Must-Fix List (numbered, for the design agent)

1. **Reconcile REQ-LVP-10 with doc 18's own boundary.** Doc 18 is titled "Literal Value
   Propagation for *Aggregation* Entry Points" and its scope is SumTerm/SingletonTerm
   (`18-literal-value-propagation.md:1,5-8`). It **explicitly** fences off CalcUsage-binding
   literals as "a path separate from the `_find_literal_redefinition()` lookup this document
   describes" (`18:163-167`), and even excludes LocalTerms (REQ-LVP-04). Filing CalcUsage
   value-fill as REQ-LVP-10 lands on the consumer class the doc hands off to a *different*
   mechanism. D3's rejection of a fresh `REQ-RES-##` ("it would hide that this is the same
   mechanism") is undercut — doc 18 says it is *not* the same mechanism. Decide deliberately
   and record it: either (i) widen doc 18's title + scope sentences to "entry points
   generally" AND reconcile/replace the "separate path" disclaimer, so the family genuinely
   includes CalcUsage inputs; or (ii) give it its own REQ family. Do not muddy doc 18 by
   assertion.

2. **Close the 0.0 silent-failure route.** `_classify_entry_points` sets the default via
   `if attr.default_value:` (`graph_builder.py:482`) — a truthiness test that drops `0.0`
   (and `""`) to `None`. A synthesized EP resolves at **Step 3**, so it is not in
   `_fallback_entry_points`; V11 (`collect_uncovered_params`, `graph_builder.py:810`) keys on
   the fell-through set, so a 0.0 literal becomes a DESIGN_ATTRIBUTE EP with a `None` default,
   emits `null`, and **escapes V11 silently** — the exact failure this epic kills. The four
   headline values are non-zero so the headline flips are safe, but the mechanism claims
   general literal-carrying and `raw_material_cost = 0.0` is a real LVP shape in this
   codebase. Fix: change the check to `is not None` (and add a regression pin for a
   0.0-valued supplied literal), or state precisely why a 0.0 supplied literal is
   out-of-scope for the materializer and guard against synthesizing one. State the chosen
   route; do not leave "reuse unchanged" resting on a false bet.

3. **Specify the synthetic-attribute collision / dedup rule.** Two real collision surfaces
   the design does not pin: (a) `_classify_entry_points` builds `design_attr_by_qname`
   **last-wins by QN** (`graph_builder.py:457-461`) — a synthetic attr sharing a real attr's
   QN silently overwrites it (or vice versa, order-dependent); (b) the dotted match in
   `_resolve_to_design_attribute` returns the **first** `(name, parent_part)` hit across all
   files, unscoped by instance (`dependency_backtracker.py:707-710`). INV-4's parent_part /
   same-instance guard addresses the *bare-name* cross-wire but not the QN-level overwrite.
   Specify: how the materializer detects that a real design attribute already covers the
   source (skip synthesis), and how QN uniqueness is guaranteed so a synthetic attr never
   overwrites or is overwritten by a real one carrying a different value.

4. **State (d)'s exact literal lookup; don't claim clean `_find_literal_redefinition`
   reuse.** For (d), `usage_type_map` is empty (verified: `plant_value_shapes` snapshot
   `usage_type_map: {}`), so `_find_literal_redefinition` falls to **Strategy 2** — a
   last-segment name match, `sanitize_name(redef.owning_part_qn.split('__')[-1]).lower() ==
   part_usage.lower()` (`graph_builder.py:1347-1350`). It matches `'Flow Sub'` only because
   the redef owner's last segment equals the owning part-def name. That is brittle for an
   *inherited* redefinition owned by a supertype, and it is not (d)'s natural operation. (d)
   wants a direct `redef.owning_part_qn == calc.owning_part_def_qn` match (verified: both
   equal `PlantValueShapesLib__Flow_Sub`), which the function does not do today. Either
   extend `_find_literal_redefinition` with a direct-owner strategy and say so, or state
   explicitly that the name-fallback is (d)'s intended path and why it is safe against
   inherited/supertype redefinitions.

5. **State the non-literal skip's loudness.** The materializer reads `redefinitions ∪
   design_overrides`, which also hold CHAIN / EXPRESSION shapes this epic defers
   (`RedefinitionType` = {LITERAL, CHAIN, EXPRESSION}, `data_models.py:240-242`).
   `_find_literal_redefinition` filters LITERAL and returns `None` for the rest — a silent
   skip. For a *referenced* binding whose only value is a non-literal, the design must state
   the behavior explicitly: the skip surfaces loudly as a V11 offender (because the binding
   falls through to Step-4), or the materializer warns Item-5 style. "Reads LITERAL only"
   currently reads as a silent drop, which this epic bans.

6. **Re-cite B2's evidence.** `test_fanout_collapses_to_one_producer_channel` binds `in s =
   scale` **twice — same input name** (`spec_chain_twolevel/library.sysml:75-80`), so it
   proves *same-name* collapse only. The renamed-consumer property is real, but it follows
   from the matcher keying on `source_path` and ignoring `param_name`
   (`dependency_backtracker.py:701-710`) — cite that, and lean on the design's own new
   renamed-consumer fixture as the proof, not the existing same-name test.

7. **Pin the SC-3 runner's public interface for Item 3 reuse.** The runner is concrete
   enough to build (reads pipeline YAML for order + wiring, imports modules, feeds JSON,
   returns `channel → value`). But "reusable by Item 3" is asserted without a pinned call
   signature / return shape. State the interface (inputs, return type) so Item 3's reuse is a
   contract. The teax-importable-vs-fixture-local fork is a legitimate plan-time open; the
   *interface* should not be.

---

## Verified (no action needed — recorded so the design agent can rely on these)

- **B4 / (d) link:** `flow_calc`'s `CalcUsageData.owning_part_def_qn =
  PlantValueShapesLib__Flow_Sub` equals the redef owner `owning_part_qn`, and
  `usage_type_map` is empty. (d) needs no usage_type_map — confirmed.
- **B3 / INV-1:** registry Steps 1–2 return before the design-attribute match
  (`dependency_backtracker.py:547-570`); a synthesized attr cannot shadow a calc-output
  channel. RN-10 / VBR-10 untouched by construction — confirmed.
- **D5 raise-proof:** `plant_value_shapes` snapshot has `redefinitions=[throughput 8.0]`,
  `design_overrides=[]`; Shape 1's `0.70` is in neither bucket, so the materializer does not
  dissolve it. The V11 re-anchor holds — confirmed.
- **Threading gap:** both call sites (`graph_rebuild.py:139-149`,
  `pipeline_builder.py:800-815`) pass `hierarchy_redefinitions` + `usage_type_map` but not
  `design_overrides`; `build_computation_graph` (`graph_builder.py:156`) has no such
  parameter. The design's F-A thread-through is real and necessary — confirmed.

---

## Recommendations

1. Resolve **F1** (REQ home) and **F2** (0.0 route) first — they are the two that touch this
   epic's core discipline (honest doc placement; no silent failure). F2 in particular should
   land a one-line fix (`is not None`) plus a regression pin, independent of the rest.
2. Tighten the three "reuse unchanged" claims (F2/F3/F4) into precise statements of what the
   existing code does and where the materializer must add or guard — the design's strength is
   its choke point, and these are the seams where the choke point actually touches sharp code.
3. F5 and F6/F7 are wording/interface tightening; do them in the same pass.
4. F8 (baseline drift) needs no design change — the SC-5 capture-diff review is the right
   mitigation; just keep the "expected zero, verify each diff" commitment explicit at capture.

---

## Resolutions

*Filled in during Stage 4 as the user resolves findings, keyed by F#. The design agent reads
this section to incorporate the review; the reviewer does not edit the design.*

---

**Overall:** Revise
**Next Steps:** Record resolutions above (especially F1 REQ-home and F2 0.0-route, which
change the doc target and add a code fix + pin), then re-run `/_my_design` (or return to the
design-agent session) pointed at this review to incorporate. The reviewer does not edit the
design.
