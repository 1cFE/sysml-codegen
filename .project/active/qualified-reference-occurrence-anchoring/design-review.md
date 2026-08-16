# Design Review: Exact Owner Anchoring for Usage-Owned One-Segment References

**Design:** `.project/active/qualified-reference-occurrence-anchoring/design.md`
**Spec:** `.project/active/qualified-reference-occurrence-anchoring/spec.md` (rev 2)
**Review File:** `.project/active/qualified-reference-occurrence-anchoring/design-review.md`
**Date:** 2026-08-15

Verification basis: every load-bearing code claim in the design was checked against the live tree
(independent line-by-line pass over `elaborate.py`, `occurrence.py`, `graph.py`,
`instance_graph.py`, the agentic-mbse evidence types, and the five named test surfaces), plus a
fresh product-lens run (ledger block appended to `product-lens.md`, gate **DISPOSED**, no BLOCK).

---

## The Point

The product is a design search: engineering parameters can be freely varied and viability and
outcomes (like LCOE) assessed, without embedding the engineering logic (`[OWNER-VERBATIM]`,
P-001). That search is only trustworthy if one semantic source occurrence becomes exactly one
runtime source reaching every and only its bound consumers, and unsupported forms fail loudly
before generation (epic mission, owner grade). This item repairs a live violation: SysIDE has
already resolved a one-segment leaf to a declaration owned by a concrete `PartUsage`, and the
elaborator throws the owner away and searches for the leaf slot from the consumer's position — so
`comp_a::length` authored inside `comp_b` can silently wire `comp_b.length`, and a mutation of the
named source moves without moving its supposed consumer.

## Fundamental Assessment

**Sound, with one fired smell escalated and disposed here, and one premise the design itself
holds open.**

This is the right piece of work. The product lens re-derived the point independently from P-001
and the epic and found no owner/`[HARD]` contradiction; the design's "The Point" quotes the owner
sources faithfully rather than inheriting the spec's framing, and the point's falsifier is wired
into the design as invariant 15 and the public-mutation validation row.

This is also the right approach. The defect is one branch — the one-segment shortcut in the shared
resolver discards the owner that every caller already delivers — and the design fixes exactly that
branch, at the last seam all six behavior lanes share, by composing three authorities that already
exist (live leaf → live owner metatype; the existing occurrence contextualizer; the existing
slot-to-target lookup). No new index, graph object, schema, or diagnostic code. Verification
confirmed the load-bearing claims: `_resolve_semantic_reference` short-circuits one-segment
references to `_resolve_leaf` with the owner discarded and `plural` not forwarded
(`elaborate.py:2069-2076`); exactly four call sites feed it, with no caller the design missed;
`_contextualize_root`/`_select_occurrences` implement the package/lineage/descendant/ambiguity
rules at the cited lines; `occurrences_for_declaration` bridges redefinition families exactly as
described. A simpler design does not exist — patching any single caller leaves the identity defect
live in the others, which is the design's own D1 rejection.

**Escalation 1 — smell 2 fired (consumer compensates for a producer guarantee), design-F2.** The
extraction fact already carries `owner_element_id` and `owner_is_definition` for the express
purpose of letting downstream distinguish definition-level from occurrence-level referents. D2
correctly finds that flag too coarse (packages and other owners also satisfy `false`), but instead
of renegotiating the producer contract the design freezes it and compensates with a live metatype
lookup — leaving frozen evidence and live lookup as two representations of one fact kept in
agreement by test discipline (the design's own risk row admits they can disagree). Tempering
assessment after code verification: the branch **decision** uses one authority only — the fact
supplies the leaf ID; owner and metatype come from the live index (`_stable_elements`,
`elaborate.py:636-653`, and `SysideAdapter.is_instance`) — so this is not a dual-authority
decision, and the live model is the same authority the whole elaborator already trusts. The smell
is real but bounded, and it needs a recorded disposition, not a redesign (see Major issue 2).

**Escalation 2 — the design's own open premise, B3/D10.** The approved spec's SC8 requires a
discriminating **authored bare** regression; the design reports a targeted probe falsified the one
proposed topology and correctly refuses to start implementation until the owner picks a route.
This deferral honors the point — it defers the evidence, not the behavior, and it is
capture-fidelity law 4 (surface, never silently resolve) done properly. But the falsifying probe
left **no artifact anywhere** — I checked the item folder, the spike dirs, and the gitignored
`out/` trees for anything written after 15:00 on 2026-08-15. The evidence for falsifying an
approved success criterion currently exists only as prose inside the design (Major issue 1).

The foundation is sound; proceed to the detailed review. Verdict at the end: **Revise** — targeted
amendments, no structural rework.

---

## Dimensional Review

### 1. Spec Compliance
**Assessment:** Concerns

Every success criterion maps to a design element: SC1 → the Architecture flow and D1–D3; SC2–5
(u4–u7) → D6 and the validation table's exact expected edges; SC6 controls → D6/validation; SC7
(alias, computed, constraint binding, predicate — sole evidence for alias and predicate) → D7's
combined cross-consumer fixture; SC9 corpus re-derivation → the task-local verifier with
adjudication (invariant 14); SC10 public mutation → invariant 15 and the mutation row; SC11
strict/lenient → invariant 12; SC12 occurrence/wire stability → invariant 5; SC13 snapshot
classification → D9; SC14 documentation tail → Integration step 8.

The two concerns:

- **SC8 is deferred, not designed.** The deferral is honest and properly gated (D10, Next-Stage
  Handoff), and challenging an `[INFERRED]` spec premise on new evidence is exactly what the
  provenance grades are for. But the design cannot fully satisfy the approved spec as written
  until the owner rules, and the falsification evidence is unrecorded (Major issue 1).
- Provenance is otherwise carried faithfully: the owner's broad invariant stays the fixed
  constraint (B1/D2), the `[INFERRED]` rows are treated as challengeable, and no owner referent
  was dropped or hardened. The spec's open questions (seam location, fixture organization,
  constraint fixture split, plural policy) are each answered by a named decision (D1, D6/D7, D7,
  D4).

### 2. Pattern Consistency
**Assessment:** Pass

The design reuses the codebase's own machinery at every step, and the citations check out:
`_contextualize_root`/`_select_occurrences` for owner selection (`elaborate.py:2119-2219`,
verified exact), `occurrences_for_declaration` for the redefinition-family bridge
(`occurrence.py:223-231`, verified), the existing `SI_OCCURRENCE_MISSING`/`SI_OCCURRENCE_AMBIGUOUS`
codes (declared `diagnostics.py:12-13`, raised throughout the existing selection path), and the
established strict/lenient and fixture/conformance test patterns. `SysideAdapter.is_instance(x,
"PartUsage")` is already the idiom at this exact boundary (`elaborate.py:2126`). The new branch
falls under the import-boundary AST guard automatically since `elaborate.py` is a guarded file.

### 3. Abstraction Quality
**Assessment:** Pass

The core concept is right-sized: occurrence anchoring as a transient resolution step, not a new
graph object. One branch in one function; caller-owned alias following, port creation, override
application, and diagnostic translation all stay put (D5), which verification confirms matches how
the four callers actually behave today. Nothing here would make a new reader's model of
elaboration more complicated — the branch table in "Branch behavior" is the whole mental model.

### 4. Duplication Avoidance
**Assessment:** Pass

D3 explicitly rejects a new exact-owner index and a raw `effective_usage_id` filter because both
would compete with the slot-family authority — the right call, and the verified code confirms the
existing selectors already own those semantics. No parallel structures introduced.

### 5. Data Structure Clarity
**Assessment:** Pass

No schema, edge type, or serialized shape changes. The owner anchor is explicitly not inserted
into `ResolvedSemanticReference.segment_ids`, stored, or serialized. The one nuance — frozen owner
evidence vs live lookup — is handled under design-F2 (Major issue 2), not a structural problem.

### 6. Route Safety
**Assessment:** Pass

Invariant 10 (never fall back to positional search after a missing/ambiguous exact owner) is the
load-bearing safety property and it is stated, tested (validation rows), and consistent with the
epic's fail-loud mission. Failures use the existing named diagnostics; no new codes, no catch-all,
no candidate-order authority. Strict/lenient parity is inherited and cited.

One accuracy correction the plan should carry: strict mode has a **second halt** the design's
failure-behavior section doesn't mention — `_finish_readiness` (`elaborate.py:2604-2613`) raises
on readiness findings **before** `validate()` runs, so "strict reaches the same resolution and
validation work, then rejects" is not exactly true for graphs with readiness findings (Minor
issue 3).

### 7. Bets & Decisions Integrity
**Assessment:** Concerns

- **B1** is a genuine bet with a stated failure mode, and it is the owner's selected invariant.
- **B2** is genuine and well-evidenced — the spike findings cited (`findings.md:3-20`) say exactly
  what the design says they say (verified).
- **B3** is the design's best work: it surfaces that an approved success criterion rests on an
  unestablished premise, reports the falsifying probe, and refuses to treat fixture authoring as
  routine. The integrity gap is that the probe is unreproducible — no model text, no log, no dated
  note (Major issue 1). An owner asked to choose between D10's routes deserves a checkable record.
- **Hidden-bet hunt:** the implicit bet that `_select_occurrences`' consumer-relative rules land
  correctly when the contextualized root is an owner *derived from the leaf* rather than one the
  author named — e.g. contextualizing `comp_a` from inside `comp_b` (u6) — is real but covered:
  the u7 dot-path controls pin exactly this landing, and the validation table asserts u6's edge
  moves with no fallback. A second implicit bet — that every resolved leaf is present in the live
  `_stable_elements` index so its owner can be inspected — holds for the corpus (the index covers
  every `Feature` with a qualified name) and fails closed through the existing
  `IdentityBoundaryError` path if not.
- **D1–D9** each name the rejected alternative and the reason; none is a mechanism choice dressed
  as a bet. D10 is correctly presented as an owner decision with a recommendation, not a decision.
- The Implementation Notes' description of the measurement harness was verified against the actual
  gitignored harness (`spike/out/bare_expression_side_scan.py`): it does patch
  `_ExactElaborator._expression_references` (the monkeypatch-as-oracle), does forward the caller's
  `plural` flag into the simulated route, and has no deep-override accounting — all three stated
  corrections are real. (An earlier pass flagged this harness as nonexistent; it is gitignored,
  which is what "ignored" means in the design. The design should say where it lives.)

### 8. Reader Comprehension
**Assessment:** Pass

The Core Concept states the mechanism in five plain sentences before any detail. The lane table
ties call sites to behaviors, the branch table is the semantics at a glance, and The Point carries
the product obligation legibly rather than by pointer. Two citation defects (Minor issues 2 and 4)
are accuracy nits, not comprehension blockers.

---

## Issues by Severity

### Critical
- None. (The B3/D10 gate blocks implementation, but the design itself imposes that gate; it is an
  open owner decision, not a design defect.)

### Major
1. **B3 falsification evidence is unrecorded** — the 2026-08-15 probe that falsified the proposed
   bare-discriminator topology left no artifact (verified: nothing in the item folder, spike dirs,
   or gitignored `out/` trees after 15:00). The D10 decision and the challenge to spec SC8 rest on
   prose alone. — Bets & Decisions / Spec Compliance.
2. **Smell 2 / design-F2: frozen owner evidence vs live metatype lookup** — the design freezes the
   producer schema whose `owner_is_definition` flag it finds too coarse and compensates with a
   live lookup; the two representations are kept in agreement only by the pinned extraction test.
   Needs a recorded disposition: accept the split with the pinning test named as the standing
   guard, or file extending `ResolvedTargetFact` with owner metatype as the follow-up that retires
   it. — Pattern Consistency / Data Structure Clarity (product-lens design-F2).
3. **design-F1: the deep-override "census" option records absence-of-evidence as acceptance
   evidence** — a census proves no affected shape was *found*, not that none is *authorable*; the
   same epistemic distinction the design insists on for D10. Reword the census outcome as a
   declared, dated, close-visible coverage gap, not an alternative form of proof. — Route Safety /
   Validation (product-lens design-F1).

### Minor
1. **design-F3: D10 route 2 needs a standing gap record** — if the owner amends SC8 to pair an
   authored conformance fixture with a constructed-fact discriminator, the amended criterion must
   carry a visible "authored bare discrimination unproven" record to close, or a later reader sees
   SC8 as fully evidenced. (product-lens design-F3)
2. **Wrong citation for slot lookup** — `elaborate.py:2278-2297` is `_transition`; the
   occurrence-fixed → `NodeRef`/`ProducerRef` lookup is `_target_at`/`_target_for_slot` at
   `elaborate.py:2350-2366` (that half of the citation is right).
3. **Strict mode's second halt** — `_finish_readiness` raises on readiness findings before
   `validate()` (`elaborate.py:2604-2613`); the Failure Behavior section and the strict/lenient
   validation row should not promise "rejects only after the same validation work" unqualified.
4. **D6 names no source path for u1–u7** — they live at
   `.project/active/self-binding-replacement/spike/fixtures/` (not the occurrence-authority spike
   folder a reader might guess), and they are **untracked throwaways** per that spike's own
   findings. "Historical spike inputs remain dated evidence" overstates what untracked files can
   promise; the copy into `tests/fixtures/` is what makes them durable, so the plan should do it
   first and the design should cite the source path.
5. **Name the harness location** — the corpus-verifier seed is
   `.project/active/self-binding-replacement/spike/out/bare_expression_side_scan.py` (gitignored);
   the design's three stated corrections to it are all verified real, but "existing ignored
   measurement harness" with no path sent one verification pass to the wrong conclusion and will
   do the same to the plan agent.

---

## Recommendations

1. **Record the B3 probe before the D10 decision** — a short dated artifact (model text, exact
   SysIDE result, the failed parent-scope variant) in the item folder or `.project/research/`, so
   the owner's route choice and the SC8 challenge rest on checkable evidence. Cheap, and it is the
   review's only gate-adjacent ask.
2. **Dispose design-F2 in the design** — one paragraph: why the split-source cost is accepted
   (live model is the elaborator's single authority; frozen fields are corroboration), which test
   is the standing guard, and whether a producer-schema follow-up is filed or declined.
3. **Reword the deep-override census option (design-F1) and route-2 outcome (design-F3)** as
   declared coverage gaps in the D10 register — named, dated, visible at close — not as
   alternative proof.
4. **Fix the four accuracy nits** (Minor 2–5): the `_transition` citation, the second strict halt,
   the u1–u7 source path and untracked caveat, the harness path.

---

## Resolutions

| Finding | Disposition |
|---|---|
| Major 1 / SC8 probe record | **Accepted.** Retained the two probe models, reporting script, exact output, and bounded conclusion at `.project/active/qualified-reference-occurrence-anchoring/spike/bare-discriminator-authorability/`. The design now cites it. |
| design-F2 / Major 2 | **Accepted in part; mechanism expansion declined.** The design now records the live model as the branch's single authority and names `test_usage_owned_fact_owner_matches_live_part_usage` as the standing corroboration guard. Pushback: frozen owner fields do not participate in the branch decision, so adding owner metatype to `ResolvedTargetFact` would duplicate the live authority and widen the cross-repository schema without a current consumer. No producer-schema follow-up is filed. A future offline owner-kind consumer must reopen that contract. |
| design-F1 / Major 3 | **Accepted.** A corpus census is no longer allowed to prove a deep-override shape impossible or pass that validation row. D11 requires either a kept affected-shape fixture or a named, dated coverage gap with explicit close disposition. |
| design-F3 / Minor 1 | **Accepted.** D10 route 2 now requires a standing `authored bare discrimination unproven` record through close. Constructed-fact discrimination is explicitly not evidence of authored reachability. |
| Minor 2 | **Accepted.** Removed `_transition` from the occurrence-fixed slot-lookup citation; `_target_at`/`_target_for_slot` at `elaborate.py:2350-2366` is the authority. |
| Minor 3 | **Accepted.** Failure behavior and validation now distinguish strict's `_finish_readiness` halt from post-validation graph-diagnostic rejection. |
| Minor 4 | **Accepted in part; “untracked” rejected as stale.** D6 now cites `.project/active/self-binding-replacement/spike/fixtures/` and makes the kept copies the conformance authority because active research paths are archived. Pushback: `git ls-files` lists all u1-u7 models, and `git log` shows them tracked since commit `991ae1e`; the older `findings.md:15` label “untracked” is no longer true. |
| Minor 5 | **Accepted.** The design names the gitignored seed harness at `.project/active/self-binding-replacement/spike/out/bare_expression_side_scan.py`. |

---

**Overall:** Revise
**Next Steps:** Record resolutions here, then re-run `/_my_design` (or return to the design-agent
session) and point it at this review to incorporate. The reviewer does not edit the design. D10
remains an owner decision regardless of the revision — the design's own handoff already blocks
production edits until it is made.
