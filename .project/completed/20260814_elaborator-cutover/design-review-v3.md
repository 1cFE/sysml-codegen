# Design Rereview V3: Elaborator Atomic Cutover

**Design:** `.project/active/elaborator-cutover/design.md`  
**Census:** `.project/active/elaborator-cutover/cutover-census.md`  
**Spec:** `.project/active/elaborator-cutover/spec.md`  
**Prior Review:** `.project/active/elaborator-cutover/design-review-v2.md`  
**Review File:** `.project/active/elaborator-cutover/design-review-v3.md`  
**Date:** 2026-08-10

---

## The Point

One loaded semantic source occurrence must become exactly one runtime source for every and only its
bound calculation, constraint, and aggregation consumers. Resolved referents must be consumed when
SysIDE loads the model, unsupported forms must fail before generation, and the instance graph must
carry the same answer through live and portable snapshot routes. These are the owner-originated
outcomes at `.project/backlog/epic_elaborate_first_architecture.md:61-80`.

## Fundamental Assessment

**Assessment: Concerns. The semantic architecture remains sound, but DR2-F1 is still materially
open. Planning may not proceed.**

The product-lens gate is **CLEAR**, and neither design smell fires
(`product-lens.md:56-79`). The instance graph remains the right sole authority. The corrected design
also closes the standard-library, licensed-command, and v6 API precision findings. It gives the
candidate one checker name, one record, one ID, reciprocal owner-acceptance tags, and a locally
explicit compare-and-swap journal.

The correction does not yet make the paired landing executable. It hashes evidence that must contain
the hash being computed, updates local refs while claiming control of protected remote refs, leaves
`HARD_BLOCKED` recovery without an authorized mutation, and verifies product tags only after the
tags it is supposed to gate already exist. Those contradictions are inside the DR2-F1 correction,
so reopening that finding does not reopen the instance-graph architecture.

The census also remains unproven. The spec requires mechanical closure before design approval, but
the inventory and checkers are deferred to implementation. DR2-L2 therefore remains open, and the
Fusion Tea half of DR2-L3 remains incomplete.

---

## Focused Finding Re-evaluation

| Finding | V3 status | Evidence |
|---|---|---|
| **DR2-F1 — singular paired-candidate promotion** | **Open — material** | One checker, record, ID, phase grammar, acceptance-tag pair, and workflow census are now consistently named (`design.md:199-206,675-724,726-741`; `cutover-census.md:206-230`). Candidate identity and promotion still contain the contradictions in **DR3-F1** below. |
| **DR2-L1 — standard-library unavailable outcome** | **Closed** | `SysideStandardLibraryDigestAdapter` owns the pinned SysIDE 0.8.4 document digest (`design.md:320-327`). Unavailable metadata/text is `SOURCE_STANDARD_LIBRARY_UNAVAILABLE`; stored authority mismatch remains `SnapshotCompatibilityError` (`design.md:334-342`; `cutover-census.md:119,162`). |
| **DR2-L2 — generated census evidence** | **Open — localized, but required before planning** | The census calls itself closed (`cutover-census.md:3,11-13`) while saying implementation will create the inventory (`cutover-census.md:17-19`). Its exact commands depend on planned checkers (`cutover-census.md:30-31,315`). The spec requires mechanical enumeration and closure before design approval (`spec.md:185-205`). See **DR3-L1**. |
| **DR2-L3 — F26 and Fusion Tea census residue** | **Partly closed** | F26 now has an independent literal oracle and both production/test responsibilities point to it (`design.md:814-820`; `cutover-census.md:94,150,237`). The exact fifteen Fusion Tea renames and arithmetic effects are designed (`design.md:526-564`), but their census treatment remains grouped prose (`cutover-census.md:176-195`). See **DR3-L2**. |
| **DR2-L4 — executable licensed gate** | **Closed** | The commands name existing exact codegen and agentic test nodes (`design.md:868-892`) and require exact collected/passed counts with zero skip, xfail, or deselection (`design.md:895-903`). Read-only collection confirmed the stated 2-node codegen and 3-node agentic selections. |
| **DR2-L5 — exact v6 API precision** | **Closed** | `source_roots` is exactly `collections.abc.Sequence[pathlib.Path] | None`, with explicit rejection and empty/`None` behavior (`design.md:230-247`; `cutover-census.md:115-116`). Every raw graph `source_file` must equal one manifest referent before typed decode (`design.md:373-380,439-445`). |

## Remaining Material Finding

### DR3-F1 — DR2-F1 still lacks a computable identity and an authoritative promotion/recovery route

**Severity: Major.** The local CAS mechanics are detailed, but the five-phase protocol cannot yet
produce the claimed cross-repository public state.

1. **The candidate identity has an unhandled second self-reference.** The candidate ID excludes only
   `candidate_id` and the candidate record's own path sentinel; no other byte or field is excluded
   (`design.md:681-705`). The candidate binds result artifacts (`design.md:699-705`), while the scale
   and TEAx evidence must itself bind the candidate ID (`design.md:833-836`). If that evidence carries
   the ID as specified, the ID depends on an artifact containing the ID being computed. The design
   needs one canonical preimage rule for candidate-ID fields in every bound evidence artifact, or it
   must bind those artifacts through a non-circular precursor digest.

2. **The branch CAS acts on local refs, not the protected public refs claimed later.** The exact phase
   inputs are filesystem paths to two repositories and a local state directory
   (`design.md:728-741`). `promote-branches` uses `git update-ref` in those repositories
   (`design.md:754-762`). The later guarantee concerns protected branches, a promotion service
   identity, and `.github` workflows (`design.md:782-788`; `cutover-census.md:218-223`). No phase
   fetches an authoritative remote state, performs a remote compare-and-swap push/API update, or
   declares the supplied repositories to be the authoritative bare repositories. A local
   `BRANCHES_PROMOTED` journal can therefore succeed without advancing either protected public
   branch.

3. **`HARD_BLOCKED` recovery requires an out-of-contract mutation.** The accepted CLI has only
   `prepare`, `verify`, `promote-branches`, `verify-tags`, and `verify-release`
   (`design.md:728-741`). `verify` may clear a hard block only after both refs have already been
   restored to their bases or both prepared commits (`design.md:749-753`), while the hard block
   prevents later gates and only the promotion service may update protected refs
   (`design.md:771-775,782-784`). No phase owns the CAS repair that creates either allowed recovered
   state or states whether recovery records `VERIFIED`, `ROLLED_BACK`, or `BRANCHES_PROMOTED`.

4. **The product-tag gate is post-publication rather than a defined publication protocol.**
   `verify-tags` requires both product tag refs to exist (`design.md:763-766`), while product-tag
   workflows are required to run `verify-tags` (`design.md:785-787`; `cutover-census.md:220-221`).
   The design never stages, publishes, rolls back, or hard-blocks the two product tags. If the
   workflow is triggered by tag creation, one tag can already be public before the paired check; if
   it is meant to run before creation, its required inputs do not exist.

**Bounded correction:** keep the singular record and acceptance-tag scheme. Define a non-circular
evidence preimage, identify the authoritative ref store, and make every branch/tag mutation an exact
remote or authoritative-bare-repository CAS under one coordinator. Add an explicit recovery
transition for each `HARD_BLOCKED` observable state and a staged product-tag publication/rollback
contract. The tests already named by `CUT-PROMO-01/02/03` can remain the proof owners
(`cutover-census.md:74-76`).

## Remaining Localized Findings

### DR3-L1 — DR2-L2 has not produced the closed inventory it claims

The required `cutover-inventory.json`, `scripts/check_cutover_census.py`, and
`scripts/check_cutover_residue.py` are still planned rather than attached evidence. The current
census explicitly defers inventory creation to implementation (`cutover-census.md:17-19`), although
R6 requires the population to be mechanically enumerated and closed before design approval
(`spec.md:185-205`). The checker commands are listed (`cutover-census.md:30-31,315`), but the script
census owns only the candidate coordinator as `SCR-06` (`cutover-census.md:197-206`).

The prior confirmed omissions remain absent from the literal affected-test rows: eight test files
and the two arithmetic goldens named by V2 (`design-review-v2.md:190-198`) do not appear in
`TEST-01` through `TEST-07` (`cutover-census.md:232-243`). This is localized only if exact-set
generation reveals no new disposition.

**Bounded correction:** generate and attach the inventory now, census both checker scripts, add
stable child rows for every discovered omitted test/golden/caller, and run exact equality plus every
self-safe residue gate. Escalate only if that run exposes a new keep/delete/migrate decision.

### DR3-L2 — DR2-L3 closes F26 but not exact Fusion Tea census ownership

F26 is closed. `CUT-F26-01` pins the group, four public keys, alias tuple, and constraint ID without
the legacy builder (`design.md:814-820`), and the production/test rows now cite it
(`cutover-census.md:150,237`).

Fusion Tea remains grouped below the census's own stable-row standard. The design names the fifteen
old-to-final bindings and the affected arithmetic records (`design.md:526-564`), but `FIX-01` records
file groups and counts rather than stable `kind=golden` rows and old-to-final generated field/caller
rows (`cutover-census.md:176-195`). That does not yet meet the inventory schema's unique
repository/path/symbol/responsibility contract (`cutover-census.md:34-47`) or R9's requirement to
record every generated-name and test consequence (`spec.md:258-266`).

**Bounded correction:** add stable rows for both arithmetic golden files and each distinct generated
field/direct caller consequence, carrying its old name, final name, owner, and independent oracle.

---

## Dimensional Review

### 1. Spec Compliance
**Assessment: Fail.** DR2-F1 cannot enforce one accepted public landing, and R6 closure evidence is
still deferred beyond design approval.

### 2. Pattern Consistency
**Assessment: Concerns.** The semantic code path follows the exact-ID pattern. The promotion path
mixes local Git refs with remote protected-branch claims without naming the authority boundary.

### 3. Abstraction Quality
**Assessment: Concerns.** One coordinator and one journal are appropriate. Their state machine needs
explicit identity-preimage, recovery, remote-ref, and product-tag transitions before the abstraction
earns its claimed guarantee.

### 4. Duplication Avoidance
**Assessment: Pass.** No second semantic graph, QN association route, candidate checker, or candidate
record is proposed.

### 5. Data Structure Clarity
**Assessment: Concerns.** The v6 schema is exact. The candidate's evidence self-reference and the
missing generated census rows leave two data contracts incomplete.

### 6. Route Safety
**Assessment: Fail.** Local branch updates can pass without public remote promotion; hard-block and
product-tag routes require mutations the accepted protocol does not own.

### 7. Bets & Decisions Integrity
**Assessment: Concerns.** The remaining hidden bets are that local refs stand in for protected public
refs and that evidence can contain the digest that binds it. Neither is true without another
mechanism.

### 8. Reader Comprehension
**Assessment: Concerns.** The semantic design is clear. An implementer must still invent the
authoritative ref store, evidence preimage, hard-block recovery transition, and tag publication
sequence.

---

## Issues by Severity

### Critical

- None.

### Major

- **DR3-F1 / DR2-F1 remains open:** candidate evidence identity is circular, and the local
  branch/tag/recovery state machine does not control the protected public refs it claims to gate.

### Minor — localized objective corrections

- **DR3-L1 / DR2-L2 remains open:** the mechanically closed inventory and residue evidence have not
  been generated, and confirmed omitted rows remain uncensused.
- **DR3-L2 / DR2-L3 partly open:** F26 is closed; exact Fusion Tea golden/generated-caller rows are
  still missing.

## Recommendations

1. Correct DR3-F1 without changing the instance-graph architecture or weakening the paired landing
   guarantee.
2. Generate the census inventory and exact-set result before claiming design closure.
3. Add the bounded Fusion Tea child rows, then run one focused V4 rereview of DR3-F1, DR3-L1, and
   DR3-L2 only.

## Resolutions

None recorded. This was a focused, non-interactive third review. The reviewer did not modify
`design.md`, `cutover-census.md`, `spec.md`, or production code.

---

**Overall: Revise**

**Next Steps:** Return this review to the design author. Planning may not proceed until DR3-F1 is
closed and the generated census proves that DR3-L1/DR3-L2 introduce no new disposition. Do not
reopen DR2-L1, DR2-L4, DR2-L5, the instance-graph architecture, source-admission design, Fusion Tea
topology, or F26 literal oracle unless the correction creates new contradictory evidence.
