# Spec: Named subsets are members of the collection they subset

**Status:** Draft
**Owner:** Reid Westwood
**Created:** 2026-10-26
**Complexity:** MEDIUM
**Branch:** `named-subset-members` (stacks on `repeated-rollup-collision`, not yet merged)
**Backlog:** `[NAMED-SUBSET-DOUBLE-COUNT]`

---

## Problem

The generator gets the number of parts wrong when a model names some members of a collection. In `part def Rack { part servers : Server[2]; }`, a usage that writes `part server_1 : Server :> servers;` is naming one of the two servers. The generator builds three: `servers[0]`, `servers[1]` and `server_1`.

Why: the generator reads declarations from SysIDE but expands them into concrete parts (occurrences) itself. It understands redefinition (`:>>`) but never reads subsetting (`:>`). So `server_1 :> servers` becomes an extra child instead of one of the servers, and `sum(servers.power)` adds only the indexed copies, which hold defaults, and leaves out `server_1` and its values. Cause with file and line: `.project/active/repeated-rollup-collision/evidence/double-count/report.md` § Cause.

The SysML meaning is settled: KerML 7.3.4.4 says a subsetting feature's values are also values of the subsetted feature, and its example has `driveWheels[2] subsets wheels[4]` as two of the four wheels (citations in the report § SysML meaning). Native SysIDE cannot settle the numbers, because it does not expand multiplicities.

This breaks ADR 0004 ("exactly one concrete occurrence, a modeled plural result, or a named refusal"). The wrong sum builds silently today. dc3 is not affected today only because no dc3 model reads a whole collection.

**[OWNER] 2026-10-26:** fix it with option A of the report, named subsets count as members of the collection they subset ("ok understood, proceed with the fix", after the orchestrator recommended A).

## Success Criteria

Numbers use the report's probe models in `.project/active/repeated-rollup-collision/evidence/double-count/shapes/` (`Server.power default 10.0`, `Rack.total = sum(servers.power)`). Sums are checked in real TEAx.

- [ ] **s1** (`servers : Server[2]`, one named subset `server_1` with power 15): the rack holds exactly two servers, `server_1` and one unnamed copy. `total` is 25.
- [ ] **s2** (`[2]`, named `server_1` 15 and `server_2` 20): the rack holds exactly `server_1` and `server_2`, no unnamed copies. `total` is 35.
- [ ] **s4** (dc3's shape: library `racks : Rack[*]`, `part :>> racks[2]` in a specializing definition, `rack_1` 15 and `rack_2` 20 subset `racks`): exactly `rack_1` and `rack_2`. `total` is 35.
- [ ] **Per-copy values stay separate.** In s1 the unnamed copy's power is 10 and `server_1`'s is 15; in s2 `server_1` is 15 and `server_2` is 20. No value reaches a copy that does not own it.
- [ ] **The `candidate-es-008` cases build the declared count of 4 PSUs** (models in `tests/fixtures/refusal_cases/`, two racks of two servers):
  - `plain_nesting`: 4 PSUs, all 0.9 (12 today).
  - `one_subset_redefines`: 4 PSUs, `rack_1.server_1` 0.95, the other three 0.9 (12 today).
  - `nested_named_subset`: 4 PSUs, all 0.95 (12 today: eight extra 0.9 defaults).
  - `nested_named_subset__single_rack`: 4 PSUs, `rack_1.server_1` 0.95, `rack_1.server_2` 0.85, and the two servers of one unnamed rack at 0.9 (8 today).
  - `outer_redefinition` and `sibling_subsets_redefine`: see the premise conflict below. These two cannot reach 4 PSUs without the count fix.
- [ ] Their stored answers in `tests/expectations/refusal_cases/cases/` are re-captured to the numbers above, so the `attr_value` seams pin the fixed output.
- [ ] **Refusals**, each with a named code and a reason specific to the case, and each covered by a refusal case in the repo's usual way:
  - more named subsets than the collection's count (e.g. three named subsets of `servers : Server[2]`);
  - a subset of a named subset (e.g. `server_1a :> server_1` where `server_1 :> servers`);
  - named subsets of a `[*]` collection stay refused as today (s3, `SI_MULTIPLICITY_UNRESOLVED`).
- [ ] **The new refusals are written down as product limits** in `docs/architecture/modeling-assumptions.md`, since some refuse valid KerML (a subset of a subset; a named subset with its own count, which is KerML 7.3.4.4's own `driveWheels[2]` example).
- [ ] **agentic-mbse guidance is corrected, or a cross-repo follow-up is filed before close.** It currently tells modelers not to `sum()` over a collection with named members (`/home/reid/src/agentic-mbse/skills/sysml-conventions/SKILL.md:153`, `/home/reid/src/agentic-mbse/docs/patterns/adr002-calculations.md:301`, and the matching line in `project_templates/MODELING_GUIDE.md.template`). After this fix that warning is false; it should show the working form and the new refusals.
- [ ] **dc3 unchanged.** Regenerating `/home/reid/src/dc3/models` gives a package byte-identical to the committed `/home/reid/src/dc3/exploration/ac_dc_baseline/dc3_baseline/`, or every difference is explained. The investigation expects none; that is not yet checked. dc3 is read-only.
- [ ] **Nothing else that builds today changes.** Proven by the whole-corpus byte check in `.project/active/repeated-rollup-collision/evidence/corpus-receipt.md`: every generating root plus the refusal cases, generated on the base branch and on this branch, compared with `diff -rq`. Every root that differs is on the expected list (the `candidate-es-008` cases above, `occurrence_seed/f1_effective_declaration_slot`, which has `rack_a :> racks` in a `Rack[2]`), or is explained in the receipt as another named subset beside its collection.

### Premise conflict: two cases need the count fix

The brief asks that `outer_redefinition` and `sibling_subsets_redefine` build 4 PSUs, and also lists `[REDEFINITION-DROPS-COUNT]` as a non-goal. Both cannot hold. In both models a rack writes `part :>> servers { ... }` without restating `[2]`, and the generator builds one copy for that redefinition (`_multiplicity_indices`, `elaboration/occurrence.py:833-835`). The stored answers confirm it: today `sibling_subsets_redefine` holds one `servers` copy per named rack.

What option A alone does to them:

- `sibling_subsets_redefine`: the extra `racks[0..1]` go away, leaving 2 PSUs (0.95 and 0.85) where the model has 4. Still a wrong count, now an undercount.
- `outer_redefinition`: `rack_1` sees a count of 1 with two named subsets, so it hits the "more named subsets than the count" refusal although the model is valid.

**[AGENT] decision:** the rule covers the shape, not just these two fixtures. When a collection is redefined without restating its count (`part :>> servers { ... }`) and it has named subsets, or the redefinition sits inside a named subset (`rack_1 :> racks` holding `part :>> servers { ... }`), the generator either builds the count the model inherits or refuses by name with a reason that points at `[REDEFINITION-DROPS-COUNT]`. It never builds a wrong count. A refusal or build case beyond the two fixtures covers the shape. I recommend design measures the count fix first: if it changes no other corpus root beyond those it explains, take it and build 4; otherwise refuse here and leave the count fix to its row. Which PSUs hold 0.95 in `outer_redefinition` is not part of this criterion (see Non-Goals).

## Known Requirements

- **[NEED]** A named subset counts as one of the members of the collection it subsets, so the collection holds the declared count, not more. (Owner, option A.)
- **[NEED]** Named subsets keep their own names and are not given index positions. Only the remaining unnamed copies are indexed. (Owner, option A; ADR 0004 rules out choosing by declaration order.)
- **[HARD]** No occurrence is chosen by arrival order, first match or proximity (ADR 0004, `.project/adr/0004-derive-occurrences-from-exact-evidence-or-refuse.md`).
- **[NEED]** A read of the whole collection, such as `sum(servers.power)`, reaches the named members and the unnamed copies, each once. (Owner, via the brief's sums.)
- **[INFERRED]** A read of a named subset by its own name (`server_1.power`) still reaches that same copy.
- **[INFERRED]** Each named subset is a distinct member. KerML allows two named subsets to be the same member, but nothing in the model says so, and with different values they must differ.
- **[INFERRED]** The rule applies wherever the named subset and the collection end up features of the same part, whether written in a usage body (s1) or in a specializing definition (s4).
- **[AGENT]** A named subset that writes its own count other than 1 (`part drive_wheels : Wheel[2] :> wheels;`) is refused by name in this item rather than counted. Counting it as several members is a possible later extension.
- **[INFERRED]** Every new refusal site gets what the repo's refusal-site practice requires (a refusal case with a stored answer, a site-account row, a mutation witness).

## Non-Goals

- `[REDEFINITION-DROPS-COUNT]` (s8): out of scope as its own row, except as decided above for the two `candidate-es-008` cases.
- `[MEMBERSHIP-LIST-IGNORED]` (s7, `part :>> servers = (server_1, server_2);`): separate row.
- Whether `comp_b :> comp_a` inherits `comp_a`'s nested redefinitions (for example, whether `server_1` in `outer_redefinition` gets the 0.95 from `part :>> servers { ... }`): open, not settled here.
- **[AGENT, reserved for the owner if the design wants to change it]** Treating the named parts as the only members of a `[*]` collection (s3 would give 35): out of scope, because SysML does not say a `[*]` collection has no other members.
- The dc3 nested form refused with `SI_OCCURRENCE_MISSING` (s5): unchanged.

## Open Questions / Deferred to design

- Count fix for the two `candidate-es-008` cases: take it or refuse (decided above as a rule; design measures and picks).
- Which index labels the unnamed copies get (for s1, `servers[0]` or something else), as long as named subsets get none and the choice does not depend on declaration order.
- Whether the refusals use new codes or existing codes with new reasons.
- A part that subsets a collection owned by some other part (not its own parent): check what it does today; refuse if it gives a wrong count.
- A collection of count 1 (`part psu : Psu;` with `part main_psu :> psu;`): under the rule `main_psu` is the one member. The corpus check will show whether any root has this shape.

---

## Related Artifacts

- **Investigation:** `.project/active/repeated-rollup-collision/evidence/double-count/report.md` (shapes and scripts beside it)
- **Corpus check method:** `.project/active/repeated-rollup-collision/evidence/corpus-receipt.md`
- **Backlog:** `.project/backlog/BACKLOG.md` rows `[NAMED-SUBSET-DOUBLE-COUNT]`, `[REDEFINITION-DROPS-COUNT]`, `[MEMBERSHIP-LIST-IGNORED]`
- **Decision:** `.project/adr/0004-derive-occurrences-from-exact-evidence-or-refuse.md`
- **Brief:** `.project/active/named-subset-members/briefs/spec.md`
- **Product lens:** `.project/active/named-subset-members/product-lens.md`
- **Design:** `.project/active/named-subset-members/design.md` (to be created)

---

**Next Steps:** After approval, proceed to `/_my_design`.
