# Final Spec Review: Unit-Lane Port Metadata Defect

**Spec:** `.project/active/unit-lane-port-metadata/spec.md`
**Contract:** `my-spec` (`/home/reid/.agents/skills/my-spec/SKILL.md`)
**Prior Review:** this file before the final 2026-08-13 review
**Review File:** `.project/active/unit-lane-port-metadata/spec-review.md`
**Date:** 2026-08-13

---

## Reality Check

**Sound.** The spec remains about the right standalone Item 8 defect. The current code still
confirms the premise: constraint-bound metadata takes the calc-only extraction branch at
`src/sysml_codegen/elaboration/elaborate.py:1670-1695`; computed-expression inputs omit unit
metadata at `src/sysml_codegen/elaboration/elaborate.py:2379-2407`; the v3 codec already preserves
`PortMetadata.unit` at `src/sysml_codegen/snapshot/instance_graph.py:222-290`; and projection
refuses unequal entry-point candidates at `src/sysml_codegen/elaboration/project.py:363-400`.
The only finding from the prior pass is now resolved, the four earlier fixes remain intact, and
the revision introduces no new contract defect.

---

## Prior Finding Verification

### Re-review L3-1 — Item 6 complete recapture coverage

**Resolved.** The handoff is now drift-detecting and covers every tracked snapshot artifact rather
than promoting a corpus subset or a count into future scope.

- Item 8 must publish its sorted final tracked path set, measured count, and set-equality evidence;
  a count without the paths is insufficient (`spec.md:210-219`).
- The handoff must update the named Item 6 design and implementation records, but it expressly may
  not replace stale `21` with `23` or with another eventual count (`spec.md:220-234`).
- Item 6 derives its expected graph-v4 path set from the version-controlled
  `tests/fixtures/**/instance_graph_snapshot.json` inventory at its own immutable baseline
  (`spec.md:227-234`). Its disposition rows must equal the union of its pre-change and final path
  sets; its graph-v4 artifact/evidence rows must equal the final path set; and every addition or
  removal must be named with authority (`spec.md:235-240`). This detects drift in both directions,
  including a removed path that a final-set-only check would miss.
- The current recapture batch is retained only as a subset gate. The spec says it cannot prove the
  complete-set obligation unless Item 6 broadens or replaces it and proves the required equalities
  (`spec.md:242-246`). That matches the code: the manifest currently names 15 captured paths
  (`tests/fixtures/v6_recapture_batch/batch.json:2-18`), and the test deliberately restricts its
  path-set comparison to corpus members (`tests/conformance/test_v6_recapture_batch.py:99-113`).

The repository measurement also checks out independently: `git ls-files
'tests/fixtures/**/instance_graph_snapshot.json'` returns 23 sorted paths on 2026-08-13, while the
accepted batch asserts 15 captured paths (`test_v6_recapture_batch.py:52-54`). The stale Item 6
records still say 21 (`calcdef-constraint-gate-design/design.md:290-294` and
`implementation-item.md:376-380`), so the spec correctly treats them as named handoff targets to
correct, not as evidence already made true.

### Dated measurements and separate recapture duties

**Resolved.** The numbers and ownership boundaries no longer drift together.

- The 23-total and 15-subset values are explicitly dated evidence, not durable scope. Item 8
  re-derives its final v3 set at its reviewed commit; Item 6 later re-derives its graph-v4 set at
  its own baseline and records drift instead of reusing either number (`spec.md:247-250`).
- Item 8 owns only its present semantic-churn assessment and conditional single v3 recapture.
  Item 6 owns the separately authorized future graph-v4 migration; Item 8 neither performs nor
  authorizes it (`spec.md:251-259`). This matches the epic's standalone ruling
  (`epic_constraint_semantics_contract.md:1171-1178`) and the downstream ownership split
  (`calcdef-constraint-gate-design/design.md:188-202, 290-294`).

---

## Earlier Fix Regression Check

| Earlier finding | Final disposition | Evidence |
|---|---|---|
| **Original L1-1 — recapture trigger scope** | **Still resolved.** | Staleness is final live movement in the exact instance-graph payload or relevant unit fields. Envelope bytes, `captured_at`, computation digests, and projected counts are recorded evidence rather than triggers (`spec.md:72-78, 194-206`). The unit field is part of the graph codec (`snapshot/instance_graph.py:222-290`). |
| **Original L1-2 — inherited full-suite pass conflicts with the baseline** | **Still resolved.** | The default maintained lane must pass; the all-marker lane is compared pre/final with zero new failing nodes; and the unconditional inherited pass remains parked (`spec.md:89-94, 275-307`). The default configuration excludes execution tests (`pyproject.toml:44-50`), while Item 5 recorded the pre-existing whole-set failure and isolated-pass account (`verification.md:16-56, 863-871`). |
| **Original L2-1 — design mechanism frozen in requirements** | **Still resolved.** | The spec fixes the semantic source and sealed-graph observable, then leaves helper placement and finalization order to design (`spec.md:126-133, 330-333`). |
| **Original L3-1 — no complete Item 8 gate over every tracked snapshot** | **Still resolved.** | Pre-change rows must equal the complete tracked path set; final rows must equal the then-current tracked set; both checks reject missing, extra, or duplicate paths and record additions/removals (`spec.md:65-71, 176-188, 271-274`). The independently enumerated current set is 23 paths, not the 15-path accepted-batch subset. |

---

## Audit

### Lens 1 — Faithfulness

No finding. The revision preserves the actual source grades, the standalone Item 8 delivery ruling,
the Item 8/Item 6 ownership split, and the surfaced full-suite premise conflict. It does not promote
ratified agent content to owner-originated authority.

### Lens 2 — Problem & Approach

No finding. The contract still repairs the two missing unit lanes at the sealed graph boundary and
leaves code placement, fixture organization, and the future Item 6 proof mechanism open to design.

### Lens 3 — Pipeline Risk

No finding. The handoff now transfers exact evidence, requires correction of every named stale
downstream record, and requires Item 6 to prove its own future complete path set. Counts, subset
gates, and Item 8's v3 churn decision cannot stand in for Item 6's graph-v4 recapture evidence.

### Lens 4 — Hygiene

No material hygiene finding.

### Lens 5 — Reader Comprehension

No comprehension finding. A reviewer can distinguish the current 23/15 measurements, Item 8's
conditional v3 duty, and Item 6's future complete graph-v4 duty on one read.

---

## Engagement Summary

**Overall take:** The final revision closes the last proof-coverage gap. I would trust this spec as
the design contract: its present Item 8 inventory gate is complete, its downstream handoff detects
path-set drift, and it keeps the two recapture duties separate.

**Here's what I need you to weigh in on:** Nothing. No unresolved finding remains in this review.

---

## Resolutions

- **[Re-review L3-1]** Verified resolved. Item 6 must re-derive and prove exact graph-v4 coverage
  over its own then-current tracked snapshot path set; the historical batch may remain only a
  subset gate.
- **[Original L1-1, L1-2, L2-1, L3-1]** Verified still resolved with no regression.

---

**Verdict:** Approve

**Next Steps:** Proceed to `my-design`. Carry the exact Item 6 handoff targets forward unchanged;
do not substitute a measured count or the accepted-batch subset for either item's path-set proof.
