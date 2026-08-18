# Implementation Plan: Stop Reinventing the Parser

**Status:** In Progress — Phases 1-2 complete; Phase 3 halted at `b4e97dd` and restructured here
**Revision:** 4
**Created:** 2026-08-17
**Last Updated:** 2026-08-18
**Phase Strategy Approved:** 2026-08-17
**Complexity:** HIGH

## Source Documents

- **Spec:** [spec.md](spec.md) — approved Revision 4
- **Design:** [design.md](design.md) — Revision 8, the targeted amendment of Revision 7, itself the
  targeted amendment of the approved Revision 6
- **Design review:** [design-review.md](design-review.md) — Revision-6 verdict `Approve`; targeted
  Revision-7 verdict `Revise`, must-fix set applied and orchestrator-verified 2026-08-17; targeted
  Revision-8 verdict `Revise`, must-fix set applied and orchestrator-verified 2026-08-18
  ("Design Revision 8 is approved for consumption by the plan revision")
- **Phase 3 stop report:**
  [run-records/phase3-stop-report.md](run-records/phase3-stop-report.md) — rulings 1-4 owner-ruled
  2026-08-18; the cause of **this** revision
- **Phase 2 audit:** [run-records/phase2-audit.md](run-records/phase2-audit.md) — `Pass with
  findings`; its m3 disposition is re-based by Phase 2b below
- **Phase 1 stop report:**
  [run-records/phase1-stop-report.md](run-records/phase1-stop-report.md) — rulings 1-7
  owner-ratified 2026-08-17; the cause of Revision 3
- **Audit:** [audit.md](audit.md) — failed-candidate verdict `Needs Work`
- **Product lens:** [product-lens.md](product-lens.md) — `audit3-F1` remains blocked until the
  production indexed-consumer proof is green
- **Revision research:**
  [expression-evidence boundary convergence assessment](../../research/20260817-164828_expression-evidence-boundary-convergence-assessment.md)
- **Failed candidate:** [plan.failed-candidate.md](plan.failed-candidate.md) — historical record;
  never resume its checklist

### Revision 4 note

Phase 3's first run tripped the stop rule and halted to the owner
([run-records/phase3-stop-report.md](run-records/phase3-stop-report.md)). The cause was a design
premise, not an implementation defect: Revision 7 required the unit operand of a `[` annotation to
be a feature reference, and that is false for every compound unit — `[kg/m^3]` is an
`OperatorExpression`. `inspect_reference_uses` therefore refused every compound-unit model on the
real corpus, and compound units are pervasive in exactly the models this product serves. Two
further premise conflicts were surfaced beside it: the raw-selector manifest cannot go green by
deletion for 11 of its rows, and `annotated_ast_value`'s deletion removed a value-site rule with no
upstream replacement. The owner ruled on all four; design Revision 8 encodes the rulings and its
targeted review is closed.

This revision consumes that amendment and restructures the remaining run:

- **New [Phase 2b](#phase-2b-land-the-shared-unit-primitive)** — the two rulings that fix the
  blocker land in **Agentic**, which Phase 3 treated as read-only. Phase 2b reopens that tree under
  its own gate, tests first, and closes with a **Phase 2 audit addendum** re-establishing the audit's
  m3 disposition on the non-emission mechanism. Codegen's dependency pin then targets that landing.
- **[Phase 3](#phase-3-make-codegen-accept-only-closed-evidence) resumes from `b4e97dd`, not from a
  rollback** **[OWNER, 2026-08-18]**. What landed there holds; the phase finishes the responsibility
  migration on top of it. The falsified "removes the ~26 unowned reads" item is restated as
  repository-wide discovery with collision-aware rows against the measured 20-row failure; the
  interim Codegen unit walk is re-implemented as policy over the shared Agentic primitive; the
  kept tests the deviation deferred are explicit checklist items; and
  `test_source_identity_extraction.py` gets its 14-row disposition table. The phase ends with a
  dedicated adversarial audit whose weak-variant obligations are recorded in its validation.
- **[Phase 4](#phase-4-close-public-routes-and-registry-authority)** is touched in one place: the
  A5b ledger row now carries **both** measured starting arms, per ruling 4. Everything else in
  Phases 4-5 stands.

Phases 1 and 2 are complete, audited, and closed. Their contract text and completion records are
history and are not rewritten here — Phase 2b re-bases one audited disposition (m3) rather than
re-opening the audit, and the strategy section's first-proof-point account of the `Cell[3]` case
describes the **strict** arm measured in Phase 1; ruling 4's lenient arm is carried in design
Revision 8's behavior matrix and in Phase 4's A5b row, which is where the reconciliation gate reads
it. Every gate not named above is unchanged.

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
contract before Codegen depends on it. Phase 2b lands the shared unit primitive that contract turned
out to need, under its own gate, because reopening Agentic reopens an audited surface. Phase 3
removes Codegen's weaker representations and raw walks. Phase 4 proves the complete public route and graph-derived registry authority. Phase 5 names
and verifies fresh immutable artifacts only after production behavior is green.

### Critical path

```text
C_base + A_base + three-leg lock verification
  -> red audit3-F1 natural-route proof (both indexed cases)
  -> Agentic semantic-evidence/v2
  -> Agentic shared unit primitive (Phase 2b; unblocks compound units)
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

### Live implementation trees and the Agentic reopening

Phases 1-3 work from dedicated worktrees under `/tmp/stop-parser-rev2/worktrees/`. Their current
state:

| Repository | Branch | Worktree | State entering Phase 2b |
|---|---|---|---|
| Agentic | `stop-parser-evidence-r2` | `/tmp/stop-parser-rev2/worktrees/agentic-mbse` | `68bca37` — Phase 2 landing plus its audit-fix pass, independently audited |
| Codegen | `stop-parser-impl-r2` | `/tmp/stop-parser-rev2/worktrees/sysml-codegen` | `b4e97dd` — one commit on top of `d257ef1`, clean, Phase 3 halted here |
| Docs | `stop-reinventing-the-parser` | `/home/reid/1cfe/sysml-codegen` | this checkout; completion records only, never implementation |

**The Agentic worktree's read-only rule is superseded, for Phase 2b only.** Phase 3 treated the
Agentic tree as a read-only upstream, which is why the compound-unit blocker could not be resolved
in place. Design Revision 8's rulings 1 and 2 land *there*, so the phase boundary must allow it
([design.md#next-stage-handoff](design.md#next-stage-handoff), consequence 1). Reopening it reopens
Phase 2's audited surface, so Phase 2b is separately gated: it re-applies every Phase-2 audited
obligation to the new bytes, and it closes with a Phase 2 audit addendum. Outside Phase 2b the
Agentic tree is read-only again, and Phase 3 consumes the Phase-2b commit as its upstream.

The reopening lands under the **same** package contract — Agentic `0.1.3`,
`SEMANTIC_EVIDENCE_API_VERSION = "semantic-evidence/v2"`. Design Revision 8 keeps that contract
because the artifact was never released
([design.md#agentic-semantic-contract](design.md#agentic-semantic-contract);
[design.md#next-stage-handoff](design.md#next-stage-handoff)). No new version is minted, and
Codegen's pin is unchanged in value — only the bytes it is verified against move from `68bca37` to
the Phase-2b commit.

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

*Served 2026-08-17: the pause was taken, the owner reviewed Phase 1, and the run was resumed by
the owner for Phases 2-5 (owner-present edit).*

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

- [x] **Base and lock verification:** record clean implementation-worktree status; prove the two
  retained commits are ancestors of `C_base` with their recorded parent relationship; run the three
  legs of [lock verification](#lock-verification--three-legs-not-one-recompute) — fixture inputs
  against `20f9e60a` read from the lock's own `probe_fixture_commit` field, current outputs through
  the committed transition-ledger validators, and the six verification/probe rows at current bytes
  with every difference ledger-owned; run the existing probe/fixture, baseline, and artifact
  topology checks in `tests/unit/test_coverage_probes.py:1`,
  `tests/conformance/test_baselines.py:1`, and
  `tests/conformance/test_evidence_artifact_topology.py:1`.
- [x] **Committed historical-tree lock check (new kept test):** today the lock leg exists only as a
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
- [x] **Codegen tests first:** extend
  `tests/conformance/test_expression_evidence_integrity.py:1` with **both** indexed red cases —
  the `Cell[1]` out-of-range singular-slot case and the `Cell[3]` plural-slot case — through the
  licensed live/admitted/capture seed, with exact diagnostic fields, downstream-entry and
  occurrence-resolution spies, and the snapshot byte-preservation assertion. Add the
  operator-wrapped form as positive regression coverage, not as a red-set member. Add the initial
  consumer table for calculation dependencies, bindings, aliases, computed attributes, predicates,
  and deep overrides.
- [x] **Codegen ownership harness:** add
  `tests/conformance/test_expression_evidence_ownership.py` with the initial reviewed selector rows,
  public-root reachability checks, deleted-symbol inventory, and the five AST evasion mutations from
  [design.md#checked-consumer-and-ownership-manifests](design.md#checked-consumer-and-ownership-manifests).
- [x] **Agentic tests first:** add `tests/test_sysml/test_reference_use.py` and
  `tests/test_sysml/test_semantic_selector_ownership.py` with the closed-variant, consumer, selector,
  and symbol-absence expectations. They must expose the current permissive helpers and boolean marker
  rather than grandfathering them.
- [x] Commit only tests/manifests and phase records on the two implementation branches. Record the
  exact expected-red node IDs; no production source changes in this phase.

### Validation

**Automated:**

- [x] Run the retained Codegen probe/baseline/topology tests and require green results.
- [x] Run all D1-D4 occurrence and mutation tests named under
  [design.md#occurrence-and-producer-matrix](design.md#occurrence-and-producer-matrix); require no
  regression.
- [x] Run the new focused Agentic and Codegen tests. Require failures to equal the recorded red set:
  **both** indexed natural-route cases with their stated reasons — Case 1 a zero-diagnostic graph,
  Case 2 `SI_OCCURRENCE_AMBIGUOUS` — plus weak representation/symbol closure and ownership-manifest
  differences.
- [x] Run the new committed historical-tree lock check; require it green.
- [x] Prove `git diff C_base -- src/sysml_codegen/elaboration/occurrence.py` is empty.
- [x] Rerun the three lock legs at the end of the phase as well as the start.

**Manual:**

- [x] Inspect the Case 1 trace and confirm the graph is produced with zero diagnostics and the
  authored reference collapsed to `cells[0].mass`, matching `audit3-F1`. Inspect the Case 2 trace
  and confirm the refusal is `SI_OCCURRENCE_AMBIGUOUS`, on the plural slot rather than the authored
  index. Do not accept a fixture, license, import, or harness failure as either red.
- [x] Confirm no command imported production code from the documentation checkout or an unrecorded
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

- [x] **Tests first:** complete `tests/test_sysml/test_reference_use.py`; extend the existing
  expression, aggregation, binding, ADR002, adapter, error, type, and public-export tests. Cover exact
  positive evidence, mapped `IndexExpression`, operand failure, depth exhaustion, missing target and
  leaf, document tiers, aggregation refusal, ordered binding evidence, and ADR002 dynamic handling.
- [x] **Closed boundary:** update `src/agentic_mbse/errors.py:5` and add
  `src/agentic_mbse/sysml/reference_use.py` with the error/value/inspector boundary specified in the
  design. Keep the neutral `ExpressionIR` separate.
- [x] **Owned acquisition:** update `src/agentic_mbse/sysml/syside_adapter.py` and
  `src/agentic_mbse/sysml/expression.py:589` so mapped metatypes, total operand materialization,
  shared depth, exact targets, authored form, and `DocumentTier` are the sole evidence owners.
- [x] **Natural Agentic consumers:** migrate
  `src/agentic_mbse/sysml/aggregation.py:251`, `aggregation.py:426`,
  `sysml/binding.py:164`, and `validation/adr002.py:641`; update
  `constraint_extraction.py` to share the exact document-tier operation.
- [x] **Atomic deletion:** remove `extract_feature_refs`, `feature_reference_facts`,
  `feature_chain_facts`, `ResolvedSemanticReferenceFact`, `has_index_segment`, `ExpressionRef`, and
  `BindingInfo.references`, including `src/agentic_mbse/sysml/__init__.py:67`, top-level exports,
  lazy aliases, tests, and docs. Do not retain a deprecation path.
- [x] **Ownership closure:** finish `tests/test_sysml/test_semantic_selector_ownership.py` so the
  discovered selector set equals the reviewed Agentic manifest, all five evasion mutations die, and
  the math-only optional IR target remains explicitly non-authoritative.
- [x] **Package contract:** bump Agentic to `0.1.3`, update `pyproject.toml`, package version,
  `uv.lock`, public API assertions, and `docs/patterns/plant-idiom.md` as required by
  [design.md#documentation-and-backlog-obligations](design.md#documentation-and-backlog-obligations).

### Validation

**Automated:**

- [x] Run the focused Agentic reference-use, adapter, expression, aggregation, binding, ADR002,
  export, and ownership tests; all Phase-1 Agentic red nodes must be green.
- [x] Run `uv run mypy --strict src/agentic_mbse/errors.py
  src/agentic_mbse/sysml/reference_use.py`; require zero errors.
- [x] Run the fast Agentic suite with the SysIDE license and `-m "not slow"`; enforce the declared
  skip set and do not run the retired PDF or paid/network cases.
- [x] Run repository-wide mypy and Ruff as baseline comparisons; require no new item-caused result
  and targeted Ruff success for every changed Python file.
- [x] Run static symbol/import searches and public-export tests; every deleted identifier and alias
  must be absent from production and public barrels.
- [x] Build a clean Agentic source archive and wheel from the phase commit; run the same focused and
  fast gates from the extracted archive and verify installed version/API markers.

**Manual:**

- [x] Inspect one exact reference payload from each natural consumer and confirm it retains root,
  members, leaf, owner, document, authored form, order, and location without carrying operator or
  literal structure.
- [x] Confirm `IndexExpression` dispatch comes from the mapped SysIDE metatype and never from a
  runtime class-name comparison.

**What we know works after this phase:** Agentic exposes one closed evidence contract, every
measured Agentic consumer uses it, and the weak fact/helper surface no longer exists.

**Rollback/stop rule:** a consumer that cannot migrate without reconstructing the weak route is a
design conflict. Stop rather than add a wrapper, compatibility alias, or manifest exemption.

---

## Phase 2b: Land the shared unit primitive

### Goal

Unblock compound units and give the annotation's parser shape one owner. Reopen the Agentic tree at
`68bca37`, retire the two shape assertions design Revision 8 supersedes, add
`unit_annotation_value` as the one structural reading of a `[` annotation, and make
`inspect_reference_uses` call it while still never emitting the unit operand. See
[design.md#one-total-inspection-operation](design.md#one-total-inspection-operation) — rulings 1 and
2 — and [design.md#agentic-semantic-contract](design.md#agentic-semantic-contract).

This is a separately gated phase because it reopens an audited surface. It is the entire Agentic
change authorized after Phase 2; nothing else in that tree moves.

### Why now

Phase 3 halted here. `[kg/m^3]` is an `OperatorExpression`, so the Revision-7 requirement that the
unit operand be a feature reference refused every compound-unit model on the real corpus — and
compound units are pervasive across `catf_mfe_model`, `catf_mfe_d5`, `catf_mfe_gated`, `fusion_tea`,
and `feature_metadata_multifile`. No Codegen-side accommodation is legal: catching the refusal,
pre-unwrapping the annotation, or restoring a raw AST unit walk are all the compatibility surface
this plan forbids. The fix is upstream, so the upstream reopens.

### Assumption under test

One shared primitive can own the annotation's parser shape for both callers — Agentic's reference
walk and Codegen's value-site policy — while the unit operand stays opaque, never traversed and
never emitted.

### Test stencils — write these first

```python
@pytest.mark.parametrize("annotation", ["[m]", "[kg/m^3]", "[W/(m·K)]"])
def test_a_unit_annotation_returns_its_value_operand_and_never_the_unit(annotation, model):
    expression = value_expression_for(model, annotation)
    assert unit_annotation_value(expression) is value_operand_of(expression)
    uses = inspect_reference_uses(expression)
    assert all(use.path.leaf.qualified_name != unit_name_of(annotation) for use in uses)

def test_wrong_arity_raises_and_never_returns_none(synthetic_three_operand_annotation):
    with pytest.raises(SemanticEvidenceError) as caught:
        unit_annotation_value(synthetic_three_operand_annotation)
    assert caught.value.code is SemanticEvidenceCode.EXPRESSION_KIND_UNSUPPORTED

def test_a_reference_in_the_value_operand_is_still_visited(model):
    uses = inspect_reference_uses(value_expression_for(model, "scale [m]"))
    assert [use.authored_text for use in uses] == ["scale"]
```

### Changes required

**See:** [design.md#one-total-inspection-operation](design.md#one-total-inspection-operation),
[design.md#d5-public-agentic-evidence-contract](design.md#d5-public-agentic-evidence-contract), and
[design.md#agentic-semantic-contract](design.md#agentic-semantic-contract).

- [ ] **Reopen the tree.** Verify `/tmp/stop-parser-rev2/worktrees/agentic-mbse` is clean at
  `68bca37` and both user checkouts report an empty `status --porcelain`. Rollback point for this
  phase: reset `stop-parser-evidence-r2` to `68bca37`.
- [ ] **Tests first**, in their own commit, red for their stated reasons before any production edit.
  The owner's four required coverage cases, per
  [design.md#evidence-and-public-boundary-matrix](design.md#evidence-and-public-boundary-matrix):
  - a simple `[m]`;
  - representative compound forms `[kg/m^3]` and `[W/(m·K)]`, which must **elaborate rather than
    refuse** — these are the cases that are red today;
  - a wrong-arity annotation through a synthetic node, which must raise
    `SemanticEvidenceError(EXPRESSION_KIND_UNSUPPORTED)` and never return `None`;
  - a reference in the **value** operand, proving the value side is still visited while the unit
    side is never emitted.
- [ ] **Retire the two superseded assertions.** At the audited `68bca37`, `_unit_annotation_value`
  (`src/agentic_mbse/sysml/reference_use.py:316`) refuses a non-feature-reference unit operand with
  `EXPRESSION_KIND_UNSUPPORTED` and an unresolved unit referent with `RESOLVED_TARGET_MISSING`, and
  kept tests in `tests/test_sysml/test_reference_use.py` pin both. **Both refusals and both
  assertions go** — they encode exactly the requirements ruling 1 drops. This is a deletion, not a
  weakening: what replaces them is the stronger non-emission fact below. The **arity** refusal
  survives and becomes the primitive's.
- [ ] **Add the primitive.** `unit_annotation_value(expression) -> Any | None` in the Agentic
  boundary: recognize `[` by **mapped metatype and operator, never a runtime class name**; enforce
  exactly two operands; return the value operand; leave the unit operand opaque. Wrong arity
  **raises** `SemanticEvidenceError(EXPRESSION_KIND_UNSUPPORTED)`. `None` means strictly one thing —
  the expression is not a `[` annotation at all — so a malformed annotation can never fall through
  and be walked as general math ([AGENT ruling 2026-08-18], design.md:577-585).
- [ ] **One caller inside Agentic.** `inspect_reference_uses` traverses only what the primitive
  returns. The never-emit rule is unchanged and is now the whole of m3's closure: the unit operand is
  never reached and never emitted, so a project-scoped unit cannot arrive at a consumer as a design
  dependency.
- [ ] **Export it.** Add `unit_annotation_value` to the public surface alongside the existing
  `semantic-evidence/v2` names, per
  [design.md#agentic-semantic-contract](design.md#agentic-semantic-contract). The package version
  stays `0.1.3` and the API marker stays `semantic-evidence/v2`; no other export changes.

### Validation

The Phase-2 audited obligations apply again to these bytes — the audit's evidence is dated to
`68bca37` and cannot certify a different tree.

**Automated:**

- [ ] Focused suites from the worktree: `tests/test_sysml/test_reference_use.py` and
  `tests/test_sysml/test_semantic_selector_ownership.py`. Record collected/passed counts and state
  the delta against the Phase-2 fix-pass figures (**32 passed / 20 passed** at `68bca37`), including
  the nodes removed by the two retired assertions.
- [ ] `uv run mypy --strict src/agentic_mbse/errors.py src/agentic_mbse/sysml/reference_use.py` →
  **zero errors**, from the worktree and from a clean extraction.
- [ ] Fast Agentic suite, licensed, `-m "not slow"`. Baseline at `68bca37` is **18 failed / 1893
  passed / 1 skipped**, the 18 being the declared `A_base` optional-dependency failures. Zero
  item-caused failures. **[OWNER-VERBATIM, 2026-08-17]** "do not rerun the PDF suite anymore" — the
  slow PDF/HTML corpus and the 15 paid/network cases stay unrun.
- [ ] Repository-wide baselines non-regressed: `mypy src/` **101 errors in 21 files**,
  `ruff check src/ tests/` **119 errors**; targeted Ruff clean on every changed file. Neither
  baseline is green and neither may be described as green.
- [ ] Artifact-isolated run from a fresh `git archive` of the phase commit, extracted under a path
  containing the `agentic-mbse` string the baseline path test requires. Reproduce the named set
  `pytest tests/test_sysml/ tests/test_validation/ tests/test_errors.py` and the fast-suite figure,
  and return Success from the scoped strict gate.
- [ ] `uv build --wheel`; install into a fresh venv and verify dist version `0.1.3`,
  `__version__` `0.1.3`, `SEMANTIC_EVIDENCE_API_VERSION` `semantic-evidence/v2`,
  `unit_annotation_value` importable from the public surface, and every previously deleted symbol
  still absent.

**Manual:**

- [ ] Against a live licensed model carrying a compound unit, confirm the reference uses for an
  annotated value contain the value operand's references and **nothing** from the unit operand.
- [ ] Confirm recognition of `[` comes from the mapped metatype and operator, with no runtime
  class-name comparison in the primitive.

**Phase 2 audit addendum (closes this phase):** record, in
[run-records/phase2-audit.md](run-records/phase2-audit.md), that m3's disposition is re-established
on the **non-emission** mechanism at the new commit. The Phase-2 closure rested partly on shape
validation, which ruling 1 deletes; the addendum states the replacement fact and the evidence for it
at these bytes, and names the two retired assertions. m3 is not inherited from the Phase-2 audit,
whose evidence is dated to the retired mechanism
([design.md#one-total-inspection-operation](design.md#one-total-inspection-operation)).

**What we know works after this phase:** compound-unit models elaborate again; one owner reads the
annotation's parser shape; the unit operand is never emitted; and the Agentic artifact Codegen pins
is green on its own gates at bytes an audit record actually covers.

**Rollback/stop rule:** if the primitive cannot be recognized without a runtime class name, or if
making compound units elaborate requires relaxing the never-emit rule, that is a design conflict.
Stop and report; do not add a Codegen-side accommodation.

---

## Phase 3: Make Codegen accept only closed evidence

### Goal

Build the pre-graph evidence inventory, closed binding variants, exact-only resolver adapter, and
total deep-relationship path. Remove Codegen's raw expression and optional-path bypasses while
leaving D1-D4 source and behavior intact. See
[design.md#d7-one-codegen-conversion-boundary](design.md#d7-one-codegen-conversion-boundary),
[design.md#binding-and-deep-path-values-are-valid-by-construction](design.md#binding-and-deep-path-values-are-valid-by-construction),
and [design.md#scoped-strict-type-boundary](design.md#scoped-strict-type-boundary).

### Starting state — resume from `b4e97dd`, no rollback

**[OWNER, 2026-08-18]** The phase resumes on `stop-parser-impl-r2` at **`b4e97dd`**, one commit on
top of `d257ef1`. The stop report's rollback point is **not** taken; what landed there holds and the
phase finishes the responsibility migration on top of it. Verify the worktree is clean at `b4e97dd`
before starting, then re-pin the upstream to the Phase-2b Agentic commit.

Landed and holding at `b4e97dd`
([run-records/phase3-stop-report.md](run-records/phase3-stop-report.md)):

- the 12 indexed bare-chain red nodes are green — both cases, all three public arms, strict and
  lenient, asserting `code == SI_INDEXED_SOURCE_UNSUPPORTED`, `reference == "cells#(2).mass"`,
  `source_file == "root-0/model.sysml"`, `source_line == 15`, refusal before consumers and before
  `OccurrenceIndex.resolve_address`, and no graph or snapshot bytes. Not one assertion was weakened;
- `elaboration/expression_evidence.py` and `extraction/binding_source.py` exist and the scoped strict
  gate returns zero on both;
- the deletions with no compatibility surface: `SourceReferenceEvidence`, `SourceForm`,
  `screen_source_readiness`, the four `binding_evidence` builders, `annotated_ast_value`,
  `_reject_indexed_sources`, `_expression_references`, `_reference_from_elements`,
  `_UnsupportedExpressionError`, and the dead `SysMLDataExtractor` reconstruction cluster;
- `git diff C_base -- src/sysml_codegen/elaboration/occurrence.py` is empty, and
  `deep_cross_scope_probe` was never restored to a captured graph.

Still open, and the content of the resumed phase: the ownership-manifest closure, the Codegen
value-site policy over the shared primitive, the missing kept tests, the disposition table, the
carried Phase-1 audit findings, the dependency pin, the D1-D4 rerun, and the extraction-based full
suite.

**Tests-after deviation, conditionally accepted** **[OWNER, 2026-08-18]**. The first run wrote some
production before its focused tests. There is **no history rewrite**. The conditions are binding and
appear as checklist items below: the missing constructor / inventory / deep-path / manifest kept
tests are added before Phase 3 closes; important boundaries are mutation-tested; the closing audit is
adversarial and tries the weak variants listed in this phase's validation. **The audit does not
substitute for a missing kept test.**

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

Items already satisfied at `b4e97dd` are verified against the tree and checked off, not redone. An
item whose evidence is not reproducible at that commit is unfinished.

- [ ] **The missing kept tests — write these before anything else in this resumption.** The
  tests-after deviation is accepted on the condition that these land before the phase closes
  **[OWNER, 2026-08-18]**. Each is a kept test, not a probe:
  - [ ] direct **constructor / exhaustiveness** tests on the closed variants — an index marker cannot
    be represented as an exact reference, and the union is handled exhaustively at every switch;
  - [ ] **inventory missing** and **inventory duplicate** tests;
  - [ ] **per-consumer inventory-bypass** tests, one per consumer adapter, proving the closed-union
    backstop independently of the inventory refusal;
  - [ ] **deep-path totality** tests, including the missing middle segment;
  - [ ] **manifest** tests for the ownership rows added below.
  Mutation-test the important boundaries: for each, introduce the weakening a regression would
  actually make and require the test to die. A test that passes against its own weakened
  implementation is not coverage.
- [x] **Closed boundary modules:** add
  `src/sysml_codegen/extraction/binding_source.py` and
  `src/sysml_codegen/elaboration/expression_evidence.py` with the narrow strict surfaces described
  in the design. *(Landed at `b4e97dd`; scoped strict returns zero on both. Verify, do not redo.)*
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
- [x] **Shared traversal:** delete and de-export `annotated_ast_value` from
  `src/sysml_codegen/extraction/unit_annotation.py:37`; keep IR-only unit unwrapping. Delete the dead
  `SysMLDataExtractor` name/path reconstruction cluster identified in
  [design.md#binding-and-deep-path-values-are-valid-by-construction](design.md#binding-and-deep-path-values-are-valid-by-construction).
  *(Landed at `b4e97dd`. The value-site rule it carried is re-homed by the next item.)*
- [ ] **The value-site policy sits over the shared primitive.** `annotated_ast_value`'s deletion
  removed a rule with no upstream replacement: the elaborator's *value-shape* decision used it too,
  and without the unwrap `= 0.2 [m]` reads as general math and mints a computed node instead of a
  literal value site. `b4e97dd` resolved that with an interim
  `expression_evidence.unit_annotated_value` implemented over Agentic's `materialize_operands` — the
  behavior is right and the owner **ratified it in substance**, but it is still a Codegen-owned AST
  unit walk. Re-implement it as **policy only** over Phase 2b's `unit_annotation_value`
  ([ruling 2](design.md#one-total-inspection-operation)): Codegen keeps the decision that `0.2 [m]`
  is a literal value site and delegates **all** structural interpretation — metatype, operator, and
  operand shape — to the primitive. It performs no operand indexing, no arity check, and no metatype
  test of its own. It does **not** catch the primitive's arity refusal; that error reaches the D7
  boundary and converts once to `SI_EVIDENCE_INCOMPLETE`. When this lands, no Codegen-owned unit walk
  survives.
- [ ] **Single public conversion:** modify the existing
  `src/sysml_codegen/orchestration/elaborated_pipeline.py:143` so live and admitted/capture arms
  build and consume the same inventory and convert owned failures once with exact reference,
  root-relative location, cause chain, and one code token.
- [ ] **Codegen ownership closure — repository-wide, collision-aware, not by deletion.** Revision 3
  carried Phase 1's premise that this phase "removes the ~26 unowned reads". **That premise is
  false** for 11 of them and is replaced by [ruling
  3](design.md#the-codegen-gate-keeps-repository-wide-scope). Finish
  `tests/conformance/test_expression_evidence_ownership.py` to this target instead:
  - [ ] **Keep repository-wide discovery.** Adapter-import scoping is rejected for the Codegen gate.
    Phase 2 used it on the Agentic side (audited deviation 2) and the Phase-2 audit recorded the hole
    it leaves — a helper can receive a live SysIDE node as an argument and read a raw selector off it
    without importing the adapter (m2, still open). Making that scope load-bearing here would turn a
    known residual into a legal escape. **A red count that shrinks because the scan narrowed is not
    progress.**
  - [ ] **Add collision-aware reviewed rows** for the two name collisions: `.operands` on the neutral
    `ExpressionIR` dataclasses (`elaboration/graph.py`, `elaboration/project.py`,
    `extraction/calc_compat_renderer.py`, `extraction/modeled_defaults.py`,
    `generation/predicate_compiler.py`, `generation/constraint_name_safety.py`) and `.referent` on
    Codegen's own `SourceFile` dataclass (`extraction/source_manifest.py` ×4,
    `orchestration/elaborated_pipeline.py` ×1). These are not raw parser reads;
    `SourceFile.referent` is a **serialized snapshot key**, so renaming it changes sealed bytes.
  - [ ] **Give each collision row its defined proof artifact**, per
    [design.md#the-codegen-gate-keeps-repository-wide-scope](design.md#the-codegen-gate-keeps-repository-wide-scope):
    the declaring type must be **provable at the read site** from a type annotation on the receiving
    parameter or attribute, or from module-local construction of the value read; and the row's proof
    is a **kept test that fails if that annotation or declaring type changes**. A prose or docstring
    claim is not a proof. An **unannotated receiver can never qualify** — it stays an unowned raw
    read and stays red. For `SourceFile.referent`, that test doubles as the rename guard.
  - [ ] **Add the adapter-free evasion mutant** — a module importing nothing, receiving the node as
    an argument, such as `def consume(node): return node.referent`. Its kill criterion is stated in
    the gate's own terms: the mutant's `(module, function, selector)` tuple must appear in the
    discovered set **and fail the manifest equality gate**. Discovery alone is not a kill. This
    mutant is what stops ruling 3's own mechanism from becoming the escape it exists to close.
  - [ ] **Close the remainder by migration or mechanical exclusion**, measured against the owner's
    **20-row** current manifest failure. Neutral-IR plus `referent` is not the whole closure.
    `usage_extractor`'s genuine raw reads and any unresolved off-route module **stay red** until one
    of those lands.
  - [ ] Keep the rest of the gate's contract: exact manifest equality, the five evasion kills,
    live/off-route reachability reconciliation, and no exact-route import of the math-only optional
    Agentic IR target.
- [ ] **Disposition table for `tests/conformance/test_source_identity_extraction.py`.** The file
  imports deleted legacy owners (`parameter_groups`, `pipeline_builder`) and **blocks collection
  today**; Phase 3 cannot close while it stands unchanged. **[OWNER, 2026-08-18]** it may be removed
  **only** with a **14-row disposition table** — one row per test function in the file, each giving
  either a replacement test ID or a precise retirement reason, judged against the responsibilities
  recorded at [`ledger-4a.md:628`](../../ledger/ledger-4a.md) (row `L-181`). **Replacements land in
  the same commit that deletes the file.** The 14 rows:
  `test_chain_target_is_the_redefining_feature`, `test_deep_chain_retains_exact_leaf_target`,
  `test_def_and_usage_context_referent_classes`, `test_written_form_separates_qualified_from_bare`,
  `test_usage_owned_fact_owner_matches_live_part_usage`,
  `test_cross_owner_consumers_share_one_exact_referent`, `test_bound_formal_identity_is_exact`,
  `test_aggregation_terms_retain_exact_targets`,
  `test_occurrence_override_value_sites_carry_exact_identity`,
  `test_authored_literal_is_a_distinct_evidence_class`,
  `test_indexed_source_is_evidence_not_flattened`,
  `test_self_binding_detected_despite_same_named_outer`,
  `test_shadowed_reference_is_not_a_self_binding`, `test_expression_source_disposition`. Record the
  table in the Phase 3 completion section and update the ledger row.
- [ ] **Carried Phase-1 audit findings — close them and cite the closure.**
  - [ ] **Minor 6:** all four `REVIEWED_ROWS` in `test_expression_evidence_ownership.py` name
    closure-proof tests that did not exist. When this phase's tests land, make
    `test_every_reviewed_row_names_a_closure_proof` **resolve** each named proof to a real test — the
    sibling `test_every_named_proof_in_the_consumer_table_resolves` is the model — not merely check
    for non-empty strings.
  - [ ] **Minor 7:** off-route reachability is proved by direct imports only (`_imports_of` parses
    one file). Make it **transitive** from the public roots. Required before Phase 4's closure gate;
    the ownership file is this phase's.
  - [ ] **Minor 8:** `tests/conformance/test_probe_fixture_lock.py:140-158` leg-3 ledger-ownership
    check substring-matches the whole ledger file. Parse the row for the path and check **both**
    hashes within that row.
  - [ ] **Informational 12:** the lock's row classifier counts `verification/fixture-manifest.json`
    as a fixture input via the `or path.startswith("verification/")` clause, which would absorb a
    future verification-code row into the wrong class. Decide fixture inputs and verification-code
    rows **structurally**, without changing what the lock covers.
- [ ] **Dependency contract:** pin Agentic `0.1.3` and `semantic-evidence/v2` — **at the Phase-2b
  commit's bytes**, not `68bca37` — bump Codegen to `0.1.1`, and update `_upstream_pins.py`,
  `pyproject.toml`, package version tests, and `uv.lock` per
  [design.md#codegen-pin-and-dependency-contract](design.md#codegen-pin-and-dependency-contract).
  The pin *values* are unchanged by Phase 2b; the artifact they are verified against moves.

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
- [ ] **Compound-unit elaboration proof — the stop's own falsifier.** The models that refused at the
  stop must elaborate again. Run the `catf_mfe_*` fixtures (`catf_mfe_model`, `catf_mfe_d5`,
  `catf_mfe_gated`) plus `fusion_tea` and `feature_metadata_multifile`, and require no
  `SI_EVIDENCE_INCOMPLETE` from a unit annotation. The five
  `tests/unit/test_elaboration_expose_shapes.py` tests that failed at the stop must be green.
  Record the distinct compound forms exercised — `[$/MWh]`, `[10^19 m^-3]`, `[kg/m^3]`, `[m³/s]`,
  `[MW·yr/m²]`, `[Pa·m³/s]`, `[W/(m·K)]`, and the rest of the stop report's list.
- [ ] Prove `git diff C_base -- src/sysml_codegen/elaboration/occurrence.py` remains empty and rerun
  the focused D1-D4 tests.
- [ ] Confirm `deep_cross_scope_probe` is still at typed refusal and was never restored to a captured
  graph — the global stop condition.
- [ ] Run the **extraction-based** full Codegen suite. From a plain worktree the default suite does
  not fully run (pre-existing at `C_base`: 6 modules fail collection, 10 further tests fail with
  `ArtifactSourceInputError`), so build a fresh extraction the way Phases 1-2 did and report the
  authoritative numbers from there. Focused suites may run from the worktree.

**Manual:**

- [ ] Trace one calculation dependency and one binding from `inspect_reference_uses` through the
  inventory to the existing occurrence resolver. Confirm there is no second raw selector or name
  reconstruction.
- [ ] Inspect off-route rows and verify their exclusions are mechanically reachable from the public
  roots rather than prose assertions.

**Closing gate — a dedicated adversarial Phase 3 audit** **[OWNER, 2026-08-18]**. The phase does not
self-certify. The audit's obligations, stated as the weak variants it must **try** and fail to make
work:

- [ ] **Skipped inventory** — reach a consumer without the pre-graph inventory having run.
- [ ] **Indexed-to-exact conversion** — get an `IndexedReferenceUse` accepted anywhere an
  `ExactReferenceUse` is required.
- [ ] **Shortened deep paths** — get a relationship path with a missing middle segment to resolve.
- [ ] **Adapter-free selector reads** — read a raw selector from a module that imports nothing, and
  survive the manifest equality gate.
- [ ] **Malformed unit arity** — get a wrong-arity `[` annotation to return `None` and be walked as
  general math rather than raising.
- [ ] **Missing diagnostic provenance** — produce a public refusal lacking the authored reference,
  root-relative `file:line`, cause chain, or one-code-token rendering.

Each variant must be refused by name. **The audit does not substitute for a missing kept test** — a
weak variant the audit fails to exploit is not evidence that the corresponding checklist test exists.

**What we know works after this phase:** weak evidence cannot be represented at Codegen's exact
boundary, every consumer has an observable backstop, compound-unit models elaborate through the
shared primitive, every raw selector has a reviewed owner with a real proof artifact, and D1-D4
remain the unchanged occurrence core.

**Rollback/stop rule:** if a production consumer still needs a raw expression for dependency
resolution, return to the owning Agentic or Codegen design boundary. Do not add a compatibility
default or optional inventory lookup. Rollback point for the resumed work: reset
`stop-parser-impl-r2` to `b4e97dd`.

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
  - **A5b — indexed bare chain, plural slot.** The row carries **two** measured starting states, per
    [ruling 4](design.md#transition-ledger-seed): **strict** refuses with an incidental
    `SI_OCCURRENCE_AMBIGUOUS` — a name about occurrence selection, for an index defect; **lenient**
    returns a graph carrying `SI_OCCURRENCE_AMBIGUOUS` + `SI_OCCURRENCE_MISSING`. Required: both arms
    refuse pre-graph with `SI_INDEXED_SOURCE_UNSUPPORTED`, and because the inventory refuses before
    occurrence resolution runs, the lenient graph disappears too. Proof: the parameterized `Cell[3]`
    case in the same file, which pins both starting states explicitly. The reconciliation gate must
    expect the lenient graph's disappearance as well as the diagnostic rename.

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
- **A green manifest is bought by narrowing the scan:** the Codegen gate keeps repository-wide
  discovery; collision rows need a provable declaring type plus a kept proof test, an unannotated
  receiver can never qualify, and the adapter-free evasion mutant must fail the equality gate. The
  20-row measurement is the denominator.
- **Reopening Agentic lands a change on a tree whose audit is dated to different bytes:** Phase 2b
  re-runs every Phase-2 audited obligation against its own commit and closes with an audit addendum
  re-establishing m3 on non-emission.
- **The tests-after deviation is quietly absorbed:** the missing kept tests are explicit checklist
  items with a mutation-testing obligation, and the closing adversarial audit is recorded as an
  addition to them, never a substitute.
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

**Completed:** 2026-08-17. Every Phase 1 checklist item and every validation box. No stop rule
tripped. The run halts here for the owner, per the Global Execution Contract's owner-directed
pause.

**Commits / identities:**

| Branch | Worktree | Base | Phase 1 commit |
|---|---|---|---|
| `stop-parser-impl-r2` | `/tmp/stop-parser-rev2/worktrees/sysml-codegen` | `C_base` `78a9beb9…` | `e4e26932729a49e4497c89842adf2d79b92deecb` |
| `stop-parser-evidence-r2` | `/tmp/stop-parser-rev2/worktrees/agentic-mbse` | `A_base` `2171016d…` | `85c7758` |

Both worktrees were verified clean at their pinned SHAs before any work and carry exactly one
commit each. `git diff C_base -- src/` is **empty**, and so is
`git diff C_base -- src/sysml_codegen/elaboration/occurrence.py`. `git diff A_base -- src/` is
empty. The changed-path set is tests, fixtures, and the transition ledger only:

```
tests/conformance/test_expression_evidence_integrity.py
tests/conformance/test_expression_evidence_ownership.py
tests/conformance/test_probe_fixture_lock.py
tests/fixtures/indexed_bare_chain_{singular,plural,operator}/model.sysml
verification/expected-transitions.md
tests/test_sysml/test_reference_use.py                    (agentic)
tests/test_sysml/test_semantic_selector_ownership.py      (agentic)
```

Rollback point: reset either branch to its base SHA. Nothing outside the two worktrees was
written; both original user checkouts retain their entry digests (`status --porcelain` empty).

**Actual changes and test results:**

*Base and ancestry.* `20f9e60a` and `43edf9bd` are both ancestors of `C_base`. `20f9e60a`'s parent
is `7b29d8b6` and `43edf9bd`'s parent is `20f9e60a`, matching the recorded relationship.
`43edf9bd`'s entire diff is one file, one insertion — `verification/probe-fixture-lock.json` —
confirming it is the lock file's home commit, not the tree its hashes describe.

*Three-leg lock verification.* Run at phase start and again at phase end; identical results.

- **Leg 1 — fixture inputs against the tree the lock names.** `probe_fixture_commit` read from the
  lock file equals `20f9e60a19b30bc1ec9a27aacb08380f4bc45602`. All **118** rows recompute against
  that tree, read from Git: **0 mismatches**. The lock was not re-derived and not rewritten.
- **Leg 2 — current outputs through the committed transition-ledger validators.**
  `verification/capture_baseline.py --check --check-current-batch --check-output-transitions`
  exits 0. `validate_current_batch` reports current `7f926978…`, 14 captured / 23 refused, against
  frozen `bd7bf245…` at `P_seed` `52a03cd`. `validate_output_transitions` reports 23 metadata-only
  snapshots, 22 maintained current snapshots, and the two named record transitions
  (`deep_cross_scope_probe`, `plant_value_shapes`) with their two golden rows. The committed caller
  `tests/conformance/test_stop_parser_documentation_contract.py` is green (9 passed).
- **Leg 3 — the six verification/probe rows at current bytes.** The five probe scripts are
  byte-identical to their lock-time hashes. `verification/capture_baseline.py` differs
  (lock-time `6aef97af…`, current `c8a7de07…`), exactly the one known difference, and it is now
  ledger-owned: a named row in `verification/expected-transitions.md` under a new
  "Verification-code transitions" section citing `da4aa78` and `46694e2`. Git confirms those are
  the only two commits that touched the file after `20f9e60a`.

*Committed historical-tree lock check (new kept test).* `tests/conformance/test_probe_fixture_lock.py`,
12 tests, all green. It reads `probe_fixture_commit` from the lock file and then asserts it (never
hard-codes `43edf9bd` as the tree), reads every locked path's bytes through the same `git show`
route `capture_baseline._git_bytes` uses, recomputes SHA-256 for all 118 rows, asserts anti-vacuity
on the count and on paths actually read, separately asserts leg 3's current-byte pins with the
ledger-ownership requirement, and asserts the lock file is unchanged after reading. It never reads
the working tree for historical bytes and never writes the lock.

*Retained harness.* `tests/unit/test_coverage_probes.py`, `tests/conformance/test_baselines.py`,
`tests/conformance/test_evidence_artifact_topology.py`: **37 passed**.

*D1-D4 occurrence and mutation matrix.* The occurrence, calc-domain, definition-owned-position,
multiplicity-authority, feature-typing, containment-address, identity, identity-boundary,
usage-owned-anchoring, plural-scope, and exact-group-identity modules: **125 passed, 0 failed**. No
regression.

*`deep_cross_scope_probe`.* Reads as the typed refusal `SI_OCCURRENCE_MISSING` ("exact output
`0b877fee-e8c8-5472-a0b2-24aebac57e50` has no producer in the consumer domain") and its captured
snapshot is absent. The never-restore condition holds.

*Full Codegen suite, from a fresh extraction of the Phase 1 commit with the declared
artifact-source manifest:* **9 failed, 2336 passed, 34 skipped, 0 collection errors**. The 9
failures are exactly the recorded red set below.

*Agentic fast suite* (`pytest tests/ -m "not slow"`): **28 failed, 1846 passed, 1 skipped**. 10 are
the recorded red set below. The other 18 are the `A_base` baseline and are unrelated to this item:
17 in `tests/test_web_backend.py` and 1 in `tests/test_equations.py`, all `ModuleNotFoundError` for
optional extraction dependencies (`PIL`, the web backend modules) that this plan may not install.
The owner-directed exclusion was honored: the slow PDF/HTML corpus suite was not invoked, and the
15 paid/network cases were not run.

*Baseline static checks.* `ruff check` is clean on every file this phase added or modified;
`ruff check tests/` reports the pre-existing 127-error `C_base` baseline, to which this phase adds
nothing. `mypy src/` reports the pre-existing baselines unchanged (Codegen 30 errors in 8 files,
Agentic 101 errors in 21 files); no item-caused diagnostic exists, by construction, because no
`src/` file changed. The scoped strict command is not runnable in Phase 1: its targets
(`extraction/binding_source.py`, `elaboration/expression_evidence.py`,
`sysml/reference_use.py`) are created in Phases 2-3.

**Recorded expected-red node IDs.**

Codegen (9), on `stop-parser-impl-r2` at `e4e2693`:

```
tests/conformance/test_expression_evidence_integrity.py::test_indexed_bare_chain_singular_slot_refuses_before_consumers[True]
tests/conformance/test_expression_evidence_integrity.py::test_indexed_bare_chain_singular_slot_refuses_before_consumers[False]
tests/conformance/test_expression_evidence_integrity.py::test_indexed_bare_chain_singular_slot_writes_no_snapshot
tests/conformance/test_expression_evidence_integrity.py::test_indexed_bare_chain_plural_slot_refuses_before_occurrence_resolution[True]
tests/conformance/test_expression_evidence_integrity.py::test_indexed_bare_chain_plural_slot_refuses_before_occurrence_resolution[False]
tests/conformance/test_expression_evidence_integrity.py::test_every_consumer_cell_names_a_proof
tests/conformance/test_expression_evidence_ownership.py::test_discovered_raw_selectors_equal_the_reviewed_manifest
tests/conformance/test_expression_evidence_ownership.py::test_no_dynamic_getattr_survives_in_production
tests/conformance/test_expression_evidence_ownership.py::test_deleted_symbols_are_absent
```

Agentic (10), on `stop-parser-evidence-r2` at `85c7758`:

```
tests/test_sysml/test_reference_use.py::test_the_closed_reference_use_boundary_module_exists
tests/test_sysml/test_reference_use.py::test_evidence_vocabulary_names_the_indexed_refusal
tests/test_sysml/test_reference_use.py::test_indexed_reference_use_has_no_path_attribute
tests/test_sysml/test_reference_use.py::test_exact_reference_use_carries_the_path_and_no_index_marker
tests/test_sysml/test_reference_use.py::test_the_permissive_boolean_index_marker_is_gone
tests/test_sysml/test_reference_use.py::test_an_indexed_use_cannot_form_an_aggregation_term
tests/test_sysml/test_semantic_selector_ownership.py::test_raw_selector_reads_stay_inside_the_owned_boundary
tests/test_sysml/test_semantic_selector_ownership.py::test_the_reviewed_boundary_modules_exist
tests/test_sysml/test_semantic_selector_ownership.py::test_permissive_symbols_are_absent
tests/test_sysml/test_semantic_selector_ownership.py::test_no_permissive_symbol_is_publicly_exported
```

**Each red is red for its stated reason** — verified by inspecting the measured `C_base` result,
not just the failure count.

- **Case 1**, `tests/fixtures/indexed_bare_chain_singular` (`cells : Cell[1]`, authored
  `picked = cells#(2).mass` at `model.sysml:15`). The route raises nothing. It returns an
  `InstanceGraph` whose `diagnostics` is `[]` and whose attribute inventory is
  `['IndexedBareChainSingular__array__cells[0]__mass',
  'IndexedBareChainSingular__array__picked']` — occurrence index 0, minted for an authored `#(2)`
  the singular slot cannot honor. Identical in strict and lenient modes. The capture arm seals a
  snapshot from that graph. This is the escape, and it matches `audit3-F1` and the design's
  behavior-matrix row exactly.
- **Case 2**, `tests/fixtures/indexed_bare_chain_plural` (`cells : Cell[3]`, same authored chain).
  Strict mode refuses with two diagnostics: `SI_OCCURRENCE_AMBIGUOUS` ("exact containment step
  `FeatureSlotId(...ea89dec6...)` has 3 concrete occurrences") then `SI_OCCURRENCE_MISSING`
  ("typed alias `IndexedBareChainPlural__array__picked` has no resolved target"). Both are
  occurrence-selection names raised for an index defect, and `OccurrenceIndex.resolve_address` has
  already run. That is the design's recorded starting diagnostic, pinned by the test.
- **Positive regression, not a red-set member.** `tests/fixtures/indexed_bare_chain_operator`
  (`cells#(2).mass * 1.0`) refuses correctly today with `SI_INDEXED_SOURCE_UNSUPPORTED` at
  `model.sysml:15`, in strict and lenient modes. Its test passes and stays.

No red is a fixture, license, import, or harness failure. All three fixtures parse and load; the
licensed tests ran live.

**Issues / deviations / rollback point:**

1. **Leg 2 required building a throwaway artifact root, because `capture_baseline.py` cannot run
   from a plain worktree.** At `C_base`, `verification/capture_baseline.py` resolves its Git history
   at import time through `verification/artifact_sources.py`, which demands the
   `STOP_PARSER_ARTIFACT_SOURCE_INPUTS` manifest and requires the running codegen root to be a
   declared `extracted/codegen/…` extraction. No committed script builds that manifest. To execute
   leg 2 as the plan specifies — *through the committed validators*, not a reimplementation — a
   disposable artifact root was built under `/tmp/stop-parser-rev2/` from `git archive`/`git bundle`
   of the two worktrees, and the validators ran from that extraction. Nothing was written into
   either worktree. Phase 5 builds the real artifact set; this is scaffolding, not a substitute.
2. **The default Codegen suite at `C_base` is only fully runnable from a declared extraction.**
   Run from an ordinary worktree with no manifest, 6 conformance/unit modules fail to *collect*
   (`test_ast_dispatch_invariant`, `test_exact_route_fingerprint_stability`,
   `test_hierarchy_resolver`, `test_stop_parser_documentation_contract`,
   `test_v6_snapshot_inventory`, `test_check_ledger_4a`) and 10 further tests fail in
   `test_self_binding_guidance_contract.py` and `test_check_proof_integrity.py`, all with the same
   `ArtifactSourceInputError`. Confirmed pre-existing: they all pass from an extraction of
   `C_base` itself. This is a property of the audited base, not a regression, and it is why the
   authoritative suite numbers above were taken from the extraction. The new lock check follows the
   same convention as its six sibling verification tests.
3. **Design-matrix gap, surfaced not resolved: the lenient arm of Case 2.** The design's behavior
   matrix records the `Cell[3]` bare chain as "REFUSED — `SI_OCCURRENCE_AMBIGUOUS`". Measured, that
   is the **strict** arm. Under `strict=False` the same fixture **returns a graph** carrying those
   two diagnostics rather than refusing, and that graph contains all three `cells[i]__mass`
   attributes with `picked` unresolved. The diagnostic identity is unchanged, so this is the
   documented strict/lenient delivery contract rather than a contradiction — the operator-wrapped
   form refuses in both arms because its refusal is pre-graph, which is exactly the ordering this
   item installs. It is recorded here because the design's matrix does not state the lenient row,
   and Phase 4's reconciliation gate will otherwise flag it as unlisted. **Not resolved in the
   test:** both arms are parameterized and both are red. Design should add the lenient row.
4. **Case 1 has a third red beyond the design's two.** The design names Case 1 as one kept test;
   the capture arm was written as a separate kept test
   (`test_indexed_bare_chain_singular_slot_writes_no_snapshot`) because the snapshot
   byte-preservation assertion needs its own `tmp_path` and refusal shape. Same case, same stated
   reason, split for legibility.
5. **The ownership manifests are target manifests, not `C_base` inventories.** `REVIEWED_ROWS`
   holds only the four contextual exceptions the design leaves in Codegen, so the red lists the
   ~26 unowned reads Phase 3 removes. The same applies to Agentic's `REVIEWED_MODULES`. Both
   scanners carry anti-vacuity tests that pass now, so an empty scan cannot make the gate green.
6. **`has_index_segment` appears only in the Agentic inventory.** It is Agentic's field
   (`sysml/data_models.py:89`), so Codegen's deleted-symbol list names it but finds nothing —
   correctly. Codegen's red names the five weak identifiers that do live there.

#### Audit-fix pass (2026-08-17)

The dedicated Phase 1 audit returned **Pass with findings**
([run-records/phase1-audit.md](run-records/phase1-audit.md), `d21406b`). Its four Major findings
are fixed in the kept tests. Tests only; no production bytes moved, and `occurrence.py` is still
the *same Git blob* as `C_base` (`af721562512d5684ce3dd1c96624fbe3355a536d` at both commits).

**Commits:** `stop-parser-impl-r2` `e4e2693` → **`d257ef109065832f629ea5c90c8faa11b7c47fa7`**;
`stop-parser-evidence-r2` `85c7758` → **`8d27fb3`**.

**Finding 1 — the green contract is now asserted as exact fields.** Both red tests assert
`reference == "cells#(2).mass"`, `source_file == "root-0/model.sysml"` and `source_line == 15`
as separate field equalities, plus no absolute or staged path in the rendered message. Measured
first, per arm: **all three arms report the same root-relative `source_file`**, whether the caller
passes a relative or an absolute model path, so one constant is correct for all three and there is
**no design conflict** — every arm can express a root-relative referent, and the
`SI_OCCURRENCE_AMBIGUOUS` diagnostic already does. What is broken is only the
`SI_INDEXED_SOURCE_UNSUPPORTED` shape: `reference=None`, `source_file=None`, `source_line=None`,
with a raw path in `detail` (live: the caller's absolute path; admitted/capture: the private
staged temp dir). The audit's demonstrated escape is closed — the old `endswith` matched all
three of those.

**Finding 4 — both cases now run all three public arms**, parameterized `arm × strict`. Case 1's
separate snapshot test is folded into its capture arm rather than duplicated. Each arm is red for
the same reason it will be green for.

**Finding 3 — the dynamic-`getattr` gate is scoped, measured first as instructed.** Rule: a module
is raw-SysIDE if it imports the SysIDE adapter or reads a reviewed selector. **Measured surprise,
surfaced not accepted:** the rule as first stated keyed on `import syside`, and *no production
module imports `syside` directly* — that is deliberate and stated at `extraction/extractor.py:14`;
Codegen reaches SysIDE only through `agentic_mbse.sysml.syside_adapter`. Keyed on `syside` the
clause is inert, and two modules that handle raw parser nodes without reading a reviewed selector —
`extraction/computed_attribute_extractor.py` (an audited off-route module) and
`extraction/feature_metadata.py` — would fall outside the gate. The import clause is therefore
keyed on the adapter, which is the same intent measured against how this repo actually reaches
SysIDE. Set size 16 → **21 modules**, recorded as `RAW_SYSIDE_MODULES` and pinned by
`test_the_raw_syside_module_set_is_the_recorded_one`; a companion test asserts no module imports
`syside` directly, so the premise cannot rot. `resolution/models.py` falls outside and its
unrelated red is gone. **Guardrail (b) re-verified:** every evasion mutant now carries the adapter
import, so each is inside the scoped gate, and **all five still die**; two anti-vacuity guards
prove the scope admits neither everything nor nothing.

**Finding 2 — the Agentic marker test survives its own deletion.** It resolves
`ResolvedSemanticReferenceFact` by `getattr` and reads absent annotations as empty. Verified
against all three states: class deleted → pass, class present without the marker → pass, today →
fail.

Also tightened: the operator-wrapped regression pins today's shape exactly rather than by suffix,
including the three fields the refusal does *not* carry, so Phase 3 cannot tighten that path
silently. Audit Minors 5-11 and Informational 12-14 are **not** addressed here; they are Phase 2-4
work per the audit's own placement.

**Updated red set — 25 nodes (was 19): Codegen 15 (was 9), Agentic 10 (unchanged).**

```
# Codegen, stop-parser-impl-r2 @ d257ef1 — 12 red-set + 3 manifest/table
tests/conformance/test_expression_evidence_integrity.py::test_indexed_bare_chain_singular_slot_refuses_before_consumers[{True,False}-{live,admitted,capture}]
tests/conformance/test_expression_evidence_integrity.py::test_indexed_bare_chain_plural_slot_refuses_before_occurrence_resolution[{True,False}-{live,admitted,capture}]
tests/conformance/test_expression_evidence_integrity.py::test_every_consumer_cell_names_a_proof
tests/conformance/test_expression_evidence_ownership.py::test_discovered_raw_selectors_equal_the_reviewed_manifest
tests/conformance/test_expression_evidence_ownership.py::test_deleted_symbols_are_absent

# Agentic, stop-parser-evidence-r2 @ 8d27fb3 — unchanged 10 nodes; only
# test_the_permissive_boolean_index_marker_is_gone was restructured.
```

`test_no_dynamic_getattr_survives_in_the_raw_syside_module_set` (renamed from
`…_survives_in_production`) is now **green**, which is correct: it is an anti-evasion gate, not a
red-set member, and its former red was the unrelated Pydantic validator.

**Re-verification at `d257ef1`.** All three lock legs green (118/118 against `20f9e60a`,
`capture_baseline.py` exit 0, the 12-test lock check green). Full Codegen suite from a fresh
extraction: **15 failed, 2340 passed, 34 skipped, 0 collection errors** — the 15 are exactly the
red set. Agentic fast suite: **28 failed, 1846 passed** — 10 recorded reds plus the same 18
`A_base` baseline failures (missing optional `PIL`/web-backend deps). `ruff check` clean on every
changed file. D1-D4 and the retained harness: **162 passed** — this run records the exact paths, so
the figure is traceable (audit Informational 13): `tests/conformance/`
`test_occurrence_domain_derivation.py`, `test_occurrence_calc_domain_derivation.py`,
`test_definition_owned_reference_positions.py`, `test_occurrence_multiplicity_authority.py`,
`test_feature_typing_integrity.py`, `test_usage_owned_reference_anchoring.py`,
`test_elaboration_plural_scope.py`, `test_exact_group_identity.py`, `test_baselines.py`,
`test_evidence_artifact_topology.py`; `tests/unit/` `test_elaboration_occurrence.py`,
`test_elaboration_containment_address.py`, `test_elaboration_identity.py`,
`test_occurrence_identity_boundary.py`, `test_coverage_probes.py` — 125 D1-D4 plus 37 retained
harness.

### Phase 2 completion

**Completed:** 2026-08-17. Every Phase 2 checklist item and every validation box. No stop rule
tripped; no consumer needed the weak route to migrate.

**Commits / identities:**

| Branch | Worktree | Base | Phase 2 commits |
|---|---|---|---|
| `stop-parser-evidence-r2` | `/tmp/stop-parser-rev2/worktrees/agentic-mbse` | Phase 1 `8d27fb3` | `40dee5c` (tests) → `4a3ec46` (implementation) → `144ae02` (docstring) |

Tests-first, as the contract requires: `40dee5c` lands the completed test file and the extended
ownership gate and is red for its stated reasons; `4a3ec46` lands production. The Codegen
worktree is untouched at `d257ef1`, and both user checkouts report an empty
`status --porcelain`. Rollback point: reset `stop-parser-evidence-r2` to `8d27fb3`.

**Actual changes and test results:**

*The 10 Phase-1 Agentic red nodes are green, each for its stated reason.* `test_reference_use.py`
28 passed, `test_semantic_selector_ownership.py` **14 passed** (audit m5: this line first read 12,
which was the count before the Minor-5 additions and did not match the file). The six reference-use nodes went
green because `agentic_mbse/sysml/reference_use.py` now exists with the closed union,
`INDEXED_REFERENCE_UNSUPPORTED` is in the vocabulary, `IndexedReferenceUse` has no `path`
attribute or annotation, `ExactReferenceUse` has `path` and no index marker,
`ResolvedSemanticReferenceFact` is deleted outright, and `build_aggregation_term` refuses an
indexed use by name. The four ownership nodes went green because every raw selector read now sits
inside `reference_use.py` or `syside_adapter.py`, both reviewed modules exist, and no permissive
symbol survives in the tree or the barrels.

*The closed boundary.* `inspect_reference_uses` owns the complete reference walk and returns
`ExactReferenceUse | IndexedReferenceUse` in first-seen order. `ExactSemanticPath` enforces its
invariants in `__post_init__` — non-empty segments, `segments[0] is root`, `segments[-1] is leaf`
— so there is no public optional-root or optional-leaf state. `require_exact_reference_use` is
exhaustive over the union and checks the concrete value at runtime, because the repository's full
static type lane is not a green gate. One shared `MAX_EXPRESSION_DEPTH` serves the inspector and
`traverse_expression`, and `inspect_reference_uses` takes no depth parameter.

*Authored evidence turned out to be real evidence, not a rendering.* `cst_node.text(source)`
against the owning document's locked text yields the exact authored span — measured
`'cells#(2).mass'` for the indexed fixture shape. `SysideAdapter.authored_text` acquires it once,
so authored form (`bare` / `qualified` / `chain`), text, segments, and qualifier travel on the
value and Codegen never rereads the CST to decide no-prefix semantics.

*Mapped index dispatch.* `IndexExpression` is in the adapter's closed type map and resolves to
`syside.core.IndexExpression`; `reference_use.py` contains zero `__name__ ==` comparisons. The old
route compared `type(first).__name__` against the string `"IndexExpression"`.

*Atomic deletion, no compatibility path.* All seven ordered deletions are gone from production,
exports, lazy aliases, tests, and docs — `extract_feature_refs`, `feature_reference_facts`,
`feature_chain_facts`, `ResolvedSemanticReferenceFact`, `has_index_segment`, `ExpressionRef`,
`BindingInfo.references` — along with `extract_feature_chain_name`,
`extract_feature_chain_segments`, and `extract_feature_reference_name`. A symbol sweep over
`src/`, `docs/`, and `tests/` finds zero live uses; the only surviving mentions are prose in
tests and one comment describing what was removed. The public barrels leak none of them and now
export `ExactSemanticPath`, `ExactReferenceUse`, `IndexedReferenceUse`, and
`inspect_reference_uses`. No wrapper, alias, or manifest exemption was added.

*Migrated consumers.* `aggregation.py` (both executable sites), `binding.py`, `validation/adr002.py`,
`expression.py`, `constraint_extraction.py`, plus three the static gate rediscovered beyond the
plan's measured list — `hierarchy.py`, `validation/level2_structure.py`,
`validation/level6_architecture.py`. Nothing needed to reconstruct the weak route.

*Static gates.* `mypy --strict src/agentic_mbse/errors.py src/agentic_mbse/sysml/reference_use.py`
→ **Success, no issues**, both from the worktree and from the clean extraction. Repository-wide
`mypy src/` is **101 errors in 21 files at `A_base` and 101 errors in 21 files now**; the only
diff is line-number drift on pre-existing diagnostics. Two item-caused diagnostics appeared
mid-work in `aggregation.py` and were fixed before commit, not accepted. `ruff check src/ tests/`
is **119 errors at `A_base` and 119 now**, and `ruff check` on every changed file passes.
Neither baseline is green and neither is described as green.

*Fast Agentic suite* (`pytest tests/ -m "not slow"`, licensed): **18 failed, 1883 passed,
1 skipped**. The 18 are exactly the declared `A_base` baseline — 17 in `tests/test_web_backend.py`
and 1 in `tests/test_equations.py`, all `ModuleNotFoundError` for optional extraction
dependencies this plan may not install. Zero item-caused failures. The owner-directed exclusion
was honored: the slow PDF/HTML corpus suite was never invoked and the 15 paid/network cases were
never run.

*Artifact-isolated validation.* `git archive` of `144ae02` extracted to
`/tmp/stop-parser-rev2/agentic-mbse-phase2/agentic-mbse` (the path keeps the `agentic-mbse`
string the baseline path test requires). From that extraction the fast suite
reproduced **18 failed / 1883 passed / 1 skipped** and the scoped strict gate returned Success.
(Audit m5: this line also carried a "focused gates: 221 passed" figure over an ad-hoc list of ten
files that the record never named, so nobody could reproduce it. It is replaced by the whole-suite
figure above and, in the audit-fix pass below, by a named directory-level set.) `uv build --wheel` produced
`agentic_mbse-0.1.3-py3-none-any.whl`; installed into a fresh venv it reports dist version
`0.1.3`, `__version__` `0.1.3`, `SEMANTIC_EVIDENCE_API_VERSION` `semantic-evidence/v2`, both new
codes present, all four boundary names importable, and every deleted symbol absent.

*Manual inspection 1 — one exact payload per natural consumer.* Against a live licensed model,
each payload retains root, members, leaf, owner, document, authored form, order, and location,
and carries no operator or literal structure:

- *expression traversal / aggregation* — `sum(cells.mass)` → one `ExactReferenceUse`,
  `form=chain`, `authored_text='cells.mass'`, `segments=('cells','mass')`, `plural=True`,
  root `Probe::Rack::cells` (owner `Probe::Rack`, kind `PartDefinition`, tier `Project`), leaf
  `Probe::Cell::mass` with its document URL and `source_location`, `resolved_member_names=('mass',)`.
  The `SumTerm` built from it keeps the same leaf, root, and members.
- *binding* — `in a = Rack::scale + Rack::bias` → an ordered two-element tuple, both
  `form=qualified` with `authored_qualifier='Rack'`, each carrying its exact leaf, owner,
  owner kind, tier, document, and line.
- *ADR002* — `reference_is_dynamic` returns `True` for both variants, and the indexed variant is
  counted without being flattened into an exact path or an empty list.

*Manual inspection 2 — mapped `IndexExpression` dispatch.* `SysideAdapter.get_type("IndexExpression")
is syside.IndexExpression` holds, the live index node answers the mapped `is_instance` query, and
the boundary source contains no runtime class-name comparison.

*Audit findings closed.*

- **Minor 5** — `PERMISSIVE_SYMBOLS` now names all seven ordered deletions plus the three helper
  names Phase 1 already had. `BindingInfo.references` gets a class-scoped scanner
  (`test_no_permissive_class_attribute_survives`) because a bare `references` is too common an
  identifier to scan for, with an anti-vacuity guard proving the scanner finds the field in
  `BindingInfo` and nowhere else. `test_every_ordered_deletion_is_covered_by_a_gate` pins that
  the two scanners together cover all seven, so the list cannot drift again — which was the
  finding's root cause, not just its symptom.
- **Minor 11** — `test_an_indexed_use_cannot_form_an_aggregation_term` now constructs a real
  `IndexedReferenceUse`, requires `pytest.raises(SemanticEvidenceError)` with
  `INDEXED_REFERENCE_UNSUPPORTED`, and asserts the carried reference and location. It proves the
  refusal precedes term construction by showing the same call over an equivalent *exact* use does
  return a term, so the refusal is the index being named rather than the call failing generally.

*Documentation.* `docs/patterns/plant-idiom.md` already carried the seven supported shapes; Phase 2
adds "The indexed form is valid SysML, and not implemented" — the authored shape, both diagnostic
names, why the refusal is structural rather than a check that could be forgotten, and the
name-the-occurrence alternative.

*Package contract.* Agentic was **already at `0.1.3`** at `A_base` — `pyproject.toml`,
`agentic_mbse.__version__`, `uv.lock`, and `tests/test_package_version.py` all agreed before this
phase, and no dependency changed, so `uv.lock` needed no edit. The version obligation is satisfied
and verified from the installed wheel rather than re-performed.

**Issues / deviations / rollback point:**

1. **Three consumers beyond the plan's measured list.** The plan named `aggregation.py` ×2,
   `binding.py`, `adr002.py`, and `constraint_extraction.py`, while noting the counts are sizing
   evidence and "the static gates must rediscover the final set before deletion." They did:
   `hierarchy.py`, `level2_structure.py`, and `level6_architecture.py` also read reviewed
   selectors and were migrated onto owned accessors. Working as designed, recorded because the
   set is larger than the plan's estimate.

2. **The ownership gate is scoped to modules that reach the parser through the adapter.** The
   name-based AST scan also flagged `node.operands` in `sysml/executable_profile.py` — but that
   is a field on the neutral `ExpressionIR` dataclasses, not a SysIDE selector, and the module is
   pinned license-free by `test_executable_profile_imports_no_syside`. Routing it through the
   boundary would have imported syside and broken that pin. The gate is therefore keyed on the
   adapter import, which is exactly the scoping the Phase-1 audit required on the Codegen side
   (Finding 3). Two anti-vacuity tests were added: the scanned set admits neither everything nor
   nothing and still contains both reviewed modules, and no production module imports `syside`
   directly, so the scope premise cannot rot silently. This is a scope rule, not an exemption —
   no module is excused from a selector it actually reads.

3. **Two recorded behavior changes, both tightenings the design asks for.**
   - A referent with no qualified name is now `RESOLVED_TARGET_MISSING` (B4). The old route
     returned an `ExpressionRef` with an empty qualified name that no consumer could classify or
     resolve. `test_empty_qualified_name_is_refused_not_passed_through` pins the new contract.
   - `tests/fixtures/constraint_fact_shapes/production_facts.json` was re-anchored on **8 changed
     lines**, all `source_name`: `"red"` → `"Color::red"`, `"on"` → `"Mode::on"`, and
     `"<placeholder Feature>"` → `"missing_value"`. Verified against the fixture source
     (`type_units.sysml:13,14,39`): the model authors `Color::red`, `Mode::on`, and
     `missing_value`, so the new values are the authored truth and the old ones were rendered
     from the resolved terminal name or a placeholder. Every other byte of the golden is
     unchanged, and the round-trip test stays green.

4. **`BindingType` moved from `types.py` to `data_models.py`.** `BindingInfo.reference_uses` needs
   the closed union, so `types.py` must import `reference_use.py`, which imports `data_models.py`,
   which imported `types.py` for `BindingType` alone. Reversing that one edge makes the layering
   acyclic: `types` → `reference_use` → `data_models`. Same enum, same name, still exported; this
   is a layering fix, not a compatibility shim.

5. **Test doubles gained the shape they were missing.** Mocks in `tests/test_sysml/conftest.py`
   now carry `element_id` and a qualified name, because the closed route captures both as
   evidence. A double without them was under-specified rather than modelling a nameless
   reference; the genuinely-nameless case is now constructed explicitly where a test wants it.

6. **A feature chain rooted in an unsupported expression kind is refused by name**
   (`EXPRESSION_KIND_UNSUPPORTED`) rather than rendered through the general math renderer. This
   keeps `reference_use.py` free of a dependency on `expression.py` and matches the item's
   posture: a chain rooted in arbitrary math is not a reference the toolchain can honor. No test
   or fixture in the tree exercises that shape, so nothing regressed.

### Phase 2b completion

**Completed:**

**Commits / identities:**

**Actual changes and test results:**

**Phase 2 audit addendum — m3 re-established on non-emission:**

**Issues / deviations / rollback point:**

### Phase 3 completion

**Completed:**

**Commits / identities:**

**Actual changes and test results:**

**14-row disposition table — `tests/conformance/test_source_identity_extraction.py`:**

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

#### Audit-fix pass (2026-08-18)

The independent Phase 2 audit returned **Pass with findings**
([run-records/phase2-audit.md](run-records/phase2-audit.md)). Its Major and every minor assigned to
this phase are closed in one commit: `stop-parser-evidence-r2` `144ae02` →
**`68bca37`**. i8 is left as-is and i11 is carried to close, per the audit.

**M1 (Major) — the shared budget now covers all three entries the design names.**
`inspect_reference_uses` had it; `extract_expression_ir` and `reconstruct_expression` raised a bare
`RecursionError` on self-nesting input, which a caller cannot tell from an interpreter limit it
caused some other way. Both now exhaust into `EXPRESSION_DEPTH_EXHAUSTED` with the operation named.
The IR counter lives on `_ExtractionContext` because the dispatch recurses through several helpers
that already thread it, and the dispatch split out as `_expression_ir_node` so the guard and the
dispatch stay one job each; reconstruction carries a private `_depth` through
`reconstruct_operator_expression`. Four kept tests in `test_reference_use.py` — one per entry, plus
`test_no_recursive_production_entry_reports_a_bare_recursion_error`, which states the set, because
M1's defect was that two of the three were never wired up at all rather than wired up wrongly.
`test_the_depth_budget_is_not_caller_selectable` now also asserts neither new entry exposes a public
depth parameter.

**m3 — the unit operand is no longer emitted, and the fix is at the boundary.**
`_unit_annotation_value` in `reference_use.py` recognises a structural `[` annotation, validates its
shape, walks only its value operand, and never emits the unit as a data reference. The old route
emitted it and relied on the downstream tier filter, which is the wrong place and the wrong rule: a
project-scoped unit is tier `Project` and would have arrived at a consumer as a design dependency.
A malformed annotation is refused by name (`EXPRESSION_KIND_UNSUPPORTED`), so shape validation did
not go away with the emission.

**Measured while closing m3, and worth carrying forward:** at SysIDE 0.8.4 a user-declared unit is
**not accepted in a quantity expression at all**. Every form tried — `attribute def U :>
UnitsAndScales::{Simple,Derived,Measurement}Unit` with a usage, and each of those typings applied
directly to the usage — fails to parse with "Invalid quantity expression, expected a measurement
unit as the second argument". So the authored shape the audit names, `3.0 [MyUnits::widget]`, cannot
be reached through a real model today, and `test_a_project_scoped_unit_is_not_emitted_either` proves
the project-tier case through the same code path with a test double instead. The test records the
measurement and why the double is the only route. The live `SI::metre` case is still covered against
a real model.

**m2 — the ownership gate's scope is structural.** `_reaches_the_parser` reads the adapter import
off parsed `Import`/`ImportFrom` nodes rather than `ADAPTER_IMPORT in path.read_text()`, so a
docstring or comment naming the adapter no longer pulls a module into scope and an aliased import no
longer escapes it. Both anti-vacuity tests still fire, and
`test_the_import_scope_is_structural_not_a_substring_match` covers both directions.

**m4 — the two probe-load sites assert a clean parse.** `except Exception: pytest.skip` would have
gone quiet on a genuine loader regression in a licensed lane. `_require_a_clean_load` asserts the
model produced no error diagnostics; a parse error in probe source is now a failing test, which is
what it is.

**m6 — `_has_defined_value` is deleted.** Its only caller read `ExpressionRef.element` to reach a
live node, and the closed route carries `ResolvedTargetFact.declares_value` instead. Nothing called
it afterwards, and the `hasattr` assertion in `test_level2_integration.py` that kept it alive was
not a caller; that assertion now pins its absence and says why.

**m7 — the scanner's `getattr` branch is exercised.** It has two detection branches and only the
attribute one had anti-vacuity mutants, so a regression in the dynamic-read branch would have gone
unnoticed while the gate stayed green. Both a positive mutant per reviewed selector and a negative
case are added.

**i10 — `_document_tier_name` drops its `or ""` fallback**, so a tier-less target propagates the
named adapter failure its docstring already promised instead of recording an empty tier a consumer
could read as "not standard library".

**m5 — the two record corrections are applied above:** the ownership file's count is 14, not 12,
and the unreproducible "221 passed" figure is replaced.

**Re-verification at `68bca37`.**

- Focused, from the worktree: `test_reference_use.py` **32 passed** (32 collected),
  `test_semantic_selector_ownership.py` **20 passed** (20 collected) — 52 together.
- Fast Agentic suite: **18 failed, 1893 passed, 1 skipped**. The 18 are the same declared `A_base`
  optional-dependency baseline; the pass count rises from 1883 by the 10 nodes this pass added.
- `mypy --strict src/agentic_mbse/errors.py src/agentic_mbse/sysml/reference_use.py` → **Success**,
  from the worktree and from the clean extraction.
- Baselines non-regressed: `mypy src/` **101 errors in 21 files** (unchanged), `ruff check src/
  tests/` **119 errors** (unchanged), `ruff check` clean on every changed file. Neither baseline is
  green and neither is described as green.
- Artifact-isolated, from a fresh `git archive` of `68bca37` extracted under
  `/tmp/stop-parser-rev2/agentic-mbse-phase2fix/agentic-mbse` (the path keeps the `agentic-mbse`
  string the baseline path test requires). **Named, reproducible set** — `pytest tests/test_sysml/
  tests/test_validation/ tests/test_errors.py`: **834 passed, 1 skipped**. Fast suite reproduces
  **18 failed / 1893 passed / 1 skipped**; scoped strict returns Success.
- Wheel: `uv build --wheel` → `agentic_mbse-0.1.3-py3-none-any.whl`. Installed into a fresh venv it
  reports dist version `0.1.3`, `__version__` `0.1.3`, API `semantic-evidence/v2`, both new codes,
  the complete boundary surface including `MAX_EXPRESSION_DEPTH`, every deleted symbol absent
  (`ExpressionRef`, `ResolvedSemanticReferenceFact`, `_has_defined_value`), and no public depth
  parameter on either newly-budgeted entry.

**Rollback point for this pass:** reset `stop-parser-evidence-r2` to `144ae02`. The Codegen
worktree is still untouched at `d257ef1` and both user checkouts report an empty
`status --porcelain`.
