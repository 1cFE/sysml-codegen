# Design: Named subsets are members of the collection they subset

**Status:** Draft
**Owner:** Reid Westwood
**Created:** 2026-10-26
**Branch:** `named-subset-members` (design written at `5593e44e`; stacks on `repeated-rollup-collision`)
**Complexity:** MEDIUM

---

## Overview

When a part names some members of a collection (`part server_1 :> servers;` beside `servers : Server[2]`), the generator builds the declared number of parts, not more: the named parts fill places in the collection and only the rest are built as unnamed copies. A read of the whole collection (`sum(servers.power)`) reaches the named parts and the unnamed copies, each once. A redefinition that does not restate its count (`part :>> servers;`) takes the count of the part it redefines. Shapes the generator cannot count exactly are refused by name.

## Related Artifacts

- **Spec:** `.project/active/named-subset-members/spec.md` (the contract)
- **Product lens:** `.project/active/named-subset-members/product-lens.md`
- **Brief:** `.project/active/named-subset-members/briefs/design.md`
- **Investigation:** `.project/active/repeated-rollup-collision/evidence/double-count/report.md` (shapes s1 to s9)
- **Corpus check method:** `.project/active/repeated-rollup-collision/evidence/corpus-receipt.md`
- **Prototype and probes (this design):** `evidence/prototype.patch`, `evidence/shapes/`, `evidence/scripts/`
- **ADRs:** 0004 (derive occurrences from exact evidence or refuse), 0011 (parser declarations, concrete occurrences), 0012 (one acquisition owner for semantic evidence), 0007 and 0019 (agentic-mbse owns neutral SysML facts and keeps no second occurrence reader)
- **Backlog:** `[NAMED-SUBSET-DOUBLE-COUNT]`, `[REDEFINITION-DROPS-COUNT]` (both closed by this item), `[MEMBERSHIP-LIST-IGNORED]` (not touched)
- **RG-1 note:** RG1-1 in `c381fb00:.project/active/subset-profile-conformance/rg1-recommendations.md` (redefinition drops the count; this item answers it)

## The Point

[OWNER] 2026-10-26, option A: a named subset counts as one of the members of the collection it subsets, so the generator builds the declared number of parts and `sum()` includes the named ones. This serves the product promise that the generator rebuilds the math the model states, with each modeled member as exactly one concrete copy, or refuses by name, and never emits a confident wrong number (`[HARD]`, ADR 0004; product 0003 and 0004). Today `servers : Server[2]` with `server_1 :> servers` builds three servers, and `sum(servers.power)` adds the two unnamed copies, which hold defaults, and leaves out `server_1`. KerML 7.3.4.4 says the subsetting part's values are values of the collection (`driveWheels[2] subsets wheels[4]` is two of the four wheels).

## Research Findings

- **Occurrences are built in one place.** `build_occurrence_index` (`elaboration/occurrence.py:936-1087`) walks part usages from the roots, asks SysIDE for each occurrence's child declarations (`native_child_declarations`, `:961-997`), and expands each child into copies with `_multiplicity_indices` (`:840-933`). An occurrence's identity is its path of (slot, index) steps (`OccurrenceStep`, `identity.py`).
- **Slots follow redefinition only.** `build_feature_slot_index` (`:386-443`) roots each declaration at the end of its `owned_redefinitions` chain. Subsetting is read nowhere in `src/` (grep for `subsett` finds nothing). So `server_1 :> servers` has its own slot and is built as an extra child.
- **Collection lookup goes through one method.** Every containment read resolves step by step through `OccurrenceIndex.resolve_address` (`:582-650`), which reads children with `children_for_slot` (`:549-552`). Its three callers are in `elaborate.py:2429`, `:2526` and `:2556`. `children_for_slot` has no other caller. So adding named members to the collection's bucket reaches every read, and only reads.
- **The count is the usage's own multiplicity.** `_multiplicity_indices` reads `usage.multiplicity` and returns one unindexed copy when there is none (`:848-850`). SysIDE's `multiplicity` is the owned one; a redefinition without a count gets `None` (checked on s8).
- **SysIDE already carries part features through subsetting.** `server_1.usages` lists the nested parts of the collection it subsets. In `candidate-es-008__outer_redefinition__part_usage`, `rack_1.server_1.psu` already reads 0.95 from `rack_1`'s `part :>> servers { part :>> psu { ... } }` today. Attribute writes on the collection are listed in `usages` too (`Rack::servers::power` in shape r11), but the generator attaches attribute values by their owner's occurrences (`_attachment`, `elaborate.py:828-856` via `occurrences_for_declaration`, `occurrence.py:507-526`), so a named subset never receives them. This is the open inheritance question the spec leaves out; it matters here because the fix puts named subsets into sums.
- **The type map has no `ReferenceSubsetting`.** `SysideAdapter.is_instance` refuses unknown type names, and agentic-mbse's map (`agentic_mbse/sysml/syside_adapter.py`) lists `Subsetting` and `Redefinition` only. The usage's own `owned_reference_subsetting` and `owned_cross_subsetting` properties identify those relationships without a type check.
- **Corpus shapes** (scan over all 457 fixture roots and dc3, `evidence/scripts/scan_subsets.py`): every named subset in dc3 (28) and in the `candidate-es-008` cases is a sibling of its collection. Other shapes: `usage_owner_bare_subset_def_owned` (a count-1 sibling, `comp_b :> comp_a`), four `candidate-es-009` cases (a part in a definition subsets a package-level part, not a sibling), `f1_effective_declaration_slot`, and two refused multiplicity cases.
- **ADR 0004** forbids choosing by order, so named parts cannot be given index positions. ADR 0012 and 0019 keep occurrence reading in sysml-codegen; nothing here moves to agentic-mbse.

## Core Concept

A collection's members are its named subsets plus as many unnamed copies as its count leaves over. The generator learns which parts are named members from the parser's subsetting relation, read once while occurrences are built: a part usage that subsets another user part usage is a named member of that part's slot. When an occurrence's children are expanded, the generator counts the named members among the siblings for each collection slot and builds only the remaining copies, numbered from zero. Each named member keeps its own name and identity, and it is also filed under the collection's slot, so a read of the collection returns the unnamed copies and the named members together, and a read of the named member by its own name still returns only it.

The count comes from the model: the usage's own multiplicity, or, when a redefinition states none, the multiplicity of the part it redefines (with that part's `ordered` and `nonunique` flags). Where membership cannot be settled exactly, the generator refuses by name: more named members than the count, a named member of a named member, a named member with its own count, a named member of a collection that is not its sibling, and a named member that SysIDE shows inheriting a non-part feature from its collection.

This is the right approach because it changes the two places that are wrong and nothing else. The count is decided where copies are built, and collection lookup is answered where every containment read already goes. No read path learns a second rule, and names play no part.

## Key Bets

- **B1. Sibling subsetting is how real models name collection members.** All 28 dc3 named subsets and every `candidate-es-008` named subset sit beside their collection under the same parent. *If false → models that name members of a collection owned elsewhere are refused (D6), and the product limit is hit often.*
- **B2. SysIDE's subsetting relation is exact evidence of membership.** `owned_subsettings` names the declaration subsetted, and its slot is the collection's slot whether the target is the definition's declaration (`Rack::servers`) or a redefinition in the usage (`rack_1::servers`). *If false → named members land in the wrong collection or none, and counts are wrong.*
- **B3. Native part inheritance through subsetting is correct and stays correct.** Nested parts of the collection reach named members through SysIDE's `usages`, and the generator already builds them. *If false → per-copy part values on named members are wrong, as they are today; this design does not make it worse, and D7 refuses the attribute case.*
- **B4. KerML gives a redefinition without a count the count it redefines** (KerML 7.3.4.5, K:1657, K:1673; RG1-1's semantics check). *If false → the count fix builds copies the model does not state.*

## Key Decisions

- **D1. Read membership once in `build_occurrence_index`, from `owned_subsettings`.** For each user part usage, take its subsetting relationships, drop redefinitions (`is_instance(..., "Redefinition")`) and the usage's own `owned_reference_subsetting` and `owned_cross_subsetting` (by identity), and keep targets that are user part usages (`usages_by_id`). Library targets such as the implicit `Parts::parts` fall out by that filter. *Rejected: reading it in `build_feature_slot_index` (the slot index holds library endpoints too and has no notion of user part usages); adding `ReferenceSubsetting` to agentic-mbse's type map (a cross-repo change for a check the usage's own property already answers).*
- **D2. Unnamed copies are numbered `0 .. n−k−1`.** In s1 the unnamed copy is `servers[0]`. Named members get no index. The number carries no claim about which member is "first", so no order is chosen (ADR 0004). *Rejected: keeping indices `k .. n−1` (implies the named ones took the first places); giving named members indices (order-based, ruled out by the spec).*
- **D3. Named members are filed under the collection slot in the children index.** `ExactOccurrence` gets `member_of_slot`, set only for sibling members, and `OccurrenceIndex.__init__` (`:483-496`) adds such an occurrence to the bucket for (parent, collection slot) as well as its own. `children_for_slot` and `resolve_address` are unchanged in code. *Rejected: a membership check inside `resolve_address` (a second rule for one lookup); a separate "members" method (every caller would need to choose).*
- **D4. The count fix is taken.** A part usage with no multiplicity takes the multiplicity of the nearest declaration it redefines that states one, and `ordered` and `nonunique` are read through the same chain (KerML K:1643 and K:1673 say a redefinition of an ordered feature must be ordered). Measured on the whole corpus (Validation Approach): every change is a correction. It closes `[REDEFINITION-DROPS-COUNT]` and answers RG1-1 by inheriting the count. *Rejected: refusing the two `candidate-es-008` shapes by name (both are valid models, and the fix is small and measured); inheriting the count but not the ordered flag (it would expand an ordered collection into indexed copies, which the existing ordered refusal exists to stop).*
- **D5. One rule for every count, including count 1.** A part with no multiplicity anywhere is one part, and a sibling that subsets it is that one part. `comp_b :> comp_a` builds only `comp_b`. *Rejected: treating only collections with a stated count as collections (a second rule; it leaves `part a :> psu; part b :> psu;` building three parts).*
- **D6. Named members of a collection that is not a sibling: refuse if that collection states a multiplicity, else build as today.** The `candidate-es-009` shape (`part def Site { part facility :> ac_facility; }`, a single package-level part) is the reuse pattern those cases pin, with reads by the part's own name, and it stays unchanged. A subset of another part's collection (`:> rack.servers`, or `:> Rack::servers` from outside a rack) would be left out of that collection's sums, so it is refused. A subsetting through a feature chain is always treated as not a sibling. *Rejected: refusing all non-sibling subsets (flips two generating `candidate-es-009` cases that read correctly); building them silently (wrong sums).*
- **D7. Refuse a named member that SysIDE shows inheriting a non-part feature from its collection.** If any feature in the named member's `usages` other than a part usage is owned by a part usage in the collection's slot, refuse. Example r11: `servers : Server[2] { :>> power = 12.0; }` with `server_1 :> servers` would build `server_1.power` 10 (KerML and SysIDE's usage view say 12) and sum 22. *Rejected: carrying attribute writes to named members (that is the spec's open inheritance non-goal); refusing every collection that owns features (refuses `outer_redefinition`, whose nested-part writes already reach named members correctly).*
- **D8. Refusal codes reuse existing codes with new reasons.** Too many named members: `SI_MULTIPLICITY_INVALID` (beside the negative-count refusal). The other shapes: `SI_MULTIPLICITY_UNSUPPORTED` (beside ordered, nonunique and range, "outside the supported occurrence model"). A redefinition that redefines two parts with different counts and states none: `SI_MULTIPLICITY_UNRESOLVED`. New `SiteReason` members name each site (Component Overview). *Rejected: new codes (nothing a user does differs from the existing codes' advice).*
- **D9. A named member that states any multiplicity is refused, including `[1]`.** The spec's `[AGENT]` item refuses counts other than 1. Refusing `[1]` too keeps the check to "states a multiplicity" with no bound evaluation, and no corpus model writes it. *Rejected: evaluating the bound to allow exactly 1 (extra mechanism for a form nobody uses).*
- **D10. Package-level roots use the same rule.** A root `server_1 :> servers` beside a root `servers : Server[2]` in the same package fills one place (shape r7: `servers[0]` and `server_1`). *Rejected: refusing it (valid model; same rule applies with no extra code beyond grouping roots by package).*

## Architecture

The change is inside `elaboration/occurrence.py`. Nothing downstream changes code, because everything reads occurrences through `OccurrenceIndex`.

1. **Read (once).** `build_occurrence_index` builds `member_target: declaration → (collection declaration, element)` from `owned_subsettings` (D1). It refuses here the shapes that need no context: several user collections, a named member of a named member, a named member with its own multiplicity.
2. **Count (per parent).** Before expanding an occurrence's children, a helper counts named members per collection slot among the sibling declarations, and decides each member's case: sibling (counted, D7 check), not a sibling with a stated multiplicity or a chain (refused, D6), not a sibling without one (built as today). Roots are grouped by package and counted the same way (D10).
3. **Expand.** `add_usage` passes the count `k` for the collection to `_multiplicity_indices`, which builds `range(n − k)` copies, or none for a single part with one named member, and refuses `k > n` (D2). `_multiplicity_indices` takes its multiplicity, owner and flags through the redefinition chain (D4).
4. **Index.** Each sibling member's `ExactOccurrence.member_of_slot` is the collection slot. `OccurrenceIndex.__init__` files it under its own slot and the collection slot (D3).
5. **Read paths.** `resolve_address` is unchanged; through `children_for_slot` a step on `servers` now yields `servers[0]` and `server_1`. Attribute nodes, writers, calc producers and the graph are unchanged in code; they see fewer occurrences.

Data in: the parser model and the slot index. Data out: the same `OccurrenceIndex` with fewer copies and named members visible under their collection.

## Required Invariants

- **I1.** For each parent and collection slot, unnamed copies plus sibling named members equal the collection's count, or the model is refused.
- **I2.** A named member's occurrence identity and display path do not change (`rack__server_1`).
- **I3.** `children_for_slot(parent, collection slot)` returns each member once; `children_for_slot(parent, member slot)` returns only the member.
- **I4.** No choice depends on declaration order, name or UUID order (ADR 0004).
- **I5.** A model with no subsetting between user part usages and no redefinition that omits a count builds byte-identical output.
- **I6.** dc3 regenerates byte-identical.

## Component Overview

- **`elaboration/occurrence.py`.** Membership read, sibling count, reduced expansion, inherited multiplicity, the collection-slot filing in `OccurrenceIndex`, and the new refusal sites. `ExactOccurrence` gains `member_of_slot`.
- **`elaboration/diagnostics.py`.** New `SiteReason` members: `occurrence_named_members_exceed_count`, `occurrence_named_member_nested`, `occurrence_named_member_multiplicity`, `occurrence_named_member_foreign_collection`, `occurrence_named_member_collections_multiple`, `occurrence_named_member_inherits_features`, `occurrence_multiplicity_inherited_ambiguous`.
- **Refusal cases.** One per new site under `tests/fixtures/refusal_cases/` with stored answers, site-account rows and mutation witnesses, per the repo's refusal-site practice (`tests/expectations/refusal_cases/`).
- **Docs.** `docs/architecture/modeling-assumptions.md`: the named-member rule and its refusals as product limits; the G1 line (`:723`) replaced by "a redefinition takes the count and ordering it redefines".

## Non-Goals

- Carrying a collection's own attribute writes to its named members (the spec's inheritance question). Refused by D7 where SysIDE shows the inheritance; filed as a backlog row.
- `[MEMBERSHIP-LIST-IGNORED]` (`part :>> servers = (server_1, server_2);`).
- Treating named parts as the only members of a `[*]` collection: s3 stays refused `SI_MULTIPLICITY_UNRESOLVED`.
- Counting a named member with its own count as several members (D9).
- The `candidate-es-009` reuse shape (D6), the dc3 nested form s5.

## Implementation Notes

- The prototype in `evidence/prototype.patch` passes every number below; treat it as a sketch. It still carries an unused helper (`_family_owns_non_part_features`) and an environment switch (`NSM_INHERIT_COUNT`) used only to measure D4; drop both.
- Exclude the reference and cross subsettings by identity with the usage's own properties (D1); do not add type names to agentic-mbse.
- Two repo guards fail on the prototype and must hold in the real code: `tests/unit/test_elaboration_import_boundaries.py` flags `next(iter(found.values()))` in `_effective_multiplicity` as first-match selection (use exactly-one unpacking after the ambiguity check), and `tests/conformance/test_expression_evidence_ownership.py` flags the dynamic `getattr(usage, special)` and `getattr(usage, flag)` reads (write each selector literally) and needs reviewed manifest rows for the new raw selector reads (`chaining_features` at the two new sites, plus `owned_subsettings`, `subsetted_feature`, `owned_reference_subsetting`, `owned_cross_subsetting`, `usages`, `is_ordered`, `is_nonunique` where the scan reports them).
- Take the inherited multiplicity's bound with the declaration that states it as `multiplicity_owner` in `_modeled_integer_bound`, so a bound that reads an attribute (`Server[n]`) resolves against the definition that owns it.
- Set `member_of_slot` only for sibling members, or a non-sibling subset (`candidate-es-009`) would be filed under a slot of a different parent.
- Every new refusal is raised from `build_occurrence_index` as a `MultiplicityExpansionError`, so it reaches the user through the same path as the existing multiplicity refusals.
- `usage_owner_bare_subset_def_owned` now refuses by D7 (Validation). Its guard test (`tests/conformance/test_usage_owned_reference_anchoring.py:468-477`) is about reference anchoring, not values. Keep the guard by dropping comp_a's `{ :>> length = 3.0; }` from the fixture, and move the original shape into a refusal case for `occurrence_named_member_inherits_features`.

## Potential Risks

- **Attribute inheritance gap.** D7 refuses only where SysIDE's usage view shows the inheritance. If SysIDE omits an inherited write, a named member reads the definition default silently, as it does today. Mitigation: the backlog row; the refusal case pins the shape SysIDE does show.
- **Ordered redefinitions now refuse.** `g1__redefinition_drops_ordered_bounds` flips from generating (one copy, ordering dropped) to refused (`occurrence_multiplicity_ordered`). Users with that shape lose a package that had the wrong count. RG1-1 recommended refusing it; this goes further and also builds the count where nothing is ordered.
- **More refusal sites.** Seven new sites, each with a case, row and witness. The plan budgets for it.

## Integration Strategy

The change is internal to occurrence building. The public package oracle and dc3 stay byte-identical. The changed fixture outputs are listed in Validation. The agentic-mbse guidance warning (`skills/sysml-conventions/SKILL.md:153`, `docs/patterns/adr002-calculations.md:301`, `project_templates/MODELING_GUIDE.md.template:130`) becomes false when this lands; the orchestrator owns that change. What it should then say:

- `sum()` over a collection with named members works: `part racks : Rack[2]; part rack_1 :> racks; part rack_2 :> racks;` makes `sum(racks.capital_cost)` add `rack_1` and `rack_2`, each once, and any unnamed copies left over.
- Name at most as many members as the count; a named member takes no count of its own; don't subset a named member; name members beside the collection (in the same part or definition), not from another part.
- Set values on each named member, not on the collection's own body (`racks : Rack[2] { :>> cost = 1.0; }` with named members is refused).
- A redefinition that omits its count keeps the inherited one (`part :>> racks;` over `Rack[2]` is two racks).
- Keep the wrong-way example only as these refusals; drop the "declare them as plain parts and add them" workaround.

## Validation Approach

Measured on the prototype (`evidence/prototype.patch` over `5593e44e`), with the scripts in `evidence/scripts/`:

- **Real TEAx sums** (`run_pkg.py` with `PYTHONPATH=src:/home/reid/src/teax/packages/teax-simkit /home/reid/src/dc3/.venv/bin/python`): s1 `total` 25.0 (`server_1` 15, `servers[0]` 10); s2 35.0 (`server_1` 15, `server_2` 20, no copies); s4 35.0 (`rack_1`, `rack_2`, no copies).
- **PSU fixtures**, each 4 PSUs, real TEAx `t.r = 2 × efficiency`: `plain_nesting` all 0.9; `one_subset_redefines` `rack_1.server_1` 0.95, others 0.9; `nested_named_subset` all 0.95; `nested_named_subset__single_rack` `rack_1.server_1` 0.95, `rack_1.server_2` 0.85, `racks[0].servers[0..1]` 0.9; `outer_redefinition` `rack_1.server_{1,2}` 0.95, `rack_2.server_{1,2}` 0.9; `sibling_subsets_redefine` `rack_1.servers[0..1]` 0.95, `rack_2.servers[0..1]` 0.85. Without D4, `outer_redefinition` refuses and `sibling_subsets_redefine` builds 2 PSUs, as the spec predicted.
- **dc3:** regenerated to scratch (`sysml-codegen generate --models models`, `--env-file /home/reid/src/dc3/.env`) on the base and on the prototype; both `diff -rq` identical to `exploration/ac_dc_baseline/dc3_baseline/`. The occurrence index drops from 153 to 121 entries; the 32 removed are exactly the indexed copies (none remain).
- **Whole corpus:** all 457 fixture roots plus the two extra roots, both classes, generated on the base and on the prototype (`corpus_all.py`), `diff -rq`. Differences, all expected:
  - the six `candidate-es-008` cases: 12 (three cases), 11, 8 or 6 PSUs become 4, values as above (params, schemas, contracts, pipeline, runnable test);
  - `part-multiplicity__redefinition_drops_bounds__expanded_part_usage`: one `servers` copy becomes `servers[0..1]` (D4, the s8 fix);
  - `g1__redefinition_drops_ordered_bounds`: generated becomes refused, `occurrence_multiplicity_ordered` (D4);
  - `occurrence_seed/f1_inherited_ordered_redef`: refused `NOTHING_TO_GENERATE` becomes refused `occurrence_multiplicity_ordered` (D4);
  - `usage_owner_bare_subset_def_owned`: generated becomes refused, `occurrence_named_member_inherits_features` (D7; `comp_b`'s usage view holds `comp_a::length = 3.0`, while the package gave `comp_b.length` 1.0). With the fixture edit above it generates again.
  - Every other root is byte-identical. `occurrence_seed/f1_effective_declaration_slot` changes its occurrence index only (`racks[1]` goes, `rack_a` fills that place) and still refuses `NOTHING_TO_GENERATE`.
- **Refusal probes** (`evidence/shapes/`): r1 three named of `[2]` and r5 two named of a single part → `SI_MULTIPLICITY_INVALID`; r2 nested, r3 and r3b own count, r4 and r4b foreign collection, r9 and r11 inherited feature → `SI_MULTIPLICITY_UNSUPPORTED` with their reasons; r8 `:>> servers` over `[*]` → `SI_MULTIPLICITY_UNRESOLVED`; s3 unchanged. r7 (roots) builds `servers[0]` and `server_1`.
- **Full suite** on the prototype: see Appendix A.

Not checked: native SysIDE values for the PSU fixtures; models outside the fixture corpus and dc3; smart regeneration; the snapshot route (`sysml-codegen snapshot`) beyond what the suite covers.

## Next-Stage Handoff

- **Fixed:** D1 to D10, the expected-change list above, dc3 byte-identity.
- **Open:** the wording of refusal messages; whether the plan merges any two sites that the refusal-site practice would let share a reason.
- **De-risk first:** land membership and the count fix together (Phase 1), rerun the corpus, and confirm the list above before touching stored answers.

## Plan

### Phase 1: Membership and count in `occurrence.py`

- [ ] Read membership once in `build_occurrence_index` (D1); `ExactOccurrence.member_of_slot`; collection-slot filing in `OccurrenceIndex.__init__` (D3).
- [ ] Sibling count per parent and per package; reduced expansion in `_multiplicity_indices` (D2, D5, D10).
- [ ] Inherited multiplicity and flags through the redefinition chain (D4).
- [ ] Refusal sites and `SiteReason` members (D6 to D9).
- [ ] Keep the two guards green: no first-match selection, literal selectors only, manifest rows for new raw reads (Implementation Notes).
- [ ] Rerun `evidence/scripts/corpus_all.py` on base and branch; the diff must equal the Validation list. Rerun dc3 to scratch; byte-identical.

### Phase 2: Pins and tests

- [ ] Re-capture the six `candidate-es-008` stored answers with `attr_value` seams at 4 PSUs and the values above.
- [ ] Update `part-multiplicity__redefinition_drops_bounds__expanded_part_usage` (occurrences seam to two copies; remove its RG1-1 `loss` block) and `g1__redefinition_drops_ordered_bounds` (now refused; remove its `loss` block); update `fixture_classes.json` for g1 and `f1_inherited_ordered_redef`.
- [ ] Edit `usage_owner_bare_subset_def_owned` as in Implementation Notes; confirm its anchoring tests pass.
- [ ] One refusal case per new site (start from `evidence/shapes/r1..r11` and the original `usage_owner_bare_subset_def_owned`), with stored answers, site-account rows and mutation witnesses.
- [ ] A real-TEAx value test for s1, s2 and s4 sums (25, 35, 35), beside `test_sibling_override_leak.py`'s pattern.
- [ ] Unit tests for I3 (collection lookup returns each member once; member lookup returns only the member) and for D2 labels.
- [ ] Full suite green, including slow tests.

### Phase 3: Docs and backlog

- [ ] `docs/architecture/modeling-assumptions.md`: named-member rule and refusals as product limits (subset of a subset; named member with its own count; foreign collection; inherited non-part feature; more named than the count); replace the G1 line.
- [ ] Backlog: close `[NAMED-SUBSET-DOUBLE-COUNT]` and `[REDEFINITION-DROPS-COUNT]`; file a row for carrying a collection's attribute writes to named members (D7's refusal).
- [ ] Record the corpus receipt for this item in `evidence/corpus-receipt.md`.
- [ ] Hand the agentic-mbse guidance list (Integration Strategy) to the orchestrator.

## Appendix A: Prototype full-suite run

Default run (`pytest tests/`, slow tests deselected) on scratch copies of `5593e44e`, base and prototype side by side. The copies are not git work trees, so 59 tests fail on both for that reason (study tools, ledger checks); they are not counted below. The prototype adds 24 failures, all expected:

- Stored answers and classes the Validation list predicts: the `candidate-es-008` `attr_value` seams (`nested_named_subset`, `..._single_rack`, `sibling_subsets_redefine`), the `occurrences` seams of `g1__redefinition_drops_ordered_bounds` and `part-multiplicity__redefinition_drops_bounds__expanded_part_usage`, g1's outcome in five refusal-case tests and the snapshot replay, and the live class of g1, `f1_inherited_ordered_redef` and `usage_owner_bare_subset_def_owned`.
- `usage_owner_bare_subset_def_owned`'s three anchoring tests (fixture edit in Implementation Notes).
- Refusal-site bookkeeping: `test_site_account.py` and two `test_site_reasons.py` tests (new sites need rows).
- The two guard findings in Implementation Notes (`test_elaboration_import_boundaries.py`, two `test_expression_evidence_ownership.py` tests).

The plain-nesting and one-subset seams did not fail because those stored answers pin only the outcome. Slow tests were not run.

---

**Next Steps:** after approval, `/_my_implement` from the Plan above.
