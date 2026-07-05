# Design Review: Part-Usage Type Indexing (SC-3)

**Design:** `.project/active/type-indexing/design.md`
**Spec:** `.project/active/type-indexing/spec.md`
**Spec review:** `.project/active/type-indexing/spec-review.md`
**Review File:** `.project/active/type-indexing/design-review.md`
**Date:** 2026-07-05
**Reviewed against committed state at base commit `5a860e0`** (working-tree churn from Item 3 ignored per instruction).

---

## Fundamental Assessment

**Sound.** The design does the minimal right thing. Two sites picked a usage's type by list
position (`next(iter(usage.types))`); the design replaces both with a heritage-walk over owned
`FeatureTyping` relationships — reusing the in-repo precedent (`_get_calc_def_name`,
`extractor.py:316-326`) rather than inventing machinery. The three fixes (superset index,
most-specific `usage_type_map`, collision tiebreak at the existing `seen_qns` dedup) each land at
the exact spot the bug lives, and the "probe first" discipline gates the one load-bearing bet (B1)
before any code. No new abstraction is unjustified: one shared heritage helper replaces the
duplication that let the two sites drift into the same bug. This is not over-engineered.

I would not recommend rework. The approach is right. But the design ships with **one must-fix
factual collision, one wrong type choice, and two probe/argument gaps** that need decisions before
the plan runs. Details below.

---

## Dimensional Review

### 1. Spec Compliance
**Assessment:** Concerns

Every settled spec ruling has a design element: superset index (REQ-EXT-13), collision tiebreak
(REQ-EXT-14), most-specific `usage_type_map` (REQ-LVP-08), the 6-shape fixture matrix, the
runtime zero-diff proof, and the agentic-mbse carry-through. The one behavioral consumer
(`_find_literal_redefinition`) is correctly identified and its non-behavioral readers traced. Good.

The concern is **the V-number assignment, which is now factually wrong** (see Critical C1). The
design assigns V8/V9 based on `modeling-assumptions.md:344-350` ending at V7. But Item 3, which
lands first, already claims **V8** for its anonymous-return diagnostic
(`return-style-extraction/design.md:17-18,89-90`). Item 4 must renumber to **V9/V10**. This is
not a style nit — the design threads V8/V9 through five places (Core Concept, D2, D3, Component
Overview, Implementation Notes warning texts, Docs plan, Next-Stage Handoff), all of which shift.

### 2. Pattern Consistency
**Assessment:** Pass

The heritage-walk reuses `_get_calc_def_name`'s pattern. Warnings append to the existing
`warnings` lists and `logger.warning`, matching `usage_extractor.py:314-315`. The tiebreak reuses
the existing `seen_qns` dedup site rather than a bolt-on post-pass (D3 correctly rejects the
post-pass). The `most_specific` specialization walk reuses the same `heritage`/`Specialization`
traversal. Nothing invents a new pattern where an existing one fits.

### 3. Abstraction Quality
**Assessment:** Pass

Three small helpers, each earning its place:
- `owned_feature_typing_targets(usage)` — the shared primitive both sites consume.
- `user_partdef_types(usage, user_qn_set)` — the index-only projection.
- `most_specific(qns, model)` — used by both `usage_type_map` (V-warn) and the tiebreak.

D1 correctly rejects the two tempting over-abstractions: (a) duplicating the walk (the original
sin), and (b) a threaded cross-stage usage→type cache (cross-stage coupling the 1-day budget does
not want). The "compute-once" R1 discipline is satisfied by centralizing the *logic*, not by a
runtime cache — a clean reading of R1. No note.

### 4. Duplication Avoidance
**Assessment:** Pass

The whole point of the shared helper is to kill the duplication that produced two copies of the
same position-pick bug. Correct call.

### 5. Data Structure Clarity
**Assessment:** Concerns

Two issues.

- **The `SysMLQN` type is the wrong wrapper (see Major M1).** `identifier_types.py:22` defines
  `SysMLQN` as the **`::`-separated** QN form ("SysML qualified name with `::` separator"). But
  the index keys and `usage_type_map` values are produced by `build_element_qualified_name(...)`,
  whose default `use_double_underscore=True` (`qualified_names.py:39,52`) yields the
  **`__`-separated** form. The design's Research Finding (design.md:63-65) asserts these are
  "PartDef qualified names — i.e. `SysMLQN`," which is false on the separator. The existing
  `dict[SysMLQN, CanonicalChannel]` in `output_registry.py:42` really does hold `::`-keys — so
  labeling `__`-form keys `SysMLQN` is inconsistent with the one existing use, and defeats the
  purpose of the NewType (which exists to *catch* separator confusion).

- **The `seen_qns` dict value type is under-specified.** D3 says `dict[str, CalcUsageData]`
  (QN → winning virtual). That is workable — the stored virtual carries `owning_part_def_qn`
  (`_create_virtual_calc_usage`, line 266), which is what the tiebreak compares. But the design
  should state that the comparison key is the *stored virtual's* `owning_part_def_qn`, not re-derive
  it. Minor; noted so the plan doesn't guess.

### 6. Route Safety
**Assessment:** Concerns

The double-instantiation route is the sharp edge, and the design *does* guard it — but the argument
should be made explicit in an invariant, because it is subtle.

- **A single template only ever reads one index key.** `_find_instantiation_paths` is called with
  `template.owning_part_def_qn` (line 317) and, at each recursion level, reads
  `index[<ownership-parent PartDef QN>]` — it walks the *ownership* chain, never the *type-variant*
  keys. So superset indexing (a usage under both `IFE Driver` and `HIF Driver`) does **not** cause
  one template to be "reached via two keys." The concern that a same template double-instantiates
  via two index keys does not arise from the index structure.
- **Cross-template collisions are the real case, and `seen_qns` catches them.** Two *different*
  templates (IFE-owned and HIF-owned, same instance name) reaching the same instantiation path
  produce the same virtual QN and meet at `seen_qns` — exactly the tiebreak point. Confirmed: the
  virtual QN is `{path}__{calc_name}` (line 246-247) and the path is identical because both resolve
  to the same retyped usage. **This is genuinely "same virtual QN, different owners"** — the
  collision class the spec means. D3's dict lets the second arrival be compared instead of dropped;
  same-owner re-arrival stays silent (idempotent multi-path). Adequate.
- **One implementation guard to state:** the per-usage key set must be a **union** (set), because
  the declared type is *both* an owned FeatureTyping target and a member of `usage.types` — naive
  concatenation would list the usage twice under that key. It is backstopped by `seen_paths` inside
  `_find_instantiation_paths` and by `seen_qns`, so it cannot produce a double virtual — but INV-1
  should say "set," and the plan should build a set.

One edge the design does not address: a **3-owner collision on one QN** (a 3-level chain
IFE→MID→HIF all owning a same-named template). D3 reduces pairwise at the dict; pairwise
most-specific converges to the sink on a chain (fine), but the V-warning dedup key
`(owner_a, owner_b, calc_name)` could emit more than one warning, or name a non-winning pair, for
a 3-way collision. Out of the pinned fixture matrix (shapes 3/4 are 2-owner). Minor — call it a
known limitation or add a 3-owner note, don't build for it.

### 7. Bets & Decisions Integrity
**Assessment:** Concerns

The bets are honest bets (each has an "if false → what fails"), and the riskiest (B1) is properly
gated by a live probe before code. But two of them are stated as more-confirmed than the probe
actually delivers.

- **B2 is half-unverified, and it is the load-bearing bet for baseline invariance — not B3 (see
  Major M3).** B2 has two halves: (a) retyped usages carry the user supertype in `usage.types`;
  (b) plain usages do *not*. Half (a) is what the research probe on fusion-tea showed. Half (b) —
  plain `part x : Subtype` excludes the user supertype from `.types` — is **not** exercised by the
  probe model, which has no plain subtype-typed usage (only `Facility.driver` typed by a root type
  with no supertype). Yet half (b) is exactly what keeps the Non-Goal *and* baseline invariance
  intact for the (common) case of an existing baseline containing a plain `part x : Subtype`. The
  design pins baseline invariance on **B3** ("no baseline carries a retyping shape"), but that is
  the wrong bet: superset indexing adds a supertype key to *any* plain subtype-typed usage whose
  `.types` includes the supertype, retyped or not. B3 is necessary but not sufficient.

- **B1's fallback is gestured at, not stated.** If the probe (Q2) shows `heritage` climbs the
  supertype chain, the design says use "an owned-only accessor (probe Q3) instead of raw heritage,
  or filter heritage to direct/owned relationships." But Q3 is marked "nice-to-have, not gating,"
  and "filter heritage to owned" has no stated mechanism — *how* do you tell an owned FeatureTyping
  from an inherited one in the `heritage` iterable? If B1 is false, the design has no concrete
  path forward, which contradicts "Design does not proceed past the probe on this point" (that is a
  stop, not a fallback). This is contained (the probe gates it, and the precedent + research make
  B1 likely true), but the "fallback" language oversells what is actually a hard stop.

Decisions (D1–D5) each name the rejected alternative with a reason — genuine decisions, not
mechanism dressed as inevitability. D4 is the exception: its premise (these keys are `SysMLQN`) is
factually wrong (M1), so the decision to type them `SysMLQN` rests on a bad reading.

**Hidden bet surfaced:** the design assumes `most_specific(qns, model)` can resolve a PartDef QN
back to its element to walk its supertype closure, at both call sites. In
`_expand_template_calc_usages` you hold `model` and two `owning_part_def_qn` *strings* — the walk
needs a QN→PartDef-element lookup (iterate `elements_of_type(model,"PartDefinition")` and match
QN). This is feasible but unstated, and it is an O(partdefs) scan per comparison unless memoized.
The design should name the lookup and say it is built once, not per collision.

### 8. Reader Comprehension
**Assessment:** Pass

The document is well-layered: Core Concept states the plain idea (declared type = owned
FeatureTyping target, not a list position) before the mechanism; the Architecture diagram shows the
three fix points; INV-1..5 pin the invariants; the bets carry explicit "if false" clauses. A tired
engineer can skim it once and know what changes and why. The one comprehension risk is that the
collision mechanics (why same-name collides and different-name does not) live across Core Concept,
B4, and INV-4 — but they are consistent and each is anchored to `usage_extractor.py:246-247`, so a
reader can assemble them. No blocking voice issue.

---

## Issues by Severity

### Critical (must fix before implementation)

- **C1 · V-number collision.** Design assigns V8/V9; Item 3 lands first and already claims **V8**
  (anonymous-return diagnostic, `return-style-extraction/design.md:17-18,89-90`). The
  `modeling-assumptions.md` V-table (`:344-350`) ends at V7 in committed state and Item 3 inserts
  V8. **Item 4 must renumber to V9 (collision tiebreak) and V10 (incomparable multi-typing).**
  Update every occurrence: Core Concept, D2, D3, Component Overview, Implementation Notes (both
  warning texts), Docs/Matrix Plan, Next-Stage Handoff. No other in-flight item touches the V-table
  beyond Item 3 (checked).

### Major (should fix before implementation)

- **M1 · `SysMLQN` is the wrong type for these keys.** `SysMLQN` is the `::`-separated form
  (`identifier_types.py:22`); the index keys and `usage_type_map` values are `__`-separated
  (`build_element_qualified_name` default). The consumer compares them against `redef.owning_part_qn`,
  also `__`-form (`graph_builder.py:1053`) — so they *must* stay `__`-form, which means they are
  **not** `SysMLQN`. D4 and the Research Finding (design.md:63-65) are wrong on this. Options:
  (a) leave them `str` (honest, zero-risk); (b) use the `EQN` family or introduce a correctly-named
  NewType for the `__`-form PartDef QN. The spec's R1/doc-10 ask is "unique-by-construction,
  scope-prefixed, no ambiguous string keys" — it does **not** mandate `SysMLQN` specifically. Do
  not switch the runtime separator to `::` to satisfy the label; that would break the consumer
  comparison.

- **M2 · Probe does not cover the multi-owned-typing shape it claims to gate.** Q2 is said to "lock
  the multi-typing ordering for D2," but `probe/model.sysml` has no usage with two or more owned
  FeatureTypings (`part x : A, B`). So D2's incomparable branch and the V10 warning are written
  blind — the very code path most likely to be wrong. Add a shape to the probe model: a usage typed
  by two unrelated user PartDefs, and print its `heritage` FeatureTyping targets. (The owned-vs-
  inherited half of Q2 *is* covered by the existing `Variant.driver` shape — that part is fine.)

- **M3 · Baseline invariance rests on B2-plain, which the probe does not test.** The zero-diff of
  the 4 baselines depends on plain subtype-typed usages excluding their user supertypes from
  `.types` (B2 half b) — not just on "no retyping shape exists" (B3). Existing baselines very likely
  contain plain `part x : Subtype` usages; if `.types` there includes the supertype, superset
  indexing adds a supertype key and can change output. The live re-capture (Validation step 4) *is*
  a real backstop that would catch this — but the stated argument (B3) is incomplete and should be
  corrected to name B2-plain as the actual invariant, and the probe model should add a plain
  `part plain_hif : 'HIF Driver'` usage so B2-plain is confirmed *before* the re-capture, not
  discovered at it.

### Minor (consider)

- **m4 · B1 fallback is a stop, not a fallback.** If Q2 shows heritage climbs the chain, the design
  has no concrete owned-only mechanism (Q3 is marked non-gating; "filter heritage to owned" has no
  stated how). Either promote Q3 to gating (it becomes load-bearing exactly when B1 fails) or state
  plainly that a false B1 halts the design pending a new approach.

- **m5 · `most_specific` QN→element lookup unstated.** Name the QN→PartDef-element resolution both
  call sites need and say it is built once (not an O(partdefs) scan per comparison).

- **m6 · 3-owner collision edge.** The V9 dedup key `(owner_a, owner_b, calc_name)` and pairwise
  reduction are correct for the 2-owner fixture shapes but under-defined for a 3-level chain
  colliding on one QN. Note as a known limitation; don't build for it.

- **m7 · State the per-usage union as a set in INV-1.** The declared type is both an owned
  FeatureTyping target and a `usage.types` member; build the key set as a union so the usage is not
  listed twice under one key (backstopped by `seen_paths`/`seen_qns`, so not a correctness bug, but
  worth pinning).

---

## Recommendations

1. **C1 — renumber V8/V9 → V9/V10** across the design. Mechanical, but blocking: Item 3 owns V8.
2. **M1 — drop the `SysMLQN` claim.** Type the `__`-form keys/values as `str` (or an honest
   `__`-form NewType), not `SysMLQN`. Fix design.md:63-65 and D4.
3. **M2 + M3 — extend `probe/model.sysml`** with (a) a two-unrelated-typing usage (locks D2/V10)
   and (b) a plain `part x : 'HIF Driver'` usage (locks B2-plain / baseline invariance). Re-run the
   probe before writing the helper; both are five-minute additions and both gate code that is
   otherwise written blind.
4. **M3 — correct the baseline-invariance argument** to rest on B2-plain, not B3; keep the live
   re-capture as the backstop.
5. **m4 — make B1's false-branch honest:** promote Q3 to gating or state it as a hard stop.
6. **m5/m6/m7 — small pins:** name the QN→element lookup and its build-once; note the 3-owner edge;
   say INV-1 is a set union.

---

## Resolutions

Resolved 2026-07-05 (applied to design.md + probe files):

- **C1 (V-number collision):** Renumbered throughout — collision tiebreak stays **V9**, incomparable
  multi-typing **V8 → V10** (Item 3 owns V8 for anonymous return). Updated Core Concept, D2, D3, Component
  Overview, both warning texts, Architecture diagram, Validation, Docs/Matrix plan ("Add V9, V10"), and
  Next-Stage Handoff. The "Warning convention" Research Finding now states Item 3 claims V8, so this item's
  free numbers are V9/V10.

- **M1 (`SysMLQN` is wrong):** Dropped the `SysMLQN` claim. Keys/values are typed plain `__`-form `str`.
  Rewrote the Research Finding (now "Key form (doc 10)") to state `SysMLQN` is the `::`-form
  (`identifier_types.py:22`) while these keys are `__`-form and the consumer compares them `__`-form
  (`graph_builder.py:1053,1056`), so the runtime form must not change to `::`; doc-10 discipline does not
  mandate `SysMLQN` here. Rewrote **D4** accordingly (chosen: plain `__`-form `str`; rejected: `SysMLQN`
  and coining a new NewType). Updated the Architecture diagram and helper signatures.

- **M2 (multi-typing probe gap):** Added `part multi : 'IFE Driver', 'Other Driver';` (two unrelated user
  typings) and a `part def 'Other Driver'` to `probe/model.sysml`. Added **Q2b** to the probe plan and
  Next-Stage Handoff so D2's incomparable branch and the V10 warning are probed, not written blind.

- **M3 (baseline invariance rests on B2-plain):** Split **B2** into halves (a) retyped carries supertype in
  `.types`, (b) **B2-plain** — plain `.types` excludes user supertypes — and named half (b) the load-bearing
  bet for baseline invariance. Corrected **B3** to "necessary but not sufficient" (covers only the retyping
  shape). Added `part plain_hif : 'HIF Driver';` to the probe model and made Q1 test its `.types` exclusion.
  Updated INV-2, the Potential Risk (now "B2-plain false"), and Validation step 4 (backstops B2-plain + B3).

- **m4 (B1 fallback is a stop):** Made B1-false an explicit **hard stop** in Implementation Notes and
  Potential Risks — report and halt, do not improvise a heritage filter. **Q3 promoted to gating** iff Q2
  shows heritage climbs the chain.

- **m5 (`most_specific` lookup):** Signature changed to `most_specific(qns, qn_to_partdef)`; the
  `{qn: PartDefElement}` lookup is built **once** from `elements_of_type(model,"PartDefinition")`, not an
  O(partdefs) scan per comparison. Stated in D2 and Component Overview.

- **m6 (3-owner collision edge):** Noted as a known limitation in D2 (pairwise reduction converges) and the
  V9 warning text (pair-keyed dedup may emit >1 line for a 3-way collision); out of the 2-owner fixture
  matrix — not built for.

- **m7 (INV-1 as set union):** INV-1 now says build the per-usage key set as a `set` (the declared type is
  both an owned FeatureTyping target and a `usage.types` member); also stated in D3/Component Overview.

- **Also:** D3 now states the tiebreak compares the **stored virtual's** `owning_part_def_qn` (line 266),
  not a re-derived value (review §5 second bullet).

**Disposition:** All Critical/Major/Minor items applied. The probe remains unexecuted in this
non-interactive session (`uv run` needs an approval the sandbox can't grant); it is handed to the plan
phase as gated de-risk #1, now covering Q1/Q2/Q2b/Q3/Q4.

---

**Overall:** **Revise.** The approach is sound and the design is well-built; it needs one must-fix
collision (C1), one wrong type choice (M1), and two probe/argument gaps (M2, M3) closed before the
plan runs. None of these touches the fundamental shape — they are corrections, not a redesign.

**Next Steps:** Record resolutions above, then re-run `/_my_design` (or return to the design-agent
session) and point it at this review to incorporate. The reviewer does not edit the design.
