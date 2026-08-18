# Implementation Plan: Stop Reinventing the Parser

**Status:** Draft
**Revision:** 3
**Created:** 2026-08-17
**Last Updated:** 2026-08-17
**Phase Strategy Approved:** 2026-08-17
**Complexity:** HIGH

## Source Documents

- **Spec:** [spec.md](spec.md) — approved Revision 4
- **Design:** [design.md](design.md) — Revision 7, the targeted amendment of the approved
  Revision 6
- **Design review:** [design-review.md](design-review.md) — Revision-6 verdict `Approve`;
  targeted Revision-7 verdict `Revise`, whose must-fix set was applied and orchestrator-verified
  on 2026-08-17
- **Phase 1 stop report:**
  [run-records/phase1-stop-report.md](run-records/phase1-stop-report.md) — rulings 1-7
  owner-ratified 2026-08-17; the cause of this revision
- **Audit:** [audit.md](audit.md) — failed-candidate verdict `Needs Work`
- **Product lens:** [product-lens.md](product-lens.md) — `audit3-F1` remains blocked until the
  production indexed-consumer proof is green
- **Revision research:**
  [expression-evidence boundary convergence assessment](../../research/20260817-164828_expression-evidence-boundary-convergence-assessment.md)
- **Failed candidate:** [plan.failed-candidate.md](plan.failed-candidate.md) — historical record;
  never resume its checklist

### Revision 3 note

Revision 2's first Phase-1 run tripped the phase's own stop rule and halted to the owner. Two
things were wrong, both inherited from design Revision 6 rather than introduced here. Its
lock-verification clause required every locked hash to recompute against the working tree, which
executes a rule the design stated wrongly: the lock is authoritative against the historical tree it
names, and current outputs are owned by the transition ledger. And its Phase-1 stencil used the
`Cell[3]` shape, which already refuses at `C_base` — under the wrong diagnostic name — so the
stencil would have gone red for the wrong reason and proved nothing. Design Revision 7 corrects
both, and the owner ratified rulings 1-7 in the stop report. This revision consumes that correction:
the three-leg lock rule, the two-case indexed red set, the committed historical-tree check, the
A5a/A5b reconciliation rows, and the `deep_cross_scope_probe` obligations. Phases 1-5, the
worktree discipline, the owner-verbatim PDF exclusion, and every Phase 2-5 gate are unchanged. The
implementation notes remain empty; no phase has completed.

## The Point

The product must parse the model with SysIDE, walk the parser's resolved semantic tree to reconstruct
the authored math, and emit that math as executable TEAx Python. A reference the toolchain cannot
honor must be refused by name before a graph, snapshot, package, or output mutation escapes. It must
never be changed into another expression through a dropped index, missing target, shortened path,
name fallback, candidate election, or caller-supplied substitute.

This revision serves that obligation by making exact parser evidence the only representable
production route. Completion requires all three closure legs from
[design.md#checked-consumer-and-ownership-manifests](design.md#checked-consumer-and-ownership-manifests):
owned acquisition, closed representation, and natural-route proof. No one leg substitutes for
another.

## Implementation Strategy

### Phasing rationale

The plan starts from the audited failed-candidate trees because they already contain the approved
D1-D4 occurrence work, retained probes, and artifact harness. Phase 1 first proves that exact base — verifying the
lock on its three legs and adding the missing committed historical-tree check — and reproduces the
indexed escape with two kept red closure tests, one per measured `C_base` behavior. Phase 2 closes Agentic's evidence
contract before Codegen depends on it. Phase 3 removes Codegen's weaker representations and raw
walks. Phase 4 proves the complete public route and graph-derived registry authority. Phase 5 names
and verifies fresh immutable artifacts only after production behavior is green.

### Critical path

```text
C_base + A_base + three-leg lock verification
  -> red audit3-F1 natural-route proof (both indexed cases)
  -> Agentic semantic-evidence/v2
  -> Codegen closed evidence boundary
  -> public route + registry closure
  -> A_final -> C_prod -> F_final -> C_evidence
  -> independent audit handoff
```

### First proof point

Two kept licensed tests on old `C_base`, and they prove different things. See
[design.md#the-indexed-red-set--both-cases-are-required-kept-tests](design.md#the-indexed-red-set--both-cases-are-required-kept-tests).

- **Case 1 is the escape itself.** `picked = cells#(2).mass` against a singular `cells : Cell[1]`
  produces a **zero-diagnostic graph** at `C_base`, in which the authored index is silently
  rewritten to `cells[0].mass`. The index is out of range, so no reading of the model makes
  occurrence zero the authored intent — the collapse is unarguable. The recorded red is that a graph
  is produced and carries zero diagnostics.
- **Case 2 is the paired red, and it refuses under the wrong name.** `picked = cells#(2).mass`
  against a plural `cells : Cell[3]` refuses at `C_base` as `SI_OCCURRENCE_AMBIGUOUS` — a name
  about occurrence selection, for an index defect. The recorded red pins that exact diagnostic and
  requires it to become `SI_INDEXED_SOURCE_UNSUPPORTED`.

Neither substitutes for the other. Case 1 cannot show that the inventory runs before occurrence
resolution, because nothing refuses on that path today; Case 2 cannot show the silent rewrite,
because that path already refuses. Both must be red at `C_base` **for their stated reason**, with
the D1-D4 occurrence tests and the three-leg lock verification green. A different failure — fixture,
license, import, or harness — is not the proof point. If either exact red result does not reproduce,
stop and return to design before changing production code.

### Overall validation approach

- Each phase writes its tests first.
- Phase 1 intentionally ends with a closed, recorded red set. Phases 2-4 turn those same kept tests
  green; they are not replaced with easier tests.
- Targeted tests run during implementation. Repository suites, scoped strict checks, baseline static
  checks, and artifact-isolated runs close the relevant phase.
- Every indexed natural-route row distinguishes inventory-before-consumer refusal from the targeted
  inventory-bypass consumer backstop.
- Every phase records its commands, results, changed paths, deviations, and rollback identity in
  the completion section immediately after it finishes.

## Global Execution Contract

### Exact starting trees

- **Codegen `C_base`:** `78a9beb956f9b5a517c08836b067f0cb0dc4ccc6`
- **Agentic `A_base`:** `2171016d3e3e0805525aa4cf787c55c6293dd00c`
- **Retained probe commit:** `20f9e60a19b30bc1ec9a27aacb08380f4bc45602`
- **Retained manifest-only lock:** `43edf9bde4db44e7973458ada732d2cd75e764f6`
- **Fusion parent:** `824a876e281a3b9aef58b1873bfbd0b20c4ab77b`
- **TEAx:** `744745f895677f3344b9884627369a6a47ed987f`
- **1costingfe:** `02543850089be175ea7c28b92a8b2a4184e1637e`

Before implementation, use dedicated clean worktrees rooted at the full Codegen and Agentic SHAs.
Do not implement from the dirty documentation checkout. Do not stage, stash, reset, clean, switch,
or otherwise alter an existing user checkout. Record each original checkout's status before work
and compare it at every phase boundary.

The retained probe and lock commits must remain ancestors of `C_base`, and their recorded parent
relationship must hold. Do not recreate the probes from historical comparison baseline `7b29d8b`.

### Lock verification — three legs, not one recompute

`C_base` is a **descendant** of the frozen evidence commits, not a byte copy of them. Nothing here
requires the current tree to byte-match the frozen `P_seed` state. So the lock is not verified by
recomputing its hashes against the working tree. It is verified on three legs, and every locked byte
is covered by exactly one of them. See
[design.md#what-the-lock-is-verified-against](design.md#what-the-lock-is-verified-against).

1. **Fixture inputs against the tree the lock itself names.** Read `probe_fixture_commit` **from
   `verification/probe-fixture-lock.json`** and require it to equal
   `20f9e60a19b30bc1ec9a27aacb08380f4bc45602`; recompute the 118 locked hashes against *that*
   commit's tree, read from Git. Never hard-code `43edf9bde4db44e7973458ada732d2cd75e764f6` as the
   tree to check — that is the lock file's home commit (its whole diff is adding the lock file), not
   the tree its hashes describe.
2. **Current outputs through the committed transition-ledger validators.** Current outputs are not
   checked against the lock. They run through the machinery already committed in
   `verification/capture_baseline.py`: `_frozen_batch` (`capture_baseline.py:76`) loads the frozen
   `P_seed` batch manifest from Git, `validate_manifest` (`:134`) requires the on-disk manifest to
   equal both the frozen bytes and their reconstruction, `validate_current_batch` (`:166`) validates
   the current batch at its own pinned hash, and `validate_output_transitions` (`:241`) requires
   every post-`P_seed` byte under `tests/fixtures` to be metadata-only or owned by a named row in
   `verification/expected-transitions.md`.
3. **The six locked verification/probe code rows pinned at current bytes.** Those rows are live
   code, not frozen evidence, so neither leg above pins them. Pin each at its **current** SHA-256 in
   the implementation tree. Any difference from its lock-time bytes must be **ledger-owned**: a
   named row in `verification/expected-transitions.md` giving the file, both hashes, the owning
   commits, and the reason. One such difference exists today —
   `verification/capture_baseline.py` moved in `da4aa78` and `46694e2`, and needs its named row
   citing both. The five probe scripts are unchanged from lock-time bytes and are pinned there.

A failure in **any** leg stops the plan and returns the item to design; never re-derive the lock.
Re-locking against `C_base` would erase the provenance the lock exists to preserve. An unowned
current-byte change to locked verification code is exactly as fatal as a lock mismatch — only the
naming authority differs.

**When the D10 probes rerun.** Two triggers, in their firing form, and only these
([design.md#probefixture-commit-lock](design.md#probefixture-commit-lock)):

1. a **lock-vs-historical-tree mismatch** — a locked hash no longer recomputes against `20f9e60a`,
   meaning evidence tampering or a history rewrite; or
2. an **unowned current-byte change to a locked verification or probe file** — one of the six
   non-fixture rows moved without a named ledger row.

A ledger-owned current-output transition is not a trigger, and neither is a ledger-owned change to a
verification file. That is the system working.

### Frozen versus current batch counts

The canonical batch manifest has two states, and every count quoted anywhere in this plan carries
its state label ([design.md#closed-fixture-inventory](design.md#closed-fixture-inventory)):

| State | Batch SHA-256 | Records |
|---|---|---|
| **Frozen, `P_seed` `52a03cd`** | `bd7bf245e3ca3923b9b5d41db97861c9fcdf64435e768d48a2d7027eb52d9288` | 15 graph / 22 typed refusals — the input inventory, reconstructed from Git |
| **Current, `C_base` `78a9beb9`** | `7f9269781a8938308715229c5be00855490e82b7e54f9cb90939195e3aeefa40` | 14 graph / 23 typed refusals — the output expectation |

The 15/22 → 14/23 move is one record, `deep_cross_scope_probe`, going graph → refusal under a named
A2 ledger row. Neither state may be presented as the other.

### `deep_cross_scope_probe` — never restore the old graph

**[AGENT] (ratified by owner, 2026-08-17)** — rulings 4-5. The old captured graph wired a consumer
to a definition-scoped name surfaced as a caller-supplied entry-point parameter with
`default_value: null`. That is this item's forbidden class verbatim: a reference the toolchain could
not honor, silently changed into another expression through a caller-supplied substitute. The
graph → refusal move is **intended tightening**.

**A change that returns `deep_cross_scope_probe` to a captured graph restores the substitution
defect and fails the item, regardless of what the batch counts look like.** This is a global stop
condition in every phase, not a reconciliation to negotiate. See
[design.md#deep_cross_scope_probe--graph-to-refusal-is-intended-tightening](design.md#deep_cross_scope_probe--graph-to-refusal-is-intended-tightening).

### Owner-directed run pause

**[OWNER-VERBATIM, 2026-08-17]** “ok ratified. Proceed. but pause AFTER Phase 1.”

Phase 1 completes and the run halts to the owner before Phase 2 begins.

### Preserved and prohibited changes

- D1-D4 are preserved. Production changes to
  `src/sysml_codegen/elaboration/occurrence.py` require a surfaced design conflict; normal
  implementation must leave that file byte-identical to `C_base`.
- Do not add a compatibility wrapper, deprecated alias, manifest exemption, optional semantic path,
  or second resolution mode for a deleted weak surface.
- Do not patch a production failure in `C_evidence`. Return to its owning phase, create a new
  production identity, and rebuild the dependent chain.
- The three off-route Codegen modules remain explicitly inventoried. A reachable one must be
  migrated or removed before closure; reachability may not be assumed.

### Owner-directed test exclusion

**[OWNER-VERBATIM, 2026-08-17]** “do not rerun the PDF suite anymore.”

The Agentic slow PDF/HTML corpus suite is permanently outside parser-work validation. Do not invoke
it or report it as passed, skipped, or required. The 15 paid/network extraction cases also remain
unrun external inputs; this plan does not authorize external transfer or spend. This exclusion does
not weaken the Agentic fast, focused SysIDE, static, Codegen, Fusion, TEAx, or artifact gates.

### Development validation commands

Load the SysIDE license into the environment for licensed tests, but never copy `.env`, its value,
or another secret into an artifact or report.

**Agentic, from its clean implementation worktree:**

```bash
uv run pytest tests/ -m "not slow"
uv run mypy --strict src/agentic_mbse/errors.py src/agentic_mbse/sysml/reference_use.py
uv run mypy src/
uv run ruff check src/ tests/
```

The scoped strict command must return zero. The repository-wide mypy and Ruff commands are
baseline comparisons against `A_base`: item-caused diagnostics are forbidden, and nonzero baseline
results must not be described as green.

**Codegen, from its clean implementation worktree:**

```bash
uv run --extra dev pytest tests/
uv run --extra dev mypy --strict src/sysml_codegen/extraction/binding_source.py \
  src/sysml_codegen/elaboration/expression_evidence.py
uv run --extra dev mypy src/
uv run --extra dev ruff check src/ tests/
```

The scoped strict command must return zero. The repository-wide mypy command is a separate baseline
comparison. The default suite does not substitute for the execution lane or final extracted-artifact
run in Phase 5.

---

## Phase 1: Verify the base and establish the red closure harness

### Goal

Prove that implementation starts from the audited trees, retain the old probes and D1-D4 behavior,
and add kept tests that reproduce the failure class before any production edit. This phase executes
[design.md#revision-6-implementation-base](design.md#revision-6-implementation-base) and gate 1 of
[design.md#sequencing-and-landing-gates](design.md#sequencing-and-landing-gates).

### Assumption under test

`C_base` contains the known indexed bare-chain escape in both its measured forms, plus the CI-2
through CI-5 seams, while its occurrence core, probe verdicts, fixture inventory, and artifact
harness remain coherent with the audited state — the lock verified against its historical tree, and
every current-tree difference owned by a named ledger row. Coherence, not byte identity, is the
claim: `C_base` is a descendant of the frozen evidence commits, not a copy of them.

### Test stencils — write these first

The red set is **two** cases, both kept tests rather than throwaway probes, and each goes red at
`C_base` for its own stated reason. See
[design.md#the-indexed-red-set--both-cases-are-required-kept-tests](design.md#the-indexed-red-set--both-cases-are-required-kept-tests).

**Case 1 — `Cell[1]` bare chain, index out of range.** The escape itself.

```python
@pytest.mark.licensed
def test_indexed_bare_chain_singular_slot_refuses_before_consumers(public_routes, tmp_path):
    # picked = cells#(2).mass against a singular cells : Cell[1]
    downstream = spy_on_expression_consumers()
    results = public_routes.live_admitted_and_capture(SINGULAR_SLOT_MODEL, output=tmp_path)
    assert all(r.code == "SI_INDEXED_SOURCE_UNSUPPORTED" for r in results)
    assert all(r.reference == "cells#(2).mass" for r in results)
    assert all(r.location == "root-0/model.sysml:<line>" for r in results)
    assert all(r.graph is None for r in results)
    assert not downstream.called
    assert snapshot_bytes(tmp_path) == NO_SNAPSHOT
```

**Expected red at `C_base`:** the model produces a graph, and that graph carries **zero
diagnostics** — the authored index is silently rewritten to `cells[0].mass`. That zero-diagnostic
collapse is the recorded red. The index is out of range, so the rewrite is unarguable.

**Case 2 — `Cell[3]` bare chain.** The ordering proof.

```python
@pytest.mark.licensed
def test_indexed_bare_chain_plural_slot_refuses_before_occurrence_resolution(public_routes):
    # picked = cells#(2).mass against a plural cells : Cell[3]
    occurrence_resolution = spy_on_occurrence_resolution()
    result = public_routes.live(PLURAL_SLOT_MODEL)
    assert result.code == "SI_INDEXED_SOURCE_UNSUPPORTED"   # C_base gives SI_OCCURRENCE_AMBIGUOUS
    assert result.reference == "cells#(2).mass"
    assert not occurrence_resolution.called
```

**Expected red at `C_base`:** the model refuses, but as `SI_OCCURRENCE_AMBIGUOUS` — a name about
occurrence selection, raised for an index defect. The recorded red pins that exact starting
diagnostic and requires it to become `SI_INDEXED_SOURCE_UNSUPPORTED`. An end-to-end "it refused"
assertion passes at `C_base` and proves nothing; the assertion must be on the code and on the
inventory running before occurrence resolution.

For both cases, a different failure — a fixture, license, import, or harness error, or the right
code from the wrong path — is not the proof point.

**Not red-set members.** Operator-wrapped forms (`cells#(2).mass * 1.0`) already refuse correctly at
`C_base` with `SI_INDEXED_SOURCE_UNSUPPORTED`; they are real expressions that enter the existing
screen. They stay in the matrix as **positive regression coverage**. A test that treats them as the
escape is measuring the wrong thing.

### Changes required

**See:** [design.md#current-code-facts](design.md#current-code-facts),
[design.md#load-bearing-bets](design.md#load-bearing-bets), and
[design.md#test-design](design.md#test-design).

- [ ] **Base and lock verification:** record clean implementation-worktree status; prove the two
  retained commits are ancestors of `C_base` with their recorded parent relationship; run the three
  legs of [lock verification](#lock-verification--three-legs-not-one-recompute) — fixture inputs
  against `20f9e60a` read from the lock's own `probe_fixture_commit` field, current outputs through
  the committed transition-ledger validators, and the six verification/probe rows at current bytes
  with every difference ledger-owned; run the existing probe/fixture, baseline, and artifact
  topology checks in `tests/unit/test_coverage_probes.py:1`,
  `tests/conformance/test_baselines.py:1`, and
  `tests/conformance/test_evidence_artifact_topology.py:1`.
- [ ] **Committed historical-tree lock check (new kept test):** today the lock leg exists only as a
  hand-run; no committed test verifies the lock against its named historical tree, and that is the
  one real residual gap in `C_base`'s evidence contract. Add it as a kept test that lands in
  `C_prod` beside the other verification tests
  ([design.md#the-missing-committed-check--phase-1-adds-it](design.md#the-missing-committed-check--phase-1-adds-it)).
  It must:
  - read `probe_fixture_commit` **from the lock file itself**, assert it equals
    `20f9e60a19b30bc1ec9a27aacb08380f4bc45602`, and recompute against *that* tree — never
    hard-coding `43edf9bd`, which is the lock file's home commit, not the tree its hashes describe;
  - read each locked path's bytes from Git at that commit (the same `git show` route `_git_bytes`
    already uses), recompute SHA-256, and require an exact match for all 118 rows;
  - assert anti-vacuity: the row count is 118 and every row was actually read;
  - separately assert leg 3 — each of the six verification/probe rows matches its current on-disk
    bytes, and any file differing from its lock-time bytes has a named ledger row;
  - never read the working tree for the historical bytes, and never rewrite the lock on mismatch.
- [ ] **Codegen tests first:** extend
  `tests/conformance/test_expression_evidence_integrity.py:1` with **both** indexed red cases —
  the `Cell[1]` out-of-range singular-slot case and the `Cell[3]` plural-slot case — through the
  licensed live/admitted/capture seed, with exact diagnostic fields, downstream-entry and
  occurrence-resolution spies, and the snapshot byte-preservation assertion. Add the
  operator-wrapped form as positive regression coverage, not as a red-set member. Add the initial
  consumer table for calculation dependencies, bindings, aliases, computed attributes, predicates,
  and deep overrides.
- [ ] **Codegen ownership harness:** add
  `tests/conformance/test_expression_evidence_ownership.py` with the initial reviewed selector rows,
  public-root reachability checks, deleted-symbol inventory, and the five AST evasion mutations from
  [design.md#checked-consumer-and-ownership-manifests](design.md#checked-consumer-and-ownership-manifests).
- [ ] **Agentic tests first:** add `tests/test_sysml/test_reference_use.py` and
  `tests/test_sysml/test_semantic_selector_ownership.py` with the closed-variant, consumer, selector,
  and symbol-absence expectations. They must expose the current permissive helpers and boolean marker
  rather than grandfathering them.
- [ ] Commit only tests/manifests and phase records on the two implementation branches. Record the
  exact expected-red node IDs; no production source changes in this phase.

### Validation

**Automated:**

- [ ] Run the retained Codegen probe/baseline/topology tests and require green results.
- [ ] Run all D1-D4 occurrence and mutation tests named under
  [design.md#occurrence-and-producer-matrix](design.md#occurrence-and-producer-matrix); require no
  regression.
- [ ] Run the new focused Agentic and Codegen tests. Require failures to equal the recorded red set:
  **both** indexed natural-route cases with their stated reasons — Case 1 a zero-diagnostic graph,
  Case 2 `SI_OCCURRENCE_AMBIGUOUS` — plus weak representation/symbol closure and ownership-manifest
  differences.
- [ ] Run the new committed historical-tree lock check; require it green.
- [ ] Prove `git diff C_base -- src/sysml_codegen/elaboration/occurrence.py` is empty.
- [ ] Rerun the three lock legs at the end of the phase as well as the start.

**Manual:**

- [ ] Inspect the Case 1 trace and confirm the graph is produced with zero diagnostics and the
  authored reference collapsed to `cells[0].mass`, matching `audit3-F1`. Inspect the Case 2 trace
  and confirm the refusal is `SI_OCCURRENCE_AMBIGUOUS`, on the plural slot rather than the authored
  index. Do not accept a fixture, license, import, or harness failure as either red.
- [ ] Confirm no command imported production code from the documentation checkout or an unrecorded
  sibling.

**What we know works after this phase:** the replacement starts from the intended audited tree, the
lock is verified on all three legs by a committed test rather than a hand-run, the recurring defect
is reproduced by two kept natural-route tests that fail for their stated reasons, and the
preservation boundary around D1-D4 and the retained evidence is explicit.

**Rollback/stop rule:** failure to reproduce either exact red for its stated reason, a failure in
any lock leg, or any D1-D4 regression returns the item to design before Phase 2. A `C_base` result
that differs from the design's recorded behavior matrix is a design conflict, not something to
reconcile in the test.

**Owner pause:** the run halts to the owner after this phase completes, per the owner-directed
pause in the Global Execution Contract.

---

## Phase 2: Close the Agentic evidence contract

### Goal

Land `semantic-evidence/v2`, make indexed and incomplete paths unrepresentable as exact evidence,
delete the permissive production surface, and migrate every Agentic consumer. Codegen does not
consume the new artifact until Agentic is independently green. See
[design.md#d5-public-agentic-evidence-contract](design.md#d5-public-agentic-evidence-contract),
[design.md#d6-documenttier-owns-b5](design.md#d6-documenttier-owns-b5), and
[design.md#agentic-semantic-contract](design.md#agentic-semantic-contract).

### Assumption under test

One provenance-complete inspector can serve expression traversal, aggregation, binding, ADR002, and
math reconstruction without a caller rebuilding names, paths, index state, or document authority.

### Test stencil — write this first

```python
def test_indexed_use_has_no_exact_path_and_cannot_form_a_term(indexed_expression):
    uses = inspect_reference_uses(indexed_expression)
    assert len(uses) == 1
    assert isinstance(uses[0], IndexedReferenceUse)
    assert not hasattr(uses[0], "path")
    with pytest.raises(SemanticEvidenceError) as caught:
        build_aggregation_term(indexed_expression)
    assert caught.value.code is SemanticEvidenceCode.INDEXED_REFERENCE_UNSUPPORTED
```

### Changes required

**See:** [design.md#closed-reference-use-values](design.md#closed-reference-use-values),
[design.md#one-total-inspection-operation](design.md#one-total-inspection-operation), and
[design.md#delete-the-permissive-production-surface](design.md#delete-the-permissive-production-surface).

- [ ] **Tests first:** complete `tests/test_sysml/test_reference_use.py`; extend the existing
  expression, aggregation, binding, ADR002, adapter, error, type, and public-export tests. Cover exact
  positive evidence, mapped `IndexExpression`, operand failure, depth exhaustion, missing target and
  leaf, document tiers, aggregation refusal, ordered binding evidence, and ADR002 dynamic handling.
- [ ] **Closed boundary:** update `src/agentic_mbse/errors.py:5` and add
  `src/agentic_mbse/sysml/reference_use.py` with the error/value/inspector boundary specified in the
  design. Keep the neutral `ExpressionIR` separate.
- [ ] **Owned acquisition:** update `src/agentic_mbse/sysml/syside_adapter.py` and
  `src/agentic_mbse/sysml/expression.py:589` so mapped metatypes, total operand materialization,
  shared depth, exact targets, authored form, and `DocumentTier` are the sole evidence owners.
- [ ] **Natural Agentic consumers:** migrate
  `src/agentic_mbse/sysml/aggregation.py:251`, `aggregation.py:426`,
  `sysml/binding.py:164`, and `validation/adr002.py:641`; update
  `constraint_extraction.py` to share the exact document-tier operation.
- [ ] **Atomic deletion:** remove `extract_feature_refs`, `feature_reference_facts`,
  `feature_chain_facts`, `ResolvedSemanticReferenceFact`, `has_index_segment`, `ExpressionRef`, and
  `BindingInfo.references`, including `src/agentic_mbse/sysml/__init__.py:67`, top-level exports,
  lazy aliases, tests, and docs. Do not retain a deprecation path.
- [ ] **Ownership closure:** finish `tests/test_sysml/test_semantic_selector_ownership.py` so the
  discovered selector set equals the reviewed Agentic manifest, all five evasion mutations die, and
  the math-only optional IR target remains explicitly non-authoritative.
- [ ] **Package contract:** bump Agentic to `0.1.3`, update `pyproject.toml`, package version,
  `uv.lock`, public API assertions, and `docs/patterns/plant-idiom.md` as required by
  [design.md#documentation-and-backlog-obligations](design.md#documentation-and-backlog-obligations).

### Validation

**Automated:**

- [ ] Run the focused Agentic reference-use, adapter, expression, aggregation, binding, ADR002,
  export, and ownership tests; all Phase-1 Agentic red nodes must be green.
- [ ] Run `uv run mypy --strict src/agentic_mbse/errors.py
  src/agentic_mbse/sysml/reference_use.py`; require zero errors.
- [ ] Run the fast Agentic suite with the SysIDE license and `-m "not slow"`; enforce the declared
  skip set and do not run the retired PDF or paid/network cases.
- [ ] Run repository-wide mypy and Ruff as baseline comparisons; require no new item-caused result
  and targeted Ruff success for every changed Python file.
- [ ] Run static symbol/import searches and public-export tests; every deleted identifier and alias
  must be absent from production and public barrels.
- [ ] Build a clean Agentic source archive and wheel from the phase commit; run the same focused and
  fast gates from the extracted archive and verify installed version/API markers.

**Manual:**

- [ ] Inspect one exact reference payload from each natural consumer and confirm it retains root,
  members, leaf, owner, document, authored form, order, and location without carrying operator or
  literal structure.
- [ ] Confirm `IndexExpression` dispatch comes from the mapped SysIDE metatype and never from a
  runtime class-name comparison.

**What we know works after this phase:** Agentic exposes one closed evidence contract, every
measured Agentic consumer uses it, and the weak fact/helper surface no longer exists.

**Rollback/stop rule:** a consumer that cannot migrate without reconstructing the weak route is a
design conflict. Stop rather than add a wrapper, compatibility alias, or manifest exemption.

---

## Phase 3: Make Codegen accept only closed evidence

### Goal

Build the pre-graph evidence inventory, closed binding variants, exact-only resolver adapter, and
total deep-relationship path. Remove Codegen's raw expression and optional-path bypasses while
leaving D1-D4 source and behavior intact. See
[design.md#d7-one-codegen-conversion-boundary](design.md#d7-one-codegen-conversion-boundary),
[design.md#binding-and-deep-path-values-are-valid-by-construction](design.md#binding-and-deep-path-values-are-valid-by-construction),
and [design.md#scoped-strict-type-boundary](design.md#scoped-strict-type-boundary).

### Assumption under test

Every Codegen dependency and binding consumer can receive closed evidence from one pre-graph
inventory and operate without raw selector reads, an optional semantic path, an index-bearing exact
fact, or a shortened relationship path.

### Test stencil — write this first

```python
def test_inventory_and_consumer_backstop_are_independent(indexed_site):
    downstream = spy_on_consumer(indexed_site.role)
    with pytest.raises(ElaborationDiagnosticError):
        build_inventory(indexed_site)
    assert not downstream.called
    with pytest.raises(IndexedSourceUnsupported):
        invoke_consumer_with_inventory_bypassed(indexed_site)
    assert downstream.entered_once
```

### Changes required

**See:** [design.md#one-codegen-conversion-boundary](design.md#d7-one-codegen-conversion-boundary),
[design.md#checked-consumer-and-ownership-manifests](design.md#checked-consumer-and-ownership-manifests),
and [design.md#diagnostic-ownership](design.md#d8-diagnostic-ownership).

- [ ] **Tests first:** turn the Phase-1 Codegen consumer and ownership tables into focused unit and
  integration tests. Add direct constructor/exhaustiveness tests, inventory-missing/duplicate tests,
  targeted inventory-bypass tests for every consumer adapter, and deep-path totality tests.
- [ ] **Closed boundary modules:** add
  `src/sysml_codegen/extraction/binding_source.py` and
  `src/sysml_codegen/elaboration/expression_evidence.py` with the narrow strict surfaces described
  in the design.
- [ ] **One inventory and exact resolver:** update
  `src/sysml_codegen/elaboration/elaborate.py:2372`, `elaborate.py:2451`, and
  `elaborate.py:2548`; update `extraction/expression_compiler.py:165` so calculation dependencies,
  bindings, aliases, computed attributes, and predicates consume inventory rows and cannot perform
  their own raw dependency walk.
- [ ] **Closed bindings:** replace the optional semantic path in
  `src/sysml_codegen/extraction/binding_evidence.py:181` and the raw missing-path failure at
  `elaboration/elaborate.py:2618` with the closed binding variants. Remove obsolete weak records and
  imports from `source_evidence.py` and related data models.
- [ ] **Total deep paths:** replace the filtering path at
  `src/sysml_codegen/elaboration/elaborate.py:1082` with the sole total relationship-path factory.
  Add the real `Feature`-only proof and forced mapped-`IndexExpression` refusal without treating the
  relationship selector as an expression tree.
- [ ] **Shared traversal:** delete and de-export `annotated_ast_value` from
  `src/sysml_codegen/extraction/unit_annotation.py:37`; keep IR-only unit unwrapping. Delete the dead
  `SysMLDataExtractor` name/path reconstruction cluster identified in
  [design.md#binding-and-deep-path-values-are-valid-by-construction](design.md#binding-and-deep-path-values-are-valid-by-construction).
- [ ] **Single public conversion:** modify the existing
  `src/sysml_codegen/orchestration/elaborated_pipeline.py:143` so live and admitted/capture arms
  build and consume the same inventory and convert owned failures once with exact reference,
  root-relative location, cause chain, and one code token.
- [ ] **Codegen ownership closure:** finish
  `tests/conformance/test_expression_evidence_ownership.py`; require exact manifest equality,
  evasion kills, live/off-route reachability reconciliation, and no exact-route import of the
  math-only optional Agentic IR target.
- [ ] **Dependency contract:** pin Agentic `0.1.3` and `semantic-evidence/v2`, bump Codegen to `0.1.1`,
  and update `_upstream_pins.py`, `pyproject.toml`, package version tests, and `uv.lock` per
  [design.md#codegen-pin-and-dependency-contract](design.md#codegen-pin-and-dependency-contract).

### Validation

**Automated:**

- [ ] Run focused expression evidence, binding, compiler, unit annotation, source identity,
  extraction, conversion-boundary, and ownership tests. All Phase-1 Codegen representation and
  selector red nodes must be green.
- [ ] Run `uv run --extra dev mypy --strict
  src/sysml_codegen/extraction/binding_source.py
  src/sysml_codegen/elaboration/expression_evidence.py`; require zero errors.
- [ ] Run the repository-wide mypy baseline comparison and targeted Ruff over every changed Python
  file; no new item-caused diagnostic.
- [ ] Prove the exact resolver rejects an indexed use, legacy fact, IR node, and duck-typed
  lookalike at runtime.
- [ ] Prove strict and lenient live/admitted calls produce the same public evidence-integrity
  refusal and no graph or snapshot for the focused failure set.
- [ ] Prove the sealed from-snapshot route cannot import or call the raw site enumerator or reference
  inspector.
- [ ] Prove `git diff C_base -- src/sysml_codegen/elaboration/occurrence.py` remains empty and rerun
  the focused D1-D4 tests.

**Manual:**

- [ ] Trace one calculation dependency and one binding from `inspect_reference_uses` through the
  inventory to the existing occurrence resolver. Confirm there is no second raw selector or name
  reconstruction.
- [ ] Inspect off-route rows and verify their exclusions are mechanically reachable from the public
  roots rather than prose assertions.

**What we know works after this phase:** weak evidence cannot be represented at Codegen's exact
boundary, every consumer has an observable backstop, and D1-D4 remain the unchanged occurrence core.

**Rollback/stop rule:** if a production consumer still needs a raw expression for dependency
resolution, return to the owning Agentic or Codegen design boundary. Do not add a compatibility
default or optional inventory lookup.

---

## Phase 4: Close public routes and registry authority

### Goal

Prove the full natural-route matrix, remove caller-supplied registry authority, reconcile outputs and
documentation, and establish a production-ready candidate. This phase closes `audit3-F1` and CI-2
through CI-5 in behavior; the product-lens block is not marked clear until Phase 5 names the green
production commit. See [design.md#d9-b9-fails-before-output-mutation](design.md#d9-b9-fails-before-output-mutation),
[design.md#evidence-and-public-boundary-matrix](design.md#evidence-and-public-boundary-matrix), and
[design.md#static-removal-checks](design.md#static-removal-checks).

### Assumption under test

Once both evidence boundaries are closed, every live, admitted, and capture consumer can prove exact
success or named refusal, and every exported registry route can derive its complete wrapper set from
the graph without another input account.

### Test stencil — write this first

```python
@pytest.mark.parametrize("consumer", NATURAL_EXPRESSION_CONSUMERS)
def test_public_evidence_matrix(consumer, live_and_capture_routes, preserved_output):
    result = live_and_capture_routes.run(consumer.indexed_model)
    assert result.diagnostic.code == "SI_INDEXED_SOURCE_UNSUPPORTED"
    assert result.diagnostic.reference == consumer.authored_reference
    assert result.inventory_refused_before_consumer
    assert result.graph is None and result.snapshot_unchanged
    assert preserved_output.bytes_after == preserved_output.bytes_before
```

### Changes required

**See:** [design.md#natural-route-closure-matrix](design.md#evidence-and-public-boundary-matrix),
[design.md#public-every-and-only-mutation-proofs](design.md#public-every-and-only-mutation-proofs),
and [design.md#documentation-and-backlog-obligations](design.md#documentation-and-backlog-obligations).

- [ ] **Tests first — registry:** extend
  `tests/conformance/test_generation_exit_type_preflight.py:1`,
  `tests/conformance/test_module_kind_faildloud.py:264`, and
  `tests/unit/test_registry_generation.py:1` for no-root, one, repeated, multiple, and unsupported
  root types through CLI, direct generator, and every exported alias. Assert byte-identical output
  preservation and the absence of a caller type-set parameter.
- [ ] **Graph-derived registry:** replace the untyped failure in
  `src/sysml_codegen/generation/registry.py:48`; remove the fifth parameter at `registry.py:245` and
  the caller account at `cli/__init__.py:734`. Derive and validate wrappers from the immutable graph
  inside every exported generation seam before output mutation.
- [ ] **Full natural-route matrix:** complete
  `tests/conformance/test_expression_evidence_integrity.py` for calculation-definition dependencies,
  calculation/constraint bindings, aliases, computed attributes, predicates, and deep overrides.
  Cover exact positive, indexed, operand/depth, and missing-target cases through live and
  admitted/capture arms, strict and lenient modes where offered.
- [ ] **Dual-layer index proof:** for each expression consumer, retain the normal public test proving
  inventory-before-consumer refusal and the internal test bypassing only inventory to prove the
  consumer backstop. For deep override, pair the real `Feature`-only structural proof with forced
  mapped-index refusal.
- [ ] **Preservation and transitions:** rerun the full occurrence/producer matrix and
  `tests/execution/test_occurrence_derivation_mutation_teax.py:1`; reconcile every changed graph,
  diagnostic, package byte, and execution result against `verification/expected-transitions.md`.
  Any unlisted difference fails.
- [ ] **Ledger rows A5a and A5b:** add both to `verification/expected-transitions.md` in the same
  landing unit as the tests that prove them
  ([design.md#transition-ledger-seed](design.md#transition-ledger-seed)). They are the two measured
  `C_base` behaviors of the bare indexed chain, split because they fail differently:
  - **A5a — indexed bare chain, singular slot.** Old: zero-diagnostic graph, authored index
    silently rewritten to occurrence zero, in range or not. Required: pre-graph
    `SI_INDEXED_SOURCE_UNSUPPORTED` naming the authored reference. Proof: the `Cell[1]`
    out-of-range case in `test_expression_evidence_integrity.py`.
  - **A5b — indexed bare chain, plural slot.** Old: incidental `SI_OCCURRENCE_AMBIGUOUS`. Required:
    the `SI_OCCURRENCE_AMBIGUOUS → SI_INDEXED_SOURCE_UNSUPPORTED` transition, with the inventory
    refusing before occurrence resolution runs. Proof: the `Cell[3]` case in the same file.

  The reconciliation gate must **expect** that diagnostic transition rather than flag it as unlisted
  drift. A5a proves the silent rewrite exists at all; A5b proves the name of the refusal changes.
- [ ] **`deep_cross_scope_probe` stays refused:** confirm reconciliation shows the record still at
  typed refusal (`SI_OCCURRENCE_MISSING`, authored reference preserved) under its named A2 row. A
  result that returns it to a captured graph is the global stop condition, not a reconciliation
  outcome.
- [ ] **Static closure:** require both ownership manifests, five evasion mutations, deleted symbols,
  off-route reachability exclusions, no dead extraction helper cluster, and no caller-supplied
  registry authority to be green together.
- [ ] **Documentation and filing:** update the architecture overview, reference documents 00/01/19,
  registry reference 20, verification matrix, diagnostic reference, Agentic plant idiom, P-003
  application status, reconciliation ledger seed, current work, and the epic status as specified in
  [design.md#documentation-and-backlog-obligations](design.md#documentation-and-backlog-obligations).
  Verify the indexed-element and output-alias follow-ups remain separately owned; do not duplicate
  them if the existing rows are correct.
- [ ] **File `[DEEP-QUALIFIED-OUTPUT-WIRING]`** as a separate agent-grade backlog row before close.
  Exact wiring for a deep qualified reference to a concrete calculation output is a real, separately
  owned capability; this item refuses it by name and does not implement it. The row names the
  authored shape in `tests/fixtures/deep_cross_scope_probe/design.sysml`, the current
  `SI_OCCURRENCE_MISSING` contract, and the A2 transition record.
- [ ] **Fix the stale fixture comment** at
  `tests/fixtures/deep_cross_scope_probe/design.sysml:75`. It currently reads "Exact projection
  wires this input to the one concrete core output," which contradicts the recorded refusal and
  describes the substitution defect that was removed. Replace it with the current contract — this
  reference refuses with `SI_OCCURRENCE_MISSING` because no producer exists in the consumer's
  domain — and point at `[DEEP-QUALIFIED-OUTPUT-WIRING]`. This is a documentation change only: the
  fixture's authored reference and its refusal are unchanged, and the fixture's locked hash class
  and ledger ownership must be respected.

### Validation

**Automated:**

- [ ] Run the complete focused natural-route and registry suites with the SysIDE license; every row
  must assert code, authored reference, root-relative `file:line`, cause chain, one rendered code
  token, and no graph/snapshot/output mutation.
- [ ] Run the full Codegen default suite, scoped strict gate, repository-wide mypy comparison, and
  Ruff. No required licensed test or route may skip.
- [ ] Run the existing occurrence matrix and public every-and-only TEAx mutation suite through live
  and snapshot generation; require parity and D1-D4 behavior.
- [ ] Run baseline/transition reconciliation; all maintained outputs outside named transitions must
  remain byte-identical.
- [ ] Run exact static-set equality and symbol-absence checks in both repositories.
- [ ] Run `git diff --check` in both production repositories.

**Manual:**

- [ ] Review both indexed bare-chain results first. The `Cell[1]` out-of-range case must now refuse
  before graph construction through live and capture instead of producing a zero-diagnostic graph;
  the `Cell[3]` case must now refuse as `SI_INDEXED_SOURCE_UNSUPPORTED` rather than
  `SI_OCCURRENCE_AMBIGUOUS`. Together they match the product-lens falsifier exactly.
- [ ] Review registry failure through the real public command and confirm the output directory's
  complete relative-path-to-bytes map is unchanged.
- [ ] Confirm no documentation claims Phase-5 artifact evidence before those artifacts exist.

**What we know works after this phase:** the three closure legs are green on a production candidate,
the audited semantic and registry bypasses are closed through natural routes, and the occurrence
core still satisfies its existing public proofs.

**Rollback/stop rule:** any production change after this phase invalidates the production candidate
and restarts its affected Phase-4 gates before artifact sealing.

---

## Phase 5: Rebuild and verify the immutable artifact chain

### Goal

Name fresh `A_final`, `C_prod`, `F_final`, and direct-child `C_evidence` identities; build and test
their immutable artifacts through the committed runner; clear the implementation-time product gate;
and hand the result to an independent auditor. See
[design.md#immutable-artifact-set](design.md#immutable-artifact-set),
[design.md#acyclic-production-and-evidence-topology](design.md#acyclic-production-and-evidence-topology),
and [design.md#required-isolated-runs](design.md#required-isolated-runs).

### Assumption under test

The committed verification tooling can reconstruct the full acceptance battery from clean archives
and wheels, authenticate subprocess and import provenance, and produce the six evidence-only files
without external staging or editable sibling imports.

### Test stencil — write this first

```python
def test_certified_topology(c_prod, f_final, c_evidence, records):
    assert parent(c_evidence) == c_prod
    assert changed_paths(c_prod, c_evidence) == SIX_EVIDENCE_ONLY_PATHS
    assert fusion_pin(f_final) == c_prod
    assert records.codegen.commit == c_prod
    assert records.runner == committed_runner(c_prod)
    assert all(record.import_roots_match_artifacts for record in records.runs)
```

### Changes required

**See:** [design.md#executable-codegen-execution-pins](design.md#executable-codegen-execution-pins),
[design.md#fusion-dependency-and-lock-changes](design.md#fusion-dependency-and-lock-changes), and
[design.md#commit-boundary-is-closed](design.md#acyclic-production-and-evidence-topology).

- [ ] **Tests first — provenance and topology:** extend
  `tests/conformance/test_evidence_artifact_topology.py:1`,
  `tests/unit/test_environment_pins.py:1`, `tests/unit/test_teax_discovery.py:1`, and verification
  tool tests to reject external run staging, wrong roots/hashes, missing explicit TEAx paths,
  unexpected skips, dirty sources, wrong parents, extra evidence paths, and self-reference.
- [ ] **Committed runner:** finish `verification/build_artifacts.py`,
  `verification/run_independent_green.py`, and `verification/audit_evidence.py` so the runner executes
  commands, retains/authenticates output and import probes, and writes the evidence records itself.
  No external script may supply a passing status or output hash.
- [ ] **Production identities:** name the independently green Agentic commit `A_final`; land every
  Codegen production source, test, fixture, doc, version, pin, lock, probe verdict, transition file,
  and runner change in `C_prod`. Build deterministic source archives and wheels from clean
  extractions and record their hashes outside the repositories while downstream verification runs.
- [ ] **Execution pins:** update `tests/execution/environment_pins.py` and
  `tests/helpers/teax_discovery.py` to consume the closed execution-provenance manifest and explicit
  TEAx root. Reject the old sibling-shape assumption while preserving wrong-tree refusal.
- [ ] **Fusion landing:** from the frozen Fusion parent, pin Agentic `0.1.3`, Codegen `0.1.1`,
  1costingfe `0.1.0`, exact immutable Git revisions, and the Codegen `C_prod` identity in
  `pyproject.toml` and `uv.lock`. Run the maintained model roots unchanged unless a real semantic
  violation is measured. Land the verified result as `F_final`.
- [ ] **Evidence child:** create `C_evidence` directly on `C_prod` with exactly
  `verification/dependencies.json`, `wheelhouse-requirements.txt`,
  `execution-provenance.json`, `independent-green.json`, `reconciliation-ledger.md`, and
  `evidence-lock.json`. No other path changes; no evidence file names or hashes `C_evidence`, and
  the lock does not hash itself.
- [ ] **Implementation-time product gate:** append the production result to the product-lens ledger
  only after the licensed live-and-capture indexed computed-attribute proof is green at `C_prod`.
  Record `audit3-F1` as fixed from that exact identity; do not clear it from a worktree-only run.

### Validation

**Automated artifact runs:**

- [ ] From the Agentic source archive, run focused semantic-evidence tests, the fast suite, scoped
  strict checking, repository-wide mypy baseline comparison, and Ruff. Do not run the retired PDF
  or paid/network cases.
- [ ] From frozen 1costingfe source, run its complete pytest suite and configured Ruff.
- [ ] From frozen TEAx source, run the simkit and battery-demo suites named in the design.
- [ ] From the Codegen source archive, run the scoped strict gate, repository-wide mypy comparison,
  default and licensed suites, live/snapshot parity, generated-package tests, and complete execution
  lane with manifest-pinned imports.
- [ ] From the Fusion source archive, run `uv lock --check`, its configured suite, complete model
  validation, and final generated Fusion/TEAx execution and mutation proofs using only the recorded
  wheels and extracted sources.
- [ ] Enforce the no-unexpected-skip rule and record selected, passed, failed, error, skipped,
  xfailed, and deselected counts for each pytest invocation.

**Automated topology and reconstruction:**

- [ ] Rebuild the Codegen archive and wheel from `C_prod`; require exact filename and SHA-256 matches
  with `dependencies.json`.
- [ ] Prove Fusion pins `C_prod` and never `C_evidence`, an editable source, or a sibling path.
- [ ] Prove `C_evidence^ == C_prod` and its changed-path set is exactly the six evidence-only files.
- [ ] Recompute every dependency, artifact, run-output, evidence-file, and lock digest.
- [ ] Run the committed mechanical auditor with explicit `C_prod`, `F_final`, and `C_evidence`
  inputs; require every group green.
- [ ] Confirm original user checkouts retain their entry status digests.

**Manual:**

- [ ] Review `independent-green.json` against retained command output and import probes. Confirm the
  committed runner, rather than external staging, produced every asserted status and hash.
- [ ] Review the final reconciliation ledger and ensure L-01-L-14/U-1-U-2 each names a final test
  and production identity without overstating a baseline or unrun case.
- [ ] Prepare the exact identity and artifact-hash handoff for an independent `$my-audit`. Do not
  self-certify or close the item in this phase.

**What we know works after this phase:** the semantic closure is green on immutable production
artifacts, Fusion consumes the certified Codegen identity, the evidence child is acyclic and
reconstructable, and an independent auditor has a complete handoff.

**Rollback/stop rule:** any Phase-5 failure caused by production source, tests, fixtures, docs,
package metadata, pins, or runner logic returns to the owning production phase and creates a new
dependent identity chain. Never repair it only in `C_evidence`.

---

## Risk Management

**See:** [design.md#potential-risks](design.md#potential-risks).

- **Selector inventory misses an evasion:** exact AST set equality plus direct, literal-`getattr`,
  local-alias, imported-alias, and dynamic-`getattr` mutation kills are Phase-1 tests and Phase-4
  gates.
- **Inventory and consumer backstop become indistinguishable:** every indexed route has two tests,
  one proving downstream consumers did not run and one bypassing only inventory to exercise the
  backstop.
- **Closed types are weakened by the wider repository type baseline:** the four narrow boundary
  files have separate zero-error strict gates; repo-wide baselines cannot waive them.
- **A red is recorded that comes from the wrong reason:** this is what tripped Revision 2. Each red
  case names its exact expected `C_base` behavior — Case 1 a zero-diagnostic graph, Case 2
  `SI_OCCURRENCE_AMBIGUOUS` — and Phase 1's stop rule fires on any other failure, including the
  right code arriving from the wrong path.
- **The lock is re-derived instead of verified:** the three legs read the historical tree from Git
  and the lock's own `probe_fixture_commit` field; a mismatch returns the item to design and never
  authorizes a replacement lock.
- **D1-D4 are accidentally reopened:** `occurrence.py` is byte-compared to `C_base`, and the existing
  occurrence and public mutation matrices run at Phases 1, 3, and 4.
- **Final evidence certifies a convenient checkout:** every run starts from a recorded archive or
  wheel and checks resolved import roots, hashes, versions, dirty status, and explicit TEAx paths.
- **A production fix lands after sealing:** any change restarts the affected chain; the evidence-only
  child cannot absorb it.

## Environment Setup

Use the repository commands in the root `CLAUDE.md` files and the exact validation contract above.
Implementation requires clean dedicated worktrees, `uv`, Python and SysIDE versions recorded by the
artifact runner, and the existing SysIDE license supplied only through the environment. Do not
install or update unrelated dependencies as part of plan execution.

## Implementation Notes

Fill these sections during `$my-implement`. Check phase boxes immediately after validation rather
than reconstructing progress later.

### Phase 1 completion

**Completed:**

**Commits / identities:**

**Actual changes and test results:**

**Issues / deviations / rollback point:**

### Phase 2 completion

**Completed:**

**Commits / identities:**

**Actual changes and test results:**

**Issues / deviations / rollback point:**

### Phase 3 completion

**Completed:**

**Commits / identities:**

**Actual changes and test results:**

**Issues / deviations / rollback point:**

### Phase 4 completion

**Completed:**

**Commits / identities:**

**Actual changes and test results:**

**Issues / deviations / rollback point:**

### Phase 5 completion

**Completed:**

**Commits / identities:**

**Actual changes and test results:**

**Issues / deviations / rollback point:**

---

**Status progression:** Draft → In Progress → Complete

**Next stage after plan approval:** `$my-implement`, followed by an independent `$my-audit`.
