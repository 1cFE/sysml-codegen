# Design Review: Lifecycle Item 2 — Shared Producer Resolution and Gate A

**Design:** `.project/active/constraint-lifecycle-shared-resolution/design.md`
**Spec:** `.project/active/constraint-lifecycle-shared-resolution/spec.md`
**Review File:** `.project/active/constraint-lifecycle-shared-resolution/design-review.md`
**Date:** 2026-07-19
**Reviewer:** independent design_review session (no authoring context)

**Method note.** Every claim below was checked against the code, not against the design's
description of it. Where the design cites a line range, I opened that range. `agentic-mbse` proper is
outside this session's sandbox; adapter fact shapes were read from the in-repo reference mirror at
`.project/reference/agentic-mbse-landed/` (synced Jul 12, post-`e352fd8`) and cross-checked against
committed snapshot JSON, which agrees. If upstream has drifted since Jul 12, finding M5 is the one
to re-verify.

---

## Fundamental Assessment

**Fail — Needs-rework**, on the ladder-unification half. The Gate A half is sound in mechanism.

The design has two separable halves and they get opposite verdicts.

**Gate A (PC-1, D9) — the diagnosis is right.** The adapter really does carry the usage on
`owner.owner` and the package on `owner.owning_definition`, exactly as described; the lowering code
really does discard the usage segment; all three design-attribute rungs build the keys the design
says they build. I confirmed each first-hand. The mechanism is correct. What it has are two concrete
defects (M5, M6), not a conceptual one.

**Ladder unification — the load-bearing argument is falsified.** The Core Concept rests on one
claim: each of the three guessing key forms has an *exact-identity twin already in the tree*, so the
guesses can be **deleted** rather than merely banned, at no coverage cost. That claim is the entire
justification for the merge — "the real argument for it" (`design.md:194`). I attacked it as the
brief directs. It fails for two of the three guesses:

- The calculation leaf-unique fallback is **not** covered by key form 12. The two build structurally
  different keys, `owner_def_qn` is frequently unavailable at the calc site, and two currently-passing
  tests break (C1).
- `_find_literal_redefinition`'s Strategy 2 is **not** subsumed by its own tier 1. The code makes
  them mutually exclusive: Strategy 2 fires *only* when the exact tier has no answer. D7's re-keying
  of `ChainRedefinitionFollow` fails identically (C2).

An exact tier that runs *before* a guess and falls through to it is a **predecessor**, not a twin.
The design reads the two as interchangeable, and that reading is what makes the deletions look safe.
Once it fails, bet B2 fails with it, and deletion inventory rows 2 and 5 become coverage losses
rather than simplifications.

Three further structural problems compound it: the resolver's proposed home in `core/` cannot hold
the data its own context requires (C3), the twelve-row table is an undercount of roughly half (C5),
and the "one mint point" collapse is specified with a result type that cannot carry what minting
needs (M1).

**The rework is bounded.** The tier/key-form *framing* is sound and worth keeping — this is not a
"start over" verdict. What fails is a specific empirical claim, and Recommendation 1 gives a route
that keeps the framing intact.

---

## Dimensional Review

### 1. Spec Compliance
**Assessment:** Concerns

Requirement coverage is broad and traceability is genuinely good — most requirements map to a named
decision or invariant, and the deletion inventory is keyed to SR-R41's six targets.

- **PC-2's replacement basis is correct, and I verified it independently.** The call chain is exactly
  as claimed and closed: `_build_agg_input_source` has two callers (`graph_builder.py:1412-1416`,
  `:1471-1475`), both inside `_build_aggregation_module`, whose only production caller is the Step
  6.7 loop at `:331-337`; `ComputationGraph` is constructed at `:436`, and nothing between `:337` and
  `:436` re-enters the aggregation path. **The backfill runs strictly before the graph exists.** D-1
  is not implicated, order-dependence is the real defect, and the design's reframing stands. One
  detail to record: the backfill at `:1333` reads `new_entry_points.get(ep_qn) or
  entry_points.get(ep_qn)`, so it can shadow an entry point created by the calc path, not just an
  earlier aggregation. The mutation is cross-source, which strengthens the order-dependence argument.
- **I9 is asserted, never mechanised.** SR-R23 / SR-A02 require two consumers of one design attribute
  to converge on **one** QN-keyed entry point. The design restates this as invariant I9
  (`design.md:442`) but no decision produces it. D8 derives the entry-point QN "from `consumer_eqn`
  and the reference" (`:387`) — which mints a *different* QN per consumer, the opposite of
  convergence. Convergence presumably happens on the `DESIGN_ATTRIBUTE` outcome path instead, but the
  design never says so. As written, I9 and D8 contradict each other.

### 2. Pattern Consistency
**Assessment:** Concerns

The design proposes a new `ResolutionContext` in `core/producer_resolution.py` (`design.md:324`). A
type of that exact name already exists at `resolution/input_resolver.py:40`, is imported by
`graph_builder.py:57`, and is constructed at `graph_builder.py:1397`. The deletion inventory removes
`resolve_input` and `AGG_STRATEGIES` but never says what happens to the existing `ResolutionContext`.
Two same-named context types in one tree is the drift this item exists to end.

Related, and sharper: see M5 on string-compare versus structural type testing.

### 3. Abstraction Quality
**Assessment:** Fail

See C3 and C5. D1's placement argument does not survive its own data contract, and the table is
specified at about half the granularity the code actually has.

### 4. Duplication Avoidance
**Assessment:** Concerns

The deletion inventory is thorough and the intent is right. But rows 2 and 5 delete live coverage
(C1, C2), and the `ResolutionContext` collision creates a duplicate rather than removing one.

### 5. Data Structure Clarity
**Assessment:** Concerns

`ProducerRequest` and `ProducerResolution` are clean as far as they go. `ProducerResolution` is
under-specified for the job D8 gives it (M1), and `ResolutionContext`'s membership is what breaks D1
(C3).

### 6. Route Safety
**Assessment:** Pass

The uniform self-reference guard (I6) is well-argued and the predicate really is identical on both
existing sites — `dependency_backtracker.py:745-754` and `input_resolver.py:263-271` both do
`channel.rsplit("__", 1)[0]` compared against consumer identity. Making a guard rejection *skip the
candidate and continue the table* (`design.md:371-372`) is a genuine improvement over both current
sites. B3 is plausible; I found no constraint shape that legitimately reads its own verdict channel.

The registry's exactness claim also holds: `core/output_registry.py:172-196` are four bare
`dict.get` calls with no case folding anywhere in the file, and the three raise sites are where the
design says. One correction worth carrying: `register_alias` (`:125-138`) is **not** a raise site —
it is first-wins with a DEBUG line and a recorded collision. The design's "the registry raises on
scoped/QN/scoped-alias collision" (`:141`) is accurate as written, but a reader may over-generalise
it to all four accessors.

### 7. Bets & Decisions Integrity
**Assessment:** Fail

- **B1 (extension, not rework):** the diagnosis is confirmed. The bet's stated reason survives better
  than I first thought — see M6 — but its *coverage* claim does not.
- **B2 (every key form is exact, guarded, or a guess with an existing twin):** **falsified.** C1 and
  C2 each break it independently. The design's own "if false" clause predicts the consequence
  precisely: "some consumer silently loses coverage at cutover."
- **B4 (identity-determined defaults):** plausible, unverified either way. R3's control (byte
  identity before commit) is the right one.
- **B5 (uniform warning needs no schema):** plausible. R5 correctly identifies that existing suites
  assert DEBUG silence and correctly records this as a behavior change, not a test fix.
- **Hidden bet, unstated:** *the three consumers' lenient entry-point QN formulas can be unified
  without moving bytes.* They are three different formulas today —
  `f"{usage_qualified_name}__{param_name}"` (`dependency_backtracker.py:76`),
  `f"{ctx.module_eqn}__{ref.replace('.', '_')}"` (`input_resolver.py:282-283`), and
  `f"{agg.module_eqn}__{l_term.attribute_name}"` (`graph_builder.py:1525`). D8 collapses them into
  one mint point without stating that they differ or which wins. R3 covers *defaults* moving; nothing
  covers entry-point *identity* moving, which is the larger byte-identity risk.
- **Second hidden bet:** *positive resolution is expressible as a pure key-form table.* It is not,
  today. `dependency_backtracker.py:635` mutates `self._fallback_entry_points` — the V11 collector —
  as a side effect of the lenient path. A `(key form) → channel` table cannot express that, and the
  design never says where the V11 collector's population moves to. Given that V11 cleanliness is the
  spec's stated stake ("a green V11 does not mean the graph is right"), this omission matters.

The verdicts on the spec's five bets each carry a real citation, and the four I spot-checked were
accurate at the cited locations. Credit where due.

### 8. Reader Comprehension
**Assessment:** Pass

Genuinely good, and it is what made these findings findable. The tier/key-form split is stated
plainly before the mechanism; the surfaced premise conflicts are placed before anything depends on
them, with epistemic status marked honestly (`design.md:39-44`); Appendix A gives a reader enough
provenance to check the table themselves — which is how C5 surfaced. The wrong claims are stated
crisply enough to test. That is the right failure mode for a design document.

---

## Issues by Severity

### Critical

**C1 — Key form 12 does not cover the deleted calculation leaf-unique fallback (B2 falsified).**
Deletion inventory row 2 deletes `dependency_backtracker.py:795-813` and `:831-856`, "covered by key
form 12" (the constraint ladder's `owner_def_qn` rung). Three independent reasons it does not.

*The key shapes never coincide.* Key form 12 builds
`f"{owner_def_qn}__{'__'.join(dotted.split('.'))}"` (`constraint_lowering.py:284`) and tests exact
membership in `design_attr_by_qn`. The leaf fallback is reached only when `"." in source_path`
(`:784`), so key form 12 would construct `{owner_def}__{parent}__{attr}`. But the entire point of the
leaf fallback is that the attribute is owned by an *unrelated* part def whose QN contains no
`{parent}` segment at all.

*`owner_def_qn` is frequently unavailable at the calc site.* The rung is hard-gated `if dotted and
owner_def_qn:` (`:283`). The calc analogue of that field is `CalcUsageData.owning_part_def_qn`
(`extraction/usage_extractor.py:125`), typed `str | None = None` and populated only when an owning
type is found (`:628-633`). Whenever it is None the rung is a no-op.

*Two currently-passing tests break.* `tests/unit/test_matcher_fixes_item7.py` builds its usage with
`owning_part_def_qn` unset:

- `test_def_owned_leaf_unique_resolves` (`:79-86`): `"magnet_holder.magnet_vol"` →
  `"Lib__MagnetPartDef__magnet_vol"`. Key form 12 would need `None__magnet_holder__magnet_vol`.
- `test_leaf_unique_ignores_calc_io_collision` (`:106-116`): `"driver.power"` →
  `"Lib__DriverDef__power"`. Same failure.

The other two tests in that group assert `None` and would still pass, but vacuously.

*Compounding it — a misclassified test.* The design calls the six tests at
`test_matcher_fixes_item7.py:79-137` "private-mechanics tests of deleted internals"
(`design.md:469`). `test_def_owned_leaf_unique_resolves` pins an *observable* resolution outcome.
Under SR-R43 its coverage must migrate, and the merged table has nowhere to migrate it to.

*And a safety filter.* The leaf fallback restricts its candidate pool via `_is_calc_def_owned`
(`:807`) specifically to stop a calc-def I/O attribute cross-wiring into a `DESIGN_ATTRIBUTE` entry
point. Key form 12 is a bare `in design_attr_by_qn` test with no such filter. D10 anticipates this by
keeping `_is_calc_def_owned` as a map-construction filter — good — but the design should confirm
that applying it at map construction is behaviour-neutral for the *constraint* consumers that read
the same map today unfiltered.

*Finally, the bare-name arm is not wholly a guess.* Only the multi-candidate tail (`:851-856`)
guesses. The `len(candidates) == 1` arm at `:842-843` is an unambiguous resolution. The inventory
deletes both as one unit.

**C2 — `_find_literal_redefinition`'s Strategy 2 is not subsumed by its own tier 1; the same defect
breaks D7.** Deletion inventory row 5 deletes Strategy 2, "covered by its own tier 1 (`:1226-1241`)."

The code makes them mutually exclusive. Strategy 2's leaf match at `graph_builder.py:1243-1245` runs
only in the `else` branch of `if target_partdef_qn is not None`, i.e. only when
`usage_type_map.get((owning_part_qn, part_usage))` returned nothing. The source comment says so
outright: *"A leaf-name match is structurally required in this fallback (there is no PartDef QN to
key on)."* Tier 1 is a predecessor that already ran and failed. Every pair Strategy 2 serves is by
definition a pair `usage_type_map` cannot answer.

**D7 fails identically, and the divergences are concrete.** `usage_type_map` is
`dict[(owning_partdef_qn, usage_name) → type_partdef_qn]` (`extraction/data_models.py:289-292`),
populated at `extraction/hierarchy_resolver.py:487-524` only for `PartUsage` members of a
`PartDefinition` with a resolvable owned `FeatureTyping`. Re-keying
`ChainRedefinitionFollow` to it loses:

- **Untyped usages.** `hierarchy_resolver.py:513-522` writes no entry when `winner` is None. Name
  matching resolves those today.
- **Multi-hop chains.** `_follow` recurses on `chain_redef.source_path` (`input_resolver.py:191`);
  the next hop's `part_usage` lives under a *different* owner def, and nothing tracks that def
  through the recursion. The key cannot be built past hop one.
- **`owning_part_qn` is not in scope.** `ChainRedefinitionFollow` sees only `ResolutionContext`
  (`:39-60`), which has no `owning_part_qn`. `_find_literal_redefinition` receives it as an explicit
  parameter (`graph_builder.py:1317`). Re-keying requires widening the frozen context — an interface
  change the design does not state.
- **A live empty-map fixture.** `resolution/supplied_values.py:256` records that fixture
  `plant_value_shapes` has an **empty** `usage_type_map`. Any chain in that shape resolves today by
  name and would resolve to nothing after the re-key. `plant_value_shapes` is in the byte-identity
  baseline set.
- **Snapshot lossiness.** `snapshot/loader.py:1148-1154` drops malformed `usage_type_map` keys with a
  warning. The name match has no snapshot dependency, so the re-key introduces a new offline-parity
  divergence — directly against SR-R30.

R4 lists the coverage question as a risk with test migration as its control, but the design presents
the re-keying itself as lossless. It is not, by construction.

**C3 — D1's `core/` placement is incompatible with the design's own `ResolutionContext`.**
`ResolutionContext` is specified to hold "the `OutputRegistry`, the by-QN design-attribute map
(filtered per D10), `redefinitions`, `usage_type_map`, and `canonical_channels`" (`design.md:326`).

`core/` is genuinely a strict leaf today — it imports only `core.*`, stdlib, `pydantic`, and
`agentic_mbse.sysml.qualified_names`. I confirmed that. But of the resolver's dependencies, only
`OutputRegistry` and `canonical_channels` live there:

| Dependency | Home | In `core/`? |
|---|---|---|
| `OutputRegistry`, `canonical_channels` | `core/output_registry.py` | yes |
| `RedefinitionData` / `RedefinitionType` | `extraction/data_models.py` | **no** |
| `DesignAttributeData` | `analysis/parameter_groups.py:78` | **no** |
| `InputSource` (aggregation's result type) | `resolution/models.py:119` | **no** |

A `core/producer_resolution.py` holding this context must import from `extraction/`, `analysis/`, and
`resolution/`, which destroys the strict-leaf property that is D1's entire justification ("cycle-free
by construction") and breaks the invariant `core/__init__.py:15` exists to protect. The rejected
alternative (`resolution/`) may in fact be correct, or the shared types need relocating first — a
wider blast radius than the design states. Either way D1 needs re-deriving against the real
dependency set.

**C5 — the twelve-row table undercounts the actual key forms by roughly half.** I2 makes the table's
declared order the drift-detection mechanism, so completeness is load-bearing: a key form that exists
in code but not in the table is exactly the drift I2 is meant to prevent. A faithful inventory of the
calculation ladder alone is fourteen forms, not the five and three Appendix A gives it:

- **Step 1c is two forms, not one.** `dependency_backtracker.py:678-680` tries
  `ScopedAliasKey((f"{consumer_scope}.{prefix}", leaf))`; `:682-684` falls back to
  `ScopedAliasKey((prefix, leaf))`.
- **The REFERENCE branch is five forms, not one.** `:735-737` does
  `sysml_qn_lookup(sanitize_qualified_name(source_path))`, then `_resolve_reference_via_registry`
  (`:531-560`) adds four more — `scoped_lookup(parent_part.leaf)` `:544`,
  `alias_lookup(parent_part.leaf)` `:546`, `scoped_lookup(consumer_scope.leaf)` `:554`,
  `alias_lookup(consumer_scope.leaf)` `:556` — each preceded by a leaf-extraction normalization at
  `:533-538`. Appendix A dismisses this whole branch as "subsumed by key forms 1 and 3 once the
  reference is not pre-split" (`design.md:636-637`), which is an assertion, not a derivation, and
  it is the same shape of claim that C1 and C2 falsified.
- **Aggregation Strategy A is four forms** (scoped + alias, each over scoped-prefixed and unscoped —
  `input_resolver.py:86-101`), listed as one.

Two structural mismatches beyond the count:

- **The scope climb is not an ordered lookup rung.** `:715-723` collects *every* distinct hit into a
  set and returns only if `len(climbed) == 1`. It is an ambiguity-refusing tier. Modeling it as row 9
  of an ordered table loses the guard that D6 correctly identifies as its whole justification. It
  also re-tries keys already tried — the loop `range(len(scope_segments), -1, -1)` includes both the
  Step-1 key and the Step-1b key — so its key set is a *superset* of two earlier rows.
- **Side effects have no home.** `_is_self_reference` filters every rung and emits DEBUG; `:635`
  mutates the V11 collector `self._fallback_entry_points`. A pure table expresses neither.

### Major

**M1 — `ProducerResolution` cannot carry what D8's mint point must produce.** D8 makes the single
lenient terminal-miss site responsible for minting the entry point. Today's mint sites build a full
`EntryPoint` with `qualified_name`, `simple_name`, `entry_type`, `default_value`, `param_group` (via
`group_deriver.classify(ep_qn)`), and `source_calc_usage` — `graph_builder.py:1322-1329` and
`:1526-1533`. `ProducerResolution` carries only `identity` and `default_value`. Either the result type
grows those fields, or the context grows a `group_deriver` (worsening C3), or minting stays with the
consumer and "one mint point" is weaker than stated. Say which.

**M2 — the three lenient entry-point QN formulas are not reconciled.** See the hidden bet in
Dimension 7. The largest untracked byte-identity risk in the plan, and no risk entry covers it.

**M3 — I9 has no mechanism.** See Dimension 1. Name where convergence happens, or drop I9 and record
SR-A02 as unaddressed.

**M4 — `ResolutionContext` name collision.** Name the fate of the existing type.

**M5 — `owner.owner.kind == "PartUsage"` is a fragile predicate that fails closed and silently.**
This is D9's branch condition, and it type-checks fine — `IdentityFact.kind` is `str | None`. But it
is not comparing against a controlled vocabulary. `constraint_extraction.py:193-200` sets
`kind=type(element).__name__` — the Python class name of the live syside object, an **open set
determined by the syside runtime**, not by agentic-mbse. Contrast `owning_definition.kind`, which
*is* a closed set fixed at `constraint_extraction.py:98-103`
(`part_def`/`calc_def`/`requirement_def`/`package`). Two vocabularies behind the same field name.

Everywhere else the extractor tests type identity structurally — `_owning_definition` uses
`SysideAdapter.is_instance(current, type_name)` (`constraint_extraction.py:617`). A string compare
against a runtime class name breaks on any syside subclass or rename, and it fails *closed into the
old package branch* with no error. The existing dispatch at least has a `raise RuntimeError` for an
unknown kind; the proposed predicate has no backstop. Recommend a structural test, or at minimum an
explicit `else` that raises rather than silently falling through, plus a `None` guard (`owner.owner`
is `IdentityFact | None` and snapshot restore preserves JSON `null`).

**M6 — the `part_usage` branch has no live fixture coverage, and neither does the path it displaces.**
The design asserts "no existing fixture should move, since no existing constraint is usage-owned"
(`design.md:574`) and makes any byte movement a stop-and-surface condition.

The premise is factually wrong but the conclusion happens to hold, for a reason the design does not
know. There **are** nine PartUsage-owned constraints — all in `catf_mfe_model`, at snapshot lines
478, 660, 1067, 1339, 1654, 1699, 2869, 2914, 2959, and they are exactly the nine
`owning_definition.kind == "package"` entries. The design's own PC-1 evidence at `:658-668` is one of
them. They will not move bytes because all 65 catf constraints are `plain_usage` form and land
`unassessed_form`, so `is_excluded_usage` short-circuits at `constraint_lowering.py:761` *before* the
owner branch is consulted — pinned by
`tests/conformance/test_constraint_migration_mapping.py:104-117`. `catf_mfe` is in the byte-identity
baseline set, so this mattered.

Two consequences the design should confront:

- The new branch has **zero currently-passing cases to preserve** — which is good for B1, and is the
  correct argument for "extension, not rework." The design should make *this* argument rather than
  the factually wrong "no existing constraint is usage-owned."
- It also has **zero live fixture coverage** until Phase 0's new fixture exists, and the surviving
  package branch has zero coverage for a *genuinely* package-owned constraint — one declared directly
  in a package body, which would have `owner.owner.kind == "Package"`, not `None`. No fixture
  exercises that shape anywhere in the repo. After the change, the `else` path is untested. Phase 2's
  validation should add that case, not just the Gate A case.

**M7 — `_expand_package_owner` is misquoted, and the dropped clause is load-bearing.** The design
quotes `((sanitize_qualified_name(usage.identity.qualified_name), ""),)` (`design.md:58-59`). The
actual code at `constraint_lowering.py:458-461` is
`((sanitize_qualified_name(usage.identity.qualified_name or owner_qn), ""),)`. Since
`identity.qualified_name` is `str | None`, the `or owner_qn` fallback carries anonymous usages. Small
in itself, but this is the function the new branch sits in front of, so the quote should be exact.

### Minor

- **m1 — line-reference drift on the precedence pins.** The design cites
  `test_constraint_resolver.py:305-420` (`design.md:474`); the spec says `:283-420` (SR-R33); the six
  `test_precedence_*` functions actually start at `:303`. SR-R33 makes these the migration guard, so
  the range should be exact.
- **m2 — Appendix A's rung-5 aliasing note** (`design.md:653-656`) identifies a real latent bug — a
  value comparison standing in for a position index — and correctly says the merged table should
  discriminate positionally. It is not carried into any key-form spec or invariant. Carry it, or it
  will be lost.
- **m3 — `_find_literal_redefinition` has an unnoticed abort.** `graph_builder.py:1250-1251`
  (`except (ValueError, TypeError): return None`) aborts the whole scan on the first non-numeric
  literal rather than skipping that redefinition. Whatever replaces this function should not
  reproduce it by accident.
- **m4 — the Strategy 2 warning is conditional.** It fires only `if len(set(strategy2_hits)) > 1`
  (`:1258`), so a single leaf hit returns silently. The design describes it as a
  "warn-and-return-first arm" (`:1246`), which overstates how visible it is today — relevant to
  R5's warning-volume estimate.

---

## Recommendations

1. **Re-derive the exact-twin argument before anything else.** C1 and C2 falsify it on two of three
   guesses. Three options, in the order I would try them: (a) find a *real* exact key form covering
   the def-owned and no-type-map populations — plausibly a design-attribute map indexed by the
   attribute's **own** owning definition rather than the consumer's; (b) keep both fallbacks as
   declared, ambiguity-guarded key forms and record them as SR-R41 deviations with this reason; (c)
   accept the coverage loss and enumerate it.

   **I recommend (b).** Both already implement I3's "multiple candidates yield no result" discipline
   — the leaf fallback returns `None` unless `len(cands) == 1` (`:802-813`), which puts it closer to
   D6's scope climb than to a guess. The genuinely indefensible behaviors are narrower than the
   inventory claims: the multi-candidate first-pick (`:851-856`) and the warn-and-return-first
   collision arm (`:1257-1267`). Delete those two; keep the unique-match arms as declared key forms.
   This preserves the design's framing and most of its deletions, and it is honest about what SR-R12
   actually forbids — guessing among candidates, not name-based candidate *identification*.
2. **Rebuild the key-form table from the code, not from Appendix A (C5).** Derive it by enumerating
   every lookup call in the three ladders. Decide explicitly where the ambiguity-refusing climb and
   the V11-collector side effect live, since neither is a table row.
3. **Re-derive D1 against the real dependency set (C3).** `resolution/` may be correct after all, or
   the shared types move to `core/` first. State which, and why the resulting cycle is manageable.
4. **Specify the mint point completely (M1, M2, M3).** Name the surviving entry-point QN formula, the
   fields the result carries, and where two consumers converge.
5. **Keep the Gate A work, with M5–M7 folded in.** PC-1's diagnosis is confirmed at the adapter level
   and D9's mechanism is right. Phase 0's stop condition is well-designed and should stay. Restate
   B1's argument on the true ground (no admitted usage-owned constraint exists today), harden the
   branch predicate, and add a genuinely-package-owned case to Phase 2's validation.

---

## Round-1 verdict (superseded)

**Needs-rework**, scoped to the ladder-unification half; Gate A approved in mechanism. C1, C2, C3,
C5 were the must-fix set; M1–M7 were specification gaps in decisions already made. See the Round-2
record below for dispositions.

---

# Round 2 — Verification of the Revision

**Design under review:** `design.md` rev 2 (Draft rev 2, revised 2026-07-19)
**Scope:** narrow. The seven items named by the author, verified against code. I did not re-review
anything already settled in round 1.
**Method:** every disposition below was checked at the cited code, first-hand. Where I could not get
a type-level guarantee I say so and name what the evidence actually is.

## Item-by-item

### 1. Deletion narrowing — **Accepted except deletion row 5, which is blocking**

> **Correction to this review.** I first recorded item 1 as fully accepted and issued an
> Approve-with-notes verdict. A verification pass that completed after that write-up surfaced the
> finding below; I confirmed it first-hand and am amending. The verdict is now
> Approve-with-revisions. The premature verdict was my error, not a change in the design.

**B1 — D7's case-sensitivity change is a coverage removal, not a leniency removal.** This is the one
genuinely blocking item.

Deletion row 5 kills `ChainRedefinitionFollow`'s case-insensitivity along with its first-`break`,
on the reasoning that "only the case-insensitivity and the first-`break` are indefensible"
(`design.md:275-276`). The first-`break` is indefensible. The `.lower()` is not — it is the
**PartDef→PartUsage naming bridge**.

`input_resolver.py:176-177` compares `sanitize_name(redef_part_name).lower()` against
`part_usage.lower()`. Part defs are PascalCase and part usages are snake_case (ADR-002), so the two
sides are *systematically* different in case and the fold is what makes them meet. `sanitize_name`
does not lowercase — if it did, the explicit `.lower()` on both sides would be dead code.

A currently-passing test pins exactly this, `tests/unit/test_graph_builder_aggregation.py:125-143`:

```python
redefs = [_make_chain_redef("capital_cost", "cost_model.total_cost", "Lib__PV_Module")]
result = _resolve_channel("pv_module.capital_cost", "Design__plant__solar_array", redefs, registry)
assert result == expected_channel
```

Last segment `PV_Module` versus reference part `pv_module`. Case-sensitive, Strategy C never fires
and the assertion fails. The same break lands on
`test_graph_builder_aggregation.py:192-210` and `tests/conformance/test_input_resolver.py:391-411`,
and `test_input_resolver.py:717-747`'s cycle-detection test degrades to passing vacuously because no
match is ever found. The live `solar_battery_model` fixture carries the same shape
(`owning_part_qn: "SolarBatteryLibrary__PV_Module"` against usage `pv_module`).

This is the same class of error round 1 caught twice: a name-based mechanism read as sloppiness when
it is in fact carrying real coverage. It is also *undeclared* — the design explicitly declares the
`test_silent_failure_family3` break and migrates it, but says nothing about these, which is what
makes this blocking rather than a note.

**Fix.** Keep the case fold; delete only the first-`break`, re-typed to collect and refuse on
multiple. That is the same treatment rows 18/19/20 already get and it is consistent with
Recommendation 1(b): the fold is name-based *identification*, which SR-R12 permits; the `break` is
the guess, which it forbids. If the fold is instead judged unsafe, that is a separate coverage
decision needing its own enumeration — not something to carry inside a deletion row.

---

**The rest of item 1 — Accepted**

The narrowed set is the right cut. SR-R12 forbids *guessing among candidates*, not name-based
candidate identification, and the four surviving deletions are exactly the guess set:
`dependency_backtracker.py:846-856` (same-file tiebreak + `candidates[0]`), `:790-793` first-hit,
`graph_builder.py:1257-1267` warn-and-return-first, `input_resolver.py:171-179` case-insensitive
first-`break`. Rows 18/19/20 give the C1 tests somewhere real to land. The retained-with-reason list
is properly recorded as SR-R41 deviations rather than silently kept.

**The declared test break is handled honestly.** `test_silent_failure_family3.py:73-86` asserts
`value == 100.0  # first-wins preserved` and will return `None` under deletion row 4. The design says
so and migrates the assertion to refusal rather than quietly dropping the test. That is the correct
treatment.

Two notes, neither blocking:

- **n1 — row 4's refusal flips compilability, which the design does not spell out.**
  `graph_builder.py:1320` is `manual_required = literal_default is None`, and `:1390`/`:1422` turn
  that into `Compilability.MANUAL_REQUIRED`. So a leaf collision that today yields `100.0` will
  yield `None` and re-label the module. It is enumerable and Phase 5's byte-identity gate catches it,
  but it should appear in the forced-difference list up front, not be discovered at the gate.
- **n2 — row 18's re-typing has no test pin.** No test exercises the dotted exact `(name,
  parent_part)` arm with multiple matches; the item7 tests all use `parent_part=""` (routing to row
  19) or `::` paths. Since `parent_part` is a bare part name, not a QN, two attributes named `gain`
  under a part named `the_host` in different packages collide, and today's first-hit silently picks
  one. The change is real and its only detector is byte identity. Add a unit pin for row 18's
  refusal in Phase 1.

### 2. D1 — **Accepted, with one correction to the stated argument**

`core/__init__.py:10` does declare `resolution → extraction, analysis, core`, and
`resolution/` is genuinely the lowest layer that may legally see all six types. The deferred-import
precedent is real: `constraint_lowering.py:1396` already does
`from sysml_codegen.resolution.graph_builder import _validate_channel_references,
collect_uncovered_params`. So the placement is legal and the precedent is accurate.

**But the cycle argument is not yet fully honest.** `core/__init__.py:15` names "analysis importing
from resolution" as precisely the layer violation the `core/` package exists to prevent. The
constraint consumer's use of the new module *is* that violation, deferred. More pointedly, rev 1
rejected `resolution/` on the grounds that "analysis↔resolution is already a managed cycle; a third
participant makes it worse" — and rev 2 reverses that judgement without addressing its own prior
reasoning. The reversal is correct (rev 1's `core/` choice was strictly worse), but D1 should say
plainly that it adds a second deferred edge to a pre-existing cycle, rather than presenting
`resolution/` as clean. One sentence.

### 3. Table recount — **Spot-checks confirm**

I checked the load-bearing pieces rather than recounting all ~24:

- **"All eleven constraint lookups are exact" — CONFIRMED**, and this is the linchpin for item 7.
  `resolve_actual` (`constraint_lowering.py:143-300`) uses only `registry.scoped_lookup`,
  `alias_lookup`, and `scoped_alias_lookup` — all bare dict lookups — plus three
  `in design_attr_by_qn` membership tests. No name-based scan anywhere in the function.
- **The scoped-alias double-fire is real.** At `:219-224`, `key_prefix = deindexed_prefix if
  scope_candidate == deindexed_scope else prefix`. When `occ_scope == deindexed_scope` the
  discriminator is true on both iterations and the identical lookup fires twice. Appendix A's m2 note
  is accurate and D2 correctly carries it as positional discrimination.
- **Appendix A is now derived from code rather than asserted.** The rev-1 defect was a claim
  ("subsumed by key forms 1 and 3") standing in for a derivation. Rev 2 gives the calls with line
  numbers and records the consequence it found along the way — that `Pkg::PartA::x` and
  `Pkg::PartB::x` construct identical keys because the reference's own owner is never consulted.
  That is the kind of fact a faithful inventory produces and an asserted one does not.

### 4. D9's QN rule — **Verified against all three sites; one residual**

The rule is `f"{consumer_eqn}__{param_name}"`, `param_name` = the consumer's formal where it has
one, else `ref.replace(".", "_")`.

- **Site 1 exact.** `dependency_backtracker.py:626-631` calls
  `terminal_disposition(usage_qualified_name=usage.qualified_name, param_name=param_name, ...)`,
  which returns `f"{usage_qualified_name}__{param_name}"` (`:76`). Calc bindings have formals.
  Reproduced.
- **Site 2 exact.** `input_resolver.py:281-283` is `param_name = ref.replace(".", "_")`;
  `ep_qn = f"{ctx.module_eqn}__{param_name}"`. Aggregation terms have no formal, so the rule's
  else-branch is literally today's code. Reproduced.
- **Site 3 rests on `LocalTerm.attribute_name` being dotless — true, but by construction and
  observation, not by type.** `graph_builder.py:1525` is
  `f"{agg.module_eqn}__{l_term.attribute_name}"`, which matches the rule only if
  `attribute_name.replace(".", "_") == attribute_name`. The structural argument is good:
  `hierarchy_resolver.py:274-281` splits `FeatureChainNode` (dotted, carries `source_path`,
  becomes a `SingletonTerm`) from `FeatureReferenceNode` (carries `attribute_name`, becomes a
  `LocalTerm`) — chain versus plain is exactly the distinction. Empirically every `attribute_name`
  across all fixtures is dotless (`d38_caret`, `solar_battery_model` are the only non-empty
  `local_terms`). But the field is a bare `str` with no invariant enforcing it.

  **This is fine as designed** — B4 names it the largest byte-identity risk and Phase 1 pins the rule
  against all three formulas *before* any cutover, which is exactly the right control and the right
  place. Worth adding the dotless assumption to the pin explicitly so a future chain-shaped
  `attribute_name` fails the unit test rather than the baseline gate.

### 5. D8 — **Sound**

The downgrade is honest and correct. `group_deriver` genuinely is absent at two of three mint sites,
and pulling `ParameterGroupDeriver` into the context would drag `analysis` into a type `analysis`
must import — the same defect that killed rev 1's `core/` placement. Splitting QN-and-default
(resolver) from `EntryPoint` construction (consumer) puts each where its data already is. Calling
"one mint point" what it actually is — one QN and default authority — is the right correction.

The order-dependence deletion still holds under the weaker claim: D9 makes lenient QNs
consumer-prefixed, so within a consumer the same identity always yields the same default, and I5 is
satisfied without the backfill.

- **n3 — cross-consumer QN collision is unspecified.** PC-2 observed that today's backfill can shadow
  an entry point created by the *calculation* path, which means calc and aggregation QNs do collide
  in practice. Under D8 each consumer computes its own default for a colliding QN, and the design
  does not say who wins. I5's "a function of its identity and the reference that mints it" is
  ambiguous when two references mint one identity. Phase 5's stop condition catches it empirically;
  a sentence in I5 would catch it by construction.

### 6. PC-3 / I10 — **Confirmed exactly as claimed**

The one-writer claim is true. `_fallback_entry_points.add` appears exactly once in the tree, at
`dependency_backtracker.py:635`, on the calculation Step-4 fall-through. Every other reference is
init (`:226`), reset (`:261`), read-out (`:354`), a copy into the graph (`graph_builder.py:440`), a
copy onto the extended graph (`constraint_lowering.py:1538`), or a read by the two collectors
(`:829`, `:869`). Nothing in `graph_builder.py` or `input_resolver.py` ever writes it. Aggregation
entry points are invisible to V11 today.

The `records_v11` mechanism reproduces that scope exactly: today's add is unconditional on the calc
lenient path, so `records_v11 = True` for every calculation lenient miss and False elsewhere is
byte-equivalent. Phase 4's stop condition ("any change in `fallback_entry_points` membership") is the
right guard, and routing the widening question to Item 3 under SR-R07 is the correct disposition —
this is a coverage-scope decision, and Item 2 deciding it silently by refactor is exactly what the
epic's item boundaries exist to prevent.

**This was a good catch.** It is the kind of finding that only surfaces from rebuilding an inventory
rather than trusting one, and it would have turned green fixtures red at Phase 5 with no obvious
cause.

### 7. D11 as a second policy axis — **Acceptable as a recorded design refinement; no spec amendment
required before implementation, but one should be queued**

The byte-preserving claim is verified: all eleven `resolve_actual` lookups are exact (item 3), so
declaring name-based forms lenient-only forbids nothing the constraint consumer does today. The
restriction is declared as data on one table, not as three code paths, so it does not reintroduce the
consumer-specific ladders contract invariant 20 bans.

It does refine SR-R14's "terminal miss is the only place strict and lenient differ." My read: this is
a **refinement of an `[INHERITED]` requirement's text, with zero behavioral effect today**, and the
design surfaced it rather than letting it pass as an implementation detail — which is the correct
handling under the surfacing duty. That is enough to proceed.

Queue the amendment alongside the SR-R16 basis correction the design already flags, so SR-R14 ends up
reading "strict and lenient differ at terminal miss and in declared key-form admissibility." Two
requirement-text corrections in one spec pass, both discovered by design, both recorded — that is the
pipeline working as intended, not debt.

## What changed my verdict

Round 1's blocking findings were all empirical claims that failed against code. Every one is now
either withdrawn (the exact-twin argument), re-derived (D1, the table, D9), or downgraded honestly
(D8). The revision does not argue with the findings; it re-verified them independently and acted.
The one place it pushed back — C1's last point about `_is_calc_def_owned` at map construction — it
pushed back correctly, and D12 is better than what I suggested.

Nothing remaining is blocking. n1–n3 and the item-1/2/4 notes are all "state this explicitly" or
"add a pin," addressable during implementation without another review round.

---

## Resolutions

*(To be filled during Stage 4, when the owner engages with this review.)*

---

**Overall:** **Approve-with-revisions.** One blocking item.

**Blocking — B1 (deletion row 5).** D7's case-sensitivity change removes the PartDef→PartUsage
naming bridge, not a leniency. Three currently-passing tests fail and a fourth degrades to vacuous;
the live `solar_battery_model` shape is affected; and unlike the other declared break, this one is
undeclared. Keep the case fold, delete only the first-`break` (collect and refuse on multiple). This
is a one-line correction to D7 plus a deletion-inventory row, not a re-derivation — it does not
reopen the round-2 approval of items 2–7.

Two smaller corrections to fold in with it: Appendix A cites `graph_builder.py:1257-1267` where the
arm is `:1258-1268`, and D6 (`:272`) says the climb skips the iterations duplicating "rows 1 and 2"
where the table note and Appendix A correctly say rows 1 and 3.

**Non-blocking — fold into implementation without a further review round:**

1. **n1** — add row 4's compilability flip to the forced-difference enumeration up front (Phase 5).
2. **n2** — add a Phase 1 unit pin for row 18's refusal-on-multiple; it has no coverage today.
3. **Item 4** — make the dotless-`attribute_name` assumption explicit in Phase 1's D9 pin, so a
   chain-shaped `LocalTerm` fails a unit test rather than the baseline gate.
4. **n3** — one sentence in I5 on which consumer's default wins if two mint the same QN.
5. **Item 2** — one sentence in D1 acknowledging that it adds a second deferred edge to the
   pre-existing analysis↔resolution cycle, reversing rev 1's own stated reason for rejecting
   `resolution/`.
6. **Item 7** — queue the SR-R14 amendment with the SR-R16 one for the next spec pass.

**Next Steps:** Record any owner resolutions above, then proceed to `/_my_implement` against the
phased plan in `design.md`. The de-risk order in the handoff is right: PC-1 via Phase 0's stop
condition, then D9's QN rule via Phase 1's pins, before any consumer is cut over.
