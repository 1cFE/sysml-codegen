# Design Review: Inherited-Attr Classifier Fix (flip the 5 xfails)

**Design:** `.project/active/classifier-fix/design.md`
**Spec:** `.project/active/classifier-fix/spec.md` (revised through `spec-review.md`)
**Review File:** `.project/active/classifier-fix/design-review.md`
**Date:** 2026-07-07
**Epic:** TRUTH-DEBT, Item 4 (SC-D); R1–R4

---

## Fundamental Assessment

**Sound approach, one must-fix on an honesty claim.** The core move is right and minimal:
widen Step-2b's single-prefix sibling test to "own prefix OR any ancestor-PartDef prefix,"
compute the ancestor set transiently at classification time, serialize only the result,
re-capture the one fixture. I verified the load-bearing mechanics against the code and they
hold: the reachability substrate, the `::`-vs-`__` trap, the compiler consequence, the
transient/snapshot compatibility, the 5-string diff, and the SC-D scoping all check out
(see the dimensional notes). No over-engineering — it's a one-predicate change reusing an
existing walk.

The problem is not the mechanism; it's a claim. **D1 sells "classification-only" as
converting a silent drop into a loud warning — "strictly better on the very severity axis
this item corrects." That is false at the boundary the spec itself identified as the
silent-drop site.** After the flip, the five attrs are `FORMULA + MANUAL_REQUIRED`, and the
graph builder's computed-attribute loop drops them through the *same* no-`else` fall-through
(`graph_builder.py:269-288`) that the spec cites as the original EXPOSE_COMPUTED silence.
The only new "loud" signal is a capture-time extraction log that is never serialized — so
the normal `generate --from-snapshot` path stays exactly as silent as before. In an epic
whose entire theme is loud-vs-silent honesty ("nothing silently dropped"), shipping that
claim uncorrected plants a new ghost. This is a **Revise**, not a Rework — the fix is to
correct the claim (and decide whether a real diagnostic belongs in scope), not to re-point
the work.

---

## Dimensional Review

### 1. Spec Compliance
**Assessment:** Concerns

Every spec [HARD] requirement has a design element: the ancestor-QN plumbing (D2), the
`ancestor PartDef`-only boundary (D3), the no-fake-test collapse (D4), the re-capture step
(Implementation Notes), the byte-identity carve-out (INV-2), the loud→silent doc loop
(Architecture). SC-D is satisfied — I confirmed the epic scopes Item 4 to classification +
xfail flip + matrix/REQ (`epic_truth_debt.md:67-69`), never to producing a module, so D1's
"classification-only" is a legitimate reading of SC-D (see D1 finding for the caveat).

The concern is the severity framing (must-fix #1). The spec's own Problem section, corrected
through spec-review, lands on "silent no-op" as the true severity and pins it to
`graph_builder.py:269-288`. The design then claims the fix makes that boundary *loud*. It
does not (see finding #1). The design is internally at odds with the spec it's implementing
on the one axis this epic cares most about.

### 2. Pattern Consistency
**Assessment:** Concerns

The design reuses the `heritage` → `Subclassification` → target walk — good, that's the
established pattern. But it overstates how much of `_supertype_closure` it reuses (should-fix
#3). The proven walk recurses via a prebuilt `qn → user-PartDef` map
(`usage_extractor.py:208`, `qn_to_partdef.get(current)`), which prunes at the user boundary —
library supertypes are named but not recursed into. The design's `_ancestor_part_qns`
instead recurses on the raw `target` element directly. That is a *new* variation, not the
live-exercised one, with two consequences the design doesn't acknowledge (finding #3).

### 3. Abstraction Quality
**Assessment:** Pass

One new module-private function, one new parameter, one widened predicate. No new class, no
schema change, leaf stays a leaf. This is the right altitude — the ancestor set is a
transient classification input and lives where classification happens. D2's rejection of
"serialize a supertype field on PartDefinitionData" is correct and well-argued (it would
rewrite every snapshot and break the carve-out).

### 4. Duplication Avoidance
**Assessment:** Concerns

`_ancestor_part_qns` deliberately does *not* share `_supertype_closure` (different QN form,
different recursion substrate). That's defensible — the leaf can't reach the `qn_to_partdef`
map. But it means a second, subtly-different supertype walker now exists, and the design
frames it as "mirrors `_supertype_closure`" when it diverges on recursion and library
pruning (finding #3). Name the divergence explicitly so a future reader doesn't "unify" the
two and reintroduce the `__`-form trap.

### 5. Data Structure Clarity
**Assessment:** Pass

`ancestor_part_qns: set[str]` of raw `::`-form QNs, built once per part, threaded as a
parameter. Explicit and traceable. The `::`-vs-`__` distinction is called out loudly and
correctly — I verified `build_element_qualified_name(target)` returns the sanitized `__`-form
(`usage_extractor.py:214`) while the design's `target.qualified_name` yields the `::`-form
that matches ref QNs and `owning_part_qualified_name` (`:194`). The "do not route through
`build_element_qualified_name`" warning is the single most important correctness note in the
design and it is right.

### 6. Route Safety
**Assessment:** Concerns

D3 keeps the boundary at "ancestor PartDef QNs only," which is correct for the fixture and
correct against `is_instance(rel, "Subclassification")` (only PartDef generalizations enter
the set). But the design's absolute — "an ancestor-prefix QN never belongs to a genuine
calc-output ref" — is false for a CalcDef nested inside an ancestor PartDef (should-fix #4).
That's a latent over-correction route the design dismisses rather than bounds.

### 7. Bets & Decisions Integrity
**Assessment:** Concerns

- **B1 (QN format)** — genuine, well-supported, Phase 0 confirms. Good.
- **B2 (heritage exposes Subclassification target)** — genuine at depth 1, but the "proven,
  live-exercised transitive" framing overstates (finding #3). The transitive step is a new
  variation; the fixture only exercises depth 1.
- **B3 (no other baseline references an inherited attr)** — honestly flagged as
  *must-verify, not assume*, with the R4 reproduce-don't-static-read discipline. This is the
  design's best bet-handling. Fold "nested CalcDef under an inherited part" into that grep
  (finding #4).
- **Hidden bet surfaced:** D1 rests on an *unstated* belief that "no module produced, but
  loud about it" is the post-fix outcome. The real post-fix outcome is "no module produced,
  and silent about it at generation." That unstated-and-wrong bet is exactly the expensive
  kind. This is must-fix #1.
- **D1 as decision** — the alternative (thread inherited names into `input_names` so they
  compile) is named and rejected with reasons; that structure is good. Reason (d) is the
  false one.

### 8. Reader Comprehension
**Assessment:** Pass

The Core Concept ("widen the notion of *mine* from one prefix to a small set") is the right
mental model, stated plainly before the mechanism. The 6-row table is concrete and honest.
The one comprehension risk is that D1(d) reads so confidently ("strictly better") that a
reader takes the severity improvement as fact and carries it forward — which is the
substance of finding #1, not a prose nit.

---

## Issues by Severity

### Critical (must-fix)

**1. D1(d)'s "silent → loud, strictly better on severity" is false at the generation
boundary — and this epic is about exactly that axis.**
After the flip the five attrs are `FORMULA + MANUAL_REQUIRED` (`compiled_expression=None`).
The graph builder's computed-attribute loop only builds a module for
`FORMULA and compilability == FULLY_COMPILABLE` (`graph_builder.py:271-274`); the `elif`
handles only `EXPOSE_CHAIN_TENTATIVE`; there is **no `else`**. So a `FORMULA + MANUAL_REQUIRED`
attr falls straight through `graph_builder.py:269-288` — no module, no `raise`, no warning —
the *same* silent no-op the spec cites as the original EXPOSE_COMPUTED sin, now reached via a
different branch. The only new diagnostic is the capture-time "FORMULA compilation failed"
warning (`computed_attribute_extractor.py:262-267`), which the design itself notes is **not
serialized** (Implementation Notes `:244-246`). So:
  - `generate --from-snapshot` (the license-free path the whole snapshot architecture
    exists to serve) re-runs no extraction → sees **zero** diagnostic.
  - `generate --models` (live) emits the extraction warning once, then the graph builder
    still silently drops the attr — no module, no generation-time signal.
So the severity is **not improved** at the boundary that matters; it is silence-for-silence,
with a transient capture-time log that evaporates. The classification is now *correct*, which
is the real win — but that is a different claim than "loud," and D1(d) should not sell a
severity improvement it doesn't deliver. **Fix:** rewrite D1(d) to state the truth (correct
classification; module still not produced; generation-time drop still silent; only new signal
is a non-serialized capture log). Then make a scope call and record it: either (a) add a loud
diagnostic at `graph_builder.py:269-288` for a `FORMULA` that reached module-build without
compiling — which is what actually delivers the "loud" and is squarely SC-F hygiene-tail
family (silent-site → fires-on-shape) — or (b) explicitly defer it as filed follow-on debt,
named, so the epic doesn't close claiming a ghost it left standing. The current "strictly
better, stop here" framing is not defensible as written.

### Major (should-fix)

**2. No test pins the five flipped attrs as `MANUAL_REQUIRED` / `compiled=None`; existing
coverage silently narrows.**
D1's central outcome — the five are `FORMULA + MANUAL_REQUIRED + compiled=None` — is asserted
by no conformance test. `test_no_compiled_expressions` (`test_computed_attributes.py:815-826`)
today iterates `EXPOSE_COMPUTED` attrs and asserts `compiled_expression is None` +
`compilability == MANUAL_REQUIRED`; it currently covers all six. Post-fix only D3 is
`EXPOSE_COMPUTED`, so the test silently narrows from 6 → 1 — a soft version of the very
collapse trap this item exists to kill (it stays green while covering almost nothing). The
byte-identity gate guards the *bytes* of `compilability`/`compiled_expression` in the
snapshot, but nothing pins the *meaning*. **Fix:** add a positive assertion that the five
`FORMULA` cases are `MANUAL_REQUIRED` with `compiled_expression=None` (extend
`test_no_compiled_expressions` to key on the FORMULA set, or add a case). This also makes the
residual silence from finding #1 explicit in a test — a test named "FORMULA but no module,
no compile" is the honest pin. The design's Component Overview lists the table rewrite and
the xfail deletion but is silent on this test; call it out.

**3. B2 overstates the transitive walk as "proven"; `_ancestor_part_qns` is a new variation,
not the live-exercised `_supertype_closure`.**
`_supertype_closure` recurses via `qn_to_partdef.get(current)` (`usage_extractor.py:208`) —
it re-resolves each supertype QN back to a *user* PartDef and prunes at the user boundary
(library QNs miss the map, recursion stops). The design's `_ancestor_part_qns` recurses on
the raw `target` element directly. Two consequences the design doesn't state: (a) **only
depth 1 is proven** — the fixture is single-level (`Derived :> Base`), so a depth-2 ancestor
chain is never exercised, and whether a raw `heritage` `target` carries a usable transitive
`.heritage` is untested (the `getattr(..., "heritage", [])` guard means it *fails silent* to
depth-1, not loud); (b) recurse-on-target **traverses into the standard library** (no
user-boundary prune), harmless for prefix matching but a broader-than-needed walk per part
per classification. **Fix:** soften B2 to "depth-1 proven; transitive-on-target is a new
variation," and either add a 2-level ancestor case to the fixture or scope the walk to the
depth the item needs; note the library-traversal difference so the two walkers aren't later
"unified."

**4. D3's "ancestor-prefix QN never belongs to a calc-output ref" is too absolute.**
A calc output resolves to its *CalcDef's* namespace (that's why D3 stays EXPOSE_COMPUTED —
`SimpleCalc` is top-level). But a CalcDef nested inside an ancestor PartDef
(`part def Base { calc def Foo { out result; } }`) has output QN
`…::'Base'::Foo::result`, which *starts with* the ancestor prefix `…::'Base'::` — so the
widened Step-2b would swallow it as a sibling ref, empty `calc_refs`, and wrongly flip a
genuine EXPOSE_COMPUTED to FORMULA. This mirrors an *existing* owning-part behavior (the same
would already happen for a CalcDef nested in the owning part), so it's not a regression, and
the fixture doesn't contain the shape — but the absolute claim is wrong and "D3 is the only
negative control needed" doesn't cover it. **Fix:** state the real invariant (calc outputs
resolve to the CalcDef namespace; the only over-correction route is a CalcDef nested under an
inherited part) and fold "nested CalcDef under an inherited PartDef" into the B3 corpus grep.

### Minor (notes)

**5. The loud→silent doc correction may miss `epic_truth_debt.md:41`.**
The design's R1 scope names `epic:340` ("The misclassification is **loud** (rejection…)") —
correct, that line exists and is the primary target. But the epic overview also says "Five
xfail cases lock a **loud** inherited-attr misclassification" (`:41`), and the summary block
uses "loud xfail" (`:16`). The item's stated purpose is to leave no ghost; sweep all "loud"
occurrences tied to *this* misclassification, not just `:340`.

**6. Verified, recorded so the design agent needn't re-prove them:**
  - **5-string diff (Q6): confirmed.** The snapshot bakes all six as
    `classification: expose_computed`, `compilability: manual_required`,
    `compiled_expression: null`. Post-fix only five `classification` strings move; compilability
    and compiled stay put; `captured_at` churns and is reverted per memory
    `byte-identity-captured-at-churn`. The claim holds exactly.
  - **D2 transient/snapshot compatibility (Q2): confirmed.** From-snapshot generation reads
    the baked `snap["computed_attributes"]` (`graph_rebuild.py:44,59`) and never calls
    `extract_computed_attributes` — it does not re-classify. So `ancestor_part_qns` only has
    to exist at capture/live time (where `part_element` is in hand), which it does. Threading
    is compatible with both paths precisely because from-snapshot is classification-frozen.
  - **Compiler consequence (Q5 / D1 mechanics): confirmed.** An inherited ref name absent from
    `input_names` compiles to `UNSUPPORTED` (`expression_compiler.py:390-392`) → `CompilationError`
    (`:209-213`) → caught → `MANUAL_REQUIRED` + warning (`computed_attribute_extractor.py:259-267`).
    Holds for the mixed cases too (L2/D2/D4): one unsupported ref fails the whole compile.
  - **SC-D scoping (Q5): confirmed.** `epic:67-69` requires the prefix check to accept the
    supertype QN, the xfail to flip, and REQ/matrix to move — never a compiled module. D1's
    classification-only scope is defensible against SC-D (the caveat is finding #1's framing,
    not the scope).

---

## Recommendations

1. **Correct D1(d) and make the residual-silence scope call (must-fix #1).** The fix's real
   win is *correct classification*, not *loud failure*. Say that. Then decide, in the design,
   whether a `graph_builder.py:269-288` diagnostic for "FORMULA that didn't compile" is
   in-scope (it's the honest delivery of "loud" and fits SC-F) or explicitly deferred as filed
   debt. Don't ship "strictly better on severity."
2. **Pin the five FORMULA + MANUAL_REQUIRED outcomes with a real test (should-fix #2)**, and
   note that `test_no_compiled_expressions` narrows to D3-only so it doesn't read as coverage
   it no longer provides.
3. **Right-size the ancestor-walk confidence (should-fix #3):** depth-1 is proven, transitive
   is a new variation; either exercise depth-2 in the fixture or scope to what's needed, and
   name the library-traversal divergence from `_supertype_closure`.
4. **Replace D3's absolute with the real invariant (should-fix #4)** and extend the B3 grep to
   nested CalcDefs under inherited parts.
5. **Sweep every "loud" tied to this misclassification (note #5)**, not just `epic:340`.

---

## Resolutions

*Filled in during Stage 4. Nothing resolved yet.*

---

**Overall:** Revise
**Next Steps:** Record resolutions here, then return to the design-agent session (or re-run
`/_my_design`) and point it at this review to incorporate. The reviewer does not edit the
design. Must-fix #1 (D1 severity claim + scope call) is the gating edit; should-fix #2–#4
sharpen honesty and confidence; note #5 closes the ghost-sweep.

ARTIFACT: .project/active/classifier-fix/design-review.md
