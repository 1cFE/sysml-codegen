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

## Resolutions

*(To be filled during Stage 4, when the owner engages with this review.)*

---

**Overall:** **Needs-rework** — scoped to the ladder-unification half. The Gate A half (PC-1, D9,
Phases 0 and 2) is approved in mechanism, with M5–M7 as must-fixes to its plan.

C1, C2, C3, C5 are the must-fix set returning to the author under max-two-round discipline. M1–M7
should be addressed in the same pass: they are specification gaps in decisions already made, not new
decisions, so they cost a revision round rather than a rethink.

**Next Steps:** Record resolutions above, then re-run `/_my_design` (or return to the design-agent
session) and point it at this review to incorporate. The reviewer does not edit the design.
