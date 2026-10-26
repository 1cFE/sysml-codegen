# Design: Named subsets are members of the collection they subset

**Status:** Draft, round 2 (after `design-review.md`, verdict Revise; orchestrator decisions in `briefs/design-round2.md`)
**Owner:** Reid Westwood
**Created:** 2026-10-26
**Branch:** `named-subset-members` (round 1 at `396dab3d`, round 2 written at `a94e6a1d`; stacks on `repeated-rollup-collision`)
**Complexity:** MEDIUM

---

## Overview

When a part names some members of a collection (`part server_1 :> servers;` beside `servers : Server[2]`), the generator builds the declared number of parts, not more. The named parts fill places in the collection and only the rest are built as unnamed copies. A read of the whole collection (`sum(servers.power)`) reaches the named parts and the unnamed copies, each once. A redefinition that does not restate its count (`part :>> servers;`) takes the count of the part it redefines. Shapes the generator cannot count exactly are refused by name.

## Round 2 changes

- **M1:** membership is tracked by slot, so a redefined member (`part :>> server_1 { ... }`, dc3's `part :>> rack_1 { ... }`) stays in its collection. D1, D3.
- **M2 and S5:** every named member that is not a sibling of its collection is refused, whatever the collection's count. That also covers the inherited count (M2). D6.
- **S1:** the check for values the generator would not carry reads what the collection's own declarations own, not SysIDE's inherited list. D7.
- **S2:** `OccurrenceIndex.children()` returns each child once. D3, I3.
- **S3:** option A is graded `[AGENT] recommended, ratified by owner 2026-10-26` (here and in the spec). The reading "a named subset with no count is one member" is recorded as an interpretation. An explicit `[1]` is accepted. D9, D11.
- **S4:** the dc3 proof regenerates from dc3's committed model tree.
- **Minor:** four named-member reasons instead of six, each raised at one site; "sibling" defined once (Core Concept).

## Related Artifacts

- **Spec:** `.project/active/named-subset-members/spec.md` (the contract)
- **Design review:** `.project/active/named-subset-members/design-review.md` (Revise; M1, M2, S1 to S5, N1 to N4 addressed here)
- **Product lens:** `.project/active/named-subset-members/product-lens.md` (design_review block appended, gate DISPOSED)
- **Briefs:** `briefs/design.md`, `briefs/design-round2.md`
- **Investigation:** `.project/active/repeated-rollup-collision/evidence/double-count/report.md` (shapes s1 to s9)
- **Corpus check method:** `.project/active/repeated-rollup-collision/evidence/corpus-receipt.md`
- **Prototype and probes:** `evidence/prototype.patch` (round 2), `evidence/shapes/` (round 1 probes r1 to r11, s8), `evidence/review-shapes/` (the review's p1 to p13), `evidence/scripts/`
- **ADRs:** 0004 (derive occurrences from exact evidence or refuse), 0011, 0012, 0007 and 0019
- **Backlog:** `[NAMED-SUBSET-DOUBLE-COUNT]`, `[REDEFINITION-DROPS-COUNT]` (both closed by this item), `[MEMBERSHIP-LIST-IGNORED]` (not touched)
- **RG-1 note:** RG1-1 in `c381fb00:.project/active/subset-profile-conformance/rg1-recommendations.md` (this item answers it)

## The Point

[AGENT] recommended, ratified by owner 2026-10-26: option A, a named subset counts as one of the members of the collection it subsets, so the generator builds the declared number of parts and `sum()` includes the named ones. This serves the product promise that the generator rebuilds the math the model states, with each modeled member as exactly one concrete copy, or refuses by name, and never emits a confident wrong number (`[HARD]`, ADR 0004; product 0003 and 0004). Today `servers : Server[2]` with `server_1 :> servers` builds three servers, and `sum(servers.power)` adds the two unnamed copies, which hold defaults, and leaves out `server_1`. KerML 7.3.4.4 says the subsetting part's values are values of the collection (`driveWheels[2] subsets wheels[4]` is two of the four wheels).

## Research Findings

- **Occurrences are built in one place.** `build_occurrence_index` (`elaboration/occurrence.py:936-1087`) walks part usages from the roots, asks SysIDE for each occurrence's child declarations (`native_child_declarations`, `:961-997`), and expands each child into copies with `_multiplicity_indices` (`:840-933`). An occurrence's identity is its path of (slot, index) steps.
- **Slots follow redefinition only.** `build_feature_slot_index` (`:386-443`) roots each declaration at the end of its redefinition chain. Subsetting is read nowhere in `src/`. So `server_1 :> servers` has its own slot and is built as an extra child.
- **A redefinition of a member carries no subsetting of its own.** In `rack : Rack { part :>> server_1 { ... } }` the declaration the generator builds is `rack::server_1`, whose `owned_subsettings` holds no subset of `servers`. Its slot is `Rack::server_1`'s slot. Keying membership by declaration loses it (review M1); keying by slot keeps it.
- **The children buckets have three readers.** `OccurrenceIndex.__init__` (`:483-496`) fills two maps keyed by (parent, slot) and (package, slot). Readers: `children_for_slot` (`:549-552`, called only from `resolve_address`), `resolve_address` itself for package roots (`:611-615`), and `children()` (`:541-547`), which iterates the parent map and would return a member filed under two slots twice. `children()` is called only by `tests/unit/test_elaboration_occurrence.py:202`. Nothing outside `occurrence.py` reads the maps.
- **The count is the usage's own multiplicity.** `_multiplicity_indices` reads `usage.multiplicity` and returns one unindexed copy when there is none (`:848-850`); a redefinition without a count gets `None`.
- **SysIDE carries part features through subsetting; the generator does not carry attribute writes.** Nested parts of the collection reach named members through SysIDE's `usages` (`outer_redefinition`: `rack_1.server_1.psu` reads 0.95 today). Attribute writes owned by a collection declaration attach only to occurrences of that declaration (`_attachment`, `elaborate.py:828-856`; `occurrences_for_declaration`, `occurrence.py:507-526`). SysIDE's `usages` does not list every inherited write either (review p5: a write in a specializing definition's `part :>> servers { ... }` is missing from `server_1`'s list).
- **The type map has no `ReferenceSubsetting`.** The usage's own `owned_reference_subsetting` and `owned_cross_subsetting` identify those relationships without a type check.
- **SysML Part 1 §7.6.3** (`agentic-mbse/docs/sysmlv2/SysML_Spec_v2_Part1/full_document.md`, near line 3559): a usage with no declared multiplicity inherits the multiplicity of the usages it subsets or redefines. That supports D4. Read literally, it also gives `server_1 :> servers` the count of `servers`, which conflicts with option A (D11).
- **Corpus shapes** (`evidence/scripts/scan_subsets.py`, all fixture roots and dc3): all 28 dc3 named subsets and every `candidate-es-008` named subset are siblings of their collection. Non-sibling subsets appear only in the four `candidate-es-009` cases (a part in a definition subsets a package-level part).

## Core Concept

A collection's members are its named subsets plus as many unnamed copies as its count leaves over.

- **Who is a named member.** A part usage that subsets another user part usage. The parser's subsetting relation is read once while occurrences are built and recorded by slot: the member's slot maps to the collection's slot. A redefinition of the member shares the member's slot, so it stays a member.
- **Siblings.** A named member and its collection are siblings when both slots are among the child declarations of the same occurrence, or among the roots of the same package. Only siblings are supported.
- **Counting.** When an occurrence's children are expanded, the generator counts the sibling named members for each collection slot and builds only the remaining copies, numbered from zero.
- **Reading.** Each named member keeps its own name and identity and is also filed under the collection's slot. A read of the collection returns the unnamed copies and the named members together. A read of the member by its own name returns only it.
- **Count source.** The usage's own multiplicity, or, when a redefinition states none, the multiplicity of the part it redefines, with that part's `ordered` and `nonunique` flags.
- **Refusals.** Where membership cannot be settled exactly, refuse by name: more named members than the count; a named member whose own form is unsupported (a count other than 1, a subset of a named member, two collections); a named member that is not a sibling; a collection with named members whose own declarations own non-part features.

This changes the two places that are wrong and nothing else. The count is decided where copies are built, and collection lookup is answered in the index every containment read uses. No read path learns a second rule, and names play no part.

## Key Bets

- **B1. Sibling subsetting is how real models name collection members.** All 28 dc3 named subsets and every `candidate-es-008` named subset are siblings. *If false → models that name members of a collection owned elsewhere are refused (D6), and the product limit is hit often.*
- **B2. A member's slot is exact evidence of membership.** The subsetting relation on the declaration that writes it names the collection, and every redefinition of that declaration shares its slot. *If false → a redefined member falls out of its collection, as in review M1.*
- **B3. Native part inheritance through subsetting is correct.** Nested parts of the collection reach named members through SysIDE's `usages`. *If false → per-copy part values on named members are wrong, as today; D7 refuses the attribute case.*
- **B4. A redefinition without a count has the count it redefines** (SysML §7.6.3; KerML 7.3.4.5, K:1657, K:1673). *If false → the count fix builds copies the model does not state.*
- **B5. Modelers mean one member when they write a named subset without a count** (D11). *If false → the generator builds one part where the modeler meant several, and the owner should take the literal SysML reading as a separate item.*

## Key Decisions

- **D1. Read membership once in `build_occurrence_index`, from `owned_subsettings`, keyed by slot.** For each user part usage, take its subsetting relationships, drop redefinitions and the usage's own reference and cross subsettings (by identity), and keep targets that are user part usages. Record member slot → collection slot. Two declarations in one member slot that name different collections are refused (D8). *Rejected: keying by declaration (review M1: `part :>> server_1` loses membership); reading it in `build_feature_slot_index` (holds library endpoints and no notion of user part usages); adding `ReferenceSubsetting` to agentic-mbse's type map (cross-repo, and the usage's own property answers it).*
- **D2. Unnamed copies are numbered `0 .. n−k−1`.** Named members get no index. The number claims nothing about which member is "first" (ADR 0004). *Rejected: indices `k .. n−1` (implies the named ones took the first places); indexing named members (order-based).*
- **D3. Named members are filed under the collection slot; `children()` reads own-slot children only.** `ExactOccurrence` gains `member_of_slot`. `OccurrenceIndex.__init__` files a member under its own slot and the collection slot in both bucket maps, and keeps a third map of each parent's children under their own slot for `children()`. `children_for_slot` and `resolve_address` keep their code. *Rejected: a membership check inside `resolve_address` (a second rule for one lookup); deduplicating inside `children()` (hides the double filing instead of keeping the maps separate).*
- **D4. The count fix is taken.** A part usage with no multiplicity takes the multiplicity of the nearest declaration it redefines that states one, and `ordered` and `nonunique` are read through the same chain (KerML K:1643, K:1673). Two redefined parts with different counts and none stated is refused `SI_MULTIPLICITY_UNRESOLVED`. It closes `[REDEFINITION-DROPS-COUNT]` and answers RG1-1 by inheriting the count. *Rejected: refusing the two `candidate-es-008` shapes (valid models; the fix is small and measured); inheriting the count but not the flags (expands an ordered collection into indexed copies, which the ordered refusal exists to stop).*
- **D5. One rule for every count, including count 1.** A part with no multiplicity anywhere is one part, and a sibling that subsets it is that one part: `comp_b :> comp_a` builds only `comp_b`. *Rejected: treating only collections with a stated count as collections (a second rule).*
- **D6. Every named member that is not a sibling is refused, and so is any subsetting through a feature chain.** The generator cannot place a part into a collection that belongs to another parent, so building it would leave an extra copy outside that collection's count and sums. This covers the inherited-count case (review M2, p12) and the count-1 case (review S5, p6, p6b) with one rule and no multiplicity test. *Rejected: refusing only when the collection states a multiplicity (round 1; misses inherited counts and count 1); building it as today (an extra copy, wrong sums).* Cost: the four `candidate-es-009` cases change. Two that generated (`typed_subsetting`, `nested_untyped_subsetting`) are refused; two that were refused `SI_OCCURRENCE_MISSING` (`composition_by_subsetting`, `..._root_part_usage`) are refused earlier with this reason, so the elaborate site they witness (`elaborate.py::_ExactElaborator._resolve_semantic_reference::coded::SI_OCCURRENCE_MISSING::4`) needs another witness case.
- **D7. Refuse a collection with named members whose own declarations own a non-part feature.** Look at the collection's declaration among the siblings and every declaration it redefines; if any directly owns a feature that is not a part usage, refuse. Example r11: `servers : Server[2] { :>> power = 12.0; }` with `server_1 :> servers` would sum 22 (KerML 24). Example p5: the write sits in a specializing definition's `part :>> servers { ... }`. Nested part writes pass, because they already reach members (`outer_redefinition`). *Rejected: checking SysIDE's inherited `usages` (round 1; misses p5, and skipped evidence it could not classify); carrying attribute writes to members (the spec's open inheritance non-goal).*
- **D8. Four named-member reasons plus one for D4, each raised at one site.** `occurrence_named_members_exceed_count` (`SI_MULTIPLICITY_INVALID`); `occurrence_named_member_form` (`SI_MULTIPLICITY_UNSUPPORTED`: a count other than 1, a subset of a named member, two collections); `occurrence_named_member_not_sibling` (`SI_MULTIPLICITY_UNSUPPORTED`); `occurrence_named_member_collection_owns_features` (`SI_MULTIPLICITY_UNSUPPORTED`); `occurrence_multiplicity_inherited_ambiguous` (`SI_MULTIPLICITY_UNRESOLVED`). A reason covers one thing the user does about it, and each reason's conditions are gathered and raised from one site, so the site account gets one row per reason. *Rejected: one reason per condition (more sites, same advice); new codes (the existing codes' advice fits).*
- **D9. A named member that states `[1]` is accepted; any other count is refused.** `[1]` is the form whose SysML meaning is exactly one member. The bound is evaluated with the existing `_modeled_integer_bound`, and the member is built unindexed either way, so writing `[1]` does not change identities. *Rejected: refusing every stated count (round 1; refuses the spec-exact form).*
- **D10. Package-level roots use the same rule.** Roots are grouped by owning package and counted like children (r7: `servers[0]` and `server_1`).
- **D11. Interpretation: a named subset with no count is one member.** This matches modeler intent and dc3's 28 uses. A literal reading of SysML Part 1 §7.6.3 gives an unadorned subsetting usage the collection's count, which would make `server_1` all of `servers`. The generator takes the one-member reading and records it as a product interpretation in `docs/architecture/modeling-assumptions.md`. *Rejected: the literal reading (it makes every dc3 named member the whole collection). If the owner wants it, that is a separate item.*

## Architecture

The change is inside `elaboration/occurrence.py`. Nothing downstream changes code, because everything reads occurrences through `OccurrenceIndex`.

1. **Read (once).** `build_occurrence_index` builds `member slot → collection slot` from `owned_subsettings` (D1) and notes members reached through a feature chain. It refuses here the forms that need no parent: two collections, a subset of a named member (D8 `form`).
2. **Count (per parent).** Before expanding an occurrence's children, `named_member_counts` maps each sibling slot to its declaration. For each member slot among them: if its collection slot is not among them, or it came through a chain, refuse (D6). Otherwise count it. Then each collection with members is checked for owned non-part features (D7). Roots are grouped by package and counted the same way (D10).
3. **Expand.** `add_usage` passes the collection's count `k`, and for a member the fact that it is one, to `_multiplicity_indices`. A collection builds `range(n − k)` copies, or none for a single part with one member, and `k > n` is refused. A member builds one unindexed occurrence, after checking any stated count is 1 (D9). Multiplicity, its owner and the flags come through the redefinition chain (D4).
4. **Index.** Each member's `ExactOccurrence.member_of_slot` is the collection slot. `OccurrenceIndex.__init__` files it under both slots in the bucket maps and under its own slot only in the `children()` map (D3).
5. **Read paths.** `resolve_address` is unchanged; a step on `servers` now yields `servers[0]` and `server_1`.

## Required Invariants

- **I1.** For each parent and collection slot, unnamed copies plus sibling named members equal the collection's count, or the model is refused.
- **I2.** A named member's identity and display path do not change (`rack__server_1`), including when it states `[1]` or is redefined.
- **I3.** `children_for_slot(parent, collection slot)` returns each member once; `children_for_slot(parent, member slot)` returns only the member; `children(parent)` returns each child once.
- **I4.** No choice depends on declaration order, name or UUID order (ADR 0004).
- **I5.** A model with no subsetting between user part usages and no redefinition that omits a count builds byte-identical output.
- **I6.** dc3 regenerated from its committed model tree is byte-identical to its committed baseline.

## Component Overview

- **`elaboration/occurrence.py`.** Membership read by slot, sibling count, reduced expansion, member expansion, inherited multiplicity and flags, the collection-slot filing and own-slot children map in `OccurrenceIndex`, and the new refusal sites. `ExactOccurrence` gains `member_of_slot`.
- **`elaboration/diagnostics.py`.** The five new `SiteReason` members in D8.
- **Refusal cases.** One per new reason, plus a new witness for the elaborate site D6 takes over, per the repo's refusal-site practice (`tests/expectations/refusal_cases/`).
- **Docs.** `docs/architecture/modeling-assumptions.md`: the named-member rule, D11's interpretation, the refusals as product limits; the G1 line (`:723`) replaced by "a redefinition takes the count and ordering it redefines".

## Non-Goals

- Carrying a collection's own attribute writes to its named members (refused by D7; filed as a backlog row).
- Placing a part into a collection owned by another parent (refused by D6; filed as a backlog row).
- `[MEMBERSHIP-LIST-IGNORED]` (`part :>> servers = (server_1, server_2);`).
- Treating named parts as the only members of a `[*]` collection: s3 stays refused `SI_MULTIPLICITY_UNRESOLVED`.
- Counting a named member with a count above 1 as several members (D9).
- The literal SysML reading of an unadorned named subset (D11).

## Implementation Notes

- `evidence/prototype.patch` (round 2, over `5593e44e`) passes every number below. It has no environment switch, no dynamic `getattr` and no first-match selection, and `tests/unit/test_elaboration_import_boundaries.py` passes on it. `tests/conformance/test_expression_evidence_ownership.py::test_discovered_raw_selectors_equal_the_reviewed_manifest` still needs reviewed manifest rows for the new raw selector reads (`owned_subsettings`, `subsetted_feature`, `owned_reference_subsetting`, `owned_cross_subsetting`, `chaining_features`, `owned_features`, `is_ordered`, `is_nonunique` where the scan reports them).
- In the prototype the `form` reason is raised from three places and `exceed_count` from two. D8 asks for one site per reason: gather the condition, then raise once.
- Take the inherited multiplicity's bound with the declaration that states it as `multiplicity_owner` in `_modeled_integer_bound`, so `Server[n]` resolves against the definition that owns `n` (review p11 gives 25).
- `usage_owner_bare_subset_def_owned` now refuses by D7. Its guard test (`tests/conformance/test_usage_owned_reference_anchoring.py:468-477`) is about reference anchoring, not values. Keep the guard by dropping comp_a's `{ :>> length = 3.0; }` from the fixture, with a comment saying why, and move the original shape into the D7 refusal case. The committed package gave `comp_b.length` 1.0 (`doubled` 2.0) where KerML gives 3.0 (6.0), so refusing it is a correction.
- The `candidate-es-009` stored answers, classes and refusal-before-first-write expectations for those four cases move to `occurrence_named_member_not_sibling`. Find a new witness case for `_resolve_semantic_reference ... SI_OCCURRENCE_MISSING::4` (an address target missing without subsetting) before re-capturing, so `test_generator_mutations.py` keeps a case for that site.

## Potential Risks

- **The `candidate-es-009` reuse shape is now refused.** `part def Site { part facility :> ac_facility; }` with `part ac_facility` at package level generated and read `facility.area` correctly. It now refuses, because it builds an extra `Fac` part outside `ac_facility`'s population. A modeler writing this shape loses a package that read correctly. dc3's committed tree has no such shape. This is the cost of the "no extra copy" rule (brief item 7); the alternative, placing members across parents, is out of scope.
- **Ordered redefinitions now refuse.** `g1__redefinition_drops_ordered_bounds` moves from generated (one copy, ordering dropped) to refused (`occurrence_multiplicity_ordered`).
- **D11 is an interpretation.** If a modeler means the literal SysML reading, the generator builds one part. Recorded in modeling assumptions.
- **Attribute inheritance stays unsupported.** D7 refuses it by ownership, so it fails closed.

## Integration Strategy

The change is internal to occurrence building. The public package oracle and dc3 stay byte-identical. The agentic-mbse guidance warning (`skills/sysml-conventions/SKILL.md:153`, `docs/patterns/adr002-calculations.md:301`, `project_templates/MODELING_GUIDE.md.template:130`) becomes false when this lands; the orchestrator owns that change. What it should then say:

- `sum()` over a collection with named members works: `part racks : Rack[2]; part rack_1 :> racks; part rack_2 :> racks;` makes `sum(racks.capital_cost)` add `rack_1` and `rack_2`, each once, and any unnamed copies left over. Redefining a member elsewhere (`part :>> rack_1 { ... }`) keeps it in the collection.
- Name at most as many members as the count. A named member takes no count, or `[1]`. Don't subset a named member. Declare named members beside the collection, in the same part or definition, not from another part or package.
- Set values on each named member, not in the collection's own body (`racks : Rack[2] { :>> cost = 1.0; }` with named members is refused, including when the body is in a specializing definition).
- A redefinition that omits its count keeps the inherited one (`part :>> racks;` over `Rack[2]` is two racks).
- Drop the "declare them as plain parts and add them" workaround.

## Validation Approach

Measured on the round-2 prototype (`evidence/prototype.patch` over `5593e44e`), scripts in `evidence/scripts/`:

- **Real TEAx sums** (`run_pkg.py`, `PYTHONPATH=src:/home/reid/src/teax/packages/teax-simkit /home/reid/src/dc3/.venv/bin/python`): s1 25.0, s2 35.0, s4 35.0, s8 30.0.
- **Review probes, real TEAx:** p10 (member redefined in the usage) 25.0, p10b (dc3 shape, `part :>> rack_1`) 25.0, p1 `hall.rack_1` 25 / `racks[0]` 20 / hall 45, p2 25, p3 35, p4 25, p7 25 / 25 / 50, p8 35, p11 25. Refused: p12, p6 and p6b `not_sibling`; p5 and p5b `collection_owns_features`; p9 `exceed_count`; p13 unchanged (`size()` unsupported).
- **Round-1 probes:** r3b (`a : Server[1] :> servers`) now builds `rack.a` and `servers[0]`, total 20.0; r7 25.0; r1, r5 `exceed_count`; r2, r3 `form`; r4, r4b `not_sibling`; r9, r11 `collection_owns_features`; r8 `SI_MULTIPLICITY_UNRESOLVED`; s3 unchanged.
- **PSU fixtures**, each 4 PSUs, `fx_params.json` byte-identical to round 1: `plain_nesting` all 0.9; `one_subset_redefines` `rack_1.server_1` 0.95, others 0.9; `nested_named_subset` all 0.95; `..._single_rack` 0.95, 0.85, `racks[0].servers[0..1]` 0.9; `outer_redefinition` `rack_1.server_{1,2}` 0.95, `rack_2.server_{1,2}` 0.9; `sibling_subsets_redefine` `rack_1.servers[0..1]` 0.95, `rack_2.servers[0..1]` 0.85. Round 1 ran these in real TEAx (`t.r = 2 × efficiency`).
- **dc3:** regenerated from `git -C /home/reid/src/dc3 archive HEAD models` (dc3 `8a98af8`) with `--package-name dc3_baseline` and the `SYSIDE_LICENSE_KEY` from `/home/reid/src/dc3/.env`, on base and prototype; both `diff -rq` identical to `exploration/ac_dc_baseline/dc3_baseline/`.
- **Whole corpus:** all fixture roots plus the two extra roots, both classes, base and prototype (`corpus_all.py`), `diff -rq`. Fourteen roots differ, all expected:
  - the six `candidate-es-008` cases: 12 (three cases), 11, 8 or 6 PSUs become 4;
  - `part-multiplicity__redefinition_drops_bounds__expanded_part_usage`: one `servers` copy becomes `servers[0..1]` (D4);
  - `g1__redefinition_drops_ordered_bounds`: generated becomes refused, ordered (D4);
  - `occurrence_seed/f1_inherited_ordered_redef`: refused `NOTHING_TO_GENERATE` becomes refused, ordered (D4);
  - `usage_owner_bare_subset_def_owned`: generated becomes refused, `collection_owns_features` (D7);
  - the four `candidate-es-009` cases: `typed_subsetting` and `nested_untyped_subsetting` generated become refused, `composition_by_subsetting` and `..._root_part_usage` change reason from `SI_OCCURRENCE_MISSING` to `not_sibling` (D6).
  - Every other root is byte-identical. M1's slot keying changed no corpus root.
- **Full suite** (default run, slow tests deselected), base and prototype scratch copies side by side: see Appendix A.

Not checked: native SysIDE values for the probes; slow tests; the `snapshot` route beyond the suite; models outside the fixture corpus and dc3; `resolve_address`'s shared-prefix narrowing when a collection is read from inside a named member (it narrows to that member, as it does for indexed copies today).

## Next-Stage Handoff

- **Fixed:** D1 to D11, the expected-change list above, dc3 byte-identity from the committed tree.
- **Open:** refusal message wording; the replacement witness case for the elaborate site in D6.
- **De-risk first:** Phase 1 with the corpus rerun; confirm the fourteen-root list before touching stored answers.

## Plan

### Phase 1: Membership and count in `occurrence.py`

- [x] Read membership once by slot in `build_occurrence_index` (D1); `ExactOccurrence.member_of_slot`; collection-slot filing and the own-slot `children()` map in `OccurrenceIndex` (D3). Note: `_read_named_membership` and `_subsetted_part_usages` in `occurrence.py`; `member_of_slot` is a required field (one constructor).
- [x] Sibling count per parent and per package; reduced collection expansion and member expansion in `_multiplicity_indices` (D2, D5, D9, D10). Note: `_multiplicity_indices` keeps its job (the copies a multiplicity builds) and its name, so the six existing site IDs stay; `_sibling_members` settles one sibling group, then `_named_member_indices` and `_unnamed_indices` adjust the indices in `add_usage`.
- [x] Inherited multiplicity and flags through the redefinition chain (D4). Note: `_stated_multiplicity`, `_is_ordered`, `_is_nonunique` over `_redefined_declarations`.
- [x] The refusals of D6, D7 and D8, one site per reason. Note: five construction sites, one per reason; the `form` reason is raised from the one helper `_refuse_named_member_form` (three conditions call it).
- [x] Keep the guards green: no first-match selection, literal selectors, manifest rows for the new raw reads. Note: the only reviewed selector read is `chaining_features`; it moved into the shared `_chain_endpoint`, which `build_feature_slot_index` now calls too, so the manifest row moved from `build_feature_slot_index` to `_chain_endpoint` (no second row).
- [x] Rerun `evidence/scripts/corpus_all.py` on base and branch; the diff must equal the fourteen-root list. Rerun dc3 from its committed tree; byte-identical. Note: exactly the fourteen roots, each with the expected outcome and reason (`evidence/corpus-receipt.md`). dc3 is identical on base and branch; see the receipt for the dc3 commit question.

### Phase 2: Pins and tests

- [x] Re-capture the six `candidate-es-008` stored answers with `attr_value` seams at 4 PSUs and the values above. Note: each answer pins every `efficiency` declaration that has nodes, plus `fx::Psu::efficiency` (an empty list where no PSU keeps the default), four nodes in each case.
- [x] Update `part-multiplicity__redefinition_drops_bounds__expanded_part_usage` (occurrences seam to two copies; remove its RG1-1 `loss` block) and `g1__redefinition_drops_ordered_bounds` (now refused; remove its `loss` block); update `fixture_classes.json` for g1 and `f1_inherited_ordered_redef`. Note: g1 is a case, so its class comes from its answer; its construct lines are now 5-6, since the ordered refusal points at the inherited `ordered` on line 5. `test_silent_loss_seams.py` no longer lists the closed `g1-redefinition-drops-bounds` family.
- [x] Add a witness case for `_resolve_semantic_reference ... SI_OCCURRENCE_MISSING::4`, then re-capture the four `candidate-es-009` cases with their classes and refusal-before-first-write expectations. Deviation: no new case was needed. `candidate-es-002__calc_input_through_part__attribute_value` already witnesses that site without subsetting (it was in the site's mutation set); its row's evidence and `mutations.json` now cite only it. The four cases witness `_sibling_members ... ::1`; `refusal_records.json` re-recorded (`scripts/refusal_records.py record`, 181 entries).
- [x] Edit `usage_owner_bare_subset_def_owned` as in Implementation Notes; confirm its anchoring tests pass. Note: 50 passed in `test_usage_owned_reference_anchoring.py`.
- [x] One refusal case per new reason (start from p12, p5, r1, r2 and the original `usage_owner_bare_subset_def_owned`), with stored answers, site-account rows and mutation witnesses. Note: seven cases, `named-member__{exceeds_count,subset_of_named_member,stated_count,not_sibling,collection_owns_features,collection_owns_features..specializing_def}__part_usage` and `part-multiplicity__inherited_ambiguous__expanded_part_usage`; five `site_account.csv` rows (explicit follow-up, public capability, each with its product limit as the coverage limitation); mutation sets measured by neutralizing each site. The 36 existing `occurrence.py` rows got their line and first evidence pointer refreshed.
- [x] Build cases for p10 and p10b (a redefined member stays a member) and r3b (`[1]` accepted). Note: `named-member__redefined_member__part_usage`, `…__specializing_def`, `named-member__stated_count_one__part_usage`, with `occurrences` seams.
- [x] A real-TEAx value test for s1, s2, s4, p10 and p10b (25, 35, 35, 25, 25), on `test_sibling_override_leak.py`'s pattern. Note: `tests/execution/test_named_subset_members_teax.py`, on `test_repeated_rollup_teax.py`'s harness (the leak test reads inputs only), plus the package-level r7 shape (25). Fixtures `tests/fixtures/named_subset_members/{one_named,two_named,specializing_def,package_roots}`; p10 and p10b reuse their refusal-case fixtures. On the base tree all six give 20.0.
- [x] Unit tests for I3 and for D2 labels, extending `tests/unit/test_elaboration_occurrence.py:202`.
- [x] Full suite green, including slow tests. Note: default run 9 failed (the known `test_check_ledger_4a.py` ×8 and one `test_study_cli.py`), 8865 passed. This repo has no `slow` marker; the deselected tests are the execution lane, run with dc3's venv and `--noconftest`: 116 passed, 29 errors, all 29 the `execution_provenance` fixture that `--noconftest` drops (base: 110 passed, the same 29).

### Phase 3: Docs and backlog

- [ ] `docs/architecture/modeling-assumptions.md`: the named-member rule; D11's interpretation; the refusals as product limits (subset of a named member, count other than 1, not a sibling, collection owns features, more named than the count); replace the G1 line.
- [ ] Backlog: close `[NAMED-SUBSET-DOUBLE-COUNT]` and `[REDEFINITION-DROPS-COUNT]`; file rows for carrying a collection's attribute writes to named members (D7) and for placing members into a collection owned by another parent (D6).
- [ ] Record this item's corpus receipt in `evidence/corpus-receipt.md`.
- [ ] Hand the agentic-mbse guidance list (Integration Strategy) to the orchestrator.

## Appendix A: Prototype full-suite run

Default run (`pytest tests/`, slow tests deselected) on scratch copies of `5593e44e`, base and round-2 prototype. The copies are not git work trees, so 59 tests fail on both for that reason (study tools, ledger checks); they are not counted. Every added failure is an expected update:

- Stored answers and classes for the fourteen corpus roots above: the `candidate-es-008` `attr_value` seams, the two `occurrences` seams, g1 across the refusal-case tests and snapshot replay, the live classes of g1, `f1_inherited_ordered_redef`, `usage_owner_bare_subset_def_owned` and the four `candidate-es-009` cases, and the refusal-before-first-write expectations for the two refused `candidate-es-009` cases.
- `test_generator_mutations.py` for the elaborate site whose only witnesses were the two refused `candidate-es-009` cases (D6), and `test_witnesses.py` for those two cases.
- `usage_owner_bare_subset_def_owned`'s three anchoring tests.
- Site bookkeeping: `test_site_account.py`, `test_site_reasons.py` (new sites need rows).
- `test_expression_evidence_ownership.py`, manifest rows for the new raw reads.

`test_elaboration_import_boundaries.py` and the dynamic-`getattr` test pass. Slow tests were not run.

---

**Next Steps:** after approval, `/_my_implement` from the Plan above.
