# Design Review: F4 Aggregation-Resolution Cutover (+ graph_builder param-group typing)

**Design:** `.project/active/f4-cutover/design.md`
**Spec:** `.project/active/f4-cutover/spec.md`
**Review File:** `.project/active/f4-cutover/design-review.md`
**Date:** 2026-07-06
**Reviewer posture:** skeptical; claims verified against live code, not the design's account.

---

## Fundamental Assessment

**Sound.** The value/side-effect split is the right cut, and the design realizes the spec's
deferred Open Question ("where the reconciliation lives") with the cleaner of the two options.

- The pure resolver stays pure (`resolve_input` keeps its `(ref, ctx, strategies)` signature),
  which preserves the parity-suite contract that is the cutover's own safety net (INV-5). Widening
  `resolve_input` to own EP registration would have needed the frozen `ResolutionContext` to carry
  mutable EP dicts + `group_deriver` + a compilability channel — correctly rejected (D1).
- It adds exactly **one** new abstraction (`_build_agg_input_source`) plus one strategy (E), and
  reuses `_find_literal_redefinition`, `group_deriver.classify`, the four `AGG_STRATEGIES`, and the
  `InputSource`/`EntryPoint` models. No parallel mechanism, no premature generality.
- The three [HARD] spec outcomes (no key collision, no lost `MANUAL_REQUIRED`, byte-identical
  baseline) each map to a stated invariant (INV-1/2/4).

I verified the load-bearing claims against the code and they hold. The findings below are gaps in
**coverage and specification**, not a flawed foundation. Proceed to the dimensional review; no
Rework.

**Verified against code:**
- **B1 uniform key — CONFIRMED.** SumTerm `param_name = f"{part_usage}_{attr}"` (`graph_builder.py:1442`),
  SingletonTerm `source_path.replace(".","_")` (`:1533`), LocalTerm undotted `attr` (`:1652`). All
  three equal `ref.replace(".","_")`. Current `resolve_input` fallback is `ref.rsplit(".",1)[-1]`
  (`input_resolver.py:270`) — leaf-only, so it genuinely diverges on multi-dot refs, and the
  one-line fix closes it.
- **L3-1 blind spot — CONFIRMED.** `TestRegression` fallback branches assert only
  `source_type != "entry_point"` (`test_input_resolver.py:820-825` SumTerm, `:849-853`
  SingletonTerm). The EP `qualified_name` is never checked.
- **Side-effect inventory — CONFIRMED.** Literal default, register/dedup guard, backfill,
  `param_group` classify, `DESIGN_ATTRIBUTE` typing, and `MANUAL_REQUIRED` all present at
  `:1453-1493` / `:1562-1608`.
- **Step-5 param_groups dead — CONFIRMED.** The `:228` binding is not read before the `:331`
  rebind (Steps 6/6.5/6.6b/6.7 use `entry_points` + `group_deriver.classify` directly). 10
  baselines exist (`solar_battery` among them).

---

## Dimensional Review

### 1. Spec Compliance
**Assessment:** Concerns

Every [HARD] spec requirement has a design element, and the risky claims check out against code.
Two coverage gaps keep this off Pass:

- The spec's [HARD] M3 requires the gate compare "the full `InputSource` the call-site block
  produces … green before the rewire." The design satisfies *green-before-rewire*, but the gate is
  **deleted at cutover** and its "old" comparand is a **formula**, not the executed old block —
  leaving only the byte-identity baseline as the permanent guard of the reconciled key. See Major 1.
- The spec's Open Question on LocalTerm-EXPOSE says implement must "not reconcile it and break the
  agreement." The design honors that for the *fallback*, but the expose-alias **channel** rewire
  (`:1640`) now routes through `resolve_input`, which never returns `None`. The rewire needs an
  explicit `source_type == "module_output"` guard or LocalTerm's key/semantics drift. See Major 2.

### 2. Pattern Consistency
**Assessment:** Pass

Strategy E is in-idiom: `ChainRedefinitionFollow` already builds
`get_channel_name(f"{ctx.instance_path}__…", output)` and checks `canonical_channels`
(`input_resolver.py:184-188`), so E's `{instance_path}__{calc_path}` construction reuses the exact
pattern and the context already carries what it needs. The choke-point-helper + pure-resolver shape
matches the "pure typed resolver + compute-once build helper" house style the design cites.

### 3. Abstraction Quality
**Assessment:** Concerns

`_build_agg_input_source` earns its existence — it is the one place the side effects can live
without polluting the pure resolver. But the "**one** helper reproduces both SumTerm and
SingletonTerm" claim glosses a structural difference the helper must absorb:

- SumTerm always looks up the literal default from **pre-split** fields
  (`term.part_usage_name`, `term.attribute_name`, `:1455-1458`).
- SingletonTerm **guards** the lookup on `"." in source_path` and splits via `rsplit(".",1)`
  (`:1567-1572`); a dotless SingletonTerm skips the lookup and `literal_default` stays `None`.

The helper's stated interface ("the split `part_usage`/`attr`") must therefore accept a
"no split / attr = None → skip lookup" case, or the dotless SingletonTerm regresses. Under-specified
(Minor 4).

### 4. Duplication Avoidance
**Assessment:** Pass

Collapsing three inline `else:` blocks into one helper *removes* duplication. Deleting the orphan
`_group_entry_points_via_deriver` (its only caller is the dead Step-5 line) removes a second copy of
the derive→convert path. `_convert_derived_groups` stays shared (`:569`).

### 5. Data Structure Clarity
**Assessment:** Concerns

The helper returns `(InputSource, manual_required: bool)` — explicit and traceable. One implicit
precondition is unstated: `resolve_input` mints the fallback QN from **`ctx.module_eqn`**
(`input_resolver.py:271`), while the call sites use **`agg.module_eqn`** (`:1467`, `:1581`). The key
only matches if the helper builds `ctx` with `module_eqn = agg.module_eqn`. True today, but state it
so implement doesn't wire a `ctx` whose `module_eqn` is something else and silently shift every
fallback key (Note 5).

### 6. Route Safety
**Assessment:** Concerns

The asymmetry the design names — `resolve_input` never returns `None`, the old function returned
channel-or-`None` — is a routing hazard at the **LocalTerm expose-alias** call site (`:1640`).
Today `if channel:` distinguishes "found" from "not found." After the rewire, `resolve_input` always
returns an `InputSource`; its fallback `entry_point` is keyed on the **alias target**
(`alias_source`, e.g. `allocation_model.total_allocation`), not on `l_term.attribute_name`. If the
rewire treats the result as truthy-channel or uses its fallback, LocalTerm's EP key diverges from
`{module_eqn}__{attribute_name}` and it inherits literal-lookup / `MANUAL_REQUIRED` semantics D5
explicitly says it must not have. The safe route (take the channel **only** when
`source_type == "module_output"`, else fall through to LocalTerm's own inline fallback) is *implied*
by the architecture diagram but never stated as a guard. Make it explicit. See Major 2.

### 7. Bets & Decisions Integrity
**Assessment:** Concerns

Bets are mostly honest and each carries an "if false" — good. Two problems:

- **B3's mitigation is factually wrong.** B3 says "the M3 gate compares the full `InputSource` for
  **all three term types**." It does not. `TestRegression` iterates `sum_terms` and
  `singleton_terms` only (`test_input_resolver.py:798`, `:827`), and the design's own conformance
  test asserts LocalTerm is **not** routed through `resolve_input` (`:489`,
  `test_local_term_not_resolved_by_input_resolver`). So the LocalTerm expose-alias channel rewire —
  the one route that newly gains Strategy E **and** the self-ref guard — has **zero M3 coverage**;
  only byte-identity guards it. The design's own Risk section correctly assigns that reroute to
  byte-identity, which contradicts B3's "all three." Fix the bet's wording; consider extending the
  gate to the expose-alias path. See Major 3.
- **B4's mechanism claim is imprecise (harmless).** B4 says the non-float warning "fires again
  independently at Step 6.6." In fact it fires **only** at Step 6.6: `derive_groups()` calls
  `_warn_nonfloat_entry_points` (`parameter_groups.py:504`, `:524`), and Step 5's
  `derive_groups_filtered` (`:569`) does not. So there is no warning in the deleted path to lose —
  deletion is *safer* than the bet states, and the "asserted twice" worry is moot. Correct the
  framing (Note 6).

Decisions (D1–D5) each name a rejected alternative with a reason — genuine decisions, not mechanism
dressed as inevitable. D4 is correctly held contingent on the reproduced mypy error (R4).

**Hidden bet surfaced:** the design bets `ctx.module_eqn == agg.module_eqn` at every reconciled
call site (Note 5) — unstated, load-bearing for INV-1. Add it.

### 8. Reader Comprehension
**Assessment:** Pass

The Core Concept gives the value/side-effect frame before the mechanism, and the three-line mental
model lands. The one place a reader is misled is B3's "all three term types" (a false precision, not
a dense one) — fixing Major 3 fixes the comprehension issue too.

---

## Issues by Severity

### Critical
- None. The foundation is sound and the load-bearing claims verified against code.

### Major
1. **M3 gate leaves no permanent key guard, and the design contradicts itself on its fate.**
   Integration Strategy says the gate is "**deleted, not retired-in-place**," but Sequencing step (5)
   says only "**remove the M3 gate's old-function dependency**." These are different outcomes. The
   gate's "old" comparand is the formula `f"{agg.module_eqn}__{ref.replace('.','_')}"`, not the
   executed old block — so after deletion, the *only* thing guarding the reconciled part-usage EP key
   is the byte-identity baseline (regenerable, so a future regression + re-capture erases the guard).
   **Recommendation:** keep the **new-side** assertion —
   `_build_agg_input_source(...).qualified_name == f"{agg.module_eqn}__{ref.replace('.','_')}"` — as a
   *surviving* permanent test. It has **no** dependency on the deleted `_resolve_aggregation_input_channel`
   (only the "old" comparand does), so "cannot compile against a deleted function" does not force
   deleting it. Delete only the old-function comparison. This closes the permanent-guard gap and
   resolves the contradiction. — Dimensions 1, 7.

2. **LocalTerm expose-alias rewire needs an explicit `source_type == "module_output"` guard.**
   `resolve_input` never returns `None`; its fallback keys the EP on `alias_source`, not
   `attribute_name`. Without the guard the LocalTerm key diverges and it wrongly gains
   literal-lookup / `MANUAL_REQUIRED` semantics (violating D5 and INV-1). State the guard in the
   design; do not leave it implied. — Dimensions 1, 6.

3. **B3's "M3 gate covers all three term types" is false; the LocalTerm expose-alias reroute has no
   M3 coverage.** `TestRegression` covers SumTerm + SingletonTerm only; LocalTerm is explicitly not
   routed through `resolve_input` in the gate. Correct the bet, and either extend the gate to the
   expose-alias channel path or state plainly that byte-identity is its sole guard (and accept the
   Major-1 risk that byte-identity is regenerable). — Dimension 7.

### Minor
4. **Helper interface must absorb the dotless-SingletonTerm case.** SingletonTerm guards the literal
   lookup on `"." in source_path` and rsplit-splits; SumTerm uses pre-split fields. The "one helper"
   claim needs the helper to accept "no split / skip lookup, `literal_default = None`." Specify it. —
   Dimension 3.

5. **State the `ctx.module_eqn == agg.module_eqn` precondition.** `resolve_input:271` builds the
   fallback QN from `ctx.module_eqn`; call sites use `agg.module_eqn`. The helper must construct
   `ctx` with `module_eqn = agg.module_eqn` or every fallback key shifts. Unstated hidden bet. —
   Dimensions 5, 7.

### Notes
6. **B4 framing:** the non-float warning fires **only** at Step 6.6, never in the deleted Step 5
   (`parameter_groups.py:524` is reached via `derive_groups()`, not `derive_groups_filtered()`).
   Deletion is safer than the bet states; reword and drop the "asserted twice" worry.
7. **R4 mypy — I could not run mypy either** (approval-gated in this sandbox, same as the design
   author). The static read is plausible: both `_group_entry_points_via_deriver` (`:539`) and
   `_convert_derived_groups` (`:572`) return `list[ParameterGroup]`, so the comment's "typed from its
   earlier `DerivedParameterGroup` binding" (`:410`) is stale. But note line 413 reassigns
   `param_groups = sorted(...)` and line 412 mutates via `.sort()` on a Pydantic-model field — if the
   reproduced error is about *those* (not "unused ignore"), D4's fix shape changes. The design's
   reproduce-first stance is correct; just flag that the fix is not guaranteed to be "delete the
   ignores."
8. **Baseline "solar_battery is the only divergent-key carrier" — not independently re-verified.**
   Write/exec were gated in this sandbox, so I could not re-run the grep. Stakes are bounded: INV-4
   requires **all 10** baselines byte-identical, so any un-anticipated divergent baseline surfaces as
   a diff in the gate regardless of whether the "only solar_battery" claim is exact. Confirmed 10
   baselines exist. Treat the claim as a targeting hint, not a gate boundary.

---

## Recommendations

1. **Keep the new-side M3 assertion as a permanent test** (Major 1) — resolve the delete-vs-retire
   contradiction in favor of retaining `_build_agg_input_source(...).qualified_name == formula`,
   which needs no deleted function. This is the single highest-value change: it gives the reconciled
   EP key a guard that outlives the baseline.
2. **State the LocalTerm expose-alias `module_output`-only guard explicitly** (Major 2) and correct
   B3 so the LocalTerm coverage gap is honest (Major 3).
3. **Specify the helper's dotless-SingletonTerm branch and the `ctx.module_eqn` precondition**
   (Minors 4, 5).
4. **Reword B4** to "fires only at Step 6.6" (Note 6); carry R4/grep caveats into implement as-is
   (Notes 7, 8).

---

## Resolutions

_(Filled during Stage 4 as the user resolves each issue. None yet — headless review.)_

---

**Overall:** Revise
**Next Steps:** Once resolutions are recorded here, re-run `/_my_design` (or return to the
design-agent session) and point it at this review to incorporate. The reviewer does not edit the
design. The foundation is sound — these are coverage/specification fixes, chiefly the permanent
key-guard (Major 1) and the LocalTerm route guard (Major 2), not a Rework.
