# Design Review: Stop Reinventing the Parser

**Design:** `.project/active/stop-reinventing-the-parser/design.md` (Revision 4)
**Spec:** `.project/active/stop-reinventing-the-parser/spec.md` (Revision 4, approved)
**Prior Review:** Revision 3 review in this file (`Revise`; F5 open)
**Product Lens:** `.project/active/stop-reinventing-the-parser/product-lens.md` (`CLEAR`, Revision 4 final rerun)
**Date:** 2026-08-16

---

## The Point

Make SysIDE's resolved semantic model the parser authority. Derive concrete occurrence identity and
contextual calculation output from modeled containment and the consumer domain, preserve complete
parser evidence through one public refusal boundary, and emit the resulting math through TEAx. No
name, path, proximity, candidate count, declaration order, or sibling checkout may stand in for the
modeled or artifact identity being proved.

## Fundamental Assessment

**Assessment: Sound — Approve.**

Revision 4 is the right piece of work and now has the right complete approach. The semantic design
still changes the existing exact route in place. Its private values and indexes earn their existence
by making modeled containment and contextual producer identity explicit without adding a strategy
layer or second resolver. The final evidence design is acyclic, mechanically checkable, and does not
change the product architecture.

The fresh product lens is `CLEAR`. Consumer-compensates-for-producer smell 2 does not fire, and
undeclared-invariant-transfer smell 7 does not fire. The design consumes parser-owned metatype,
resolved-target, and document-tier evidence; it explicitly leaves concrete occurrence
materialization with codegen and final artifact provenance with the verification records.

F5 is resolved. F1-F4 and F6-F8 remain resolved. The spec's deferred design questions have concrete
answers or fail-fast measured gates. No implementation choice can select a fallback architecture,
and no open design choice remains.

## Final F5 Verification

| Required correction | Result | Evidence |
|---|---|---|
| `C_prod` is the complete production identity | **Resolved** | `C_prod` contains all production source, tests, fixtures, public docs, package metadata, dependency minimums, pins, and locks needed to build, consume, and test codegen. It excludes only the final cross-repository evidence files (`design.md:567-574,589-595,945-948`). |
| Fusion pins only `C_prod` | **Resolved** | Fusion writes the exact full `C_prod` SHA into both `pyproject.toml` and `uv.lock`; audit rejects `C_evidence`, sibling paths, and editable sources. The installed wheel must match the wheel built from `C_prod` (`design.md:575-577,601-612,643-658`). |
| `F_final` closes before evidence | **Resolved** | Fusion lands `F_final`, builds and verifies its archive, and only then may codegen create the evidence commit (`design.md:575-580,949-954`). |
| `C_evidence` is evidence-only and outside production identity | **Resolved** | `C_evidence` is a direct child of `C_prod`, changes exactly six named evidence paths, is never archived or certified as codegen, is never pinned downstream, and is excluded from the certified tuple (`design.md:578-595,601-606`). |
| No self-reference remains | **Resolved** | The evidence records name `C_prod` and `F_final`, not `C_evidence`; no record stores its own commit or hash; `evidence-lock.json` excludes itself; audit supplies `C_evidence` externally (`design.md:583-587,596-609`). |
| Evidence-lock coverage is coherent | **Resolved** | The lock hashes all five sibling evidence-only files plus the production-side probe lock and expected-transition ledger. `dependencies.json`, itself locked, carries the `C_prod` archive hash that seals the remaining production-side records transitively (`design.md:553-563,589-599,607-614`). |
| The changed-path boundary is mechanically auditable | **Resolved** | Audit requires `C_evidence^ == C_prod` and exact equality between the changed-path set and the six declared evidence-only paths (`design.md:589-606`). |
| The agentic suite includes slow tests | **Resolved** | Agentic config defaults to `-m 'not slow'` (`../agentic-mbse/pyproject.toml:93-100`), while its documented full-suite command is `uv run pytest tests/ -m ""` (`../agentic-mbse/CLAUDE.md:58-65`; `design.md:660-682`). A review-time full-repository collection selected 1,836 of 1,869 tests under the default and all 1,869 with the empty-marker override; `-m slow` selected the same 33 added cases. |

## Regression Guard Verification

| Finding | Result | Evidence |
|---|---|---|
| F1 — parser-owned standard-library classification | **Remains resolved** | D6 consumes SysIDE's installed `DocumentTier` member directly, refuses missing or unknown evidence, and gives names, paths, origins, and packages no classification role (`design.md:323-345`). The Revision-4 product-lens rerun keeps design-F1 fixed. |
| F2 — operational address and direct-package rule | **Remains resolved** | D2 retains exact address construction and instantiation, shared-prefix occurrence selection, direct-package no-prefix behavior, and refusal for nested no-prefix targets (`design.md:135-207`). |
| F3 — contextual calculation-output producer | **Remains resolved** | D3 retains the exact output-declaration bucket, optional exact usage filter, consumer-domain contextualization, alias collapse only for the same effective producer, and zero/multiple refusal (`design.md:209-261`). |
| F4 — one public evidence conversion boundary | **Remains resolved** | D5 keeps one public agentic error contract, and D7 routes live plus admitted/snapshot extraction through one conversion function with no compatibility overload (`design.md:280-391`). |
| F6 — B8 sequencing | **Remains resolved** | B8a is a pre-change real-corpus totality gate with anti-vacuity checks and no new error API; B8b is the post-D5 forced typed regression. D1-D4 remain blocked behind B2/B8a/B10 (`design.md:463-496,928-958`). |
| F7 — B9 fail-before-write proof | **Remains resolved** | D9 keeps the preflight before mutation, stable public diagnostic, nonzero status, and byte-for-byte output preservation proof (`design.md:409-437`). |
| F8 — general semantic owner with containment-local validation | **Remains resolved** | D1 keeps `semantic_owner` acquisition-only for every owner kind and `None`; D2 applies the closed three-kind validation only while building containment addresses and preserves attachment/formal behavior (`design.md:106-160`). |
| Second resolver or fallback architecture | **Absent** | The design changes the existing exact route in place and forbids flags, selectable resolvers, compatibility layers, and fallback election. Static tests reject the retired selection paths (`design.md:79-102,869-880`). |

## Dimensional Review

### 1. Spec Compliance

**Assessment: Pass.** Every A1-A6 and B1-B10 row has a design owner and matching proof form. The
design preserves `[HARD]` parser/declaration authority, keeps candidate enumeration as an
implementation technique rather than a fixed requirement, preserves P-002, and carries P-003/P-004
without hardening an example or dropping an owner referent. F5 now makes the immutable landing proof
executable.

### 2. Pattern Consistency

**Assessment: Pass.** The design extends the existing occurrence index, exact elaborator,
generation preflight, immutable Git identity, and current execution-pin purpose. It does not invent
a parallel framework.

### 3. Abstraction Quality

**Assessment: Pass.** `ContainmentAddress`, `ConsumerDomain`, and the producer record are private,
immutable, narrow data. Removing them would put modeled-path and contextual-producer rules back into
implicit scans and candidate selection.

### 4. Duplication Avoidance

**Assessment: Pass.** There is one semantic-owner selector, one address-instantiation operation, one
producer index, one parser-owned standard-library classification, and one public conversion
boundary. The production/evidence split assigns distinct jobs rather than duplicating identity.

### 5. Data Structure Clarity

**Assessment: Pass.** Semantic identities, scopes, addresses, producer records, production artifact
identity, and evidence identity are explicit and traceable. The six-file evidence boundary is a
closed set with an exact parent relation.

### 6. Route Safety

**Assessment: Pass.** Live and admitted/snapshot routes share the fail-closed conversion. B9 fails
before writes. Downstream verification rejects editable or sibling sources and imports outside the
recorded artifact roots.

### 7. Bets and Decisions Integrity

**Assessment: Pass.** B2, B8a, and B10 are honest kill gates with specified falsifiers and return to
design on a contrary result. B8b is correctly separated from the pre-change gate. The final
artifact topology, identity ownership, evidence coverage, suite commands, and landing order are
decisions, not hidden bets. No fallback or unresolved alternative remains.

### 8. Reader Comprehension

**Assessment: Pass.** The design states the parser-to-TEAx model before its mechanisms. A reader can
trace semantic authority, refusal ownership, occurrence derivation, test gates, and the
`C_prod` → `F_final` → `C_evidence` landing on one pass.

## Issues by Severity

### Critical

None.

### Major

None.

### Minor

None.

## Recommendations

1. Proceed to `$my-plan` and preserve the eight sequencing gates as persistent checked phases.
2. Keep the exact `C_prod`, `F_final`, `C_evidence`, six-path boundary, and slow-inclusive agentic
   command as plan-level acceptance checks.
3. Return to design if any B2/B8a/B10 kill gate produces a result outside its permitted verdict.

## Resolutions

- **F1: FIXED (remains fixed).** Direct SysIDE `DocumentTier` classification remains authoritative;
  the fresh product-lens gate is `CLEAR`.
- **F2: FIXED (remains fixed).** Exact containment-address instantiation and the direct-package rule
  remain.
- **F3: FIXED (remains fixed).** Contextual calculation-output producer resolution remains.
- **F4: FIXED (remains fixed).** One live/admitted evidence conversion boundary remains.
- **F5: FIXED.** `C_prod` is the complete and sole certified codegen production identity; Fusion's
  `F_final` pins it; direct-child `C_evidence` records `C_prod` and `F_final` through an exact
  evidence-only path set and is excluded from production identity. No record is self-referential,
  and `uv run pytest tests/ -m ""` is verified to include the slow-marked agentic tests.
- **F6: FIXED (remains fixed).** B8a is the pre-change real-corpus gate; B8b is post-D5; D1-D4 remain
  behind B2/B8a/B10.
- **F7: FIXED (remains fixed).** B9 fails before writes and proves byte preservation.
- **F8: FIXED (remains fixed).** General semantic-owner acquisition and existing attachment/formal
  behavior remain; strict owner-kind validation is containment-address-only.

## Verdict

**Overall: Approve**

Revision 4 is approved for planning. Run `$my-plan`; preserve the worktree and carry the exact
production/evidence boundaries and fail-fast probes into the persistent implementation checklist.
