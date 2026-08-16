# Implementation Plan: Exact Owner Anchoring for Usage-Owned One-Segment References

**Status:** Complete — certified 2026-08-15 (`audit.md`, verdict Certify)
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

- [x] Extend
  `.project/active/qualified-reference-occurrence-anchoring/spike/bare-discriminator-authorability/`
  into a bounded learning test over the legal scoping/redefinition candidates it names; preserve
  every model, command, load result, exact leaf/owner ID, and conclusion.
- [x] Create
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
- [x] If either search finds an authored affected shape, promote that exact model for Phase 2. If it
  does not, stop and obtain the owner disposition required by D10/D11; update `spec.md`, `design.md`,
  and the standing gap record only as that disposition authorizes.

### Validation

**Automated:**

- [x] Run both retained probe drivers under the licensed environment; both exit normally and write
  no generated package or production file.
- [x] Run `uv run --extra dev ruff check` on retained Python probe code.
- [x] Confirm `git diff -- src/ tests/` is empty at the phase gate.

**Manual:**

- [x] Verify each conclusion distinguishes “candidate falsified,” “affected shape found,” and
  “authorability unproven.”
- [x] Verify a route-2 D10 disposition retains `authored bare discrimination unproven`, and a D11
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

- [x] Before adding red tests, run and record the licensed full-suite baseline, including exact
  failures and `-rs` skip reasons. Keep this result separate from the intentional red set below.
- [x] Copy the tracked u1–u7 models, including u3b, from
  `.project/active/self-binding-replacement/spike/fixtures/` to same-named roots under
  `tests/fixtures/`. Preserve their bytes at copy time; the kept copies become the conformance
  authority.
- [x] Add `tests/fixtures/usage_owned_reference_consumers/` for the combined qualified lanes and
  scalar `sum()` term. Add the Phase-1 bare/deep fixture only if that phase authorized one.
- [x] Create `tests/conformance/test_usage_owned_reference_anchoring.py`. Pin u4–u7's exact typed
  outcomes, u1–u3b controls, unaffected owner/form controls, full diagnostics, plural singularity,
  occurrence records, and slot-derived node IDs. Use `tests/helpers/elaboration_graph.py:19-52` for
  readable lookup only; typed IDs remain the assertions.
- [x] Extend `tests/conformance/test_source_identity_extraction.py:151-193` with
  `test_usage_owned_fact_owner_matches_live_part_usage`, asserting the frozen owner ID agrees with
  the exact live leaf owner and that the live owner is a `PartUsage`.
- [x] Create
  `.project/active/qualified-reference-occurrence-anchoring/verification/corpus_compare.py` and a
  versioned `before.json`. Adapt the gitignored seed at
  `.project/active/self-binding-replacement/spike/out/bare_expression_side_scan.py` only for site
  discovery and typed actual capture. Do not carry its prospective resolver, plural forwarding, or
  missing deep-override accounting. Because the seed is ignored, the maintained verifier must be
  self-contained; if the seed is absent, reconstruct from the two cited research reports rather
  than blocking. Freeze the preexisting tracked-root set so newly copied regression fixtures do not
  inflate the corpus comparison.
- [x] Record the tracked snapshot inventory and byte digests before repair using
  `scripts/assess_v6_snapshot_churn.py:57-81,234-357`; write the result under `verification/`.

### Validation

**Automated:**

- [x] Run the new conformance file and record the exact expected red set: u4 missing, u5/u7
  ambiguous, u6 silently wrong, plus affected combined-fixture assertions. Controls must pass.
- [x] Run the extraction guard; it passes before repair because it checks authority agreement, not
  the defective edge.
- [x] Run the before-state verifier twice; canonical output is byte-identical and every tracked site
  has a typed edge, full diagnostic, or named structural no-edge reason.

**Manual:**

- [x] Inspect the u6 failure to confirm it is the wrong typed target, not a load or fixture failure.
- [x] Confirm `before.json` stores exact IDs and diagnostics; source spelling is classification
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

- [x] Add the plural-caller/raw-alias stencil above to
  `tests/conformance/test_usage_owned_reference_anchoring.py` and confirm it is red for the target
  identity rather than for fixture syntax.
- [x] Modify the one-segment branch at
  `src/sysml_codegen/elaboration/elaborate.py:2062-2076`: recover the exact live leaf and semantic
  owner, guard on live `PartUsage`, contextualize that owner with scalar cardinality, select the
  exact leaf slot at the selected occurrence, and require one typed target.
- [x] Reuse `elaborate.py:2119-2219` and `elaborate.py:2350-2366`. Preserve the existing
  `_resolve_leaf` route for all other owner kinds. Do not add fallback, resolver-level alias
  following, or a new diagnostic code.

### Validation

**Automated:**

- [x] Run `test_usage_owned_reference_anchoring.py` and
  `test_source_identity_extraction.py`; all Phase-2 red tests are green and controls remain green.
- [x] Run `tests/unit/test_elaboration_import_boundaries.py:189-215`; the new branch introduces no
  name, qualified-name, path-prefix, or first-match authority.
- [x] Run Ruff on `elaborate.py` and the touched tests; run focused mypy on `elaborate.py`.

**Manual:**

- [x] Inspect u4–u7 typed edges and full diagnostics. Confirm u6 has no residual edge to
  `comp_b.length` and no recovery path was invoked.
- [x] Compare Phase-2 occurrence records and node IDs byte-for-byte with the repaired graphs.

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

- [x] Extend `tests/conformance/test_elaboration_public_mutation.py:136-184` with the combined
  fixture. Assert every and only calculation, alias/computed, constraint, predicate, and aggregation
  consumer, plus the single changed public default.
- [x] Extend `tests/conformance/test_elaboration_graph_roundtrip.py:32-47,202-218` or the focused
  conformance file to compare the full decoded graph and raw alias targets, not only
  `semantic_edges()`.
- [x] Add temporary capture/relocation coverage following
  `tests/conformance/test_snapshot_v6_routes.py:52-87,118-143`; do not enroll new fixtures in the
  committed v6 batch solely for this test.
- [x] Add strict/lenient parity cases following
  `tests/conformance/test_elaboration_fail_closed.py:24-92`. Keep owner-resolution controls free of
  unrelated readiness findings; test `_finish_readiness`'s earlier strict halt separately.
- [x] Run live-versus-committed assessment before touching snapshots. If a changed stored edge is
  found, retain the exact stale typed-edge comparison, then recapture only that classified fixture.

### Validation

**Automated:**

- [x] Run the public mutation, graph round-trip, v6 route, fail-closed, and owner-anchoring files
  together under the license; all pass with no license-related skip.
- [x] Run `scripts/assess_v6_snapshot_churn.py` and compare its tracked set and unchanged fixture
  payloads with Phase 2.

**Manual:**

- [x] Confirm the projected/generated source names are checked only as public compatibility output;
  typed graph identity made every semantic decision.
- [x] If recapture occurred, verify the retained pre-recapture diff names the changed consumer edge
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

- [x] Produce canonical `verification/after.json` from the shipped resolver and
  `verification/adjudication.md`. For every changed edge or diagnostic, record fix/regression,
  topology, exact before/after identity, and reasoning. Leave zero unadjudicated rows.
- [x] Compare occurrence records, slot-derived node IDs, snapshot digests, and unaffected edges with
  the Phase-2 artifacts. Update only a snapshot already classified in Phase 4.
- [x] Check `.project/active/self-binding-replacement/spec.md:56,66-70,74-78` against landed
  behavior. Correct a mismatch only within the spec's bounded instruction; do not change D-5/D-7
  guidance or fusion-tea migration. Record that the final verifier remains `/_my_close`.
- [x] Update this plan's completion notes and checkboxes with actual commands, counts, deviations,
  standing gaps, and snapshot dispositions.

### Validation

**Automated:**

- [x] With `SYSIDE_LICENSE_KEY` loaded, run the focused owner-anchoring, extraction, public mutation,
  graph-roundtrip, snapshot-v6, fail-closed, and import-boundary files; all pass independently.
- [x] Run `uv run --extra dev ruff check src/ tests/` and `uv run --extra dev mypy src/`.
- [x] Run `uv run --extra dev pytest tests/ -rs`. Compare with the Phase-2 full-suite baseline:
  zero new failures, every touched/affected file green independently, and no license-related skip.

**Manual:**

- [x] Reconcile every spec success criterion with one retained test or evidence row. Do not check SC8
  or the deep-override lane as fully evidenced if its standing gap remains open.
- [x] Confirm only `elaborate.py` changed in production and no evidence, occurrence, slot, graph,
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

**Completed:** 2026-08-15, licensed environment, commits `7673bf9` (D11) and `d78c42e` (D10). The
narrative below was reconstructed at audit time from the retained evidence — the implementing
session left this block a stencil while filling every other phase's. The work itself was verified,
not assumed: `/_my_audit` re-ran both probe drivers under the license (exit 0 each, `git status`
clean afterwards), re-ran `ruff check` on the retained probe code (passes), and confirmed
`git diff --stat 2768c68 d78c42e -- src/ tests/` is empty, so the phase gate held.

**Actual Changes:**

- `spike/bare-discriminator-authorability/` — extended into a 14-candidate bounded sweep
  (`sweep.py`) over legal scoping and redefinition shapes, with `findings.md` recording each
  model, load result, exact leaf/owner ID, and conclusion. **Result: affected shape found.** Nine
  of fourteen candidates discriminate, across two independent legal families (`alias` and
  `import`) and four consumer lanes. D10 route 1 is therefore available on evidence and SC8 is
  authorable as written; bet B3 is confirmed. `c01-alias-parent-scope` was recommended and later
  promoted as `tests/fixtures/usage_owner_bare_alias`.
- `spike/deep-override-authorability/` — `probe.py`, `probe-output.txt`, `findings.md`, and 15
  authored candidates. **Result: no affected shape found**, over 15 candidates plus all 13 tracked
  fixture roots carrying a chained redefinition (51 live lane sites, every one two or three
  segments). Dated gap `deep override affected-shape coverage unproven` recorded; no fixture
  promoted; the close disposition stays with the owner.

**Issues:** None. Neither probe touched `src/` or `tests/`, and neither search was labelled an
impossibility proof — the D11 conclusion is `authorability unproven`, which is what the risk note
requires.

**Deviations:** None from the phase as planned. The one substantive outcome the plan allowed for —
a search that finds nothing — occurred on the D11 side and took the disposition route D11 names.

### Phase 2 Completion

**Completed:** 2026-08-15, licensed environment (`set -a; source ../agentic-mbse/.env; set +a`),
branch `main` at `d78c42e`. No file under `src/` was touched — `git diff -- src/` is empty.

**Actual Changes:**

*Fixtures (13 new roots under `tests/fixtures/`)*

- Copied byte-for-byte from `.project/active/self-binding-replacement/spike/fixtures/` to
  same-named roots: `u1_usage_qual_self`, `u2_usage_qual_two_owner_occ`,
  `u3_usage_qual_multi_occ`, `u3b_usage_qual_single_occ`, `u4_usage_qual_pkg_sibling`,
  `u5_usage_qual_named_sibling`, `u6_usage_qual_crossnamed`, `u7_both_spellings`. Verified with
  `diff` against their sources.
- Copied byte-for-byte from the Phase-1 bare-discriminator learning test: `usage_owner_bare_alias`
  (from `c01-alias-parent-scope`, the authorized bare discriminator), `usage_owner_bare_alias_def_owned`
  (`c06`) and `usage_owner_bare_subset_def_owned` (`c08`) as definition-owned guard controls, and
  `usage_owner_bare_alias_arrayed` (`c12`) as the no-hidden-recovery negative. **No deep-override
  fixture was added** — D11 found no affected shape and its dated gap record stands.
- Authored `tests/fixtures/usage_owned_reference_consumers/model.sysml`: one named source
  (`plant.comp_a.length`, 3.0) read from seven consumers authored inside the sibling
  `plant.comp_b` (7.0) — typed alias, alias-following calculation input, computed attribute,
  calculation input, typed constraint actual, asserted inline predicate, and a direct scalar
  `sum()` term. It loads with zero errors and zero warnings and elaborates with zero diagnostics.
- `tests/fixtures/usage_owned_reference_consumers/PROVENANCE.md` records where each of the
  thirteen roots came from and what it is for, because the two research paths are archived at
  close (D6).
- `tests/expectations/constraint_population/usage_owned_reference_consumers.json` — required by
  the constraint-population oracle's rule 1 for any constraint-bearing fixture. Both its rows were
  checked against the model source, and the oracle's own domain comparison passes.

*Tests*

- `tests/conformance/test_usage_owned_reference_anchoring.py` (48 nodes): affected qualified lanes
  (u4–u7), the affected bare lane, the seven combined-fixture consumer lanes plus the fan-out
  obligation, controls (u1–u3b and the two definition-owned guards), the arrayed-owner negative,
  and identity-derivation nodes parametrized over all thirteen roots.
- `tests/conformance/test_source_identity_extraction.py::test_usage_owned_fact_owner_matches_live_part_usage`
  — the D2 authority guard. Green before the repair, as predicted: it compares frozen owner
  identity with the exact live leaf's owner, not the defective edge.

*Verification (`verification/`)*

- `before-full-suite.txt` + `README.md` — the pre-change baseline and how to reproduce every
  artifact.
- `corpus_roots.json` — 140 frozen roots.
- `corpus_compare.py` + `before.json` — the pre-repair ledger.
- `before-snapshot-inventory.json` — 23 tracked snapshots, 0 stale.

**Results:**

- **Full-suite baseline (before any fixture):** 17 failed, 2080 passed, 34 skipped, 88 deselected,
  170.09s. All 17 failures are `ModuleNotFoundError: No module named 'pandas'` — environmental and
  untouched by this item. All 34 skips are golden-fixture skips; **zero license-related skips**.
- **Full suite after this phase:** 32 failed, 2117 passed, 34 skipped, 88 deselected, 169.46s. The
  failure delta is exactly the 15 intentional red nodes and nothing else; no baseline failure
  disappeared. 37 new passing nodes (33 controls in the new file, the extraction guard, 3
  constraint-oracle rows for the new fixture).
- **The intentional red set (15), each red for the target identity:**
  `test_u4_package_sibling_binds_the_package_scoped_occurrence` (today `SI_OCCURRENCE_MISSING`),
  `test_u5_named_sibling_binds_the_named_occurrence` (today `SI_OCCURRENCE_AMBIGUOUS`),
  `test_u6_cross_owner_consumer_binds_the_named_sibling` (today a silent edge to
  `comp_b.length`), `test_u7_paired_spellings_bind_distinct_nodes` and
  `test_u7_qualified_edges_equal_their_dot_path_controls` (today both inputs ambiguous),
  `test_bare_alias_discriminator_binds_the_aliased_owner` (today a silent edge to
  `comp_b.length`), the seven `test_combined_*` lane nodes and
  `test_combined_named_source_reaches_every_and_only_its_consumers` (today all seven edges land on
  `comp_b.length`), and `test_arrayed_exact_owner_refuses_rather_than_answering` (today a silent
  answer where scalar owner selection must refuse).
- **Not a fixture failure.** `test_combined_fixture_loads_and_elaborates_cleanly` passes, all six
  control nodes pass, and the ledger records a typed edge for every combined-fixture site — so
  each red node above is a wrong or missing typed target, not a load or syntax problem. u6's
  failure was inspected directly: two `NodeRef`s differing in the occurrence step, no diagnostic.
- **Ledger determinism:** three consecutive runs byte-identical.
- **Quality:** `ruff check` clean on every file added or edited. `mypy` on the new test file and
  the verifier reports only `import-untyped` for `sysml_codegen.*` — the package ships no
  `py.typed`, so every module outside `src/` gets these, including the pre-existing
  `tests/conftest.py` and `tests/helpers/elaboration_graph.py`. No other mypy error remains.

**Issues:**

- The combined fixture declares constraints, which enrolls it in the constraint-population
  oracle's all-fixtures sweep. Missing that would have produced a red test for a bookkeeping
  reason rather than for the defect, which the phase forbids. Resolved by adding the expectation
  file; the oracle's three rows for the fixture pass.
- No premise conflict was found. Nothing contradicted the plan or the design.

**Deviations:**

- **Ledger rows carry a `promoted` section alongside `corpus`.** The brief requires freezing the
  pre-existing root set so new fixtures do not inflate the comparison, and it separately requires
  capturing c12's current silent answer. Both hold: the 140 frozen roots are the comparison, and
  the 13 promoted roots are captured in their own section, which is also where the pre-repair
  occurrence records and slot-derived node IDs are frozen.
- **Byte-exact identity freezing lives in the ledger, not in the conformance file.** Pinning
  occurrence-record and node-ID wire strings inline would have put a page of UUIDs in a file whose
  job is to be read. The conformance file pins the *derivation* — every attribute node ID equals
  `NodeId(ATTRIBUTE, scope, slot)` and every occurrence record agrees with its own containment slot
  — over all thirteen roots; `before.json` holds the exact strings Phase 3 and Phase 5 compare.
- **Two extra promoted fixtures beyond the plan's text.** The plan named the u-family and one
  Phase-1 fixture. The Phase-1 findings identified `c06`/`c08` as definition-owned guard controls
  and `c12` as the no-hidden-recovery negative, and the orchestrator's brief carried all three into
  this phase; they are promoted so the guard survives the archival of the research path.
- **u2, u3 and u3b turn out to be definition-owned-leaf controls.** Their qualifier names a usage,
  but the leaf it resolves to is declared on the part definition, so the repaired branch never
  activates for them and the ledger records zero in-population sites for those roots. Their
  conformance nodes and docstrings say so. This sharpens the plan's description rather than
  contradicting it — they remain exactly the "retain their existing exact edges or named
  diagnostics" controls the spec asks for.
- **Three ledger counts independently corroborate the 2026-08-15 measurement** (76 computed
  expression sites, 15 constraint bindings, zero alias and zero inline-predicate sites in the
  tracked corpus). Nothing required correcting.

### Phase 3 Completion

**Completed:** 2026-08-15, licensed environment (`set -a; source ../agentic-mbse/.env; set +a`),
branch `main` at `85f598a`. One production file changed and nothing else: `git diff --stat` is
`src/sysml_codegen/elaboration/elaborate.py` alone. No test file was edited — the Phase-2 oracle
stands exactly as written.

**Actual Changes:**

*The one seam (`src/sysml_codegen/elaboration/elaborate.py`)*

- `_resolve_semantic_reference`'s one-segment arm now calls `_resolve_direct_reference` instead of
  `_resolve_leaf` directly. That is the whole call-site change; the multi-segment arm, the plural
  handling, and every caller are untouched.
- New `_resolve_direct_reference(leaf_id, consumer_scope)`, placed immediately above `_resolve_leaf`
  so the two one-segment routes read together:
  1. Look up the exact leaf in the live element index and take its live semantic owner through the
     existing `_semantic_owner`.
  2. Guard on `SysideAdapter.is_instance(owner, "PartUsage")`. Not `owner_is_definition`, not source
     spelling, not qualified-name text (D2). Any other owner kind — definition, package,
     enumeration, calculation, or none — returns `self._resolve_leaf(...)` unchanged.
  3. Contextualize the owner declaration through the existing `_select_occurrences` over
     `occurrences_for_declaration(owner_id)`, with `plural=False` hard-coded and a comment naming
     why: the caller's flag describes the aggregation the caller is expanding, not this reference
     (D4).
  4. Take the leaf's target at that one occurrence through the existing `_target_at`, which is the
     established slot → `NodeRef`/`ProducerRef` lookup.
  5. Raise the existing `SI_OCCURRENCE_MISSING` if that occurrence carries no target for the leaf.
- The scalar selection is unpacked as `[owner_occurrence] = ...`, matching `_resolve_leaf`'s own
  `[producer] = self._select_calc_nodes(...)` idiom: `_select_occurrences(plural=False)` guarantees
  exactly one, so a violation is a loud invariant failure rather than a silently handled case.
- **No fallback exists to invoke.** Once the owner guard passes there is no `except`, no retry, and
  no second route out of the function — a missing or ambiguous owner propagates the existing
  `_ReferenceResolutionError` to the caller that already knows how to translate it. No new
  diagnostic code, no resolver-level alias following, no caller change (D5).

*Verification artifacts added*

- `verification/after-phase3.json` — the post-repair ledger from the same `corpus_compare.py`, so
  the before/after comparison below is file-to-file rather than remembered.
- `verification/after-phase3-full-suite.txt` — the post-repair full-suite run.

**Results:**

- **The 15 red nodes are green and nothing beside them moved.**
  `test_usage_owned_reference_anchoring.py`: 48 passed (15 failed / 33 passed immediately before the
  edit, verified by stashing the change and re-running — the red/green split is caused by this
  branch and by nothing else). `test_source_identity_extraction.py`: 14 passed, including the D2
  authority guard.
- **Import-boundary guard:** `tests/unit/test_elaboration_import_boundaries.py` 14 passed. The new
  helper is inspected automatically by the AST guard and needed no exemption — it selects on
  declaration identity and metatype only.
- **Full suite:** 17 failed, 2132 passed, 34 skipped, 88 deselected, 172.37s. The failing *node set*
  is byte-identical to `before-full-suite.txt`'s — all 17 are the environmental
  `ModuleNotFoundError: No module named 'pandas'`. Passing nodes went 2080 → 2132: the 37 Phase-2
  additions plus the 15 repaired nodes. All 34 skips are golden-fixture skips; zero license skips,
  so this is a real licensed run.
- **Quality:** `ruff check` clean; `mypy` reports no issue in `elaborate.py`. `ruff format --diff`
  shows 9 hunks in the file, all pre-existing (identical on the unmodified file at `85f598a`) and
  none inside the new code.
- **Corpus, before → after** (`before.json` vs `after-phase3.json`, 140 frozen roots, 409 sites):
  outcomes move from 405 edge / 4 diagnostic to **409 edge / 0 diagnostic**. Exactly 5 sites change
  and each is a predicted repair: u4's `SI_OCCURRENCE_MISSING` and u5's, u7's `a_len` and u7's
  `b_len` `SI_OCCURRENCE_AMBIGUOUS` all become typed edges, and u6's silent edge moves from the
  `comp_b` occurrence to the `comp_a` occurrence at the same slot. No site anywhere in the corpus
  gained a diagnostic. Site keys, lanes, and the 15 refused-root strings are unchanged.
- **Promoted fixtures, before → after** (16 sites): 12 edge / 4 diagnostic becomes 15 edge /
  1 diagnostic. The 14 changed sites are the u4/u5/u7 repairs, u6's moved edge, the combined
  fixture's seven consumer lanes (alias raw target, alias-following calc input, computed attribute,
  calc input, constraint actual, inline predicate, and the scalar `sum()` term) all moving from the
  `comp_b` occurrence to `comp_a`'s, the bare alias discriminator moving the same way, and
  `usage_owner_bare_alias_arrayed` moving from a **silent answer to
  `SI_OCCURRENCE_AMBIGUOUS` ("consumer context contains 2 candidate occurrences")** with the
  consumer left unbound. That last one is the phase's own no-hidden-recovery proof.
- **Identity is untouched.** The `identity` block — every occurrence wire ID, attribute node ID,
  calculation node ID, and constraint node ID — compares **equal for all 153 roots** (140 corpus +
  13 promoted) between `before.json` and `after-phase3.json`. Zero differences.
- **Manual u4–u7 inspection** (typed edges and full diagnostics printed directly from the live
  graphs): u4 binds the package-scoped `shared_component` occurrence; u5 binds the named `comp_a`
  occurrence; u6 binds occurrence `dd373162…` (`comp_a`) where it previously bound `87f9e6f2…`
  (`comp_b`); u7's `a_len`/`b_len` bind distinct occurrences that equal their dot-path control edges
  byte for byte. All four graphs carry **zero diagnostics**.
- **u6 has no residual edge and no recovery path ran.** `comp_b.length` has an empty consumer list,
  and a call counter on `_resolve_leaf` records **0 invocations across u6's entire elaboration** —
  the repaired branch answered without the positional route being reached at all.

**Issues:**

- None. No premise conflict surfaced: no caller, evidence schema, occurrence index, slot index,
  graph model, projection path, or snapshot codec needed to change, and no Phase-2 assertion needed
  weakening. Every one of the 15 red nodes went green on the branch as designed.

**Deviations:**

- **The Phase-3 test stencil was already landed by Phase 2, so no test was written here.** Its four
  assertions exist node-for-node in the oracle file: the scalar `sum()` term under a `plural=True`
  caller (`test_combined_direct_sum_term_is_scalar_and_reaches_the_named_source`), the raw alias
  target (`test_combined_alias_raw_target_is_the_named_source`), the qualified-equals-dot-path edge
  comparison (`test_u7_qualified_edges_equal_their_dot_path_controls`), and the no-fallback
  diagnostic check (`graph.diagnostics == []` on every affected node). All four were confirmed red
  for target identity in Phase 2 and are green now. Adding a duplicate stencil would have added a
  second oracle for the same obligation.
- **The owner is contextualized through `_select_occurrences` rather than `_contextualize_root`.**
  Both are in the range the plan names for reuse. `_contextualize_root` re-dispatches on owner
  metatype and returns `OccurrenceId | CalcNode`, but the branch has already established
  `PartUsage`, so calling it would mean testing the same metatype twice and then narrowing a union
  that cannot occur. Calling the occurrence selector directly mirrors `_contextualize_root`'s own
  `PartUsage` arm exactly — same candidates, same package/lineage/descendant/ambiguity policy — with
  nothing duplicated but the two-line candidate list.

### Phase 4 Completion

**Completed:** 2026-08-15, licensed environment (`set -a; source ../agentic-mbse/.env; set +a`),
branch `main` at `98970c9`. **No production file changed** — `git status --porcelain src/` is empty
at the phase gate, and no public or codec route needed one.

**Actual Changes:**

*Shared test helper (`tests/helpers/elaboration_graph.py`)*

- `every_typed_edge(graph)` — every consumer input port in the whole graph, keyed and valued by
  typed ID. A source-keyed query answers "who reads this"; this answers "what does anything read
  at all", which is the only form that can see a consumer binding somewhere unintended.
- `every_alias_target(graph)` — raw `alias_target` across the whole graph, the edges
  `InstanceGraph.semantic_edges()` does not carry (D8).

Both are used by all four test files below, so the typed oracle has one definition rather than
three drifting copies.

*Public mutation (`tests/conformance/test_elaboration_public_mutation.py`)*

- `test_usage_owned_public_mutation_reaches_every_and_only_its_consumers` — copies the combined
  fixture, changes `comp_a`'s `:>> length = 3.0;` to `5.0`, and runs the live, projected, and
  encode/decode-then-project routes.
- The **only** bar is structural, not enumerated: the six ports that reach the named source are
  asserted to be *every* input port in the graph
  (`set(every_typed_edge(graph)) == typed_source_consumers(...)`). An unintended seventh consumer
  fails the test wherever it binds — including one binding the enclosing sibling, which a
  source-keyed query cannot see. The whole-graph alias map is pinned the same way.
- `_source_consumers` gained a `source_qn` parameter; it previously closed over the module-level
  `SOURCE_QN`, and two existing call sites were updated.

*Round trip (`tests/conformance/test_elaboration_graph_roundtrip.py`)*

- `test_usage_owned_anchoring_survives_the_codec_including_raw_alias_targets` — first asserts the
  omission the plan names, that the alias node's ID appears nowhere in `live.semantic_edges()`,
  then compares the **full decoded graph** (`rebuilt == live`), the re-encoded bytes, the whole
  alias map, the whole typed-edge map, and `project(rebuilt) == project(live)`.

*Snapshot routes (`tests/conformance/test_snapshot_v6_routes.py`)*

- `test_usage_owned_anchoring_survives_capture_and_relocation` — captures the combined fixture to
  `tmp_path`, loads it in place and from a relocated copy, and compares instance fingerprints, the
  full projected payload against the independent live arm, and the typed edges and alias target on
  both loaded graphs. **The fixture is not enrolled in the committed v6 batch** (D9).

*Strict/lenient (`tests/conformance/test_elaboration_fail_closed.py`)*

- `test_owner_anchoring_resolves_identically_in_strict_and_lenient`, parametrized over the six
  owner-anchoring fixtures that elaborate cleanly (combined, u4, u5, u6, u7, bare alias). Each
  asserts an empty lenient diagnostic set first, so two graphs failing the same way cannot pass by
  comparing equal.
- `test_ambiguous_exact_owner_is_lenient_diagnostic_and_strict_refusal` — the arrayed-owner
  negative: one `SI_OCCURRENCE_AMBIGUOUS` and an unbound consumer in lenient mode, the same code
  raised as `ElaborationDiagnosticError` in strict.
- `test_strict_readiness_halt_precedes_graph_diagnostic_rejection` — the earlier `_finish_readiness`
  halt, tested separately on `source_identity_indexed_source`. It pins that
  `ElaborationDiagnosticError` is **not** a subclass of `ElaborationError`, which is what makes the
  two strict exits distinguishable by type rather than by message text.

*Verification artifacts*

- `verification/phase4-snapshot-assessment.json` — the live-versus-committed assessment, run before
  any snapshot was touched.
- `verification/after-phase4-full-suite.txt` and a new `verification/README.md` section describing
  both.

**Results:**

- **Focused files together under the license:** `test_elaboration_public_mutation.py`,
  `test_elaboration_graph_roundtrip.py`, `test_snapshot_v6_routes.py`,
  `test_elaboration_fail_closed.py`, `test_usage_owned_reference_anchoring.py`, and
  `test_source_identity_extraction.py` — **100 passed, 0 skipped**. No license-related skip; a
  skipped licensed test would have made the result worthless.
- **11 new test nodes**, all green: 1 public mutation, 1 round trip, 1 snapshot route, and 8 in the
  fail-closed file (6 parity parameters plus the two negatives).
- **Negative control — the new nodes are not vacuous.** The working tree's `elaborate.py` was
  temporarily replaced with its pre-repair content from `85f598a`, the new nodes were run, and the
  file was restored (`git status --porcelain src/` empty afterwards, verified). **7 of the 11 fail
  on the pre-repair resolver**: the public-mutation node, the round-trip node, the snapshot-route
  node, parity for u4/u5/u7, and the arrayed negative. The 4 that still pass are exactly the ones
  that should: parity for the combined fixture, u6, and the bare alias, because the pre-repair
  defect was *silent and symmetric across both modes* — a parity claim cannot see it, which is why
  the anchoring claim lives in the other three files — plus the readiness-halt node, which is about
  a different fixture and a different exit.
- **Snapshot assessment, run first (D9): 23 tracked, 23 assessed, 0 stale, 0 missing, 0 extra, 0
  duplicate.** Compared field by field with Phase 2's `before-snapshot-inventory.json`, the two
  documents differ in exactly two keys — `baseline_commit` and `git_status` — both describing the
  run rather than a snapshot. All 23 rows, instance-graph payload digests and port-unit maps
  included, are byte-identical. **No recapture occurred and none was warranted:** D9's trigger is an
  exposed and classified live/stored edge difference, and there is none.
- **Full suite:** 17 failed, 2143 passed, 34 skipped, 88 deselected, 172.50s. All 17 failures are
  the same environmental `ModuleNotFoundError: No module named 'pandas'` as the Phase-2 baseline —
  confirmed by count and cause, not by memory. Passing nodes went 2132 → 2143, exactly the 11 nodes
  this phase adds. All 34 skips are golden-fixture skips; zero license skips.
- **Quality:** `ruff check` clean on all five touched files. `mypy` on them reports **no new error**
  — every message is the pre-existing pattern Phase 2 recorded (`import-untyped` because the
  package ships no `py.typed`, plus unannotated `graph` parameters in functions that predate this
  phase). None points at a line this phase wrote.

**Manual checks:**

- **Names are compatibility output, not the oracle.** Every semantic assertion compares `NodeRef`,
  `NodeId`, or typed port IDs. Display paths appear only as lookup keys, so a rename breaks a lookup
  loudly but can never make a wrong edge look right. The one rendered set, `COMBINED_CONSUMERS`, is
  produced by `_typed_consumer_surface` *from* the typed consumer node IDs — it renders a typed
  answer rather than deciding one. The pipeline YAML and generated JSON checks run last and are
  labelled in the docstring as what they are.
- **Recapture check: not applicable, and that is the recorded outcome.** No snapshot bytes changed.
  `phase4-snapshot-assessment.json` is the retained evidence that the assessment ran before any
  snapshot work and came back with zero stale rows and byte-identical payloads.

**Issues:**

- None. No premise conflict surfaced. Projection and both codecs consumed the repaired typed edges
  mechanically, exactly as the phase's assumption predicted; nothing in `src/` needed to change.

**Deviations:**

- **The two typed-oracle helpers live in `tests/helpers/elaboration_graph.py`, not in each test
  file.** Four files need the same whole-graph enumeration, and three copies would drift. The
  module's docstring frames it as display-metadata lookup; these two are typed-identity queries, so
  they are the first of their kind there. That is the smaller cost than duplication.
- **`_source_consumers` gained a parameter.** It hardcoded the mixed-consumers source qualified
  name, which the new test cannot use. Parameterizing it was preferable to a second near-identical
  helper; the two existing call sites pass `SOURCE_QN` explicitly and their assertions are
  unchanged.
- **A temporary working-tree revert of `elaborate.py` was used for the negative control**, the same
  technique Phase 3 used to establish its red/green split. It is a read of the pre-repair behavior,
  not a production change: the file was restored immediately and the clean `git status` on `src/` is
  recorded above. Without it, "these tests pass" would not establish that they *can* fail.
- **The plan's stencil line `assert typed_consumers(changed, ...) == EXPECTED_CONSUMERS` is
  implemented as a stronger whole-graph comparison.** Comparing the changed graph's full typed-edge
  and alias maps against the baseline's proves the same thing and also catches an edge that moved
  anywhere else in the graph, which an expected-set comparison against a fixed list would not.

### Phase 5 Completion

**Completed:** 2026-08-15, licensed environment (`set -a; source ../agentic-mbse/.env; set +a`),
branch `main` at `a3b46dc`. **No production file changed** — `git diff --stat 2768c68..HEAD -- src/`
is `elaborate.py` alone, 51 insertions and 6 deletions, which is exactly what Phase 3 landed. No
evidence, occurrence, slot, graph, projection, or codec schema was widened; the diff adds one private
helper and rewires one call.

**Actual Changes:**

*Verification (`verification/`)*

- `after.json` — the shipped resolver's ledger, from the same `corpus_compare.py` command as
  `before.json`.
- `adjudicate.py` + `adjudication-diff.txt` — a ledger differ and its output. It decides nothing: it
  keys both ledgers by typed identity and prints changed site keys, changed outcomes, changed
  refusals, changed identity blocks, and any other changed root field. Needs no license.
- **`adjudication.md` — the deliverable.** All 19 changed rows ruled on, the Validation section as
  run, all 14 spec success criteria reconciled, and the bounded documentation check.
- `phase5-snapshot-assessment.json`, `after-phase5-full-suite.txt` — the snapshot inventory and full
  suite at this commit.
- `README.md` gained a "Certification — Phase 5" section describing all five.

*Documentation (bounded, one file)*

- `.project/active/self-binding-replacement/spec.md:53-61` — the D-6 bullet said the shipped
  elaborator "currently loses that owner". Corrected to past tense, naming the landing commit
  (`98970c9`) and file, and stating that the shipped elaborator now honors the exact usage owner. It
  still names the behavior as codegen defect F-6 rather than the meaning of `::`. **D-5, D-7, and the
  fusion-tea migration sentences are untouched.** The final verifier remains `/_my_close`.

**Results:**

- **Ledger determinism and provenance.** Two consecutive `corpus_compare.py` runs at this commit are
  byte-identical, and the result is also byte-identical to `after-phase3.json` — the expected
  outcome, since Phases 4 and 5 changed no production file; a difference would have been the finding.
- **Structural checks all hold.** Site keys equal (corpus 409 = 409, promoted 16 = 16, zero one-sided
  keys); zero after rows without an edge, diagnostic, or named structural reason; **zero roots with a
  changed identity block, out of 153**; the same 15 refused corpus roots with the same reason
  strings. `adjudicate.py` reports **0 structural problems**.
- **19 changed rows, every one a fix, zero unadjudicated.** Corpus 405 edge / 4 diagnostic → **409
  edge / 0 diagnostic** (rows 1–5: u4, u5, u7×2 repaired from diagnostic to typed edge; u6's silent
  `comp_b` edge moved to `comp_a` at the same slot). Promoted 12 edge / 4 diagnostic → **15 edge / 1
  diagnostic** (rows 6–10 the same five in their maintained copies; rows 11–17 the combined fixture's
  seven consumer lanes; row 18 the bare discriminator; row 19 the arrayed-owner refusal). 404 of 409
  corpus sites are untouched, and **no corpus row is a bare reference**, so there was no unclassified
  bare change.
- **The arrayed-owner call, made explicitly.** `usage_owner_bare_alias_arrayed` moved from a silent
  answer to `SI_OCCURRENCE_AMBIGUOUS`. Adjudicated **fix**, and the decisive fact was measured rather
  than assumed: the answer it used to give was occurrence `e559a865`, which is **`comp_b`** — the
  enclosing sibling, not either arrayed `comp_a` occurrence. It replaced a confidently wrong number
  with a named refusal for a reference that has no single right answer. Blast radius measured at
  zero: no corpus site gained a diagnostic, no snapshot went stale, no suite failure appeared. The
  compatibility cost is recorded in full in `adjudication.md`, including what an affected author
  sees.
- **Focused files:** 114 passed / 0 skipped together under the license, and independently 48, 14, 3,
  14, 6, 15, 14 — all green. Zero license-related skips.
- **Full suite:** **17 failed, 2143 passed, 34 skipped, 88 deselected, 170.81s.** The failing node set
  is identical to the Phase-2 baseline's, name for name; all 17 are the environmental missing-`pandas`
  failures. Passing nodes 2080 → 2143, fully accounted as 37 (Phase 2) + 15 (Phase 3) + 11 (Phase 4).
  Zero license-related skips.
- **Snapshots:** 23 tracked, 23 assessed, **0 stale**, 0 missing, 0 extra, 0 duplicate. Field-by-field
  against the pre-repair inventory the two documents differ in exactly two keys, `baseline_commit`
  and `git_status`, both describing the run. **No recapture, none warranted** — D9's trigger never
  fired.
- **Standing gaps.** D11's `deep override affected-shape coverage unproven` remains **open** and is
  named as not-evidenced in `adjudication.md`; the lane again measured **0** one-segment sites across
  every root that elaborated. D10 took route 1 on evidence, so SC8 is evidenced by the authored
  discriminator (`usage_owner_bare_alias`, row 18) and carries no gap record.

**Issues:**

- **`ruff check src/ tests/` reports 131 findings and `mypy src/` reports 52 errors. Neither gate is
  clean project-wide and neither ever was.** The plan asks for these commands to be run, so this is
  reported as it is rather than as "clean". Both finding sets were re-captured at the item's start
  commit `2768c68` in a scratch worktree and diffed: **identical, line for line, in both tools**, and
  **zero** mypy errors are in `src/sysml_codegen/elaboration/`. This item therefore contributes no new
  finding from either its production edit or its thirteen fixtures and five test files. The
  pre-existing backlog was not touched — absorbing it is exactly what the phase's risk note forbids.
- **No premise conflict surfaced.** Nothing contradicted the plan, the design, or the spec, and no
  row looked like a regression.

**Deviations:**

- **`adjudicate.py` was added; the plan did not name it.** The phase requires zero unadjudicated rows
  across 425 sites and 153 identity blocks. Eyeballing two 500 KB JSON documents is not a check, so
  the differ is the mechanism and `adjudication.md` is the judgment. It is deliberately inert — it
  never reads the model, never re-resolves anything, and needs no license — which keeps it from
  becoming a second resolver the way the plan's risk note warns.
- **A scratch git worktree at `2768c68` was used for the ruff/mypy baseline**, then removed. Without
  it, "131 findings" could not be shown to be pre-existing rather than newly introduced.
- **`phase5-snapshot-assessment.json` is a third near-identical 3.7 MB inventory.** Phase 4 already
  has one and it is unchanged. It is kept anyway because this is the certification phase and the
  claim "no snapshot is stale at the shipped commit" should rest on a capture at that commit, not on
  an earlier one plus an argument.
- **One out-of-bounds mismatch was surfaced, not fixed.**
  `.project/active/self-binding-replacement/spec.md:132-139` carries the same stale present tense
  ("the current one-segment resolver normalizes to a feature slot…") in a `[HARD]` requirement. It
  sits outside the inventory this item was given, and that inventory was drawn deliberately, so it is
  flagged in `adjudication.md` for close or the owner rather than edited here.

---

**Status:** Draft → In Progress → Complete → **Certified** (`audit.md`, 2026-08-15)
**Next Step:** After plan approval, run `/_my_implement` from Phase 1. Use `/_my_audit` after all
phases pass; the bounded self-binding verification completes in `/_my_close`.
