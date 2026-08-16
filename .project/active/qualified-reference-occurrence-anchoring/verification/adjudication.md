# Corpus adjudication — exact owner anchoring for usage-owned one-segment references

**Phase:** 5 (certification)
**Captured:** 2026-08-15, branch `main` at `a3b46dc`, licensed environment
(`set -a; source ../agentic-mbse/.env; set +a`)
**Verdict:** every changed row is a fix. **Zero unadjudicated rows.** One row is a behavior
change that can make a model which loads today start failing; it is adjudicated on its merits in
[The one hard call](#the-one-hard-call--the-arrayed-owner-refusal), and it is a fix.

Everything below is what the shipped resolver actually did when re-run at the commit above. No row
is carried over from a Phase-3 note or a research prediction.

## How this was produced

```bash
set -a; source ../agentic-mbse/.env; set +a
V=.project/active/qualified-reference-occurrence-anchoring/verification

# capture the shipped resolver's answer at every in-population site
uv run python $V/corpus_compare.py --output $V/after.json

# list every difference against the frozen before-state
uv run python $V/adjudicate.py $V/before.json $V/after.json > $V/adjudication-diff.txt
```

`after.json` is the same document `before.json` is: the shipped elaborator's typed answer at every
one-segment reference whose exact leaf is owned by a live `PartUsage`, keyed by
`(root, lane, consumer node, reference ordinal, leaf declaration)`. The verifier predicts nothing
and never decides an edge from source text.

Two independent runs of `corpus_compare.py` at this commit are **byte-identical**, so the capture is
deterministic. It is also byte-identical to `after-phase3.json`, which is the expected result and
not the evidence: Phases 4 and 5 changed no production file, so a differing ledger would have been
the finding. `adjudicate.py` is new here and decides nothing — it diffs two captured ledgers and
prints what a human must rule on.

## Structural checks — the phase's own stencil, with actual results

| Stencil assertion | Result |
|---|---|
| `site_keys(after) == site_keys(before)` | **holds.** corpus 409 = 409, promoted 16 = 16; zero keys only in one side |
| every after row has an edge, a diagnostic, or a named structural reason | **holds.** 0 uncovered rows in either section |
| `occurrence_records(after) == occurrence_records(before)` | **holds.** 0 roots with a changed `identity` block, out of 140 corpus + 13 promoted = **153** |
| refusal strings unchanged | **holds.** 15 refused corpus roots, same roots, same reason strings |
| `unadjudicated_differences(before, after) == []` | **holds.** all 19 changed rows are ruled on below |

Corpus totals move **405 edge / 4 diagnostic → 409 edge / 0 diagnostic** over the same 409 sites and
the same lane split (318 calc binding, 76 computed expression, 15 constraint binding). Promoted
totals move **12 edge / 4 diagnostic → 15 edge / 1 diagnostic** over the same 16 sites.

Four root-level `diagnostics` lists also changed (u4, u5, u7 in both sections, and the arrayed
negative). Each pairs with one of its own changed sites below — the same event seen at the graph
level — and `adjudicate.py` labels them `paired with a changed site`. None is unpaired.

## The 19 changed rows

Occurrence steps are abbreviated to their first 8 hex digits and named. Full wire IDs are in
`adjudication-diff.txt`; the ledgers hold the exact strings.

### Rows 1–5 — the corpus (spike copies of u4–u7)

| # | Root | Lane | Written | Before | After | Verdict |
|---|---|---|---|---|---|---|
| 1 | `spike/fixtures/u4_usage_qual_pkg_sibling` | calc binding | `shared_component::length` | `SI_OCCURRENCE_MISSING` | edge → `shared_component` (`ae393bfa`) | **fix** |
| 2 | `spike/fixtures/u5_usage_qual_named_sibling` | calc binding | `comp_a::length` | `SI_OCCURRENCE_AMBIGUOUS` | edge → `plant.comp_a` (`eecdcddf`) | **fix** |
| 3 | `spike/fixtures/u6_usage_qual_crossnamed` | calc binding | `comp_a::length` | edge → `plant.comp_b` (`87f9e6f2`) | edge → `plant.comp_a` (`dd373162`) | **fix** |
| 4 | `spike/fixtures/u7_both_spellings` | calc binding | `comp_a::length` | `SI_OCCURRENCE_AMBIGUOUS` | edge → `plant.comp_a` (`95d32d62`) | **fix** |
| 5 | `spike/fixtures/u7_both_spellings` | calc binding | `comp_b::length` | `SI_OCCURRENCE_AMBIGUOUS` | edge → `plant.comp_b` (`869ecad0`) | **fix** |

**Topology and reasoning.**

- **Row 1 (u4).** `shared_component` is a package-scoped `PartUsage`; the consumer sits under a
  different root (`plant`). The consumer's own lineage contains no occurrence of the leaf's slot, so
  the old positional route reported `SI_OCCURRENCE_MISSING` for a reference whose owner is
  unambiguous and directly nameable. The repaired route selects the owner's single occurrence and
  reads the leaf slot there. The after-edge is a **one-step** occurrence, which is exactly right for
  a package-level part. A missing diagnostic replaced by the only occurrence the author could have
  meant is a fix.
- **Rows 2, 4, 5 (u5, u7).** Two sibling occurrences carry the same leaf slot, so the positional
  route saw two candidates and refused. The written qualifier names one of them. Selecting the named
  owner first leaves exactly one candidate. Row 4 and row 5 are the discriminating pair: written
  `comp_a::length` and `comp_b::length` in the same consumer now land on **distinct** occurrences,
  which a fan-out-of-one accident could not produce. A false ambiguity replaced by the owner the
  author wrote is a fix.
- **Row 3 (u6).** The only row in the corpus that was silently wrong before. The reference
  `comp_a::length` is authored inside `comp_b`; the old route matched the consumer's own lineage and
  bound `plant.comp_b.length`. The slot is unchanged (`5be4d227`) and only the occupancy step moved
  from `comp_b` to `comp_a`. This is the item's headline defect: one modeled source occurrence was
  not reaching its bound consumer, and a competing value was substituted with no diagnostic. Fix.

No corpus row is a bare reference. All five written texts are `::`-qualified, so the corpus produced
**no unclassified bare change** — the phase's assumption, measured rather than assumed.

### Rows 6–10 — the promoted u4–u7 copies

Same five topologies at `tests/fixtures/u4…`–`u7…`, byte-identical models to the spike copies, and
the outcomes match row for row (compare rows 6–10 with 1–5 above). Adjudication is identical:
**five fixes**. They appear twice because the item deliberately froze the research fixtures and
their maintained copies in separate ledger sections; the duplication is a consistency check, and it
passed.

### Rows 11–17 — the combined consumer fixture

`tests/fixtures/usage_owned_reference_consumers` has one modeled source, `plant.comp_a.length`
(3.0), read from seven consumers authored inside the sibling `plant.comp_b` (7.0). Every one of the
seven moved from `comp_b`'s occurrence (`fd0e7f52`) to `comp_a`'s (`e078eb54`) at the **same slot**
(`518b2191`).

| # | Lane | Written | Verdict |
|---|---|---|---|
| 11 | alias (raw `alias_target`) | `comp_a::length` | **fix** |
| 12 | calc binding | `comp_a::length` | **fix** |
| 13 | calc binding via the alias | `aliased_length` | **fix** |
| 14 | computed expression | `comp_a::length * 2.0` | **fix** |
| 15 | computed expression, `plural=True` caller | `sum(comp_a::length)` | **fix** |
| 16 | constraint binding | `comp_a::length` | **fix** |
| 17 | constraint predicate | `comp_a::length > 0.0` | **fix** |

**Reasoning.** Before the repair all seven consumers read 7.0 — the enclosing sibling's value — for a
reference that names `comp_a` explicitly. Each now reads the source it names. Two rows carry extra
weight:

- **Row 13** is the alias-following consumer. Its own owner is `comp_b` (the alias declaration
  `aliased_length` is authored there), and it moved because the alias's raw target in row 11 moved.
  That is the intended layering: the resolver anchored the alias, and alias following happened where
  it already happened. No resolver-level alias following was added.
- **Row 15** is the scalar `sum()` term under a caller passing `plural=True`. It stayed **singular** —
  one edge, not a fan-out across sibling occurrences. This is the cardinality risk the design named,
  and the shipped answer is the scalar one.

### Row 18 — the bare discriminator

| # | Root | Lane | Written | Before | After | Verdict |
|---|---|---|---|---|---|---|
| 18 | `tests/fixtures/usage_owner_bare_alias` | computed expression | `a_len * 2.0` | edge → `plant.comp_b` (`7479b60a`) | edge → `plant.comp_a` (`5c33d1dc`) | **fix** |

`a_len` is an alias declared on `Plant` for `comp_a::length`; the consumer is a computed attribute
inside `comp_b`. The written text names no owner at all, so this is the authored **bare** shape D10
searched for, and it discriminates: consumer lineage says `comp_b`, the exact leaf's owner says
`comp_a`, and they differ. Before, it silently read 7.0. After, it reads the 3.0 the alias points at.
Same slot, occupancy step moved. Fix, and it is the sole authored evidence that the repair covers
the bare form as well as the qualified one.

### The one hard call — the arrayed-owner refusal

| # | Root | Lane | Written | Before | After |
|---|---|---|---|---|---|
| 19 | `tests/fixtures/usage_owner_bare_alias_arrayed` | computed expression | `a_len * 2.0` | edge → `plant.comp_b` (`e559a865`) | `SI_OCCURRENCE_AMBIGUOUS` — "consumer context contains 2 candidate occurrences", consumer left unbound |

**Verdict: fix.** This is the row the brief singled out, and it is the only row where the product
lost an answer it used to give. The call is made on these facts.

**The model.** `part comp_a : 'Component'[2]` — the owner has two occurrences, `comp_a[0]` and
`comp_a[1]`. `alias a_len for comp_a::length` names that owner without an index. A computed
attribute inside the scalar sibling `comp_b` reads `a_len * 2.0`.

**What the answer used to be.** The before-edge is occurrence `e559a865`, and `e559a865` is
**`comp_b`** — verified by printing the fixture's occurrence records, not inferred. So the answer the
product used to give was not `comp_a[0]` and not `comp_a[1]`. It was the enclosing sibling's own
`length`, the same wrong-owner substitution as rows 3, 11–17 and 18. The old behavior was not a
lenient reading of an ambiguous reference; it was a confident wrong number that happened to be
reachable.

**What the right answer is.** There isn't one. A scalar reference names one value; the owner it names
has two occurrences and the model states no index. `comp_a[0]` and `comp_a[1]` are equally
defensible, and picking either would be the same class of invention the item exists to remove.

**The call.** Trading a confidently wrong number for a named refusal is exactly the item's declared
"fail loudly rather than fall back" intent (`plan.md:30`, design D5), and it is the intent's hardest
case rather than an exception to it. A silent answer here would corrupt a design search in the way
`P-001` cares about most: an LCOE result computed from a value the author never wrote, with nothing
in the output saying so. The refusal names the code, the count, and the consumer, so an author who
hits it can fix the model by writing the index.

**Blast radius, measured.** Zero in the tracked corpus. All 409 corpus sites produce an edge after
the repair and **no site anywhere gained a diagnostic** except this one, which lives in a fixture
this item authored as its own no-hidden-recovery negative. The 23 committed v6 snapshots are
byte-unchanged and none is stale. The full suite gained no failure. So the compatibility cost is
real but currently unrealized: the shape that refuses is *arrayed owner + unindexed scalar
reference*, and nothing tracked in this repository authors it except the fixture built to catch it.

**What an affected author sees.** A model that elaborated yesterday and contains that shape will now
raise `ElaborationDiagnosticError` in strict mode, or carry an `SI_OCCURRENCE_AMBIGUOUS` diagnostic
and an unbound consumer in lenient mode. Both are pinned by
`test_ambiguous_exact_owner_is_lenient_diagnostic_and_strict_refusal`. That is a real behavior
change and it is recorded here as one, not smuggled in as a repair.

**Residual worth the owner's eye (not a blocker).** The message says "consumer context contains 2
candidate occurrences". It is accurate and names the count, but it does not name the two candidates
or suggest the index syntax that resolves it. Improving it would be an author-experience change with
no semantic content, and this item's design forbids new diagnostic codes, so it is left alone and
noted here.

## What did not change

- **Identity.** Every occurrence wire ID, attribute node ID, calculation node ID, and constraint node
  ID compares equal across all **153** roots. Zero identity blocks differ. Feature slots are stable
  in the changed rows too: in all 19, only the occupancy step moved or a diagnostic became an edge —
  no slot changed.
- **Unaffected edges.** 404 of the 409 corpus sites are untouched.
- **Refused roots.** The same 15 corpus roots refuse for the same recorded reasons; none started or
  stopped refusing.
- **Deep-override lane.** 0 one-segment sites across every root that elaborated, before and after.
  Counted, not assumed — this is the standing D11 gap, measured again here.
- **Snapshots.** `phase5-snapshot-assessment.json`: **23 tracked, 23 assessed, 0 stale, 0 missing, 0
  extra, 0 duplicate**. Compared field by field against Phase 2's `before-snapshot-inventory.json`,
  the two documents differ in exactly **two** keys, `baseline_commit` and `git_status`, both
  describing the run rather than a snapshot. Every payload digest is byte-identical. No snapshot was
  recaptured and none was warranted.

## Validation — run at `a3b46dc`, reported exactly

**Focused files, together under the license** (`test_usage_owned_reference_anchoring.py`,
`test_source_identity_extraction.py`, `test_elaboration_public_mutation.py`,
`test_elaboration_graph_roundtrip.py`, `test_snapshot_v6_routes.py`,
`test_elaboration_fail_closed.py`, `tests/unit/test_elaboration_import_boundaries.py`):
**114 passed, 0 skipped, 0 failed.** Zero license-related skips.

**Each file independently:** 48, 14, 3, 14, 6, 15, 14 — all green, in that order.

**Full suite** (`uv run --extra dev pytest tests/ -rs -q`, saved to
`verification/after-phase5-full-suite.txt`): **17 failed, 2143 passed, 34 skipped, 88 deselected in
170.81s.**

- The failing node set is **identical** to the Phase-2 baseline's, name for name. All 17 are
  `ModuleNotFoundError: No module named 'pandas'` — environmental, pre-existing, untouched here.
- Passing nodes went 2080 → 2143. The +63 is fully accounted: 37 Phase-2 additions, 15 Phase-3
  repaired nodes, 11 Phase-4 additions.
- All 34 skips are golden-fixture skips. **Zero license-related skips**, so this is a real licensed
  run.

**`uv run --extra dev ruff check src/ tests/`: 131 findings. `uv run --extra dev mypy src/`: 52
errors.** Neither gate is clean project-wide and neither ever was. Both finding sets were captured
again at the item's start commit `2768c68` in a scratch worktree and diffed:

- ruff — **identical finding set**, line for line, 131 = 131.
- mypy — **identical finding set**, 52 = 52, and **zero** of them are in `src/sysml_codegen/elaboration/`.

So this item contributes no new finding to either gate, including from the thirteen fixtures and
five test files it added. The pre-existing backlog is out of scope and was not touched
(`plan.md:440-442` — do not absorb unrelated fixes). `ruff check` is clean on `verification/`.

## Spec success criteria — one retained test or evidence row each

| # | `spec.md` criterion | Evidence | State |
|---|---|---|---|
| 1 | Owner occurrence precedes leaf slot, across every shared resolver consumer | The seven combined-fixture lane nodes (`test_combined_*`) cover alias, alias-following calc input, computed attribute, calc input, constraint actual, inline predicate, and scalar `sum()`; `test_combined_named_source_reaches_every_and_only_its_consumers` pins the fan-out | met |
| 2 | u4 package sibling → `shared_component.length`, no diagnostic | `test_u4_package_sibling_binds_the_package_scoped_occurrence`; rows 1/6 | met |
| 3 | u5 named sibling → `plant.comp_a.length`, no ambiguity | `test_u5_named_sibling_binds_the_named_occurrence`; rows 2/7 | met |
| 4 | u6 cross-owner → `comp_a`, never `comp_b`, no fallback edge | `test_u6_cross_owner_consumer_binds_the_named_sibling`; row 3/8. Phase 3 also proved `_resolve_leaf` is invoked 0 times in u6's elaboration | met |
| 5 | u7 paired spellings → distinct nodes equal to their dot-path controls | `test_u7_paired_spellings_bind_distinct_nodes`, `test_u7_qualified_edges_equal_their_dot_path_controls`; rows 4/5 land on distinct occurrences | met |
| 6 | u1–u3b and definition/package/enum/feature-chain controls unchanged | `test_u1_…`, `test_u2_…`, `test_u3_arrayed_qualifier_remains_ambiguous`, `test_u3b_…`, `test_definition_owned_alias_leaf_keeps_the_consumer_local_edge`, `test_definition_owned_subset_leaf_keeps_the_consumer_local_edge`. Non-`PartUsage` owners are outside the ledger's population by construction, so their evidence is those nodes plus the unchanged full suite, not a ledger row | met |
| 7 | Kept qualified regressions cover alias, computed, constraint binding, predicate | Rows 11, 14, 16, 17 and their named test nodes. For alias and predicate these are the **sole** evidence, as the criterion states — the corpus has zero of each | met |
| 8 | Kept bare regression with discriminating topology | `usage_owner_bare_alias` + `test_bare_alias_discriminator_binds_the_aliased_owner`; row 18 shows consumer lineage and exact owner landing on **different** occurrences, so it cannot pass on a fan-out-of-one accident. D10 took route 1 on evidence, so no gap record attaches | met |
| 9 | Broader surface re-derived; every difference adjudicated | This document. 409 corpus + 16 promoted sites, 19 changed rows, zero unadjudicated | met |
| 10 | Public off-default mutation reaches every and only its consumers, live and round-trip | `test_usage_owned_public_mutation_reaches_every_and_only_its_consumers`, `test_usage_owned_anchoring_survives_the_codec_including_raw_alias_targets`, `test_usage_owned_anchoring_survives_capture_and_relocation` | met |
| 11 | Strict and lenient agree on semantic identity | `test_owner_anchoring_resolves_identically_in_strict_and_lenient` (6 fixtures), `test_ambiguous_exact_owner_is_lenient_diagnostic_and_strict_refusal`, `test_strict_readiness_halt_precedes_graph_diagnostic_rejection` | met |
| 12 | Feature slots, occurrence records, serialized occurrence IDs unchanged | Identity blocks equal across 153 roots; `test_attribute_node_ids_stay_derived_from_occurrence_and_slot` and `test_occurrence_records_stay_anchored_to_their_containment_slot`, parametrized over all 13 promoted roots | met |
| 13 | Every live-vs-snapshot difference classified; unaffected bytes unchanged | `phase4-snapshot-assessment.json` and `phase5-snapshot-assessment.json`: 0 stale, payloads byte-identical to the pre-repair inventory. No recapture, because D9's trigger never fired | met |
| 14 | Close-time check of the bounded self-binding spec locations | Checked and corrected below; **the final verifier remains `/_my_close`** | prepared, verified at close |

**Not evidenced, and deliberately so.** The **deep-override lane** carries the standing D11 gap
`deep override affected-shape coverage unproven`, open by owner disposition. The lane has 0
one-segment sites in the whole corpus, so nothing in the shipped tree exercises it. It is not a
success criterion, it is not claimed as covered anywhere above, and it must stay visible through
close.

## The bounded documentation obligation

The instruction (`spec.md:149-160`) bounds the inventory to
`.project/active/self-binding-replacement/spec.md:56` and its Success Criteria at `:66-70,74-78`.

**Checked against landed behavior.**

- **The F-6 bullet (`:53-61` after this edit; `:56` still lands on the F-6 sentence) had one mismatch
  and it is corrected.** It said the shipped elaborator
  "currently loses that owner before occurrence selection". That is now false: the repair landed at
  `98970c9`. The bullet now reads in the past tense, names the landing commit and file, and states
  that the shipped elaborator honors the exact usage owner SysIDE resolved. **It still names the
  behavior as codegen defect F-6 rather than the meaning of `::`**, which is what the criterion
  requires. The D-5 local-rename sentence and the D-7 cross-part path sentence are untouched, and the
  fusion-tea migration choice is untouched.
- **`:66-70`** — "Any D-6 explanation is checked against the landed exact-owner repair, not today's
  positional defect." Still correct as an instruction to that item, and now satisfiable. No change.
- **`:74-78`** — "it states that codegen honors the exact usage owner SysIDE resolved after the
  separate repair; it never presents positional slot search as the language semantics." Still correct
  and its precondition is now met. No change.

**Surfaced, out of bounds, not changed.** The same stale present tense survives at
`.project/active/self-binding-replacement/spec.md:132-139` — a `[HARD]` requirement saying "the
current one-segment resolver normalizes to a feature slot before using the owner and then selects by
consumer position". That is a landed-false claim in the same document, but it sits outside the
inventory this item was given, and the inventory was drawn deliberately. Flagged here for the close
stage or the owner rather than edited.

**The final verifier remains `/_my_close`.** This phase performed the check and the one bounded
correction; close re-verifies both locations against the tree as it stands then.

## Findings

- **No regression was found.** All 19 changed rows are fixes, including the one that trades an answer
  for a refusal, for the reasons recorded above.
- **No premise conflict surfaced.** Nothing contradicted the plan, the design, or the spec.
- Two items are recorded for an owner rather than resolved here: the ambiguity message's wording (see
  row 19), and the out-of-bounds stale `[HARD]` line in the self-binding spec (see above). Neither
  blocks close.
