# Implementation Plan: Exact Owner Anchoring for Usage-Owned One-Segment References

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-08-15 19:03 PDT
**Last Updated:** 2026-08-15 19:03 PDT
**Branch:** main (`2768c68` at plan start)
**Complexity:** MEDIUM

## Source Documents

- **Spec:** `.project/active/qualified-reference-occurrence-anchoring/spec.md`
- **Design:** `.project/active/qualified-reference-occurrence-anchoring/design.md`
- **Design review:** `.project/active/qualified-reference-occurrence-anchoring/design-review.md`
- **Bare-discriminator probe:**
  `.project/active/qualified-reference-occurrence-anchoring/spike/bare-discriminator-authorability/findings.md`
- **Project commands:** `CLAUDE.md`

## The Point

**[OWNER-VERBATIM, 2026-08-13]** The product seeks a design search where engineering design
parameters can be freely varied and viability and outcomes such as LCOE can be assessed, without
embedding engineering logic by predetermining free variables and backing into the rest.

That search is trustworthy only when one modeled source occurrence becomes exactly one runtime
source reaching every and only its bound consumers. Today, a one-segment reference can retain
SysIDE's exact leaf but discard its `PartUsage` owner. `comp_a::length` authored inside `comp_b` can
then wire silently to `comp_b.length`. This work must make the graph honor the exact usage owner,
fail loudly rather than fall back, and preserve occurrence, slot, and public identity everywhere
else. This carries the ELABORATE-FIRST owner-grade mission from the
[spec Problem](spec.md#problem) and the design's [The Point](design.md#the-point).

## Implementation Strategy

### Phasing Rationale

The sequence resolves evidence risk before code risk. Phase 1 settles the two authorability gates
that the reviewed design leaves open. Phase 2 makes the research fixtures durable, writes the red
conformance surface, and freezes the pre-repair corpus/snapshot state. Phase 3 changes one production
seam. Phase 4 proves that the internal edge reaches public and snapshot routes. Phase 5 adjudicates
the whole corpus and runs certification checks.

### Critical Path

`D10/D11 evidence disposition → durable red fixtures + before ledger → one resolver repair →
public/snapshot proof → corpus adjudication + close readiness`

No production edit begins until Phase 1 is complete. If either learning test ends in an unproven
coverage gap, stop for the owner disposition required by
[Key Decisions](design.md#key-decisions) before Phase 2.

### First Proof Point

The first proof is a Phase-1 result that says whether legal authored models can exercise D10 and
D11. The first code proof is u6 changing from its silent `comp_b.length` edge to
`comp_a.length` while its occurrence records and slot-derived node IDs stay unchanged.

### Overall Validation Approach

- Start every phase with a kept test, executable probe, or comparison assertion.
- Use typed `NodeRef`/`ProducerRef`, full diagnostics, and structured occurrence IDs as the oracle.
- Load `SYSIDE_LICENSE_KEY` before licensed tests and inspect `-rs` output for license skips.
- Compare post-change results with a captured pre-change ledger; do not rely on memory or research
  predictions.
- Run affected tests independently and run the full suite. Phase 2 captures the actual full-suite
  baseline, including any currently documented ordering-dependent failures; Phase 5 permits no new
  failure and requires every affected file to pass independently.

---

## Phase 1: Resolve Authored-Shape Evidence Gates

### Goal

Resolve D10's authored bare discriminator and D11's deep-literal-override affected shape before any
production work. This phase implements the evidence policy in
[Key Decisions](design.md#key-decisions) and
[Next-Stage Handoff](design.md#next-stage-handoff).

### Assumption Under Test

A legal SysML model can produce each required one-segment `PartUsage`-owned fact shape. If a bounded
search finds none, its result is a standing coverage gap, not proof of impossibility.

### Test Stencil — Write This First

```python
for candidate in authored_candidates:
    loaded, fact, consumer_scope = load_and_capture(candidate)
    assert fact is None or len(fact.segment_element_ids) == 1
    record(loaded, source_text(candidate), fact, live_owner(fact))
    if affected(fact):
        assert current_target(fact, consumer_scope) != owner_target(fact, consumer_scope)
```

### Changes Required

**See:** [the open premise](design.md#one-spec-premise-is-not-yet-established),
[Key Bets](design.md#key-bets), and [Potential Risks](design.md#potential-risks).

- [ ] Extend
  `.project/active/qualified-reference-occurrence-anchoring/spike/bare-discriminator-authorability/`
  into a bounded learning test over the legal scoping/redefinition candidates it names; preserve
  every model, command, load result, exact leaf/owner ID, and conclusion.
- [ ] Create
  `.project/active/qualified-reference-occurrence-anchoring/spike/deep-override-authorability/`
  with the same evidence shape for one-segment deep literal redefinitions. Include the resolver's
  `plural=True` call but judge the direct reference against the scalar policy.
  **Result (2026-08-15):** no affected shape found. The probe searched 15 authored candidates plus
  all 13 tracked fixture roots containing a chained redefinition — 51 live lane sites, every one
  two or three segments, so the one-segment branch is never reached. The lane's `plural=True` call
  is genuinely plural (an arrayed child writes both occurrences) but returns before `plural` is
  read on the one-segment path, so D4's scalar policy is untestable from this lane. Conclusion
  `authorability unproven`; dated gap `deep override affected-shape coverage unproven` recorded in
  `spike/deep-override-authorability/findings.md`. No fixture is promoted to Phase 2; the close
  disposition stays with the owner.
- [ ] If either search finds an authored affected shape, promote that exact model for Phase 2. If it
  does not, stop and obtain the owner disposition required by D10/D11; update `spec.md`, `design.md`,
  and the standing gap record only as that disposition authorizes.

### Validation

**Automated:**

- [ ] Run both retained probe drivers under the licensed environment; both exit normally and write
  no generated package or production file.
- [ ] Run `uv run --extra dev ruff check` on retained Python probe code.
- [ ] Confirm `git diff -- src/ tests/` is empty at the phase gate.

**Manual:**

- [ ] Verify each conclusion distinguishes “candidate falsified,” “affected shape found,” and
  “authorability unproven.”
- [ ] Verify a route-2 D10 disposition retains `authored bare discrimination unproven`, and a D11
  gap retains `deep override affected-shape coverage unproven`, through close.

**What We Know Works After This Phase:** The implementation has an owner-approved, reproducible
acceptance route for both open evidence questions, or it is intentionally stopped before code.

---

## Phase 2: Durable Fixtures, Red Tests, and Before-State Ledger

### Goal

Make every discriminating case durable and freeze the exact pre-repair graph, corpus, snapshot, and
full-suite state. The phase ends with expected red repair tests and passing controls.

### Assumption Under Test

One symmetric fixture can carry the qualified alias, computed, calculation, constraint-actual,
asserted-predicate, and scalar-direct-aggregation lanes without introducing unrelated readiness
findings.

### Test Stencil — Write This First

```python
graph = elaborate_fixture("u6_usage_qual_crossnamed", strict=False)
source = attr(graph, "plant.comp_a.length")
consumer = calc(graph, "plant.comp_b.area_calc")
assert only_input_edge(consumer) == NodeRef(source.node_id)  # red before repair
assert occurrence_records(graph) == frozen_occurrence_records["u6"]
assert exact_diagnostics(graph) == ()
```

### Changes Required

**See:** [Key Decisions](design.md#key-decisions) D2/D6–D8,
[Evidence and Snapshot Flow](design.md#evidence-and-snapshot-flow), and
[Validation Approach](design.md#validation-approach).

- [ ] Before adding red tests, run and record the licensed full-suite baseline, including exact
  failures and `-rs` skip reasons. Keep this result separate from the intentional red set below.
- [ ] Copy the tracked u1–u7 models, including u3b, from
  `.project/active/self-binding-replacement/spike/fixtures/` to same-named roots under
  `tests/fixtures/`. Preserve their bytes at copy time; the kept copies become the conformance
  authority.
- [ ] Add `tests/fixtures/usage_owned_reference_consumers/` for the combined qualified lanes and
  scalar `sum()` term. Add the Phase-1 bare/deep fixture only if that phase authorized one.
- [ ] Create `tests/conformance/test_usage_owned_reference_anchoring.py`. Pin u4–u7's exact typed
  outcomes, u1–u3b controls, unaffected owner/form controls, full diagnostics, plural singularity,
  occurrence records, and slot-derived node IDs. Use `tests/helpers/elaboration_graph.py:19-52` for
  readable lookup only; typed IDs remain the assertions.
- [ ] Extend `tests/conformance/test_source_identity_extraction.py:151-193` with
  `test_usage_owned_fact_owner_matches_live_part_usage`, asserting the frozen owner ID agrees with
  the exact live leaf owner and that the live owner is a `PartUsage`.
- [ ] Create
  `.project/active/qualified-reference-occurrence-anchoring/verification/corpus_compare.py` and a
  versioned `before.json`. Adapt the gitignored seed at
  `.project/active/self-binding-replacement/spike/out/bare_expression_side_scan.py` only for site
  discovery and typed actual capture. Do not carry its prospective resolver, plural forwarding, or
  missing deep-override accounting. Because the seed is ignored, the maintained verifier must be
  self-contained; if the seed is absent, reconstruct from the two cited research reports rather
  than blocking. Freeze the preexisting tracked-root set so newly copied regression fixtures do not
  inflate the corpus comparison.
- [ ] Record the tracked snapshot inventory and byte digests before repair using
  `scripts/assess_v6_snapshot_churn.py:57-81,234-357`; write the result under `verification/`.

### Validation

**Automated:**

- [ ] Run the new conformance file and record the exact expected red set: u4 missing, u5/u7
  ambiguous, u6 silently wrong, plus affected combined-fixture assertions. Controls must pass.
- [ ] Run the extraction guard; it passes before repair because it checks authority agreement, not
  the defective edge.
- [ ] Run the before-state verifier twice; canonical output is byte-identical and every tracked site
  has a typed edge, full diagnostic, or named structural no-edge reason.

**Manual:**

- [ ] Inspect the u6 failure to confirm it is the wrong typed target, not a load or fixture failure.
- [ ] Confirm `before.json` stores exact IDs and diagnostics; source spelling is classification
  metadata only.

**What We Know Works After This Phase:** The defect is reproduced on durable tests, every control
has a frozen before-state, and later phases cannot hide a changed occurrence or snapshot identity.

---

## Phase 3: Repair the Shared One-Segment Resolver

### Goal

Land the minimal production change at the one common policy seam. No caller, evidence schema,
occurrence index, slot index, graph model, projection path, or snapshot codec changes.

### Assumption Under Test

The existing owner contextualizer and occurrence-fixed slot target lookup compose into the required
owner → occurrence → leaf edge without changing cardinality or caller-owned alias behavior.

### Test Stencil — Write This First

```python
graph = elaborate_fixture("usage_owned_reference_consumers")
assert edge_for("qualified_sum_term", graph) == edge_for("comp_a.length", graph)
assert edge_count("qualified_sum_term", graph) == 1
assert raw_alias_target("qualified_alias", graph) == node_ref("comp_a.length", graph)
assert no_positional_fallback_diagnostic(graph)
```

### Changes Required

**See:** [Core Concept](design.md#core-concept), [Resolution Flow](design.md#resolution-flow),
[Required Invariants](design.md#required-invariants), and
[Implementation Notes](design.md#implementation-notes).

- [ ] Add the plural-caller/raw-alias stencil above to
  `tests/conformance/test_usage_owned_reference_anchoring.py` and confirm it is red for the target
  identity rather than for fixture syntax.
- [ ] Modify the one-segment branch at
  `src/sysml_codegen/elaboration/elaborate.py:2062-2076`: recover the exact live leaf and semantic
  owner, guard on live `PartUsage`, contextualize that owner with scalar cardinality, select the
  exact leaf slot at the selected occurrence, and require one typed target.
- [ ] Reuse `elaborate.py:2119-2219` and `elaborate.py:2350-2366`. Preserve the existing
  `_resolve_leaf` route for all other owner kinds. Do not add fallback, resolver-level alias
  following, or a new diagnostic code.

### Validation

**Automated:**

- [ ] Run `test_usage_owned_reference_anchoring.py` and
  `test_source_identity_extraction.py`; all Phase-2 red tests are green and controls remain green.
- [ ] Run `tests/unit/test_elaboration_import_boundaries.py:189-215`; the new branch introduces no
  name, qualified-name, path-prefix, or first-match authority.
- [ ] Run Ruff on `elaborate.py` and the touched tests; run focused mypy on `elaborate.py`.

**Manual:**

- [ ] Inspect u4–u7 typed edges and full diagnostics. Confirm u6 has no residual edge to
  `comp_b.length` and no recovery path was invoked.
- [ ] Compare Phase-2 occurrence records and node IDs byte-for-byte with the repaired graphs.

**What We Know Works After This Phase:** Every shared resolver caller inherits exact usage-owner
anchoring through one production seam, while identity construction and unaffected forms are stable.

---

## Phase 4: Public Mutation, Strict/Lenient, and Snapshot Routes

### Goal

Prove that the repaired internal edge is the same source seen by public generation and snapshot
round trips, and expose any stale committed snapshot before recapture.

### Assumption Under Test

Projection and codecs consume final typed edges mechanically, including raw alias targets that
`InstanceGraph.semantic_edges()` omits.

### Test Stencil — Write This First

```python
baseline, changed = live_and_roundtrip_routes("usage_owned_reference_consumers")
assert typed_consumers(baseline, "comp_a.length") == EXPECTED_CONSUMERS
assert typed_consumers(changed, "comp_a.length") == EXPECTED_CONSUMERS
assert alias_targets(roundtrip(changed)) == alias_targets(changed)
assert changed_public_defaults(baseline, changed) == {"comp_a.length"}
assert unchanged_sources(baseline, changed)
```

### Changes Required

**See:** [Evidence and Snapshot Flow](design.md#evidence-and-snapshot-flow),
[Failure Behavior](design.md#failure-behavior), and
[Validation Approach](design.md#validation-approach).

- [ ] Extend `tests/conformance/test_elaboration_public_mutation.py:136-184` with the combined
  fixture. Assert every and only calculation, alias/computed, constraint, predicate, and aggregation
  consumer, plus the single changed public default.
- [ ] Extend `tests/conformance/test_elaboration_graph_roundtrip.py:32-47,202-218` or the focused
  conformance file to compare the full decoded graph and raw alias targets, not only
  `semantic_edges()`.
- [ ] Add temporary capture/relocation coverage following
  `tests/conformance/test_snapshot_v6_routes.py:52-87,118-143`; do not enroll new fixtures in the
  committed v6 batch solely for this test.
- [ ] Add strict/lenient parity cases following
  `tests/conformance/test_elaboration_fail_closed.py:24-92`. Keep owner-resolution controls free of
  unrelated readiness findings; test `_finish_readiness`'s earlier strict halt separately.
- [ ] Run live-versus-committed assessment before touching snapshots. If a changed stored edge is
  found, retain the exact stale typed-edge comparison, then recapture only that classified fixture.

### Validation

**Automated:**

- [ ] Run the public mutation, graph round-trip, v6 route, fail-closed, and owner-anchoring files
  together under the license; all pass with no license-related skip.
- [ ] Run `scripts/assess_v6_snapshot_churn.py` and compare its tracked set and unchanged fixture
  payloads with Phase 2.

**Manual:**

- [ ] Confirm the projected/generated source names are checked only as public compatibility output;
  typed graph identity made every semantic decision.
- [ ] If recapture occurred, verify the retained pre-recapture diff names the changed consumer edge
  and that unrelated snapshot bytes remain identical.

**What We Know Works After This Phase:** A mutation of the named source reaches exactly the intended
public consumers on live and rebuilt routes, and snapshot handling is classified rather than broad.

---

## Phase 5: Corpus Adjudication and Certification

### Goal

Re-derive the full affected surface from the shipped resolver, adjudicate every difference, run
project quality checks, and prepare the bounded documentation verification for close.

### Assumption Under Test

The repaired route produces the five predicted qualified fixes, no unclassified bare change, no
occurrence/wire change, and no unrelated regression. Predictions are not acceptance evidence.

### Test Stencil — Write This First

```python
before = load_ledger("before.json")
after = capture_from_shipped_resolver()
assert site_keys(after) == site_keys(before)
assert all(row.edge or row.diagnostic or row.no_edge_reason for row in after)
assert occurrence_records(after) == occurrence_records(before)
assert unadjudicated_differences(before, after) == []
```

### Changes Required

**See:** [Integration Strategy](design.md#integration-strategy),
[Validation Approach](design.md#validation-approach), and
[spec Success Criteria](spec.md#success-criteria).

- [ ] Produce canonical `verification/after.json` from the shipped resolver and
  `verification/adjudication.md`. For every changed edge or diagnostic, record fix/regression,
  topology, exact before/after identity, and reasoning. Leave zero unadjudicated rows.
- [ ] Compare occurrence records, slot-derived node IDs, snapshot digests, and unaffected edges with
  the Phase-2 artifacts. Update only a snapshot already classified in Phase 4.
- [ ] Check `.project/active/self-binding-replacement/spec.md:56,66-70,74-78` against landed
  behavior. Correct a mismatch only within the spec's bounded instruction; do not change D-5/D-7
  guidance or fusion-tea migration. Record that the final verifier remains `/_my_close`.
- [ ] Update this plan's completion notes and checkboxes with actual commands, counts, deviations,
  standing gaps, and snapshot dispositions.

### Validation

**Automated:**

- [ ] With `SYSIDE_LICENSE_KEY` loaded, run the focused owner-anchoring, extraction, public mutation,
  graph-roundtrip, snapshot-v6, fail-closed, and import-boundary files; all pass independently.
- [ ] Run `uv run --extra dev ruff check src/ tests/` and `uv run --extra dev mypy src/`.
- [ ] Run `uv run --extra dev pytest tests/ -rs`. Compare with the Phase-2 full-suite baseline:
  zero new failures, every touched/affected file green independently, and no license-related skip.

**Manual:**

- [ ] Reconcile every spec success criterion with one retained test or evidence row. Do not check SC8
  or the deep-override lane as fully evidenced if its standing gap remains open.
- [ ] Confirm only `elaborate.py` changed in production and no evidence, occurrence, slot, graph,
  projection, or codec schema was widened.

**What We Know Works After This Phase:** The shipped resolver is certified against durable focused
tests, public/snapshot behavior, a fully adjudicated corpus, stable identities, and the bounded
documentation obligation.

---

## Environment Setup

Use the repository environment and commands from `CLAUDE.md`:

```bash
set -a
source ../agentic-mbse/.env
set +a
uv run --extra dev pytest <targets> -rs
```

- The companion checkout must remain at `../agentic-mbse`; no dependency or schema edit is planned.
- Do not interpret an unlicensed skip as passing evidence.
- Preserve the existing user-owned changes in `product-lens.md`, `design-review.md`, `design.md`, and
  the retained bare probe while implementing this plan.

## Risk Management

See [Potential Risks](design.md#potential-risks) for the full analysis.

- **Phase 1 — unprovable authored shape:** stop for owner disposition; never label a bounded search
  as impossibility proof.
- **Phase 2 — fixture syntax masks the defect:** require successful load and exact current typed
  outcome before treating a red assertion as the intended failure.
- **Phase 2/5 — verifier becomes a second resolver:** capture shipped actuals only; source text is a
  site/classification key, never an edge authority.
- **Phase 3 — cardinality drift:** force scalar one-segment owner selection and pin direct `sum()`.
- **Phase 3 — hidden positional recovery:** make owner-selection failure final and retain negative
  ambiguity/missing controls.
- **Phase 4 — snapshot churn:** expose a stale typed edge before recapture and change only its
  classified snapshot.
- **Phase 5 — unrelated suite failures:** compare with the pre-change baseline and keep all affected
  files independently green rather than absorbing unrelated fixes into this item.

## Implementation Notes

### Phase 1 Completion

**Completed:**
**Actual Changes:**
**Issues:**
**Deviations:**

### Phase 2 Completion

**Completed:**
**Actual Changes:**
**Issues:**
**Deviations:**

### Phase 3 Completion

**Completed:**
**Actual Changes:**
**Issues:**
**Deviations:**

### Phase 4 Completion

**Completed:**
**Actual Changes:**
**Issues:**
**Deviations:**

### Phase 5 Completion

**Completed:**
**Actual Changes:**
**Issues:**
**Deviations:**

---

**Status:** Draft → In Progress → Complete
**Next Step:** After plan approval, run `/_my_implement` from Phase 1. Use `/_my_audit` after all
phases pass; the bounded self-binding verification completes in `/_my_close`.
