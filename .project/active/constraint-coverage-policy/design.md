# Design: Coverage Report and TEAx Policy (CONSTRAINT-SEMANTICS Item 3)

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-08-12
**Branch:** `item7-rebuild` (codegen worktree `/home/reid/1cfe/sysml-codegen-item7-rebuild`, commit
`01c4b34`); coordinated change in TEAx (`/home/reid/1cfe/teax`, branch off `main` `fa0e06a`)
**Provenance:** every decision below is `[AGENT]` by construction. Requirements it serves carry the
spec's grades; nothing here re-grades an inherited item.

---

## Overview

Give the generated constraint report a coverage account derived from the embedded catalog, replace
the not-failed headline with a five-state coverage-truthful one in both vocabularies, and make TEAx's
study policy react to partial coverage without ever claiming more than was assessed.

## Related Artifacts

- **Spec:** `.project/active/constraint-coverage-policy/spec.md` (reviewed, revised)
- **Spec review:** `.project/active/constraint-coverage-policy/spec-review.md`
- **Product lens:** `.project/active/constraint-coverage-policy/product-lens.md`
- **Brief:** `.project/active/constraint-coverage-policy/briefs/design.md`
- **Epic:** `.project/backlog/epic_constraint_semantics_contract.md` (Item 3)
- **Required Reading (background, not re-derived):** the lifecycle contract's "Headline states and
  coverage truth" + invariants 32/33/41/46/46a/48/49/50/61;
  `.project/concepts/constraint-execution-lifecycle-requirements.md` LC-E05/E06/E10/E11/E12/E13;
  `.project/active/constraint-catalog-totality/design.md` "Token Vocabulary (Item 3 cites this
  section)" and "Item 3 coordination";
  `.project/research/20260812-101200_constraint-semantics-end-to-end.md` §§2, 4–5
- **Decision record:** ADR-009 (`docs/architecture/modeling-assumptions.md` §9) — cited, not re-filed.
  There is no `.project/adr/` directory in this repo; decision records live in the lifecycle contract
  and in `modeling-assumptions.md`. Noted rather than worked around.

## The Point

A design search is only viable if it can tell a candidate that passed its physics gates from a
candidate nobody checked. Today it cannot: a package reports `all_satisfied` when two of nine gates
were assessed, and TEAx labels a model with 65 unassessed checks `unconstrained` — the same label a
genuinely constraint-free model gets. The obligation is owner-graded at its root:

> **[OWNER-VERBATIM]** (2026-08-12) "when we started this whole cleanup, it was while defining a
> policy around how to use constraints to enforce things like physics in a way that make our overall
> 'design search' viable"

and the rule that follows is **[INHERITED]**: no report and no study label may claim more coverage
than was assessed. Items 1 and 2 fixed the meanings and the authority. This item builds the consumer:
the report that states its coverage, the vocabulary that can say "partial", and the policy that keeps
a partially-covered candidate out of the search's steering loop.

## Research Findings

Every TEAx line number below was read first-hand this stage at `fa0e06a` (clean). Codegen citations
are at `01c4b34`. Corrections to the spec's second-hand cites are marked **corrected**.

**TEAx, verified.**

- `CANONICAL_HEADLINE` lives in `packages/teax-simkit/simkit/evaluation/evidence.py:44-51`
  (**corrected** — the spec cites `evaluation/projection.py`, which only *imports* it). It maps four
  report tokens onto `ResponseEntry`, and `ResponseEntry` (`evidence.py:40`) is **one type doing two
  jobs**: per-constraint status and aggregate headline.
- The normalization seam is a bare subscript: `projection.py:59`,
  `responses = {"headline": CANONICAL_HEADLINE[report.headline]}`. An unmapped token is a `KeyError`
  today — exactly what invariant 46a forbids.
- `study/policy.py` has **two** dispatch tables, not one: `_DISPOSITION_BY_HEADLINE:32-37`
  (`DispositionPolicy`, case states) and `_HEADLINE_DISPOSITION:76-80` (`ObjectivePolicy`, the real
  study path). Both are bare subscripts. `unconstrained` is produced by the *absence* of a headline
  key (`policy.py:65-68` and `:112-116`), which the spec's cite matches.
- `ACCEPTED_CATALOG_SCHEMA_VERSIONS = frozenset({"2.0.0"})` at
  `evaluation/package_load.py:39`, beside `ACCEPTED_RUNTIME_CONTRACT_VERSIONS = frozenset({"1.0.0"})`
  (`:33`) and `TRUSTED_VERIFIER_SHA256` (`:47`). `study/model_contract.py:46-51` fails closed on an
  unaccepted catalog version before reading any field. **The fail-closed window Item 2 opened is
  already open**: codegen ships `3.0.0` today, so TEAx main already refuses every newly generated
  package at the study seam. That is what makes "codegen first" safe.
- **Durable case records:** `study/store.py:62-71` — one `cases` row per candidate with
  `evidence_digest` (content-addressed artifact) and `assessment_json`. The artifact is the encoded
  `ModelEvidence`, whose `report` field is the generated report's whole `model_dump(mode="json")`
  tree (`evidence.py:87-90`). **Coverage reaches the durable record for free** the moment it is a
  report field; the policy-side carry is for queryability, not for existence.
- **Invariant 50's route is already mechanized.** `Compatibility` (`study/compatibility.py`) binds
  eight fields including `model_contract_fingerprint` and `evidence_schema_version`;
  `store.py:147-151` raises `IncompatibleStore` when a store is reopened with a different binding.
  A catalog/report schema move changes the fingerprint, so an old store *cannot* be silently rebound.
- **No durable study store with results worth keeping exists.** The only `study.db` files in the tree
  are two archived spike work dirs under
  `.project/completed/20260713_constraint-study-integration-spike/_work/`. The spec's open question
  ("does one exist yet?") resolves to **no**, and the item is not undersized on that account.
- **`_freeze` already covers the new block.** `evidence.py:17-28` recurses mappings and sequences at
  attach, so a nested `coverage` object inside `report` becomes a `MappingProxyType` with no mutable
  container reachable. Invariant 41 needs a test here, not a mechanism.
- `PolicyConfig` (`study/config.py:41-44`) is a `StrictBaseModel` and is digested whole into
  `StudyConfig.semantic_fingerprint()` (`:69`). A new policy field is therefore auditable in YAML
  *and* identity-bearing by construction.
- **A premise the spec did not have (surfaced, and owned by D7 below).** `study/cli.py:42` derives
  `expects_report = bool(load_model_contract(...).concrete_entries)`. Once a constraint-bearing model
  with zero concrete entries ships a report, that derivation is wrong: it would tell the projection
  seam not to expect a report for exactly the packages this item teaches to emit one, silently
  disabling the 46a corruption check (`projection.py:50-55`) for them.

**Codegen, verified.**

- The headline is computed in `templates/report_aggregator.py.jinja2:44-58`, from statuses alone;
  `templates/constraint_types.py.jinja2:24-29` is the four-field `ConstraintReport`.
- The aggregator is minted at `elaboration/project.py:891-919`, and `:891` (`if not
  constraint_outputs: return`) is the line that suppresses it for a constraint-bearing model.
- **Exit-ancestor retention already exists.** `generation/pipeline.py:284-296` pins every
  `REPORT_AGGREGATOR` output channel into the exit points structurally. Invariant 32's retention half
  needs no new mechanism — a zero-input aggregator, once minted, is retained.
- `render_report_aggregator` (`generation/modules.py:353-380`) already bakes `catalog_fingerprint`
  and `EXPECTED_IDS` as generation-time constants. Baking coverage is the same move, not a new one.
- One rule, three seams: `ships_constraint_machinery` (`resolution/models.py:644-656`), read by
  `generation/registry.py:353-362`, `cli/__init__.py:404-414`, and `cli/__init__.py:455-464`. Its
  docstring names this item as its superseder.
- The divergence check has a template: `_preflight_constraint_totality` (`cli/__init__.py:316-399`)
  refuses a catalog whose rows no longer match the fingerprint sealed at projection.
- The four `all_satisfied` assertions: `tests/execution/test_constraint_verdicts_exact_route.py:171,
  416, 540` (bare) and `tests/execution/test_fusion_tea_real_teax.py:244-259` (whole-dump equality,
  whose docstring already demands that a new report field be accounted for before it passes).
- **Cross-repo coupling, measured:** `/home/reid/1cfe/item7-rebuild-venv/bin/python -c "import
  simkit"` resolves to `/home/reid/1cfe/teax/packages/teax-simkit/simkit/__init__.py`. Codegen's
  execution lane runs against the TEAx **working tree**, and `PreparedEvaluator.evaluate`
  (`evaluation/evaluator.py:184`) calls `project(...)`, which subscripts `CANONICAL_HEADLINE`. So a
  codegen test that evaluates a new-vocabulary report goes red until the TEAx branch is checked out.
  This governs the landing order (D8) and is not optional sequencing colour.

## Core Concept

The report gains a second, orthogonal fact. Today it carries one summary token computed from whatever
results happened to arrive. After this item it carries **a headline** — still one precedence-ordered
token — **and a coverage account**: how many constraint usages the model authored, how many of them
are applicable asserted gates, how many of those were actually assessed, and why the rest were not.
The account is computed once at generation from the embedded catalog and baked into the aggregator as
constants, exactly the way the catalog fingerprint already is, because coverage is a property of the
model and not of the design point. The headline then becomes a function of the runtime statuses *and*
the baked account: full satisfaction is claimable only when the account says nothing was left
unassessed. Because the account is always present, a `violation` report still says how much was
checked — and since TEAx's evidence artifact already stores the report tree whole, that reaches the
durable case record without anyone carrying it there.

The key insight is that "partial" was never a kind of satisfaction. It is a statement about the
denominator. Once the denominator is a first-class field, the headline stops being the only place
coverage can live, the crossing rules in the contract resolve cleanly, and the study policy has
something concrete to be conservative about.

## Key Bets

- **B1.** Item 2's `catalog.usage_records` is a complete and correct enumeration of every authored
  constraint usage, with a correct disposition and `occurrence_count` on each. *If false → the report
  states confident coverage numbers that are wrong, which is strictly worse than today's silence,
  because a wrong number is trusted.*
- **B2.** Coverage is a generation-time constant: which gates are applicable and which were assessed
  depends on the model, never on the candidate's input values. *If false → baking is invalid and the
  account must be computed per evaluation from data the aggregator does not have.*
- **B3.** A constraint-bearing model always projects a non-`None` `constraint_catalog` at Item 2's
  HEAD, including one whose usages are *all* non-reaching. *If false → the report-required trigger
  cannot be read from the catalog for exactly the models the zero-input branch exists to serve, and
  the trigger must move to the instance graph's domain.* (Cheapest first probe in the plan; a
  `/_my_spike` is not warranted — it is one generation run on an existing fixture.)
- **B4.** No durable study store holds results worth keeping, and TEAx's eight-field compatibility
  binding already implements invariant 50's archive-and-begin route. *If false → the transition is
  real migration work, this item is undersized, and that is an owner-visible decision, not a design
  call.* Verified this stage (Research Findings); the bet is that it stays true until landing.
- **B5.** Renaming `all_satisfied` makes every stale reader fail closed rather than quietly misread
  the strengthened claim. *If false — a reader that defaults on an unknown token — the rename hides a
  wrong reading instead of exposing it.* Mitigated by D1's fail-closed obligation on both sides and by
  a grep sweep of every headline reader in both repos.

## Key Decisions

### D1 — Token spellings: mirror the contract's own state names

The report vocabulary becomes the contract's five state names, mechanically transliterated:
`violation`, `indeterminate`, `full_satisfaction`, `partial_coverage`, `not_assessed`. The canonical
runtime vocabulary keeps its verdict-shaped spellings and gains one state: `satisfied`, `violated`,
`indeterminate`, `not_assessed`, `partial_coverage`.

| report token (generated) | canonical token (TEAx) | contract state |
|---|---|---|
| `violation` | `violated` | 1 |
| `indeterminate` | `indeterminate` | 2 |
| `full_satisfaction` | `satisfied` | 3 |
| `partial_coverage` | `partial_coverage` | 4 |
| `not_assessed` | `not_assessed` | 5 |
| *(report absent)* | *(no headline key)* → `unconstrained` | 6 |

*Rejected: `satisfied_partial` and `partially_satisfied`, the two spellings the umbrella left open.*
Both encode coverage as a flavour of satisfaction, which is the exact confusion this item exists to
remove — in a partially-covered model every gate that *was* assessed passed; what is partial is the
denominator. The umbrella deferred the choice rather than narrowing it to those two, so picking a
third is inside design's authority; it is recorded here because it visibly overrides both offered
spellings. *Rejected: keeping `all_satisfied` for state 3.* Its meaning strengthens from "nothing
failed" to "everything was checked and passed"; a token whose meaning changes under a reader is the
silent-misread failure mode B5 names. Renaming turns every stale reader into a named refusal.

Fail-closed, both sides: the report side keeps a closed `Literal` on `ConstraintReport.headline`
(pydantic refuses an unknown token at construction). The runtime side replaces both bare subscripts
(`projection.py:59`, `policy.py:70`/`:135`) with an explicit lookup raising a new named
`UnknownHeadlineToken` beside `CorruptConstraintEvidence` in `evidence.py`. It is **not** an
`AssessmentFailed`: a token the runtime cannot map means the runtime does not understand the package,
which must stop the run, not record a per-case policy failure that looks healthy in the store.

### D2 — Coverage as a nested block, with two distinctly named tier counts

`ConstraintReport.coverage: CoverageAccount`, a nested model, not flat fields.

```python
class CoverageAccount(BaseModel):          # generated, schemas/constraint_types.py
    authored_usage_total: int              # inventory totality: every authored usage, every form
    applicable_gate_total: int             # feasibility denominator
    assessed_gate_count: int               # usage tier — the NEW name
    unassessed_gate_count: int             # applicable_gate_total - assessed_gate_count
    inapplicable_gate_count: int           # asserted gates removed by explicit inapplicability
    unassessed_reasons: dict[str, int]     # Item 2 reason tokens -> count; sums to unassessed
    coverage_state: Literal["complete", "partial", "none"]
```

`ConstraintReport.assessed_count` is renamed `assessed_entry_count` and keeps its occurrence-tier
meaning (`len(results)`). The two tiers are now unmistakable in the field names, which is what the
spec's `[INFERRED]` two-tier rule demands. The histogram is keyed by Item 2's reason tokens alone
(`owner_has_no_occurrences`, `owner_absent`, `owner_kind_unattachable`, `classification_incomplete`,
`non_numerical`, `unassessed_form`, `profile_blocked`) — they are unique across kinds in Item 2's
table, so a `kind.reason` compound key would add a join for nothing. `coverage_state` is the coverage
axis itself, carried so it survives a higher-precedence headline.

*Rejected: flat fields on `ConstraintReport`.* Six loose counts read as peers of `headline` and
`results`, and TEAx would have to reassemble them to hand coverage to a case record as one thing.
*Rejected: keeping `assessed_count` for the occurrence tier.* We pay a breaking schema bump either
way, and a reader who never opens the docstring must not have to guess which tier `assessed_count`
means. The catalog join stays where it already is: the report's existing top-level
`catalog_fingerprint`, which addresses the per-usage detail in `contracts/model_contract.json`. The
block carries no per-usage rows — invariant 48, one authority.

### D3 — Derivation runs at generation, in one function, checked from both ends

One pure function, `generation/coverage.py::coverage_account(catalog) -> CoverageAccount` shape,
computed once into `ConstraintGenerationPlan`, rendered into the aggregator as baked constants beside
`CATALOG_FINGERPRINT` and `EXPECTED_IDS`. Divergence is made a failure at three points:

1. **Generation preflight** (a sixth check beside the five existing ones, in `cli/__init__.py`):
   recompute the account from the catalog and refuse if it differs from the plan's, with a named
   `CodeGenerationError`. The existing `_preflight_constraint_totality` seal check already covers a
   catalog perturbed after projection sealed it.
2. **Report construction**: `CoverageAccount` carries validators pinning the arithmetic identities
   (`assessed + unassessed == applicable_gate_total`, `sum(unassessed_reasons.values()) ==
   unassessed_gate_count`, `coverage_state` agrees with the counts). An internally inconsistent bake
   cannot construct.
3. **Runtime verification** (TEAx): the study seam compares the report's `catalog_fingerprint` against
   the loaded model contract's catalog fingerprint and refuses on mismatch — the report and the
   catalog it claims to summarize must be the same catalog.

*Rejected: computing the account in the aggregator at runtime from embedded catalog data.* The
catalog ships in `contracts/model_contract.json`, outside the importable pipeline path; making the
aggregator read it would add file I/O to a pure module and create a second reader of the catalog
inside the generated package. It would also recompute a constant once per candidate.

### D4 — RULING: every asserted gate dispositioned inapplicable reads **not assessed**

The spec surfaced this as a crossing of two published rules and required a ruling, not a coin flip.

**Ruling:** a model whose only asserted gates all carry an explicit inapplicability disposition reads
`not_assessed`, with `applicable_gate_total = 0`, `inapplicable_gate_count = N`, `coverage_state =
"none"`. Concretely, the precedence function's full-satisfaction arm requires
`assessed_gate_count > 0`.

**Reasoning, against the contract.**

1. Appendix C's vacuous-gate cell is written with a conditional that presupposes survivors: the
   inapplicable usage "drops out of the feasibility denominator and the headline reads full
   satisfaction **when every remaining gate passed**" (contract `:793`). With zero remaining gates the
   antecedent is vacuous. Reading a vacuous conditional as an entitlement is the weaker inference.
2. State 5's test is unconditional and matches this model literally: "the model has constraint usages
   but no applicable asserted gate at all" (contract `:459-460`). A model whose asserted gates are all
   inapplicable has no applicable asserted gate. No inference is needed.
3. State 3 defines full satisfaction as "every applicable asserted gate was **assessed** and passed" —
   a claim about assessment having happened. Zero assessments cannot support it.
4. The governing obligation breaks the tie: no report may claim more coverage than was assessed.
   `full_satisfaction` is the strongest claim in the vocabulary, and awarding it for zero assessments
   is today's `all_satisfied` defect wearing a new token.
5. Nothing is lost. The coverage axis distinguishes the two zero-denominator shapes without a headline
   distinction: a descriptive-only model has `inapplicable_gate_count = 0`, an all-inapplicable model
   has it positive. A consumer that wants "all gates were deliberately waived" reads that field.

**Contract consequence to carry to close:** Appendix C's cell, read literally, permits the other
answer in the degenerate case. It wants "…and at least one gate remains" added. Recorded here as a
ruling with reasoning; the amendment is Item 1 territory and is filed, not performed.

### D5 — The report-required trigger, stated once

A report is required **iff the model authors at least one constraint usage** — i.e.
`catalog.usage_records` is non-empty. `ships_constraint_machinery` keeps its name and its single
home (`resolution/models.py`); only its body changes, from `bool(concrete_entries)` to
`bool(usage_records)`, with `has_executable_content` retained for callers that genuinely mean "is
there anything to execute". Item 2's A4 cure is preserved: the rule still lives in one place, and
what changes is what it says, exactly as its docstring anticipated.

`project.py:891`'s early return becomes conditional on the same population, read from the instance
graph's `constraint_usages` domain (the catalog is assembled from it). Two readings of one rule is
the drift A4 exists to stop, so the new coverage preflight closes it as a check: a graph carries a
`REPORT_AGGREGATOR` module **iff** its catalog has usage rows, refused by name either way.

*Rejected: triggering on "no applicable asserted gate".* That is the epic's scope-4 wording; it leaves
a model whose asserted gates all produced zero eligible entries with no aggregator, which is the
partial-coverage branch LC-E12 and Appendix C both require to exist. The contract is the later and
more specific authority (spec, "Surfaced, not resolved").

### D6 — Headline precedence: statuses decide the top two, the account decides the rest

Computed in the aggregator, over the runtime statuses and the baked account:

```
violated in statuses                                   -> "violation"
indeterminate in statuses                              -> "indeterminate"
unassessed_gate_count == 0 and assessed_gate_count > 0 -> "full_satisfaction"
applicable_gate_total > 0                              -> "partial_coverage"
otherwise                                              -> "not_assessed"
```

Result-list non-emptiness stops deciding anything (it was the whole defect). The account is emitted
in every report regardless of which arm fired, which is the two-axes ruling in code: a `violation`
report carries `coverage_state = "partial"` and its counts, and TEAx can separate "rejected on
physics, fully covered" from "rejected on physics, sixty gates unchecked".

### D7 — TEAx policy, config, and the `expects_report` authority

- **Vocabulary split.** `ResponseEntry` stops doing two jobs: `ConstraintStatus` (three values, per
  constraint) and `HeadlineResponse` (five values) become distinct, and the `responses` mapping is
  typed as their union. Adding `partial_coverage` to the single old type would have implied a
  per-constraint status can be partial. *Rejected: one widened type (cheaper, and wrong).*
- **Dispatch.** Both tables gain the state: `ObjectivePolicy`'s `_HEADLINE_DISPOSITION` maps
  `partial_coverage -> keep-for-boundary` (the conservative default), and `DispositionPolicy`'s
  `_DISPOSITION_BY_HEADLINE` maps it to a `partial_coverage` case state. Both subscripts become
  fail-closed lookups (D1).
- **Opt-in.** `PolicyConfig` gains
  `partial_coverage: Literal["keep-for-boundary", "feed-strategy"] = "keep-for-boundary"`. It is one
  visible YAML line; `StrictBaseModel`'s `extra="forbid"` fails closed on a typo; and because the
  whole policy block is digested into `study_definition_fingerprint` (`config.py:69`), flipping it
  **starts a new study lineage** instead of silently changing a running study's meaning. That is what
  makes the opt-in auditable in the strong sense.
- **Opted-in behaviour.** `partial_coverage` then takes the identical path `satisfied` takes —
  objective values against `penalty_threshold`, yielding `penalize` or `feed-strategy`. *Rejected: a
  third bespoke path*, which would produce a disposition no configuration can explain. The assessment
  record always carries `headline: "partial_coverage"`, so the case stays honest about what it was.
- **Coverage into durable case records, two carriers.** The evidence artifact already contains the
  whole report tree including `coverage` (Research Findings) — that is existence. Additionally
  `assessment_json` carries `coverage` verbatim plus `catalog_fingerprint`, and `query.py` surfaces
  them on the case row, so a study query answers "how covered was this candidate" without opening
  artifacts. Policy copies; it never writes evidence (invariant 49).
- **`expects_report` authority moves** from `concrete_entries` to `usage_records` at
  `study/cli.py:42`. This is the premise the spec did not have: without it, the 46a corruption check
  is silently disabled for exactly the packages this item teaches to emit a zero-input report.
- **Invariant 41.** `_freeze` already deep-freezes the nested block; the obligation here is a test
  that pins it (mutating `evidence.report["coverage"]` raises), not a mechanism. The pre-existing
  nested-model violation the contract records is untouched and out of scope.
- **Invariant 50.** Route: **archive-and-begin, already mechanized**. No store holds results worth
  keeping (Research Findings), and the compatibility binding refuses to reopen an old store once
  `model_contract_fingerprint` moves. `EVIDENCE_SCHEMA_VERSION` bumps `v1 -> v2` so the lineage split
  is stated rather than merely implied by a fingerprint. Nothing rewrites a stored record — additive
  or versioned, as required, with no owner-visible surfacing needed.

### D8 — Schema versions and landing order

**Versions.** `CATALOG_SCHEMA_VERSION` stays `3.0.0` — this item adds no catalog field (Item 2's
hand-off). `RUNTIME_CONTRACT_VERSION` bumps `1.0.0 -> 2.0.0`: the report shape a runtime reads is that
surface, and a renamed field plus a new required block plus new headline tokens is breaking. TEAx
**replaces** rather than extends both vendored sets — `ACCEPTED_RUNTIME_CONTRACT_VERSIONS = {"2.0.0"}`,
`ACCEPTED_CATALOG_SCHEMA_VERSIONS = {"3.0.0"}` — so an old package fails at seal verification before
any report is read. Deletion over compatibility layers. `TRUSTED_VERIFIER_SHA256` does **not** move:
`contracts/verify.py` reads the version out of the seal data and contains no version literal, so its
bytes are unchanged (verified this stage). No re-vendor of the verifier hash.

**Order, and what breaks if violated.**

0. Probe B3 (does a wholly non-reaching constraint model project a non-`None` catalog?). *Violated →
   D5's trigger is unreadable and the zero-input branch silently never fires.*
1. **Codegen source lands**: coverage account, report schema, templates, precedence, zero-input
   aggregator, trigger supersession, preflight, version bump, regenerated baselines. The three bare
   `all_satisfied` asserts move here. The `test_fusion_tea_real_teax.py:244-259` whole-dump
   expectation is **hand-written from the settled semantics before the test is run** — owner
   sequencing, and the one place in this item where reverse-engineering an expectation from observed
   behaviour would destroy the evidence.
2. **TEAx branch off `fa0e06a`**: vocabulary split, fail-closed lookups, policy + config, vendored
   sets, `expects_report` authority, evidence `v2`, assessment carry, query surface.
3. **Codegen execution lane and cross-repo tests run green** with that branch checked out. This step
   is *after* 2 by necessity, not by preference: codegen's venv imports `simkit` from the TEAx working
   tree, so a new-vocabulary report projected through `PreparedEvaluator` cannot pass against
   unmodified TEAx. *Violated (running step 1's suite before step 2 exists) → a red lane that reads
   like a codegen defect and is not one.*
4. **Publish: codegen first, TEAx second.** *Violated (TEAx first) → a TEAx accepting only
   `3.0.0`/`2.0.0` rejects every package the then-current codegen main produces, and studies stop.*
   Codegen-first is safe because TEAx main already fails closed on `3.0.0` today.

**"Never bump TEAx first" is about publication, not about checkout order.** A local TEAx branch
existing before codegen's suite runs is not a bump; nothing is pushed until both trees are green.
All TEAx work stays on that branch — `main` is never committed to (**[NEED]**, owner).

## Architecture

```
elaborate ──> InstanceGraph.constraint_usages   (Item 2: the whole authored domain)
                     │
project ─────────────┼──> ConstraintCatalog (sealed, fingerprinted)   ── the ONE authority
                     │            │
                     │            ├── coverage_account(catalog)  [generation/coverage.py]
                     │            │            │
                     └──> aggregator module ◄──┘ baked constants
                                  │
generate ────────────────────────>├── schemas/constraint_types.py  (ConstraintReport + CoverageAccount)
                                  ├── modules/…report_aggregator.py (precedence over statuses + account)
                                  ├── pipelines/…yaml               (report channel pinned as exit)
                                  └── contracts/model_contract.json (catalog by value, per-usage detail)
                                  │
preflight ───────────────────────>│  recompute account vs plan; aggregator-iff-usage-rows; seal
                                  ▼
                        [sealed package]
                                  │
TEAx  package_load ──> model_contract ──> expects_report = bool(usage_records)
      evaluate ──> projection: CANONICAL_HEADLINE lookup (fail-closed) ──> ModelEvidence(frozen)
      policy ──> headline -> disposition (+ partial_coverage opt-in) ──> assessment
      store ──> cases row: evidence artifact (report tree, incl. coverage) + assessment_json
```

Data flows one way. The catalog is the only place per-usage coverage detail exists; the report carries
a compact summary derived from it and addressed to it by fingerprint; TEAx re-derives nothing.

## Required Invariants

1. `ConstraintReport.coverage` is present on **every** report, whatever the headline.
2. `assessed_gate_count + unassessed_gate_count == applicable_gate_total`, and
   `sum(unassessed_reasons.values()) == unassessed_gate_count`.
3. `headline == "full_satisfaction"` implies `unassessed_gate_count == 0 and assessed_gate_count > 0`.
4. A `REPORT_AGGREGATOR` module exists **iff** the catalog has at least one usage row; the report
   channel is an exit point whenever the module exists.
5. The coverage account rendered into a package equals `coverage_account(catalog)` for that package's
   sealed catalog. No second inventory, no hand-maintained agreement.
6. Every report token has exactly one canonical counterpart and vice versa; an unknown token on either
   side raises a named error and never yields a satisfied or unconstrained reading.
7. Nothing reachable from `ModelEvidence.report["coverage"]` is mutable.
8. Reopening a study store across the report/catalog schema move raises `IncompatibleStore`.

## Component Overview

- **`generation/coverage.py`** (new, codegen) — `coverage_account(catalog)`: the one derivation. Pure,
  license-free, unit-testable against a hand-built catalog.
- **`templates/constraint_types.py.jinja2`** — gains `CoverageAccount` with its validators;
  `ConstraintReport` gains `coverage`, renames `assessed_count`, and widens `headline`'s `Literal`.
- **`templates/report_aggregator.py.jinja2`** — bakes the account as a constant; implements D6.
- **`generation/modules.py::render_report_aggregator`** — passes the account into the template.
- **`generation/constraint_plan.py`** — carries the computed account so the preflight and the renderer
  read one value.
- **`cli/__init__.py`** — sixth preflight: account recomputation + aggregator-iff-usage-rows.
- **`resolution/models.py::ships_constraint_machinery`** — body changes; home and callers do not.
- **`elaboration/project.py::_build_constraint_modules`** — mints the zero-input aggregator.
- **`contracts/versions.py`** — `RUNTIME_CONTRACT_VERSION = "2.0.0"`.
- **TEAx `evaluation/evidence.py`** — split vocabularies, extended map, `UnknownHeadlineToken`.
- **TEAx `evaluation/projection.py`** — fail-closed lookup; report/catalog fingerprint agreement.
- **TEAx `evaluation/package_load.py`** — re-vendored accepted sets.
- **TEAx `study/policy.py`, `study/config.py`, `study/cli.py`, `study/query.py`** — dispatch, opt-in,
  `expects_report` authority, coverage on the case row.

## Non-Goals

- Touching `agentic-mbse`. Nothing here names a companion surface; if implementation finds one, that
  is a surfacing event, not a quiet edit.
- Any per-usage detail outside the catalog, or a second inventory of any kind.
- Changing Item 2's disposition vocabulary, usage-tier schema, or totality gate.
- Fixing the pre-existing nested-model invariant-41 violation the contract records.
- CATF migration and intent classes (Item 5); calc-def gate execution (Item 6).
- Changing `BLOCK`-halts-generation semantics; executing requirement satisfaction; an evaluated
  advisory tier for plain constraints.
- Aggregation-by-definition with drill-down — not built, and not foreclosed: the account is a summary
  addressed to the catalog, so a later drill-down reads the catalog rather than needing new report
  fields.

## Implementation Notes

- **Probe B3 first.** One generation run on a fixture whose constraint usages are all non-reaching,
  checking `graph.constraint_catalog is not None`. Everything in D5 rests on it.
- **`catf_mfe_d5` is the descriptive-only fixture**, not a partial one: all 65 usages are bare
  `constraint`, so it reads `not_assessed` with `authored_usage_total = 65` and
  `applicable_gate_total = 0`. That number appearing in a report is this epic's headline evidence.
- **Baselines churn broadly.** Every constraint-bearing baseline regenerates; fixtures that previously
  generated no aggregator gain one. Constraint-free fixtures must stay byte-identical (LC-E12) — that
  is the gate that proves the trigger did not widen. Two stale-baseline classes are known and
  pre-existing (`deep_cross_scope`, `plant_values`); do not absorb them.
- **Gates:** `/home/reid/1cfe/item7-rebuild-venv/bin/python -m pytest`, never `uv run`. License via
  `set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a`; a green run with license-skip lines is
  not a run. TEAx suite from `/home/reid/1cfe/teax/packages/teax-simkit` (`pytest`, `testpaths =
  simkit/tests`).
- **Do not ruff-format generated baselines** — generator-owned bytes.

## Potential Risks

- **Wrong-but-confident counts (B1).** Mitigated by deriving from the sealed catalog only, by the
  arithmetic validators, and by the preflight — but a systematic misreading of a disposition token
  would pass all three. Mitigation: the six-state matrix is pinned against **hand-written** expected
  accounts per fixture, never against generated output.
- **The cross-repo red window (step 3).** Between codegen's source landing and the TEAx branch, the
  codegen execution lane is red for a non-defect reason. Mitigation: land them in one working session
  and record the intermediate state in `verification.md` so a later reader does not mistake it for a
  regression.
- **`RUNTIME_CONTRACT_VERSION` bump blast radius.** Any other consumer of a sealed package is refused
  after the bump. Known consumers are TEAx and codegen's own tests; the fusion/stellarator demo
  branches are local and pinned, and are not re-generated by this item.
- **Two readings of the report-required rule** (`project.py` over the domain, seams over the catalog).
  Mitigated by making the correspondence a preflight check rather than a convention.

## Integration Strategy

This completes the chain Items 1 and 2 started: Item 1 fixed the meanings, Item 2 made the catalog own
the complete domain, and this item makes the report and the study consume it. It replaces the
not-failed headline and Item 2's interim `ships_constraint_machinery` rule; it adds nothing beside the
catalog and retires nothing else. Item 5's CATF migration will read the same account to show its
all-65 disposition table, and Item 6's calc-def gates enter the denominator through the same
`applicable_gate_total` without a report change.

## Validation Approach

Pinned independently, each by a test no other state satisfies:

1. **Six-state matrix, twice** — five report headline values plus report-absent, and six runtime
   dispositions. Expected accounts hand-written from the settled semantics.
2. **Violation + non-full coverage** — one violated gate, at least one unassessed applicable gate:
   headline `violation`, `coverage_state "partial"`, and the counts present in the case record.
3. **Full satisfaction is unclaimable under partial assessment** — some gates assessed, all passing.
4. **Both zero-input branches** — descriptive-only → `not_assessed`; asserted gates with zero eligible
   entries → `partial_coverage`; both with a retained exit-point channel.
5. **D4's ruling** — all asserted gates inapplicable → `not_assessed` with positive
   `inapplicable_gate_count`.
6. **Divergence refusals** — perturb the plan's account, and perturb the catalog after sealing; each
   observes its named refusal.
7. **Unknown tokens fail closed** — a hand-built report with an unmapped token on the report side, and
   an unmapped canonical token on the runtime side; both name an error, neither reads satisfied.
8. **Invariant 41** — mutating the nested coverage block through evidence raises.
9. **Invariant 50** — reopening a store across the fingerprint move raises `IncompatibleStore`.
10. **Cross-repo pins** — codegen's version drift test extended to `RUNTIME_CONTRACT_VERSION`; TEAx
    pins the token map against a codegen-generated fixture package.
11. **Three-route parity** — live, snapshot, relocated agree on report bytes including the account.
12. **Byte stability** — constraint-free fixtures unchanged.

New fixtures required: asserted-with-zero-eligible, all-inapplicable, mixed-partial, and
violation-plus-partial. Reuse `catf_mfe_d5` for descriptive-only.

## Next-Stage Handoff

- **Fixed:** the token map (D1), the block shape and field names (D2), generation-time derivation
  (D3), the D4 ruling, the report-required trigger (D5), the precedence function (D6), keep-for-
  boundary default with fingerprint-bearing opt-in (D7), version moves and landing order (D8).
- **Open for the plan:** fixture authoring specifics; whether the sixth preflight is one function or
  two; exact `query.py` column surface; where the hand-written fusion coverage block is recorded
  before it is run.
- **De-risk first:** probe B3, then hand-write the `test_fusion_tea_real_teax.py` expected account —
  both are cheap and both gate work that would otherwise be redone.

---
**Next Step:** `/_my_design_review` (fresh session), then `/_my_plan`.

## Appendix A — Product-lens ledger entry (design stage)

Appended to `.project/active/constraint-coverage-policy/product-lens.md` at the same time as this
design; reproduced here so the design is self-contained. **Provenance flag:** the runner script
`/home/reid/.claude/scripts/product-lens.md` is outside this session's sandbox; the method is
reconstructed from the spec-stage entry in that ledger and from Item 2's, per this epic's convention.

**Point** (re-derived from sources, unchanged from the spec-stage entry; all five items still hold and
are not restated). **Falsifier** (unchanged): a constraint-bearing model that still emits no report; a
coverage number computed from anything but the catalog; a state present in one vocabulary only; a
study store silently rebound.

**Findings**

- **design-F1 [DONE, in this design] — the `expects_report` authority was about to be silently
  invalidated.** `study/cli.py:42` derives it from `concrete_entries`. D5 makes a package with zero
  concrete entries ship a report, which would turn off the 46a corruption check for precisely those
  packages. Not visible from the codegen repo; found by reading TEAx first-hand this stage. Owned by
  D7.
- **design-F2 [FILED, Item 1 territory] — Appendix C's vacuous-gate cell over-permits in the
  degenerate case.** Its conditional presupposes surviving gates; read literally it also licenses
  `full_satisfaction` for a model with none. D4 rules against that reading with its reasoning
  published; the cell wants "…and at least one gate remains" at close.
- **design-F3 [ACCEPTED, recorded] — the epic's scope-4 wording stays looser than the contract.** D5
  follows LC-E10. The spec already surfaced this; nothing new to resolve, and the epic text still
  wants the correction at close.

**Not findings (checked, clean):** no owner-graded statement is contradicted — D-1, D-2 and D-3 are
untouched, and D3's one-direction derivation is the correct invariant-48 posture. The
`[OWNER-VERBATIM]` design-search quote is carried whole in The Point at the owner's emphasis. The
`[NEED]` sequencing instruction is honoured explicitly in D8 step 1, including the prohibition on
reverse-engineering the fusion expectation. Q6's defaults are reproduced exactly in D7. Invariants 32
(both halves), 41 (both halves), 48, 49, 50, and 61 are each carried whole rather than to the clause
this design needed. Invariant 50's route is resolved by verified fact, not by assumption, and required
no owner-visible surfacing.

**Gate: DISPOSED (design-F1..design-F3)** — nothing blocks. The one finding that changes the build
(design-F1) is owned inside this design; the other two are records for close.
