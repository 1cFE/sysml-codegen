# Product lens: PR-readiness cleanup

## spec — 2026-10-06 — rev .project/active/pr-readiness-cleanup/spec.md

Point (re-derived): Deliver a working PR without cleanup remnants while preserving parser-derived math, named refusals, and honest assurance claims. Fixture convergence remains owner-originated; the additional PR assurance scope remains undecided. [source: `.project/research/20261005-205701_pr-readiness-cleanup-remainder.md`, opening owner quote; `.project/product/0003-no-workarounds-for-bad-models.md` and `0004-product-identity-parse-walk-emit.md`, first-capture owner quotes; active `.project/adr/0004-derive-occurrences-from-exact-evidence-or-refuse.md`; `.project/active/elaborator-downstream/spec-review.md`, Resolution L2-2; grade: owner]

Falsifier: The spec permits guessed resolution, weakens validation to obtain green results, retains the inert duplicate occurrence, or claims downstream completion without discharging its retained obligations.

Findings: None. SC4 removes the duplicate; SC9–SC12 preserve evidence obligations and blocking force. The unanswered PR finish-line decision is explicitly parked without choosing for the owner.

Source grades: ADR `0005` and product `0002`/`0005`/`0006` authorities remain agent/ratified; research C1–C10 recommendations remain AGENT and map to INFERRED acceptance criteria. Downstream scope/convergence rulings retain owner authority; ratified boundary and `REQ-SI` recommendations remain agent/ratified.

Smells: None fired.

Gate: CLEAR for draft fidelity. This verdict does not answer the pending owner scope decision or authorize dependent readiness/closure claims.

## spec-revision — 2026-10-08 — rev .project/active/pr-readiness-cleanup/spec.md

Epic: ELABORATE-FIRST

Point (re-derived): Preserve parser-interpreted math and exact-source wiring, protect real generated packages against regressions, and determine current customer compatibility before the PR. [source: `.project/product/0003-no-workarounds-for-bad-models.md` and `0004-product-identity-parse-walk-emit.md`, first-capture owner quotes; cleanup `spec-review.md`, owner direction and Resolutions L2-2/L2-4; grade: owner]

Falsifier: The candidate guesses model semantics, loses parser-native value units or handwritten implementations, or claims customer acceptance passed while six baseline failures remain undispositioned.

Findings:

- spec-revision-F1 [DO] Customer acceptance still needs an agreed outcome: the review proposes passing acceptance tests but reports six shared baseline failures. — cleanup `spec-review.md`, L2-4 acceptance formulation (AGENT inference from owner direction) — disposition: explicitly parked in the spec's owner question; no waiver inferred, and dependent acceptance conclusions remain parked.

Unit-removal disposition: No contract-change ADR is required on the located authority. Removing the three guessers follows owner product promises `0003`/`0004` and the explicit L2-2 ruling. Parser-native written-value units and constraint behavior remain required. SC8 includes reconciliation of the inherited unit-metadata description in `docs/architecture/modeling-assumptions.md`; no invariant ownership transfers.

Parent assurance: SC9/SC10 preserve retained Item 8 obligations and its single completion authority. The referenced downstream ledger's `spec-F1` was explicitly resolved; no live parent BLOCK was located. Scope removal does not establish completion.

Smells: None fired.

Gate: DISPOSED (spec-revision-F1) for draft fidelity; customer acceptance disposition remains pending.

## spec-clarification — 2026-10-08 — rev .project/active/pr-readiness-cleanup/spec.md

Epic: ELABORATE-FIRST

Point (re-derived): Emit parser-resolved math without model workarounds, and establish current customer compatibility before the PR by diagnosing failures and repairing their causes. [source: `.project/product/0003-no-workarounds-for-bad-models.md` and `0004-product-identity-parse-walk-emit.md`, first-capture owner quotes; cleanup `spec-review.md`, Resolution L2-4; owner clarification captured in spec Known Requirements, 2026-10-08; grade: owner]

Falsifier: Compatibility evidence dismisses an unresolved codegen defect as customer debt, or invents model semantics to preserve a baseline result.

Findings: None. SC13 requires reproduced causes, codegen regression repair, and revision-specific rerun evidence. The owner permits model repair rather than a blanket no-new-failures rule; the Non-Goals keep broad customer physics/economics changes separate.

Resolves:

- spec-revision-F1: FIXED — authority: owner — basis: “I am not requiring "no new failures" if we have model issues -- those can be fixed”; SC13 replaces the unresolved acceptance formulation with diagnosis and repair, informed by the owner-named customer cleanup reports. This resolves the specification question; customer compatibility remains to be demonstrated.

Smells: None fired.

Gate: CLEAR
