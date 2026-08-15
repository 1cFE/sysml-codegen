# Audit 4 — Independent composite audit of Phase 4

**Verdict:** FINDINGS (8 numbered; none blocking Phase 5 *assembly*, two blocking the
acceptance packet's central claim)
**Audited:** 2026-08-11
**Branch:** `item7-rebuild`
**Range:** Gate 4A commit `804d8a2` → HEAD `54ecb3b`
**Auditor:** fresh session; implemented none of this work.

---

## Environment, asserted before any measurement

Every number below was produced in this environment. The 4D session lost hours to the F2
resolution trap, so this is the first thing recorded, not the last.

```
python      /home/reid/1cfe/item7-rebuild-venv/bin/python
sysml_codegen  /home/reid/1cfe/sysml-codegen-item7-rebuild/src/sysml_codegen/__init__.py
agentic_mbse   /home/reid/1cfe/agentic-mbse-item7-rebuild/src/agentic_mbse/__init__.py
license     set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a   (key present)
```

Both editable sources resolve into the paired `*-item7-rebuild` worktrees. No import resolves
to an original or forensic checkout.

---

## Summary

The Phase 4 recovery did **not** repeat the original run's self-certification. Every recorded
measurement I re-ran reproduced exactly — the full licensed suite, the corpus, the execution
lane, the v6 verify, both checker modes, and two of the eight dual dry-run probes all landed on
their recorded numbers to the digit. The dispositions are real work: 298 rows, none
self-proving, replacement proofs green across the board, and the one genuinely hard problem
(the duals) was measured, found false, and escalated rather than smoothed over.

The failure is narrower and lives in one place: **the retirement runbook over-claims.** It is
headed "Status: MECHANICAL", and it is not. Its four steps enumerate 66 ledger rows; 128
`retire-with-owner` test modules and 34 `repoint` rows are named by no step at all, and step 1's
per-node edit table — the artifact that exists specifically to make the step mechanical — is
incomplete on both axes. I measured this rather than inferred it: executing step 4's single
deletion as written turns 16 test modules into collection errors, and simulating step 1's
fixture/script deletions turns 7 nodes red in 3 surviving files the table does not mention.

This matters because "the retirement is prepared to the point where executing it is mechanical"
is the headline the owner is being asked to accept at the Phase 5 stop. The preparation is
real; the runbook does not yet carry it.

---

## What I verified, and how

### 1. The executed deletions (G0 + G1) — CLEAN

**C1 (`analysis/signature_extractor.py`, L-006 / L-241).** Re-verified the whole chain myself
rather than reading the commit message.

- *The module was genuinely dead.* At `6ba346e~1` the only references anywhere in `src` were
  the `analysis/__init__.py:26` re-export and the module's own test. No production caller.
- *`preservation.py` owns the responsibility.* `should_regenerate_stencil`
  (`src/sysml_codegen/generation/preservation.py:109`) carries the same decision logic behind
  `_extract_signature_from_impl` (`:46`) and `_generate_expected_signature_from_module`
  (`:170`), with the field-set comparison in `FunctionSignature.matches`. It is live —
  `cli/__init__.py:432` calls it.
- *Its tests pass.* Re-ran the C1 proof myself:
  `check_ledger_4a.py replacements --row L-006 --row L-241` → `green` on both, 32 + 20 + 21 = 73
  nodes.

The two implementations differ in mechanism (visitor class vs `ast.walk`) and in input
(`CalculationDefinitionData` vs `PipelineModule`); `reference/23` states that difference
explicitly. The responsibility transfer is real.

**C2 (registry class-name collision, fail-before-mutate).** Re-ran the specimen:
`tests/conformance/test_public_authority_switch.py` → **19 passed**, including
`test_a_registry_class_name_collision_refuses_before_the_writer_runs` (`:468`). The test does
the right thing — it snapshots the populated output tree, runs `run_codegen` on
`unresolvable_attr_probe`, and asserts three separate properties: the run returns `False`, the
log carries the package's own named refusal, `"Unexpected error"` does **not** appear, and the
tree is byte-equal to `before`. The ordering claim is additionally pinned by the sibling
`test_a_refusal_after_the_context_but_before_the_writer_also_leaves_the_tree`, which injects
the refusal at the `_reconcile_params_coverage` boundary — that one proves the *ordering* rather
than the fixture, which is the right design.

**Exception identity across the error-class move.** Measured directly, not assumed:

```
SysMLParsingError  core.errors is orchestration.pipeline_context is generation  → True
CodeGenerationError core.errors is orchestration.pipeline_context is generation → True
```

Same class objects through every re-export. Every existing `except` in `cli/__init__.py:1013,
1016, 1124, 1127`, `analysis/constraint_lowering.py:721` and `tests/helpers/legacy_route.py:72,
75` still catches what it caught. `generation/errors.py` no longer defines the class and only
imports it for typing — no shadow class exists.

### 2. The checker machinery — sound within stated limits; I found four

I read both scripts and then attacked them.

**What `check_ledger_4a.py` genuinely catches.** The design is better than it needed to be. The
candidate set comes from a Git *diff*, not a worktree scan, so deletions are visible (the exact
failure that lost 118 paths the first time). `check_states` verifies state claims against
`git cat-file`, not against the ledger's own word. `removal_surface` is machine-readable from
`removes` blocks rather than parsed out of prose. `data_hits` is deliberately over-reporting on
the non-module axis. `replacement_is_green` distinguishes green / missing / deselected / failed
and refuses `exit 0 without a passing summary` — absence cannot be proof.

**Attacks that failed (the machinery held):**

- *Self-proving rows.* I looked for any row whose `replacement_proof_node` lives in the file the
  row retires. Ten rows do — and **all ten are `repoint`**, where the file survives and the
  surviving node is the correct proof. Zero `retire-with-owner` rows prove themselves.
- *Aliased imports.* `_import_keys` handles `from pkg import mod`, `import pkg.mod as x`, and
  `from pkg.mod import *`. I could not construct a static import spelling it misses.
- *`retire-with-owner` with no proof.* Zero such rows.

**Attacks that succeeded — report these as machinery limits, not as bugs:**

1. **Transitive import breakage is invisible.** `surface_hits` walks each file's own AST. A file
   that breaks because a *helper it imports* breaks is not seen. Measured: the checker reports 2
   surviving test files broken at module level by group `4B-G4`; deleting `tests/helpers/
   legacy_route.py` actually breaks **16**. See F1.
2. **`group_readiness` clears on the disposition *label*, not on measurement.** A file marked
   `repoint` clears its group whether or not the repoint was performed —
   `check_surface_coverage` skips any path that has a row at all. The "all six groups READY"
   claim therefore rests entirely on 185 hand-authored disposition labels being truthful. I
   found one that is not (F2, L-298).
3. **Vacuity is undetectable, and 89 proof entries name a whole file.** `replacement_is_green`
   runs the node and looks for `passed`. A node that exists and asserts nothing is green. 89 of
   the proof entries (32 distinct files) name a file rather than a `::node`, so "green" means
   "that file passes" — usually true regardless of whether it covers the retired responsibility.
   This is a real ceiling on what the checker can promise; the per-node accounting in the ledger
   notes is what actually carries that weight, and it is prose.
4. **A textual data scan misses computed filenames.** `data_hits` matches literal basenames, so
   a path built by f-string or a `glob("*.json")` is missed. Narrow, and the over-reporting
   posture is the right trade.

**`check_proof_integrity.py`.** Correct as written, and now **structurally incapable of
failing**: it derives `blocked_paths` from `group_readiness().blockers`, which reached zero at
chunk 19, so the problem loop has nothing to iterate. Its own output is honest about this — it
prints "0 problems over **0 blocked files**" — but the runbook lists it in the per-step battery
as if it were an ongoing gate. It also has **no test suite of its own**
(`tests/unit/test_check_proof_integrity.py` does not exist), unlike `check_ledger_4a.py`, which
has 642 lines of tests. See F6.

**Their own suites.** `check_ledger_4a.py`'s tests run inside the full suite (green). The
checker's four modes at HEAD: `paths` **298 rows / 0 problems**, `surface` **0 unrowed
breakages**, `groups` **all six READY**, `replacements` **0 failures across all 298 rows**.

### 3. Disposition sampling — 31 rows, weighted as the brief asked

Rows examined in some depth: L-006, L-011, L-028, L-032, L-033, L-034, L-036, L-037, L-094,
L-120, L-125, L-129, L-130, L-132, L-133, L-135, L-167, L-180, L-181, L-182, L-185, L-186,
L-189, L-191, L-192, L-193, L-194, L-206, L-212, L-219, L-241, L-249, L-275, L-276, L-277,
L-279, L-281, L-284, L-289, L-292, L-295, L-298.

**The execution-lane restoration (chunk 11) — accurate.** This is the heaviest claim in Phase 4
and it holds. Per-file node counts, measured:

| File | Nodes | Role |
|---|---:|---|
| `test_constraint_execution.py` (L-192) | 15 | legacy |
| `test_constraint_def_owned_redefining_execution.py` (L-191) | 1 | legacy |
| `test_constraint_occurrence_demand_execution.py` (L-193) | 1 | legacy |
| `test_gate_a_execution.py` (L-194) | 1 | legacy |
| `test_constraint_verdicts_exact_route.py` | 15 | **replacement** |
| `test_fusion_tea_real_teax.py` | 12 | live |
| `test_fusion_tea_mutation_teax.py` | 8 | live |

15 + 1 + 1 + 1 + 15 + 12 + 8 = **53**, exactly the recorded execution lane, and the replacement
file's 15 nodes pass. "15 nodes vs the legacy 15" is accurate for L-192. The per-node accounting
on the L-192 row names a specific replacement for each of the fifteen, and L-191/193/194 each
name a specific node inside that file. One legacy node
(`test_zero_assertion_aggregator_not_assessed`) is explicitly **not** replaced and carried to
the owner as a product question — that is recorded on the row and in the plan, which is the
honest handling.

**The part-6 re-derivations — mechanism citations real.** Spot-checked the citations that carry
weight. `elaboration/project.py:229,264` do construct with `fallback_entry_points=set()`, which
is the basis for L-249's "structurally unreachable on the exact route" argument. The banner
claims about unreachability are true — I measured the construction closure independently
(below) rather than trusting the pins.

**Chunks 17–19 (the fatigued work) — mostly sound, one row false.** The chunk-19 disposition
reasoning is careful, and the one `archive-with-findings` (L-182) correctly names a
`findings_home`, which `check_states` enforces. But L-298's responsibility statement is
**false against the code** — see F2. That is the only outright false disposition statement I
found, and I found it by measurement, not by reading.

**Import-localization claims — hold where checked.** The three chunk-17 localizations and the
two chunk-18 ones do move their imports function-local; the surface check confirms none of them
appears as a module-level breakage.

### 4. The dual measurements — both reproduced exactly

| Probe | Recorded | Re-measured here |
|---|---|---|
| `probe_calc_def_data_qualifier_drop.py` (L-034, codegen) | 58 of 86 consumer nodes fail; baseline 311 passed / 18 skipped | **58 failed, 253 passed, 18 skipped** (253 + 58 = 311) ✓ |
| `probe_constraint_profile_qualifier_drop.py facts` (L-036, paired worktree) | 34 of 450 | **34 failed, 416 passed** (= 450) ✓ |

**The two unrowed agentic call sites are real.** Verified in the paired worktree:

- `agentic_mbse/validation/level4_constraints.py:55` calls `extract_constraint_facts`, `:56`
  calls `evaluate_profile`.
- `agentic_mbse/validation/level6_architecture.py:620` and `:621`, identically.

Neither file has a ledger row — I checked the row set directly, not the note text: zero rows
whose path contains `level4` or `level6`. The L-036 probe's own failures include
`test_level4_reconciliation.py` and `test_item12_checks.py` nodes, which is the breakage
arriving from the consumer side.

**The runbook's owner-gated fifth entry carries them.** Confirmed: the sequence table's fifth
row is "the dual **qualifier drop** — L-033, L-034, L-036, L-037 — **OWNER-GATED.** Not part of
any step", and step 1's dual table states plainly that L-036/L-037 "cannot execute the `removes`
block at all". The separation is honest and the sizing is attached. This is the part of Phase 4
that best resists the self-certification charge: the prescribed action was measured, found
impossible, and escalated with numbers instead of being narrowed to fit.

### 5. The runbook's "mechanical" claim — **does not hold** (F1, F2)

Desk-checked with targeted measurements in a throwaway `git worktree` (created, measured,
removed; the audited tree was never mutated).

**Step 4, executed as written.** Step 4 deletes two rows (L-008, L-276) and has no per-node edit
table. Deleting `tests/helpers/legacy_route.py` alone:

```
16 test modules newly fail to collect
(baseline collection errors: 1, the environment-dependent tests/execution TEAx sibling)
```

14 carry `retire-with-owner` and are presumably *meant* to go — but no step lists them, so an
operator following the runbook deletes L-276 and gets 16 collection errors. Two of the 16,
`test_public_authority_switch.py` (L-279) and `test_uncovered_params.py` (L-249), are `repoint`
rows whose files **survive**; their per-node edits exist nowhere in the runbook.
`test_public_authority_switch.py` is the file that holds the 3E authority pins and is the named
replacement proof node for six G0 rows.

**Step 1, executed as written.** Simulating only its fixture and script deletions (37
`extraction_snapshot.json` + `scripts/capture_extraction_snapshots.py`):

```
tests/conformance/test_d5_variants.py            3 failed
tests/unit/test_capture_fixtures_filter.py       2 failed
tests/conformance/test_public_authority_switch.py 2 failed
```

None of the three is in step 1's per-node edit table. The last two failures are
`test_a_v5_snapshot_is_refused_by_name_at_the_loader` and
`test_generate_from_a_v5_snapshot_refuses_without_falling_back` — the v5 typed-refusal pins.
After the fixtures go, the refusal silently changes class from "refused by name" to
"file not found". That is the exact concern L-180 was repointed to protect against, applied to a
file the runbook's post-step check does not cover (it names only
`test_snapshot_v5_gate.py`).

**Steps 2 and 3.** Step 2 (G2′) breaks two surviving test files at module level —
`test_source_identity_routes.py` (L-182, `archive-with-findings`, a **test** file with 12 nodes
that will raise a collection error while sitting in `tests/`) and `test_uncovered_params.py`
(`from sysml_codegen.snapshot import build_full_graph_from_snapshot`, `:53`). Neither step has an
edit table. Step 3 is clean.

**The arithmetic of the gap.** Steps 1–4 name **66** rows. The ledger carries **133**
`retire-with-owner` (131 unnamed by any step, 128 of them test modules), **34** `repoint`
(all unnamed) and **18** `archive-with-findings`. The dispositions exist and are good; the
runbook does not carry them into an executable sequence.

### 6. The proposed v6 batch — correctly marked, but load-bearing (F4)

- `capture_v6_batch.py --verify` → **15 captured / 22 refused / 0 deviations**. Reproduced.
- Spot-checked three records against the live verify run: `wi014_toy` (graph 4/4/1/1),
  `unresolvable_attr_probe` (graph 10/9/0/0), `solar_battery_model` (refused, 24×
  `SI_SELF_BINDING`). All three agree with `batch.json` and with the recorded corpus outcomes,
  including the exact multiset counts rather than a summary.
- **PROPOSED marking is everywhere it should be**: the manifest's `status` field
  (`capture_v6_batch.py:255`), `batch.json`'s top-level `status`, the batch README's first line,
  the commit message, and the plan.

What is *not* true is the README's implication that the batch is inert. Measured: removing the
15 snapshots the batch added yields **38 failed + 57 errors**. It is reversible by Git, as the
README says, but ~95 test outcomes now depend on those bytes. See F4.

### 7. The 4D documentation — good, with two corrections

- **Distinctness check**: `31 numbered reference documents checked, 0 identical-content groups`.
  Reproduced. The check compares exact full-file bytes with an empty allowlist — no similarity
  threshold, which is the right call.
- **Code references resolve.** I extracted every `` `*.py` `` reference from `reference/00`,
  `reference/27`, `CLAUDE.md`, `overview.md` and `verification-matrix.md` and resolved each
  against the tree: 15, 16, 11, 33 and 95 references respectively, **zero unresolved**. The one
  apparent miss, `input_resolver.py` in the matrix, is a deliberate historical reference ("the
  standalone aggregation resolver … was deleted") and correct.
- **Banners.** Spot-checked all eleven. Each carries the three parts: the subject named by
  module path, the state ("present in the tree and importable, and **not reachable from any
  public caller**"), and the gating ("prepared and gated on owner acceptance at the Phase 5
  stop"). `09` correctly carries the scoped mixed banner instead.
- **I measured the banners' central claim independently** rather than trusting the pins. From
  `orchestration.exact_pipeline_context`, all eight legacy modules I probed —
  `hierarchy_resolver`, `dependency_backtracker`, `graph_builder`, `output_registry`,
  `pipeline_builder`, `constraint_lowering`, `producer_resolution`, `parameter_groups` — are
  **unreachable**. The construction closure is genuinely clean. `reference/25`'s "measured"
  claim about `hierarchy_resolver` is true.
- **The carried byte-identity claim is true, and I re-measured it** rather than inheriting it
  (this is the 3D/F1 class the brief warned about): `git diff --name-only 1672c57 804d8a2 --
  docs/architecture/ CLAUDE.md` → **0 files**. The 4D record's "the restore step was already
  satisfied" is correct. At HEAD, 21 doc files differ, matching the ten-subject table.
- **The stale-docstring count is an undercount** — see F5.
- **CLAUDE.md's import-residual sentence is false as written** — see F3.

### 8. The gates — every recorded number reproduced

| Gate | Recorded | Measured here |
|---|---|---|
| Full licensed suite | 3840 passed / 47 skipped / 53 deselected | **3840 / 47 / 53** ✓ |
| `no live syside license` lines | 0 | **0** ✓ |
| Execution lane (`-m execution`) | 53 passed | **53** ✓ |
| Corpus ledger (`-k corpus`) | 12 passed | **12** ✓ |
| `capture_v6_batch.py --verify` | 15 / 22 / 0 | **15 / 22 / 0** ✓ |
| `check_ledger_4a.py paths` | 298 rows / 0 problems | **298 / 0** ✓ |
| `check_ledger_4a.py surface` | 0 unrowed breakages | **0** ✓ |
| `check_ledger_4a.py groups` | all six READY | **all six READY** ✓ |
| `check_ledger_4a.py replacements` | green for every row | **0 failures / 298 rows** ✓ |
| `check_proof_integrity.py` | 0 problems over 0 blocked files | **0 / 0** ✓ |
| `ruff check src` | 16 | **16** ✓ |
| `ruff check src tests scripts` | 866 | **866** ✓ |
| `mypy src` | 69 errors in 16 files | **69 in 16** ✓ |
| `git diff --check` | clean | **clean** ✓ |

**Battery consistency across the Phase 4 commits.** I checked the sequence for numbers that
moved without explanation. The one apparent discontinuity resolves cleanly: chunk 19 records
**3830**, Gate 4D records a **3817** baseline and **3827** final. The gap is exactly 13, and it
is the `test_exact_constraint_route.py` module the 4D session ignored under the F2 resolution
trap. 3830 − 13 = 3817; 3827 + 13 = 3840 = today's measurement. The 4D note states this and the
arithmetic checks out in both directions. The G0→G1 delta (3577 → 3565 = −12: 13 deleted nodes
less 1 new multi-node replacement test) also reconciles.

### 9. Cross-cutting honesty check

I sampled measured-claim assertions across the Phase 4 records and re-ran five of them: the two
dual probes, the byte-identity restore claim, the execution-lane 15-vs-15 accounting, and the
chunk-19 end-state checker proof. **All five reproduced.** I found no instance of the 3D/F1
class — a number carried forward from an earlier session without re-measurement — in the Phase 4
records. The one place a stale number could have hidden (the 4D suite counts, measured in a
divergent environment) is explicitly flagged, re-measured by the orchestrator, and the flag is
committed at `54ecb3b`.

---

## Findings

### F1 — HIGH — The runbook's four steps do not name the work the retirement requires

**Evidence.** Steps 1–4 enumerate 66 ledger rows. 131 `retire-with-owner` rows (128 of them test
modules) and all 34 `repoint` rows are named by no step. Measured in a scratch worktree:
deleting step 4's `tests/helpers/legacy_route.py` alone produces **16 new collection errors**
against a baseline of 1. Steps 2, 3 and 4 have no per-node edit table at all.

**Why the checker did not catch it.** `surface_hits` sees only each file's own AST, so
transitive breakage through a helper is invisible; it reports 2 module-level breakages for
`4B-G4` where 16 modules actually stop collecting.

**Resolution.** Either (a) each step's row list is extended to name every file that retires or
gets edited with it, or (b) the runbook states plainly that the four steps are the *production*
deletions and that the test-side execution is derived from the ledger's `disposition_4c` column
by a script. (b) is cheaper and more honest; a mechanical derivation is checkable in a way a
hand-copied list is not. Until one of these lands, the runbook heading should not read
"MECHANICAL".

### F2 — HIGH — Step 1's per-node edit table is incomplete, and one disposition statement is false

**Evidence.** Simulating step 1's fixture and script deletions (measured, scratch worktree):

- `tests/conformance/test_d5_variants.py` — 3 failures. `:116` asserts
  `(d5.FIXTURES / original / "extraction_snapshot.json").is_file()` for `catf_mfe_model`
  (L-061), `solar_battery_model` (L-089) and `gate_a` (L-072) — all three deleted by step 1.
  **L-298's disposition note says "Names the v5 snapshot filename only to exclude it from a
  variant … Nothing to change when the family retires." That is false**: the reference is a
  positive existence assertion, not an exclusion.
- `tests/unit/test_capture_fixtures_filter.py` — 2 failures. `:90` and `:102` shell out to
  `scripts/capture_extraction_snapshots.py`, which step 1 deletes (L-275). L-292's note is bare
  ("Gate 4C part 5: see reason").
- `tests/conformance/test_public_authority_switch.py` — 2 failures, both v5 typed-refusal pins.
  After the fixtures go the refusal changes class from "refused by name" to "file not found",
  which is the property L-180 exists to protect. Step 1's post-step check covers only
  `test_snapshot_v5_gate.py`.

**Resolution.** Add the three files to step 1's edit table with their per-node edits; correct
L-298's disposition note to state what actually has to change; extend step 1's post-step
"typed refusal is still typed" check to cover the two `test_public_authority_switch.py` nodes.

### F3 — MEDIUM — `CLAUDE.md` understates the CLI import residual by a factor of three

**Evidence.** `CLAUDE.md` lists eleven modules as pending retirement, then says "the CLI's
*import* closure still reaches three of those modules — pinned by name so the residual cannot
grow." Measured: the closure of `sysml_codegen.cli` reaches **10 of those 11** (all but
`orchestration.snapshot_context`). The sentence is true about the *pin* —
`LEGACY_AUTHORITY_MODULES` is a named four-module set of which three are reached — but it is
written as a claim about the closure, and a Phase 5 reader will take it that way.

This is the same class of defect Gate 4D existed to remove, in the document 4D wrote last.

**Resolution.** Reword to name the pinned set explicitly ("a pinned four-module set, of which
three are reached") and state the real closure size, or widen `LEGACY_AUTHORITY_MODULES`.

### F4 — MEDIUM — The PROPOSED v6 batch is load-bearing, and the packet should say so

**Evidence.** The batch README says "This batch is not authority. It is *readiness*" and
"Everything in this batch is reversible by Git." Measured: removing the 15 snapshots the batch
added yields **38 failed, 57 errors** across the suite. Git-reversible is true; cost-free is
not.

**Resolution.** One line in the acceptance packet: revising the batch means re-running
`capture_v6_batch.py` and re-greening ~95 test outcomes, not reverting a commit. This is
information the owner needs to price the decision, and it strengthens rather than weakens the
batch's case.

### F5 — LOW/MEDIUM — More than two production docstrings are stale in the recorded class

**Evidence.** Gate 4D records exactly two (`orchestration/exact_pipeline_context.py:3-6`,
`elaboration/__init__.py:5-7`) — both confirmed still present. Sweeping for siblings found at
least two more, both in live production files:

- `src/sysml_codegen/generation/constraint_catalog.py:3-4` — "Assembly runs once, early
  (`orchestration/pipeline_builder.py`, right after `extend_graph_with_constraints`)". The only
  callers of `assemble_constraint_catalog` are `pipeline_builder.py:1153` and
  `snapshot/graph_rebuild.py:225`, both retiring. The docstring describes the legacy call site
  as the live one and becomes a dangling reference at steps 1–2.
- `src/sysml_codegen/generation/pipeline.py:7` — "Takes ComputationGraph (from graph_builder) as
  input". On the exact route the graph comes from `elaboration/project.py`.

**Resolution.** Add both to the retirement commit's docstring list, alongside the two already
recorded. The 4D record should not read as a complete inventory.

### F6 — LOW — `check_proof_integrity.py` is now vacuous and untested

**Evidence.** `blocked_paths` derives from `group_readiness().blockers`, which is zero since
chunk 19, so the problem loop cannot execute. The output is honest ("0 problems over **0
blocked files**"), but the per-step battery lists it as a live gate at every step. There is no
`tests/unit/test_check_proof_integrity.py`.

**Resolution.** Either drop it from the per-step battery (its job was done during preparation
and it did it — it caught six proof nodes), or keep it and say in the battery that a 0/0 reading
is expected and means "nothing left to check", not "checked and clean". A small test file
proving it fires on a constructed blocked row would be worth the twenty minutes.

### F7 — LOW — Stated limits of the checker machinery, for the Phase 5 auditor's record

Not defects; ceilings that the acceptance packet should not be read as exceeding.

1. `group_readiness` clears on the disposition *label*. "All six groups READY" means 185
   hand-authored labels say the files are handled, not that anyone measured it. One label was
   wrong (F2).
2. `surface_hits` misses transitive breakage (F1).
3. 89 proof entries name a file rather than a node; vacuity is undetectable. The per-node
   accounting that carries the real weight lives in prose on the rows.
4. `data_hits` matches literal basenames only; computed filenames and globs are missed.

### F8 — LOW — Dead back-compat alias

`src/sysml_codegen/generation/preservation.py:167` defines
`should_regenerate_stencil_from_graph = should_regenerate_stencil` "for backward compatibility
during transition". Its only references are the package's own re-exports
(`generation/__init__.py:38, 80`). No caller. It should retire with the transition it names.

---

## Verdict

**FINDINGS.** Phase 5 assembly **may start** — F1 and F2 do not block assembling a candidate
with the legacy stack present-but-unreachable, and every property that state depends on is
green and independently re-measured here.

But **F1 and F2 must be resolved before the acceptance packet claims the retirement is
mechanical**, because that claim is the headline decision the owner is being asked to rule on.
As it stands, an operator executing the runbook literally would end each of steps 1, 2 and 4
with a red suite and no instruction saying what to do about it. The preparation behind the
runbook is genuine and thorough; the runbook is the thin part.

On the question the brief actually asked — did Phase 4 repeat the original run's
self-certification in subtler form — **no.** Twelve recorded measurements reproduced to the
digit, the hardest problem in the phase (the duals) was measured, found false, and escalated
with its cost attached rather than smoothed into a rename, and no measured claim I sampled had
been carried forward without re-measurement. The over-claim in F1 is a documentation gap in one
section, not a pattern of unverified assertion.

---

## What I did not verify

The Phase 5 auditor inherits this list. It is what a certification with honest limits looks
like.

- **I executed no retirement step.** F1 and F2 are simulations of *parts* of steps 1 and 4 in a
  scratch worktree (fixtures + capture script for step 1; `legacy_route.py` for step 4). I did
  not simulate the production-module deletions of step 1, nor steps 2 and 3 at all. The true
  post-step suite state is unmeasured, and **may be worse than F1/F2 report** — I sampled the
  cheap deletions, not the expensive ones.
- **I did not re-verify 267 of the 298 ledger rows.** I read ~31 in depth. For the rest I relied
  on the checker's mechanical passes (`paths`, `surface`, `groups`, `replacements`, proof
  integrity), whose ceilings are stated in F7. In particular I did **not** independently confirm
  the responsibility statement of most `retire-with-owner` rows by reading both the retiring
  and the replacing test.
- **Chunk 19's node accounting is unverified.** "432 nodes across the 35 files: 166 / 254 / 12,
  of which 63 retire per-node and 191 keep collecting" — I did not recount these. They are
  post-retirement predictions and cannot be measured without executing the retirement.
- **Six of the eight dual dry-run probes.** I re-ran L-034 (codegen) and L-036 `facts`
  (agentic). L-033's three, L-037's three, and the `profile`/`result`/`preflight` arms are
  unverified beyond the recorded notes.
- **I read `reference/00`, `reference/27`, `CLAUDE.md`, `overview.md` and
  `verification-matrix.md` for code-reference accuracy and banner content, not claim-by-claim
  for every prose assertion.** The five false claims 4D says it corrected were not each
  re-derived; I verified the two that are mechanically checkable (the deleted
  `signature_extractor` references, and `collect_uncovered_params`' real home in
  `resolution/uncovered_params.py`).
- **The eleven banner-only documents' bodies.** The 4D record already states these were not
  re-read line by line. Neither did I.
- **The agentic-mbse suite was not run in full.** I ran only the L-036 probe's consumer set (450
  nodes) in the paired worktree.
- **Real TEAx execution beyond the collected lane.** The execution lane's 53 nodes pass in this
  environment; I did not exercise the SimKit-hosted acceptance path separately, and
  `tests/execution` raises an environment-dependent collection error outside the primary
  worktree.
- **Performance/scale measurements.** Out of Phase 4's scope; untouched.
- **The `_CONSTRAINT_LOGGER`, `GrandfatheredSnapshotError` and `build_pipeline_context`
  re-export items** carried under "Also in this phase, already prepared" were not verified
  beyond confirming G0 removed the `cli` half.
