# Spec Review: Part-Usage Type Indexing (SC-3)

**Spec:** `.project/active/type-indexing/spec.md`
**Contract:** `claude-pack/commands/_my_spec.md`
**Review File:** `.project/active/type-indexing/spec-review.md`
**Date:** 2026-07-05

---

## Reality Check

**Sound.** The spec is about the right work item, the Problem section is accurate against HEAD, and the core requirements are directionally correct. I verified the two bug sites (`usage_extractor.py:163` `next(iter(usage.types))`; `hierarchy_resolver.py:527-531` same pattern), the heritage-walk precedent (`extractor.py:316-326`), and the baseline-invariance claim (no existing fixture carries a retyping shape). The full lens audit follows.

The headline issues are two REQ-tag collisions with **already-shipped** requirements (not just the flagged Item-3 conflict), and an under-specified collision policy that as written contains one unimplementable requirement.

---

## Audit

### Lens 1 — Faithfulness

**L1-1 · Direct claim:** The spec proposes `REQ-LVP-07`, but that tag **already exists and is shipped** — `docs/architecture/reference/18-literal-value-propagation.md:51` and `verification-matrix.md:274`: "Literal default found SHALL keep module FULLY_COMPILABLE; no default SHALL set MANUAL_REQUIRED." This is a harder collision than the one the orchestrator flagged: it clashes with a live requirement in the matrix, not an in-flight sibling. `REQ-LVP-01`–`07` are all taken; the next free tag is **`REQ-LVP-08`**. (Note: the spec's own body text at line 91 cross-references "REQ-LVP-06" as the map's consumer — see L1-3, that reference is also imprecise.)

**L1-2 · Direct claim:** The proposed `REQ-EXT-10` and `REQ-EXT-11` collide with Item 3, whose committed design (`return-style-extraction/design.md:158-161`, D5) claims `REQ-EXT-10/11/12`, and Item 3 lands first. `REQ-EXT-01`–`12` are all taken at HEAD; the next free tags are **`REQ-EXT-13`+**. Renumber both proposed EXT tags.

**L1-3 · Direct claim:** The `usage_type_map` requirement (spec 87-91) says the map "feeds literal-value propagation (REQ-LVP-06)." REQ-LVP-06 is only the *threading* requirement (data plumbed from `HierarchyExtractionResult` to `_build_aggregation_module`). The consumer whose **behavior actually changes** under this fix is the type-aware branch of `_find_literal_redefinition` (`graph_builder.py:1042-1043`, governed by REQ-LVP-01 Strategy 1 — "type-aware match via `target_partdef_qn`"). That is the one place a retyped usage's declared-type-vs-first-type difference changes an output. The spec should name that consumer and confirm no other reader of `usage_type_map` relied on the old first-type value. I traced the consumers: the only behavioral one is `graph_builder.py` (`_find_literal_redefinition` via `_build_aggregation_module`); the rest are serialization/threading. So the scope is genuinely small — but the spec asserts "a single declared type per usage is correct here" without having checked, and it should show the check.

### Lens 2 — Problem & Approach

**L2-1 · Question to the user — the headline:** The collision policy has a gap that the "same virtual QN" framing hides. Walk the mechanism:

- A retyped usage indexed under both `IFE Driver` and `HIF Driver` gets its instantiation path found by *both* the IFE-owned template expansion and the HIF-owned template expansion.
- Each virtual instance's QN is `{path}__{calc_instance_name}` (`usage_extractor.py:246-247`). Two templates collide on the **same** virtual QN only when the subtype's calc has the **same instance name** as the supertype's — i.e., a genuine override/redefinition.
- If the subtype's template calc has a **different** name (but was semantically meant to *replace* the supertype's), the two produce **different** virtual QNs, both instantiate, and the "same virtual QN" collision guard **never fires**. That is the silent double-count.

So the [NEED] at spec 97-100 ("differently-named → both instantiate; if that risks double-counting, warn the modeler") is, as written, not implementable: there is no signal that distinguishes "two legitimately distinct calcs" from "the subtype's differently-named calc was meant to replace the supertype's." Warning on *every* supertype+subtype differently-named pair would be pure noise. **The honest options are:** (a) both instantiate, full stop, and drop the differently-named warning ambition; or (b) define the *exact*, detectable trigger for the warning. Which do you want? My read: (a) is correct — if the modeler wrote two differently-named calcs, generating both is faithful; the dangerous case is same-name, which the same-QN guard already covers.

**L2-2 · If-then tradeoff:** The spec elevates "preserve accidental supertype-template flow on retyped usages" to a [HARD] success criterion (spec 54-56), while the Non-Goals (spec 117-122) explicitly *decline* to make supertype templates reach a **plain** `part x : Subtype` usage. Net effect: two ways of writing the same intent behave differently — `part :>> x : Sub` pulls supertype templates (kept as an accident), `part x : Sub` does not (needs the deferred supertype-chain walk). This is defensible **if** the goal is strictly "don't regress what retyped usages get today, on a 1-day budget." It is a problem **if** it entrenches an inconsistency the MFE-epic supertype-walk will later have to unwind — at which point "preserve the accident" may need to be *undone*, not extended. Is locking the accident as a [HARD] guarantee the right call, or should preservation be a [NEED] ("don't regress") rather than a contract the later walk must honor?

**L2-3 · Direct claim (tension between two success criteria):** SC bullet 2 (spec 54-56) guarantees the retyped usage "still instantiates any supertype-owned template calcs it instantiated before." SC bullet 5 (spec 62-64) and the [NEED] at 102-104 introduce a most-specific-owner tiebreak where "the subtype wins" for a colliding QN — which **drops** the supertype's template for that QN. For the same-QN collision case these two criteria point in opposite directions, and the spec never states that the tiebreak is a deliberate *exception* to the preservation guarantee. A reader can reasonably read bullet 2 as absolute. Make the precedence explicit: preservation holds *except* where a same-QN collision triggers the tiebreak.

### Lens 3 — Pipeline Risk

**L3-1 · Question to the user / verify-at-design:** "Owned FeatureTyping target" is treated as singular and unambiguous ([HARD], spec 74-78), but the anointed precedent `_get_calc_def_name` (`extractor.py:316-326`) returns the **first** FeatureTyping it encounters while iterating `elem.heritage` — itself a position-based pick, which is ironic given the bug being fixed *is* position-based selection. Two things design must pin: (a) behavior when a usage has **multiple** owned FeatureTypings (SysML permits it) — first-in-heritage, or is that another latent bug? (b) confirm `heritage` yields **owned** typings only, not typings inherited from the supertype chain — if heritage climbs the chain, a plain `part x : Sub` could resolve through `Sub`'s own FeatureTyping to its supertype and quietly contradict the Non-Goal. The spec asserts "owned FeatureTyping target" as if settled; it needs one probe to confirm both.

**L3-2 · Rewrite request:** The spec defers fixture *design* (fine) but under-pins the fixture *shapes*. Success criteria pin the happy path (retyped → subtype template) and the same-QN collision, but leave two contested shapes unpinned — exactly the ones L2-1/L2-2 turn on. Ask the spec to pin the required fixture matrix so design cannot quietly skip them: (a) retyped usage, subtype-owned template only; (b) same-named template on both supertype and subtype → same-QN collision (tiebreak/warn); (c) **differently-named** templates on both → both instantiate, as the *tested, intended* outcome (locks L2-1's resolution); (d) plain `part x : Subtype` as the **out-of-scope negative** — supertype template must NOT reach it, locking the Non-Goal against future drift; (e) baseline-invariance across the existing 4. Pinning shapes ≠ pinning SysML text; the exact model stays a design/plan call.

**L3-3 · Direct claim:** The byte-identical baseline requirement (spec 59-61, 93-95) states the *what* but not the *how* of proof. "All-types indexing adds no consequential keys" is a reasoning claim, not evidence — and the fix changes the index key set for every model. The success criterion should require a **runtime re-run** of the 4 pipeline baselines through generation with a zero-diff result as the evidence, not inspection. (I confirmed no existing fixture carries a retyping shape via static grep, so the claim is very likely true — but "likely true by reasoning" is exactly what let SC-3 survive 1,500 tests.)

### Lens 4 — Hygiene

*(None material. The research report cites the precedent at `extractor.py:251-259` while the spec cites `316-326`; the spec is correct at HEAD, so this is a non-issue — noting only so it isn't re-flagged.)*

### Lens 5 — Reader Comprehension

**L5-1 · Rewrite request:** The collision policy is scattered across four locations with subtly different framings — SC bullet 5 (same-QN), the two [NEED]s (differently-named vs same-QN), and two Open Questions. A reader cannot assemble the actual policy in one pass, which is part of why the L2-1 gap is easy to miss. Consolidate the collision handling into one place that states, in order: what counts as a collision, what the deterministic outcome is, and what (if anything) warns. This is the same edit L2-1 and L2-3 will drive.

---

## Engagement Summary

**Overall take:** The work item is sound and the Problem section is accurate — this is a **Revise**, not a rework. But two of the proposed REQ tags collide with *already-shipped* requirements (not just the flagged Item-3 conflict), and the collision policy as written contains one requirement that cannot be implemented as stated. Those need decisions before design.

**Here's what I need you to weigh in on:**

1. **[L2-1]** The collision policy's "same virtual QN" guard only catches *same-named* templates on both types. Differently-named templates on both types both instantiate silently, and the [NEED] to "warn if that double-counts" is not implementable — there's no signal for "meant to replace." Decide: both-instantiate-full-stop (my recommendation), or define an exact warning trigger.
2. **[L1-1, L1-2]** Renumber the REQ tags. `REQ-LVP-07` **already exists shipped** → use `REQ-LVP-08`. `REQ-EXT-10/11` collide with Item 3 → use `REQ-EXT-13`+.
3. **[L2-2]** Should "preserve the accidental supertype-template flow on retyped usages" be a [HARD] contract, or a [NEED] ("don't regress")? As [HARD] it entrenches an inconsistency (retyped gets it, plain subtype doesn't) that the later MFE supertype-walk may have to undo.
4. **[L3-1]** "Owned FeatureTyping target" is treated as singular, but the precedent picks first-in-heritage. Design must confirm the multi-FeatureTyping behavior and that `heritage` is owned-only (not inherited) — else the Non-Goal leaks.
5. **[L3-2, L2-3]** Pin the required fixture shapes (esp. differently-named-both and the plain-subtype negative) and state the tiebreak as an explicit exception to the preservation guarantee.
6. **[L1-3]** Name the real `usage_type_map` consumer (`_find_literal_redefinition`, REQ-LVP-01) and confirm no other consumer relied on first-type — the check is small (one site) but the spec asserts it without showing it.

---

## Resolutions

Resolved 2026-07-05 (user rulings applied to spec.md):

- **L1-1 / L1-2 (REQ renumber):** `REQ-LVP-07`→**`REQ-LVP-08`**; `REQ-EXT-10/11`→**`REQ-EXT-13/14`**.
  Applied in spec's "Proposed REQ tags" section.
- **L1-3 (name real consumer):** Spec now names `_find_literal_redefinition` (graph_builder,
  REQ-LVP-01 Strategy 1) as the one behavioral consumer of `usage_type_map`, and requires design
  to confirm no other consumer relied on first-type. Fixed the imprecise REQ-LVP-06 cross-ref.
- **L2-1 (differently-named):** Ruling (a) — **both instantiate, full stop; warning dropped.**
  Rationale recorded (replacement uses same name → same-QN case). Locked by fixture shape 4.
- **L2-2 (preserve supertype flow):** Stays **[HARD]** — epic's stated mechanism and baseline
  invariance both depend on it.
- **L2-3 (tiebreak vs preservation):** Same-QN collision → **most-specific-owner tiebreak PLUS a
  warning** naming both candidates and the winner, stated as the single explicit exception to the
  preservation contract.
- **L3-1 (multi-FeatureTyping / owned-vs-inherited):** Requirement is "declared type = owned
  FeatureTyping target"; index handles multiple owned typings, `usage_type_map` picks most-specific
  (deterministic-first + warning if incomparable). Node-shape details marked as a design-time probe.
- **L3-2 / L5-1 (fixture matrix + consolidation):** Added a pinned Fixture Matrix (6 shapes incl.
  differently-named-both and the plain-subtype negative) and consolidated the whole collision policy
  into one "Collision & Multi-Type Policy" subsection.
- **L3-3 (baseline proof):** Baseline byte-identical SC now requires an actual runtime re-run
  (zero-diff), not inspection.

---

**Verdict:** **Revise** — the work item is sound; the spec needs the REQ renumbering, an implementable collision policy, and a few pinned decisions before it becomes the design contract.

**Next Steps:** Once resolutions are recorded here, re-run `/_my_spec` (or return to the spec-agent session) and point it at this review to incorporate. The reviewer does not edit the spec directly.
