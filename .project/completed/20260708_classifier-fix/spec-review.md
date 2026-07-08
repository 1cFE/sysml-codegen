# Spec Review: Inherited-Attr Classifier Fix (flip the 5 xfails)

**Spec:** `.project/active/classifier-fix/spec.md`
**Contract:** `claude-pack/commands/_my_spec.md`
**Review File:** `.project/active/classifier-fix/spec-review.md`
**Date:** 2026-07-07

---

## Reality Check

**Concerns (Revise, not Rework).** The work item is real and sound: Step-2b's prefix
check does fail for inherited attributes, the root cause is genuinely pinned
(`test_computed_attributes.py:794`), and the fix direction (accept an ancestor-PartDef
namespace QN) is correct. The spec also surfaced the test-honesty trap accurately.

But two load-bearing claims are wrong or missing against the code at HEAD:

1. The "loud (a rejection)" framing is **false** — the code silently drops
   EXPOSE_COMPUTED. Doc 16's "silent no-ops" is the correct description, and the
   spec's reconciliation requirement currently points the docs the wrong way.
2. The classifier fix **cannot flip the tests on its own**. The conformance tests read
   a committed snapshot that bakes `classification: "expose_computed"`. Flipping the
   xfails requires re-capturing that snapshot — a required, license-dependent, in-scope
   step the spec never mentions.

Both are targeted edits, not a re-point of the work item. Verdict: **Revise**.

---

## Audit

### Lens 1 — Faithfulness

**L1-1 · Direct claim (MUST-FIX):** The spec's Problem section says an inherited-attr
attribute lands in EXPOSE_COMPUTED as "a **loud** wrong classification (a rejection, not
a silent wrong value)" (`spec.md:31-34`), and the epic/matrix repeat it
(`verification-matrix.md:136`: "**loud** (EXPOSE_COMPUTED rejection, not silent wrong
output)"). **The code contradicts this.** The graph builder's computed-attribute loop
handles only FORMULA and EXPOSE_CHAIN_TENTATIVE; EXPOSE_COMPUTED falls through with no
`else`, no `raise`, no warning (`resolution/graph_builder.py:269-288`). The extractor
returns EXPOSE_COMPUTED with no diagnostic (`computed_attribute_extractor.py:163`). The
integration test literally asserts this: `test_expose_computed_no_module_no_error`
("codegen didn't error", `tests/integration/test_computed_attributes_e2e.py:135-142`).
So the behavior is a **silent no-op** — no module, no diagnostic, no wrong value —
exactly what doc 16 says (`16-computed-attributes.md:392-395`, "silently produce no
pipeline module ... silent no-ops"). The half that's true is "not a silent wrong value"
(no wrong number is emitted). The half that's false is "loud / a rejection."

Consequence: the spec's `[INFERRED]` reconciliation requirement (`spec.md:116-120`)
frames doc 16 as the outlier to be brought in line with the "loud" epic/matrix framing.
That is backwards — doc 16 is correct. The reconciliation must resolve **toward
"silent,"** and the matrix `:136` block *and* the spec's own Problem framing carry the
error that needs correcting, not doc 16. The spec should (a) fix its Problem wording to
"silent no-op," (b) require the docs loop to pin the code-verified truth *with the
citation* (`graph_builder.py:269-288` / the e2e test), not merely "don't leave them
disagreeing," and (c) add the matrix `:136` "loud (EXPOSE_COMPUTED rejection)" phrase to
the list of text to correct. "No model hits it, so nothing breaks in production" still
holds and still motivates the item — the *severity mechanism* is what's misstated.

**L1-2 · Direct claim (MUST-FIX):** The spec treats the fix as a code change to
`computed_attribute_extractor.py` plus a test-table flip, and asserts the five xfailed
cases "PASS as real assertions" (`spec.md:50-53`). But classification is computed in the
**extraction** layer and **serialized into the committed snapshot**: the fixture reads
`load_extraction_snapshot("unresolvable_attr_probe")`
(`tests/conformance/conftest.py:128`), and that JSON bakes
`"classification": "expose_computed"` ×6 (verified in
`tests/fixtures/unresolvable_attr_probe/extraction_snapshot.json`). The conformance
tests read the baked value, **not a live classifier run**. A Step-2b code fix therefore
changes nothing the suite observes until the snapshot is re-captured via
`scripts/capture_extraction_snapshots.py` (the fixture is registered there in
`EXTRACTION_ONLY_MODELS`, `scripts/capture_extraction_snapshots.py:118`). Re-capture is
live extraction → needs the syside license (memory: `syside-license-via-scripts-not-dashc`),
falls under R3 capture discipline, and **rewrites the committed JSON** (5 values flip
EXPOSE_COMPUTED→FORMULA; D3 must stay expose_computed). The spec's Scope, Success
Criteria, and Open Questions omit this entirely. As written, "flip the xfails to PASS"
is not achievable. This must be named as an in-scope step, with its license dependency
and its committed-fixture diff.

### Lens 2 — Problem & Approach

**L2-1 · Question to the user (SHOULD-FIX):** The whole fix rests on the classifier
being able to *see* the owning part's ancestor PartDef QNs. The spec acknowledges the
data isn't plumbed today — `_classify_attribute_expression` gets a single
`owning_part_qualified_name` string (`computed_attribute_extractor.py:66`), and
`sibling_attr_names` is built from `owned_members`, which excludes inherited attrs
(`computed_attribute_extractor.py:188-191`) — and marks the supertype-chain extraction
in-scope (`spec.md:77-84`, Open Question `:139-143`). That's good. **But it assumes the
supertype chain is reachable from `part_element` at extraction time and never confirms
it.** Everything downstream (the `ancestor_part_qns` parameter, the Step-2b predicate)
is dead if SysIDE doesn't surface generalizations off the raw PartDef element the
extractor holds. This is the one genuinely open design unknown, and it's load-bearing.
The spec should flag "confirm SysIDE exposes the generalization/supertype chain from
`part_element`" as the first thing design must verify — not fold it silently into "exact
plumbing is a design choice." Do we already extract supertype/generalization info
anywhere (e.g. the retype/`:>>` machinery behind REQ-LVP-09 / REQ-VBR-11 clearly reaches
inheritance data)? If so, name it as the substrate; if not, the reachability check is
the first design gate.

**L2-2 · Note (holds up):** The over-correction boundary is defined correctly. D3
(`mixed_expose = my_calc.result * base_rate`) stays EXPOSE_COMPUTED because it carries a
genuine calc-output ref (`result`, whose QN is in the CalcDef namespace — *not* an
ancestor PartDef namespace), so `calc_refs` stays non-empty after `base_rate` is
reclassified to a sibling. The spec's insistence on "ancestor **PartDef** QNs"
specifically (`spec.md:70-75`) — not "any non-owning namespace" — is exactly what keeps
D3 safe. No change needed; recording it as verified.

### Lens 3 — Pipeline Risk

**L3-1 · If-then tradeoff (SHOULD-FIX):** Success Criterion `spec.md:64-66` and Non-Goals
`spec.md:132-133` assert baselines stay byte-identical because "no corpus/fusion-tea
model hits this shape." That claim is **asserted, not verified**, and the corpus makes
it non-obvious: PartDef inheritance (`:>`) appears across ~30 fixture models including
`fusion_tea` itself — a baseline model (`scripts/capture_extraction_snapshots.py:110`).
Two things to separate:
- **The real guarantee is stronger than the spec's reason.** Baselines derive from
  *un-recaptured* snapshots. A code-only classifier change cannot move them, because
  their classifications are frozen in their committed snapshots. So byte-identity holds
  **as long as re-capture is scoped to `unresolvable_attr_probe` only** — which is
  exactly what `select_fixtures` allows. The spec should state *this* as the mechanism,
  not "no model hits the shape."
- **The assumption is still worth verifying**, because the moment anyone re-captures a
  baseline snapshot (an audit, a future item, an over-broad capture invocation), any
  fusion_tea/corpus computed attribute that references an inherited attr *would* flip
  and the baseline *would* change. The spec should verify — grep the corpus for computed
  attributes referencing inherited attributes, or re-capture-and-diff `fusion_tea` once —
  rather than assert. Per R4, a filed "no model hits it" is a static-read verdict until
  reproduced.
- **Corollary:** "baselines byte-identical" as a blanket claim is wrong for the one file
  that *must* change — `unresolvable_attr_probe/extraction_snapshot.json`. The spec
  should carve that out as the single intended, reviewed churn (ties to L1-2).

**L3-2 · Note (test-honesty trap — well-handled):** The spec caught both hazards
precisely: the `test_misclassification_documented` body only calls `pytest.xfail` when
`classification != correct_cls` and asserts nothing otherwise (`:786-792`), and its
parametrization filters `v[0] != v[1]` (`:757`), which yields **zero** cases once the
table is updated so `actual == correct` for the five rows. The `[HARD]` no-fake-test
requirement (`spec.md:86-101`) is an outcome constraint (five real, positively-asserting
cases), mechanism deferred — sufficient to force a real, non-empty test. One small
sharpening: the spec leans on R1's "independently-anchored expectation" elsewhere but
doesn't say it here. For a classification-equality test the expected value is a literal
(`FORMULA`), so it's independently anchored by construction — worth one sentence tying
the five cases to a literal expectation (and noting `correct_cls == FORMULA` as a
filter selects exactly L1/L2/D1/D2/D4 and excludes D3). Minor.

**L3-3 · Rewrite request (SHOULD-FIX):** The spec's test-coordination scope names only
the conformance file's table and its two consumer tests (`spec.md:103-108`). It does not
account for the **integration** e2e tests keyed off classification lists
(`tests/integration/test_computed_attributes_e2e.py:44-48`, `EXPOSE_COMPUTED_ATTRS` /
FORMULA lists, `test_backlog_accuracy`'s "0 functions to implement"). Those run on
`attr_expr_probe`, not `unresolvable_attr_probe`, so they likely don't move — **but the
spec should confirm that** rather than leave the e2e suite unmentioned. If `attr_expr_probe`
has no inherited-attr computed attribute, say so; if it does, those lists move too. Right
now the reader can't tell whether the e2e suite was considered.

### Lens 4 — Hygiene

None material. Line-ref accuracy is good (Step-2b `:112,123`, xfail `:787`, root cause
`:794`, table `:642`, consumers `:726`/`:764`, filter `:757` all check out; the doc note
the spec cites as `:114-116` is actually ~`:115-117`, not worth a change).

### Lens 5 — Reader Comprehension

**L5-1 · Note:** The spec reads well on one pass. The one comprehension risk is that the
Problem section states "loud (a rejection)" so confidently that a reader takes it as
verified fact and carries the error forward (that's L1-1's substance, not a separate
prose issue).

---

## Engagement Summary

**Overall take:** The work item is sound and the test-honesty trap was caught well, but
two load-bearing claims fail against the code. The "loud rejection" framing is false —
the pipeline silently drops EXPOSE_COMPUTED, and doc 16 (which the spec treats as the
outlier to fix) is the one that's right. And the fix can't flip the tests at all without
re-capturing a committed snapshot that bakes the classification — a step the spec never
mentions. Both are fixable with targeted edits.

**Here's what I need you to weigh in on:**

1. **[L1-1]** "Loud vs silent" is inverted. Code silently skips EXPOSE_COMPUTED
   (`graph_builder.py:269-288`; e2e `test_expose_computed_no_module_no_error`). Doc 16's
   "silent no-ops" is correct. Fix the spec's Problem wording, and re-aim the
   reconciliation requirement so the matrix `:136` "loud" phrase and the epic framing get
   corrected toward "silent" — with the code citation, not just "make them agree."

2. **[L1-2]** The fix is invisible to the suite without a snapshot re-capture. The
   conformance tests read `classification: "expose_computed"` baked into
   `unresolvable_attr_probe/extraction_snapshot.json`. Flipping the xfails requires
   re-capturing it via `scripts/capture_extraction_snapshots.py` (syside license, R3
   discipline, committed-JSON diff). This must be an explicit in-scope step.

3. **[L2-1]** Does SysIDE actually expose the supertype/ancestor chain off `part_element`
   at extraction time? The entire fix depends on it and the spec assumes it. Name it as
   the first design gate; point at existing inheritance-aware extraction (the `:>>`
   retype machinery behind REQ-LVP-09 / REQ-VBR-11) if it's reusable substrate.

4. **[L3-1]** Byte-identity is asserted, not verified, and the corpus (incl. fusion_tea,
   a baseline model) uses `:>` pervasively. Verify the claim, state the *real* guarantee
   (baselines derive from un-recaptured snapshots; re-capture is scoped to the target
   fixture only), and carve out the one file that *must* change.

5. **[L3-3]** Confirm the integration e2e tests
   (`test_computed_attributes_e2e.py:44-48`) don't move — or fold them into the
   test-coordination scope if they do.

---

## Resolutions

*Filled in during Stage 5, keyed by finding ID. Nothing resolved yet.*

---

**Verdict:** Revise
**Next Steps:** Record resolutions here, then re-run `/_my_spec` (or return to the
spec-agent session) and point it at this review to incorporate. The reviewer does not
edit the spec. The two must-fix items (L1-1 loud→silent inversion; L1-2 missing snapshot
re-capture scope) are the gating edits; L2-1/L3-1/L3-3 sharpen the design hand-off.
