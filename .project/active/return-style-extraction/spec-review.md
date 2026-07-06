# Spec Review: Return-Style & Bare-Parameter Extraction (SC-2)

**Spec:** `.project/active/return-style-extraction/spec.md`
**Contract:** `claude-pack/commands/_my_spec.md`
**Review File:** `.project/active/return-style-extraction/spec-review.md`
**Date:** 2026-07-05

---

## Reality Check

**Sound.** This spec is unusually well-grounded. Every code-facing claim I checked against HEAD is true: the two filter sites (`extractor.py:204`, `:242`), the AST-capture block (`:223-228`), `_get_direction`'s `"Return"` handling (`:296-306`), and the Item-1 V7 guard (`:271-278`) are all where the spec says they are. The syside node-shape table matches the research report's probe table. The no-double-ingestion mechanism holds up under inspection. The baseline-invariance claim is supported — no committed fixture calc def uses a direction-carrying ReferenceUsage member. The work item is the right size and pointed at the right problem.

The findings below are refinements and reviewer decisions, not corrections. The strongest is a concrete docs/code lockstep miss (L1-1). The rest are honesty-of-deferral and design-clarity items. Recommend **Revise** — small, targeted.

---

## Audit

### Lens 1 — Faithfulness

**L1-1 · Direct claim:** The relaxation makes the *existing* V7 message false, and the spec doesn't call for fixing it. V7 today reads (both at `extractor.py:272-278` and `modeling-assumptions.md:350`): *"Likely cause: return-style ('return y : Real = expr') or bare 'in' parameters, which are not yet extracted (Item 3)…"*. Once Item 3 lands, those forms **are** extracted, so any remaining zero-output case is no longer caused by them — the message now names a fixed bug as the likely cause and points the modeler at Item 3 for something Item 3 already did. The spec reconciles `01-extraction.md` but never mentions revising the V7 wording in code and in the Validation Rules table. This is exactly the R1 "requirement IDs + docs move with code" obligation. Add it to scope: after relaxation, V7 should point at the real remaining causes (genuinely empty calc def; anonymous return, which V8 now catches earlier).

**L1-2 · Direct claim (confirming, not faulting):** The node-shape table (spec lines 20-26) is faithful to the research report (report lines 104-109), including the subtle `return attribute y` + body form decomposing into `AttributeUsage(Out) + direction-None ReferenceUsage`. The doc-contradiction claim also checks out: `01-extraction.md:27-32` really does teach `in capacity : Real; … return total_cost : Real = capacity * unit_cost;` — both the bare-`in` and return forms the extractor currently drops. No action; recording that the faithfulness spine is solid.

### Lens 2 — Problem & Approach

**L2-1 · If-then tradeoff:** The decision to defer body-assignment expression capture rests on an unverified premise, and the fact that would confirm it is itself deferred. Non-Goal rationale point 4 (spec line 148) asserts "The six IFE calc defs use inline return form, so they auto-implement without it." That is the load-bearing justification for the deferral — *if* the IFE defs are inline-return, deferring capture costs nothing; *if* any are body-assignment form, deferring means they extract an output but regress to a `NotImplementedError` stencil, which is the epic's "work in original return form" criterion degraded. But the only way to check is the IFE verification procedure (Open Questions), which "design should decide whether [it] is a live-run gate on Item 3 close or a recorded procedure executed opportunistically." So the deferral could be ratified now and its premise checked *after* Item 3 closes. **Decide the sequencing explicitly:** either the IFE-form check gates Item 3 close (so the deferral is only final once the inline-form premise is confirmed), or the spec should state plainly that the deferral is provisional and names the follow-up trigger if the premise turns out false.

**L2-2 · Question to the user:** Is the epic's phrase "the six converted IFE calc defs **work** in original return form" (epic line 174) satisfied by *extraction* alone, or does it demand *auto-implementation*? The spec threads this carefully — success criterion (spec lines 76-77) says "extract," and the verification procedure (spec line 168) adds a "non-empty `output_expression_asts` for the inline-return ones" check — so it covers both. But the epic's own wording is ambiguous and this is the criterion the whole item is judged against. Confirm the reading: "work" = extracts correctly *and* auto-implements (no stencil) for the inline-return defs. If so, the spec is honest and complete; just make the equivalence explicit so the audit at close can't be gamed by "it extracts, ship it."

### Lens 3 — Pipeline Risk

**L3-1 · Rewrite request:** The anonymous-return diagnostic (V8) must inspect *raw members*, not the attribute lists — and the spec leaves this implicit in a way that could mislead design. Here's the mechanism: `_extract_attribute` returns `None` for a nameless member (`extractor.py:407-409`), so an anonymous `return : Real = expr` never lands in `output_attributes`. It is therefore **invisible** to any check that reads the attribute lists — the calc def just looks zero-output and hits V7. For V8 to fire *before* V7 (the HARD requirement at spec lines 98-101), the detection has to scan `elem.owned_members` for a direction-Out/Return member whose name is empty after `sanitize_name`. The spec's Open Question hints at this ("on first sight of a nameless direction-Out member") but the HARD requirement is phrased as if the nameless member is observable in the pipeline. Ask design to state the constraint plainly: the V8 check operates on raw members because the nameless one leaves no trace in `output_attributes`.

**L3-2 · Question to the user:** Item 2 (concurrent) adds `snapshot_format_version` and promotes the serializer from `tests/helpers/` to `src/sysml_codegen/snapshot/`; the capture script imports `tests.helpers.snapshot_serializer` today. The spec's fixture-capture requirement (spec lines 122-128) correctly delegates format to `scripts/capture_extraction_snapshots.py` rather than pinning a version — so it won't freeze a stale format. Good. But it never acknowledges the sequencing: if Item 2 lands first, the new fixture's snapshot must be captured *after* rebasing on Item 2 (new format + possibly a changed serializer import path), or the snapshot will be in the old format and Item 2's version-mismatch hard-error will reject it. **Add a one-line ordering note:** capture the new fixture's snapshot against whichever of {old, Item-2 versioned} format is current at implementation time, and if Item 2 has landed, capture through the promoted `snapshot/` package. Cheap insurance against a format-mismatch surprise at Item 3 close.

**L3-3 · If-then tradeoff:** Baseline-invariance is asserted from a runtime fact, and the byte-identical re-run is the only real proof. "No committed fixture uses a direction-carrying ReferenceUsage member" (spec line 107) is correct as far as source text shows — I grepped every fixture calc def and found no `return`-style or bare-`in` declarations. But whether a member is a ReferenceUsage vs AttributeUsage is a syside *representation* fact, not always visible in the `.sysml` source, so the source grep is necessary-but-not-sufficient. The spec already has the actual guard: the "byte-identical after the change" success criterion (spec lines 69-71). That's the proof. Recommend making the dependency explicit — the source-level claim is the hypothesis; the byte-identical capture run is what confirms it — so the implementer treats a baseline diff as a real signal to investigate, not noise to re-baseline away.

### Lens 4 — Hygiene

**L4-1 · (none material.)** The spec is well-structured and the tags are honest — `[HARD]` items are genuinely forced by syside's node model and the no-double-ingestion criterion; the `[NEED]` auto-impl item is correctly a stakeholder outcome, not a mechanism; `[INFERRED]` items are genuinely inferable. Nothing here rises to a finding.

### Lens 5 — Reader Comprehension

**L5-1 · (none material.)** The Problem section's node-shape table is the right tool for a subtle distinction and reads cleanly on one pass. The deferral rationale is numbered and skimmable. A tired engineer can read this once and know the four forms, the one rejected form, and what's deferred. No comprehension-blocking finding.

---

## Engagement Summary

**Overall take:** This is a strong, well-verified spec — every code pointer, the node-shape table, the double-ingestion mechanism, and the baseline-safety claim hold up against HEAD. It's a Revise, not a Rework: the fixes are one concrete docs/code lockstep miss and a handful of "make the implicit explicit" tightenings. I'd trust the design phase on this once the items below are recorded.

**Here's what I need you to weigh in on:**

1. **[L1-1]** The V7 message (code `extractor.py:272-278` + `modeling-assumptions.md:350`) says return-style/bare-in are "not yet extracted (Item 3)" — false once Item 3 lands. Add "revise V7 wording" to scope so docs and code stay in lockstep (R1).
2. **[L2-1]** The body-assignment-capture deferral is justified by "the six IFE defs are inline-return" — an unverified premise whose check is itself deferred. Decide: does the IFE-form verification gate Item 3 close, or is the deferral explicitly provisional with a named follow-up trigger?
3. **[L2-2]** Confirm the reading of the epic's "work in original return form" = extracts *and* auto-implements (no stencil) for inline-return defs, so the close-out audit can't pass on extraction alone.
4. **[L3-1]** Make explicit that the V8 anonymous-return check must scan raw members — the nameless member is invisible in `output_attributes` (because `_extract_attribute` returns `None` for it), so it can't be detected from the attribute lists.
5. **[L3-2]** Add an ordering note for the new fixture's snapshot vs Item 2's format-versioning, so it isn't captured in a format Item 2's mismatch-guard will reject.

---

## Resolutions

*Filled in during Stage 5, keyed by finding ID.*

---

**Verdict:** Revise
**Next Steps:** Once resolutions are recorded, re-run `/_my_spec` (or return to the spec-agent session) and point it at this review to incorporate. The reviewer does not edit the spec.
