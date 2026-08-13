# Verification: Coverage Report and TEAx Policy (CONSTRAINT-SEMANTICS Item 3)

**Stage:** implement · **Completed:** 2026-08-13
**Repos:** codegen `/home/reid/1cfe/sysml-codegen-item7-rebuild` branch `item7-rebuild`;
TEAx `/home/reid/1cfe/teax` branch `constraint-semantics-item3` (off `main` `fa0e06a`).
**Nothing is pushed. TEAx `main` was never committed to.**

---

## Headline

All eight phases complete. Both suites green. The red window opened at Phase 3 with 62 tests,
never grew, and closed at Phase 6 with zero.

| gate | result |
|---|---|
| codegen full licensed suite (all markers) | **2047 passed, 34 skipped, 1 known pre-existing failure** |
| codegen license-skip lines | **0** |
| TEAx full suite | **311 passed, 0 failed** (baseline at `fa0e06a`: green; mid-item: 30 failed) |
| red window | opened 62, closed **0** |
| codegen ruff / mypy | 138 / 55 — **baseline, zero new** |
| TEAx ruff / mypy | 322 / 119 — **down from 325 / 133** |
| `git diff --check` both repos | clean |
| companion `agentic-mbse` | `5088b41`, `status --porcelain` empty — **unchanged from the Phase 0 value** |
| baseline byte churn | **zero** |

**The one failure is pre-existing and not mine.**
`tests/execution/test_fusion_tea_real_teax.py::test_the_lane_runs_the_real_simkit` fails
whenever the whole `-m execution` set runs in one process — a sibling module imports the
in-repo stub runner, whose fake `simkit` would shadow the installed one. **Reproduced at the
parent commit `826adf0` with the identical assertion**, and it passes when run alone
(verified both, twice). Not absorbed, not counted, not fixed here.

---

## The red window (PD6)

Opened when Phase 3 bumped `RUNTIME_CONTRACT_VERSION`; enumerated in `red-window.txt`.

| file | tests |
|---|---|
| `test_c19_nested_occurrence_teax.py` | 17 |
| `test_fusion_tea_mutation_teax.py` | 20 |
| `test_constraint_verdicts_exact_route.py` | 14 |
| `test_fusion_tea_real_teax.py` | 11 |
| **total** | **62** |

**All 62 carried one signature**, which is B5 holding for real rather than in principle:

```
simkit.evaluation.package_load.SealVerificationError: seal violation: recorded
runtime_contract_version '2.0.0' is not in the accepted runtime-contract versions ['1.0.0']
```

Not one failed any other way. Checked at the Phase 4 and Phase 5 gates: the set was
**byte-identical** to the Phase 3 list both times, and everything outside it stayed green.
Closed in Phase 6.

---

## Phase 0 — probes, and the ledger written first

- **Companion baseline taken as a value:** `agentic-mbse` `5088b41`, clean. Re-checked at every
  phase gate and at the end: unchanged.
- **B3 holds.** `catf_mfe_d5`, `constraint_domain_plain_forms`, `constraint_domain_satisfy`, and
  `constraint_domain_satisfy_calc_def` each project a non-`None` catalog with non-empty
  `usage_records` and zero `eligible` rows. D5's trigger is readable from the catalog for exactly
  the models the zero-input branch exists to serve. **No stop.**
- **D9 reachability: 0 hits in 105 usage records** across the 57 fixture directories that
  elaborate standalone. The `@inapplicable:` marker appears in five fixtures; four are negative
  fixtures that refuse elaboration already, and in the fifth the marker sits on a `non_reaching`
  record. **D9's refusal breaks nothing that exists.**
- **`expected-coverage.md` committed before any coverage code existed** — 13 accounts derived
  from `.sysml` source against D3's bucket table, each citing the file and line it counted. No
  entry is transcribed from a catalog dump or a generated report.
- The fusion open check resolved from source: `hif_plant.sysml:223` is a `//` comment, not a
  second declaration. One authored usage.

---

## The expected-account ledger — 13 entries, all reproduced

`coverage_account()` reproduces **every** hand-written entry exactly
(`tests/unit/test_coverage_ledger_agreement.py`, which *parses* the ledger's index block rather
than transcribing it, so artifact and test cannot drift apart).

| fixture | account (authored / applicable / assessed / unassessed / inapplicable / reasons / state) | headline |
|---|---|---|
| `fusion_tea` | 1 / 1 / 1 / 0 / 0 / `{}` / complete | `full_satisfaction` |
| `gate_a_d5` | 1 / 1 / 1 / 0 / 0 / `{}` / complete | `full_satisfaction` |
| `constraint_multi_instance` | 1 / 1 / 1 / 0 / 0 / `{}` / complete | `full_satisfaction` (entry count **3**) |
| `constraint_def_owned_redefining` | 1 / 1 / 1 / 0 / 0 / `{}` / complete | `full_satisfaction` |
| `constraint_domain_inapplicable` | 2 / 1 / 1 / 0 / 1 / `{}` / complete | `full_satisfaction` |
| **`catf_mfe_d5`** | **65 / 0 / 0 / 0 / 0 / `{}` / none** | **`not_assessed`** |
| `constraint_domain_plain_forms` | 2 / 0 / 0 / 0 / 0 / `{}` / none | `not_assessed` |
| `constraint_domain_satisfy` | 2 / 0 / 0 / 0 / 0 / `{}` / none | `not_assessed` |
| `constraint_coverage_all_inapplicable` | 1 / 0 / 0 / 0 / **1** / `{}` / none | `not_assessed` |
| `constraint_domain_detached_owner` | 2 / 2 / 1 / 1 / 0 / `{owner_has_no_occurrences: 1}` / partial | `partial_coverage` |
| `constraint_non_numerical` | 2 / 2 / 1 / 1 / 0 / `{non_numerical: 1}` / partial | `partial_coverage` |
| `constraint_coverage_zero_eligible` | 1 / 1 / 0 / 1 / 0 / `{owner_has_no_occurrences: 1}` / partial | `partial_coverage` |
| `constraint_coverage_violation_partial` | 2 / 2 / 1 / 1 / 0 / `{owner_has_no_occurrences: 1}` / partial | `violation` |

**B1 is discharged.** No triage was needed: Item 2's enumeration and dispositions are correct
for every shape in the corpus. `catf_mfe_d5`'s 65 was re-measured by the two documented greps
(`assert constraint` = 0, `constraint def` = 0, bare `constraint` declarations = 65).

---

## Fixtures — the PD4 survey cut five to three

| design's required shape | outcome |
|---|---|
| asserted-with-zero-eligible | **authored** `constraint_coverage_zero_eligible` |
| all-inapplicable | **authored** `constraint_coverage_all_inapplicable` |
| violation-plus-partial | **authored** `constraint_coverage_violation_partial` |
| eligible-plus-inapplicable (refusal) | **authored** `constraint_coverage_eligible_inapplicable` |
| mixed-partial | **reused** `constraint_domain_detached_owner` |
| descriptive-only | **reused** `catf_mfe_d5`, unedited |

Four expectation files added to Item 2's population oracle. Two authoring facts worth the next
reader's time: the `@inapplicable:` marker is dropped by the parser inside an inline-predicate
constraint body (so both marked fixtures use the definition-typed form), and the oracle's source
scan counts marker *tokens anywhere in the file*, so prose must not quote the token.

---

## Aggregator churn — 8 fixtures gained one, and zero baselines moved

A before/after sweep over all 108 fixture directories: **8 gained an aggregator, none lost one,
none newly erroring.** Every one is a constraint-bearing model with zero eligible entries —
precisely the population D5 widened to:

`catf_mfe_d5` (65 usages), `constraint_domain_plain_forms`, `constraint_domain_satisfy`,
`constraint_domain_satisfy_calc_def`, and the four new `constraint_coverage_*` fixtures.

**None of the eight has a committed baseline**, so `tests/fixtures/baseline_outputs/*` did not
move a byte and constraint-free fixtures are byte-identical (LC-E12). There was no third cause of
churn because there was no churn. The two known stale-baseline classes (`deep_cross_scope`,
`plant_values`) were not touched.

---

## The six states, pinned twice

`tests/execution/test_constraint_coverage_matrix.py` — 11 tests, all green. Each state runs the
whole chain: model → elaborate → project → generate → seal → TEAx's own loader → execute →
`project()` onto the canonical vocabulary → policy disposition. Nothing re-implements the
precedence rule or the token map.

| state | fixture | report headline | canonical | disposition |
|---|---|---|---|---|
| 1 violation | `constraint_coverage_violation_partial` | `violation` | `violated` | `reject` |
| 2 indeterminate | (precedence matrix, `test_report_precedence.py`) | `indeterminate` | `indeterminate` | `keep-for-boundary` |
| 3 full satisfaction | `gate_a_d5` | `full_satisfaction` | `satisfied` | `feed-strategy` |
| 4 partial coverage | `constraint_domain_detached_owner` | `partial_coverage` | `partial_coverage` | `keep-for-boundary` |
| 5 not assessed | `constraint_domain_plain_forms`, `constraint_coverage_all_inapplicable` | `not_assessed` | `not_assessed` | `keep-for-boundary` |
| 6 report absent | `sample_model` | *(no report channel, no evidence schema)* | *(no headline key)* | `unconstrained` |

Also pinned there: `catf_mfe_d5` is no longer silent; D4's two `not_assessed` models stay
distinguishable by `inapplicable_gate_count` (0 vs 1); a `violation` carries its coverage all the
way into `assessment_json` and that record is JSON-serializable; and invariant 3 as a property
across the matrix — `full_satisfaction` implies nothing unassessed **and** at least one gate ran,
and no other state could have claimed it.

The two-tier asymmetry (DR-12) is pinned deliberately in two places: `assessed_gate_count = 1`
beside `assessed_entry_count = 3` on a real `constraint_multi_instance` package, and 1-beside-40
over the rendered aggregator.

---

## Refusals — four, all fail-before-mutate

`cli/__init__.py::_preflight_coverage_account`, at step 1.9: after the plan is built, before
`_clear_output_directory`. Verified at implementation that the only thing between the earlier
preflight block and this call is `ensure_package_tree_is_link_free`, which inspects and raises
and writes nothing. Both end-to-end negative tests assert the output tree is empty afterwards.

1. account disagrees with its catalog · 2. aggregator disagrees with the usage rows (both
directions) · 3. an untaught reason token · 4. D9's contradiction.

The recomputation is a real check, not a tautology, and proving that took choosing the
perturbation carefully: moving `assessed_gate_count` is caught by the account's own arithmetic
identities *before* any comparison happens and would have proved the wrong guard.
`authored_usage_total` sits outside those identities, so a wrong value there can only be caught by
reading the catalog.

D9's message, read by hand:
> `constraint_coverage_eligible_inapplicable::Live::live_but_marked (fa74a348-…) is marked
> inapplicable but produced 1 executable entries: … Remove the marker, or stop asserting the gate.`

---

## Versions

| constant | before | after |
|---|---|---|
| `RUNTIME_CONTRACT_VERSION` | `1.0.0` | **`2.0.0`** |
| `CATALOG_SCHEMA_VERSION` | `3.0.0` | `3.0.0` — **unmoved** |
| `TRUSTED_VERIFIER_SHA256` | — | **unmoved** |
| TEAx `ACCEPTED_RUNTIME_CONTRACT_VERSIONS` | `{"1.0.0"}` | **`{"2.0.0"}`** (replaced) |
| TEAx `ACCEPTED_CATALOG_SCHEMA_VERSIONS` | `{"2.0.0"}` | **`{"3.0.0"}`** (replaced) |
| TEAx `EVIDENCE_SCHEMA_VERSION` | `v1` | **`v2`** — invariant 50's carrier |

---

## PD5 — what the probe found, and what it corrected

**The design's fallback does not work, and that is why replace was the only coherent option.**
Extending the vendored sets instead of replacing them was costed as trading "refuse before
reading any report" for "refuse at the projection seam". Measured: it buys nothing. The old
packages emit the retired token `all_satisfied`, and 28 of the 30 mid-item TEAx failures were
`UnknownHeadlineToken`, not `SealVerificationError`. The suite is red either way. Owner ruled
replace stands.

### All five fixture packages regenerated

| package | source of record | notes |
|---|---|---|
| `constraint_free` | own `models/` | `handwritten/` was a stencil, not hand-filled |
| `excluded_only` | own `models/` | same; regenerated as `excl_only` to match its declared name |
| `zero_channel` | own `models/` | same |
| `sealed_package` | **adopted `tests/fixtures/wi014_toy`** | see below |
| `f1_arithmetic` | **new `models/toy_plant.sysml`** | see below |

**`sealed_package` needed no new authoring.** It had no `.sysml` anywhere. Per the owner's
cheaper-path-first instruction, the codegen corpus was checked before authoring: `wi014_toy`
(`toy_library.sysml` + `toy_plant.sysml`) *is* the model — identical channel names
(`toy_plant__demo_plant__area_calc__area`, `…__cost_calc__cost`), identical entry attributes, and
the same single `affordable` constraint. Adopted verbatim into `sealed_package/models` and
regenerated. Its `handwritten/` tree also turned out to be a stencil. The design's half-day
estimate was not spent.

**`f1_arithmetic` needed more than the pin refresh, and the extra is surfaced not absorbed.**
Pins were refreshed as decided, old → new:

| pin | old | new |
|---|---|---|
| `SYSML_SHA` | `512786c7dfab44fba7a0185d09e845b7494c702d` | `cb7b95c6ef6a887a59eae25353496d4e7a2619ac` |
| `AGENTIC_SHA` | `4ed2a0728ea49298666415cd389d9a6173a81a3e` | `5088b417c9e5453271291d46cd5fb23fc0579b1e` |
| `LOCK_SHA256` | `b457136b857974c655094b86496dc88809b2dc405146340aa5f02ebb8a284c05` | `6429f5d89b7a931ee9bcb21ec530085a5e7a9e76056dd9a57bd0cd24f521276a` |
| `agentic-mbse` | `0.1.0` | `0.1.2` |
| `Pydantic` | `2.12.5` | `2.13.4` |

The generation environment was reconstructed (two detached git worktrees plus a fresh venv) and
the preflight **passed**. The body then failed:

```
ModuleNotFoundError: No module named 'sysml_codegen.analysis.constraint_lowering'
```

`_build_context` calls `analysis.constraint_lowering` and `analysis.parameter_groups` — **both
deleted by the codegen cutover recovery (2026-08-12)**. The script cannot run at any current
revision, so the premise behind decision 2 (that refreshing the pins is sufficient) is false.

Applying the same principle the owner set for `sealed_package` — regenerate from a model, never
hand-patch — the three predicates were authored as `models/toy_plant.sysml` and the script was
**deleted** rather than kept as something that cannot run. `GENERATION.md` records the new route,
why it changed, and every identity that moved. **The result is byte-reproducible**: regenerating
from the model at the end of the item produced the identical executable fingerprint
`0cd8912baae8267e48437fd8a308eaf9944fe7f5c15fadbaf85d4c54be7cb17b`, so the fixture's provenance
is now a model plus a released generator rather than a bespoke script and a pinned environment.

> **For the owner:** this is a correction to decision 2's premise, not a silent extension of it.
> The alternative was hand-patching, which was rejected outright.

### Pre-existing drift surfaced by regeneration — recorded, not owned by Item 3

Regenerating at HEAD necessarily carries fa0e06a-to-HEAD codegen drift. **None of this is an
Item 3 change**; Item 3 touched no entry-point key and no constraint id. Annotated at every site:

| what | before | after |
|---|---|---|
| entry-point keys | `toy_plant__Toy_Plant__plant_length` | `toy_plant__demo_plant__plant_length` |
| f1 entry keys | `toy_plant__Toy_Plant__division_a` | `toy_plant__fixture__division_a` |
| f1 constraint ids | `f1_division_check` | `toy_plant__fixture__f1_division_check__b973058cd670a967` |
| f1 module order | declaration order | the projection's (`f3, f1, f2`) |
| `constraint_free` key | `constraint_free_plant__Free_Plant__width_design` | `constraint_free_plant__freePlant__width_design` |

Cause of the key move: a `DESIGN_ATTRIBUTE` keys by the supplying attribute's **display path**
(ADR-001), and that path now names the part *usage* rather than its def. TEAx tests pinning the
old keys were updated in the same commit with the same annotation.

### One behavioural change in a regenerated fixture, and it is the item working

`excluded_only` now reads **`partial_coverage`** where it read `not_assessed`. Its one asserted
gate is excluded as `non_numerical`, and an asserted gate the profile refused stays in the
denominator as an unassessed one: 1 / 1 / 0 / 1 / 0 / `{non_numerical: 1}` / partial. The old
reading conflated "one gate, refused by the profile" with "no applicable gate at all" — the two
zero-input branches collapsing into one, which is exactly what this item exists to separate.

---

## Deviations from the plan, with reasons

1. **A fourth seam, where D5 named three.** `project.py::_typed_module_order` gated the
   aggregator's *ordering* entry on `executable_constraints` — the old rule in a second place.
   Widening only the mint made the two inventories disagree and projection refused by name
   (`SI_EDGE_DANGLING`), which is the fail-closed check doing its job. Both now read
   `constraint_usages`.
2. **`generate_teax_module`'s aggregator arm now refuses.** It had the catalog but not the
   account; deriving there would be a second derivation of a producer fact (invariant 5), and an
   optional `coverage=None` with a fallback is the shim this epic's bar rejects. The arm was
   already dead in production — the CLI renders through the plan. It refuses and names the route.
3. **Three new fixtures, not five** (PD4 survey).
4. **`coverage_state` is a property, not a field**, derived from the counts, so the state and the
   counts cannot disagree by construction.
5. **`f1_arithmetic`'s script deleted** — see PD5 above.
6. **Two Item 2 tests inverted rather than deleted.** `test_a_usage_only_package_ships_no_
   constraint_machinery` became `…ships_the_machinery_and_a_zero_input_report`, asserting against
   the same three artifacts. Item 2's own docstring said Item 3 would supersede it. Two hand-built
   catalogs carried a concrete entry with no usage row — a shape no projection produces — and
   gained one.
7. **Phase 0's probe file kept as a durable test** rather than scratch: both claims are properties
   worth pinning, and a scratch file that answers a question once leaves nothing behind.

## Bugs found and fixed in this item's own work

- **Frozen coverage could not be serialized.** `ModelEvidence` deep-freezes the report tree
  (invariant 41), so `coverage` arrives as a `MappingProxyType`, and `json` refuses one. The policy
  now thaws *its copy* on the way into `assessment_json`; the evidence copy stays frozen and
  unshared. Caught by 16 TEAx failures, not by a review.

---

## Completion criteria

**sysml-codegen** — all met.
- [x] Every report carries an account derived by `coverage_account()` from the sealed catalog,
      identities enforced at construction (producer dataclass **and** generated validator).
- [x] Five headline tokens; `full_satisfaction` requires `unassessed_gate_count == 0 and
      assessed_gate_count > 0`.
- [x] A `REPORT_AGGREGATOR` exists iff the catalog has usage rows; its channel is an exit point
      (asserted through the real `_build_exit_points` with membership narrowed to nothing, so the
      pin is structural rather than incidental capture-everything); constraint-free byte-identical.
- [x] Four named refusals, all fail-before-mutate.
- [x] `RUNTIME_CONTRACT_VERSION = "2.0.0"`; `CATALOG_SCHEMA_VERSION` still `3.0.0`;
      `TRUSTED_VERIFIER_SHA256` unmoved; `has_executable_content` deleted.
- [x] The four `all_satisfied` sites assert coverage claims from the Phase 0 ledger, not from a run.

**teax** — all met.
- [x] Split vocabularies (`ConstraintStatus` / `HeadlineResponse`); all three former bare
      subscripts fail closed via `UnknownHeadlineToken`; `partial_coverage` in both dispatch
      tables with `keep-for-boundary` default and the fingerprint-bearing opt-in.
- [x] `ships_constraint_report` is the single consumer authority; `_report_declared_in_spec`
      deleted; `expects_constraint_report` required at **15** test sites (PD6's count was exact).
- [x] Vendored sets replaced; evidence `v2`; coverage in `assessment_json` and on `CaseView`.
- [x] All five committed fixture packages regenerated and loading.

**Spanning both** — all met.
- [x] Six states pinned in both vocabularies, each by a test no other state satisfies.
- [x] Reopening a store across the item raises `IncompatibleStore`, carried by
      `evidence_schema_version`.
- [x] Both full suites green, ruff/mypy zero-new in both, `git diff --check` clean in both,
      companion untouched.

---

## Open, and deliberately not done here

- **Filed for close, not performed** (as the plan directs): Appendix C's vacuous-gate cell wants
  "…and at least one gate remains" (design-F2); the epic's scope-4 wording wants the contract's
  phrasing (design-F3); the companion's authoring-time advisory for the eligible+inapplicable
  combination (D9's follow-on).
- **The pre-existing `test_the_lane_runs_the_real_simkit` ordering artifact.** Reproduced at the
  parent commit; needs an owner, not this item.
- **The two known stale-baseline classes** (`deep_cross_scope`, `plant_values`) — pre-existing,
  untouched, still need an owner.
- **Nothing is pushed.** Publication order when it happens is codegen first, TEAx second (D8
  step 4). TEAx `main` is still at `fa0e06a`.
