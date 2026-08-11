# Design Rereview V2: Elaborator Atomic Cutover

**Design:** `.project/active/elaborator-cutover/design.md`  
**Census:** `.project/active/elaborator-cutover/cutover-census.md`  
**Spec:** `.project/active/elaborator-cutover/spec.md`  
**Prior Review:** `.project/active/elaborator-cutover/design-review.md`  
**Review File:** `.project/active/elaborator-cutover/design-review-v2.md`  
**Date:** 2026-08-10

---

## The Point

One loaded semantic source occurrence must become exactly one runtime source for every and only its
bound calculation, constraint, and aggregation consumers. Public mutation must reach every intended
consumer and no independent source. Resolved referents must be consumed when SysIDE loads the model,
unsupported forms must fail before generation, and the instance graph must carry the same answer
through live and portable snapshot routes. These are owner-originated outcomes at
`.project/backlog/epic_elaborate_first_architecture.md:61-80`.

## Fundamental Assessment

**Assessment: Concerns. The architecture is sound, but one material release-contract gap remains.**

This remains the right piece of work and the right overall approach. The revised design now gives
the instance graph one explicit lifetime owner, admits exact staged source bytes, removes the
qualified-name association route, and binds owner acceptance to a content-addressed paired
candidate. The product-lens gate is **CLEAR**. Neither design smell fired: staged admission and
receipt verification own guarantees that SysIDE and a mutable projected graph do not provide, and
the design explicitly records each invariant-ownership change.

Material findings **DR-F1, DR-F2, and DR-F3 are closed**. DR-F4 is only partly closed. Its candidate
identity binds the right content, but the branch/merge/tag/release enforcement remains an assertion
rather than one executable cross-repository phase contract. The design names the wrong checker,
does not census the checker or workflow callers, alternates between one paired candidate ID and two
candidate IDs, and does not define how each phase obtains and verifies the reciprocal repository
state or prevents one-sided promotion.

That gap affects the atomic landing contract, not presentation or test bookkeeping. The verdict is
therefore **Revise**. The design does not need reshaping from first principles. It needs a focused
DR-F4 correction and rereview. The remaining DR-F5–DR-F9 residues are localized and objectively
checkable; they do not independently justify Revise.

---

## DR-F1–DR-F9 Closure

| Finding | Status | Rereview basis |
|---|---|---|
| **DR-F1 — one `PipelineContext` authority** | **Closed** | Direct public construction is rejected; the context privately stores only canonical instance bytes, canonical selection, and a projection receipt. Every graph view is freshly decoded and projected, mutation cannot persist, the receipt binds instance fingerprint, targets, `include_all`, projector marker, and the full computation digest, and certifying generation verifies at entry and before sealing (`design.md:220-274`; `cutover-census.md:71-73,108-109,168`). There is no retained graph pair to mismatch. |
| **DR-F2 — exact admitted source bytes and set** | **Closed; one localized typed-failure addition** | One staged admission owner fixes roots, overlap ownership, symlink/case/NFC policy, file set, logical referents, before/after file identity, staged hashes, exact SysIDE user-document equality, external-import policy, additions/removals, freshness, relocation, and failure order (`design.md:284-331,408-458`). The standard-library compatibility surface is feasible; the bounded probe below closes the remaining premise check. Add a named standard-library-unavailable admission code, but no architecture change is needed. |
| **DR-F3 — QN association dual** | **Closed** | D10 unconditionally promotes identified extraction/profile/compiler cores to the unsuffixed APIs and deletes the transitional names, QN candidate selector, QN definition map, exports, and callers. Validation levels 4 and 6 consume `item.decision`; preflight accepts an already-decided exact result and cannot associate candidates (`design.md:185-193,558-565`; `cutover-census.md:165-167,284,287`). |
| **DR-F4 — immutable paired candidate and atomic gates** | **Not closed — material** | The candidate record and acceptance invalidation are strong, but phase enforcement is incomplete. See **DR2-F1** below (`design.md:653-694,739`; census omission). |
| **DR-F5 — normative v6 schema and bumps** | **Closed in substance; localized precision residue** | The revised design gives exact nested keys, types, enums, cardinality, ordering, duplicate/unknown-key rules, canonicalization, nested and outer digests, fixed validation order, and explicit format/graph/IR/profile/projector bump rules (`design.md:333-433`). Specify the exact public `source_roots` type and require every graph `source_file` referent to name a `sources.files` row. Neither changes marker ownership. |
| **DR-F6 — exact census and no residue** | **Not yet objectively closed; localized correction** | The inventory schema and exact-set checker contract are specified (`cutover-census.md:15-54`), but `cutover-inventory.json`, `scripts/check_cutover_census.py`, and `scripts/check_cutover_residue.py` do not exist, so the claimed comparison has not run. The confirmed omitted callers/tests/goldens from the first review are still absent from the literal member lists, `TEST-07` remains a catch-all, and NR-01/NR-09 still do not name one executable self-safe check (`cutover-census.md:208-214,273-291`). Generate and attach the inventory, expand stable child rows, and run exact equality. This remains localized only while that process exposes no new keep/delete/migrate decision. |
| **DR-F7 — independent F26 oracle** | **Closed; stale cross-reference residue** | `CUT-F26-01` now pins the literal `wi014_toy` group, four source keys, alias tuple, and constraint ID without importing the old builder (`design.md:720-726`; `cutover-census.md:91`). Route parity and absence remain separate. Update `PROD-02` and `TEST-02`, which still describe F26 as only `CUT-V6-03` plus absence (`cutover-census.md:147,209`). |
| **DR-F8 — Fusion Tea fallout and separate proofs** | **Closed in substance; localized census residue** | The exact 15 renames, formal/expression changes, 15-record and 3-record arithmetic-golden fallout, direct generated calls, stable module/schema/output/source identities, and separate C25, C2, C19, arithmetic, and real-TEAx proofs are explicit (`design.md:505-556,711-726`; `cutover-census.md:85,94-99,173-192`). Persist the two golden files and every old/final generated input/caller consequence as exact inventory/census rows instead of grouped prose. |
| **DR-F9 — timing, execution, license, Ruff, mypy** | **Closed except one invalid licensed command** | Public capture timing wraps the complete stock call; TEAx interpreter/path/SHA/state, execution collection and pass counts, repository commands, and identity-based Ruff/mypy baseline comparison are exact (`design.md:728-800`). The agentic licensed command names two nonexistent test files and neither repository registers a `licensed` pytest marker. Replace it with real exact test nodes and zero-skip assertions, or add and census the intended marked tests. No threshold or repository-scope change is needed. |

The accepted-batch population is exact. `B37-01` through `B37-37` match the Item-5 ledger
path-for-path and classify **14 v6 graphs, 22 capture refusals, and one non-R7 no-calculation control**
with no 38th row (`cutover-census.md:219-271`). C19 remains a separate focused proof as required.

### Bounded standard-library compatibility probe

The pinned environment contains SysIDE `0.8.4`. Its exported `Environment.get_default()` surface
provides the environment document mutexes; each document exposes URL, language, and text. A
read-only probe sorted 94 `(portable-name, language, UTF-8 text)` rows and produced SHA-256
`ada7a0818f72e95f3953e46592bec91026bbd954efda251decc35d4036272f67`. Repeating the probe with
`SYSIDE_LICENSE_KEY` unset produced the same count and digest.

This validates the design premise at `design.md:313-314,344-345,420-421`: the loader can reproduce
the pinned standard-library authority without loading a user model or requiring a license. The
implementation should give that adapter one named owner and map an unavailable or unreadable
environment to a closed typed admission/compatibility failure before graph decode. The existing
`SnapshotCompatibilityError` already owns digest mismatch; adding a precise live/capture admission
code is a localized correction.

---

## Dimensional Review

### 1. Spec Compliance

**Assessment: Fail**

The semantic and snapshot contracts are now implementable, and DR-F1–DR-F3 are closed. DR-F4 still
does not mechanically enforce the spec's one atomic shipped authority across both repositories.
The missing generated inventory and invalid licensed command are concrete local failures, but they
do not change the verdict because DR2-F1 already requires design revision.

Capture fidelity is preserved. Owner outcomes remain distinct from agent-authored cutover strategy,
the maintained Fusion Tea referent and arithmetic payload survives, and no challengeable inferred
mechanism is silently promoted to an owner-settled requirement.

### 2. Pattern Consistency

**Assessment: Concerns**

The code architecture now follows the certified exact-ID pattern: typed identity inside, rendered
names at projection, and one downstream computation plan. The remaining inconsistency is workflow
level. Content addressing is precise, while promotion is still described as a coordinated action
without a correspondingly precise coordinator and phase contract.

### 3. Abstraction Quality

**Assessment: Pass**

The narrow context, projection receipt, staged admission record, v6 envelope, and single exact
agentic decision core each own one necessary invariant. Removing any of them would reopen a prior
finding. The design avoids another graph, registry, resolver, or compatibility adapter.

### 4. Duplication Avoidance

**Assessment: Pass**

There is no retained semantic graph pair or QN association path. Inner and outer snapshot digests
have explicit nested scopes rather than competing ownership. Historical dual-run evidence remains
history and no executable comparator survives the final state.

### 5. Data Structure Clarity

**Assessment: Concerns**

The v6 schema and candidate content model are explicit. The remaining clarity problems are local:
the exact `source_roots` public type, graph-to-source referent cross-check, absent generated census
inventory, and singular/plural candidate wording.

### 6. Route Safety

**Assessment: Concerns**

Live, capture, in-place v6, and relocated v6 share admission, graph validation, selection, and
projection. Standard-library validation is reproducible without a license. Repository promotion is
the unsafe route: the design does not yet state how a branch, proposed merge tree, tag, or release
obtains and verifies the reciprocal repository ref or prevents one side from advancing alone.

### 7. Bets & Decisions Integrity

**Assessment: Concerns**

The graph, source, and standard-library bets now have evidence and falsifiers. The remaining hidden
bet is that saying CI invokes a checker and candidates are promoted as a pair is enough to create a
two-repository atomic gate. It is not. The design must either name a real promotion coordinator and
its phase-specific checks or narrow the contract to tag/release atomicity through an authorized spec
change.

### 8. Reader Comprehension

**Assessment: Concerns**

The semantic architecture is clear in one pass. The candidate section is not yet a buildable mental
model because one paired candidate ID becomes plural and the phase argument has no defined phase
semantics. The implementer would still have to choose the cross-repository enforcement mechanism.

---

## Issues by Severity

### Critical

- None.

### Major — design author must address

- **DR2-F1 — Paired-candidate promotion is not an executable atomic gate.** The singular
  `elaborator-cutover-candidate/v1` record correctly binds both repositories, every accepted corpus
  and evidence byte, contracts, commands, environment, and TEAx state. Acceptance correctly cites
  its digest and any bound change creates a new ID (`design.md:653-677`). But the only command names
  `scripts/check_cutover_release.py`, while the required canonical checker is
  `scripts/check_cutover_candidate.py`; neither checker nor the CI workflows has a census row. The
  design does not define the phase-specific algorithm for trusted reciprocal checkout/ref
  acquisition, candidate and proposed-merge-tree verification, required branch checks, tag/release
  ref verification, or coordinated promotion. “CI invokes it” and “promoted ... as a pair” do not
  prevent one repository from advancing alone (`design.md:679-694`).

  **Required correction:** define one checker name and one singular paired candidate/acceptance
  schema. Specify exact `branch`, `merge`, `tag`, and `release` inputs and invariants. Census the
  checker, its tests, and each workflow caller. Define the coordinator or protected-ref protocol
  that obtains both exact candidates, verifies both base-to-candidate patches and resulting trees,
  verifies every bound artifact/evidence byte, rejects any changed ID, and prevents or recovers a
  one-sided promotion. If the intended guarantee is only release atomicity because two Git merges
  cannot be transactional, amend the design/spec claim explicitly and rereview that decision.

### Minor — localized objective corrections

- **DR2-L1 — Standard-library unavailable outcome.** Name the SysIDE 0.8.4 environment-digest
  adapter and add a precise typed failure for an unavailable/unreadable standard library. Digest
  mismatch already maps to `SnapshotCompatibilityError`.
- **DR2-L2 — Census evidence is not generated.** Produce `cutover-inventory.json`, add every
  confirmed omitted caller/test/golden as a stable row or child row, and make the exact-set and
  residue checkers self-safe and executable. The confirmed set includes
  `test_catalog_definition_join.py`, `test_occurrence_roundtrip_parity.py`,
  `test_constraint_catalog_determinism.py`, `test_diagnostic_screen.py`,
  `test_factory_calc_usage.py`, `test_sanitize_invariance.py`,
  `test_hygiene_tail_agg_compile.py`, `test_matcher_fixes_item7.py`,
  `calc_def_compilation_golden.json`, and `calc_compat_parity_golden.json`. If inventory generation
  reveals a new disposition, escalate it back to design review.
- **DR2-L3 — F26/Fusion Tea census residue.** Point every F26 responsibility to `CUT-F26-01` and
  persist the two arithmetic goldens plus old/final generated field and direct-caller rows.
- **DR2-L4 — Invalid licensed gate.** Replace the nonexistent agentic test paths and unregistered
  `licensed` marker with an exact selection that collects at least one intended live test and fails
  on skip, xfail, or deselection. The invalid paths are
  `tests/test_validation/levels/test_level4_constraints.py` and
  `tests/test_validation/levels/test_level6_architecture.py` (`design.md:783-790`).
- **DR2-L5 — V6 API precision.** State the exact `source_roots` type and validate every graph
  `source_file` referent against `sources.files`.

---

## Recommendations

1. Return to the design author for DR2-F1 only. Keep the content-addressed candidate schema; finish
   the enforcement protocol around it.
2. Rerun a focused design review of the revised candidate checker and phase gates. A full
   architecture rereview is unnecessary unless the guarantee is weakened or another repository is
   added.
3. Apply DR2-L1 through DR2-L5 as objective corrections and record their exact checker results.
4. Proceed to planning only after DR2-F1 passes rereview and the generated census exposes no new
   disposition.

## Resolutions

None recorded. This was a fresh, non-interactive rereview. The reviewer modified only this review
artifact and did not edit the design, census, spec, product-lens ledger, or production code.

---

**Overall: Revise**

**Next Steps:** A design-author revision and focused DR-F4 rereview are still required. Planning may
proceed after that material gate is closed and the localized objective corrections pass. The
instance-graph architecture, staged admission approach, QN-core convergence, v6 schema direction,
Fusion Tea migration, and 37-path population do not need to be reopened.
