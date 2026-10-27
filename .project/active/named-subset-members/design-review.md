# Design Review: Named subsets are members of the collection they subset

**Design:** `.project/active/named-subset-members/design.md` (rev `90c01150`)
**Spec:** `.project/active/named-subset-members/spec.md`
**Review File:** `.project/active/named-subset-members/design-review.md`
**Date:** 2026-10-26
**Reviewer:** fresh subagent; did not write the spec or design. Probes ran on the prototype patch applied in a scratch worktree (`/tmp/claude-1000/nsm-review/`, now removed). Probe models are in `/tmp/claude-1000/nsm-review/shapes/`.

---

## The Point

Today the generator builds too many parts when a model names some members of a collection. With `servers : Server[2]` and `part server_1 :> servers;` it builds three servers, and `sum(servers.power)` adds the two unnamed copies (defaults) and leaves out `server_1`. That is a confident wrong number. KerML 7.3.4.4 says a subsetting feature's values are values of the subsetted feature, so `server_1` is one of the two servers. The owner chose option A: a named subset counts as one of the collection's members, the generator builds the declared count, and `sum()` reaches every member once. The product promise behind it (ADR 0004, product 0003 and 0004) is: each modeled member is exactly one concrete copy, or the model is refused by name. The owner's priority across this effort is no silent wrong numbers.

## Fundamental Assessment

**Sound approach, two holes that still build silent wrong numbers. Verdict: Revise.**

The approach is right. Reading the parser's subsetting relation once, shrinking the copy count where copies are built, and filing named members under the collection's slot so every containment read sees them is the smallest change that fixes the cause. The count fix (D4) is correct SysML. I reran every number the design claims and they hold (details under Proof below).

But the brief's first test was "try to make it build a wrong count or sum", and two ordinary shapes still do, with no diagnostic:

1. **A named member that is redefined somewhere else loses its membership** (must-fix M1). `part def Rack { part servers : Server[2]; part server_1 :> servers; }` with `part rack : Rack { part :>> server_1 { :>> power = 15.0; } }` builds three servers and `total` is 20.0 in real TEAx. The right answer is 25. The same happens in the dc3 shape when a usage sets values on `rack_1` with `part :>> rack_1 { ... }` (20.0, should be 25). This is the natural next thing a dc3 modeler writes.
2. **D6 tests the collection's own multiplicity, not the inherited one from D4** (must-fix M2, found by the product lens and reproduced). A named member that is not a sibling, aimed at a redefinition without a count, is built as an extra part and left out of the sum: 20.0 where KerML gives 25.

Both have small fixes inside the design's own frame (below). Neither changes the approach, so this is Revise, not Rework.

Product lens: run as a separate subagent against the repo's product statements. Gate **BLOCKED** on M2 (its F1); block is in the Product Lens section at the end. The brief limits me to writing this file, so the block is recorded here and not yet appended to `product-lens.md`. No structural smell fired.

---

## Dimensional Review

### 1. Spec Compliance
**Assessment:** Concerns

- Every success criterion has a design element, and the measured numbers match: s1 25, s2 35, s4 35; the six `candidate-es-008` cases at 4 PSUs with the listed values; the premise conflict resolved by taking the count fix.
- The spec's `[NEED]` "a read of the whole collection reaches the named members and the unnamed copies, each once" fails in M1 and M2. The spec's falsifier ("a model of a shape the spec does not list builds a count that differs from the model's, with no refusal") fires.
- The spec's `[INFERRED]` rule "applies wherever the named subset and the collection end up features of the same part" is exactly what M1 breaks: after `part :>> server_1`, the member and the collection are still features of the same part, but the design keys membership by declaration, and the redefining declaration has no subsetting of its own.
- Provenance: option A is labelled `[OWNER]` in the spec and design. The quoted words ("ok understood, proceed with the fix", after the orchestrator recommended A) are the owner approving a recommendation, which capture-fidelity grades `[AGENT] (ratified by owner, 2026-10-26)`. Nothing changes in practice, because the substance is KerML 7.3.4.4. (Note N4.)

### 2. Pattern Consistency
**Assessment:** Pass

- Refusals go through `MultiplicityExpansionError` beside the existing multiplicity refusals, with existing codes and new `SiteReason` members. That is the repo's pattern.
- Reading raw parser properties in `occurrence.py` is allowed by ADR 0012; the design names the manifest rows and the two guards (`test_elaboration_import_boundaries.py`, `test_expression_evidence_ownership.py`) that must stay green.

### 3. Abstraction Quality
**Assessment:** Concerns

- **Membership is keyed by declaration, but everything else in the index is keyed by slot** (the slot is the root of a redefinition chain, `build_feature_slot_index`, `occurrence.py:386-443`). That mismatch is the cause of M1. Keying membership by the member's slot fixes it: I tried it in the scratch worktree (a slot-keyed lookup in `named_member_counts` and for `member_of_slot`) and both M1 shapes give 25.0, while s1, s2, s4, r1, r2, r4, r7, r9 and r11 give the same results as before.
- **Filing a member in two buckets leaks into `OccurrenceIndex.children()`** (`occurrence.py:547-553`), which iterates the same dictionary. On s1, `children(rack)` now returns `server_1` twice. Only a unit test calls `children()` today (`tests/unit/test_elaboration_occurrence.py:202`), so nothing is wrong yet, but the design's claim that the change reaches "every read, and only reads" missed this method. (Should-fix S2.)
- The rest is at the right level: no new class, one new field on `ExactOccurrence`, `children_for_slot` and `resolve_address` unchanged.

### 4. Duplication Avoidance
**Assessment:** Pass

No parallel structure. The only near-duplicate is the D7 check against SysIDE's `usages` while the prototype also carries an unused ownership helper (`_family_owns_non_part_features`). S1 recommends using ownership instead, so one of the two goes.

### 5. Data Structure Clarity
**Assessment:** Pass

`member_target`, `member_slot` and `member_of_slot` are explicit. After M1 the natural shape is one map from member slot to collection slot.

### 6. Route Safety
**Assessment:** Concerns

Read "route" here as "the path a model takes to build or refuse". Two fall-throughs build instead of refusing:

- D6 builds a non-sibling named member "as today" whenever the target has no owned multiplicity. That covers the inherited-count case (M2) and the count-1 case (S5).
- The D7 loop steps past evidence it cannot classify (`except KeyError: continue`, and the owner filters before it). ADR 0004 asks for a named refusal when parser evidence cannot be classified, not a skip. S1's ownership check removes most of this loop.

### 7. Bets & Decisions Integrity
**Assessment:** Concerns

- **B4 (redefinition inherits the count) is right, and stronger than the design says.** SysML Part 1 §7.6.3 (`agentic-mbse/docs/sysmlv2/SysML_Spec_v2_Part1/full_document.md`, around line 3559): "If a multiplicity is not declared for a usage, then the usage inherits the multiplicity constraints of any other usages it subsets or redefines." KerML 7.3.4.5: a redefinition requires the same values, so multiplicity restrictions apply both ways. KerML 7.3.4.4: "If a subsetted feature is ordered, then the subsetting feature must also be ordered", and the same applies to redefinition. So the three flips are corrections:
  - `g1__redefinition_drops_ordered_bounds` (`part :>> servers;` over `Server[2] ordered`): it built one copy with the ordering dropped, which was a wrong count. Refusing it as ordered is right.
  - `f1_inherited_ordered_redef`: it was refused as `NOTHING_TO_GENERATE` and is now refused as ordered. Same outcome, more accurate reason.
  - `usage_owner_bare_subset_def_owned`: `comp_b :> comp_a` with `comp_a { :>> length = 3.0; }`. The committed package gives `comp_b.length` 1.0, so `doubled` is 2.0; by KerML `comp_b` is `comp_a`, so it is 6.0. Today's output is a wrong number, and refusing is a correction. The design handles it honestly. One cost: its plan keeps the anchoring guard by deleting the value write from the fixture, which makes that fixture test less. That is acceptable only if the original moves into the D7 refusal case, as planned.
- **Hidden bet, which conflicts with the same §7.6.3 sentence (should-fix S3).** That sentence also says a usage with explicit owned subsettings that declares no multiplicity inherits the subsetted feature's multiplicity. The `[1..1]` default applies only when there is no explicit subsetting (condition 3). Read literally, `part server_1 :> servers;` beside `servers : Server[2]` has multiplicity 2, so it would be both servers, not one. Option A treats an unadorned named subset as one member. That matches what modelers mean and dc3's 28 uses, but it is an interpretation, and the design does not state it. Then D9 refuses `server_1 : Server[1] :> servers`, which is the one form whose spec meaning is exactly "one member". This is a premise conflict to surface, not to settle quietly. My recommendation: record the interpretation in `modeling-assumptions.md`, and accept an explicit `[1]` (D9 currently rejects it only to avoid evaluating a bound, and evaluating it is cheap with `_modeled_integer_bound`). I did not check whether SysIDE exposes an inherited multiplicity for subsetting usages.
- **B2 is true for direct subsetting and false through redefinition.** The subsetting relation is exact evidence, but only on the declaration that writes it. A redefinition of the member inherits the membership semantically and carries no `owned_subsettings` of its own (M1).
- **B3 / D7 rest on SysIDE's `usages` being complete.** It is not complete. Probe p5: `part def Rack12 :> Rack { part :>> servers { :>> power = 12.0; } }` and `part rack : Rack12 { part server_1 :> Rack::servers; }` builds and sums 22.0. By KerML 7.3.4.5 every value of `rack.servers` has power 12, and `server_1` is one of them, so the answer is 24. The same model written `:> servers` (p5b) is refused by D7. The design's Risks section accepts exactly this gap. It is avoidable (S1).
- D1 to D10 each name a rejected alternative. D6's "build as today" for count-1 non-siblings contradicts D5's "one rule for every count" (S5).

### 8. Reader Comprehension
**Assessment:** Pass

The Core Concept states the rule in plain words before the mechanism, and the Architecture's five steps map one-to-one onto code. The term "sibling" carries a lot of weight (it decides counted, refused or built as today). The design should define it once: a named member and its collection are siblings when both are child declarations of the same occurrence, or roots of the same package. After M1, it should say "by slot".

---

## Proof (what I reran)

- **Real TEAx sums** on the prototype: s1 25.0, s2 35.0, s4 35.0. Correct.
- **Whole corpus**, base `90c01150` and prototype, 464 roots each, `corpus_all.py`, `diff -rq`: exactly 10 roots differ. They are the six `candidate-es-008` cases, `part-multiplicity__redefinition_drops_bounds__expanded_part_usage`, `g1__redefinition_drops_ordered_bounds` (generated, now refused as ordered), `f1_inherited_ordered_redef` (refusal reason changes) and `usage_owner_bare_subset_def_owned` (generated, now refused under D7). This matches the design's list.
- **dc3:** byte-identical to `exploration/ac_dc_baseline/dc3_baseline/` on both base and prototype, **but only when regenerated from the committed models** (`git archive HEAD models`) with `--package-name dc3_baseline`. The dc3 working tree has uncommitted model edits right now (`ac_site.sysml`, `dc_site.sysml`, `baseline_costs.sysml`, a new `rated_costs.sysml`), and generating from `/home/reid/src/dc3/models` as the design says gives hundreds of differences on base too. The plan's dc3 step needs to name this (should-fix S4).
- **Brief probes on the prototype**, real TEAx:
  - Nested named members at two levels (p1): `hall.rack_1` 25, `racks[0]` 20, hall 45. Correct.
  - Named member in a specializing definition (p2): 25. Correct.
  - Named member under a collection redefined to `[3]`, in a specializing definition (p3) or in the usage (p8): 35. Correct.
  - Sum read from outside the parent, `sum(rack.servers.power)` (p4): 25. Correct.
  - Named members declared in the definition, two instances (p7): 25, 25, hall 50, with no sibling leak between racks. Correct.
  - Usage shrinks a collection below its named members, `part :>> servers[1]` over two named members (p9): refused, `exceed_count`. Correct.
  - Inherited count with an attribute bound redefined in a subdefinition (p11, `Server[n]`, `n` 3, then 2): 25. Correct.
  - **Named member redefined in a usage (p10, p10b): 20.0, wrong (M1).**
  - **Non-sibling member of an inherited-count redefinition (p12, the lens's F1 shape): 20.0, wrong (M2).**
  - **Collection value through a specializing definition with a qualified subset (p5): 22.0, wrong (S1).**
  - Count-1 non-sibling inside a definition (p6b: `part psu : Server;` with `part sub { part main :> psu { :>> power = 15.0; } }`, `total = psu.power * 2`): 20.0, where KerML would give 30. Whether this model is well-formed is doubtful, because `main`'s featuring type does not specialize `psu`'s. (S5.)
  - `size(servers)`: refused today as an unsupported expression, so it cannot go wrong here.

Not checked: native SysIDE values for any probe; the slow test suite; the `snapshot` route; `resolve_address`'s shared-prefix narrowing when the reading expression sits inside a named member (a member is now also a candidate under the collection slot, so a read of the collection from inside `server_1` would narrow to `server_1`; this behaves the same as for indexed copies today, and I did not find a model that reads that way).

---

## Issues by Severity

### Critical (must fix before implementation)

- **M1. A redefined named member drops out of its collection, and the sum is silently wrong.** p10: `Rack { servers[2]; server_1 :> servers; }`, `rack : Rack { part :>> server_1 { :>> power = 15.0; } }` gives three servers and 20.0 (should be two and 25). p10b, the dc3 shape (`Site :> SiteLib { :>> racks[2]; rack_1 :> racks; rack_2 :> racks; }`, `site : Site { part :>> rack_1 { :>> cost = 15.0; } }`): 20.0, should be 25. Today's code is equally wrong here, so this is not a regression, but the item claims the double count is fixed, and this is the most likely next shape. Fix: key membership by the member's slot (the root of its redefinition chain) instead of its declaration, in the count and for `member_of_slot`. Tested in scratch: both give 25 and the design's other probes are unchanged. Add D-level text and a build case. — Dimensions 1, 3, 7
- **M2. D6 reads the owned multiplicity, so a non-sibling member of an inherited-count collection builds as an extra part.** p12: `rack : Rack { part :>> servers; }` and `Hall { part spare : Server :> rack::servers { ... } }` gives 20.0 (KerML 25). Restating `[2]` makes it refuse. Fix: D6 tests the effective multiplicity from D4 (`_effective_multiplicity`), and add a refusal case for this shape. — Dimensions 6, 7; product-lens F1 (BLOCK)

### Major (should fix)

- **S1. D7 trusts SysIDE's `usages`, which misses a collection value written in a specializing definition** (p5: 22.0, should be 24). Fix: decide D7 by ownership. Refuse when the collection's effective declaration among the siblings, or any declaration it redefines, directly owns a feature that is not a part usage. This still lets `outer_redefinition` through, since its collection body holds only `part :>> psu`. It removes the `except KeyError: continue` skip, and the prototype already has the helper. — Dimensions 6, 7
- **S2. `OccurrenceIndex.children()` returns a named member twice** (verified on s1). Fix: dedupe in `children()` or build it from the own-slot buckets only, add it to I3, and correct the Research Findings claim that only `children_for_slot` reads the buckets. — Dimension 3
- **S3. Surface the §7.6.3 premise conflict, and accept an explicit `[1]`.** SysML says an unadorned subsetting usage inherits the collection's multiplicity. Option A reads it as one member. Record that reading as a product interpretation in `modeling-assumptions.md`. Change D9 so that `[1]` is accepted (the spec-exact form) and other counts stay refused. If the owner wants the literal reading, that is a different item. — Dimension 7; capture-fidelity law 4
- **S4. Make the dc3 proof reproducible.** Regenerate from `git archive HEAD models` (or a named dc3 commit) with `--package-name dc3_baseline`, not from the live `/home/reid/src/dc3/models`, which has uncommitted edits today. — Proof
- **S5. D6's count-1 exemption contradicts D5.** A non-sibling member of a part with no count is built beside it. Today that is the `candidate-es-009` reuse shape, which reads correctly. But p6b shows a model that builds a number KerML disagrees with. Either state in D6 why this cannot give a wrong number on a valid model (for example, that such a subset is ill-formed when featuring types don't conform, and the `candidate-es-009` targets are package-level parts, whose default multiplicity is `0..*` per §7.6.3), or refuse when the member writes a value that its target also binds. — Dimensions 6, 7; product-lens F2

### Minor (consider)

- **N1. Fewer refusal reasons.** Three of the new reasons (nested, own multiplicity, several collections) are each "this named-member form is outside the occurrence model", with no different user action. One reason with a specific message would do, and it means fewer rows, cases and witnesses. The prototype already reuses `foreign_collection` for the several-collections and feature-chain cases, while the design lists a separate `collections_multiple`. Pick one and make the design and code agree.
- **N2. Define "sibling" once** (Dimension 8), by slot after M1.
- **N3.** The `usage_owner_bare_subset_def_owned` fixture edit weakens an existing fixture. Keep the original shape as the D7 refusal case, as planned, and say in the fixture's comment why the value was removed.
- **N4.** Regrade option A from `[OWNER]` to `[AGENT] (ratified by owner, 2026-10-26)` in the spec and design (capture-fidelity settled rule). No effect on the gate.

---

## Recommendations

1. Key membership by slot (M1) and test D6 against the effective multiplicity (M2). Add build/refusal cases for p10, p10b and p12 to Phase 2.
2. Replace D7's SysIDE-usage check with the ownership check (S1); add p5 as a refusal case.
3. Fix `children()` (S2), record the §7.6.3 interpretation, and accept `[1]` (S3).
4. Pin the dc3 step to committed models (S4). Settle S5 in D6's text or with a refusal.
5. Then the Phase 1 corpus rerun should still equal the current 10-root list. M1's change touched none of the corpus roots in my scratch run of the design's own probes, but I did not rerun the whole corpus with it.

---

## Product Lens (block for `product-lens.md`, not yet appended)

```
## design_review — 2026-10-26 — rev 90c01150 (named-subset-members), .project/active/named-subset-members/design.md
Point (re-derived): The generator reproduces the members and count the model states, read from parser evidence (KerML 7.3.4.4: a subsetting part's values are values of the collection). A read of the whole collection reaches every modeled member exactly once, each with its own values. Any shape it cannot derive exactly is refused by name; it never builds a confident wrong number. [source: .project/adr/0004 ([OWNER], active); .project/product/0003 and 0004 ([OWNER-VERBATIM]: "we follow what KerML, SysMLv2 and SysIDE support"); option A in spec.md:22, grade: owner/HARD]
Falsifier: A valid model whose collection has a named subset generates without refusal, and sum() over the collection differs from the KerML value, or the built members do not equal its count.
Findings:
- design_review-F1 [DON'T] D6 refuses a non-sibling named subset only if the collection states a multiplicity (owned); with D4 a redefinition without a count inherits one, so the member is built as an extra part left out of the sum. Reproduced: rack : Rack { part :>> servers; } plus Hall { part spare :> rack::servers { power = 15 } } gives total 20.0 (KerML 25). Fix: use the effective multiplicity; add a refusal case. — ADR 0004 [OWNER] / P-003, P-004 (owner/HARD) — disposition: BLOCK
- design_review-F2 [DON'T] D6 builds a count-1 non-sibling member beside its target, the second rule D5 rejects for siblings. Disposition wanted: show it cannot give a wrong number on a valid model, or refuse conflicting value writes. — P-003 applied by inference (AGENT) — disposition: DISPOSE-and-proceed
- design_review-F3 [DO] D7 relies on SysIDE's usages view; decide by ownership of the collection's redefinition family instead, or show the view is complete. — ADR 0004 obligation; remedy inferred (AGENT) — disposition: DISPOSE-and-proceed
- design_review-F4 [DO] Option A is [OWNER] in spec and design, but the record is the owner approving a recommendation: regrade to [AGENT] (ratified by owner, 2026-10-26). — capture-fidelity settled rule — disposition: DISPOSE-and-proceed
Smells: none fired.
Gate: BLOCKED (design_review-F1)
```

Reviewer additions to the lens: F3 is now reproduced (probe p5, 22.0 against KerML 24), and M1 (redefined named member) is a second silent wrong sum at the same grade as F1.

---

## Resolutions

(Filled in when the owner or orchestrator resolves each issue.)

---

**Overall:** Revise
**Next Steps:** Record resolutions here, then return to the design agent (or re-run `/_my_design`) pointing at this review. The reviewer does not edit the design. M1 and M2 need no owner input, because they bring the design in line with its own rule and ADR 0004. S3 is the one point to put to the owner: SysML's literal reading of an unadorned named subset differs from option A.
