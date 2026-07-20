# Evidence: Lifecycle Remediation Item 1 — Occurrence and Demand Integrity

**Status:** Phases 0–6 complete. Candidate certified for the scope Item 1 owns.
**Candidate revision:** `28bc8b0fc22ba85cbed94febf0963bebf7cd600e`
**Item 0 RED predecessor:** `ecdc7285be1508c08e82830c93072306f40e6b34`
**Coordinated pins:** agentic-mbse `515e08bbcd70aa9d23212765161bd02b3e3d8f23`,
TEAx `d545701f575133350474108c96202a2ac5244462`
**Recorded:** 2026-07-19

Every claim below is supported by a recorded command output from this session. Claims
this item does **not** support are stated as such in
[Subset labels and what stays open](#subset-labels-and-what-stays-open).

---

## 1. Owner ruling on LOC (supersedes the production-growth gate)

**[OWNER-VERBATIM], 2026-07-19:** "honestly I do not give a fuck about LOC any more.
what a mistake that was. I just want you agents to strive for simpler code."

The epic's Simplification and Deletion Mandate was amended accordingly (epic commit
`a1435e1`): every numeric LOC gate, baseline, per-file cap, and LOC-deviation review is
retired epic-wide. Still binding, judged qualitatively: **deletion over shims**, and **no
collapsed intentional boundaries**.

Consequently the Stop #4 condition raised at the end of Phase 4 and the OD-R43 hard-gate
deviation are **dissolved by owner ruling**, and certification proceeded. Every LOC row
below and in the spec/design (Phase 4/5 union reruns, OD-R41–R44, OD-A13, and the Final
Completion Gate's "non-positive executable LOC" line) is **retired by owner ruling
2026-07-19 (epic commit a1435e1)** — recorded once, informationally, never as pass/fail.
The approved spec and design text is left unrewritten.

### Final metrics (informational only — not a gate)

Measured by the frozen counter `production_metrics.py`, SHA-256
`70fddc980bfd49cb46248fa4fcd2735d7879f118675b64f3bcb993217e4c4a0c` (unmodified since
Phase 0). Two readings, because the tool derives its union differently depending on
whether the candidate revision differs from the baseline:

| Union | Baseline | Candidate | Net |
|---|---:|---:|---:|
| Nine-file starting inventory (comparable to all prior reports) | 3,552 | 3,818 | **+266** |
| Automatic git-diff union at the candidate revision | 2,546 | 2,812 | **+266** |
| Design-units equivalent of the nine-file union (counter − 28) | 3,524 | 3,790 | +266 |

AST statements 1,907 → 2,064; branch points 644 → 683; raw lines 5,211 → 5,606.
Machine-readable output: `evidence/item1-candidate-metrics-ninefile.json` and
`evidence/item1-candidate-metrics.json`.

The design's Appendix A per-file numbers are in the design's own counting units; the
frozen counter reads the identical tree 28 lines higher. Both systems are reported; the
approved design numbers are not revised.

**Qualitative simplification actually delivered** (the standard that survives the
ruling): deleted `materialize_supplied_values` + its nested route `_demand`,
`collect_bare_actual_demand`, `RecordingOccurrenceIndex`, the route-counted loop, the
`synth[target.qn]` last-write-wins overwrite, the silent missing-source drop, the route
tuple plumbing, and both duplicated live/replay materialize-and-bucket blocks. No
wrapper, feature flag, compatibility alias, route adapter, or dead fallback remains.
`lower_constraints` complexity fell 34 → 19 (115 → 63 statements). The growth is the
cost of capability that did not previously exist: verified association, an all-or-nothing
prepared batch, a structured cycle error, and a four-record demand/resolution/provenance
model replacing a route-counted sweep that was cheaper because it was wrong.

---

## 2. Public licensed observations

Licensed environment loaded from `/home/reid/1cfe/agentic-mbse/.env` before every run.
`-rs` reported **no skip** for any required node.

| Node | Result |
|---|---|
| `test_r4_live_anonymous_association` | PASS |
| `test_r4_valid_replay_not_corrupt` | PASS |
| `test_r5_finite_first_cycle_is_atomic` | PASS |
| `test_r7_shared_target_dedup_grouping_counts` | PASS |
| `test_r7_multi_target_order_permutations` | PASS |
| `test_r7_constraint_only_provenance_after_resolution` | PASS |

Focused licensed selection (the five historical RED nodes): **5 passed, 0 skipped**.
Full acceptance file: **6 passed**.

### Observed behaviour against the recorded RED

| Defect | RED at `ecdc7285` | Candidate |
|---|---|---|
| R-4 live anonymous association | summary `3/2/0`, three owners queried | `1/1/0`, `part_occurrences == ["OccurrenceDemandAnonymous__Admitted"]` |
| R-4 valid replay | raised `FrozenOccurrenceIndexCorruptionError` for excluded owner `OccurrenceDemandAnonymous__Excluded` | replay graph and catalog equal the live ones |
| R-5 finite-first cycle | `DID NOT RAISE` | `CodeGenerationError` from `RecursiveContainmentError`, all five cause fields exact |
| R-7 shared target | `2/2/0` | `1/1/0`, grouped `calc_route_params`, default `17.0` |
| R-7 ordered targets | `6/6/0` | `3/3/0` |

R-5 exact cause fields: `requested_owner_qn` / `edge_owner_qn` / `edge_type_qn` =
`OccurrenceDemandCycle__Node`, `edge_feature_name` = `recursive`, `cycle_path` =
`("OccurrenceDemandCycle__Node", "OccurrenceDemandCycle__Node")`.

---

## 3. Generated TEAx execution (OD-A11)

`tests/execution/test_constraint_occurrence_demand_execution.py::test_sibling_literal_overrides_produce_distinct_values_and_verdicts`
plus the `test_multi_instance_expansion_n_modules_one_predicate` control:
**2 passed**.

Run through production generation and real teax-simkit:

- Generated input values: `OccurrenceOverride__plant__low__reading == 4.0`,
  `OccurrenceOverride__plant__high__reading == 6.0` — distinct, from sibling `:>>`
  overrides on one part def.
- Verdicts against `reading >= 5.0`: low `("violated", False)`, high
  `("satisfied", True)`.
- `constraint_report`: `assessed_count == 2`, `headline == "violation"`; the violated
  run completes rather than raising (INV-3), and the report is persisted with both
  statuses present.

**Environment note for a fresh auditor.** This lane cannot run under this repo's `uv run`
— teax-simkit imports `pandas`, which the codegen venv lacks, and the failure is a bare
`ModuleNotFoundError` that looks like a product defect but is not (the pre-existing
control fails identically). The working incantation is the agentic-mbse venv with the
repo `src` on `PYTHONPATH`:

```bash
set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a
TEAX_SIMKIT_PATH=../teax/packages/teax-simkit \
  PYTHONPATH=/home/reid/1cfe/sysml-codegen/src \
  /home/reid/1cfe/agentic-mbse/.venv/bin/python -m pytest -q -rs -o addopts= -m execution \
  tests/execution/test_constraint_occurrence_demand_execution.py \
  tests/execution/test_constraint_execution.py::test_multi_instance_expansion_n_modules_one_predicate
```

---

## 4. Repository gates

| Gate | Result |
|---|---|
| Full suite | **3,009 passed, 26 skipped, 16 deselected, 0 failed** |
| Focused normal | 63 passed |
| Focused optimized (`python -O`) | 63 passed |
| Affected regression union (16 files) | 162 passed |
| Unchanged absolute-reference controls | 2 passed |
| Mypy | 76 errors in 17 files — **equal to the Phase 0 baseline** |
| Ruff `check src/` | clean |
| Ruff `format --check src/` | 19 would reformat — **one fewer than the baseline's 20** |
| `pyproject.toml` / `uv.lock` diff vs predecessor | empty |
| Deletion absence check | no matches |

The absolute-reference controls
(`test_chamber_power_disambiguated_to_chamber_b`,
`test_quoted_owner_refs_reclassify_to_design_attribute`) pass unchanged, which is the
standing evidence that B2's exact-target-QN identity did not merge distinct targets.

Format check honesty: this repository carries pre-existing unformatted production files
(20 at the predecessor). Two files I touched became newly unformatted during
implementation and were formatted; `supplied_values.py` was unformatted at the
predecessor and is now formatted. Net one fewer. Fixtures and `baseline_outputs` were
never formatted — they are generator-owned bytes and byte-identity gates depend on them.

Deletion absence, run over `src tests docs`:

```
rg -n 'RecordingOccurrenceIndex|collect_bare_actual_demand|materialize_supplied_values|admit_qns|synth\[target\.qn\]'
-> no matches
```

---

## 5. Preservation

| Artifact | Value | Status |
|---|---|---|
| Acceptance file SHA-256 | `aea7c8219d716f4ca1ecb154ca6ed8a13e0c15b1184fdcfe2d92b556eacb624b` | unchanged since Phase 0 |
| Existing-fixture aggregate | `73ba5ca931c14f58df70a36f16fd8fe4ba6a724c806438b9722175f66f356b50` | equal to the predecessor tree |
| `baseline_outputs` aggregate | `0bbea88f5d7e0a6997ea09613d340d7eeeaa7511a6bdd691c4834c464021b34c` | equal to the predecessor tree |
| Snapshot format | v3 | unchanged |
| Executable profile | `executable-profile/v4` | unchanged |
| Package version | 0.1.0 | unchanged |
| `.claude/projects/` | untracked, never staged or modified | preserved |

`git status --short -- tests/fixtures` shows only the new untracked
`constraint_occurrence_demand/` tree. No tracked fixture or baseline byte changed.

### Phase 0 fixture-digest correction

Phase 0 recorded the existing-fixture aggregate as `fde9c5df...54bd5` and the
`baseline_outputs` aggregate as `921bbb6a...bf66`. **Neither value is reproducible**, and
the discrepancy is not fixture drift: running the recorded commands against the
predecessor tree at `ecdc7285` yields `73ba5ca9...f356b50` and `0bbea88f...4021b34c` —
byte-identical to the candidate. Phase 0 mis-recorded them, most likely by computing them
in a different working directory or against a different file set.

The corrected aggregates are reissued here. **The Phase 0 record is deliberately not
overwritten**, per orchestrator disposition — a future auditor should see both the wrong
original and this correction rather than a silently repaired history.

---

## 6. Recorded deviations

All are agent-grade, ratified by the orchestrator on the dates shown. None is
owner-settled; each is challengeable by re-deriving against the reasoning below.

1. **`predicate_source_key` on `PreparedConstraintUsage`** (accepted 2026-07-19). The
   record carries a seventh field beyond the design's six-field table. An admitted
   *anonymous inline* assert — exactly the R-4 fixture — reaches the referent-mapping arm
   of the predicate-source-key ladder, so leaving that ladder in `lower_constraints` would
   violate the design's own I10 ("lowering cannot rediscover"). Carrying the finished key
   satisfies I10 and moved the whole source-location policy out of lowering.

2. **`ResolvedDemand` has four fields, not five; `select_group_source` is a separate
   step** (accepted 2026-07-19, compelled by the confirmed defect in §7). `group_source`
   cannot live on the record, because the record is constructed before the caller knows
   whether the target survives the REQ-SVM-03 collision guard. Provenance selection is now
   a call-site decision — policy at the call site, mechanism in the utility.

3. **Nullable `source_location_mode` / `source_roots` on `prepare_constraint_usages`**
   (recorded 2026-07-19). Kept exactly as `lower_constraints` had them, so route-absence
   still fails at the same place with the same message. Requiring them would change
   behaviour for facts that legitimately have no route.

4. **`RedefinitionData` carries no source path** (recorded 2026-07-19). The design's
   provenance tier 3 ("one unique real source from the winning override/redefinition
   records") has no field to read. Implemented as the unique source file among captured
   design attributes belonging to that record's owner. Deterministic and derived only from
   real captured data, but an interpretation rather than the literal design text.

5. **`Mapping[Any, ...]` on the enrichment key type** (recorded 2026-07-19). The design
   specifies `Mapping[Union[Path, str], ...]`; `Mapping` is invariant in its key type, so
   that annotation makes mypy reject the live `dict[Path, ...]` caller outright. Annotated
   `Any` with the constraint stated in a comment; both key kinds normalize to `Path`
   immediately.

6. **Indirect-cycle fixture gap** (accepted as-is 2026-07-19; Phase 0 overlay bytes
   deliberately not modified). The plan's Phase 2 validation asks for an indirect cycle
   asserted with `OccurrenceDemandCycle__A` / `__B` QNs. **Those QNs exist nowhere in the
   fixture tree** — `cycle/model.sysml` models only the self-cycle
   (`part recursive : Node`). This is a plan-drafting discrepancy, not an implementation
   gap. Indirect detection is proven instead at unit level by
   `test_indirect_cycle_raises_structured_context`, asserting `cycle_path == ("A","B","A")`
   and the closing edge `(A, "b", B)`. Closing the line verbatim would require a new
   fixture and therefore new Phase 0 overlay bytes.

7. **Cycle edge-field orientation** (accepted 2026-07-19: the approved design wins over
   plan prose). The design fixes the fields as
   `(owning_definition_qn, feature_name, target_definition_qn)`. For the A/B case that
   yields `cycle_path == ("A","B","A")` with edge `(A, "b", B)`, which the plan's
   validation line loosely calls "the closing B-to-A edge". Implemented per the design's
   field definition and asserted with the observed values.

8. **`all_occurrences()` records recursive definitions in `blocked`** (recorded
   2026-07-19). The bulk best-effort dump treats a recursive containment the same way it
   already treats a non-finite multiplicity, rather than raising through the dump.
   `occurrences_of` itself still raises loud (INV-2).

---

## 7. Confirmed correctness defect found in review, and its fix

**Found by independent review after Phase 4; CONFIRMED and orchestrator-verified at the
source.**

`resolve_logical_demand` computed and validated grouping provenance for *every* numeric
result, while the REQ-SVM-03 collision guard that discards that value ran later in
`enrich_graph_design_attributes`. Failure mode: a target already covered by a real
captured design attribute, whose calc origins sit in two different `.sysml` files, raised
`calc-origin provenance is ambiguous` — where the deleted route correctly kept the real
value and skipped synthesis with a warning. Validating provenance for a value that is
definitely discarded is wrong.

**Fix.** `group_source` left `ResolvedDemand`; provenance selection became the public
`select_group_source(resolved, *, exact_real_sources)`, which the enrichment seam calls
only after the collision guard has confirmed the target really will be synthesized. The
load-bearing `assert resolved.group_source is not None` disappeared with the restructure
rather than being converted, since `select_group_source` returns a `Path` or raises — no
load-bearing assert remains.

**Pinned semantics preserved exactly:** a collision still counts as applied, still emits
exactly one REQ-SVM-03 warning, keeps the real value, and synthesizes nothing;
non-collision counts, INFO/warning bytes, and ordering are byte-identical.

**Regression test.**
`tests/unit/test_logical_demand_resolution.py::test_collision_covered_target_with_split_calc_sources_does_not_raise`
pins both halves: it first asserts that selecting provenance for that exact demand *does*
raise `calc-origin provenance is ambiguous`, then asserts the enrichment seam completes
without raising, keeps the real `99.0`, adds nothing under the second route's file, logs
one `already covers` warning, and reports `scanned 1 ... 1 literal applied`. Phase 0
overlay bytes were not touched.

**Auditor note, stated plainly:** this test could not be executed against the pre-fix code
to demonstrate RED, because it imports `select_group_source`, which did not exist then —
the stashed attempt errored at import rather than showing the raise. The first half of the
test is the standing substitute proof, and it is permanent rather than a one-off run.

---

## 8. Subset labels and what stays open

Item 1 closes what it observed and no more.

- **Same-checkout replay is regression-only and non-certifying.** Every replay assertion
  in this item rebuilds from a snapshot captured in the same checkout. It does **not**
  certify relocated-tree or full-tree generation. Item 5 retains relocated proof; Item 13
  retains composed-artifact proof. This is stated in the acceptance file's module
  docstring, in the test names, and here.
- **Item 2's producer/exact-QN resolver was not absorbed.** `_binding_target` and the
  materializer-local value ladder remain the only changed demand seams. No Item 2 resolver
  symbol or import appears in the diff, and no new target-equivalence rule was introduced.
- **R-8 (unmappable warning locations) remains open under Item 4.** The known predecessor
  behaviour — the warning-location projector can raise while rendering a NON_NUMERICAL
  warning and thereby mask a later BLOCK — is **not** closed here. Item 1 moved that
  preflight into preparation mechanically; warning bytes, order, and failure behaviour are
  unchanged, and no unmappable-warning test was added. Item 4 / register row 4 owns its
  total behaviour.
- **Item 5 (relocated whole-tree proof) and Item 13 (sealed-artifact proof) remain open**
  with their recorded ownership. Nothing here substitutes for them.
- **Warning-location totality, general producer/exact-QN resolution, and sealed-artifact
  proof were explicitly not attempted.** No scope-absorption stop was triggered.

### Bets, as they stood up

| Bet | Outcome |
|---|---|
| B1 ordered identity/location pairing is sufficient within one batch | **Held.** Distinguished deletion, duplication, reorder, and both field edits on two anonymous siblings whose identities are identical `(None, None)`. |
| B2 exact `_BindingTarget.qn` is complete Item 1 identity | **Held.** Distinct scopes reconciled semantically; the unchanged absolute-reference controls show no distinct targets merged. |
| B3 calc-route source is the grouping authority | **Held.** Adding an assertion over an existing calc input does not regroup it. |
| B4 constraint-only numeric provenance is deterministic | **Held**, via the four-tier ladder — with deviation 4 above on how tier 3 reads its source. |
| B5 a live occurrence query mutates nothing before returning | **Held.** Private staging plus batch atomicity proved by the later-owner-failure and cycle tests. |

---

## 9. Reproduction

```bash
git checkout 28bc8b0fc22ba85cbed94febf0963bebf7cd600e
uv sync --frozen
set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a

uv run --frozen pytest -q -rs tests/                 # 3009 passed, 26 skipped
uv run --frozen python -O -m pytest -q -rs \
  tests/conformance/test_constraint_occurrence_demand_acceptance.py \
  tests/unit/test_constraint_usage_preparation.py \
  tests/unit/test_logical_demand_resolution.py \
  tests/unit/test_part_instance_index.py \
  tests/unit/test_supplied_values.py                 # 63 passed
uv run --frozen mypy src/                            # 76 errors (baseline)
uv run --frozen ruff check src/                      # clean
```

TEAx execution uses the agentic-mbse venv incantation recorded in §3.
