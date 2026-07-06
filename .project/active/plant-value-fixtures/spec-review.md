# Spec Review: Plant-Value & Blind-Spot Fixtures (PIPELINE-TRUTH Item 1)

**Spec:** `.project/active/plant-value-fixtures/spec.md`
**Contract:** `claude-pack/commands/_my_spec.md`
**Review File:** `.project/active/plant-value-fixtures/spec-review.md`
**Date:** 2026-07-06

---

## Reality Check

**Sound.** The spec is about the right work item, its problem statement matches epic Item 1
and discovery §D6, and every code-facing claim I checked holds: `collect_uncovered_params`
(`graph_builder.py:810`) is pure with fields `(module, input, missing_key)`, V11 raises at the
generation boundary not graph build (`cli/__init__.py:265`), `build_full_graph_from_snapshot`
exists (`graph_rebuild.py:125`), and every named fixture and test file is present. The scope
decomposition (headline / extend twolevel / secondary shapes / capture hygiene) faithfully
mirrors the epic. It is not a rewrite candidate.

But there is one crux the spec asserts without engaging its mechanism — whether the headline
fixture actually trips V11 — and the current corpus is strong evidence it is harder than the
spec assumes. That plus a handful of tightenings put this at **Revise / APPROVED-WITH-CHANGES**.

---

## Audit

### Lens 1 — Faithfulness

**L1-1 · Direct claim (the V11-trip crux — highest stakes):** The spec states as a `[HARD]`
requirement and Success Criterion that the headline fixture "trips V11 today" with an offender
set reproducing **all three** value-provision mechanisms (subtype-def literal via retype; bare
no-retype `part :>>` literal block; twolevel chain). But `collect_uncovered_params`
(`graph_builder.py:810`) only flags an EP that is **valueless** (`default_value is None`) — it
explicitly excludes "a bound literal parsed to a float." And `tests/unit/test_uncovered_params.py`
(header, lines 15–33) records that after Items 9/10 of the prior epic, *the plain-usage LITERAL
class is pre-filled and the two cross-part CHAIN pins were wired*, so **the only committed
fixture that still fires the collector is `chain_override_probe`, on a calc-output ref**. Two of
the spec's three mechanisms — (a) and (b) — are **literal**-valued. If the fixture author places
those literals where the Item-9 pre-fill reaches them, the EPs get a value and **V11 does not
trip** for those mechanisms. The fixture can only trip V11 if the literal is consumed *cross-part*
so the plant-calc-input EP stays valueless (that cross-part path is exactly what Item 2 has not
yet built). The spec never states this constraint; it defers "shape layout" to the plan
(Open Questions) as if any arrangement that parses will do. **This is the difference between a
real "before" pin and an empty one Item 2 has nothing to flip.** The spec must (a) make the
cross-part-consumption constraint explicit (the literal feeds a plant-calc input, not a
plain-usage EP), and (b) require a probe confirming a non-empty, mechanism-covering offender set
*before the fixture is accepted*, not assert it.

**L1-2 · Direct claim:** The "Known limitation" section (lines 242–251) and the fusion-tea
exemplar paths are stale and wrong. The orchestrator discharged the limitation — the live files
were read and the register's exemplars confirmed — and the register's paths **omit the
`models/designs/hif_ife/` subdirectory**. The spec carries the uncorrected paths throughout:
`hif_driver.sysml:81,83,84` and `hif_plant.sysml:36-49,51-65` (Problem, lines 19–22), and
`~/1cfe/fusion-tea/models/{ife_plant,hif_plant,hif_driver,ife_cost_parameters}.sysml`
(Related Artifacts, line 264). Correct paths are `~/1cfe/fusion-tea/models/designs/hif_ife/…`.
The "could not be read directly" limitation should be replaced with the discharged fact plus the
corrected paths, so execution copies from reality.

**L1-3 · Question to the user:** Decision D3 (line 140) says the `quoted_owner_formula`
reclassification is reviewed "against post-Item-7 computed-attribute behavior." Which Item 7 —
the **prior** epic's (already landed) or **this** epic's (Item 7 = matrix reconciliation, which
runs *after* Item 1)? If it means this epic's, that is a forward dependency and a contradiction
with "already-landed … not a code change." I read it as the prior epic, but the phrase is
genuinely ambiguous and a future reader could infer a forward dep. Name the epic.

### Lens 2 — Problem & Approach

**L2-1 · If-then tradeoff (the empirical-pin vacuity guard — orchestrator Q2):** SC-3 and D5
say each secondary shape's behavior is "pinned by a test, determined empirically at capture, not
assumed." That is the right stance for a *before*-state snapshot. But the epic's R1 bans the
REQ-EXT-09 anti-pattern (expectation computed by the code under test), and a bare
`snapshot == committed snapshot` byte-pin is exactly that shape: its expectation is the snapshot
the code just produced. It guards drift but documents **nothing** about the shape's behavior — a
future reader learns only "the bytes didn't change." The spec should require each per-shape pin to
assert a **specific observed property** (e.g. "shape X yields entry point Y with `default_value
is None`" or "shape X is dropped — no module input references it"), not a whole-snapshot equality.
The ife_plant precedent (memory note `plant-idiom-fixtures`) does this — it labels shape-by-shape,
not byte-by-byte. Without this tightening, "pinned by a test" degrades into the vacuous pin the
epic explicitly bans.

**L2-2 · If-then tradeoff (scope escape hatch — orchestrator Q4/Q5):** The spec requires the
secondary shapes to "load and capture" and hard-requires **zero production-code changes**. Two of
the named shapes are exotic — a quoted OUTPUT parameter name (`out attribute 'net cost'`) and a
Style-E mixed `out attribute` + `return` calc def inside a quoted def. If one of these does not
merely *degrade* but **crashes the extractor**, then "load and capture" cannot be satisfied
without a code change — and the spec's zero-code constraint would be violated, or the shape
silently dropped. The spec gives no fallback. It should state the escape hatch explicitly: a
secondary shape that cannot be captured without a production-code change is **FILED to the
fixture-gap register** (matching D4's filing discipline), not fixed here. As written, "load and
capture" reads as guaranteed when it is empirically not.

**L2-3 · Direct claim:** The spec is well-sized and the D1 decision (new fixture, not an
`ife_plant` edit) is well-argued and correct — folding a V11-tripping shape into `ife_plant`
would churn its byte-pinned baselines. No finding; recorded so the reviewer knows this was
attacked and held.

### Lens 3 — Pipeline Risk

**L3-1 · Direct claim (byte-identity is not checkable as specified — orchestrator Q3):** The
cross-cutting requirement says "every existing baseline not deliberately touched stays
byte-identical," and the deliberately-touched set is enumerated. But **neither capture script
accepts a selective argument** — `capture_extraction_snapshots.py:159` and
`capture_pipeline_baselines.py:73` both loop over *all* registered fixtures with no filter.
Running either script rewrites **every** snapshot/baseline. Worse, the spec's own rider says
`wi014_toy` / `self_named_binding_trap` / `quoted_owner_formula` need "path canonicalization" —
which means a fresh capture *does* change committed paths; there is no reason that same
canonicalization wouldn't also alter the untouched fixtures on a full run. So the enumerated
procedure ("run `scripts/capture_*.py`") actively contradicts the byte-identity criterion. The
spec must specify **how** selective capture is achieved (add a fixture-name filter to the scripts,
or run-all-then-`git checkout` the untouched set) so byte-identity is actually checkable and not
just asserted.

**L3-2 · Question to the user:** SC-1 (line 52) requires the headline offender set to reproduce
"the `spec_chain_twolevel`-style chain" *in the headline*, while the extended `spec_chain_twolevel`
(SC-2) also covers mechanism (c). Does the headline need its **own** (c)-style chain instance, or
does SC-1 lean on the twolevel fixture? Lines 24–25 and 85 say "reuse the twolevel shape," which
reads as the headline containing its own copy. If the headline is meant to be self-contained on
all three mechanisms, say so; if (c) lives only in twolevel, SC-1's "all three in the offender
set" is describing two fixtures, not one. Small, but it changes what the headline test asserts.

**L3-3 · Rewrite request:** The agentic-mbse impact (SC line 70, epic Scope §5) is recorded as a
success criterion but no Known Requirement says *what* gets recorded or *where* the impact list
lives. Item 9 consumes it. Either point at the impact-list artifact or state the one sentence that
must be captured, so Item 9 has something concrete to accumulate.

### Lens 4 — Hygiene

**L4-1 · Rewrite request:** The three mechanism labels collide across documents — the spec uses
(a)/(b)/(c), the memory note `plant-idiom-fixtures` uses A/B/C/D for a *different* mechanism
partition (mech A/B/C/D there), and the reader must hold both. One cross-reference line
("spec's (a)/(b)/(c) are not the memory note's A/B/C/D") would prevent a mis-map during
execution. Minor.

### Lens 5 — Reader Comprehension

**L5-1 · (none material).** The spec is dense but legible — Problem leads with the point, the
decisions are argued, the deliberately-touched set is a clean table. The one comprehension risk is
L1-1's buried assumption (the reader cannot tell from the spec that "trips V11" is contingent on
cross-part placement), but that is a substance finding, not a voice one.

---

## Engagement Summary

**Overall take:** The work item is right and the code claims check out, but the spec asserts its
headline deliverable — "the fixture trips V11" — without engaging the one mechanism
(`collect_uncovered_params`'s valueless test, plus the Item-9 literal pre-fill) that has already
neutralized every other literal and chain fixture in the corpus. If the fixture is authored the
obvious way, it may generate clean and leave Item 2 with an empty pin to flip. That, plus a
byte-identity procedure that the capture scripts can't actually deliver, are the two must-fixes;
the rest are tightenings.

**Here's what I need you to weigh in on:**

1. **[L1-1]** The V11-trip is contingent, not automatic: literal mechanisms (a)/(b) only trip if
   consumed cross-part (valueless plant-calc EP). Make that constraint explicit and require a
   probe confirming a non-empty, three-mechanism offender set before accepting the fixture.
2. **[L3-1]** Byte-identity is asserted but not checkable — the capture scripts have no selective
   mode and rewrite everything. Specify the selective-capture procedure.
3. **[L2-1]** Guard the per-shape pins against the epic's own banned anti-pattern: require each to
   assert a specific observed property, not a whole-snapshot byte-equality.
4. **[L2-2]** Add the escape hatch: a secondary shape that can't be captured without a code change
   is FILED, not fixed — otherwise "load and capture" + "zero production code" can collide.
5. **[L1-2]** Fix the stale "Known limitation" and the fusion-tea paths (add
   `models/designs/hif_ife/`); the limitation is discharged.
6. **[L1-3]** Disambiguate "post-Item-7" — prior epic or this one.

---

## Must-Fix List (numbered)

1. **[L1-1]** Make the V11-trip contingency explicit — the literal shapes (a)/(b) must be consumed
   cross-part so the plant-calc-input EP is valueless; require a capture-time probe confirming a
   non-empty offender set covering all three mechanisms before the fixture is accepted. Reconcile
   SC-1's "all three mechanisms in the offender set" (asserted) with D5's "measured, not assumed"
   — define the fallback if a mechanism does not surface as an offender.
2. **[L3-1]** Specify the selective-capture procedure so "everything else byte-identical" is
   checkable (fixture-name filter on the capture scripts, or run-all-then-revert-untouched).
3. **[L2-1]** Require each secondary-shape pin to assert a specific observed property, not a
   whole-snapshot equality, to stay clear of the epic R1 REQ-EXT-09 ban.
4. **[L2-2]** State the scope escape hatch: a secondary shape that cannot be captured without a
   production-code change is FILED to the fixture-gap register, not fixed.
5. **[L1-2]** Replace the discharged "Known limitation" with the confirmed fact and correct all
   fusion-tea paths to `~/1cfe/fusion-tea/models/designs/hif_ife/…`.
6. **[L1-3]** Name which epic's Item 7 the `quoted_owner_formula` reclassification is reviewed
   against.
7. **[L3-2]** Clarify whether the headline carries its own mechanism-(c) chain or relies on the
   extended twolevel.
8. **[L3-3]** Point the agentic-mbse impact record at a concrete artifact / one-line content.

---

## Resolutions

*Filled in during Stage 5, keyed by finding ID, as the user resolves each.*

---

**Verdict:** APPROVED-WITH-CHANGES (Revise)

The work item is sound and belongs first on Track A. The must-fixes are targeted spec edits, not a
rework — chiefly the V11-trip contingency (L1-1) and the byte-identity procedure (L3-1), which are
the two that could otherwise let the headline deliverable land vacuously. Once resolutions are
recorded, re-run `/_my_spec` (or return to the spec-agent session) and point it at this review to
incorporate. The reviewer does not edit the spec.
