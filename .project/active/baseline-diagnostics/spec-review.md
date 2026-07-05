# Spec Review: Baseline Repair & Silent-Failure Diagnostics

**Spec:** `.project/active/baseline-diagnostics/spec.md`
**Contract:** `claude-pack/commands/_my_spec.md`
**Review File:** `.project/active/baseline-diagnostics/spec-review.md`
**Date:** 2026-07-05

---

## Reality Check

**Sound.** The spec is about the right work item, and its code-facing claims check out against HEAD. I verified the four load-bearing ones directly:

- The red test is a byte-exact YAML baseline compare over four models (`test_gen_pipeline_yaml.py:541`); solar_battery's `entry_fusion` inputs are in non-alphabetical group order, matching the "ordering swap" story.
- **D2 is checked, not assumed.** `constraints.py` is imported by nothing in `src/` or `tests/`; `constraint_validator.py.jinja2` is referenced only by `constraints.py`; no `test_constraints.py` exists; `constraint_extractor.py` does import `reconstruct_expression` from the live `expression_utils.py`. The dead-code deletion is safe exactly as the spec states.
- The SC-2 crash is real: `teax_module.py.jinja2:118` indexes `output_attributes[0]` in the single-output branch, so zero outputs raise `IndexError`.
- The SC-1 stub (`extractor.py:106-107`) and both SC-7 warning sites exist.

The core requirements are directionally correct and design would not be misled. Three gaps below are worth resolving before this becomes the contract — none of them sink the item.

---

## Audit

### Lens 1 — Faithfulness

**L1-1 · Direct claim (positive):** D2's "cleanly unimported" claim is accurate, and the spec verified it rather than asserting it. Nothing to fix — recorded so the reviewer knows the deletion is safe. The one nuance: the spec says `constraint_extractor.py` "imports `expression_utils.reconstruct_expression` — a live module (SC-6's target)." Confirmed (`constraint_extractor.py:17`). The keep decision is sound.

**L1-2 · If-then tradeoff:** The epic's Item 1 success criterion reads "Generating the **WI-014 toy and IFE models** emits the new constraint / EXPOSE_PURE / zero-output diagnostics" (epic:113). This spec instead tests against `catf_mfe_model` (constraints), an unnamed shape-A EXPOSE fixture, and a new zero-output fixture — because WI-014 is imported later (Item 8) and the IFE models live outside the sandbox. That substitution is the *right* call, but the spec never says it is making it. Add one line reconciling the divergence, so a reader cross-checking the epic's Item 1 SC doesn't think a fixture was dropped. (This ties directly into L3-1, which is the substitution's real cost.)

### Lens 2 — Problem & Approach

**L2-1 · Question to the user:** D1 fixes the ordering at `generation/pipeline.py:66` (the emission boundary), but the non-deterministic order is *produced* at `graph_builder.py:364`, where `entry_point_groups=param_groups` is written into the ComputationGraph. R1 names ComputationGraph the sole input to generation and invokes "compute once, fix at the source." Sorting in the template leaves the ComputationGraph itself carrying a discovery-ordered list — any other consumer of `graph.entry_point_groups` (and Item 2's snapshot-driven rebuild, which reconstructs the graph) stays non-deterministic. Sorting `param_groups` in `graph_builder` before the `ComputationGraph(...)` construction makes the graph deterministic at the true source, which is what D1's own rationale claims to do ("made deterministic where it is produced"). Your commit message even says "sort at source." **Recommend sorting in `graph_builder`, not `generation/pipeline.py` — and reconcile D1's cited line (`pipeline.py:66`) with that.** Is there a reason the sort has to live in the generation layer?

### Lens 3 — Pipeline Risk

**L3-1 · Question to the user:** SC-7's real-fixture coverage looks unfunded. REQ-CA-30 rewords the two EXPOSE_PURE warnings and success criterion (spec:64) requires "Generating an EXPOSE_PURE-bearing model (**shape A / part-def**) emits the reworded message," locked by a no-mock conformance test (R1). But the only EXPOSE fixtures in the repo — `catf_mfe_model` and `attr_expr_probe` — are **shape B** (part-*usage*), which the research says drops *silently* (the alias registers fine, no warning fires). Shape A, the one that actually trips `_resolve_expose_pure`'s "key not found" warning, is described in the research as "the toy" = WI-014, which Item 8 imports later. So today there may be **no in-repo fixture that fires the warnings being reworded** — meaning REQ-CA-30 has nothing to test against. The spec lists a new zero-output fixture as a deliverable (spec:130) but no new shape-A EXPOSE fixture. **Either Item 1 needs a minimal shape-A fixture as an explicit deliverable, or REQ-CA-30's real-fixture test has to wait for Item 8.** Which one? (If a shape-A fixture already exists that I missed, name it in the spec.)

**L3-2 · Direct claim:** Two statements about baseline churn contradict each other. Success criterion spec:68 is hard: "No baseline changes beyond the re-captured solar_battery YAML." But the churn guard (spec:190-193) and Open Question (spec:158-161) say that *if* the sort reorders a currently-green baseline, design may "accept the reviewed re-capture (ordering is execution-irrelevant)." Those cannot both hold — a reviewed re-capture of another baseline *is* a change beyond solar_battery. Good news: I checked, and for the **narrow** fix (sort `entry_point_groups` only) it is moot — chain_spike and attr_expr_probe have a single group, sample_model has none, so the sort is a provable no-op for all three green baselines. The risk is scope drift: D1's text also says "**Any** collection whose order feeds YAML and depends on discovery order is sorted by a stable key," which, read broadly (modules, module inputs, exit points), *would* churn the other baselines. **Resolve by scoping the sort to `entry_point_groups` only and deleting the "accept re-capture" fallback** — so the hard SC is unambiguous and the design can't reach for the escape hatch.

**L3-3 · Rewrite request:** REQ-CA-30 says it rewords "the two existing warning sites." At the file level that's `graph_builder.py` + `output_registry_builder.py`, but `graph_builder._resolve_expose_pure` actually has *two* distinct warnings: "could not identify instance/output from refs" (~line 672, a malformed-refs condition) and "key not found in output registry" (~line 682, the actual name-drop). Only the name-drop warnings should get the "the alias name is dropped; the value flows via channel X" rewording — the malformed-refs one is a different failure. Ask the spec to name the specific warning strings (or conditions) being reworded so design doesn't reword all three indiscriminately.

**L3-4 · If-then tradeoff (low stakes):** The SC-2 fail-fast and Item 3 interact cleanly, and the spec handles it (Non-Goals spec:138-141: legal return-style models hard-error here, extract correctly in Item 3, and no fixture has that shape today so nothing regresses). No action — flagged only so the reviewer confirms the "loud interim error on legal SysML" tradeoff is acceptable. It is strictly better than the current Jinja crash.

### Lens 4 — Hygiene

**L4-1 · Rewrite request (trivial):** Header says `Complexity: MEDIUM`; the epic sizes Item 1 at 0.5–1 day and the spec body calls it "a 0.5–1 day hardening pass." Not worth a round-trip on its own — align the label if the spec is touched anyway.

### Lens 5 — Reader Comprehension

No material blocker. The Problem section leads with the point (one red test, three silent failures), the Decisions Recorded section states D1/D2 plainly with evidence, and the tags are honest. A tired engineer can skim it once and know the work item.

---

## Engagement Summary

**Overall take:** The item is correctly scoped and the spec's code claims survive verification — including D2's dead-code deletion, which was checked rather than assumed. Three things to resolve before design: SC-7 may have no real fixture to test against in this item, D1 should probably sort one layer earlier, and one hard success criterion contradicts the churn-guard fallback (though empirically the narrow fix is a clean no-op).

**Here's what I need you to weigh in on:**

1. **[L3-1]** SC-7's reworded EXPOSE_PURE warnings only fire on shape A (part-def), which appears absent from the repo until Item 8 imports WI-014. Does Item 1 add a minimal shape-A fixture (making it a deliverable), or does REQ-CA-30's no-mock test defer to Item 8? As written, the success criterion can't be met with existing fixtures.
2. **[L2-1]** D1 sorts at the generation template (`pipeline.py:66`), but the order is produced in `graph_builder.py:364` where the ComputationGraph is built. Sorting there instead makes the graph itself deterministic (better for R1 and Item 2's snapshot rebuild) and matches your "sort at source" commit message. Confirm the target site.
3. **[L3-2]** "No baseline changes beyond solar_battery" (hard SC) contradicts the churn-guard's "accept a reviewed re-capture of another baseline." I verified the narrow entry-group sort is a no-op for all three green baselines, so scope the sort to `entry_point_groups` only and drop the fallback — then the hard SC stands clean.
4. **[L3-3]** `graph_builder._resolve_expose_pure` has two warnings, not one; only the "key not found" name-drop should be reworded. Have the spec name the exact warnings so design doesn't touch the malformed-refs one.

---

## Resolutions

*Filled in during Stage 5 as you resolve each finding.*

- **[L3-1]** _(pending)_
- **[L2-1]** _(pending)_
- **[L3-2]** _(pending)_
- **[L3-3]** _(pending)_
- **[L1-2]** _(pending)_
- **[L4-1]** _(pending)_

---

**Verdict:** Revise
**Next Steps:** The work item is sound; the edits are targeted (SC-7 fixture funding, D1 sort site, the SC/churn-guard contradiction, SC-7 warning precision). Once resolutions are recorded here, re-run `/_my_spec` (or return to the spec-agent session) and point it at this review to incorporate. The reviewer does not edit the spec.
