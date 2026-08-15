# Spec Re-review: Lifecycle Remediation Item 1 — Occurrence and Demand Integrity

**Spec:** `.project/active/constraint-lifecycle-occurrence-demand/spec.md`
**Historical Review:** `.project/active/constraint-lifecycle-occurrence-demand/spec-review.md`
**Contract:** `/home/reid/.agents/skills/my-spec/SKILL.md`
**Review Skill:** `/home/reid/.agents/skills/my-spec-review/SKILL.md`
**Date:** 2026-07-19

---

## Verdict Summary

**Approve.** The revision closes every historical must-fix without changing the work item or
absorbing Item 2, Item 5, or Item 13. The requirements now distinguish owner outcomes, inherited
lifecycle obligations, and agent-selected proof/design bets; the acceptance matrix is strong enough
to reject the partial fixes identified by the first review.

There are no residual must-fix or advisory findings. Design can safely treat this spec as its
contract.

## Reality Check

**Sound.** The revised problem still matches the Item 0 predecessor and current production seams:
admission is reduced to nullable-QN membership, recursive containment still returns an empty subtree,
and calc plus constraint demand is appended before last-write-wins synthesis
(`constraint_lowering.py:451-472`, `part_instance_index.py:157-161`,
`supplied_values.py:247-312`). The five affected production files are unchanged between the pinned
sysml-codegen predecessor `ecdc7285be1508c08e82830c93072306f40e6b34` and current `8d4f298`, so
the revised contract is still aimed at the reproduced defects.

The Item 0 revisions and lock digests in OD-R30 match
`.project/active/constraint-lifecycle-candidate-pin/evidence.md:8-26`. The five-file starting
inventory also reproduces exactly as 3,527 newline-delimited lines.

---

## Historical Must-fix Closure

| Historical finding | Status | Revised closure | Independent verification |
|---|---|---|---|
| L1-1 — provenance laundering | **Closed** | Only the four owner-originated outcomes remain `[NEED]` (`spec.md:36-48`). Detailed lifecycle rules are `[INHERITED]`; association, demand, evidence, and accounting bets are `[INFERRED]` (`spec.md:54-218`). Acceptance rows are explicitly non-normative proof instruments (`spec.md:239-243`). | This preserves the upstream rule that ratification does not rewrite origin (`constraint-execution-lifecycle-contract/spec.md:39-45`). The explicit bet index also says the defaults remain challengeable (`spec.md:261-274`). |
| L1-2 — replay overstated as certification | **Closed** | OD-R04 assigns row-1 closure to public live cells; OD-R08 and OD-R27 label same-checkout replay regression-only; OD-R34 leaves relocated/full LC-I09 evidence open (`spec.md:61-76`, `149-152`, `181-184`). OD-A07–OD-A12 preserve that distinction (`spec.md:253-258`). | This matches register row 1 and row 5 exactly (`constraint-execution-authoritative-lifecycle-contract.md:504-511`; `constraint-execution-lifecycle-contract/spec.md:482-489`). |
| L2-1 — contradictory anonymous identity contract | **Closed** | OD-R10 requires a one-to-one usage/decision association. OD-R11 permits ordered pairing only with cardinality, identity, and location cross-checks and explicitly declines to require a new durable identity (`spec.md:80-89`). OD-A01 mutates deletion, duplication, reorder, and cardinality (`spec.md:247`). | The profile currently returns one decision per usage in source order (`../agentic-mbse/src/agentic_mbse/sysml/executable_profile.py:996-1008`) and each decision carries identity/location (`:120-131`). The revision targets the actual association loss at `constraint_lowering.py:451-459` without claiming cross-version stability. |
| L2-2 — circular demand identity / Item 2 absorption | **Closed** | OD-R20 defines equality as exact `_BindingTarget.qn` equality after the existing materializer normalizer. OD-R21 places dedup after that normalizer and before literal resolution, and excludes new syntactic equivalence and general producer resolution (`spec.md:114-128`). | The boundary matches `_binding_target` and `_resolve_value` (`supplied_values.py:61-99`, `148-203`). OD-R05 and the Non-Goals keep the shared producer/exact-QN resolver in Item 2 (`spec.md:65-67`, `276-280`). |
| L2-3 — grouping policy presented as owner-settled | **Closed** | Calc-route precedence and constraint-only provenance are now explicit `[INFERRED]` bets with rationale, not `[NEED]` or settled decisions (`spec.md:129-137`, `266-274`). OD-A08 and OD-A09 test both defaults without changing their provenance (`spec.md:254-255`). | The treatment matches the upstream shared-demand observation while remaining honest that the exact precedence is agent-selected (`constraint-execution-authoritative-lifecycle-contract.md:427-430`). |
| L3-1 — cycle failure could return a finite prefix | **Closed** | OD-R15 makes a mixed finite-plus-cycle owner query atomic across branch permutations and forbids owner results, recording, demand, context, transcript, graph, catalog, or target mutation (`spec.md:101-106`). OD-A05 tests the finite-first case, reversed orders, repeated traversal, and all zero-mutation observations (`spec.md:251`). | This directly attacks the current empty-subtree revisit (`part_instance_index.py:157-161`) and verifies the recorder remains record-after-complete (`part_instance_index.py:392-395`). |
| L3-2 — demand replay parity missing | **Closed** | OD-R27 requires same-checkout replay parity for OD-R20–OD-R26, including identity, grouping, counts, warning values/order, producer, and catalog (`spec.md:149-152`). OD-A08–OD-A10 exercise shared, constraint-only, and multi-target demand on live and replay (`spec.md:254-256`). | These cases cover both current call sites (`pipeline_builder.py:842-856`; `snapshot/graph_rebuild.py:93-110`) while OD-R08/OD-R34 prevent replay from being presented as relocated certification. |
| L3-3 — RED predecessor ambiguous | **Closed** | OD-R30 names one coordinated agentic-mbse/sysml-codegen/TEAx revision and lock set; OD-R31 requires unchanged defect-specific tests to fail for the intended reason; OD-R32 rejects the historical green slice as RED (`spec.md:156-175`). OD-A11 names the five new nodes (`spec.md:257`). | The revisions and SHA-256 digests match Item 0 evidence (`constraint-lifecycle-candidate-pin/evidence.md:8-26`). The recorded 31-test slice did pass while all three defects remained, so it is correctly retained only as baseline regression evidence. |
| L3-4 — deterministic order untested across targets | **Closed** | OD-R25 fixes unique-target processing, count, warning, and synthesis order (`spec.md:141-145`). OD-A10 uses three ordered targets spanning collision, non-literal, and clean outcomes; it pins normalized order, synthesized order, counts, exact two-warning order, multiplicity, route reversal, input reversal, live, and replay (`spec.md:256`). | The expected messages and counts correspond to the current collision and summary seams (`supplied_values.py:271-331`) and would fail unordered or route-counted implementations. |
| L3-5 — production reduction gate gameable | **Closed** | OD-R41 freezes the Item 0 production manifest and the before/after path union; new, deleted, and moved paths have explicit zero-side treatment. OD-R42 prevents non-production and blank/comment reductions from offsetting production control flow. OD-R43 requires non-positive executable production LOC or an owner-reviewed deviation. OD-R44 adds branch/complexity and deletion proof (`spec.md:199-215`). | The frozen inventory and automatic-addition rule prevent a post-hoc allowlist (`spec.md:220-237`), and OD-A13 requires a complete union ledger (`spec.md:259`). This is consistent with Item 0's production counting boundary (`constraint-lifecycle-candidate-pin/evidence.md:47-68`). |

## Historical Advisory Closure

| Historical finding | Status | Verification |
|---|---|---|
| L4-1 — duplicate decision homes | **Closed** | Requirements are the single normative home; acceptance rows cite requirement IDs and expressly create no second grade or precedence rule (`spec.md:239-243`). |
| L5-1 — agent bets invisible to the reviewer | **Closed** | The Explicit Agent Bets table names association, demand equivalence, shared grouping, constraint-only provenance, ordering, cycle error shape, and the close gate, and says each remains challengeable (`spec.md:261-274`). |

---

## Independent Regression Scan

### Material contradiction

None found. Public-live row-1 closure, non-certifying same-checkout replay, and later relocated and
composed proof remain consistent across OD-R04/OD-R08/OD-R27/OD-R34 and the upstream register.

### Provenance laundering

None found. `[NEED]` is confined to the four recorded owner outcomes. No agent mechanism is marked
settled or owner-originated, and the acceptance table does not re-grade requirements.

### Scope absorption

None found. OD-R20–OD-R21 stop at the existing supplied-value target normalizer; OD-R05 and the
Non-Goals retain shared producer resolution, relocated portability, and composed artifact proof in
Items 2, 5, and 13.

### Untestable acceptance

None found. Each historical gap now has a falsifiable case with named mutations or exact observable
order/count/message/state outcomes. The evidence and accounting gates also bind the coordinate and
measured path union rather than allowing an implementation-selected proof scope.

## Residual Findings

**Must-fix:** None.

**Advisory:** None.

---

**Verdict:** Approve

**Next Steps:** Proceed to `my-design`. Design should treat OD-R10–OD-R45 as the normative detailed
contract, preserve the explicit agent-bet status, and map its validation plan to OD-A01–OD-A13.
