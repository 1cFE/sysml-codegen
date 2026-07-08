# Spec Review: Matrix Sweep Residue (TRUTH-DEBT Item 5)

**Spec:** `.project/active/matrix-sweep-residue/spec.md`
**Contract:** `claude-pack/commands/_my_spec.md`
**Review File:** `.project/active/matrix-sweep-residue/spec-review.md`
**Date:** 2026-07-07

---

## Reality Check

**Concerns.** The work item itself is right — the 33-row disposition table (17 strengthen / 11
reframe / 5 cite) and the sweep-completion decision are sound, and every spot-checked row held up
against the code and tests. But the spec's premise about *why now* rests on a fact that is now
false: it claims REQ-CA-01 is "essentially already discharged" at HEAD, and it presents its own
Re-verification section (251 PASS + 4 UNTESTED, the 256-vs-255 discrepancy) as current state. Both
have been overtaken by Item 3 landing (`9f37790`) after the spec was authored. This isn't a Stage-0
fail — the disposition table survives untouched — but the spec cannot go to `/plan` carrying a
re-verification section that describes a HEAD that no longer exists. See L1-1/L1-2 below.

---

## Audit

### Lens 1 — Faithfulness

**L1-1 · Direct claim:** The spec's central "why now" claim — that REQ-CA-01's row text "has
already moved at HEAD… which is essentially the reframe the filing prescribed" — does not hold up.
At HEAD (`docs/architecture/verification-matrix.md:142`) the row text still reads: "…the transient
sixth, `EXPOSE_CHAIN_TENTATIVE`, never survives the Phase-3b confirm pass to a reader — INV-F."
That is the exact over-claim the reframe target (`spec.md` table B, row CA-01) says to drop. I
grepped every test referencing `EXPOSE_CHAIN_TENTATIVE`
(`tests/conformance/test_computed_attributes.py`, `tests/unit/test_computed_attribute_extraction.py`,
`tests/conformance/test_data_models.py`) — none assert the transient value is absent from
reader-facing output after the confirm pass. `test_classification_exhaustive`
(`test_computed_attributes.py:85`) in fact treats `EXPOSE_CHAIN_TENTATIVE` as a *valid* member of
the classification, not an excluded one. **The reframe is not a no-op.** It's a live, needed edit,
and the spec's ↺HEAD flag on this row (and the Problem-section paragraph built on it) should be
corrected, not carried into the plan as "confirm already-discharged."

**L1-2 · Direct claim:** The Re-verification section is stale against the actual HEAD state. The
spec (authored before Item 3 landed) reports "251 PASS + 4 UNTESTED + 0 DEFERRED" with a
256-vs-255 summary discrepancy, and lists DM-08/PGD-06/RES-05/RES-08 as the 4 UNTESTED rows. I
counted the matrix directly at current HEAD (`4b9d697`): `grep -c "^| REQ-"` → 256 rows;
`grep "^| REQ-" | grep -c PASS` → 255; `grep "^| REQ-" | grep -c UNTESTED` → 1 (only REQ-PGD-06,
line 397). DM-08, RES-05, RES-08 are all `PASS` now (lines 168, 467, 470), matching commit
`9f37790`'s message ("rows UNTESTED→PASS, recount 256=255+1"). **The 256-vs-255 discrepancy this
spec spends a Success Criterion, a Known-Requirements bullet, and an Open Question on is already
reconciled — 255 + 1 = 256, no gap.** This is exactly the drift the spec itself warns about in its
own "why now" paragraph (R4: a disposition filed at a prior commit is a static-read verdict, not a
fact at HEAD) — the warning was correct, but the spec's own re-verification act needs to be re-run
one more time before this ships as the plan's contract, or the plan will spend its first step
"reconciling" a discrepancy that isn't there and may get confused when the DM-08/RES-05/RES-08 rows
it expects to flip are already flipped.

**L1-3 · Direct claim (verified, no defect):** I independently reproduced the two named high-value
strengthens.
- **REQ-EC-04**: confirmed. The internal gate at `expression_compiler.py:217-223` is real; the only
  test class (`test_expression_compiler.py:314-359`, `TestReqEc04AstParseValidation`) calls
  `python_ast.parse()` externally on `compile_expression()`'s return value and never drives an
  emitted-Python failure through the internal `try/except`. Deleting the gate would not fail any
  current test. STR judgment holds.
- **REQ-AS-06**: confirmed. `test_aggregation_scoping.py:479-513` wraps the resolution check in
  `if result is not None:` and only asserts `resolved_count > 0` — exactly the "40 of 41 could be
  unresolvable" gap the spec describes. STR judgment holds.

Two more spot-checks beyond the required minimum, both confirmed accurate:
- **REQ-BASE-04**: 10 baseline dirs (`tests/fixtures/baseline_outputs/*`) vs. 4 parametrized models
  in `test_baselines.py`'s `MODELS` list — matches the spec's claim exactly.
- **REQ-BASE-01 / citation to REQ-GA-01**: `test_baselines.py:69-79`
  (`test_computation_graph_baseline_is_well_formed`, marked `REQ-BASE-01`) checks only 3 dict keys
  exist. `test_graph_assembly.py:460-509` (`TestBaselineComparison`, marked `REQ-GA-01`) does the
  full module-by-module JSON compare the row text actually describes. Citation fix is accurate.
- **REQ-REG-06**: confirmed circular — `test_gen_registry.py:539-579` derives its expected type set
  from the same SUT helper (`_collect_exit_point_primitive_types`) it is testing. STR judgment (and
  the R1 anti-vacuity framing) holds.

### Lens 2 — Problem & Approach

No findings beyond L1-1/L1-2's downstream effect: the sweep-completion decision (complete the read,
re-file only fix-overflow) and the disposition table are the right shape and don't need to change.
The EPC(8) + LVP(9) + GA(8) = 25 residue-anchor arithmetic checks out against the matrix
(`grep -c "^| REQ-EPC-"` = 8, `REQ-LVP-` = 9, `REQ-GA-` = 8).

### Lens 3 — Pipeline Risk

**L3-1 · If-then tradeoff:** If the plan runs the Re-verification act itself (as R4 mandates) before
touching anything, L1-1/L1-2 self-correct at implement time and cost nothing beyond the spec's own
stated discipline. But if the plan trusts the spec's Re-verification section as a starting fact
(reasonable, since spec re-verification sections are normally meant to save the plan a rediscovery
pass), it will burn a step reconciling a discrepancy that's gone and may misjudge CA-01 as a
no-op. **Given the spec explicitly asks the plan to re-reproduce everything (R4), this is
should-fix, not must-fix** — but it should still be corrected before the plan is authored, so the
plan opens against fact instead of against a script it has to override.

### Lens 4 — Hygiene

**L4-1 · Rewrite request (minor):** REQ-SNAP-18's reframe rationale says "the `generation_timestamp`
token exists nowhere in the repo." That's not quite true — it appears in the test itself
(`test_snapshot_generation.py:282-296`), in the matrix row, and in several `.project/` artifacts
documenting the dead template. What's actually true, and what the cited test checks, is narrower:
no `.py` file under `src/sysml_codegen` passes it into a render call, and the template file that
once carried it (`pydantic_schema.py.jinja2`) has been deleted entirely (confirmed: no `.jinja2`
file in the repo references it). Ask the spec agent to tighten this to "no production render site
remains" rather than "the token exists nowhere."

### Lens 5 — Reader Comprehension

No findings. The disposition tables are dense but appropriately so — this is a ledger, and a
tired engineer can scan REQ id → disposition → action in one pass per row.

---

## Engagement Summary

**Overall take:** The disposition table is solid work — every spot-check across STR/REF/CITE held
up, including the two named high-value rows and the residue-anchor arithmetic. But the spec's
opening motivation and its mandated Re-verification section describe a HEAD that Item 3 has since
overtaken, and one of its two headline "already discharged" claims (CA-01) is flatly wrong when
checked against the actual tests. This needs a HEAD refresh before it goes to `/plan`, not a
rework of the disposition table itself.

**Here's what I need you to weigh in on:**

1. **[L1-1]** CA-01 is not a no-op. The row text still asserts INV-F ("never survives… to a
   reader") and nothing tests that. Confirm you want the ↺HEAD flag and the Problem-section
   framing corrected to "still needs the reframe" before this goes to plan — or if you'd rather
   let the plan's R4 reproduction step catch and fix it live (cheaper, but means the spec ships
   with a claim you know is wrong).
2. **[L1-2]** The Re-verification section's numbers (251/4/0, the 256-vs-255 gap) are stale —
   current HEAD is 255 PASS + 1 UNTESTED = 256, no discrepancy. Same question: patch the spec's
   Re-verification section now, or let the plan's mandatory re-reproduction absorb it silently.
   I'd lean toward patching now — the spec's own R1 for downstream artifacts ("no PASS row pins
   less than its text") applies just as well to the spec's own re-verification prose pinning a
   fact that's gone.
3. **[L4-1]** Minor precision fix on SNAP-18's rationale — your call whether it's worth a spec
   edit or just a note for the plan agent to read past.

---

## Resolutions

_(none yet — awaiting user engagement)_

---

**Verdict:** Revise
**Next Steps:** The disposition table, sweep decision, and Non-Goals need no rework. Once L1-1 and
L1-2 are resolved (patch the spec's Problem/Re-verification sections against current HEAD, or
explicitly delegate the correction to the plan's R4 step), re-run `/_my_spec` pointed at this
review, or hand this file to `/_my_plan` with an explicit note that the Re-verification section is
known-stale and the plan's first act supersedes it. The reviewer does not edit the spec.
