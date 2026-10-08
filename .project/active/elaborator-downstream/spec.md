# Spec: Elaborator Downstream Remediation and Certification

**Status:** Reconciled — retained Item 8 scope implemented through PR-readiness cleanup; final evidence and independent audit govern completion
**Owner:** Reid W
**Created:** 2026-08-16
**Reconciled:** 2026-10-08
**Completion authority:** ELABORATE-FIRST Item 8; no replacement item or epic

## Problem

Elaboration, parser/identity follow-through, and repository retirement have shipped. Item 8's remaining work is accurate fixture convergence, current customer validation, guidance, documentation, and evidence reconciliation. The [PR-readiness cleanup spec](../pr-readiness-cleanup/spec.md) is the execution contract for that bounded remainder; this record reconciles the original 21 criteria without creating another completion authority. Both predecessor dependencies are satisfied.

## Known Requirements

- **[NEED]** A modeled source occurrence supplies exactly one runtime source to all and only its modeled consumers, across supported calculation/constraint/aggregation forms; unsupported forms refuse. Authority: parent epic's owner mission invariant; [source-identity reconciliation](../../reference/source-identity-reconciliation.md) preserves original grades and evidence bounds.
- **[NEED]** Regeneration/proof, historical impact, and certification retain one Item 8 completion authority, amended by the later owner scope rulings. Authority: [original review](spec-review.md), Resolution L2-1 (2026-08-16); [cleanup review](../pr-readiness-cleanup/spec-review.md), Resolution L2-1 (2026-10-07).
- **[NEED]** Delete the inert fixture workaround and converge its post-R-2 shape. Authority: original review Resolution L2-2; cleanup review records the mechanical accepted-batch amendment and source provenance at fusion-tea `9e1ff87bb:models/` (2026-08-16). Current customer models are validated at their own named revision; they are not copied wholesale into the historical fixture.
- **[NEED]** Validate current customer compatibility before PR; diagnose causes and permit coordinated model/consumer repairs. Authority: cleanup review Resolution L2-4 and the later owner clarification in the cleanup spec.
- **[INHERITED]** Preserve product `0002`'s deep-override evidence bound and `[ANCHORING-ARRAYED-DIAGNOSTIC]`; preserve retired mechanism dispositions and independent evidence requirements. Sources: product `0002` and the original review's ratified-agent resolutions.

## Original Success Criteria — Current Dispositions

Original wording and order are recoverable at `6872977:.project/active/elaborator-downstream/spec.md`. This table is their current disposition, not a claim that every old checkbox was tested anew. Fresh candidate results and remaining bounds live in the [cleanup evidence](../pr-readiness-cleanup/evidence.md); the independent audit verifies retained outcomes.

| Original SC | Current disposition | Authority / evidence coordinate |
|-------------|---------------------|---------------------------------|
| 1 — Customer public generation and verification | Delivered public route; final candidate validation recorded in cleanup evidence. | Cleanup SC13; current customer archive/loader receipts, live/snapshot tests. |
| 2 — No customer identity workaround | Delivered customer removal; preserved by current package/source comparison. | Research SC2 disposition; current model-family and mutation evidence. |
| 3 — Fixture convergence | Implemented: inert occurrence removed; eleven files match historical post-R-2 customer. | Original owner Resolution L2-2; cleanup C4 exact-source/graph receipt. |
| 4 — Affected fixture/customer pins | Implemented at measured topology; enum-positive resolution remains distinct from enum refusal. | Cleanup SC4 and C4 focused/stock-runtime receipts. |
| 5 — Fixed-point customer LCOE | Historical fixture anchor `270.1211779380445` retained; current customer uses its own changed model identity/results. The old blanket numerical freeze is superseded by later customer work, not used to replace current physics. | Research SC5 disposition; cleanup SC4b/SC13 runtime results. |
| 6 — Additional joined model/package/study proof | Descoped by owner; no additional proof required. | Cleanup review Resolution L2-1, 2026-10-07. |
| 7 — Unrelated-consumer arm of that added proof | Descoped with SC6; existing independent mutation tests remain evidence at their own bounds. | Same owner resolution; current mutation evidence, not a new joined-study claim. |
| 8 — Eight-field old/new study lineage | Descoped by owner. | Cleanup review Resolution L2-1. |
| 9 — Named copied-store incompatibility proof | Not required by owner. | Cleanup review Resolution L2-1. |
| 10 — July impact census/report | Retired by owner. | Cleanup review Resolution L2-1, “Retire it.” |
| 11 — July verdict/consumer report preservation | Superseded with the retired impact-report obligation. Historical originals remain untouched. | Same owner scope ruling. |
| 12 — External-use attestation | Not required by owner. | Cleanup review Resolution L2-1. |
| 13 — Independently grounded REQ-SI family | Reconciled from original LC-SI grades and Item-3 coordinates, with bounded evidence and explicit gaps. Its added composed-study clause is descoped, not labeled PASS. | Cleanup SC9; [source-identity mapping](../../reference/source-identity-reconciliation.md); current verification matrix. |
| 14 — Deep-override/array diagnostic bounds | Retained; no broader certificate manufactured. | Product `0002`; `[ANCHORING-ARRAYED-DIAGNOSTIC]`; source-identity mapping. |
| 15 — Item-3 certification/guidance reconciliation | Present with per-requirement/cell evidence bounds and dispositions; missing coordinates are visible. | Source-identity mapping and cleanup audit. |
| 16 — Modeling-pattern guidance | Delivered, with the later companion warning fixed at committed revision; positive/negative/example-force checks retained. | Cleanup SC1; committed companion revision and guidance tests. |
| 17 — README commands/purpose | Implemented for current live/v6 routes and companion layout. | Cleanup C8 documentation and CLI/public smoke checks. |
| 18 — Fourteen mixed historical docs | Later authorized retirements supersede deleted-doc authorship; finite remaining live accounts corrected. | PR #15 retirement; cleanup C8 finite document changes. |
| 19 — Retain document 25/legacy hierarchy extraction | Superseded by later owner-authorized retirement of that off-route surface. | Research SC19; PR #15 and absence/replacement ledger evidence. |
| 20 — Named pre-work/final regression evidence | Durable all-22 output oracle and pre-change licensed/customer identities captured; final results distinguish intended differences and reproduced causes. | Cleanup SC7/SC11/SC13; baseline `6872977`, immutable expectation manifest. |
| 21 — Final evidence/audit readiness | Final candidate evidence and independent audit govern readiness; cleanup delivery does not itself close Item 8 or the epic. | Cleanup plan phase4/5, evidence, and audit. |

## Non-Goals

- Additional historical assurance work is excluded by the owner rulings cited in the criterion table; the original review retains their reasons and verbatim payload.
- Broad customer physics changes, new solving/compiler capabilities, and predecessor remediation remain separately owned. Targeted customer model/consumer repairs during compatibility work are coordinated under the later owner authorization.

## Related Artifacts

- [Parent epic](../../backlog/epic_elaborate_first_architecture.md), Item 8.
- [Original review](spec-review.md) and [cleanup review/resolutions](../pr-readiness-cleanup/spec-review.md).
- [Cleanup specification](../pr-readiness-cleanup/spec.md), [plan](../pr-readiness-cleanup/plan.md), [evidence](../pr-readiness-cleanup/evidence.md), and [source-identity reconciliation](../../reference/source-identity-reconciliation.md).
- Product promises `0002`, `0003`, `0005`, `0006`, and the original authoritative lifecycle contract/LC-SI catalog.

**Next boundary:** Independent audit of retained outcomes, then the human-controlled close and post-close branch gate.
