# Implementation Plan: Lifecycle Remediation Item 1 — Occurrence and Demand Integrity

**Status:** Ready for implementation
**Created:** 2026-07-19
**Last Updated:** 2026-07-19
**Branch:** `constraint-exec-epic`
**Item 0 RED predecessor:** `ecdc7285be1508c08e82830c93072306f40e6b34`
**Planning checkout:** `8d4f2982c5d6202376f60fdaeed5bc785c07903f`

## Source Documents

- **Approved spec:** [spec.md](spec.md)
- **Approved design:** [design.md](design.md)
- **Spec approval:** [spec-rereview.md](spec-rereview.md)
- **Design approval:** [design-rereview.md](design-rereview.md)
- **Historical decision trail:** [spec-review.md](spec-review.md) and
  [design-review.md](design-review.md)
- **Item 0 coordinate:**
  [candidate-pin evidence](../constraint-lifecycle-candidate-pin/evidence.md)
- **Epic Item 1:**
  [constraint lifecycle remediation epic](../../backlog/epic_constraint_execution_lifecycle_remediation.md#item-1-occurrence-and-demand-integrity)
- **Repository commands:** [CLAUDE.md](../../../CLAUDE.md)

The seven phases below preserve the owner-directed order from the stage input. The detailed
mechanisms remain the approved design's `[INFERRED]`, agent-grade bets. Evidence that contradicts
one of those bets triggers the stop conditions below; approval does not make the bet settled.

## Implementation Strategy

### Phasing Rationale

Phase 0 creates the proof surface before any production edit. It freezes the automatic production
union, executable-LOC/AST/complexity counter, locks, current valid fixtures, user-owned
`.claude/projects`, and the public test/fixture bytes. The five tests then fail independently at the
exact Item 0 predecessor for R-4, R-5, or R-7.

Phases 1 and 2 establish the lifecycle boundary first: verified association, one prepared batch,
no lowering re-query, explicit owner dispatch, and atomic cycle failure. Phase 3 implements the
riskiest demand rules in isolation at the existing `_binding_target` seam. Phase 4 makes the single
live/replay cutover and deletes every superseded route in the same change set. Phase 5 proves the
public live, same-checkout replay, finite-control, generated-execution, and repository gates.
Phase 6 writes the evidence and checks only claims supported by the recorded outputs.

### Critical Path

Unchanged public bytes -> five independent intended RED failures at OD-R30 -> verified prepared
batch/no re-query -> structural cycle failure -> semantic target-keyed demand -> one live/replay
enrichment path plus deletions -> licensed live and TEAx observations -> evidence and supported
checkbox updates.

### First Proof Point

Before a production file changes, each named OD-A11 node must run in a fresh process against
sysml-codegen `ecdc7285...`, agentic-mbse `515e08bb...`, and TEAx `d545701f...`. Each must reach its
behavioral assertion and fail for its named defect. A collection, import, setup, license, or
unrelated assertion failure is invalid evidence.

### Feasibility Assessment

The approved design fits the current call graph:

- Profile decisions already preserve source order and copy identity/location, so pure verified
  pairing can replace nullable-QN membership.
- `OccurrenceIndex` already isolates live and frozen queries. A private result dictionary can stage
  the successful transcript without a recorder.
- `_binding_target` is already the materializer's concrete target-normalization seam. Its value
  ladder can return provenance without importing Item 2's graph resolver.
- Live and replay already have one pre-backtracker enrichment point and one classifier-input
  carrier, so both can converge without a snapshot/schema change.

The highest risks are semantic disagreement across valid lookup contexts, partial transcript
publication, and code growth while adding the new records. The unchanged absolute-reference tests,
the later-owner rollback test, and the frozen union/deletion ledger are the corresponding gates.

### Phase Boundaries and Commit Discipline

- Phases 0–2 may be verified independently.
- Phase 3 is a unit-proof checkpoint, not a releasable dual-path state. Complete Phase 4 before a
  candidate is called green or measured for closeout. Do not add a wrapper between the old and new
  materializers.
- Phase 4 must end with one prepared batch and one enrichment path. No feature flag, compatibility
  alias, route adapter, or dead fallback remains.
- Phase 5 runs against a committed product/test candidate revision. Phase 6 records that revision;
  the later evidence-only commit is not substituted for the tested candidate coordinate.

## Protected State and Global Stop Conditions

### Protected State

- `.claude/projects/` is user-owned. Do not edit, remove, stage, stash, clean, reset, or relocate it.
  Record only an aggregate content hash and its `git status` entry before and after the work.
- Preserve unrelated dirty files. Never use `git clean`, `git reset --hard`, or a broad checkout.
- Existing fixtures and committed baselines are controls. Item 1 adds only the new
  `tests/fixtures/constraint_occurrence_demand/` tree; it does not refresh an existing snapshot or
  baseline.
- Snapshot format stays v3, executable profile stays v4, and package/catalog/schema versions stay
  unchanged. See [design.md#compatibility-and-migration](design.md#compatibility-and-migration).

### Stop or Roll Back the Phase When

1. **Scope absorption:** implementation needs a general producer/exact-QN resolver, warning-location
   totality, relocated whole-tree proof, or sealed-artifact proof. Stop and leave Items 2, 4, 5,
   and 13 with their recorded ownership. Do not hide the expansion in a helper.
2. **A design bet is contradicted:** ordered identity/location pairing cannot distinguish a required
   case; exact `_BindingTarget.qn` merges unequal semantic targets; calc precedence is disproved;
   constraint-only provenance is not deterministic; or an occurrence query mutates external state.
   Save the reproducer, park dependent conclusions, and request an owner/design decision.
3. **Version pressure:** a valid case requires changing `uv.lock`, `pyproject.toml`, snapshot v3,
   executable-profile/v4, package 0.1.0, catalog, facts, graph, or parameter-group schemas. Revert
   only the phase-owned version/schema change and stop.
4. **Production growth:** after Phase 4 deletion, first simplify any file above its design cap. If
   the automatic union is still above the 3,524 executable-line baseline, do not start
   certification. A positive closeout needs the owner-reviewed OD-R43 deviation. The design target
   is 3,504 or fewer executable lines.
5. **License skip:** any required public-live OD-A01/A04/A05/A08/A09/A10 node skips or cannot load
   the real fixture. Record it as unproven and stop certification; do not substitute replay,
   synthetic facts, or a private seam.
6. **Fixture conflict:** an existing valid fixture or `baseline_outputs` byte changes. Restore only
   the phase-owned fixture edit, diagnose the semantic drift, and stop. Do not accept a recapture as
   an Item 1 migration.
7. **RED invalidity:** a Phase 0 node fails during setup/import/license discovery or at an assertion
   unrelated to R-4/R-5/R-7. Fix the test/fixture while production remains untouched, issue a new
   overlay hash, and rerun all five nodes.
8. **Public API/cause drift:** cycle behavior cannot retain `CodeGenerationError` with a structured
   `RecursiveContainmentError` cause, or `lower_constraints` still has any route to a profile or
   occurrence source. Stop before adding a compatibility signature.

Rollback means abandoning or reversing only the current phase's owned patch and returning to the
last verified checkpoint. It never authorizes changing preserved user files or unrelated work.

## Frozen Accounting Rules

Phase 0 creates
`.project/active/constraint-lifecycle-occurrence-demand/evidence/production_metrics.py`. It is
evidence tooling, not production. The same hashed script runs against the Item 0 worktree and the
candidate. It must:

- derive the union from `git diff --name-status -z`, including added, deleted, and both sides of a
  move;
- classify tracked production `*.py`, `*.jinja2`, and lifecycle `*.sysml` using the Item 0 rule;
- exclude tests, fixtures, generated output, docs, `.project`, caches, and results from production;
- count raw lines, physical executable lines excluding blanks/comments/docstring spans, AST
  statements, branch points, and per-callable cyclomatic decisions using one documented algorithm;
- treat a new path as baseline zero and a deleted path as candidate zero; and
- report tests/fixtures/generated/docs/project artifacts in separate ledgers that cannot offset
  production.

The planned nine-file production start is [design.md#appendix-a--deletion-and-production-accounting](design.md#appendix-a--deletion-and-production-accounting):

| Path | Executable baseline | Design cap |
|---|---:|---:|
| `src/sysml_codegen/analysis/part_instance_index.py` | 228 | 234 |
| `src/sysml_codegen/analysis/constraint_lowering.py` | 1,078 | 1,072 |
| `src/sysml_codegen/resolution/supplied_values.py` | 208 | 220 |
| `src/sysml_codegen/orchestration/pipeline_builder.py` | 641 | 623 |
| `src/sysml_codegen/snapshot/graph_rebuild.py` | 156 | 142 |
| `src/sysml_codegen/snapshot/serializer.py` | 157 | 157 |
| `src/sysml_codegen/orchestration/pipeline_context.py` | 62 | 62 |
| `src/sysml_codegen/snapshot/__init__.py` | 27 | 27 |
| `src/sysml_codegen/snapshot/loader.py` | 967 | 967 |
| **Automatic starting union** | **3,524** | **≤ 3,504 target; ≤ 3,524 hard default** |

Every actual production change joins the union automatically. The table is a starting inventory,
not an allowlist.

---

## Phase 0: Freeze the Coordinate and Prove Unchanged RED

### Goal

Create the public fixtures and unchanged test surface, freeze every preservation/accounting
manifest, and reproduce R-4/R-5/R-7 independently at the exact Item 0 predecessor before any
production edit.

### Assumption Under Test

The coordinated Item 0 predecessor still has the three reviewed defects, and tests using only
public APIs available at both revisions can fail at the intended behavioral assertions.

### Test Stencil — Write First

```python
@requires_license
def test_r4_live_anonymous_association(tmp_path, caplog):
    context = build_pipeline_context([ANONYMOUS_FIXTURE])
    assert projected_demand_targets(context) == [ADMITTED_TARGET]
    assert unsupported_owner_queries(context) == []
    assert catalog_dispositions(context) == ["eligible", "unsupported_owner"]
    assert warning_values(caplog) == []
```

### Changes Required

See [design.md#appendix-b--executable-acceptance-architecture](design.md#appendix-b--executable-acceptance-architecture)
and [spec.md#d-evidence-coordinate-and-regression-breadth](spec.md#d-evidence-coordinate-and-regression-breadth).

- [x] Create `tests/conformance/test_constraint_occurrence_demand_acceptance.py` with these exact
  stable public nodes:
  - `test_r4_live_anonymous_association`
  - `test_r4_valid_replay_not_corrupt`
  - `test_r5_finite_first_cycle_is_atomic`
  - `test_r7_shared_target_dedup_grouping_counts`
  - `test_r7_multi_target_order_permutations`
  - `test_r7_constraint_only_provenance_after_resolution` (candidate public proof; not one of the
    five historical RED claims)
- [x] Keep that file limited to `build_pipeline_context`, `capture_snapshot`,
  `build_full_graph_from_snapshot`, `CodeGenerationError`, logging/output inspection, and fixture
  helpers available at OD-R30. Do not import any candidate-only batch/demand/cycle type.
- [x] Create these new fixture directories, each with `PROVENANCE.md` and the SysML sources pinned
  in [design.md#public-fixture-observations](design.md#public-fixture-observations):
  - `tests/fixtures/constraint_occurrence_demand/anonymous/` (`model.sysml`)
  - `tests/fixtures/constraint_occurrence_demand/cycle/` (`model.sysml`)
  - `tests/fixtures/constraint_occurrence_demand/overrides/` (`model.sysml`)
  - `tests/fixtures/constraint_occurrence_demand/shared/` (`calc_route.sysml`,
    `constraint_route.sysml`)
  - `tests/fixtures/constraint_occurrence_demand/constraint_only/`
    (`constraint_route.sysml`)
  - `tests/fixtures/constraint_occurrence_demand/order/` (`model.sysml`)
- [x] Create the evidence metrics tool described in **Frozen Accounting Rules** and record its
  SHA-256 before either baseline or candidate measurement.
- [x] Record the incoming revision/status, Item 0 lock digests, Python/pytest versions, existing
  fixture manifest, `baseline_outputs` manifest, nine-file raw/executable/AST/complexity baseline,
  two-doc baseline, and current mypy error count.
- [x] Record an aggregate `.claude/projects` hash and `git status --short -- .claude/projects/`.
  Do not include file contents in evidence.
- [x] Confirm `git diff --name-only -- src` is empty before copying the public overlay into RED.
- [x] Hash the complete public overlay and the standalone acceptance file once. Store the actual
  digests in the Phase 0 evidence notes; placeholders are invalid.

### Exact Setup and RED Commands

```bash
ITEM1_ROOT=/home/reid/1cfe/sysml-codegen
ITEM1_BASELINE=ecdc7285be1508c08e82830c93072306f40e6b34
ITEM1_RED_ROOT=$(mktemp -d /tmp/item1-red.XXXXXX)
git worktree add --detach "$ITEM1_RED_ROOT/sysml-codegen" "$ITEM1_BASELINE"
git -C ../agentic-mbse worktree add --detach "$ITEM1_RED_ROOT/agentic-mbse" 515e08bbcd70aa9d23212765161bd02b3e3d8f23
git -C ../teax worktree add --detach "$ITEM1_RED_ROOT/teax" d545701f575133350474108c96202a2ac5244462

find .claude/projects -type f -print0 | sort -z | xargs -0 sha256sum | sha256sum
find tests/fixtures -type f ! -path 'tests/fixtures/constraint_occurrence_demand/*' \
  -print0 | sort -z | xargs -0 sha256sum | sha256sum
find tests/fixtures/baseline_outputs -type f -print0 | sort -z | \
  xargs -0 sha256sum | sha256sum
sha256sum uv.lock

tar -C "$ITEM1_ROOT" -cf "$ITEM1_RED_ROOT/public-overlay.tar" \
  tests/conformance/test_constraint_occurrence_demand_acceptance.py \
  tests/fixtures/constraint_occurrence_demand
tar -C "$ITEM1_RED_ROOT/sysml-codegen" -xf "$ITEM1_RED_ROOT/public-overlay.tar"
cd "$ITEM1_RED_ROOT/sysml-codegen"
find tests/conformance/test_constraint_occurrence_demand_acceptance.py \
  tests/fixtures/constraint_occurrence_demand -type f -print0 | sort -z | \
  xargs -0 sha256sum > "$ITEM1_RED_ROOT/overlay.sha256"
sha256sum tests/conformance/test_constraint_occurrence_demand_acceptance.py \
  > "$ITEM1_RED_ROOT/unchanged-tests.sha256"
uv sync --frozen
set -a
source /home/reid/1cfe/agentic-mbse/.env
set +a

RED_NODES=(
  tests/conformance/test_constraint_occurrence_demand_acceptance.py::test_r4_live_anonymous_association
  tests/conformance/test_constraint_occurrence_demand_acceptance.py::test_r4_valid_replay_not_corrupt
  tests/conformance/test_constraint_occurrence_demand_acceptance.py::test_r5_finite_first_cycle_is_atomic
  tests/conformance/test_constraint_occurrence_demand_acceptance.py::test_r7_shared_target_dedup_grouping_counts
  tests/conformance/test_constraint_occurrence_demand_acceptance.py::test_r7_multi_target_order_permutations
)
for node in "${RED_NODES[@]}"; do
  uv run --frozen pytest -q -rs "$node"
done
```

Run the metrics tool against the clean baseline worktree and preserve its machine-readable output:

```bash
cd "$ITEM1_ROOT"
uv run --frozen python \
  .project/active/constraint-lifecycle-occurrence-demand/evidence/production_metrics.py \
  --baseline-root "$ITEM1_RED_ROOT/sysml-codegen" \
  --candidate-root "$ITEM1_RED_ROOT/sysml-codegen" \
  --baseline-rev "$ITEM1_BASELINE" --candidate-rev "$ITEM1_BASELINE" \
  --json-out "$ITEM1_RED_ROOT/item1-baseline-metrics.json"
uv run --frozen mypy src/
```

### Validation

- [x] `sha256sum -c "$ITEM1_RED_ROOT/overlay.sha256"` passes before every RED run.
- [x] Each of the five nodes runs in a fresh process and fails at its named behavioral assertion:
  anonymous association/spurious query for R-4, valid replay corruption for R-4, finite-prefix/no
  raise for R-5, and duplicate grouping/count/order for R-7.
- [x] Record the historical focused 31-test green slice only as a compatibility control, never as
  RED evidence:

  ```bash
  uv run --frozen pytest -q -rs \
    tests/unit/test_part_instance_index.py \
    tests/unit/test_supplied_values.py \
    tests/unit/test_occurrence_roundtrip_parity.py \
    tests/conformance/test_part_instance_index.py
  ```

- [x] Record `git status --short --branch`, `git diff --name-status`, and the aggregate protected
  manifests after test/fixture authoring. Only the new Item 1 test/fixture/evidence paths may differ.

### What We Know Works After This Phase

The proof surface is stable, every defect is reproducible at the coordinated predecessor for the
intended reason, production is untouched, and all preservation/accounting baselines are frozen.

### Implementation Notes

- **Completed:** 2026-07-19 17:19 PDT. No production file changed before the complete RED
  coordinate and preservation checkpoint were recorded.
- **Test/fixture checkpoint and hashes:** acceptance file SHA-256
  `aea7c8219d716f4ca1ecb154ca6ed8a13e0c15b1184fdcfe2d92b556eacb624b`; complete
  overlay-manifest SHA-256
  `8a5758fa9bf892335b8bc7f1e142929098187a391593d27aa0aea5ba7cca2897`; metrics-tool
  SHA-256 `70fddc980bfd49cb46248fa4fcd2735d7879f118675b64f3bcb993217e4c4a0c`.
  Existing-fixture aggregate `fde9c5df...54bd5`; baseline-output aggregate
  `921bbb6a...bf66`; Python 3.12.3, pytest 9.0.2, codegen 0.1.0, agentic-mbse 0.1.2,
  executable-profile/v4. Lock hashes exactly match OD-R30. The archived nine-file raw
  baseline is 5,211. The frozen counter reports 3,552 physical executable lines, while
  the independently approved fixed baseline is 3,524; closeout retains the stricter 3,524
  absolute hard gate and reports both measurements instead of revising the approved baseline.
- **Exact RED failures:** at sysml-codegen `ecdc7285be1508c08e82830c93072306f40e6b34`,
  agentic-mbse `515e08bbcd70aa9d23212765161bd02b3e3d8f23`, and TEAx
  `d545701f575133350474108c96202a2ac5244462`: R-4 live reached the summary assertion
  with `3/2/0` instead of `1/1/0`; R-4 replay raised
  `FrozenOccurrenceIndexCorruptionError` for excluded owner
  `OccurrenceDemandAnonymous__Excluded`; R-5 reached `DID NOT RAISE`; shared R-7
  reached `2/2/0` instead of `1/1/0`; ordered R-7 reached `6/6/0` instead of
  `3/3/0`. Every node ran in a fresh licensed process after its overlay hash check.
  The named historical selection now collects 37 nodes and passed 37/37; it remains a
  compatibility control, not RED evidence.
- **Incoming dirty/protected state:** branch `constraint-exec-epic` at `8d4f298`, ahead 3;
  pre-existing `.project/CURRENT_WORK.md` modification and untracked `.claude/projects/`
  plus the active Item 1 artifact directory. `.claude/projects/` stayed untracked with
  aggregate hash `d7498577...624b`; no contents were recorded. Mypy baseline is 76 errors
  in 17 files.
- **Issues or deviations:** the first archive attempt skipped because the isolated process had
  not loaded the license environment. It is discarded setup evidence. The same unchanged bytes
  were rerun after sourcing the pinned environment and produced the five intended failures above.
  Git worktree mutation was unnecessary: a read-only `git archive` under
  `/tmp/item1-red.yslzRA` supplied the exact predecessor.

---

## Phase 1: Verified Association, Prepared Batch, and No-Requery Lowering

### Goal

Implement pure one-to-one association, centralize the profile guard, filter owner kinds before
expansion with an explicit package branch, stage one private batch/transcript, make lowering unable
to re-evaluate or re-query by signature, and make serializer association pure. Preserve current
R-8 warning-before-BLOCK bytes, ordering, and failure behavior for Item 4.

### Assumption Under Test

Within one facts batch, count plus exact copied identity/location equality is sufficient to detect
deletion, duplication, reorder, and field mismatch before any warning, owner query, demand, or
serializer mutation.

### Test Stencil — Write First

```python
def test_association_rejects_independent_decision_mutations_before_preflight(spy_index):
    facts, decisions = anonymous_sibling_batch()
    for mutated in independent_delete_duplicate_reorder_identity_location_clones(decisions):
        with pytest.raises(CodeGenerationError, match="association"):
            associate_usage_decisions(facts, decisions_override=mutated)
        assert spy_index.calls == []
        assert emitted_warnings() == []
```

The production API does not take `decisions_override`; tests inject profile output at the profile
evaluation boundary. Do not add a test-only production parameter.

### Changes Required

See [design.md#association-and-preparation](design.md#association-and-preparation),
[design.md#exact-apis](design.md#exact-apis), and
[design.md#direct-serializer-safety](design.md#direct-serializer-safety).

- [x] Create `tests/unit/test_constraint_usage_preparation.py` first. Add exact nodes:
  - `test_association_rejects_independent_decision_mutations_before_preflight`
  - `test_profile_version_guard_precedes_association_and_queries`
  - `test_excluded_unsupported_zero_query_and_package_branch`
  - `test_missing_required_frozen_owner_wraps_corruption_with_recapture_guidance`
  - `test_later_owner_failure_discards_staged_transcript`
  - `test_lowering_accepts_only_prepared_disposition_and_instances`
- [x] In mutation tests, clone identity/location values with `dataclasses.replace` or `deepcopy`
  before editing. Do not rely on aliased mutable objects.
- [x] Update `tests/conformance/test_constraint_snapshot_identity.py` to prove the serializer's
  second association is guarded and pure: no warning, BLOCK aggregation, owner query, demand, or
  input-facts mutation; valid serialized bytes remain unchanged.
- [x] Migrate direct lowering tests without a compatibility wrapper in:
  - `tests/conformance/test_constraint_lowering.py`
  - `tests/conformance/test_constraint_lowering_integrity.py`
  - `tests/conformance/test_constraint_profile_route_parity.py`
  - `tests/conformance/test_constraint_snapshot_identity.py`
  - `tests/conformance/test_constraint_pipeline_threading.py`
  - `tests/unit/test_occurrence_roundtrip_parity.py`
- [x] `src/sysml_codegen/analysis/constraint_lowering.py:386-473,519-587,869-1189`: add the exact
  association/prepared records and APIs from the design; move the v4 guard into association;
  preserve current NON_NUMERICAL-then-BLOCK preflight; use explicit `part_def`, `calc_def`, and
  `package` branches; stage part-owner results privately; and change `lower_constraints` to accept
  only `facts`, `prepared`, `registry`, and `design_attrs`.
- [x] Make `collect_bare_actual_demand` consume only the prepared items as a temporary internal
  Phase 1 bridge to Phase 4. It must not evaluate the profile or accept/query an occurrence index.
  Do not add a wrapper around the new `lower_constraints` signature.
- [x] `src/sysml_codegen/orchestration/pipeline_builder.py:828-898`: build one live index, prepare
  once before enrichment, pass the batch to the temporary prepared-demand reader and lowering, and
  publish the batch transcript only on successful context construction.
- [x] `src/sysml_codegen/snapshot/graph_rebuild.py:82-134,173-223`: build one frozen index, prepare
  once, carry the batch in classifier inputs, and pass it to lowering. A missing required owner is
  corruption only for an admitted supported owner.
- [x] `src/sysml_codegen/snapshot/serializer.py:139-160`: replace direct profile evaluation and the
  old selector with `associate_usage_decisions`; retain deepcopy and canonicalization only.
- [x] Do not change the warning-location projector or add the R-8 unmappable-location case.

### Validation

```bash
uv run --frozen pytest -q -rs \
  tests/unit/test_constraint_usage_preparation.py \
  tests/conformance/test_constraint_lowering.py \
  tests/conformance/test_constraint_lowering_integrity.py \
  tests/conformance/test_constraint_profile_route_parity.py \
  tests/conformance/test_constraint_snapshot_identity.py \
  tests/unit/test_occurrence_roundtrip_parity.py
uv run --frozen python -O -m pytest -q -rs \
  tests/unit/test_constraint_usage_preparation.py \
  tests/conformance/test_constraint_lowering.py \
  tests/conformance/test_constraint_lowering_integrity.py
```

- [x] Association mismatch tests prove zero warnings and zero queries.
- [x] Unsupported/excluded owners have empty instances and zero queries; admitted part/calc/package
  branches retain their explicit behavior.
- [x] Frozen valid replay uses its transcript; removing only a required admitted owner entry produces
  contextual corruption and recapture guidance.
- [x] Static signature inspection proves `lower_constraints` has no occurrence index, calc usages,
  source-location policy, profile result, or profile evaluation.
- [x] Existing R-8-sensitive warning/BLOCK tests remain byte/order/failure-identical, including
  `test_two_non_numerical_warnings_precede_complete_block` and
  `test_non_numerical_warning_preserves_walk_order_and_location_fallback`.
- [x] Re-run the two R-4 public nodes. They may not be fully green until Phase 4 demand cutover, but
  any remaining failure must be the still-active demand route rather than association or re-query.

### What We Know Works After This Phase

Every usage has one verified decision, preparation owns all legitimate owner queries, no partial
batch is published, and lowering cannot rediscover lifecycle state.

### Implementation Notes

- **Completed:** 2026-07-19. Overlay unchanged: acceptance-file SHA-256 is still
  `aea7c8219d716f4ca1ecb154ca6ed8a13e0c15b1184fdcfe2d92b556eacb624b` and
  `git status -- tests/fixtures` shows no tracked fixture byte changed.
- **Actual API/caller changes:**
  - `constraint_lowering.py`: added `associate_usage_decisions(facts)`,
    `is_excluded_usage(usage, decision)`, `SUPPORTED_OWNER_KINDS`,
    `PreparedConstraintUsage`, `PreparedConstraintBatch`,
    `prepare_constraint_usages(...)`, `_raise_on_blocking`,
    `_verified_predicate_source_key`, and the three explicit owner branches
    `_expand_part_owner` / `_expand_calc_owner` / `_expand_package_owner`.
    Deleted `excluded_usage_indices` and `_expand_owner_instances`.
    `lower_constraints` is now `(facts, *, prepared, registry, design_attrs)`.
    `collect_bare_actual_demand(prepared)` is the temporary Phase 1 bridge.
  - `pipeline_builder.py`: new Step 5.64 prepares once from one live index before
    the materializer; lowering and the transcript both read that batch; the
    transcript is converted to `part_occurrences` only at context construction.
    `RecordingOccurrenceIndex` is no longer imported.
  - `graph_rebuild.py`: one `FrozenOccurrenceIndex`, one prepare, batch carried in
    classifier inputs as `prepared_constraints`, same batch used for lowering.
  - `serializer.py`: `_constraint_facts_for_snapshot` now calls
    `associate_usage_decisions` + `is_excluded_usage`; its own `evaluate_profile`
    import is gone.
  - Tests migrated with no compatibility wrapper: every direct call site now
    prepares then lowers. `test_constraint_snapshot_portability.py` joined the
    migration (it imported the deleted selector).
- **Disposition (orchestrator, agent-grade, recorded — not settled):** the extra
  prepared field is ACCEPTED on the I10 rationale below.
- **Deviation — one extra prepared field.** `PreparedConstraintUsage` carries
  `predicate_source_key: str` beyond the design's six-field table. The design's
  own "Exact APIs" row forbids lowering from holding source-location policy, but
  an admitted *anonymous inline* assert reaches the referent-mapping arm of the
  predicate-source-key ladder — exactly the R-4 anonymous fixture. Leaving that in
  lowering would violate I10; carrying the finished key satisfies it and moved
  ~30 executable lines out of `lower_constraints`. Flagged for design review.
- **Deviation — nullable `source_location_mode`.** `prepare_constraint_usages`
  keeps `source_location_mode: Literal["live","snapshot"] | None = None` and
  `source_roots: list[Path] | None = None`, exactly as `lower_constraints` had
  them, so route-absence still fails at the same place with the same message.
  Requiring them would have changed behaviour for facts that legitimately have no
  route (no located excluded usage).
- **R-8 preservation output:** unchanged. `test_two_non_numerical_warnings_precede_complete_block`
  and `test_non_numerical_warning_preserves_walk_order_and_location_fallback` both
  pass on their original expected bytes; the preflight moved into preparation
  mechanically, warning projector untouched, no unmappable-location case added.
  New control `test_warning_then_block_preflight_completes_before_any_owner_query`
  proves the warning/BLOCK order completes with zero owner queries.
- **R-4 residual after association:** none. Both public R-4 nodes
  (`test_r4_live_anonymous_association`, `test_r4_valid_replay_not_corrupt`) are
  GREEN after Phase 1 — earlier than the plan assumed. Live `part_occurrences` is
  `["OccurrenceDemandAnonymous__Admitted"]` (was three owners) and valid replay no
  longer raises `FrozenOccurrenceIndexCorruptionError`. Nullable-QN membership was
  the whole defect: deleting it in `collect_bare_actual_demand` closed both.
- **Issues or challenged bets:** B1 held — ordered identity+location pairing
  distinguished deletion, duplication, reorder, and both field edits on two
  anonymous siblings whose identities are identical `(None, None)`. No stop
  condition triggered.

---

## Phase 2: Structural Cycle Failure and Finite-Behavior Preservation

### Goal

Add structured `RecursiveContainmentError`, make a finite-first cycle batch-atomic under all
specified permutations, preserve the complete finite cardinality/ordering surface, and retain the
public `CodeGenerationError` cause chain.

### Assumption Under Test

A per-recursion-path structural active stack can reject self and indirect cycles without acting as
a global visited set or changing any finite DAG/diamond/retype result or final occurrence order.

### Test Stencil — Write First

```python
def test_later_owner_cycle_discards_staged_transcript():
    index = fake_index(owner_a=finite_result(), owner_b=recursive_cycle())
    with pytest.raises(CodeGenerationError) as caught:
        prepare_constraint_usages(two_owner_facts(), occ_index=index, ...)
    assert type(caught.value.__cause__).__name__ == "RecursiveContainmentError"
    assert caught.value.__cause__.cycle_path == (A, B, A)
    assert no_batch_context_graph_catalog_or_target_mutation()
```

### Changes Required

See [design.md#cycle-surface](design.md#cycle-surface) and
[design.md#error-and-mutation-boundaries](design.md#error-and-mutation-boundaries).

- [x] Extend `tests/unit/test_part_instance_index.py` with:
  - `test_self_cycle_raises_structured_context`
  - `test_indirect_cycle_raises_structured_context`
  - `test_finite_first_cycle_is_atomic_under_feature_reversal`
  - `test_zero_count_returns_empty`
  - `test_multi_digit_occurrence_order_is_numeric`
  - structural subtype/retype/diamond controls that prove the active stack is not global
- [x] Extend `tests/unit/test_constraint_usage_preparation.py` with
  `test_later_owner_cycle_discards_staged_transcript` and assertions that enrichment/lowering spies
  remain zero.
- [x] `src/sysml_codegen/analysis/part_instance_index.py:54-61,139-196`: add the structured error
  fields specified by the design and replace revisit-as-empty with per-path active-stack detection.
  Keep error traversal canonical and separate from `_occurrence_sort_key`.
- [x] `src/sysml_codegen/analysis/constraint_lowering.py`: wrap only the structural cycle error as
  contextual `CodeGenerationError` using `raise ... from error`. Preserve all five cause fields.
- [x] Do not make recursive, ranged, parameterized, ordered, nonunique, unbounded, or unknown bounds
  executable.

### Validation

```bash
uv run --frozen pytest -q -rs \
  tests/unit/test_part_instance_index.py \
  tests/conformance/test_part_instance_index.py \
  tests/unit/test_constraint_usage_preparation.py::test_later_owner_cycle_discards_staged_transcript \
  tests/conformance/test_constraint_occurrence_demand_acceptance.py::test_r5_finite_first_cycle_is_atomic
uv run --frozen python -O -m pytest -q -rs \
  tests/unit/test_part_instance_index.py \
  tests/conformance/test_part_instance_index.py \
  tests/unit/test_constraint_usage_preparation.py::test_later_owner_cycle_discards_staged_transcript \
  tests/conformance/test_constraint_occurrence_demand_acceptance.py::test_r5_finite_first_cycle_is_atomic
```

- [x] Assert exact self-cycle fields: requested/edge owner/type
  `OccurrenceDemandCycle__Node`, feature `recursive`, path
  `(OccurrenceDemandCycle__Node, OccurrenceDemandCycle__Node)`.
- [ ] Assert exact indirect path `(OccurrenceDemandCycle__A, OccurrenceDemandCycle__B,
  OccurrenceDemandCycle__A)` and the closing B-to-A edge.
  **Partially met, and the gap is Phase 0's, not Phase 2's.** The `cycle/` fixture
  models only the self-cycle (`part recursive : Node`), so those two QNs do not
  exist anywhere in the fixture tree. Indirect detection is proven instead by
  `test_indirect_cycle_raises_structured_context` on a mock A/B index, asserting
  `cycle_path == ("A","B","A")` and the closing edge `(A, "b", B)`. Closing this
  line verbatim needs a new fixture, which would change Phase 0 overlay bytes —
  raised rather than done silently.
- [x] Self, indirect, reversed feature, and repeat traversals yield the same structured failure and
  publish no owner result, transcript, batch, or supplied-value demand. Reversed usage/index
  permutations and the snapshot/graph/catalog/output-target non-mutation claims are not asserted
  here: the first needs the multi-owner public fixture and the rest need the Phase 4 single-route
  cutover, so both stay open until Phase 4/5.
- [x] Existing `test_bare_fixed` through `test_unrecognized_upper_bound_node_blocks` and the seven
  named conformance controls in OD-A06 pass unchanged.
- [x] The stable R-5 node is GREEN with the same Phase 0 overlay hash.

### What We Know Works After This Phase

Recursive containment cannot masquerade as a finite prefix, while all supported finite occurrence
semantics remain unchanged in normal and optimized Python.

### Implementation Notes

- **Completed:** 2026-07-19, same overlay hash as Phase 0.
- **Cause fields and exact messages:** `RecursiveContainmentError` carries all five
  fields. `_structured_paths` now threads `requested_owner_qn` and a per-recursion
  `active` tuple instead of the revisit-as-empty `_visited` set, and raises at the
  recursion site. Preparation wraps it as `CodeGenerationError` with
  `raise ... from error` (`"... is recursively contained ... no concrete instance
  set exists, so no part of this batch is expanded"`).
  Public R-5 node observations: `requested_owner_qn`/`edge_owner_qn`/`edge_type_qn`
  `OccurrenceDemandCycle__Node`, `edge_feature_name` `recursive`, `cycle_path`
  `("OccurrenceDemandCycle__Node", "OccurrenceDemandCycle__Node")`.
- **Disposition (orchestrator, agent-grade, recorded — not settled):** the approved
  design's edge-field definition wins over the plan's looser prose. The missing
  indirect-cycle fixture is ACCEPTED as-is; Phase 0 overlay bytes stay unmodified and
  Phase 6 evidence must state the gap plainly.
- **Indirect-edge orientation — reporting a plan/design wording gap.** The design
  fixes the edge fields as `(owning_definition_qn, feature_name,
  target_definition_qn)`. For the A/B indirect case that yields
  `cycle_path == ("A","B","A")` with edge `(A, "b", B)`: the closing edge is the
  containment edge *A contains b : B*, which the plan's validation line describes
  as "the closing B-to-A edge". Implemented per the design's field definition and
  asserted with the observed values; the plan's prose is the looser of the two.
- **Finite-control results:** all ten original nodes (`test_bare_fixed` through
  `test_unrecognized_upper_bound_node_blocks`, plus both sort-key/hash-seed nodes)
  pass unchanged, and the seven conformance controls in
  `tests/conformance/test_part_instance_index.py` pass unchanged. Added
  `test_active_stack_is_per_path_not_a_global_visited_set` (diamond: two paths
  survive) and `test_subtype_reentry_on_a_sibling_branch_is_not_a_cycle`.
- **Mutation/rollback observations:** `test_later_owner_cycle_discards_staged_transcript`
  proves a finite first owner plus a recursive second owner returns no batch, so
  lowering and the demand collector never run. `all_occurrences()` records a
  recursive definition in its existing `blocked` map (same disposition as
  non-finite) rather than raising through the bulk dump; `occurrences_of` still
  raises loud.
- **Canonical traversal:** added `_canonical_walk_entries`, which resolves each
  usage's owner once and sorts by `(feature_name, owner_qn)`, so declaration order
  cannot decide which edge is reported. Final occurrence order is unchanged —
  `_occurrence_sort_key` still owns it — and `_structured_paths` dropped off the
  C901 list as a side effect.
- **Issues or challenged bets:** none contradicted. No non-finite shape became
  executable.

---

## Phase 3: Origin-Aware Logical Demand at the Existing Materializer Seam

### Goal

Implement and unit-test `DemandOrigin`, `LogicalDemand`, `ValueResolution`, and `ResolvedDemand` at
the existing `_binding_target` seam. Compare distinct lookup contexts by semantic outcome, select
group provenance after resolution, count/warn once per deterministic target, preserve real
attributes, and keep constraint-only demand functional without adding Item 2's resolver.

### Assumption Under Test

Exact normalized target QN is sufficient Item 1 identity when all distinct origin lookup contexts
are retained and accepted only when their numeric or unresolved/nonliteral outcomes agree.

### Test Stencil — Write First

```python
def test_absolute_target_accepts_distinct_scopes_with_equal_outcomes():
    demand = logical_demand(ABSOLUTE_TARGET, origins=[calc_scope_a(), calc_scope_b()])
    resolved = resolve_logical_demand(demand, values=both_resolve_to(17.0))
    assert resolved.value == 17.0
    assert resolved.nonliteral is False
    assert resolved.group_source == Path("calc_route.sysml")
    assert len(resolved.outcomes) == 2
```

### Changes Required

See [design.md#logical-demand-and-resolution](design.md#logical-demand-and-resolution),
[design.md#logical-resolution-and-provenance](design.md#logical-resolution-and-provenance), and
[spec.md#c-supplied-value-demand-identity-and-precedence](spec.md#c-supplied-value-demand-identity-and-precedence).

- [x] Create `tests/unit/test_logical_demand_resolution.py` first with exact nodes:
  - `test_absolute_target_accepts_distinct_scopes_with_equal_outcomes`
  - `test_absolute_target_rejects_different_semantic_outcomes`
  - `test_literal_nonliteral_and_unresolved_disagreement_is_contextual`
  - `test_calc_origin_group_precedes_constraint_origin_after_resolution`
  - `test_constraint_only_provenance_ladder_and_missing_failure`
  - `test_distinct_lookup_context_is_evaluated_once`
  - `test_unique_target_counts_warning_and_synthesis_order`
  - `test_real_attribute_collision_counts_applied_once_and_keeps_real_value`
- [x] Extend `tests/unit/test_supplied_values.py` with unchanged precedence/direct-owner controls
  against the new resolution outcome, without weakening their existing values or warning bytes.
- [x] `src/sysml_codegen/resolution/supplied_values.py:37-203`: add the exact four immutable records,
  make `_match_override`/`_resolve_value` retain the winning `RedefinitionData` and source, and keep
  tier 2a local rather than importing `_find_literal_redefinition` or another graph resolver.
- [x] Normalize every calc/prepared-constraint origin through `_binding_target` before merging.
  Sort logical demands by target QN and origins by the approved canonical origin key.
- [x] Implement `resolve_logical_demand` with one evaluation per distinct lookup context, semantic
  outcome comparison, and post-resolution provenance tiers. Reject `None`, `Path("unknown")`, CWD,
  sentinels, conflicting sources at the selected tier, and numeric results with no source.
- [x] Implement the new copy-on-write `enrich_graph_design_attributes` seam and its unique logical
  scan/apply/nonliteral/warning/synthesis behavior. Keep it uncalled by production until Phase 4.
- [x] Leave the old route-level function untouched only until Phase 4 replaces its callers. Do not
  make either function wrap or delegate to the other, and do not call Phase 3 a releasable state.
- [x] Do not modify `resolution/graph_builder.py`, `analysis/parameter_groups.py`, producer
  selection, strict actual resolution, or any schema.

### Validation

```bash
uv run --frozen pytest -q -rs \
  tests/unit/test_logical_demand_resolution.py \
  tests/unit/test_supplied_values.py
uv run --frozen python -O -m pytest -q -rs \
  tests/unit/test_logical_demand_resolution.py \
  tests/unit/test_supplied_values.py
```

- [x] Equal outcomes across distinct scopes pass; different numeric outcomes and
  literal/nonliteral/unresolved disagreements fail with target plus ordered origin contexts.
- [x] Calc provenance wins only after successful resolution. Constraint-only provenance covers
  exact captured source, real winning record, portable usage fallback, tier conflict, and absence.
- [~] Unique targets produce the exact OD-A08/OD-A09 info summaries **and** OD-A10 warning
  order/counts; context evaluations do not increment logical counts. **Split, per audit F2.**
  OD-A08/OD-A09 exact INFO summaries and the no-double-count property are proven publicly and
  live. OD-A10 is delivered in two pieces: the stable node
  `test_r7_multi_target_order_permutations` proves target order, defaults, dedup, and
  live/replay parity (observed 3/3/0, warnings `[]`); the warning-order half is proven by
  `tests/unit/test_logical_demand_resolution.py::test_two_warnings_occur_in_order_within_one_batch`,
  which pins both warning bytes in order within one batch. The design's live 3/2/1 shape is
  **not** delivered — see the recorded deviation in evidence.md §6.
- [x] A real attribute collision counts as applied, emits one warning, preserves the real value,
  and creates no synthetic attribute.
- [x] No Item 2 resolver symbol/import or new target-equivalence rule appears in the diff.

### What We Know Works After This Phase

The new demand model preserves every origin needed for correct resolution and provenance, yet
performs one deterministic logical operation per existing normalized target.

### Implementation Notes

- **Completed:** 2026-07-19, landed together with Phase 4 in one session. Phase 3 was
  never left as a releasable state.
- **Resolution/provenance observations:** the four records landed with the design's
  exact fields. `_match_override`/`_resolve_value` now return the winning
  `RedefinitionData`; tier 2a matches the exact type QN locally, which removed the
  `_find_literal_redefinition` import from this module entirely, so the helper's
  brittle Strategy-2 name fallback is now structurally unreachable from the
  materializer. `resolve_logical_demand` evaluates each distinct lookup context once
  (three origins over two contexts produce two `ValueResolution`s) and requires
  identical `(value, nonliteral)` outcomes. Provenance tiers verified end to end:
  calc-origin source wins over a constraint origin on a shared target (B3); the
  constraint-only ladder walks exact captured target source -> real winning-record
  owner source -> portable constraint-usage source; `Path("unknown")`, `None`, and CWD
  are rejected as absences; two distinct sources at the selected tier raise.
- **Exact count/warning outputs:** two calc routes onto one target now log
  `scanned 1 ... 1 literal applied, 0 non-literal skipped` (was 2/2). Three distinct
  targets log `scanned 3 ... 3 literal applied` and synthesize in ascending target-QN
  order. A real-attribute collision counts as applied, emits exactly one
  `already covers` warning, keeps the real value, and synthesizes nothing. A
  non-literal-only target counts once as a skip.
- **Deviation — `RedefinitionData` carries no source path.** The design's tier-3
  wording ("one unique real source from the winning override/redefinition records")
  has no field to read: the record type has only `owning_part_qn`,
  `attribute_name`, `redefinition_type`, `literal_value`, `expression_text`,
  `expression_ast`. Implemented as the unique source file among captured design
  attributes belonging to that owner (`_owner_source`). Deterministic and derived only
  from real captured data, but it is an interpretation, not the literal design text.
- **Deviation — `Mapping[Any, ...]` on the enrichment key type.** The design specifies
  `Mapping[Union[Path, str], ...]`. `Mapping` is invariant in its key type, so that
  annotation makes mypy reject the live `dict[Path, ...]` caller. Annotated `Any` with
  the constraint stated in a comment; both key kinds normalize to `Path` immediately.
- **Temporary Phase 3 non-releasable state:** none survived the session. The old
  route-level `materialize_supplied_values` was never adapted to the new 3-tuple
  ladder — it was deleted in Phase 4 instead, so no wrapper or dual path ever existed.
- **Audit remediation (2026-07-19, candidate 2).** Independent audit returned *Needs work*
  (`audit.md`). Fixed: audit F1, a silent value-loss regression introduced by the tier-2a/2b
  merge — a malformed literal on the type def did `return None, False, None`, exiting the
  whole tier loop and suppressing a valid literal on the consuming part def. The predecessor
  fell through and resolved 42.0; the candidate lost the value with no warning at all
  (`0 applied, 0 skipped`). The malformed branch now `continue`s, restoring predecessor
  fall-through exactly. Regression test
  `tests/unit/test_supplied_values.py::test_malformed_type_def_literal_does_not_suppress_part_def_literal`
  was verified RED against the pre-fix code and GREEN after. The pre-existing final-tier
  swallow (all tiers malformed -> silent `None`) is deliberately unchanged: it predates
  Item 1 and belongs to Item 4's diagnostics scope.
  Added additively, without touching the Phase 0 overlay (its SHA-256 is still
  `aea7c821...eacb624b`): fixture `tests/fixtures/constraint_occurrence_demand/cycle_indirect/`
  plus new file `tests/conformance/test_constraint_occurrence_demand_supplementary.py` with
  `test_r5_indirect_cycle_is_atomic_on_the_public_route`, closing OD-A05's `A -> B -> A`
  variant on the public route; and
  `test_two_warnings_occur_in_order_within_one_batch` for OD-A10's warning-order half.
- **Audit notes F4-F7 dispositions.**
  - **F7 applied.** `_usable_source` no longer compares against `Path.cwd()`; a pure
    resolution helper must not classify identical inputs differently depending on the
    directory the generator ran from.
  - **F6 declined with reason, recorded at the call site.** The count noun *is* wrong —
    the log says "referenced bindings" but reports `len(demands)`, the number of normalized
    targets. Correcting it changes bytes pinned in the Phase 0 acceptance overlay, whose
    SHA-256 is the RED/GREEN anchor. A comment at `supplied_values.py` records the defect and
    says to fix noun and anchor together once the anchor is retired.
  - **F4 declined with reason.** `_owner_source` reports "no source" and "two conflicting
    sources" identically, downgrading a tier silently where `_unique_source` would raise.
    Fixing it properly means widening `ValueResolution.winning_source` to carry a set — a
    third deviation from the design's record shape — and it must not raise during resolution,
    since eager provenance validation is exactly the defect fixed in candidate 1. The current
    downgrade is conservative: control falls to a lower tier that itself raises on ambiguity
    or absence, so no wrong value is grouped silently; only the tier attribution is coarser.
    Worth doing as a scoped design-contract change, not folded into audit remediation.
  - **F5 declined with reason.** `source_location_mode=None` genuinely has two disagreeing
    consumers (`_project_excluded_location` raises; `_verified_predicate_source_key` falls back
    to an unvalidated basename). Both production callers pass explicit values, so the
    disagreement is reachable only from unit tests. Making the source-key path raise too would
    require updating the migrated unit call sites that pass no mode; that is the right fix and
    is deferred rather than done here. Deviation 3 in evidence.md is corrected to say the
    "same place, same message" claim holds for the excluded-location path only.
- **Post-review correctness fix (CONFIRMED defect, fixed 2026-07-19).** Independent
  review found that `resolve_logical_demand` computed and validated grouping
  provenance for *every* numeric result, while the REQ-SVM-03 collision guard that
  discards the value ran later in `enrich_graph_design_attributes`. A target already
  covered by a real captured design attribute, whose calc origins sat in two different
  `.sysml` files, therefore raised `calc-origin provenance is ambiguous` — where the
  deleted route correctly kept the real value and skipped synthesis with a warning.
  Validating provenance for a value that is definitely discarded is wrong.
  **Fix:** `group_source` is no longer a `ResolvedDemand` field. Provenance selection
  moved to a public `select_group_source(resolved, *, exact_real_sources)`, which the
  enrichment seam calls *only* after the collision guard has confirmed the target will
  really be synthesized. Resolution owns the value; the call site owns whether a
  grouping decision exists at all — policy at the call site, mechanism in the utility.
  The load-bearing `assert resolved.group_source is not None` disappeared with the
  restructure rather than being converted, since `select_group_source` returns `Path`
  or raises. Pinned semantics are unchanged: a collision still counts as applied, still
  emits exactly one REQ-SVM-03 warning, keeps the real value, and synthesizes nothing;
  non-collision counts, INFO/warning bytes, and ordering are byte-identical.
  **Regression test:** `test_collision_covered_target_with_split_calc_sources_does_not_raise`
  in `tests/unit/test_logical_demand_resolution.py` pins both halves — it first asserts
  that selecting provenance for that demand *does* raise `calc-origin provenance is
  ambiguous`, then asserts the enrichment seam completes without raising, keeps the
  real `99.0`, adds nothing under the second route's file, logs one `already covers`
  warning, and reports `scanned 1 ... 1 literal applied`. Phase 0 overlay bytes were
  not touched.
- **Disposition (orchestrator, agent-grade, recorded — not settled):** the four-field
  `ResolvedDemand` contract deviation is ACCEPTED as compelled by the confirmed defect.
  The `select_group_source` restructure is the right shape — policy at the call site,
  mechanism in the utility.
- **Deviation — `ResolvedDemand` has four fields, not five.** The design's table lists
  `group_source` on the record. The defect above is the reason it cannot live there:
  the record is built before the caller knows whether the target survives the collision
  guard. Recorded as a deviation, superseding the design's field list for this record.
- **Issues or challenged bets:** B2 held (exact normalized target QN was sufficient
  identity in every case, with distinct scopes reconciled semantically rather than
  structurally). B3 and B4 held. B5 held.

---

## Phase 4: One Live/Replay Enrichment Route and Deletion Cutover

### Goal

Switch live and replay to one `Path`-keyed copy-on-write enrichment seam and one prepared batch,
then delete the recorder, bare-demand collector, duplicate route blocks, last-write-wins synthesis,
and stale comments/docs. Leave no wrapper or feature flag.

### Assumption Under Test

The shared enrichment return can replace both route-specific materialize/bucket loops without
mutating either input map and without changing valid snapshot bytes, parameter grouping,
absolute-reference behavior, or retained producer roots.

### Test Stencil — Write First

```python
def test_live_and_replay_call_one_prepare_and_one_copy_on_write_enrichment(monkeypatch):
    live = instrument_pipeline_builder(monkeypatch)
    replay = instrument_graph_rebuild(monkeypatch)
    assert live.calls == ["prepare", "enrich", "lower"]
    assert replay.calls == ["prepare", "enrich", "lower"]
    assert live.input_attributes_unchanged and replay.input_attributes_unchanged
    assert all(isinstance(key, Path) for key in live.enriched_attributes)
```

### Changes Required

See [design.md#live-construction-and-capture-call-order](design.md#live-construction-and-capture-call-order),
[design.md#same-checkout-replay-call-order](design.md#same-checkout-replay-call-order), and
[design.md#appendix-a--deletion-and-production-accounting](design.md#appendix-a--deletion-and-production-accounting).

- [x] Update `tests/unit/test_design_overrides_threaded.py` to spy on
  `enrich_graph_design_attributes`, assert one call on replay, and prove the loaded attribute
  mapping/lists are unchanged.
- [x] Extend `tests/conformance/test_snapshot_constraint_parity.py` and
  `tests/conformance/test_constraint_pipeline_threading.py` with one prepare -> enrich -> group ->
  lower route assertions and retained-root/catalog observations.
- [x] Migrate `tests/unit/test_supplied_values.py` from `materialize_supplied_values` to the new
  enrichment seam. Delete tests that only certify the removed tuple/route implementation; retain
  every behavioral precedence/collision/nonliteral control.
- [x] `src/sysml_codegen/orchestration/pipeline_builder.py:828-904`: replace the temporary prepared
  demand bridge and manual bucket loop with the shared enrichment return; use its `Path` keys to
  build `ParameterGroupDeriver`; lower from the same batch; publish the successful transcript.
- [x] `src/sysml_codegen/snapshot/graph_rebuild.py:82-134,173-223`: use one `FrozenOccurrenceIndex`,
  one prepared batch carried in classifier inputs, the same enrichment return, and the same batch
  for lower. Never mutate `snap["design_attributes"]` during enrichment.
- [x] Delete `collect_bare_actual_demand` and its exports/imports/comments from
  `constraint_lowering.py`, `pipeline_builder.py`, `graph_rebuild.py`, tests, and docs.
- [x] Delete `RecordingOccurrenceIndex` and its recorder-specific prose from
  `part_instance_index.py`; update `FrozenOccurrenceIndex`/deserialize comments to describe the
  successful prepared transcript.
- [x] Delete `materialize_supplied_values`, the nested route `_demand`, route-counted loop,
  `synth[target.qn]` overwrite, silent missing-source drop, route tuple plumbing, and all imports.
- [x] Correct truth-bearing comments only in:
  - `src/sysml_codegen/orchestration/pipeline_context.py:133-137`
  - `src/sysml_codegen/snapshot/__init__.py:12-18`
  - `src/sysml_codegen/snapshot/loader.py:773-775`
  - `src/sysml_codegen/snapshot/serializer.py:84-87`
- [x] Update `docs/architecture/reference/27-snapshot-generation.md:42-43,77` and
  `docs/architecture/reference/28-constraint-lowering-and-catalog.md:19,47` to describe the landed
  prepared-batch/enrichment/lowering flow. State same-checkout replay's limited role. Do not add
  compensating prose about rejected paths.
- [x] Do not touch `snapshot/capture.py`, `orchestration/snapshot_context.py`, or
  `analysis/parameter_groups.py` unless contradictory implementation evidence triggers a scope
  stop. Any such path automatically joins the ledger.

### Validation

```bash
uv run --frozen pytest -q -rs \
  tests/conformance/test_constraint_occurrence_demand_acceptance.py \
  tests/unit/test_constraint_usage_preparation.py \
  tests/unit/test_logical_demand_resolution.py \
  tests/unit/test_part_instance_index.py \
  tests/unit/test_supplied_values.py \
  tests/unit/test_design_overrides_threaded.py \
  tests/unit/test_occurrence_roundtrip_parity.py \
  tests/conformance/test_constraint_pipeline_threading.py \
  tests/conformance/test_snapshot_constraint_parity.py \
  tests/conformance/test_constraint_snapshot_identity.py
uv run --frozen python -O -m pytest -q -rs \
  tests/conformance/test_constraint_occurrence_demand_acceptance.py \
  tests/unit/test_constraint_usage_preparation.py \
  tests/unit/test_logical_demand_resolution.py \
  tests/unit/test_part_instance_index.py \
  tests/unit/test_supplied_values.py
```

- [x] All five stable public RED nodes are GREEN with the Phase 0 overlay hash unchanged.
- [x] `test_r7_constraint_only_provenance_after_resolution` is GREEN live and same-checkout replay.
- [x] Copy-on-write tests prove a new `dict[Path, list[DesignAttributeData]]`, copied lists, and no
  mutation of the input mapping.
- [x] Source deletion checks return no matches:

  ```bash
  rg -n 'RecordingOccurrenceIndex|collect_bare_actual_demand|materialize_supplied_values|admit_qns|synth\[target\.qn\]' \
    src tests docs
  ```

- [x] Review explicit owner dispatch to prove no final/default arm grants package behavior.
- [ ] Re-run the metrics tool over the automatic baseline/candidate union. Simplify any path above
  its cap. Stop before Phase 5 if total executable LOC exceeds 3,524; target 3,504 or fewer.
  **NOT MET — Stop #4 invoked.** The tool was rerun and genuine simplification was
  performed, but the union lands at 3,827 on the frozen counter (3,799 in design units)
  against a 3,552 / 3,524 gate. Certification is not started. Full ledger in the
  Implementation Notes below.
- [x] Run complexity and structural checks:

  ```bash
  uv run --frozen ruff check --select C901,PLR0912,PLR0915 \
    src/sysml_codegen/analysis/part_instance_index.py \
    src/sysml_codegen/analysis/constraint_lowering.py \
    src/sysml_codegen/resolution/supplied_values.py \
    src/sysml_codegen/orchestration/pipeline_builder.py \
    src/sysml_codegen/snapshot/graph_rebuild.py
  ```

- [x] Confirm no version/schema/lock drift:

  ```bash
  git diff --exit-code ecdc7285be1508c08e82830c93072306f40e6b34 -- pyproject.toml uv.lock
  rg -n 'executable-profile/v4|snapshot-v3|SNAPSHOT_FORMAT_VERSION' src tests
  ```

- [x] Existing fixture and baseline manifests remain equal to Phase 0. Verified against
  the baseline tree rather than Phase 0's recorded digests: existing-fixture aggregate
  `73ba5ca9...f356b50` and `baseline_outputs` aggregate `0bbea88f...4021b34c` are
  byte-identical between the candidate and `ecdc7285`, and `git status -- tests/fixtures`
  shows no tracked fixture changed. Phase 0 recorded `fde9c5df...54bd5` /
  `921bbb6a...bf66`, which the baseline tree does not reproduce under the recorded
  commands — a Phase 0 mis-recording, not fixture drift. Per orchestrator disposition,
  Phase 6 evidence reissues the corrected aggregates with that note and does not
  overwrite the Phase 0 record.

### What We Know Works After This Phase

Live and replay share one lifecycle route, all obsolete control-flow paths are gone, and the
candidate satisfies the default simplification gate before broad certification begins.

### Implementation Notes

- **Completed:** 2026-07-19. Cutover complete; **certification NOT started** — see the
  Stop #4 ledger below.
- **Actual deletions and call order:** deleted `materialize_supplied_values` and its
  nested route `_demand` (including the route-counted loop, the `synth[target.qn]`
  last-write-wins overwrite, the silent missing-source drop, and the
  `constraint_actual_demand` tuple plumbing); `collect_bare_actual_demand` and every
  import of it; `RecordingOccurrenceIndex` and its recorder prose; the duplicate
  live/replay materialize-and-bucket blocks. `rg -n
  'RecordingOccurrenceIndex|collect_bare_actual_demand|materialize_supplied_values|admit_qns|synth\[target\.qn\]'
  src tests docs` returns no matches. No wrapper, flag, alias, or dead fallback
  remains. Call order proven by
  `test_live_and_replay_call_one_prepare_and_one_copy_on_write_enrichment`: both live
  and replay record exactly `["prepare", "enrich", "lower"]`, the input attribute
  mapping is unchanged across the call, and every returned key is a `Path`.
- **Test results:** full suite **3008 passed, 26 skipped, 0 failed** — first fully
  green run of the item. All six public acceptance nodes GREEN (the five stable RED
  nodes plus `test_r7_constraint_only_provenance_after_resolution`), live and
  same-checkout replay, with the Phase 0 overlay hash
  `aea7c8219d716f4ca1ecb154ca6ed8a13e0c15b1184fdcfe2d92b556eacb624b` unchanged.
  Optimized (`-O`) focused gate: 62 passed.
- **Version/fixture preservation result:** `git diff` against the Item 0 predecessor
  for `pyproject.toml` and `uv.lock` is empty. Snapshot v3, executable-profile/v4, and
  package 0.1.0 untouched. `git status -- tests/fixtures` shows only the new untracked
  `constraint_occurrence_demand/` tree; existing-fixture aggregate `73ba5ca9...f356b50`
  and `baseline_outputs` aggregate `0bbea88f...4021b34c` both equal the values the
  baseline tree at `ecdc7285` reproduces. Mypy holds at the 76-error baseline (a
  77th error I introduced on the enrichment key annotation was fixed, not waived).
- **Complexity:** 16 findings at both revisions. `lower_constraints` improved 34 -> 19
  (115 -> 63 statements); `_structured_paths` and `materialize_supplied_values` left
  the list; `enrich_graph_design_attributes` (11) and
  `_verified_predicate_source_key` (11) joined it.

#### STOP #4 INVOKED — production growth gate not met

Measured by the frozen counter (`70fddc98...`, unmodified) over the automatic union:

| Path | Baseline | Candidate | Delta | Design cap | Over cap |
|---|---:|---:|---:|---:|---:|
| `analysis/constraint_lowering.py` | 1,083 | 1,160 | +77 | 1,072 | +88 |
| `analysis/part_instance_index.py` | 229 | 258 | +29 | 234 | +24 |
| `resolution/supplied_values.py` | 213 | 382 | +169 | 220 | +162 |
| `orchestration/pipeline_builder.py` | 645 | 645 | 0 | 623 | +22 |
| `snapshot/graph_rebuild.py` | 156 | 153 | −3 | 142 | +11 |
| `snapshot/serializer.py` | 157 | 160 | +3 | 157 | +3 |
| `orchestration/pipeline_context.py` | 63 | 63 | 0 | 62 | +1 |
| `snapshot/__init__.py` | 31 | 31 | 0 | 27 | +4 |
| `snapshot/loader.py` | 975 | 975 | 0 | 967 | +8 |
| **Union (frozen counter)** | **3,552** | **3,821** | **+269** | — | — |
| **Union (design units, counter − 28)** | **3,524** | **3,793** | **+269** | — | — |

(`supplied_values.py` reads 376 after the post-review provenance fix, down from 382.)

- **Hard gate** (orchestrator decision: no net growth, frozen counter ≤ 3,552):
  **FAIL by 269**.
- **Design target** (net −20, ≤ 3,532): **FAIL by 289**.
- AST statements 1,907 -> 2,064; branch points 644 -> 683; raw lines 5,211 -> 5,609.
- Independent simplification review confirmed the remainder is irreducible capability
  cost: only ~5-15 lines of deliberate defensive guards are recoverable, and those are
  to be left in place. No further LOC reduction is being attempted. The OD-R43
  deviation goes to the owner as-is.
- Final gate re-run after the correctness fix: full suite **3009 passed, 26 skipped,
  0 failed**; six public nodes GREEN; Phase 3 and Phase 4 focused gates green in both
  normal and `-O` mode; mypy steady at the 76-error baseline.

Certification is not started. The candidate is left honest: no test weakened, no error
context deleted, no semantics packed into one-liners to move the counter.

**Why the design's net-negative expectation did not hold.** Appendix A set
`constraint_lowering.py` and `pipeline_builder.py` caps *below* their baselines while
Item 1 adds, by the design's own mandate, machinery that did not previously exist:
association with full identity/location verification, a prepared batch with an
all-or-nothing owner transcript, `PreparedConstraintUsage`/`PreparedConstraintBatch`,
a five-field structured `RecursiveContainmentError` with per-path cycle detection, and
four immutable demand records plus a resolution and four-tier provenance engine. The
deleted code was smaller precisely because it was wrong — a route-counted loop with
last-write-wins synthesis and nullable-QN membership is far cheaper in lines than one
verified logical operation per target with deterministic provenance. Deletion recovered
roughly 110 executable lines; the required replacements cost roughly 385.

**Simplification actually performed** (genuine, not counter-gaming): merged the tier-2a
and tier-2b redefinition scans into one owner loop; dropped the
`_find_literal_redefinition` dependency entirely; collapsed the duplicated
live/replay materialize-and-bucket blocks into one shared enrichment return; replaced
an O(n²) conflict-message comprehension with a keyed lookup; folded the two-branch
prepared-item construction into one. These are reflected in the numbers above.

**What would close the gap** — all of which exceed this item's authority:
1. An owner-reviewed **OD-R43 deviation** accepting the growth as the cost of
   correctness (the orchestrator explicitly cannot grant this).
2. Re-scoping the demand model — e.g. dropping `ValueResolution`/`ResolvedDemand` as
   published records and returning bare tuples — which contradicts the approved design's
   Data Contracts.
3. Simplifying `snapshot/loader.py` (+8 over cap) and `pipeline_builder.py` (+22 over
   cap) where they were already over cap at the predecessor. Both are pre-existing
   overages unrelated to Item 1, and touching them is out of scope.

---

## Phase 5: Public Live, Replay, Execution, and Repository Gates

### Goal

Complete every Item 1 public licensed observation, same-checkout replay regression, generated TEAx
verdict, unchanged absolute-reference control, normal/optimized/affected/full gate, mypy baseline,
Ruff/format/diff check, and fixture manifest check at one committed candidate coordinate.

### Assumption Under Test

The unit-proven lifecycle remains correct through public source extraction, immediate capture and
replay, graph/catalog generation, parameter grouping, and real TEAx execution without modifying an
existing valid fixture.

### Test Stencil — Write First

```python
@requires_license
@pytest.mark.execution
def test_sibling_literal_overrides_produce_distinct_values_and_verdicts(tmp_path):
    package = generate_fixture_package("constraint_occurrence_demand/overrides", tmp_path)
    outputs = execute_generated_package(package)
    assert generated_input_values(package) == {LOW_TARGET: 4.0, HIGH_TARGET: 6.0}
    assert verdict(outputs, "low") == ("violated", False)
    assert verdict(outputs, "high") == ("satisfied", True)
```

### Changes Required

See [design.md#od-a01od-a13-map](design.md#od-a01od-a13-map),
[design.md#candidate-gates](design.md#candidate-gates), and
[spec.md#mandatory-acceptance-cases](spec.md#mandatory-acceptance-cases).

- [x] Create `tests/execution/test_constraint_occurrence_demand_execution.py` with
  `test_sibling_literal_overrides_produce_distinct_values_and_verdicts`. Use production generation
  plus real teax-simkit, exact 4.0/6.0 inputs, and violated/False versus satisfied/True verdicts.
- [x] Finish public assertions in
  `tests/conformance/test_constraint_occurrence_demand_acceptance.py` without changing any Phase 0
  byte. If an expectation was incomplete, Phase 0 was incomplete; do not silently edit the overlay.
- [x] Add no production code in this phase except a narrowly diagnosed correction that re-enters
  the relevant earlier phase and reruns all downstream checks.
- [x] Commit the product/tests/fixtures candidate, record `CANDIDATE_REV=$(git rev-parse HEAD)`, and
  require the tracked production/test/fixture surface to be clean at that revision. The preserved
  untracked `.claude/projects/` state does not invalidate the coordinate.

### Licensed Public Selection

```bash
set -a
source /home/reid/1cfe/agentic-mbse/.env
set +a
uv run --frozen pytest -q -rs \
  tests/conformance/test_constraint_occurrence_demand_acceptance.py::test_r4_live_anonymous_association \
  tests/conformance/test_constraint_occurrence_demand_acceptance.py::test_r5_finite_first_cycle_is_atomic \
  tests/conformance/test_constraint_occurrence_demand_acceptance.py::test_r7_shared_target_dedup_grouping_counts \
  tests/conformance/test_constraint_occurrence_demand_acceptance.py::test_r7_constraint_only_provenance_after_resolution \
  tests/conformance/test_constraint_occurrence_demand_acceptance.py::test_r7_multi_target_order_permutations
TEAX_SIMKIT_PATH=../teax/packages/teax-simkit \
  uv run --frozen pytest -q -rs -o addopts= -m execution \
  tests/execution/test_constraint_occurrence_demand_execution.py::test_sibling_literal_overrides_produce_distinct_values_and_verdicts \
  tests/execution/test_constraint_execution.py::test_multi_instance_expansion_n_modules_one_predicate
```

- [x] `-rs` shows no skip for OD-A01/A04/A05/A08/A09/A10. Any required skip stops certification.
- [x] A01/A02/A07 exact warning sequence is `[]`; excluded/unsupported owners make zero queries.
- [x] A08/A09 exact INFO summaries and A10 exact ordered warnings match the spec byte-for-byte.
- [x] Same-checkout replay results are labeled regression-only and non-certifying in test names,
  comments, and evidence.

### Focused Normal and Optimized Gates

```bash
uv run --frozen pytest -q -rs \
  tests/conformance/test_constraint_occurrence_demand_acceptance.py \
  tests/unit/test_constraint_usage_preparation.py \
  tests/unit/test_logical_demand_resolution.py \
  tests/unit/test_part_instance_index.py \
  tests/unit/test_supplied_values.py
uv run --frozen python -O -m pytest -q -rs \
  tests/conformance/test_constraint_occurrence_demand_acceptance.py \
  tests/unit/test_constraint_usage_preparation.py \
  tests/unit/test_logical_demand_resolution.py \
  tests/unit/test_part_instance_index.py \
  tests/unit/test_supplied_values.py
```

### Affected Regression Union

```bash
uv run --frozen pytest -q -rs \
  tests/unit/test_occurrence_roundtrip_parity.py \
  tests/unit/test_design_overrides_threaded.py \
  tests/conformance/test_part_instance_index.py \
  tests/conformance/test_constraint_lowering.py \
  tests/conformance/test_constraint_lowering_integrity.py \
  tests/conformance/test_constraint_profile_route_parity.py \
  tests/conformance/test_constraint_snapshot_identity.py \
  tests/conformance/test_constraint_pipeline_threading.py \
  tests/conformance/test_snapshot_constraint_parity.py \
  tests/conformance/test_constraint_catalog_determinism.py \
  tests/conformance/test_constraint_migration_mapping.py \
  tests/conformance/test_parameter_group_deriver.py \
  tests/conformance/test_sibling_channel_ambiguity.py \
  tests/conformance/test_matcher_reclassification.py \
  tests/conformance/test_ife_plant.py \
  tests/conformance/test_fusion_tea_snapshot.py
```

### Exact Unchanged Absolute-Reference Controls

```bash
uv run --frozen pytest -q -rs \
  tests/conformance/test_sibling_channel_ambiguity.py::test_chamber_power_disambiguated_to_chamber_b \
  tests/conformance/test_matcher_reclassification.py::test_quoted_owner_refs_reclassify_to_design_attribute \
  tests/conformance/test_matcher_reclassification.py::test_shared_design_attribute_key_collapses \
  tests/conformance/test_ife_plant.py::test_ife_plant_graph_builds \
  tests/conformance/test_ife_plant.py::test_shape4_wires_to_exact_channel \
  tests/conformance/test_fusion_tea_snapshot.py::test_fusion_tea_snapshot_zero_offenders \
  tests/conformance/test_fusion_tea_snapshot.py::test_renamed_consumers_collapse_to_one_source_ep
```

### Existing Finite and Shared-Producer Controls

- [x] Run and record:
  - `tests/conformance/test_constraint_lowering.py::test_multi_instance_three_ids_three_channels_shared_binding`
  - `tests/conformance/test_constraint_pipeline_threading.py::test_multi_instance_end_to_end_through_wired_path`
  - `tests/conformance/test_constraint_catalog_determinism.py::test_catalog_fingerprint_deterministic_across_repeated_live_loads`
  - `tests/execution/test_constraint_execution.py::test_multi_instance_expansion_n_modules_one_predicate`
- [x] Pin the three existing occurrence suffixes and shared channel from OD-A03 exactly as specified
  in [design.md#od-a01od-a13-map](design.md#od-a01od-a13-map).

### Full Quality Gates

```bash
uv run --frozen pytest -q -rs tests/
uv run --frozen mypy src/
uv run --frozen ruff check \
  src \
  tests/conformance/test_constraint_occurrence_demand_acceptance.py \
  tests/unit/test_constraint_usage_preparation.py \
  tests/unit/test_logical_demand_resolution.py \
  tests/unit/test_part_instance_index.py \
  tests/unit/test_supplied_values.py \
  tests/execution/test_constraint_occurrence_demand_execution.py
uv run --frozen ruff format --check \
  src \
  tests/conformance/test_constraint_occurrence_demand_acceptance.py \
  tests/unit/test_constraint_usage_preparation.py \
  tests/unit/test_logical_demand_resolution.py \
  tests/unit/test_part_instance_index.py \
  tests/unit/test_supplied_values.py \
  tests/execution/test_constraint_occurrence_demand_execution.py
git diff --check ecdc7285be1508c08e82830c93072306f40e6b34 HEAD
```

- [x] Full suite is run with the license loaded. Record all passes/skips/deselections; distinguish
  unrelated intentional skips from required live cells.
- [x] Mypy is equal to or better than the Phase 0 baseline; do not relabel baseline errors as new.
- [x] Ruff, format, and diff checks pass.
- [x] Existing fixture, `baseline_outputs`, lock, and `.claude/projects` aggregate hashes match
  Phase 0. The new Item 1 fixture tree matches the public overlay manifest.
- [~] **Retired by owner ruling 2026-07-19 (epic commit a1435e1).** Re-run the automatic union and complexity reports at `CANDIDATE_REV`; the hard non-positive
  executable gate and all five OD-R40 absence claims pass.

### What We Know Works After This Phase

All Item 1 public live cells, same-checkout regression routes, generated values/verdicts, finite and
absolute-reference controls, and repository quality gates are proven at one candidate coordinate.

### Implementation Notes

- **Completed:** 2026-07-19.
- **Candidate revision and lock hashes:**
  `CANDIDATE_REV=28bc8b0fc22ba85cbed94febf0963bebf7cd600e`, built on `cfeb7ee`
  (Phases 1-4) and `a1435e1` (epic LOC amendment). Tracked product/test/fixture surface
  clean at that revision. `git diff` against the Item 0 predecessor for
  `pyproject.toml` and `uv.lock` is empty — locks unchanged from OD-R30.
- **Licensed live/TEAx output:** licensed five-node selection ran with `-rs` and showed
  **no skip** — 5 passed; full acceptance file 6 passed. TEAx execution 2 passed (new
  sibling-override node plus the multi-instance control): generated inputs `low=4.0` /
  `high=6.0`, verdicts `("violated", False)` / `("satisfied", True)`,
  `constraint_report` `assessed_count=2` / `headline="violation"`, persisted with both
  statuses. **Environment gotcha:** the TEAx lane cannot run under this repo's `uv run`
  (teax-simkit imports `pandas`, absent from the codegen venv; the pre-existing control
  fails identically, which is how it was diagnosed as environmental). Working
  incantation recorded in evidence.md §3.
- **Normal/optimized/affected/full results:** full suite 3,009 passed / 26 skipped /
  16 deselected / 0 failed. Focused normal 63; focused `-O` 63. Affected regression
  union (16 files) 162 passed. Absolute-reference controls 2 passed. OD-A03
  finite/shared-producer controls 3 passed, with occurrences
  `constraint_multi_instance__the_design__c__cell[0..2]` and the single shared channel
  `constraint_multi_instance__the_design__c__cell__power_calc__p` pinned as specified.
- **Mypy/Ruff/format/diff/manifests:** mypy 76 errors in 17 files, equal to the Phase 0
  baseline (no baseline error relabelled as new). Ruff `check src/` clean. Ruff
  `format --check src/`: 19 would reformat versus the predecessor's 20 — I formatted the
  two production files my work made newly unformatted, and `supplied_values.py` came out
  formatted; fixtures and `baseline_outputs` were never formatted (generator-owned bytes,
  byte-identity gates depend on them). Existing-fixture aggregate
  `73ba5ca9...f356b50` and `baseline_outputs` aggregate `0bbea88f...4021b34c` equal the
  predecessor tree; acceptance-file hash `aea7c821...eacb624b` unchanged since Phase 0;
  `.claude/projects/` untracked and untouched throughout.
- **Issues or unproven skips:** none. No required licensed or TEAx node skipped. The LOC
  union/complexity rows are retired by owner ruling and recorded informationally only.

---

## Phase 6: Evidence, Ledgers, and Supported Status Updates

### Goal

Produce `evidence.md` with unchanged RED/GREEN hashes and exact outputs, honest LC-I09 labels,
complete production/deletion accounting, open later-item boundaries, and only supported checkbox
or status updates.

### Assumption Under Test

The recorded commands, hashes, revisions, and observations are sufficient for a fresh auditor to
reproduce every Item 1 claim without relying on chat history or treating same-checkout replay as a
certifying relocated route.

### Evidence Stencil — Write First

```text
assert red_manifest_sha256 == green_manifest_sha256
assert each_red_node.failed_at == named_defect_assertion
assert each_green_node.exit_code == 0
assert required_live_skips == []
assert candidate_executable_loc <= baseline_executable_loc
assert open_items includes [4, 5, 13]
assert replay_label == "same-checkout regression; non-certifying"
```

### Changes Required

- [x] Create `.project/active/constraint-lifecycle-occurrence-demand/evidence.md` with these
  sections:
  - exact repository revisions, versions, locks, imported module paths, license state, and public
    versus private seam;
  - fixture, owner kind, source form/polarity, anonymity, actual source, occurrence/override shape,
    and open predecessor rows for every public observation;
  - Phase 0 overlay manifest and standalone test hash, rechecked unchanged at RED and GREEN;
  - one command, exit code, and exact failure output per RED node, plus the corresponding exact
    GREEN output;
  - historical 31-green control clearly labeled non-RED;
  - OD-A01–OD-A13 results and OD-R traceability back to this plan;
  - normal, optimized, affected, licensed public, TEAx, full, mypy, Ruff, format, diff, and fixture
    manifest outputs;
  - automatic changed-path union with raw/executable/AST/branch/complexity before/after per file,
    zero-side handling, separate non-production ledgers, and named deletion proof;
  - version/schema non-change record and exact source-absence outputs;
  - LC-I09 subset label: public live row-1 observations may support Item 1; same-checkout replay is
    regression-only/non-certifying; relocated/full-tree/composed coordinates remain open; and
  - explicit open Items 4 (R-8 warning-location totality), 5 (relocated whole tree), and 13
    (composed sealed artifact). Also state that Item 2's resolver was not absorbed.
- [x] At the committed candidate, reconstruct the overlay from Git and verify it in both worktrees:

  ```bash
  CANDIDATE_REV=$(git rev-parse HEAD)
  git archive "$CANDIDATE_REV" -- \
    tests/conformance/test_constraint_occurrence_demand_acceptance.py \
    tests/fixtures/constraint_occurrence_demand | \
    tar -xf - -C "$ITEM1_RED_ROOT/sysml-codegen"
  (cd "$ITEM1_RED_ROOT/sysml-codegen" && sha256sum -c "$ITEM1_RED_ROOT/overlay.sha256")
  sha256sum -c "$ITEM1_RED_ROOT/overlay.sha256"
  sha256sum tests/conformance/test_constraint_occurrence_demand_acceptance.py
  ```

- [x] Run each of the five stable nodes again in a fresh candidate process and record its exact pass
  output beside the historical failure.
- [x] Update this plan's phase checkboxes and implementation notes immediately from recorded facts.
- [x] Update the four spec success-criterion checkboxes only if every supporting public observation
  and simplification gate is present.
- [x] Update design/plan status to implemented only when the candidate and all required gates are
  complete. Do not rewrite approved `[INFERRED]` bets as settled.
- [x] Update Epic Item 1's four success-criterion checkboxes only when evidence directly supports
  each one. Do not check Item 5's relocated leg or Item 13's composed proof.
- [x] Update `.project/CURRENT_WORK.md` with the tested candidate revision, evidence path, exact gate
  summary, open Items 4/5/13, and next stage (`my-audit`). Preserve unrelated entries.

### Validation

- [x] Mechanically verify every OD-A01–OD-A13 and every OD-R row below has a recorded evidence
  pointer and no unsupported `pass`, `certified`, or `complete` label.
- [x] Verify no placeholder digest, `[TO BE FILLED]`, unchecked completed action, or unrecorded
  deviation remains in the completed plan/evidence.
- [x] Run final artifact checks:

  ```bash
  rg -n 'TO BE FILLED|PLACEHOLDER|TBD' \
    .project/active/constraint-lifecycle-occurrence-demand/plan.md \
    .project/active/constraint-lifecycle-occurrence-demand/evidence.md
  git diff --check
  git status --short --branch
  ```

- [x] A fresh audit can reproduce the evidence without modifying the stable overlay or existing
  fixtures.

### What We Know Works After This Phase

Item 1 has a truthful, reproducible record at one candidate coordinate. The record closes only the
supported row-1 public-live scope and leaves later lifecycle ownership explicit.

### Implementation Notes

- **Completed:** 2026-07-19.
- **Evidence revision/path:**
  `.project/active/constraint-lifecycle-occurrence-demand/evidence.md`, recorded at
  `CANDIDATE_REV=28bc8b0fc22ba85cbed94febf0963bebf7cd600e`. Machine-readable metrics in
  `evidence/item1-candidate-metrics-ninefile.json` and
  `evidence/item1-candidate-metrics.json`.
- **RED/GREEN hash equality:** the five stable RED failures and their GREEN passes use
  identical public bytes — acceptance file SHA-256
  `aea7c8219d716f4ca1ecb154ca6ed8a13e0c15b1184fdcfe2d92b556eacb624b` at both the Phase 0
  RED run and the candidate, with the `constraint_occurrence_demand/` fixture tree
  unmodified since Phase 0.
- **Final production/deletion ledger:** deleted `materialize_supplied_values` + nested
  route `_demand`, `collect_bare_actual_demand`, `RecordingOccurrenceIndex`, the
  route-counted loop, the `synth[target.qn]` last-write-wins overwrite, the silent
  missing-source drop, the route tuple plumbing, and both duplicated live/replay
  materialize-and-bucket blocks. `rg` over `src tests docs` returns no matches for any
  of them. No wrapper, feature flag, compatibility alias, route adapter, or dead
  fallback remains. LOC ledger retired by owner ruling; recorded informationally in
  evidence.md §1 (nine-file union 3,552 -> 3,818, net +266).
- **Checkbox/status updates:** this plan's Phase 0-6 checkboxes and notes; spec success
  criteria supported by public observation; epic Item 1 criteria supported by evidence;
  `CURRENT_WORK.md`. Unrelated entries preserved. Two rows are marked `[~] retired by
  owner ruling` rather than checked, because they gate on LOC.
- **Open Items 4/5/13 and audit handoff:** R-8 unmappable warning locations stays open
  under Item 4 — Item 1 moved that preflight mechanically and made no claim the masking
  path is closed. Relocated whole-tree proof stays with Item 5; sealed-artifact /
  composed-thread proof stays with Item 13. Item 2's producer/exact-QN resolver was not
  absorbed. Same-checkout replay is labeled regression-only and non-certifying in test
  names, comments, and evidence. Eight recorded deviations are listed in evidence.md §6,
  and the review-confirmed collision-guard defect plus its regression test in §7 —
  including the honest note that the regression test could not be executed against
  pre-fix code because it imports a symbol that did not exist then.

---

## OD-A Acceptance Traceability

| Case | Phase(s) | Exact test/proof | Required evidence |
|---|---|---|---|
| **OD-A01** | 0, 1, 5, 6 | Stable `test_r4_live_anonymous_association`; unit `test_association_rejects_independent_decision_mutations_before_preflight` | Intended R-4 RED; unchanged GREEN hash; pair cardinality/identity/location mutations; zero-query/warning proof; live admitted-only target/catalog observations. |
| **OD-A02** | 1, 5, 6 | `test_excluded_unsupported_zero_query_and_package_branch`; `test_missing_required_frozen_owner_wraps_corruption_with_recapture_guidance`; stable valid-replay node | Query spy by owner kind; explicit package branch; genuine missing-entry corruption; valid transcript success; exact `[]` warnings live/replay. |
| **OD-A03** | 2, 5, 6 | Four existing multi-instance/catalog/execution nodes named in Phase 5 | Exact three suffixes, module/channel/catalog order, one shared producer channel on each occurrence, repeated-live fingerprint stability. |
| **OD-A04** | 0, 5, 6 | `test_sibling_literal_overrides_produce_distinct_values_and_verdicts` | Public source, generated input values 4.0/6.0, TEAx low violated/False and high satisfied/True, no skip. |
| **OD-A05** | 0, 2, 6 | Stable `test_r5_finite_first_cycle_is_atomic`; unit `test_later_owner_cycle_discards_staged_transcript` | Intended R-5 RED; exact structured cause fields/paths; permutation stability; zero returned/published/mutated state. |
| **OD-A06** | 2, 5, 6 | Existing `test_bare_fixed`–`test_unrecognized_upper_bound_node_blocks`; seven conformance controls; new zero-count/multi-digit/retype/diamond tests | Normal and `-O` outputs for every unsupported and finite control; unchanged nine-path oracle and integer order. |
| **OD-A07** | 0, 1, 4, 5, 6 | Stable `test_r4_valid_replay_not_corrupt` | Intended R-4 replay RED; live/replay association, demand/group/count/input/catalog equality; exact `[]`; explicit non-certifying label. |
| **OD-A08** | 0, 3, 4, 5, 6 | Stable `test_r7_shared_target_dedup_grouping_counts`; logical-demand units | Intended R-7 RED; exact normalized target, calc group, 1/1/0, INFO bytes, `[]` warnings, one producer, live/replay/reversal parity. |
| **OD-A09** | 3, 4, 5, 6 | Public `test_r7_constraint_only_provenance_after_resolution`; unit `test_constraint_only_provenance_ladder_and_missing_failure` | Target/group `constraint_route_params`, 1/1/0, INFO bytes, `[]`, producer/catalog parity, provenance tiers/conflicts/absence, replay non-certifying. |
| **OD-A10** | 0, 3, 4, 5, 6 | Stable `test_r7_multi_target_order_permutations`; unique-order unit | Intended R-7 RED; exact three-target and one-synth order, 3/2/1, exact two warnings once/in order, defaults, route/input reversal, live/replay parity. |
| **OD-A11** | 0, 6 | The five stable named RED/GREEN nodes | One authored byte set; manifest/test hashes; one fresh process per node; exact failure and pass outputs; historical 31 greens labeled controls only. |
| **OD-A12** | 5, 6 | Licensed selection, focused normal/`-O`, affected union, full suite, TEAx execution | One candidate coordinate; no required skips; public live subset labels; same-checkout replay non-certifying; relocated/full LC-I09 open. |
| **OD-A13** | 0, 4, 6 | Metrics tool, source-absence checks, diff/fixture ledgers | Automatic union, zero-side treatment, raw/executable/AST/branch/complexity delta, five deletion proofs, separate non-production ledgers, ≤ baseline hard gate. |

## OD-R Requirement Traceability

| Requirement | Phase(s) | Test/evidence route |
|---|---|---|
| **OD-R01** | 1, 5 | Prepared owner-kind dispatch versus independent source-form predicate controls; A01–A03. |
| **OD-R02** | 2, 5 | Existing multi-instance IDs/modules/channels/catalog plus A04 execution; A03/A04. |
| **OD-R03** | 2 | Structural self/indirect/finite-first failures and unsupported-cardinality controls; A05/A06. |
| **OD-R04** | 5, 6 | Required public live cells, regression-only replay label, open relocated/composed cells; A03–A07/A12. |
| **OD-R05** | 0, 3, 6 | Scope diff firewall; no graph/general resolver changes; evidence names open Items 2/5/13. |
| **OD-R06** | 0, 5 | Public fixtures through `build_pipeline_context` and real execution; no synthetic closure claim; A01/A03–A05/A08–A10/A12. |
| **OD-R07** | 0, 1, 6 | Same-batch association and unchanged same-semantic-capture hashes; no cross-version/tracking claim; A01/A07. |
| **OD-R08** | 5, 6 | Same-checkout replay parity recorded as non-certifying; A07–A10/A12. |
| **OD-R10** | 1 | Pure one-to-one association plus independent deletion/duplication/reorder mutations; A01. |
| **OD-R11** | 1 | Cardinality, exact identity, and exact location checks before preflight/queries; A01 unit. |
| **OD-R12** | 1 | Excluded/unsupported zero-query/demand and admitted part/calc/package branches; A01/A02. |
| **OD-R13** | 1, 4 | Explicit package branch, unknown-owner contextual behavior, source review proving no fallback; A02/A13. |
| **OD-R14** | 1, 4, 5 | One live/frozen prepared query contract, valid replay, missing admitted key corruption only; A02/A07. |
| **OD-R15** | 2 | Per-query/batch atomic cycle tests with full cause context and zero downstream mutation; A05. |
| **OD-R16** | 2, 5 | Complete existing finite suite plus zero-count, multi-digit, subtype/retype/diamond controls; A03/A06. |
| **OD-R20** | 3 | `_binding_target` exact-QN normalization tests for `::`, one-hop dotted, and bare routes; A08–A10. |
| **OD-R21** | 3, 4 | Merge before resolution/materialization; source diff proves no Item 2 equivalence/resolver; A08–A10/A13. |
| **OD-R22** | 3, 5 | Calc-origin group precedence after equal semantic resolution, route/input reversal; A08. |
| **OD-R23** | 3, 5 | Exact-real -> winning-record -> usage-source constraint-only ladder, conflicts/absence; A09. |
| **OD-R24** | 3, 5 | Existing precedence/direct-owner tests and real-collision control remain unchanged; A10 and affected union. |
| **OD-R25** | 3, 5 | Ascending normalized target order, one logical count/warning/synth, complete reversal; A08/A10. |
| **OD-R26** | 3, 4, 5 | One retained shared producer and one constraint-only materialization through live/replay graph/catalog; A03/A08/A09. |
| **OD-R27** | 4, 5, 6 | Same shared seam and exact live/replay identity/group/count/warning/producer/catalog parity; A07–A10. |
| **OD-R30** | 0, 6 | Exact three-repository revisions, package/profile versions, and lock hashes from Item 0. |
| **OD-R31** | 0, 6 | One stable overlay, five fresh intended RED processes, same bytes at candidate GREEN; A11. |
| **OD-R32** | 0, 6 | Historical 31 greens recorded only as compatibility controls; A11. |
| **OD-R33** | 5, 6 | Focused normal/`-O`, affected union, compatible full, licensed public live, and execution gates; A12. |
| **OD-R34** | 5, 6 | Full per-cell coordinate fields, public/private seam, non-certifying replay, open LC-I09 legs; A12. |
| **OD-R35** | 5, 6 | Generated exact inputs and real TEAx verdicts for sibling occurrence overrides; A04. |
| **OD-R40** | 4, 6 | Symbol/source absence plus reviewed explicit dispatch and target-keyed implementation; A13. |
| **OD-R41** | 0, 4, 6 | Pre-edit automatic nine-path start, diff-derived added/deleted/moved union, zero-side rules; A13. |
| **OD-R42** | 0, 6 | Hashed counter classification and separate test/fixture/generated/docs/project ledgers; A13. |
| **OD-R43** | 4, 6 | ≤3,524 hard default, ≤3,504 design target, owner-deviation stop if positive; A13. |
| **OD-R44** | 0, 4, 6 | Identical AST/complexity algorithm, Ruff complexity checks, and five duplicate-path deletions; A13. |
| **OD-R45** | 4, 6 | Corrected comments/docs name association, owner filtering, cycle atomicity, replay role, and target normalization without compensating prohibition prose. |

## Final Completion Gate

Item 1 is ready for `my-audit` only when all of the following are true:

- [x] Every Phase 0–6 action and validation checkbox supported by evidence is checked.
- [x] Five stable RED failures and five GREEN passes use identical public test/fixture hashes.
- [x] OD-A01–OD-A13 and every OD-R row have exact evidence pointers.
- [x] Required licensed live and TEAx nodes have no skip.
- [~] **Retired by owner ruling 2026-07-19 (epic commit a1435e1)** — recorded informationally in evidence.md §1, not as pass/fail. Automatic production union is complete and executable LOC is non-positive versus 3,524,
  with the design's 3,504 target either met or explained while still below the hard gate.
- [x] `RecordingOccurrenceIndex`, `collect_bare_actual_demand`, route-level materialization,
  last-write-wins synthesis, nullable-QN membership, recursive empty return, and implicit package
  fallback are absent.
- [x] Existing fixture/baseline, lock/version/schema, absolute-reference, finite, R-8, normal,
  optimized, affected, full, mypy, Ruff, format, and diff controls are recorded.
- [x] Evidence calls LC-I09 a public-live subset, calls same-checkout replay non-certifying, and
  leaves Items 4, 5, and 13 open.
- [x] Spec/design/plan/epic/CURRENT_WORK status changes make no claim beyond the evidence.

After implementation, run `my-audit`; the implementing agent does not self-certify.
