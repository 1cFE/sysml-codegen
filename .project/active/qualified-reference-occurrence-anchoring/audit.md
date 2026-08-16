# Audit: Exact Owner Anchoring for Usage-Owned One-Segment References

**Verdict:** Certify
**Audited:** 2026-08-15
**Branch:** main
**Commit:** `2d2162e` (diff audited: `2768c68..HEAD`)
**Auditor evidence:** every runtime claim below was re-run by this audit under the licensed
environment, not read from the implementers' logs. Where a number appears, this pass produced it.

---

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

**Product-lens ledger gate: CLEAR.** I scanned every block in
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
  without an edge/diagnostic/named reason, 0 identity-block changes over 153 roots, **0 structural
  problems**. The corpus population is also genuinely complete: `corpus_roots.json`'s 140 roots
  cover every `tests/fixtures/` directory except `golden`, `baseline_outputs`, `baseline_yaml`, and
  `v6_recapture_batch`, and `find` confirms none of those four contains a `.sysml` file.
- **SC10 — public off-default mutation, live and round-trip.** Met; node passes at HEAD and fails
  pre-repair.
- **SC11 — strict/lenient semantic parity.** Met; 6 parity parameters plus both negatives pass.
- **SC12 — feature slots, occurrence records, serialized IDs unchanged.** Met. Zero identity-block
  differences across all 153 roots in my regenerated ledgers.
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

**Certify.** The product-lens ledger gate is CLEAR with no unresolved owner or `[HARD]`
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
