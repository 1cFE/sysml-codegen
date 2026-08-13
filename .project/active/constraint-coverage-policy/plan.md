# Implementation Plan: Coverage Report and TEAx Policy

**Status:** Draft
**Created:** 2026-08-13
**Last Updated:** 2026-08-13
**Epic:** CONSTRAINT-SEMANTICS, Item 3
**Branch:** `item7-rebuild` (codegen worktree `/home/reid/1cfe/sysml-codegen-item7-rebuild`); TEAx work
on a branch off `main` `fa0e06a` in `/home/reid/1cfe/teax` — **TEAx `main` is never committed to**
(`[NEED]`, owner).

## Source Documents

- **Design:** `.project/active/constraint-coverage-policy/design.md` (rev 2, commit `dc397e7`) ←
  component detail, D1–D9, the bucket table, the token map, required invariants 1–11, the validation
  list, landing order. **Do not re-derive any of it here; open the design.**
- **Spec:** `.project/active/constraint-coverage-policy/spec.md` (success criteria, provenance,
  the Sequencing `[NEED]`)
- **Design review:** `.project/active/constraint-coverage-policy/design-review.md` (DR-1..DR-13, all
  resolved in rev 2)
- **Stage brief:** `.project/active/constraint-coverage-policy/briefs/plan.md`

## The Point

A design search is only viable if it can tell a candidate that passed its physics gates from a
candidate nobody checked. Today it cannot.

A generated package reports `all_satisfied` whenever nothing failed, whatever fraction of the
model's authored gates was actually assessed — the headline is computed from the statuses that
happened to arrive (`templates/report_aggregator.py.jinja2:44-58`). A constraint-bearing model with
nothing eligible emits no report at all (`elaboration/project.py:892`), and TEAx reads that silence
as `unconstrained` — the same label a genuinely constraint-free model gets. So `catf_mfe_d5`, with
65 authored checks and none assessed, is indistinguishable from a model with no checks.

The governing obligation is owner-graded at its root:

> **[OWNER-VERBATIM]** (2026-08-12) "when we started this whole cleanup, it was while defining a
> policy around how to use constraints to enforce things like physics in a way that make our overall
> 'design search' viable"

and the rule that follows is **[INHERITED]**: no report and no study label may claim more coverage
than was assessed.

Item 1 fixed what each state means. Item 2 made the embedded catalog own the complete authored-usage
domain. This item builds the consumer: a report that states its coverage from that catalog, a
vocabulary in both repos that can say "partial", and a study policy that keeps a partially-covered
candidate out of the search's steering loop. Item 5's disposition table and Item 6's calc-def gates
both enter through the account this item creates.

## Implementation Strategy

**Phasing rationale.** Four forces set the order.

1. **The owner's sequence is a hard rail.** Documentation corrections and *all* hand-written expected
   outputs land before the confirmation tests run, and expectations are never reverse-engineered from
   what the code does. So fixtures and their expected accounts are authored in Phases 0–1, from
   `.sysml` source and D3's bucket table, before a line of coverage code exists.
2. **De-risk the pure function first.** `coverage_account()` is license-free, has no generated-code
   dependency, and is where bet B1 (the catalog is a complete and correct enumeration) is either
   discharged or exposed. It is proved against the whole fixture corpus in Phase 2 — before any
   report shape, template, or version moves — which is the cheapest possible place to learn the
   accounting is wrong.
3. **The cross-repo checkout inversion (D8).** Publication order is codegen-first, but codegen's venv
   imports `simkit` from the TEAx *working tree*, so the local TEAx branch has to exist before
   codegen's execution lane can go green. That opens a deliberate red window at Phase 3 and closes it
   at Phase 6. It is a working-order inversion, not a bump: nothing is pushed until both trees are
   green.
4. **Small, gated steps inside the window.** Phases 3–5 run with a red execution lane, so each one
   gates on an *enumerated* red set that must not grow, plus a green everything-else.

**Critical path.**

```
P0 probes (B3, D9-reachability) + kept-failing characterization + fusion expected block
 → P1 fixture corpus + the expected-account ledger (hand-written from .sysml source)
 → P2 generation/coverage.py: bucket table, D9 refusal, KNOWN_REASONS pin   ← FIRST PROOF POINT
 → P3 report schema + precedence + baked constants + RUNTIME_CONTRACT_VERSION 2.0.0   ← red window OPENS
 → P4 report-required trigger (D5), zero-input aggregator, three seams, baselines
 → P5 sixth preflight + divergence refusals
 → P6 TEAx branch off fa0e06a: vocabulary, policy, config, one report authority, evidence v2   ← window CLOSES
 → P7 cross-repo green: matrix, parity, both suites, verification.md
```

**First proof point.** End of Phase 2: `coverage_account()` reproduces the hand-written ledger entry
for every constraint-bearing fixture in the corpus, including `catf_mfe_d5`'s
`authored_usage_total = 65, applicable_gate_total = 0` and `fusion_tea`'s complete account — with
zero change to any generated byte. If the accounting is wrong, it is wrong here, before the schema
bump, the templates, the trigger, or TEAx.

**Overall validation approach.** Every phase writes its tests first, names a gate that must be green
before the next phase starts, and states what is then known to work. The full licensed codegen suite
runs at the end of Phases 2, 5, and 7; the TEAx suite at the end of Phases 6 and 7; focused tests
every phase.

## What Does NOT Change

Check these at every phase gate. They are the fixed points the item is balanced on.

- **`CATALOG_SCHEMA_VERSION` stays `3.0.0`.** Verified this stage against
  `contracts/versions.py`: this item adds no catalog field and re-keys nothing, so Item 2's token
  stands and `tests/conformance/test_catalog_schema_version.py` keeps passing unchanged.
  `RUNTIME_CONTRACT_VERSION` is the only version that moves.
- **`TRUSTED_VERIFIER_SHA256` does not move.** `contracts/verify.py` reads the version out of the
  seal data and contains no version literal, so its bytes are unchanged by the bump.
- **Item 2's usage-tier schema.** No new catalog field, no renamed catalog field, no change to
  `DISPOSITION_REASONS`, `SOURCE_FORMS`, `ASSERTED_SOURCE_FORMS`, mint-time behaviour, or the
  totality gate. This item reads them; it does not author them.
- **`instance-graph/v3`** and the snapshot codec. Nothing in this item changes what the graph
  carries.
- **The frozen CATF twins.** `catf_mfe_model` and `catf_mfe_d5` are not edited; `catf_mfe_d5` stays
  byte-reversal-pinned and keeps its 65 usage carriers, 9 `eligible`.
- **Generated baselines outside the vocabulary change.** `tests/fixtures/baseline_outputs/*` holds
  only `registry_init.py` and `computation_graph.json`. Legitimate churn has exactly two causes:
  a fixture that *gains* an aggregator under D5's widened trigger, and a fixture whose channel set
  moves for that reason. **Constraint-free fixtures must stay byte-identical** (LC-E12) — that is the
  gate proving the trigger did not widen too far. The two known stale-baseline classes
  (`deep_cross_scope`, `plant_values`) are pre-existing; do not absorb them.
- **`agentic-mbse` is untouched.** Not an assumption — a check: `git -C /home/reid/1cfe/agentic-mbse
  status --porcelain` is empty at every phase gate, and `git -C /home/reid/1cfe/agentic-mbse log
  --oneline -1` is unchanged from the value recorded in Phase 0. If implementation finds a companion
  surface it needs, that is a surfacing event (D9's authoring advisory is *filed* for the companion,
  not built here).
- **`BLOCK`-halts-generation semantics**, requirement satisfaction execution, the pre-existing
  nested-model invariant-41 violation, CATF migration (Item 5), calc-def gates (Item 6).
- **TEAx `main`.** Never committed to. All TEAx work is on the branch off `fa0e06a`.

## Plan-Owned Decisions

The design left four things to the plan; a fifth is a finding this stage measured. Decided here so
the implementer does not reopen them.

**PD1 — The sixth preflight is one function, placed after the plan build and before the clear.**

`_preflight_coverage_account(graph, constraint_plan)` in `cli/__init__.py`, called immediately after
`build_constraint_generation_plan(...)` (`cli/__init__.py:~1190`) and before
`_clear_output_directory`. It carries all four checks the design names — account recomputation from
`graph.constraint_catalog` compared against the plan's, aggregator-iff-usage-rows, the
`KNOWN_REASONS`/`DISPOSITION_REASONS` vocabulary pin, and D9's refusal — each raising a distinctly
named `CodeGenerationError`. One function because they share the catalog read and the same failure
class; four messages because each has its own cure.

*Fail-before-mutate holds at that position*: verified this stage that the only thing between the
existing preflight block and the clear is `ensure_package_tree_is_link_free`
(`contracts/seal.py:48-57`), which inspects and raises — it writes nothing. The account itself is
computed once, inside `build_constraint_generation_plan`, onto a new
`ConstraintGenerationPlan.coverage` field (`generation/constraint_plan.py:17-23`), so the renderer
and the preflight read one value. D9's refusal and the vocabulary pin live inside
`coverage_account()` itself, so they fire at plan build — earlier still, and before any write either
way.

**PD2 — The hand-written expected accounts live in
`.project/active/constraint-coverage-policy/expected-coverage.md`.**

One entry per fixture: the account's seven fields, the expected headline, and *the source evidence
that produced it* — the `.sysml` file and line of each constraint usage, or the two greps for a
fixture too large to enumerate by eye. Committed **before** the test that asserts it is written. This
is the artifact the DR-6 instruction demands and the answer to the design's open item "where the
hand-written fusion coverage block is recorded before it is run."

**The expectation rule, stated once and enforced at every phase gate:** an expected account is
derived from what the *author wrote* — the fixture's SysML source read against D3's bucket table —
never transcribed from a catalog dump, a generated report, or Item 2's disposition table. A
transcription inherits exactly the error B1 names and falsifies nothing. Reading the catalog to
confirm *which usages a model declares* is a legitimate cross-check of the source reading; reading it
to obtain *the counts* is the shortcut this rule forbids.

**PD3 — `query.py` surface: two named fields on `CaseView`, no DB column, no migration.**

`CaseView` (`study/query.py:46-57`) gains `coverage: Mapping[str, Any] | None` and
`catalog_fingerprint: str | None`, populated in `_case_view` (`query.py:103-134`) from the already-
decoded `assessment` dict. `cases()` gains no new filter — filtering by coverage is not in this
item's scope. The `cases` table is untouched: `assessment_json` already carries whatever policy
writes into it, which is why D7's "coverage into durable case records" costs a policy copy and a
view field rather than a schema change.

**PD4 — Fixture policy: survey before authoring, and register the refusal fixture.**

The design lists five new fixtures. Some shapes may already exist —
`constraint_domain_detached_owner`, `constraint_domain_block_non_reaching`,
`constraint_domain_inapplicable*` (five of them), `constraint_non_numerical`, `catf_mfe_d5`. Phase 1
surveys those first and authors only what is genuinely missing; a reused fixture still gets a ledger
entry. New fixtures are named `constraint_coverage_*` so the corpus reads by purpose.

The eligible-plus-inapplicable fixture is a **refusal** fixture: generation is supposed to fail on
it. Any corpus-wide sweep that generates every fixture must expect the refusal rather than trip over
it — find those sweeps in Phase 1 and register it, following Item 2's refusal-list precedent
(`.project/active/constraint-catalog-totality/v2-refusal-list.txt`).

**PD5 — SURFACED: TEAx's five committed fixture packages are refused by D8's version replace.**

Measured this stage, read-only at `fa0e06a`. `simkit/tests/evaluation/fixtures/` holds five generated
packages — `constraint_free`, `excluded_only`, `sealed_package`, `zero_channel`, `f1_arithmetic` —
every one carrying `"catalog_schema_version": "2.0.0"` and `"runtime_contract_version": "1.0.0"`.
D8 has TEAx **replace** its vendored sets with `{"3.0.0"}` and `{"2.0.0"}`, so all five fail closed
at `package_load` and every test that loads one goes red. The design costed the replace decision and
did not cost this.

Regeneration is the intended route and it is **not free**: each package's `handwritten/` tree holds
hand-filled implementations (not stencils), the package contract seals the final on-disk bytes, and
`f1_arithmetic` regenerates through its own `generate_fixture.py` whose pins (`SYSML_SHA
512786c7…`, lockfile, environment fingerprint) are stale. Phase 6 opens with a probe on one package
before the other four are attempted.

**If the probe shows regeneration exceeds what remains of this item, the fallback — vendoring the
accepted sets as extended (`{"2.0.0","3.0.0"}`, `{"1.0.0","2.0.0"}`) rather than replaced — is an
owner-visible decision, not a quiet edit.** It weakens D8's "refuse before reading any report" to
"refuse at the projection seam by `UnknownHeadlineToken`", which is still fail-closed but is a
different promise than the design published. Surface it; do not take it silently.

**PD6 — The red window is gated by an enumerated set that may not grow.**

At the moment Phase 3 lands, run the full licensed suite once and write the exact list of failing
tests, with each failure's signature, into `verification.md` under "Red window". Phases 4 and 5 gate
on: everything outside that list green, and the list itself neither growing nor changing signature. A
new red test inside the window is a defect, not the window.

**Correction to carry (minor).** The design sizes D7's required-argument change at "fourteen
evaluation-layer test call sites". Measured at `fa0e06a`: 17 `PreparedEvaluator(`/`FileBackedEvaluator(`
constructions, of which one is production (`study/cli.py:43`) and one test site already passes the
flag — so **15 test sites** need it added. Mechanical either way; recount at implementation.

---

## Phase 0: Probes, Characterization, and the Fusion Expected Block

### Goal

Collapse the two cheap uncertainties the design named, pin today's lying behaviour as a kept-failing
test, and hand-write the one expected output that gates everything downstream — all before any
production code moves.

### Assumption Under Test

B3: a constraint-bearing model whose usages are *all* non-reaching still projects a non-`None`
`constraint_catalog`. Everything in D5 rests on it. And D9's reachability claim: no fixture in the
tree today carries an `eligible` usage with an `@inapplicable:` marker, so D9's refusal breaks no
existing model.

### Test Stencil (Write This First)

```python
# tests/unit/test_coverage_probes.py (NEW, scratch — folded into the real tests later)
def test_b3_non_reaching_only_model_still_projects_a_catalog(detached_owner_graph):
    """D5's trigger is unreadable if this is None."""
    assert detached_owner_graph.constraint_catalog is not None
    assert detached_owner_graph.constraint_catalog.usage_records          # non-empty
    assert not [r for r in ... if r.disposition_kind == "eligible"]       # nothing eligible

# tests/execution/test_constraint_coverage_characterization.py (NEW, kept-failing)
@pytest.mark.xfail(strict=True, reason="Item 3: the report can lie — partial assessment reads all_satisfied")
def test_partial_assessment_does_not_read_as_full_satisfaction(mixed_partial_package):
    assert mixed_partial_package.outputs[REPORT_CH].headline != "all_satisfied"

@pytest.mark.xfail(strict=True, reason="Item 3: an excluded-only model emits no report at all")
def test_excluded_only_model_ships_a_report(excluded_only_graph):
    assert any(m.module_kind is ModuleKind.REPORT_AGGREGATOR for m in excluded_only_graph.modules)
```

### Changes Required

**See `design.md` for:** B3 (Key Bets), D9 (the reachable shape), *Implementation Notes* "Probe B3
first", *Potential Risks* "D9 refuses a model that generates today".

- [x] Record the companion baseline: `git -C /home/reid/1cfe/agentic-mbse log --oneline -1` and a
      clean `status --porcelain`, written into `verification.md`. This is the untouched-companion
      check, taken as a value now so it can be compared later.
- [x] **Probe B3** on an existing non-reaching-only fixture (`constraint_domain_detached_owner` is
      the candidate). Record the answer in `verification.md`. *If `None`* → STOP and surface: D5's
      trigger has to move to the instance graph's `constraint_usages` domain and the design's D5
      needs revising, not working around.
- [x] **Probe D9 reachability**: confirm across the corpus that no usage record is both `eligible`
      and carries `inapplicability_reason`. The design verified the five
      `constraint_domain_inapplicable*` fixtures all sit on `Detached` parts; confirm corpus-wide, in
      one pass over projected catalogs. Record the count.
- [x] **Two kept-failing characterization tests**, exactly the two shapes the brief names: partial
      assessment reading `all_satisfied`, and the excluded-only model emitting no report. Both
      `xfail(strict=True)` so they fail loudly when they start passing. They flip in Phases 3 and 4.
- [x] **Hand-write the `test_fusion_tea_real_teax.py:244-259` expected coverage block** into
      `expected-coverage.md` (PD2), from the fixture's SysML source. Derived this stage and carried
      here as the starting entry, to be confirmed not re-derived from output:

      `tests/fixtures/fusion_tea` declares exactly one constraint usage —
      `assert constraint viability : 'Viability Threshold'` at
      `designs/generic_ife/ife_plant.sysml:155`. (`library/analyses/fusion_cycle.sysml:29` is a
      `constraint def`, a definition not a usage; the two other grep hits are prose inside doc
      comments.) It is asserted, not marked inapplicable, and it expands — the current test asserts
      one result. By D3's bucket table it is row 3:

      | field | value |
      |---|---|
      | `authored_usage_total` | 1 |
      | `applicable_gate_total` | 1 |
      | `assessed_gate_count` | 1 |
      | `unassessed_gate_count` | 0 |
      | `inapplicable_gate_count` | 0 |
      | `unassessed_reasons` | `{}` |
      | `coverage_state` | `"complete"` |

      with `headline = "full_satisfaction"` and `assessed_entry_count = 1`.

      **One open check, resolved from source:** `designs/hif_ife/hif_plant.sysml:223` comments that
      the viability constraint is *inherited* from the IFE plant. Read the test's model roots and
      that file: if the HIF design declares (rather than inherits) a second usage, the account is for
      two usages and the ledger entry changes before the test is touched.
- [x] Add the ledger entries for the three bare-assert sites'
      fixtures (`test_constraint_verdicts_exact_route.py:171, 416, 540`) the same way — read each
      one's fixture source, write the account, then the headline each site should assert.

### Validation

**Automated:**
- [ ] `/home/reid/1cfe/item7-rebuild-venv/bin/python -m pytest tests/unit/test_coverage_probes.py -q`
      → probes recorded (the B3 probe passes or STOPS the item).
- [ ] The two characterization tests **fail** — and fail for the stated reason, not an import error.
      Read the failure text.

**Manual:**
- [ ] `expected-coverage.md` exists, is committed, and every entry cites the `.sysml` file and line
      it was read from. No entry cites a catalog dump or a generated report.

**What We Know Works After This Phase:** the catalog is readable for the models D5's new trigger has
to serve; D9's refusal breaks nothing that exists; today's two defects are pinned by tests that will
tell us when they stop being defects; and the one expectation that must not be reverse-engineered is
written down before any code can influence it.

---

## Phase 1: The Fixture Corpus and the Expected-Account Ledger

### Goal

Every shape the validation list needs exists as a fixture, with a hand-written expected account, and
nothing about the fixtures depends on code this item has not written yet.

### Assumption Under Test

That the shapes are authorable at Item 2's HEAD — in particular that a fixture can be built whose
asserted gates are applicable and produce *zero* eligible entries (the `partial_coverage` zero-input
branch), and one with a violated gate beside an unassessed applicable gate. The fixture's
*dispositions* are observable today from the projected catalog, so a mis-shaped fixture is caught
here rather than in Phase 5 when it is load-bearing.

### Test Stencil (Write This First)

```python
# tests/unit/test_coverage_fixture_shapes.py (NEW)
@pytest.mark.parametrize("fixture,expected_kinds", COVERAGE_FIXTURE_SHAPES)
def test_fixture_produces_the_intended_dispositions(fixture, expected_kinds):
    """Shape check against Item 2's landed catalog — NOT a coverage assertion."""
    catalog = project_fixture(fixture).constraint_catalog
    assert Counter(r.disposition_kind for r in catalog.usage_records) == expected_kinds
```

### Changes Required

**See `design.md` for:** *Validation Approach* (the fixture list), D3's bucket table, D4, D9,
*Implementation Notes* (`catf_mfe_d5` is descriptive-only, not partial).

- [x] **Survey first (PD4).** For each of the design's five required shapes, check whether an
      existing fixture already carries it: `constraint_domain_detached_owner`,
      `constraint_domain_block_non_reaching`, the five `constraint_domain_inapplicable*`,
      `constraint_non_numerical`, `constraint_domain_plain_forms`, `catf_mfe_d5`. Record the mapping.
- [x] Author only the missing ones, as `constraint_coverage_*`:
      - [x] `…_zero_eligible` — applicable asserted gates, zero eligible entries → `partial_coverage`
      - [x] `…_all_inapplicable` — every asserted gate carries `@inapplicable:` → D4's `not_assessed`
            with positive `inapplicable_gate_count`
      - [x] `…_partial_mixed` — some gates assessed and passing, some unassessed → `partial_coverage`
      - [x] `…_violation_partial` — one violated gate plus ≥1 unassessed applicable gate →
            `violation` **and** a non-full account
      - [x] `…_eligible_inapplicable` — the D9 refusal fixture (generation must fail on it)
- [x] Register the refusal fixture wherever corpus sweeps enumerate fixtures (PD4), so a sweep
      expects the refusal instead of tripping on it.
- [x] Keep fixtures **minimal**. An over-built fixture has burned this epic before: Item 13's cell 18
      turned out to be a fixture-shape defect, not a product defect. One shape per fixture.
- [x] Write the ledger entry for every fixture above — including reused ones — into
      `expected-coverage.md`, from source, per PD2's expectation rule. `catf_mfe_d5`'s entry uses the
      two documented greps; re-run and record them: `assert constraint` = **0**, bare `constraint`
      usage declarations = **65**, `constraint def` = **0** (measured this stage), which puts all 65
      in bucket 1 and fixes every field: `authored_usage_total = 65`, `applicable_gate_total = 0`,
      all other counts `0`, `unassessed_reasons = {}`, `coverage_state = "none"`, headline
      `not_assessed`.

### Validation

**Automated:**
- [x] Fixture-shape tests pass — each new fixture produces the dispositions its ledger entry assumes.
- [x] Full licensed suite still green (no production code has moved; a red here means a fixture
      broke a sweep).

**Manual:**
- [x] Ledger reviewed entry by entry against the fixture source. Any entry whose evidence is "the
      catalog says so" is rewritten from source or deleted.
- [x] Companion untouched check.

**What We Know Works After This Phase:** every state in the six-state matrix has a model that
produces it, the expected answer for each is written down and source-derived, and none of it can have
been influenced by the code this item is about to write.

---

## Phase 2: `generation/coverage.py` — The Bucket Table, D9, and the Vocabulary Pin

### Goal

The derivation exists, is pure, and reproduces the whole ledger. Nothing generated moves yet.

### Assumption Under Test

B1 — that Item 2's `usage_records` is a complete and correct enumeration with a correct disposition
and `occurrence_count` on each. This phase is where a systematic misreading shows up as a ledger
mismatch, at the cheapest possible cost. Also: that D3's four rows really are exhaustive and mutually
exclusive over the closed vocabularies.

### Test Stencil (Write This First)

```python
# tests/unit/test_coverage_account.py (NEW)
def test_every_bucket_row_over_hand_built_records():
    """D3's table, row by row, over records built here — no fixture, no generation."""
    account = coverage_account(catalog_of(
        record(form="plain_usage",       kind="excluded",     reason="unassessed_form"),   # row 1
        record(form="definition_typed",  kind="excluded",     reason="non_numerical",
               inapplicability_reason="vacuous"),                                          # row 2
        record(form="inline",            kind="eligible",     reason="admitted"),          # row 3
        record(form="named_usage_reference", kind="non_reaching", reason="owner_absent"),  # row 4
    ))
    assert account.authored_usage_total == 4
    assert account.applicable_gate_total == 2 and account.assessed_gate_count == 1
    assert account.unassessed_reasons == {"owner_absent": 1}
    assert account.coverage_state == "partial"

@pytest.mark.parametrize("reason", sorted(all_reasons(DISPOSITION_REASONS) - {"admitted"}))
def test_each_reason_token_buckets_and_the_identities_hold(reason): ...

def test_eligible_plus_inapplicable_is_refused_by_name():
    with pytest.raises(CodeGenerationError, match="marked inapplicable but produced"):
        coverage_account(catalog_of(record(form="inline", kind="eligible",
                                           reason="admitted", inapplicability_reason="vacuous")))

def test_an_unknown_reason_refuses_with_the_ruling_instruction(monkeypatch):
    """KNOWN_REASONS pin: adding a reason to Item 2 must force a coverage ruling."""
    with pytest.raises(CodeGenerationError, match="has not been taught reason"):
        assert_reason_vocabulary_is_known({"eligible": {"admitted"}, "excluded": {"brand_new"}})

# tests/unit/test_coverage_ledger_agreement.py (NEW) — the first proof point
@pytest.mark.parametrize("fixture,expected", LEDGER)     # loaded from expected-coverage.md
def test_derived_account_equals_the_hand_written_account(fixture, expected):
    assert coverage_account(project_fixture(fixture).constraint_catalog) == expected
```

### Changes Required

**See `design.md` for:** D3 in full (the bucket table, the two predicates, why the rows sit where they
do), D9's ruling and message, *Component Overview* (`generation/coverage.py`), *Required Invariants*
2, 5, 6, 9.

- [x] **`src/sysml_codegen/generation/coverage.py`** (NEW): `coverage_account(catalog)`, the frozen
      `KNOWN_REASONS` set, and the vocabulary-pin check. Implement the table **as the function's
      literal structure** — a row predicate per row — not as scattered conditionals (design,
      *Implementation Notes*). The two predicates read `source_form in ASSERTED_SOURCE_FORMS` and
      `inapplicability_reason is not None`, using the **catalog** spelling
      (`resolution/models.py:519`), not the graph's `inapplicability`.
- [x] D9's refusal raises here, naming usage QN, `declaration_id`, and the entry count.
- [x] The account is returned as a plain dataclass/mapping at this phase — the pydantic
      `CoverageAccount` with validators is the *generated* type and lands in Phase 3. Keep the
      arithmetic identities asserted here too, so a bad account cannot leave the function.
- [x] `KNOWN_REASONS` documents, per token, whether it sits inside or outside the feasibility
      denominator — that is the ruling a future reason has to make.

### Validation

**Automated:**
- [x] Unit tests: every bucket row, every one of the nine non-`admitted` reason tokens
      (5 `excluded` + 4 `non_reaching`, `elaboration/graph.py:259-278`), the identities, D9's
      refusal, the vocabulary-pin refusal.
- [x] **Ledger agreement over the whole corpus** — the first proof point.
- [x] Full licensed codegen suite green, **zero license-skip lines**. Nothing generated moved, so a
      regression here is real.
- [x] `ruff check src/`, `mypy src/` → zero new.

**Manual:**
- [x] Read the diff of `coverage.py` against D3's table side by side. Four rows, four branches.
- [x] Any ledger mismatch is triaged before proceeding: **fixture wrong, ledger wrong, or B1 false**.
      If B1 is false — the catalog's enumeration or a disposition is wrong — STOP and surface; that
      is an Item 2 defect and the plan does not absorb it.

**What We Know Works After This Phase:** the accounting rule is real, total, and agrees with what the
fixtures' authors actually wrote — proven with no generated byte changed and no license-gated path
involved.

---

## Phase 3: Report Schema, Precedence, Baked Constants, Version Bump

**⚠ The cross-repo red window OPENS in this phase and closes in Phase 6.**

### Goal

The generated report carries the account and the new five-token vocabulary, the headline is computed
from statuses *and* the account, and the runtime-contract version says so.

### Assumption Under Test

B2 — coverage is a generation-time constant, so baking it is valid. And B5 — renaming `all_satisfied`
makes stale readers fail closed rather than misread. The window itself tests B5 for real: TEAx
refuses, loudly, by name.

### Test Stencil (Write This First)

```python
# tests/unit/test_report_precedence.py (NEW) — D6, over the generated aggregator's own function
@pytest.mark.parametrize("statuses,account,expected", [
    (["violated", "satisfied"], PARTIAL,  "violation"),          # top arm survives partial coverage
    (["indeterminate"],         COMPLETE, "indeterminate"),
    (["satisfied"],             COMPLETE, "full_satisfaction"),
    (["satisfied"],             PARTIAL,  "partial_coverage"),   # SC: unclaimable under partial
    ([],                        NONE,     "not_assessed"),       # D4's ruling
])
def test_precedence(statuses, account, expected): ...

def test_the_two_tiers_are_deliberately_asymmetric(one_gate_many_occurrences_report):
    """DR-12: this is the two-tier rule working, not a bug to 'fix' later."""
    assert one_gate_many_occurrences_report.coverage.assessed_gate_count == 1
    assert one_gate_many_occurrences_report.assessed_entry_count == 40

def test_coverage_account_rejects_inconsistent_arithmetic():
    with pytest.raises(ValidationError):
        CoverageAccount(applicable_gate_total=3, assessed_gate_count=1, unassessed_gate_count=1, ...)
```

### Changes Required

**See `design.md` for:** D1 (the token map table), D2 (the block, the renamed field, derived histogram
keys), D3 (baked constants), D6 (precedence), D8 (versions), *Required Invariants* 1, 2, 3.

- [ ] `templates/constraint_types.py.jinja2` — add `CoverageAccount` with its validators; add
      `coverage` to `ConstraintReport`; rename `assessed_count` → `assessed_entry_count`; widen
      `headline`'s `Literal` to the five report tokens (`:24-29`).
- [ ] `templates/report_aggregator.py.jinja2` — bake the account as a constant beside
      `CATALOG_FINGERPRINT`/`EXPECTED_IDS`; implement D6's five-arm precedence (`:44-58`).
- [ ] `generation/modules.py::render_report_aggregator` (`:353-380`) — pass the account through.
- [ ] `generation/constraint_plan.py` — `ConstraintGenerationPlan.coverage`, computed once (PD1).
- [ ] `contracts/versions.py` — `RUNTIME_CONTRACT_VERSION = "2.0.0"`, with the docstring saying what
      broke: a renamed field, a new required block, and new headline tokens.
- [ ] `tests/conformance/test_runtime_contract_version.py` (NEW, mirroring
      `test_catalog_schema_version.py`) — pin `2.0.0` as the reviewed token and state the TEAx
      re-vendor obligation. **Do not touch** `test_catalog_schema_version.py`: `3.0.0` stands.
- [ ] **Move the four `all_satisfied` assertions** to the new vocabulary, each asserting a coverage
      claim, using the ledger entries written in Phase 0 — not values read off a run:
      - [ ] `tests/execution/test_constraint_verdicts_exact_route.py:171, 416, 540`
      - [ ] `tests/execution/test_fusion_tea_real_teax.py:245` — the whole-dump equality; paste the
            Phase 0 block, including `coverage` and the renamed `assessed_entry_count`.
- [ ] **Do not touch** `docs/architecture/modeling-assumptions.md:551-554` — that `all_satisfied` sits
      inside ADR-009's frozen "what the contract said" quotation.
- [ ] Regenerate any baseline whose bytes legitimately move (expect none yet — the trigger widens in
      Phase 4).

### Validation

**Automated:**
- [ ] Focused: precedence matrix, validators, two-tier asymmetry, version pin.
- [ ] **Open the red window (PD6):** run the full licensed suite once and write the exact failing set
      plus each signature into `verification.md`. Expect the simkit-loading execution tests —
      `tests/execution/test_constraint_verdicts_exact_route.py`, `test_fusion_tea_real_teax.py`,
      `test_fusion_tea_mutation_teax.py`, `test_c19_nested_occurrence_teax.py`, and any of
      `tests/conformance/test_constraint_generation_integration.py` /
      `tests/runtime/test_fusion_tea_acceptance.py` that loads a generated package — failing on
      TEAx's `ACCEPTED_RUNTIME_CONTRACT_VERSIONS = {"1.0.0"}` refusal and/or the unmapped headline
      token. **Everything outside that list must be green.**
- [ ] `ruff`/`mypy` zero-new.

**Manual:**
- [ ] Read one generated `constraint_types.py` and one `report_aggregator.py` end to end. The baked
      account is a literal constant; the precedence function reads it; there is no catalog file I/O.
- [ ] Every red test's failure signature is a *version refusal or an unknown token* — the fail-closed
      behaviour B5 predicted. A red test failing any other way is a defect.

**What We Know Works After This Phase:** the report can state coverage, full satisfaction is
unclaimable when anything is unassessed, and stale readers refuse by name instead of misreading.

---

## Phase 4: The Report-Required Trigger, the Zero-Input Aggregator, and the Three Seams

**Red window still open.**

### Goal

Every constraint-bearing model ships a report — including the two zero-input branches — and the rule
saying so lives in exactly one place.

### Assumption Under Test

That flipping `ships_constraint_machinery` from `bool(concrete_entries)` to `bool(usage_records)` has
exactly the three per-seam consequences D5 (rev 2, DR-11) names and no fourth. `catf_mfe_d5` is the
shape that shows it: 65 bare constraints, zero concrete entries, now emitting a report.

### Test Stencil (Write This First)

```python
def test_descriptive_only_model_ships_a_zero_input_aggregator(catf_mfe_d5_graph):
    agg = [m for m in catf_mfe_d5_graph.modules if m.module_kind is ModuleKind.REPORT_AGGREGATOR]
    assert len(agg) == 1 and not agg[0].inputs
    assert agg[0].outputs[0].channel in exit_point_channels(catf_mfe_d5_graph)   # invariant 32

def test_constraint_free_model_stays_inert(sample_model_graph):
    """LC-E12: the trigger widened, it did not become universal."""
    assert not any(m.module_kind is ModuleKind.REPORT_AGGREGATOR for m in sample_model_graph.modules)
    assert sample_model_graph.constraint_catalog is None

def test_has_executable_content_is_gone():
    assert not hasattr(ComputationGraph, "has_executable_content")
```

### Changes Required

**See `design.md` for:** D5 in full (the trigger, the three seams, what each starts doing),
*Required Invariants* 4 and 10, *Implementation Notes* (baseline churn is narrower than it looks).

- [ ] `resolution/models.py` — `ships_constraint_machinery` (`:644-656`) body becomes
      `bool(usage_records)`; keep the name and the single home (Item 2's A4 cure).
      **Delete `has_executable_content`** (`:596`) — `ships_constraint_machinery` is its only caller.
- [ ] `elaboration/project.py:892` — the early return becomes conditional on the same population,
      read from the instance graph's `constraint_usages` domain.
- [ ] `cli/__init__.py:411` — collapse the redundant `catalog is not None and …` guard.
- [ ] Confirm each seam's new behaviour on `catf_mfe_d5`: `schemas/constraint_types.py` emitted
      (`cli/__init__.py:455-464`), registry imports the report types
      (`generation/registry.py:353-362`), name-safety preflight runs over an empty entry set
      (`:404-414`).
- [ ] Regenerate the baselines that legitimately churn; **review the diff fixture by fixture**. Only
      two causes are legitimate (a fixture gaining an aggregator; its channel set moving as a
      result). A third cause is a finding. Do not `ruff format` baselines.
- [ ] The Phase 0 characterization test for the excluded-only shape flips to passing — remove its
      `xfail` and keep the assertion.

### Validation

**Automated:**
- [ ] Focused: both zero-input branches (descriptive-only → `not_assessed`; asserted-with-zero-
      eligible → `partial_coverage`), exit-point retention on both, constraint-free byte stability,
      `has_executable_content` absent.
- [ ] Full licensed suite: green **outside the enumerated red set**, and that set unchanged (PD6).
- [ ] `ruff`/`mypy` zero-new; `git diff --check` clean.

**Manual:**
- [ ] Baseline diff review under the timestamp-churn protocol — a full re-capture rewrites every
      `captured_at`, so diff timestamps separately and revert them, leaving only real churn visible.
- [ ] Companion untouched check.

**What We Know Works After This Phase:** no constraint-bearing model is silent any more, the two
zero-input branches are distinguishable by headline, and constraint-free packages are byte-identical.

---

## Phase 5: The Sixth Preflight and the Divergence Refusals

**Red window still open.**

### Goal

An account that disagrees with its catalog, an aggregator that disagrees with the usage rows, an
untaught reason token, and D9's contradiction each refuse generation by name, before anything is
written.

### Assumption Under Test

That PD1's placement is genuinely fail-before-mutate, and that the recomputation is a real check
rather than a tautology — it must fail when one side is perturbed.

### Test Stencil (Write This First)

```python
def test_a_perturbed_plan_account_refuses_before_any_write(tmp_path, monkeypatch):
    monkeypatch.setattr(plan, "coverage", replace(plan.coverage, assessed_gate_count=99))
    with pytest.raises(CodeGenerationError, match="coverage account"):
        run_codegen(config)
    assert not list(tmp_path.iterdir())          # fail-before-mutate

def test_aggregator_without_usage_rows_refuses(graph_with_orphan_aggregator): ...
def test_usage_rows_without_aggregator_refuses(graph_missing_aggregator): ...
def test_the_d9_fixture_refuses_generation_by_name(tmp_path):
    with pytest.raises(CodeGenerationError, match="marked inapplicable but produced"):
        run_codegen(config_for("constraint_coverage_eligible_inapplicable"))
    assert not list(tmp_path.iterdir())
```

### Changes Required

**See `design.md` for:** D3 "Divergence is a failure at two ends", D9, *Required Invariants* 4, 5, 6,
9; and PD1 above for placement and shape.

- [ ] `cli/__init__.py` — `_preflight_coverage_account(graph, constraint_plan)` with its four named
      refusals, called after `build_constraint_generation_plan` and before `_clear_output_directory`.
- [ ] Confirm nothing between the existing preflight block and that call mutates the output tree
      (verified this stage for `ensure_package_tree_is_link_free`; re-confirm if the code moved).
- [ ] Negative tests for all four refusals, each asserting the output tree is untouched.
- [ ] The existing `_preflight_constraint_totality` (`:317-399`) is untouched — it already covers a
      catalog perturbed after projection sealed it.

### Validation

**Automated:**
- [ ] Focused: four refusals × (named message, nothing written).
- [ ] Full licensed suite: green outside the red set, set unchanged.
- [ ] `ruff`/`mypy` zero-new.

**Manual:**
- [ ] Trip one refusal by hand and read the message. It names the usage and says what to do.

**What We Know Works After This Phase:** codegen's half is complete. The account cannot ship
disagreeing with its catalog, and the one authoring contradiction that could have silenced a live
gate refuses instead.

---

## Phase 6: The TEAx Branch — Vocabulary, Policy, One Report Authority

**Repo:** `/home/reid/1cfe/teax`, on a branch off `main` `fa0e06a`. **Never commit to `main`.**
**This phase closes the red window.**

### Goal

TEAx understands the five-token vocabulary, fails closed on anything else, disposes partial coverage
conservatively with an auditable opt-in, answers "does this package ship a report" in exactly one
place, and carries coverage into durable case records.

### Assumption Under Test

B4 — no durable store holds results worth keeping, and the compatibility binding refuses to reopen
one once `evidence_schema_version` moves. And PD5 — that the five committed fixture packages can be
regenerated at acceptable cost under D8's version replace.

### Test Stencil (Write This First)

```python
# simkit/tests/evaluation/test_headline_vocabulary.py (NEW)
def test_every_report_token_maps_to_exactly_one_canonical_token():
    assert set(CANONICAL_HEADLINE) == {"violation","indeterminate","full_satisfaction",
                                       "partial_coverage","not_assessed"}
    assert len(set(CANONICAL_HEADLINE.values())) == len(CANONICAL_HEADLINE)

def test_an_unmapped_token_raises_and_never_reads_satisfied():
    with pytest.raises(UnknownHeadlineToken):
        project(report_with_headline("all_satisfied"))       # the OLD token, now unknown

# simkit/tests/study/test_partial_coverage_policy.py (NEW)
def test_partial_coverage_defaults_to_keep_for_boundary(objective_policy):
    assert objective_policy.dispose(headline="partial_coverage").disposition == "keep-for-boundary"

def test_the_opt_in_starts_a_new_study_lineage(cfg):
    assert StudyConfig(policy=PolicyConfig(partial_coverage="feed-strategy")).semantic_fingerprint() \
        != StudyConfig(policy=PolicyConfig()).semantic_fingerprint()

# simkit/tests/evaluation/test_constraint_evidence_durability.py (EXTEND)
def test_coverage_survives_the_file_backed_round_trip(file_backed_package):
    harvested = harvest(persist(evaluate(file_backed_package)))
    assert harvested.report["coverage"] == GENERATED_COVERAGE     # byte-equal, no adapter
    with pytest.raises(TypeError):
        harvested.report["coverage"]["assessed_gate_count"] = 0   # invariant 41

# simkit/tests/study/test_store_compatibility.py (EXTEND)
def test_reopening_across_the_evidence_bump_raises(v1_store):
    """Invariant 50, through its real carrier — vary evidence_schema_version, not the contract fp."""
    with pytest.raises(IncompatibleStore):
        open_store(v1_store, definition=with_evidence_schema_version("v2"))
```

### Changes Required

**See `design.md` for:** D1 (fail-closed, both sides), D7 in full, D8 (versions, order), *Component
Overview* (the TEAx list), *Required Invariants* 7, 8, 10, 11.

**A — Fixture regeneration probe (PD5), first.**
- [ ] Create the branch off `fa0e06a`. Record the SHA.
- [ ] Confirm the measurement: five packages under `simkit/tests/evaluation/fixtures/*/package_live`
      at catalog `2.0.0` / runtime-contract `1.0.0`.
- [ ] Probe **one** package (`constraint_free` — smallest, model-based) end to end: regenerate from
      its `models/*.sysml` with the new codegen, restore the hand-filled `handwritten/` tree, re-seal,
      and load it through `package_load`. Record what it cost and what broke.
- [ ] *If the probe shows the full regeneration exceeds the item's remaining budget* → STOP and
      surface PD5's fallback (extend rather than replace the vendored sets) as an owner decision.
      Do not take the fallback silently.
- [ ] Otherwise regenerate the other four, including `f1_arithmetic` through its own
      `generate_fixture.py` with its pins refreshed (`SYSML_SHA`, lockfile, environment fingerprint).

**B — Vocabulary and fail-closed seam.**
- [ ] `evaluation/evidence.py:40-51` — split `ResponseEntry` into `ConstraintStatus` (three values)
      and `HeadlineResponse` (five); type `responses` as their union; extend `CANONICAL_HEADLINE` per
      D1's table; add `UnknownHeadlineToken` beside `CorruptConstraintEvidence`. It is **not** an
      `AssessmentFailed`.
- [ ] `evaluation/projection.py:59` — explicit lookup, raising `UnknownHeadlineToken`.
- [ ] `evaluation/package_load.py:33/39` — re-vendor `ACCEPTED_RUNTIME_CONTRACT_VERSIONS = {"2.0.0"}`
      and `ACCEPTED_CATALOG_SCHEMA_VERSIONS = {"3.0.0"}` (subject to PD5). `TRUSTED_VERIFIER_SHA256`
      does **not** move.

**C — One report-expectation authority.**
- [ ] `study/model_contract.py` — add `ships_constraint_report(contract) -> bool(contract.usage_records)`.
- [ ] `study/cli.py:42` — call it, replacing the `concrete_entries` read.
- [ ] `evaluation/evaluator.py:79-87` — **delete** `_report_declared_in_spec`; make
      `expects_constraint_report` a required constructor argument on `PreparedEvaluator` (`:128`) and
      `FileBackedEvaluator` (`:207`). Pass it explicitly at the ~15 test sites (PD6 correction).

**D — Policy, config, case records.**
- [ ] `study/policy.py` — `_HEADLINE_DISPOSITION:76-80` maps `partial_coverage → keep-for-boundary`;
      `_DISPOSITION_BY_HEADLINE:32-37` maps it to a `partial_coverage` **disposition**. Both
      subscripts (`:70`, `:135`) become fail-closed lookups. The `cases.state` lifecycle column is
      untouched — no migration.
- [ ] `study/config.py:41-44` — `PolicyConfig.partial_coverage: Literal["keep-for-boundary",
      "feed-strategy"] = "keep-for-boundary"`. Opted-in takes the identical path `satisfied` takes.
- [ ] Policy copies `coverage` and `catalog_fingerprint` into `assessment_json`; it never writes
      evidence (invariant 49).
- [ ] `study/query.py` — PD3's two `CaseView` fields, populated in `_case_view`.
- [ ] Evidence schema `v1 → v2` (the invariant-50 carrier).

### Validation

**Automated:**
- [ ] TEAx focused: token map both directions, both fail-closed lookups, policy dispatch default and
      opt-in, fingerprint lineage change, durability round-trip + invariant 41, store
      incompatibility through `evidence_schema_version`.
- [ ] **Full TEAx suite** from `/home/reid/1cfe/teax/packages/teax-simkit` (`pytest`, `testpaths =
      simkit/tests`), run under the interpreter that resolves `syside`/codegen — the
      agentic-mbse venv, not teax's own `.venv` and not `uv run`, which are known broken here.
- [ ] `ruff`/`mypy` zero-new **in TEAx**.

**Manual:**
- [ ] `git -C /home/reid/1cfe/teax branch --show-current` is the item branch, and `main` has no new
      commits.
- [ ] Read the regenerated fixture packages' `contracts/model_contract.json`: `3.0.0`, and a
      `coverage` block present in every constraint-bearing report shape.

**What We Know Works After This Phase:** both vocabularies carry all five states, an unknown token
raises on either side, a partially-covered candidate does not steer the search unless a study says so
in writing, coverage reaches the durable record, and the old store cannot be silently reopened.

---

## Phase 7: Cross-Repo Green, the Six-State Matrix, and the Final Gates

### Goal

Close the red window, pin every state end to end, and record the evidence.

### Assumption Under Test

That the two halves compose: a package generated by the new codegen, loaded and projected by the new
TEAx, produces the expected headline *and* the expected disposition for all six states — and that
nothing in the item moved a byte it should not have.

### Test Stencil (Write This First)

```python
# tests/execution/test_constraint_coverage_matrix.py (NEW, codegen)
@pytest.mark.parametrize("fixture,report_headline,canonical,disposition", SIX_STATES)
def test_each_state_is_pinned_by_something_no_other_state_satisfies(
    fixture, report_headline, canonical, disposition):
    report = evaluate_through_real_teax(fixture)
    assert report.headline == report_headline
    assert project(report)["headline"] == canonical
    assert dispose(canonical) == disposition

def test_violation_still_states_its_coverage(violation_partial_fixture):
    r = evaluate_through_real_teax(violation_partial_fixture)
    assert r.headline == "violation" and r.coverage.coverage_state == "partial"
    assert case_record_for(r).coverage["unassessed_gate_count"] > 0

def test_three_route_parity_includes_the_account(live, snapshot, relocated):
    assert live.report_bytes == snapshot.report_bytes == relocated.report_bytes
```

### Changes Required

**See `design.md` for:** *Validation Approach* items 1–17 — this phase is where the ones not already
placed land.

- [ ] Six-state matrix, twice (five report headlines + report-absent; six runtime dispositions), each
      state asserted against its ledger entry.
- [ ] Violation-plus-partial through to the case record (spec success criterion 2).
- [ ] Full satisfaction unclaimable under partial assessment (criterion 3).
- [ ] D4's ruling pinned; the two-tier asymmetry pinned deliberately (DR-12).
- [ ] Three-route parity — live, snapshot, relocated agree on report bytes including the account.
- [ ] Cross-repo pins: codegen's version drift test covers `RUNTIME_CONTRACT_VERSION`; TEAx pins the
      token map against a codegen-generated fixture package.
- [ ] The zero-input report-authority test (validation item 12): `ships_constraint_report` answers
      `True` from `usage_records`, the invariant-46a corruption check still fires when the report
      channel is removed, and no spec-derived fallback exists to disagree.
- [ ] Remove the last Phase 0 `xfail` — both characterization tests now pass as assertions.
- [ ] Documentation corrections, **before** the confirmation run: the two Appendix-C / epic-text
      corrections this item filed (design-F2 and design-F3) are filed for close, not performed here;
      what *is* performed is any doc line in this repo that states the old headline vocabulary
      outside ADR-009's frozen quotation. Grep and fix, then run.

### Validation — the final gates, named

- [ ] Focused tests across both repos, all green.
- [ ] **The red window is closed:** the enumerated set from Phase 3 is empty.
- [ ] **Full licensed codegen suite** in `/home/reid/1cfe/sysml-codegen-item7-rebuild`:
      `set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a` then
      `/home/reid/1cfe/item7-rebuild-venv/bin/python -m pytest tests/` → green, with **zero
      license-skip lines** (a green run with skips is not a run). Never `uv run`.
- [ ] **Full TEAx suite** from `/home/reid/1cfe/teax/packages/teax-simkit` → green.
- [ ] **Cross-repo compatibility tests** green (version pins, token map, fixture packages).
- [ ] `ruff check src/` and `mypy src/` → zero new **in both repos**.
- [ ] Generated-artifact review complete: baselines diffed under the timestamp-churn protocol, every
      churned byte attributable to one of the two legitimate causes.
- [ ] `git diff --check` clean in both repos.
- [ ] **Companion untouched:** `git -C /home/reid/1cfe/agentic-mbse status --porcelain` empty and
      `log --oneline -1` equal to the Phase 0 value.
- [ ] `verification.md` written with **exact counts**: fixtures in the corpus and how many gained an
      aggregator; ledger entry count; `catf_mfe_d5`'s account (65 / 0 / 0 / 0 / 0 / `{}` / `none`);
      the red-window set and the phase it closed; focused and full test counts in both repos; ruff
      and mypy before/after in both; the TEAx branch SHA and the five regenerated fixture packages;
      the `RUNTIME_CONTRACT_VERSION` move and the unchanged `CATALOG_SCHEMA_VERSION`.

**What We Know Works After This Phase:** all six states are independently pinned end to end, coverage
survives a higher-precedence headline all the way into the durable record, and both repos are green
with nothing pushed yet.

---

## Completion Criteria (Both Repos)

The item is done when all of these hold. Publication is codegen first, TEAx second (D8 step 4); the
item does not close on codegen alone.

**sysml-codegen (`item7-rebuild`):**
- [ ] Every report carries a coverage account derived by `coverage_account()` from the sealed
      catalog, with the arithmetic identities enforced at construction.
- [ ] Five report headline tokens; `full_satisfaction` requires `unassessed_gate_count == 0 and
      assessed_gate_count > 0`.
- [ ] A `REPORT_AGGREGATOR` exists iff the catalog has usage rows, and its channel is an exit point;
      constraint-free packages byte-identical.
- [ ] Four named refusals at the coverage preflight, all fail-before-mutate.
- [ ] `RUNTIME_CONTRACT_VERSION = "2.0.0"`; `CATALOG_SCHEMA_VERSION` still `3.0.0`;
      `TRUSTED_VERIFIER_SHA256` unmoved. `has_executable_content` deleted.
- [ ] The four `all_satisfied` sites assert coverage claims, from hand-written expectations.

**teax (branch off `fa0e06a`, never `main`):**
- [ ] Split vocabularies, fail-closed lookups on all three former bare subscripts, `partial_coverage`
      in both dispatch tables with the conservative default and the fingerprint-bearing opt-in.
- [ ] `ships_constraint_report` is the single consumer authority; `_report_declared_in_spec` deleted
      and `expects_constraint_report` required.
- [ ] Vendored sets re-vendored; evidence `v2`; coverage in `assessment_json` and on `CaseView`.
- [ ] The five committed fixture packages regenerated and loading (or PD5's fallback taken as an
      owner decision, recorded).

**Spanning both:**
- [ ] Six states pinned in both vocabularies, each by a test no other state satisfies.
- [ ] Reopening a store across the item raises `IncompatibleStore`, carried by
      `evidence_schema_version`.
- [ ] Both full suites green, ruff/mypy zero-new in both, `git diff --check` clean in both,
      companion untouched, counts in `verification.md`.

**Deliberately outside the item, tracked as hand-offs:** Appendix C's vacuous-gate cell wants "…and
at least one gate remains" (design-F2); the epic's scope-4 wording wants the contract's phrasing
(design-F3); the companion's authoring-time advisory for the eligible+inapplicable combination (D9's
filed follow-on). All three are filed for close, not performed here.

---

## Environment Setup

**See CLAUDE.md.** Four things bite in this item specifically.

- **Codegen gates run `/home/reid/1cfe/item7-rebuild-venv/bin/python -m pytest`, never `uv run`.**
- **The license is not in this repo.** `set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a`, and
  verify zero license-skip lines — a missing key silently degrades the suite into a fake baseline.
- **The TEAx suite** runs from `/home/reid/1cfe/teax/packages/teax-simkit` under the agentic-mbse
  venv; teax's own `.venv` and `uv run` are known broken for this. Push TEAx over HTTPS, not SSH.
- **Fixtures and generated baselines are format-exempt.** Never `ruff format` them; byte-identity
  gates depend on those bytes.

## Risk Management

**See `design.md#potential-risks` for the full analysis.** Phase-specific mitigations:

- **Phase 2 — wrong-but-confident counts (B1).** The ledger is written from source in Phases 0–1 and
  the derivation is checked against it before any generated byte moves. A mismatch is triaged three
  ways, and "B1 is false" stops the item rather than being absorbed.
- **Phases 3–5 — the cross-repo red window.** Enumerated at open, gated for no growth, closed in
  Phase 6, and recorded in `verification.md`. Land the whole window inside one working session if
  possible; a red lane left overnight reads like a codegen defect and is not one.
- **Phase 6 — PD5's fixture regeneration.** Probed on one package before four more are attempted,
  with a named fallback that is an owner decision rather than a quiet edit.
- **Phase 6 — the required `expects_constraint_report` argument.** ~15 mechanical test-site edits,
  sized in advance so the phase does not discover them.
- **Phase 4 — unexplained baseline churn.** Exactly two causes are legitimate. A third is a finding.
- **Phase 1 — over-built fixtures.** One shape per fixture. Item 13's cell 18 was a fixture defect
  masquerading as a product defect; the shape test in Phase 1 is what catches that early.
- **`RUNTIME_CONTRACT_VERSION` blast radius.** Every consumer of a sealed package is refused after
  the bump. Known consumers are TEAx and codegen's own tests; the fusion/stellarator demo branches
  are local, pinned, and not regenerated by this item.
- **D9 refuses a model that generates today.** Intended. Nothing in the tree carries the combination
  (probed in Phase 0). If a customer model does, the refusal names the usage and the fix is one doc
  comment.

## Scale Note (Honest)

The design estimates ~11h of execute+validate — a ~2-day item. **This phasing implies more, and the
overrun is concentrated in two places the design did not size.**

1. **PD5's fixture regeneration (Phase 6A).** Five committed TEAx packages, each needing generation
   with the license, restoration of hand-filled `handwritten/` implementations, and a re-seal;
   `f1_arithmetic` additionally needs its reproduction script's pins refreshed. Call it half a day if
   the probe goes well, and an open question if it does not — which is exactly why it is probed
   before it is attempted.
2. **The fixture corpus and ledger (Phases 0–1).** Up to five new fixtures plus a hand-written,
   source-derived account for every fixture in the matrix. This is the DR-6 mitigation and it is not
   compressible: a transcribed expectation proves nothing. Roughly half a day, and the survey step
   (PD4) is the only real lever on it.

Call the item **~3 days**, not 2. If the Phase 1 survey shows more fixtures need authoring than the
five listed, or the Phase 6A probe goes badly, say so at that point rather than absorbing it.

## Implementation Notes

[TO BE FILLED DURING IMPLEMENTATION]

### Phase 0 Completion
**Completed:** 2026-08-13

**Actual Changes:**
- `.project/active/constraint-coverage-policy/expected-coverage.md` (NEW) — the PD2 ledger. Nine
  existing-fixture entries and four intended new-fixture entries, every one derived from `.sysml`
  source against D3's bucket table, each citing the file and line it counted.
- `tests/unit/test_coverage_probes.py` (NEW) — B3 and D9's reachability claim, license-free off
  `catf_mfe_d5`'s committed v6 snapshot. Both pass.
- `tests/execution/test_constraint_coverage_characterization.py` (NEW) — the two `xfail(strict=True)`
  characterization tests. Both fail for the stated reason, read under `--runxfail`:
  `assert 'all_satisfied' != 'all_satisfied'` and the aggregator module absent.

**Probe results (recorded in `verification.md` and in the ledger's cross-check section):**
- Companion baseline: `agentic-mbse` at `5088b41`, `status --porcelain` empty.
- **B3 holds.** `catf_mfe_d5` (65 usages, 0 eligible, 0 entries), `constraint_domain_plain_forms`,
  `constraint_domain_satisfy`, and `constraint_domain_satisfy_calc_def` each project a non-`None`
  catalog with non-empty `usage_records`. D5's trigger is readable. No stop.
- **D9 reachability: 0 hits.** A corpus sweep over the 57 fixture directories that elaborate
  standalone scanned all 105 usage records; none is both `eligible` and carries an
  `inapplicability_reason`. The `@inapplicable:` marker appears in five fixtures; four are negative
  fixtures that refuse elaboration already, and in `constraint_domain_inapplicable` the marker sits
  on a `non_reaching` record.

**Issues:** none.

**Deviations:**
- The plan's `test_coverage_probes.py` is described as scratch to be folded in later. It was written
  as a durable test instead — both claims are properties worth keeping, and a scratch file that
  answers a question once and is deleted leaves nothing pinning the answer.
- The fusion open check resolved from source: `hif_plant.sysml:223` is a `//` comment, not a second
  declaration. The account stands at one usage, exactly as the plan carried it.

### Phase 1 Completion
**Completed:** 2026-08-13

**PD4 survey — the design listed five new fixtures; three were genuinely missing.**

| design's required shape | outcome |
|---|---|
| asserted-with-zero-eligible | **authored** `constraint_coverage_zero_eligible`. No existing fixture has it: every fixture carrying an asserted non-reaching gate also carries a live one. |
| all-inapplicable | **authored** `constraint_coverage_all_inapplicable`. `constraint_domain_inapplicable` has a marked gate *beside* a live one, which is the non-degenerate case, not D4's. |
| mixed-partial | **reused** `constraint_domain_detached_owner` (1 assessed + 1 non-reaching). `constraint_domain_block_non_reaching`, `constraint_domain_containment`, and `constraint_non_numerical` carry the same shape; `constraint_non_numerical` is also in the ledger because its unassessed reason is `non_numerical` rather than a reachability one. |
| violation-plus-partial | **authored** `constraint_coverage_violation_partial`. |
| eligible-plus-inapplicable (refusal) | **authored** `constraint_coverage_eligible_inapplicable`. |
| descriptive-only | **reused** `catf_mfe_d5`, unedited. |

**Actual Changes:**
- Four fixtures under `tests/fixtures/constraint_coverage_*/model.sysml`, one shape each.
- Four expectation files under `tests/expectations/constraint_population/` — Item 2's oracle
  requires one per constraint-bearing fixture, and rules 1 and 2 fail without them.
- `tests/unit/test_coverage_fixture_shapes.py` (NEW) — 10 cases: the disposition histogram and the
  marker count for each of the nine ledger fixtures, plus the D9 contradiction asserted as a
  combination on a single record (a histogram cannot see a combination).
- `expected-coverage.md` extended with a machine-readable ledger index block.

**Issues:**
- **The marker does not attach on the inline form.** Both marked fixtures were first authored as
  `assert constraint x { doc /* @inapplicable: … */ <predicate> }` and the marker never reached the
  domain. This is the known SysIDE gap that `test_constraint_population_oracle.py`'s rule 3 exists to
  make loud — a `doc` comment inside an inline-predicate constraint body is dropped. Both were
  re-authored on the definition-typed form (`assert constraint x : Positive { doc /* … */ in v = a; }`),
  which is how every existing marked fixture is written. `source_form` moves `inline` →
  `definition_typed`; both are asserted, so no bucket and no account field moves.
- **The oracle counts marker *tokens in the file*, not markers on usages.** An explanatory `//`
  comment in `constraint_coverage_eligible_inapplicable` that quoted the marker token made the source
  scan read two markers against one on the domain. Reworded; the fixture now says why in a comment.

**Deviations:** three new fixtures rather than five, per the survey. Recorded above with the reason
for each reuse.

**Gate:** full licensed suite green — **1938 passed, 34 skipped, 67 deselected**, and
**zero `no live syside license` skip lines** (all 34 skips are parametrized "nothing to compare in
the golden" cases in `test_computed_attribute_golden.py` (25) and `test_calc_compat_parity.py` (9)).
Companion still `5088b41`, clean.

### Phase 2 Completion
**Completed:** 2026-08-13

**Actual Changes:**
- `src/sysml_codegen/generation/coverage.py` (NEW, 233 lines) — `coverage_account(catalog)`,
  `CoverageAccountData`, the frozen `KNOWN_REASONS` map, `assert_reason_vocabulary_is_known`, and
  D9's refusal. The bucket table is the function's literal structure: four branches in table order,
  each commented with its row number, and the two predicates are named functions
  (`_is_asserted`, `_is_inapplicable`) reading the **catalog** spelling `inapplicability_reason`.
- `KNOWN_REASONS` is a mapping rather than a set, so each token carries the ruling a future reason
  will have to make — where it sits relative to the feasibility denominator.
- `tests/unit/test_coverage_account.py` (NEW) — 40 cases: every bucket row, all three non-asserted
  forms × row 1, all nine non-`admitted` tokens × all three asserted forms × row 4, row 2 for every
  asserted form, the empty catalog, the derived-histogram rule, and both refusals.
- `tests/unit/test_coverage_ledger_agreement.py` (NEW) — the ledger index parsed out of
  `expected-coverage.md` rather than transcribed, so the artifact the owner reviews and the table the
  test asserts cannot drift apart.

**FIRST PROOF POINT — passed.** All 13 ledger entries reproduce exactly, including `catf_mfe_d5`'s
65 / 0 / 0 / 0 / 0 / `{}` / `none` and `fusion_tea`'s complete account. Every expectation was
committed in Phase 0/1 before this code existed. **B1 is discharged**: no triage was needed, so the
catalog's enumeration and dispositions are correct for every shape in the corpus.

**Issues:** none.

**Deviations:**
- The plan's stencil returns an object whose `coverage_state` is a field. It is a property here,
  derived from the counts, so the state and the counts cannot disagree by construction — the
  validator the design asks for on the generated model has nothing to check on this side.
- `coverage_account` is `applicable + inapplicable <= authored` rather than `==`: bucket 1 (inventory
  only) is real and populated, so equality would be wrong.

**Gate:** 54 focused tests green; full licensed suite green, zero license-skip lines; zero new ruff
(`src/` baseline 12, unchanged) and zero new mypy (`src/` baseline 55, unchanged) — neither tool
reports anything in the new files. No generated byte moved.

### Phase 3 Completion
**Completed:** 2026-08-13 — **the red window is OPEN.**

**Actual Changes:**
- `templates/constraint_types.py.jinja2` — `CoverageAccount` with a `model_validator` carrying all
  three identities; `ConstraintReport` gains `coverage`, renames `assessed_count` →
  `assessed_entry_count`, and widens `headline` to the five report tokens.
- `templates/report_aggregator.py.jinja2` — `COVERAGE` baked beside `CATALOG_FINGERPRINT` and
  `EXPECTED_IDS`; D6's five-arm precedence replaces the three-arm status-only rule.
- `generation/modules.py::render_report_aggregator` — takes the account as a required argument.
- `generation/constraint_plan.py` — `ConstraintGenerationPlan.coverage`, computed once at the top of
  `build_constraint_generation_plan`, so D9's refusal and the vocabulary pin fire at plan build.
- `contracts/versions.py` — `RUNTIME_CONTRACT_VERSION = "2.0.0"`, docstring naming all three breaks.
- `tests/conformance/test_runtime_contract_version.py` (NEW), `tests/unit/test_report_precedence.py`
  (NEW, 15 cases), `tests/unit/conftest.py` (fixtures that render and import the real templates).
- The four `all_satisfied` sites moved to the new vocabulary, each asserting a coverage claim taken
  from its Phase 0 ledger entry. Two further `assessed_count` reads (`:304`, `:594`) renamed, and one
  fixture `PROVENANCE.md` line that stated the old field.
- `docs/architecture/modeling-assumptions.md:554` **not touched** — ADR-009's frozen quotation.

**RED WINDOW (PD6) — enumerated at open, in `red-window.txt`: 62 tests.**

| file | count |
|---|---|
| `test_c19_nested_occurrence_teax.py` | 17 |
| `test_fusion_tea_mutation_teax.py` | 20 |
| `test_constraint_verdicts_exact_route.py` | 14 |
| `test_fusion_tea_real_teax.py` | 11 |

**All 62 carry one signature**, which is exactly the fail-closed behaviour B5 predicted:

```
simkit.evaluation.package_load.SealVerificationError: seal violation: recorded
runtime_contract_version '2.0.0' is not in the accepted runtime-contract versions ['1.0.0']
```

Not one red test fails any other way. Everything outside the window is green:
**1957 passed, 34 skipped (zero license skips)** on the non-execution lane.

**Excluded from the window as pre-existing:**
`test_fusion_tea_real_teax.py::test_the_lane_runs_the_real_simkit` fails whenever the whole
`-m execution` set runs in one process — a sibling module imports the in-repo stub runner.
**Reproduced at the parent commit `826adf0` with the identical assertion**, and it passes when run
alone. Not absorbed, not counted.

**Issues:**
- `generate_teax_module`'s `REPORT_AGGREGATOR` arm had the catalog but no account. Deriving there
  would be a second derivation of a producer fact (invariant 5), and an optional `coverage=None`
  with a fallback is the shim this epic's bar rejects. **The arm now refuses by name and points at
  `build_constraint_generation_plan`**, which is the only route that has the account — and is what
  the CLI already used, so the arm was dead in production. Its test became a refusal test plus a
  positive test on the plan route. Recorded as a deviation, not a silent edit.
- `RUNTIME_CONTRACT_VERSION` rides the **package seal**, not the model contract; the drift test
  asserts against `seal_package` accordingly.

**Deviations:** the `generate_teax_module` refusal above. Nothing else.

**Manual gate:** read a generated `constraint_types.py` and `report_aggregator.py` for
`constraint_domain_detached_owner` end to end. `COVERAGE` is a literal dict
(`2 / 2 / 1 / 1 / 0 / {'owner_has_no_occurrences': 1} / 'partial'`) matching that fixture's ledger
entry exactly; the precedence function reads it; there is no catalog file I/O.

**Gate:** ruff `src/` 12 (baseline, unchanged), mypy `src/` 55 (baseline, unchanged), zero findings
in any new file. `git diff --check` clean. Companion still `5088b41`, clean.

### Phase 4 Completion
**Completed:** 2026-08-13 — **red window still open, unchanged.**

**Actual Changes:**
- `resolution/models.py` — `ships_constraint_machinery` reads `bool(catalog.usage_records)`.
  `has_executable_content` **deleted**; no reader remained anywhere in the tree.
- `elaboration/project.py` — the early return at the aggregator mint reads
  `self.graph.constraint_usages`.
- `cli/__init__.py:411` — the redundant `catalog is not None and …` guard collapsed to the rule
  itself, with an assert narrowing the type.
- `tests/unit/test_report_required_trigger.py` (NEW, 6 cases) — both zero-input branches, exit-point
  retention through the real `_build_exit_points` with membership narrowed to nothing (so the pin is
  structural, not incidental capture-everything), constraint-free inertness, and the two-readings
  agreement property the coverage preflight will refuse a violation of.
- The excluded-only characterization test's `xfail` is removed; the assertion stands.

**Issues — a FOURTH seam, not the three D5 named.**
`project.py::_typed_module_order` gated the aggregator's *ordering* entry on
`executable_constraints`, the old rule in a second place. With only the mint widened, the two
inventories disagreed and projection refused by name
(`SI_EDGE_DANGLING: typed module inventory disagrees with projected module inventory`) — the fail-
closed check doing its job. Fixed to read the same `constraint_usages` population. Its dependency
set is still whatever is executable, which for a zero-input branch is nothing, so a
descriptive-only model's report orders first.

Two Item 2 tests asserted the old rule and were updated rather than deleted:
- `test_a_usage_only_package_ships_no_constraint_machinery` → `…ships_the_machinery_and_a_zero_
  input_report`, assertions inverted against the same three artifacts, plus the baked account.
  Item 2's own docstring said Item 3 would supersede it.
- Two hand-built catalogs (`test_module_kind_faildloud.py`, `test_constraint_generation_
  integration.py`) carried a concrete entry with no usage row — a shape no projection produces,
  since every entry joins a usage row by `declaration_id`. Both gained the row.

**Baseline churn: ZERO, and that is the LC-E12 gate passing.** A before/after corpus sweep over all
108 fixture directories shows exactly **8 fixtures gained an aggregator**, none lost one, none
newly erroring:

| fixture | usages | entries |
|---|---|---|
| `catf_mfe_d5` | 65 | 0 |
| `constraint_domain_plain_forms` | 2 | 0 |
| `constraint_domain_satisfy` | 2 | 0 |
| `constraint_domain_satisfy_calc_def` | 2 | 0 |
| the four `constraint_coverage_*` fixtures (new this item) | 1–2 | 0–1 |

Every one is a constraint-bearing model with zero eligible entries — precisely the population D5
widened to. **None of the eight has a committed baseline**, so `tests/fixtures/baseline_outputs/*`
did not move a byte, and constraint-free fixtures are byte-identical by construction. No third
cause of churn appeared, because there was no churn.

**Deviations:** the fourth seam above. The design's DR-11 named three; there were four.

**Gate:** 1963 passed, 34 skipped (zero license skips) outside the window; the red window
**byte-identical** to the Phase 3 list, 62 entries, all still the one `SealVerificationError`
signature. ruff/mypy baselines unchanged. `git diff --check` clean. Companion `5088b41`, clean.

### Phase 5 Completion

### Phase 6 Completion

### Phase 7 Completion

---

**Status**: Draft → In Progress → Complete
