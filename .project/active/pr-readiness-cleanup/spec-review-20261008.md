# Spec Review: PR-readiness cleanup

**Spec:** `.project/active/pr-readiness-cleanup/spec.md`
**Contract:** `/home/reid/.agents/skills/my-spec/SKILL.md`
**Review File:** `.project/active/pr-readiness-cleanup/spec-review-20261008.md`
**Date:** 2026-10-08

This review assesses the revised contract against the earlier review's recorded owner resolutions and the October 8 customer clarification. The earlier `spec-review.md` remains the authority for those resolutions. Code inspection verifies the unit readers, JSON encoders, public refusal/clearing boundaries, and historical execution-channel account. Relevant downstream authority and the owner-named customer repair reports were consulted. No new runtime acceptance is claimed by this review.

## Reality Check

**Sound.** This is the bounded cleanup the owner requested. The revised spec incorporates public functional regression tests, an independent output baseline, candidate-bound execution evidence, licensed recapture, and preservation of handwritten implementations. It captures removal of all three unit guessers while retaining parser-native written-value units, and it correctly treats current customer failures as causes to diagnose and repair rather than a blanket failure-count gate. One numerical-channel count needs a mechanical correction before the spec becomes the design contract.

## Audit

### Lens 1 — Faithfulness

**L1-1 · Direct claim:** SC4b's channel counts conflict. It requires nine total exits including constraint evaluation and reporting, then requires LCOE and “the other seven numerical channels.” The existing eleven-channel set contains nine numerical channels plus the evaluation and report (`tests/execution/test_fusion_tea_real_teax.py:55`). Removing the two standalone driver outputs leaves seven numerical channels total: LCOE, recirculation, Meier COE, capital cost, reactor cost, and the remaining driver's two outputs. Therefore SC4b has six other numerical channels, not seven. Correct that count while retaining the complete surviving channel set and report assertions. This needs no owner judgment or scope change.

The final owner calls are otherwise preserved with their sources. The inference grade of the detailed regression checks stays explicit. The historical joined proof, lineage, external attestation, copied-store proof, and July impact report remain descoped or retired rather than being converted into passing evidence. Source-identity obligations and Item 8's single completion authority remain visible.

### Lens 2 — Problem & Approach

No material finding. The work targets metadata, rendering defenses, fixture cleanup, typing, tests, documentation, and assurance reconciliation. The spec leaves storage and sequencing to design and does not require another elaborator architecture. Current-customer validation includes the three identified generation cases and permits coordinated model or consumer repairs under the owner's clarification.

### Lens 3 — Pipeline Risk

No additional material finding. SC7 requires a durable baseline before implementation and explicit intended differences. SC2 exercises both public routes and protects existing output; SC3 exercises consumed declarations on live and snapshot routes; SC4 retains numerical, mutation, and report evidence; SC5 requires real handwritten preservation. SC11 binds execution to candidate artifacts and distinguishes newly run results from inherited results. SC13 requires reproduced failure attribution and repair of codegen regressions while identifying remaining customer cleanup. These provisions resolve the earlier review's substantive regression gaps.

### Lens 4 — Hygiene

No material finding. The spec explicitly tells downstream work to use the review's corrections rather than stale research recommendations and citations.

### Lens 5 — Reader Comprehension

No material finding. The success criteria remain detailed, but their labels expose the work groups and the candidate/customer evidence boundaries. Further restructuring is unnecessary for this cleanup.

## Engagement Summary

**Overall take:** The revised spec is a sound contract for the authorized cleanup after one channel-count correction. Its regression protections address the prior review, and its customer criterion reflects the owner's latest direction without imposing a new acceptance rule.

1. **[L1-1]** Correct SC4b to preserve six numerical channels in addition to LCOE, giving seven numerical channels and two constraint exits in total.

No new owner decision is needed. Carry the corrected spec into the smallest design and plan that can implement and verify its existing scope.

## Resolutions

Pending incorporation of L1-1 by the spec author. Existing owner resolutions remain in `spec-review.md`; this review does not amend them.

**Verdict:** Revise — one mechanical correction.
**Next Steps:** Have the spec author correct SC4b, then proceed to design without another reviewer cycle for this objectively verifiable edit.

## Coordinator disposition — 2026-10-08

[AGENT] SC4b now says six other numerical channels alongside LCOE, preserving the seven numerical plus two constraint/report exits. Verified against the reviewer's cited channel arithmetic. This localized count correction needs no new review round.
