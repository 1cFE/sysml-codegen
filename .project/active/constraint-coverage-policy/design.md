# Design: Coverage Report and TEAx Policy (CONSTRAINT-SEMANTICS Item 3)

**Status:** Draft — rev 2 (design review DR-1..DR-13 incorporated 2026-08-12)
**Owner:** Reid W
**Created:** 2026-08-12
**Branch:** `item7-rebuild` (codegen worktree `/home/reid/1cfe/sysml-codegen-item7-rebuild`, rev 1 at
`01c4b34`, review at `328032e`); coordinated change in TEAx (`/home/reid/1cfe/teax`, branch off
`main` `fa0e06a`)
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
- **Design review:** `.project/active/constraint-coverage-policy/design-review.md` (verdict Revise;
  DR-1..DR-13, resolutions recorded there by ID)
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

Every TEAx line number below was read first-hand at `fa0e06a` (clean, read-only). Codegen citations
are at `328032e`. **corrected** marks a fix to the spec's second-hand cites; **rev 2** marks a fix the
design review found in rev 1.

**TEAx, verified.**

- `CANONICAL_HEADLINE` lives in `packages/teax-simkit/simkit/evaluation/evidence.py:44-51`
  (**corrected** — the spec cites `evaluation/projection.py`, which only *imports* it). It maps four
  report tokens onto `ResponseEntry`, and `ResponseEntry` (`evidence.py:40`) is **one type doing two
  jobs**: per-constraint status and aggregate headline.
- The normalization seam is a bare subscript: `projection.py:59`. An unmapped token is a `KeyError`
  today — exactly what invariant 46a forbids.
- `study/policy.py` has **two** dispatch tables: `_DISPOSITION_BY_HEADLINE:32-37` (`DispositionPolicy`)
  and `_HEADLINE_DISPOSITION:76-80` (`ObjectivePolicy`, the real study path), subscripted at `:70` and
  `:135`. Both are bare. `unconstrained` is produced by the *absence* of a headline key
  (`policy.py:65-68`, `:112-116`).
- **"Does this package ship a report" is answered twice on the consumer side** (**rev 2**, DR-2):
  `study/cli.py:42` (`bool(load_model_contract(...).concrete_entries)`) and
  `evaluation/evaluator.py:79-87` (`_report_declared_in_spec`, the default for both
  `PreparedEvaluator:139-143` and `FileBackedEvaluator:243-246`), whose docstring states the coupling
  outright: *"The study layer overrides this with the catalog authority; the two must agree."*
  Fourteen test call sites rely on that default; one production caller passes the flag. Owned by D7.
- `ACCEPTED_CATALOG_SCHEMA_VERSIONS = {"2.0.0"}`, `ACCEPTED_RUNTIME_CONTRACT_VERSIONS = {"1.0.0"}`,
  `TRUSTED_VERIFIER_SHA256` at `package_load.py:33/39/47`; `study/model_contract.py:46-51` fails closed
  on an unaccepted catalog version before reading any field. **The fail-closed window Item 2 opened is
  already open** — codegen ships `3.0.0` today, so TEAx main already refuses every newly generated
  package at the study seam. That is what makes "codegen first" safe. `ModelContractData` already
  carries `usage_records` (`model_contract.py:36`), so D7's authority move is a one-word change.
- **Durable case records:** `study/store.py:62-71` — one `cases` row per candidate with
  `evidence_digest` and `assessment_json`. The artifact is the encoded `ModelEvidence`, whose `report`
  field is the generated report's whole `model_dump(mode="json")` tree (`evidence.py:87-90`), passed
  through by `study/evidence_io.py:47-56` without a second dump. **Coverage reaches the durable record
  for free** the moment it is a report field, on the prepared and file-backed routes alike.
- **Invariant 50's carrier (rev 2, DR-5).** Rev 1 said a catalog/report schema move changes
  `model_contract_fingerprint`. It does not, for the packages that could have a store. That
  fingerprint is codegen's `semantic_fingerprint` over five inputs only — `parameters`, `outputs`,
  `constraint_catalog`, `evaluation_semantics`, `catalog_schema_version`
  (`contracts/model_contract.py:59-70`, verified). This item adds no catalog field and keeps
  `CATALOG_SCHEMA_VERSION` at `3.0.0`, so for an already-constraint-bearing package whose channel set
  does not change, all five are byte-identical. The real carriers are `evidence_schema_version`
  (`v1 -> v2`, D7) and `executable_fingerprint` (the generated bytes move); both are bound fields in
  `Compatibility` (`study/compatibility.py`), and `store.py:147-151` raises `IncompatibleStore` on any
  disagreement. The conclusion survives, over-determined; the mechanism is corrected.
- **No durable study store with results worth keeping exists.** The only `study.db` files in the tree
  are two archived spike work dirs under
  `.project/completed/20260713_constraint-study-integration-spike/_work/`. The spec's open question
  resolves to **no**, and the item is not undersized on that account.
- `_freeze` (`evidence.py:17-28`) recurses mappings and sequences at attach, so a nested `coverage`
  object inside `report` becomes a `MappingProxyType`. Invariant 41 needs a test here, not a mechanism.
- `PolicyConfig` (`study/config.py:41-44`) is a `StrictBaseModel` digested whole into
  `StudyConfig.semantic_fingerprint()` (`config.py:61-73`, **rev 2** — the digest is the whole method,
  not the single line rev 1 cited), which becomes `study_definition_fingerprint`. A new policy field
  is auditable in YAML *and* identity-bearing by construction.

**Codegen, verified.**

- The headline is computed in `templates/report_aggregator.py.jinja2:44-58` from statuses alone;
  `templates/constraint_types.py.jinja2:24-29` is the four-field `ConstraintReport`.
- The aggregator is minted at `elaboration/project.py:892-919`, and `:892` (`if not
  constraint_outputs: return`, **rev 2** — rev 1 cited `:891`) is the line that suppresses it for a
  constraint-bearing model.
- **Closed vocabularies** (`elaboration/graph.py`): `ASSERTED_SOURCE_FORMS:244`,
  `SOURCE_FORMS:247-256`, `DISPOSITION_REASONS:259-278` (nine non-`admitted` reasons across three
  kinds; reason tokens are unique across kinds, so no compound key is needed), `expected_severity:292`.
  The catalog row spells the marker `inapplicability_reason` (`resolution/models.py:519`); the graph
  record spells it `inapplicability` (`graph.py:318`). `coverage_account` sees the **catalog**
  spelling (**rev 2**, DR-10).
- **The marker is read independently of the disposition.** `_read_annotation`
  (`elaborate.py:1188-1235`) reads `@inapplicable:` off the usage's documentation and never raises; a
  malformed marker becomes an error-grade disposition (`classification_incomplete`). Item 2's own
  field docstring: it "never rewrites the disposition beside it." So an **eligible** usage carrying
  the marker is reachable — the hidden false bet the review found. Owned by D9.
- **Exit-ancestor retention already exists.** `generation/pipeline.py:284-296` pins every
  `REPORT_AGGREGATOR` output channel into the exit points structurally.
- `render_report_aggregator` (`generation/modules.py:353-380`) already bakes `catalog_fingerprint` and
  `EXPECTED_IDS` as generation-time constants. Baking coverage is the same move.
- One rule, three seams: `ships_constraint_machinery` (`resolution/models.py:644-656`), read by
  `generation/registry.py:353-362`, `cli/__init__.py:404-414` (which carries a redundant `catalog is
  not None and …` guard at `:411`), and `cli/__init__.py:455-464`. `has_executable_content`
  (`models.py:596`) has exactly **one** caller in the tree — `ships_constraint_machinery` itself.
- The divergence check has a template: `_preflight_constraint_totality` (`cli/__init__.py:316-399`).
- The four `all_satisfied` assertions: `tests/execution/test_constraint_verdicts_exact_route.py:171,
  416, 540` (bare) and `tests/execution/test_fusion_tea_real_teax.py:245` (whole-dump). No committed
  baseline carries a headline token — `tests/fixtures/baseline_outputs/*` holds only
  `registry_init.py` and `computation_graph.json`. `modeling-assumptions.md:551-554` mentions
  `all_satisfied` inside ADR-009's frozen "what the contract said" quotation and must **not** move.
- **Cross-repo coupling, measured:** `/home/reid/1cfe/item7-rebuild-venv/bin/python -c "import
  simkit"` resolves to `/home/reid/1cfe/teax/packages/teax-simkit/simkit/__init__.py`, and
  `PreparedEvaluator.evaluate` (`evaluation/evaluator.py:184`) calls `project(...)`, which subscripts
  `CANONICAL_HEADLINE`. A codegen test that evaluates a new-vocabulary report goes red until the TEAx
  branch is checked out. This governs D8's order and is not optional colour.

## Core Concept

The report gains a second, orthogonal fact. Today it carries one summary token computed from whatever
results happened to arrive. After this item it carries **a headline** — still one precedence-ordered
token — **and a coverage account**: how many constraint usages the model authored, how many of them
are applicable asserted gates, how many of those were actually assessed, and why the rest were not.
The account is computed once at generation from the embedded catalog by a total function over Item 2's
closed vocabularies, and baked into the aggregator as constants, exactly the way the catalog
fingerprint already is, because coverage is a property of the model and not of the design point. The
headline then becomes a function of the runtime statuses *and* the baked account: full satisfaction is
claimable only when the account says nothing was left unassessed. Because the account is always
present, a `violation` report still says how much was checked — and since TEAx's evidence artifact
already stores the report tree whole, that reaches the durable case record without anyone carrying it
there.

The key insight is that "partial" was never a kind of satisfaction. It is a statement about the
denominator. Once the denominator is a first-class field computed by a rule anyone can check, the
headline stops being the only place coverage can live, the crossing rules in the contract resolve
cleanly, and the study policy has something concrete to be conservative about.

## Key Bets

- **B1.** Item 2's `catalog.usage_records` is a complete and correct enumeration of every authored
  constraint usage, with a correct disposition and `occurrence_count` on each. *If false → the report
  states confident coverage numbers that are wrong, which is strictly worse than today's silence,
  because a wrong number is trusted.* Mitigation is specified in Potential Risks and is load-bearing:
  expected accounts are derived from each fixture's **SysML source**, never from a catalog dump.
- **B2.** Coverage is a generation-time constant: which gates are applicable and which were assessed
  depends on the model, never on the candidate's input values. *If false → baking is invalid and the
  account must be computed per evaluation from data the aggregator does not have.*
- **B3.** A constraint-bearing model always projects a non-`None` `constraint_catalog` at Item 2's
  HEAD, including one whose usages are *all* non-reaching. *If false → the report-required trigger
  cannot be read from the catalog for exactly the models the zero-input branch exists to serve, and
  the trigger must move to the instance graph's domain.* One generation run on an existing fixture; a
  `/_my_spike` is not warranted.
- **B4.** No durable study store holds results worth keeping, and TEAx's eight-field compatibility
  binding refuses to reopen a store once a bound field moves. *If false → the transition is real
  migration work, this item is undersized, and that is an owner-visible decision, not a design call.*
  Verified this stage; **the binding field that carries it is `evidence_schema_version`, not
  `model_contract_fingerprint`** (Research Findings, D7).
- **B5.** Renaming `all_satisfied` makes every stale reader fail closed rather than quietly misread
  the strengthened claim. *If false — a reader that defaults on an unknown token — the rename hides a
  wrong reading instead of exposing it.* Mitigated by D1's fail-closed obligation on both sides and by
  the two-repo sweep recorded in Research Findings.

## Key Decisions

### D1 — Token spellings: mirror the contract's own state names

The report vocabulary becomes the contract's five state names, mechanically transliterated:
`violation`, `indeterminate`, `full_satisfaction`, `partial_coverage`, `not_assessed`. The canonical
runtime vocabulary keeps its verdict-shaped spellings and gains one state.

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
(pydantic refuses an unknown token at construction). The runtime side replaces all three bare
subscripts (`projection.py:59`, `policy.py:70`, `policy.py:135`) with an explicit lookup raising a new
named `UnknownHeadlineToken` beside `CorruptConstraintEvidence` in `evidence.py`. It is **not** an
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
    unassessed_reasons: dict[str, int]     # reason token -> count; sums to unassessed_gate_count
    coverage_state: Literal["complete", "partial", "none"]
```

`ConstraintReport.assessed_count` is renamed `assessed_entry_count` and keeps its occurrence-tier
meaning (`len(results)`). The two tiers are now unmistakable in the field names, which is what the
spec's `[INFERRED]` two-tier rule demands.

**The histogram keys are derived, not listed (rev 2, DR-3).** Rev 1 published seven reason tokens
where a rule belongs. The rule is in D3's bucket table: a key appears iff some usage record lands in
the *unassessed gate* bucket carrying that reason, and the count is how many did. No zero-filled keys,
no hand-maintained list to drift against `DISPOSITION_REASONS`. Which of Item 2's nine non-`admitted`
reasons can appear is a consequence of the table, not an input to it.

`coverage_state` is the coverage axis itself, carried so it survives a higher-precedence headline:
`complete` when `applicable_gate_total > 0 and unassessed_gate_count == 0`, `partial` when
`applicable_gate_total > 0 and unassessed_gate_count > 0`, `none` when `applicable_gate_total == 0`.

*Rejected: flat fields on `ConstraintReport`.* Six loose counts read as peers of `headline` and
`results`, and TEAx would have to reassemble them to hand coverage to a case record as one thing.
*Rejected: keeping `assessed_count` for the occurrence tier.* We pay a breaking schema bump either
way, and a reader must not have to guess which tier it means. The catalog join stays where it already
is: the report's existing top-level `catalog_fingerprint`, which addresses the per-usage detail in
`contracts/model_contract.json`. The block carries no per-usage rows — invariant 48, one authority.

**The two tiers can look surprising, legitimately (rev 2, DR-12).** `assessed_entry_count` counts
occurrences and `assessed_gate_count` counts usages, so one gate over forty occurrences reads
`assessed_gate_count = 1, assessed_entry_count = 40`. That asymmetry is the two-tier rule working and
is pinned by a deliberate test. The *other* corner the review named — a non-empty `results` list beside
`assessed_gate_count == 0` — is **unreachable** under D9's refusal, and Required Invariant 9 states why.

### D3 — Derivation runs at generation, by a total function, checked from both ends

One pure function, `generation/coverage.py::coverage_account(catalog) -> CoverageAccount` shape,
computed once into `ConstraintGenerationPlan`, rendered into the aggregator as baked constants beside
`CATALOG_FINGERPRINT` and `EXPECTED_IDS`.

**The bucket table (rev 2, DR-1).** Every `ConstraintCatalogUsageRecord` lands in exactly one bucket.
Two predicates over the closed vocabularies decide it:

- **asserted** ≡ `source_form in ASSERTED_SOURCE_FORMS` (`graph.py:244` — `definition_typed`, `inline`,
  `named_usage_reference`; the other three forms in `SOURCE_FORMS` are not asserted)
- **inapplicable** ≡ `inapplicability_reason is not None` (catalog spelling, `models.py:519`)

| # | asserted | inapplicable | `disposition_kind` | bucket | contributes to |
|---|---|---|---|---|---|
| 1 | no | either | any | **inventory only** | `authored_usage_total` |
| 2 | yes | yes | any | **inapplicable gate** | `authored_usage_total`, `inapplicable_gate_count` |
| 3 | yes | no | `eligible` | **assessed gate** | `authored_usage_total`, `applicable_gate_total`, `assessed_gate_count` |
| 4 | yes | no | `excluded` \| `non_reaching` | **unassessed gate** | `authored_usage_total`, `applicable_gate_total`, `unassessed_gate_count`, `unassessed_reasons[reason] += 1` |

Row 2 combined with `disposition_kind == "eligible"` is the authoring contradiction D9 refuses; it is
listed as a row so the table stays total, and the refusal is where the combination is handled rather
than counted. `disposition_kind` is closed to those three values by `DISPOSITION_REASONS`, and
`_preflight_constraint_totality` already refuses an unknown kind/reason pair, so the four rows are
exhaustive and mutually exclusive. `authored_usage_total = len(usage_records)` falls out as the sum.

**Why the rows sit where they do**, against the contract's own words: row 1 is "plain and
requirement-side usages are never applicable asserted gates"; row 2 is "a usage stops being applicable
only when it carries an explicit inapplicability disposition"; rows 3 and 4 are the form-not-predicate
test — an asserted gate the profile excluded or that reached nothing stays in the denominator as an
unassessed one, which is why `excluded` and `non_reaching` share a bucket. Nothing in the table
consults the predicate.

**The reason vocabulary is pinned, and grows loudly (rev 2, DR-3).** `generation/coverage.py` holds a
frozen `KNOWN_REASONS` set — the vocabulary this derivation was written against — and compares it
against `DISPOSITION_REASONS` at preflight, not only when a record happens to carry a token. If Item 2
ever adds a reason, generation refuses by name: *"coverage derivation has not been taught reason
`<token>`: rule whether it sits inside or outside the feasibility denominator."* A new cause for a
gate not being assessed genuinely needs a coverage ruling, so silently bucketing it would be the
failure, not the inconvenience.

**Divergence is a failure at two ends.**

1. **Generation preflight** (a sixth check beside the five existing ones, in `cli/__init__.py`):
   recompute the account from the catalog and refuse if it differs from the plan's, with a named
   `CodeGenerationError`. The existing `_preflight_constraint_totality` seal check already covers a
   catalog perturbed after projection sealed it.
2. **Report construction**: `CoverageAccount` carries validators pinning the arithmetic identities
   (`assessed + unassessed == applicable_gate_total`, `sum(unassessed_reasons.values()) ==
   unassessed_gate_count`, `coverage_state` agrees with the counts). An internally inconsistent bake
   cannot construct.

**Dropped from rev 1 (DR-7):** a third, runtime "check" comparing the report's `catalog_fingerprint`
against the model contract's. It proves the report and the catalog are the same catalog; it verifies
no account. It could only ever fail on a codegen defect *inside one seal-verified package*, and it
would have been a third consumer-side re-derivation of a producer fact added in the same breath as
DR-2 removes the second. The real runtime protection is the package seal over the bytes. Deleted, not
demoted.

*Rejected: computing the account in the aggregator at runtime from embedded catalog data.* The catalog
ships in `contracts/model_contract.json`, outside the importable pipeline path; making the aggregator
read it would add file I/O to a pure module and a second reader of the catalog inside the generated
package, and would recompute a constant once per candidate.

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
   but no applicable asserted gate at all" (contract `:459-460`).
3. State 3 defines full satisfaction as "every applicable asserted gate was **assessed** and passed" —
   a claim about assessment having happened. Zero assessments cannot support it.
4. The governing obligation breaks the tie: no report may claim more coverage than was assessed.
   `full_satisfaction` is the strongest claim in the vocabulary, and awarding it for zero assessments
   is today's `all_satisfied` defect wearing a new token.
5. Nothing is lost. A descriptive-only model has `inapplicable_gate_count = 0`; an all-inapplicable
   model has it positive. A consumer that wants "all gates were deliberately waived" reads that field.

**Contract consequence to carry to close:** Appendix C's cell, read literally, permits the other answer
in the degenerate case. It wants "…and at least one gate remains" added. Filed, not performed.

### D9 — RULING: an inapplicability marker on an assessed gate is refused, loudly

*(Numbered D9 because it was added at rev 2; it belongs beside D4 and is cross-referenced from D3 and
D6.)*

**The reachable shape.** `@inapplicable:` is read off the usage's documentation at mint
(`elaborate.py:1188-1235`) independently of the disposition, and Item 2 states it "never rewrites the
disposition beside it." So an asserted usage whose owner *does* expand, which produces concrete entries
and real verdicts, can also carry the marker. Rev 1 bet silently that this could not matter. It can.

**Ruling.** A usage record with `disposition_kind == "eligible"` and `inapplicability_reason is not
None` is an **authoring contradiction** and refuses generation by name, at the coverage preflight,
before any output is written: *"`<usage QN>` (`<declaration_id>`) is marked inapplicable but produced
`<n>` executable entries: an inapplicability marker states a gate is not part of the feasible set, and
this gate ran."* It is never silently dropped from the denominator.

**Reasoning.**

1. **The risk decides it.** The alternative — honour the marker and drop the gate — makes an
   annotation a silent kill-switch for a live gate. Someone could delete a failing physics check from
   the feasible set with one doc comment, and the report would say `full_satisfaction` over a
   denominator that quietly shrank. That is the exact class of defect this epic exists to end, and it
   would be reintroduced by the mechanism meant to make coverage honest.
2. **It is a directive defect, and Item 2 already grades those loudly.** A malformed `@inapplicable:`
   marker is already an error-grade disposition that the completeness gate turns into a named halt
   (Item 2 audit A3/R2). A well-formed marker whose *meaning* contradicts the model is the same kind of
   defect — the directive cannot be honoured — and gets the same treatment.
3. **Inapplicability remains legitimate everywhere it was meant to be.** Rows 2 and 4 of D3's table
   still apply to unassessed gates: a vacuous gate (invariant 61's case), a `non_numerical` one, a
   non-reaching one. What is refused is exclusively the gate that demonstrably ran. `eligible` is
   decided only for a usage that expanded to at least one scope (Item 2's precedence step 3), so
   `eligible` ⇔ "it produced entries" and the refusal condition needs no separate occurrence test.
4. **It makes the accounting total instead of ambiguous.** With the refusal, an inapplicable gate never
   has concrete entries, therefore never contributes a result, therefore never contributes a status.
   D2's arithmetic cannot break, D6's top arm cannot fire from a non-applicable gate (contract state 1
   requires an **applicable** gate), and D4's edge case has no results list to surprise anyone with.
   One refusal removes three separate unhandled interactions.

*Rejected: honour the marker and drop the gate silently* — reason 1. *Rejected: count it in
`assessed_gate_count` while excluding it from `applicable_gate_total`* — arithmetically impossible
against D3's identity, and it would report a gate as assessed that the author declared out of scope.
*Rejected: forbid the combination at authoring time in Item 2* — that is an Item 2 schema/mint change
and a surfacing event, and it is the wrong layer: the contradiction is only visible once you ask the
coverage question, which is this item's question. **Filed as a follow-on:** the companion's authoring
validation should advise on this at authoring time, where it is actionable (Item 2's D10 puts authoring
advisories in the companion). Not built here.

### D5 — The report-required trigger, stated once

A report is required **iff the model authors at least one constraint usage** — i.e.
`catalog.usage_records` is non-empty. `ships_constraint_machinery` keeps its name and its single home
(`resolution/models.py`); only its body changes, from `bool(concrete_entries)` to
`bool(usage_records)`. Item 2's A4 cure is preserved: the rule still lives in one place, and what
changes is what it says, exactly as its docstring anticipated. **`has_executable_content` is deleted**
(rev 2, DR-8) — `ships_constraint_machinery` is its only caller in the tree, and keeping a property
with no reader for a hypothetical future one is the shim this epic's bar rejects.

`project.py:892`'s early return becomes conditional on the same population, read from the instance
graph's `constraint_usages` domain. Two readings of one rule is the drift A4 exists to stop, so the new
coverage preflight closes it as a check: a graph carries a `REPORT_AGGREGATOR` module **iff** its
catalog has usage rows, refused by name either way.

**What the three seams then do (rev 2, DR-11).** The rule change has a per-seam consequence, and a
descriptive-only package like `catf_mfe_d5` (65 bare constraints, zero concrete entries) is the shape
that shows it. It starts emitting `schemas/constraint_types.py` (`cli/__init__.py:455-464`); starts
importing `ConstraintEvaluation`/`ConstraintReport` in its registry (`generation/registry.py:353-362`);
and starts running the constraint-name-safety preflight (`cli/__init__.py:404-414`) over an empty entry
set. All three are correct — the package now genuinely ships a report. While there, collapse the
redundant `catalog is not None and …` guard at `cli/__init__.py:411`, which exists only to narrow the
type and is now covered by the rule itself.

*Rejected: triggering on "no applicable asserted gate".* That is the epic's scope-4 wording; it leaves
a model whose asserted gates all produced zero eligible entries with no aggregator, which is the
partial-coverage branch LC-E12 and Appendix C both require to exist. The contract is the later and more
specific authority.

### D6 — Headline precedence: statuses decide the top two, the account decides the rest

Computed in the aggregator, over the runtime statuses and the baked account:

```
violated in statuses                                   -> "violation"
indeterminate in statuses                              -> "indeterminate"
unassessed_gate_count == 0 and assessed_gate_count > 0 -> "full_satisfaction"
applicable_gate_total > 0                              -> "partial_coverage"
otherwise                                              -> "not_assessed"
```

**The status set contains only applicable assessed gates, by construction** (rev 2, DR-4). Contract
state 1 requires "at least one **applicable** asserted gate was assessed and failed", so the top arm
must not fire from a gate outside the denominator. It cannot: an inapplicable gate is either unassessed
(no entries, no results) or refused by D9. No applicability filter is needed at runtime, and adding one
would be a second place the rule lives. Required Invariant 9 states the property the refusal buys.

Result-list non-emptiness stops deciding anything (it was the whole defect). The account is emitted in
every report regardless of which arm fired, which is the two-axes ruling in code: a `violation` report
carries `coverage_state = "partial"` and its counts, and TEAx can separate "rejected on physics, fully
covered" from "rejected on physics, sixty gates unchecked".

### D7 — TEAx policy, config, and one authority for "ships a report"

- **Vocabulary split.** `ResponseEntry` stops doing two jobs: `ConstraintStatus` (three values, per
  constraint) and `HeadlineResponse` (five values) become distinct, and the `responses` mapping is
  typed as their union. *Rejected: one widened type* — cheaper, and it would have implied a
  per-constraint status can be partial.
- **Dispatch.** Both tables gain the state: `ObjectivePolicy`'s `_HEADLINE_DISPOSITION` maps
  `partial_coverage -> keep-for-boundary` (the conservative default), and `DispositionPolicy`'s
  `_DISPOSITION_BY_HEADLINE` maps it to a `partial_coverage` **disposition** (rev 2, DR-9 — that
  table's values are dispositions surfaced as `CaseView.disposition` from `assessment_json`,
  `study/query.py:130`; the `cases.state` lifecycle column is untouched and needs no migration). Both
  subscripts become fail-closed lookups (D1).
- **Opt-in.** `PolicyConfig` gains
  `partial_coverage: Literal["keep-for-boundary", "feed-strategy"] = "keep-for-boundary"`. One visible
  YAML line; `extra="forbid"` fails closed on a typo; and because the whole policy block is digested
  into `study_definition_fingerprint` (`config.py:61-73`), flipping it **starts a new study lineage**
  instead of silently changing a running study's meaning.
- **Opted-in behaviour.** `partial_coverage` then takes the identical path `satisfied` takes —
  objective values against `penalty_threshold`, yielding `penalize` or `feed-strategy`. *Rejected: a
  third bespoke path*, which would produce a disposition no configuration can explain. The assessment
  record always carries `headline: "partial_coverage"`.
- **One authority for "does this package ship a report" (rev 2, DR-2).** The consumer side answers this
  twice today. The fix is removal, not re-syncing:
  - `study/model_contract.py` gains one function, `ships_constraint_report(contract) ->
    bool(contract.usage_records)` — the same population as the producer's D5 trigger. `study/cli.py:42`
    calls it, replacing the `concrete_entries` read.
  - `_report_declared_in_spec` (`evaluator.py:79-87`) is **deleted**, and
    `expects_constraint_report` becomes a required constructor argument on `PreparedEvaluator` and
    `FileBackedEvaluator`. The evaluation layer is isolation-clean and genuinely has no catalog
    authority; inventing one from the pipeline spec is what the "the two must agree" docstring was
    papering over. Fourteen evaluation-layer test call sites pass the flag explicitly, which turns a
    silent derivation into a stated expectation at each site.
  This is D5's standard applied across the repo boundary — the same reason the design makes the two
  codegen-side readings a preflight check rather than a convention. Without it, the invariant-46a
  corruption check (`projection.py:50-55`) would silently switch off for exactly the zero-input
  packages this item teaches to emit a report, which is `design-F1` one layer out.
- **Coverage into durable case records, two carriers.** The evidence artifact already contains the
  whole report tree including `coverage` — that is existence, on the prepared and file-backed routes
  alike (`evidence_io.py:47-56`). Additionally `assessment_json` carries `coverage` verbatim plus
  `catalog_fingerprint`, and `query.py` surfaces them on the case row, so a study query answers "how
  covered was this candidate" without opening artifacts. Policy copies; it never writes evidence
  (invariant 49).
- **Invariant 41.** `_freeze` already deep-freezes the nested block; the obligation is a test that pins
  it, not a mechanism. The pre-existing nested-model violation is untouched and out of scope.
- **Invariant 50 (rev 2, DR-5).** Route: **archive-and-begin, already mechanized**. No store holds
  results worth keeping, and the store refuses to reopen once a bound `Compatibility` field moves. The
  carrier is **`evidence_schema_version`, bumped `v1 -> v2`** — the primary mechanism, not a
  legibility nicety, because `model_contract_fingerprint` can be byte-identical across this item
  (Research Findings). `executable_fingerprint` also moves, so the refusal is over-determined; the test
  pins the `evidence_schema_version` carrier specifically, since one that varied only the model
  contract could pass today and silently stop proving anything. Nothing rewrites a stored record —
  additive or versioned, as required, with no owner-visible surfacing needed.

### D8 — Schema versions and landing order

**Versions.** `CATALOG_SCHEMA_VERSION` stays `3.0.0` — this item adds no catalog field (Item 2's
hand-off). `RUNTIME_CONTRACT_VERSION` bumps `1.0.0 -> 2.0.0`: the report shape a runtime reads is that
surface, and a renamed field plus a new required block plus new headline tokens is breaking. TEAx
**replaces** rather than extends both vendored sets — `ACCEPTED_RUNTIME_CONTRACT_VERSIONS = {"2.0.0"}`,
`ACCEPTED_CATALOG_SCHEMA_VERSIONS = {"3.0.0"}` — so an old package fails at seal verification before
any report is read. `TRUSTED_VERIFIER_SHA256` does **not** move: `contracts/verify.py` reads the
version out of the seal data and contains no version literal, so its bytes are unchanged (verified).

**Order, and what breaks if violated.**

0. Probe B3 (does a wholly non-reaching constraint model project a non-`None` catalog?). *Violated →
   D5's trigger is unreadable and the zero-input branch silently never fires.*
1. **Codegen source lands**: coverage account and its bucket table, report schema, templates,
   precedence, zero-input aggregator, trigger supersession, D9's refusal, preflight, version bump,
   regenerated baselines. The three bare `all_satisfied` asserts move here. The
   `test_fusion_tea_real_teax.py:245` whole-dump expectation is **hand-written from the settled
   semantics before the test is run** — owner sequencing, and the one place where reverse-engineering
   an expectation from observed behaviour would destroy the evidence.
2. **TEAx branch off `fa0e06a`**: vocabulary split, fail-closed lookups, policy + config,
   `ships_constraint_report` as the single authority (and `_report_declared_in_spec` deleted), vendored
   sets, evidence `v2`, assessment carry, query surface.
3. **Codegen execution lane and cross-repo tests run green** with that branch checked out. After 2 by
   necessity: codegen's venv imports `simkit` from the TEAx working tree, so a new-vocabulary report
   projected through `PreparedEvaluator` cannot pass against unmodified TEAx. *Violated (running step
   1's suite before step 2 exists) → a red lane that reads like a codegen defect and is not one.*
4. **Publish: codegen first, TEAx second.** *Violated (TEAx first) → a TEAx accepting only
   `3.0.0`/`2.0.0` rejects every package the then-current codegen main produces, and studies stop.*
   Codegen-first is safe because TEAx main already fails closed on `3.0.0` today.

**"Never bump TEAx first" is about publication, not checkout order.** A local TEAx branch existing
before codegen's suite runs is not a bump; nothing is pushed until both trees are green. All TEAx work
stays on that branch — `main` is never committed to (**[NEED]**, owner).

## Architecture

```
elaborate ──> InstanceGraph.constraint_usages   (Item 2: the whole authored domain)
                     │
project ─────────────┼──> ConstraintCatalog (sealed, fingerprinted)   ── the ONE authority
                     │            │
                     │            ├── coverage_account(catalog)   [generation/coverage.py]
                     │            │     bucket table over (asserted, inapplicable, disposition_kind)
                     │            │     + D9 refusal + KNOWN_REASONS vocabulary pin
                     └──> aggregator module ◄──┘ baked constants
                                  │
generate ────────────────────────>├── schemas/constraint_types.py  (ConstraintReport + CoverageAccount)
                                  ├── modules/…report_aggregator.py (precedence over statuses + account)
                                  ├── pipelines/…yaml               (report channel pinned as exit)
                                  └── contracts/model_contract.json (catalog by value, per-usage detail)
                                  │
preflight ───────────────────────>│  recompute account vs plan; aggregator-iff-usage-rows;
                                  │  reason-vocabulary pin; D9 refusal; existing seal check
                                  ▼
                        [sealed package]
                                  │
TEAx  model_contract ──> ships_constraint_report(contract) = bool(usage_records)   ── ONE authority
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
6. Every usage record lands in exactly one bucket of D3's table, and every reason token in
   `DISPOSITION_REASONS` is in `KNOWN_REASONS` — otherwise generation refuses by name.
7. Every report token has exactly one canonical counterpart and vice versa; an unknown token on either
   side raises a named error and never yields a satisfied or unconstrained reading.
8. Nothing reachable from `ModelEvidence.report["coverage"]` is mutable.
9. No usage record is both `eligible` and inapplicable (D9). Therefore an inapplicable gate contributes
   no concrete entry, no result, and no status, and the headline's status set contains only occurrences
   of applicable assessed gates.
10. "Does this package ship a report" is answered in exactly one place per repo: codegen's
    `ships_constraint_machinery`, TEAx's `ships_constraint_report`.
11. Reopening a study store across this item raises `IncompatibleStore`, carried by
    `evidence_schema_version`.

## Component Overview

- **`generation/coverage.py`** (new, codegen) — `coverage_account(catalog)`: the bucket table, the D9
  refusal, and the `KNOWN_REASONS` vocabulary pin. Pure, license-free, unit-testable against a
  hand-built catalog.
- **`templates/constraint_types.py.jinja2`** — gains `CoverageAccount` with its validators;
  `ConstraintReport` gains `coverage`, renames `assessed_count`, widens `headline`'s `Literal`.
- **`templates/report_aggregator.py.jinja2`** — bakes the account as a constant; implements D6.
- **`generation/modules.py::render_report_aggregator`** — passes the account into the template.
- **`generation/constraint_plan.py`** — carries the computed account so preflight and renderer read one
  value.
- **`cli/__init__.py`** — sixth preflight: account recomputation, aggregator-iff-usage-rows, reason
  vocabulary, D9 refusal; and the redundant `:411` guard collapses.
- **`resolution/models.py`** — `ships_constraint_machinery` body changes; `has_executable_content`
  deleted.
- **`elaboration/project.py::_build_constraint_modules`** — mints the zero-input aggregator (`:892`).
- **`contracts/versions.py`** — `RUNTIME_CONTRACT_VERSION = "2.0.0"`.
- **TEAx `evaluation/evidence.py`** — split vocabularies, extended map, `UnknownHeadlineToken`.
- **TEAx `evaluation/projection.py`** — fail-closed lookup.
- **TEAx `evaluation/evaluator.py`** — `_report_declared_in_spec` deleted; `expects_constraint_report`
  required.
- **TEAx `evaluation/package_load.py`** — re-vendored accepted sets.
- **TEAx `study/model_contract.py`** — `ships_constraint_report`, the single consumer authority.
- **TEAx `study/policy.py`, `study/config.py`, `study/cli.py`, `study/query.py`** — dispatch, opt-in,
  authority call, coverage on the case row.

## Non-Goals

- Touching `agentic-mbse`. Nothing here names a companion surface; if implementation finds one, that is
  a surfacing event, not a quiet edit. (D9's authoring-time advisory is *filed* for the companion, not
  built.)
- Any per-usage detail outside the catalog, or a second inventory of any kind.
- Changing Item 2's disposition vocabulary, usage-tier schema, mint-time behaviour, or totality gate —
  including forbidding the eligible+inapplicable combination at authoring time (D9 refuses it at
  generation instead).
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
- **The bucket table is a plan input.** D3's four rows, the `KNOWN_REASONS` pin, and D9's refusal are
  the artifact the preflight, the validators, and the hand-written fixtures all read. Implement the
  table as the function's literal structure, not as scattered conditionals.
- **`catf_mfe_d5` is the descriptive-only fixture**, not a partial one: all 65 usages are bare
  `constraint`, so it reads `not_assessed` with `authored_usage_total = 65` and
  `applicable_gate_total = 0`.
- **Baseline churn is narrower than it looks (DR-11).** `tests/fixtures/baseline_outputs/*` holds only
  `registry_init.py` and `computation_graph.json`. Fixtures that gain an aggregator churn in both;
  fixtures already carrying one churn in neither unless their channel set moves; constraint-free
  fixtures must stay byte-identical (LC-E12), which is the gate proving the trigger did not widen. Two
  stale-baseline classes are known and pre-existing (`deep_cross_scope`, `plant_values`) — do not
  absorb them.
- **Gates:** `/home/reid/1cfe/item7-rebuild-venv/bin/python -m pytest`, never `uv run`. License via
  `set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a`; a green run with license-skip lines is not
  a run. TEAx suite from `/home/reid/1cfe/teax/packages/teax-simkit` (`pytest`, `testpaths =
  simkit/tests`).
- **Do not ruff-format generated baselines** — generator-owned bytes.

## Potential Risks

- **Wrong-but-confident counts (B1).** Mitigated by deriving from the sealed catalog only, by the
  arithmetic validators, and by the preflight — but a systematic misreading of a disposition would pass
  all three. **The mitigation is specific, and the specificity is the whole point (DR-6): each
  fixture's expected account is written from that fixture's `.sysml` source and D3's bucket table —
  reading what the author wrote and deciding how many gates there are — never transcribed from a
  catalog dump, a generated report, or Item 2's disposition table.** A transcription would inherit the
  exact error B1 names and would falsify nothing. Fixture sources are small enough to make this
  practical; `catf_mfe_d5` at 65 usages is counted the honest way that scales — two greps over the
  fixture source, `assert` = **0** and bare `constraint` declarations = **65** (run this stage), which
  puts all 65 in bucket 1 and fixes every field of the account without counting to 65 by eye. That is
  still source-derived: it reads what the author wrote, not what the catalog concluded. The plan
  carries this as an explicit instruction, not as a note.
- **The cross-repo red window (step 3).** Between codegen's source landing and the TEAx branch, the
  codegen execution lane is red for a non-defect reason. Mitigation: land them in one working session
  and record the intermediate state in `verification.md`.
- **The required `expects_constraint_report` argument (D7)** touches fourteen TEAx test call sites. All
  mechanical, none semantic; sized here so the plan does not discover it.
- **`RUNTIME_CONTRACT_VERSION` bump blast radius.** Any other consumer of a sealed package is refused
  after the bump. Known consumers are TEAx and codegen's own tests; the fusion/stellarator demo
  branches are local, pinned, and not regenerated by this item.
- **D9 refuses a model that generates today.** A model with an eligible gate carrying `@inapplicable:`
  stops generating. That is the intent (an annotation must not kill a live gate), and nothing in the
  tree carries the combination: `@inapplicable:` appears in five fixtures
  (`tests/fixtures/constraint_domain_inapplicable*`), and in every one the marker sits on a `Detached`
  part with zero occurrences — the vacuous-gate case the marker exists for. Verified this stage. If a
  customer model carries it, the refusal names the usage and the fix is one doc comment.

## Integration Strategy

This completes the chain Items 1 and 2 started: Item 1 fixed the meanings, Item 2 made the catalog own
the complete domain, and this item makes the report and the study consume it. It replaces the
not-failed headline and Item 2's interim `ships_constraint_machinery` rule, deletes
`has_executable_content` and TEAx's second report-expectation derivation, and adds nothing beside the
catalog. Item 5's CATF migration reads the same account for its all-65 disposition table; Item 6's
calc-def gates enter the denominator through `applicable_gate_total` without a report change.

## Validation Approach

Pinned independently, each by a test no other state satisfies:

1. **Six-state matrix, twice** — five report headline values plus report-absent, and six runtime
   dispositions. Expected accounts hand-written from fixture `.sysml` sources (Potential Risks).
2. **Violation + non-full coverage** — one violated gate, at least one unassessed applicable gate:
   headline `violation`, `coverage_state "partial"`, counts present in the case record.
3. **Full satisfaction is unclaimable under partial assessment** — some gates assessed, all passing.
4. **Both zero-input branches** — descriptive-only → `not_assessed`; asserted gates with zero eligible
   entries → `partial_coverage`; both with a retained exit-point channel.
5. **D4's ruling** — all asserted gates inapplicable → `not_assessed` with positive
   `inapplicable_gate_count`.
6. **D9's refusal** — a fixture with an eligible gate carrying `@inapplicable:` refuses generation by
   name, before any output is written; plus the unit case over a hand-built catalog.
7. **Bucket-table totality** — a unit test over hand-built usage records covering every row of D3's
   table and every reason token in `DISPOSITION_REASONS`, asserting the arithmetic identities hold in
   each; plus the vocabulary-pin refusal when `KNOWN_REASONS` and `DISPOSITION_REASONS` disagree.
8. **Divergence refusals** — perturb the plan's account, and perturb the catalog after sealing; each
   observes its named refusal.
9. **Unknown tokens fail closed** — a hand-built report with an unmapped token on the report side, and
   an unmapped canonical token on the runtime side; both name an error, neither reads satisfied.
10. **Invariant 41** — mutating the nested coverage block through evidence raises.
11. **Invariant 50, through its real carrier** — reopening a store whose bound
    `evidence_schema_version` is `v1` with a `v2` definition raises `IncompatibleStore`. The test varies
    that field specifically, not the model-contract fingerprint.
12. **One report-expectation authority** — a zero-input package: `ships_constraint_report` answers
    `True` from `usage_records`, the 46a corruption check still fires when the report channel is
    removed, and no spec-derived fallback exists to disagree with it.
13. **File-backed persist/harvest round-trip (DR-13)** — invariant 46's clause: generate, persist, and
    harvest a report through `FileBackedEvaluator` and assert the `coverage` block survives byte-equal
    with no consumer-side adapter. Home: TEAx's existing
    `tests/evaluation/test_constraint_evidence_durability.py`, which already covers the
    prepared/file-backed pair.
14. **Cross-repo pins** — codegen's version drift test extended to `RUNTIME_CONTRACT_VERSION`; TEAx
    pins the token map against a codegen-generated fixture package.
15. **Three-route parity** — live, snapshot, relocated agree on report bytes including the account.
16. **The two-tier asymmetry (DR-12)** — one gate over many occurrences: `assessed_gate_count = 1`
    beside `assessed_entry_count = n`, asserted deliberately so it is not later "fixed".
17. **Byte stability** — constraint-free fixtures unchanged.

New fixtures required: asserted-with-zero-eligible, all-inapplicable, mixed-partial,
violation-plus-partial, and eligible-plus-inapplicable (refusal). Reuse `catf_mfe_d5` for
descriptive-only.

## Next-Stage Handoff

- **Fixed:** the token map (D1), the block shape and derived histogram keys (D2), the bucket table,
  vocabulary pin and two-ended divergence check (D3), the D4 and D9 rulings, the report-required
  trigger and per-seam consequences (D5), the precedence function and its status-set property (D6),
  keep-for-boundary default with fingerprint-bearing opt-in and one report-expectation authority (D7),
  version moves and landing order (D8).
- **Open for the plan:** fixture authoring specifics; whether the sixth preflight is one function or
  several; exact `query.py` column surface; where the hand-written fusion coverage block is recorded
  before it is run.
- **De-risk first:** probe B3, then hand-write the `test_fusion_tea_real_teax.py` expected account —
  both cheap, both gating work that would otherwise be redone.
- **Inherited instruction, not a note:** expected accounts come from fixture `.sysml` sources and D3's
  bucket table. A catalog-dump transcription does not discharge B1 and is not an acceptable shortcut.

---
**Next Step:** `/_my_plan` — with D3's bucket table as a plan input.

## Appendix A — Product-lens ledger entry (design stage)

Appended to `.project/active/constraint-coverage-policy/product-lens.md`; reproduced here so the design
is self-contained. **Provenance flag:** the runner script `/home/reid/.claude/scripts/product-lens.md`
is outside this session's sandbox; the method is reconstructed from the spec-stage entry in that ledger
and from Item 2's, per this epic's convention. The reviewer's own lens pass (`design_review-F1..F3`,
gate DISPOSED) is carried in the review file and folded into DR-2, DR-3, and DR-13.

**Point** (re-derived from sources, unchanged from the spec-stage entry; all five items still hold).
**Falsifier** (unchanged): a constraint-bearing model that still emits no report; a coverage number
computed from anything but the catalog; a state present in one vocabulary only; a study store silently
rebound.

**Findings**

- **design-F1 [DONE, in this design] — the `expects_report` authority was about to be silently
  invalidated.** Found at rev 1 in `study/cli.py:42`; the review found its sibling at
  `evaluator.py:79-87`. Owned by D7, which now removes the duplication rather than re-syncing it.
- **design-F2 [FILED, Item 1 territory] — Appendix C's vacuous-gate cell over-permits in the degenerate
  case.** D4 rules against that reading with published reasoning; the cell wants "…and at least one gate
  remains" at close.
- **design-F3 [ACCEPTED, recorded] — the epic's scope-4 wording stays looser than the contract.** D5
  follows LC-E10; the epic text still wants the correction at close.
- **design-F4 [DONE at rev 2] — an annotation could have become a silent kill-switch for a live gate.**
  An eligible usage carrying `@inapplicable:` is reachable, and honouring it would let one doc comment
  remove a failing physics check from the denominator while the headline read `full_satisfaction`. D9
  refuses it loudly instead, and files the authoring-time advisory for the companion.

**Not findings (checked, clean):** no owner-graded statement is contradicted — D-1, D-2 and D-3 are
untouched, and D3 derives in one direction with no consumer-side reconstruction (rev 2 *removes* two
consumer-side re-derivations: DR-7's runtime check and DR-2's spec-derived default). The
`[OWNER-VERBATIM]` design-search quote is carried whole in The Point at the owner's emphasis. The
`[NEED]` sequencing instruction is honoured in D8 step 1 and again in Next-Stage Handoff. Q6's defaults
are reproduced exactly in D7. Invariants 32, 41, 48, 49, 50, and 61 are each carried whole. Invariant
50's discharge now names the field that actually moves.

**Gate: DISPOSED (design-F1..design-F4)** — nothing blocks.
