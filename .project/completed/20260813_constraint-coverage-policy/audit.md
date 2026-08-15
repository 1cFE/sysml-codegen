# Audit: Coverage Report and TEAx Policy (CONSTRAINT-SEMANTICS Item 3)

**Verdict:** Certify-with-residuals
**Audited:** 2026-08-13
**Branch:** codegen `item7-rebuild` · TEAx `constraint-semantics-item3`
**Commit:** codegen `cb19011` · TEAx `e0c7e48` (two off `fa0e06a`) · companion `5088b41` untouched

---

## The Point

A design search is only viable if it can tell a candidate that passed its physics gates from a
candidate nobody checked. Before this item it could not. A generated package reported
`all_satisfied` whenever nothing that happened to arrive had failed — two of nine gates assessed
read the same as nine of nine. A constraint-bearing model with sixty-five authored, unassessed
checks emitted no report at all, and TEAx read that silence as `unconstrained`: the same label a
genuinely constraint-free model gets.

The obligation is owner-graded at its root:

> **[OWNER-VERBATIM]** (2026-08-12) "when we started this whole cleanup, it was while defining a
> policy around how to use constraints to enforce things like physics in a way that make our
> overall 'design search' viable"

and the rule that follows is **[INHERITED]**: no report and no study label may claim more coverage
than was assessed. Item 1 fixed what each state means; Item 2 made the catalog own the complete
authored-usage domain. This item builds the consumer — a report that states its coverage, a
vocabulary that can say "partial", and a study policy that keeps a partially-covered candidate out
of the search's steering loop.

## Summary

The item delivers what it claims, and the load-bearing claims reproduce independently. I re-ran
both suites from scratch and hit the implementer's numbers exactly (codegen 2047 passed / 34
skipped / 1 known pre-existing failure, zero license-skip lines; TEAx 311 / 0), reproduced both
regenerated-fixture byte-reproducibility claims by regenerating from source and comparing
executable fingerprints, and hand-derived a ledger account from `.sysml` source to confirm B1's
mitigation is real rather than transcribed.

The residuals are one shape, not many: **four new refusal and opt-in paths are implemented
correctly and pinned by no test.** I verified each mechanism by direct probe, so these are gaps in
proof rather than defects — but three of them are named spec success criteria, and one of those is
marked `[x]` in `verification.md` on the strength of a test that predates the item and varies a
different field. That combination is what keeps this from a clean Certify.

The three judgment calls the brief asked for all resolve in the implementer's favour, and the
`excluded_only` semantic change is not a widening — it is the owner-ratified LC-E12 amendment
landing.

## Product Judgment

**Is this the right piece of work?** Yes. The item attacks the defect at the layer that owns it:
coverage becomes a *derived* fact about the model, computed once from the sealed catalog by a total
function over Item 2's closed vocabularies, and every consumer reads it rather than reconstructing
it. Two consumer-side re-derivations were *deleted* in the process (`_report_declared_in_spec`, and
the runtime report-vs-catalog check DR-7 proposed), and none was added. That direction — the
producer states a fact once — is the one the epic exists to establish.

**Product-lens ledger gate: DISPOSED.** Every entry in `product-lens.md` across all five stages
(spec, design, design-review, design rev-2, audit) is DISPOSED; no `BLOCK` stands anywhere in the
ledger, and no epic-level block is referenced. The audit-stage lens filed four findings, all
DISPOSE-grade, carried below as A-4, A-5, A-6 and a can't-find note.

**Structural smells.** Two fired and both are resolved here rather than left sitting green:

- **Smell 1 (two representations manually synchronized)** fires on the vendored cross-repo
  constants — codegen's `RUNTIME_CONTRACT_VERSION` / `CATALOG_SCHEMA_VERSION` against TEAx's
  `ACCEPTED_*` sets. **Resolved:** the no-import boundary between the repos is a standing design
  constraint, and the item handles the sync the safe way — the accepted sets were *replaced*, not
  extended, so a pre-item package fails at seal verification before any report is read, and an
  unmapped token refuses by name at all three former bare subscripts (verified by probe below).
  Manual sync with a fail-closed check on both sides is the correct shape here, not a smell left
  standing.
- **Smell 6 (a baseline preserving behaviour that contradicts the product's reason)** fires
  narrowly, as A-5: one parametrized case in a TEAx test went vacuous when regeneration reordered
  the modules. **Resolved as a residual**, not a blocker — the property it covered is still covered
  once by its sibling case, and the reorder is annotated at the site.

Smells 3, 4 and 5 did not fire. The item moves *against* smell 5 deliberately: `all_satisfied` was
renamed rather than redefined, and back-compatible acceptance of old packages was refused, so a
stale reader breaks by name instead of silently misreading a strengthened claim.

Nothing owner-graded is contradicted. Certify is permitted on the lens gate.

---

## Findings

### A-1 — The runtime fail-closed path is implemented and pinned by nothing · **Medium**

`UnknownHeadlineToken` (`teax/packages/teax-simkit/simkit/evaluation/evidence.py:38`) is raised at
three seams: `canonical_headline` (`evidence.py:87`) and `_disposition_for` over both dispatch
tables (`study/policy.py:57`). **No test in either repository references it.** A repo-wide grep
returns only the four definition/raise sites and one production import; the codegen matrix test
calls `canonical_headline` and `_disposition_for` only on tokens that succeed.

Spec success criterion — "Unknown or unmapped report and runtime headline tokens fail closed with a
named error — no fallthrough to a satisfied or unconstrained reading, no unnormalized `KeyError`" —
is met on the report side only (`tests/unit/test_report_precedence.py:135`,
`test_the_headline_literal_refuses_the_retired_token`, via the pydantic `Literal`). Design
Validation Approach item 9 asks for both sides; the runtime side was not built.

**Verified by probe, so this is unproven and not broken.** Direct calls confirm all three seams
refuse by name, and that the retired token is refused on the old-package path:

```
REFUSED canonical_headline   'all_satisfied' → UnknownHeadlineToken
REFUSED canonical_headline   'bogus'         → UnknownHeadlineToken
REFUSED _HEADLINE_DISPOSITION    'all_satisfied' → UnknownHeadlineToken
REFUSED _DISPOSITION_BY_HEADLINE 'all_satisfied' → UnknownHeadlineToken
partial_coverage present in both tables: keep-for-boundary / partial_coverage
```

**What should change:** three test cases in TEAx — one per seam — asserting `UnknownHeadlineToken`
on `all_satisfied` and on an invented token. This is B5's entire mitigation; leaving it untested
means a future refactor that reinstates a bare subscript or a `.get(..., default)` goes green.

### A-2 — Invariant 41 over the nested coverage block is unproven · **Medium**

Spec success criterion, `[INFERRED]` (review L3-3a): "The new nested coverage block is proven
unmutable from downstream code, to the same standard invariant 41 sets for the rest of the report."
Design Validation Approach item 10 names the test: "mutating the nested coverage block through
evidence raises."

**No such test exists.** The closest is
`teax/…/simkit/tests/evaluation/test_constraint_evidence_durability.py:215`, which does
`dict(evidence.report["coverage"])` — that implies a mapping proxy but asserts nothing about
mutability. `verification.md`'s completion lists do not claim this criterion either way.

Verified by probe: `ModelEvidence._freeze` does deep-freeze the block, and mutation raises
`TypeError` at both the top level and inside `unassessed_reasons`. Mechanism sound, proof absent.

**What should change:** one test attempting to write `evidence.report["coverage"]["…"]` and its
nested histogram, asserting `TypeError`.

### A-3 — Invariant 50's carrier is claimed `[x]` but pinned by a pre-existing test that varies a different field · **Medium**

`verification.md:351` records `[x] Reopening a store across the item raises IncompatibleStore,
carried by evidence_schema_version`. The only `IncompatibleStore` test is
`teax/…/simkit/tests/study/test_compatibility.py`, which is **untouched by this item**
(`git diff fa0e06a..HEAD` on that path is empty) and varies `strategy_config`, not
`evidence_schema_version`.

The design anticipated exactly this and asked for the opposite (Validation Approach item 11): "The
test varies that field specifically, not the model-contract fingerprint" — because "one that varied
only the model contract could pass today and silently stop proving anything." The test that exists
is that test.

Verified by probe: `evidence_schema_version` *is* a bound `Compatibility` field, and reopening a
`v1` store with a `v2` definition raises `IncompatibleStore`. The invariant holds; the claim that a
test proves it does not.

**What should change:** either add the field-specific test the design named, or downgrade the
`verification.md` claim to what the evidence supports. The overclaim is the more serious half — a
`[x]` on an unbuilt test is what makes a later reader stop looking.

### A-4 — `indeterminate` is never pinned end to end, and never against a partial account · **Low**

`tests/execution/test_constraint_coverage_matrix.py` is titled "All six states, end to end", but
`SIX_STATES` (`:36-42`) carries five rows and none is `indeterminate` — two `not_assessed` variants
occupy the fifth slot. At unit tier, `tests/unit/test_report_precedence.py:55` pins
`(["indeterminate", "satisfied"], COMPLETE, "indeterminate")` only. So the contract-ordered case
*indeterminate outranks partial coverage* is untested at every tier.

The state is not unpinned overall: the report token is pinned over the real rendered aggregator, and
its canonical counterpart is pinned 1:1 in `teax/…/test_projection.py::test_headline_normalization`
along with all five tokens. So the spec criterion is met in the letter ("pinned by a test that no
other state satisfies"); what is missing is the precedence interaction the item newly created.

No behaviour defect: the emitted `run` checks statuses before consulting the account, so the arm is
correct as written. **What should change:** add `(["indeterminate"], PARTIAL, "indeterminate")` to
the precedence table, and one execution-lane row.

### A-5 — A regenerated fixture left one parametrized case asserting over an empty tuple · **Low**

`teax/…/simkit/tests/evaluation/test_f1_arithmetic_normalization.py:202`. The
`test_later_failure_keeps_earlier_work_internal_without_aggregate` parametrization has two cases;
regenerating `f1_arithmetic` from the authored model moved execution order to `f3, f1, f2`, so the
`nested_division` case — whose failed channel is now the *first* module — had its
`earlier_channels` tuple emptied to `()`. The loop at `:219` now has no iterations, and the case no
longer proves anything about earlier evidence surviving a later failure.

The property is still covered once, by the sibling `zero_negative_power` case, and the reorder is
annotated honestly at `:189-190`. This is a strength regression, not a hole.

**What should change:** re-point the case at a later-executing module so both cases carry earlier
channels again.

### A-6 — Four doc sites still teach the rule this item retired · **Low**

Each is factual drift in text a future reader will treat as current:

1. `teax/…/simkit/evaluation/projection.py:44-47` — `project()`'s docstring still says
   `expects_report` is derived by the study layer "from `load_model_contract(...).concrete_entries`"
   and that "the evaluator's spec-derived default agrees." Both halves are now false: D7 moved the
   study layer to `ships_constraint_report` over `usage_records`, and deleted the spec-derived
   default outright. This is the most consequential of the four — it describes a deleted mechanism
   at the seam the item rebuilt.
2. `teax/…/simkit/study/policy.py` — `DispositionPolicy`'s class docstring names the canonical
   vocabulary as `satisfied|violated|indeterminate|not_assessed`, omitting `partial_coverage`, which
   the class now dispatches on twelve lines above.
3. `teax/…/simkit/tests/evaluation/fixtures/excluded_only/models/excl_library.sysml` — the
   `constraint def 'Flag Set'` doc comment states the package's headline is `not_assessed`. The
   package it generates emits `partial_coverage`, correctly.
4. `teax/…/simkit/tests/evaluation/test_constraint_evidence_durability.py:175` — section header
   "INV-B — excluded-only → exact not_assessed surface", above a test correctly named for and
   asserting `partial_coverage`.

**What should change:** correct all four. Verifiable from the files, no rerun needed.

---

## The four judgment calls

### `f1_arithmetic`'s deleted generation script — sound, and better than the plan it replaced

The design's decision 2 assumed refreshing the script's environment pins would be sufficient. That
premise is genuinely false: `generate_fixture.py` called
`sysml_codegen.analysis.constraint_lowering` and `analysis.parameter_groups`, both deleted by the
cutover recovery on 2026-08-12. The script cannot run at any current codegen revision, so keeping it
would have meant committing a reproduction route that does not reproduce.

The replacement is the stronger artifact. I regenerated the package from `models/toy_plant.sysml`
through the ordinary public route and got the identical executable fingerprint:

```
regen  0cd8912baae8267e48437fd8a308eaf9944fe7f5c15fadbaf85d4c54be7cb17b
commit 0cd8912baae8267e48437fd8a308eaf9944fe7f5c15fadbaf85d4c54be7cb17b   MATCH
```

The fixture's provenance moved from "a bespoke script plus a pinned environment" to "a model plus a
released generator" — the same claim every other package in the tree makes. That removes a special
exemption rather than creating one. `GENERATION.md` records the route, the reason, and every
identity that moved. **Correct on the merits; the post-hoc ratification was warranted.**

Same check on the adopted `sealed_package` model: regenerating from the `wi014_toy` sources produces
`ca18d4caa6ed52fb556a409218858577170f8baec92a522a864cab036559140b`, byte-identical to the committed
package. The adoption claim holds — that model really is that package.

### `excluded_only` `not_assessed` → `partial_coverage` — mandated, not a widening

LC-E12, as amended by Item 1 and **owner-ratified 2026-08-12**, is explicit: "zero eligible entries
under an asserted usage is partial coverage, not the not-assessed surface." LC-E10 carries the same
correction for the trigger. The fixture has exactly one `assert constraint flag_ok` with a boolean
predicate the profile excludes as `non_numerical` — an asserted, unmarked gate the profile refused,
which is D3 row 4: in the denominator, unassessed. The baked account reads
`1 / 1 / 0 / 1 / 0 / {non_numerical: 1} / partial`.

The old reading conflated "one gate, refused by the profile" with "no applicable gate at all" — the
two zero-input branches collapsing into one, which is the specific confusion this item exists to
separate. **The new reading is the contract's, and it is the item working.** The fixture's own doc
comment and one test header still teach the old rule; that is A-6, a documentation defect, not a
semantic one.

### `Free_Plant` → `freePlant` drift annotations — complete and honest

A repo-wide grep across TEAx for `Free_Plant` and `Toy_Plant` returns exactly two hits, and both are
*explanations* of the move rather than residue: `f1_arithmetic/GENERATION.md:59` and
`simkit/tests/evaluation/conftest.py:27`. Every changed site carries the same annotation naming the
cause (a `DESIGN_ATTRIBUTE` keys by the supplying attribute's display path, ADR-001, and that path
now names the part *usage*), the direction, and the disclaimer that it is pre-existing
`fa0e06a`-to-HEAD drift surfaced by regeneration rather than an Item 3 change. That disclaimer is
accurate — Item 3's diff touches no entry-point key and no constraint id. **Complete and honest.**

### `test_the_lane_runs_the_real_simkit` — genuinely pre-existing and out of scope

Reproduced and diagnosed independently rather than taken on the implementer's word:

- The test **passes alone** (1 passed) and `tests/execution` as a directory is **78/78 green**.
- It fails only when the whole `-m execution` set is collected over `tests/`, because collecting
  `tests/runtime/` imports the in-repo stub runner, whose fake `simkit` would shadow the installed
  one. The assertion at `:157` is precisely a guard against that shadowing.
- `git diff 826adf0..cb19011 -- tests/runtime/` is **empty**, and the diff to
  `test_fusion_tea_real_teax.py` touches neither `stub_owner` nor the import guard.

The failure mechanism is collection order in a sibling directory Item 3 never touched. **Genuinely
pre-existing; correctly not absorbed.**

---

## Probe evidence

| # | probe | result |
|---|---|---|
| 1 | Six-state matrix exists and passes; report token and canonical token asserted independently | **PASS with residual** — `test_constraint_coverage_matrix.py` runs the whole chain (elaborate → project → generate → seal → TEAx loader → execute → `project()` → policy) and asserts headline, `coverage_state`, canonical token and disposition separately, re-implementing neither the precedence rule nor the token map. `indeterminate` is pinned at unit + projection tier only → **A-4** |
| 2 | The headline cannot lie: partial assessment cannot read `full_satisfaction`; violation + non-full coverage reaches the durable case record | **PASS** — `test_full_satisfaction_is_unclaimable_when_anything_was_unassessed` asserts it as a property across every matrix fixture, including the negative half ("could have claimed it and did not"). `test_violation_states_its_coverage_all_the_way_into_the_case_record` drives a real `violation` package through `DispositionPolicy` and asserts `assessment["coverage"]["unassessed_gate_count"] == 1`, the catalog fingerprint, and `json.dumps`-ability |
| 3 | Coverage derives from the sealed catalog; forced divergence fails by name | **PASS** — `_preflight_coverage_account` (`cli/__init__.py`, step 1.9, before `_clear_output_directory`) recomputes from the graph's catalog. `tests/conformance/test_coverage_preflight.py` perturbs `authored_usage_total` (chosen *outside* the arithmetic identities, so the guard under test is the catalog comparison and not the validator), asserts the named refusal through the real generation route, and asserts the output tree is empty afterwards |
| 4 | Unknown report token and unknown canonical token both refuse; retired `all_satisfied` refuses on an old package | **CODE PASS / TEST GAP** — all three runtime seams and the report-side `Literal` refuse by name under direct probe; only the report side has a test → **A-1** |
| 5 | Excluded-only emits the report as `partial_coverage`; constraint-free stays report-free → `unconstrained` | **PASS** — baked account verified in the committed package; `test_the_sixth_state_is_the_absence_of_a_report` asserts no `constraint_types.py`, no `constraint_report` channel, and `ships_constraint_report` False. Semantic change judged correct against LC-E10/E12 above |
| 6 | D9's eligible + `@inapplicable` contradiction refuses by name | **PASS** — two tests; the refusal names the usage QN, the declaration id, the entry count and the cure, and fires before any write |
| 7 | Five TEAx packages load; `sealed_package`'s adopted model generates it; `f1_arithmetic` byte-reproducible | **PASS** — all five at `runtime_contract_version 2.0.0`; both regeneration fingerprints MATCH (above) |
| 8 | Suites and counters | **PASS, all exact** — see table below |
| 9 | B1 spot-check: a ledger account hand-derived from `.sysml`, independently | **PASS** — `constraint_domain_detached_owner` source has two `assert constraint`: `vacuous_gate` on `part def Detached` (nothing types it → zero occurrences) and `reached_gate` on `Live` (instantiated as `part the_live`). By D3's table that is 2 / 2 / 1 / 1 / 0 / `{owner_has_no_occurrences: 1}` / partial — exactly the ledger entry. The accounting is source-derived, not transcribed |
| 10 | Invariant 41 deep-freeze over the nested block | **CODE PASS / TEST GAP** — mutation raises `TypeError` at both levels under probe → **A-2** |
| 11 | Invariant 50 carrier | **CODE PASS / TEST GAP** — reopening a `v1` store with `v2` raises `IncompatibleStore` under probe → **A-3** |
| 12 | `partial_coverage` opt-in: default keep-for-boundary, config line flips to feed-strategy, both carry the headline | **CODE PASS / TEST GAP** — probe: `default → keep-for-boundary`, `explicit-keep → keep-for-boundary`, `opt-in → feed-strategy`, all three carrying `headline=partial_coverage`. No test exercises the opt-in → noted under **A-1**'s family |

### Counters, reproduced from scratch

| gate | claimed | measured | |
|---|---|---|---|
| codegen suite, all markers | 2047 passed / 34 skipped / 1 known failure | 1970 + 77 = **2047 passed**, **34 skipped**, **1 failed** | ✅ exact |
| codegen license-skip lines | 0 | **0** | ✅ |
| TEAx full suite | 311 passed / 0 failed | **311 passed, 0 failed**, exit 0 | ✅ exact |
| codegen ruff (`src tests`) | 138 | **138** | ✅ |
| codegen mypy (`src/`) | 55 | **55** | ✅ |
| TEAx ruff (`simkit`) | 322 (from 325) | **322** | ✅ |
| TEAx mypy (`simkit`) | 119 (from 133) | **119** | ✅ |
| baseline byte churn | zero | `git diff 826adf0..cb19011 -- tests/fixtures/baseline_outputs/` **empty** | ✅ |
| both repos clean | clean | `git status --porcelain` empty in both | ✅ |
| companion untouched | `5088b41`, clean | **`5088b41`**, clean | ✅ |
| TEAx `main` untouched | `fa0e06a` | **`fa0e06a`**; checkout on `constraint-semantics-item3` | ✅ |

The codegen figure needed the marker override — `pyproject.toml` sets `addopts = -m "not execution"`,
so a bare `pytest tests/` reads 1970/34 and silently omits the execution lane. The claimed 2047 is
the union, and it is right.

---

### Plan completion

All eight phases complete; zero unchecked boxes in `plan.md`. The seven recorded deviations are all
sound, and two are improvements on the design:

- **Deviation 1 (a fourth seam).** `project.py::_typed_module_order` gated the aggregator's
  *ordering* entry on `executable_constraints` — D5's old rule in a place the design did not
  enumerate. Widening only the mint made the two inventories disagree and projection refused by name
  (`SI_EDGE_DANGLING`). Both now read `constraint_usages` (`project.py:1028-1033`). The fail-closed
  check finding the design's own gap is the system working.
- **Deviation 2 (`generate_teax_module`'s aggregator arm refuses).** Verified at
  `generation/modules.py:434-440`: rather than accept an optional `coverage=None` with a fallback,
  the arm raises and names the route that has the account. That is the shim this epic's bar rejects,
  correctly declined.
- **Deviation 4 (`coverage_state` is a property, not a field)** on `CoverageAccountData` — the state
  and the counts cannot disagree by construction, which is strictly better than validating them
  against each other. The generated pydantic model still carries it as a field *and* validates the
  agreement, because it receives baked constants rather than deriving them.

### Spec conformance

Twelve success criteria. Nine verified met and marked; three left unchecked:

| criterion | verdict |
|---|---|
| Six states, report + canonical each independently pinned | **met**, residual A-4 |
| Coverage survives a higher-precedence headline into the case record | **met** |
| Full satisfaction impossible under partial assessment | **met** |
| Descriptive-only → zero-input not-assessed; zero usages → report-free → `unconstrained` | **met** |
| Excluded-only → zero-input aggregator reading partial coverage, pinned separately | **met** |
| Coverage derived one-directionally; divergence fails, proven by a negative test | **met** |
| Partial coverage defaults keep-for-boundary; feed-strategy only by explicit config; both persist | **met in code**, opt-in path untested (A-1 family) — marked, with the residual named |
| `[INFERRED]` nested coverage block proven unmutable | **not met** — A-2, left unchecked |
| Unknown/unmapped tokens fail closed on both sides | **not met** — A-1, left unchecked |
| `[INHERITED: invariant 50]` durable-store transition proven, not assumed | **not met** — A-3, left unchecked |
| Cross-repo tests, both suites, ruff/mypy zero-new, `git diff --check` clean, exact counts recorded | **met**, all reproduced |
| Four `all_satisfied` assertions moved to coverage claims | **met** |

The last one deserves its own note, because it carried the owner's `[NEED]` sequencing instruction.
`test_fusion_tea_real_teax.py:244-259` is the whole-dump equality on the real-TEAx route, and its
new expected `coverage` block is hand-written with a source citation in the diff itself
(`ife_plant.sysml:155` is the one usage; `fusion_cycle.sysml:29` is a `constraint def`;
`hif_plant.sysml:223` is a comment, not a second declaration). The three bare asserts each gained a
ledger-cited account rather than a token swap. **The expectations were captured from the settled
semantics, not reverse-engineered from a run** — the instruction is discharged, visibly.

**Non-goals respected.** The companion is byte-identical at `5088b41`. No catalog field was added
(`CATALOG_SCHEMA_VERSION` still `3.0.0`). Item 2's disposition vocabulary, usage-tier schema and
totality gate are untouched — `KNOWN_REASONS` is a consumer-side pin that *refuses* an untaught
token rather than adding one. The pre-existing nested-model invariant-41 violation was not absorbed.

### Design conformance

Implementation follows the design. Spot-checks against the load-bearing decisions:

- **D3's bucket table is the function's literal structure**, as the design instructed, not scattered
  conditionals — `generation/coverage.py::coverage_account` walks the four rows in order with a
  comment per row, and the table is reproduced in the module docstring.
- **D9's refusal** is a single guarded function called first in the loop, so it fires before any
  bucketing.
- **D5's rule stayed in one home.** `ships_constraint_machinery` kept its name and location; only
  its body changed, exactly as Item 2's A4 cure requires and as its own docstring anticipated.
  `has_executable_content` is deleted, not deprecated.
- **D2's two tiers** are distinct in the field names (`assessed_gate_count` usage-tier,
  `assessed_entry_count` occurrence-tier), and the asymmetry is pinned deliberately in two places so
  a later reader cannot "reconcile" it away.
- **D3's histogram keys are derived, not listed** — a key appears iff a gate landed on it.
- **D7's single consumer authority** landed: `ships_constraint_report` over `usage_records`, and
  `_report_declared_in_spec` deleted with `expects_constraint_report` promoted to a required
  argument at every call site.

One design item was not built: Validation Approach items 9, 10 and 11 (A-1, A-2, A-3). Those are the
three unchecked criteria; the deviation is silent in `verification.md`, which is what makes A-3 an
overclaim rather than a known gap.

### Code integrity

No slop or failure-honesty findings. Specifically checked and clean:

- **No silent fallbacks.** Every new failure path raises and names the cure. There is no
  `try/except Exception`, no `coverage=None` default, and no back-compat shim — the aggregator arm
  that could not derive the account refuses rather than defaulting (deviation 2), and
  `ObjectivePolicy` reads `config.partial_coverage` by attribute rather than `getattr` fallback, so a
  renamed field is an `AttributeError` and not a silent reversion to the conservative default
  (`policy.py:186-190`, and the comment says so).
- **No god functions.** `_preflight_coverage_account` carries four refusals but they share one
  catalog read and one failure class, each with its own message and its own cure; the docstring
  states why they are one function. That is cohesion, not a mode switch.
- **No policy in utilities.** `coverage_account` is pure and license-free; the decision about *where*
  it runs lives at the CLI seam.
- **`_thawed` is the right direction.** The `MappingProxyType`/`json` collision was solved by thawing
  the *assessment's* copy on the way out, leaving the evidence copy frozen and unshared — the
  alternative (not freezing) would have broken invariant 41 to make serialization work.

---

## Certification

**Verdict: Certify-with-residuals.** The work is correct, the claims reproduce, and the product-lens
gate is DISPOSED with no standing block anywhere in the ledger. Six residuals (A-1..A-6) are carried
forward; none is a behaviour defect, and I verified each affected mechanism by direct probe rather
than inferring it from the absence of a failure.

**Recommended before close:** A-3's `verification.md` claim should be corrected regardless of
whether the test is written, because an unearned `[x]` is what stops the next reader looking. A-1
and A-2 are each a handful of test cases against paths the epic's whole fail-closed posture rests
on. A-4, A-5 and A-6 are cheap and can ride along.

**Marked:** all eight plan phases (already checked by the implementer, verified here); nine of twelve
spec success criteria; three left unchecked with the finding named beside each. The epic item
heading is **not** marked ✅ — three criteria are open.

**Not checked:**

- **The fusion/stellarator demo branches.** The `RUNTIME_CONTRACT_VERSION` bump refuses any other
  consumer of a sealed package. The design records these as local, pinned and not regenerated; I did
  not open them to confirm nothing there breaks.
- **The 34 skipped codegen tests.** Zero are license skips, which was the claim under test; I did not
  enumerate what the other skip reasons are or whether any should now run.
- **The two known stale-baseline classes** (`deep_cross_scope`, `plant_values`). Pre-existing,
  untouched by this item, and I did not attempt to resolve or re-diagnose them.
- **TEAx code paths outside the constraint/report/policy surface.** I read the diff and ran the full
  suite, but only audited the evaluation, study-policy, config, query and model-contract changes in
  depth.
- **The `expected-coverage.md` ledger beyond one entry.** I hand-derived
  `constraint_domain_detached_owner` from source to test whether the source-derivation discipline was
  real. The other twelve entries I verified only through
  `test_coverage_ledger_agreement.py`, which parses the ledger rather than transcribing it — a good
  test, but it proves agreement between artifact and code, not that either matches the `.sysml`.
- **Item 3's interaction with Items 5 and 6.** The design claims the account extends to CATF
  migration and calc-def gates without a report change; not exercised.
- **Publication.** Nothing is pushed; I did not verify the codegen-first landing order beyond
  confirming both trees are clean and TEAx `main` is still at `fa0e06a`.
- **The three unproven mechanisms (A-1, A-2, A-3) beyond a single direct probe each.** A probe is not
  a regression test.
