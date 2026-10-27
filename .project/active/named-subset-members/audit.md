# Audit: Named subsets are members of the collection they subset

**Verdict:** Needs Work
**Audited:** 2026-10-26
**Branch:** `named-subset-members`
**Commit:** `153d09e2` (code and docs; branch tip `bc89c6df` adds only the audit brief). Compared against `63819eab`, whose `src/` is identical to `ed736479` and `26dbcc5e`.

---

## The Point

The generator got the number of parts wrong when a model named some members of a collection. In `part def Rack { part servers : Server[2]; }`, a usage writing `part server_1 : Server :> servers;` names one of the two servers, but the generator built three (`servers[0]`, `servers[1]`, `server_1`), and `sum(servers.power)` added the two default copies and left `server_1` out. KerML 7.3.4.4 says a subsetting feature's values are values of the subsetted feature, so `server_1` is one of the two. That broke ADR 0004 (each modeled member is exactly one concrete copy, or the generator refuses by name) and built a wrong sum silently. The owner ratified option A (`[AGENT]` recommended, 2026-10-26): a named subset counts as one member of its collection, the generator builds the declared count, and a whole-collection read reaches every member once. The owner's priority is no silent wrong numbers.

## Summary

The core rule works for the shapes the spec and design list, and for most new shapes I tried: subtype members, nested collections with their own named members, named members inside repeated rolled-up sub-assemblies, mixed literal and expression overrides, a count raised or lowered by a redefinition, and diamond-inherited counts all give the right sums in real TEAx. The suite, corpus receipt and dc3 claims reproduce exactly.

Two shapes still build a wrong sum silently, and both are new on this branch:

- Membership is keyed by slot across the whole model, so one usage's `part :>> spare :> servers` makes `spare` a member of `servers` in every other usage of `Rack` too. A plain `rack_b : Rack` sums 11 where the model gives 20 (base gave 20).
- A named member that reads its own collection (`sum(servers.power)` written inside `server_1`, or a "share of the total" attribute) sees only itself. The design named this case and did not check it.

## Product Judgment

This is the right piece of work. Option A matches KerML and the owner's ratified choice, and the refusals it adds fail closed. But the owner's stated priority is no silent wrong numbers, and both blockers below are silent wrong numbers that this change introduces in exactly the feature it adds. That is a real contradiction with what the owner asked for, so the verdict is Needs Work.

The product-lens ledger has no open `BLOCK`; its earlier findings (spec-F1 to F3, design_review-F1 to F4, M1) are disposed and still hold in the code. I did not run a fresh product-lens subagent or append to `product-lens.md`, because this audit was scoped to write only `audit.md`. None of the audit's code smells fired except as described under the blockers.

## Blockers

### B1. A subsetting added by one redefinition makes the part a member in every other usage (`occurrence.py:1082-1115`, `:1121-1165`)

`_read_named_membership` records "member slot → collection slot" once for the whole model. `_sibling_members` then treats any sibling whose slot is in that map as a named member. A slot is shared by a declaration and every redefinition of it. So when one usage redefines an inherited part and adds a subsetting, the base declaration and every other usage of the same definition become members too.

Reproduced in real TEAx (both models build, no refusal):

```sysml
part def Server { attribute power : Real default 10.0; }
part def Rack { part servers : Server[2]; part spare : Server { :>> power default 1.0; }
                attribute total : Real = sum(servers.power); }
part rack_a : Rack { part :>> spare :> servers { :>> power = 15.0; } }
part rack_b : Rack;
```

- `rack_a.total` 25.0 (correct: `spare` 15 and one copy).
- `rack_b.total` **11.0**. The model gives 20 (`servers[0..1]`; `spare` is not a server in `rack_b`). Base gives 20.0.

The same happens through a specializing definition (`part def PoolRack :> Rack { part :>> spare :> servers; }` with `rack_a : PoolRack` and `rack_b : Rack`): `rack_b` 11.0, base 20.0.

The design's bet B2 says every redefinition of a member shares its slot, so a redefined member stays a member. That is true, but the code also uses the converse, that every declaration in a member's slot is a member, and that is false when the subsetting is added by a redefinition. The same model-wide map also refuses a valid model where two usages redefine `spare` into two different collections (`subsets more than one part`).

What should change: decide membership per parent, from the sibling declaration and the declarations it redefines (the same walk D7 already does for owned features), not from every declaration that shares the slot. Add a build case with two usages of one definition, only one of which adds the subsetting.

### B2. A named member that reads its own collection sees only itself (`occurrence.py:492-506` with `resolve_address`, `:645-656`)

A named member is now filed under its collection's slot. `resolve_address` narrows each step to the candidates that are a prefix of the reader's own path (the shared-prefix rule). When the reader is inside `server_1`, the `servers` step finds `server_1` among the candidates and narrows to it. Base did not file `server_1` under `servers`, so the narrowing never fired for named members.

Reproduced in real TEAx:

| Model (Server power default 10.0) | Branch | Model gives | Base |
|---|---|---|---|
| `rack : Rack { part server_1 :> servers { :>> power = 15.0; attribute seen = sum(servers.power); } }` | `seen` **15.0** | 25 | 20.0 |
| Same, with `server_1` declared in `part def Rack` | `seen` **15.0** | 25 | 20.0 |
| `hall : Hall { part rack_1 :> racks { attribute share = total / sum(racks.total); } }` (Hall `racks : Rack[2]`, each rack 20) | `share` **1.0** | 0.5 | 0.5 |
| `server_1` (power 30) and `server_2` each with `frac = power / sum(servers.power)`, `total = sum(servers.frac)` | each `frac` **1.0**, total **2.0** | 0.75, 0.25, total 1.0 | 1.5, 0.5, 0.0 |

A read from a sibling that is not a member (`part mon { :>> seen = sum(servers.power); }`) gives the correct 25.0.

The "share of the total" row is a regression: base gave 0.5 (right only because every rack held defaults), the branch gives 1.0. This breaks the spec's `[NEED]` that a read of the whole collection reaches the named members and the unnamed copies, each once. The design's Validation Approach lists this read as not checked and says it narrows "as it does for indexed copies today".

What should change: either a read of a collection from inside one of its own members reaches the whole collection, or that read is refused by name. A build or refusal case and a real-TEAx value should pin it. Note the indexed-copy analogue below (N4) is the same mechanism and is wrong on base too; whichever answer is chosen here should be checked against it.

## Advisory

### Should-fix

- **S1. The `[MEMBERSHIP-LIST-IGNORED]` note is wrong about base (`.project/backlog/BACKLOG.md:105`).** It says s7 sums 35.0 "on the generator at `ed736479`", so the row's 10 was not reproduced. I get **10.0** on base (`63819eab`, whose `src/` is identical to `ed736479`): base builds one `servers` copy at the default and leaves `server_1` and `server_2` out of the sum. The note contradicts itself on this point (it also says base builds "one `servers` copy beside them"). The branch gives 35.0, which is correct per SysML (the list binds `servers` to `(server_1, server_2)`, and both also subset it), but only because the two parts subset `servers`; the list is still not read. A list that names parts which do not subset the collection (`part :>> servers = (a, b);` with `a` 15 and `b` 20) gives **20.0** on the branch and 10.0 on base, where the model gives 35. The row should say: base 10 reproduced; branch 35 for s7 because of subsetting; the list itself is still ignored, so the list-only form now gives 20 instead of 10, still wrong.
- **S2. The D7 limit in the docs is narrower than the code (`docs/architecture/modeling-assumptions.md:437`).** The row says a collection is refused when its declaration "sets a value". The code (`_owns_non_part_feature`, `occurrence.py`) refuses any owned feature that is not a part usage, including a new attribute with no value, a port or a constraint. Example: `servers : Server[2] { attribute seen : Real = sum(servers.power); }` with a named member is refused `occurrence_named_member_collection_owns_features`. Say "owns a feature that is not a part (a value, a new attribute, a port, a constraint)". The agentic-mbse guidance (`docs/patterns/adr002-calculations.md:328`, landed at agentic-mbse `80c64eee`) has the same narrow wording.

### Notes

- **N1. `_sibling_members` runs once per copy (`occurrence.py:1352`).** `child_members` depends only on `child_declarations`, which is per usage, but it is computed inside the loop over indices. Hoist it above the loop. No effect on output.
- **N2. Inherited counts are de-duplicated by Python object identity (`occurrence.py:886`, `id(stated[0])`).** If SysIDE ever returned two wrapper objects for one multiplicity, a diamond would be refused as ambiguous. This fails closed, and the diamond probe (`part def D :> B, C { part :>> B::servers, C::servers; }`) builds 20.0 correctly today, so it is a note only.
- **N3. A subsetting whose endpoint has no qualified name is skipped silently (`occurrence.py:1075-1076`).** I could not build a model that reaches this (an unnamed part cannot be referenced), so it looks harmless, but a short comment saying why it cannot be a user part would make the skip honest.
- **N4. Pre-existing, not this item: an indexed copy that reads its own collection also sees only itself.** `servers : Server[2] { :>> frac = power / sum(servers.power); }` gives `frac` 1.0 for each copy and `sum(servers.frac)` 2.0 on both base and branch (the model gives 0.5 each, total 1.0). On the branch this exact shape is refused when the collection has named members (D7), but without named members it builds. Not on the backlog; worth a row, and it bears on how B2 is fixed.
- **N5. `nonunique` named members cannot be written for parts.** SysIDE rejects `part servers : Server[2] nonunique;` ("Subsetting feature cannot be nonunique if subsetted feature is unique"), so the nonunique inheritance in `_is_nonunique` is reached only through models SysIDE already flags. Nothing to fix.

## Findings Detail

### Plan completion

All three phases are done as their notes say. I found no placeholder code or TODOs in the diff. The deviations the implementer lists are sound: no new witness case was needed for the elaborate site D6 takes over (`candidate-es-002__calc_input_through_part__attribute_value` already witnesses it); `_multiplicity_indices` keeps its job and name so site IDs stay stable; the `chaining_features` manifest row moved to the shared `_chain_endpoint` rather than gaining a second row.

### Spec conformance

- **s1** verified: 25.0 in real TEAx; `server_1` and `servers[0]`.
- **s2** verified: 35.0; only `server_1` and `server_2`.
- **s4** verified: 35.0; only `rack_1` and `rack_2`.
- **Per-copy values** verified for s1 and s2 through the params (`server_1` 15, copy 10; 15 and 20). Not verified in general because of B1, where a value-free usage loses a copy.
- **`candidate-es-008` at 4 PSUs** verified from the regenerated params of all six cases, values exactly as the spec lists, including `outer_redefinition` and `sibling_subsets_redefine` through the count fix.
- **Stored answers re-captured** verified: the suite passes with them.
- **Refusals** verified: exceed count, subset of a named member and `[*]` (s3, `occurrence_multiplicity_upper_unresolved`) each refuse with their own reason and have a refusal case.
- **Limits documented** verified, with S2's wording gap.
- **agentic-mbse guidance** done at agentic-mbse `80c64eee` (`docs/patterns/adr002-calculations.md:301-332`, `project_templates/MODELING_GUIDE.md.template:130`). If B1 or B2 is fixed by refusing a shape, that guidance will need the new limit.
- **dc3 unchanged** verified: from `git -C /home/reid/src/dc3 archive 8a98af8 models exploration/ac_dc_baseline/dc3_baseline`, base and branch output are each `diff -rq` identical to the committed baseline.
- **Nothing else that builds changes** verified: I regenerated all 471 roots on both sides (branch's root list and fixtures). Base 200 generated / 271 refused, branch 190 / 281, no crashes, and `diff -rq` finds exactly the 27 roots the receipt lists, each with the reason it states.
- **[NEED] whole-collection read reaches every member once**: not met for a read from inside a named member (B2).
- **[NEED] named members keep their names, only unnamed copies indexed** met.
- **[HARD] no choice by order** met: sorting is by wire ID for determinism only; counts and filing do not depend on order.
- **[INFERRED] reads by own name, distinct members, sibling rule in usages and definitions** met.
- **[AGENT] a named member with its own count other than 1 is refused** met (`[2]` refused `form`; `[0..1]` refused as a range; `[1]` builds).
- **[INFERRED] refusal-site practice** met: site-account rows and mutation witnesses exist and their tests pass.
- **Non-goals** respected. `[MEMBERSHIP-LIST-IGNORED]` stays open (see S1 for its note).

### Design conformance

The code follows D1 to D11 where the design places them. The one gap is the converse of bet B2, described under blocker B1: the design keys membership by slot to keep redefined members in (review M1), and the code applies that key model-wide instead of per parent. The design flagged the shared-prefix narrowing for named members as unchecked; B2 shows it is wrong.

### Code integrity

The code reads cleanly and matches the surrounding style: small helpers, one docstring each, frozen dataclasses for the two membership maps. Each of the five reasons is raised from one construction site (`occurrence.py:895`, `:1055`, `:1149`, `:1163`, `:1196`); the `form` reason's three conditions call one helper, which is what the design asked for. `ruff check src/` and `mypy src/` are clean. Findings are N1 to N3 above. No broad excepts, no compatibility shims, no environment switches.

---

## Certification

Checked, by running:

- Default suite in a worktree at `153d09e2`: 9 failed (the known `test_check_ledger_4a.py` ×8 and one `test_study_cli.py`), 8865 passed.
- `tests/execution/test_named_subset_members_teax.py` with dc3's venv and `--noconftest`: 6 passed.
- Whole corpus, 471 roots, base and branch, `diff -rq`: matches the receipt exactly.
- dc3 at `8a98af8` from its committed tree, base and branch: both byte-identical to the committed baseline.
- 33 new probe models in real TEAx on base and branch (subtype members, nested named collections, repeated rolled-up assemblies, mixed overrides, raised and lowered counts, count 1, `[0..1]`, `nonunique`, diamond counts, reference subsetting, membership lists, reads from inside members). Probe models are in `/tmp/claude-1000/nsm-audit/probes/` until that scratch folder is cleaned; the two blocker models are written out above.

Not marked: I did not tick spec checkboxes or update `CURRENT_WORK.md`, because this audit was scoped to write only `audit.md`, and the verdict is Needs Work.

**Not checked:** native SysIDE values for the probes (sums were checked in real TEAx against values worked by hand from KerML); the execution lane beyond the one new test file; the `snapshot` route beyond the suite; models outside the fixture corpus and dc3; dc3 at its current `HEAD`; whether B2's narrowing also affects non-sum reads (a plain `servers.power` read from inside a member was not probed separately); a fresh product-lens run.

---

## Round 2

**Verdict:** Pass
**Audited:** 2026-10-26, fresh reviewer
**Commits:** `550b3ee1` (B1), `3cc2fb98` (B2), `9e809ee0` (S1, S2), `27037160` (record). Compared against round 1 (`153d09e2`) and base (`63819eab`).

### The point

Both blockers are fixed, and I could not break either fix. Every probe I built gives the value worked out by hand from KerML, in real TEAx. The suite, corpus and dc3 claims reproduce exactly. One should-fix remains: the B2 fix also changes a shape that used to build, and the docs do not say so.

### B1: membership is now decided per parent

`_sibling_members` (`occurrence.py:1107`) now reads each sibling from its own declaration and the declarations it redefines (`_subsetted_through_redefinitions`, `occurrence.py:1081`). It no longer uses a model-wide map. Probes, all in real TEAx (Server power default 10, `spare` default 1 unless stated):

| Shape | Round 1 | Round 2 | Model gives |
|---|---|---|---|
| Audit k1: `rack_a : Rack { part :>> spare :> servers {15} }`, plain `rack_b : Rack` | 25, **11** | 25, 20 | 25, 20 |
| Audit k2: through `PoolRack :> Rack` | 11, **11** | 11, 20 | 11, 20 |
| Subsetting added two levels down in a usage: `hall_a : Hall { part :>> racks { part :>> spare :> servers; } }`, plain `hall_b` | 22, **22** | 22, 40 | 22, 40 |
| Same through a specializing def `PoolHall :> Hall` | 22, **22** | 22, 40 | 22, 40 |
| Added in a named rack `rack_1 :> racks` only, with a single `solo : Rack` beside it | hall_a **22**, solo **11**, hall_b **22** | 31, 20, 40 | 31, 20, 40 |
| A redefinition of a redefinition: `P2 :> PoolRack { part :>> spare {3} }`; plain `Rack`; `PoolRack` | 13, **11**, 11 | 13, 20, 11 | 13, 20, 11 |
| `rack_x : PoolRack { part :>> spare {2} }` (no subsetting written in the usage) and `rack_y : Rack { part :>> spare {2} }` | 12, **12** | 12, 20 | 12, 20 |
| Two usages put `spare` in two different collections (`servers` in one, `backups` in the other) | refused (`form`) | 11/20 and 20/11 | 11/20 and 20/11 |
| Membership added in one def-owned usage (`Hall { rack_a : Rack { :>> spare :> servers } rack_b : Rack }`), and another usage adding it to `rack_b` | hall_1 tb **11** | hall_1 11/20, hall_2 11/15 | 11/20, 11/15 |
| A member added in a specializing def reads its share: `PoolRack :> Rack { part :>> spare :> servers { :>> frac = power / sum(servers.power); } }` (spare 30) | frac **1.0**, rack_b **40** | 0.75, 20 | 0.75, 20 |

The `rack_x` row matters most: the usage's `:>> spare` resolves to `PoolRack::spare`, so the walk through redefinitions still finds the subsetting. The two-collections row was refused in round 1 because of the model-wide map; it now builds the right numbers.

### B2: a written name reaches every occurrence it names

`resolve_address` (`occurrence.py:601`) now narrows a step to the reader's own path only for steps the reader did not write. Those are the steps implied by where the first written part is declared. `_reference_address` (`elaborate.py:2487`) returns the index of the first written step. Probes (round 1 → round 2, then the hand value):

- **A copy reading its own nested part:** `servers : Server[2] { part disk; :>> d = disk.size; }` (and with `sum(disk.size)`). Total 8 → 8 (8). It still reads its own disk.
- **A named member reading its own nested part and the whole collection's:** `s1 :> servers { part :>> disk {7}; alld = sum(servers.disk.size); }`. `alld` 7 → 11 (11); total 11.
- **Two levels of indexed copies:** `racks : Rack[2] { servers : Server[2] { fs = power / sum(servers.power); fr = power / sum(racks.servers.power); } }`. `sum(racks.total)` 4 → 2 (2), `sum(racks.servers.fr)` 4 → 1 (1). Base also gave 4 and 4. This is the N4 fix reaching nested collections.
- **Two levels with named members:** `rack_1 :> racks { server_1 :> servers {30} }`. Rack 40, hall 60; `power / sum(servers.power)` 1.0 → 0.75 (0.75); `power / sum(racks.servers.power)` 1.0 → 0.5 (0.5); `power / sum(racks.total)` 0.75 → 0.5 (0.5).
- **The same with the collections declared in definitions**, and with a named rack overriding its `psu`: load 0.4, `f` 0.667, `g` 0.4, all as worked by hand.
- **Shadowing:** `Server` owns its own `part servers : Sub[2]` (power 1), and `server_1 :> servers` writes `sum(servers.power)`. 2.0 → 2.0 (2.0, the inner `servers` by name resolution); rack total 25.
- **A copy reading a part declared beside its collection, inside a named rack:** `racks : Rack[2] { part psu; servers : Server[2] { load = power / psu.cap; } }`, `rack_1 :> racks { part :>> psu {50} }`. `sum(racks.servers.load)` 0.6 → 0.6 (0.6). Base refused it.
- **Inside repeated rolled-up sub-assemblies** (the `repeated_rollup` shape, named leaf `l1 :> leaf` with `share = capital_cost / sum(leaf.capital_cost)`), in a usage and in the definition with one usage overriding `l1`: share 1.0 → 0.667 (0.667), and 0.5 for the overridden one; totals 90 and 160 on both rounds.
- **The `repeated_rollup` and `sibling_override_leak` fixtures:** byte-identical between rounds (whole-corpus check below).
- **A copy reading a sibling copy by index** (`servers#(2).power`, `servers#(2).disk.size`): refused `evidence_indexed_reference_unsupported` on all three trees, so B2 does not reach it.
- **A collection redefined in a usage with a larger count:** `part :>> servers[4] { :>> frac = power / sum(servers.power); }`. Total 4.0 → 1.0 (1.0).

### Should-fix

- **S3. A single-value read through a collection's name, written inside a copy, now refuses. The docs do not say so (`docs/architecture/modeling-assumptions.md:423`).**
  - Two shapes built on base and round 1 by reading the reader's own copy:
    - `servers : Server[2] { :>> x = servers.power * 1.0; }` gave 20.
    - `racks : Rack[2] { part psu; servers : Server[2] { load = power / racks.psu.cap; } }` gave 0.4.
  - Both now refuse with `occurrence_containment_step_ambiguous` ("reference='servers.power' … has 2 concrete occurrences").
  - That is the right answer under KerML, because the name means every member, and it fails closed. No corpus root and no dc3 file uses this shape.
  - But a modeler whose model built before now gets a refusal with no hint. The fix on their side is to drop the collection name (`power`, `psu.cap`).
  - What to change: add one sentence to the named-members section, and to the agentic-mbse guidance if it shows reads written inside a copy. It should say that writing the collection's name inside a copy means the whole collection, so a single-value read refuses, and that a copy reads its own value by the plain name.

### Notes

- **N6.** The `[MEMBERSHIP-LIST-IGNORED]` row (S1) and the D7 limit row (S2) now say what I measured and what the code refuses. The round-2 note explains why round 1's base value was wrong (`values.sh` ran the editable install for both sides). That fix is in `27037160`.
- **N7.** N1 is done: `child_members` is computed once per usage (`occurrence.py:1307`). The early `if not indices: return` it adds skips building a usage with zero copies; the suite and corpus show no change from it.

### Certification (round 2)

Checked, by running:

- **Default suite** in a worktree at `27037160`: 9 failed (the known `test_check_ledger_4a.py` ×8 and one `test_study_cli.py`), 8880 passed, 11 skipped.
- **`tests/execution/test_named_subset_members_teax.py`** with dc3's venv and `--noconftest`: 13 passed. `ruff check src/` and `mypy src/` are clean.
- **Whole corpus** (478 roots, the round-2 fixture list), round-1 `src/` against round-2 `src/`, with the receipt's `corpus_keys.py`. Each side gave 197 generated and 281 refused, no crashes. `diff -rq` differs in exactly the seven new `named_subset_members` fixtures the receipt names. So the corpus claim holds on every root, not only a sample.
- **dc3** at `8a98af8` (`git archive`, dc3 read only), generated with round-2 `src/`: `diff -rq` identical to the committed `exploration/ac_dc_baseline/dc3_baseline/`.
- **All 49 earlier probes** (`evidence/audit-probes/`, `evidence/review-shapes/`) on round 1 and round 2. They are identical except the B1 and B2 probes (k1, k2, a1, a4, a5, a6, a7), which now give the hand-worked values.
- **24 new probe models** on base, round 1 and round 2, all in real TEAx. They are in `/tmp/claude-1000/nsm-audit2/probes/` until that scratch folder is cleaned.

Not checked:

- native SysIDE values (the hand values come from KerML);
- dc3 at `HEAD`;
- models outside the corpus and dc3;
- a fresh product-lens run;
- whether agentic-mbse's guidance shows the single-value read S3 describes.

Spec checkboxes and `CURRENT_WORK.md` are untouched, because this audit writes only `audit.md`.
