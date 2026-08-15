# Design Rereview V4: Elaborator Atomic Cutover

**Design:** `.project/active/elaborator-cutover/design.md`  
**Census:** `.project/active/elaborator-cutover/cutover-census.md`  
**Inventory:** `.project/active/elaborator-cutover/cutover-inventory.json`  
**Prior Review:** `.project/active/elaborator-cutover/design-review-v3.md`  
**Review File:** `.project/active/elaborator-cutover/design-review-v4.md`  
**Date:** 2026-08-10

---

## The Point

One loaded semantic source occurrence must become exactly one runtime source for every and only its
bound calculation, constraint, and aggregation consumers. Resolved referents must survive the live
and portable snapshot routes, unsupported forms must fail before generation, and the resolved
instance graph must be the sole shipped semantic authority. This rereview does not reopen that
architecture. It checks only whether the V3 corrections make the paired landing and its census
evidence executable.

## Scope

Only **DR3-F1**, **DR3-L1**, and **DR3-L2** were re-evaluated, as required. V3's closed findings and
the instance-graph architecture were not reopened. The corrections create no direct contradictory
evidence against them. The V3 product-lens result therefore remains controlling and clear
(`design-review-v3.md:20-35`).

## Fundamental Assessment

**Assessment: Pass. The three V3 findings are closed. Planning may proceed.**

The candidate identity now has a finite, deterministic preimage. The promotion protocol now acts on
the two actual GitHub origins with remote compare-and-swap, explicit protected-ref prerequisites,
one authorized hard-block recovery phase, and a staged paired product-tag protocol. The checked-in
census evidence is current for both dirty worktrees, states its comparison limit honestly, and
closes the exact affected set mechanically. The Fusion Tea consequences now have stable child rows.

---

## Focused Finding Re-evaluation

| Finding | V4 status | Evidence |
|---|---|---|
| **DR3-F1 — computable identity and authoritative promotion/recovery route** | **Closed** | The record-self and evidence-template preimages are explicit and reversible (`design.md:676-725`). GitHub origins are authoritative, local refs are preparation-only, all public branch/product-tag changes are remote leased updates, recovery is an accepted phase, and verification is read-only (`design.md:701-745,749-839`). |
| **DR3-L1 — generated closed inventory** | **Closed** | Both checkers and their tests are censused (`cutover-census.md:101-155,3493-3504`; `cutover-inventory.json:692-724,3412-3444`). Current evidence independently recomputes to two dirty repositories, 78 discovered paths, and 231 current sorted rows; compare and both bounded residue checks pass. |
| **DR3-L2 — exact Fusion Tea census ownership** | **Closed** | The census has `FTGEN-01` through `FTGEN-15`, each with the maintained owner or direct caller, exact old-to-final field, and independent oracle (`cutover-census.md:3475-3491`). `GOLDEN-01` and `GOLDEN-02` separately own both arithmetic files and their controls (`cutover-census.md:3583-3584`). |

## DR3-F1 Verification

### Candidate identity is computable

- The candidate record omits `candidate_id`, replaces only its own path row with the declared
  `candidate-self-excluded/v1` sentinel, and hashes the resulting canonical payload
  (`design.md:676-686`).
- Every ID-bearing JSON evidence artifact starts as a schema-declared template. The record binds its
  template hash and complete JSON-pointer set using `hash_kind:"evidence-template"`; ordinary
  evidence remains final-byte-hashed (`design.md:688-693`).
- Materialization replaces only declared sentinels. Verification reverses those exact pointers,
  rejects undeclared candidate-ID occurrences, and rechecks the template hash. The materialized byte
  hash is journal evidence and is explicitly excluded from the candidate-ID input
  (`design.md:695-699`). Results likewise cannot bind an ID-bearing materialized final-byte hash
  (`design.md:715-725`). There is therefore no final-byte hash cycle.

### Public authority and mutations are explicit

- The two exact authoritative origins are
  `https://github.com/1cFE/sysml-codegen.git` and
  `https://github.com/1cFE/agentic-mbse.git`; local repositories and worktrees are preparation inputs
  only (`design.md:701-714`). Hidden prepared refs are local-only and do not advance a public branch
  (`design.md:727-736`). Owner acceptance tags are published to those origins by missing-ref CAS
  (`design.md:738-745`).
- Before `prepare`, both repositories must install branch and tag rulesets. The promotion App is the
  only branch/product-tag writer; direct push, deletion, force update, and ordinary merge are
  forbidden, while the owner-only acceptance namespace is immutable (`design.md:832-839`).
- `prepare` freshly reads both origins. `promote-branches` performs exact remote
  `--force-with-lease` updates, records the observed expected OID, push result, and returned
  `ls-remote` OID, and compensates the first origin by an inverse remote lease if the second fails
  (`design.md:771-790`). The canonical journal covers acceptance/product tag object IDs, every fresh
  authoritative observation, push return, compensation, error, and transition (`design.md:820-825`).

### Recovery and paired product tags are complete

- `verify` is read-only: it may fetch objects and emit a result, but it changes no ref or journal
  state and cannot clear a hard block (`design.md:777-781`).
- `recover-hard-block` is the sole authorized repair mutation. It permits only bound base/prepared
  branch OIDs or missing/exact staged product-tag OIDs, has exact paired terminal states, compensates
  a failed second update, and refuses foreign or ambiguous state without mutation
  (`design.md:791-801`).
- `publish-tags` constructs the exact annotated objects locally, journals `TAGS_STAGED`, publishes
  each protected remote tag by missing-ref lease, compensates the first by a leased deletion, and
  records rollback, hard-block, or paired publication. `verify-tags` and `verify-release` are then
  read-only and reject missing, one-sided, foreign, or hard-blocked state
  (`design.md:802-818`).

DR3-F1 is closed without weakening the logical-atomic landing guarantee and without changing the
instance-graph architecture.

## DR3-L1 Verification

The census states the evidence boundary accurately: it was generated from the certified dirty
current worktrees, uses `comparison_basis:"current-worktree"` and
`exact_base_comparison:false`, proves current affected paths and byte identities, and does not claim
a clean-base comparison (`cutover-census.md:15-21`). The inventory records both repositories as
dirty, with exact HEAD and dirty-state digests (`cutover-inventory.json:10-26`). Existing inventory
rows bind their current bytes; planned/runtime rows remain visibly non-present. The scanner and
compare contracts are deterministic and exact-set based (`scripts/check_cutover_census.py:138-224,
233-280`).

The residue checker has a closed 23-term encoded vocabulary, omits its own checker/test filenames,
uses Python AST symbols plus bounded non-Python text scanning, and accepts transitional hits only
when their path has an existing `delete` or `migrate` inventory row
(`scripts/check_cutover_residue.py:18-18,461-473,493-578`). The census correctly labels the 363/5
results as inventoried transitional evidence, not final absence; the implementation candidate must
rerun with `--expect absent` and obtain zero (`cutover-census.md:65-70,3647-3666`).

### Focused command results

```text
.venv/bin/python scripts/check_cutover_census.py compare \
  --census .project/active/elaborator-cutover/cutover-census.md \
  --inventory .project/active/elaborator-cutover/cutover-inventory.json \
  --require-sorted --require-closed
{"closed": true, "rows": 231, "sorted": true}

Read-only independent recomputation of generated metadata, both repository states,
all derived row hashes/sizes/states, sorted keys, and marker discovery:
{"derived_rows_current": true, "dirty_repositories": 2, "discovered": 78, "rows": 231, "sorted": true}

.venv/bin/python scripts/check_cutover_residue.py --repo codegen=. \
  --repo agentic=../agentic-mbse \
  --inventory .project/active/elaborator-cutover/cutover-inventory.json \
  --rule all --expect inventoried
{"expect": "inventoried", "hits": 363, "rule": "all"}

.venv/bin/python scripts/check_cutover_residue.py --repo codegen=. \
  --repo agentic=../agentic-mbse \
  --inventory .project/active/elaborator-cutover/cutover-inventory.json \
  --rule item6-dual-2 --expect inventoried
{"expect": "inventoried", "hits": 5, "rule": "item6-dual-2"}

Read-only reconstruction of every encoded residue term against the checker source:
{'encoded_rules': 23, 'plain_self_matches': 0}

.venv/bin/python -m pytest -o addopts='' \
  tests/unit/test_check_cutover_census.py \
  tests/unit/test_check_cutover_residue.py -q
....                                                                     [100%]
4 passed in 0.35s
```

DR3-L1 is closed. The current 363/5 counts do not claim final deletion; they prove that the bounded
current residue is fully inventoried before implementation.

## DR3-L2 Verification

The design still fixes the exact fifteen model bindings and their final names (`design.md:527-546`).
It separately identifies the two arithmetic files, their affected records and unchanged controls,
and the direct runtime calls (`design.md:548-565`). The correction now projects those obligations
into stable census children:

- `FTGEN-01` through `FTGEN-15` each name the maintained analysis owner, exact generated field or
  direct-call consequence, old-to-final name, and independent oracle
  (`cutover-census.md:3475-3491`).
- `GOLDEN-01` owns the fifteen affected compilation records. `GOLDEN-02` owns the three changed
  parity records and the unchanged `lcoe`, `gamma`, and `f_recirc` controls
  (`cutover-census.md:3583-3584`).
- The generated inventory binds the three maintained analysis files, the direct runtime caller, and
  both golden bytes as current `migrate` rows (`cutover-inventory.json:2681-2730,2766-2798,
  3344-3359`).

The focused stable-row query returned exactly fifteen `FTGEN-*` rows and two `GOLDEN-*` rows. DR3-L2
is closed.

---

## Dimensional Impact of This Rereview

- **Spec Compliance: Pass in scope.** The paired public landing and pre-planning R6/R9 evidence that
  failed V3 now have executable contracts and current mechanical proof.
- **Data Structure Clarity: Pass in scope.** Candidate self-reference, evidence-template hashing,
  inventory rows, and Fusion Tea child identities now have finite and explicit schemas.
- **Route Safety: Pass in scope.** All public mutations are authoritative remote CAS operations;
  verification is read-only; hard blocks have one authorized repair phase; product tags cannot pass
  one-sided.
- **Bets and Decisions Integrity: Pass in scope.** The prior hidden bets that local refs stood in for
  public refs and that evidence could hash its own final bytes have been removed.
- **Reader Comprehension: Pass in scope.** An implementer no longer needs to invent the preimage,
  authority boundary, recovery route, tag sequence, or census closure method.

No other dimension or closed finding was re-evaluated.

## Issues by Severity

### Critical

- None.

### Major

- None.

### Minor

- None within the required V4 scope.

## Resolutions

- **DR3-F1:** Closed by the schema-declared candidate/evidence preimage and the authoritative remote
  branch/tag CAS, recovery, and verification protocol.
- **DR3-L1:** Closed by the checked-in current-worktree inventory, exact 231-row comparison, censused
  checkers/tests, bounded self-safe residue results, and 4/4 focused unit tests.
- **DR3-L2:** Closed by the fifteen stable generated/caller rows and two stable arithmetic-golden
  rows with named owners and independent oracles.

---

**Overall: Pass**

**Planning may proceed: Yes.** The next pipeline stage may run `$my-plan`. This rereview changed only
`design-review-v4.md`; it did not edit the design, census, inventory, scripts, tests, or code.
