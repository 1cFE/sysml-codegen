# Design Review: Return-Style & Bare-Parameter Extraction (SC-2)

**Design:** `.project/active/return-style-extraction/design.md`
**Spec:** `.project/active/return-style-extraction/spec.md`
**Review File:** `.project/active/return-style-extraction/design-review.md`
**Date:** 2026-07-05

---

## Fundamental Assessment

**Sound.** The approach is the minimal correct fix, and it is unusually well-grounded.

The design's core move — replace the `is_instance(member, "AttributeUsage")` gate
with a `_is_parameter_member` predicate that also admits direction-carrying
`ReferenceUsage` members — is exactly right. I re-verified every load-bearing code
claim against HEAD and the research probe table:

- The two filter sites (`extractor.py:204`, `:242`), the AST-capture block
  (`:223-228`), `_get_direction` (`:296-306`), and the V7 guard (`:271-278`) are
  all where the design says they are.
- The probe table (research lines 106-108) confirms the direction values the
  predicate depends on: named `return` is direction **Out** (not a distinct
  `Return` kind), bare `in` is direction **In**, and the body-assignment target
  is a **direction-None** `ReferenceUsage`. So `is_in or is_out` admits the first
  two and excludes the third. The double-ingestion guard is airtight.
- `_extract_attribute` and all its sub-helpers (`_extract_default_value`,
  `_extract_unit`, `_extract_attribute_documentation`) duck-type on `name`,
  `heritage`/`FeatureTyping`, `feature_value_expression`, `cst_node` — none gate on
  `AttributeUsage`. So auto-impl for a named `return` genuinely falls out for free
  once the filter admits it. Claim verified.
- REQ-EXT-10/11/12 are collision-free (HEAD tops out at REQ-EXT-09); V8 is free
  (modeling-assumptions tops out at V7).

This is a predicate extraction, not a new abstraction. The complexity matches the
problem. Do **not** rework it.

Two findings keep this at **Revise** rather than Approve, and both are about the
one form the design reasons least carefully about — because it is the one form the
research **did not probe**:

1. **A hidden bet under V8** (the anonymous-return node shape is assumed, not
   probed — Dimension 7 / M1).
2. **A stale rationale in D4** about what the snapshot can and cannot show, now
   that `compilation_results` is landing (scrutiny #4 / M2).

Neither breaks the mechanism. Both are "the design's stated justification is
incomplete, tighten it before implement." Details below.

---

## Dimensional Review

### 1. Spec Compliance
**Assessment:** Concerns

Every success criterion maps to a design element, and the mapping is honest:

- Named `return` extraction + auto-impl → predicate branch 2 + AST block (I5, D4).
- Bare `in` → predicate branch 2.
- No double-ingestion → direction-None exclusion + name-match belt-and-braces (I2).
- Anonymous `return` diagnostic → V8 pre-scan (I3).
- Byte-identical baselines → data-flow-invariance argument + re-run proof (I1).
- Docs lockstep → 01-extraction/modeling-assumptions/verification-matrix rows (D5).
- V7 rewording → Implementation Notes (incorporates spec-review L1-1).
- A-2 stencil → Component Overview + Implementation Notes.

The gap is the **auto-impl assertion strategy under Item 2** (see M2). The spec's
central `[NEED]` — named return-style calc defs auto-implement, expression reaches
`output_expression_asts` — is asserted only by a live test (D4), on the stated
grounds that the snapshot can't show it. That ground is now false: the snapshot's
`compilation_results` block (already threaded at
`capture_extraction_snapshots.py:111` for full-pipeline models) is precisely where
CalcUsage auto-impl becomes visible offline. Since D3 makes `return_styles` a
full-pipeline model, its committed snapshot **will** pin `compilation_results`, and
the design's offline-assertion list never mentions it. Not a compliance failure —
the live test still satisfies the criterion — but the design is under-specified for
the world it explicitly tells the implementer to capture in (Risk 4: "capture
through the promoted `snapshot/` package").

### 2. Pattern Consistency
**Assessment:** Pass

- The predicate reuses `_get_direction` rather than re-deriving direction. Correct.
- The V8 pre-scan iterates `elem.owned_members` — the same ownership API as both
  member passes (`:203`, `:241`). Consistent (scrutiny #3 confirmed).
- The `anonymous_return` fixture mirrors `zero_output_calc` (extraction-raises,
  live-only, no snapshot). Established pattern.
- The A-2 stencil fix follows the existing sysml-conventions stencil location.

### 3. Abstraction Quality
**Assessment:** Pass

One private predicate, two call sites, one short pre-scan. Nothing wraps anything
that didn't need wrapping. D1 correctly rejects inlining the two-branch check
(would let the two passes drift, violating the HARD "both passes agree"
requirement). D2's choice of a standalone V8 scan over a flag-in-the-loop is the
right call — it decouples V8 correctness from the filter's admission logic. A
senior engineer would not ask "why is this here?" of anything in this design.

### 4. Duplication Avoidance
**Assessment:** Pass

The single shared predicate is itself the anti-duplication move (D1). No parallel
structures introduced.

### 5. Data Structure Clarity
**Assessment:** Concerns

The four-forms table (design lines 170-176) is the clearest artifact in the design
and traces each syside node shape to its predicate branch and result. Good.

The unclear part is the **content of the new `return_styles` snapshot**. The design
treats the snapshot as I/O-attribute assertions only (Validation Approach: input/
output counts + no-double-ingestion). But a full-pipeline snapshot carries far more —
`compilation_results` chief among it. The design does not say what that block should
contain for the four styles (style B: one entry, compilable; style D: no entry,
skipped), nor that it becomes a pinned, committed part of the fixture. See M2.

### 6. Route Safety
**Assessment:** Concerns

V8 raises unconditionally on the **first** raw member with direction Out and an
empty sanitized name. Two questions the design does not answer (scrutiny #3):

- **Can a calc def have both an anonymous `return` and a named output?** If yes,
  V8 rejects a calc def that would otherwise extract a usable output — because V8
  scans raw members and never consults `output_attributes`. The design frames V8 as
  firing "before V7" on a calc that is zero-output anyway; the mixed case breaks
  that framing (V7 wouldn't fire; V8 would). This is likely not constructible legal
  SysML (a calc def has one result parameter), which is why I rate it Minor, not
  Major — but the design should state the intended behavior and confirm the
  legality rather than leave the unconditional raise unexamined.

- **Is the anonymous-return node actually a direction-Out, empty-name member?**
  This is the hidden bet — see M1. If syside synthesizes a name or reports
  direction None, V8's route never fires and the anonymous return falls through to
  V7 (or worse). V8's entire routing rests on an unprobed node shape.

### 7. Bets & Decisions Integrity
**Assessment:** Concerns

The three stated bets (B1 named-return direction/expression, B2 body-assignment
direction-None, B3 no fixture uses a direction-carrying ref) are genuine reality
claims, each with a stated failure mode, and each is backed by the probe table. The
decisions (D1-D6) each name the rejected alternative. That part is honest.

**Hidden bet (M1).** There is a fourth load-bearing belief the design does not
state: *the anonymous `return : Real = expr;` form is a direction-Out
`ReferenceUsage` whose name sanitizes to empty.* V8's entire detection predicate is
built on it. And it is the **one form absent from the research probe table** — the
probe (research lines 106-108) covers the three supported forms plus the
body-assignment double-member, but never the anonymous form. Line 115(b) only
*recommends* rejecting anonymous return; it does not report a probe of its node
shape. So the belief that makes V8 fire is exactly the belief no one has checked.

If it is wrong in either axis:
- *Name not empty* (syside synthesizes a `result` name) → V8 never fires, and the
  form may even extract a spurious output. Silent.
- *Direction not Out* (reported None) → V8's direction filter skips it → falls to
  V7's generic message. The precise-diagnostic requirement (I3, HARD) fails
  silently.

This should be promoted to a stated bet (B4) and — more importantly — added to the
"De-risk first" handoff list, which currently tells the implementer to probe the
named-return expression and style-D generation but **not** the anonymous-return
node shape. The de-risk list has a gap precisely where the unprobed bet lives.

### 8. Reader Comprehension
**Assessment:** Pass

A tired engineer can read this once and know the four forms, the one rejected form,
the single predicate, and what's deferred. The Core Concept states the real problem
("is this a parameter?" vs the proxy "is this an AttributeUsage?") plainly before
the mechanism. The four-forms table anchors the abstraction to concrete node shapes.
No comprehension-blocking voice.

---

## Issues by Severity

### Critical
- None.

### Major
- **M1 · Hidden bet: anonymous-return node shape is unprobed.** V8's detection
  (direction-Out + empty sanitized name) is the one form the research probe table
  never covered. If syside names the anonymous result or reports direction None, V8
  silently misses it and I3 (HARD) fails. Promote to a stated bet; add to the
  de-risk-first list. — Dimension 7 / scrutiny #1.
- **M2 · D4 rationale is stale under Item 2's `compilation_results`.** D4 asserts
  auto-impl presence is "invisible offline" because the snapshot nullifies
  `output_expression_asts`. But `compilation_results` (threaded at
  `capture_extraction_snapshots.py:111`; built at `pipeline_builder.py:547-567`,
  compiling only AST-bearing defs, try/excepted) surfaces it offline: style B gets a
  compilable entry, style D is skipped. Because D3 makes `return_styles` a
  full-pipeline model, its committed snapshot pins this block, which the design's
  offline assertions never mention. Keep the live test, but reconcile the rationale
  and specify the snapshot's `compilation_results` content. — Dimensions 1 & 5 /
  scrutiny #4.

### Minor
- **m1 · V8 mixed-case behavior unstated.** An anonymous `return` co-existing with a
  named output would be rejected by V8's unconditional raise, masking a usable
  output. Likely not legal SysML; state the intended behavior and confirm. —
  Dimension 6 / scrutiny #3.
- **m2 · V7 edit must match the live string.** The design's "revised V7 wording"
  targets both `extractor.py:272-278` and `modeling-assumptions.md:350`. The live
  modeling-assumptions text (`:350`) differs slightly in phrasing from the extractor
  string; the implementer must match each live string, not assume they are
  identical. Housekeeping.
- **m3 · Style D full-pipeline capture is de-risked but load-bearing.** The design's
  Risk 1 mitigation is sound — `pipeline_builder.py:547` skips no-AST defs and
  `graph_builder.py:239` conditionally consumes compilation results, so style D
  won't crash capture. Worth confirming live per the handoff, since D3's
  full-pipeline choice depends on it. (Recording as verified-in-review, low risk.)

---

## Recommendations

1. **Add B4 and extend the de-risk-first list (M1).** State the anonymous-return
   node-shape bet explicitly, and make "probe the anonymous `return : Real = expr;`
   form live — confirm it is a direction-Out member whose `sanitize_name` is empty"
   the first de-risk step, ahead of writing V8. This is the cheapest possible
   insurance and it closes the one gap the research left open.

2. **Reconcile D4 with `compilation_results` (M2).** Correct the rationale: offline
   is blind only to the raw AST object, not to auto-impl — `compilation_results`
   makes style B (entry present) vs style D (skipped) observable in the committed
   snapshot. Decide explicitly whether to *also* assert on `compilation_results`
   offline (style B present + compilable, style D absent) or to state why the live
   test remains the sole auto-impl assertion. Either way, name `compilation_results`
   in the Validation Approach so the implementer isn't surprised by it in the diff.

3. **State V8's mixed-case behavior (m1).** One sentence: whether an anonymous
   `return` alongside a named output is possible and, if so, that V8 still rejects
   it (and why that's acceptable).

---

## Resolutions

*Filled in during Stage 4. One entry per resolved issue — this is what the design
agent reads to incorporate the review.*

---

**Overall:** Revise
**Next Steps:** Once resolutions are recorded, re-run `/_my_design` (or return to
the design-agent session) and point it at this review to incorporate. The reviewer
does not edit the design.
