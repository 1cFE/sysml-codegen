# Spec Review: Canonical Usage Domain and Catalog Totality (CONSTRAINT-SEMANTICS Item 2)

**Spec:** `.project/active/constraint-catalog-totality/spec.md`
**Contract:** `claude-pack/commands/_my_spec.md`
**Review File:** `.project/active/constraint-catalog-totality/spec-review.md`
**Date:** 2026-08-12

---

## Reality Check

**Sound.** The spec is about the right work item, the Problem section is materially accurate, and
every code-facing claim I checked holds. `_scopes_for_owner` really has no `CalculationDefinition`
branch (`elaboration/elaborate.py:522-539`); `_build_constraint_nodes` really emits one node per
returned scope and nothing for zero scopes (`elaborate.py:997-1017`); REQ-EXT-09 really reads PASS
(`docs/architecture/verification-matrix.md:336`) and REQ-CL-04 PARTIAL (`:214`); the codec really
fingerprints the whole document and refuses an unknown schema (`snapshot/instance_graph.py:88,
907, 927-932`, version constant `instance-graph/v2` at `:68`) and really refuses a constraint
record whose identity fields disagree (`:771-776`); the two Item 1 forward pointers are exactly
where the spec says (`docs/architecture/modeling-assumptions.md:476-477`, `:489-496`); the tree
holds 21 `instance_graph_snapshot.json` fixtures. All seven epic Item 2 success criteria are
carried, plus one honestly-marked `[AGENT]` addition. All five product-lens dispositions
(spec-F1..F5) are visible in the text.

Design would not be badly misled by this spec. It would, however, hit one requirement that cannot
be met as literally written (L1-1), one requirement that its own Open Questions contradicts
(L3-1), and two obligations that no success criterion would catch if dropped (L3-2). Revise.

---

## Audit

### Lens 1 — Faithfulness

**L1-1 · Direct claim:** The form-classification requirement (`spec.md:105-109`) is wrong about
what the exact route actually classifies, and the error is load-bearing for the Q7 obligation.

Three problems in one sentence:

- It cites `agentic_mbse/sysml/constraint_extraction.py:703-723`. The classifier the *exact
  route* uses is in this repo, at `elaboration/elaborate.py:1119-1137`. The cited module is the
  legacy constraint-fact extraction path — the same dual pass ELABORATE-FIRST Item 7 scope 2 is
  deleting (`epic_elaborate_first_architecture.md:444`). Building the canonical domain against
  the module that is being deleted is exactly the failure mode the item exists to prevent.
- It says "the five source forms" and then lists six tokens. The exact route emits exactly five:
  `requirement_constraint`, `named_usage_reference`, `definition_typed`, `inline`, and the
  `plain_usage` fall-through (`elaborate.py:1126-1137`).
- The extra token is `satisfy` — and there is no `satisfy` source form anywhere in the exact
  route (zero hits for `satisfy` in `elaborate.py`; the only sibling vocabulary is
  `collect_constraint_manifest`'s assert→satisfy→requirement→plain *kind* ladder,
  `extraction/extractor.py:101-108`, which is a different vocabulary on the sweep this item is
  retiring or demoting).

Why it matters beyond a citation fix: the umbrella spec's Q7 ruling requires `satisfy` to receive
a **named visible exclusion** (`constraint-semantics-contract/spec.md:159-162`), and REQ-EXT-09
already names "a named requirement/satisfy exclusion" as an admissible carrier. But a
`SatisfyRequirementUsage` reaching `_constraint_metadata` today takes the `else` branch and comes
out as `plain_usage` — indistinguishable from a bare `constraint`. So "form classification is
**preserved** on every domain member" understates the work: satisfy has to be *newly*
distinguished, not preserved. As written the requirement reads as free, and design could
reasonably believe it is.

**L1-2 · Rewrite request:** The same requirement is tagged `[INHERITED: umbrella spec, Modeling
policy (Q1, Q7)]`. Q1 is assert-only enforcement; Q7 is requirement-side forms staying
non-executable and visible. Neither states that owner kind, owner QN, source file, and source line
are preserved on every domain member. The real sources are epic Item 2 scope 1 ("Preserve exact
declaration identity and form classification") and contract invariant 28's carried-field list
(`contract:221-231`). Cite what actually supports it; an `[INHERITED]` whose source does not
contain the claim is an `[INFERRED]` wearing a borrowed grade.

**L1-3 · Rewrite request:** `spec.md:88` writes `D-3 owner-verbatim "no second catalog
authority"`. D-3's owner-verbatim text is *"100% Option A. We need to purge this mess."*
(`contract:503`). "No second catalog authority" is an accurate *paraphrase of D-3's consequence*
(see `contract:825`), but it is presented inside quotation marks next to the words
"owner-verbatim." This is inherited verbatim from the umbrella spec, so it is not this author's
invention — but the item's own product-lens ledger quotes D-3 correctly
(`product-lens.md:20-21`), so the corrected form is one line away. Capture-fidelity law 1: a quote
claimed as verbatim has to appear.

**L1-4 · Direct claim:** The parked REQ-EXT-09 boundary discrepancy (`spec.md:115-121`) describes
half the fact. The spec says today's row "sweeps `ConstraintUsage` including subtypes but excludes
`RequirementUsage` and its `satisfy` subtype," in tension with Q7. Read the row in full
(`01-extraction.md:20`): it excludes those subtypes from the swept *domain* and then lists "a
named requirement/satisfy exclusion" as an admissible *carrier*. The row contradicts itself. The
conflict design has to resolve is therefore internal to REQ-EXT-09, not row-versus-ruling — and
the fix is likelier to be a row rewrite than a domain-boundary decision. Parking is the right
move; park the whole fact.

**L1-5 · Question to the user:** The Success Criteria header (`spec.md:54-56`) declares every entry
`[INHERITED: epic Item 2 / constraint-semantics-contract/spec.md]` unless marked otherwise. Two
things ride on that blanket. First, criterion 6 adds "and each row's grade matches its evidence,"
which appears in neither source — it is a reasonable inference, but it is inheriting a grade it
did not earn. Second, the `A / B` slash leaves it unstated which source each criterion came from,
which is what an `[INHERITED]` citation exists to record. **Do you want per-entry citations here,
or is the blanket acceptable given both sources are in Required Reading?**

### Lens 2 — Problem & Approach

**L2-1 · If-then tradeoff:** The 21-vs-37 fixture discrepancy is surfaced honestly
(`spec.md:185-189`), but the requirement text quietly picks a side: "the obligation is one
reviewed recapture covering **every snapshot fixture in the tree**." That is the 21 reading.

The mundane explanation is visible in the source and the spec does not offer it: 37 is the
**corpus row count** (`epic_elaborate_first_architecture.md:302` — "All 37 fixtures have
live-checked route outcomes"; `:378` — "corpus 37/37"), while the tree holds 96 fixture
directories of which 21 carry an `instance_graph_snapshot.json`. So:

- **If** the Item 7 obligation means "recapture every snapshot that exists," 21 is right and the
  spec's wording is correct — say so and close it.
- **If** it means "the 37-row corpus must be snapshot-covered," then 16 corpus fixtures are
  *missing* snapshots and this item's recapture scope grows, which is a real scope change, not a
  count-recording detail.

Parking a number is fine. Parking it while the requirement text resolves it in one direction is
not. Either surface the corpus-versus-snapshot-subset explanation and let design settle it, or
state plainly that the narrower reading is provisional.

**L2-2 · Question to the user:** The spec forbids a second inventory, puts the gate on graph +
embedded catalog (`spec.md:88-92`), gives the manifest sweep an explicit fate of *retired or
test-side oracle* (`:93-99`), and separately requires the gate's evidence to be independent of the
gate (`:164-166`). Those three are in tension if the manifest is retired: `collect_constraint_manifest`
is the only existing independent enumeration of the authored population, it has no non-test caller
in `src/` today (grep: definition at `extraction/extractor.py:98`, a docstring mention at
`extraction/constraint_report.py:3`, all other hits in `tests/conformance/test_extractor.py`), and
both requirement rows plus `modeling-assumptions.md:489-492` define the population *by* it.
**If the manifest retires, what plays the independent oracle for the totality tests?** The spec
leaves design free to discover late that "retire it" and "prove totality independently" cannot both
be chosen. Naming the candidate — or naming this as the coupling design must resolve first — is
cheap here and expensive later.

### Lens 3 — Pipeline Risk

**L3-1 · Direct claim:** The spec contradicts itself on the vacuous-advisory ruling. The severity
requirement states it as settled: "Per invariant 61 and LC-E13 that advisory is emitted by
authoring validation at warning grade; this item implements that, **it does not reopen it**"
(`spec.md:136-138`). The Open Questions section then reopens it, on both axes: "Where the
authoring advisory surfaces for the vacuous case (elaboration diagnostic stream versus authoring
validation in the companion repo), **and at what grade it is recorded**" (`:245-246`). Invariant
61 fixes both the surface and the grade (`contract:476-481`). The spec-side disposition record for
spec-F1 says the question was "narrowed to which surface emits it, not whether the ruling stands"
(`product-lens.md:130-132`) — the narrowing landed in the requirement but not in the question. As
written, design gets a settled ruling and a live question about the same thing.

**L3-2 · Direct claim:** Two obligations have no success criterion that would fail if they were
dropped.

- The `[NEED]` doc-correction obligation (`spec.md:204-209`) — correcting
  `modeling-assumptions.md:476-477` and `:489-496` before confirmation tests run. This is the
  owner-directed sequencing rule and the product-lens spec-F2 disposition. No criterion mentions
  documentation. Criterion 7 covers tests, lint, types, and diffs; none of those catch a shipped
  doc still describing pre-landing behavior — which is precisely the ledger's own falsifier
  (`product-lens.md:34-36`).
- The manifest-sweep fate requirement (`spec.md:93-99`). "Leaving it unowned is not [design's
  call]" is stated in the requirement, but nothing in Success Criteria would notice if it stayed
  unowned.

Both need a criterion, or an explicit note that they are verified by review rather than by a
criterion.

**L3-3 · Rewrite request:** The headline number and the parked boundary question interact and the
spec does not say how. Criterion 1 promises "exactly **65** usage carriers"; the domain-boundary
requirement (`spec.md:115-121`) leaves open whether `RequirementUsage`/`satisfy` join the domain.
A reader cannot tell whether resolving that question moves 65. It does not — the item's own
product-lens verified that `catf_mfe_d5` authors no `satisfy` and no requirement usage
(`product-lens.md:112-115`) — but that fact lives only in the ledger. Put it in the spec, next to
either the criterion or the parked question. A parked question that visibly cannot move the
headline number is clean parking; one that might is a hole.

**L3-4 · Direct claim:** The three disposition kinds are spelled two ways in the authority and the
spec silently picks one. Epic Item 2 scope 2 says "**executable**, excluded with reason, or
non-reaching with reason" (`epic:289-290`); contract invariant 28 and the umbrella spec say
"**eligible**, excluded-with-reason, or non-reaching-with-reason" (`contract:223-224`). The spec
uses `eligible` (`spec.md:125-127`) — which matches the contract and the existing
`Eligibility` field on `ConstraintNode` (`elaboration/graph.py:201`), so it is almost certainly
right. But token spellings are explicitly deferred to design (`spec.md:242-244`), and design will
rediscover this divergence. One line recording that the epic's `executable` and the contract's
`eligible` name the same kind, with the contract governing, saves that.

### Lens 4 — Hygiene

No material findings. Citations are dense but they resolve; the one that does not is L1-1's, which
is a faithfulness problem, not a hygiene one.

### Lens 5 — Reader Comprehension

**L5-1 · Rewrite request:** "Carrier" is the spec's headline unit — "exactly **65** usage
carriers," "removing or duplicating any carrier" — and it is never defined. The spec elsewhere uses
"domain member," "usage-tier record," and "disposition" for what appear to be the same or adjacent
things. A reader has to reverse-engineer whether a carrier is the record, the disposition, or the
pair, and the completeness diagnostic's contract depends on which. Define it once, on first use in
Success Criteria, in plain words, and use one term after that.

---

## Engagement Summary

**Overall take:** The spec is faithful to the settled rulings, carries all seven inherited success
criteria, applies all five product-lens dispositions, and every code claim I spot-checked holds.
The defects are targeted, not structural: one requirement is written against the wrong (and
soon-to-be-deleted) classifier and understates real work, the Open Questions section reopens a
ruling the spec's own requirement declares closed, and two obligations have no criterion that
would catch their omission.

**Here's what I need you to weigh in on:**

1. **[L1-1]** Form classification points at the companion repo's legacy extraction module, not the
   exact route's classifier (`elaborate.py:1119-1137`), miscounts the forms, and lists a `satisfy`
   form that does not exist — today satisfy collapses to `plain_usage`. Q7's named satisfy
   exclusion is new work, not preservation. This one changes what design has to build.
2. **[L3-1]** The advisory's home and grade are stated as settled in the severity requirement and
   reopened in Open Questions. Pick one — invariant 61 already picked.
3. **[L2-2]** If the manifest sweep retires, nothing obvious remains to serve as the independent
   totality oracle the spec requires. Worth naming the coupling before design commits.
4. **[L2-1]** The 21-vs-37 parking resolves itself in the requirement text. The likely explanation
   (37 = corpus rows, 21 = snapshot-bearing subset of 96 fixture dirs) is in the sources and
   unstated here; if the corpus reading wins, this item's recapture scope grows by 16 fixtures.
5. **[L3-2]** No success criterion covers the doc-correction obligation or the manifest's fate —
   including the doc correction that is the product-lens ledger's own falsifier.
6. **[L3-3, L5-1]** The "exactly 65" headline rests on a term the spec never defines
   ("carrier") and sits next to a parked boundary question the spec never says is harmless to it
   (it is — the ledger checked).

---

## Resolutions

_To be filled in as findings are resolved. One entry per finding, keyed by ID._

---

**Verdict:** Revise
**Next Steps:** Record resolutions above, then re-run `/_my_spec` (or return to the spec-agent
session) pointed at this review to incorporate. The reviewer does not edit the spec. Nothing here
blocks moving to `/_my_design` on the underlying work item — the findings are corrections to the
contract's text, not to its direction.
