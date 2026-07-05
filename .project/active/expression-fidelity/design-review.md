# Design Review: Expression Reconstruction Fidelity (SC-6)

**Design:** `.project/active/expression-fidelity/design.md`
**Spec:** `.project/active/expression-fidelity/spec.md`
**Review File:** `.project/active/expression-fidelity/design-review.md`
**Date:** 2026-07-05
**Reviewer posture:** skeptical senior engineer; verified every code-facing and spec-facing claim against HEAD (1f1b227) and the KerML spec.

---

## Fundamental Assessment

**Sound approach, but the second fix is specified with correctness bugs, and its
headline evidence is false.**

The overall shape is right and I would not rework it:

- Two local defects, correctly diagnosed: literal branches sit after the
  invocation catch-all (dead code), and the operator renderer drops parens.
- The fix is local and structural — reorder the dispatch, teach the renderer one
  parenthesization rule. No new abstractions, no over-engineering.
- The second half is a **review gate**, not code, because the change reaches
  executable fields only on the aggregation path and only inertly for today's
  corpus. Making the byte-identity diff the gate (INV-1) is the correct backstop,
  and the aggregation-path analysis is careful and matches the spec review's
  resolution.
- The precedence **table** is correct. I had the kerml-expert verify it against
  KerML Table 6 (§8.2.5.8.1): `**`/`^` right-associative, unary `-`/`not` tighter
  than power, `not` at unary precedence, `**`/`^` same rank, and the full ordering
  — **all five claims hold**. Generated docstrings built on the table itself will
  bracket correctly.

So the foundation is fine. But the heart of the second fix — the `needs_parens`
helper and the evidence that drove its design — does not survive scrutiny:

1. **Appendix A's "zero paren churn" is false.** The baseline strings it analyzed
   were produced by a reconstructor that *structurally cannot emit parens*, so
   they cannot show whether the source had a meaning-changing group. At least four
   committed baselines have real groups that the fix will (correctly) restore.
   Appendix A explicitly lists two of them as "flat, no group."
2. **The `needs_parens` pseudocode has a rank/tightness polarity contradiction**
   with its own precedence table — an implementer following the doc literally
   inverts every unequal-precedence decision, which is exactly the
   `(a + b) * c` category the fix targets.
3. **The "unary operands never need wrapping" claim is wrong** — it renders wrong
   math for `-(a + b)`, `not (a and b)`, `not (a == b)`.
4. **The single repro fixture exercises only the equal-precedence branch**, so it
   cannot catch #2 or #3 — and #1 + #2 can mask each other at regen.

These are fixable in the design without changing the approach. Verdict is
**Revise**, but the three Critical items must be corrected before `/_my_plan`,
because they are wrong-math and wrong-evidence, not polish.

---

## Dimensional Review

### 1. Spec Compliance
**Assessment:** Concerns

The design covers every spec requirement structurally: `is_instance` dispatch
before the catch-all (HARD), `is_literal_expression` alignment (HARD), the
two-tier regen and byte-identity gate (HARD), REQ-AST-03 revision + known-deviation
note (HARD), the real-AST fixture (HARD), and the license-window fallback. The
aggregation-path invariant is stated correctly (INV-1, corpus-scoped-and-checked),
matching the spec review's L1-1 resolution.

The gap is the `[NEED]` requirement — "operator expressions preserve
parenthesization so displayed math is unambiguous" (spec:121). The design's
mechanism for this (the `needs_parens` helper) is specified with two correctness
bugs (Critical C2, C3 below). A design can technically name the requirement and
still fail to meet it if the mechanism is wrong. It is wrong for the looser-child
and unary cases, so the spec's core display-fidelity goal is not yet met by the
design as written.

### 2. Pattern Consistency
**Assessment:** Pass

`is_instance` dispatch matches the rest of `reconstruct_expression` (FCE/OE/FRE
already use it) and `is_literal_expression`. Revising REQ-AST-03 in place (D5)
rather than superseding it is the right call — the FCE<OE<FRE ordering is still
canonical; only the "...Literal" tail is defective. The license-gating reuse of
`requires_license` follows an existing pattern (`test_snapshot_generation.py:35-47`),
though the reuse mechanism is under-specified (Minor m2).

### 3. Abstraction Quality
**Assessment:** Pass

No new abstractions beyond a precedence dict and a `≤10`-line helper. That is the
right weight for the problem. The helper is the correct locus for the parens rule.
The problem is the helper's *specification* (Dimension covered under Critical), not
its existence or altitude.

### 4. Duplication Avoidance
**Assessment:** Concerns

One concrete duplication risk: `_license_available` (`test_snapshot_generation.py:35`)
is a module-private function that spins up a full `load_models()` probe. The design
says the real-AST test "reuses this exactly" but the new test lives in a different
file. Copy-pasting `_license_available` means two live license probes per run.
Factor the marker to `tests/conftest.py` or `tests/helpers/` so it is imported, not
duplicated (Minor m2).

### 5. Data Structure Clarity
**Assessment:** Concerns

The precedence representation is internally inconsistent, and this is a real
implementer trap (Critical C2). The table (`design.md:227-238`) is labeled "Rank"
with "Rank 1 = tightest" — smaller number binds tighter. The `needs_parens`
pseudocode (`design.md:250-257`) reads `if cp < pp: return True # child binds
looser`. For "cp < pp" to mean "child binds looser," `prec()` must return
*tightness* (larger = tighter) — the **opposite** polarity from the rank column.
The design never says `prec()` returns the inverse of the rank number. An
implementer who builds `prec` as a dict straight from the rank table gets every
unequal-precedence decision backwards. This is the single most dangerous ambiguity
in the doc.

### 6. Route Safety
**Assessment:** Pass

Dispatch routing is explicit and the reorder is safe: literal `is_instance` checks
are false for OE/FRE/FCE (B1, INV-4, confirmed — literals have no subtype overlap
with operator/reference nodes), so moving them ahead of the invocation catch-all
cannot capture a non-literal node. The catch-all correctly becomes the last branch
before `str(node)`. The FCE<OE<FRE ordering the conformance test guards is
untouched (see Bets & Decisions and Reader Comprehension for the confirmation).

### 7. Bets & Decisions Integrity
**Assessment:** Concerns

The stated bets (B1–B3) are honest and each carries an "if false" consequence. B1
is verified. B2/B3 are the corpus-scoped empirical claims and are correctly framed
as checked-not-structural.

But there is a **hidden bet the design does not state**: *"the buggy reconstructor's
output strings are a faithful census of which source expressions contain
meaning-changing groups."* This bet is load-bearing for Appendix A, D1's evidence,
and the regen review's "expected: none" paren line — and it is **false**. A
reconstructor that never emits parens erases exactly the information Appendix A
tries to read from its output. This is the most expensive kind of unstated bet:
wrong, and everything downstream leans on it (Critical C1).

D1 (precedence-aware over always-paren) is the right decision and *survives* the
corrected evidence — in fact it is strengthened: precedence-aware restores the
handful of real groups exactly, where always-paren would bury them under ~30
redundant nestings. But D1's *stated* justification ("zero baselines gain a paren")
must be replaced with the true one.

D3 (`"*"` for `LiteralInfinity`, `"null"` for `NullExpression`) records its
rationale and both are confirmed absent from the corpus — genuinely defensive.
D4/D5 are sound.

### 8. Reader Comprehension
**Assessment:** Concerns

The doc is well-structured and mostly readable. Two comprehension failures, both
load-bearing:

- The rank-table-vs-pseudocode polarity mismatch (C2) means a careful reader
  cannot implement the helper correctly from the doc without guessing which
  convention `prec()` uses.
- The "unary operands never need wrapping" sentence (`design.md:260`) reads as a
  settled fact with a plausible-sounding justification ("they bind tighter than
  any binary"). The justification conflates the unary *operator* binding tight with
  the unary *operand* being atomic. A reader trusts it and ships `-a + b` for
  `-(a + b)` (C3).

Confirmed correct for the reader's benefit: the FCE<OE<FRE conformance test
(`test_ast_dispatch_invariant.py:209-223`) asserts `fce < oe < fre` as a *relative*
ordering only (line 220), with no absolute-position check and no assertion on
literal position. Moving literals to after FRE / before the catch-all leaves it
green. The design's claim on `design.md:325` is accurate.

---

## Issues by Severity

### Critical (must fix before implementation)

- **C1 — Appendix A's "zero paren churn" is false; ≥4 baselines gain parens.**
  The buggy reconstructor emits `f"{left}{op}{right}"` with no parens
  (`expression_utils.py:96`), so a source group like `(a + b) * c` renders as
  `a + b * c` — the group is invisible in the stored string. Appendix A read those
  strings and concluded "no baseline has a meaning-changing group." That inference
  is unsound: the strings cannot carry the evidence. Concrete counterexamples,
  verified against source + committed snapshot:
  - `attr_expr_probe/design.sysml:62` — `(r_inner + r_outer) / 2.0 - r_major`.
    Committed snapshot stores `r_inner + r_outer / LiteralRationalEvaluation() -
    r_major` (group gone). Appendix A lists this as "`/` binds tighter → flat" —
    **wrong**; the `/` node's left child is the `+` group, which binds looser and
    needs parens.
  - `attr_expr_probe/design.sysml:77-78` — `(m_neutron * p_fusion) + p_input +
    eta_thermal * (f_pump * eta_pump + f_subsystem) * (m_neutron * p_fusion)`.
    Committed snapshot flattens it to `m_neutron * p_fusion + p_input + eta_thermal
    * f_pump * eta_pump + f_subsystem * m_neutron * p_fusion` — different math.
    Appendix A lists the flattened form as a natural-precedence chain. The
    `(f_pump * eta_pump + f_subsystem)` group (a `+` inside `*`) will gain parens.
  - `expression_binding_probe/library.sysml:8` — `combined_input * (1.0 +
    tax_rate)`. `+` right-child of `*` → gains parens.
  - `catf_mfe_model/.../performance_metrics.sysml:222` —
    `(target_plates.surface_area_inner + target_plates.surface_area_outer) * ...`
    → gains parens.

  Impact: the fix is *working correctly* by restoring these groups — the code is
  not wrong. But the design's evidence and its prediction are wrong, which
  corrupts the regen review (see M1). Rewrite Appendix A: the buggy strings cannot
  reveal groups; enumerate the real paren-gainers from the **source models** (or
  re-parsed ASTs), and state that the exact set is confirmed at Tier-1 regen.

- **C2 — `needs_parens` rank/tightness polarity is contradictory.** The precedence
  table numbers rank 1 = tightest (smaller = tighter). The pseudocode's
  `if cp < pp: return True # child binds looser` requires `prec()` to return
  tightness (larger = tighter) — the opposite polarity. Test it on the primary
  target `(r_inner + r_outer) / 2.0`: parent `/` (rank 4), child `+` (rank 5),
  left side. With `prec := rank`, `cp=5 > pp=4 → return False` (no parens) — the
  bug persists. With `prec :=` tightness, `cp < pp → return True` (parens) —
  correct. The doc must state explicitly that `prec()` returns binding tightness
  (the inverse of the rank column), or renumber the table so smaller = looser. As
  written, the natural implementation inverts every unequal-precedence decision —
  precisely the meaning-changing groups the fix exists to restore.

- **C3 — "unary operands never need wrapping" renders wrong math.** `design.md:260`
  exempts unary operands from parens because "they bind tighter than any binary."
  That confuses the unary *operator* (which does bind tight, KerML rank 2) with
  the unary *operand* (which can be a looser binary). Because KerML puts unary
  above **all** binary including power, any binary operand of a unary operator
  binds looser and needs parens:
  - `-(a + b)` — current/proposed unary render `f"-{operand}"`
    (`expression_utils.py:101`) yields `-a + b` = `(-a) + b`. Wrong.
  - `not (a and b)` → `not a and b` = `(not a) and b`. Wrong.
  - `not (a == b)` → `not a == b` = `(not a) == b` (KerML `not` is tight). Wrong.
  The unary branch must apply `needs_parens` to its operand (child binds looser
  than the unary op → wrap). This was one of the five cases scrutiny #1 named, and
  the design gets it inverted.

### Major (should fix)

- **M1 — Regen review checklist bakes in the false "expected: none" paren line.**
  Checklist item 2 (`design.md:288-290`) tells the reviewer to expect added parens:
  "none, per Appendix A." Given C1, parens **will** bloom across `attr_expr_probe`
  (×2), `expression_binding_probe`, and `catf_mfe_model`. A reviewer primed to
  expect zero will either hard-stop on legitimate churn, or — worse — if C2's
  polarity bug also ships, the missing parens match the "expect none" prime and the
  reviewer waves through a persisting bug. C1 and C2 can mask each other exactly
  here. Fix: replace "expected: none" with the enumerated paren-gainer set (from
  the corrected Appendix A), so the reviewer distinguishes expected group-restoration
  from an actual regression.

- **M2 — INV-3's single repro fixture cannot prove the helper correct.** The repro
  `capacity * rate + capacity * (rate / 2.0) * 3.0` exercises only the
  **equal-precedence, associativity-unfavored** branch (right child of a left-assoc
  `*`). That branch is correct regardless of the C2 polarity bug, so the repro test
  passes even if C2 and C3 ship. The fixture (or the unit tests around the helper)
  must also cover: a looser child on each side (`(a + b) * c`, `a * (b + c)`) to
  exercise the `cp≠pp` branches and catch C2; a unary-over-binary case (`-(a + b)`,
  `not (a and b)`) to catch C3; and power associativity (`a ** b ** c` renders flat,
  `(a ** b) ** c` gains parens) to pin the right-assoc branch. These can be
  mock-free unit tests on `reconstruct_operator_expression` if a full parsed AST is
  costly; the point is branch coverage, not a live license.

### Minor (consider)

- **m1 — `LiteralInfinity` → `"*"` readability.** Defensive-only and KerML-faithful,
  rationale recorded (D3); confirmed absent from the corpus. But in a rendered
  docstring `x * *` (multiply-then-infinity) is genuinely ambiguous. Worth one
  sentence in D3 acknowledging the readability cost so the choice is a recorded
  trade, not an oversight. No change to the decision required.

- **m2 — License-marker reuse mechanism unspecified.** `_license_available` /
  `requires_license` are private to `test_snapshot_generation.py:35-47`. State how
  the new test acquires the marker (factor to `tests/conftest.py` or a helper and
  import — do not duplicate `_license_available`, which would run a second live
  probe).

- **m3 — Verify guard-test counts stay green after literals switch to `is_instance`.**
  Two conformance guards could interact with the reorder: `REQ-AST-04`'s exact
  counts (5 dual-check / 8 multi-type dispatch functions,
  `test_ast_dispatch_invariant.py:252-276`) and any `is_literal_expression` callers
  that now see `LiteralInfinity`/`NullExpression` return `True`. Both are expected
  to stay green (`reconstruct_expression` is already multi-type; the two new literal
  types are unlikely to appear in the corpus), but the plan should assert it rather
  than assume it.

- **m4 — "No existing fixture exercises this shape" (`design.md:64`, D4) is
  imprecise.** Existing fixtures **do** contain meaning-changing groups (the `cp≠pp`
  category — C1's list). What the corpus lacks is the *equal-precedence
  associativity-unfavored* shape the repro targets. The new fixture still earns its
  place (it uniquely covers that branch and stays isolated from `attr_expr_probe`'s
  regen), but the justification should say "no existing fixture exercises the
  equal-precedence associativity case," not imply the corpus has no groups at all.

---

## Recommendations

1. **Fix the paren helper spec (C2, C3) and add branch-covering tests (M2).** State
   `prec()` polarity explicitly, apply `needs_parens` to unary operands, and prove
   the helper with unit tests over all branches — looser child both sides, unary
   over binary, power associativity — not just the equal-precedence repro. This is
   the wrong-math core; fix it first.
2. **Rewrite Appendix A and the paren-churn evidence (C1).** Re-derive the
   paren-gainer set from source models, not from buggy strings. State the honest
   D1 justification (precedence-aware restores ~4 real groups; always-paren adds
   ~30 redundant nestings). Keep D1 — it is strengthened, not weakened.
3. **Correct the regen review's paren expectation (M1).** Replace "added parens
   expected: none" with the enumerated set, and note that C1+C2 could mask each
   other so the reviewer must positively confirm each expected paren appears, not
   just that "no surprise parens" appeared.
4. **Tidy the minors (m1–m4)** in the same pass: record the `"*"` readability
   trade, specify the license-marker factoring, add the guard-count assertion to
   the plan, and sharpen the D4 justification.

Everything else — the dispatch reorder, `is_instance` alignment, the byte-identity
gate, the REQ-AST-03 revision + deviation note, the license-window fallback, the
aggregation-path analysis, and the precedence **table** — is correct and needs no
change.

---

## Resolutions

All three Criticals, both Majors, and all four Minors applied to `design.md`
(2026-07-05). Approach unchanged; only the second fix's math, evidence, and test
coverage corrected.

- **C1 — Appendix A rewritten from source.** Replaced the "zero paren churn"
  census (which read paren-erased output strings) with a source-verified table of
  the four paren-restorers: `attr_expr_probe/design.sysml:62` and `:77-78`,
  `expression_binding_probe/library.sysml:8`,
  `catf_mfe_model/library/components/divertor.sysml:222`. Each confirmed against
  the actual `.sysml` source. The Research Findings evidence paragraph and D1's
  justification restated honestly: precedence-aware *restores* ~4 real groups;
  always-paren buries them under ~30+ redundant nestings. D1 stands, strengthened.

- **C2 — polarity fixed.** Stated one convention explicitly: `RANK[op]` is the
  table's rank number, smaller = tighter; all comparisons written against it
  directly ("child looser" = `RANK[child] > RANK[parent]`). No separate
  tightness number. Rewrote `needs_parens` accordingly.

- **C3 — unary operands wrap.** Removed the false "unary operands never need
  wrapping." The unary branch now runs `needs_parens(unary_op, operand,
  "operand")`; since unary is rank 2 (tighter than all binary), any binary operand
  wraps. `-(a + b)`, `not (a and b)` render correctly.

- **Hand-traces added** (part of the artifact): a-(b-c), a/(b*c), -(a+b),
  a**(b**c), (a**b)**c — all five traced in a table, proving right-associativity
  and unary handling.

- **M1 — regen checklist corrected.** "Expected: none" replaced with the
  enumerated paren-restorer set; reviewer must *positively confirm* each expected
  paren appears (a missing one is a hard stop), so C1+C2 cannot mask each other.

- **M2 — test matrix extended.** The live fixture (Component 4) now carries all
  four branch shapes (equal-prec repro, unequal-prec both sides, unary-over-binary,
  power associativity). Added Component 5: no-license branch-coverage unit tests
  pinning the five hand-traces so C2/C3 stay caught when the license-gated test
  skips. Offline guard (Component 6) also asserts the four paren-restorers appear.

- **m1** — D3 records the `x * *` readability trade for `LiteralInfinity → "*"`.
- **m2** — Validation Approach specifies factoring `requires_license` /
  `_license_available` into `tests/conftest.py`, imported not duplicated.
- **m3** — Validation Approach adds a guard-count assertion (REQ-AST-04 counts,
  `is_literal_expression` callers) for the plan to check, not assume.
- **m4** — D4 and the Research Findings claim sharpened to "no fixture exercises
  the *equal-precedence associativity-unfavored* shape," not "no fixture has
  groups."

---

## Verification Round (2026-07-05)

Targeted re-check of the four applied areas. All pass; no residual blockers.

**1. `needs_parens` polarity + five hand-traces — PASS.** The doc now states one
convention (`design.md:296-302`): `RANK[op]` from the table, smaller = tighter,
all comparisons written against the rank directly ("child looser" =
`RANK[child] > RANK[parent]`). The pseudocode (`design.md:311-317`) matches it.
I re-traced all five rows of the hand-trace table (`design.md:334-340`)
*independently*, using ranks unary=2, `**`/`^`=3, `*`/`/`=4, `+`/`-`=5:

| Case | My trace | Design row | Match |
|---|---|---|---|
| `a-(b-c)` | `-`(5)/`-`(5)/right, equal, left-assoc→unfavored=right → wrap | wrap | ✓ |
| `a/(b*c)` | `/`(4)/`*`(4)/right, equal, left-assoc→right → wrap | wrap | ✓ |
| `-(a+b)` | unary`-`(2)/`+`(5)/operand, `5>2`→looser → wrap | wrap | ✓ |
| `a**(b**c)` | `**`(3)/`**`(3)/right, equal, right-assoc→unfavored=left; side=right → no wrap | no wrap | ✓ |
| `(a**b)**c` | `**`(3)/`**`(3)/left, equal, right-assoc→left; side=left → wrap | wrap | ✓ |

Every row matches, and each renders the mathematically correct grouping. The C2
inversion trap is closed — feeding rank numbers straight into the pseudocode now
gives right answers, and the doc explicitly forbids building a separate tightness
number.

**2. Appendix A source-verification — PASS.** Spot-checked all four restorers
against the actual `.sysml` (not the design's prose):
- `attr_expr_probe/design.sysml:62` → `(r_inner + r_outer) / 2.0 - r_major` ✓
- `expression_binding_probe/library.sysml:8` → `combined_input * (1.0 + tax_rate)` ✓
- `catf_mfe_model/library/components/divertor.sysml:222` → the constraint
  `total_heat_load <= n_divertor_modules * (target_plates.surface_area_inner +
  target_plates.surface_area_outer) * target_plates.heat_flux_capability` ✓
  (correctly noted as constraint text, which `reconstruct_expression` also serves).
- `attr_expr_probe/design.sysml:77-78` (verified prior round) ✓

All four file:line references are accurate and each is a genuine looser-or-equal-
unfavored child that the fix restores.

**3. Unary branch — PASS.** The unary operand now runs the same helper
(`design.md:320-326`): `-(a + b)` wraps; `- -a` stays flat (nested unary operand
is atomic, `binary_op_of → None`); and the KerML-specific `-(a ** b)` wraps while
`(-a) ** b` renders flat as `-a ** b` (unary tighter than power). Correct in both
directions.

**4. Regen checklist positive-confirm — PASS.** Checklist item 2
(`design.md:367-375`) now requires the reviewer to *positively confirm each
enumerated paren appears*, with a missing one a hard stop "same as a surprise one"
— explicitly because a C2-class bug would silently drop exactly these parens. The
offline totality guard (Component 6, `design.md:261-265`) independently asserts the
four restorers are present in regenerated snapshots. M1 is resolved with a genuine
double-check, not a relabel.

**Residual (non-blocking, plan-time):** Component 5's offline unit tests rely on a
named-type stub driving `reconstruct_operator_expression`'s type checks
(`design.md:251-259`). The design flags the right caveat itself — stubs cover the
parens/precedence logic but *not* dispatch ordering, which still needs the
real-AST test. The plan should just confirm the stub actually exercises the
helper's `is_binary_operator_expr` check (trivial if the helper keys off
`hasattr(operator)` + operand count; needs the name-fallback if it keys off
`is_instance`). Low risk, no design change required.

---

**Overall:** Approve
**Next Steps:** Proceed to `/_my_plan`. The three Criticals (C1 evidence, C2
polarity, C3 unary), both Majors (M1 regen expectation, M2 test coverage), and all
four Minors are resolved in `design.md`, verified against source and re-traced
independently. The five hand-traces are the acceptance test for the helper —
implement them exactly. One low-risk plan-time confirmation on the Component 5 stub
mechanism; nothing blocking.
