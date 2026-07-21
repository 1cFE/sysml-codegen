# Spec Review: Lifecycle Remediation Item 1 — Occurrence and Demand Integrity

**Spec:** `.project/active/constraint-lifecycle-occurrence-demand/spec.md`
**Contract:** `/home/reid/.agents/skills/my-spec/SKILL.md`
**Review File:** `.project/active/constraint-lifecycle-occurrence-demand/spec-review.md`
**Date:** 2026-07-19

---

## Reality Check

**Sound, with contract-blocking concerns.** The draft is about the right register row, and its
problem statement matches the current implementation: demand admission still uses nullable-QN set
membership, recursive containment still returns an empty subtree, and calc/constraint demand still
appends two actionable records before last-write-wins synthesis. The work item does not fail Stage 0,
but design should not treat this draft as the contract until the provenance, association, demand
identity, proof-scope, and evidence-gate findings below are fixed.

Severity in this review is explicit: **Must-fix** blocks design-contract approval; **Advisory** should
improve the revision but does not independently block it.

---

## Audit

### Lens 1 — Faithfulness

**L1-1 · Direct claim · Must-fix:** The draft repeatedly upgrades agent-authored or inherited rules
to owner-stated `[NEED]` requirements. The ratified lifecycle contract explicitly says ratification
does not change origin (`constraint-execution-authoritative-lifecycle-contract.md:24-25`; companion
spec `:43-45`). Yet every top-level success criterion is `[NEED]` (`spec.md:41-64`), and OD-R01,
OD-R05, OD-R07, OD-R11, OD-R14, OD-R18, OD-R19, OD-R21, OD-R22, OD-R24, OD-R27, and OD-R29 are also
`[NEED]`. Their sources are the agent-authored remediation item, `[INHERITED]` LC-D rules, or
`[INFERRED]` proof/deletion rules. The Item 2/5/13 non-goals are likewise labeled `[NEED]` even
though register ownership is inherited. Re-run the capture-fidelity absorb mapping across the whole
spec: owner-originated content may be `[NEED]`; ratified agent recommendations remain `[INFERRED]` or
`[INHERITED]` with their source. The owner's simplification quote supports the reduction outcome,
not every exact deletion path or measurement mechanism chosen here.

**L1-2 · Direct claim · Must-fix:** OD-R26 overstates what Item 1 can certify. It says Item 1 may
close row 1's “live and same-checkout replay claims” (`spec.md:193-195`), but the normative register
closes row 1 on the live cells and assigns the anonymous cell's relocated route to row 5
(`constraint-execution-authoritative-lifecycle-contract.md:504-511`; lifecycle spec `:482-489`).
LC-I09 defines a certifying snapshot route as relocated replay with the full coordinate and artifact
thread (`constraint-execution-lifecycle-contract/spec.md:416-421`). Same-checkout replay is valuable
R-4 regression evidence, but it is not a completed LC-I09 acceptance route. Rewrite the closure
language so Item 1 can close row 1 from the required live observations while recording same-checkout
replay as non-certifying defect evidence; Item 5 retains relocated/full-tree certification.

### Lens 2 — Problem & Approach

**L2-1 · Direct claim · Must-fix:** The anonymous usage/decision contract is internally inconsistent.
OD-R01 requires a new “non-null, occurrence-stable identity” (`spec.md:94-96`), OD-R04 denies edited-
version stability (`:104-106`), and the design deferral says either ordered correspondence or an
explicit key is acceptable (`:271-274`). Ordered correspondence is not itself a non-null identity.
The current profile already returns one decision per usage in exact list order
(`../agentic-mbse/src/agentic_mbse/sysml/executable_profile.py:996-1008`); the actual R-4 defect is
loss of that association when code converts decisions to a nullable-QN set
(`constraint_lowering.py:451-463`). State the outcome as a verified one-to-one usage/decision
association that distinguishes anonymous siblings and fails on deletion or reorder. Positional
association may implement it only with cardinality and identity/location cross-checks. Do not force
a new durable identity that drifts into Item 5 portability or Item 12 cross-version tracking.

**L2-2 · Direct claim · Must-fix:** OD-R14 and OD-R15 leave a circular demand-identity rule that can
accidentally absorb Item 2. Identity is defined as the normalized concrete target, but deduplication
must happen “before value resolution” (`spec.md:148-154`). Current supplied-value code first maps a
route reference to a concrete materializer target (`supplied_values.py:61-99`) and only then resolves
the supplied literal (`:148-203`); general producer/exact-QN actual resolution is a separate lowering
ladder and belongs to Item 2. The spec must distinguish these seams. Item 1 may normalize to the
materializer's target identity and deduplicate before literal resolution/materialization. It must
not introduce a second general resolver. If two syntactically different references are expected to
coalesce, the spec must say which existing target-normalization rule proves they are the same target;
otherwise that expansion belongs to Item 2.

**L2-3 · Direct claim · Must-fix:** The cross-route grouping policy is a defensible agent bet, not an
owner-settled outcome. OD-A09 requires the calc-route group from file A and labels it `[NEED]`
(`spec.md:84`), while OD-R16 correctly admits that calc-origin precedence is `[INFERRED]`
(`:155-158`). The upstream matrix requires the exact parameter group to survive deterministically,
and R-7 proves that appending an assertion must not silently regroup an existing calc input; neither
source makes the chosen precedence owner-originated. Keep calc-origin precedence and the
constraint-only provenance/fail-loud defaults as explicit `[INFERRED]` bets with their rationale, or
obtain an owner decision. The sentence “No owner decision is required” (`:260`) is false while the
draft presents these bets as `[NEED]`.

### Lens 3 — Pipeline Risk

**L3-1 · Direct claim · Must-fix:** OD-A07 does not yet make atomic cycle failure hard to fake. It
tests self/indirect cycles and a finite sibling independently (`spec.md:82`), but the current defect
is an empty return at the revisit point (`part_instance_index.py:157-161`). A partial fix could still
collect a finite branch, encounter a later cycle, and return or record the prefix. Add an order-
adversarial case in which one queried owner has both a finite branch and a cycle, with permutations
that visit the finite branch first. It must raise, return no owner result, leave that owner absent
from `RecordingOccurrenceIndex.recorded`, invoke no demand materialization, and yield no context,
snapshot, graph, catalog, or target mutation. This directly proves invariant 18 and the recorder's
record-after-complete behavior (`part_instance_index.py:392-395`).

**L3-2 · Direct claim · Must-fix:** Same-checkout replay coverage is complete for the anonymous R-4
case but not for the demand fixes. OD-A09 and OD-A11 require public live behavior only
(`spec.md:84-87`), even though the changed collection/materialization logic is duplicated at the
live and replay call sites (`pipeline_builder.py:842-856`; `snapshot/graph_rebuild.py:93-110`).
OD-R22 promises route parity for Item 1 values (`spec.md:178-180`), but no mandatory case observes
shared-route dedup or a constraint-only target after replay. Add same-checkout replay observations to
OD-A09 and OD-A11 for demand identity, grouping, counts, warning bytes/order, retained producer, and
catalog values. Keep relocation and whole-tree byte certification explicitly with Item 5.

**L3-3 · Direct claim · Must-fix:** The RED contract does not identify one exact predecessor. The
header names sysml-codegen `8d4f298` (`spec.md:9`), the baseline section names Item 0
`ecdc728` (`:224`), and the original reproduced review used `512786c`. OD-R24 says only “exact
predecessor” (`:184-187`) while the success criterion says “reviewed/pinned predecessor” (`:57-60`).
Select one exact coordinated sysml-codegen/agentic-mbse revision and lock/profile set for the
unchanged defect-specific RED tests, then require failure for the intended reason before candidate
GREEN. This matters because the existing focused slice is green while all three defects remain: this
review ran 31 current part-index, supplied-value, occurrence-roundtrip, and snapshot-identity tests,
and all 31 passed. Current tests therefore cannot serve as historical RED evidence without new
defect-specific nodes.

**L3-4 · Direct claim · Must-fix:** The count/warning cases prove cardinality for one target, not
deterministic ordering across targets. OD-A09 has one duplicate logical target with no warning;
OD-A10 has one real-attribute collision warning (`spec.md:84-85`). Both can pass if a new set/dict
dedup produces nondeterministic ordering whenever two or more unique targets exist, despite OD-R18's
stronger byte-order promise (`:162-164`). Add a multi-target permutation case with at least one
collision and one non-literal/clean target. It must pin target order, synthesized-attribute order,
counts, warning order and exact warning multiplicity under calc/constraint and input-order reversal.

**L3-5 · Direct claim · Must-fix:** The simplification gate can be gamed by post-hoc scope selection.
The draft gives a five-file candidate baseline, then lets design “narrow or extend” the path list
(`spec.md:220-235`). OD-R29/R30 require accounting and a non-positive touched-surface result, but do
not explicitly require the union of before/after production paths, including deleted, moved, and new
files. Freeze that union before implementation against the Item 0 revision; count a new file from
zero and a deleted file to zero; and prohibit comments/docs/tests/generated output from offsetting
production control-flow growth. The close gate should also record a concrete branch/complexity or
duplicate-path measure for the changed hotspots. Otherwise deleting comments can satisfy LOC while
the route-specific mechanisms remain duplicated, contrary to the owner's actual simplification
outcome.

### Lens 4 — Hygiene

**L4-1 · Rewrite request · Advisory:** The same rules are repeated in Success Criteria, Mandatory
Acceptance Cases, and Known Requirements, and their grades already disagree: calc-route precedence
is `[NEED]` in OD-A09 but `[INFERRED]` in OD-R16. Keep each decision in one requirement home and let
the acceptance table point to requirement IDs. This will reduce the chance that future revisions fix
one copy while leaving another hardened or stale.

### Lens 5 — Reader Comprehension

**L5-1 · Rewrite request · Advisory:** A reviewer cannot currently tell which behaviors came from the
owner and which are proposed defaults. The “No owner decision is required” lead is followed by four
agent-selected mechanisms, while other agent-selected outcomes have already been written as
`[NEED]`. After correcting provenance, give the reader a short review-facing statement of the bets
they are accepting: verified positional-vs-keyed association, materializer-target demand identity,
calc-route grouping precedence, constraint-only provenance failure, and the per-item LOC gate. Do
not call them settled merely because design may proceed with a default.

---

## Engagement Summary

**Overall take:** The draft correctly frames Item 1 and is unusually strong on public execution,
constraint-only demand, owner filtering, and finite-behavior preservation. It still cannot become
the design contract because it launders provenance, leaves two core identities ambiguous, and has
acceptance gaps that allow partial cycle fixes, live/replay drift, nondeterministic warning order,
weak RED evidence, and cosmetic LOC wins.

**Here's what must be resolved before design:**

1. **[L1-1, L2-3]** Regrade owner, inherited, and agent-authored content honestly; calc-route
   grouping and the exact deletion/evidence mechanisms are not owner-originated `[NEED]` items.
2. **[L2-1]** Replace the contradictory “non-null identity or ordered correspondence” language with
   one falsifiable usage/decision bijection that rejects anonymous reorder/deletion.
3. **[L2-2]** Define demand identity at the supplied-value materializer target seam without building
   Item 2's shared producer resolver inside Item 1.
4. **[L3-1, L3-4]** Strengthen the matrix against partial finite-before-cycle returns and multi-target
   count/warning ordering defects.
5. **[L1-2, L3-2]** Treat same-checkout replay as Item 1 regression evidence, add it for R-7 and
   constraint-only demand, and reserve relocated/full-tree certification for Item 5.
6. **[L3-3]** Pin one exact coordinated RED predecessor and require unchanged defect-specific failures;
   the current 31-test slice is green despite all three defects.
7. **[L3-5]** Freeze an ungameable before/after production scope and add a real duplicate/complexity
   reduction check, not LOC alone.

**Advisory cleanup:** [L4-1, L5-1] remove duplicate homes and make the agent bets visible to the human
reviewer.

---

## Resolutions

No resolutions were recorded in this non-interactive review stage.

---

**Verdict:** Revise
**Next Steps:** Return this review to the spec agent and incorporate every must-fix finding without
editing the spec from the review session. Re-run `my-spec-review` after revision; proceed to
`my-design` only when the revised provenance and acceptance gates are trustworthy.
