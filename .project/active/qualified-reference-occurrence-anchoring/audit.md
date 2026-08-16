# Audit: Exact Owner Anchoring for Usage-Owned One-Segment References

**Verdict:** Needs Work — scoped re-verification closes findings **1 and 6** and reopened finding
**5** on incomplete census evidence. That census was repaired on 2026-08-16 and now reports 770
observed leaves, 0 absent, with 15 roots named as residual unmeasured population; the repair awaits
re-verification. Findings 2, 3, 4, and 7 were outside this pass. See
[Scoped re-verification](#scoped-re-verification--2026-08-16-remediation-c2fa657) and
[Finding 5 repair](#finding-5-repair--2026-08-16-census-corrected-at-the-resolver-boundary).
**Audited:** 2026-08-15; independently re-audited, remediated, and scoped-reverified 2026-08-16
**Branch:** main
**Commit:** remediation `c2fa657` (core repair `98970c9`)
**Verification note:** the scoped pass re-ran the focused/full suites, current and historical corpus
captures, destructive comparator controls, focused quality checks, and the retained census under
the licensed environment. Snapshot reassessment was outside this pass. The superseded body retains
the 2026-08-15 audit's earlier experiments.

**Supersession note:** the 2026-08-15 audit record is retained below for traceability, but its
Certify verdict and its claims of 153-root identity coverage and complete shared-lane evidence are
superseded by the independent re-audit in the next section.

---

## Independent re-audit — 2026-08-16

### Outcome

**Needs Work for certification evidence.** The production resolver repair matches the design and
the exercised runtime behavior is sound. The certification does not hold as written because two
success criteria were checked using evidence that does not cover what the artifacts claim.

The independent product-lens gate is **DISPOSED**, not CLEAR. Its finding is lower than owner grade,
so it does not block the repair. It does need an explicit close disposition or a bounded follow-up.
See `product-lens.md`, `independent-audit-F1`.

### Findings

1. **High — SC12's 153-root identity proof only captured 13 roots.**
   `verification/corpus_compare.py:507` calls `capture_root(..., with_identity=False)` for all 140
   frozen corpus roots and enables identity only for the 13 promoted roots at `:508`.
   `verification/adjudicate.py:53-54,98-104` maps each missing block to `None`, compares
   `None == None`, and reports those roots as compared. The ledgers contain 13 `identity` blocks,
   not 153. This falsifies the byte-exact claims in `plan.md`, `verification/README.md`,
   `verification/adjudication.md`, and the original audit. SC12 is reopened until before/after
   identities are captured for the 140 frozen roots and compared without treating absence as
   evidence.

2. **High — SC1 was marked met while one shared resolver lane remains unevidenced.** Deep literal
   overrides call the shared resolver at `src/sysml_codegen/elaboration/elaborate.py:1032-1052`.
   D11 found no authorable one-segment affected shape, and the retained verifier measures zero such
   sites. The owner explicitly allowed the run to continue with that named gap; that disposition did
   not create acceptance evidence for the lane. The original audit nevertheless says the combined
   fixture covers all six lanes and checks SC1. It does not cover deep override. SC1 is reopened;
   close must either obtain the reserved owner disposition or add discriminating evidence.

3. **Medium — arrayed aggregation exposes a user-visible cardinality split.** The repair forces
   `plural=False` in `elaborate.py:2320-2331`. A licensed paired probe found that, for
   `comp_a : Component[2]`, `sum(comp_a::length)` refuses with `SI_OCCURRENCE_AMBIGUOUS` and no
   inputs, while `sum(comp_a.length)` yields two exact-owner inputs and no diagnostic. The kept sum
   test uses a scalar owner, so forwarding `plural=True` would still return one edge and the test
   would stay green. Preserving scalar direct-reference policy was an explicit design decision, so
   this is not an unapproved implementation deviation. It is still a product inconsistency and
   fires product-lens smells 3 and 6. Carry `independent-audit-F1` to close and give it a named
   disposition or bounded follow-up.

4. **Medium — the close documentation obligation is still open and internally contradictory.**
   `.project/active/self-binding-replacement/spec.md:53-59` says the shipped resolver honors the
   exact owner; its `[HARD]` requirement at `:132-139` says the current resolver still selects by
   consumer position. The anchoring spec's SC14 remains unchecked. This does not invalidate the
   runtime repair, but the item is not close-ready.

5. **Low — an absent live leaf fails open, and the verifier shares the blind spot.**
   `_resolve_direct_reference` falls back to `_resolve_leaf` when `_elements` lacks the exact leaf
   (`elaborate.py:2314-2317`). The corpus verifier excludes the same shape at
   `verification/corpus_compare.py:220-223`. A fresh scan of 138 loadable retained roots found zero
   such one-segment facts, so this is latent rather than demonstrated. Make the absence explicit or
   keep a test if a legal authored shape is found.

6. **Low — two fail-closed edges are weakly pinned.** The arrayed strict/lenient test compares only
   diagnostic codes (`test_elaboration_fail_closed.py:215-225`), although the design asks for the
   full consumer/parameter/detail tuple. The selected-owner-but-missing-leaf-target error at
   `elaborate.py:2335-2341` has no kept test.

7. **Low — retained captures omit the editable companion revision.** The run depends on the sibling
   `agentic-mbse` checkout, but the ledger does not record its commit. Reproduction today used the
   clean checkout at `1decd9525888`; historical provenance is incomplete.

### Independent verification

- Focused licensed suite: **114 passed**.
- Full licensed suite: **17 failed, 2143 passed, 34 skipped, 88 deselected**. Re-running the 17
  failures confirmed the exact three files and the same missing-`pandas` cause.
- Fresh `after.json`: byte-identical to the retained file. Adjudication still reports 19 changed
  outcomes and zero edge/refusal drift; its identity total is the evidence bug described above.
- Fresh absent-leaf census: 138 loadable roots, zero one-segment facts absent from `_elements`.
- Focused Ruff: clean. Focused mypy on `elaborate.py`: clean.
- Fresh snapshot assessment from the broad verification pass: 23/23 assessed, zero stale.

### Not checked

- The historical pre-repair source-revert mutation experiment was not repeated.
- `before.json` was not regenerated under the historical resolver during this pass.
- The project-wide Ruff/mypy baseline was not rebuilt in a historical worktree.
- SysIDE's own choice of exact leaf remains upstream authority; this audit checked codegen's use of
  that answer.

---

## Remediation — 2026-08-16 (findings 1, 5, 6)

The owner authorized findings **1, 5, and 6**. Findings 2, 3, 4, and 7 are untouched and reserved
for close. Everything below was re-run in the licensed environment, and no existing assertion was
weakened to make anything pass — the one assertion that changed was strengthened.

### Finding 1 — closed. Identity is now measured, and absence can no longer pass as agreement.

`corpus_compare.py` captures an identity block for every root that elaborates; the `with_identity`
switch is gone rather than defaulted. `before.json` was regenerated under the **pre-repair**
resolver — `git checkout 98970c9^ -- src/sysml_codegen/elaboration/elaborate.py`, capture, restore,
`git diff -- src/` empty — so it measures the old resolver rather than reconstructing it. Apart from
the added identity blocks and the one fixture finding 6 required, the regenerated `before.json` is
identical to the committed one, field for field. Two consecutive `after.json` runs are
byte-identical.

The comparator bug is fixed at the root: `adjudicate.py` raises `MissingIdentityBlockError` when a
root that elaborated carries no identity block, naming ledger, section, and root. Only a refused
root may lack one — it produced no graph — and its refusal string is compared instead. Verified by
deleting a block from a ledger and re-running.

**The measured result: 139 roots compared, 0 with a changed identity block** (125 corpus + 14
promoted; 15 corpus roots refuse to elaborate). The four spike-fixture roots the re-audit flagged as
having actually changed sites are inside that compared set, and their identities did not move.
Changed rows are 20, not 19: the extra row is the new fixture, refusing on both sides with no edge
either way, adjudicated in `verification/adjudication.md`. `plan.md`,
`verification/README.md`, and `verification/adjudication.md` now state these numbers; SC12 is met on
that evidence.

### Finding 5 — closed. The absent leaf refuses, and the verifier no longer shares the blind spot.

`_resolve_direct_reference` now refuses a leaf its element index does not hold, rather than falling
through to `_resolve_leaf`. The reasoning is recorded in the function's docstring and is the item's
own intent applied to itself: that index holds every declaration carrying a reload-stable qualified
name, so a missing leaf means the resolved fact and the index disagree about what the model
contains. Owner classification is then unanswerable, and the definition-owned route answers from the
*consumer's* lineage — the positional guess this item exists to delete, taken in the one case nobody
could see. It refuses by name instead (`SI_OCCURRENCE_MISSING`).

Proof that nothing regresses: `verification/absent_leaf_census.py` and its retained
`absent-leaf-census.json` measure the new refusal across 154 roots — **139 measured to completion,
1 partially, 14 unmeasured; 770 one-segment reference leaves observed, 0 absent from the element
index.** The ledger's changed-row set is unchanged apart from the new fixture, and no corpus row
moved. This paragraph originally read "the whole population … 769 leaves"; the scoped
re-verification found that claim false and the census was repaired. See
[Finding 5 repair](#finding-5-repair--2026-08-16-census-corrected-at-the-resolver-boundary).

The path is kept under test at the resolver boundary
(`tests/unit/test_direct_reference_unknown_leaf.py`), which is the honest place for it: the census
says no authored model reaches this, and inventing a fixture that pretends otherwise would be worse
evidence than none. `corpus_compare.py` resolves its leaves against a full live `Feature` index
rather than the elaborator's, so a leaf the elaborator cannot see is rowed and measured instead of
dropped.

### Finding 6 — closed. Both edges pinned, and the second one turned out to be authorable.

`test_ambiguous_exact_owner_is_lenient_diagnostic_and_strict_refusal` now pins the whole diagnostic
the design names — consumer node ID, parameter, and detail text — and compares the strict and
lenient diagnostic lists by value rather than by code counter.

The selected-owner-but-missing-leaf-target raise **is** reachable from an authored model, contrary
to the expectation that it might not be. A one-segment reference naming a `PartUsage`-owned
*calculation usage* rather than one of its outputs (`comp_a::twice * 2.0`) loads cleanly, resolves
to the exact `twice` declaration, selects `comp_a`'s occurrence, and finds no attribute or computed
target there. `tests/fixtures/usage_owner_calc_usage_leaf` is that model and
`test_selected_owner_without_a_leaf_target_refuses_by_name` pins the refusal on the full tuple,
with the owner and leaf wires derived from the model rather than pasted in.

### Verification of the remediation

- Full suite: **17 failed, 2145 passed, 34 skipped, 88 deselected.** Failing node set identical by
  name to `after-phase5-full-suite.txt`; all 17 are the environmental missing-`pandas` failures. The
  two added passes are the two tests above. All 34 skips are golden-fixture skips; zero
  license-related skips.
- `adjudicate.py` on the regenerated ledgers: **0 structural problems**, 0 changed refusals, 0
  changed identity blocks, 20 changed outcomes, no unpaired root-field change.
- Focused Ruff on the changed production, test, and verification files: clean. Focused mypy on
  `elaborate.py`: clean. The pre-existing project-wide backlog was not touched.
- The production edit is confined to `elaborate.py`. No schema, index, projection, or codec widened.

---

## Scoped re-verification — 2026-08-16 (remediation `c2fa657`)

### Outcome

**Needs Work within the requested scope.** Findings 1 and 6 close on independently regenerated
evidence. Finding 5's production fail-closed change is correct, but the retained census does not
measure the whole population it claims. Findings 2, 3, 4, and 7 were not re-adjudicated.

The bounded product-lens pass found no new product contradiction or structural smell in findings
1, 5, and 6. Its gate is CLEAR for this remediation. The earlier arrayed-aggregation finding and
its DISPOSED status remain untouched and outside this pass.

### Finding status

1. **Closed — identity coverage and absence handling now hold.** Fresh current and historical
   captures reproduce the retained ledgers. There are 154 roots: 139 elaborate and carry identity,
   while 15 refuse and carry no graph identity. All 139 before/after identity blocks compare equal.
   Removing one identity block raises `MissingIdentityBlockError` with side, section, and root
   (`verification/adjudicate.py:61-85`). Altering a refusal string produces a structural problem.
   After removing the new identity blocks and finding-6 fixture, the historical capture matches the
   pre-remediation ledger. SC12 is verified.

5. **Reopened — the runtime fix holds, but the “whole population” census is incomplete.** The
   resolver now refuses an unknown leaf instead of taking the positional fallback
   (`src/sysml_codegen/elaboration/elaborate.py:2322-2328`), and its boundary test passes
   (`tests/unit/test_direct_reference_unknown_leaf.py:45-60`). However,
   `verification/absent_leaf_census.py:72-88` returns as soon as `elaborator.run()` raises. Leaf
   collection happens only afterward at `:90-93`, and totals at `:107-112` convert every refused
   row's absent count to zero. The retained `s5_sibling_formal` row therefore records only its later
   graph-validation refusal (`verification/absent-leaf-census.json:38-41`). Catching that same
   refusal and inspecting the already-populated elaborator found one processed one-segment leaf,
   with zero absent. The claimed total at `:759-763` is therefore at least 770, not 769. The census
   must either inspect safely available pending references on refused roots or state that those
   roots are unmeasured; it cannot call 769 the whole population. **Repaired 2026-08-16 — see
   [Finding 5 repair](#finding-5-repair--2026-08-16-census-corrected-at-the-resolver-boundary)
   below.** The re-verification's arithmetic is confirmed exactly: the true observed count is 770.

6. **Closed — both weak edges are now pinned.** The arrayed strict/lenient test asserts the full
   consumer, parameter, detail, empty-input, and cross-mode diagnostic value
   (`tests/conformance/test_elaboration_fail_closed.py:207-231`). The authored calculation-usage
   leaf fixture reaches the missing-target branch, and its kept test pins the full refusal tuple
   (`:242-274`). Ledger row 20 records the same refusal code before and after with only its detail
   sharpened. The test diff strengthens one assertion and adds tests; it weakens none.

### Independent verification

- Focused licensed suite: **116 passed**.
- Full licensed suite: **17 failed, 2145 passed, 34 skipped, 88 deselected**, matching the retained
  count; the scoped code reviewer confirmed the exact 17-node baseline.
- Fresh `after.json` and `absent-leaf-census.json`: byte-identical to the retained files.
- Historical `before.json`: regenerated with the pre-repair resolver and semantically identical to
  the retained file after normalizing only the temporary checkout path.
- Clean adjudication: 20 changed outcomes, 139 identity blocks compared, 15 unchanged refusals,
  zero structural problems. Missing-identity and changed-refusal controls both fired.
- Focused Ruff and mypy: clean. `git diff -- src/` remained empty after the historical capture.

### Not checked

- Findings 2, 3, 4, and 7, per `briefs/reverification-scope.md`.
- The remaining 14 refused roots were not post-failure-enumerated; the census must be repaired
  before it can supply that evidence. The repair below shows all 14 refuse before the resolver runs
  at all, so their populations stay unmeasured and are now reported as such.
- Snapshot reassessment, the repo-wide Ruff/mypy backlog, the 88 deselected tests, and a historical
  full-suite run under the pre-repair resolver.

---

## Finding 5 repair — 2026-08-16 (census corrected at the resolver boundary)

### What was wrong

`census_root` reconstructed one-segment leaves from the elaborator's pending lists *after*
`elaborator.run()` returned. A root that refused mid-run returned early with a `refused` string and
no leaf key at all, so `main`'s `row.get(..., 0)` scored it as zero leaves and zero absent. That is
absence of measurement read as a measurement of zero — the same defect as finding 1's comparator,
which mapped a missing identity block to `None` and read `None == None` as agreement. Finding 1's
own fix was written by the pass that then wrote this census, so the blind spot travelled.

### The repair

The census now counts where the branch actually runs. `LeafObservations.observe` wraps
`_resolve_direct_reference` on the elaborator instance; every call records the leaf it was handed
and whether `_elements` held it *at that moment*, then delegates to the shipped implementation
unchanged. A partial run therefore still reports what it saw. Each root carries an explicit
`measurement`:

- `complete` — `run()` returned; the root's whole one-segment population was observed.
- `partial` — `run()` raised after the branch had already run; the observations are real, the
  remainder is unknown. The refusal reason is recorded.
- `none` — elaboration never started (load, extraction, or validation refusal); nothing is known.

No row can be zero-by-absence: `partial` and `none` rows are counted as residual unmeasured
population in the totals block, and the JSON states the claim it is entitled to make in a
`population_claim` field rather than leaving a reader to infer "whole population."

### The re-derived numbers

**154 roots — 139 complete, 1 partial, 14 unmeasured. 770 one-segment reference leaves observed,
0 absent from the element index.**

- The re-verification's arithmetic is exact. `s5_sibling_formal` resolves one one-segment leaf
  before its producer-cycle refusal; that leaf is the 770th. The old count of 769 was one short.
- The other 14 refused roots refuse before the resolver runs — load failure, extraction refusal,
  blocking validation, or an elaboration invariant that fires ahead of any reference resolution —
  so they observe nothing and are recorded as `none`, not as zero.
- **The absent count is zero on this new measurement, not on the old one.** No observed leaf, on
  any root including the partially measured one, was missing from the element index. The runtime
  refusal remains unreached by any authored model in the corpus, which is why it stays pinned at
  the resolver boundary in `tests/unit/test_direct_reference_unknown_leaf.py` rather than by a
  fixture pretending otherwise.
- 15 roots hold residual unmeasured population. The census, `verification/README.md`, `plan.md`,
  and this audit no longer claim whole-population coverage.

### Verification of the repair

- Full suite: **17 failed, 2145 passed, 34 skipped, 88 deselected**
  (`verification/after-finding5-full-suite.txt`); failing node set identical by name to
  `after-phase6-full-suite.txt`. No assertion was weakened; no test or production file changed.
- Focused Ruff and `ruff format` on the census script: clean.
- The change is confined to `verification/absent_leaf_census.py` and the artifacts carrying the
  corrected numbers. `src/` is untouched.

---

## Original 2026-08-15 audit record (superseded where noted above)

## The Point

The product obligation is a design search where engineering parameters vary freely and viability
and outcomes (like LCOE) are assessed, without the engineering logic being embedded — the owner's
words in `.project/product/P-001-design-search-free-variation.md:11-18`. That search is only
trustworthy if changing one modeled source occurrence changes **every and only** the consumers
bound to that occurrence, and if an unsupported form fails loudly instead of picking a candidate
(`.project/backlog/epic_elaborate_first_architecture.md:31-33,84-86`).

This item repairs a violation of exactly that. SysIDE resolves a one-segment reference to an exact
leaf declaration; when a `PartUsage` owns that declaration, the owner *is* the occurrence the
author named. The shipped resolver threw the owner away and re-found the leaf's feature slot by
walking the **consumer's** occurrence lineage. A consumer authored inside `comp_b` that named
`comp_a::length` therefore bound `comp_b.length` — silently, with no diagnostic, at the same slot.
I reproduced that on the pre-repair resolver: the consumer read `7.0` where the model says `3.0`.
A confident wrong number in an LCOE chain is the worst failure mode P-001 has.

## Summary

The repair is one branch in one file, and it does what the spec and design say it does. I
independently reproduced every load-bearing claim: the 15 Phase-2 nodes go red on the pre-repair
resolver and green at HEAD; 7 of the 11 Phase-4 nodes go red with 4 honestly-explained exceptions;
both corpus ledgers regenerate **byte-identical** from my own runs; the full suite is 17 failed /
2143 passed with a failing node set identical to the pre-change baseline, all 17 environmental
missing-`pandas`. Zero unadjudicated corpus rows, and the arrayed-owner fix-vs-regression call is
correct on evidence I measured myself.

Four things are worth the owner's eye and none blocks certification: the plan's Phase-1 Completion
block was left an empty stencil, a landed-false `[HARD]` line survives (deliberately, out of
bounds) in the self-binding spec, the arrayed-owner refusal reaches a wider authored surface than
its fixture implies, and one narrow branch-predicate blind spot is shared by the code and the
verifier that measures it.

## Product Judgment

**Is this the right piece of work? Yes, without qualification.** It removes a silent wrong answer
on the exact axis P-001 depends on, and it removes it by *deleting* an inference (consumer
position) rather than adding a mechanism. Where the repaired route cannot choose, it refuses by
name instead of guessing — the loud-failure half of the ELABORATE-FIRST mission, applied to its
own hardest case.

**Historical product-lens ledger gate: CLEAR (superseded 2026-08-16).** I scanned every block in
`product-lens.md`, not just the latest. `spec-F1` is resolved by citation in the second block.
`design-F1`, `design-F2`, and `design-F3` are `DISPOSED`, and I verified each disposition was
actually carried out rather than merely promised: D11 now records a dated coverage gap instead of
offering a census as proof (`design.md:250-256`); D2 carries the named split-source acceptance and
its standing guard (`design.md:203-215`), and that guard is a real test I read and ran
(`tests/conformance/test_source_identity_extraction.py:197-227`); D10 route 2 requires the
`authored bare discrimination unproven` record (`design.md:238-248`). No block records a `BLOCK`.
No epic-level product-lens block is referenced.

**Structural smells (product-lens §4), checked mechanically:**

- *Test passes only by selecting one route or duplicate* — **did not fire.** The opposite is built
  in: `test_combined_named_source_reaches_every_and_only_its_consumers`
  (`tests/conformance/test_usage_owned_reference_anchoring.py:302-323`) and the public-mutation
  node assert the whole-graph typed-edge map, so a seventh consumer binding anywhere fails the
  test wherever it binds.
- *Special category exempts a case whose meaning is unchanged* — **did not fire.** The
  definition/package-owner exemption is a real semantic distinction: those owners have no
  occurrence of their own. Two authored controls pin it
  (`test_definition_owned_alias_leaf_keeps_the_consumer_local_edge`, `…subset…`).
- *Two representations kept manually in sync* — **fired, and is resolved here.** Frozen
  `owner_element_id` / `owner_is_definition` on `ResolvedTargetFact` coexist with the live metatype
  lookup the branch actually uses. This is design-F2, already disposed at design time. I accept it
  for this item on two checks I made myself: the branch has exactly one deciding authority
  (`elaborate.py:2314-2317` reads the live leaf, its live owner, and `SysideAdapter.is_instance`),
  and the disagreement guard is a real executing test, not a promise. Escalated into this judgment
  and resolved in it.
- *Correctness depends on downstream knowledge of an internal representation* — did not fire.
- *A baseline preserves behavior contradicting the product's reason to exist* — **did not fire, and
  this is checkable rather than asserted.** Every one of the 19 changed ledger rows lives in the
  spike fixtures or in the 13 fixtures this item added; **zero** changed rows touch a pre-existing
  `tests/fixtures/` root, so no committed v6 snapshot could be carrying a stale mis-anchored edge.
  I derived that from my own regenerated ledger, independently of the snapshot assessment JSON.

## Findings

### Plan completion

Phases 2–5 are complete and their validation items hold. Phase 1's work is complete but its record
is not.

- **`plan.md:445-450` — the Phase-1 Completion block is an empty stencil.** `**Completed:**`,
  `**Actual Changes:**`, `**Issues:**`, `**Deviations:**` all have no content, and its eight
  checkboxes (`plan.md:101-134`) were never ticked, while every other phase carries a full
  completion record. The work itself landed and is real: I re-ran both probe drivers under the
  license (`probe.py` and `sweep.py`, exit 0 each, `git status` clean afterwards), `ruff check` on
  the retained probe code passes, and `git diff --stat 2768c68 d78c42e -- src/ tests/` is empty, so
  the phase gate held. The findings are substantive documents, not stubs
  (`spike/bare-discriminator-authorability/findings.md`,
  `spike/deep-override-authorability/findings.md`), and the D11 result is additionally recorded
  inline at `plan.md:105-116`. This is a traceability gap, not a work gap. I have ticked the boxes
  I verified; the narrative block should be filled at close.

### Spec conformance

Every criterion below was checked against a test I ran or an evidence row I regenerated.

- **SC1 — owner occurrence precedes leaf slot, across every shared resolver consumer.** Met. The
  seven `test_combined_*` lane nodes cover all six caller lanes plus alias-following; all seven go
  red on the pre-repair resolver and green at HEAD.
- **SC2 — u4 package sibling.** Met. `SI_OCCURRENCE_MISSING` pre-repair → edge to the
  package-scoped occurrence, zero diagnostics, at HEAD.
- **SC3 — u5 named sibling.** Met. `SI_OCCURRENCE_AMBIGUOUS` pre-repair → `plant.comp_a.length`.
- **SC4 — u6 cross-owner.** Met, and this is the headline. I watched the pre-repair failure: same
  slot `5be4d227`, occurrence step `87f9e6f2` (`comp_b`) where the test demands `comp_a`, with an
  empty diagnostic list. The test also asserts the wrong node has *no* consumer, so a silent
  fallback added later would fail it.
- **SC5 — u7 paired spellings.** Met. Two qualified inputs land on distinct occurrences and equal
  their in-fixture dot-path controls edge for edge.
- **SC6 — u1–u3b and definition/package/enum/chain controls unchanged.** Met. All six control nodes
  pass on both the pre-repair and repaired resolver, which is what proves the red set is about
  target identity rather than fixture breakage.
- **SC7 — kept qualified regressions cover alias, computed, constraint binding, predicate.** Met.
  Rows 11, 14, 16, 17 with named test nodes; the alias raw target is asserted on `alias_target`,
  which `semantic_edges()` omits.
- **SC8 — kept bare regression with a discriminating topology.** Met, and not on an accident. On
  the pre-repair resolver `usage_owner_bare_alias` binds `comp_b.length` (occurrence `7479b60a`);
  at HEAD it binds `comp_a.length`. Consumer lineage and exact owner genuinely differ, so it cannot
  pass on the corpus's fan-out-of-one equality. D10 took route 1 on real probe evidence (9 of 14
  swept topologies discriminate), so no gap record attaches. **Not overclaimed:** the kept bare
  evidence is entirely the `alias` family; the probe's truly-bare `import` shapes (c04/c05) were
  not promoted. SC8 asks for one discriminating bare regression and gets one.
- **SC9 — broader surface re-derived, every difference adjudicated.** Met, and this is the
  strongest single check in the audit. I re-ran `corpus_compare.py` at HEAD: **byte-identical to
  `after.json`**. I installed the pre-repair file and re-ran it: **byte-identical to `before.json`**.
  I re-ran `adjudicate.py` over my own captures: output **identical** to the committed
  `adjudication-diff.txt` — 409/409 and 16/16 site keys, 5 + 14 = 19 changed outcomes, 0 rows
  without an edge/diagnostic/named reason and **0 structural problems**. This pass reported 0
  identity-block changes over 153 roots; the independent re-audit proved only 13 blocks existed.
  The corpus population is otherwise genuinely complete: `corpus_roots.json`'s 140 roots
  cover every `tests/fixtures/` directory except `golden`, `baseline_outputs`, `baseline_yaml`, and
  `v6_recapture_batch`, and `find` confirms none of those four contains a `.sysml` file.
- **SC10 — public off-default mutation, live and round-trip.** Met; node passes at HEAD and fails
  pre-repair.
- **SC11 — strict/lenient semantic parity.** Met; 6 parity parameters plus both negatives pass.
- **SC12 — feature slots, occurrence records, serialized IDs unchanged.** The 2026-08-15 pass marked
  this met. **Superseded:** only 13 promoted identity blocks were captured; SC12 is reopened.
- **SC13 — every live-vs-snapshot difference classified; unaffected bytes unchanged.** Met, and
  provable without trusting the assessment file: no changed ledger row touches a pre-existing
  fixture root, so no committed snapshot can be stale. No snapshot bytes appear anywhere in
  `2768c68..HEAD`. D9's recapture trigger correctly never fired.
- **SC14 — close-time check of the bounded self-binding spec.** Prepared, not closed, and correctly
  left so. The F-6 bullet at `.project/active/self-binding-replacement/spec.md:53-61` now reads in
  the past tense, names `98970c9` and the file, still calls the behavior codegen defect F-6 rather
  than the meaning of `::`, and leaves the D-5, D-7, and fusion-tea sentences untouched — I read
  all of it. Its verifier is `/_my_close` by the criterion's own text, so this box stays open.

**Non-goals respected.** Nothing reconstructs occurrence identity from qualifier text; the branch
keys on the live owner's metatype. No name, qualified name, display path, source span, or candidate
order selects anything. No schema, index, codec, projection, or public identifier changed.

### Design conformance

The implementation follows the design, including the two decisions most likely to be quietly
dropped.

- **D1/D3 — one seam, existing selectors reused.** `_resolve_direct_reference`
  (`elaborate.py:2294-2342`) composes `_select_occurrences` and `_target_at`; no new index, no
  duplicated ambiguity policy.
- **D2 — metatype guard, live authority.** `SysideAdapter.is_instance(owner, "PartUsage")`, never
  `owner_is_definition`.
- **D4 / invariant 7 — scalar under a plural caller.** Enforced with `plural=False` at
  `elaborate.py:2330` and pinned by the `sum()` node. I probed it directly: `sum(comp_a::length)`
  over an arrayed `comp_a` refuses cleanly with `SI_OCCURRENCE_AMBIGUOUS` rather than fanning out
  or crashing.
- **D5/invariant 11 — alias following stays with the caller.** The branch returns a raw edge;
  `_resolve_aliases` still assigns `alias_target` at `elaborate.py:2439`.
- **Invariant 10 — no positional recovery.** A missing target raises rather than retrying
  `_resolve_leaf` (`elaborate.py:2336-2341`), and the arrayed negative pins it end to end.
- **Documented deviation, and it is the right call.** Phase 3 used `_select_occurrences` directly
  instead of `_contextualize_root`. `_contextualize_root` re-dispatches on the very metatype the
  branch has already established and returns a union that cannot occur here; calling the selector
  directly mirrors its `PartUsage` arm with identical candidates and policy. Recorded in the plan,
  not silent.

One design-level note. The `[owner_occurrence] = self._select_occurrences(...)` destructuring at
`elaborate.py:2324` depends on a non-local invariant. I checked every `plural=False` return path of
`_select_occurrences` (`elaborate.py:2153-2214`) and each returns exactly one element or raises, so
the unpack is safe — and it matches the existing idiom at `elaborate.py:2353`. No change needed.

### Code integrity

No placeholder, TODO, FIXME, dead code, skipped test, or assertion-free test in anything this item
added or changed. No broad `except Exception`, no defensive default, no compatibility shim. Two
observations, both low severity:

- **`elaborate.py:2314-2317` — a leaf absent from the element index silently keeps the old route,
  and the verifier that would measure it excludes the same rows.** `_stable_elements` skips
  Features with no `qualified_name` (`elaborate.py:641-642`), so `self._elements.get(leaf_id)`
  returning `None` falls through to `_resolve_leaf`. `corpus_compare.py:221-223` drops exactly the
  same rows from its population. Branch and measurement therefore share one blind spot. In practice
  it is close to unreachable — a one-segment reference resolved by SysIDE names a named feature, so
  it has a qualified name — which is why this is an observation rather than a finding. What should
  change, if anything ever does: make the absent-element case explicit rather than an implicit
  fall-through, so it cannot become a silent route for a shape nobody measured.
- **`tests/conformance/test_usage_owned_reference_anchoring.py:464-476,480-496` — the two
  identity-stability parametrizations are close to tautological.** `node_id == NodeId(ATTRIBUTE,
  scope, slot_id)` restates how the node is constructed, so it can only fail if identity
  construction itself is rewritten. That is a real (if narrow) guard, and the docstrings honestly
  say the byte-level before/after evidence lives in the ledger — which I regenerated and which does
  carry the weight. No change needed; recorded so nobody later reads these two names as the
  identity proof.

### The claims you asked me to test specifically

- **Item 1 — the edit is confined.** Confirmed. `git diff 2768c68..HEAD -- src/` is
  `elaboration/elaborate.py` alone: one private helper added, one call rewired, 51 insertions and 6
  deletions. No evidence schema, occurrence or slot index, graph model, projection, or codec was
  touched or widened.
- **Item 2 — the 15 red assertions were not weakened.**
  `test_usage_owned_reference_anchoring.py` was added at `85f598a` and
  `git diff 85f598a HEAD -- <that file>` is **empty**. The assertions that passed are the exact
  bytes that failed.
- **Item 3 — the tests genuinely fail without the repair, and the exceptions are honest.**
  Confirmed by running the pre-repair file in place. Anchoring file: **15 failed, 33 passed**, and
  the 15 names match the docstring list one for one. I inspected three failures directly and each
  is a target-identity mismatch, not a load error: u6 differs only in the occurrence step at an
  unchanged slot, the bare discriminator lands on `comp_b`, and the arrayed case produces *no
  diagnostic at all*. Phase-4 nodes: **7 failed, 4 passed**, exactly as claimed. The four that stay
  green are honest, not convenient. Parity for the combined fixture, u6, and the bare alias passes
  pre-repair because a parity test compares strict to lenient, and the pre-repair defect was a
  silent wrong edge produced *identically* in both modes — the comparison is structurally incapable
  of seeing it, which is why u4/u5/u7 (which produced diagnostics pre-repair) do fail. The
  readiness node uses a different fixture and a different exit and could not be affected. The plan
  says exactly this and it is correct.
- **Item 4 — every criterion maps to real evidence, with gaps not overclaimed.** Confirmed above.
  SC8 is genuinely evidenced; the deep-override lane is explicitly listed as *not evidenced* under
  the standing D11 gap, in the adjudication's own "Not evidenced, and deliberately so" section, and
  is claimed nowhere as covered. I re-ran the D11 probe reasoning against the ledger: the lane
  still measures 0 one-segment sites.
- **Item 5 — zero unadjudicated rows, and the arrayed call is sound.** Confirmed by regenerating
  both ledgers and the diff. On the arrayed call I did not take the adjudication's word for the
  decisive fact: I ran the pre-repair resolver on the fixture and the consumer bound
  `BareAliasArrayedOwner__plant__comp_b__length` with zero diagnostics. The old answer was the
  enclosing sibling's value, which the reference does not name under any reading — not `comp_a[0]`,
  not `comp_a[1]`. Trading that for a named refusal is a fix, not a regression.
- **Item 6 — no placeholder, TODO, dead code, skipped or empty test.** Confirmed by search and by
  reading every added test.

### Ruff and mypy (raised after launch)

The premise needs one correction: the plan does not imply these gates come back clean. The
validation item is literally "Run `uv run --extra dev ruff check src/ tests/` and
`uv run --extra dev mypy src/`" (`plan.md:390`), and Phase 5's Issues section reports the real
numbers in the first sentence rather than burying them. Nothing was misrepresented.

**The delta claim holds exactly.** I built a scratch worktree at `2768c68` and diffed both tools
line for line against HEAD: ruff **131 = 131, identical**; mypy **52 = 52, identical**; **zero**
mypy errors anywhere in `src/sysml_codegen/elaboration/`. This item contributes no new finding to
either gate from its production edit, its thirteen fixtures, or its five test files.

**Leaving the backlog alone was right, and not merely defensible.** 91 of the 131 ruff findings sit
in `tests/fixtures/baseline_outputs/**` and `tests/conformance/golden/**` — generator-owned bytes
that byte-identity gates compare against. Reformatting them would break those gates, which is a
real regression traded for a lint score. The remaining 40 are unrelated pre-existing test-file
lint whose repair belongs to whoever owns those files. Absorbing either set into a semantics repair
is exactly what the plan's own risk note forbids.

---

## Certification

**2026-08-15 verdict: Certify (superseded 2026-08-16).** The product-lens ledger gate was CLEAR with no unresolved owner or `[HARD]`
contradiction; the one structural smell that fired (design-F2's split representation) is resolved
in the Product Judgment above on evidence I checked rather than inherited.

Verified and marked: spec success criteria 1–13 (SC14 left open — it is a close-stage criterion by
its own text); plan Phases 1–5, including Phase 1's validation items which I re-ran myself.

Three things must travel to `/_my_close`, none of them blocking:

1. **The landed-false `[HARD]` line.** `.project/active/self-binding-replacement/spec.md:132-139`
   still says "the current one-segment resolver normalizes to a feature slot before using the owner
   and then selects by consumer position." That is now false. Phase 5 surfaced it rather than
   editing it because it sits outside the owner-drawn bounded inventory — the correct
   capture-fidelity call — but it leaves an active `[HARD]` requirement stating something the
   shipped code contradicts.
2. **The arrayed-owner refusal has a wider authored surface than its fixture suggests.** The
   adjudication measures blast radius at zero in the tracked corpus, which is true, but the shape
   that now refuses is *any* unindexed one-segment reference to an arrayed owner's leaf — including
   under `sum()`, which an author might plausibly write and might reasonably expect to fan out. I
   verified both halves: post-repair `sum(comp_a::length)` over `comp_a[2]` refuses with
   `SI_OCCURRENCE_AMBIGUOUS`, and **pre-repair it silently summed the sibling's `7.0`**, so this is
   the same fix and never a working aggregation. It is worth naming for the owner because the
   author-facing likelihood is higher than "one fixture built to catch it" conveys. The
   adjudication's own note about the diagnostic message not naming the candidates or the index
   syntax belongs with it.
3. **Phase 1's empty Completion block** (`plan.md:445-450`) should be filled from the evidence that
   already exists.

**Not checked:**

- **Generated-package runtime behavior.** I verified typed graph edges, diagnostics, projection
  equality, and the shipped public JSON in the mutation test. I did not execute a generated package
  against real TEAx/simkit, and no lane of this item claims that.
- **Models outside the frozen corpus.** A handful of project probe roots
  (`.project/active/silent-failure-hardening/probes/`, `type-indexing/probe`,
  `return-style-extraction/probe`, `spike-concrete-expansion-instance-index`, and the `completed/`
  probe models) are not in `corpus_roots.json`. None is loaded by the suite, and the frozen set is
  the one the 2026-08-15 scans measured, so this is a stated boundary rather than a gap — but it is
  a boundary, and a usage-owned one-segment site in one of those roots would not have been counted.
- **SysIDE's own resolution.** The whole repair rests on SysIDE having resolved the written text to
  the right exact leaf. I audited what codegen does with that answer, not whether SysIDE's answer
  is right.
- **The v6 batch's live-vs-stored assessment as executed by Phase 4/5.** I did not re-run
  `assess_v6_snapshot_churn.py`. I reached "no snapshot can be stale" a different way — no changed
  ledger row touches a pre-existing fixture root — which is independent of, and I think stronger
  than, re-running the same script.
- **Long-run or performance characteristics.** Not in scope for this item and not examined.
