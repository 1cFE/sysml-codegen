# Design Review: Resolution Matcher Fixes & Warning Reconciliation (SC-8)

**Design:** `.project/active/warning-reconciliation/design.md`
**Spec:** `.project/active/warning-reconciliation/spec.md`
**Review File:** `.project/active/warning-reconciliation/design-review.md`
**Date:** 2026-07-05
**Reviewer posture:** skeptical; claims re-traced against HEAD (88115b8) code and committed baselines.

---

## Fundamental Assessment

**Sound approach, two load-bearing mechanisms built on incorrect premises.**

The core concept is right and well-argued: three defects compound into warnings that
fire on healthy models and go silent on a broken one, and the fix separates them by
*stage and severity* (resolve benign misses, hard-fail the genuine dangle, warn once on
tracked residue). The matcher fixes, the atomic six-site flip, the deriver-untouched
decision, and the collector/`_validate_channel_references` sibling pattern are all solid.
I verified the flip's six sites (all exact, no seventh), the deriver's QN-keyed indices
(no change needed), and the registry-key-not-serialized claim. Those stand.

But the two mechanisms the scrutiny brief flagged both rest on premises the code
contradicts:

1. **V11's predicate is wrong at the boundary.** `default_value is None` is not the
   signature of "broken." The schema layer renders every null-default entry point as a
   **required Pydantic field** — that *is* the codebase's supported "user must provide
   this value" mechanism. V11 as designed (always-strict, no escape hatch) would
   hard-fail a valid model that uses a required, no-default input. The current corpus
   doesn't exercise the shape, so the tests would pass green while the invariant is wrong
   for the general model.

2. **D2's disambiguator is inoperative.** The QN-suffix guard keys on the part-**usage**
   name, but a def-owned attribute's qualified name carries the part-**def** name segment
   (different identifier, different case). The guard never fires. B1 — the bet the whole
   mechanism rests on — is false as stated. Safety collapses to the same-file tiebreak,
   which can silently cross-wire to a wrong value.

Neither is fatal to the work item — the foundation is sound and the fixes are the right
fixes. This is a **Revise**: two Critical corrections to the mechanisms, then proceed.
Do not Rework.

---

## Dimensional Review

### 1. Spec Compliance
**Assessment:** Concerns

The design covers every spec requirement — the two matcher fixes, the six-site flip, the
two-layer collector + strict boundary, the catf_mfe xfail decision, the reconciliation
summary at WARNING, the seeded fixture, and the behavioral-review worksheet. It correctly
resolves the spec's open questions (def-owned owner → backtracker; enforcement site →
generation boundary; summary level → WARNING).

The concern is that the spec's success criterion — "a *genuinely uncovered* input fails
loudly" (spec.md:70-72) and "clean fixture models generate with **zero WARNING lines**"
(spec.md:60) — is satisfied *on the current corpus* but not *in general*, because V11's
predicate catches more than "genuinely uncovered." See Critical-1. The spec itself frames
V11 as "no matching key in **any** parameter group" (spec.md:71); the design's crux
finding correctly shows membership can never fail (Step 6.8), so it substitutes
"null-default." But "null-default" ≠ "uncovered" — a required user-fill input is
null-default *and* legitimately in its group. The design substituted a predicate that is
broader than the spec's intent.

### 2. Pattern Consistency
**Assessment:** Pass

The collector mirrors `_validate_channel_references` (`graph_builder.py:612`); the flip
reuses Item 5's `sanitize_qualified_name`; the boundary sits beside
`_check_duplicate_output_paths`. No new subsystem. The def-owned branch extends the
existing `_resolve_to_design_attribute` dotted branch rather than introducing a parallel
matcher. This is the right instinct throughout.

### 3. Abstraction Quality
**Assessment:** Concerns

The collector-is-pure / boundary-raises split (INV-3) is clean and correct — it keeps
collector-only conformance tests from tripping strict enforcement. Good.

The concern is the V11-vs-summary boundary (D4 vs D5). The design presents them as two
mechanisms covering different cases: V11 = "wired input → null-minted key" (hard), summary
= "fell through AND valueless" (soft). But trace the populations (see Critical-1): a
fall-through is always wired, so the summary's population is a **subset** of V11's. The
only members V11 has that the summary does not are non-fall-through null-default inputs —
which are exactly the legitimate user-fill inputs V11 should *not* abort on. So the delta
that makes V11 a distinct, broader, hard check is precisely its false-positive set. Two
abstractions whose difference is a bug is a sign one of them is mis-scoped.

### 4. Duplication Avoidance
**Assessment:** Pass

No parallel structures. The design explicitly rejects a deriver-side matcher (D1) once it
establishes the deriver is already QN-keyed — verified: `_attr_index`
(`parameter_groups.py:304-314`), `classify` and `get_default_value`
(`parameter_groups.py:530-550`) key on `qualified_name`, never `parent_part`. A backtracker
fix propagates for free. D1 is correct.

### 5. Data Structure Clarity
**Assessment:** Pass

`fallback_entry_points` on `BacktrackingResult`, `UncoveredInput` from the collector, and
the EntryPoint(kind, default) flow are all explicit and traceable. The data-flow line in
the Architecture section is accurate.

### 6. Route Safety
**Assessment:** Concerns

Two routing concerns, both in the matcher cascade (D2):

- **Same-file tiebreak can cross-wire.** The design asks "is same-file a safe tiebreak or
  should it also refuse?" Answer from the data: it is **not** safe. See Critical-2.
- The always-strict boundary with no escape hatch (D4) is the right call *if* the predicate
  is right. With the current predicate it is a route with no fallback that fails valid
  input — the classic unsafe catch-all. Fix the predicate (Critical-1) and this becomes
  safe again.

### 7. Bets & Decisions Integrity
**Assessment:** Fail

The decisions are honest and each names its rejected alternative — D1 through D5 are real
decisions with real alternatives. The failure is in the bets.

- **B1 is false as stated.** "The resolved `qualified_name` of a def-owned design
  attribute contains the owning part-**usage** name as a segment." It does not — it
  contains the part-**def** name. The design cites `...__battery_system__pack_count` as
  agent-verified; the actual QN is `SolarBatteryLibrary__Battery_System__pack_count` (def
  name, PascalCase). The second cited example, `...__solar_battery_plant__p_net_mw`, is a
  *usage-owned* attribute (`parent_part = "solar_battery_plant"`), which resolves through
  the existing exact-match branch, not the new def-owned branch — so it does not evidence
  B1 at all. The bet's own "if false → cross-wire" clause fires, and the mitigation it
  points to (the QN-suffix guard) is the thing that doesn't work. This is the most
  expensive kind of finding: a load-bearing belief the design rests on that is wrong, with
  a stated verification that was misread.

- **B4 is stated in the wrong direction.** It de-risks against cases going *quiet* ("an
  SC-5 cross-part case goes quiet"). The actual risk with V11's predicate is the opposite —
  it fires *too loud*, on valid models. The design has no bet, risk, or mitigation covering
  the false-positive direction. That is the hidden bet: **"every wired null-default entry
  point is a defect."** It is unstated and false.

- B2 (no seventh flip site) and B3 (resolving keys keep their value) are honest. B2
  verified: exactly six call sites, no seventh.

### 8. Reader Comprehension
**Assessment:** Pass

Dense but navigable. The Core Concept leads with the plain model (three defects compound)
before mechanism. The V11 crux section is the clearest part of the document — it walks the
membership-can-never-fail insight step by step. A tired engineer can follow it. The one
comprehension hazard is that B1's false premise reads as settled fact ("agent-verified"),
which will mislead the implementer into coding a guard that does nothing; that is captured
as Critical-2, a substance finding.

---

## Issues by Severity

### Critical

- **C1 · V11's predicate hard-fails valid models (crux).** `default_value is None` is the
  codebase's representation of a *required, user-supplied* input, not only of a broken one.
  Verified: the schema template renders a null-default EP as a required Pydantic field with
  no default (`templates/parameter_group_schema.py.jinja2:10-11`, `extra: "forbid"` at
  `:17`); the README documents null params as "require explicit values before pipeline
  execution" (`generation/entry_point.py:118`); `_get_library_default` deliberately returns
  None for a symbolic default like `"1.0 / q_eng"` (`graph_builder.py:594,608`); and an
  unbound library default returns None (`parameter_groups.py:543-544`). So a valid model
  with an unbound, no-default (or symbolic-default) library input produces a wired
  null-default `LIBRARY_DEFAULT` entry point, and V11 — always strict, no escape hatch (D4)
  — aborts generation on it.

  The current corpus does not exercise this shape (empirically verified: all four clean
  fixtures have **zero** wired null-default inputs; the sole case is catf_mfe's one
  `usage_literal`), so the design's tests pass green while the invariant is wrong for the
  general model. The population math makes the defect precise: V11's set = the
  reconciliation summary's set (fall-through ∩ valueless) **∪** legitimate user-fill inputs.
  The extra coverage that makes V11 broader and harder than the summary *is* its
  false-positive set. **Fix:** narrow V11 to the fall-through-and-valueless population the
  design already tracks in `fallback_entry_points` (catf_mfe is a fall-through; a proper
  Strategy-2 library default is not), *or* establish and document that required-no-default
  library inputs are an unsupported modeling shape and prove no model relies on the
  user-fill workflow. The first is strongly preferred — the runtime-safety concern is the
  dangle, not the user-fill input. — Dimensions 1, 3, 6, 7

- **C2 · D2's QN-suffix guard is inoperative; safety collapses to an unsafe same-file
  tiebreak.** The guard is `attr.qualified_name.endswith(f"__{parent_part}__{leaf}")` with
  `parent_part` = the binding's part-**usage** name (design.md:313). But a def-owned
  attribute's QN carries the part-**def** name segment: `...__Battery_System__pack_count`,
  not `...__battery_system__pack_count` (verified against `solar_battery` extraction
  snapshot). The usage name and def name are different identifiers with different case, so
  `suffixed` is **always empty** for def-owned attrs. Resolution always falls through to
  `len(cands) == 1` (leaf-uniqueness) or the same-file tiebreak.

  Consequences: (a) B1's "two defs cannot cross-wire because the usage segment differs" is
  false — the segment that differs is the def name, and the guard keyed on the usage name
  never sees it. (b) The same-file tiebreak *can* cross-wire: if the intended def-owned
  attr lives in file Y but a same-leaf sibling (e.g. another material's `yield_strength` —
  four exist in one file in the corpus) lives in the usage's file X, `len(same_file) == 1`
  picks the sibling → wrong value, silently. INV-2 claims "never picks among >1 unless the
  guard resolves to exactly one"; the same-file branch can resolve to exactly one *wrong*
  one. **Fix:** drop the QN-suffix guard (it does nothing) and make same-file **refuse**,
  not pick — the design's own scrutiny question answered by the data. Keep `len(cands) == 1`
  (leaf-unique, safe, and what actually drives the solar_battery dedup). Genuinely ambiguous
  same-leaf-different-def dotted bindings then fall to Step-4 → caught by the summary; that
  is the only safe behavior without a usage→def type map (which the design correctly
  rejects as out of scope). Rewrite B1/D2 to describe what actually resolves. — Dimensions
  6, 7

### Major

- **M1 · V11 and the reconciliation summary should be reconciled, not just co-located.**
  If C1 is fixed by narrowing V11 to fall-through-and-valueless, V11 and the summary share a
  population — so the design must answer why one is a hard abort and the other a warning on
  the same set. Likely resolution: the fall-through-and-valueless set *is* the hard-failure
  set (the pipeline references a key the JSON never mints — a real runtime break), so it
  should abort (V11), and the summary's role narrows to a human-readable digest of the same
  abort, or to fall-throughs that are *not* wired (if any exist). Clarify the two
  mechanisms' populations explicitly once C1 is resolved. — Dimension 3

### Minor

- **m1 · Verbatim-warning-capture worksheet should be Phase 0.** The design defers the
  verbatim "Registry unresolved" line set and the full reclassification/value diff to a live
  `run_codegen` at implement (Appendix B) and files it under "Open for plan." Correct call
  (the design sandbox couldn't run codegen), but the plan must make it the *first* task — the
  before-baseline capture has to happen before any matcher change lands, or the before→after
  diff (the R3 audit deliverable, B3's regression guard) is unrecoverable. Confirm the plan
  puts it at Phase 0. — Dimension 1

- **m2 · README null-param documentation is subtly inconsistent with generation, and this
  interacts with C1.** `entry_point.py:118` says null-value params appear in the JSON and
  require explicit values, but `generate_all_derived_jsons` (`:297`) *omits* the key
  entirely (no null placeholder). Whichever way C1 resolves, this doc/behavior gap is worth
  a one-line note — if user-fill is supported, the JSON arguably *should* emit the null
  placeholder so the pipeline reference is satisfiable and the user sees what to fill; if it
  is not supported, the README line is stale. Not in this item's scope to fix, but name it
  so the C1 decision is made with the full picture. — Dimension 1

### Confirmations (verified, no action)

- Six-site flip: all six line numbers exact at HEAD; exactly six call sites of
  `sysml_qn_lookup` / `sysml_to_python_qualified_name` / raw registration — **no seventh
  site** (B2 holds).
- Deriver untouched (D1): `_attr_index`, `classify`, `get_default_value` all QN-keyed,
  never `parent_part`. A backtracker fix propagates. Correct.
- Flip byte-invariant on baselines (INV-6): the FORMULA `::`-form registry key is built in
  memory (`output_registry_builder.py:130`) and never serialized; every `::` in committed
  baselines is a `calc_def_qualified_name` field, not a registry key. Confirmed.
- V11 fires on exactly catf_mfe `[cryo_load.magnet_volume]` on the current corpus (INV-4);
  all four clean fixtures are 0 wired null-default inputs (INV-5 holds *for the current
  corpus* — but see C1 for why that is not a general guarantee).
- Step-4 fallback site and reconciliation-summary placement (post-assembly, in
  `run_codegen`) are correct; the count-summary format is sane.

---

## Recommendations

1. **Fix V11's predicate (C1).** Narrow it from "wired null-default" to the
   fall-through-and-valueless population already tracked in `fallback_entry_points`, so it
   catches the genuine dangle (catf_mfe) without aborting valid required-user-fill models.
   Then reconcile V11 and the summary (M1) — state their populations explicitly.
2. **Fix D2 (C2).** Drop the inoperative QN-suffix guard, make same-file **refuse**, keep
   leaf-unique (`len(cands) == 1`). Rewrite B1 and D2 to match what actually resolves
   (def-name segment, not usage-name; safety = refuse-on-ambiguity, not suffix
   disambiguation).
3. **Correct B1 and B4 in the bets section.** B1 is false; B4 points the wrong way and hides
   the real bet ("every wired null-default EP is a defect"). Surface and test the
   false-positive direction.
4. **Make the before-baseline capture Phase 0 in the plan (m1).**
5. **Note the JSON null-placeholder gap (m2)** as input to the C1 decision.

The matcher fixes, the six-site flip, the deriver decision, and the collector pattern need
no change — they verified clean.

---

## Resolutions

*(To be filled in during Stage 4, as the user resolves each finding. This section is what
the design agent reads to incorporate the review — the reviewer does not edit the design.)*

---

**Overall:** Revise
**Next Steps:** Record resolutions above, then re-run `/_my_design` (or return to the
design-agent session) and point it at this review to incorporate. The two Critical findings
(C1 V11 predicate, C2 D2 guard) are the gate; the confirmations need no action. The reviewer
does not edit the design.
