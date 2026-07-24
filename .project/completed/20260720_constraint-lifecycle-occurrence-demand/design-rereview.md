# Design Re-review: Lifecycle Remediation Item 1 — Occurrence and Demand Integrity

**Design:** `.project/active/constraint-lifecycle-occurrence-demand/design.md`  
**Approved Spec:** `.project/active/constraint-lifecycle-occurrence-demand/spec.md`  
**Spec Approval:** `.project/active/constraint-lifecycle-occurrence-demand/spec-rereview.md`  
**Historical Review:** `.project/active/constraint-lifecycle-occurrence-demand/design-review.md`  
**Date:** 2026-07-19

---

## Verdict Summary

**Approve.** The revised design closes C1, C2, C3, C5, M1–M5, and all four historical
advisories. C4 is correctly resolved as a register-boundary correction: Item 1 preserves the
existing warning-before-BLOCK preflight order, places complete association before it, and places
all owner queries after it. The design explicitly leaves warning-location totality open for Item
4/register row 4 and introduces no new R-8 regression.

The approach remains proportional to the work. It replaces the current duplicated live/replay
queries and route-counted materialization with one prepared batch and one target-keyed demand
operation. Its new records carry information that the existing code currently loses; they do not
introduce a general resolver, persisted schema, or parallel compatibility path.

## Review Basis

This was a focused independent re-review. It read the revised design, approved spec, spec approval,
historical design review, register ownership, and the current implementation seams named by those
artifacts. It did not reopen broad exploration already completed by the historical review.

The current checkout remains the right comparison point:

- The nine planned Python paths and two architecture docs are byte-identical between the OD-R30
  predecessor `ecdc7285be1508c08e82830c93072306f40e6b34` and current
  `8d4f2982c5d6202376f60fdaeed5bc785c07903f`.
- The raw line baselines in Appendix A reproduce for all nine Python paths and both docs.
- The current code still has the reviewed defects: nullable-QN demand membership and suppressed
  expansion failures (`constraint_lowering.py:430-473`), revisit-as-empty recursion
  (`part_instance_index.py:142-161`), per-owner recorder commits
  (`part_instance_index.py:379-395`), route-counted/last-write-wins materialization
  (`supplied_values.py:206-332`), and duplicate live/replay queries
  (`pipeline_builder.py:828-898`; `graph_rebuild.py:82-110,214-223`).

## Historical Finding Closure

### Critical findings

| Finding | Status | Independent closure verification |
|---|---|---|
| **C1 — same-target conflict rejects legitimate scopes** | **Closed** | D5 separates normalized target identity from origin lookup context. D6 evaluates each distinct context and accepts raw scope/owning-PartDef differences when numeric or unresolved/nonliteral outcomes agree (`design.md:149-157,210-230,288-306`). Only semantic outcome disagreement raises. Appendix B keeps unchanged sibling, retype, IFE, and fusion controls and adds direct equal-outcome/conflicting-outcome unit cases (`design.md:631-639`). The named control APIs and fixtures exist at both OD-R30 and current. |
| **C2 — provenance required before it can be known** | **Closed** | `ValueResolution` carries the winning record and source; `ResolvedDemand` carries the selected group source (`design.md:210-230`). D7 and the resolution flow choose calc/exact-real/winning-record/usage provenance only after all contexts resolve (`design.md:158-162,288-306`). I7 keeps scan/apply/nonliteral count, warning, synthesis, and group choice to one logical operation per normalized target (`design.md:373-378`). |
| **C3 — recorder transaction stops at one owner** | **Closed** | D2 deletes `RecordingOccurrenceIndex`, stages successful part-owner results in a private local dictionary, and constructs the immutable transcript only after every prepared item succeeds (`design.md:136-140,186-208,248-260`). There is no externally held journal to leak owner A when owner B fails. OD-A05 adds the later-owner rollback case, and the error table forbids a returned batch, transcript, context, graph, catalog, snapshot, or target mutation (`design.md:388-404,616-617`). B5 honestly states the load-bearing assumption that an occurrence query has no external mutation; current live and frozen occurrence sources satisfy that boundary. |
| **C4 — warning projection can mask BLOCK** | **Boundary corrected; no Item 1 fix required** | The lifecycle contract assigns “out-of-root warning followed by BLOCK” to diagnostics/defaults register row 4, and Epic Item 4 explicitly owns total warning rendering. D11 does not claim closure (`design.md:176-179`). I1 places complete association before warning projection; I2 preserves warning-before-BLOCK preflight before every owner query (`design.md:362-365`). The architecture acknowledges that unmappable warning projection may still mask BLOCK and preserves its bytes/order/failure behavior (`design.md:248-266`). This is the required Item 1 boundary and adds no new R-8 regression. |
| **C5 — APIs do not enforce the call graph** | **Closed** | The exact API table pins association, preparation, resolution, enrichment, and lowering ownership (`design.md:232-244`). Live and replay each call preparation once and reuse its batch (`design.md:313-342`). `lower_constraints` accepts the prepared batch but no occurrence index, owner-expansion calc usages, source-location policy, or profile result; I10 also forbids profile evaluation and occurrence queries. Replay carries the batch through the existing classifier-input result rather than rebuilding it. |

### Major findings

| Finding | Status | Independent closure verification |
|---|---|---|
| **M1 — serializer ownership ambiguous** | **Closed** | D10 chooses the bounded second association and narrows “evaluate once” to live construction or one replay rebuild (`design.md:171-175,313-358`). The shared association helper owns the `PROFILE_SEMANTIC_VERSION` guard and complete pair validation. Direct serialization uses it only for excluded/unsupported location canonicalization, emits no warning, aggregates no BLOCK, performs no query/expansion/demand, and mutates only a deep copy. Valid serialized shape and meaning do not change, so no format/profile/package/catalog/schema bump is justified. |
| **M2 — claimed production union incomplete** | **Closed** | Appendix A now starts with nine Python paths, not six, and separately records two architecture docs (`design.md:507-570`). It includes serializer plus truth-bearing comment changes in pipeline context, snapshot exports, and loader. The pure serializer choice makes changes to capture and snapshot context unnecessary. OD-R41 remains automatic: any actual added/changed/moved/deleted production path joins the union, so the starting list cannot become a post-hoc allowlist. |
| **M3 — non-positive executable LOC implausible** | **Closed** | Appendix A gives per-file executable baselines, additions, named deletions, and candidate caps. The budget is 3,524 to at most 3,504 executable lines, with `+181/-201` allocated across the planned starting union (`design.md:515-531`). The added records and staging are funded by concrete deletions: the recorder, duplicate demand collector/query plumbing, route tuple/count loop, last-write-wins synthesis, and duplicated live/replay bucketing (`design.md:533-550`). The target is aggressive but plausible and honest: counts are provisional, every changed path auto-joins, closeout reruns the same counter plus Ruff/AST checks, and a positive result requires the owner-reviewed OD-R43 deviation. The design does not claim the implementation has already met the gate. |
| **M4 — acceptance architecture not executable** | **Closed** | Appendix B names five unchanged RED/GREEN nodes in one file and restricts them to APIs present at OD-R30 and candidate: `build_pipeline_context`, `capture_snapshot`, `build_full_graph_from_snapshot`, and `CodeGenerationError` (`design.md:574-589`). Those APIs exist at both revisions. The fixture table pins source values, groups, targets, counts, warnings, transcript observations, and generated verdicts (`design.md:591-607`). OD-A01–OD-A13 map exact existing/candidate selectors and public observations; the worktree/overlay/hash recipe prevents candidate-conditional RED tests; candidate gates separate normal, optimized, full, licensed-live, and TEAx execution, with skips explicitly unproven (`design.md:609-700`). |
| **M5 — agent bets hardened in handoff** | **Closed** | The Key Bets section marks B1–B5 `[INFERRED]`, agent-grade, and challengeable (`design.md:108-127`). The handoff says every inferred bet and mechanism must be re-derived or challenged when implementation evidence conflicts, while only owner-originated outcomes and register ownership are settled (`design.md:496-504`). No approval language upgrades the bets’ provenance. |

### Historical advisories

| Advisory | Status | Independent closure verification |
|---|---|---|
| **A1 — overbroad copy-on-write claim** | **Closed** | D9 and I9 limit the claim to the attribute mapping and its lists, return a new `Path`-keyed map for both routes, and explicitly leave calc self-binding rescue as existing mutation (`design.md:167-170,379-380`). |
| **A2 — stale snapshot-context defaults** | **Closed as bounded follow-up** | Compatibility records the existing default-field asymmetry and explains why no prepared batch enters `PipelineContext`; `snapshot_context.py` therefore stays outside Item 1 unless implementation evidence changes that boundary (`design.md:438-443`). |
| **A3 — aliased mutation tests** | **Closed** | OD-A01 requires independent identity/location clones through `dataclasses.replace`/`deepcopy` before deletion, duplication, reorder, identity edit, and location edit (`design.md:611-613`). |
| **A4 — cycle stack structure** | **Closed** | The cycle stack is per recursion path, detects re-entry of an active definition, and carries the incoming owner/feature/type edge as structured error evidence. It is neither a global visited set nor the final ordering key (`design.md:145-148,268-286`). The public surface is one outer `CodeGenerationError` caused by `RecursiveContainmentError`, with five typed cause fields and exact self/indirect cycle paths pinned in OD-A05 (`design.md:268-286,616-617`). |

## Focused Contract Checks

### Semantic demand and provenance

**Pass.** Exact `_BindingTarget.qn` remains the Item 1 equality seam. Contexts are retained and
compared by resolved meaning rather than raw scope. Equal outcomes preserve the existing
sibling/retype/IFE/fusion controls; different numeric values or literal/nonliteral/unresolved
dispositions fail with target and origin context. Provenance selection happens afterward. Counts,
warnings, synthesis, and grouping remain one per normalized target.

### Atomic preparation and no re-query

**Pass.** Preparation is the only owner-query boundary. It verifies association, completes existing
preflight, filters owners, stages all supported owner results privately, and freezes one batch.
Live construction and replay rebuild each call it once. Lowering cannot receive an occurrence
source and therefore cannot query one; its stated ownership also excludes profile evaluation.

### Serializer and versioning

**Pass.** The serializer’s second association is disclosed, pure, guarded, and narrower than
preparation. It cannot emit warnings, handle BLOCK, query occurrences, or discover demand. Because
the prepared records remain ephemeral and valid snapshot bytes keep their v3 meaning, retaining the
existing snapshot/profile/package/catalog/schema versions is the correct choice.

### Cycle, copy-on-write, and mutation surfaces

**Pass.** Cycle detection has one structured internal error and one stable public generation error
surface. Attribute enrichment normalizes `Path | str` keys into a fresh `Path`-keyed mapping and
does not overstate unrelated replay mutation. Failure boundaries stage resolution results and log
events before returning the enriched map.

### Accounting, evidence, and capture fidelity

**Pass.** The production union is automatic, the provisional per-file budget is falsifiable, and
the acceptance plan can run unchanged public nodes at RED and GREEN. Licensed public cells cannot
be certified by a skip, while same-checkout replay stays regression-only. All mechanism and proof
choices inherited from `[INFERRED]` spec requirements remain challengeable.

## Dimensional Summary

| Dimension | Assessment |
|---|---|
| Spec compliance | Pass |
| Pattern consistency | Pass |
| Abstraction quality | Pass |
| Duplication avoidance | Pass |
| Data structure clarity | Pass |
| Route safety | Pass within the Item 1 / Item 4 register boundary |
| Bets and decisions integrity | Pass |
| Reader comprehension | Pass |

## Residual Findings

**Must-fix:** None.

**Advisory:** None.

---

**Overall:** Approve  
**Next Steps:** Proceed to `my-plan`. Planning and implementation must preserve the exact batch/API
ownership, automatic accounting union, unchanged RED/GREEN surface, and the explicit Item 4 R-8
boundary recorded here.
